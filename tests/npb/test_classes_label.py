"""
Tests for PDSLabel class.
"""

import os
from pathlib import Path
from typing import cast, Type
from unittest.mock import call, mock_open

import pytest

from pds.naif_pds4_bundler.classes.label.label import PDSLabel

# Patch targets — resolved to where the names are looked up inside label.py
_PATCH_ADD_CR = "pds.naif_pds4_bundler.classes.label.label.add_carriage_return"
_PATCH_COMPARE = "pds.naif_pds4_bundler.classes.label.label.compare_files"
_PATCH_GLOB = "pds.naif_pds4_bundler.classes.label.label.glob.glob"
# Path.glob/Path.exists are patched on the class itself (not label.py's
# namespace) since `Path` is a class object, not a rebindable function
# reference -- patching it here affects every Path instance, including
# the ones _pick_val_label constructs internally.
_PATCH_PATH_GLOB = "pathlib.Path.glob"
_PATCH_PATH_EXISTS = "pathlib.Path.exists"


# ---------------------------------------------------------------------------
# Shared builder helpers
# ---------------------------------------------------------------------------
# make_context_products/make_bundle/make_collection/make_product/
# make_setup_pds4 live in conftest.py's label_test_helpers fixture, shared
# with test_classes_label_pds4.py. Only the PDS3-flavored setup builder is
# specific to this file.

def _make_setup_pds3(label_test_helpers, **kwargs):
    setup = label_test_helpers.make_setup_pds4(**kwargs)
    setup.pds_version = "3"
    return setup


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def setup_pds4(label_test_helpers):
    return label_test_helpers.make_setup_pds4()


@pytest.fixture
def setup_pds3(label_test_helpers):
    return _make_setup_pds3(label_test_helpers)


@pytest.fixture
def product(label_test_helpers):
    return label_test_helpers.make_product()


# ===========================================================================
# PDSLabel.__init__
# ===========================================================================

class TestPDSLabelInit:
    """Covers PDSLabel.__init__ – version-agnostic branches only.

    The pds_version-gated behavior this class used to cover (XML_MODEL,
    PDS4_MISSION_NAME/PDS4_OBSERVER_NAME, END_OF_LINE, MISSIONS/OBSERVERS/
    TARGETS, and the context_products lookup) now lives on PDS4Label; see
    test_classes_label_pds4.py::TestPDS4LabelInit.
    """

    def test_uses_setup_creation_date_time(self, setup_pds4, product):
        """setup has creation_date_time"""
        setup_pds4.creation_date_time = "2023-06-15T12:00:00"
        label = PDSLabel(setup_pds4, product)
        assert label.PRODUCT_CREATION_TIME == "2023-06-15T12:00:00"
        assert label.PRODUCT_CREATION_DATE == "2023-06-15"
        assert label.PRODUCT_CREATION_YEAR == "2023"

    def test_uses_product_creation_date(self, setup_pds4, product):
        """setup does NOT have creation_date_time → use product's dates"""
        label = PDSLabel(setup_pds4, product)
        assert label.PRODUCT_CREATION_TIME == "2024-01-01T00:00:00"
        assert label.PRODUCT_CREATION_DATE == "2024-01-01"
        assert label.PRODUCT_CREATION_YEAR == "2024"

    def test_non_kernel_class_builds_from_setup(self, setup_pds4, product):
        """class is NOT one of the excluded kernel classes then
        build missions/observers/targets from setup"""
        label = PDSLabel(setup_pds4, product)
        assert "TestMission" in label.missions
        assert "TestObserver" in label.observers
        assert "TestTarget" in label.targets

    @pytest.mark.parametrize("class_name", [
        "SpiceKernelPDS4Label",
        "InSightLabel",
        "MavenLabel"
    ])
    def test_kernel_class_uses_product_missions(self, setup_pds4, product, class_name):
        # Dynamically create the class with the parametrized name
        cls = cast(Type[PDSLabel], type(class_name, (PDSLabel,), {}))

        # Instantiate and initialize
        label = object.__new__(cls)
        PDSLabel.__init__(label, setup_pds4, product)

        assert label.missions == product.missions
        assert label.observers == product.observers
        assert label.targets == product.targets

    # NOTE: PDS4_MISSION_NAME/PDS4_OBSERVER_NAME (and the non-list-wrapping
    #       bug affecting them) are PDS4-only; see
    #       test_classes_label_pds4.py::TestPDS4LabelInit for those two cases.
    #       The list-wrapping of self.missions/self.observers itself is
    #       version-agnostic and stays covered below and via the pds3 cases.

    def test_pds4_secondary_targets_non_list_wrapped(self, setup_pds4, product):
        setup_pds4.secondary_targets = 'SingleTarget'
        label = PDSLabel(setup_pds4, product)
        assert label.targets == ['TestTarget', 'SingleTarget']

    def test_pds3_secondary_missions_non_list_wrapped(self, setup_pds3, product):
        setup_pds3.secondary_missions = "SingleMission"
        label = PDSLabel(setup_pds3, product)
        assert label.missions == ['TestMission', 'SingleMission']
        assert not hasattr(label, 'PDS4_MISSION_NAME')

    def test_pds3_secondary_observers_non_list_wrapped(self, setup_pds3, product):
        setup_pds3.secondary_observers = 'SingleObserver'
        label = PDSLabel(setup_pds3, product)
        assert label.observers == ['TestObserver', 'SingleObserver']
        assert not hasattr(label, 'PDS4_OBSERVER_NAME')

    def test_pds3_secondary_targets_non_list_wrapped(self, setup_pds3, product):
        setup_pds3.secondary_targets = 'SingleTarget'
        label = PDSLabel(setup_pds3, product)
        assert label.targets == ['TestTarget', 'SingleTarget']

    def test_pds4_secondary_missions_list(self, setup_pds4, product):
        setup_pds4.secondary_missions = ["MissionB", "MissionC"]
        label = PDSLabel(setup_pds4, product)
        assert label.missions == ['TestMission', "MissionB", "MissionC"]

    def test_pds4_secondary_observers_list(self, setup_pds4, product):
        setup_pds4.secondary_observers = ["ObsB", "ObsC"]
        label = PDSLabel(setup_pds4, product)
        assert label.observers == ['TestObserver', "ObsB", "ObsC"]

    def test_pds4_secondary_targets_list(self, setup_pds4, product):
        setup_pds4.secondary_targets = ["TargetB", "TargetC"]
        label = PDSLabel(setup_pds4, product)
        assert label.targets == ['TestTarget', "TargetB", "TargetC"]

    def test_pds3_secondary_missions_list(self, setup_pds3, product):
        setup_pds3.secondary_missions = ["MissionB", "MissionC"]
        label = PDSLabel(setup_pds3, product)
        assert label.missions == ['TestMission', "MissionB", "MissionC"]

    def test_pds3_secondary_observers_list(self, setup_pds3, product):
        setup_pds3.secondary_observers = ["ObsB", "ObsC"]
        label = PDSLabel(setup_pds3, product)
        assert label.observers == ['TestObserver', "ObsB", "ObsC"]

    def test_pds3_secondary_targets_list(self, setup_pds3, product):
        setup_pds3.secondary_targets = ["TargetB", "TargetC"]
        label = PDSLabel(setup_pds3, product)
        assert label.targets == ['TestTarget', "TargetB", "TargetC"]


# ===========================================================================
# PDSLabel.write_label
# ===========================================================================

class TestPDSLabelWriteLabel:
    """Covers PDSLabel.write_label – all branches."""

    @pytest.fixture
    def label_for(self, label_test_helpers):
        """Factory fixture: builds a bare label ready for write_label.

        Built directly off PDSLabel, with _label_extension/_eol assigned as
        plain instance attributes — decoupled from PDS3Label/PDS4Label. The
        coupling between those subclasses' real properties and write_label
        is covered separately by the integration tests in
        test_classes_label_pds3.py/test_classes_label_pds4.py.
        """
        def _build(
            pds_version="4",
            label_name_has_ext=False,
            is_checksum=False,
            has_inventory=False,
            diff=False,
            is_pds3_kernel=False,
        ):
            setup = (label_test_helpers.make_setup_pds4() if pds_version == "4"
                    else _make_setup_pds3(label_test_helpers))
            setup.diff = diff
            setup.pds_version = pds_version

            product = label_test_helpers.make_product()

            if label_name_has_ext:
                ext = ".xml" if pds_version == "4" else ".lbl"
                product.path = f"/staging/bundle{ext}"
                product.extension = ext.lstrip(".")
            elif has_inventory:
                product.path = "/staging/inventory_collection.bc"
            else:
                product.path = "/staging/test_kernel.bc"
                product.extension = "bc"

            # cls_name only matters for write_label's unrelated "suppress
            # trailing log line for SpiceKernelPDS3Label" check.
            cls_name = "SpiceKernelPDS3Label" if is_pds3_kernel else "PDSLabel"
            cls = cast(Type[PDSLabel], type(cls_name, (PDSLabel,), {}))
            label = object.__new__(cls)
            label.setup = setup
            label.product = product
            label.name = ""
            label._template = "/tmpl/template.xml"
            label._label_extension = ".xml" if pds_version == "4" else ".lbl"
            label._eol = "\r\n"

            if is_checksum:
                label.__class__ = type("ChecksumLabelClass", (PDSLabel,), {})
                label.name = f"/staging{os.sep}checksum.lbl"
                product.path = label.name
                label._template = "/tmpl/template.lbl"
                product.extension = "lbl"
                product.record_bytes = 80

            return label
        return _build

    @staticmethod
    def _run_write(label, mocker, template_content="Line with $name\n"):
        mocker.patch("builtins.open", mock_open(read_data=template_content))
        mocker.patch(_PATCH_ADD_CR, side_effect=lambda line, eol, setup: line + "\n")
        mocker.patch.object(Path, "relative_to", return_value=Path("rel/path"))
        mock_add = mocker.patch.object(label.setup, "add_file")
        label.write_label()
        return mock_add

    def test_pds4_writes_xml_label(self, label_for, mocker):
        label = label_for(pds_version="4")
        mock_add = self._run_write(label, mocker)
        assert label.name.endswith(".xml")
        mock_add.assert_called_once()

    def test_pds3_writes_lbl_label(self, label_for, mocker):
        label = label_for(pds_version="3")
        self._run_write(label, mocker)
        assert label.name.endswith(".lbl")

    def test_label_ext_already_in_path_uses_path_directly(self, label_for, mocker):
        label = label_for(pds_version="4", label_name_has_ext=True)
        self._run_write(label, mocker)
        assert "bundle" in label.name

    def test_inventory_in_name_strips_inventory_prefix(self, label_for, mocker):
        label = label_for(has_inventory=True)
        self._run_write(label, mocker)
        assert "inventory_" not in label.name

    def test_checksum_lbl_pads_line_to_record_bytes(self, label_for, mocker):
        """checksum.lbl lines must be padded to record_bytes - 2."""
        label = label_for(pds_version="3", is_checksum=True)
        label.name = f"/staging{os.sep}checksum.lbl"
        mocker.patch("builtins.open", mock_open(read_data="short\n"))
        mock_cr = mocker.patch(_PATCH_ADD_CR, side_effect=lambda line, eol, setup: line + "\n")
        mocker.patch.object(Path, "relative_to", return_value=Path("c"))
        mocker.patch.object(label.setup, "add_file")
        label.write_label()
        mock_cr.assert_called()

    def test_diff_true_calls_compare(self, label_for, mocker):
        label = label_for(diff=True)
        mock_cmp = mocker.patch.object(label, "compare")
        mocker.patch("builtins.open", mock_open(read_data=""))
        mocker.patch(_PATCH_ADD_CR, side_effect=lambda line, eol, setup: line + "\n")
        mocker.patch.object(Path, "relative_to", return_value=Path("r"))
        mocker.patch.object(label.setup, "add_file")
        label.write_label()
        mock_cmp.assert_called_once()

    def test_spice_kernel_pds3_label_no_trailing_log_info(self, label_for, mocker):
        """SpiceKernelPDS3Label must NOT emit a trailing logging.info('') call."""
        label = label_for(is_pds3_kernel=True)
        mock_log = mocker.patch("pds.naif_pds4_bundler.classes.label.label.logging.info")
        mocker.patch("builtins.open", mock_open(read_data=""))
        mocker.patch(_PATCH_ADD_CR, side_effect=lambda line, eol, setup: line + "\n")
        mocker.patch.object(Path, "relative_to", return_value=Path("r"))
        mocker.patch.object(label.setup, "add_file")
        label.write_label()
        empty_calls = [c for c in mock_log.call_args_list if c == call("")]
        assert len(empty_calls) == 0

    def test_silent_mode_suppresses_print(self, label_for, mocker):
        label = label_for()
        label.setup.args.silent = True
        mock_print = mocker.patch("builtins.print")
        mocker.patch("builtins.open", mock_open(read_data=""))
        mocker.patch(_PATCH_ADD_CR, side_effect=lambda line, eol, setup: line + "\n")
        mocker.patch.object(Path, "relative_to", return_value=Path("r"))
        mocker.patch.object(label.setup, "add_file")
        label.write_label()
        mock_print.assert_not_called()


# ===========================================================================
# PDSLabel.compare
# ===========================================================================

class TestPDSLabelCompare:
    """Covers PDSLabel.compare – all three fallback levels and success path."""

    @pytest.fixture
    def label_for(self, label_test_helpers):
        """Factory fixture: builds a bare label ready for compare."""

        def _build(collection_name="spice_kernels", label_name_part="kernel"):
            setup = label_test_helpers.make_setup_pds4()
            setup.diff = "html"
            product = label_test_helpers.make_product()
            product.collection.name = collection_name
            product.name = "kernel.bc"
            product.extension = "bc"
            label = PDSLabel.__new__(PDSLabel)
            label.setup = setup
            label.product = product
            label.name = str(Path(f"/staging/spice_kernels/ck/{label_name_part}.xml"))
            return label

        return _build

    @staticmethod
    def _level1_hit(hit):
        """Return a side_effect callable that simulates finding a prior-version
        label in the level-1 while loop, then cleanly exits that loop.
        """
        call_count = [0]

        def _side_effect(_):
            call_count[0] += 1
            if call_count[0] == 1:
                return [hit]  # i=1: val_label recorded, match_flag stays True
            else:
                return []  # i=2: match_flag=False -> while exits

        return _side_effect

    # ------------------------------------------------------------------
    # Level 1 success: a prior-version label is found.
    # The while loop runs once per character in the filename.  We use a
    # callable side_effect that returns [] for all prefix calls except the
    # last valid one, where it returns the hit, then [] to exit the loop.
    # ------------------------------------------------------------------
    def test_level1_found_calls_compare_files(self, label_for, mocker):
        label = label_for()
        hit = "/bundle/spice_kernels/ck/kernel.xml"
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=self._level1_hit(hit))
        label.compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Level 1 no match → level 2 succeeds. _pick_val_label issues at most
    # one Path.glob call now (the exact-name glob became a .exists()
    # check), so each level-2/level-3 success case needs at most one
    # Path.glob mock plus (except for "bundle", which never checks
    # existence) one Path.exists mock.
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        ["collection_name", "label_name_part", "name_override", "glob_return", "needs_exists"],
        [
            (
                "spice_kernels", "collection", f"/staging/spice_kernels{os.sep}collection_label.xml",
                [Path("/bundle/spice_kernels/ck/inventory_coll.bc")], True,
            ),
            (
                "spice_kernels", "bundle", str(Path("/staging/bundle_label.xml")),
                [Path("/bundle/bundle_v1.xml")], False,
            ),
            ("spice_kernels", "kernel", None, [Path("/bundle/kern.bc")], True),
            (
                "miscellaneous", "orbnum", f"/staging/miscellaneous/orb{os.sep}orbnum.xml",
                [Path("/bundle/misc/orb/old.bc")], True,
            ),
        ],
        ids=["collection-label", "bundle-label", "generic-label", "miscellaneous-appends-subdir"],
    )
    def test_level2_succeeds(
        self, label_for, mocker, collection_name, label_name_part, name_override, glob_return, needs_exists
    ):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name=collection_name, label_name_part=label_name_part)
        if name_override:
            label.name = name_override
        mocker.patch(_PATCH_GLOB, side_effect=[[]])  # level-1: miss
        mocker.patch(_PATCH_PATH_GLOB, return_value=glob_return)  # level-2
        if needs_exists:
            mocker.patch(_PATCH_PATH_EXISTS, return_value=True)
        label.compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Level 1 & 2 both fail → level 3 (InSight test data) succeeds.
    # ------------------------------------------------------------------
    @pytest.mark.parametrize(
        ["collection_name", "label_name_part", "name_override", "glob_return", "needs_exists"],
        [
            (
                "spice_kernels", "kernel", None,
                [Path("/root/data/insight_spice/spice_kernels/ck/insight_ck.bc")], True,
            ),
            (
                "spice_kernels", "kernel", f"/staging/spice_kernels{os.sep}collection_label.xml",
                [Path("/insight/ck/inv_coll.bc")], True,
            ),
            (
                "spice_kernels", "kernel", str(Path("/staging/bundle_label.xml")),
                [Path("/insight/bundle_v1.xml")], False,
            ),
            (
                "miscellaneous", "orbnum", f"/staging/miscellaneous/orb{os.sep}orbnum.xml",
                [Path("/root/data/insight_spice/miscellaneous/orb/insight.bc")], True,
            ),
        ],
        ids=["fallback-insight-data", "collection-label", "bundle-label", "miscellaneous-appends-subdir"],
    )
    def test_level3_succeeds(
        self, label_for, mocker, collection_name, label_name_part, name_override, glob_return, needs_exists
    ):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name=collection_name, label_name_part=label_name_part)
        if name_override:
            label.name = name_override
        mocker.patch(_PATCH_GLOB, side_effect=[[]])  # level-1: miss
        mocker.patch(_PATCH_PATH_GLOB, side_effect=[[], glob_return])  # level-2 empty, level-3 hit
        if needs_exists:
            mocker.patch(_PATCH_PATH_EXISTS, return_value=True)
        label.compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # All three levels fail → nothing compared, no exception raised
    # ------------------------------------------------------------------
    def test_all_levels_fail_no_exception(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, return_value=[])
        mocker.patch(_PATCH_PATH_GLOB, return_value=[])
        label_for().compare()
        mock_cmp.assert_not_called()

    # ------------------------------------------------------------------
    # Level 1: miscellaneous collection adds product-type sub-directory
    # ------------------------------------------------------------------
    def test_level1_miscellaneous_collection(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name="miscellaneous", label_name_part="orbnum")
        label.name = f"/staging/miscellaneous/orb{os.sep}orbnum.xml"
        hit = "/bundle/misc/orb/old_orbnum.xml"
        mocker.patch(_PATCH_GLOB, side_effect=self._level1_hit(hit))
        label.compare()

    # ------------------------------------------------------------------
    # Level 1: collection name is neither spice_kernels nor miscellaneous
    #           → no subdirectory appended
    # ------------------------------------------------------------------
    def test_level1_other_collection_no_subdir(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name="document")
        label.name = f"/staging/document{os.sep}spiceds.xml"
        hit = "/bundle/document/spiceds_v1.xml"
        mocker.patch(_PATCH_GLOB, side_effect=self._level1_hit(hit))
        label.compare()

    # ------------------------------------------------------------------
    # Level 1: "collection" appears in the label filename → no sub-dir added
    # ------------------------------------------------------------------
    def test_level1_collection_in_label_filename(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(
            collection_name="spice_kernels",
            label_name_part="collection_inventory",
        )
        label.name = f"/staging/spice_kernels{os.sep}collection_inventory.xml"
        hit = "/bundle/ck/old_collection_inventory.xml"
        mocker.patch(_PATCH_GLOB, side_effect=self._level1_hit(hit))
        label.compare()

    # ------------------------------------------------------------------
    # Level 2 finds a product candidate but no label file exists for it
    # on disk (candidate.exists() is False) → falls through to level 3,
    # which succeeds.
    # ------------------------------------------------------------------
    def test_level2_missing_candidate_falls_through_to_level3(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[[]])  # level-1: miss
        mocker.patch(_PATCH_PATH_GLOB, side_effect=[
            [Path("/bundle/spice_kernels/ck/kern.bc")],  # level-2: val_products found...
            [Path("/root/data/insight_spice/spice_kernels/ck/insight_ck.bc")],  # level-3: val_products
        ])
        mocker.patch(_PATCH_PATH_EXISTS, side_effect=[False, True])  # ...but candidate missing; level-3 has one
        label_for().compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Level 3 finds a product candidate but no label file exists for it
    # either → the raise is caught by level-3's own except, and
    # compare_files is never called.
    # ------------------------------------------------------------------
    def test_level3_missing_candidate_suppressed_by_except(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[[]])  # level-1: miss
        mocker.patch(_PATCH_PATH_GLOB, side_effect=[
            [],  # level-2: val_products empty -> raises, falls to level-3
            [Path("/root/data/insight_spice/spice_kernels/ck/insight_ck.bc")],  # level-3: val_products
        ])
        mocker.patch(_PATCH_PATH_EXISTS, return_value=False)  # level-3 candidate also missing
        label_for().compare()
        mock_cmp.assert_not_called()


# ===========================================================================
# PDSLabel._val_label_directory / _pick_val_label / _find_* — direct tests
# ===========================================================================
# The TestPDSLabelCompare tests above only exercise these through compare(),
# by controlling glob.glob's call sequence. That pins compare()'s overall
# behavior but never calls the extracted helpers directly, so it doesn't
# prove each one is independently correct in isolation. These tests call
# them directly instead.

class TestPDSLabelCompareHelpers:
    """Direct calls to the fallback-strategy helpers extracted from compare()."""

    @pytest.fixture
    def label_for_helper(self, label_test_helpers):
        """Factory fixture: builds a bare label ready for compare().

        Duplicated from TestPDSLabelCompare rather than inherited via
        subclassing, since subclassing a pytest test class would cause its
        tests to be collected and re-run a second time under this class.
        """

        def _build(collection_name="spice_kernels", label_name_part="kernel", subdir="ck"):
            setup = label_test_helpers.make_setup_pds4()
            setup.diff = "html"
            product = label_test_helpers.make_product()
            product.collection.name = collection_name
            product.name = "kernel.bc"
            product.extension = "bc"
            label = PDSLabel.__new__(PDSLabel)
            label.setup = setup
            label.product = product
            label.name = str(Path(f"/staging/{collection_name}/{subdir}/{label_name_part}.xml"))
            return label

        return _build

    @staticmethod
    def _level1_hit(hit):
        """Return a side_effect callable that simulates finding a prior-version
        label in the level-1 while loop, then cleanly exits that loop.
        """
        call_count = [0]

        def _side_effect(_):
            call_count[0] += 1
            if call_count[0] == 1:
                return [hit]
            else:
                return []

        return _side_effect

    # -- _val_label_directory ------------------------------------------

    @pytest.mark.parametrize(
        ["collection_name", "name_override", "expected"],
        [
            (
                "spice_kernels",
                None,
                str(Path("/bundle/test_spice", "spice_kernels", "ck")) + os.sep,
            ),
            (
                "miscellaneous",
                str(Path("/staging/miscellaneous/orb/orbnum.xml")),
                str(Path("/bundle/test_spice", "miscellaneous", "orb")) + os.sep,
            ),
            (
                "document",
                None,
                str(Path("/bundle/test_spice", "document")) + os.sep,
            ),
            (
                "spice_kernels",
                str(Path("/staging/spice_kernels/collection.xml")),
                str(Path("/bundle/test_spice", "spice_kernels")) + os.sep,
            ),
        ],
        ids=[
            "spice_kernels-appends-subdir",
            "miscellaneous-appends-subdir",
            "other-collection-no-subdir",
            "collection-in-name-suppresses-subdir",
        ],
    )
    def test_val_label_directory(self, label_for_helper, collection_name, name_override, expected):
        label = label_for_helper(collection_name=collection_name)
        if name_override:
            label.name = name_override
        result = label._val_label_directory("/bundle/test_spice/")
        assert result == expected

    # -- _pick_val_label: branch selection, unified substring-of-basename
    #    matching rule (used by both the similar-type and InSight-fallback
    #    call sites). Real product names embed "collection"/"bundle" as a
    #    basename prefix (e.g. "collection_spice_kernels_v001.xml",
    #    "bundle_insight_spice_v009.xml"), never as a standalone path
    #    component, so the match must be substring-based to work at all. --

    @pytest.mark.parametrize(
        ["name", "val_label_path", "glob_pattern", "glob_return", "expected"],
        [
            (
                f"/staging/spice_kernels{os.sep}collection_spice_kernels_v001.xml",
                "/insight/ck/",
                "*.bc",
                [Path("/insight/ck/inventory_old.bc")],
                Path("/insight/ck/old.xml"),
            ),
            (
                f"/staging{os.sep}bundle_insight_spice_v009.xml",
                "/insight/",
                "bundle_*.xml",
                [Path("/insight/bundle_v1.xml")],
                Path("/insight/bundle_v1.xml"),
            ),
            (
                f"/staging/ck{os.sep}kernel.xml",
                "/bundle/ck/",
                "*.bc",
                [Path("/bundle/ck/kernel.v01.bc")],
                Path("/bundle/ck/kernel.v01.xml"),
                # Also a regression case for the .split(".")[0] truncation
                # bug: the stem must keep everything but the final
                # extension, not just the text before the first dot.
            ),
            (
                # A directory literally named "collection" must NOT trigger
                # the collection branch -- only the basename is checked, not
                # the full path. The basename here ("label.xml") has no
                # "collection" substring, so this falls through to else.
                f"/staging{os.sep}collection{os.sep}label.xml",
                "/insight/ck/",
                "*.bc",
                [Path("/insight/ck/kernel.bc")],
                Path("/insight/ck/kernel.xml"),
            ),
            (
                # Known, accepted trade-off of substring matching: "bundle"
                # is a substring of "unbundled_data.xml" (from "unbundled"),
                # so this still triggers the bundle branch even though the
                # file is not actually a bundle label. This is the price of
                # a rule that must also match real names like
                # "bundle_insight_spice_v009.xml". The bundle branch is
                # checked first and returns immediately, so it never checks
                # candidate.exists() either -- max(matches) is the answer.
                f"/staging/spice_kernels{os.sep}unbundled_data.xml",
                "/insight/ck/",
                "bundle_*.xml",
                [Path("/insight/ck/bundle_v2.xml")],
                Path("/insight/ck/bundle_v2.xml"),
            ),
        ],
        ids=[
            "collection-branch-realistic-name",
            "bundle-branch-realistic-name",
            "else-branch-multidot-stem",
            "collection-directory-without-basename-match-falls-to-else",
            "bundle-substring-collision-is-accepted-trade-off",
        ],
    )
    def test_pick_val_label_branch_selection(
        self, label_for_helper, mocker, name, val_label_path, glob_pattern, glob_return, expected
    ):
        label = label_for_helper()
        label.name = name
        mocker.patch.object(label, "_val_label_directory", return_value=val_label_path)
        mock_glob = mocker.patch(_PATCH_PATH_GLOB, return_value=glob_return)
        mocker.patch(_PATCH_PATH_EXISTS, return_value=True)
        result = label._pick_val_label(Path("/unused"))
        assert result == expected
        mock_glob.assert_called_once_with(glob_pattern)

    # -- _pick_val_label: failure paths ---------------------------------
    # The three raise sites: bundle's own glob comes up empty, the shared
    # path's val_products glob comes up empty (can't call max()), or the
    # shared path derives a candidate that doesn't exist on disk.

    @pytest.mark.parametrize(
        ["name", "val_label_path", "glob_return", "exists_return"],
        [
            (f"/staging{os.sep}bundle_insight_spice_v009.xml", "/insight/", [], False),
            (f"/staging/ck{os.sep}kernel.xml", "/bundle/ck/", [], False),
            (
                f"/staging/ck{os.sep}kernel.xml",
                "/bundle/ck/",
                [Path("/bundle/ck/kernel.v01.bc")],
                False,
            ),
        ],
        ids=[
            "bundle-branch-glob-empty",
            "shared-branch-val-products-empty",
            "shared-branch-candidate-missing",
        ],
    )
    def test_pick_val_label_raises_when_no_match(
        self, label_for_helper, mocker, name, val_label_path, glob_return, exists_return
    ):
        label = label_for_helper()
        label.name = name
        mocker.patch.object(label, "_val_label_directory", return_value=val_label_path)
        mocker.patch(_PATCH_PATH_GLOB, return_value=glob_return)
        mocker.patch(_PATCH_PATH_EXISTS, return_value=exists_return)
        with pytest.raises(Exception, match="No label for comparison found."):
            label._pick_val_label(Path("/unused"))

    # -- _find_prior_version_label ---------------------------------------

    def test_find_prior_version_label_returns_hit(self, label_for_helper, mocker):
        label = label_for_helper()
        hit = "/bundle/spice_kernels/ck/kernel_old.xml"
        mocker.patch(_PATCH_GLOB, side_effect=self._level1_hit(hit))
        assert label._find_prior_version_label() == hit

    def test_find_prior_version_label_returns_none_on_no_match(self, label_for_helper, mocker):
        label = label_for_helper()
        mocker.patch(_PATCH_GLOB, return_value=[])
        assert label._find_prior_version_label() is None

    # -- _find_similar_type_label -----------------------------------------

    def test_find_similar_type_label_returns_hit(self, label_for_helper, mocker):
        label = label_for_helper()
        mocker.patch(_PATCH_PATH_GLOB, return_value=[Path("/bundle/spice_kernels/ck/kern.bc")])
        mocker.patch(_PATCH_PATH_EXISTS, return_value=True)
        assert label._find_similar_type_label() == str(Path("/bundle/spice_kernels/ck/kern.xml"))

    def test_find_similar_type_label_returns_none_when_val_products_empty(self, label_for_helper, mocker):
        label = label_for_helper()
        mocker.patch(_PATCH_PATH_GLOB, return_value=[])
        assert label._find_similar_type_label() is None

    # -- _find_insight_fallback_label -------------------------------------

    def test_find_insight_fallback_label_returns_hit_and_logs(self, label_for_helper, mocker):
        label = label_for_helper()
        mocker.patch(
            _PATCH_PATH_GLOB,
            return_value=[Path("/root/data/insight_spice/spice_kernels/ck/insight_ck.bc")],
        )
        mocker.patch(_PATCH_PATH_EXISTS, return_value=True)
        mock_log = mocker.patch("pds.naif_pds4_bundler.classes.label.label.logging.warning")
        result = label._find_insight_fallback_label()
        assert result == str(Path("/root/data/insight_spice/spice_kernels/ck/insight_ck.xml"))
        # The "Comparing with..." message must only fire on success, and
        # must be the ONLY warning logged (no leftover "not found" message).
        mock_log.assert_called_once_with("-- Comparing with InSight test label.")

    def test_find_insight_fallback_label_returns_none_when_val_products_empty(self, label_for_helper, mocker):
        label = label_for_helper()
        mocker.patch(_PATCH_PATH_GLOB, return_value=[])
        mock_log = mocker.patch("pds.naif_pds4_bundler.classes.label.label.logging.warning")
        assert label._find_insight_fallback_label() is None
        mock_log.assert_called_once_with("-- No label for comparison found.")
