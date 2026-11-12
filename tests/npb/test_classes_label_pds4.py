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

import re
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Sequence, Type
from unittest.mock import MagicMock

import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.classes.label.pds4_label import (
    PDS4Label,
    _ContextKind,
)
from pds.naif_pds4_bundler.classes.label.pds4_orbnum_file import (
    OrbnumFilePDS4Label,
)


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
        """context products are cached from collection.bundle.context_products"""
        ctx = product.collection.bundle.context_products
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label.setup is setup_pds4
        assert label.product is product
        # Incidental: __init__ also derives the destination filename from
        # the fixture product's path ("/staging/test_kernel.bc" -> ".xml").
        assert label.name == "/staging/test_kernel.xml"
        assert label._context_products is ctx

    def test_pds4_context_empty_list_is_cached_as_is(self, mock_class_methods, setup_pds4, product):
        """An empty (but present) collection.bundle.context_products list is
        cached as-is; it is not a lookup failure, so it does not trigger
        the fallback to product.bundle.context_products.
        """
        product.collection.bundle.context_products = []
        product.bundle.context_products = ["should not be used"]
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._context_products == []

    def test_pds4_context_attribute_error_falls_back(self, setup_pds4, product):
        """Construction does not raise when product.collection.bundle is
        entirely inaccessible (AttributeError); the try/except in __init__
        swallows it and falls back to product.bundle.context_products.
        """
        product.collection = MagicMock(spec=[])
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._context_products is product.bundle.context_products

    def test_pds4_context_type_error_falls_back(self, setup_pds4, product):
        """A TypeError resolving collection.bundle is handled the same as
        the missing-collection AttributeError case - falling back to
        product.bundle.context_products."""

        class _RaisingCollection:
            """Stand-in whose .bundle access raises instead of resolving,
            unlike a MagicMock(spec=[]) which raises AttributeError."""

            @property
            def bundle(self):
                raise TypeError("boom")

        product.collection = _RaisingCollection()
        product.setup = setup_pds4

        label = PDS4Label(product)
        assert label._context_products is product.bundle.context_products

    def test_pds4_single_mission_name(self, mock_class_methods, setup_pds4, product):
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._label_fields["PDS4_MISSION_NAME"] == "TestMission"

    @pytest.mark.parametrize("secondary_missions, expected_name",[
        (["OtherMission"], "TestMission and OtherMission"),
        (["MissionB", "MissionC"], "TestMission, MissionB, and MissionC"),
    ])
    def test_pds4_multiple_mission_name(self, mock_class_methods, setup_pds4, product, secondary_missions, expected_name):
        setup_pds4.secondary_missions = secondary_missions
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._label_fields["PDS4_MISSION_NAME"] == expected_name

    def test_pds4_single_observer_name(self, mock_class_methods, setup_pds4, product):
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._label_fields["PDS4_OBSERVER_NAME"] == "TestObserver spacecraft and its"

    @pytest.mark.parametrize("secondary_observer, expected_name",[
        (["OtherObserver"], "TestObserver and OtherObserver spacecraft and their"),
        (["ObsB", "ObsC"], "TestObserver, ObsB, and ObsC spacecraft and their"),
    ])
    def test_pds4_multiple_observer_name(self, mock_class_methods, setup_pds4, product, secondary_observer, expected_name):
        setup_pds4.secondary_observers = secondary_observer
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._label_fields["PDS4_OBSERVER_NAME"] == expected_name

    @pytest.mark.parametrize("eol, expected_eol_name",[
        ('LF', 'Line-Feed'),
        ('CRLF', 'Carriage-Return Line-Feed')
    ])
    def test_pds4_end_of_line(self, label_test_helpers, product, eol, expected_eol_name):
        setup = label_test_helpers.make_setup_pds4(end_of_line=eol)
        product.setup = setup
        label = PDS4Label(product)
        assert label._label_fields["END_OF_LINE"] == expected_eol_name

    def test_pds4_end_of_line_invalid(self, label_test_helpers, product):
        """end_of_line is invalid (neither CRLF nor LF)"""
        setup = label_test_helpers.make_setup_pds4(end_of_line="CR")
        with pytest.raises(NPBError, match=r'End of Line provided via configuration '
                                            r'is not CRLF nor LF\.'):
            product.setup = setup
            PDS4Label(product)

    # TODO: The following two test cases demonstrate an issue:
    #       If they are not a list, the code to set up PDS4_MISSION_NAME
    #       and PDS4_OBSERVER_NAME, results in a list of letters.
    def test_pds4_secondary_missions_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = "SingleMission"
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label.missions == ['TestMission', 'SingleMission']
        # TODO: This is a bug!!!!
        assert label._label_fields["PDS4_MISSION_NAME"] == 'TestMission, S, i, n, g, l, e, M, i, s, s, i, o, and n'

    def test_pds4_secondary_observers_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_observers = 'SingleObserver'
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label.observers == ['TestObserver', 'SingleObserver']
        # TODO: This is a bug!!!
        assert label._label_fields["PDS4_OBSERVER_NAME"] == 'TestObserver, S, i, n, g, l, e, O, b, s, e, r, v, e, and r spacecraft and their'

    def test_pds4_sets_missions_targets_observers(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = ["MissionB", "MissionC"]
        setup_pds4.secondary_observers = ["ObsB", "ObsC"]
        setup_pds4.secondary_targets = ["TargetB", "TargetC"]

        # Since the mock is called, the values of the MISSIONS,
        # OBSERVERS and TARGETS should be the ones provided as return_value
        # in the mock.
        product.setup = setup_pds4
        label = PDS4Label(product)
        assert label._label_fields["MISSIONS"] == 'MockedMission'
        assert label._label_fields["OBSERVERS"] == 'MockedObserver'
        assert label._label_fields["TARGETS"] == 'MockedTarget'


# ===========================================================================
# PDS4Label._match_context_entry
# ===========================================================================
# Reads self._context_products, so exercised against a bare (__init__-
# bypassed) instance with that attribute set directly.

class TestPDS4LabelMatchContextEntry:
    """Covers PDS4Label._match_context_entry – all branches."""

    @staticmethod
    def _label_with(context_products):
        label = PDS4Label.__new__(PDS4Label)
        label._context_products = context_products
        return label

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
        label = self._label_with(context_products)
        result = label._match_context_entry(
            name, valid_types=valid_types, case_insensitive=case_insensitive
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
        label = self._label_with(ctx)
        lid, _ = label._match_context_entry("Mars", valid_types=("Target",))
        assert lid == "urn:x:mars-new"


# ===========================================================================
# PDS4Label._render_context_entry
# ===========================================================================
# Reads self.setup.eol_pds4/self.setup.xml_tab, so exercised against a bare
# (__init__-bypassed) instance with a stub setup carrying just those two.

class TestPDS4LabelRenderContextEntry:
    """Covers PDS4Label._render_context_entry – all branches."""

    @staticmethod
    def _label_with(eol, tab):
        label = PDS4Label.__new__(PDS4Label)
        label.setup = SimpleNamespace(eol_pds4=eol, xml_tab=tab)
        return label

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
        label = self._label_with(eol, tab)
        result = label._render_context_entry(tag, indent, name, type_, lid, reference_type)
        assert result == expected


# ===========================================================================
# PDS4Label.get_missions/get_observers/get_targets: pinned output
# ===========================================================================

def _context_product(name: str, type_: str, lid: str) -> dict:
    """Build a context product entry as the label expects to find it."""
    return {"name": [name], "type": [type_], "lidvid": f"{lid}::1.0"}


# Rendered blocks for the default context products, in the label's PDS4 EOL
# and indentation (xml_tab = 2).
MISSION_BLOCK = (
    "    <Investigation_Area>\r\n"
    "      <name>TestMission</name>\r\n"
    "      <type>Mission</type>\r\n"
    "      <Internal_Reference>\r\n"
    "        <lid_reference>urn:nasa:pds:testmission</lid_reference>\r\n"
    "        <reference_type>data_to_investigation</reference_type>\r\n"
    "      </Internal_Reference>\r\n"
    "    </Investigation_Area>\r\n"
)
OTHER_MISSION_BLOCK = (
    "    <Investigation_Area>\r\n"
    "      <name>OtherMission</name>\r\n"
    "      <type>Other Investigation</type>\r\n"
    "      <Internal_Reference>\r\n"
    "        <lid_reference>urn:nasa:pds:othermission</lid_reference>\r\n"
    "        <reference_type>data_to_investigation</reference_type>\r\n"
    "      </Internal_Reference>\r\n"
    "    </Investigation_Area>\r\n"
)
OBSERVER_BLOCK = (
    "      <Observing_System_Component>\r\n"
    "        <name>TestObserver</name>\r\n"
    "        <type>Spacecraft</type>\r\n"
    "        <Internal_Reference>\r\n"
    "          <lid_reference>urn:nasa:pds:testobserver</lid_reference>\r\n"
    "          <reference_type>is_instrument_host</reference_type>\r\n"
    "        </Internal_Reference>\r\n"
    "      </Observing_System_Component>\r\n"
)
OTHER_OBSERVER_BLOCK = (
    "      <Observing_System_Component>\r\n"
    "        <name>OtherObserver</name>\r\n"
    "        <type>Rover</type>\r\n"
    "        <Internal_Reference>\r\n"
    "          <lid_reference>urn:nasa:pds:otherobserver</lid_reference>\r\n"
    "          <reference_type>is_instrument_host</reference_type>\r\n"
    "        </Internal_Reference>\r\n"
    "      </Observing_System_Component>\r\n"
)
TARGET_BLOCK = (
    "    <Target_Identification>\r\n"
    "      <name>TestTarget</name>\r\n"
    "      <type>Planet</type>\r\n"
    "      <Internal_Reference>\r\n"
    "        <lid_reference>urn:nasa:pds:testtarget</lid_reference>\r\n"
    "        <reference_type>data_to_target</reference_type>\r\n"
    "      </Internal_Reference>\r\n"
    "    </Target_Identification>\r\n"
)
LOWERCASE_TARGET_BLOCK = (
    "    <Target_Identification>\r\n"
    "      <name>testtarget</name>\r\n"
    "      <type>Planet</type>\r\n"
    "      <Internal_Reference>\r\n"
    "        <lid_reference>urn:nasa:pds:testtarget</lid_reference>\r\n"
    "        <reference_type>data_to_target</reference_type>\r\n"
    "      </Internal_Reference>\r\n"
    "    </Target_Identification>\r\n"
)
DWARF_TARGET_BLOCK = (
    "    <Target_Identification>\r\n"
    "      <name>Ceres</name>\r\n"
    "      <type>Dwarf planet</type>\r\n"
    "      <Internal_Reference>\r\n"
    "        <lid_reference>urn:nasa:pds:ceres</lid_reference>\r\n"
    "        <reference_type>data_to_target</reference_type>\r\n"
    "      </Internal_Reference>\r\n"
    "    </Target_Identification>\r\n"
)
EXTRA_CONTEXT = [
    _context_product("OtherMission", "Other Investigation",
                     "urn:nasa:pds:othermission"),
    _context_product("OtherObserver", "Rover", "urn:nasa:pds:otherobserver"),
    _context_product("Ceres", "Dwarf Planet", "urn:nasa:pds:ceres"),
]


@pytest.fixture
def label_for(
        label_test_helpers: SimpleNamespace) -> Callable[..., PDS4Label]:
    """Build a label without running ``__init__`` and set one attribute.

    The context products are the shared defaults plus any extra ones, so
    a test can match more than one mission, observer or target.
    """
    def _build(
        attr: str = "missions",
        entries: Any = None,
        extra_context: Sequence[dict] = (),
        cls: Type[PDS4Label] = PDS4Label,
    ) -> PDS4Label:
        label = cls.__new__(cls)
        label.setup = label_test_helpers.make_setup_pds4()
        label.product = label_test_helpers.make_product()
        label._context_products = (
            label_test_helpers.make_context_products() + list(extra_context)
        )
        setattr(label, attr, entries)
        return label
    return _build


class TestPDS4LabelContextRenderingPinned:
    """Pins the exact output and errors of get_missions/observers/targets.

    Every expectation is a whole-string comparison, so a change in
    whitespace, ordering, type handling or reference type shows up.
    """

    @pytest.mark.parametrize("method, attr, entries, expected", [
        ("get_missions", "missions", "TestMission", MISSION_BLOCK),
        ("get_missions", "missions", ["TestMission"], MISSION_BLOCK),
        ("get_missions", "missions", ["", "TestMission", None], MISSION_BLOCK),
        ("get_missions", "missions", ["TestMission", "OtherMission"],
         MISSION_BLOCK + OTHER_MISSION_BLOCK),
        ("get_observers", "observers", "TestObserver", OBSERVER_BLOCK),
        ("get_observers", "observers", ["TestObserver"], OBSERVER_BLOCK),
        ("get_observers", "observers", ["", "TestObserver", None],
         OBSERVER_BLOCK),
        # The text after the comma is dropped before matching and rendering.
        ("get_observers", "observers", ["TestObserver, extra text"],
         OBSERVER_BLOCK),
        ("get_observers", "observers", ["TestObserver", "OtherObserver"],
         OBSERVER_BLOCK + OTHER_OBSERVER_BLOCK),
        ("get_targets", "targets", "TestTarget", TARGET_BLOCK),
        ("get_targets", "targets", ["TestTarget"], TARGET_BLOCK),
        ("get_targets", "targets", ["", "TestTarget", None], TARGET_BLOCK),
        # Matched by case only: the name is rendered as typed, the type
        # comes from the context product.
        ("get_targets", "targets", ["testtarget"], LOWERCASE_TARGET_BLOCK),
        # capitalize() lowercases everything after the first letter, so
        # 'Dwarf Planet' is rendered as 'Dwarf planet'.
        ("get_targets", "targets", ["Ceres"], DWARF_TARGET_BLOCK),
        ("get_targets", "targets", ["TestTarget", "testtarget"],
         TARGET_BLOCK + LOWERCASE_TARGET_BLOCK),
    ])
    def test_output_is_pinned(self, label_for: Callable[..., PDS4Label],
                              method: str, attr: str, entries: Any,
                              expected: str) -> None:
        """Rendered XML matches byte for byte scalars, lists and gaps.

        Covers a single value, a list, empty entries mixed with real ones,
        several entries in order, an observer with trailing text, a target
        matched by case only and a multi-word target type.
        """
        # Label that knows the default context products plus the extra ones
        label = label_for(attr, entries, EXTRA_CONTEXT)

        # Render the block through the method under test
        result = getattr(label, method)()

        # Exactly the expected XML, ending in a single end of line
        assert result == expected

    @pytest.mark.parametrize("method, attr, entries, expected_reference", [
        ("get_missions", "missions", ["TestMission"],
         "ancillary_to_investigation"),
        ("get_targets", "targets", ["TestTarget"], "ancillary_to_target"),
        # Observers always use the same reference type, whatever the subclass.
        ("get_observers", "observers", ["TestObserver"],
         "is_instrument_host"),
    ])
    def test_subclass_reference_type(self, label_for: Callable[..., PDS4Label],
                                     method: str, attr: str, entries: Any,
                                     expected_reference: str) -> None:
        """A subclass that overrides a reference type changes the XML.

        The orbnum label overrides the mission and target reference types.
        The rendered block must use them, and the observer type must stay
        'is_instrument_host'.
        """
        # Label of the subclass that overrides the reference types
        label = label_for(attr, entries, cls=OrbnumFilePDS4Label)

        # Render the block through the method under test
        result = getattr(label, method)()

        # The reference type comes from the subclass, not from PDS4Label
        assert f"<reference_type>{expected_reference}</reference_type>" in result

    @pytest.mark.parametrize("method, attr, entries, message", [
        ("get_missions", "missions", ["Nope"],
         "LID has not been obtained for mission Nope."),
        # A target is in the context products, but it is not a valid mission.
        ("get_missions", "missions", ["TestTarget"],
         "LID has not been obtained for mission TestTarget."),
        # The error quotes the whole entry, not just the part before the comma.
        ("get_observers", "observers", ["Nope, extra text"],
         "LID has not been obtained for observer Nope, extra text."),
        ("get_targets", "targets", ["Nope"],
         "LID has not been obtained for target Nope."),
        ("get_missions", "missions", ["", None],
         "test_kernel.bc missions not defined."),
        ("get_observers", "observers", [""],
         "test_kernel.bc observers not defined."),
        ("get_targets", "targets", [""],
         "test_kernel.bc targets not defined."),
    ])
    def test_error_messages(self, label_for: Callable[..., PDS4Label],
                            method: str, attr: str, entries: Any,
                            message: str) -> None:
        """Unmatched and empty entries raise an NPBError with this message.

        An entry with no matching context product names the entry in the
        error. A list with only empty entries reports that nothing is
        defined for the product.
        """
        # Label whose entries cannot be matched, or are all empty
        label = label_for(attr, entries)

        # Rendering has to stop with the error, matching the whole message
        with pytest.raises(NPBError, match=f"^{re.escape(message)}$"):
            getattr(label, method)()


# A kind the real code does not have, to show the loop is not tied to the
# three real ones. With xml_tab = 2 and indent 1, the tag sits at 2 spaces.
WIDGET = _ContextKind(
    "widget", "widgets", "Widget_Area", 1, valid_types=("Gadget",),
)
WIDGET_CONTEXT = [
    _context_product("W1", "Gadget", "urn:nasa:pds:w1"),
    _context_product("W2", "big gadget", "urn:nasa:pds:w2"),
]
WIDGET_BLOCK = (
    "  <Widget_Area>\r\n"
    "    <name>W1</name>\r\n"
    "    <type>Gadget</type>\r\n"
    "    <Internal_Reference>\r\n"
    "      <lid_reference>urn:nasa:pds:w1</lid_reference>\r\n"
    "      <reference_type>x_to_y</reference_type>\r\n"
    "    </Internal_Reference>\r\n"
    "  </Widget_Area>\r\n"
)
LOWERCASE_WIDGET_BLOCK = (
    "  <Widget_Area>\r\n"
    "    <name>w1</name>\r\n"
    "    <type>Gadget</type>\r\n"
    "    <Internal_Reference>\r\n"
    "      <lid_reference>urn:nasa:pds:w1</lid_reference>\r\n"
    "      <reference_type>x_to_y</reference_type>\r\n"
    "    </Internal_Reference>\r\n"
    "  </Widget_Area>\r\n"
)
CAPITALIZED_WIDGET_BLOCK = (
    "  <Widget_Area>\r\n"
    "    <name>W2</name>\r\n"
    "    <type>Big gadget</type>\r\n"
    "    <Internal_Reference>\r\n"
    "      <lid_reference>urn:nasa:pds:w2</lid_reference>\r\n"
    "      <reference_type>x_to_y</reference_type>\r\n"
    "    </Internal_Reference>\r\n"
    "  </Widget_Area>\r\n"
)


class TestPDS4LabelRenderContextKind:
    """The shared loop on its own, with a kind that is not a real one."""

    @pytest.mark.parametrize("kind, entries, expected", [
        # Its own tag and indent, and the reference type that was passed in.
        (WIDGET, ["W1"], WIDGET_BLOCK),
        # Each flag on its own: the name is matched without regard to case
        # but rendered as typed, the type is capitalized, and the text after
        # a comma is left out of the name.
        (replace(WIDGET, case_insensitive=True), ["w1"],
         LOWERCASE_WIDGET_BLOCK),
        (replace(WIDGET, valid_types=None, capitalize_type=True), ["W2"],
         CAPITALIZED_WIDGET_BLOCK),
        (replace(WIDGET, name_before_comma=True), ["W1, more text"],
         WIDGET_BLOCK),
    ])
    def test_kind_fields_drive_the_output(
        self,
        label_for: Callable[..., PDS4Label],
        kind: _ContextKind,
        entries: Any,
        expected: str,
    ) -> None:
        """The tag, indent, matching and type handling come from the kind.

        A made-up kind is rendered with each flag switched on in turn, and
        the XML has to follow the kind and the reference type passed in.
        """
        # Label that knows the made-up widget context products
        label = label_for(extra_context=WIDGET_CONTEXT)

        # Render the entries with the made-up kind
        result = label._render_context_kind(kind, entries, "x_to_y")

        # The block follows the kind, not any of the real ones
        assert result == expected

    @pytest.mark.parametrize("entries, message", [
        (["Nope"], "LID has not been obtained for widget Nope."),
        ([""], "test_kernel.bc widgets not defined."),
    ])
    def test_kind_words_in_errors(
        self,
        label_for: Callable[..., PDS4Label],
        entries: Any,
        message: str,
    ) -> None:
        """Both error messages use the words of the kind being rendered.

        An entry with no context product names the entry and the kind, and a
        list of empty entries reports that nothing is defined for the product.
        """
        # Label that knows the made-up widget context products
        label = label_for(extra_context=WIDGET_CONTEXT)

        # Rendering has to stop with the error, matching the whole message
        with pytest.raises(NPBError, match=f"^{re.escape(message)}$"):
            label._render_context_kind(WIDGET, entries, "x_to_y")


class TestPDS4LabelContextTypes:
    """Which context product types each kind accepts."""

    @pytest.mark.parametrize("method, attr, type_", [
        ("get_missions", "missions", "Mission"),
        ("get_missions", "missions", "Other Investigation"),
        ("get_observers", "observers", "Spacecraft"),
        ("get_observers", "observers", "Rover"),
        ("get_observers", "observers", "Lander"),
        ("get_observers", "observers", "Host"),
        # A target can be any kind of body.
        ("get_targets", "targets", "Planet"),
        ("get_targets", "targets", "Ring"),
    ])
    def test_accepted_type_is_rendered(
        self,
        label_for: Callable[..., PDS4Label],
        method: str,
        attr: str,
        type_: str,
    ) -> None:
        """A context product of an accepted type is found and rendered.

        The product is named 'Subject' so nothing in the default context
        products can match it by accident.
        """
        # Label with a single 'Subject' product of the type under test
        subject = _context_product("Subject", type_, "urn:nasa:pds:subject")
        label = label_for(attr, ["Subject"], [subject])

        # Render the block through the method under test
        result = getattr(label, method)()

        # The block carries the type of the context product
        assert f"<type>{type_}</type>" in result

    @pytest.mark.parametrize("method, attr, singular, type_", [
        ("get_missions", "missions", "mission", "Spacecraft"),
        ("get_missions", "missions", "mission", "Planet"),
        ("get_observers", "observers", "observer", "Mission"),
        ("get_observers", "observers", "observer", "Planet"),
    ])
    def test_rejected_type_raises(
        self,
        label_for: Callable[..., PDS4Label],
        method: str,
        attr: str,
        singular: str,
        type_: str,
    ) -> None:
        """A context product of the wrong type counts as not found.

        Missions and observers only look at their own types, so a product
        with the right name but another type gives the same error as a name
        that is missing.
        """
        # Label with a single 'Subject' product of the wrong type
        subject = _context_product("Subject", type_, "urn:nasa:pds:subject")
        label = label_for(attr, ["Subject"], [subject])
        message = f"LID has not been obtained for {singular} Subject."

        # Rendering has to stop with the error for that entry
        with pytest.raises(NPBError, match=f"^{re.escape(message)}$"):
            getattr(label, method)()


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
        setup_pds4.args.diff = False
        setup_pds4.args.silent = True
        product.path = str(tmp_path / "test_kernel.bc")
        product.extension = "bc"

        product.setup = setup_pds4

        label = PDS4Label(product)
        label._template = str(tmp_path / "template.xml")
        Path(label._template).write_text("Static content line\n")

        label.write_label()

        written = Path(label.name)
        assert written.suffix == ".xml"
        assert written.read_bytes() == b"Static content line\r\n"
