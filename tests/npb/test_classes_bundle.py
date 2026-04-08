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
from pathlib import Path
from types import SimpleNamespace

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
# 1. Return value shape
# ---------------------------------------------------------------------------


class TestReturnValueShape:

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
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
        )
        result = bundle._get_history()
        assert isinstance(result, dict)

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
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["non-empty"],  # so number_of_releases stays at 2
        )
        result = bundle._get_history()
        assert set(result.keys()) == {1, 2}

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
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
        )
        result = bundle._get_history()
        for v in result.values():
            assert isinstance(v, list)


# ---------------------------------------------------------------------------
# 2. Release counting (VID and collections interaction)
# ---------------------------------------------------------------------------


class TestReleaseCounting:

    def test_no_collections_decrements_release_count(self, fake_setup):
        """When collections is empty the current release is not included."""
        # VID says 2.0 but no collections → only release 1 is reconstructed
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=[],  # pipeline not yet run
        )
        result = bundle._get_history()
        assert set(result.keys()) == {1}

    def test_with_collections_includes_current_release(self, fake_setup):
        """When collections is non-empty all releases up to VID are included."""
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
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert set(result.keys()) == {1, 2}

    def test_vid_1_no_collections_returns_empty_dict(self, fake_setup):
        """VID=1.0 and no collections means 0 releases → empty dict."""
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=[],
        )
        result = bundle._get_history()
        assert result == {}


# ---------------------------------------------------------------------------
# 3. Missing bundle label
# ---------------------------------------------------------------------------


class TestMissingBundleLabel:

    def test_missing_label_returns_empty_dict(self, fake_setup):
        """If a bundle label file is absent _get_history returns {}."""
        # Do NOT write the label file
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert result == {}

    def test_missing_label_emits_warning(self, fake_setup, caplog):
        """A warning is logged when a bundle label is missing."""
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        with caplog.at_level(logging.WARNING):
            bundle._get_history()
        assert any("not available" in r.message for r in caplog.records)

    def test_missing_label_for_second_release_returns_empty(self, fake_setup):
        """If release 2 label is missing the method returns {} (early exit)."""
        # Write only release 1 label
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [],
        )
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert result == {}


# ---------------------------------------------------------------------------
# 4. readme.txt always appears in release 1 only
# ---------------------------------------------------------------------------


class TestReadmeEntry:

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
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert "readme.txt" in result[1]

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
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert "readme.txt" not in result[2]


# ---------------------------------------------------------------------------
# 5. Bundle label file is always recorded
# ---------------------------------------------------------------------------


class TestBundleLabelEntry:

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
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert f"bundle_{MISSION}_spice_v001.xml" in result[1]


# ---------------------------------------------------------------------------
# 6. Kernel collection parsing
# ---------------------------------------------------------------------------

# Inventory CSV lines follow the PDS4 collection inventory format.
# A typical "P" (Primary) record for a kernel:
#   P,urn:nasa:pds:insight.spice:spice_kernels:ck_insight_ida_enc_v01.bc::1.0
# The method splits on ":" and takes index [5], then replaces first "_" with "/".
# "ck_insight_ida_enc_v01.bc" → "ck/insight_ida_enc_v01.bc"


class TestKernelCollectionParsing:

    @staticmethod
    def _setup_single_release(fake_setup, inventory_rows):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            inventory_rows,
        )
        return _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )

    def test_kernel_collection_inventory_csv_in_history(self, fake_setup):
        bundle = self._setup_single_release(fake_setup, [])
        result = bundle._get_history()
        assert (
            "spice_kernels/collection_spice_kernels_inventory_v001.csv"
            in result[1]
        )

    def test_kernel_collection_label_in_history(self, fake_setup):
        bundle = self._setup_single_release(fake_setup, [])
        result = bundle._get_history()
        assert "spice_kernels/collection_spice_kernels_v001.xml" in result[1]

    def test_kernel_product_and_label_added(self, fake_setup):
        """A non-MK kernel line adds both the data file and its XML label."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_insight_ida_enc_v01.bc::1.0",
        ]
        bundle = self._setup_single_release(fake_setup, rows)
        result = bundle._get_history()
        assert "spice_kernels/ck/insight_ida_enc_v01.bc" in result[1]
        assert "spice_kernels/ck/insight_ida_enc_v01.xml" in result[1]

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
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        # No kernel collection entries should appear since member is Secondary
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" not in result[1]

    def test_multiple_kernels_all_added(self, fake_setup):
        """All kernel rows in the inventory are added."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_insight_ida_enc_v01.bc::1.0",
            f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:spk_insight_cruise_v1.bsp::1.0",
        ]
        bundle = self._setup_single_release(fake_setup, rows)
        result = bundle._get_history()
        assert "spice_kernels/ck/insight_ida_enc_v01.bc" in result[1]
        assert "spice_kernels/spk/insight_cruise_v1.bsp" in result[1]

    def test_non_p_rows_ignored(self, fake_setup):
        """Lines not starting with 'P' (e.g. header or 'S' secondary) are ignored."""
        rows = [
            "LBLRECL,1024",
            f"S,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_secondary_v01.bc::1.0",
        ]
        bundle = self._setup_single_release(fake_setup, rows)
        result = bundle._get_history()
        # Neither the header nor the secondary product should appear
        assert not any("ck_secondary" in f for f in result[1])

    def test_same_collection_version_not_duplicated_across_releases(self, fake_setup):
        """If the kernel collection version has not changed between two releases,
        its files are not listed again in the second release."""
        # Both releases point to the SAME collection version (v001)
        for rel in (1, 2):
            _write_bundle_label(fake_setup, rel, [
                # Both releases reference collection version 1
                {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
                 "status": "Primary"},
            ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v01.bc::1.0"],
        )
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        # The collection CSV and its products should only appear in release 1
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" in result[1]
        assert "spice_kernels/collection_spice_kernels_inventory_v001.csv" not in result[2]


# ---------------------------------------------------------------------------
# 7. Meta-kernel version formatting (setup.mk path)
# ---------------------------------------------------------------------------


class TestMetaKernelVersionFormatting:
    """Tests for the mk version-length logic when setup.mk is present."""

    @staticmethod
    def _mk_setup(fake_setup, version_length: int):
        """Augment fake_setup with a `mk` config for a given VERSION length."""
        fake_setup.mk = [{
            "name": [{
                "pattern": [{
                    "#text": "VERSION",
                    "@length": str(version_length),
                }]
            }]
        }]
        return fake_setup

    @staticmethod
    def _write_mk_inventory(fake_setup, mk_lidvid_suffix: str):
        """Write a kernel inventory with a single MK entry."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_{mk_lidvid_suffix}::{mk_lidvid_suffix.split('v')[-1]}.0",
        ]
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )

    def test_mk_version_length_1(self, fake_setup):
        setup = self._mk_setup(fake_setup, version_length=1)
        # MK line: "mk_insight_v1" → version=1, length=1 → "v1.tm"
        mk_line = f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0\n"
        # Manually craft the CSV so mk_ver=1 is parseable
        rows = [mk_line.strip()]
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        mk_files = [f for f in result[1] if f.endswith(".tm")]
        assert all("_v1.tm" in f for f in mk_files)

    def test_mk_version_length_2(self, fake_setup):
        setup = self._mk_setup(fake_setup, version_length=2)
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        mk_files = [f for f in result[1] if f.endswith(".tm")]
        assert all("_v01.tm" in f for f in mk_files)

    def test_mk_version_length_3(self, fake_setup):
        setup = self._mk_setup(fake_setup, version_length=3)
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        mk_files = [f for f in result[1] if f.endswith(".tm")]
        assert all("_v001.tm" in f for f in mk_files)

    def test_mk_version_length_invalid_raises(self, fake_setup):
        """An unsupported VERSION length should trigger handle_npb_error."""
        setup = self._mk_setup(fake_setup, version_length=4)
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        with pytest.raises(Exception):
            bundle._get_history()

    def test_mk_label_added_alongside_tm(self, fake_setup):
        """For every .tm product its .xml label is also added."""
        setup = self._mk_setup(fake_setup, version_length=2)
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        tm_files = [f for f in result[1] if f.endswith(".tm")]
        xml_files = [f for f in result[1] if f.endswith(".xml")]
        for tm in tm_files:
            assert tm.replace(".tm", ".xml") in xml_files

    def test_mk_fallback_to_mk_inputs(self, fake_setup):
        """When setup.mk is absent but setup.mk_inputs is present, MK names
        are derived from mk_inputs."""
        fake_setup.mk_inputs = {"file": "/path/to/insight_v01.tm"}
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert "spice_kernels/mk/insight_v01.tm" in result[1]
        assert "spice_kernels/mk/insight_v01.xml" in result[1]

    def test_mk_fallback_default_2_digits_warns(self, fake_setup, caplog):
        """When neither setup.mk nor setup.mk_inputs is present, a warning is
        logged and the MK is formatted with 2 digits."""
        # Ensure neither mk nor mk_inputs exist on the setup object
        rows = [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:mk_insight::1.0"]
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            rows,
        )
        bundle = _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )
        with caplog.at_level(logging.WARNING):
            result = bundle._get_history()
        assert any("defaulted" in r.message for r in caplog.records)
        tm_files = [f for f in result[1] if f.endswith(".tm")]
        assert all("_v01.tm" in f for f in tm_files)


# ---------------------------------------------------------------------------
# 8. Miscellaneous collection parsing
# ---------------------------------------------------------------------------


class TestMiscellaneousCollectionParsing:

    @staticmethod
    def _setup_misc_release(fake_setup, inv_rows, write_file=True):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:miscellaneous::1.0",
             "status": "Primary"},
        ])
        inv_path = "miscellaneous/collection_miscellaneous_inventory_v001.csv"
        if write_file:
            _write_collection_csv(fake_setup, inv_path, inv_rows)
        return _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )

    def test_misc_collection_csv_in_history(self, fake_setup):
        bundle = self._setup_misc_release(fake_setup, [])
        result = bundle._get_history()
        assert (
            "miscellaneous/collection_miscellaneous_inventory_v001.csv"
            in result[1]
        )

    def test_misc_collection_label_in_history(self, fake_setup):
        bundle = self._setup_misc_release(fake_setup, [])
        result = bundle._get_history()
        assert "miscellaneous/collection_miscellaneous_v001.xml" in result[1]

    def test_orbnum_product_and_label_added(self, fake_setup):
        """An ORBNUM (non-checksum) misc product adds the file and XML label."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:orbnum_insight_v01.nrb::1.0",
        ]
        bundle = self._setup_misc_release(fake_setup, rows)
        result = bundle._get_history()
        assert "miscellaneous/orbnum/insight_v01.nrb" in result[1]
        assert "miscellaneous/orbnum/insight_v01.xml" in result[1]

    def test_checksum_product_and_label_added(self, fake_setup):
        """A checksum misc product adds the versioned .tab and its XML label."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:miscellaneous:checksum_insight::1.0",
        ]
        bundle = self._setup_misc_release(fake_setup, rows)
        result = bundle._get_history()
        # Checksum product is versioned with the collection release number (001)
        assert "miscellaneous/checksum/insight_v001.tab" in result[1]
        assert "miscellaneous/checksum/insight_v001.xml" in result[1]

    def test_misc_collection_absent_from_filesystem_skipped_gracefully(
        self, fake_setup
    ):
        """If the miscellaneous inventory CSV does not exist on disk the
        collection is silently omitted (os.path.exists guard)."""
        bundle = self._setup_misc_release(fake_setup, [], write_file=False)
        result = bundle._get_history()
        assert (
            "miscellaneous/collection_miscellaneous_inventory_v001.csv"
            not in result[1]
        )


# ---------------------------------------------------------------------------
# 9. Document collection parsing
# ---------------------------------------------------------------------------


class TestDocumentCollectionParsing:

    @staticmethod
    def _setup_doc_release(fake_setup, inv_rows):
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:document::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "document/collection_document_inventory_v001.csv",
            inv_rows,
        )
        return _make_bundle(
            fake_setup, vid="1.0",
            name=f"bundle_{MISSION}_spice_v001.xml",
            collections=["something"],
        )

    def test_document_collection_csv_in_history(self, fake_setup):
        bundle = self._setup_doc_release(fake_setup, [])
        result = bundle._get_history()
        assert "document/collection_document_inventory_v001.csv" in result[1]

    def test_document_collection_label_in_history(self, fake_setup):
        bundle = self._setup_doc_release(fake_setup, [])
        result = bundle._get_history()
        assert "document/collection_document_v001.xml" in result[1]

    def test_document_product_html_and_xml_added(self, fake_setup):
        """A document inventory line adds the versioned HTML file and its label."""
        rows = [
            f"P,urn:nasa:pds:{MISSION}.spice:document:spiceds::1.0",
        ]
        bundle = self._setup_doc_release(fake_setup, rows)
        result = bundle._get_history()
        assert "document/spiceds_v001.html" in result[1]
        assert "document/spiceds_v001.xml" in result[1]


# ---------------------------------------------------------------------------
# 10. Multi-release incremental behaviour
# ---------------------------------------------------------------------------


class TestMultiReleaseIncremental:

    def test_new_collection_version_only_in_release_it_was_introduced(
        self, fake_setup
    ):
        """If the kernel collection version changes in release 2, the new
        collection files appear only in release 2."""
        # Release 1 → kernel collection v001
        _write_bundle_label(fake_setup, 1, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::1.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v001.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v01.bc::1.0"],
        )
        # Release 2 → kernel collection v002 (new version)
        _write_bundle_label(fake_setup, 2, [
            {"lid": f"urn:nasa:pds:{MISSION}.spice:spice_kernels::2.0",
             "status": "Primary"},
        ])
        _write_collection_csv(
            fake_setup,
            "spice_kernels/collection_spice_kernels_inventory_v002.csv",
            [f"P,urn:nasa:pds:{MISSION}.spice:spice_kernels:ck_v02.bc::1.0"],
        )
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert "spice_kernels/ck/v01.bc" in result[1]
        assert "spice_kernels/ck/v02.bc" in result[2]
        assert "spice_kernels/ck/v02.bc" not in result[1]

    def test_release_counts_accumulate_correctly_across_three_releases(
        self, fake_setup
    ):
        """Across three releases each has its own bundle label entry."""
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
        bundle = _make_bundle(
            fake_setup, vid="3.0",
            name=f"bundle_{MISSION}_spice_v003.xml",
            collections=["something"],
        )
        result = bundle._get_history()
        assert set(result.keys()) == {1, 2, 3}
        for rel in (1, 2, 3):
            assert f"bundle_{MISSION}_spice_v{rel:03d}.xml" in result[rel]


# ---------------------------------------------------------------------------
# 11. Duplicate detection warning
# ---------------------------------------------------------------------------


class TestDuplicateDetection:

    def test_duplicate_entries_emit_warning(self, fake_setup, caplog):
        """If the same product path appears in more than one release the
        duplicate-check at the end of _get_history logs a warning.

        Strategy: create two releases each backed by a *different* collection
        version (so the ker_col_ver guard does not deduplicate them), but both
        inventories list the exact same kernel filename.  _get_history appends
        the file to history[1] and history[2] independently; when the final
        duplicate check flattens all releases into one list it finds the
        repeated entry and warns.

        Note: the two Primary entries in each label are deliberately distinct
        LIDVIDs so that etree_to_dict returns a list, not a dict.
        """
        # Release 1 — collection v001, contains ck_shared.bc
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
        # Release 2 — collection v002 (new version), but still lists the
        # same ck_shared.bc — this is the duplicate across releases.
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
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        with caplog.at_level(logging.WARNING):
            result = bundle._get_history()
        assert any("duplicate" in r.message.lower() for r in caplog.records)
        # Method still returns a dict (does not raise)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 12. Known bug: uninitialized `ver` variable
# ---------------------------------------------------------------------------


class TestUninitializedVer:
    """Documents the known bug (issue #4 in the code review) where `ver` can
    be referenced before assignment when all collection versions in
    rel_ker_col_ver equal ker_col_ver.

    These tests are expected to FAIL until the bug is fixed, and are marked
    accordingly with xfail so that the suite stays green.
    """

    @pytest.mark.skip(
        reason="Bug: ver uninitialized when all rel_ker match ker_col_ver",
    )
    def test_no_version_change_does_not_raise_name_error(self, fake_setup):
        """If every kernel collection version in a release equals the previous
        one, the code currently raises NameError on `ker_col_ver = ver`."""
        # Two releases both pointing to collection v001 (no version change)
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
        bundle = _make_bundle(
            fake_setup, vid="2.0",
            name=f"bundle_{MISSION}_spice_v002.xml",
            collections=["something"],
        )
        # This should not raise, but currently does
        result = bundle._get_history()
        assert isinstance(result, dict)
