"""Unit tests for the configuration functions in utils/config.py."""
import pytest

from pds.naif_pds4_bundler.utils import get_mission_and_observer_and_target

# What the function returns when the mission defaults ('M', 'O' and 'T')
# are used for the three values.
DEFAULTS = (["M"], ["O"], ["T"])

# A pattern that configures the three values, and what it gives back.
FULL = {
    "@pattern": r"^full.*",
    "missions": {"mission_name": ["M1", "M2"]},
    "observers": {"observer": ["O1", "O2"]},
    "targets": {"target": ["T1", "T2"]},
}
FULL_RESULT = (["M1", "M2"], ["O1", "O2"], ["T1", "T2"])

# A pattern that configures nothing.
BARE = {"@pattern": r"^bare.*"}


def by_pattern(*entries):
    """Build a kernel list configuration, keyed by pattern."""
    return {entry["@pattern"]: entry for entry in entries}


@pytest.mark.parametrize("config, name, expected", [
    pytest.param(
        by_pattern(FULL), "full_001.bc", FULL_RESULT,
        id="match-configured"),
    # The configuration parser leaves a value that appears once in the
    # configuration as a bare string, not as a list.
    pytest.param(
        by_pattern({"@pattern": r"^one.*",
                    "missions": {"mission_name": "M1"},
                    "observers": {"observer": "O1"},
                    "targets": {"target": "T1"}}),
        "one_001.bc", ("M1", "O1", "T1"),
        id="match-single-values"),
    pytest.param(
        by_pattern(BARE), "bare_001.bc", DEFAULTS,
        id="match-not-configured"),
    pytest.param(
        by_pattern({"@pattern": r"^part.*", "targets": {"target": ["T1"]}}),
        "part_001.bc", (["M"], ["O"], ["T1"]),
        id="match-partly-configured"),
    pytest.param(
        by_pattern(FULL, BARE), "other_001.bc", DEFAULTS,
        id="no-match"),
    pytest.param(
        by_pattern(FULL, {"@pattern": r"^full_0.*",
                          "missions": {"mission_name": ["OTHER"]}}),
        "full_001.bc", FULL_RESULT,
        id="several-matches-first-wins"),
    pytest.param(
        by_pattern(BARE, FULL), "full_001.bc", FULL_RESULT,
        id="match-after-no-match"),
    # With no patterns the defaults are never applied. This is a known defect
    # that is fixed separately, so the test pins the result it has today.
    pytest.param(
        {}, "any_001.bc", ([], [], []),
        id="empty-configuration"),
])
def test_get_mission_and_observer_and_target(config, name, expected):
    """The first pattern matching the name gives the missions, observers and
    targets, and the mission defaults fill in what it does not configure.

    A name that matches no pattern gets the mission defaults. An empty
    configuration gets three empty lists.
    """
    # The mission defaults, short so they stand out in the results
    defaults = {"mission_name": "M", "observer": "O", "target": "T"}

    # Look the name up in the configuration
    result = get_mission_and_observer_and_target(config, name, **defaults)

    # The values come from the first matching pattern or, if it does not
    # configure them, from the defaults
    assert result == expected
