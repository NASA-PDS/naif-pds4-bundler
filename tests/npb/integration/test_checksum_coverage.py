"""Integration tests for the coverage times of the PDS4 checksum product.

The checksum takes its start and stop times from a few labels of the archive.
These tests run the real Setup and the real ChecksumProduct against real
label files, and only the bundle and its products are small stand-ins.
"""
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.product.product_checksum import (
    ChecksumProduct,
)
from pds.naif_pds4_bundler.classes.setup import Setup

# Times of the bundle label. They are wider than any other label on purpose,
# so the test fails if the checksum ever reads them.
WIDE_START = "1990-01-01T00:00:00Z"
WIDE_STOP = "2100-01-01T00:00:00Z"


def write_label(path: Path, start: str, stop: str) -> Path:
    """Write a label that only has the start and stop times.

    :param path: Path of the label, whose folders are created if needed.
    :param start: Value of the start date time.
    :param stop: Value of the stop date time.
    :return: The path of the label.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "<Time_Coordinates>\n"
        f"  <start_date_time>{start}</start_date_time>\n"
        f"  <stop_date_time>{stop}</stop_date_time>\n"
        "</Time_Coordinates>\n")
    return path


def build_checksum(setup: Setup, labels: list[Path]) -> ChecksumProduct:
    """Create a checksum product for a bundle whose products have ``labels``.

    The bundle also has a readme with a checksum and a bundle label whose
    times are wider than any other, as a real release does.

    :param setup: Real setup of the sandbox.
    :param labels: Labels of the products in the staging area.
    :return: The checksum product, not yet generated.
    """
    staging = Path(setup.staging_directory)
    (staging / "miscellaneous").mkdir(parents=True, exist_ok=True)
    bundle_label = write_label(staging / "readme.xml", WIDE_START, WIDE_STOP)

    # A product only needs a path and a label for the checksum to list them.
    # The checksum cuts the names at '/maven_spice/', so they are given with
    # forward slashes, whatever the platform.
    products = [SimpleNamespace(path=label.with_suffix(".bc").as_posix(),
                                label=SimpleNamespace(name=label.as_posix()))
                for label in labels]
    readme_label = SimpleNamespace(name=bundle_label.as_posix())
    bundle = SimpleNamespace(
        collections=[SimpleNamespace(product=products)],
        readme=SimpleNamespace(label=readme_label),
        checksum="e" * 32)
    collection = SimpleNamespace(name="miscellaneous", bundle=bundle)

    return ChecksumProduct(setup, collection)


def test_only_coverage_labels_set_the_times(real_setup: Setup) -> None:
    """Check that only some labels define the start and stop times.

    The times come from the labels of the spice_kernels collection inventory
    and from the orbnum labels: the earliest start and the latest stop of all
    of them. Other labels of the archive are ignored, even if their times are
    wider.
    """
    # Write the labels that define the coverage, the earliest start in one
    # of them and the latest stop in another, and two labels that do not.
    staging = Path(real_setup.staging_directory)
    labels = [
        write_label(staging / "spice_kernels/collection_spice_kernels_v001.xml",
                    "2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z"),
        write_label(staging / "spice_kernels/collection_spice_kernels_v002.xml",
                    "2013-12-01T00:00:00Z", "2016-06-01T00:00:00Z"),
        write_label(staging / "miscellaneous/orbnum/orbnum_01.xml",
                    "2014-06-01T00:00:00Z", "2017-02-01T00:00:00Z"),
        write_label(staging / "spice_kernels/ck/wide.xml",
                    WIDE_START, WIDE_STOP),
        write_label(staging / "document/collection_document_v001.xml",
                    WIDE_START, WIDE_STOP),
    ]
    checksum = build_checksum(real_setup, labels)

    # Work out the coverage.
    checksum.set_coverage()

    # The start is the earliest one and the stop is the latest one.
    assert checksum.start_time == "2013-12-01T00:00:00Z"
    assert checksum.stop_time == "2017-02-01T00:00:00Z"


def test_previous_checksum_entries_set_the_times(real_setup: Setup) -> None:
    """Check that the labels in the previous checksum count in an increment.

    A label that was released before and is listed in the previous checksum
    file is not in the staging area, but its times still count.
    """
    # Release a spice_kernels collection label and list it, with its own
    # label, in the previous checksum file.
    bundle = Path(real_setup.bundle_directory) / "maven_spice"
    write_label(bundle / "spice_kernels/collection_spice_kernels_v001.xml",
                "2013-11-20T00:00:00Z", "2014-03-01T00:00:00Z")
    previous = bundle / "miscellaneous/checksum/checksum_v001.tab"
    previous.parent.mkdir(parents=True)
    previous.write_text(
        f"{'a' * 32}  spice_kernels/collection_spice_kernels_v001.xml\n")
    previous.with_suffix(".xml").write_text("previous checksum label\n")
    real_setup.increment = True

    # Add a later label in the staging area and work out the coverage.
    staging = Path(real_setup.staging_directory)
    label = write_label(
        staging / "spice_kernels/collection_spice_kernels_v002.xml",
        "2014-03-01T00:00:00Z", "2015-01-01T00:00:00Z")
    checksum = build_checksum(real_setup, [label])
    checksum.set_coverage()

    # The start comes from the previous release and the stop from this one.
    assert checksum.start_time == "2013-11-20T00:00:00Z"
    assert checksum.stop_time == "2015-01-01T00:00:00Z"


def test_generate_keeps_the_times_of_set_coverage(real_setup: Setup) -> None:
    """Check that generating the checksum does not change its times.

    Generating also hashes the bundle label and the readme, which are not
    coverage products, so the start and stop stay as set_coverage() left
    them.
    """
    # Work out the coverage first, as the pipeline does.
    staging = Path(real_setup.staging_directory)
    label = write_label(
        staging / "spice_kernels/collection_spice_kernels_v001.xml",
        "2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z")
    checksum = build_checksum(real_setup, [label])
    checksum.set_coverage()
    times = ("2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z")
    assert (checksum.start_time, checksum.stop_time) == times

    # Write the checksum file.
    checksum.generate()

    # The times are the same, and not the ones of the bundle label.
    assert (checksum.start_time, checksum.stop_time) == times


def test_mission_times_are_used_without_coverage_labels(
        real_setup: Setup, caplog: pytest.LogCaptureFixture) -> None:
    """Check that the mission times are used when no label defines coverage.

    The start and stop of the mission become the ones of the checksum, and
    the log warns about it.
    """
    # Build a checksum whose only label does not define coverage.
    staging = Path(real_setup.staging_directory)
    label = write_label(staging / "spice_kernels/ck/wide.xml",
                        WIDE_START, WIDE_STOP)

    # Work out the coverage.
    with caplog.at_level(logging.WARNING):
        checksum = build_checksum(real_setup, [label])
        checksum.set_coverage()

    # Both times are the mission ones, with the warnings of today.
    assert checksum.start_time == real_setup.mission_start
    assert checksum.stop_time == real_setup.mission_finish
    assert [r.getMessage() for r in caplog.records] == [
        '-- Default to version 1.',
        '-- Make sure this is the first release of the archive.',
        '',
        '-- Start time set to mission start time: 2013-11-18T19:20:42Z',
        '-- Stop time set to mission finish time: 2050-01-01T00:00:00Z']


@pytest.mark.parametrize("release, labels, start, stop", [
    pytest.param(1, ["spice_kernels/collection_spice_kernels_v001.xml"],
                 "2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z",
                 id="first-release"),
    pytest.param(2, ["spice_kernels/collection_spice_kernels_v002.xml"],
                 "2015-01-01T00:00:00Z", "2016-01-01T00:00:00Z",
                 id="second-release"),
])
def test_history_checksum_uses_the_labels_of_its_release(
        real_setup: Setup, release: int, labels: list[str], start: str,
        stop: str) -> None:
    """Check the times of a checksum generated for a previous release.

    The checksum is generated from the files of that release, so its times
    come from the labels of that release and not from the ones of the
    current one.
    """
    # Release two collection labels, one per release, and one more in the
    # staging area for the current release.
    bundle = Path(real_setup.bundle_directory) / "maven_spice"
    write_label(bundle / "spice_kernels/collection_spice_kernels_v001.xml",
                "2014-01-01T00:00:00Z", "2015-01-01T00:00:00Z")
    write_label(bundle / "spice_kernels/collection_spice_kernels_v002.xml",
                "2015-01-01T00:00:00Z", "2016-01-01T00:00:00Z")
    staging = Path(real_setup.staging_directory)
    current = write_label(
        staging / "spice_kernels/collection_spice_kernels_v003.xml",
        "2016-01-01T00:00:00Z", "2017-01-01T00:00:00Z")
    checksum = build_checksum(real_setup, [current])

    # Generate the checksum of the release from its history.
    checksum.generate(history=(release, labels))

    # The times are the ones of the labels of that release.
    assert (checksum.start_time, checksum.stop_time) == (start, stop)
