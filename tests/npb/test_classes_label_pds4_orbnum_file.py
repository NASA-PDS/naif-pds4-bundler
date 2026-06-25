"""Tests for the OrbnumFilePDS4Label class.

Two test classes are provided:

* TestOrbnumFilePDS4Label – unit tests that mock the inherited label writing
  so the constructor, ``get_table_character_fields``,
  ``get_table_character_description`` and ``field_template`` are exercised in
  isolation.

* TestOrbnumFilePDS4LabelIntegration – integration tests that run the real
  PDSLabel.write_label() logic, writing an actual XML label to disk and
  asserting on its parsed structure.

The OrbNum label is a 'kernel-branch' label: PDSLabel.__init__ reads
missions/observers/targets from the product itself, and the child sets
FILE_NAME / PRODUCT_LID / PRODUCT_VID / START_TIME / STOP_TIME afterwards. All
product values are copied verbatim; the only transformations are str()
coercions of the numeric fields and the assembly of the Field_Character and
description blocks.
"""
from pathlib import Path
import xml.etree.ElementTree as ElementTree
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_orbnum_file import OrbnumFilePDS4Label


# Dotted path of the inherited writer, patched out in every unit test so the
# constructor runs without touching the filesystem.
WRITE_LABEL = 'pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label'

# Minimal OrbNum table template. The two composite placeholders ($FIELDS and
# $TABLE_CHARACTER_DESCRIPTION) are pre-rendered by the child before the writer
# substitutes the scalar ones. The $FIELDS line sits at column 0 because the
# rendered fields already carry their own indentation.
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


def _param(name: str, unit: str = '') -> dict:
    """Build one ORBNUM field descriptor with the eight keys field_template reads.

    :param name: field name (also drives the "No." guard for Special_Constants)
    :param unit: optional unit; omitted from the output when empty
    :return: a single ``params`` entry
    """
    return {'name': name, 'number': '1', 'location': '1',
            'type': 'ASCII_Integer', 'length': '5', 'format': '%5d',
            'description': 'desc', 'unit': unit}


@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialize the generic conftest factories for OrbNum labels.

    :param base_helpers: generic Setup/base-product factories from conftest
    :return: container with ``make_setup`` and ``make_product`` callables
    """

    def _make_orbnum_product(staging_dir: Path,
                             name: str = 'maven_orb_v01.orb',
                             params: dict | None = None,
                             table_char_description: str = 'ORBNUM table',
                             blank_records: bool = True,
                             header_length: int = 873,
                             records: int = 100,
                             record_fixed_length: int = 128) -> MagicMock:
        type_dir = staging_dir / 'miscellaneous'
        type_dir.mkdir(parents=True, exist_ok=True)

        product = base_helpers.make_product(
            path=str(type_dir / name), name=name,
            lid='urn:nasa:pds:maven_spice:miscellaneous:orbnum_' + name,
            collection_name='miscellaneous')

        # Kernel-branch labels read these three from the product itself.
        product.missions = ['MAVEN']
        product.observers = ['MAVEN']
        product.targets = ['Mars']

        product.start_time = '2024-01-01T00:00:00Z'
        product.stop_time = '2024-01-31T23:59:59Z'
        product.description = 'MAVEN orbit number file'

        # Numeric metadata; the child str()-coerces these. Real ints because
        # FIELDS_LENGTH does integer arithmetic.
        product.header_length = header_length
        product.records = records
        product.record_fixed_length = record_fixed_length

        product.table_char_description = table_char_description
        product.blank_records = blank_records

        # Default ground set covers every field_template branch at once: the
        # "No." field (no Special_Constants), a field with a unit, one without.
        if params is None:
            params = {'No.': _param('No.'), 'UTC': _param('UTC', unit='s'),
                      'Alt': _param('Alt')}
        product.params = params

        return product

    return SimpleNamespace(make_setup=base_helpers.make_setup,
                           make_product=_make_orbnum_product)


def _build(helpers: SimpleNamespace, staging: Path,
           setup_kwargs: dict | None = None,
           product_kwargs: dict | None = None) -> OrbnumFilePDS4Label:
    """Construct an OrbnumFilePDS4Label with write_label patched out.

    Centralises the setup/product/patch boilerplate shared by the unit tests.

    :param helpers: specialised OrbNum factories
    :param staging: writable staging root
    :param setup_kwargs: optional overrides forwarded to make_setup
    :param product_kwargs: optional overrides forwarded to make_product
    :return: constructed label (write_label not called)
    """
    setup = helpers.make_setup(**(setup_kwargs or {}))
    product = helpers.make_product(staging, **(product_kwargs or {}))
    with patch(WRITE_LABEL, autospec=True):
        return OrbnumFilePDS4Label(setup, product)


# ===========================================================================
# Unit tests
# ===========================================================================

class TestOrbnumFilePDS4Label:
    """Unit tests for OrbnumFilePDS4Label."""

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> OrbnumFilePDS4Label:
        """A default label instance with write_label mocked.

        :param tmp_path: pytest temporary directory
        :param helpers: specialised OrbNum factories
        :return: constructed label
        """
        return _build(helpers, tmp_path / 'staging')

    @pytest.mark.parametrize('attribute, expected', [
        ('FILE_NAME', 'maven_orb_v01.orb'),
        ('PRODUCT_LID',
         'urn:nasa:pds:maven_spice:miscellaneous:orbnum_maven_orb_v01.orb'),
        ('PRODUCT_VID', '1.0'),
        ('FILE_FORMAT', 'Character'),
        ('START_TIME', '2024-01-01T00:00:00Z'),
        ('STOP_TIME', '2024-01-31T23:59:59Z'),
        ('DESCRIPTION', 'MAVEN orbit number file'),
        ('HEADER_LENGTH', '873'),
        ('TABLE_OFFSET', '873'),
        ('TABLE_RECORDS', '100'),
        ('NUMBER_OF_FIELDS', '3'),
        ('name', 'maven_orb_v01.xml')])
    def test_scalar_attributes(self, label: OrbnumFilePDS4Label,
                               attribute: str, expected: str) -> None:
        # Verify every scalar label attribute the constructor populates. Each
        # is either a verbatim copy of a product field (FILE_NAME, PRODUCT_LID,
        # times, DESCRIPTION), a fixed constant (FILE_FORMAT == "Character"), or
        # a str()-coerced numeric (HEADER_LENGTH, TABLE_OFFSET, TABLE_RECORDS,
        # NUMBER_OF_FIELDS). TABLE_OFFSET equals HEADER_LENGTH because the table
        # data begins right after the header, and 'name' is the XML label name
        # derived from the product name. One parameter row per attribute.
        assert getattr(label, attribute) == expected

    def test_template_path(self, label: OrbnumFilePDS4Label) -> None:
        # The child must point 'template' at the OrbNum-specific XML template
        # file, resolved by joining setup.templates_directory with the fixed
        # template_product_orbnum_table.xml filename.
        assert label.template == str(
            Path(label.setup.templates_directory)
            / 'template_product_orbnum_table.xml')

    def test_stores_references_and_writes_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # The constructor must keep the exact setup and product objects it is
        # given (identity, not a copy) and must trigger label generation by
        # calling write_label() once and only once.
        setup = helpers.make_setup()
        product = helpers.make_product(tmp_path / 'staging')

        with patch(WRITE_LABEL, autospec=True) as mock_write:
            label = OrbnumFilePDS4Label(setup, product)

        assert label.setup is setup
        assert label.product is product
        mock_write.assert_called_once_with(label)

    @pytest.mark.parametrize('product_attr, value, label_attr', [
        ('lid', '', 'PRODUCT_LID'),
        ('vid', 'not-a-version', 'PRODUCT_VID'),
        ('start_time', 'not-a-time', 'START_TIME'),
        ('stop_time', '', 'STOP_TIME'),
        ('name', 'no_extension', 'FILE_NAME'),
        ('description', '', 'DESCRIPTION')])
    def test_values_copied_verbatim(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attr: str, value: str, label_attr: str) -> None:
        # These product fields are copied straight onto the label with no
        # validation: empty strings and clearly invalid values (bad version, bad
        # timestamp, name without extension) must pass through unchanged. This
        # documents that sanitising inputs is not this class's responsibility.
        setup = helpers.make_setup()
        product = helpers.make_product(tmp_path / 'staging')
        setattr(product, product_attr, value)

        with patch(WRITE_LABEL, autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert getattr(label, label_attr) == value

    @pytest.mark.parametrize('product_attr, value, label_attr, expected', [
        ('header_length', 0, 'HEADER_LENGTH', '0'),
        ('header_length', 512, 'TABLE_OFFSET', '512'),
        ('records', 0, 'TABLE_RECORDS', '0'),
        ('records', 4096, 'TABLE_RECORDS', '4096')])
    def test_numeric_fields_str_coerced(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_attr: str, value: int, label_attr: str,
            expected: str) -> None:
        # The numeric product fields (header_length, records) are stored as
        # their str() form. The boundary value 0 is included on purpose: it is
        # falsy, so a naive "if value" guard would wrongly drop it; here it must
        # still render as the string "0".
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={product_attr: value})

        assert getattr(label, label_attr) == expected

    @pytest.mark.parametrize('product_name, expected_label_name', [
        ('maven_orb_v01.orb', 'maven_orb_v01.xml'),
        ('maven_orb', 'maven_orb.xml'),
        # TODO: BUG; split(".")[0] truncates at the FIRST dot, so a multi-dot
        #       name loses everything after it.
        ('maven_orb.v01.orb', 'maven_orb.xml')])
    def test_label_name_truncates_at_first_dot(
            self, tmp_path: Path, helpers: SimpleNamespace,
            product_name: str, expected_label_name: str) -> None:
        # FILE_NAME keeps the full product name, but 'name' (the XML label
        # filename) is built as split(".")[0] + ".xml". The three rows cover a
        # normal single-dot name, a name with no dot, and the buggy multi-dot
        # case where everything after the first dot is lost.
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={'name': product_name})

        assert label.FILE_NAME == product_name
        assert label.name == expected_label_name

    @pytest.mark.parametrize('end_of_line, record_fixed_length, expected', [
        ('LF', 128, '128'),
        ('LF', 0, '0'),
        ('CRLF', 128, '129'),
        ('CRLF', 0, '1')])
    def test_fields_length_accounts_for_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace,
            end_of_line: str, record_fixed_length: int,
            expected: str) -> None:
        # FIELDS_LENGTH is the fixed record length plus the end-of-line cost:
        # +1 byte for CRLF (the extra carriage return), +0 for LF. The branch is
        # driven by the parent-computed END_OF_LINE, which derives from
        # setup.end_of_line. Boundary value 0 is included for both line endings.
        label = _build(
            helpers, tmp_path / 'staging',
            setup_kwargs={'end_of_line': end_of_line},
            product_kwargs={'record_fixed_length': record_fixed_length})

        assert label.FIELDS_LENGTH == expected

    def test_fields_length_raises_for_non_numeric_record_length(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Because FIELDS_LENGTH does integer arithmetic on record_fixed_length
        # with no type check, a non-numeric value raises TypeError during
        # construction. This pins the current (fragile) behaviour and flags it.
        # TODO: BUG; validate/cast record_fixed_length to int before adding,
        #       so a bad value fails with a clear message instead of a raw
        #       TypeError.
        setup = helpers.make_setup()
        product = helpers.make_product(tmp_path / 'staging')
        product.record_fixed_length = 'not-a-number'

        with patch(WRITE_LABEL, autospec=True):
            with pytest.raises(TypeError):
                OrbnumFilePDS4Label(setup, product)

    @pytest.mark.parametrize('params, expected', [
        ({}, '0'),
        ({'No.': _param('No.')}, '1'),
        ({'No.': _param('No.'), 'UTC': _param('UTC', 's'),
          'Alt': _param('Alt')}, '3')])
    def test_number_of_fields(self, tmp_path: Path, helpers: SimpleNamespace,
                              params: dict, expected: str) -> None:
        # NUMBER_OF_FIELDS is the count of entries in product.params rendered as
        # a string, checked for zero, one and several fields.
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={'params': params})

        assert label.NUMBER_OF_FIELDS == expected

    def test_empty_params_yields_empty_fields(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # With an empty params mapping the field-building loop never iterates,
        # so the concatenated FIELDS string must be empty (covers the
        # zero-iteration branch of get_table_character_fields).
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={'params': {}})

        assert label.FIELDS == ''

    @pytest.mark.parametrize('name, unit, blanks, has_unit, has_constants', [
        ('Alt', '', False, False, False),   # plain field
        ('UTC', 's', False, True, False),   # unit only
        ('Alt', '', True, False, True),     # Special_Constants only
        ('UTC', 's', True, True, True),     # both optional blocks
        ('No.', '', True, False, False)])   # "No." is exempt from constants
    def test_field_template_optional_blocks(
            self, tmp_path: Path, helpers: SimpleNamespace, name: str,
            unit: str, blanks: bool, has_unit: bool,
            has_constants: bool) -> None:
        # field_template has two optional sections. The <unit> line is emitted
        # only when a unit is set. The Special_Constants block is emitted only
        # when blank_records is on AND the field is not the reserved "No."
        # (orbit numbers are never blank). The five rows cover every
        # combination, including the "No." exemption. The mandatory
        # <Field_Character> wrapper and <name> are always present.
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={'blank_records': blanks,
                                       'params': {name: _param(name, unit)}})

        assert (f'<unit>{unit}</unit>' in label.FIELDS) is has_unit
        assert ('<Special_Constants>' in label.FIELDS) is has_constants
        # The mandatory parts are always present exactly once.
        assert label.FIELDS.count('<Field_Character>') == 1
        assert f'<name>{name}</name>' in label.FIELDS

    def test_fields_concatenated_in_order(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # get_table_character_fields emits exactly one <Field_Character> block
        # per param and concatenates them in the params mapping order. Verified
        # by counting the blocks and checking the names appear in insertion
        # order (No. -> UTC -> Alt from the default product).
        label = _build(helpers, tmp_path / 'staging',
                       product_kwargs={'blank_records': False})

        assert label.FIELDS.count('<Field_Character>') == 3
        assert (label.FIELDS.index('<name>No.</name>')
                < label.FIELDS.index('<name>UTC</name>')
                < label.FIELDS.index('<name>Alt</name>'))

    @pytest.mark.parametrize('xml_tab, eol', [
        (1, '\n'), (4, '\n'), (2, '\r\n')])
    def test_field_template_indentation_and_eol(
            self, tmp_path: Path, helpers: SimpleNamespace,
            xml_tab: int, eol: str) -> None:
        # field_template indents the <Field_Character> element by 4*xml_tab
        # spaces and its children by 5*xml_tab, and terminates every line with
        # the configured PDS4 end-of-line. Checked across several tab widths and
        # both LF and CRLF; the trailing eol means the block ends with one.
        setup = helpers.make_setup(eol_pds4=eol)
        setup.xml_tab = xml_tab
        product = helpers.make_product(
            tmp_path / 'staging', blank_records=False,
            params={'Alt': _param('Alt')})

        with patch(WRITE_LABEL, autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        lines = label.FIELDS.split(eol)
        assert lines[0] == ' ' * (4 * xml_tab) + '<Field_Character>'
        assert lines[1] == ' ' * (5 * xml_tab) + '<name>Alt</name>'

        # Every non-empty rendered line ends with eol (so split leaves a tail).
        assert label.FIELDS.endswith(eol)

    def test_field_template_forwards_all_arguments(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # get_table_character_fields must unpack each param dict and pass its
        # values to field_template positionally, in the documented order, with
        # product.blank_records appended as the trailing 'blanks' argument.
        # field_template is stubbed, so we assert on the call signature (and that
        # its return value is what ends up in FIELDS) rather than the rendering.
        params = {'Alt': {'name': 'Alt', 'number': '7', 'location': '28',
                          'type': 'ASCII_Real', 'length': '12',
                          'format': '%12.3f', 'description': 'altitude',
                          'unit': 'km'}}
        setup = helpers.make_setup()
        product = helpers.make_product(tmp_path / 'staging',
                                       blank_records=True, params=params)

        with patch(WRITE_LABEL, autospec=True):
            with patch.object(OrbnumFilePDS4Label, 'field_template',
                              autospec=True, return_value='STUB') as mock_field:
                label = OrbnumFilePDS4Label(setup, product)

        assert label.FIELDS == 'STUB'
        mock_field.assert_called_once_with(
            label, 'Alt', '7', '28', 'ASCII_Real', '12', '%12.3f',
            'altitude', 'km', True)

    @pytest.mark.parametrize('tcd, xml_tab, eol, expected', [
        ('', 1, '\n', ''),
        ('ORBNUM table', 1, '\n',
         '\n      <description>ORBNUM table</description>\n'),
        ('ORBNUM table', 2, '\n',
         '\n            <description>ORBNUM table</description>\n'),
        ('ORBNUM table', 1, '\r\n',
         '\r\n      <description>ORBNUM table</description>\r\n')])
    def test_table_character_description(
            self, tmp_path: Path, helpers: SimpleNamespace, tcd: str,
            xml_tab: int, eol: str, expected: str) -> None:
        # TABLE_CHARACTER_DESCRIPTION: when table_char_description is non-empty
        # it is wrapped in a <description> element indented by 6*xml_tab spaces
        # and surrounded by the eol on both sides; when empty, the wrapping
        # branch is skipped and the attribute stays the empty string. Rows cover
        # the empty case, two tab widths, and CRLF.
        setup = helpers.make_setup(eol_pds4=eol)
        setup.xml_tab = xml_tab
        product = helpers.make_product(tmp_path / 'staging',
                                       table_char_description=tcd)

        with patch(WRITE_LABEL, autospec=True):
            label = OrbnumFilePDS4Label(setup, product)

        assert label.TABLE_CHARACTER_DESCRIPTION == expected


# ===========================================================================
# Integration tests
# ===========================================================================

class TestOrbnumFilePDS4LabelIntegration:
    """Integration tests for OrbnumFilePDS4Label + the real writer."""

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Template-on-disk + staging environment for the real writer.

        :param tmp_path: pytest temporary directory
        :param helpers: specialised OrbNum factories
        :return: (setup, product, template_path, expected_label_path)
        """
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        template_path = templates_dir / 'template_product_orbnum_table.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        product = helpers.make_product(staging_dir)
        label_path = staging_dir / 'miscellaneous' / 'maven_orb_v01.xml'

        return setup, product, template_path, label_path

    def test_label_is_written_as_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # End-to-end: run the real writer against an on-disk template and parse
        # the result. The label must resolve the right template, write to the
        # expected staging path, and produce well-formed XML where every scalar
        # placeholder is substituted, the table description is rendered, and one
        # Field_Character element exists per param. No "$" placeholder survives.
        setup, product, template_path, label_path = env

        label = OrbnumFilePDS4Label(setup, product)

        assert label.template == str(template_path)
        assert Path(label.name) == label_path
        assert label_path.exists()

        root = ElementTree.parse(label_path).getroot()
        assert root.tag == 'orbnum_table'
        assert root.findtext('file_name') == 'maven_orb_v01.orb'
        assert root.findtext('header_length') == '873'
        assert root.findtext('fields') == '3'

        table = root.find('Table_Character')
        assert table.findtext('description') == 'ORBNUM table'
        assert len(table.findall('Field_Character')) == 3

        # No placeholder may survive substitution.
        assert '$' not in label_path.read_text(encoding='utf-8')

    def test_empty_description_omits_description_element(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # When table_char_description is empty, the composite placeholder
        # renders to nothing, so Table_Character must contain no <description>
        # child and the overall document must still parse as valid XML.
        setup, product, _, label_path = env
        product.table_char_description = ''

        OrbnumFilePDS4Label(setup, product)

        table = ElementTree.parse(label_path).getroot().find('Table_Character')
        assert table.find('description') is None
        assert '$' not in label_path.read_text(encoding='utf-8')

    @pytest.mark.parametrize('end_of_line, eol_pds4, has_crlf', [
        ('LF', '\n', False),
        ('CRLF', '\r\n', True)])
    def test_end_of_line_is_honoured(
            self, env: tuple[MagicMock, MagicMock, Path, Path],
            end_of_line: str, eol_pds4: str, has_crlf: bool) -> None:
        # The written file must use the configured line ending: raw bytes
        # contain CRLF when end_of_line is CRLF and must not when it is LF.
        setup, product, _, label_path = env
        setup.end_of_line = end_of_line
        setup.eol_pds4 = eol_pds4

        OrbnumFilePDS4Label(setup, product)

        assert (b'\r\n' in label_path.read_bytes()) is has_crlf

    def test_label_registered_relative_to_staging(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # After writing, the label registers itself with setup.add_file using a
        # path relative to the staging directory (not an absolute path), called
        # exactly once.
        setup, product, _, label_path = env

        OrbnumFilePDS4Label(setup, product)

        setup.add_file.assert_called_once_with(
            str(label_path.relative_to(Path(setup.staging_directory))))

    def test_missing_template_raises_and_does_not_register(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # If the template file is missing, write_label opens the output file
        # first (creating an empty label) and then fails with FileNotFoundError
        # when it tries to read the template. Because the failure happens before
        # registration, setup.add_file must not be called and the output stays
        # empty.
        setup, product, template_path, label_path = env
        template_path.unlink()

        with pytest.raises(FileNotFoundError):
            OrbnumFilePDS4Label(setup, product)

        assert label_path.read_text(encoding='utf-8') == ''
        setup.add_file.assert_not_called()

    def test_malformed_template_is_written_without_validation(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # The writer performs no XML validation: given a structurally malformed
        # template it still substitutes placeholders, writes the file, and
        # registers it. We confirm FILE_NAME was rendered (no leftover "$"),
        # that the content is genuinely unparseable XML, and that add_file was
        # still called with the staging-relative path.
        setup, product, template_path, label_path = env
        template_path.write_text(
            '<orbnum_table>\n  <file_name>$FILE_NAME</file_name>\n',
            encoding='utf-8')

        OrbnumFilePDS4Label(setup, product)

        written = label_path.read_text(encoding='utf-8')
        assert 'maven_orb_v01.orb' in written
        assert '$FILE_NAME' not in written
        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written)
        setup.add_file.assert_called_once_with(
            str(label_path.relative_to(Path(setup.staging_directory))))
