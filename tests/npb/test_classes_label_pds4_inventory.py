"""Tests for the InventoryPDS4Label class.

Two test classes are provided:

* TestInventoryPDS4Label – unit tests that mock the inherited label writing
  so the constructor can be exercised in isolation. ``PDSLabel.__init__`` is
  NOT mocked: it runs for real (as in the sibling label test modules), so the
  inventory product must expose every attribute the parent reads, and the
  physical inventory file pointed to by ``inventory.path`` must exist on disk
  because the constructor counts its lines for ``N_RECORDS``.

* TestInventoryPDS4LabelIntegration – integration tests that exercise
  InventoryPDS4Label together with the real PDSLabel.write_label() logic,
  writing an actual XML label to a temp directory and asserting on its
  contents.

InventoryPDS4Label is peculiar compared with the other PDS4 labels:

* The template name is derived from ``collection.type`` (NOT from a fixed
  string and NOT from ``collection.name``).
* START_TIME / STOP_TIME come from two mutually exclusive sources depending on
  ``collection.name``:
    - 'miscellaneous'  -> the min start / max stop of the checksum products
                          found in ``collection.product``.
    - anything else    -> setup.increment_start / setup.increment_finish.
* N_RECORDS is the number of physical lines of the inventory file.
* The XML label name is ``collection.name`` truncated at the FIRST dot
  (the same truncation bug shared by every other PDS4 label).
"""
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_inventory import InventoryPDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the collaborator mocks (setup, collection, inventory)
# ---------------------------------------------------------------------------

@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic factories for collection-inventory labels.

    Reuses ``base_helpers.make_setup`` (adding the increment_* attributes the
    label needs in the non-miscellaneous branch) and ``base_helpers.make_product``
    (used both for the inventory product and for the checksum products held by
    the collection), and adds a ``make_collection`` factory.

    :param base_helpers: generic Setup/base-product factories from conftest
    :return: container with make_setup, make_inventory, make_checksum_product
             and make_collection callables
    """

    def _make_setup(end_of_line: str = 'LF', eol_pds4: str = '\n') -> MagicMock:
        # Reuse the generic setup and add the increment window consumed by the
        # non-miscellaneous branch of the constructor.
        setup = base_helpers.make_setup(end_of_line=end_of_line,
                                        eol_pds4=eol_pds4)
        setup.increment_start = '2024-02-01T00:00:00Z'
        setup.increment_finish = '2024-02-28T23:59:59Z'
        return setup

    def _make_inventory(staging_dir: Path,
                        name: str = 'collection_spice_kernels_inventory_v001.csv',
                        n_records: int = 3) -> MagicMock:
        # The inventory product file physically lives under the staging dir and
        # must exist because the constructor opens it to count records. We write
        # "n_records" real lines so N_RECORDS can be asserted deterministically.
        staging_dir.mkdir(parents=True, exist_ok=True)
        inventory_path = staging_dir / name
        inventory_path.write_text(
            ''.join(f'P,urn:nasa:pds:maven_spice:product_{i}::1.0\n'
                    for i in range(n_records)),
            encoding='utf-8')

        return base_helpers.make_product(
            path=str(inventory_path),
            name=name,
            lid='urn:nasa:pds:maven_spice:spice_kernels',
            collection_name='spice_kernels')

    def _make_checksum_product(name: str, start_time: str,
                               stop_time: str) -> MagicMock:
        # A minimal stand-in for a checksum product: only 'name' (used by the
        # '"checksum" in product.name' filter) and the two coverage strings
        # are read by the miscellaneous branch.
        product = base_helpers.make_product(path=name, name=name)
        product.start_time = start_time
        product.stop_time = stop_time
        return product

    def _make_collection(name: str = 'spice_kernels',
                         coll_type: str = 'spice_kernels',
                         products: list[MagicMock] | None = None) -> MagicMock:
        # 'type' drives the template path; 'name' drives both the time-source
        # branch and the XML label name; 'product' is only iterated in the
        # miscellaneous branch.
        collection = MagicMock()
        collection.name = name
        collection.type = coll_type
        collection.lid = 'urn:nasa:pds:maven_spice:spice_kernels'
        collection.vid = '1.0'
        collection.product = products if products is not None else []
        return collection

    return SimpleNamespace(make_setup=_make_setup,
                           make_inventory=_make_inventory,
                           make_checksum_product=_make_checksum_product,
                           make_collection=_make_collection)


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestInventoryPDS4Label:
    """Unit tests for InventoryPDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> InventoryPDS4Label:
        """Build an InventoryPDS4Label (spice_kernels branch) while mocking the
        inherited file writing.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized inventory factories
        :return: constructed label with write_label patched out
        """
        setup = helpers.make_setup()

        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging, n_records=3)
        collection = helpers.make_collection()

        # Avoid real template reading and file writing in unit tests. Note that
        # PDSLabel.__init__ is intentionally NOT mocked.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            instance = InventoryPDS4Label(setup, collection, inventory)

        return instance

    # ------------------------------------------------------------------
    # Regular tests – attribute assignments (spice_kernels / else branch)
    # ------------------------------------------------------------------

    def test_attribute_assignments(self, label: InventoryPDS4Label) -> None:
        # Validate the PDS4 inventory label attributes populated during
        # construction for the non-miscellaneous (else) branch.

        # FILE_NAME is copied verbatim from inventory.name.
        assert label.FILE_NAME == 'collection_spice_kernels_inventory_v001.csv'

        # The collection identifiers are copied from collection.lid/vid.
        assert label.COLLECTION_LID == 'urn:nasa:pds:maven_spice:spice_kernels'
        assert label.COLLECTION_VID == '1.0'

        # In the else branch the coverage comes from setup.increment_*.
        assert label.START_TIME == '2024-02-01T00:00:00Z'
        assert label.STOP_TIME == '2024-02-28T23:59:59Z'

        # N_RECORDS is the line count of the physical inventory file, as a str.
        assert label.N_RECORDS == '3'

        # The XML label name is derived from collection.name (no dot here).
        assert label.name == 'spice_kernels.xml'

    def test_template_path_is_derived_from_collection_type(
            self, label: InventoryPDS4Label) -> None:
        # The label resolves the template from collection.type, NOT from a fixed
        # name and NOT from collection.name.
        expected_template = str(
            Path(label.setup.templates_directory)
            / 'template_collection_spice_kernels.xml')

        assert label.template == expected_template

    def test_constructor_stores_references_and_writes_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Validate constructor wiring and its single write_label side effect.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging)
        collection = helpers.make_collection()

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            label = InventoryPDS4Label(setup, collection, inventory)

        # setup, product (the inventory) and collection are stored as-is.
        assert label.setup is setup
        assert label.product is inventory
        assert label.collection is collection

        # write_label() is called exactly once with the label instance.
        mock_write.assert_called_once_with(label)

    # ------------------------------------------------------------------
    # get_*_reference_type – the two fixed-string overrides
    # ------------------------------------------------------------------

    def test_get_mission_reference_type(self, label: InventoryPDS4Label) -> None:
        # The override returns the literal collection_to_investigation string.
        assert label.get_mission_reference_type() == 'collection_to_investigation'

    def test_get_target_reference_type(self, label: InventoryPDS4Label) -> None:
        # The override returns the literal collection_to_target string.
        assert label.get_target_reference_type() == 'collection_to_target'

    # ------------------------------------------------------------------
    # Template path is parametrized on collection.type
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('coll_type', [
        'spice_kernels', 'document', 'miscellaneous'])
    def test_template_path_uses_collection_type_value(
            self, tmp_path: Path, helpers: SimpleNamespace,
            coll_type: str) -> None:
        # Whatever collection.type is, it is interpolated verbatim into the
        # template file name.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging)

        # Keep name == 'spice_kernels' to stay in the else branch; only vary
        # type so the template is the single thing under test.
        collection = helpers.make_collection(name='spice_kernels',
                                             coll_type=coll_type)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.template == str(
            Path(setup.templates_directory)
            / f'template_collection_{coll_type}.xml')

    # ------------------------------------------------------------------
    # N_RECORDS – line counting over the physical inventory file
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('n_records, expected', [
        (0, '0'), (1, '1'), (42, '42')])
    def test_n_records_counts_physical_lines(
            self, tmp_path: Path, helpers: SimpleNamespace,
            n_records: int, expected: str) -> None:
        # N_RECORDS must equal the number of lines in the inventory file,
        # converted to a string, including the empty-file (0 lines) case.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging, n_records=n_records)
        collection = helpers.make_collection()

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.N_RECORDS == expected

    def test_constructor_raises_when_inventory_file_missing(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # The constructor opens self.product.path for reading; a missing file
        # must raise FileNotFoundError because there is no defensive handling.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging)
        collection = helpers.make_collection()

        # Point the inventory at a non-existent path AFTER creation.
        inventory.path = str(staging / 'does_not_exist.csv')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(FileNotFoundError):
                InventoryPDS4Label(setup, collection, inventory)

    # ------------------------------------------------------------------
    # Miscellaneous branch – coverage from the checksum products
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('checksum_times, expected_start, expected_stop', [
        ([('checksum_v01.tab', '2024-01-10T00:00:00', '2024-01-20T00:00:00')],
         '2024-01-10T00:00:00', '2024-01-20T00:00:00'),
        ([('checksum_v03.tab', '2024-03-01T00:00:00', '2024-03-31T00:00:00'),
          ('checksum_v01.tab', '2024-01-01T00:00:00', '2024-01-31T00:00:00'),
          ('checksum_v02.tab', '2024-02-01T00:00:00', '2024-02-28T00:00:00')],
         '2024-01-01T00:00:00', '2024-03-31T00:00:00')])
    def test_miscellaneous_branch_uses_checksum_min_start_max_stop(
            self, tmp_path: Path, helpers: SimpleNamespace,
            checksum_times: list[tuple[str, str, str]],
            expected_start: str, expected_stop: str) -> None:
        # For the miscellaneous collection the coverage is the earliest checksum
        # start and the latest checksum stop, regardless of insertion order.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(
            staging, name='collection_miscellaneous_inventory_v001.csv')

        checksums = [helpers.make_checksum_product(name, start, stop)
                     for name, start, stop in checksum_times]
        collection = helpers.make_collection(name='miscellaneous',
                                             coll_type='miscellaneous',
                                             products=checksums)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.START_TIME == expected_start
        assert label.STOP_TIME == expected_stop

    def test_miscellaneous_branch_ignores_non_checksum_products(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Only products whose name contains 'checksum' contribute to the
        # coverage window; everything else is skipped by the filter.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(
            staging, name='collection_miscellaneous_inventory_v001.csv')

        # A non-checksum product with extreme times that MUST be ignored, plus
        # one real checksum that defines the expected window.
        non_checksum = helpers.make_checksum_product(
            'orbnum_v01.nrb', '1999-01-01T00:00:00', '2099-12-31T00:00:00')
        checksum = helpers.make_checksum_product(
            'checksum_v01.tab', '2024-01-05T00:00:00', '2024-01-25T00:00:00')
        collection = helpers.make_collection(
            name='miscellaneous', coll_type='miscellaneous',
            products=[non_checksum, checksum])

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.START_TIME == '2024-01-05T00:00:00'
        assert label.STOP_TIME == '2024-01-25T00:00:00'

    def test_miscellaneous_branch_does_not_use_increment_times(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Guard the branch contract: in the miscellaneous branch the increment
        # window is irrelevant even if present on setup.
        setup = helpers.make_setup()
        setup.increment_start = 'SHOULD_NOT_BE_USED_START'
        setup.increment_finish = 'SHOULD_NOT_BE_USED_STOP'
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(
            staging, name='collection_miscellaneous_inventory_v001.csv')

        checksum = helpers.make_checksum_product(
            'checksum_v01.tab', '2024-01-01T00:00:00', '2024-01-31T00:00:00')
        collection = helpers.make_collection(
            name='miscellaneous', coll_type='miscellaneous',
            products=[checksum])

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.START_TIME == '2024-01-01T00:00:00'
        assert label.STOP_TIME == '2024-01-31T00:00:00'

    def test_miscellaneous_branch_without_checksums_raises_value_error(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # For the 'miscellaneous' collection, when no product name contains
        # 'checksum', there is no time source: the constructor now raises a
        # descriptive ValueError instead of IndexError.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(
            staging, name='collection_miscellaneous_inventory_v001.csv')

        # A collection whose products contain no 'checksum' in their names.
        non_checksum = helpers.make_checksum_product(
            'orbnum_v01.nrb', '2024-01-01T00:00:00', '2024-01-31T00:00:00')

        collection = helpers.make_collection(
            name='miscellaneous', coll_type='miscellaneous',
            products=[non_checksum])

        expected_message = (
            f'NPB bug: no checksum product found in collection '
            f'{collection.lid}::{collection.vid}; START_TIME and '
            f'STOP_TIME cannot be determined for the miscellaneous label.')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(ValueError, match=f'^{expected_message}$'):
                InventoryPDS4Label(setup, collection, inventory)

    def test_miscellaneous_branch_with_empty_product_list_raises_value_error(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Same root cause as above but with an entirely empty
        # collection.product list: the empty start_times still triggers the
        # descriptive ValueError.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(
            staging, name='collection_miscellaneous_inventory_v001.csv')

        collection = helpers.make_collection(
            name='miscellaneous', coll_type='miscellaneous', products=[])

        expected_message = (
            f'NPB bug: no checksum product found in collection '
            f'{collection.lid}::{collection.vid}; START_TIME and '
            f'STOP_TIME cannot be determined for the miscellaneous label.')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(ValueError, match=f'^{expected_message}$'):
                InventoryPDS4Label(setup, collection, inventory)

    # ------------------------------------------------------------------
    # XML label name derivation (truncation bug)
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('collection_name, expected_label_name', [
        ('spice_kernels', 'spice_kernels.xml'),
        ('document', 'document.xml'),
        # TODO: BUG; collection.name.split(".")[0] truncates at the FIRST dot,
        #       so a name with more than one dot loses everything after it.
        ('collection.document_inventory_v001.csv', 'collection.xml')])
    def test_label_name_is_derived_from_text_before_first_dot(
            self, tmp_path: Path, helpers: SimpleNamespace,
            collection_name: str, expected_label_name: str) -> None:
        # Document how collection names are converted into XML label names.
        # Note: the name is kept in the else branch (any non-miscellaneous
        # value), so coverage comes from setup.increment_*.
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        inventory = helpers.make_inventory(staging)
        collection = helpers.make_collection(name=collection_name,
                                             coll_type='spice_kernels')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = InventoryPDS4Label(setup, collection, inventory)

        assert label.name == expected_label_name


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

TEMPLATE_CONTENT = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<collection>\n'
    '  <file_name>$FILE_NAME</file_name>\n'
    '  <collection_lid>$COLLECTION_LID</collection_lid>\n'
    '  <collection_vid>$COLLECTION_VID</collection_vid>\n'
    '  <start_date_time>$START_TIME</start_date_time>\n'
    '  <stop_date_time>$STOP_TIME</stop_date_time>\n'
    '  <number_of_records>$N_RECORDS</number_of_records>\n'
    '</collection>\n')


class TestInventoryPDS4LabelIntegration:
    """Integration tests for InventoryPDS4Label + PDSLabel + template."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, MagicMock, Path, Path]:
        """Create the temporary PDS4 template and staging environment used by
        integration tests.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized inventory factories
        :return: tuple of (setup, collection, inventory, template_path,
                 expected_label_path)
        """
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # The template name must match the one selected from collection.type.
        template_path = templates_dir / 'template_collection_spice_kernels.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # 3-line inventory placed directly under staging.
        inventory = helpers.make_inventory(staging_dir, n_records=3)
        collection = helpers.make_collection(name='spice_kernels',
                                             coll_type='spice_kernels')

        # The inherited writer derives the XML label path from product.path:
        # it swaps the product extension for '.xml' AND, because the path
        # contains 'inventory', it strips the 'inventory_' token. So
        # '...collection_spice_kernels_inventory_v001.csv' becomes
        # '...collection_spice_kernels_v001.xml'.
        expected_label_path = Path(
            inventory.path.replace('.csv', '.xml').replace('inventory_', ''))

        return setup, collection, inventory, template_path, expected_label_path

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path]
            ) -> None:
        # Render the inventory XML template and validate the generated label.
        setup, collection, inventory, template_path, label_path = env

        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        label = InventoryPDS4Label(setup, collection, inventory)

        # The class resolved the template from collection.type.
        assert label.template == str(template_path)

        # The real writer mutates label.name to the generated XML file path.
        assert Path(label.name) == label_path

        # The final XML file has been created in staging.
        assert label_path.exists()

        # Compare the generated label with the exact expected content. The else
        # branch supplies the increment coverage; N_RECORDS is the line count.
        assert label_path.read_text(encoding='utf-8') == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<collection>\n'
            '  <file_name>'
            'collection_spice_kernels_inventory_v001.csv</file_name>\n'
            '  <collection_lid>'
            'urn:nasa:pds:maven_spice:spice_kernels</collection_lid>\n'
            '  <collection_vid>1.0</collection_vid>\n'
            '  <start_date_time>2024-02-01T00:00:00Z</start_date_time>\n'
            '  <stop_date_time>2024-02-28T23:59:59Z</stop_date_time>\n'
            '  <number_of_records>3</number_of_records>\n'
            '</collection>\n')

    def test_label_file_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path]
            ) -> None:
        # The rendered label must be well-formed XML with all placeholders
        # substituted by the label state.
        setup, collection, inventory, _, label_path = env

        InventoryPDS4Label(setup, collection, inventory)

        tree = ElementTree.parse(label_path)
        root = tree.getroot()

        assert root.tag == 'collection'
        assert root.findtext('file_name') == (
            'collection_spice_kernels_inventory_v001.csv')
        assert root.findtext('number_of_records') == '3'

        # No unresolved template placeholders must remain.
        assert '$' not in label_path.read_text(encoding='utf-8')

    @pytest.mark.parametrize('end_of_line, eol_pds4', [
        ('LF', '\n'),
        ('CRLF', '\r\n')])
    def test_label_respects_configured_end_of_line(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path],
            end_of_line: str, eol_pds4: str) -> None:
        # The inherited writer must honour the configured PDS4 end-of-line
        # sequence when writing the label.
        setup, collection, inventory, _, label_path = env

        setup.end_of_line = end_of_line
        setup.eol_pds4 = eol_pds4

        InventoryPDS4Label(setup, collection, inventory)

        raw = label_path.read_bytes()

        if eol_pds4 == '\r\n':
            assert b'\r\n' in raw
        else:
            assert b'\r\n' not in raw
            assert b'\n' in raw

    # ------------------------------------------------------------------
    # setup.add_file side-effect
    # ------------------------------------------------------------------

    def test_add_file_called_with_label_path(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path]
            ) -> None:
        # The generated XML label must be registered relative to staging.
        setup, collection, inventory, _, label_path = env

        InventoryPDS4Label(setup, collection, inventory)

        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)

    # ------------------------------------------------------------------
    # Error and invalid-input integration behaviour
    # ------------------------------------------------------------------

    def test_missing_template_propagates_file_not_found_error(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path]
            ) -> None:
        # Missing inventory templates must fail without registering the label.
        setup, collection, inventory, template_path, label_path = env

        template_path.unlink()

        with pytest.raises(FileNotFoundError):
            InventoryPDS4Label(setup, collection, inventory)

        # The writer opens the output file before the template, so the empty
        # output label is created even though writing fails.
        assert label_path.exists()
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            assert f.read() == ''

        # add_file() was not called.
        setup.add_file.assert_not_called()

    def test_invalid_xml_template_is_written_without_xml_validation(
            self, env: tuple[MagicMock, MagicMock, MagicMock, Path, Path]
            ) -> None:
        # Rendered XML labels are written and registered without XML validation.
        setup, collection, inventory, template_path, label_path = env

        template_path.write_text('<collection>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        InventoryPDS4Label(setup, collection, inventory)

        assert label_path.exists()
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # The known placeholder is rendered even though the XML is malformed.
        assert ('<file_name>collection_spice_kernels_inventory_v001.csv'
                '</file_name>') in written_label
        assert '$FILE_NAME' not in written_label

        # XML parsing fails only when the test validates the generated content.
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written_label)

        # The label is still registered relative to the staging directory.
        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)

    def test_miscellaneous_collection_renders_checksum_coverage(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # End-to-end check of the miscellaneous branch: the rendered coverage
        # must be the checksum min-start / max-stop.
        #
        # NOTE: the physical output file is derived by the inherited writer from
        # inventory.path (NOT from self.name). Here inventory.path ends in
        # '...inventory_v001.csv', so the writer produces
        # '...inventory_v001.xml'. self.name remains 'miscellaneous.xml' purely
        # as label state; the two diverge for this collection.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # collection.type drives the template name; for miscellaneous the type
        # is also 'miscellaneous'.
        template_path = templates_dir / 'template_collection_miscellaneous.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        inventory = helpers.make_inventory(
            staging_dir, name='collection_miscellaneous_inventory_v001.csv',
            n_records=2)
        checksums = [
            helpers.make_checksum_product(
                'checksum_v02.tab', '2024-02-01T00:00:00', '2024-02-28T00:00:00'),
            helpers.make_checksum_product(
                'checksum_v01.tab', '2024-01-01T00:00:00', '2024-01-31T00:00:00')]
        collection = helpers.make_collection(name='miscellaneous',
                                             coll_type='miscellaneous',
                                             products=checksums)

        label = InventoryPDS4Label(setup, collection, inventory)

        # The writer-generated file is derived from inventory.path, stripping
        # the 'inventory_' token: '...miscellaneous_inventory_v001.csv' ->
        # '...miscellaneous_v001.xml'.
        label_path = Path(
            inventory.path.replace('.csv', '.xml').replace('inventory_', ''))
        assert label_path.exists()

        # self.name is the (logical) truncated collection name; for
        # 'miscellaneous' there is no dot, so it is 'miscellaneous.xml'. It is
        # asserted on the constructed instance, not as the physical file.
        assert label.collection.name == 'miscellaneous'

        assert label_path.read_text(encoding='utf-8') == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<collection>\n'
            '  <file_name>collection_miscellaneous_inventory_v001.csv</file_name>\n'
            '  <collection_lid>urn:nasa:pds:maven_spice:spice_kernels</collection_lid>\n'
            '  <collection_vid>1.0</collection_vid>\n'
            '  <start_date_time>2024-01-01T00:00:00</start_date_time>\n'
            '  <stop_date_time>2024-02-28T00:00:00</stop_date_time>\n'
            '  <number_of_records>2</number_of_records>\n'
            '</collection>\n')
