"""Tests for Product class."""
import os.path
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import pds.naif_pds4_bundler.classes.product.product as product_module
from pds.naif_pds4_bundler.classes.product.product import Product


def make_product_setup(tmp_path: Path, checksum: bool = False,
                       pds_version: str = '4') -> SimpleNamespace:
    # Create a minimal setup object with only the attributes required by Product.
    setup = SimpleNamespace()

    setup.args = SimpleNamespace(checksum=checksum)
    setup.date_format = 'maklabel'
    setup.mission_acronym = 'maven'
    setup.pds_version = pds_version
    setup.volume_id = 'MAVEN_1001'
    setup.working_directory = str(tmp_path / 'working')

    setup.add_file = Mock()
    setup.add_checksum = Mock()

    return setup


def make_product_without_init(path: Path, setup: SimpleNamespace,
                              new_product: bool = True) -> Product:
    # Build a Product instance without calling __init__. This keeps register
    # tests focused on register itself and avoids the constructor auto-registering
    # the product before the test is ready.
    product = Product.__new__(Product)

    product.path = str(path)
    product.setup = setup
    product.new_product = new_product

    return product


class TestProductInit:

    @pytest.mark.parametrize('file_name, expected_extension', [
        ('bundle_maven_spice_v001.xml', 'xml'),
        ('readme', 'readme')])
    def test_init_uses_configured_creation_datetime_and_initializes_attributes(
            self, mocker, tmp_path, file_name, expected_extension) -> None:
        # Verify that Product.__init__ uses setup.creation_date_time when it is already
        # configured, initializes constructor-only attributes, and delegates file-derived
        # state to register() without calling creation_time().

        # Build a minimal setup.
        setup_instance = make_product_setup(tmp_path)

        # Forces a configured date.
        setup_instance.creation_date_time = '2026-05-27T10:20:30Z'

        # Create a product instance to which the attributes setup, path and
        # new_product will then be added.
        product = Product.__new__(Product)
        product.setup = setup_instance
        product.path = str(tmp_path / file_name)
        product.new_product = False

        # Mock create_time to check that it is not called.
        creation_time_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.creation_time')

        # Mock the register() method to avoid disk I/O and to verify that the
        # constructor calls it only once.
        register_mock = mocker.patch.object(Product, 'register', autospec=True)

        Product.__init__(product)

        # Check that the given date is used.
        assert product.creation_time == '2026-05-27T10:20:30Z'

        # Check that the date has been correctly derived without the time.
        assert product.creation_date == '2026-05-27'

        # Check the extension.
        assert product.extension == expected_extension

        # Check that these attributes have been initialised but do not yet have
        # a calculated value.
        assert product.checksum is None
        assert product._size is None

        # It confirms that no new date was generated.
        creation_time_mock.assert_not_called()

        # Check that only call once to register.
        register_mock.assert_called_once_with(product)

    @pytest.mark.parametrize('date_format, generated_creation_time', [
        ('maklabel', '2026-05-27T10:20:30Z'),
        ('infomod2', '2026-05-27T10:20:30.000Z')])
    def test_init_generates_creation_time_when_setup_has_no_creation_datetime(
            self, mocker, tmp_path, date_format, generated_creation_time) -> None:
        # Verify that Product.__init__ generates creation_time through creation_time()
        # when setup.creation_date_time is absent, using setup.date_format and still
        # initializing the constructor-owned attributes before delegating to register().

        # Build a minimal setup instance.
        setup_instance = make_product_setup(tmp_path)
        setup_instance.date_format = date_format

        # Build a product instance.
        product = Product.__new__(Product)

        # Assign the setup that the constructor will use.
        product.setup = setup_instance

        # Assign the product's path.
        product.path = str(tmp_path / 'collection_spice_kernels_v001.xml')

        # Adds the new_product attribute even it will not be used.
        product.new_product = False

        # Mock creation_time to return the date.
        creation_time_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.creation_time',
            return_value=generated_creation_time)

        # Mock the register call.
        register_mock = mocker.patch.object(Product, 'register', autospec=True)

        Product.__init__(product)

        # Check that the constructor has stored the value returned by
        # creation_time().
        assert product.creation_time == generated_creation_time

        # Check that creation_date is correctly derived from creation_time.
        assert product.creation_date == '2026-05-27'

        # Check that the file extension is correctly obtained from the filename.
        assert product.extension == 'xml'

        # Check that the attributes calculated by register() are initialised to
        # None in the constructor.
        assert product.checksum is None
        assert product._size is None

        # Check that the creation_time and register called once.
        creation_time_mock.assert_called_once_with(time_format=date_format)
        register_mock.assert_called_once_with(product)


class TestProductRegister:

    def test_register_uses_checksum_registry_and_registers_new_pds4_product(
            self, mocker, tmp_path) -> None:
        # Verify the main PDS4 registration path: register() reads the file size, reuses
        # the checksum found in the checksum registry, skips fallback checksum sources,
        # and registers a new product using its maven_spice-relative archive path.

        # Build the product path within a realistic PDS4 structure.
        product_path = (tmp_path / 'bundle' / 'maven_spice' / 'spice_kernels' /
                        'spk' / 'maven_orbit_v01.bsp')

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('kernel-content', encoding='utf-8')

        # Create a minimal setup.
        # The attribute checksum=True enables registry scanning; pds_version='4'
        # enables PDS4 path logic.
        setup = make_product_setup(tmp_path, checksum=True, pds_version='4')

        # Create a Product instance ready run a register() call.
        product = make_product_without_init(product_path, setup)

        # Mock the function that searches for the checksum in the record and
        # force it to find it.
        registry_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_registry',
            return_value='registry-checksum')

        # Mock the fallback function from the tag to verify that it is not used.
        label_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_label')

        # Mock the MD5 calculation to verify that the checksum is not
        # recalculated.
        md5_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.md5')

        product.register()

        # Calculate the real file size
        expected_size = str(product_path.stat().st_size)

        # Check the internal attributes.
        assert product._size == expected_size
        assert product.size == expected_size
        assert product.checksum == 'registry-checksum'

        registry_mock.assert_called_once_with(str(product_path),
                                              setup.working_directory)

        # Check that the tag fallback was not used and that the checksum was not
        # calculated.
        label_mock.assert_not_called()
        md5_mock.assert_not_called()

        # Check that the new product has been registered with the expected
        # relative path PDS4.
        setup.add_file.assert_called_once_with(
            os.path.join(f'spice_kernels', 'spk', 'maven_orbit_v01.bsp'))

        # Check that the checksum has been registered using the full path and
        # the resolved checksum.
        setup.add_checksum.assert_called_once_with(
            str(product_path), 'registry-checksum')

    @pytest.mark.parametrize('registry_value', ['', None])
    def test_register_falls_back_to_label_checksum_when_registry_has_no_match(
            self, mocker, tmp_path, registry_value) -> None:
        # Verify that register() falls back to checksum_from_label() when checksum
        # lookup is enabled but the checksum registry does not contain a value, without
        # recalculating md5 or registering the product when new_product is False.

        # Build a realistic timeline for the product.
        product_path = tmp_path / 'maven_spice' / 'document' / 'spiceds_v001.html'

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('<html />', encoding='utf-8')

        # Create a minimal setup with checksum verification enabled.
        setup = make_product_setup(tmp_path, checksum=True)
        product = make_product_without_init(product_path, setup, new_product=False)

        # Mock the search in the registry and ensure that no checksum is found.
        registry_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_registry',
            return_value=registry_value)

        # Mock the search in the tag and ensure that a checksum is found.
        label_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_label',
            return_value='label-checksum')

        # Mock md5() to verify that it is not being used.
        md5_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.md5')

        product.register()

        # Check the internal attributes.
        assert product.size == str(product_path.stat().st_size)
        assert product.checksum == 'label-checksum'

        # Check that registry and label have been called once and md5 has not
        # been called.
        registry_mock.assert_called_once_with(str(product_path),
                                              setup.working_directory)
        label_mock.assert_called_once_with(str(product_path))
        md5_mock.assert_not_called()

        # Check that neither the product nor its checksum has been recorded
        # because new_product=False.
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()

    @pytest.mark.parametrize('registry_value, label_value', [
        ('', ''),
        (None, None)])
    def test_register_computes_md5_when_registry_and_label_have_no_checksum(
            self, mocker, tmp_path, registry_value, label_value) -> None:
        # Verify the final checksum fallback: when checksum lookup is enabled but both
        # the registry and the product label return no checksum, register() computes the
        # checksum with md5() and does not register setup side effects for existing products.

        # Build a realistic path for the product.
        product_path = (tmp_path / 'maven_spice' / 'miscellaneous' /
                        'orbnum' / 'orbn_00001.orb')

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('orbit-number', encoding='utf-8')

        # Create a minimal setup with the checksum option enabled.
        setup = make_product_setup(tmp_path, checksum=True)
        product = make_product_without_init(product_path, setup, new_product=False)

        # Mock the registry lookup and force it not to return a checksum.
        registry_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_registry',
            return_value=registry_value)

        # Mock the search by tag and also forces it not to return a checksum.
        label_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_label',
            return_value=label_value)

        # Mock the MD5 calculation to return a fixed, verifiable value.
        md5_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.md5',
            return_value='computed-checksum')

        product.register()

        # Check that the file size has been calculated correctly.
        assert product.size == str(product_path.stat().st_size)

        # Check that the final checksum comes from md5().
        assert product.checksum == 'computed-checksum'

        # Check that registry, label and md5 calls once.
        registry_mock.assert_called_once_with(str(product_path),
                                              setup.working_directory)
        label_mock.assert_called_once_with(str(product_path))
        md5_mock.assert_called_once_with(str(product_path))

        # Check that no product or checksum was recorded because
        # new_product=False.
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()

    def test_register_computes_md5_without_reading_registry_when_checksum_is_disabled(
            self, mocker, tmp_path) -> None:
        # Verify that register() skips registry and label checksum lookup when checksum
        # reuse is disabled, computes the checksum directly with md5(), and does not
        # register setup side effects for existing products.

        # Build a realistic path for the product.
        product_path = tmp_path / 'maven_spice' / 'readme.txt'

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('readme', encoding='utf-8')

        # Create a minimal setup with checksum reuse disabled.
        setup = make_product_setup(tmp_path, checksum=False)
        product = make_product_without_init(product_path, setup, new_product=False)

        # Mock registry and label to verify that they are not being used.
        registry_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_registry')
        label_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_label')

        # Mock the MD5 calculation and force a stable result.
        md5_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.md5',
            return_value='computed-checksum')

        product.register()

        # Check that the size has been calculated correctly and that the final
        # checksum comes from md5().
        assert product.size == str(product_path.stat().st_size)
        assert product.checksum == 'computed-checksum'

        # Confirms that neither the register nor the label has been checked.
        registry_mock.assert_not_called()
        label_mock.assert_not_called()

        # Confirms that the checksum has been calculated directly from the
        # product path.
        md5_mock.assert_called_once_with(str(product_path))

        # Check that there are no side effects because new_product=False.
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()

    def test_register_recalculates_checksum_for_checksum_product(self, mocker,
                                                                 tmp_path) -> None:
        # Verify the ChecksumProduct-specific branch: register() must always
        # recalculate checksum files with md5(), skipping checksum registry and
        # label lookup even when checksum reuse is enabled.

        # Build a minimal class named 'ChecksumProduct'. It does not inherit
        # from Product.
        checksum_product_spec = type('ChecksumProduct', (), {})

        # Build a realistic path for the product.
        product_path = tmp_path / 'maven_spice' / 'maven_release_03.checksum'

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('checksum-registry', encoding='utf-8')

        # Create a minimal setup with checksum reuse enabled. In this test, it
        # is enabled deliberately to demonstrate that ChecksumProduct ignores it.
        setup = make_product_setup(tmp_path, checksum=True)

        # Create a test object that appears to be a 'ChecksumProduct'.
        product = Mock(spec=checksum_product_spec)
        product.path = product_path
        product.setup = setup
        product.new_product = False

        # Mock the registry, label and md5 calls.
        registry_mock = mocker.patch.object(product_module,
                                            'checksum_from_registry')
        label_mock = mocker.patch.object(product_module, 'checksum_from_label')
        md5_mock = mocker.patch.object(product_module, 'md5',
                                       return_value='checksum-file-md5')

        Product.register(product)

        # Check that the size has been calculated correctly and that the
        # checksum comes from md5().
        assert product._size == str(product_path.stat().st_size)
        assert product.checksum == 'checksum-file-md5'

        # Check that neither registry nor label has been called.
        registry_mock.assert_not_called()
        label_mock.assert_not_called()

        # Check that the checksum was recalculated using md5() with the correct
        # path.
        md5_mock.assert_called_once_with(product.path)

        # Check that there are no side effects because new_product=False.
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()

    def test_register_registers_new_pds3_product_with_volume_relative_path(
            self, mocker, tmp_path) -> None:
        # Verify the PDS3 new-product registration path: register() computes the file
        # size and checksum, then registers the product using the path relative to the
        # configured volume_id directory instead of the PDS4 mission_spice directory.

        # Build a realistic PDS3 path.
        product_path = (tmp_path / 'bundle' / 'MAVEN_1001' / 'data' /
                        'spk' / 'maven_orbit_v01.bsp')

        # Create all the necessary directories.
        product_path.parent.mkdir(parents=True)
        product_path.write_text('kernel-content', encoding='utf-8')

        # Create a minimal setup configured for PDS3 with checksum reuse
        # disabled.
        setup = make_product_setup(tmp_path, checksum=False, pds_version='3')
        product = make_product_without_init(product_path, setup)

        # Mock the md5() function to produce a stable and verifiable checksum.
        md5_mock = mocker.patch('pds.naif_pds4_bundler.classes.product.product.md5',
                                return_value='computed-checksum')

        product.register()

        # Check that register() has correctly read the file size and that the
        # final checksum is the value returned by md5().
        assert product.size == str(product_path.stat().st_size)
        assert product.checksum == 'computed-checksum'

        # Check that md5() has been called once with the full product path.
        md5_mock.assert_called_once_with(str(product_path))

        # Check the key point of the test: in PDS3, the path recorded must be
        # relative to the MAVEN_1001/ volume, and the checksum must be recorded
        # using the full path and the calculated checksum.
        setup.add_file.assert_called_once_with('data/spk/maven_orbit_v01.bsp')
        setup.add_checksum.assert_called_once_with(str(product_path),
                                                   'computed-checksum')

    def test_register_raises_file_not_found_before_computing_checksum(
            self, mocker, tmp_path) -> None:
        # Verify that register() fails immediately when the product file does not exist,
        # preserving the previous product state and avoiding checksum or setup
        # registration side effects.

        # Creates a path to a file that does not exist, causing a
        # FileNotFoundError to be raised.
        product_path = tmp_path / 'maven_spice' / 'missing.xml'

        # Create a minimal setup with checksum verification enabled. Even if it
        # is enabled, the method should not reach that logic because the file
        # does not exist.
        setup = make_product_setup(tmp_path, checksum=True)

        # Initialise a previous state to demonstrate that the early failure does
        # not overwrite those attributes.
        product = make_product_without_init(product_path, setup, new_product=True)
        product.checksum = 'previous-checksum'
        product._size = 'previous-size'

        # Mocks registry, label and md5 calls.
        registry_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_registry')
        label_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.checksum_from_label')
        md5_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.md5')

        with pytest.raises(FileNotFoundError):
            product.register()

        # Check that the checksum above has not been altered and that the file
        # size has not changed.
        assert product.checksum == 'previous-checksum'
        assert product.size == 'previous-size'

        # Check that no attempt has been made to resolve or calculate any
        # checksums.
        registry_mock.assert_not_called()
        label_mock.assert_not_called()
        md5_mock.assert_not_called()

        # Check that no files or checksums have been recorded in the setup.
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()
