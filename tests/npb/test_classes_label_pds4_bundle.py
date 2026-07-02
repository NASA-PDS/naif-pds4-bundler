"""Tests for the BundlePDS4Label class.

Two test classes are provided:

* TestBundlePDS4Label – unit tests that mock only the inherited
  ``PDSLabel.write_label`` so the constructor and the BUNDLE_MEMBER_ENTRIES
  building logic are exercised in isolation. ``PDSLabel.__init__`` is NOT
  mocked: it runs for real, so the readme product must expose every attribute
  the parent reads.

* TestBundlePDS4LabelIntegration – integration tests that exercise
  BundlePDS4Label together with the real ``PDSLabel.write_label`` logic,
  writing an actual XML label to a temp directory and asserting on its
  contents.

Why BundlePDS4Label differs from the other PDS4 label classes:

* ``product`` IS the readme; bundle identity comes from ``product.bundle``
  (``lid`` / ``vid`` / ``collections``), not from the product itself.
* ``self.name`` is never set by the constructor; the inherited writer assigns
  it from ``product.path`` verbatim because the path already ends in ``.xml``.
* ``START_TIME`` / ``STOP_TIME`` come from ``setup.increment_start`` /
  ``setup.increment_finish``, not from the product.
* ``BUNDLE_MEMBER_ENTRIES`` is built by concatenating one
  ``<Bundle_Member_Entry>`` per collection. ``collection.name`` selects the
  reference-type suffix; ``collection.updated`` selects Primary/Secondary.
  For the ``miscellaneous`` collection, the reference-type suffix also depends
  on ``setup.information_model_float`` vs the threshold 1011001000.0.
"""
import re
from pathlib import Path
from types import SimpleNamespace
import xml.etree.ElementTree as ElementTree
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_bundle import BundlePDS4Label

# Fully-qualified write_label target. Centralised so a relocation only needs
# one edit.
WRITE_LABEL_TARGET = (
    'pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label')


def _build_label(setup: MagicMock, readme: MagicMock) -> BundlePDS4Label:
    """Construct a ``BundlePDS4Label`` with ``write_label`` patched to a no-op.

    ``PDSLabel.__init__`` is left intact so its real attribute wiring runs.

    :param setup:  configured PDS4 Setup mock
    :param readme: readme product mock carrying the ``bundle`` aggregate
    :return: constructed label instance
    """
    with patch(WRITE_LABEL_TARGET, autospec=True):
        return BundlePDS4Label(setup, readme)


# ---------------------------------------------------------------------------
# Helpers – factories for the collaborator mocks
# ---------------------------------------------------------------------------

@pytest.fixture()
def helpers(base_helpers: SimpleNamespace) -> SimpleNamespace:
    """Specialise the generic factories for bundle labels.

    Extends ``base_helpers.make_setup`` with the bundle-specific fields and
    adds ``make_collection`` and ``make_readme`` factories.

    :param base_helpers: generic Setup/product factories from conftest
    :return: namespace with ``make_setup``, ``make_readme``, ``make_collection``
    """

    def _make_setup(end_of_line: str = 'LF', eol_pds4: str = '\n') -> SimpleNamespace:
        setup = base_helpers.make_setup(end_of_line=end_of_line,
                                        eol_pds4=eol_pds4)
        setup.increment_start = '2024-02-01T00:00:00Z'
        setup.increment_finish = '2024-02-28T23:59:59Z'
        setup.author_list = 'Doe, J.; Roe, R.'
        setup.doi = '10.17189/maven_spice'
        return setup

    def _make_collection(name: str = 'spice_kernels',
                         lid: str = 'urn:nasa:pds:maven_spice:spice_kernels',
                         vid: str = '1.0',
                         updated: object = True) -> SimpleNamespace:
        # SimpleNamespace exposes only the four attributes the constructor reads.
        # Any unexpected access raises AttributeError immediately rather than
        # returning a silent MagicMock.
        return SimpleNamespace(name=name, lid=lid, vid=vid, updated=updated)

    def _make_readme(staging_dir: Path,
                     name: str = 'bundle_maven_spice_v001.xml',
                     collections: list[SimpleNamespace] | None = None,
                     bundle_lid: str = 'urn:nasa:pds:maven_spice',
                     bundle_vid: str = '1.0') -> MagicMock:
        # readme.path ends in '.xml' so write_label uses it verbatim (the
        # else-branch of PDSLabel.write_label that handles the bundle case).
        staging_dir.mkdir(parents=True, exist_ok=True)
        readme = base_helpers.make_product(
            path=str(staging_dir / name),
            name=name,
            lid=bundle_lid,
            collection_name='miscellaneous')
        readme.bundle.lid = bundle_lid
        readme.bundle.vid = bundle_vid
        readme.bundle.collections = (
            [_make_collection()] if collections is None else collections)
        return readme

    return SimpleNamespace(make_setup=_make_setup,
                           make_readme=_make_readme,
                           make_collection=_make_collection)


# ---------------------------------------------------------------------------
# Module-level literals used by multiple tests
# ---------------------------------------------------------------------------

# The exact <Bundle_Member_Entry> XML block for a Primary spice_kernels
# collection rendered with xml_tab=1 and LF line endings. Written once as an
# independent literal so any drift in the source f-string is caught.
SPICE_KERNELS_PRIMARY_ENTRY = (
    ' <Bundle_Member_Entry>\n'
    '  <lidvid_reference>'
    'urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
    '  <member_status>Primary</member_status>\n'
    '  <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
    ' </Bundle_Member_Entry>\n')


# ===========================================================================
# Class 1 – Unit tests
# ===========================================================================

class TestBundlePDS4Label:
    """Unit tests for BundlePDS4Label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path: Path,
              helpers: SimpleNamespace) -> BundlePDS4Label:
        """Return a label built from a single default spice_kernels collection.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialised bundle factories
        :return: constructed label with write_label patched out
        """
        setup = helpers.make_setup()
        staging = tmp_path / 'staging'
        readme = helpers.make_readme(staging)
        return _build_label(setup, readme)

    # ------------------------------------------------------------------
    # Attribute assignments
    # ------------------------------------------------------------------

    def test_attribute_assignments(self, label: BundlePDS4Label) -> None:
        # Bundle identity comes from product.bundle, not from the product.
        assert label.BUNDLE_LID == 'urn:nasa:pds:maven_spice'
        assert label.BUNDLE_VID == '1.0'

        # Scalar metadata copied verbatim from setup and readme.
        assert label.AUTHOR_LIST == 'Doe, J.; Roe, R.'
        assert label.DOI == '10.17189/maven_spice'
        assert label.FILE_NAME == 'bundle_maven_spice_v001.xml'

        # Time coverage comes from setup.increment_*, not from the product.
        assert label.START_TIME == '2024-02-01T00:00:00Z'
        assert label.STOP_TIME == '2024-02-28T23:59:59Z'

        # The single default collection produces exactly one member entry.
        assert label.BUNDLE_MEMBER_ENTRIES == SPICE_KERNELS_PRIMARY_ENTRY

        # Per-collection scratch attrs reflect the last processed collection.
        assert label.COLL_NAME == 'spice_kernel'
        assert label.COLL_LIDVID == 'urn:nasa:pds:maven_spice:spice_kernels::1.0'
        assert label.COLL_STATUS == 'Primary'

    def test_template_path_is_bundle_template(
            self, label: BundlePDS4Label) -> None:
        # The template path is fixed to 'template_bundle.xml' under the
        # configured templates' directory.
        assert label.template == str(
            Path(label.setup.templates_directory) / 'template_bundle.xml')

    def test_constructor_does_not_set_name_attribute(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Unlike other PDS4 labels, BundlePDS4Label never assigns self.name.
        # PDSLabel.__init__ sets it to '' and write_label assigns the real path
        # later. With write_label patched, it must remain ''.
        label = _build_label(helpers.make_setup(),
                             helpers.make_readme(tmp_path / 'staging'))
        assert label.name == ''

    def test_constructor_stores_references_and_calls_write_label_once(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # setup and product (readme) must be stored by identity, and write_label
        # must be called exactly once with the label instance as argument.
        setup = helpers.make_setup()
        readme = helpers.make_readme(tmp_path / 'staging')

        with patch(WRITE_LABEL_TARGET, autospec=True) as mock_write:
            label = BundlePDS4Label(setup, readme)

        assert label.setup is setup
        assert label.product is readme
        mock_write.assert_called_once_with(label)

    # ------------------------------------------------------------------
    # get_*_reference_type overrides
    # ------------------------------------------------------------------

    def test_get_mission_reference_type(self, label: BundlePDS4Label) -> None:
        assert label.get_mission_reference_type() == 'bundle_to_investigation'

    def test_get_target_reference_type(self, label: BundlePDS4Label) -> None:
        assert label.get_target_reference_type() == 'bundle_to_target'

    # ------------------------------------------------------------------
    # BUNDLE_MEMBER_ENTRIES – per-collection rendering
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('coll_name, updated, expected_coll_name, expected_status, expected_entry', [
        ('spice_kernels', True, 'spice_kernel', 'Primary',
         ' <Bundle_Member_Entry>\n'
         '  <lidvid_reference>urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
         '  <member_status>Primary</member_status>\n'
         '  <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
         ' </Bundle_Member_Entry>\n'),
        ('spice_kernels', False, 'spice_kernel', 'Secondary',
         ' <Bundle_Member_Entry>\n'
         '  <lidvid_reference>urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
         '  <member_status>Secondary</member_status>\n'
         '  <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
         ' </Bundle_Member_Entry>\n'),
        ('document', True, 'document', 'Primary',
         ' <Bundle_Member_Entry>\n'
         '  <lidvid_reference>urn:nasa:pds:maven_spice:document::1.0</lidvid_reference>\n'
         '  <member_status>Primary</member_status>\n'
         '  <reference_type>bundle_has_document_collection</reference_type>\n'
         ' </Bundle_Member_Entry>\n'),
        ('document', False, 'document', 'Secondary',
         ' <Bundle_Member_Entry>\n'
         '  <lidvid_reference>urn:nasa:pds:maven_spice:document::1.0</lidvid_reference>\n'
         '  <member_status>Secondary</member_status>\n'
         '  <reference_type>bundle_has_document_collection</reference_type>\n'
         ' </Bundle_Member_Entry>\n')])
    def test_single_collection_entry_for_fixed_name_branches(
            self, tmp_path: Path, helpers: SimpleNamespace,
            coll_name: str, updated: bool, expected_coll_name: str,
            expected_status: str, expected_entry: str) -> None:
        # Covers the spice_kernels and document name branches and both values of
        # collection.updated. expected_entry is a handwritten literal, not a
        # formula that mirrors the source code.
        setup = helpers.make_setup()
        collection = helpers.make_collection(
            name=coll_name,
            lid=f'urn:nasa:pds:maven_spice:{coll_name}',
            updated=updated)
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[collection])

        label = _build_label(setup, readme)

        assert label.COLL_NAME == expected_coll_name
        assert label.COLL_STATUS == expected_status
        assert label.BUNDLE_MEMBER_ENTRIES == expected_entry

    @pytest.mark.parametrize(
        'information_model_float, expected_coll_name, updated,'
        ' expected_status, expected_entry', [
            (1011001000.0, 'miscellaneous', True, 'Primary',
             ' <Bundle_Member_Entry>\n'
             '  <lidvid_reference>urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
             '  <member_status>Primary</member_status>\n'
             '  <reference_type>bundle_has_miscellaneous_collection</reference_type>\n'
             ' </Bundle_Member_Entry>\n'),
            (1011001000.0, 'miscellaneous', False, 'Secondary',
             ' <Bundle_Member_Entry>\n'
             '  <lidvid_reference>urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
             '  <member_status>Secondary</member_status>\n'
             '  <reference_type>bundle_has_miscellaneous_collection</reference_type>\n'
             ' </Bundle_Member_Entry>\n'),
            (1016000000.0, 'miscellaneous', True, 'Primary',
             ' <Bundle_Member_Entry>\n'
             '  <lidvid_reference>urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
             '  <member_status>Primary</member_status>\n'
             '  <reference_type>bundle_has_miscellaneous_collection</reference_type>\n'
             ' </Bundle_Member_Entry>\n'),
            (1011000999.0, 'member', True, 'Primary',
             ' <Bundle_Member_Entry>\n'
             '  <lidvid_reference>urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
             '  <member_status>Primary</member_status>\n'
             '  <reference_type>bundle_has_member_collection</reference_type>\n'
             ' </Bundle_Member_Entry>\n'),
            (1010000000.0, 'member', False, 'Secondary',
             ' <Bundle_Member_Entry>\n'
             '  <lidvid_reference>urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
             '  <member_status>Secondary</member_status>\n'
             '  <reference_type>bundle_has_member_collection</reference_type>\n'
             ' </Bundle_Member_Entry>\n')])
    def test_miscellaneous_branch_depends_on_information_model_threshold(
            self, tmp_path: Path, helpers: SimpleNamespace,
            information_model_float: float, expected_coll_name: str,
            updated: bool, expected_status: str, expected_entry: str) -> None:
        # Covers the miscellaneous name branch. The threshold >= 1011001000.0
        # selects 'miscellaneous'; below it selects the legacy 'member'. Both
        # Primary and Secondary are parametrized to guarantee are both reached.
        # expected_entry is a handwritten literal, not a formula that mirrors
        # the source code.
        setup = helpers.make_setup()
        setup.information_model_float = information_model_float
        collection = helpers.make_collection(
            name='miscellaneous',
            lid='urn:nasa:pds:maven_spice:miscellaneous',
            updated=updated)
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[collection])

        label = _build_label(setup, readme)

        assert label.COLL_NAME == expected_coll_name
        assert label.COLL_STATUS == expected_status
        assert label.BUNDLE_MEMBER_ENTRIES == expected_entry

    def test_multiple_collections_are_concatenated_in_order(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Three collections must produce three entries in source order, with
        # independent statuses. The expected value is a handwritten literal.
        setup = helpers.make_setup()
        collections = [
            helpers.make_collection(
                name='spice_kernels',
                lid='urn:nasa:pds:maven_spice:spice_kernels', updated=True),
            helpers.make_collection(
                name='document',
                lid='urn:nasa:pds:maven_spice:document', updated=False),
            helpers.make_collection(
                name='miscellaneous',
                lid='urn:nasa:pds:maven_spice:miscellaneous', updated=True)]
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=collections)

        label = _build_label(setup, readme)

        assert label.BUNDLE_MEMBER_ENTRIES == (
            ' <Bundle_Member_Entry>\n'
            '  <lidvid_reference>'
            'urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
            '  <member_status>Primary</member_status>\n'
            '  <reference_type>'
            'bundle_has_spice_kernel_collection</reference_type>\n'
            ' </Bundle_Member_Entry>\n'
            ' <Bundle_Member_Entry>\n'
            '  <lidvid_reference>'
            'urn:nasa:pds:maven_spice:document::1.0</lidvid_reference>\n'
            '  <member_status>Secondary</member_status>\n'
            '  <reference_type>'
            'bundle_has_document_collection</reference_type>\n'
            ' </Bundle_Member_Entry>\n'
            ' <Bundle_Member_Entry>\n'
            '  <lidvid_reference>'
            'urn:nasa:pds:maven_spice:miscellaneous::1.0</lidvid_reference>\n'
            '  <member_status>Primary</member_status>\n'
            '  <reference_type>'
            'bundle_has_miscellaneous_collection</reference_type>\n'
            ' </Bundle_Member_Entry>\n')

    def test_empty_collections_list_leaves_member_entries_empty(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # An empty collections list must leave BUNDLE_MEMBER_ENTRIES as '' and
        # must never create the per-collection scratch attributes.
        label = _build_label(helpers.make_setup(),
                             helpers.make_readme(tmp_path / 'staging',
                                                 collections=[]))

        assert label.BUNDLE_MEMBER_ENTRIES == ''
        assert not hasattr(label, 'COLL_NAME')
        assert not hasattr(label, 'COLL_LIDVID')
        assert not hasattr(label, 'COLL_STATUS')

    @pytest.mark.parametrize('xml_tab, expected_entry', [
        (1, SPICE_KERNELS_PRIMARY_ENTRY),
        (2, '  <Bundle_Member_Entry>\n'
            '    <lidvid_reference>urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
            '    <member_status>Primary</member_status>\n'
            '    <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
            '  </Bundle_Member_Entry>\n'),
        (4, '    <Bundle_Member_Entry>\n'
            '        <lidvid_reference>urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
            '        <member_status>Primary</member_status>\n'
            '        <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
            '    </Bundle_Member_Entry>\n')])
    def test_member_entry_indentation_scales_with_xml_tab(
            self, tmp_path: Path, helpers: SimpleNamespace,
            xml_tab: int, expected_entry: str) -> None:
        # The wrapper element uses tab spaces; inner elements use 2*tab.
        # Each expected_entry is a handwritten literal.
        setup = helpers.make_setup()
        setup.xml_tab = xml_tab
        readme = helpers.make_readme(tmp_path / 'staging')

        label = _build_label(setup, readme)

        assert label.BUNDLE_MEMBER_ENTRIES == expected_entry

    @pytest.mark.parametrize('eol, eol_char, expected', [
        ('LF', '\n', SPICE_KERNELS_PRIMARY_ENTRY),
        ('CRLF', '\r\n',
         (' <Bundle_Member_Entry>\r\n'
          '  <lidvid_reference>'
          'urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\r\n'
          '  <member_status>Primary</member_status>\r\n'
          '  <reference_type>'
          'bundle_has_spice_kernel_collection</reference_type>\r\n'
          ' </Bundle_Member_Entry>\r\n'))])
    def test_member_entry_uses_end_of_line(
            self, tmp_path: Path, helpers: SimpleNamespace,
            eol, eol_char, expected) -> None:
        # Verifies that BUNDLE_MEMBER_ENTRIES is generated using the configured
        # end-of-line format (LF or CRLF), producing the expected XML output in
        # each case.
        setup = helpers.make_setup(end_of_line=eol, eol_pds4=eol_char)
        readme = helpers.make_readme(tmp_path / 'staging')

        label = _build_label(setup, readme)

        assert label.BUNDLE_MEMBER_ENTRIES == expected

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_unknown_collection_name_raises_value_error(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # An unrecognised collection.name fails fast with a descriptive
        # ValueError instead of silently reading stale/missing scratch state.
        unknown = helpers.make_collection(
            name='unexpected_collection',
            lid='urn:nasa:pds:maven_spice:unexpected', updated=True)
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[unknown])

        expected_message = (
            'NPB bug: the collection name unexpected_collection is not '
            'supported in PDS4 Bundle Label.')
        with pytest.raises(ValueError, match=f'^{re.escape(expected_message)}$'):
            _build_label(helpers.make_setup(), readme)

    def test_unknown_collection_name_after_known_collection_raises_value_error(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # An unrecognised collection.name following a recognised one must
        # still raise immediately, rather than silently reusing the
        # previous iteration's COLL_NAME/COLL_LIDVID/COLL_STATUS to emit a
        # duplicate entry.
        known = helpers.make_collection(
            name='document',
            lid='urn:nasa:pds:maven_spice:document', updated=False)
        unknown = helpers.make_collection(
            name='unexpected_collection',
            lid='urn:nasa:pds:maven_spice:unexpected', updated=True)
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[known, unknown])

        expected_message = (
            'NPB bug: the collection name unexpected_collection is not '
            'supported in PDS4 Bundle Label.')
        with pytest.raises(ValueError, match=f'^{re.escape(expected_message)}$'):
            _build_label(helpers.make_setup(), readme)

    @pytest.mark.parametrize('updated_value, expected_status', [
        (True, 'Primary'),
        (1, 'Primary'),
        ('yes', 'Primary'),
        (['item'], 'Primary'),
        (False, 'Secondary'),
        (0, 'Secondary'),
        ('', 'Secondary'),
        ([], 'Secondary'),
        (None, 'Secondary')])
    def test_collection_updated_is_evaluated_as_truthiness(
            self, tmp_path: Path, helpers: SimpleNamespace,
            updated_value: object, expected_status: str) -> None:
        # collection.updated is tested with a bare 'if', not '== True'.
        # Any truthy value gives Primary; any falsy value gives Secondary.
        collection = helpers.make_collection(name='spice_kernels',
                                             updated=updated_value)
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[collection])

        label = _build_label(helpers.make_setup(), readme)

        assert label.COLL_STATUS == expected_status

    @pytest.mark.parametrize('setup_attribute, value, label_attribute', [
        ('author_list', '', 'AUTHOR_LIST'),
        ('author_list', 'Solo, H.', 'AUTHOR_LIST'),
        ('doi', '', 'DOI'),
        ('doi', '10.0/x', 'DOI'),
        ('increment_start', 'not-a-valid-datetime', 'START_TIME'),
        ('increment_finish', '', 'STOP_TIME')])
    def test_setup_values_are_copied_without_validation(
            self, tmp_path: Path, helpers: SimpleNamespace,
            setup_attribute: str, value: str, label_attribute: str) -> None:
        # The constructor copies setup values verbatim; the caller is
        # responsible for validation.
        setup = helpers.make_setup()
        setattr(setup, setup_attribute, value)
        readme = helpers.make_readme(tmp_path / 'staging')

        label = _build_label(setup, readme)

        assert getattr(label, label_attribute) == value

    @pytest.mark.parametrize('bundle_lid, bundle_vid', [
        ('urn:nasa:pds:maven_spice', '1.0'),
        ('urn:nasa:pds:other_spice', '9.9'),
        ('', '')])
    def test_bundle_identity_is_read_from_product_bundle_not_product(
            self, tmp_path: Path, helpers: SimpleNamespace,
            bundle_lid: str, bundle_vid: str) -> None:
        # BUNDLE_LID and BUNDLE_VID come from product.bundle, not from
        # product directly. This is the main structural oddity of this label.
        readme = helpers.make_readme(tmp_path / 'staging',
                                     bundle_lid=bundle_lid,
                                     bundle_vid=bundle_vid)

        label = _build_label(helpers.make_setup(), readme)

        assert label.BUNDLE_LID == bundle_lid
        assert label.BUNDLE_VID == bundle_vid

    def test_file_name_is_readme_name_verbatim_without_truncation(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # FILE_NAME is readme.name verbatim. Unlike other PDS4 labels that
        # truncate at the first dot, this class does a direct assignment.
        readme = helpers.make_readme(tmp_path / 'staging',
                                     name='bundle_maven_spice_v002.0.xml')

        label = _build_label(helpers.make_setup(), readme)

        assert label.FILE_NAME == 'bundle_maven_spice_v002.0.xml'

    def test_coll_lidvid_concatenates_lid_and_vid_verbatim(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # COLL_LIDVID is collection.lid + '::' + collection.vid with no
        # normalisation. An unusual vid proves no transformation occurs.
        collection = helpers.make_collection(
            name='spice_kernels',
            lid='urn:nasa:pds:maven_spice:spice_kernels',
            vid='3.14')
        readme = helpers.make_readme(tmp_path / 'staging',
                                     collections=[collection])

        label = _build_label(helpers.make_setup(), readme)

        assert label.COLL_LIDVID == 'urn:nasa:pds:maven_spice:spice_kernels::3.14'


# ===========================================================================
# Class 2 – Integration tests
# ===========================================================================

# Minimal template that exercises every bundle placeholder. The
# $BUNDLE_MEMBER_ENTRIES placeholder is immediately concatenated with the
# closing tag on the same physical file line so that write_label (which
# rstrips each template line before substitution) injects the multiline
# block without producing extra blank lines.
TEMPLATE_CONTENT = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<bundle>\n'
    '  <logical_identifier>$BUNDLE_LID</logical_identifier>\n'
    '  <version_id>$BUNDLE_VID</version_id>\n'
    '  <author_list>$AUTHOR_LIST</author_list>\n'
    '  <start_date_time>$START_TIME</start_date_time>\n'
    '  <stop_date_time>$STOP_TIME</stop_date_time>\n'
    '  <file_name>$FILE_NAME</file_name>\n'
    '  <doi>$DOI</doi>\n'
    '  <Bundle_Member_Entries>\n'
    '$BUNDLE_MEMBER_ENTRIES'
    '  </Bundle_Member_Entries>\n'
    '</bundle>\n')


class TestBundlePDS4LabelIntegration:
    """Integration tests for BundlePDS4Label + PDSLabel.write_label."""

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path: Path, helpers: SimpleNamespace
            ) -> tuple[MagicMock, MagicMock, Path, Path]:
        """Prepare a real template file and staging directory.

        :param tmp_path: pytest temporary directory
        :param helpers:  specialised bundle factories
        :return: (setup, readme, template_path, expected_label_path)
        """
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        template_path = templates_dir / 'template_bundle.xml'
        template_path.write_text(TEMPLATE_CONTENT, encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        readme = helpers.make_readme(staging_dir)
        return setup, readme, template_path, Path(readme.path)

    # ------------------------------------------------------------------
    # File creation and content
    # ------------------------------------------------------------------

    def test_label_file_is_created_from_template(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # Verify file-creation contracts: template resolution, label.name
        # assignment, file existence, and absence of unreplaced placeholders.
        # Semantic field values are verified in test_label_file_is_valid_xml.
        setup, readme, template_path, label_path = env

        label = BundlePDS4Label(setup, readme)

        assert label.template == str(template_path)
        assert Path(label.name) == label_path
        assert label_path.exists()
        assert '$' not in label_path.read_text(encoding='utf-8')

    def test_label_file_is_valid_xml(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # The rendered file must be well-formed XML with every placeholder
        # substituted by the correct value from the label state.
        setup, readme, _, label_path = env

        BundlePDS4Label(setup, readme)

        expected = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<bundle>\n'
                    '  <logical_identifier>urn:nasa:pds:maven_spice</logical_identifier>\n'
                    '  <version_id>1.0</version_id>\n'
                    '  <author_list>Doe, J.; Roe, R.</author_list>\n'
                    '  <start_date_time>2024-02-01T00:00:00Z</start_date_time>\n'
                    '  <stop_date_time>2024-02-28T23:59:59Z</stop_date_time>\n'
                    '  <file_name>bundle_maven_spice_v001.xml</file_name>\n'
                    '  <doi>10.17189/maven_spice</doi>\n'
                    '  <Bundle_Member_Entries>\n'
                    ' <Bundle_Member_Entry>\n'
                    '  <lidvid_reference>urn:nasa:pds:maven_spice:spice_kernels::1.0</lidvid_reference>\n'
                    '  <member_status>Primary</member_status>\n'
                    '  <reference_type>bundle_has_spice_kernel_collection</reference_type>\n'
                    ' </Bundle_Member_Entry>\n'
                    '  </Bundle_Member_Entries></bundle>\n')

        assert label_path.read_text(encoding="utf-8") == expected

    def test_label_written_with_lf_contains_no_crlf(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # With end_of_line='LF' the raw file must contain LF and no CRLF.
        setup, readme, _, label_path = env
        setup.end_of_line = 'LF'
        setup.eol_pds4 = '\n'

        BundlePDS4Label(setup, readme)
        raw = label_path.read_bytes()

        assert b'\r\n' not in raw
        assert b'\n' in raw

    def test_label_written_with_crlf_contains_crlf_sequences(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # With end_of_line='CRLF' the raw file must contain CRLF sequences.
        setup, readme, _, label_path = env
        setup.end_of_line = 'CRLF'
        setup.eol_pds4 = '\r\n'

        BundlePDS4Label(setup, readme)
        raw = label_path.read_bytes()

        assert b'\r\n' in raw

    def test_multiple_collections_render_all_member_entries(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # Every collection must produce a member entry in the written label,
        # in source order and with the correct reference type and status.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()
        (templates_dir / 'template_bundle.xml').write_text(
            TEMPLATE_CONTENT, encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        collections = [
            helpers.make_collection(
                name='spice_kernels',
                lid='urn:nasa:pds:maven_spice:spice_kernels', updated=True),
            helpers.make_collection(
                name='document',
                lid='urn:nasa:pds:maven_spice:document', updated=False)]
        readme = helpers.make_readme(staging_dir, collections=collections)

        BundlePDS4Label(setup, readme)

        entries = ElementTree.parse(
            Path(readme.path)).getroot().find('Bundle_Member_Entries')

        assert len(entries.findall('Bundle_Member_Entry')) == 2
        assert [e.findtext('reference_type')
                for e in entries.findall('Bundle_Member_Entry')] == [
                   'bundle_has_spice_kernel_collection',
                   'bundle_has_document_collection']
        assert [e.findtext('member_status')
                for e in entries.findall('Bundle_Member_Entry')] == [
                   'Primary', 'Secondary']

    def test_stray_coll_placeholder_in_template_is_substituted_by_writer(
            self, tmp_path: Path, helpers: SimpleNamespace) -> None:
        # TODO: BUG, it substitutes every public string attribute of the label
        #       whose name appears in a template line, including the scratch
        #       attrs COLL_NAME, COLL_LIDVID, COLL_STATUS. These are
        #       implementation details of BundlePDS4Label and not part of the
        #       public template contract. A template containing $COLL_NAME would
        #       silently receive the last collection's value.
        templates_dir = tmp_path / 'templates'
        staging_dir = tmp_path / 'staging'
        templates_dir.mkdir()
        staging_dir.mkdir()

        (templates_dir / 'template_bundle.xml').write_text(
            '<bundle>\n'
            '  <leaked>$COLL_NAME</leaked>\n'
            '</bundle>\n',
            encoding='utf-8')

        setup = helpers.make_setup()
        setup.templates_directory = str(templates_dir)
        setup.staging_directory = str(staging_dir)

        collections = [
            helpers.make_collection(
                name='spice_kernels',
                lid='urn:nasa:pds:maven_spice:spice_kernels', updated=True),
            helpers.make_collection(
                name='document',
                lid='urn:nasa:pds:maven_spice:document', updated=True)]
        readme = helpers.make_readme(staging_dir, collections=collections)

        BundlePDS4Label(setup, readme)
        written = Path(readme.path).read_text(encoding='utf-8')

        # The leaked value is the last collection's COLL_NAME ('document').
        assert '<leaked>document</leaked>' in written
        assert '$COLL_NAME' not in written

    # ------------------------------------------------------------------
    # setup.add_file side effect
    # ------------------------------------------------------------------

    def test_add_file_called_with_staging_relative_label_path(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # write_label must register the label using its path relative to the
        # staging directory, not as an absolute path.
        setup, readme, _, _ = env

        BundlePDS4Label(setup, readme)

        setup.add_file.assert_called_once_with('bundle_maven_spice_v001.xml')

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_missing_template_raises_file_not_found_error(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # A missing template must raise FileNotFoundError. The output file is
        # created empty before the template is opened, so it exists but is
        # empty. add_file must not be called.
        setup, readme, template_path, label_path = env
        template_path.unlink()

        with pytest.raises(FileNotFoundError):
            BundlePDS4Label(setup, readme)

        assert label_path.exists()
        assert label_path.read_text(encoding='utf-8') == ''
        setup.add_file.assert_not_called()

    def test_malformed_template_is_written_without_xml_validation(
            self, env: tuple[MagicMock, MagicMock, Path, Path]) -> None:
        # write_label does not validate XML; a malformed template is rendered
        # and registered. The caller is responsible for template correctness.
        setup, readme, template_path, label_path = env
        template_path.write_text('<bundle>\n'
                                 '  <file_name>$FILE_NAME</file_name>\n',
                                 encoding='utf-8')

        BundlePDS4Label(setup, readme)

        written = label_path.read_text(encoding='utf-8')
        assert '<file_name>bundle_maven_spice_v001.xml</file_name>' in written
        assert '$FILE_NAME' not in written

        with pytest.raises(ElementTree.ParseError):
            ElementTree.fromstring(written)

        setup.add_file.assert_called_once_with('bundle_maven_spice_v001.xml')
