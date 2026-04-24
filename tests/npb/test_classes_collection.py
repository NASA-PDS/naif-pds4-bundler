"""Tests for Collection class — one test class per method, 100% branch coverage."""
import logging
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.collection.collection import Collection


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

def make_setup(pds_version="4", increment=True, release="3",
               mission_name="TEST_MISSION", mission_acronym="test",
               observer="TEST_OBSERVER", target="TEST_TARGET",
               logical_identifier="urn:nasa:pds:test_bundle",
               bundle_directory="/fake/bundle",
               staging_directory="/fake/staging"):
    """Return a minimal mock Setup object."""
    return MagicMock(
        pds_version=pds_version,
        increment=increment,
        release=release,
        mission_name=mission_name,
        mission_acronym=mission_acronym,
        observer= observer,
        target=target,
        logical_identifier=logical_identifier,
        bundle_directory=bundle_directory,
        staging_directory=staging_directory,
        kernel_list_config={}
    )


def make_collection(c_type="spice_kernel", pds_version="4", **setup_kwargs):
    """Instantiate a Collection with minimal mocking."""
    setup = make_setup(pds_version=pds_version, **setup_kwargs)
    # Patch set_collection_lid so __init__ doesn't fail on missing 'type' attr
    with patch.object(Collection, "set_collection_lid", autospec=True):
        col = Collection(c_type, setup, bundle=MagicMock())
    col.type = c_type  # attribute normally set by subclass
    return col, setup


# ---------------------------------------------------------------------------
# Collection.__init__
# ---------------------------------------------------------------------------

class TestCollectionInit:
    """Tests for Collection.__init__."""

    def test_basic_attributes_set(self):
        setup = make_setup(pds_version="4")
        bundle = MagicMock()
        with patch.object(Collection, "set_collection_lid", autospec=True) as mock_lid:
            col = Collection("spice_kernel", setup, bundle)
            mock_lid.assert_called_once_with(col)

        assert col.bundle is bundle
        assert col.name == "spice_kernel"
        assert col.product == []
        assert col.setup is setup
        assert col.vid == ""
        assert col.updated is False

    def test_set_collection_lid_called_when_pds4(self):
        """set_collection_lid must be called when pds_version == '4'."""
        setup = make_setup(pds_version="4")
        with patch.object(Collection, "set_collection_lid", autospec=True) as mock_lid:
            Collection("spice_kernel", setup, bundle=MagicMock())
        mock_lid.assert_called_once()

    def test_set_collection_lid_not_called_when_pds3(self):
        """set_collection_lid must NOT be called when pds_version != '4'."""
        setup = make_setup(pds_version="3")
        with patch.object(Collection, "set_collection_lid", autospec=True) as mock_lid:
            Collection("spice_kernel", setup, bundle=MagicMock())
            Collection("spice_kernel", setup, bundle=MagicMock())
        mock_lid.assert_not_called()


# ---------------------------------------------------------------------------
# Collection.add
# ---------------------------------------------------------------------------

class TestCollectionAdd:
    """Tests for Collection.add."""

    def test_add_appends_product(self):
        col, _ = make_collection()
        product = MagicMock()
        col.add(product)
        assert product in col.product

    def test_add_sets_updated_true(self):
        col, _ = make_collection()
        assert col.updated is False
        col.add(MagicMock())
        assert col.updated is True

    def test_add_multiple_products(self):
        col, _ = make_collection()
        p1, p2 = MagicMock(), MagicMock()
        col.add(p1)
        col.add(p2)
        assert col.product == [p1, p2]


# ---------------------------------------------------------------------------
# Collection.get_mission_and_observer_and_target
# ---------------------------------------------------------------------------

class TestCollectionGetMissionAndObserverAndTarget:
    """Tests for Collection.get_mission_and_observer_and_target."""

    PATTERN = r"^test_kernel.*"

    def _make_col_with_list(self, ker_config_overrides=None):
        """Return a Collection whose .list and setup.kernel_list_config are wired up."""
        col, setup = make_collection()

        # Build a minimal ker_config for the matched pattern
        ker_config = {}
        if ker_config_overrides:
            ker_config.update(ker_config_overrides)

        setup.kernel_list_config = {self.PATTERN: ker_config}
        col.list = MagicMock(json_config={"k1": {"@pattern": self.PATTERN}})
        return col, setup

    def test_no_pattern_match_returns_defaults(self):
        """Pattern does NOT match (falls through to default assignment)"""
        col, setup = self._make_col_with_list()
        # Use a name that doesn't match PATTERN
        missions, observers, targets = col.get_mission_and_observer_and_target("unrelated_file.bc")
        assert missions == [setup.mission_name]
        assert observers == [setup.observer]
        assert targets == [setup.target]

    def test_match_no_optional_keys_uses_setup_defaults(self):
        """Pattern matches, no optional keys → fall back to set up defaults"""
        col, setup = self._make_col_with_list(ker_config_overrides={})
        missions, observers, targets = col.get_mission_and_observer_and_target("test_kernel_001.bc")
        assert missions == [setup.mission_name]
        assert observers == [setup.observer]
        assert targets == [setup.target]

    @pytest.mark.parametrize('config, expected_missions, expected_targets, expected_obs',[
        ({"missions": {"mission_name": ["MISSION_A", "MISSION_B"]}},
         ["MISSION_A", "MISSION_B"], ['TEST_TARGET'], ['TEST_OBSERVER']),
        ({"targets": {"target": ["MARS", "PHOBOS"]}},
         ['TEST_MISSION'], ["MARS", "PHOBOS"], ['TEST_OBSERVER']),
        ({"observers": {"observer": ["MRO", "MEX"]}},
         ['TEST_MISSION'], ['TEST_TARGET'], ["MRO", "MEX"]),
        ({"missions": {"mission_name": ["M1"]},
          "targets": {"target": ["T1"]},
          "observers": {"observer": ["O1"]}},
         ["M1"], ["T1"], ["O1"])
    ])
    def test_match_with_keys(self, config, expected_missions, expected_targets, expected_obs):
        """Pattern matches, all optional keys present"""
        col, setup = self._make_col_with_list(ker_config_overrides=config)
        missions, obs, targets = col.get_mission_and_observer_and_target("test_kernel_001.bc")
        assert missions == expected_missions
        assert targets == expected_targets
        assert obs == expected_obs

    def test_empty_json_config_returns_empty_lists(self):
        """Empty JSON config → loop body never executes"""
        col, setup = make_collection()
        mock_list = MagicMock()
        mock_list.json_config = {}
        col.list = mock_list
        missions, observers, targets = col.get_mission_and_observer_and_target("any_file.bc")
        assert missions == []
        assert observers == []
        assert targets == []


# ---------------------------------------------------------------------------
# Collection.set_collection_lid
# ---------------------------------------------------------------------------

class TestCollectionSetCollectionLid:
    """Tests for Collection.set_collection_lid."""

    def test_lid_set_when_not_pds3(self):
        col, setup = make_collection(c_type="spice_kernel", pds_version="4")
        col.set_collection_lid()
        expected = f"{setup.logical_identifier}:spice_kernel"
        assert col.lid == expected

    def test_lid_not_set_when_pds3(self):
        col, setup = make_collection(pds_version="3")
        col.set_collection_lid()
        assert not hasattr(col, "lid")


# ---------------------------------------------------------------------------
# Collection.set_collection_vid
# ---------------------------------------------------------------------------

class TestCollectionSetCollectionVid:
    """Tests for Collection.set_collection_vid."""

    # Helper to get a ready-to-use collection without triggering "lid"
    # side effects.
    @staticmethod
    def _collection(c_type="spice_kernel", **setup_kwargs):
        col, setup = make_collection(c_type=c_type, **setup_kwargs)
        col.type = c_type
        return col, setup

    def test_no_increment_uses_release(self, caplog):
        """Increment is False."""
        col, setup = self._collection(increment=False, release="5")
        col.set_collection_vid()
        assert col.vid == "5.0"

    @pytest.mark.parametrize("updated, fake_versions, vid", [
        (True,
         ["/fake/bundle/test_spice/spice_kernels/collection_v003.xml"],
         "4.0"),
        (False,
         ["/fake/bundle/test_spice/spice_kernels/collection_v003.xml"],
         "3.0"),
        (True,
         ["/fake/bundle/test_spice/spice_kernels/collection_v001.xml",
          "/fake/bundle/test_spice/spice_kernels/collection_v003.xml",
          "/fake/bundle/test_spice/spice_kernels/collection_v002.xml"],
         "4.0") # v003 + 1
    ])
    def test_increment_true_success_glob(self, updated, fake_versions, vid):
        col, _ = self._collection(increment=True)
        col.updated = updated
        with patch("pds.naif_pds4_bundler.classes.collection.collection.glob.glob",
                   return_value=fake_versions):
            col.set_collection_vid()
        assert col.vid == vid

    @pytest.mark.parametrize("c_type, vid",[
        ('spice_kernel', '7.0'),
        ('document', '1.0')
    ])
    def test_increment_glob_fails(self, c_type, vid, caplog):
        col, setup = self._collection(c_type=c_type, increment=True, release="7")
        col.updated = True
        # glob returns empty → IndexError on [-1] → triggers except block
        with patch("pds.naif_pds4_bundler.classes.collection.collection.glob.glob",
                   return_value=[]):
            with caplog.at_level(logging.WARNING):
                col.set_collection_vid()
        assert col.vid == vid

    @pytest.mark.parametrize("c_type, vid", [
        ("spice_kernel", "2.0"),
         ("miscellaneous", "1.0")
    ])
    def test_increment_glob_raises_exception(self, c_type, vid, caplog):
        """Ensure any BaseException (not just IndexError) triggers fallback."""
        col, setup = self._collection(c_type=c_type, increment=True, release="2")
        col.updated = False
        with patch("pds.naif_pds4_bundler.classes.collection.collection.glob.glob",
                   side_effect=OSError("disk error")):
            with caplog.at_level(logging.WARNING):
                col.set_collection_vid()
        assert col.vid == vid
