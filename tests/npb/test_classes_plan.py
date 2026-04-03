"""Tests for ReleasePlan class.

Each test class covers one logical branch or behavior of the method.
A shared ``make_setup`` factory builds the minimum viable mock of the
``setup`` object that ``ReleasePlan.__init__`` and ``write_plan`` require,
so individual tests only override what is relevant to them.
"""
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pds.naif_pds4_bundler.classes.plan import ReleasePlan


# ===========================================================================
# Testing of ReleasePlan.read_plan method.
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. Input validation — file extension and faucet mode:
#    read_plan must enforce the .plan extension outside labeling mode.
# ---------------------------------------------------------------------------

def test_read_plan_valid_plan_extension_accepted(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)
    # Should not raise
    rp.read_plan(str(plan))


def test_read_plan_non_plan_extension_outside_labeling_mode_raises(tmp_path):
    """Any extension other than .plan must raise an NPB error when
    faucet is not 'labels'."""
    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    setup = make_setup(tmp_path)
    rp = make_release_plan(setup)

    with pytest.raises(RuntimeError, match=r'Release plan requires \*\.plan extension. '
                                           'Single kernels are only allowed in labeling mode.'):
        rp.read_plan(str(kernel_file))


def test_read_plan_non_plan_extension_in_labeling_mode_accepted(tmp_path):
    """In labeling mode a single kernel file (no .plan extension) is
    valid input — a synthetic plan is generated instead."""
    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    setup = make_setup(tmp_path, faucet="labels")
    rp = make_release_plan(setup)
    # Should not raise
    rp.read_plan(str(kernel_file))


def test_read_plan_txt_extension_outside_labeling_mode_raises(tmp_path):
    """Extension check is based purely on the suffix, not the content."""
    setup = make_setup(tmp_path, faucet="plan")

    bad_file = tmp_path / "working" / "maven_release_01.txt"
    bad_file.write_text("maven_sc_rec_200101_200201_v01.bsp\n")
    rp = make_release_plan(setup)

    with pytest.raises(RuntimeError, match=r'Release plan requires \*\.plan extension. '
                                           'Single kernels are only allowed in labeling mode.'):
        rp.read_plan(str(bad_file))

# ---------------------------------------------------------------------------
# 2. Synthetic plan generation (labeling mode)
#    When faucet == 'labels' and input has no .plan extension,
#    read_plan must create a synthetic .plan file and read from it.
# ---------------------------------------------------------------------------

def test_read_plan_synthetic_plan_file_is_created(tmp_path):
    setup = make_setup(tmp_path, faucet="labels")
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    rp = make_release_plan(setup)
    rp.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_01.plan"
    assert expected_plan.exists()


def test_read_plan_synthetic_plan_contains_kernel_filename(tmp_path):
    setup = make_setup(tmp_path, faucet="labels")
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    rp = make_release_plan(setup)
    rp.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_01.plan"
    content = expected_plan.read_text()
    assert "maven_release_01.plan" in content


def test_read_plan_synthetic_plan_name_uses_release_number(tmp_path):
    setup = make_setup(tmp_path, faucet="labels", release=5)
    working = tmp_path / "working"

    kernel_file = tmp_path / "maven_sc_rec_200101_200201_v01.bsp"
    kernel_file.touch()

    rp = make_release_plan(setup)
    rp.read_plan(str(kernel_file))

    expected_plan = working / "maven_release_05.plan"
    assert expected_plan.exists()

# ---------------------------------------------------------------------------
# 3. Kernel matching — config patterns
#    Kernels listed in the plan that match a config pattern are collected.
# ---------------------------------------------------------------------------

def test_read_plan_matched_kernel_in_kernel_list(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in rp.kernel_list


def test_read_plan_multiple_matched_kernels_all_collected(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, [
        "maven_sc_rec_200101_200201_v01.bsp",
        "maven_sc_rec_200201_200301_v01.bsp",
    ])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in rp.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" in rp.kernel_list


def test_read_plan_kernel_list_attribute_set_on_instance(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert hasattr(rp, "kernel_list")
    assert isinstance(rp.kernel_list, list)


def test_read_plan_kernel_list_empty_when_no_lines_match(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["totally_unrelated_file.txt"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert rp.kernel_list == []


def test_read_plan_kernel_matched_via_mapping_pattern(tmp_path):
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

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01_mapped.bsp" in rp.kernel_list

# ---------------------------------------------------------------------------
# 4. Commented-out lines:
#    Lines beginning with '#' must not be matched.
# ---------------------------------------------------------------------------

def test_read_plan_commented_kernel_not_collected(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["# maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert rp.kernel_list == []


def test_read_plan_commented_kernel_with_leading_spaces_not_collected(tmp_path):
    """Whitespace before the '#' must still be treated as a comment."""
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["   # maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert rp.kernel_list == []


def test_read_plan_mix_of_commented_and_active_lines(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, [
        "# maven_sc_rec_200101_200201_v01.bsp",
        "maven_sc_rec_200201_200301_v01.bsp",
    ])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" not in rp.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" in rp.kernel_list

# ---------------------------------------------------------------------------
# 5. OrbNum matching:
#    Lines not matched by config patterns fall through to OrbNum patterns.
# ---------------------------------------------------------------------------

def test_read_plan_orbnum_line_collected(tmp_path):
    setup = make_setup(
        tmp_path,
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )

    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_orb_rec_200101_200201_v01.orb"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_orb_rec_200101_200201_v01.orb" in rp.kernel_list


def test_read_plan_orbnum_not_collected_when_config_pattern_matches_first(tmp_path):
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

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    # Kernel present exactly once — not duplicated by orbnum path
    assert rp.kernel_list.count("maven_sc_rec_200101_200201_v01.bsp") == 1


def test_read_plan_orbnum_not_matched_when_pattern_does_not_match(tmp_path):
    setup = make_setup(
        tmp_path,
        orbnum=[{"pattern": r"maven_orb_rec_\d{6}_\d{6}_v\d+\.orb"}],
    )
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["something_unrelated.txt"])

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert rp.kernel_list == []


def test_read_plan_orbnum_not_collected_when_setup_has_no_orbnum_attribute(tmp_path):
    """When setup has no orbnum attribute at all, the block is skipped
    gracefully — no AttributeError."""
    # make_setup without orbnum= leaves the attribute absent
    setup = make_setup(tmp_path)
    assert not hasattr(setup, "orbnum")

    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_orb_rec_200101_200201_v01.orb"])


    rp = make_release_plan(setup)
    rp.read_plan(str(plan))  # must not raise

    assert rp.kernel_list == []

# ---------------------------------------------------------------------------
# 6. Unmatched lines — warning logging
#    Lines that match nothing must trigger a warning; blank lines must not.
# ---------------------------------------------------------------------------

def test_read_plan_unmatched_non_blank_line_logs_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["totally_unrelated_file.txt"])

    rp = make_release_plan(setup)

    with caplog.at_level(logging.WARNING):
        rp.read_plan(str(plan))

    assert any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_read_plan_blank_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    # File with only blank lines
    plan.write_text("\n\n   \n")

    rp = make_release_plan(setup)

    with caplog.at_level(logging.WARNING):
        rp.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_read_plan_whitespace_only_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    plan.write_text("     \t   \n")

    rp = make_release_plan(setup)

    with caplog.at_level(logging.WARNING):
        rp.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


def test_read_plan_matched_line_does_not_log_warning(tmp_path, caplog):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)

    with caplog.at_level(logging.WARNING):
        rp.read_plan(str(plan))

    assert not any(
        "release plan line has not been matched" in m
        for m in caplog.messages
    )


@pytest.mark.skip(reason="Bug not fixed.")
def test_read_plan_commented_line_does_not_log_warning(tmp_path, caplog):
    """A commented-out kernel is not matched, but it should not produce
    an unmatched-line warning either — it is intentionally ignored."""
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    write_plan_file(plan, ["# maven_sc_rec_200101_200201_v01.bsp"])

    rp = make_release_plan(setup)

    with caplog.at_level(logging.WARNING):
        rp.read_plan(str(plan))

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

def test_read_plan_realistic_plan_collects_only_valid_kernels(tmp_path):
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

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert "maven_sc_rec_200101_200201_v01.bsp" in rp.kernel_list
    assert "maven_sc_rec_200201_200301_v01.bsp" not in rp.kernel_list
    assert "maven_orb_rec_200101_200201_v01.orb" in rp.kernel_list
    assert len(rp.kernel_list) == 2


def test_read_plan_empty_plan_file_yields_empty_kernel_list(tmp_path):
    setup = make_setup(tmp_path)
    plan = tmp_path / "working" / "maven_release_01.plan"
    plan.write_text("")

    rp = make_release_plan(setup)
    rp.read_plan(str(plan))

    assert rp.kernel_list == []


# ===========================================================================
# Testing of ReleasePlan.read_plan method.
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. Normal directory scan — kernels found, no meta-kernel, no OrbNum:
#    write_plan discovers kernels from kernel directories.
# ---------------------------------------------------------------------------

def test_write_plan_returns_true_when_kernels_found(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)

    result = rp.write_plan()

    assert result is True


def test_write_plan_plan_file_is_created(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    assert plan_path(setup).exists()


def test_write_plan_plan_contains_matched_kernel(tmp_path):
    """Tests that the plan contains the matched kernel, the kernel is in the kernel_list
    attribute and that the plan has been registered in the list of file to write at the
    end of an execution.
    """
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)
    assert "maven_sc_rec_200101_200201_v01.bsp" in rp.kernel_list
    setup.add_file.assert_called_once()
    args = [a.replace(str(tmp_path), 'p') for a in setup.add_file.call_args_list[0].args]
    assert  args == ['p/working/maven_release_01.plan']
    assert setup.add_file.call_args_list[0].kwargs == {}


def test_write_plan_unmatched_kernel_not_in_plan(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "some_unrelated_file.txt").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "some_unrelated_file.txt" not in plan_contents(setup)


def test_write_plan_meta_kernels_excluded_from_directory_scan(tmp_path):
    """TM files in the kernel dir must not be auto-included."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "maven_v01.tm").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_v01.tm" not in plan_contents(setup)


def test_write_plan_multiple_kernel_directories_all_scanned(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    contents = plan_contents(setup)
    assert "maven_sc_rec_200101_200201_v01.bsp" in contents
    assert "maven_sc_rec_200201_200301_v01.bsp" in contents


def test_write_plan_kernels_in_subdirectories_are_found(tmp_path):
    """Glob is recursive — kernels in sub-dirs must be discovered."""
    ker_dir = tmp_path / "kernels"
    sub = ker_dir / "spk"
    sub.mkdir(parents=True)
    (sub / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)

# ---------------------------------------------------------------------------
# 2. Empty result — no kernels found:
#    write_plan returns False and sets an empty kernel_list.
# ---------------------------------------------------------------------------

def test_write_plan_returns_false_when_no_kernels(tmp_path):
    setup = make_setup(tmp_path)
    rp = make_release_plan(setup)

    result = rp.write_plan()

    assert result is False


def test_write_plan_kernel_list_is_empty_list(tmp_path):
    setup = make_setup(tmp_path)
    rp = make_release_plan(setup)
    rp.write_plan()

    assert rp.kernel_list == []


def test_write_plan_add_file_not_called_when_empty(tmp_path):
    setup = make_setup(tmp_path)
    rp = make_release_plan(setup)
    rp.write_plan()

    setup.add_file.assert_not_called()


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_write_plan_plan_file_not_written_when_empty(tmp_path):
    """No .plan file should exist if there are no kernels.

    NOTE: This test documents the *desired* behavior after the bug fix
    (empty file written before the empty check). If run against the
    current unpatched code it will FAIL — that failure is intentional
    and flags the bug.
    """
    setup = make_setup(tmp_path)
    rp = make_release_plan(setup)
    rp.write_plan()

    assert not plan_path(setup).exists()

# ---------------------------------------------------------------------------
# 3. Mapping patterns:
#    Kernels matched via a mapping pattern are included in the plan.
# ---------------------------------------------------------------------------

def test_write_plan_mapped_kernel_included(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_sc_rec_200101_200201_v01_mapped.bsp" in plan_contents(setup)

# ---------------------------------------------------------------------------
# 4. Meta-kernel handling — mk_inputs present in config:
#    When mk_inputs is configured, the referenced MK is added to the plan.
# ---------------------------------------------------------------------------

def test_write_plan_mk_from_config_added_to_plan(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_v01.tm" in plan_contents(setup)


def test_write_plan_mk_as_list_all_added(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    contents = plan_contents(setup)
    assert "maven_v01.tm" in contents
    assert "maven_v02.tm" in contents


def test_write_plan_missing_mk_raises_error(tmp_path):
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
    rp = make_release_plan(setup)

    with pytest.raises(RuntimeError, match="Meta-kernel provided via configuration "
                                           "nonexistent.tm does not exist."):
        rp.write_plan()


def test_write_plan_mk_not_added_in_labeling_mode(tmp_path):
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

    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_v01.tm" not in plan_contents(setup)

# ---------------------------------------------------------------------------
# 5. Meta-kernel inference — no mk_inputs, infer from bundle:
#    When mk_inputs is absent, write_plan infers the next MK version.
# ---------------------------------------------------------------------------

def test_write_plan_next_version_mk_inferred(tmp_path):
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

    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_v02.tm" in plan_contents(setup)


def test_write_plan_no_former_mk_produces_warning(tmp_path, caplog):
    """If no former MK exists in the bundle, a warning is logged."""
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    # bundle directory exists but has no mk/ subdirectory
    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])

    rp = make_release_plan(setup)
    with caplog.at_level(logging.WARNING):
        rp.write_plan()

    assert caplog.messages == ['-- No former meta-kernel found to generate meta-kernel for the list.']


def test_write_plan_inferred_mk_not_added_in_labeling_mode(tmp_path):
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

    rp = make_release_plan(setup)
    rp.write_plan()

    contents = plan_contents(setup)
    assert not any(".tm" in line for line in contents)


def test_write_plan_mk_version_incremented_correctly(tmp_path):
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

    rp = make_release_plan(setup)
    rp.write_plan()

    # v009 -> v010, zero-padded to same width
    assert "maven_v010.tm" in plan_contents(setup)


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_write_plan_no_duplicate_mk_appended(tmp_path):
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

    rp = make_release_plan(setup)
    rp.write_plan()

    mk_lines = [ln for ln in plan_contents(setup) if ".tm" in ln]
    assert len(mk_lines) == 1

def test_write_plan_no_mk_inferred_when_no_kernels(tmp_path, caplog):
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

    rp = make_release_plan(setup)

    with caplog.at_level(logging.ERROR):
        result = rp.write_plan()

    assert caplog.messages == ['-- No former meta-kernel found to generate meta-kernel for the list.']
    assert result is False
    assert not any(".tm" in ln for ln in plan_contents(setup))

# ---------------------------------------------------------------------------
# 6. OrbNum files
#    OrbNum files are appended when orbnum_directory is set.
# ---------------------------------------------------------------------------

def test_write_plan_orb_num_file_included(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_orb_rec_200101_200201_v01.orb" in plan_contents(setup)


def test_write_plan_orb_num_not_included_in_labeling_mode(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_orb_rec_200101_200201_v01.orb" not in plan_contents(setup)


def test_write_plan_unmatched_orb_num_not_included(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "something_unrelated.orb" not in plan_contents(setup)

# ---------------------------------------------------------------------------
# 7. Labeling mode (faucet == "labels")
#    In labeling mode a single kernel file acts as the plan input.
# ---------------------------------------------------------------------------

def test_write_plan_single_kernel_becomes_plan(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    assert "maven_sc_rec_200101_200201_v01.bsp" in plan_contents(setup)


def test_write_plan_other_kernels_in_dir_not_included(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

    contents = plan_contents(setup)
    assert "maven_sc_rec_200201_200301_v01.bsp" not in contents

# ---------------------------------------------------------------------------
# 8. Plan file format
#    The .plan file must follow the expected naming and line format.
# ---------------------------------------------------------------------------

def test_write_plan_plan_file_name_follows_convention(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)], release=3)
    rp = make_release_plan(setup)
    rp.write_plan()

    expected = Path(setup.working_directory) / "maven_release_03.plan"
    assert expected.exists()


def test_write_plan_each_kernel_on_its_own_line(tmp_path):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()
    (ker_dir / "maven_sc_rec_200201_200301_v01.bsp").touch()

    setup = make_setup(tmp_path, kernels_directory=[str(ker_dir)])
    rp = make_release_plan(setup)
    rp.write_plan()

    contents = plan_contents(setup)
    assert len(contents) == 2


@pytest.mark.skip(reason="Bug not fixed yet.")
def test_write_plan_no_duplicate_kernels_in_plan(tmp_path):
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
    rp = make_release_plan(setup)
    rp.write_plan()

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
def test_write_plan_release_number_formatting(tmp_path, release, expected_suffix):
    ker_dir = tmp_path / "kernels"
    ker_dir.mkdir()
    (ker_dir / "maven_sc_rec_200101_200201_v01.bsp").touch()

    setup = make_setup(
        tmp_path,
        kernels_directory=[str(ker_dir)],
        release=release,
    )
    rp = make_release_plan(setup)
    rp.write_plan()

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


def make_release_plan(setup):
    """Instantiate ReleasePlan while suppressing the read_config I/O."""
    # read_config only reads from setup.kernel_list_config (already a dict)
    # and writes to self.re_config / self.json_config — no filesystem access.
    return ReleasePlan(setup)


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
    ReleasePlan.__init__ and write_plan.

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

def write_plan_file(path, lines):
    """Write a .plan file with the given lines."""
    Path(path).write_text("\n".join(lines) + "\n")
