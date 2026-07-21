"""Tests for the OrbnumFilePDS4Label class.

Two test classes are provided:

* TestOrbnumFilePDS4Label – unit tests that mock the inherited label
  writing so the constructor, ``get_table_character_fields``,
  ``get_table_character_description`` and ``field_template`` can be
  exercised in isolation.

* TestOrbnumFilePDS4LabelIntegration – integration tests that exercise
  OrbnumFilePDS4Label together with the real PDSLabel.write_label() logic,
  writing an actual XML label to a temp directory and asserting on its
  contents.

The OrbNum label is a 'kernel' label: the parent PDSLabel.__init__ does NOT set
FILE_NAME / PRODUCT_LID / PRODUCT_VID / START_TIME / STOP_TIME; the child sets
them after super().__init__(). All product values are copied verbatim, without
validation; the only transformations are str() coercions of the numeric fields
and the assembly of the Field_Character / table description blocks.
"""
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_orbnum_file import OrbnumFilePDS4Label


# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------

def make_param(name: str, number: str = '1', location: str = '1',
               type_field: str = 'ASCII_Integer', length: str = '5',
               format_field: str = '%5d', description: str = 'desc',
               unit: str = '') -> dict:
    """Build a single ORBNUM field descriptor.

    product.params is an ordered mapping whose values are dicts with exactly
    these eight keys; field_template reads each one by name, so this factory
    mirrors that contract.

    :param name: value rendered inside <name> (also drives the "No." guard)
    :param number: value rendered inside <field_number>
    :param location: value rendered inside <field_location>
    :param type_field: value rendered inside <data_type>
    :param length: value rendered inside <field_length>
    :param format_field: value rendered inside <field_format>
    :param description: value rendered inside <description>
    :param unit: value rendered inside <unit> (omitted when falsy)
    :return: a single ``params`` entry
    """
    return {'name': name, 'number': number, 'location': location,
            'type': type_field, 'length': length, 'format': format_field,
            'description': description, 'unit': unit}


@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic factories for OrbNum file labels.

    Reuses ``base_helpers.make_setup`` as-is and wraps
    ``base_helpers.make_product`` to add the OrbNum-specific fields
    (missions/observers/targets, the numeric header/record metadata, the
    table-character description and the ``params`` mapping) and the on-disk
    <staging>/miscellaneous/<name> layout used by the inherited writer.

    :param base_helpers: generic Setup/base-product factories from conftest
    :return: container with ``make_setup`` and ``make_product`` callables
    """

    def _make_orbnum_product(
            staging_dir: Path,
            name: str = 'maven_orb_v01.orb',
            params: dict | None = None,
            table_char_description: str = 'ORBNUM table',
            blank_records: bool = True,
            header_length: int = 873,
            records: int = 100,
            record_fixed_length: int = 128) -> MagicMock:
        # The OrbNum file is physically placed under
        # <staging>/miscellaneous/<name>, matching the real Product staging
        # layout consumed by write_label().
        type_dir = staging_dir / 'miscellaneous'
        type_dir.mkdir(parents=True, exist_ok=True)

        product = base_helpers.make_product(
            path=str(type_dir / name),
            name=name,
            lid='urn:nasa:pds:maven_spice:miscellaneous:orbnum_' + name,
            collection_name='miscellaneous')

        # OrbNum is a 'kernel' label: PDSLabel.__init__ reads missions/
        # observers/targets from the product itself (not from setup), so they
        # must be real lists whose values match the CONTEXT_PRODUCTS entries
        # used by get_missions() / get_observers() / get_targets().
        product.missions = ['MAVEN']
        product.observers = ['MAVEN']
        product.targets = ['Mars']

        # OrbNum-specific fields copied by OrbnumFilePDS4Label.
        product.start_time = '2024-01-01T00:00:00Z'
        product.stop_time = '2024-01-31T23:59:59Z'
        product.description = 'MAVEN orbit number file'

        # Numeric metadata; the child str()-coerces each of these. They are
        # real ints because FIELDS_LENGTH performs integer arithmetic
        # (record_fixed_length + eol_length).
        product.header_length = header_length
        product.records = records
        product.record_fixed_length = record_fixed_length

        # The table-character description drives the optional <description>
        # block; an empty string suppresses it.
        product.table_char_description = table_char_description

        # When truthy (and the field is not "No.") each field gains a
        # Special_Constants block flagging blank-space missing constants.
        product.blank_records = blank_records

        # The ORBNUM ground set: an ordered mapping of field descriptors. The
        # default mixes a "No." field (never gets Special_Constants), a field
        # with a unit and one without, exercising every field_template branch.
        if params is None:
            params = {
                'No.': make_param('No.', number='1', location='1',
                                  type_field='ASCII_Integer', length='5',
                                  format_field='%5d',
                                  description='orbit number'),
                'UTC': make_param('UTC', number='2', location='7',
                                  type_field='ASCII_String', length='20',
                                  format_field='%20s',
                                  description='UTC time', unit='s'),
                'Alt': make_param('Alt', number='3', location='28',
                                  type_field='ASCII_Real', length='12',
                                  format_field='%12.3f',
                                  description='altitude')}

        product.params = params

        return product

    return SimpleNamespace(make_setup=base_helpers.make_setup,
                           make_product=_make_orbnum_product)


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestOrbnumFilePDS4Label:
    """Unit tests for OrbnumFilePDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> OrbnumFilePDS4Label:
        """Build an OrbnumFilePDS4Label instance while mocking inherited file
        writing.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized OrbNum factories
        :return: constructed label with write_label patched out
        """
        # Create a controlled Setup mock with the PDS4 attributes needed by the
        # label.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked OrbNum product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build an OrbNum product mock with the attributes read by
        # OrbnumFilePDS4Label.
        product = helpers.make_product(staging)

        # Avoid real template reading and file writing in unit tests.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            # Instantiate the real class so its constructor assignments are
            # executed.
            instance = OrbnumFilePDS4Label(setup, product)

        return instance

    # ------------------------------------------------------------------
    # Regular tests
    # ------------------------------------------------------------------

    def test_attribute_assignments(self, label: OrbnumFilePDS4Label) -> None:
        # Validate the PDS4 OrbNum label attributes populated during
        # construction.

        # Check that FILE_NAME has been copied from product.name.
        assert label.FILE_NAME == 'maven_orb_v01.orb'

        # Check that the PDS4 logical identifier and the product version have
        # been copied correctly from product.lid and product.vid.
        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:miscellaneous:orbnum_maven_orb_v01.orb')
        assert label.PRODUCT_VID == '1.0'

        # Check the fixed value defined by OrbnumFilePDS4Label.
        assert label.FILE_FORMAT == 'Character'

        # Check that the time coverage is copied from product.start_time and
        # product.stop_time, respectively.
        assert label.START_TIME == '2024-01-01T00:00:00Z'
        assert label.STOP_TIME == '2024-01-31T23:59:59Z'

        # Check that the description is copied from product.description.
        assert label.DESCRIPTION == 'MAVEN orbit number file'

        # Check that the numeric metadata is str()-coerced. HEADER_LENGTH and
        # TABLE_OFFSET both come from product.header_length because the table
        # data begins right after the header.
        assert label.HEADER_LENGTH == '873'
        assert label.TABLE_OFFSET == '873'
        assert label.TABLE_RECORDS == '100'

        # Check that the number of fields is the str() of len(product.params).
        assert label.NUMBER_OF_FIELDS == '3'

        # Check that the XML label name is derived from the product name.
        assert label.name == 'maven_orb_v01.xml'

    def test_template_path_is_orbnum_template(
            self, label: OrbnumFilePDS4Label) -> None:
        # The label must resolve the OrbNum-specific XML template under the
        # configured templates' directory.
        expected_template = str(
            Path(label.setup.templates_directory)
            / 'template_product_orbnum_table.xml')

        assert label._template == expected_template

    # ------------------------------------------------------------------
    # _*_reference_type overrides
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('information_model_float, expected_mission, expected_target', [
        (1014000000.0, 'ancillary_to_investigation', 'ancillary_to_target'),
        (1013000000.0, 'data_to_investigation', 'data_to_target'),
    ])
    def test_reference_type_threshold(
            self, information_model_float, expected_mission, expected_target) -> None:
        # Both overrides depend only on setup.information_model_float, so a
        # bare instance with just that attribute set is enough to exercise
        # the >= 1014000000.0 threshold on both sides.
        instance = object.__new__(OrbnumFilePDS4Label)
        instance.setup = SimpleNamespace(information_model_float=information_model_float)

        assert instance._mission_reference_type == expected_mission
        assert instance._target_reference_type == expected_target

    def test_constructor_stores_references_and_writes_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Validate constructor wiring and its single write_label side effect.

        # Build the collaborators required by the label constructor.
        setup = helpers.make_setup()

        # Create the staging directory used by the mocked OrbNum product path.
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Avoid real file writing while checking the constructor side effect.
        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True) as mock_write:
            label = OrbnumFilePDS4Label(setup, product)

        # Verify that label.setup is exactly the same setup object that was
        # passed to the constructor, and the same applies to label.product with
        # the product object.
        assert label.setup is setup
        assert label.product is product

        # Check that write_label() was called once and that it was called with
        # the label instance.
        mock_write.assert_called_once_with(label)

    @pytest.mark.parametrize('product_attribute, value, label_attribute', [
        ('lid', '', 'PRODUCT_LID'),
        ('vid', 'not-a-valid-version', 'PRODUCT_VID'),
        ('start_time', 'not-a-valid-start-time', 'START_TIME'),
        ('stop_time', '', 'STOP_TIME'),
        ('name', 'no_extension_name', 'FILE_NAME'),
        ('description', '', 'DESCRIPTION')])
    def test_product_values_are_copied_without_validation(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attribute: str, value: str,
            label_attribute: str) -> None:
        # Verify that the constructor copies product values verbatim, without
        # validating or transforming them.

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
            label = OrbnumFilePDS4Label(setup, product)

        # Check that the expected label attribute contains exactly the value
        # assigned to the product.
        assert getattr(label, label_attribute) == value

    @pytest.mark.parametrize('product_attribute, value, label_attribute, expected', [
        ('header_length', 0, 'HEADER_LENGTH', '0'),
        ('header_length', 512, 'TABLE_OFFSET', '512'),
        ('records', 0, 'TABLE_RECORDS', '0'),
        ('records', 4096, 'TABLE_RECORDS', '4096')])
    def test_numeric_fields_are_str_coerced(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attribute: str, value: int, label_attribute: str,
            expected: str) -> None:
        # The numeric product metadata is stored as its str() representation.
        # The boundary value 0 is included on purpose: it is falsy, so a naive
        # "if value" guard would wrongly drop it; it must still render as "0".

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock and override the numeric attribute under test.
        product = helpers.make_product(staging)
        setattr(product, product_attribute, value)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert getattr(label, label_attribute) == expected

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
        product.lid = 'urn:nasa:pds:maven_spice:miscellaneous:orbnum_distinct'
        product.vid = '9.9'

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.PRODUCT_LID == (
            'urn:nasa:pds:maven_spice:miscellaneous:orbnum_distinct')
        assert label.PRODUCT_VID == '9.9'

    @pytest.mark.parametrize('product_name, expected_label_name', [
        ('maven_orb_v01.orb', 'maven_orb_v01.xml'),
        ('maven_orb', 'maven_orb.xml'),
        ('maven_orb.v01.orb', 'maven_orb.v01.xml')])
    def test_label_name_is_derived_from_stem(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_name: str, expected_label_name: str) -> None:
        # Document how product names are converted into XML label names. The
        # last case has more than one dot; only the last suffix is replaced.

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
            label = OrbnumFilePDS4Label(setup, product)

        # FILE_NAME is the verbatim product name (no truncation there).
        assert label.FILE_NAME == product_name

        # The XML label name is the truncated-at-first-dot value.
        assert label.name == expected_label_name

    @pytest.mark.parametrize('end_of_line, record_fixed_length, expected', [
        ('LF', 128, '128'),
        ('LF', 0, '0'),
        ('CRLF', 128, '129'),
        ('CRLF', 0, '1')])
    def test_fields_length_accounts_for_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace, end_of_line: str,
            record_fixed_length: int, expected: str) -> None:
        # FIELDS_LENGTH is the fixed record length plus the end-of-line cost:
        # +1 byte for CRLF (the trailing carriage return), +0 for LF. The
        # branch is driven by the parent-computed END_OF_LINE, which derives
        # from setup.end_of_line. Boundary value 0 is included for both endings.

        setup = helpers.make_setup(end_of_line=end_of_line)
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock and override the fixed record length.
        product = helpers.make_product(staging)
        product.record_fixed_length = record_fixed_length

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS_LENGTH == expected

    def test_constructor_raises_when_record_length_is_not_numeric(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # TODO: BUG; record_fixed_length is used in integer arithmetic with no
        #       type validation, so a non-numeric value raises TypeError and
        #       aborts label generation with no informative message. Fix: cast
        #       to int() before adding the end-of-line length.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging)

        # Replace the fixed record length with a non-numeric value.
        product.record_fixed_length = 'not-a-number'

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with pytest.raises(TypeError):
                OrbnumFilePDS4Label(setup, product)

    # ------------------------------------------------------------------
    # get_table_character_fields / field_template – the field blocks
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('params, expected_number_of_fields', [
        ({}, '0'),
        ({'No.': make_param('No.')}, '1'),
        ({'No.': make_param('No.'),
          'UTC': make_param('UTC', unit='s'),
          'Alt': make_param('Alt')}, '3')])
    def test_number_of_fields_matches_params_count(
            self, tmp_path: Path, helpers: SimpleNamespace, params: dict,
            expected_number_of_fields: str) -> None:
        # NUMBER_OF_FIELDS is the str() of the number of entries in
        # product.params, checked for zero, one and several fields.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock with the parametrized params mapping.
        product = helpers.make_product(staging, params=params)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.NUMBER_OF_FIELDS == expected_number_of_fields

    def test_get_table_character_fields_empty_params_returns_empty_string(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # With an empty params mapping the field-building loop never iterates,
        # so the concatenated FIELDS string must be empty.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(staging, params={})

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS == ''

    @pytest.mark.parametrize('name, unit, blank_records, expected', [
        ('Alt', '', False,
         '    <Field_Character>\n'
         '     <name>Alt</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <description>desc</description>\n'
         '    </Field_Character>\n'),
        ('UTC', 's', False,
         '    <Field_Character>\n'
         '     <name>UTC</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <unit>s</unit>\n'
         '     <description>desc</description>\n'
         '    </Field_Character>\n'),
        ('Alt', '', True,
         '    <Field_Character>\n'
         '     <name>Alt</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <description>desc</description>\n'
         '     <Special_Constants>\n'
         '      <missing_constant>blank space</missing_constant>\n'
         '     </Special_Constants>\n'
         '    </Field_Character>\n'),
        ('No.', '', True,
         '    <Field_Character>\n'
         '     <name>No.</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <description>desc</description>\n'
         '    </Field_Character>\n')])
    def test_field_template_renders_optional_blocks(
            self, tmp_path: Path, helpers: SimpleNamespace, name: str,
            unit: str, blank_records: bool, expected: str) -> None:
        # field_template has two optional sections. The <unit> line is emitted
        # only when a unit is set. The Special_Constants block is emitted only
        # when blank_records is on AND the field is not the reserved "No."
        # (orbit numbers are never blank). Each row pins one full block.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Build the product mock with a single parametrized field.
        product = helpers.make_product(
            staging, blank_records=blank_records,
            params={name: make_param(name, unit=unit)})

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS == expected

    def test_get_table_character_fields_concatenates_in_order(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # get_table_character_fields emits exactly one <Field_Character> block
        # per param and concatenates them in the params mapping order.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        # Default product carries three fields in the order No., UTC, Alt.
        product = helpers.make_product(staging, blank_records=False)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        # One block per param.
        assert label.FIELDS.count('<Field_Character>') == 3

        # The blocks appear in insertion order.
        assert (label.FIELDS.index('<name>No.</name>')
                < label.FIELDS.index('<name>UTC</name>')
                < label.FIELDS.index('<name>Alt</name>'))

    @pytest.mark.parametrize('xml_tab, expected', [
        (1,
         '    <Field_Character>\n'
         '     <name>Alt</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <description>desc</description>\n'
         '    </Field_Character>\n'),
        (2,
         '        <Field_Character>\n'
         '          <name>Alt</name>\n'
         '          <field_number>1</field_number>\n'
         '          <field_location unit="byte">1</field_location>\n'
         '          <data_type>ASCII_Integer</data_type>\n'
         '          <field_length unit="byte">5</field_length>\n'
         '          <field_format>%5d</field_format>\n'
         '          <description>desc</description>\n'
         '        </Field_Character>\n')])
    def test_field_template_honours_xml_tab(
            self, tmp_path: Path, helpers: SimpleNamespace, xml_tab: int,
            expected: str) -> None:
        # The indentation must scale with setup.xml_tab: 4*tab spaces for the
        # <Field_Character> element and 5*tab spaces for its children.

        setup = helpers.make_setup()
        setup.xml_tab = xml_tab

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, blank_records=False,
            params={'Alt': make_param('Alt')})

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS == expected

        # Explicitly assert the leading indentation width to make the contract
        # unambiguous.
        first_line = label.FIELDS.split(setup.eol_pds4)[0]
        assert first_line == f"{' ' * 4 * xml_tab}<Field_Character>"

    @pytest.mark.parametrize('eol_pds4, expected', [
        ('\n',
         '    <Field_Character>\n'
         '     <name>Alt</name>\n'
         '     <field_number>1</field_number>\n'
         '     <field_location unit="byte">1</field_location>\n'
         '     <data_type>ASCII_Integer</data_type>\n'
         '     <field_length unit="byte">5</field_length>\n'
         '     <field_format>%5d</field_format>\n'
         '     <description>desc</description>\n'
         '    </Field_Character>\n'),
        ('\r\n',
         '    <Field_Character>\r\n'
         '     <name>Alt</name>\r\n'
         '     <field_number>1</field_number>\r\n'
         '     <field_location unit="byte">1</field_location>\r\n'
         '     <data_type>ASCII_Integer</data_type>\r\n'
         '     <field_length unit="byte">5</field_length>\r\n'
         '     <field_format>%5d</field_format>\r\n'
         '     <description>desc</description>\r\n'
         '    </Field_Character>\r\n')])
    def test_field_template_honours_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace, eol_pds4: str,
            expected: str) -> None:
        # The configured PDS4 end-of-line sequence must be used as the line
        # terminator inside the generated block (and for the trailing EOL).

        setup = helpers.make_setup(eol_pds4=eol_pds4)

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, blank_records=False,
            params={'Alt': make_param('Alt')})

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS == expected
        assert label.FIELDS.endswith(eol_pds4)

    def test_field_template_forwards_all_descriptor_values(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # get_table_character_fields must unpack each param dict and pass its
        # values to field_template positionally, in the documented order, with
        # product.blank_records appended as the trailing ``blanks`` argument.
        # field_template is stubbed so we assert on the call signature and that
        # its return value is what ends up in FIELDS.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, blank_records=True,
            params={'Alt': make_param(
                'Alt', number='7', location='28', type_field='ASCII_Real',
                length='12', format_field='%12.3f', description='altitude',
                unit='km')})

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            with patch.object(OrbnumFilePDS4Label, 'field_template',
                              autospec=True,
                              return_value='STUB') as mock_field:
                label = OrbnumFilePDS4Label(setup, product)

        # The fields string is exactly the stubbed return value.
        assert label.FIELDS == 'STUB'

        # field_template received every descriptor value positionally, in order,
        # with product.blank_records as the trailing ``blanks`` argument.
        mock_field.assert_called_once_with(
            label, 'Alt', '7', '28', 'ASCII_Real', '12', '%12.3f',
            'altitude', 'km', True)

    # ------------------------------------------------------------------
    # get_table_character_description
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('table_char_description, expected', [
        ('', ''),
        ('ORBNUM table',
         '\n      <description>ORBNUM table</description>\n')])
    def test_table_character_description_is_wrapped_when_present(
            self, tmp_path: Path, helpers: SimpleNamespace,
            table_char_description: str, expected: str) -> None:
        # TABLE_CHARACTER_DESCRIPTION wraps a non-empty product description and
        # leaves the empty case as the empty string.

        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, table_char_description=table_char_description)

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.TABLE_CHARACTER_DESCRIPTION == expected

    @pytest.mark.parametrize('xml_tab, expected', [
        (1, '\n      <description>ORBNUM table</description>\n'),
        (2, '\n            <description>ORBNUM table</description>\n')])
    def test_table_character_description_honours_xml_tab(
            self, tmp_path: Path, helpers: SimpleNamespace, xml_tab: int,
            expected: str) -> None:
        # The <description> indentation inside the table-character block must
        # scale with setup.xml_tab (6*tab spaces).

        setup = helpers.make_setup()
        setup.xml_tab = xml_tab

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, table_char_description='ORBNUM table')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.TABLE_CHARACTER_DESCRIPTION == expected

    @pytest.mark.parametrize('eol_pds4, expected', [
        ('\n', '\n      <description>ORBNUM table</description>\n'),
        ('\r\n', '\r\n      <description>ORBNUM table</description>\r\n')])
    def test_table_character_description_honours_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace, eol_pds4: str,
            expected: str) -> None:
        # Both the leading and trailing terminators of the wrapped block must
        # use the configured PDS4 end-of-line.

        setup = helpers.make_setup(eol_pds4=eol_pds4)

        staging = tmp_path / 'staging'
        staging.mkdir(parents=True, exist_ok=True)

        product = helpers.make_product(
            staging, table_char_description='ORBNUM table')

        with patch('pds.naif_pds4_bundler.classes.label.label.'
                   'PDSLabel.write_label', autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.TABLE_CHARACTER_DESCRIPTION == expected


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

TEMPLATE_CONTENT = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<orbnum_table>\n'
    '  <file_name>$FILE_NAME</file_name>\n'
    '  <logical_identifier>$PRODUCT_LID</logical_identifier>\n'
    '  <version_id>$PRODUCT_VID</version_id>\n'
    '  <file_format>$FILE_FORMAT</file_format>\n'
    '  <start_date_time>$START_TIME</start_date_time>\n'
    '  <stop_date_time>$STOP_TIME</stop_date_time>\n'
    '  <description>$DESCRIPTION</description>\n'
    '  <header_length>$HEADER_LENGTH</header_length>\n'
    '  <table_offset>$TABLE_OFFSET</table_offset>\n'
    '  <records>$TABLE_RECORDS</records>\n'
    '  <fields>$NUMBER_OF_FIELDS</fields>\n'
    '  <fields_length>$FIELDS_LENGTH</fields_length>\n'
    '  <Table_Character>$TABLE_CHARACTER_DESCRIPTION\n'
    '$FIELDS  </Table_Character>\n'
    '</orbnum_table>\n')


class TestOrbnumFilePDS4LabelIntegration:
    """Integration tests for OrbnumFilePDS4Label + PDSLabel + template."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Create the temporary PDS4 template and staging environment used by
        integration tests.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialized OrbNum factories
        :return: tuple of (setup, product, template_path, expected_label_path)
        """
        # Create isolated directories for the template input and label output.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        # Write the OrbNum XML template consumed by PDSLabel.write_label().
        template_path = templates_dir / 'template_product_orbnum_table.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        # Build the setup mock and point it to the temporary integration
        # folders.
        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        # Build the OrbNum product whose label will be generated in staging.
        # The physical OrbNum file lives under <staging>/miscellaneous/<name>.
        product = helpers.make_product(staging_dir)

        # The inherited writer derives the XML label path from product.path by
        # replacing the ``.<extension>`` suffix with ``.xml``.
        expected_label_path = (staging_dir / 'miscellaneous'
                               / 'maven_orb_v01.xml')

        # Return only the objects/paths needed by the integration tests.
        return setup, product, template_path, expected_label_path

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Render the OrbNum XML template and validate the generated label.

        # Retrieve the objects and paths required by the integration test.
        setup, product, template_path, label_path = env

        # Configure the line-ending for PDS4.
        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        # Instantiate the real label so the template is read and the XML is
        # written.
        label = OrbnumFilePDS4Label(setup, product)

        # Check that the class resolved the configured OrbNum template.
        assert label._template == str(template_path)

        # The real writer mutates label.name to the generated XML file path.
        assert Path(label.name) == label_path

        # Check that the final XML file has been created in staging.
        assert label_path.exists()

        # Compare the generated label with the exact expected content. The
        # composite placeholders ($TABLE_CHARACTER_DESCRIPTION and $FIELDS) are
        # pre-rendered by the child before the writer substitutes the scalars.
        assert label_path.read_text(encoding='utf-8') == (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<orbnum_table>\n'
            '  <file_name>maven_orb_v01.orb</file_name>\n'
            '  <logical_identifier>'
            'urn:nasa:pds:maven_spice:miscellaneous:orbnum_maven_orb_v01.orb'
            '</logical_identifier>\n'
            '  <version_id>1.0</version_id>\n'
            '  <file_format>Character</file_format>\n'
            '  <start_date_time>2024-01-01T00:00:00Z</start_date_time>\n'
            '  <stop_date_time>2024-01-31T23:59:59Z</stop_date_time>\n'
            '  <description>MAVEN orbit number file</description>\n'
            '  <header_length>873</header_length>\n'
            '  <table_offset>873</table_offset>\n'
            '  <records>100</records>\n'
            '  <fields>3</fields>\n'
            '  <fields_length>128</fields_length>\n'
            '  <Table_Character>\n'
            '      <description>ORBNUM table</description>\n'
            '    <Field_Character>\n'
            '     <name>No.</name>\n'
            '     <field_number>1</field_number>\n'
            '     <field_location unit="byte">1</field_location>\n'
            '     <data_type>ASCII_Integer</data_type>\n'
            '     <field_length unit="byte">5</field_length>\n'
            '     <field_format>%5d</field_format>\n'
            '     <description>orbit number</description>\n'
            '    </Field_Character>\n'
            '    <Field_Character>\n'
            '     <name>UTC</name>\n'
            '     <field_number>2</field_number>\n'
            '     <field_location unit="byte">7</field_location>\n'
            '     <data_type>ASCII_String</data_type>\n'
            '     <field_length unit="byte">20</field_length>\n'
            '     <field_format>%20s</field_format>\n'
            '     <unit>s</unit>\n'
            '     <description>UTC time</description>\n'
            '     <Special_Constants>\n'
            '      <missing_constant>blank space</missing_constant>\n'
            '     </Special_Constants>\n'
            '    </Field_Character>\n'
            '    <Field_Character>\n'
            '     <name>Alt</name>\n'
            '     <field_number>3</field_number>\n'
            '     <field_location unit="byte">28</field_location>\n'
            '     <data_type>ASCII_Real</data_type>\n'
            '     <field_length unit="byte">12</field_length>\n'
            '     <field_format>%12.3f</field_format>\n'
            '     <description>altitude</description>\n'
            '     <Special_Constants>\n'
            '      <missing_constant>blank space</missing_constant>\n'
            '     </Special_Constants>\n'
            '    </Field_Character>\n'
            '  </Table_Character></orbnum_table>\n')

    def test_label_file_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # The rendered label must be well-formed XML with all placeholders
        # substituted by the label state.
        setup, product, _, label_path = env

        OrbnumFilePDS4Label(setup, product)

        # Parse the rendered label; a malformed result would raise ParseError.
        tree = ElementTree.parse(label_path)
        root = tree.getroot()

        assert root.tag == 'orbnum_table'
        assert root.findtext('file_name') == 'maven_orb_v01.orb'
        assert root.findtext('fields') == '3'

        # The Table_Character element must hold the rendered description and one
        # Field_Character per param.
        table = root.find('Table_Character')
        assert table.findtext('description') == 'ORBNUM table'
        assert len(table.findall('Field_Character')) == 3

        # No unresolved template placeholders must remain.
        assert '$' not in label_path.read_text(encoding='utf-8')

    def test_label_with_empty_table_character_description_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # When table_char_description is empty the composite placeholder renders
        # to nothing, so Table_Character must contain no <description> child and
        # the document must still parse as valid XML.
        setup, product, _, label_path = env

        # Override the description to be empty.
        product.table_char_description = ''

        OrbnumFilePDS4Label(setup, product)

        tree = ElementTree.parse(label_path)
        root = tree.getroot()

        table = root.find('Table_Character')
        assert table.find('description') is None
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

        OrbnumFilePDS4Label(setup, product)

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
        OrbnumFilePDS4Label(setup, product)

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
        # Missing OrbNum templates must fail without registering the label.

        # Retrieve the integration objects and paths prepared by the fixture.
        setup, product, template_path, label_path = env

        # Physically delete the XML template created by the fixture.
        template_path.unlink()

        # Capture the exception.
        with pytest.raises(FileNotFoundError):
            OrbnumFilePDS4Label(setup, product)

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
        template_path.write_text('<orbnum_table>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        OrbnumFilePDS4Label(setup, product)

        # The writer still creates the output label.
        assert label_path.exists()

        # Read the generated malformed XML label.
        with open(label_path, 'rt', encoding='utf-8', newline='') as f:
            written_label = f.read()

        # The known placeholder is rendered even though the XML is malformed.
        assert '<file_name>maven_orb_v01.orb</file_name>' in written_label
        assert '$FILE_NAME' not in written_label

        # XML parsing fails only when the test validates the generated content.
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written_label)

        # Because this layer does not validate XML, the label is still
        # registered relative to the staging directory.
        expected_relative = str(
            label_path.relative_to(Path(setup.staging_directory)))
        setup.add_file.assert_called_once_with(expected_relative)
