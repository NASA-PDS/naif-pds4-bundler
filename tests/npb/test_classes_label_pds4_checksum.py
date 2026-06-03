"""Tests for the ChecksumPDS4Label class.

Two test classes are provided:

* TestChecksumPDS4Label – unit tests that mock label writing so the
  constructor can be tested in isolation.

* TestChecksumPDS4LabelIntegration – integration tests that exercise
  ChecksumPDS4Label together with the real PDSLabel.write_label() logic,
  writing an actual XML label to a temp directory and asserting on its
  contents.
"""
from pathlib import Path
import textwrap
import xml.etree.ElementTree as ElementTree
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_checksum import ChecksumPDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------

def _make_setup(tmp_path: Path, end_of_line: str = 'LF',
                eol_pds4: str = "\n") -> MagicMock:
    """Return a fully-configured mock Setup object for PDS4 usage."""
    setup = MagicMock()

    # Basic execution context expected by the label hierarchy.
    setup.pds_version = '4'
    setup.volume_id = 'maven_0001'
    setup.mission_acronym = 'maven'
    setup.mission_name = 'MAVEN'
    setup.observer = 'MAVEN'
    setup.target = 'Mars'

    # Secondary context values are empty because these tests only need the
    # primary mission, observer and target metadata.
    setup.secondary_missions = []
    setup.secondary_observers = []
    setup.secondary_targets = []

    # Temporary project directories used by the label writer.
    setup.root_dir = str(tmp_path)
    setup.templates_directory = str(tmp_path / 'templates')
    setup.staging_directory = str(tmp_path / 'staging')
    setup.working_directory = str(tmp_path / 'work')
    setup.bundle_directory = str(tmp_path / 'bundle')

    # Disable unrelated diff/compare behaviour during label generation.
    setup.diff = False

    # PDS4 XML metadata that may be consumed by PDSLabel or template rendering.
    setup.xml_model = 'https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1F00.sch'
    setup.schema_location = 'https://pds.nasa.gov/pds4/pds/v1 PDS4_PDS_1F00.xsd'

    setup.information_model = '1.16.0.0'
    setup.information_model_float = 1016000000.0
    setup.logical_identifier = 'urn:nasa:pds:maven_spice'

    # End-of-line configuration used when writing PDS4 XML labels.
    setup.end_of_line = end_of_line
    setup.eol_pds4 = eol_pds4

    # XML indentation configuration expected by the inherited writer.
    setup.xml_tab = 1

    # Simulate CLI flags used by the writer without invoking the real parser.
    setup.args = MagicMock()
    setup.args.silent = True
    setup.args.verbose = False

    # Mock side effect so tests can assert the generated label was registered.
    setup.add_file = MagicMock()

    return setup


def _make_product(staging_dir: Path, name: str = 'checksum.tab') -> MagicMock:
    """Build a realistic Checksum product mock with the attributes used by
    label writing."""

    # Context products may be consumed by inherited PDS4 label logic.
    context_products = [
        {'name': ['MAVEN'],
         'type': ['Mission'],
         'lidvid': 'urn:nasa:pds:context:investigation:mission.maven::1.0'},
        {'name': ['MAVEN'],
         'type': ['Spacecraft'],
         'lidvid': ('urn:nasa:pds:context:instrument_host:'
                    'spacecraft.maven::1.0')},
        {'name': ['Mars'],
         'type': ['Planet'],
         'lidvid': 'urn:nasa:pds:context:target:planet.mars::1.0'}]

    product = MagicMock()

    # Physical checksum file metadata used directly by ChecksumPDS4Label.
    product.name = name
    product.extension = name.rsplit('.', 1)[-1] if '.' in name else ''
    product.path = str(staging_dir / name)

    # PDS4 product identifiers copied by ChecksumPDS4Label.
    product.lid = 'urn:nasa:pds:maven_spice:checksum'
    product.vid = '1.0'

    # Temporal coverage copied by ChecksumPDS4Label.
    product.start_time = '2024-01-01T00:00:00'
    product.stop_time = '2024-01-31T23:59:59'

    # Creation metadata may be consumed by the inherited PDSLabel writer.
    product.creation_time = '2024-02-01T12:00:00'
    product.creation_date = '2024-02-01'

    # File metadata commonly substituted in PDS4 templates.
    product.size = '2048'
    product.checksum = 'd41d8cd98f00b204e9800998ecf8427e'

    # Collection/bundle context expected by some inherited PDS4 logic.
    product.collection.name = 'miscellaneous'
    product.collection.bundle.context_products = context_products
    product.bundle.context_products = context_products

    return product


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestChecksumPDS4Label:
    """Unit tests for ChecksumPDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path) -> ChecksumPDS4Label:
        """Build a ChecksumPDS4Label instance while mocking inherited file
         writing."""
        # Create a controlled Setup mock with the PDS4 attributes needed by the
        # label.
        setup = _make_setup(tmp_path)

        # Create the staging directory used by the mocked checksum product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build a checksum product mock with the attributes read by
        # ChecksumPDS4Label.
        product = _make_product(staging)

        # Avoid real template reading and file writing in unit tests.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            # Instantiate the real class so its constructor assignments are
            # executed.
            instance = ChecksumPDS4Label(setup, product)

        return instance

    # ------------------------------------------------------------------
    # Regular tests
    # ------------------------------------------------------------------

    def test_attribute_assignments(self, label: ChecksumPDS4Label) -> None:
        # Validate the PDS4 checksum label attributes populated during
        # construction.

        # Check that FILE_NAME has been copied from product.name.
        assert label.FILE_NAME == 'checksum.tab'

        # Check that the PDS4 logical identifier and the product version have
        # been copied correctly from product.lid.
        assert label.PRODUCT_LID == 'urn:nasa:pds:maven_spice:checksum'
        assert label.PRODUCT_VID == '1.0'

        # Check a fixed value defined by ChecksumPDS4Label.
        assert label.FILE_FORMAT == 'Character'

        # Verifies that the start and end times of the time coverage are copied
        # from product.start_time and product.stop_time, respectively.
        assert label.START_TIME == '2024-01-01T00:00:00'
        assert label.STOP_TIME == '2024-01-31T23:59:59'

        # Check that the XML label name is derived correctly from the product
        # name.
        assert label.name == 'checksum.xml'

    def test_setup_and_product_reference_stored(self, tmp_path: Path) -> None:
        # Validate that the inherited constructor stores setup and product on
        # the label.

        # Build the Setup mock that will be passed to the label constructor.
        setup = _make_setup(tmp_path)

        # Build the temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock that will be passed to the label constructor.
        product = _make_product(staging)

        # Patch PDSLabel.write_label() to prevent actual file writing during
        # this unit test.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = ChecksumPDS4Label(setup, product)

        # Check that label.setup points to the same setup object that was passed
        # to the constructor.
        assert label.setup == setup

        # Check that label.product points to the same product object that was
        # passed to the constructor.
        assert label.product == product

    def test_write_label_called_once_during_init(self, tmp_path: Path) -> None:
        # Validate that creating a PDS4 checksum label invokes the inherited
        # writer once.

        # Build the Setup mock with the needed attributes to instance
        # ChecksumPDS4Label.
        setup = _make_setup(tmp_path)

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock.
        product = _make_product(staging)

        # Patch PDSLabel.write_label function to prevent the files from actually
        # being written and to be able to count how many times write_label() has
        # been called.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            label = ChecksumPDS4Label(setup, product)

        # Check that write_label() was called exactly once, and it was called on
        # the specific label instance.
        mock_write.assert_called_once_with(label)

    # ------------------------------------------------------------------
    # Edge cases and error paths
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('product_name, expected_file_name, expected_label_name', [
        ('checksum.tab', 'checksum.tab', 'checksum.xml'),
        ('checksum', 'checksum', 'checksum.xml'),
        ('checksum.v01.tab', 'checksum.v01.tab', 'checksum.xml')])
    def test_label_name_is_derived_from_text_before_first_dot(
            self, tmp_path: Path, product_name: str, expected_file_name: str,
            expected_label_name: str) -> None:
        # Document how product names are converted into XML label names.

        # Mock the setup so that you can build the label.
        setup = _make_setup(tmp_path)

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock.
        product = _make_product(staging, name=product_name)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = ChecksumPDS4Label(setup, product)

        # Check that FILE_NAME exactly matches the original product name.
        assert label.FILE_NAME == expected_file_name

        # Check the name of the generated XML tag.
        assert label.name == expected_label_name

    @pytest.mark.parametrize('product_attribute, value, label_attribute', [
        ('lid', '', 'PRODUCT_LID'),
        ('vid', 'not-a-valid-version', 'PRODUCT_VID'),
        ('start_time', 'not-a-valid-start-time', 'START_TIME'),
        ('stop_time', '', 'STOP_TIME')])
    def test_product_values_are_copied_without_validation(
            self, tmp_path: Path, product_attribute: str, value: str,
            label_attribute: str) -> None:
        # Mock a setup with the attributes required to build the label.
        setup = _make_setup(tmp_path)

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Mock a product with valid values by default.
        product = _make_product(staging)

        # Dynamically modify the product attribute
        setattr(product, product_attribute, value)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = ChecksumPDS4Label(setup, product)

        # Check that the expected attribute of the label contains exactly the
        # value assigned to the product.
        assert getattr(label, label_attribute) == value

    def test_write_label_errors_are_propagated(self, tmp_path: Path) -> None:
        # Mock setup with the attributes required to build the label.
        setup = _make_setup(tmp_path)

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Mock the product.
        product = _make_product(staging)

        # Patch PDSLabel.write_label to simulate a write failure.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True,
                   side_effect=RuntimeError('write failed')) as mock_write:
            # Capture the exception.
            with pytest.raises(RuntimeError, match='write failed'):
                ChecksumPDS4Label(setup, product)

        # Check that write_label() called once.
        mock_write.assert_called_once()

    @pytest.mark.parametrize('missing_owner, missing_attribute', [
        ('setup', 'templates_directory'),
        ('product', 'name'),
        ('product', 'lid'),
        ('product', 'vid'),
        ('product', 'start_time'),
        ('product', 'stop_time')])
    def test_missing_constructor_dependency_raises_attribute_error(
            self, tmp_path: Path, missing_owner, missing_attribute) -> None:
        # Verify that missing setup/product attributes fail during construction
        # before the label writer is invoked.

        # Mock a valid setup.
        setup = _make_setup(tmp_path)

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Mock a valid product.
        product = _make_product(staging)

        # Remove the required dependency selected by the parametrized case.
        target = setup if missing_owner == 'setup' else product
        delattr(target, missing_attribute)

        # Patch the PDSLabel.write_label.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            # Capture the exception and check the error message.
            with pytest.raises(AttributeError, match=missing_attribute):
                ChecksumPDS4Label(setup, product)

        # Check that write_label() was not called.
        mock_write.assert_not_called()


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

TEMPLATE_CONTENT = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <checksum>
      <file_name>$FILE_NAME</file_name>
      <logical_identifier>$PRODUCT_LID</logical_identifier>
      <version_id>$PRODUCT_VID</version_id>
      <file_format>$FILE_FORMAT</file_format>
      <start_date_time>$START_TIME</start_date_time>
      <stop_date_time>$STOP_TIME</stop_date_time>
    </checksum>
""")


class TestChecksumPDS4LabelIntegration:
    """Integration tests for ChecksumPDS4Label + PDSLabel + template."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Create the temporary PDS4 template and staging environment used by
         integration tests."""

        # Create isolated directories for the template input and label output.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # Write the checksum XML template consumed by PDSLabel.write_label().
        template_path = templates_dir / 'template_product_checksum_table.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        # Build the setup mock and point it to the temporary integration folders.
        setup = _make_setup(tmp_path)
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # Build the checksum product whose label will be generated in staging.
        product = _make_product(staging_dir)

        # Return only the objects/paths needed by the integration tests.
        return setup, product, template_path, staging_dir / 'checksum.xml'

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('end_of_line, eol_pds4', [
        ('LF', '\n'), ('CRLF', '\r\n')])
    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path],
            end_of_line: str, eol_pds4: str) -> None:
        """Render the checksum XML template and validate the generated label."""
        # Retrieve the objects and paths required by the integration test.
        setup, product, template_path, label_path = env

        # Configure the line-ending variant covered by this parametrized case.
        setup.end_of_line = end_of_line
        setup.eol_pds4 = eol_pds4

        # Instantiate the real label so the template is read and the XML is written.
        label = ChecksumPDS4Label(setup, product)

        # Check that the class resolved the configured checksum template.
        assert label.template == str(template_path)

        # Check that the final checksum.xml file was created in staging.
        assert label_path.exists()

        # Read raw bytes to validate LF/CRLF without newline normalization.
        raw_label = label_path.read_bytes()

        # Check that the generated file uses the configured line separator.
        if eol_pds4 == '\n':
            assert b'\r' not in raw_label
        else:
            assert b'\r\n' in raw_label
            assert b'\n' not in raw_label.replace(b'\r\n', b'')
            assert b'\r' not in raw_label.replace(b'\r\n', b'')

        written_label = raw_label.decode('utf-8')

        # Check that every placeholder from the test template was replaced.
        assert '$' not in written_label

        # Parse the generated XML to validate behaviour instead of exact formatting.
        root = ElementTree.fromstring(written_label)

        # Validate the XML values rendered from ChecksumPDS4Label metadata.
        expected_values = {
            'file_name': product.name,
            'logical_identifier': product.lid,
            'version_id': product.vid,
            'file_format': 'Character',
            'start_date_time': product.start_time,
            'stop_date_time': product.stop_time,
        }

        for tag_name, expected_value in expected_values.items():
            assert root.findtext(tag_name) == expected_value

    # ------------------------------------------------------------------
    # setup.add_file side-effect
    # ------------------------------------------------------------------

    def test_add_file_called_with_label_path(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Register the generated XML label using its staging-relative path.

        # Only setup and product are needed to trigger the real label
        # generation.
        setup, product, _, _ = env

        # Generate the label using the real writer.
        ChecksumPDS4Label(setup, product)

        # The generated label must be registered relative to staging, not
        # absolute.
        setup.add_file.assert_called_once_with('checksum.xml')

    # ------------------------------------------------------------------
    # Error and invalid-input integration behaviour
    # ------------------------------------------------------------------

    def test_missing_template_propagates_file_not_found_error(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Missing checksum templates must fail without registering the label.

        # Retrieve the integration objects and paths prepared by the fixture.
        setup, product, template_path, label_path = env

        # Physically delete the XML template created by the fixture.
        template_path.unlink()

        # Capture the exception.
        with pytest.raises(FileNotFoundError):
            ChecksumPDS4Label(setup, product)

        # Check that the output file has been created.
        assert label_path.exists()

        # Check that the created file is empty.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            assert f.read() == ''

        # Check that setup.add_file() was not called.
        setup.add_file.assert_not_called()

    def test_invalid_xml_template_is_written_without_xml_validation(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Rendered XML labels are written and registered without XML validation.

        # Retrieve the integration objects and paths prepared by the fixture.
        setup, product, template_path, label_path = env

        # Replace the valid template with malformed XML that still has a valid
        # placeholder to render.
        template_path.write_text('<checksum>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        ChecksumPDS4Label(setup, product)

        # The writer still creates the output label.
        assert label_path.exists()

        # Read the generated malformed XML label.
        with open(label_path, 'rt', encoding='utf-8', newline="") as f:
            written_label = f.read()

        # The known placeholder is rendered even though the XML is malformed.
        assert '<file_name>checksum.tab</file_name>' in written_label
        assert '$FILE_NAME' not in written_label

        # XML parsing fails only when the test validates the generated content.
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written_label)

        # Because this layer does not validate XML, the label is still registered.
        setup.add_file.assert_called_once_with('checksum.xml')
