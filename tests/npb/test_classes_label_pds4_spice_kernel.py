"""Tests for the SpiceKernelPDS4Label class.

Two test classes are provided:

* TestSpiceKernelPDS4Label – unit tests that mock the inherited label
  writing so the constructor can be exercised in isolation.

* TestSpiceKernelPDS4LabelIntegration – integration tests that exercise
  SpiceKernelPDS4Label together with the real PDSLabel.write_label()
  logic, writing an actual XML label to a temp directory and asserting
  on its contents.
"""
from pathlib import Path
import textwrap
import xml.etree.ElementTree as ElementTree
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_spice_kernel import SpiceKernelPDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------


@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic factories for SPICE kernel labels.

        Reuses ``base_helpers.make_setup`` as-is and wraps
        ``base_helpers.make_product`` to add the SPICE-kernel-specific fields
        (missions/observers/targets, file_format, type, description and
        Z-suffixed coverage) and the on-disk <staging>/<type>/<name> layout.

        :param base_helpers: generic Setup/base-product factories from conftest
        :return: container with ``make_setup`` and ``make_product`` callables
        """

    def _make_spice_kernel_product(staging_dir: Path, name: str = 'maven_orbit_v01.bsp',
                                   kernel_type: str = 'spk') -> MagicMock:
        # The kernel is physically placed under <staging>/<type>/<name>, matching
        # the real Product staging layout consumed by write_label().
        type_dir = staging_dir / kernel_type
        type_dir.mkdir(parents=True, exist_ok=True)

        product = base_helpers.make_product(path=str(type_dir / name),
                                            name=name,
                                            lid=(f'urn:nasa:pds:maven_spice:spice_kernels:'
                                                 f'{kernel_type}_{name}'),
                                            collection_name='spice_kernels')

        # SpiceKernelPDS4Label is a 'kernel' label: missions/observers/targets are
        # taken from the product itself (not from setup), so they must be present.
        product.missions = ['MAVEN']
        product.observers = ['MAVEN']
        product.targets = ['Mars']

        # SPICE-kernel specific fields copied by SpiceKernelPDS4Label.
        product.file_format = 'Binary'
        product.start_time = '2024-01-01T00:00:00Z'
        product.stop_time = '2024-01-31T23:59:59Z'
        product.type = kernel_type
        product.description = 'Orbit reconstruction kernel'

        return product

    return SimpleNamespace(make_setup=base_helpers.make_setup,
                           make_product=_make_spice_kernel_product)


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestSpiceKernelPDS4Label:
    """Unit tests for SpiceKernelPDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> SpiceKernelPDS4Label:
        """Build a SpiceKernelPDS4Label instance while mocking inherited file
        writing.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized SPICE kernel factories
        :return: constructed label with write_label patched out
        """
        # Create a controlled Setup mock with the PDS4 attributes needed by the
        # label.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked kernel product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build a SPICE kernel product mock with the attributes read by
        # SpiceKernelPDS4Label.
        product = helpers.make_product(staging)

        # Avoid real template reading and file writing in unit tests.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            # Instantiate the real class so its constructor assignments are
            # executed.
            instance = SpiceKernelPDS4Label(setup, product)

        return instance

    # ------------------------------------------------------------------
    # Regular tests
    # ------------------------------------------------------------------

    def test_attribute_assignments(self,
                                   label: SpiceKernelPDS4Label) -> None:
        # Validate the PDS4 SPICE-kernel label attributes populated during
        # construction.

        # Check that FILE_NAME has been copied from product.name.
        assert label.FILE_NAME == 'maven_orbit_v01.bsp'

        # Check that the PDS4 logical identifier and the product version have
        # been copied correctly from product.lid and product.vid.
        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:spice_kernels:spk_maven_orbit_v01.bsp')
        assert label.PRODUCT_VID == '1.0'

        # Check that the file format is copied verbatim from product.file_format.
        assert label.FILE_FORMAT == 'Binary'

        # Check that the time coverage is copied from product.start_time and
        # product.stop_time, respectively.
        assert label.START_TIME == '2024-01-01T00:00:00Z'
        assert label.STOP_TIME == '2024-01-31T23:59:59Z'

        # Check that KERNEL_TYPE_ID is the upper-cased product.type.
        assert label.KERNEL_TYPE_ID == 'SPK'

        # Check that the kernel description is copied from product.description.
        assert label.SPICE_KERNEL_DESCRIPTION == 'Orbit reconstruction kernel'

    def test_template_path_is_spice_kernel_template(
            self, label: SpiceKernelPDS4Label) -> None:
        # The label must resolve the SPICE-kernel-specific XML template under
        # the configured templates' directory.
        expected_template = str(
            Path(label.setup.templates_directory)
            / 'template_product_spice_kernel.xml')

        assert label.template == expected_template

    def test_constructor_stores_references_and_writes_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Validate constructor wiring and its single write_label side effect.

        # Build the collaborators required by the label constructor.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked kernel product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Avoid real file writing while checking the constructor side effect.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            label = SpiceKernelPDS4Label(setup, product)

        # Verify that label.setup is exactly the same setup object that was
        # passed to the constructor, and the same applies to label.product with
        # the product object.
        assert label.setup is setup
        assert label.product is product

        # Check that write_label() was called once and that it was called with
        # the label instance.
        mock_write.assert_called_once_with(label)

    @pytest.mark.parametrize('product_type, expected_kernel_type_id', [
        ('spk', 'SPK'),
        ('ck', 'CK'),
        ('SCLK', 'SCLK'),
        ('Fk', 'FK'),
        ('ik', 'IK')])
    def test_kernel_type_id_is_upper_cased(
            self, tmp_path: Path, helpers: SimpleNamespace, product_type: str,
            expected_kernel_type_id: str) -> None:
        # Document that KERNEL_TYPE_ID is always the upper-cased product.type,
        # regardless of the original casing.

        # Mock the setup so that the label can be built.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock with the parametrized kernel type.
        product = helpers.make_product(
            staging, name=f'maven_kernel_v01.{product_type}',
            kernel_type=product_type)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = SpiceKernelPDS4Label(setup, product)

        # The kernel type identifier must be the upper-cased product type.
        assert label.KERNEL_TYPE_ID == expected_kernel_type_id

    @pytest.mark.parametrize(
        'product_attribute, value, label_attribute', [
            ('lid', '', 'PRODUCT_LID'),
            ('vid', 'not-a-valid-version', 'PRODUCT_VID'),
            ('start_time', 'not-a-valid-start-time', 'START_TIME'),
            ('stop_time', '', 'STOP_TIME'),
            ('file_format', 'not-a-real-format', 'FILE_FORMAT'),
            ('name', 'no_extension_name', 'FILE_NAME'),
            ('description', '', 'SPICE_KERNEL_DESCRIPTION')])
    def test_product_values_are_copied_without_validation(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attribute: str, value: str,
            label_attribute: str) -> None:
        # Verify that the constructor copies product values verbatim, without
        # validating or transforming them (except KERNEL_TYPE_ID, covered
        # separately).

        # Mock a setup with the attributes required to build the label.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Mock a product with valid values by default.
        product = helpers.make_product(staging)

        # Dynamically override the product attribute under test.
        setattr(product, product_attribute, value)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = SpiceKernelPDS4Label(setup, product)

        # Check that the expected label attribute contains exactly the value
        # assigned to the product.
        assert getattr(label, label_attribute) == value

    def test_child_overrides_parent_field_assignments(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # The parent PDSLabel.__init__ does not set FILE_NAME/PRODUCT_LID/
        # PRODUCT_VID/START_TIME/STOP_TIME for kernel labels; the child sets
        # them after super().__init__(). This test guards that contract:
        # changing the product values is reflected in the final label state.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Distinctive values to prove the child assignment wins.
        product = helpers.make_product(staging)
        product.lid = 'urn:nasa:pds:maven_spice:spice_kernels:ck_distinct'
        product.vid = '9.9'

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = SpiceKernelPDS4Label(setup, product)

        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:spice_kernels:ck_distinct')
        assert label.PRODUCT_VID == '9.9'

    def test_constructor_raises_when_product_type_is_not_a_string(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # product.type.upper() requires a string; a non-string type must raise
        # because the constructor performs no defensive validation.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Replace the kernel type with a non-string value (no .upper()).
        product.type = 12345

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(AttributeError):
                SpiceKernelPDS4Label(setup, product)


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

TEMPLATE_CONTENT = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <spice_kernel>
      <file_name>$FILE_NAME</file_name>
      <logical_identifier>$PRODUCT_LID</logical_identifier>
      <version_id>$PRODUCT_VID</version_id>
      <file_format>$FILE_FORMAT</file_format>
      <kernel_type>$KERNEL_TYPE_ID</kernel_type>
      <start_date_time>$START_TIME</start_date_time>
      <stop_date_time>$STOP_TIME</stop_date_time>
      <description>$SPICE_KERNEL_DESCRIPTION</description>
    </spice_kernel>
""")


class TestSpiceKernelPDS4LabelIntegration:
    """Integration tests for SpiceKernelPDS4Label + PDSLabel + template."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Create the temporary PDS4 template and staging environment used by
        integration tests.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized SPICE kernel factories
        :return: tuple of (setup, product, template_path, expected_label_path)
        """
        # Create isolated directories for the template input and label output.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # Write the SPICE kernel XML template consumed by PDSLabel.write_label().
        template_path = templates_dir / 'template_product_spice_kernel.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        # Build the setup mock and point it to the temporary integration folders.
        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # Build the SPICE kernel product whose label will be generated in
        # staging. The physical kernel lives under <staging>/spk/<name>.
        product = helpers.make_product(staging_dir)

        # The inherited writer derives the XML label path from product.path by
        # replacing the ``.<extension>`` suffix with ``.xml``.
        expected_label_path = (staging_dir / 'spk'
                               / 'maven_orbit_v01.xml')

        # Return only the objects/paths needed by the integration tests.
        return setup, product, template_path, expected_label_path

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Render the SPICE kernel XML template and validate the generated label.

        # Retrieve the objects and paths required by the integration test.
        setup, product, template_path, label_path = env

        # Configure the line-ending for PDS4.
        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        # Instantiate the real label so the template is read and the XML is
        # written.
        label = SpiceKernelPDS4Label(setup, product)

        # Check that the class resolved the configured SPICE kernel template.
        assert label.template == str(template_path)

        # The real writer mutates label.name to the generated XML file path.
        assert Path(label.name) == label_path

        # Check that the final XML file has been created in staging.
        assert label_path.exists()

        # Read the generated label preserving its exact line endings.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # Compare the generated label with the exact expected XML content.
        assert written_label == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<spice_kernel>\n'
            '  <file_name>maven_orbit_v01.bsp</file_name>\n'
            '  <logical_identifier>'
            'urn:nasa:pds:maven_spice:spice_kernels:spk_maven_orbit_v01.bsp'
            '</logical_identifier>\n'
            '  <version_id>1.0</version_id>\n'
            '  <file_format>Binary</file_format>\n'
            '  <kernel_type>SPK</kernel_type>\n'
            '  <start_date_time>2024-01-01T00:00:00Z</start_date_time>\n'
            '  <stop_date_time>2024-01-31T23:59:59Z</stop_date_time>\n'
            '  <description>Orbit reconstruction kernel</description>\n'
            '</spice_kernel>\n')

    def test_label_file_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # The rendered label must be well-formed XML with all placeholders
        # substituted by the label state.
        setup, product, _, label_path = env

        SpiceKernelPDS4Label(setup, product)

        # Parse the rendered label; a malformed result would raise ParseError.
        tree = ElementTree.parse(label_path)
        root = tree.getroot()

        assert root.tag == 'spice_kernel'
        assert root.findtext('file_name') == 'maven_orbit_v01.bsp'
        assert root.findtext('kernel_type') == 'SPK'

        # No unresolved template placeholders must remain.
        assert '$' not in label_path.read_text(encoding='utf-8')

    @pytest.mark.parametrize('end_of_line, eol_pds4', [
        ('LF', '\n'),
        ('CRLF', '\r\n')])
    def test_label_respects_configured_end_of_line(
            self, env: tuple[MagicMock, MagicMock, Path, Path],
            end_of_line: str, eol_pds4: str) -> None:
        # The inherited writer must honour the configured PDS4 end-of-line
        # sequence when writing the label.
        setup, product, _, label_path = env

        setup.end_of_line = end_of_line
        setup.eol_pds4 = eol_pds4

        SpiceKernelPDS4Label(setup, product)

        # Read the raw bytes to inspect the actual line terminators.
        raw = label_path.read_bytes()

        if eol_pds4 == '\r\n':
            # Every line must terminate with CRLF.
            assert b'\r\n' in raw
        else:
            # No CR must be present for a pure LF configuration.
            assert b'\r\n' not in raw
            assert b'\n' in raw

    # ------------------------------------------------------------------
    # setup.add_file side-effect
    # ------------------------------------------------------------------

    def test_add_file_called_with_label_path(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Register the generated XML label using its staging-relative path.

        # Only setup and product are needed to trigger the real label
        # generation.
        setup, product, _, label_path = env

        # Generate the label using the real writer.
        SpiceKernelPDS4Label(setup, product)

        # The generated label must be registered relative to staging, not
        # absolute.
        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)

    # ------------------------------------------------------------------
    # Error and invalid-input integration behaviour
    # ------------------------------------------------------------------

    def test_missing_template_propagates_file_not_found_error(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Missing SPICE kernel templates must fail without registering the label.

        # Retrieve the integration objects and paths prepared by the fixture.
        setup, product, template_path, label_path = env

        # Physically delete the XML template created by the fixture.
        template_path.unlink()

        # Capture the exception.
        with pytest.raises(FileNotFoundError):
            SpiceKernelPDS4Label(setup, product)

        # The writer opens the output file before the template, so the empty
        # output label is created even though writing fails.
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
        template_path.write_text('<spice_kernel>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        SpiceKernelPDS4Label(setup, product)

        # The writer still creates the output label.
        assert label_path.exists()

        # Read the generated malformed XML label.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # The known placeholder is rendered even though the XML is malformed.
        assert '<file_name>maven_orbit_v01.bsp</file_name>' in written_label
        assert '$FILE_NAME' not in written_label

        # XML parsing fails only when the test validates the generated content.
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written_label)

        # Because this layer does not validate XML, the label is still
        # registered relative to the staging directory.
        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)
