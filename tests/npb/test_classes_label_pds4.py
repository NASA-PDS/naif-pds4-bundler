"""
Tests for PDS4Label class.

PDS4Label carries everything that used to live behind
``if setup.pds_version == "4":`` guards inside PDSLabel.__init__, plus the
three PDS4-only context-product methods (get_missions/get_observers/
get_targets) and the default reference-type values. See
test_classes_label.py for the version-agnostic PDSLabel coverage and
test_classes_label_pds3.py for the (currently much thinner) PDS3Label
coverage.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pds.naif_pds4_bundler.classes.label.pds4_label import PDS4Label

# Patch target — resolved to where the name is looked up inside pds4_label.py
_PATCH_HANDLE_ERROR = "pds.naif_pds4_bundler.classes.label.pds4_label.handle_npb_error"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------
# make_context_products/make_product/make_setup_pds4 come from conftest.py's
# label_test_helpers fixture, shared with test_classes_label.py.

@pytest.fixture
def setup_pds4(label_test_helpers):
    return label_test_helpers.make_setup_pds4()


@pytest.fixture
def product(label_test_helpers):
    return label_test_helpers.make_product()


# ===========================================================================
# PDS4Label.__init__
# ===========================================================================

class TestPDS4LabelInit:
    """Covers PDS4Label.__init__ – all branches moved from PDSLabel."""

    @staticmethod
    @pytest.fixture
    def mock_class_methods(mocker):
        # Mocks all three methods at once
        mocker.patch('pds.naif_pds4_bundler.classes.label.pds4_label.PDS4Label.get_missions',
                     return_value='MockedMission')
        mocker.patch('pds.naif_pds4_bundler.classes.label.pds4_label.PDS4Label.get_observers',
                     return_value='MockedObserver')
        mocker.patch('pds.naif_pds4_bundler.classes.label.pds4_label.PDS4Label.get_targets',
                     return_value='MockedTarget')

    def test_pds4_context_from_collection_bundle(self, setup_pds4, product):
        """context products from collection.bundle"""
        label = PDS4Label(setup_pds4, product)
        assert label.setup is setup_pds4
        assert label.product is product
        assert label.name == ""

    def test_pds4_context_falls_back_to_product_bundle(self, mock_class_methods, setup_pds4, product):
        """Construction does not raise when collection.bundle.context_products
        is falsy. The internal try/except silently falls back to
        product.bundle.context_products; whether that fallback value is
        used correctly is covered separately by each of get_missions/
        get_observers/get_targets' own test_context_fallback_to_product_bundle
        test.
        """
        product.collection.bundle.context_products = []
        PDS4Label(setup_pds4, product)

    def test_pds4_context_attribute_error_falls_back(self, setup_pds4, product):
        """Construction does not raise when product.collection.bundle is
        entirely inaccessible (AttributeError); the try/except in __init__
        swallows it and falls back to product.bundle.context_products.
        """
        product.collection = MagicMock(spec=[])
        PDS4Label(setup_pds4, product)

    def test_pds4_single_mission_name(self, mock_class_methods, setup_pds4, product):
        label = PDS4Label(setup_pds4, product)
        assert label.PDS4_MISSION_NAME == "TestMission"

    @pytest.mark.parametrize("secondary_missions, expected_name",[
        (["OtherMission"], "TestMission and OtherMission"),
        (["MissionB", "MissionC"], "TestMission, MissionB, and MissionC"),
    ])
    def test_pds4_multiple_mission_name(self, mock_class_methods, setup_pds4, product, secondary_missions, expected_name):
        setup_pds4.secondary_missions = secondary_missions
        label = PDS4Label(setup_pds4, product)
        assert label.PDS4_MISSION_NAME == expected_name

    def test_pds4_single_observer_name(self, mock_class_methods, setup_pds4, product):
        label = PDS4Label(setup_pds4, product)
        assert label.PDS4_OBSERVER_NAME == "TestObserver spacecraft and its"

    @pytest.mark.parametrize("secondary_observer, expected_name",[
        (["OtherObserver"], "TestObserver and OtherObserver spacecraft and their"),
        (["ObsB", "ObsC"], "TestObserver, ObsB, and ObsC spacecraft and their"),
    ])
    def test_pds4_multiple_observer_name(self, mock_class_methods, setup_pds4, product, secondary_observer, expected_name):
        setup_pds4.secondary_observers = secondary_observer
        label = PDS4Label(setup_pds4, product)
        assert label.PDS4_OBSERVER_NAME == expected_name

    @pytest.mark.parametrize("eol, expected_eol_name",[
        ('LF', 'Line-Feed'),
        ('CRLF', 'Carriage-Return Line-Feed')
    ])
    def test_pds4_end_of_line(self, label_test_helpers, product, eol, expected_eol_name):
        setup = label_test_helpers.make_setup_pds4(end_of_line=eol)
        label = PDS4Label(setup, product)
        assert label.END_OF_LINE == expected_eol_name

    def test_pds4_end_of_line_invalid(self, label_test_helpers, product):
        """end_of_line is invalid (neither CRLF nor LF)"""
        setup = label_test_helpers.make_setup_pds4(end_of_line="CR")
        with pytest.raises(RuntimeError, match=r'End of Line provided via configuration '
                                               r'is not CRLF nor LF\.'):
            PDS4Label(setup, product)

    # TODO: The following two test cases demonstrate an issue:
    #       If they are not a list, the code to set up PDS4_MISSION_NAME
    #       and PDS4_OBSERVER_NAME, results in a list of letters.
    def test_pds4_secondary_missions_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = "SingleMission"
        label = PDS4Label(setup_pds4, product)
        assert label.missions == ['TestMission', 'SingleMission']
        # TODO: This is a bug!!!!
        assert 'TestMission, S, i, n, g, l, e, M, i, s, s, i, o, and n' == label.PDS4_MISSION_NAME

    def test_pds4_secondary_observers_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_observers = 'SingleObserver'
        label = PDS4Label(setup_pds4, product)
        assert label.observers == ['TestObserver', 'SingleObserver']
        # TODO: This is a bug!!!
        assert 'TestObserver, S, i, n, g, l, e, O, b, s, e, r, v, e, and r spacecraft and their' == label.PDS4_OBSERVER_NAME

    def test_pds4_sets_missions_targets_observers(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = ["MissionB", "MissionC"]
        setup_pds4.secondary_observers = ["ObsB", "ObsC"]
        setup_pds4.secondary_targets = ["TargetB", "TargetC"]

        # Since the mock is called, the values of the MISSIONS,
        # OBSERVERS and TARGETS should be the ones provided as return_value
        # in the mock.
        label = PDS4Label(setup_pds4, product)
        assert label.MISSIONS == 'MockedMission'
        assert label.OBSERVERS == 'MockedObserver'
        assert label.TARGETS == 'MockedTarget'


# ===========================================================================
# PDS4Label._resolve_context_products
# ===========================================================================

class TestPDS4LabelResolveContextProducts:
    """Covers the one behavior not already exercised indirectly by the
    get_missions/get_observers/get_targets fallback tests: an empty-but-
    present context_products list is returned as-is, not treated as a
    reason to fall back to product.bundle.context_products."""

    def test_empty_list_does_not_trigger_fallback(self):
        label = PDS4Label.__new__(PDS4Label)
        product = MagicMock()
        product.collection.bundle.context_products = []
        product.bundle.context_products = ["should not be used"]
        label.product = product

        assert label._resolve_context_products() == []


# ===========================================================================
# PDS4Label._match_context_entry
# ===========================================================================
# Pure static helper shared by get_missions/get_observers/get_targets — no
# PDS4Label instance needed to exercise it.

class TestPDS4LabelMatchContextEntry:
    """Covers PDS4Label._match_context_entry – all branches."""

    @pytest.mark.parametrize(
        "context_products, name, valid_types, case_insensitive, expected",
        [
            pytest.param(
                [{"name": ["Mars"], "type": ["Target"], "lidvid": "urn:x:mars::1.0"}],
                "Mars", ("Target",), False, ("urn:x:mars", "Target"),
                id="match_by_name_and_type",
            ),
            pytest.param(
                [{"name": ["Mars"], "type": ["Planet"], "lidvid": "urn:x:mars::1.0"}],
                "Mars", None, False, ("urn:x:mars", "Planet"),
                id="no_type_filter_accepts_any_type",
            ),
            pytest.param(
                [{"name": ["MARS"], "type": ["Target"], "lidvid": "urn:x:mars::1.0"}],
                "mars", None, True, ("urn:x:mars", "Target"),
                id="case_insensitive_match",
            ),
            pytest.param(
                [{"name": ["MARS"], "type": ["Target"], "lidvid": "urn:x:mars::1.0"}],
                "mars", None, False, (None, None),
                id="case_sensitive_by_default_no_match",
            ),
            pytest.param(
                [{"name": ["Mars"], "type": ["Planet"], "lidvid": "urn:x:mars::1.0"}],
                "Mars", ("Target",), False, (None, None),
                id="name_matches_but_type_not_in_valid_types",
            ),
            pytest.param(
                [{"name": ["Venus"], "type": ["Target"], "lidvid": "urn:x:venus::1.0"}],
                "Mars", ("Target",), False, (None, None),
                id="no_match_returns_none_none",
            ),
            pytest.param(
                [], "Mars", None, False, (None, None),
                id="empty_context_products_returns_none_none",
            ),
        ],
    )
    def test_match_context_entry(
        self, context_products, name, valid_types, case_insensitive, expected
    ):
        result = PDS4Label._match_context_entry(
            context_products, name, valid_types=valid_types, case_insensitive=case_insensitive
        )
        assert result == expected

    def test_multiple_matches_last_one_wins(self):
        """Mirrors the pre-existing getters: the matching loop never
        ``break``s, so if more than one entry matches, the last one in
        the list determines the result."""
        ctx = [
            {"name": ["Mars"], "type": ["Target"], "lidvid": "urn:x:mars-old::1.0"},
            {"name": ["Mars"], "type": ["Target"], "lidvid": "urn:x:mars-new::2.0"},
        ]
        lid, type_ = PDS4Label._match_context_entry(ctx, "Mars", valid_types=("Target",))
        assert lid == "urn:x:mars-new"


# ===========================================================================
# PDS4Label._render_context_entry
# ===========================================================================
# Pure static helper shared by get_missions/get_observers/get_targets — no
# PDS4Label instance needed to exercise it.

class TestPDS4LabelRenderContextEntry:
    """Covers PDS4Label._render_context_entry – all branches."""

    @pytest.mark.parametrize(
        "eol, tab, tag, indent, name, type_, lid, reference_type, expected",
        [
            pytest.param(
                "\r\n", 2, "Investigation_Area", 2,
                "TestMission", "Mission", "urn:nasa:pds:testmission", "data_to_investigation",
                '    <Investigation_Area>\r\n'
                '      <name>TestMission</name>\r\n'
                '      <type>Mission</type>\r\n'
                '      <Internal_Reference>\r\n'
                '        <lid_reference>urn:nasa:pds:testmission</lid_reference>\r\n'
                '        <reference_type>data_to_investigation</reference_type>\r\n'
                '      </Internal_Reference>\r\n'
                '    </Investigation_Area>\r\n',
                id="indent_2_matches_investigation_area_layout",
            ),
            pytest.param(
                "\r\n", 2, "Observing_System_Component", 3,
                "TestObserver", "Spacecraft", "urn:x:testobserver", "is_instrument_host",
                '      <Observing_System_Component>\r\n'
                '        <name>TestObserver</name>\r\n'
                '        <type>Spacecraft</type>\r\n'
                '        <Internal_Reference>\r\n'
                '          <lid_reference>urn:x:testobserver</lid_reference>\r\n'
                '          <reference_type>is_instrument_host</reference_type>\r\n'
                '        </Internal_Reference>\r\n'
                '      </Observing_System_Component>\r\n',
                id="indent_3_matches_observing_system_component_layout",
            ),
            pytest.param(
                "\n", 1, "Target_Identification", 2,
                "TestTarget", "Planet", "urn:x:testtarget", "data_to_target",
                '  <Target_Identification>\n'
                '   <name>TestTarget</name>\n'
                '   <type>Planet</type>\n'
                '   <Internal_Reference>\n'
                '    <lid_reference>urn:x:testtarget</lid_reference>\n'
                '    <reference_type>data_to_target</reference_type>\n'
                '   </Internal_Reference>\n'
                '  </Target_Identification>\n',
                id="different_eol_and_tab_are_honored_not_hardcoded",
            ),
        ],
    )
    def test_render_context_entry(
        self, eol, tab, tag, indent, name, type_, lid, reference_type, expected
    ):
        result = PDS4Label._render_context_entry(
            eol, tab, tag, indent, name, type_, lid, reference_type
        )
        assert result == expected


# ===========================================================================
# PDS4Label.get_missions
# ===========================================================================

class TestPDS4LabelGetMissions:
    """Covers PDS4Label.get_missions – all branches."""

    @pytest.fixture
    def label_for(self, label_test_helpers):
        """Factory fixture: returns a callable that builds a bare label."""
        def _build(missions, context_products=None, fallback_to_bundle=False):
            setup = label_test_helpers.make_setup_pds4()
            product = label_test_helpers.make_product()
            ctx = context_products or label_test_helpers.make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])  # no .bundle
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDS4Label.__new__(PDS4Label)
            label.setup = setup
            label.product = product
            label.missions = missions if isinstance(missions, list) else [missions]
            return label
        return _build

    @pytest.mark.parametrize('missions, expected', [
        (['TestMission'], '    <Investigation_Area>\r\n'
                          '      <name>TestMission</name>\r\n'
                          '      <type>Mission</type>\r\n'
                          '      <Internal_Reference>\r\n'
                          '        <lid_reference>urn:nasa:pds:testmission</lid_reference>\r\n'
                          '        <reference_type>data_to_investigation</reference_type>\r\n'
                          '      </Internal_Reference>\r\n'
                          '    </Investigation_Area>\r\n'),
        ('TestMission', '    <Investigation_Area>\r\n'
                        '      <name>TestMission</name>\r\n'
                        '      <type>Mission</type>\r\n'
                        '      <Internal_Reference>\r\n'
                        '        <lid_reference>urn:nasa:pds:testmission</lid_reference>\r\n'
                        '        <reference_type>data_to_investigation</reference_type>\r\n'
                        '      </Internal_Reference>\r\n'
                        '    </Investigation_Area>\r\n')
    ])
    def test_mission(self, label_for, missions, expected):
        label = label_for(missions)
        label.missions = missions
        result = label.get_missions()
        assert result == expected

    def test_context_falls_back_to_product_bundle(self, label_for):
        result = label_for(["TestMission"], fallback_to_bundle=True).get_missions()
        assert "TestMission" in result

    def test_empty_mission_name_skipped_calls_error(self, label_for, mocker):
        """A falsy mission entry (empty string) must be skipped."""
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for([""]).get_missions()
        mock_err.assert_called()

    def test_other_investigation_type_accepted(self, label_for):
        ctx = [
            {
                "name": ["TestMission"],
                "type": ["Other Investigation"],
                "lidvid": "urn:nasa:pds:testmission::1.0",
            }
        ]
        result = label_for(["TestMission"], context_products=ctx).get_missions()
        assert result == ('    <Investigation_Area>\r\n'
                          '      <name>TestMission</name>\r\n'
                          '      <type>Other Investigation</type>\r\n'
                          '      <Internal_Reference>\r\n'
                          '        <lid_reference>urn:nasa:pds:testmission</lid_reference>\r\n'
                          '        <reference_type>data_to_investigation</reference_type>\r\n'
                          '      </Internal_Reference>\r\n'
                          '    </Investigation_Area>\r\n')

    def test_no_lid_found_calls_handle_npb_error(self, label_for, mocker):
        """No context product matches → mission_lid never set → handle_npb_error."""
        ctx = [
            {
                "name": ["Different"],
                "type": ["Mission"],
                "lidvid": "urn:nasa:pds:different::1.0",
            }
        ]
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for(["TestMission"], context_products=ctx).get_missions()
        mock_err.assert_called()


# ===========================================================================
# PDS4Label.get_observers
# ===========================================================================

class TestPDS4LabelGetObservers:
    """Covers PDS4Label.get_observers – all branches."""

    @pytest.fixture
    def label_for(self, label_test_helpers):
        """Factory fixture: builds a bare label with given observers."""
        def _build(observers, context_products=None, fallback_to_bundle=False):
            setup = label_test_helpers.make_setup_pds4()
            product = label_test_helpers.make_product()
            ctx = context_products or label_test_helpers.make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDS4Label.__new__(PDS4Label)
            label.setup = setup
            label.product = product
            label.observers = observers if isinstance(observers, list) else [observers]
            return label
        return _build

    def test_single_observer_spacecraft(self, label_for):
        result = label_for(["TestObserver"]).get_observers()
        assert "TestObserver" in result
        assert "Observing_System_Component" in result

    def test_observers_not_a_list_wrapped(self, label_for):
        label = label_for("TestObserver")
        label.observers = "TestObserver"  # scalar
        assert "TestObserver" in label.get_observers()

    def test_context_fallback_to_product_bundle(self, label_for):
        result = label_for(["TestObserver"], fallback_to_bundle=True).get_observers()
        assert "TestObserver" in result

    def test_rover_type_accepted(self, label_for):
        ctx = [{"name": ["TestObserver"], "type": ["Rover"], "lidvid": "urn:x::1.0"}]
        assert "Rover" in label_for(["TestObserver"], ctx).get_observers()

    def test_lander_type_accepted(self, label_for):
        ctx = [{"name": ["TestObserver"], "type": ["Lander"], "lidvid": "urn:x::1.0"}]
        assert "Lander" in label_for(["TestObserver"], ctx).get_observers()

    def test_host_type_accepted(self, label_for):
        ctx = [{"name": ["TestObserver"], "type": ["Host"], "lidvid": "urn:x::1.0"}]
        assert "Host" in label_for(["TestObserver"], ctx).get_observers()

    def test_comma_in_observer_name_strips_suffix(self, label_for):
        """Observer names like 'Name, suffix' → only 'Name' used for look-up."""
        ctx = [{"name": ["TestObserver"], "type": ["Spacecraft"], "lidvid": "urn:x::1.0"}]
        assert "TestObserver" in label_for(["TestObserver, extra"], ctx).get_observers()

    def test_empty_observer_skipped_calls_error(self, label_for, mocker):
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for([""]).get_observers()
        mock_err.assert_called()

    def test_no_lid_calls_handle_npb_error(self, label_for, mocker):
        ctx = [{"name": ["NoMatch"], "type": ["Spacecraft"], "lidvid": "urn:x::1.0"}]
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for(["TestObserver"], ctx).get_observers()
        mock_err.assert_called()

    def test_trailing_eol_appended(self, label_for):
        assert label_for(["TestObserver"]).get_observers().endswith("\r\n")


# ===========================================================================
# PDS4Label.get_targets
# ===========================================================================

class TestPDS4LabelGetTargets:
    """Covers PDS4Label.get_targets – all branches."""

    @pytest.fixture
    def label_for(self, label_test_helpers):
        """Factory fixture: builds a bare label with given targets."""
        def _build(targets, context_products=None, fallback_to_bundle=False):
            setup = label_test_helpers.make_setup_pds4()
            product = label_test_helpers.make_product()
            ctx = context_products or label_test_helpers.make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDS4Label.__new__(PDS4Label)
            label.setup = setup
            label.product = product
            label.targets = targets if isinstance(targets, list) else [targets]
            return label
        return _build

    def test_single_target(self, label_for):
        result = label_for(["TestTarget"]).get_targets()
        assert "TestTarget" in result
        assert "Target_Identification" in result

    def test_targets_not_a_list_wrapped(self, label_for):
        label = label_for("TestTarget")
        label.targets = "TestTarget"  # scalar
        assert "TestTarget" in label.get_targets()

    def test_context_fallback_to_product_bundle(self, label_for):
        result = label_for(["TestTarget"], fallback_to_bundle=True).get_targets()
        assert "TestTarget" in result

    def test_case_insensitive_name_match(self, label_for):
        ctx = [{"name": ["TESTTARGET"], "type": ["planet"], "lidvid": "urn:x::1.0"}]
        assert "testtarget" in label_for(["testtarget"], ctx).get_targets()

    def test_no_match_renders_none_without_raising(self, label_for, mocker):
        """Characterizes a known gap (tracked separately, not fixed here):
        unlike get_missions/get_observers, a target with no matching
        context product does not call handle_npb_error — lid/type fall
        through as the literal string "None" instead. This pins the
        current behavior, so it can't change silently; it is not an
        endorsement of it."""
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        ctx = [{"name": ["Different"], "type": ["Target"], "lidvid": "urn:x:different::1.0"}]
        result = label_for(["TestTarget"], ctx).get_targets()
        mock_err.assert_not_called()
        assert "<lid_reference>None</lid_reference>" in result
        assert "<type>None</type>" in result

    def test_empty_target_skipped_calls_error(self, label_for, mocker):
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for([""]).get_targets()
        mock_err.assert_called()

    def test_trailing_eol_appended(self, label_for):
        assert label_for(["TestTarget"]).get_targets().endswith("\r\n")


# ===========================================================================
# PDS4Label._mission_reference_type / _target_reference_type
# ===========================================================================

class TestPDS4LabelDefaultReferenceTypes:
    """Covers PDS4Label's own default reference types.

    Per-leaf overrides (Checksum/Bundle/Document/Inventory/OrbnumFile) are
    covered in each leaf class's own test file; SpiceKernelPDS4Label and
    MetaKernelPDS4Label have no override and so are covered by inheriting
    this same default, exercised here directly on PDS4Label.
    """

    def test_default_mission_reference_type(self):
        label = object.__new__(PDS4Label)
        assert label._mission_reference_type == "data_to_investigation"

    def test_default_target_reference_type(self):
        label = object.__new__(PDS4Label)
        assert label._target_reference_type == "data_to_target"


# ===========================================================================
# PDS4Label + PDSLabel.write_label integration
# ===========================================================================

class TestPDS4LabelWriteLabelIntegration:
    """Integration test: PDS4Label wired into the real (inherited)
    PDSLabel.write_label. The isolated behavior of write_label itself is
    covered, decoupled from PDS3Label/PDS4Label, in
    test_classes_label.py::TestPDSLabelWriteLabel; this verifies the two
    classes actually work together end to end.
    """

    def test_write_label_produces_xml_file_with_pds4_eol(
            self, setup_pds4, product, tmp_path):
        setup_pds4.staging_directory = str(tmp_path)
        setup_pds4.diff = False
        setup_pds4.args.silent = True
        product.path = str(tmp_path / "test_kernel.bc")
        product.extension = "bc"

        label = PDS4Label(setup_pds4, product)
        label._template = str(tmp_path / "template.xml")
        Path(label._template).write_text("Static content line\n")

        label.write_label()

        written = Path(label.name)
        assert written.suffix == ".xml"
        assert written.read_bytes() == b"Static content line\r\n"
