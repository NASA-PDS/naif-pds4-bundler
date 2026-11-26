"""Tests for Collection class — one test class per method, 100% branch coverage."""
import logging
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.collection.collection import Collection
from pds.naif_pds4_bundler.classes.exceptions import NPBInternalError


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


def make_collection(c_type="spice_kernels", pds_version="4", **setup_kwargs):
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
# Collection.replace
# ---------------------------------------------------------------------------

class TestCollectionReplace:
    """Tests for Collection.replace."""

    @pytest.mark.parametrize("position", [
        pytest.param(0, id="first"),
        pytest.param(1, id="middle"),
        pytest.param(2, id="last"),
    ])
    def test_replace_keeps_position(self, position: int) -> None:
        """The new element takes the old one's position in the list, and the
        other elements and their order stay the same.
        """
        # Fill the collection with a copy of the list, so that 'elements'
        # still holds the original content after the replacement.
        col, _ = make_collection()
        elements = [object(), object(), object()]
        col.product = list(elements)
        new = object()

        # Swap the element found at the position under test.
        col.replace(elements[position], new)

        # Only that position differs from the original list.
        expected = list(elements)
        expected[position] = new
        assert col.product == expected

    @pytest.mark.parametrize("updated", [
        pytest.param(False, id="not-updated"),
        pytest.param(True, id="updated"),
    ])
    def test_replace_leaves_updated_unchanged(self, updated: bool) -> None:
        """The 'updated' flag has the same value before and after a
        replacement.
        """
        # Set the list and the flag directly, because add() would always leave
        # the flag set to True.
        col, _ = make_collection()
        old = object()
        col.product = [old]
        col.updated = updated

        # Replace the only element of the collection.
        col.replace(old, object())

        # The flag keeps the value it had.
        assert col.updated is updated

    def test_replace_matches_by_identity(self) -> None:
        """Only the exact object given is replaced, even when an equal but
        distinct object comes before it in the list.
        """
        # Two separate lists with the same content are equal, but they are not
        # the same object. The lookalike goes first, where a search by
        # equality would stop.
        col, _ = make_collection()
        lookalike, old, new = ["checksum"], ["checksum"], object()
        col.product = [lookalike, old]

        # Ask to replace the second of the two.
        col.replace(old, new)

        # Compare with 'is', since '==' can't tell the two lists apart.
        assert col.product[0] is lookalike
        assert col.product[1] is new

    @pytest.mark.parametrize("c_type", ["spice_kernels", "miscellaneous"])
    @pytest.mark.parametrize("elements", [
        pytest.param([], id="empty-collection"),
        pytest.param([object()], id="unrelated-element"),
        pytest.param([["checksum"]], id="equal-element-only"),
    ])
    def test_replace_missing_element_raises(
        self, elements: list, c_type: str
    ) -> None:
        """For both the SPICE kernels and miscellaneous collections, replacing
        an element that isn't there raises NPBInternalError naming that
        collection, and leaves the collection as it was.
        """
        # Build the collection under the given name and fill it with a copy, so
        # the original list still shows what it held.
        col, _ = make_collection(c_type=c_type)
        col.product = list(elements)

        # The element to replace is a new list, so it is never one of the
        # stored objects, not even when its content matches one of them. The
        # error message must carry the name of this collection.
        with pytest.raises(NPBInternalError, match=f"{c_type} collection"):
            col.replace(["checksum"], object())

        # Comparing the ids shows that every stored object is still the same
        # one, in the same order.
        assert list(map(id, col.product)) == list(map(id, elements))
        assert col.updated is False


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
        col, _ = make_collection(pds_version="3")
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
        """When increment is False, the collection VID is set directly from
        the bundle release number instead of being derived from a previous
        version on disk.
        """
        col, _ = self._collection(increment=False, release="5")
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
        # find_latest_versioned_file globs both directories itself now via
        # Path.glob, so the patch target is pathlib.Path.glob.
        col, _ = self._collection(increment=True)
        col.updated = updated
        with patch("pathlib.Path.glob",
                   return_value=fake_versions):
            col.set_collection_vid()
        assert col.vid == vid

    @pytest.mark.parametrize("c_type, vid", [
        ('spice_kernels', '7.0'),
        ('document', '1.0')
    ])
    def test_increment_glob_fails(self, c_type, vid, caplog):
        col, _ = self._collection(c_type=c_type, increment=True, release="7")
        col.updated = True
        # An empty file list is a normal "nothing found yet" result, not an
        # error: find_latest_versioned_file returns (None, None) for it, and
        # set_collection_vid falls back to a default version (7 for
        # spice_kernels since it tracks the release; 1 for anything else).
        with patch("pathlib.Path.glob",
                   return_value=[]):
            with caplog.at_level(logging.WARNING):
                col.set_collection_vid()
        assert col.vid == vid

    def test_increment_glob_raises_exception_propagates(self):
        """Test that set_collection_vid lets a Path.glob failure (e.g. a disk
        error) propagate as an OSError, instead of silently swallowing it into a
        fallback version the way the old `except BaseException` did.

        A glob failure is a real error, not a "no previous version found" case,
        so it must not be hidden behind a made-up version number.

        TODO: This OSError propagates out of run_pipeline() (pipeline/npb.py),
              which only catches NPBError, and is caught only by the generic
              `except Exception` in __main__.py's main(). That handler prints a
              one-line message and exits with code 3, but skips everything
              handle_npb_error() normally does for a real NPBError (logging via
              the Log object, write_file_list(), write_checksum_registry(),
              template cleanup, spiceypy.kclear()). Fixing this properly likely
              means a broader refactor of pipeline error handling (e.g. having
              run_pipeline() also catch unexpected exceptions and route them
              through handle_npb_error()), not a local change to this method --
              tracked here since this test is what exercises that gap.
        """
        # Build a Collection instance to call set_collection_vid() on. The
        # specific values chosen (c_type, release, updated) don't drive any
        # assertion below: the exception fires inside Path.glob, before any of
        # set_collection_vid's own logic (fallback-by-collection-type, version
        # bump) ever gets a chance to run.
        col, _ = self._collection(c_type="spice_kernels", increment=True, release="2")
        col.updated = False

        # Replace the real Path.glob (called from find_latest_versioned_file
        # in utils.files, not from this module directly) with a mock that
        # raises OSError("disk error") instead of returning a file list.
        # This simulates a filesystem failure, which is a different
        # scenario from "no files found" (an empty list).
        with patch("pathlib.Path.glob",
                   side_effect=OSError("disk error")):

            # Call the method under test inside pytest.raises: this block passes
            # only if col.set_collection_vid() raises an OSError whose message
            # matches "disk error". It fails if the call raises nothing (meaning
            # the exception got swallowed somewhere) or raises a different
            # exception type. That's the actual check: proof that the OSError
            # reaches the caller instead of being absorbed into a fallback
            # version.
            with pytest.raises(OSError, match="disk error"):
                col.set_collection_vid()
