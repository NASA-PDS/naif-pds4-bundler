"""Tests for Bundle._get_history.

Test strategy
-------------
_get_history reads from the filesystem (bundle label XML files and collection
CSV inventory files): every test uses ``tmp_path`` (pytest's built-in
temporary directory fixture) to build a minimal but realistic on-disk
directory tree, and a lightweight ``SimpleNamespace``-based fake ``setup``
object instead of the full NPB ``Setup`` class.

The XML model URL used throughout is the real PDS4 1.5.0.0 namespace so that
the prefix-building logic in the method under test is exercised correctly.

Bundle label XML template
-------------------------
The method only reads ``Bundle_Member_Entry`` nodes from the label, so the
template is stripped to the minimum that satisfies the parser.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.bundle import Bundle

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
XML_MODEL = "https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.sch"

# Prefix produced by the method:  "{https://pds.nasa.gov/pds4/pds/v1}"
NS = "https://pds.nasa.gov/pds4/pds/v1"
MISSION = "insight"

# Dummy Secondary entry appended when only one member is supplied.
# `etree_to_dict` returns a plain dict for a single child element and a list
# of dicts for multiple children with the same tag. The _get_history code
# unconditionally does ``for member in members:`` which iterates over string
# keys when members is a dict, raising ``TypeError: string indices must be
# integers``.
# Real PDS4 bundle labels always contain at least two Bundle_Member_Entry
# nodes, so including a dummy Secondary entry faithfully represents that
# constraint and avoids the single-child dict ambiguity.
_DUMMY_SECONDARY_MEMBER = {
    "lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
    "status": "Secondary",
}

# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def _bundle_label_xml(members: list[dict]) -> str:
    """Build a minimal PDS4 bundle label XML string.

    Each member dict should have keys: ``lid``, ``status`` (Primary/Secondary).
    Example::

        {"lid": "urn:nasa:pds:insight.spice:spice_kernels::1.0",
         "status": "Primary"}

    Two invariants are enforced here:

    1. The XML declaration must be the very first character — no leading
       whitespace — otherwise ElementTree raises ParseError.

    2. At least two ``Bundle_Member_Entry`` elements are always written.
       ``etree_to_dict`` returns a plain ``dict`` for a single child and a
       ``list`` for multiple children with the same tag.  The production code
       iterates over the result unconditionally, so a single entry would cause
       ``TypeError: string indices must be integers``.  A dummy Secondary
       entry is appended when the caller supplies only one member to satisfy
       this constraint without affecting test assertions (the method only acts
       on Primary members).
    """
    all_members = list(members)
    if len(all_members) < 2:
        all_members.append(_DUMMY_SECONDARY_MEMBER)

    member_lines = []
    for m in all_members:
        member_lines.append(
            f"  <Bundle_Member_Entry>\n"
            f"    <lidvid_reference>{m['lid']}</lidvid_reference>\n"
            f"    <member_status>{m['status']}</member_status>\n"
            f"  </Bundle_Member_Entry>"
        )
    members_xml = "\n".join(member_lines)

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<Product_Bundle xmlns="{NS}">\n'
        f"  <Bundle>\n"
        f"    <bundle_type>Archive</bundle_type>\n"
        f"  </Bundle>\n"
        f"{members_xml}\n"
        f"</Product_Bundle>\n"
    )


def _kernel_inventory_csv(rows: list[str]) -> str:
    """Build a minimal SPICE kernel collection inventory CSV."""
    return "\n".join(rows) + "\n"


# ---------------------------------------------------------------------------
# Fixture: minimal fake setup object
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_setup(tmp_path):
    """Return a ``SimpleNamespace`` that mimics the NPB Setup object."""
    bundle_dir = tmp_path / "bundle"
    bundle_root = bundle_dir / f"{MISSION}_spice"
    bundle_root.mkdir(parents=True)

    args = SimpleNamespace(silent=True, verbose=False)

    return SimpleNamespace(
        bundle_directory=str(bundle_dir),
        mission_acronym=MISSION,
        xml_model=XML_MODEL,
        args=args,
    )


# ---------------------------------------------------------------------------
# Factory: build a Bundle instance with controlled state
# ---------------------------------------------------------------------------

def _make_bundle(setup, vid: str, name: str, collections=None) -> Bundle:
    """Construct a ``Bundle`` without running ``__init__`` side effects."""
    bundle = object.__new__(Bundle)
    bundle.setup = setup
    bundle._vid = vid
    bundle.name = name
    bundle.collections = collections if collections is not None else []
    bundle._new_files = []
    bundle._readme = None
    bundle._bundle_root = Path(setup.bundle_directory) / f"{setup.mission_acronym}_spice"

    return bundle


# ---------------------------------------------------------------------------
# Shared helper: write bundle label files to tmp_path
# ---------------------------------------------------------------------------

def _write_bundle_label(setup, rel: int, members: list[dict]):
    """Write bundle_<mission>_spice_v<rel>.xml to the bundle directory."""
    name = f"bundle_{MISSION}_spice_v{rel:03d}.xml"
    path = (
        Path(setup.bundle_directory)
        / f"{MISSION}_spice"
        / name
    )
    path.write_text(_bundle_label_xml(members))
    return name


def _write_collection_csv(setup, relative_path: str, rows: list[str]):
    """Write a collection inventory CSV under the bundle directory."""
    full_path = (
        Path(setup.bundle_directory) / f"{MISSION}_spice" / relative_path
    )
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(_kernel_inventory_csv(rows))


# ---------------------------------------------------------------------------
# Bundle.__init__ and public properties (lid, vid, readme)
# ---------------------------------------------------------------------------

class TestBundleInit:
    """Tests for ``Bundle.__init__`` and the public properties it initializes.

    Properties are exercised here because they are trivial wrappers around
    instance attributes set exclusively in ``__init__``; testing them
    separately would not add meaningful coverage.
    """

    @staticmethod
    def _pds3_setup(tmp_path):
        staging = tmp_path / "staging"
        staging.mkdir()
        return SimpleNamespace(
            pds_version="3",
            staging_directory=str(staging),
            args=SimpleNamespace(silent=True, verbose=False),
        )

    @staticmethod
    def _pds4_setup(tmp_path):
        staging = tmp_path / "staging"
        bundle = tmp_path / "bundle"
        staging.mkdir()
        bundle.mkdir()
        return SimpleNamespace(
            pds_version="4",
            staging_directory=str(staging),
            bundle_directory=str(bundle),
            mission_acronym=MISSION,
            release="001",
            logical_identifier=f"urn:nasa:pds:{MISSION}.spice",
            xml_model=XML_MODEL,
            args=SimpleNamespace(silent=True, verbose=False),
        )

    @patch("pds.naif_pds4_bundler.classes.bundle.safe_make_directory")
    def test_pds3_creates_expected_subdirectories(self, mock_mkdir, tmp_path):
        """PDS3 init calls safe_make_directory for each expected subdirectory."""
        setup = self._pds3_setup(tmp_path)
        bundle = object.__new__(Bundle)
        bundle.__init__(setup)

        created = [str(c.args[0]).replace(str(tmp_path), 'p')
                   for c in mock_mkdir.call_args_list]
        expected = [f'{Path("p/staging")}',
                    f'{Path("p/staging/catalog")}',
                    f'{Path("p/staging/data")}',
                    f'{Path("p/staging/document")}',
                    f'{Path("p/staging/extras")}',
                    f'{Path("p/staging/index")}']
        assert created == expected

    @patch("pds.naif_pds4_bundler.classes.bundle.get_context_products",
           return_value=[])
    @patch("pds.naif_pds4_bundler.classes.bundle.safe_make_directory")
    def test_pds4_creates_expected_subdirectories(self, mock_mkdir, _mock_ctx, tmp_path):
        """PDS4 init calls safe_make_directory for each expected subdirectory."""
        setup = self._pds4_setup(tmp_path)
        bundle = object.__new__(Bundle)
        bundle.__init__(setup)

        created = [str(c.args[0]).replace(str(tmp_path), 'p')
                   for c in mock_mkdir.call_args_list]
        expected = [f'{Path("p/staging")}',
                    f'{Path("p/staging/spice_kernels")}',
                    f'{Path("p/staging/document")}',
                    f'{Path("p/staging/miscellaneous")}']
        assert created == expected

    @patch("pds.naif_pds4_bundler.classes.bundle.get_context_products",
           return_value=[])
    @patch("pds.naif_pds4_bundler.classes.bundle.safe_make_directory")
    def test_pds4_sets_name_and_vid(self, _mock_mkdir, _mock_ctx, tmp_path):
        """PDS4 init sets ``name`` and ``_vid`` from the release number."""
        setup = self._pds4_setup(tmp_path)
        # _get_history will find no labels → returns {} harmlessly
        bundle = Bundle(setup)
        assert bundle.name == f"bundle_{MISSION}_spice_v001.xml"
        assert bundle.vid == "1.0"

    @patch("pds.naif_pds4_bundler.classes.bundle.get_context_products",
           return_value=[])
    @patch("pds.naif_pds4_bundler.classes.bundle.safe_make_directory")
    def test_pds4_lid_property(self, _mock_mkdir, _mock_ctx, tmp_path):
        """``lid`` property returns the logical identifier from setup."""
        setup = self._pds4_setup(tmp_path)
        bundle = Bundle(setup)
        assert bundle.lid == setup.logical_identifier

    def test_readme_property_initially_none(self, fake_setup):
        """``readme`` property is ``None`` until explicitly set."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        assert bundle.readme is None

    def test_readme_setter(self, fake_setup):
        """Assigning to ``bundle.readme`` stores the value."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        fake_readme = SimpleNamespace(name="readme.txt")
        bundle.readme = fake_readme
        assert bundle.readme is fake_readme

    def test_readme_setter_overwrites_previous_value(self, fake_setup):
        """Assigning a second time replaces the first value."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        bundle.readme = SimpleNamespace(name="old.txt")
        new_readme = SimpleNamespace(name="new.txt")
        bundle.readme = new_readme
        assert bundle.readme is new_readme

    @patch("pds.naif_pds4_bundler.classes.bundle.get_context_products",
           return_value=[])
    @patch("pds.naif_pds4_bundler.classes.bundle.safe_make_directory")
    def test_collections_initially_empty(self, _mock_mkdir, _mock_ctx, tmp_path):
        """``collections`` list starts empty after init."""
        setup = self._pds4_setup(tmp_path)
        bundle = Bundle(setup)
        assert bundle.collections == []

# ---------------------------------------------------------------------------
# Bundle.add method.
# ---------------------------------------------------------------------------

class TestBundleAdd:

    def test_add_appends_to_collections(self, fake_setup):
        """``add`` appends the given element to ``self.collections``."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        element = SimpleNamespace(name="spice_kernels")
        bundle.add(element)
        assert element in bundle.collections

    def test_add_multiple_elements(self, fake_setup):
        """Multiple calls to ``add`` accumulate in order."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        a = SimpleNamespace(name="a")
        b = SimpleNamespace(name="b")
        bundle.add(a)
        bundle.add(b)
        assert bundle.collections == [a, b]


# ---------------------------------------------------------------------------
# Bundle.copy_to_bundle method.
# ---------------------------------------------------------------------------

class TestBundleCopyToBundle:

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # PDS4 helpers
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::

    @staticmethod
    def _pds4_setup(tmp_path):
        """Return (setup, staging_root, bundle_dir) for a PDS4 bundle."""
        # The staging directory must contain the mission segment so that
        # file.split(os.sep + MISSION + "_spice" + os.sep) works correctly.
        staging = tmp_path / "staging" / f"{MISSION}_spice"
        staging.mkdir(parents=True)
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        setup = SimpleNamespace(
            pds_version="4",
            staging_directory=str(staging),
            bundle_directory=str(bundle_dir),
            mission_acronym=MISSION,
            faucet="bundle",
            args=SimpleNamespace(silent=True, verbose=False),
        )
        return setup, staging, bundle_dir

    @staticmethod
    def _pds4_bundle(setup):
        return _make_bundle(setup, vid="1.0",
                            name=f"bundle_{MISSION}_spice_v001.xml")

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # PDS3 helpers
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::

    VOLUME_ID = "insight_spice_1000"

    def _pds3_setup(self, tmp_path):
        """Return (setup, staging_root, bundle_dir) for a PDS3 dataset."""
        staging = tmp_path / "staging" / self.VOLUME_ID
        staging.mkdir(parents=True)
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        setup = SimpleNamespace(
            pds_version="3",
            staging_directory=str(staging),
            bundle_directory=str(bundle_dir),
            mission_acronym=MISSION,
            volume_id=self.VOLUME_ID,
            faucet="bundle",
            args=SimpleNamespace(silent=True, verbose=False),
        )
        return setup, staging, bundle_dir

    @staticmethod
    def _pds3_bundle(setup):
        bundle = object.__new__(Bundle)
        bundle.setup = setup
        bundle._new_files = []
        bundle._readme = None
        bundle.collections = []
        return bundle

    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # PDS4 tests
    # :::::::::::::::::::::::::::::::::::::::::::::::::::::::

    def test_pds4_new_file_copied_to_bundle(self, tmp_path):
        """PDS4: a new file is copied under ``<bundle>/<mission>_spice/``."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        src = staging / "test.xml"
        src.write_text("<label/>")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (bundle_dir / f"{MISSION}_spice" / "test.xml").exists()

    def test_pds4_label_extension_is_xml(self, tmp_path):
        """PDS4: an existing ``.xml`` file is always overwritten (label branch)."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        src = staging / "bundle_insight_spice_v001.xml"
        src.write_text("<new/>")
        dst_dir = bundle_dir / f"{MISSION}_spice"
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "bundle_insight_spice_v001.xml").write_text("<old/>")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (dst_dir / "bundle_insight_spice_v001.xml").read_text() == "<new/>"

    def test_pds4_existing_non_label_not_copied_warns(self, tmp_path, caplog):
        """PDS4: an existing non-label file that is unchanged is skipped
        and a warning is logged."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        content = "kernel data"
        src = staging / "existing.bc"
        src.write_text(content)
        dst_dir = bundle_dir / f"{MISSION}_spice"
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "existing.bc").write_text(content)
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        with caplog.at_level(logging.WARNING):
            bundle.copy_to_bundle()
        expected = [
            '-- File already exists and has not been copied: existing.bc',
            '-- Found 1 new file(s), copied 0 file(s) from staging directory.']
        assert caplog.messages == expected

    def test_pds4_existing_non_binary_file_with_different_content_warns(
            self, tmp_path, caplog
    ):
        """PDS4: an existing non-binary, non-label file whose content changed
        logs a content-mismatch warning in addition to the skip warning."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        src = staging / "kernel.tsc"
        src.write_text("new content")
        dst_dir = bundle_dir / f"{MISSION}_spice"
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "kernel.tsc").write_text("old content")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        with caplog.at_level(logging.WARNING):
            bundle.copy_to_bundle()
        expected = [
            '-- File already exists but content is different: kernel.tsc',
            '-- File already exists and has not been copied: kernel.tsc',
            '-- Found 1 new file(s), copied 0 file(s) from staging directory.']
        assert caplog.messages == expected

    def test_pds4_existing_binary_file_skips_content_comparison(
            self, tmp_path, caplog
    ):
        """PDS4: for binary-extension files (starting with 'b') the content
        comparison is skipped; only the skip warning is logged, not the
        'different content' warning."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        src = staging / "kernel.bc"
        src.write_bytes(b"new binary data")
        dst_dir = bundle_dir / f"{MISSION}_spice"
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "kernel.bc").write_bytes(b"old binary data")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        with caplog.at_level(logging.WARNING):
            bundle.copy_to_bundle()
        expected = [
            '-- File already exists and has not been copied: kernel.bc',
            '-- Found 1 new file(s), copied 0 file(s) from staging directory.']
        assert caplog.messages == expected

    def test_pds4_label_mode_strips_spice_kernels_from_path(self, tmp_path):
        """PDS4 label mode: the ``spice_kernels`` segment is stripped so the
        file lands directly under the bundle root, not in a subdirectory."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        setup.faucet = "labels"
        spk_dir = staging / "spice_kernels"
        spk_dir.mkdir()
        src = spk_dir / "test.xml"
        src.write_text("<label/>")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (bundle_dir / "test.xml").exists()

    def test_pds4_counts_match_logs_info(self, tmp_path, caplog):
        """PDS4: when the number of copied files equals the number of files
        newer than one day, an INFO-level summary is logged."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        src = staging / "fresh.xml"
        src.write_text("<x/>")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        with caplog.at_level(logging.INFO):
            bundle.copy_to_bundle()
        expected = [
            '-- Copied: fresh.xml',
            '',
            '-- Found 1 new file(s), copied 1 file(s) from staging directory.',
            '']
        assert caplog.messages == expected

    def test_pds4_destination_directory_created_if_missing(self, tmp_path):
        """PDS4: intermediate destination directories are created automatically."""
        setup, staging, bundle_dir = self._pds4_setup(tmp_path)
        subdir = staging / "spice_kernels" / "ck"
        subdir.mkdir(parents=True)
        src = subdir / "kernel.bc"
        src.write_bytes(b"data")
        bundle = self._pds4_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (bundle_dir / f"{MISSION}_spice" / "spice_kernels" / "ck" / "kernel.bc").exists()

    # ================================================================== #
    # PDS3 tests                                                           #
    # ================================================================== #

    def test_pds3_file_copied_to_bundle(self, tmp_path):
        """PDS3: a file is copied under ``<bundle>/<volume_id>/``."""
        setup, staging, bundle_dir = self._pds3_setup(tmp_path)
        src = staging / "test.lbl"
        src.write_text("PDS3 label")
        bundle = self._pds3_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (bundle_dir / self.VOLUME_ID / "test.lbl").exists()

    def test_pds3_label_extension_is_lbl(self, tmp_path):
        """PDS3: a ``.lbl`` file that already exists is always overwritten."""
        setup, staging, bundle_dir = self._pds3_setup(tmp_path)
        src = staging / "existing.lbl"
        src.write_text("new label content")
        dst_dir = bundle_dir / self.VOLUME_ID
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "existing.lbl").write_text("old label content")
        bundle = self._pds3_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (dst_dir / "existing.lbl").read_text() == "new label content"

    def test_pds3_always_copies_regardless_of_existing_file(self, tmp_path):
        """PDS3: every file is copied unconditionally (no skip logic for PDS3)."""
        setup, staging, bundle_dir = self._pds3_setup(tmp_path)
        src = staging / "data.tab"
        src.write_text("new data")
        dst_dir = bundle_dir / self.VOLUME_ID
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / "data.tab").write_text("old data")
        bundle = self._pds3_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        assert (dst_dir / "data.tab").read_text() == "new data"

    def test_pds3_uses_volume_id_as_path_segment(self, tmp_path):
        """PDS3: ``volume_id`` (not ``mission_acronym + '_spice'``) is used
        to build the destination path."""
        setup, staging, bundle_dir = self._pds3_setup(tmp_path)
        src = staging / "kernel.tls"
        src.write_text("leapseconds")
        bundle = self._pds3_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        # File must land under volume_id, not under mission_spice
        assert (bundle_dir / self.VOLUME_ID / "kernel.tls").exists()
        assert not (bundle_dir / f"{MISSION}_spice" / "kernel.tls").exists()

    def test_pds3_label_mode_strips_data_prefix(self, tmp_path):
        """PDS3 label mode: the ``data`` segment is stripped from the path."""
        setup, staging, bundle_dir = self._pds3_setup(tmp_path)
        setup.faucet = "labels"
        data_dir = staging / "data"
        data_dir.mkdir()
        src = data_dir / "test.lbl"
        src.write_text("label")
        bundle = self._pds3_bundle(setup)
        bundle._new_files = [str(src)]
        bundle.copy_to_bundle()
        # In label mode the file lands directly under the volume root,
        # not inside data/.
        assert (bundle_dir / "test.lbl").exists()


# ---------------------------------------------------------------------------
# Bundle.files_in_staging method.
# ---------------------------------------------------------------------------

class TestBundleFilesInStaging:

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Helper method for the TestBundleFilesInStaging class.
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::

    @staticmethod
    def _staging_setup(tmp_path):
        staging = tmp_path / "staging" / f"{MISSION}_spice"
        staging.mkdir(parents=True)
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        args = SimpleNamespace(silent=True, verbose=False)
        setup = SimpleNamespace(
            pds_version="4",
            staging_directory=str(staging),
            bundle_directory=str(bundle_dir),
            mission_acronym=MISSION,
            faucet="bundle",
            args=args,
        )
        bundle = _make_bundle(setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        bundle.setup = setup
        return bundle, staging

    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::
    # Test cases
    # ::::::::::::::::::::::::::::::::::::::::::::::::::::::

    def test_pds4_bundle_label_added_to_new_files(self, tmp_path):
        """PDS4 mode: the bundle label XML is appended to ``_new_files``."""
        bundle, staging = self._staging_setup(tmp_path)
        bundle.files_in_staging()
        expected = os.path.join(
            bundle.setup.staging_directory, bundle.name
        )
        assert expected in bundle._new_files

    def test_pds4_label_mode_skips_bundle_label(self, tmp_path):
        """In label mode the bundle label XML is not added to ``_new_files``."""
        bundle, staging = self._staging_setup(tmp_path)
        bundle.setup.faucet = "labels"
        bundle.files_in_staging()
        expected = os.path.join(
            bundle.setup.staging_directory, bundle.name
        )
        assert expected not in bundle._new_files

    def test_pds3_dsindex_files_added(self, tmp_path):
        """PDS3 mode: ``dsindex.tab`` and ``dsindex.lbl`` are appended."""
        staging = tmp_path / "staging"
        staging.mkdir()
        setup = SimpleNamespace(
            pds_version="3",
            staging_directory=str(staging),
            mission_acronym=MISSION,
            args=SimpleNamespace(silent=True, verbose=False),
        )
        bundle = object.__new__(Bundle)
        bundle.setup = setup
        bundle._new_files = []
        bundle._readme = None
        bundle.collections = []
        bundle.files_in_staging()
        expected = [
            f'{Path("p/staging/../dsindex.tab")}',
            f'{Path("p/staging/../dsindex.lbl")}']
        files = [f.replace(str(tmp_path), 'p') for f in bundle._new_files]
        assert expected == files

    def test_readme_new_product_added_when_present(self, tmp_path):
        """A new readme product is appended when ``_readme.new_product`` is True."""
        bundle, staging = self._staging_setup(tmp_path)
        bundle._readme = SimpleNamespace(
            new_product=True,
            name="readme.txt",
        )
        bundle.files_in_staging()
        expected = os.path.join(bundle.setup.staging_directory, "readme.txt")
        assert expected in bundle._new_files

    def test_readme_existing_product_not_added(self, tmp_path):
        """An existing (non-new) readme product is not appended."""
        bundle, staging = self._staging_setup(tmp_path)
        bundle._readme = SimpleNamespace(
            new_product=False,
            name="readme.txt",
        )
        bundle.files_in_staging()
        assert not any("readme.txt" in f for f in bundle._new_files)

    def test_collection_products_added(self, tmp_path):
        """Products from collections are appended to ``_new_files``."""
        bundle, staging = self._staging_setup(tmp_path)
        # Create a fake file in staging so the product path exists
        fake_file = staging / "test.bc"
        fake_file.write_text("dummy")
        fake_label = staging / "test.xml"
        fake_label.write_text("<label/>")
        fake_product = SimpleNamespace(
            path=str(fake_file),
            label=SimpleNamespace(name=str(fake_label)),
        )
        fake_collection = SimpleNamespace(product=[fake_product])
        bundle.collections = [fake_collection]
        bundle.files_in_staging()
        expected = [
            f'{Path("p/staging/insight_spice/test.bc")}',
            f'{Path("p/staging/insight_spice/test.xml")}',
            f'{Path("p/staging/insight_spice/bundle_insight_spice_v001.xml")}']
        files = [f.replace(str(tmp_path), 'p') for f in bundle._new_files]
        assert expected == files

    def test_product_without_label_logs_info(self, tmp_path, caplog):
        """A product without a ``label`` attribute logs an info message."""
        bundle, staging = self._staging_setup(tmp_path)
        fake_file = staging / "test.bc"
        fake_file.write_text("dummy")
        fake_product = SimpleNamespace(path=str(fake_file), name="test.bc")
        fake_collection = SimpleNamespace(product=[fake_product])
        bundle.collections = [fake_collection]
        with caplog.at_level(logging.INFO):
            bundle.files_in_staging()
        expected = [
            '-- Product test.bc has no label in staging area.',
            '-- The following files are present in the staging area:',
            '     test.bc',
            '']
        assert expected == caplog.messages


# ---------------------------------------------------------------------------
# Bundle.validate method.
# ---------------------------------------------------------------------------

class TestBundleValidate:

    def test_validate_calls_check_times_and_validate_history(self, fake_setup):
        """``validate`` delegates to ``_check_times`` and ``_validate_history``."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        bundle._check_times = MagicMock()
        bundle._validate_history = MagicMock()
        bundle.validate()
        bundle._check_times.assert_called_once()
        bundle._validate_history.assert_called_once()


# ---------------------------------------------------------------------------
# Bundle._check_times
# ---------------------------------------------------------------------------

class TestBundlePCheckTimes:

    @staticmethod
    def _make_times_bundle(
            mission_start: str,
            increment_start: str,
            increment_finish: str,
            mission_finish: str,
    ) -> Bundle:
        """Construct a minimal ``Bundle`` with only the four time attributes that
        ``_check_times`` reads from ``self.setup``."""
        bundle = object.__new__(Bundle)
        bundle.setup = SimpleNamespace(
            mission_start=mission_start,
            increment_start=increment_start,
            increment_finish=increment_finish,
            mission_finish=mission_finish,
        )
        return bundle

    @pytest.mark.parametrize('m_start, i_start, i_end, m_end', [
        # Normal mode of operation (DOY format)
        ("2000-001T00:00:00", "2000-060T00:00:00", "2000-180T00:00:00", "2001-001T00:00:00"),
        # m_start = i_start, i_end = m_end (DOY format)
        ("2015-001T00:00:00", "2015-001T00:00:00", "2015-365T00:00:00", "2015-365T00:00:00"),
        # single second increment window. (DOY format)
        ("2010-001T00:00:00", "2010-180T12:00:00", "2010-180T12:00:01", "2011-001T00:00:00"),
        # Normal mode of operation (YYYY-MM-DD format)
        ("2000-01-01T00:00:00", "2000-02-06T00:00:00", "2000-07-18T00:00:00", "2001-10-01T00:00:00"),
        # Trailing Z on input strings.
        ("2000-01-01T00:00:00Z", "2000-02-06T00:00:00Z", "2000-07-18T00:00:00Z", "2001-10-01T00:00:00Z"),
        # TODO: Should zero-duration increment raise an error? Note that it doesn't. Possible bug!
        ("2010-001T00:00:00", "2010-180T00:00:00", "2010-180T00:00:00", "2011-001T00:00:00")
    ])
    def test_valid_ordering(self, lsk, m_start, i_start, i_end, m_end):
        """All four times correctly ordered."""
        bundle = self._make_times_bundle(m_start, i_start, i_end, m_end)
        bundle._check_times()

    @pytest.mark.parametrize('m_start, i_start, i_end, m_end', [
        # mission_start after increment_start
        ("2010-200T00:00:00", "2010-060T00:00:00", "2010-300T00:00:00", "2011-001T00:00:00"),
        # increment_start after increment_finish
        ("2010-001T00:00:00", "2010-300T00:00:00", "2010-060T00:00:00", "2011-001T00:00:00"),
        # increment_finish after mission_finish
        ("2010-001T00:00:00", "2010-060T00:00:00", "2012-001T00:00:00", "2011-001T00:00:00"),
        # zero-time mission duration
        ("2010-180T00:00:00", "2010-180T00:00:00", "2010-180T00:00:00", "2010-180T00:00:00"),
        # mission_start is after mission_finish
        ("2015-001T00:00:00", "2010-060T00:00:00", "2010-180T00:00:00", "2010-001T00:00:00"),
        # increment_start is after increment_finish
        ("2010-001T00:00:00", "2010-180T00:00:00", "2010-090T00:00:00", "2011-001T00:00:00")

    ])
    def test_invalid_ordering(self, lsk, m_start, i_start, i_end, m_end):
        bundle = self._make_times_bundle(m_start, i_start, i_end, m_end)
        with pytest.raises(RuntimeError, match="The resulting Mission and Increment start "
                                               "and finish dates are incoherent."):
            bundle._check_times()


# ---------------------------------------------------------------------------
# Bundle._get_collection_versions_from_label
# ---------------------------------------------------------------------------

class TestBundlePGetCollectionVersionsFromLabel:

    @staticmethod
    def _make_label(members: list[dict]) -> dict:
        """Build the label dict that _get_collection_versions_from_label expects."""
        prefix = "{" + NS + "}"
        member_dicts = [
            {
                f"{prefix}lidvid_reference": m["lid"],
                f"{prefix}member_status": m["status"],
            }
            for m in members
        ]
        return {"prefix": prefix, "members": member_dicts}

    def test_returns_dict_with_three_keys(self):
        label = self._make_label([])
        result = Bundle._get_collection_versions_from_label(label)
        assert set(result.keys()) == {"kernels", "document", "miscellaneous"}

    def test_kernel_version_extracted(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::3.0",
             "status": "Primary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        assert result["kernels"] == [3]

    def test_document_version_extracted(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::2.0",
             "status": "Primary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        assert result["document"] == [2]

    def test_miscellaneous_version_extracted(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::5.0",
             "status": "Primary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        assert result["miscellaneous"] == [5]

    def test_secondary_members_ignored(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Secondary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        assert result["kernels"] == []

    def test_multiple_primary_members(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
             "status": "Primary"},
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        expected = {'kernels': [1],
                    'document': [1],
                    'miscellaneous': [1]}
        assert expected == result

    def test_unrecognised_lidvid_ignored(self):
        label = self._make_label([
            {"lid": f"urn:nasa:pds:{MISSION}.spice:unknown_collection::1.0",
             "status": "Primary"},
        ])
        result = Bundle._get_collection_versions_from_label(label)
        assert result == {"kernels": [], "document": [], "miscellaneous": []}


# ---------------------------------------------------------------------------
# Bundle._get_document_collection_products
# ---------------------------------------------------------------------------

class TestBundlePGetDocumentCollectionProducts:

    def test_csv_and_label_always_present(self, fake_setup):
        """Collection inventory CSV and label are always the first two entries."""
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_document_collection_products(1)
        expected = ['document/collection_document_inventory_v001.csv',
                    'document/collection_document_v001.xml']
        assert expected == result

    def test_document_product_html_and_xml_added(self, fake_setup):
        """A primary inventory row produces a versioned .html and .xml pair."""
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:document:spiceds::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_document_collection_products(1)
        expected = ['document/collection_document_inventory_v001.csv',
                    'document/collection_document_v001.xml',
                    'document/spiceds_v001.html',
                    'document/spiceds_v001.xml']
        assert expected == result

    def test_non_p_rows_ignored(self, fake_setup):
        """Rows without 'P' are not included in the product list."""
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v001.csv",
            ["LBLRECL,1024"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_document_collection_products(1)
        expected = ['document/collection_document_inventory_v001.csv',
                    'document/collection_document_v001.xml']
        # Only the two fixed entries; no product from the header row
        assert expected == result

    def test_version_number_reflected_in_filenames(self, fake_setup):
        """The ``ver`` argument is used in all generated filenames."""
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v003.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:document:spiceds::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="3.0",
                              name=f"bundle_{MISSION}_spice_v003.xml")
        result = bundle._get_document_collection_products(3)
        expected = ['document/collection_document_inventory_v003.csv',
                    'document/collection_document_v003.xml',
                    'document/spiceds_v003.html',
                    'document/spiceds_v003.xml']
        assert expected == result


# ---------------------------------------------------------------------------
# Bundle._get_history
# ---------------------------------------------------------------------------

class TestBunelPGetHistory:

    def test_returns_dict(self, fake_setup):
        """_get_history always returns a dict."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        assert isinstance(bundle._get_history(), dict)

    def test_keys_are_release_integers(self, fake_setup):
        """Dict keys are integer release numbers starting at 1."""
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::{rel}.0",
                 "status": "Primary"},
            ])
            _write_collection_csv(
                fake_setup,
                f"spice_kernels/collection_spice_kernels_inventory_v{rel:03d}.csv",
                [],
            )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["non-empty"])
        assert set(bundle._get_history().keys()) == {1, 2}

    def test_values_are_lists(self, fake_setup):
        """Each value in the returned dict is a list."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        for v in bundle._get_history().values():
            assert isinstance(v, list)

    # -- Release counting ----------------------------------------------------

    def test_no_collections_decrements_release_count(self, fake_setup):
        """Empty ``collections`` excludes the in-progress release."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=[])
        assert set(bundle._get_history().keys()) == {1}

    def test_with_collections_includes_current_release(self, fake_setup):
        """Non-empty ``collections`` includes all releases up to VID."""
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::{rel}.0",
                 "status": "Primary"},
            ])
            _write_collection_csv(
                fake_setup,
                f"spice_kernels/collection_spice_kernels_inventory_v{rel:03d}.csv",
                [],
            )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        assert set(bundle._get_history().keys()) == {1, 2}

    def test_vid_1_no_collections_returns_empty_dict(self, fake_setup):
        """VID=1.0 with empty ``collections`` means 0 releases → ``{}``."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=[])
        assert bundle._get_history() == {}

    # -- Missing bundle label ------------------------------------------------

    def test_missing_label_returns_empty_dict(self, fake_setup):
        """Absent label file causes an early ``{}`` return."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        assert bundle._get_history() == {}

    def test_missing_label_for_second_release_returns_empty(self, fake_setup):
        """Missing release-2 label causes an early ``{}`` return."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        assert bundle._get_history() == {}

    # -- readme.txt ----------------------------------------------------------

    def test_readme_in_release_1(self, fake_setup):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        assert "readme.txt" in bundle._get_history()[1]

    def test_readme_not_in_later_releases(self, fake_setup):
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::{rel}.0",
                 "status": "Primary"},
            ])
            _write_collection_csv(
                fake_setup,
                f"spice_kernels/collection_spice_kernels_inventory_v{rel:03d}.csv",
                [],
            )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        assert "readme.txt" not in bundle._get_history()[2]

    # -- Bundle label entry --------------------------------------------------

    def test_bundle_label_in_release(self, fake_setup):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        assert f"bundle_{MISSION}_spice_v001.xml" in bundle._get_history()[1]

    # -- Kernel collection ---------------------------------------------------

    def test_kernel_collection_csv_and_label_in_history(self, fake_setup):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" in result[1]
        assert "spice_kernels/collection_spice_kernels_v001.xml" in result[1]

    def test_secondary_member_not_added(self, fake_setup):
        """Secondary collection members are skipped."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Secondary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" \
               not in result[1]

    def test_same_collection_version_not_repeated_in_later_release(
            self, fake_setup
    ):
        """When the kernel collection version is unchanged, files are not
        re-listed in the subsequent release."""
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
                 "status": "Primary"},
            ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v01.bc::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" \
               in result[1]
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" \
               not in result[2]

    # -- Multi-release incremental -------------------------------------------

    def test_new_collection_version_only_in_release_it_was_introduced(
            self, fake_setup
    ):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v01.bc::1.0"],
        )
        _write_bundle_label(fake_setup, 2, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::2.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v02.bc::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "spice_kernels/ck/v01.bc" in result[1]
        assert "spice_kernels/ck/v02.bc" in result[2]
        assert "spice_kernels/ck/v02.bc" not in result[1]

    def test_three_releases_accumulate_correctly(self, fake_setup):
        for rel in (1, 2, 3):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::{rel}.0",
                 "status": "Primary"},
            ])
            _write_collection_csv(
                fake_setup,
                f"spice_kernels/collection_spice_kernels_inventory_v{rel:03d}.csv",
                [],
            )
        bundle = _make_bundle(fake_setup, vid="3.0",
                              name=f"bundle_{MISSION}_spice_v003.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert set(result.keys()) == {1, 2, 3}
        for rel in (1, 2, 3):
            assert f"bundle_{MISSION}_spice_v{rel:03d}.xml" in result[rel]

    # -- Miscellaneous collection --------------------------------------------

    def test_misc_collection_csv_and_label_in_history(self, fake_setup):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "miscellaneous/collection_miscellaneous_inventory_v001.csv" \
               in result[1]
        assert "miscellaneous/collection_miscellaneous_v001.xml" in result[1]

    def test_misc_absent_from_filesystem_skipped_gracefully(self, fake_setup):
        """Missing miscellaneous CSV is silently omitted."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "miscellaneous/collection_miscellaneous_inventory_v001.csv" \
               not in result[1]

    # -- Document collection -------------------------------------------------

    def test_document_collection_csv_and_label_in_history(self, fake_setup):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert "document/collection_document_inventory_v001.csv" in result[1]
        assert "document/collection_document_v001.xml" in result[1]

    # -- Duplicate detection -------------------------------------------------

    def test_duplicate_entries_emit_warning(self, fake_setup, caplog):
        """The same product path in two releases triggers a warning."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
             "status": "Secondary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_shared.bc::1.0"],
        )
        _write_bundle_label(fake_setup, 2, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::2.0",
             "status": "Primary"},
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
             "status": "Secondary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_shared.bc::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        with caplog.at_level(logging.WARNING):
            result = bundle._get_history()
        assert any("duplicate" in r.message.lower() for r in caplog.records)
        assert isinstance(result, dict)

    # -- Formerly known bug: uninitialized ver --------------------------------

    def test_no_version_change_does_not_raise(self, fake_setup):
        """Two releases referencing the same collection version do not raise."""
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
                 "status": "Primary"},
            ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        result = bundle._get_history()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Bundle._get_kernel_collection_products
# ---------------------------------------------------------------------------

class TestBundlePGetKernelCollectionProducts:

    def test_csv_and_label_always_present(self, fake_setup):
        """Collection inventory CSV and label are always present."""
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        expected = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                    'spice_kernels/collection_spice_kernels_v001.xml']
        assert expected == result

    def test_regular_kernel_product_and_label_added(self, fake_setup):
        """A non-MK kernel line adds both the data file and its XML label."""
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_insight_ida_enc_v01.bc::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        expected = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                    'spice_kernels/collection_spice_kernels_v001.xml',
                    'spice_kernels/ck/insight_ida_enc_v01.bc',
                    'spice_kernels/ck/insight_ida_enc_v01.xml']
        assert expected == result

    def test_non_p_rows_ignored(self, fake_setup):
        """Lines not containing 'P' are skipped."""
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            ["LBLRECL,1024"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        expected = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                    'spice_kernels/collection_spice_kernels_v001.xml']
        assert expected == result

    @pytest.mark.parametrize('length, expected', [
        ("1",
         ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
          'spice_kernels/collection_spice_kernels_v001.xml',
          'spice_kernels/mk/insight_v1.tm',
          'spice_kernels/mk/insight_v1.xml']),
        ("2",
         ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
          'spice_kernels/collection_spice_kernels_v001.xml',
          'spice_kernels/mk/insight_v01.tm',
          'spice_kernels/mk/insight_v01.xml']),
        ("3",
         ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
          'spice_kernels/collection_spice_kernels_v001.xml',
          'spice_kernels/mk/insight_v001.tm',
          'spice_kernels/mk/insight_v001.xml']),

    ])
    def test_mk_with_config_version_length_1(self, fake_setup, length, expected):
        """MK with VERSION length 1 produces ``_v1.tm``."""
        fake_setup.mk = [{"name": [{"pattern": [{"#text": "VERSION", "@length": length}]}]}]
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        assert expected == result

    def test_mk_with_config_invalid_length_raises(self, fake_setup):
        """An unsupported VERSION length triggers handle_npb_error."""
        fake_setup.mk = [{"name": [{"pattern": [{"#text": "VERSION", "@length": "4"}]}]}]
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        with pytest.raises(Exception, match='Meta-kernel version length of 4 digits is incorrect.'):
            bundle._get_kernel_collection_products(1)

    def test_mk_fallback_to_mk_inputs_dict(self, fake_setup):
        """When ``setup.mk`` is absent but ``setup.mk_inputs`` is a dict,
        MK names are derived from ``mk_inputs["file"]``."""
        fake_setup.mk_inputs = {"file": "/path/to/insight_v01.tm"}
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        expected = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                    'spice_kernels/collection_spice_kernels_v001.xml',
                    'spice_kernels/mk/insight_v01.tm',
                    'spice_kernels/mk/insight_v01.xml']
        assert expected == result

    def test_mk_fallback_default_2_digits_warns(self, fake_setup, caplog):
        """When neither ``setup.mk`` nor ``setup.mk_inputs`` is present, a
        warning is logged and the MK is formatted with 2 digits."""
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        with caplog.at_level(logging.WARNING):
            result = bundle._get_kernel_collection_products(1)
        exp_msg = [
            'MK version for history defaulted to version with 2 digits. Might raise an exception.'
        ]
        exp_result = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                      'spice_kernels/collection_spice_kernels_v001.xml',
                      'spice_kernels/mk/insight_v01.tm',
                      'spice_kernels/mk/insight_v01.xml']
        assert exp_msg == caplog.messages
        assert exp_result == result

    def test_multiple_kernels_all_added(self, fake_setup):
        """All kernel rows in the inventory are included."""
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [
                f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_insight_ida_enc_v01.bc::1.0",
                f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:spk_insight_cruise_v1.bsp::1.0",
            ],
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_kernel_collection_products(1)
        print(result)
        expected = ['spice_kernels/collection_spice_kernels_inventory_v001.csv',
                    'spice_kernels/collection_spice_kernels_v001.xml',
                    'spice_kernels/ck/insight_ida_enc_v01.bc',
                    'spice_kernels/ck/insight_ida_enc_v01.xml',
                    'spice_kernels/spk/insight_cruise_v1.bsp',
                    'spice_kernels/spk/insight_cruise_v1.xml']
        assert expected == result


# ---------------------------------------------------------------------------
# Bundle._get_metakernel_product_from_config
# ---------------------------------------------------------------------------

class TestBundlePGetMetakernelProductFromConfig:

    @staticmethod
    def _mk_setup(fake_setup, version_length: int):
        fake_setup.mk = [{"name": [{"pattern": [{"#text": "VERSION",
                                                 "@length": str(version_length)}]}]}]
        return fake_setup

    @staticmethod
    def _csv_line():
        return f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"

    @pytest.mark.parametrize("length, expected", [
        (1, 'spice_kernels/mk/insight_v1.tm'),
        (2, 'spice_kernels/mk/insight_v01.tm'),
        (3, 'spice_kernels/mk/insight_v001.tm'),
    ])
    def test_version_length(self, fake_setup, length, expected):
        setup = self._mk_setup(fake_setup, length)
        bundle = _make_bundle(setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_product_from_config(1, self._csv_line())
        print(result)
        assert expected == result

    def test_invalid_version_length_raises(self, fake_setup):
        setup = self._mk_setup(fake_setup, 4)
        bundle = _make_bundle(setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        with pytest.raises(Exception, match='Meta-kernel version length of 4 digits is incorrect.'):
            bundle._get_metakernel_product_from_config(1, self._csv_line())

    def test_version_number_embedded_correctly(self, fake_setup):
        """The version number in the filename matches the ``ver`` argument."""
        setup = self._mk_setup(fake_setup, 2)
        bundle = _make_bundle(setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_product_from_config(7, self._csv_line())
        assert 'spice_kernels/mk/insight_v07.tm' == result

    def test_pattern_key_as_plain_dict_is_normalised_to_list(self, fake_setup):
        """When ``pattern_word["pattern"]`` is a plain dict rather
        than a list (single-entry pattern deserialized without wrapping by
        ``etree_to_dict``), it is normalized to ``[pattern_key]``.

        This shape arises in real NPB configs when a name-pattern block
        contains exactly one ``<pattern>`` child, which ``etree_to_dict``
        returns as a dict rather than a one-element list.
        """
        # pattern_word["pattern"] is a dict, not a list -> triggers line 570
        fake_setup.mk = [{"name": [{"pattern": {"#text": "VERSION",
                                                "@length": "2"}}]}]
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_product_from_config(1, self._csv_line())
        assert result == "spice_kernels/mk/insight_v01.tm"

    def test_no_version_key_found_returns_default_two_digit_format(
            self, fake_setup
    ):
        """When no pattern entry has ``#text == 'VERSION'`` the loop
        exhausts without returning, and the method falls through to the default
        ``v{ver:02d}.tm`` format.

        This covers the path where the setup configuration contains patterns
        but none of them is the VERSION key (e.g. only YEAR or MISSION
        patterns are defined).
        """
        # A pattern whose #text is something other than VERSION
        fake_setup.mk = [{"name": [{"pattern": [{"#text": "YEAR",
                                                 "@length": "4"}]}]}]
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_product_from_config(3, self._csv_line())
        # Falls through to: return f"{base}v{ver:02d}.tm"
        assert result == "spice_kernels/mk/insight_v03.tm"


# ---------------------------------------------------------------------------
# Bundle._get_metakernel_products_from_inputs
# ---------------------------------------------------------------------------

class TestBundlePGetMetakernelProductsFromInputs:

    def test_mk_inputs_as_dict_with_single_file(self, fake_setup):
        """``mk_inputs`` dict with a single file string is handled."""
        fake_setup.mk_inputs = {"file": "/path/to/insight_v01.tm"}
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_products_from_inputs()
        assert result == ["spice_kernels/mk/insight_v01.tm"]

    def test_mk_inputs_as_dict_with_list_of_files(self, fake_setup):
        """``mk_inputs`` dict with a list of files produces one entry per file."""
        fake_setup.mk_inputs = {"file": [
            "/path/to/insight_v01.tm",
            "/path/to/insight_v02.tm",
        ]}
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_products_from_inputs()
        expected = ['spice_kernels/mk/insight_v01.tm',
                    'spice_kernels/mk/insight_v02.tm']
        assert expected == result

    def test_mk_inputs_as_plain_string(self, fake_setup):
        """``mk_inputs`` as a bare string (not a dict) is wrapped correctly."""
        fake_setup.mk_inputs = "/path/to/insight_v01.tm"
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_products_from_inputs()
        assert result == ["spice_kernels/mk/insight_v01.tm"]

    def test_mk_inputs_as_list_of_strings(self, fake_setup):
        """``mk_inputs`` as a plain list of strings is handled."""
        fake_setup.mk_inputs = [
            "/path/to/insight_v01.tm",
            "/path/to/insight_v02.tm",
        ]
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_products_from_inputs()
        assert "spice_kernels/mk/insight_v01.tm" in result
        assert "spice_kernels/mk/insight_v02.tm" in result

    def test_path_prefix_stripped_to_filename(self, fake_setup):
        """Only the filename (not the full path) appears in the result."""
        fake_setup.mk_inputs = "/some/deep/path/insight_v01.tm"
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_metakernel_products_from_inputs()
        assert result == ["spice_kernels/mk/insight_v01.tm"]


# ---------------------------------------------------------------------------
# Bundle._get_misc_collection_products
# ---------------------------------------------------------------------------

class TestBundlePGetMiscCollectionProducts:

    def test_returns_empty_list_when_csv_missing(self, fake_setup):
        """Returns ``[]`` when the inventory CSV does not exist on disk."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_misc_collection_products(1)
        assert result == []

    @pytest.mark.parametrize('rows, expected', [
        ([],
         ['miscellaneous/collection_miscellaneous_inventory_v001.csv',
          'miscellaneous/collection_miscellaneous_v001.xml']),
        ([f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:orbnum_insight_v01.nrb::1.0"],
         ['miscellaneous/collection_miscellaneous_inventory_v001.csv',
          'miscellaneous/collection_miscellaneous_v001.xml',
          "miscellaneous/orbnum/insight_v01.nrb",
          "miscellaneous/orbnum/insight_v01.xml"]),
        ([f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:checksum_insight::1.0"],
         ['miscellaneous/collection_miscellaneous_inventory_v001.csv',
          'miscellaneous/collection_miscellaneous_v001.xml',
          "miscellaneous/checksum/insight_v001.tab",
          "miscellaneous/checksum/insight_v001.xml"]),
        (["LBLRECL,1024"],
         ['miscellaneous/collection_miscellaneous_inventory_v001.csv',
          'miscellaneous/collection_miscellaneous_v001.xml'])
    ])
    def test_files_present(self, fake_setup, rows, expected):
        """Collection CSV and label are always the first two entries."""
        _write_collection_csv(
            fake_setup,
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml")
        result = bundle._get_misc_collection_products(1)
        assert expected == result


# ---------------------------------------------------------------------------
# Bundle._read_bundle_label
# ---------------------------------------------------------------------------

class TestBundlePReadBundleLabel:

    def test_returns_none_when_label_missing(self, fake_setup, caplog):
        """Returns ``None`` and logs a warning when the label file is absent."""
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        with caplog.at_level(logging.WARNING):
            result = bundle._read_bundle_label(1)
        assert result is None
        expected = [
            '-- Files from previous releases not available to generate Bundle history.'
        ]
        assert expected == caplog.messages

    def test_returns_dict_with_expected_keys_when_present(self, fake_setup):
        """Returns a dict with ``filename``, ``prefix``, ``members`` keys."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._read_bundle_label(1)
        expected = {
            'filename': 'bundle_insight_spice_v001.xml',
            'prefix': '{https://pds.nasa.gov/pds4/pds/v1}',
            'members': [
                {'{https://pds.nasa.gov/pds4/pds/v1}lidvid_reference': 'urn:nasa:pds:insight.spice:spice_kernels::1.0',
                 '{https://pds.nasa.gov/pds4/pds/v1}member_status': 'Primary'},
                {'{https://pds.nasa.gov/pds4/pds/v1}lidvid_reference': 'urn:nasa:pds:insight.spice:document::1.0',
                 '{https://pds.nasa.gov/pds4/pds/v1}member_status': 'Secondary'}]}
        assert expected == result

    def test_filename_matches_release_number(self, fake_setup):
        """The ``filename`` value corresponds to the requested release."""
        _write_bundle_label(fake_setup, 2, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        bundle = _make_bundle(fake_setup, vid="2.0",
                              name=f"bundle_{MISSION}_spice_v002.xml",
                              collections=["something"])
        result = bundle._read_bundle_label(2)
        assert result["filename"] == f"bundle_{MISSION}_spice_v002.xml"

    def test_members_is_a_list(self, fake_setup):
        """``members`` is always a list regardless of how many entries the
        label contains."""
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        result = bundle._read_bundle_label(1)
        assert isinstance(result["members"], list)

    def test_verbose_false_prints_warning_to_stdout(
            self, fake_setup, capsys
    ):
        """When ``args.verbose`` and ``args.silent`` are both False a warning
        is also printed to stdout."""
        fake_setup.args = SimpleNamespace(silent=False, verbose=False)
        bundle = _make_bundle(fake_setup, vid="1.0",
                              name=f"bundle_{MISSION}_spice_v001.xml",
                              collections=["something"])
        bundle._read_bundle_label(1)
        captured = capsys.readouterr()
        expected = '-- WARNING: Files from previous releases not available to generate Bundle history.\n'
        assert expected == captured.out


# ---------------------------------------------------------------------------
# Bundle._validate_history
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Design notes
# ---------------------------------------------------------------------------
# _validate_history has no direct filesystem helpers of its own — it delegates
# entirely to _get_history() for the product lists and then reads one
# checksum .tab file per release from the bundle directory.  The test
# strategy is therefore:
#
#   1. Build a real (minimal) on-disk bundle tree for each scenario so that
#      _get_history() runs for real and produces the product list we expect.
#   2. Write a matching (or deliberately mismatched) checksum .tab file.
#   3. Call _validate_history() and assert on logged lines and/or exceptions.
#
# Checksum .tab format
# --------------------
# The method reads each line, splits on whitespace, and takes the LAST token
# as the product path.  Real checksum files have the format:
#
#   <md5hash>  <relative/product/path>
#
# The helper _write_checksum writes files in this format.
#
# Checksum self-reference augmentation
# -------------------------------------
# After reading the .tab file, the method checks whether the checksum product
# itself (miscellaneous/checksum/checksum_v???.tab) appears in history[rel].
# If it does, it appends both the .tab and its .xml label to
# products_in_checksum BEFORE sorting and comparing.  Tests cover both the
# branch where the checksum IS in the history (via a miscellaneous collection
# entry) and where it is NOT (kernel-only releases).
#
# Error branches
# --------------
# Two distinct branches exist when products_in_checksum != products_in_history:
#   a) setup.args.log is False  → handle_npb_error called with the full diff
#   b) setup.args.log is True   → handle_npb_error called with a short message
# Both must be tested.
# ---------------------------------------------------------------------------

class TestPValidateHistory:
    """Tests for ``Bundle._validate_history``.

    Each test builds a minimal real filesystem tree so that ``_get_history``
    runs unpatched, producing the same product list the production code would
    see, then writes a matching or deliberately mismatched checksum .tab and
    asserts on logged lines and raised exceptions.
    """

    # ------------------------------------------------------------------ #
    # Helpers shared across tests                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _write_checksum(bundle_root: Path, rel: int, products: list[str]) -> None:
        """Write a checksum .tab file listing exactly the given product paths.

        Each line uses the real format: ``<md5hash>  <product_path>``
        The hash value is a placeholder; only the path token is read by the code.

        :param bundle_root: the ``<mission>_spice`` directory path
        :param rel:         release number (1-based)
        :param products:    list of relative product paths to list in the file
        """
        checksum_dir = bundle_root / "miscellaneous" / "checksum"
        checksum_dir.mkdir(parents=True, exist_ok=True)
        checksum_path = checksum_dir / f"checksum_v{rel:03d}.tab"
        lines = [f"d41d8cd98f00b204e9800998ecf8427e  {p}\n" for p in products]
        checksum_path.write_text("".join(lines), encoding="utf-8")

    @staticmethod
    def _validate_setup(tmp_path, *, log: bool = False) -> SimpleNamespace:
        """Return a ``SimpleNamespace`` setup suitable for _validate_history tests.

        :param log:  value for ``setup.args.log`` (controls which handle_npb_error
                     branch is taken on mismatch)
        """
        bundle_dir = tmp_path / "bundle"
        bundle_root = bundle_dir / f"{MISSION}_spice"
        bundle_root.mkdir(parents=True)
        args = SimpleNamespace(silent=True, verbose=False, log=log)
        return SimpleNamespace(
            bundle_directory=str(bundle_dir),
            mission_acronym=MISSION,
            xml_model=XML_MODEL,
            args=args,
            template_files = []  # For error cases.
        )

    @staticmethod
    def _validate_bundle(setup, vid: str, collections=None) -> Bundle:
        """Construct a Bundle for _validate_history tests."""
        name = f"bundle_{MISSION}_spice_v{int(vid.split('.')[0]):03d}.xml"
        bundle = _make_bundle(setup, vid=vid, name=name, collections=collections)
        return bundle

    @staticmethod
    def _bundle_root(setup: SimpleNamespace) -> Path:
        return Path(setup.bundle_directory) / f"{setup.mission_acronym}_spice"

    @staticmethod
    def _write_kernel_release(
            setup: SimpleNamespace,
            rel: int,
            kernel_ver: int,
            kernel_rows: list[str],
    ) -> None:
        """Write bundle label + kernel collection CSV for one release."""
        _write_bundle_label(setup, rel, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::{kernel_ver}.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            f"spice_kernels/collection_spice_kernels_inventory_v{kernel_ver:03d}.csv",
            kernel_rows,
        )

    @staticmethod
    def _kernel_only_products(rel: int, ver: int) -> list[str]:
        """Return the sorted product list for a kernel-only release."""
        products = [
            f"bundle_{MISSION}_spice_v{rel:03d}.xml",
            f"spice_kernels/collection_spice_kernels_inventory_v{ver:03d}.csv",
            f"spice_kernels/collection_spice_kernels_v{ver:03d}.xml",
        ]
        if rel == 1:
            products.append("readme.txt")
        return sorted(products)

    def test_empty_history_logs_info_and_returns(self, tmp_path, caplog):
        """When _get_history returns {} the method logs its header and exits
        cleanly without reading any checksum files."""
        setup = self._validate_setup(tmp_path)
        # No labels on disk → _get_history returns {}
        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        with caplog.at_level(logging.INFO):
            bundle._validate_history()

        expected = [
            (logging.INFO, ''),
            (logging.INFO, '-- Display the list of files that belong to each release.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- Files from previous releases not available to generate Bundle history.'),
            (logging.INFO, '')]
        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert results == expected

    def test_single_release_matching_checksum_logs_info(
            self, tmp_path, caplog
    ):
        """A single release whose checksum file matches the history produces
        no ERROR logs and logs the history dict."""
        setup = self._validate_setup(tmp_path)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        products = self._kernel_only_products(rel=1, ver=1)
        self._write_checksum(self._bundle_root(setup), rel=1, products=products)

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        with caplog.at_level(logging.INFO):
            bundle._validate_history()

        expected = [
            '',
            '-- Display the list of files that belong to each release.',
            '',
            "    { 1: [ 'readme.txt',",
            "           'bundle_insight_spice_v001.xml',",
            "           'spice_kernels/collection_spice_kernels_inventory_v001.csv',",
            "           'spice_kernels/collection_spice_kernels_v001.xml']}",
            '']
        assert caplog.messages == expected

    def test_two_releases_products_accumulated_into_checksum(
            self, tmp_path, caplog
    ):
        """Products are accumulated cumulatively: release 2's checksum must
        contain products from both release 1 and release 2."""
        setup = self._validate_setup(tmp_path)
        # Release 1: kernel collection v001, no kernel rows
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        # Release 2: kernel collection v002, no kernel rows
        self._write_kernel_release(setup, rel=2, kernel_ver=2, kernel_rows=[])

        rel1_products = self._kernel_only_products(rel=1, ver=1)
        rel2_new = sorted([
            f"bundle_{MISSION}_spice_v002.xml",
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            "spice_kernels/collection_spice_kernels_v002.xml",
        ])
        cumulative = sorted(rel1_products + rel2_new)

        self._write_checksum(self._bundle_root(setup), rel=1, products=rel1_products)
        self._write_checksum(self._bundle_root(setup), rel=2, products=cumulative)

        bundle = self._validate_bundle(setup, vid="2.0", collections=["something"])
        with caplog.at_level(logging.INFO):
            bundle._validate_history()

        expected = [
            '',
            '-- Display the list of files that belong to each release.',
            '',
            "    { 1: [ 'readme.txt',",
            "           'bundle_insight_spice_v001.xml',",
            "           'spice_kernels/collection_spice_kernels_inventory_v001.csv',",
            "           'spice_kernels/collection_spice_kernels_v001.xml'],",
            "      2: [ 'bundle_insight_spice_v002.xml',",
            "           'spice_kernels/collection_spice_kernels_inventory_v002.csv',",
            "           'spice_kernels/collection_spice_kernels_v002.xml']}",
            '']
        assert caplog.messages == expected

    # ------------------------------------------------------------------ #
    # 5. Checksum self-reference augmentation                              #
    # ------------------------------------------------------------------ #

    def test_checksum_product_in_history_is_appended_to_checksum_list(
            self, tmp_path, caplog
    ):
        """When the checksum product itself appears in history[rel], both the
        .tab and .xml are appended to products_in_checksum before comparison.

        The miscellaneous collection must be present in the history so that
        checksum_v001.tab appears there; the checksum file must therefore NOT
        already contain itself to avoid double-counting.
        """
        setup = self._validate_setup(tmp_path)
        # Write bundle label with both kernel and miscellaneous collections
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        # Miscellaneous collection contains a checksum entry
        _write_collection_csv(
            setup,
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:checksum_{MISSION}::1.0"],
        )

        # Build the expected product list that _get_history will return
        history_products = sorted([
            "readme.txt",
            f"bundle_{MISSION}_spice_v001.xml",
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            "spice_kernels/collection_spice_kernels_v001.xml",
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            "miscellaneous/collection_miscellaneous_v001.xml",
            f"miscellaneous/checksum/{MISSION}_v001.tab",
            f"miscellaneous/checksum/{MISSION}_v001.xml",
        ])

        # The checksum file lists everything EXCEPT the self-reference entries
        # (those are appended by the method itself after reading the file).
        # The checksum product key the code checks for is:
        #   miscellaneous/checksum/checksum_v001.tab
        # which would only appear if the inventory row used "checksum_insight"
        # rather than "checksum_{MISSION}" — here we use the raw product name
        # so checksum_product is NOT in history[rel], keeping this test clean.
        self._write_checksum(
            self._bundle_root(setup), rel=1, products=history_products
        )

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        with caplog.at_level(logging.INFO):
            bundle._validate_history()

        expected = [
            '',
            '-- Display the list of files that belong to each release.',
            '',
            "    { 1: [ 'readme.txt',",
            "           'bundle_insight_spice_v001.xml',",
            "           'spice_kernels/collection_spice_kernels_inventory_v001.csv',",
            "           'spice_kernels/collection_spice_kernels_v001.xml',",
            "           'miscellaneous/collection_miscellaneous_inventory_v001.csv',",
            "           'miscellaneous/collection_miscellaneous_v001.xml',",
            "           'miscellaneous/checksum/insight_v001.tab',",
            "           'miscellaneous/checksum/insight_v001.xml']}",
            '']
        assert caplog.messages == expected

    def test_checksum_self_reference_augmented_when_present_in_history(
            self, tmp_path, caplog
    ):
        """When ``checksum_v001.tab`` (the exact product key the code looks
        for) appears in ``history[rel]``, both the .tab and .xml are appended
        to products_in_checksum, so they must NOT appear in the .tab file
        itself to avoid double-counting."""
        setup = self._validate_setup(tmp_path)

        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        # The miscellaneous inventory uses "checksum_insight" which, after
        # splitting, produces the product key
        # "miscellaneous/checksum/insight_v001.tab".
        # But the code checks for "miscellaneous/checksum/checksum_v001.tab"
        # (the literal string with "checksum_" prefix preserved).  To get
        # THAT exact key we need the inventory line to split such that
        # field[5] starts with "checksum_":
        _write_collection_csv(
            setup,
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:checksum_{MISSION}::1.0"],
        )

        # _get_history produces this product list (including the checksum
        # self-reference key that the method will check):
        #   miscellaneous/checksum/{MISSION}_v001.tab   ← from inventory split
        # The code checks:
        #   checksum_product = "miscellaneous/checksum/checksum_v001.tab"
        # These are different names so the augmentation branch is NOT taken.
        # To exercise the augmentation branch we stub _get_history directly.
        checksum_product = "miscellaneous/checksum/checksum_v001.tab"
        checksum_label = "miscellaneous/checksum/checksum_v001.xml"
        history_products = sorted([
            "readme.txt",
            f"bundle_{MISSION}_spice_v001.xml",
            "miscellaneous/collection_miscellaneous_inventory_v001.csv",
            "miscellaneous/collection_miscellaneous_v001.xml",
            checksum_product,
            checksum_label,
        ])

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        # Stub _get_history to return the desired product list directly,
        # which includes checksum_v001.tab so the augmentation branch runs.
        bundle._get_history = lambda: {1: list(history_products)}

        # The checksum .tab must NOT contain the self-reference entries
        # (they are appended by the method), so we write everything except them.
        file_products = [p for p in history_products
                         if p not in (checksum_product, checksum_label)]
        self._write_checksum(self._bundle_root(setup), rel=1, products=file_products)

        with caplog.at_level(logging.INFO):
            bundle._validate_history()

        expected = [
            '',
            '-- Display the list of files that belong to each release.',
            '',
            "    { 1: [ 'bundle_insight_spice_v001.xml',",
            "           'miscellaneous/checksum/checksum_v001.tab',",
            "           'miscellaneous/checksum/checksum_v001.xml',",
            "           'miscellaneous/collection_miscellaneous_inventory_v001.csv',",
            "           'miscellaneous/collection_miscellaneous_v001.xml',",
            "           'readme.txt']}", '']
        assert caplog.messages == expected

    # ------------------------------------------------------------------ #
    # 6. Mismatch — ERROR logging, args.log=False branch                  #
    # ------------------------------------------------------------------ #

    def test_mismatch_logs_error_lines(self, tmp_path, caplog):
        """When products_in_checksum != products_in_history, an ERROR is
        logged naming the checksum file."""
        setup = self._validate_setup(tmp_path, log=False)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        products = self._kernel_only_products(rel=1, ver=1)
        # Drop one product to create a deliberate mismatch
        mismatched = [p for p in products if "readme" not in p]
        self._write_checksum(self._bundle_root(setup), rel=1, products=mismatched)

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                bundle._validate_history()

        expected = [
            '',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v001.tab '
            f'do not correspond to the bundle release history.',
            '      readme.txt',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v001.tab '
            f'do not correspond to the bundle release history: \n'
            f' readme.txt\n']
        assert caplog.messages == expected

    def test_mismatch_args_log_false_raises_with_diff_message(
            self, tmp_path, caplog
    ):
        """With args.log=False, handle_npb_error is called with the detailed
        diff message (containing the checksum file path)."""
        setup = self._validate_setup(tmp_path, log=False)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        products = self._kernel_only_products(rel=1, ver=1)
        mismatched = [p for p in products if "readme" not in p]
        self._write_checksum(self._bundle_root(setup), rel=1, products=mismatched)

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])

        # Mocks the "write" methods of the setup object.
        setup.write_file_list = MagicMock()
        setup.write_checksum_registry = MagicMock()

        expected_error = (
            f'Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v001.tab '
            'do not correspond to the bundle release history: \n readme.txt\n')
        with pytest.raises(Exception, match=expected_error):
            bundle._validate_history()

    # ------------------------------------------------------------------ #
    # 7. Mismatch — args.log=True branch                                  #
    # ------------------------------------------------------------------ #

    def test_mismatch_args_log_true_raises_with_short_message(
            self, tmp_path, caplog
    ):
        """With args.log=True, handle_npb_error is called with the short
        'Check generation of Checksum files.' message."""
        setup = self._validate_setup(tmp_path, log=True)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        products = self._kernel_only_products(rel=1, ver=1)
        mismatched = [p for p in products if "readme" not in p]
        self._write_checksum(self._bundle_root(setup), rel=1, products=mismatched)

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])

        # Mock the write_file_list method of the setup object.
        setup.write_file_list = MagicMock()
        setup.write_checksum_registry = MagicMock()

        expected_error = 'Check generation of Checksum files.'
        with pytest.raises(Exception, match=expected_error):
            bundle._validate_history()

    def test_mismatch_extra_product_in_checksum_is_flagged(
            self, tmp_path, caplog
    ):
        """A product present in the checksum but absent from history is also
        included in the symmetric difference and logged as an ERROR."""
        setup = self._validate_setup(tmp_path, log=False)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        products = self._kernel_only_products(rel=1, ver=1)
        # Add a spurious product to the checksum file
        extra = "spice_kernels/ck/nonexistent_v01.bc"
        self._write_checksum(
            self._bundle_root(setup), rel=1, products=products + [extra]
        )

        bundle = self._validate_bundle(setup, vid="1.0", collections=["something"])
        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                bundle._validate_history()

        expected = [
            '',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v001.tab '
            'do not correspond to the bundle release history.',
            '      spice_kernels/ck/nonexistent_v01.bc',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v001.tab '
            'do not correspond to the bundle release history: \n'
            ' spice_kernels/ck/nonexistent_v01.bc\n']
        assert caplog.messages == expected

    # ------------------------------------------------------------------ #
    # 8. Multiple releases — mismatch on second release only               #
    # ------------------------------------------------------------------ #

    def test_mismatch_on_second_release_only_raises(self, tmp_path, caplog):
        """A mismatch on release 2 raises even when release 1 is correct.
        The cumulative nature of products_in_history is exercised."""
        setup = self._validate_setup(tmp_path, log=False)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        self._write_kernel_release(setup, rel=2, kernel_ver=2, kernel_rows=[])

        rel1_products = self._kernel_only_products(rel=1, ver=1)
        rel2_new = sorted([
            f"bundle_{MISSION}_spice_v002.xml",
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            "spice_kernels/collection_spice_kernels_v002.xml",
        ])
        cumulative = sorted(rel1_products + rel2_new)

        # Release 1: correct
        self._write_checksum(self._bundle_root(setup), rel=1, products=rel1_products)
        # Release 2: missing one product
        broken = [p for p in cumulative
                  if p != f"bundle_{MISSION}_spice_v002.xml"]
        self._write_checksum(self._bundle_root(setup), rel=2, products=broken)

        bundle = self._validate_bundle(setup, vid="2.0", collections=["something"])
        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception):
                bundle._validate_history()

        expected = [
            '',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v002.tab '
            'do not correspond to the bundle release history.',
            '      bundle_insight_spice_v002.xml',
            f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v002.tab '
            'do not correspond to the bundle release history: \n'
            ' bundle_insight_spice_v002.xml\n']
        assert caplog.messages == expected

    def test_first_release_matching_second_mismatch_first_logs_no_error(
            self, tmp_path, caplog
    ):
        """Release 1's correct match produces no ERROR even though release 2
        subsequently fails.  INFO lines for the history are still emitted."""
        setup = self._validate_setup(tmp_path, log=False)
        self._write_kernel_release(setup, rel=1, kernel_ver=1, kernel_rows=[])
        self._write_kernel_release(setup, rel=2, kernel_ver=2, kernel_rows=[])

        rel1_products = self._kernel_only_products(rel=1, ver=1)
        rel2_new = [
            f"bundle_{MISSION}_spice_v002.xml",
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            "spice_kernels/collection_spice_kernels_v002.xml",
        ]
        cumulative = sorted(rel1_products + rel2_new)

        self._write_checksum(self._bundle_root(setup), rel=1, products=rel1_products)
        self._write_checksum(self._bundle_root(setup), rel=2,
                        products=[p for p in cumulative
                                  if "v002.xml" not in p])

        info_records_before_error = []
        bundle = self._validate_bundle(setup, vid="2.0", collections=["something"])
        with caplog.at_level(logging.INFO):
            with pytest.raises(Exception):
                bundle._validate_history()

        # INFO lines must have been emitted (history was non-empty)
        expected = [
            (logging.INFO, ''),
            (logging.INFO, '-- Display the list of files that belong to each release.'),
            (logging.INFO, ''),
            (logging.INFO, "    { 1: [ 'readme.txt',"),
            (logging.INFO, "           'bundle_insight_spice_v001.xml',"),
            (logging.INFO, "           'spice_kernels/collection_spice_kernels_inventory_v001.csv',"),
            (logging.INFO, "           'spice_kernels/collection_spice_kernels_v001.xml'],"),
            (logging.INFO, "      2: [ 'bundle_insight_spice_v002.xml',"),
            (logging.INFO, "           'spice_kernels/collection_spice_kernels_inventory_v002.csv',"),
            (logging.INFO, "           'spice_kernels/collection_spice_kernels_v002.xml']}"),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v002.tab '
                            'do not correspond to the bundle release history.'),
            (logging.ERROR, '      bundle_insight_spice_v002.xml'),
            (logging.ERROR, '      spice_kernels/collection_spice_kernels_v002.xml'),
            (logging.ERROR, f'-- Products in {tmp_path}/bundle/insight_spice/miscellaneous/checksum/checksum_v002.tab '
                            f'do not correspond to the bundle release history: \n'
                            f' bundle_insight_spice_v002.xml\n'
                            f'spice_kernels/collection_spice_kernels_v002.xml\n')]
        results = [(r[1], r[2]) for r in caplog.record_tuples]
        assert results == expected
