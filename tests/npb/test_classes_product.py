"""Tests for Product class."""
import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

import pds.naif_pds4_bundler.classes.product.product as product_module
from pds.naif_pds4_bundler.classes.product.product import Product
from pds.naif_pds4_bundler.classes.run_state import RunState


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

    return setup


def make_product_without_init(path: Path, setup: SimpleNamespace,
                              new_product: bool = True) -> Product:
    # Build a Product instance without calling __init__, so the tests control
    # every attribute the methods under test read.
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
        # configured and initializes the attributes that derive_file_attributes()
        # fills in later, without calling creation_time().

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

    @pytest.mark.parametrize('date_format, generated_creation_time', [
        ('maklabel', '2026-05-27T10:20:30Z'),
        ('infomod2', '2026-05-27T10:20:30.000Z')])
    def test_init_generates_creation_time_when_setup_has_no_creation_datetime(
            self, mocker, tmp_path, date_format, generated_creation_time) -> None:
        # Verify that Product.__init__ generates creation_time through creation_time()
        # when setup.creation_date_time is absent, using setup.date_format and still
        # initializing the constructor-owned attributes.

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

        Product.__init__(product)

        # Check that the constructor has stored the value returned by
        # creation_time().
        assert product.creation_time == generated_creation_time

        # Check that creation_date is correctly derived from creation_time.
        assert product.creation_date == '2026-05-27'

        # Check that the file extension is correctly obtained from the filename.
        assert product.extension == 'xml'

        # Check that the attributes calculated by derive_file_attributes() are initialised to
        # None in the constructor.
        assert product.checksum is None
        assert product._size is None

        # Check that creation_time was called once.
        creation_time_mock.assert_called_once_with(time_format=date_format)


class TestProductSetCommonAttributes:

    @pytest.mark.parametrize('creation_date_time, expected', [
        ('2026-05-27T10:20:30Z', '2026-05-27T10:20:30Z'),
        (None, '2026-06-01T01:02:03Z'),
    ])
    def test_sets_creation_time_date_and_extension(
            self, mocker, tmp_path, creation_date_time, expected) -> None:
        # The creation time comes from the setup when it has one and is
        # generated otherwise; the date and the extension are derived.

        # A bare product whose setup may or may not carry a creation time.
        setup = make_product_setup(tmp_path)
        if creation_date_time:
            setup.creation_date_time = creation_date_time
        product = Product.__new__(Product)
        product.setup = setup
        product.path = str(tmp_path / 'collection_inventory_v001.csv')
        mocker.patch(
            'pds.naif_pds4_bundler.classes.product.product.creation_time',
            return_value='2026-06-01T01:02:03Z')

        # Set the attributes.
        product._set_common_attributes()

        # All three are set, and nothing that needs the file is touched.
        assert product.creation_time == expected
        assert product.creation_date == expected.split('T')[0]
        assert product.extension == 'csv'
        assert not hasattr(product, 'checksum')


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


class StubHookProduct(Product):
    # Overrides the hook with a directory the pds_version fallback never yields.
    @property
    def _archive_root_dir(self) -> str:
        return 'custom_root'


class StubFailingHookProduct(Product):
    # Implements the hook but fails with an error other than NotImplementedError.
    @property
    def _archive_root_dir(self) -> str:
        raise ValueError('boom')


class TestProductDeriveFileAttributes:

    @pytest.mark.parametrize('new_product', [True, False])
    def test_derive_file_attributes_sets_attributes(
            self, mocker, tmp_path, new_product) -> None:
        """Size, checksum and the path to register are stored on the product,
        new or not."""

        # A real file inside the archive layout and a fixed checksum.
        path = tmp_path / 'maven_spice' / 'readme.txt'
        path.parent.mkdir(parents=True)
        path.write_text('readme', encoding='utf-8')
        product = make_product_without_init(
            path, make_product_setup(tmp_path), new_product=new_product)
        mocker.patch.object(
            Product, '_compute_checksum', return_value='hook-sum')

        # Derive the attributes.
        product.derive_file_attributes()

        # The attributes are there.
        assert product.size == str(len('readme'))
        assert product.checksum == 'hook-sum'
        assert product.registered_path == str(path)

    def test_registered_path_is_kept_when_the_path_changes_afterwards(
            self, mocker, tmp_path) -> None:
        """Registering uses the path the file had when it was derived, even
        if the product path is replaced later on."""

        # Derive the attributes of a new product.
        path = tmp_path / 'maven_spice' / 'readme.txt'
        path.parent.mkdir(parents=True)
        path.write_text('readme', encoding='utf-8')
        product = make_product_without_init(path, make_product_setup(tmp_path))
        mocker.patch.object(
            Product, '_compute_checksum', return_value='hook-sum')
        product.derive_file_attributes()

        # A subclass changes the path after deriving, and then the product is
        # registered.
        product.path = str(tmp_path / 'bundle_maven_spice_v001.xml')
        run_state = RunState()
        run_state.register_product(product)

        # The original path is the one that reached the run state.
        assert run_state.file_list == ['readme.txt']
        assert run_state.checksum_registry == [f'{path} hook-sum']

    def test_init_does_not_read_the_file(self, tmp_path) -> None:
        """The constructor only sets the common attributes; it neither reads
        the file nor derives anything from it."""

        # Product with a path that does not exist on disk.
        product = Product.__new__(Product)
        product.setup = make_product_setup(tmp_path)
        product.path = str(tmp_path / 'missing.txt')

        # Build it.
        Product.__init__(product)

        # Nothing was derived.
        assert product.checksum is None
        assert product.size is None
        assert product.registered_path is None

    def test_derive_file_attributes_uses_real_checksum_resolution(
            self, tmp_path) -> None:
        """derive_file_attributes() and the real _compute_checksum() work
        together.

        The other derive tests patch the checksum hook. This one leaves it
        alone (only the setup is fake), so the connection between the two is
        checked once, end to end.
        """
        # Preparation: a real file, with reuse off so md5 is the only source.
        path = tmp_path / 'maven_spice' / 'readme.txt'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'readme')
        setup = make_product_setup(tmp_path, checksum=False)
        product = make_product_without_init(path, setup, new_product=False)

        # Execution.
        product.derive_file_attributes()

        # Verification: the stored checksum is the real md5 of the content.
        assert product.checksum == hashlib.md5(b'readme').hexdigest()

    def test_derive_file_attributes_raises_file_not_found_before_checksum(
            self, mocker, tmp_path) -> None:
        """A missing file makes derive_file_attributes() fail early and
        change nothing.

        The size is read first, so a missing file must raise FileNotFoundError
        before any checksum is computed, and the product keeps the state it
        had before.
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
            product.derive_file_attributes()

        # Verification: old state untouched and no checksum computed.
        assert product.checksum == 'previous-checksum'
        assert product.size == 'previous-size'
        hook_mock.assert_not_called()


class TestProductArchivePath:

    @pytest.mark.parametrize('product_class, pds_version, parts, expected', [
        (Product, '4',
         ('bundle', 'maven_spice', 'spice_kernels', 'spk', 'k.bsp'),
         Path('spice_kernels', 'spk', 'k.bsp')),
        (Product, '3',
         ('bundle', 'MAVEN_1001', 'data', 'spk', 'k.bsp'),
         Path('data', 'spk', 'k.bsp')),
        (StubHookProduct, '4',
         ('bundle', 'custom_root', 'data', 'k.bsp'),
         Path('data', 'k.bsp')),
        (StubHookProduct, '3',
         ('bundle', 'custom_root', 'data', 'k.bsp'),
         Path('data', 'k.bsp')),
    ])
    def test_archive_path_is_relative_to_the_archive_directory(
            self, tmp_path, product_class, pds_version, parts,
            expected) -> None:
        """The path starts below '<mission>_spice' (PDS4), the volume id
        (PDS3) or the directory named by an implemented _archive_root_dir."""

        # Skip __init__; only registered_path and setup matter here.
        product = product_class.__new__(product_class)
        product.registered_path = str(tmp_path.joinpath(*parts))
        product.setup = make_product_setup(tmp_path, pds_version=pds_version)

        # Read the property.
        archive_path = product.archive_path

        # Everything up to and including the archive directory is dropped.
        assert archive_path == expected

    def test_archive_path_does_not_swallow_errors_from_archive_root_dir_hook(
            self, tmp_path) -> None:
        """Only NotImplementedError triggers the fallback.

        Any other error raised by an implemented hook is a real bug and must
        propagate.
        """
        # A layout the fallback could resolve, so a wrongly swallowed error
        # would show up as a successful path.
        product = StubFailingHookProduct.__new__(StubFailingHookProduct)
        product.registered_path = str(tmp_path / 'maven_spice' / 'k.bsp')
        product.setup = make_product_setup(tmp_path)

        # Reading the path must raise the hook's own error.
        with pytest.raises(ValueError, match='boom'):
            _ = product.archive_path
