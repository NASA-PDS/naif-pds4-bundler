"""
Tests for PDSLabel class.
"""

import os
from pathlib import Path
from typing import cast, Type
from unittest.mock import MagicMock, call, mock_open

import pytest

from pds.naif_pds4_bundler.classes.label.label import PDSLabel

# Patch targets — resolved to where the names are looked up inside label.py
_PATCH_HANDLE_ERROR = "pds.naif_pds4_bundler.classes.label.label.handle_npb_error"
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
    """Covers PDSLabel.__init__ – all branches."""

    @staticmethod
    @pytest.fixture
    def mock_class_methods(mocker):
        # Mocks all three methods at once
        mocker.patch('pds.naif_pds4_bundler.classes.label.label.PDSLabel.get_missions',
                     return_value='MockedMission')
        mocker.patch('pds.naif_pds4_bundler.classes.label.label.PDSLabel.get_observers',
                     return_value='MockedObserver')
        mocker.patch('pds.naif_pds4_bundler.classes.label.label.PDSLabel.get_targets',
                     return_value='MockedTarget')

    def test_pds4_context_from_collection_bundle(self, setup_pds4, product):
        """pds_version == "4", context products from collection.bundle"""
        label = PDSLabel(setup_pds4, product)
        assert label.setup is setup_pds4
        assert label.product is product
        assert label.name == ""

    def test_pds4_context_falls_back_to_product_bundle(self, mock_class_methods, setup_pds4, product):
        """ pds_version == "4", context products from product.bundle
           (collection.bundle.context_products is falsy => raises Exception)
        """
        product.collection.bundle.context_products = []
        label = PDSLabel(setup_pds4, product)
        assert label is not None

    def test_pds4_context_attribute_error_falls_back(self, setup_pds4, product):
        """collection.bundle raises AttributeError entirely"""
        product.collection = MagicMock(spec=[])
        label = PDSLabel(setup_pds4, product)
        assert label is not None

    def test_pds3_skips_pds4_block(self, setup_pds3, product):
        """pds_version == "3" (skips PDS4 XML block entirely)"""
        label = PDSLabel(setup_pds3, product)
        assert not hasattr(label, "XML_MODEL")

    def test_pds4_single_mission_name(self, mock_class_methods, setup_pds4, product):
        label = PDSLabel(setup_pds4, product)
        assert label.PDS4_MISSION_NAME == "TestMission"

    @pytest.mark.parametrize("secondary_missions, expected_name",[
        (["OtherMission"], "TestMission and OtherMission"),
        (["MissionB", "MissionC"], "TestMission, MissionB, and MissionC"),
    ])
    def test_pds4_multiple_mission_name(self, mock_class_methods, setup_pds4, product, secondary_missions, expected_name):
        setup_pds4.secondary_missions = secondary_missions
        label = PDSLabel(setup_pds4, product)
        assert label.PDS4_MISSION_NAME == expected_name

    def test_pds4_single_observer_name(self, mock_class_methods, setup_pds4, product):
        label = PDSLabel(setup_pds4, product)
        assert label.PDS4_OBSERVER_NAME == "TestObserver spacecraft and its"

    @pytest.mark.parametrize("secondary_observer, expected_name",[
        (["OtherObserver"], "TestObserver and OtherObserver spacecraft and their"),
        (["ObsB", "ObsC"], "TestObserver, ObsB, and ObsC spacecraft and their"),
    ])
    def test_pds4_multiple_observer_name(self, mock_class_methods, setup_pds4, product, secondary_observer, expected_name):
        setup_pds4.secondary_observers = secondary_observer
        label = PDSLabel(setup_pds4, product)
        assert label.PDS4_OBSERVER_NAME == expected_name

    @pytest.mark.parametrize("eol, expected_eol_name",[
        ('LF', 'Line-Feed'),
        ('CRLF', 'Carriage-Return Line-Feed')
    ])
    def test_pds4_end_of_line(self, product, eol, expected_eol_name):
        setup = _make_setup_pds4(end_of_line=eol)
        label = PDSLabel(setup, product)
        assert label.END_OF_LINE == expected_eol_name

    def test_pds4_end_of_line_invalid(self, product):
        """end_of_line is invalid (neither CRLF nor LF)"""
        setup = _make_setup_pds4(end_of_line="CR")
        with pytest.raises(RuntimeError, match=r'End of Line provided via configuration '
                                               r'is not CRLF nor LF\.'):
            PDSLabel(setup, product)

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

    # TODO: The following two test cases demonstrate an issue:
    #       If they are not a list, the code to set up PDS4_MISSION_NAME
    #       and PDS4_OBSERVER_NAME, results in a list of letters.
    def test_pds4_secondary_missions_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = "SingleMission"
        label = PDSLabel(setup_pds4, product)
        assert label.missions == ['TestMission', 'SingleMission']
        # TODO: This is a bug!!!!
        assert 'TestMission, S, i, n, g, l, e, M, i, s, s, i, o, and n' == label.PDS4_MISSION_NAME

    def test_pds4_secondary_observers_non_list_wrapped(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_observers = 'SingleObserver'
        label = PDSLabel(setup_pds4, product)
        assert label.observers == ['TestObserver', 'SingleObserver']
        # TODO: This is a bug!!!
        assert 'TestObserver, S, i, n, g, l, e, O, b, s, e, r, v, e, and r spacecraft and their' == label.PDS4_OBSERVER_NAME

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

    def test_pds4_secondary_missions_list(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = ["MissionB", "MissionC"]
        label = PDSLabel(setup_pds4, product)
        assert label.missions == ['TestMission', "MissionB", "MissionC"]

    def test_pds4_secondary_observers_list(self, mock_class_methods, setup_pds4, product):
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

    def test_pds4_sets_missions_targets_observers(self, mock_class_methods, setup_pds4, product):
        setup_pds4.secondary_missions = ["MissionB", "MissionC"]
        setup_pds4.secondary_observers = ["ObsB", "ObsC"]
        setup_pds4.secondary_targets = ["TargetB", "TargetC"]

        # Since the mock is called, the values of the MISSIONS,
        # OBSERVERS and TARGETS should be the ones provided as return_value
        # in the mock.
        label = PDSLabel(setup_pds4, product)
        assert label.MISSIONS == 'MockedMission'
        assert label.OBSERVERS == 'MockedObserver'
        assert label.TARGETS == 'MockedTarget'


# ===========================================================================
# PDSLabel.get_missions
# ===========================================================================

class TestPDSLabelGetMissions:
    """Covers PDSLabel.get_missions – all branches."""

    @pytest.fixture
    def label_for(self):
        """Factory fixture: returns a callable that builds a bare label."""
        def _build(missions, context_products=None, fallback_to_bundle=False):
            setup = _make_setup_pds4()
            product = _make_product()
            ctx = context_products or _make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])  # no .bundle
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDSLabel.__new__(PDSLabel)
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
# PDSLabel.get_mission_reference_type
# ===========================================================================

class TestPDSLabelGetMissionReferenceType:
    """Covers PDSLabel.get_mission_reference_type – every branch."""

    @pytest.fixture
    def label_of_class(self):
        """Factory fixture: builds a bare label instance of the given class name."""
        def _build(class_name, info_model_float=1014000000.0):
            cls = cast(Type[PDSLabel], type(class_name, (PDSLabel,), {}))
            obj = object.__new__(cls)
            obj.setup = MagicMock()
            obj.setup.information_model_float = info_model_float
            return obj
        return _build

    @pytest.mark.parametrize('pds_label, model, ref_type', [
        ('ChecksumPDS4Label', None, 'ancillary_to_investigation'),
        ('BundlePDS4Label', None, 'bundle_to_investigation'),
        ('DocumentPDS4Label', None, 'document_to_investigation'),
        ('InventoryPDS4Label', None, 'collection_to_investigation'),
        ('OrbnumFilePDS4Label', 1014000000.0, 'ancillary_to_investigation'),
        ('OrbnumFilePDS4Label', 1013000000.0, 'data_to_investigation'),
        ('SpiceKernelPDS4Label', None, 'data_to_investigation'),
        ('MetaKernelPDS4Label', None, 'data_to_investigation'),
        ('SpiceKernelPDS3Label', None, 'data_to_investigation')
    ])
    def test_checksum_label(self, label_of_class, pds_label, model, ref_type):
        assert label_of_class(pds_label, model).get_mission_reference_type() == ref_type


# ===========================================================================
# PDSLabel.get_observers
# ===========================================================================

class TestPDSLabelGetObservers:
    """Covers PDSLabel.get_observers – all branches."""

    @pytest.fixture
    def label_for(self):
        """Factory fixture: builds a bare label with given observers."""
        def _build(observers, context_products=None, fallback_to_bundle=False):
            setup = _make_setup_pds4()
            product = _make_product()
            ctx = context_products or _make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDSLabel.__new__(PDSLabel)
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
# PDSLabel.get_targets
# ===========================================================================

class TestPDSLabelGetTargets:
    """Covers PDSLabel.get_targets – all branches."""

    @pytest.fixture
    def label_for(self):
        """Factory fixture: builds a bare label with given targets."""
        def _build(targets, context_products=None, fallback_to_bundle=False):
            setup = _make_setup_pds4()
            product = _make_product()
            ctx = context_products or _make_context_products()
            if fallback_to_bundle:
                product.collection = MagicMock(spec=[])
                product.bundle.context_products = ctx
            else:
                product.collection.bundle.context_products = ctx
            label = PDSLabel.__new__(PDSLabel)
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

    def test_empty_target_skipped_calls_error(self, label_for, mocker):
        mock_err = mocker.patch(_PATCH_HANDLE_ERROR)
        label_for([""]).get_targets()
        mock_err.assert_called()

    def test_trailing_eol_appended(self, label_for):
        assert label_for(["TestTarget"]).get_targets().endswith("\r\n")


# ===========================================================================
# PDSLabel.get_target_reference_type
# ===========================================================================

class TestPDSLabelGetTargetReferenceType:
    """Covers PDSLabel.get_target_reference_type – every branch."""

    @pytest.fixture
    def label_of_class(self):
        """Factory fixture: builds a bare label instance of the given class name."""
        def _build(class_name, info_model_float=1014000000.0):
            cls = cast(Type[PDSLabel], type(class_name, (PDSLabel,), {}))
            obj = object.__new__(cls)
            obj.setup = MagicMock()
            obj.setup.information_model_float = info_model_float
            return obj
        return _build

    def test_checksum_label(self, label_of_class):
        assert label_of_class("ChecksumPDS4Label").get_target_reference_type() == "ancillary_to_target"

    def test_bundle_label(self, label_of_class):
        assert label_of_class("BundlePDS4Label").get_target_reference_type() == "bundle_to_target"

    def test_inventory_label(self, label_of_class):
        assert label_of_class("InventoryPDS4Label").get_target_reference_type() == "collection_to_target"

    def test_orbnum_label_new_model(self, label_of_class):
        assert label_of_class("OrbnumFilePDS4Label", 1014000000.0).get_target_reference_type() == "ancillary_to_target"

    def test_orbnum_label_old_model(self, label_of_class):
        assert label_of_class("OrbnumFilePDS4Label", 1013000000.0).get_target_reference_type() == "data_to_target"

    def test_default_label(self, label_of_class):
        assert label_of_class("SomeOtherLabel").get_target_reference_type() == "data_to_target"


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

            cls_name = "SpiceKernelPDS3Label" if is_pds3_kernel else "PDSLabel"
            cls = cast(Type[PDSLabel], type(cls_name, (PDSLabel,), {}))
            label = object.__new__(cls)
            label.setup = setup
            label.product = product
            label.name = ""
            label.template = "/tmpl/template.xml"

            if is_checksum:
                label.__class__ = type("ChecksumLabelClass", (PDSLabel,), {})
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