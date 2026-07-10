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
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_checksum import ChecksumPDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------

@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic factories for checksum labels.

        Reuses ``base_helpers.make_setup`` as-is and wraps
        ``base_helpers.make_product`` to set the checksum-specific identity.

        :param base_helpers: generic Setup/base-product factories from conftest
        :return: container with ``make_setup`` and ``make_product`` callables
        """

    def _make_checksum_product(staging_dir: Path,
                               name: str = 'checksum.tab') -> MagicMock:
        # The checksum product lives directly under the staging directory.
        return base_helpers.make_product(path=str(staging_dir / name),
                                         name=name,
                                         lid='urn:nasa:pds:maven_spice:checksum',
                                         collection_name='miscellaneous')

    return SimpleNamespace(make_setup=base_helpers.make_setup,
                           make_product=_make_checksum_product)


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestChecksumPDS4Label:
    """Unit tests for ChecksumPDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path, helpers: SimpleNamespace) -> ChecksumPDS4Label:
        """Build a ChecksumPDS4Label instance while mocking inherited file
         writing."""
        # Create a controlled Setup mock with the PDS4 attributes needed by the
        # label.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked checksum product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build a checksum product mock with the attributes read by
        # ChecksumPDS4Label.
        product = helpers.make_product(staging)

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

    def test_constructor_stores_references_and_writes_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Validate constructor wiring and its single write_label side effect.

        # Build the collaborators required by the label constructor.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked checksum product path.
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Avoid real file writing while checking the constructor side effect.
        with patch("pds.naif_pds4_bundler.classes.label.label."
                   "PDSLabel.write_label", autospec=True) as mock_write:
            label = ChecksumPDS4Label(setup, product)

        # Verify that label.setup is exactly the same setup object that was
        # passed to the constructor, and the same applies to label.product with
        # the product object.
        assert label.setup is setup
        assert label.product is product

        # Check that write_label() was called once and that it was called with
        # the label instance.
        mock_write.assert_called_once_with(label)

    # ------------------------------------------------------------------
    # Edge cases and error paths
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('product_name, expected_file_name, expected_label_name', [
        ('checksum.tab', 'checksum.tab', 'checksum.xml'),
        ('checksum', 'checksum', 'checksum.xml'),
        ('checksum.v01.tab', 'checksum.v01.tab', 'checksum.v01.xml')])
    def test_label_name_is_derived_from_stem(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_name: str, expected_file_name: str,
            expected_label_name: str) -> None:
        # Document how product names are converted into XML label names.

        # Mock the setup so that you can build the label.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock.
        product = helpers.make_product(staging, name=product_name)

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
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attribute: str, value: str,
            label_attribute: str) -> None:
        # Mock a setup with the attributes required to build the label.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Mock a product with valid values by default.
        product = helpers.make_product(staging)

        # Dynamically modify the product attribute
        setattr(product, product_attribute, value)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = ChecksumPDS4Label(setup, product)

        # Check that the expected attribute of the label contains exactly the
        # value assigned to the product.
        assert getattr(label, label_attribute) == value


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
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
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
        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # Build the checksum product whose label will be generated in staging.
        product = helpers.make_product(staging_dir)

        # Return only the objects/paths needed by the integration tests.
        return setup, product, template_path, staging_dir / 'checksum.xml'

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        """Render the checksum XML template and validate the generated label."""
        # Retrieve the objects and paths required by the integration test.
        setup, product, template_path, label_path = env

        # Configure the line-ending for PDS4.
        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        # Instantiate the real label so the template is read and the XML is written.
        label = ChecksumPDS4Label(setup, product)

        # Check that the class resolved the configured checksum template.
        assert label.template == str(template_path)

        # Check that the final checksum.xml file has been created in staging.
        assert label_path.exists()

        # Read the generated label preserving its exact line endings.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # Compare the generated label with the exact expected XML content.
        assert written_label == ('<?xml version="1.0" encoding="UTF-8"?>\n'
                                 '<checksum>\n'
                                 '  <file_name>checksum.tab</file_name>\n'
                                 '  <logical_identifier>'
                                 'urn:nasa:pds:maven_spice:checksum'
                                 '</logical_identifier>\n'
                                 '  <version_id>1.0</version_id>\n'
                                 '  <file_format>Character</file_format>\n'
                                 '  <start_date_time>2024-01-01T00:00:00</start_date_time>\n'
                                 '  <stop_date_time>2024-01-31T23:59:59</stop_date_time>\n'
                                 '</checksum>\n')

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
