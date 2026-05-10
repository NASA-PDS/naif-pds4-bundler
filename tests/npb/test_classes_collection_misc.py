"""Tests for MiscellaneousCollection.
"""
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.collection.collection_misc import MiscellaneousCollection


# ---------------------------------------------------------------------------
# Patch target
# ---------------------------------------------------------------------------

_SET_LID = "pds.naif_pds4_bundler.classes.collection.collection.Collection.set_collection_lid"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_setup(pds_version="4"):
    return MagicMock(pds_version=pds_version)


def make_bundle():
    return MagicMock()


def make_kernels():
    return MagicMock()


# ---------------------------------------------------------------------------
# MiscellaneousCollection.__init__
# ---------------------------------------------------------------------------

class TestMiscellaneousCollection:
    """Tests for MiscellaneousCollection.__init__ and the kind property."""

    @pytest.mark.parametrize("pds_version, o_type",[
        ("3", "extras"),
        ("4", "miscellaneous")
    ])
    def test_init_sets_proper_type_based_on_pds_version(self, pds_version, o_type):
        with patch(_SET_LID):
            obj = MiscellaneousCollection(make_setup(pds_version), make_bundle(), make_kernels())
        assert obj.type == o_type
        assert obj.name == o_type

    def test_pds4_calls_set_collection_lid(self):
        """set_collection_lid must be called for pds_version == '4'."""
        with patch(_SET_LID) as mock_lid:
            MiscellaneousCollection(make_setup("4"), make_bundle(), make_kernels())
        mock_lid.assert_called_once()

    def test_non_pds4_does_not_call_set_collection_lid(self):
        """set_collection_lid must NOT be called when pds_version != '4'."""
        with patch(_SET_LID) as mock_lid:
            MiscellaneousCollection(make_setup("3"), make_bundle(), make_kernels())
        mock_lid.assert_not_called()

    @pytest.mark.parametrize("pds_version", ["3", "4"])
    def test_class_attributes_properly_set(self, pds_version):
        """self.list must be assigned the kernels argument before super().__init__."""
        setup = make_setup(pds_version)
        bundle = make_bundle()
        kernels = make_kernels()
        with patch(_SET_LID):
            obj = MiscellaneousCollection(setup, bundle, kernels)
        assert obj.list is kernels
        assert obj.setup is setup
        assert obj.bundle is bundle

    @pytest.mark.parametrize("pds_version, kind",[
        ("3", "extras"),
        ("4", "miscellaneous")
    ])
    def test_kind_returns_proper_type(self, pds_version, kind):
        with patch(_SET_LID):
            obj = MiscellaneousCollection(make_setup(pds_version), make_bundle(), make_kernels())
        assert obj.kind == kind
        assert obj.kind == obj.type
