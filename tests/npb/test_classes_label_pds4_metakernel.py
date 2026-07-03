"""Tests for the MetaKernelPDS4Label class.

Two test classes are provided:

* TestMetaKernelPDS4Label – unit tests that mock the inherited label
  writing so the constructor and ``get_kernel_internal_references`` can be
  exercised in isolation.

* TestMetaKernelPDS4LabelIntegration – integration tests that exercise
  MetaKernelPDS4Label together with the real PDSLabel.write_label() logic,
  writing an actual XML label to a temp directory and asserting on its
  contents.

The MK label is a 'kernel' label: the parent PDSLabel.__init__ does NOT set
FILE_NAME / PRODUCT_LID / PRODUCT_VID / START_TIME / STOP_TIME; the child sets
them after super().__init__(). All product values are copied verbatim, without
validation (except KERNEL_TYPE_ID, which is upper-cased).
"""
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_metakernel import MetaKernelPDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------

@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic factories for meta-kernel (MK) labels.

    Reuses ``base_helpers.make_setup`` as-is and wraps
    ``base_helpers.make_product`` to add the MK-specific fields (file_format
    is fixed to 'Character' by the label itself, but type, description and the
    ``collection_metakernel`` list of kernel names are taken from the product)
    and the on-disk <staging>/mk/<name> layout used by the inherited writer.

    :param base_helpers: generic Setup/base-product factories from conftest
    :return: container with ``make_setup`` and ``make_product`` callables
    """

    def _make_metakernel_product(
            staging_dir: Path,
            name: str = 'maven_v01.tm',
            collection_metakernel: list[str] | None = None) -> MagicMock:
        # The meta-kernel is physically placed under <staging>/mk/<name>,
        # matching the real Product staging layout consumed by write_label().
        type_dir = staging_dir / 'mk'
        type_dir.mkdir(parents=True, exist_ok=True)

        product = base_helpers.make_product(
            path=str(type_dir / name),
            name=name,
            lid='urn:nasa:pds:maven_spice:spice_kernels:mk_' + name,
            collection_name='spice_kernels')

        # MK is a 'kernel' label: PDSLabel.__init__ reads missions/observers/
        # targets from the product itself (not from setup), so they must be
        # real lists whose values match the CONTEXT_PRODUCTS entries used by
        # get_missions() / get_observers() / get_targets().
        product.missions = ['MAVEN']
        product.observers = ['MAVEN']
        product.targets = ['Mars']

        # MK-specific fields copied by MetaKernelPDS4Label.
        product.start_time = '2024-01-01T00:00:00Z'
        product.stop_time = '2024-01-31T23:59:59Z'
        product.type = 'mk'
        product.description = 'MAVEN SPICE meta-kernel'

        # The list of kernels referenced by the MK. They are plain strings,
        # NOT objects: extension_to_type() and ``.lower()`` operate on them.
        if collection_metakernel is None:
            collection_metakernel = ['naif0012.tls', 'maven_orbit_v01.bsp']
        product.collection_metakernel = collection_metakernel

        return product

    return SimpleNamespace(make_setup=base_helpers.make_setup,
                           make_product=_make_metakernel_product)


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestMetaKernelPDS4Label:
    """Unit tests for MetaKernelPDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> MetaKernelPDS4Label:
        """Build a MetaKernelPDS4Label instance while mocking inherited file
        writing.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized MK factories
        :return: constructed label with write_label patched out
        """
        # Create a controlled Setup mock with the PDS4 attributes needed by the
        # label.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked MK product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build an MK product mock with the attributes read by
        # MetaKernelPDS4Label.
        product = helpers.make_product(staging)

        # Avoid real template reading and file writing in unit tests.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            # Instantiate the real class so its constructor assignments are
            # executed.
            instance = MetaKernelPDS4Label(setup, product)

        return instance

    # ------------------------------------------------------------------
    # Regular tests
    # ------------------------------------------------------------------

    def test_attribute_assignments(self, label: MetaKernelPDS4Label) -> None:
        # Validate the PDS4 MK label attributes populated during construction.

        # Check that FILE_NAME has been copied from product.name.
        assert label.FILE_NAME == 'maven_v01.tm'

        # Check that the PDS4 logical identifier and the product version have
        # been copied correctly from product.lid and product.vid.
        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:spice_kernels:mk_maven_v01.tm')
        assert label.PRODUCT_VID == '1.0'

        # Check the fixed value defined by MetaKernelPDS4Label.
        assert label.FILE_FORMAT == 'Character'

        # Check that the time coverage is copied from product.start_time and
        # product.stop_time, respectively.
        assert label.START_TIME == '2024-01-01T00:00:00Z'
        assert label.STOP_TIME == '2024-01-31T23:59:59Z'

        # Check that KERNEL_TYPE_ID is the upper-cased product.type.
        assert label.KERNEL_TYPE_ID == 'MK'

        # Check that the kernel description is copied from product.description.
        assert label.SPICE_KERNEL_DESCRIPTION == 'MAVEN SPICE meta-kernel'

        # Check that the XML label name is derived from the product name.
        assert label.name == 'maven_v01.xml'

    def test_template_path_is_metakernel_template(
            self, label: MetaKernelPDS4Label) -> None:
        # The label must resolve the MK-specific XML template under the
        # configured templates' directory.
        expected_template = str(
            Path(label.setup.templates_directory)
            / 'template_product_spice_kernel_mk.xml')

        assert label.template == expected_template

    def test_constructor_stores_references_and_writes_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Validate constructor wiring and its single write_label side effect.

        # Build the collaborators required by the label constructor.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked MK product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Avoid real file writing while checking the constructor side effect.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            label = MetaKernelPDS4Label(setup, product)

        # Verify that label.setup is exactly the same setup object that was
        # passed to the constructor, and the same applies to label.product with
        # the product object.
        assert label.setup is setup
        assert label.product is product

        # Check that write_label() was called once and that it was called with
        # the label instance.
        mock_write.assert_called_once_with(label)

    @pytest.mark.parametrize('product_type, expected_kernel_type_id', [
        ('mk', 'MK'),
        ('MK', 'MK'),
        ('Mk', 'MK')])
    def test_kernel_type_id_is_upper_cased(
            self, tmp_path: Path, helpers: SimpleNamespace, product_type: str,
            expected_kernel_type_id: str) -> None:
        # Document that KERNEL_TYPE_ID is always the upper-cased product.type,
        # regardless of the original casing. Note the label copies product.type
        # verbatim (upper-cased); it does not re-derive it from the extension.

        # Mock the setup so that the label can be built.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock and override its type.
        product = helpers.make_product(staging)
        product.type = product_type

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        # The kernel type identifier must be the upper-cased product type.
        assert label.KERNEL_TYPE_ID == expected_kernel_type_id

    @pytest.mark.parametrize('product_attribute, value, label_attribute', [
        ('lid', '', 'PRODUCT_LID'),
        ('vid', 'not-a-valid-version', 'PRODUCT_VID'),
        ('start_time', 'not-a-valid-start-time', 'START_TIME'),
        ('stop_time', '', 'STOP_TIME'),
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
            label = MetaKernelPDS4Label(setup, product)

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
        product.lid = 'urn:nasa:pds:maven_spice:spice_kernels:mk_distinct'
        product.vid = '9.9'

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:spice_kernels:mk_distinct')
        assert label.PRODUCT_VID == '9.9'

    @pytest.mark.parametrize('product_name, expected_label_name', [
        ('maven_v01.tm', 'maven_v01.xml'),
        ('maven', 'maven.xml'),
        # TODO: BUG; product.name.split(".")[0] truncates at the FIRST dot, so
        #       a legitimate multi-dot name loses everything after it.
        ('maven_v01.0.tm', 'maven_v01.xml')])
    def test_label_name_is_derived_from_text_before_first_dot(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_name: str, expected_label_name: str) -> None:
        # Document how product names are converted into XML label names. The
        # last case proves the truncation bug shared with the other PDS4
        # labels.

        # Mock the setup so that the label can be built.
        setup = helpers.make_setup()

        # Build a temporal staging directory.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock with the parametrized name.
        product = helpers.make_product(staging, name=product_name)

        # Patch PDSLabel.write_label() to prevent actual file writing.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        # FILE_NAME is the verbatim product name (no truncation there).
        assert label.FILE_NAME == product_name

        # The XML label name is the truncated-at-first-dot value.
        assert label.name == expected_label_name

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
                MetaKernelPDS4Label(setup, product)

    # ------------------------------------------------------------------
    # get_kernel_internal_references – the MK-specific logic
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('collection_metakernel, expected_lids, expected', [
        (['naif0012.tls'], [('lsk', 'naif0012.tls')],
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'),
        (['naif0012.tls', 'maven_orbit_v01.bsp', 'maven_sclk_v02.tsc'],
         [('lsk', 'naif0012.tls'),
          ('spk', 'maven_orbit_v01.bsp'),
          ('sclk', 'maven_sclk_v02.tsc')],
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'spk_maven_orbit_v01.bsp</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'sclk_maven_sclk_v02.tsc</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'),
        (['MAVEN_Frames_V01.TF'],
         [('fk', 'maven_frames_v01.tf')],
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'fk_maven_frames_v01.tf</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n')])
    def test_get_kernel_internal_references_builds_expected_block(
            self, tmp_path: Path, helpers: SimpleNamespace,
            collection_metakernel: list[str],
            expected_lids: list[tuple[str, str]],
            expected: str) -> None:
        # Verify that the internal-references block is built from
        # collection_metakernel, one <Internal_Reference> per kernel, preserving
        # insertion order, lower-casing the kernel name in the LID, and using
        # extension_to_type to resolve the kernel type.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, collection_metakernel=collection_metakernel)

        # write_label is mocked: the attribute is computed during __init__ and
        # we assert on the stored value.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        assert label.KERNEL_INTERNAL_REFERENCES == expected

    @pytest.mark.parametrize('xml_tab, expected', [
        (1,
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'),
        (2,
         '    <Internal_Reference>\n'
         '      <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '      <reference_type>data_to_associate</reference_type>\n'
         '    </Internal_Reference>\n'),
        (4,
         '        <Internal_Reference>\n'
         '            <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '            <reference_type>data_to_associate</reference_type>\n'
         '        </Internal_Reference>\n')])
    def test_get_kernel_internal_references_honours_xml_tab(
            self, tmp_path: Path, helpers: SimpleNamespace,
            xml_tab: int, expected: str) -> None:
        # The indentation of the generated block must scale with setup.xml_tab:
        # 2*tab spaces for <Internal_Reference> and 3*tab spaces for its
        # children.

        setup = helpers.make_setup()
        setup.xml_tab = xml_tab

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, collection_metakernel=['naif0012.tls'])

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        assert label.KERNEL_INTERNAL_REFERENCES == expected

        # Explicitly assert the leading indentation widths to make the contract
        # unambiguous.
        first_line = label.KERNEL_INTERNAL_REFERENCES.split(setup.eol_pds4)[0]
        assert first_line == f"{' ' * 2 * xml_tab}<Internal_Reference>"

    @pytest.mark.parametrize('eol_pds4, expected', [
        ('\n',
         '  <Internal_Reference>\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\n'
         '   <reference_type>data_to_associate</reference_type>\n'
         '  </Internal_Reference>\n'),
        ('\r\n',
         '  <Internal_Reference>\r\n'
         '   <lid_reference>urn:nasa:pds:maven_spice:spice_kernels:'
         'lsk_naif0012.tls</lid_reference>\r\n'
         '   <reference_type>data_to_associate</reference_type>\r\n'
         '  </Internal_Reference>\r\n')])
    def test_get_kernel_internal_references_honours_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace,
            eol_pds4: str, expected: str) -> None:
        # The configured PDS4 end-of-line sequence must be used as the line
        # terminator inside the generated block (and for the trailing EOL).

        setup = helpers.make_setup(eol_pds4=eol_pds4)

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, collection_metakernel=['naif0012.tls'])

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        assert label.KERNEL_INTERNAL_REFERENCES == expected
        assert label.KERNEL_INTERNAL_REFERENCES.endswith(eol_pds4)

    def test_get_kernel_internal_references_empty_collection_returns_only_eol(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # TODO: BUG; with an empty collection_metakernel the method returns just
        #       the EOL string ("".rstrip() + eol == eol) instead of an empty
        #       string. A label rendered with this value gets a stray blank line
        #       in the internal-references section.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging, collection_metakernel=[])

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = MetaKernelPDS4Label(setup, product)

        # Documents the current (buggy) behaviour.
        assert label.KERNEL_INTERNAL_REFERENCES == setup.eol_pds4

    def test_get_kernel_internal_references_raises_value_error_for_unknown_extension(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # An unrecognised kernel extension fails fast with a descriptive
        # ValueError instead of an unhandled KeyError from extension_to_type().
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, collection_metakernel=['unexpected_file.txt'])

        expected_message = (
            "Unsupported kernel extension 'TXT' for kernel "
            "unexpected_file.txt: not present in the SPICE kernel type "
            "map.")

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(ValueError, match=expected_message):
                MetaKernelPDS4Label(setup, product)


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

TEMPLATE_CONTENT = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<spice_kernel_mk>\n'
    '  <file_name>$FILE_NAME</file_name>\n'
    '  <logical_identifier>$PRODUCT_LID</logical_identifier>\n'
    '  <version_id>$PRODUCT_VID</version_id>\n'
    '  <file_format>$FILE_FORMAT</file_format>\n'
    '  <kernel_type>$KERNEL_TYPE_ID</kernel_type>\n'
    '  <start_date_time>$START_TIME</start_date_time>\n'
    '  <stop_date_time>$STOP_TIME</stop_date_time>\n'
    '  <description>$SPICE_KERNEL_DESCRIPTION</description>\n'
    '</spice_kernel_mk>\n')


class TestMetaKernelPDS4LabelIntegration:
    """Integration tests for MetaKernelPDS4Label + PDSLabel + template."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Create the temporary PDS4 template and staging environment used by
        integration tests.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized MK factories
        :return: tuple of (setup, product, template_path, expected_label_path)
        """
        # Create isolated directories for the template input and label output.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # Write the MK XML template consumed by PDSLabel.write_label().
        template_path = templates_dir / 'template_product_spice_kernel_mk.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        # Build the setup mock and point it to the temporary integration folders.
        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # Build the MK product whose label will be generated in staging. The
        # physical meta-kernel lives under <staging>/mk/<name>.
        product = helpers.make_product(staging_dir)

        # The inherited writer derives the XML label path from product.path by
        # replacing the ``.<extension>`` suffix with ``.xml``.
        expected_label_path = staging_dir / 'mk' / 'maven_v01.xml'

        # Return only the objects/paths needed by the integration tests.
        return setup, product, template_path, expected_label_path

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Render the MK XML template and validate the generated label.

        # Retrieve the objects and paths required by the integration test.
        setup, product, template_path, label_path = env

        # Configure the line-ending for PDS4.
        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        # Instantiate the real label so the template is read and the XML is
        # written.
        label = MetaKernelPDS4Label(setup, product)

        # Check that the class resolved the configured MK template.
        assert label.template == str(template_path)

        # The real writer mutates label.name to the generated XML file path.
        assert Path(label.name) == label_path

        # Check that the final XML file has been created in staging.
        assert label_path.exists()

        # Compare the generated label with the exact expected content.
        # The template only contains scalar placeholders so each line maps
        # directly to a single substitution — no EOL ambiguity.
        assert label_path.read_text(encoding='utf-8') == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<spice_kernel_mk>\n'
            '  <file_name>maven_v01.tm</file_name>\n'
            '  <logical_identifier>'
            'urn:nasa:pds:maven_spice:spice_kernels:mk_maven_v01.tm'
            '</logical_identifier>\n'
            '  <version_id>1.0</version_id>\n'
            '  <file_format>Character</file_format>\n'
            '  <kernel_type>MK</kernel_type>\n'
            '  <start_date_time>2024-01-01T00:00:00Z</start_date_time>\n'
            '  <stop_date_time>2024-01-31T23:59:59Z</stop_date_time>\n'
            '  <description>MAVEN SPICE meta-kernel</description>\n'
            '</spice_kernel_mk>\n')

    def test_label_file_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # The rendered label must be well-formed XML with all placeholders
        # substituted by the label state.
        setup, product, _, label_path = env

        MetaKernelPDS4Label(setup, product)

        # Parse the rendered label; a malformed result would raise ParseError.
        tree = ElementTree.parse(label_path)
        root = tree.getroot()

        assert root.tag == 'spice_kernel_mk'
        assert root.findtext('file_name') == 'maven_v01.tm'
        assert root.findtext('kernel_type') == 'MK'

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

        MetaKernelPDS4Label(setup, product)

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
        MetaKernelPDS4Label(setup, product)

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
        # Missing MK templates must fail without registering the label.

        # Retrieve the integration objects and paths prepared by the fixture.
        setup, product, template_path, label_path = env

        # Physically delete the XML template created by the fixture.
        template_path.unlink()

        # Capture the exception.
        with pytest.raises(FileNotFoundError):
            MetaKernelPDS4Label(setup, product)

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
        template_path.write_text('<spice_kernel_mk>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        MetaKernelPDS4Label(setup, product)

        # The writer still creates the output label.
        assert label_path.exists()

        # Read the generated malformed XML label.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # The known placeholder is rendered even though the XML is malformed.
        assert '<file_name>maven_v01.tm</file_name>' in written_label
        assert '$FILE_NAME' not in written_label

        # XML parsing fails only when the test validates the generated content.
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written_label)

        # Because this layer does not validate XML, the label is still
        # registered relative to the staging directory.
        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)
