"""Tests for Product class."""
import hashlib
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
    # Build a Product instance without calling __init__. This
    # keeps register tests focused on register itself and avoids the
    # constructor auto-registering the product before the test is ready.
    product = Product.__new__(Product)

    product.path = str(path)
    product.setup = setup
    product.new_product = new_product

    return product


class TestProductInit:

    @pytest.mark.parametrize('file_name, expected_extension', [
        ('bundle_maven_spice_v001.xml', 'xml'),
        ('readme', 'readme'),
        (Path('document') / 'spiceds_v001.html', 'html')])
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


class TestProductComputeChecksum:

    @pytest.mark.parametrize(
        'reuse, registry, label, expected, registry_calls, label_calls, md5_calls', [
            (True, 'reg', 'lab', 'reg', 1, 0, 0),
            (True, '', 'lab', 'lab', 1, 1, 0),
            (True, None, 'lab', 'lab', 1, 1, 0),
            (True, '', '', 'md5', 1, 1, 1),
            (True, None, None, 'md5', 1, 1, 1),
            (False, 'reg', 'lab', 'md5', 0, 0, 1)])
    def test_compute_checksum_resolves_registry_then_label_then_md5(
            self, mocker, tmp_path, reuse, registry, label, expected,
            registry_calls, label_calls, md5_calls) -> None:
        """The checksum comes from the registry, then the label, then md5().

        With checksum reuse on, a registry hit is used as is. If the registry
        gives nothing (empty string or None) we try the label, and if that is
        empty too we compute md5(). With reuse off, only md5() is used. The
        call counts show which sources were actually asked along the way.
        """
        # Preparation: every lookup returns the value of the case, and md5
        # returns a fixed marker so we can tell where the result came from.
        setup = make_product_setup(tmp_path, checksum=reuse)
        product = make_product_without_init(tmp_path / 'p.bsp', setup)
        registry_mock = mocker.patch.object(
            product_module, 'checksum_from_registry', return_value=registry)
        label_mock = mocker.patch.object(
            product_module, 'checksum_from_label', return_value=label)
        md5_mock = mocker.patch.object(product_module, 'md5', return_value='md5')

        # Execution.
        checksum = product._compute_checksum()

        # Verification: the right source won and the others were left alone.
        assert checksum == expected
        assert registry_mock.call_count == registry_calls
        assert label_mock.call_count == label_calls
        assert md5_mock.call_count == md5_calls

    def test_compute_checksum_passes_path_and_working_directory_to_lookups(
            self, mocker, tmp_path) -> None:
        """Each checksum source receives the arguments it needs.

        The registry lookup takes the product path and the working directory,
        while the label lookup and md5() only take the path. The first two
        return nothing here, so that all three get called.
        """
        # Preparation: reuse on and empty lookups, so we go through every source.
        setup = make_product_setup(tmp_path, checksum=True)
        product = make_product_without_init(tmp_path / 'p.bsp', setup)
        registry_mock = mocker.patch.object(
            product_module, 'checksum_from_registry', return_value='')
        label_mock = mocker.patch.object(
            product_module, 'checksum_from_label', return_value='')
        md5_mock = mocker.patch.object(product_module, 'md5', return_value='md5')

        # Execution.
        product._compute_checksum()

        # Verification: exact arguments, and in the right order.
        registry_mock.assert_called_once_with(product.path, setup.working_directory)
        label_mock.assert_called_once_with(product.path)
        md5_mock.assert_called_once_with(product.path)

    def test_compute_checksum_returns_real_md5_of_file_content(
            self, tmp_path) -> None:
        """The checksum is the actual md5 digest of the file content.

        Every other test mocks md5(). This one runs the real thing, so a bad
        hookup to the hashing helper, or a wrong return type, would show up.
        """
        # Preparation: a real file, with reuse off so md5 is the only source.
        path = tmp_path / 'readme.txt'
        path.write_bytes(b'readme')
        setup = make_product_setup(tmp_path, checksum=False)
        product = make_product_without_init(path, setup)

        # Execution.
        checksum = product._compute_checksum()

        # Verification: same value as an independent hashlib computation.
        assert checksum == hashlib.md5(b'readme').hexdigest()



class TestProductRegister:

    @pytest.mark.parametrize('pds_version, parts, expected_relative', [
        ('4', ('bundle', 'maven_spice', 'spice_kernels', 'spk', 'k.bsp'),
         os.path.join('spice_kernels', 'spk', 'k.bsp')),
        ('3', ('bundle', 'MAVEN_1001', 'data', 'spk', 'k.bsp'),
         os.path.join('data', 'spk', 'k.bsp'))])
    def test_register_records_new_product_relative_to_archive_dir(
            self, mocker, tmp_path, pds_version, parts, expected_relative) -> None:
        """A new product is registered with its path inside the archive.

        In PDS4 the archive directory is '<mission>_spice' and in PDS3 it is
        the volume id. Either way, the size and checksum end up on the product
        and the setup is told about the file using the path below that
        directory.
        """
        # Preparation: a real file in the layout of each PDS version. The
        # checksum is fixed, since how it is resolved is not what we test here.
        path = tmp_path.joinpath(*parts)
        path.parent.mkdir(parents=True)
        path.write_text('kernel-content', encoding='utf-8')
        setup = make_product_setup(tmp_path, pds_version=pds_version)
        product = make_product_without_init(path, setup)
        mocker.patch.object(Product, '_compute_checksum', return_value='hook-sum')

        # Execution.
        product.register()

        # Verification: size and checksum are stored on the product.
        assert product.size == str(len('kernel-content'))
        assert product.checksum == 'hook-sum'

        # The setup gets the archive-relative path and the full-path checksum.
        setup.add_file.assert_called_once_with(expected_relative)
        setup.add_checksum.assert_called_once_with(str(path), 'hook-sum')

    def test_register_does_not_record_existing_product(
            self, mocker, tmp_path) -> None:
        """Only products flagged as new are registered in the setup.

        For an existing product (new_product=False) the size and checksum are
        still set, but the setup must not be told anything about it.
        """
        # Preparation: a real file, not flagged as new, and a fixed checksum.
        path = tmp_path / 'maven_spice' / 'readme.txt'
        path.parent.mkdir(parents=True)
        path.write_text('readme', encoding='utf-8')
        setup = make_product_setup(tmp_path)
        product = make_product_without_init(path, setup, new_product=False)
        mocker.patch.object(Product, '_compute_checksum', return_value='hook-sum')

        # Execution.
        product.register()

        # Verification: attributes are set, but nothing is registered.
        assert product.size == str(len('readme'))
        assert product.checksum == 'hook-sum'
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()

    def test_register_uses_real_checksum_resolution_for_base_product(
            self, tmp_path) -> None:
        """register() and the real _compute_checksum() work together.

        The other register() tests patch the checksum hook. This one leaves
        it alone (only the setup is fake), so the connection between the two
        is checked once, end to end.
        """
        # Preparation: a real file, with reuse off so md5 is the only source.
        path = tmp_path / 'maven_spice' / 'readme.txt'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'readme')
        setup = make_product_setup(tmp_path, checksum=False)
        product = make_product_without_init(path, setup, new_product=False)

        # Execution.
        product.register()

        # Verification: the stored checksum is the real md5 of the content.
        assert product.checksum == hashlib.md5(b'readme').hexdigest()

    def test_register_raises_file_not_found_before_computing_checksum(
            self, mocker, tmp_path) -> None:
        """A missing file makes register() fail early and change nothing.

        The size is read first, so a missing file must raise FileNotFoundError
        before any checksum is computed or anything is registered, and the
        product keeps the state it had before.
        """
        # Preparation: a path that does not exist, with reuse on (it must not
        # matter), and a previous state that has to survive the failure.
        setup = make_product_setup(tmp_path, checksum=True)
        product = make_product_without_init(tmp_path / 'missing.xml', setup)
        product.checksum = 'previous-checksum'
        product._size = 'previous-size'
        hook_mock = mocker.patch.object(Product, '_compute_checksum')

        # Execution.
        with pytest.raises(FileNotFoundError):
            product.register()

        # Verification: old state untouched, no checksum computed and nothing
        # registered in the setup.
        assert product.checksum == 'previous-checksum'
        assert product.size == 'previous-size'
        hook_mock.assert_not_called()
        setup.add_file.assert_not_called()
        setup.add_checksum.assert_not_called()
