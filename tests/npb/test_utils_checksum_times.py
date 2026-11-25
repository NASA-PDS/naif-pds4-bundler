"""Unit tests for the pds.naif_pds4_bundler.utils.checksum_times module."""
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.utils import checksum_coverage

COLLECTION = "spice_kernels/collection_spice_kernels_v001.xml"
COLLECTION_2 = "spice_kernels/collection_spice_kernels_v002.xml"
MISSION = ("2000-01-01T00:00:00Z", "2050-01-01T00:00:00Z")
LABEL = ("2010-01-01T00:00:00Z", "2011-01-01T00:00:00Z")
OTHER = ("2012-01-01T00:00:00Z", "2013-01-01T00:00:00Z")


def times(start: str, stop: str) -> str:
    """Return the lines of a label that hold the start and stop times."""
    return (f"<start_date_time>{start}</start_date_time>\n"
            f"<stop_date_time>{stop}</stop_date_time>\n")


def write(path: Path, content: str) -> None:
    """Write a label, creating its folders if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture
def setup(tmp_path: Path) -> SimpleNamespace:
    """Provide the setup values the function needs."""
    return SimpleNamespace(
        bundle_directory=str(tmp_path / "bundle"),
        staging_directory=str(tmp_path / "staging"),
        mission_acronym="maven",
        mission_start=MISSION[0],
        mission_finish=MISSION[1])


@pytest.mark.parametrize("name, expected", [
    pytest.param(COLLECTION, LABEL, id="collection-label"),
    pytest.param("miscellaneous/orbnum/orbit.xml", LABEL, id="orbnum-label"),
    pytest.param("miscellaneous/orbnum/orbit.xml.bak", LABEL,
                 id="xml-anywhere-in-orbnum-name"),
    pytest.param("miscellaneous/orbnum/orbit.orb", MISSION, id="orbnum-table"),
    pytest.param("spice_kernels/collection_spice_kernels_inventory_v001.csv",
                 MISSION, id="collection-inventory"),
    pytest.param("spice_kernels/ck/kernel.xml", MISSION, id="kernel-label"),
    pytest.param("document/collection_document_v001.xml", MISSION,
                 id="other-collection"),
])
def test_only_coverage_labels_count(
        setup: SimpleNamespace, name: str, expected: tuple) -> None:
    """Check which file names provide the times."""
    write(Path(setup.staging_directory, name), times(*LABEL))

    result = checksum_coverage([name], setup, "checksum_v001.tab")

    assert result == expected


@pytest.mark.parametrize("labels, expected", [
    pytest.param({"bundle/maven_spice": LABEL, "staging": OTHER}, LABEL,
                 id="bundle-wins-over-staging"),
    pytest.param({"bundle/maven_spice": LABEL}, LABEL, id="only-in-bundle"),
    pytest.param({"staging": OTHER}, OTHER, id="only-in-staging"),
])
def test_label_lookup(setup: SimpleNamespace, tmp_path: Path, labels: dict,
                      expected: tuple) -> None:
    """Check where each label is read from."""
    for folder, label_times in labels.items():
        write(tmp_path / folder / COLLECTION, times(*label_times))

    result = checksum_coverage([COLLECTION], setup, "checksum_v001.tab")

    assert result == expected


def test_missing_label_is_logged_and_skipped(
        setup: SimpleNamespace, caplog: pytest.LogCaptureFixture) -> None:
    """Check a missing label is reported and the others are still read."""
    write(Path(setup.staging_directory, COLLECTION_2), times(*LABEL))

    result = checksum_coverage(
        [COLLECTION, COLLECTION_2], setup, "checksum_v001.tab")

    assert result == LABEL
    assert caplog.record_tuples == [(
        "root", logging.ERROR,
        "-- Product required to determine checksum_v001.tab coverage: "
        f"{COLLECTION} not found.")]


START_WARNING = f"-- Start time set to mission start time: {MISSION[0]}"
STOP_WARNING = f"-- Stop time set to mission finish time: {MISSION[1]}"


@pytest.mark.parametrize("content, expected, warnings", [
    pytest.param(f"<stop_date_time>{LABEL[1]}</stop_date_time>\n",
                 (MISSION[0], LABEL[1]), [START_WARNING], id="no-start"),
    pytest.param(f"<start_date_time>{LABEL[0]}</start_date_time>\n",
                 (LABEL[0], MISSION[1]), [STOP_WARNING], id="no-stop"),
    pytest.param("<Time_Coordinates/>\n", MISSION,
                 [START_WARNING, STOP_WARNING], id="no-times"),
])
def test_mission_times_are_the_fallback(
        setup: SimpleNamespace, caplog: pytest.LogCaptureFixture, content: str,
        expected: tuple, warnings: list) -> None:
    """Check the mission times replace the ones no label provides."""
    write(Path(setup.staging_directory, COLLECTION), content)

    result = checksum_coverage([COLLECTION], setup, "checksum_v001.tab")

    assert result == expected
    assert [(r.levelno, r.getMessage()) for r in caplog.records] == [
        (logging.WARNING, message) for message in warnings]


@pytest.mark.parametrize("first, second, expected", [
    pytest.param(times(*LABEL), times(*OTHER), (LABEL[0], OTHER[1]),
                 id="across-labels"),
    pytest.param(times(*OTHER) + times(*LABEL), "", (LABEL[0], OTHER[1]),
                 id="several-lines-in-one-label"),
    pytest.param(times(*LABEL).replace("\n", ""), "", LABEL,
                 id="both-tags-on-one-line"),
    # '.' sorts before 'Z', so the later time counts as the earlier one.
    pytest.param(times("2010-01-01T00:00:00Z", "2010-01-01T00:00:00Z"),
                 times("2010-01-01T00:00:00.500Z", "2010-01-01T00:00:00.500Z"),
                 ("2010-01-01T00:00:00.500Z", "2010-01-01T00:00:00Z"),
                 id="compared-as-strings"),
])
def test_earliest_start_and_latest_stop(
        setup: SimpleNamespace, first: str, second: str,
        expected: tuple) -> None:
    """Check which of all the times found are returned."""
    write(Path(setup.staging_directory, COLLECTION), first)
    write(Path(setup.staging_directory, COLLECTION_2), second)

    result = checksum_coverage(
        [COLLECTION, COLLECTION_2], setup, "checksum_v001.tab")

    assert result == expected


def test_missing_labels_are_reported_in_name_order(
        setup: SimpleNamespace, caplog: pytest.LogCaptureFixture) -> None:
    """Check the order of the errors does not depend on the input order."""
    checksum_coverage([COLLECTION_2, COLLECTION], setup, "checksum_v001.tab")

    errors = [r.args[1] for r in caplog.records if r.levelno == logging.ERROR]
    assert errors == [COLLECTION, COLLECTION_2]


def test_messages_are_logged_for_the_caller(
        setup: SimpleNamespace, caplog: pytest.LogCaptureFixture) -> None:
    """Check the log records name the function that asked for the times."""
    def calling_function() -> None:
        checksum_coverage([COLLECTION], setup, "checksum_v001.tab")

    calling_function()

    assert [r.funcName for r in caplog.records] == ["calling_function"] * 3
