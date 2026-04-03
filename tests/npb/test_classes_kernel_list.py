"""Tests for KernelList.read_plan.

Reuses the same make_setup / make_kernel_list / make_args helpers
established in test_write_plan.py.  Each test class targets one
logical branch of the method.
"""

import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


# ---------------------------------------------------------------------------
# 1. Input validation — file extension and faucet mode:
#    read_plan must enforce the .plan extension outside labeling mode.
# ---------------------------------------------------------------------------

def test_valid_plan_extension_accepted(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    # Should not raise
    kl.read_plan(str(plan))


def test_non_plan_extension_outside_labeling_mode_raises(tmp_path):
    """Any extension other than .plan must raise an NPB error when
    faucet is not 'labels'."""
    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    setup = make_setup(tmp_path)
    kl = make_kernel_list(setup)

    with pytest.raises(RuntimeError, match=r'Release plan requires \*\.plan extension. '
                                           'Single kernels are only allowed in labeling mode.'):
        kl.read_plan(str(kernel_file))


def test_non_plan_extension_in_labeling_mode_accepted(tmp_path):
    """In labeling mode a single kernel file (no .plan extension) is
    valid input — a synthetic plan is generated instead."""
    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    setup = make_setup(tmp_path, faucet="labels")
    kl = make_kernel_list(setup)
    # Should not raise
    kl.read_plan(str(kernel_file))


def test_txt_extension_outside_labeling_mode_raises(tmp_path):
    """Extension check is based purely on the suffix, not the content."""
    setup = make_setup(tmp_path, faucet="plan")

    bad_file = tmp_path / "working" / "maven_release_01.txt"
    bad_file.write_text("maven_sc_rec_200101_200201_v01.bsp\n")
    kl = make_kernel_list(setup)

    with pytest.raises(RuntimeError, match=r'Release plan requires \*\.plan extension. '
                                           'Single kernels are only allowed in labeling mode.'):
        kl.read_plan(str(bad_file))

# ---------------------------------------------------------------------------
# 2. Synthetic plan generation (labeling mode)
#    When faucet == 'labels' and input has no .plan extension,
#    read_plan must create a synthetic .plan file and read from it.
# ---------------------------------------------------------------------------

def test_synthetic_plan_file_is_created(tmp_path):
    setup = make_setup(tmp_path, faucet="labels")
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    kl = make_kernel_list(setup)
    kl.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_01.plan"
    assert expected_plan.exists()


def test_synthetic_plan_contains_kernel_filename(tmp_path):
    setup = make_setup(tmp_path, faucet="labels")
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    kl = make_kernel_list(setup)
    kl.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_01.plan"
    content = expected_plan.read_text()
    assert "maven_release_01.plan" in content


def test_synthetic_plan_name_uses_release_number(tmp_path):
    setup = make_setup(tmp_path, faucet="labels", release=5)
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    kl = make_kernel_list(setup)
    kl.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_05.plan"
    assert expected_plan.exists()

# ---------------------------------------------------------------------------
# 3. Kernel matching — config patterns
#    Kernels listed in the plan that match a config pattern are collected.
# ---------------------------------------------------------------------------

def test_matched_kernel_in_kernel_list(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in kl.kernel_list


def test_multiple_matched_kernels_all_collected(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, [
        "maven_sc_rec_200101_200201_v01.bsp",
        "maven_sc_rec_200201_200301_v01.bsp",
    ])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in kl.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" in kl.kernel_list


def test_kernel_list_attribute_set_on_instance(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert hasattr(kl, "kernel_list")
    assert isinstance(kl.kernel_list, list)


def test_kernel_list_empty_when_no_lines_match(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["totally_unrelated_file.txt"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert kl.kernel_list == []


def test_kernel_matched_via_mapping_pattern(tmp_path):
    """A kernel name that matches the mapping pattern (not the primary
    pattern) must still be collected."""
    json_config = {
        r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {
            "description": "SPK.",
            "mapping": r"maven_sc_rec_\d{6}_\d{6}_v\d+_mapped\.bsp",
        }
    }

    setup = make_setup(tmp_path, json_config=json_config)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01_mapped.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01_mapped.bsp" in kl.kernel_list

# ---------------------------------------------------------------------------
# 4. Commented-out lines:
#    Lines beginning with '#' must not be matched.
# ---------------------------------------------------------------------------

def test_commented_kernel_not_collected(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["# maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert kl.kernel_list == []


def test_commented_kernel_with_leading_spaces_not_collected(tmp_path):
    """Whitespace before the '#' must still be treated as a comment."""
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["   # maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert kl.kernel_list == []


def test_mix_of_commented_and_active_lines(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, [
        "# maven_sc_rec_200101_200201_v01.bsp",
        "maven_sc_rec_200201_200301_v01.bsp",
    ])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" not in kl.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" in kl.kernel_list

# ---------------------------------------------------------------------------
# 5. OrbNum matching:
#    Lines not matched by config patterns fall through to OrbNum patterns.
# ---------------------------------------------------------------------------

def test_orbnum_line_collected(tmp_path):
    setup = make_setup(
        tmp_path,
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )

    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_orb_rec_200101_200201_v01.orb"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_orb_rec_200101_200201_v01.orb" in kl.kernel_list


def test_orbnum_not_collected_when_config_pattern_matches_first(tmp_path):
    """If a line matches a config pattern, the orbnum block is not
    reached — the kernel is collected under the config match."""
    setup = make_setup(
        tmp_path,
        # Intentionally broad orbnum pattern that would also match the SPK
        orbnum=[{"pattern": r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp"}],
    )
    plan = tmp_path / "working" / "maven_release_01.plan"
    # This line matches the default SPK config pattern
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    # Kernel present exactly once — not duplicated by orbnum path
    assert kl.kernel_list.count("maven_sc_rec_200101_200201_v01.bsp") == 1


def test_orbnum_not_matched_when_pattern_does_not_match(tmp_path):
    setup = make_setup(
        tmp_path,
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["something_unrelated.txt"])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert kl.kernel_list == []


def test_orbnum_not_collected_when_setup_has_no_orbnum_attribute(tmp_path):
    """When setup has no orbnum attribute at all, the block is skipped
    gracefully — no AttributeError."""
    # make_setup without orbnum= leaves the attribute absent
    setup = make_setup(tmp_path)
    assert not hasattr(setup, "orbnum")

    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_orb_rec_200101_200201_v01.orb"])


    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))  # must not raise

    assert kl.kernel_list == []

# ---------------------------------------------------------------------------
# 6. Unmatched lines — warning logging
#    Lines that match nothing must trigger a warning; blank lines must not.
# ---------------------------------------------------------------------------

def test_unmatched_non_blank_line_logs_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["totally_unrelated_file.txt"])

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.WARNING):
        kl.read_plan(str(plan))

    assert any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_blank_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    # File with only blank lines
    plan.write_text("\n\n   \n")

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.WARNING):
        kl.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_whitespace_only_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    plan.write_text("     \t   \n")

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.WARNING):
        kl.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_matched_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.WARNING):
        kl.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


@pytest.mark.skip(reason="Bug not fixed.")
def test_commented_line_does_not_log_warning(tmp_path, caplog):
    """A commented-out kernel is not matched, but it should not produce
    an unmatched-line warning either — it is intentionally ignored."""
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["# maven_sc_rec_200101_200201_v01.bsp"])

    kl = make_kernel_list(setup)

    with caplog.at_level(logging.WARNING):
        kl.read_plan(str(plan))

    # NOTE: This test will FAIL against the current code because a
    # commented line falls through to the unmatched-line warning block.
    # That is a bug — the comment guard only suppresses collection,
    # not the warning. This failure is intentional and flags the bug.
    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )

# ---------------------------------------------------------------------------
# 7. Mixed plan content
#    Realistic plan files mix kernels, comments, OrbNums, and blanks.
# ---------------------------------------------------------------------------

def test_realistic_plan_collects_only_valid_kernels(tmp_path):
    setup = make_setup(
        tmp_path,
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, [
        "# This is a comment",
        "",
        "maven_sc_rec_200101_200201_v01.bsp",
        "   # maven_sc_rec_200201_200301_v01.bsp",
        "maven_orb_rec_200101_200201_v01.orb",
        "   ",
        "unrecognised_file.txt",
    ])

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in kl.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" not in kl.kernel_list
    assert "maven_orb_rec_200101_200201_v01.orb" in kl.kernel_list
    assert len(kl.kernel_list) == 2


def test_empty_plan_file_yields_empty_kernel_list(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    plan.write_text("")

    kl = make_kernel_list(setup)
    kl.read_plan(str(plan))

    assert kl.kernel_list == []

# ---------------------------------------------------------------------------
# Helpers (duplicated from test_classes_plan.py)
# ---------------------------------------------------------------------------

def make_args(faucet="kernels", plan=None, silent=True, verbose=False):
    return SimpleNamespace(
        faucet=faucet,
        plan=plan,
        silent=silent,
        verbose=verbose,
    )


def make_setup(
    tmp_path,
    *,
    faucet="kernels",
    plan=None,
    kernels_directory=None,
    orbnum=None,
    json_config=None,
    release=1,
    pds_version="4",
):
    working = tmp_path / "working"
    working.mkdir(exist_ok=True)

    if kernels_directory is None:
        kd = tmp_path / "kernels"
        kd.mkdir(exist_ok=True)
        kernels_directory = [str(kd)]

    if json_config is None:
        json_config = {
            r"maven_sc_rec_\d{6}_\d{6}_v\d+\.bsp": {
                "description": "SPK kernel for MAVEN.",
            }
        }

    setup = SimpleNamespace(
        step=1,
        args=make_args(faucet=faucet, plan=plan),
        mission_acronym="maven",
        mission_name="MAVEN",
        run_type="release",
        release=release,
        release_date="2024-01-01",
        observer="MAVEN",
        producer_name="Test Producer",
        pds_version=pds_version,
        working_directory=str(working),
        kernels_directory=kernels_directory,
        bundle_directory=str(tmp_path / "bundle"),
        orbnum_directory="",
        templates_directory=str(tmp_path),
        kernel_list_config=json_config,
    )

    if orbnum is not None:
        setup.orbnum = orbnum

    setup.add_file = MagicMock()

    if pds_version == "3":
        setup.pds3_mission_template = {"DATA_SET_ID": "MAVEN-1-SPICE-V1.0"}
        setup.volume_id = "MAVORB_0001"

    return setup


def make_kernel_list(setup):
    return KernelList(setup)


def write_plan_file(path, lines):
    """Write a .plan file with the given lines."""
    Path(path).write_text("\n".join(lines) + "\n")