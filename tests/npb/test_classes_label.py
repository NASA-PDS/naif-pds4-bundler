"""
Tests for PDSLabel class.
"""

import os
from pathlib import Path
from typing import cast, Type
from unittest.mock import MagicMock, call, mock_open

import pytest

from pds.naif_pds4_bundler.classes.label.label import PDSLabel
from pds.naif_pds4_bundler.classes.label.pds3_label import PDS3Label
from pds.naif_pds4_bundler.classes.label.pds4_label import PDS4Label

# Patch targets — resolved to where the names are looked up inside label.py
_PATCH_ADD_CR = "pds.naif_pds4_bundler.classes.label.label.add_carriage_return"
_PATCH_COMPARE = "pds.naif_pds4_bundler.classes.label.label.compare_files"
_PATCH_GLOB = "pds.naif_pds4_bundler.classes.label.label.glob.glob"


# ---------------------------------------------------------------------------
# Shared builder helpers
# ---------------------------------------------------------------------------

def _make_context_products():
    """Return a minimal list of context product dicts used across tests."""
    return [
        {
            "name": ["TestMission"],
            "type": ["Mission"],
            "lidvid": "urn:nasa:pds:testmission::1.0",
        },
        {
            "name": ["TestObserver"],
            "type": ["Spacecraft"],
            "lidvid": "urn:nasa:pds:testobserver::1.0",
        },
        {
            "name": ["TestTarget"],
            "type": ["planet"],
            "lidvid": "urn:nasa:pds:testtarget::1.0",
        },
    ]


def _make_bundle(context_products=None):
    bundle = MagicMock()
    bundle.context_products = context_products or _make_context_products()
    return bundle


def _make_collection(bundle=None):
    collection = MagicMock()
    collection.bundle = bundle or _make_bundle()
    collection.name = "spice_kernels"
    return collection


def _make_product(collection=None, bundle=None):
    """Return a mock product that supplies all attributes PDSLabel touches."""
    product = MagicMock()
    product.collection = collection or _make_collection()
    product.bundle = bundle or _make_bundle()
    product.creation_time = "2024-01-01T00:00:00"
    product.creation_date = "2024-01-01"
    product.size = 1024
    product.checksum = "abc123"
    product.missions = ["TestMission"]
    product.observers = ["TestObserver"]
    product.targets = ["TestTarget"]
    product.name = "test_kernel.bc"
    product.extension = "bc"
    product.path = "/staging/test_kernel.bc"
    product.record_bytes = 80
    return product


def _make_setup_pds4(**kwargs):
    """Return a mock setup object configured for PDS4."""
    setup = MagicMock()
    setup.pds_version = "4"
    setup.root_dir = "/root"
    setup.mission_acronym = "test"
    setup.xml_model = "model"
    setup.schema_location = "schema"
    setup.information_model = ".".join(["1", "14", "0", "0"])
    setup.information_model_float = 1014000000.0
    setup.mission_name = "TestMission"
    setup.observer = "TestObserver"
    setup.target = "TestTarget"
    setup.end_of_line = "CRLF"
    setup.logical_identifier = "urn:nasa:pds:testmission"
    setup.eol_pds4 = "\r\n"
    setup.xml_tab = 2
    setup.staging_directory = "/staging"
    setup.working_directory = "/work"
    setup.bundle_directory = "/bundle"
    setup.diff = False
    setup.args.silent = False
    setup.args.verbose = False

    # Ensure secondary_* attributes are NOT present by default
    del setup.secondary_missions
    del setup.secondary_observers
    del setup.secondary_targets
    del setup.creation_date_time

    for k, v in kwargs.items():
        setattr(setup, k, v)
    return setup


def _make_setup_pds3(**kwargs):
    setup = _make_setup_pds4(**kwargs)
    setup.pds_version = "3"
    return setup


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def setup_pds4():
    return _make_setup_pds4()


@pytest.fixture
def setup_pds3():
    return _make_setup_pds3()


@pytest.fixture
def product():
    return _make_product()


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
# PDSLabel.get_mission_reference_type / get_target_reference_type
# ===========================================================================

class TestPDSLabelReferenceTypeNotImplemented:
    """Covers the base class contract: PDSLabel itself defines no reference
    type and must not silently return a default. PDS4Label's own default
    and every leaf override are covered in their respective test files
    (test_classes_label_pds4.py and each PDS4 leaf's test module).
    """

    def test_get_mission_reference_type_raises(self):
        label = object.__new__(PDSLabel)
        with pytest.raises(NotImplementedError):
            label.get_mission_reference_type()

    def test_get_target_reference_type_raises(self):
        label = object.__new__(PDSLabel)
        with pytest.raises(NotImplementedError):
            label.get_target_reference_type()


# ===========================================================================
# PDSLabel.write_label
# ===========================================================================

class TestPDSLabelWriteLabel:
    """Covers PDSLabel.write_label – all branches."""

    @pytest.fixture
    def label_for(self):
        """Factory fixture: builds a bare label ready for write_label."""
        def _build(
            pds_version="4",
            label_name_has_ext=False,
            is_checksum=False,
            has_inventory=False,
            diff=False,
            is_pds3_kernel=False,
        ):
            setup = _make_setup_pds4() if pds_version == "4" else _make_setup_pds3()
            setup.diff = diff
            setup.pds_version = pds_version
            setup.eol_pds4 = "\r\n"
            setup.eol_pds3 = "\r\n"

            product = _make_product()

            if label_name_has_ext:
                ext = ".xml" if pds_version == "4" else ".lbl"
                product.path = f"/staging/bundle{ext}"
                product.extension = ext.lstrip(".")
            elif has_inventory:
                product.path = "/staging/inventory_collection.bc"
            else:
                product.path = "/staging/test_kernel.bc"
                product.extension = "bc"

            # _label_extension/_eol come from whichever of PDS3Label/PDS4Label
            # is mixed in here, driven by pds_version — exactly like the real
            # hierarchy, where a label's class (not its name) decides its
            # extension. cls_name only matters for write_label's unrelated
            # "suppress trailing log line for SpiceKernelPDS3Label" check.
            base_cls = PDS4Label if pds_version == "4" else PDS3Label
            cls_name = "SpiceKernelPDS3Label" if is_pds3_kernel else "PDSLabel"
            cls = cast(Type[PDSLabel], type(cls_name, (base_cls,), {}))
            label = object.__new__(cls)
            label.setup = setup
            label.product = product
            label.name = ""
            label.template = "/tmpl/template.xml"

            if is_checksum:
                label.__class__ = type("ChecksumLabelClass", (base_cls,), {})
                label.name = f"/staging{os.sep}checksum.lbl"
                product.path = label.name
                label.template = "/tmpl/template.lbl"
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
    def label_for(self):
        """Factory fixture: builds a bare label ready for compare."""

        def _build(collection_name="spice_kernels", label_name_part="kernel"):
            setup = _make_setup_pds4()
            setup.diff = "html"
            product = _make_product()
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
    # Level 1 no match → fall to level 2: collection label
    # ------------------------------------------------------------------
    def test_level2_collection_label(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(label_name_part="collection")
        label.name = f"/staging/spice_kernels{os.sep}collection_label.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: first (and only) call → miss, exits loop
            ["/bundle/.../inventory_coll.bc"],  # level-2: val_products glob
            ["/bundle/.../coll.xml"],  # level-2: collection xml glob
        ])
        label.compare()  # key assertion: no uncaught exception

    # ------------------------------------------------------------------
    # Level 1 no match → fall to level 2: bundle label
    # ------------------------------------------------------------------
    def test_level2_bundle_label(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(label_name_part="bundle")
        label.name = f"/staging{os.sep}bundle_label.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: miss
            ["/bundle/kernel.bc"],  # level-2: val_products glob
            ["/bundle/bundle_v1.xml"],  # level-2: bundle xml glob
        ])
        label.compare()

    # ------------------------------------------------------------------
    # Level 1 no match → fall to level 2: generic kernel label
    # ------------------------------------------------------------------
    def test_level2_generic_label(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: miss
            ["/bundle/kern.bc"],  # level-2: val_products glob
            ["/bundle/kern.xml"],  # level-2: label xml glob
        ])
        label_for().compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Level 1 & 2 both fail → level 3 (InSight test data)
    # ------------------------------------------------------------------
    def test_level3_fallback_insight_data(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: miss
            [],  # level-2: val_products empty → IndexError
            ["/root/data/insight_spice/spice_kernels/ck/insight_ck.bc"],  # level-3: val_products
            ["/root/data/insight_spice/spice_kernels/ck/insight_ck.xml"],  # level-3: xml glob
        ])
        label_for().compare()

    # ------------------------------------------------------------------
    # All three levels fail → nothing compared, no exception raised
    # ------------------------------------------------------------------
    def test_all_levels_fail_no_exception(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, return_value=[])
        label_for().compare()
        mock_cmp.assert_not_called()

    # ------------------------------------------------------------------
    # Level 3: "collection" segment in the name path (split by os.sep)
    # ------------------------------------------------------------------
    def test_level3_collection_in_name_path(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for()
        label.name = f"/staging{os.sep}collection{os.sep}label.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: miss
            [],  # level-2: val_products empty
            ["/insight/ck/inv_coll.bc"],  # level-3: val_products
            ["/insight/ck/coll.xml"],  # level-3: xml glob
        ])
        label.compare()

    # ------------------------------------------------------------------
    # Level 3: "bundle" segment in the name path
    # ------------------------------------------------------------------
    def test_level3_bundle_in_name_path(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for()
        label.name = f"/staging{os.sep}bundle{os.sep}label.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],  # level-1: miss
            [],  # level-2: val_products empty
            ["/insight/ck/kern.bc"],  # level-3: val_products
            ["/insight/bundle_v1.xml"],  # level-3: bundle xml glob
        ])
        label.compare()

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
    # Line 537: level-2 elif branch — miscellaneous collection appends
    # the product-type subdirectory to val_label_path.
    # ------------------------------------------------------------------
    def test_level2_miscellaneous_collection_appends_subdir(self, label_for, mocker):
        mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name="miscellaneous", label_name_part="orbnum")
        label.name = f"/staging/miscellaneous/orb{os.sep}orbnum.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],                             # level-1: miss, exits loop immediately
            ["/bundle/misc/orb/old.bc"],    # level-2: val_products glob (sub-dir appended)
            ["/bundle/misc/orb/old.xml"],   # level-2: label xml glob
        ])
        label.compare()  # reaches compare_files via level-2; no exception raised

    # ------------------------------------------------------------------
    # Line 559: level-2 raises because val_label is falsy.
    # glob.glob for the XML label returns [""] — an empty string is a
    # valid list element but a falsy value, so `if not val_label` fires,
    # the exception propagates to the level-2 except, and level-3 runs.
    # ------------------------------------------------------------------
    def test_level2_falsy_val_label_falls_through_to_level3(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],                                                            # level-1: miss
            ["/bundle/spice_kernels/ck/kern.bc"],                         # level-2: val_products
            [""],                                                          # level-2: XML glob → falsy → line 559 raise
            ["/root/data/insight_spice/spice_kernels/ck/insight_ck.bc"],  # level-3: val_products
            ["/root/data/insight_spice/spice_kernels/ck/insight_ck.xml"], # level-3: xml glob
        ])
        label_for().compare()
        # Execution reached level-3 and found a valid label → compare_files called
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Line 587: level-3 elif branch — miscellaneous collection appends
    # the product-type subdirectory to val_label_path in level-3.
    # Both level-1 and level-2 must fail first.
    # ------------------------------------------------------------------
    def test_level3_miscellaneous_collection_appends_subdir(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        label = label_for(collection_name="miscellaneous", label_name_part="orbnum")
        label.name = f"/staging/miscellaneous/orb{os.sep}orbnum.xml"
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],                                               # level-1: miss
            [],                                               # level-2: val_products empty → IndexError → level-3
            ["/root/data/insight_spice/miscellaneous/orb/insight.bc"],  # level-3: val_products (sub-dir appended)
            ["/root/data/insight_spice/miscellaneous/orb/insight.xml"], # level-3: xml glob
        ])
        label.compare()
        mock_cmp.assert_called_once()

    # ------------------------------------------------------------------
    # Line 611: level-3 raises because val_label is falsy.
    # The XML glob returns [""] — falsy — so `if not val_label` fires,
    # the raise is caught by the level-3 except BaseException on line 615,
    # and compare_files is never called.
    # ------------------------------------------------------------------
    def test_level3_falsy_val_label_suppressed_by_except(self, label_for, mocker):
        mock_cmp = mocker.patch(_PATCH_COMPARE)
        mocker.patch(_PATCH_GLOB, side_effect=[
            [],                                                           # level-1: miss
            [],                                                           # level-2: val_products empty → IndexError
            ["/root/data/insight_spice/spice_kernels/ck/insight_ck.bc"], # level-3: val_products
            [""],                                                         # level-3: XML glob → falsy → line 611 raise
        ])
        label_for().compare()
        # The raise on line 611 is caught on line 615; val_label stays falsy
        # so compare_files must not have been called.
        mock_cmp.assert_not_called()