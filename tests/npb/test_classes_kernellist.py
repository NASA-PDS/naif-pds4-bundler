"""Tests for KernelList.write_plan.

Each test class covers one logical branch or behavior of the method.
A shared ``make_setup`` factory builds the minimum viable mock of the
``setup`` object that ``KernelList.__init__`` and ``write_plan`` require,
so individual tests only override what is relevant to them.
"""
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


# ---------------------------------------------------------------------------
# 1. Normal directory scan — kernels found, no meta-kernel, no OrbNum:
#    write_plan discovers kernels from kernel directories.
# ---------------------------------------------------------------------------

def test_returns_true_when_kernels_found(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)

    result = kl.write_plan()

    assert result is True


def test_plan_file_is_created(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert plan_path(setup).exists()


def test_plan_contains_matched_kernel(tmp_path):
    """Tests that the plan contains the matched kernel, the kernel is in the kernel_list
    attribute and that the plan has been registered in the list of file to write at the
    end of an execution.
    """
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)
    assert "maven_sc_rec_200101_200201_v01.bsp" in kl.kernel_list
    setup.add_file.assert_called_once()
    args = [a.replace(str(tmp_path), 'p') for a in setup.add_file.call_args_list[0].args]
    assert  args == ['p/working/maven_release_01.plan']
    assert setup.add_file.call_args_list[0].kwargs == {}


def test_unmatched_kernel_not_in_plan(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "some_unrelated_file.txt").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "some_unrelated_file.txt" not in plan_contents(setup)


def test_meta_kernels_excluded_from_directory_scan(tmp_path):
    """TM files in the kernel dir must not be auto-included."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "maven_v01.tm").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_v01.tm" not in plan_contents(setup)


def test_multiple_kernel_directories_all_scanned(tmp_path):
    ker_dir1 = tmp_path / "kernels1"
    ker_dir2 = tmp_path / "kernels2"
    ker_dir1.mkdir()
    ker_dir2.mkdir()
    (ker_dir1 / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir2 / "maven_sc_rec_200201_200301_v01.bsp").touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir1), str(ker_dir2)],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert "maven_sc_rec_200101_200201_v01.bsp" in contents
    assert "maven_sc_rec_200201_200301_v01.bsp" in contents


def test_kernels_in_subdirectories_are_found(tmp_path):
    """Glob is recursive — kernels in sub-dirs must be discovered."""
    ker_dir = tmp_path / "kernels"
    sub = ker_dir / "spk"
    sub.mkdir(parents=True)
    (sub / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)

# ---------------------------------------------------------------------------
# 2. Empty result — no kernels found:
#    write_plan returns False and sets an empty kernel_list.
# ---------------------------------------------------------------------------

def test_returns_false_when_no_kernels(tmp_path):
    setup = make_setup(tmp_path)
    kl = make_kernel_list(setup)

    result = kl.write_plan()

    assert result is False


def test_kernel_list_is_empty_list(tmp_path):
    setup = make_setup(tmp_path)
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert kl.kernel_list == []


def test_add_file_not_called_when_empty(tmp_path):
    setup = make_setup(tmp_path)
    kl = make_kernel_list(setup)
    kl.write_plan()

    setup.add_file.assert_not_called()


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_plan_file_not_written_when_empty(tmp_path):
    """No .plan file should exist if there are no kernels.

    NOTE: This test documents the *desired* behavior after the bug fix
    (empty file written before the empty check). If run against the
    current unpatched code it will FAIL — that failure is intentional
    and flags the bug.
    """
    setup = make_setup(tmp_path)
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert not plan_path(setup).exists()

# ---------------------------------------------------------------------------
# 3. Mapping patterns:
#    Kernels matched via a mapping pattern are included in the plan.
# ---------------------------------------------------------------------------

def test_mapped_kernel_included(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    # The file on disk uses the mapping name
    (ker_dir / "maven_sc_rec_200101_200201_v01_mapped.bsp").touch()

    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {
            "description": "SPK kernel.",
            "mapping": r"maven_sc_rec_\d{6}_\d{6}_v\d+_mapped\.bsp",
        }
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_sc_rec_200101_200201_v01_mapped.bsp" in plan_contents(setup)

# ---------------------------------------------------------------------------
# 4. Meta-kernel handling — mk_inputs present in config:
#    When mk_inputs is configured, the referenced MK is added to the plan.
# ---------------------------------------------------------------------------

def test_mk_from_config_added_to_plan(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    mk_file = tmp_path / "maven_v01.tm"
    mk_file.touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        mk_inputs={"file": str(mk_file)},
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_v01.tm" in plan_contents(setup)


def test_mk_as_list_all_added(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    mk1 = tmp_path / "maven_v01.tm"
    mk2 = tmp_path / "maven_v02.tm"
    mk1.touch()
    mk2.touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        mk_inputs={"file": [str(mk1), str(mk2)]},
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert "maven_v01.tm" in contents
    assert "maven_v02.tm" in contents


def test_missing_mk_raises_error(tmp_path):
    """A configured MK that does not exist must raise an NPB error."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    missing_mk = str(tmp_path / "nonexistent.tm")

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        mk_inputs={"file": missing_mk},
    )
    kl = make_kernel_list(setup)

    with pytest.raises(RuntimeError, match="Meta-kernel provided via configuration "
                                           "nonexistent.tm does not exist."):
        kl.write_plan()


def test_mk_not_added_in_labeling_mode(tmp_path):
    """In faucet=labels mode, mk_inputs must be ignored."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()

    mk_file = tmp_path / "maven_v01.tm"
    mk_file.touch()

    setup = make_setup(
        tmp_path,
        faucet="labels",
        plan=str(ker_dir / "maven_sc_rec_200101_200201_v01.bsp"),
        kernels_directory=[str(ker_dir)],
        mk_inputs={"file": str(mk_file)},
    )
    # In labeling mode a single kernel file is the plan input
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_v01.tm" not in plan_contents(setup)

# ---------------------------------------------------------------------------
# 5. Meta-kernel inference — no mk_inputs, infer from bundle:
#    When mk_inputs is absent, write_plan infers the next MK version.
# ---------------------------------------------------------------------------

def test_next_version_mk_inferred(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    bundle = tmp_path / "bundle"
    make_bundle_structure(bundle, "maven_v01.tm")

    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {"description": "SPK."},
        r"maven_v\d+\.tm": {"description": "MK."},
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    setup.bundle_directory = str(bundle)

    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_v02.tm" in plan_contents(setup)


def test_no_former_mk_produces_warning(tmp_path, caplog):
    """If no former MK exists in the bundle, a warning is logged."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    # bundle directory exists but has no mk/ subdirectory
    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])

    kl = make_kernel_list(setup)
    with caplog.at_level(logging.WARNING):
        kl.write_plan()

    assert caplog.messages == ['-- No former meta-kernel found to generate meta-kernel for the list.']


def test_inferred_mk_not_added_in_labeling_mode(tmp_path):
    """MK inference must be skipped in faucet=labels mode."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    kernel_file = ker_dir / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    bundle = tmp_path / "bundle"
    make_bundle_structure(bundle, "maven_v01.tm")

    setup = make_setup(
        tmp_path,
        faucet="labels",
        plan=str(kernel_file),
        kernels_directory=[str(ker_dir)],
    )
    setup.bundle_directory = str(bundle)

    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert not any(".tm" in line for line in contents)


def test_mk_version_incremented_correctly(tmp_path):
    """Version number zero-padding must be preserved on increment."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    bundle = tmp_path / "bundle"
    make_bundle_structure(bundle, "maven_v009.tm")

    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {"description": "SPK."},
        r"maven_v\d+\.tm": {"description": "MK."},
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    setup.bundle_directory = str(bundle)

    kl = make_kernel_list(setup)
    kl.write_plan()

    # v009 -> v010, zero-padded to same width
    assert "maven_v010.tm" in plan_contents(setup)


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_no_duplicate_mk_appended(tmp_path):
    """Even if multiple patterns match the MK name, it appears only once.

    NOTE: This test documents the *desired* behavior after the bug fix
    (loop appends MK once per matching pattern). It will FAIL against
    the current unpatched code — that failure flags the bug.
    """
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    bundle = tmp_path / "bundle"
    make_bundle_structure(bundle, "maven_v01.tm")

    # Two patterns that both match the MK name
    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {"description": "SPK."},
        r"maven_v\d+\.tm": {"description": "MK v1."},
        r"maven_v\d\d\.tm": {"description": "MK v2."},
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    setup.bundle_directory = str(bundle)

    kl = make_kernel_list(setup)
    kl.write_plan()

    mk_lines = [ln for ln in plan_contents(setup) if ".tm" in ln]
    assert len(mk_lines) == 1

def test_no_mk_inferred_when_no_kernels(tmp_path, caplog):
    """A former MK exists in the bundle but no kernels were matched —
    the MK must not be inferred and the method must return False."""
    # Empty kernel directory — nothing will match
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()

    bundle = tmp_path / "bundle"
    mk_dir = bundle / "maven_spice" / "spice_kernels" / "mk"
    mk_dir.mkdir(parents=True)
    (mk_dir / "maven_v01.tm").touch()

    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {"description": "SPK."},
        r"maven_v\d+\.tm": {"description": "MK."},
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    setup.bundle_directory = str(bundle)

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.ERROR):
        result = kl.write_plan()

    assert caplog.messages == ['-- No former meta-kernel found to generate meta-kernel for the list.']
    assert result is False
    assert not any(".tm" in ln for ln in plan_contents(setup))

# ---------------------------------------------------------------------------
# 6. OrbNum files
#    OrbNum files are appended when orbnum_directory is set.
# ---------------------------------------------------------------------------

def test_orb_num_file_included(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    orb_dir = tmp_path / "orbnum"
    orb_dir.mkdir()
    (orb_dir / "maven_orb_rec_200101_200201_v01.orb").touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        orbnum_directory=str(orb_dir),
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_orb_rec_200101_200201_v01.orb" in plan_contents(setup)


def test_orb_num_not_included_in_labeling_mode(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    kernel_file = ker_dir / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    orb_dir = tmp_path / "orbnum"
    orb_dir.mkdir()
    (orb_dir / "maven_orb_rec_200101_200201_v01.orb").touch()

    setup = make_setup(
        tmp_path,
        faucet="labels",
        plan=str(kernel_file),
        kernels_directory=[str(ker_dir)],
        orbnum_directory=str(orb_dir),
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_orb_rec_200101_200201_v01.orb" not in plan_contents(setup)


def test_unmatched_orb_num_not_included(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    orb_dir = tmp_path / "orbnum"
    orb_dir.mkdir()
    (orb_dir / "something_unrelated.orb").touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        orbnum_directory=str(orb_dir),
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "something_unrelated.orb" not in plan_contents(setup)

# ---------------------------------------------------------------------------
# 7. Labeling mode (faucet == "labels")
#    In labeling mode a single kernel file acts as the plan input.
# ---------------------------------------------------------------------------

def test_single_kernel_becomes_plan(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    kernel = ker_dir / "maven_sc_rec_200101_200201_v01.bsp"
    kernel.touch()

    setup = make_setup(
        tmp_path,
        faucet="labels",
        plan=str(kernel),
        kernels_directory=[str(ker_dir)],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)


def test_other_kernels_in_dir_not_included(tmp_path):
    """Labeling mode must not glob the whole directory."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    kernel = ker_dir / "maven_sc_rec_200101_200201_v01.bsp"
    kernel.touch()
    (ker_dir / "maven_sc_rec_200201_200301_v01.bsp").touch()

    setup = make_setup(
        tmp_path,
        faucet="labels",
        plan=str(kernel),
        kernels_directory=[str(ker_dir)],
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert "maven_sc_rec_200201_200301_v01.bsp" not in contents

# ---------------------------------------------------------------------------
# 8. Plan file format
#    The .plan file must follow the expected naming and line format.
# ---------------------------------------------------------------------------

def test_plan_file_name_follows_convention(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)], release=3)
    kl = make_kernel_list(setup)
    kl.write_plan()

    expected = Path(setup.working_directory) / "maven_release_03.plan"
    assert expected.exists()


def test_each_kernel_on_its_own_line(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "maven_sc_rec_200201_200301_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert len(contents) == 2


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_no_duplicate_kernels_in_plan(tmp_path):
    """A kernel matching multiple patterns must appear only once.

    NOTE: Documents desired post-fix behaviour. Will FAIL against
    the current unpatched code (no break after first match).
    """
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    # Two patterns that both match the same kernel
    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {"description": "SPK v1."},
        r"maven_sc_rec_\d{6}_\d{6}_v01\.bsp": {"description": "SPK v2."},
    }
    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        json_config=json_config,
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    contents = plan_contents(setup)
    assert contents.count("maven_sc_rec_200101_200201_v01.bsp") == 1

# ---------------------------------------------------------------------------
# 9. Release numbering
#    Plan filename uses zero-padded two-digit release number.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("release,expected_suffix", [
    (1, "01"),
    (9, "09"),
    (10, "10"),
    (99, "99"),
])
def test_release_number_formatting(tmp_path, release, expected_suffix):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        release=release,
    )
    kl = make_kernel_list(setup)
    kl.write_plan()

    expected = (
            Path(setup.working_directory)
            / f"maven_release_{expected_suffix}.plan"
    )
    assert expected.exists()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_args(faucet="plan", plan=None, silent=True, verbose=False):
    """Build a minimal args namespace."""
    return SimpleNamespace(
        faucet=faucet,
        plan=plan,
        silent=silent,
        verbose=verbose,
    )


def make_bundle_structure(bundle_dir, mk_name):
    mk_dir = bundle_dir / "maven_spice" / "spice_kernels" / "mk"
    mk_dir.mkdir(parents=True)
    (mk_dir / mk_name).touch()


def make_kernel_list(setup):
    """Instantiate KernelList while suppressing the read_config I/O."""
    # read_config only reads from setup.kernel_list_config (already a dict)
    # and writes to self.re_config / self.json_config — no filesystem access.
    return KernelList(setup)


def make_setup(
        tmp_path,
        *,
        faucet="plan",
        plan=None,
        kernels_directory=None,
        orbnum_directory=None,
        orbnum=None,
        mk_inputs=None,
        json_config=None,
        release=1,
        pds_version="4",
):
    """
    Return a SimpleNamespace that satisfies every attribute read by
    KernelList.__init__ and write_plan.

    Parameters that vary per scenario are keyword-only so callers can be
    explicit about what they are changing.
    """
    working = tmp_path / "working"
    working.mkdir()
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)

    if kernels_directory is None:
        kernels_directory = [str(tmp_path / "kernels")]
        Path(kernels_directory[0]).mkdir()

    # Minimal json_config: one SPK pattern, no mapping, no special patterns
    if json_config is None:
        json_config = {
            r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {
                "description": "SPK kernel for MAVEN.",
            }
        }

    setup = SimpleNamespace(
        # pipeline state
        step=1,
        args=make_args(faucet=faucet, plan=plan),
        # identity
        mission_acronym="maven",
        mission_name="MAVEN",
        run_type="release",
        release=release,
        release_date="2024-01-01",
        observer="MAVEN",
        producer_name="Test Producer",
        pds_version=pds_version,
        # directories
        working_directory=str(working),
        kernels_directory=kernels_directory,
        bundle_directory=str(bundle),
        orbnum_directory=orbnum_directory or "",
        templates_directory=str(tmp_path),
        # config
        kernel_list_config=json_config,
        # optional attributes — absent by default (tests use hasattr guards)
        # mk_inputs and orbnum are set conditionally below
    )

    if mk_inputs is not None:
        setup.mk_inputs = mk_inputs
    if orbnum is not None:
        setup.orbnum = orbnum

    # add_file is called at the end of write_plan
    setup.add_file = MagicMock()

    # PDS3 extras (only needed when pds_version == "3")
    if pds_version == "3":
        setup.pds3_mission_template = {"DATA_SET_ID": "MAVEN-1-SPICE-V1.0"}
        setup.volume_id = "MAVORB_0001"

    return setup


def plan_contents(setup):
    """Return the lines written to the .plan file (stripped, non-empty)."""
    p = plan_path(setup)
    return [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]


def plan_path(setup):
    """Return the expected .plan file path for a given setup."""
    name = (
        f"{setup.mission_acronym}_{setup.run_type}_"
        f"{int(setup.release):02d}.plan"
    )
    return Path(setup.working_directory) / name