"""Unit tests for the pds.naif_pds4_bundler.utils.time module."""
from datetime import datetime
from pathlib import Path

import io
import pytest
import spiceypy

from pds.naif_pds4_bundler.utils import time


# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"

@pytest.fixture
def lsk():
    """Provides the standard LSK."""
    lsk_file = str(KERNELS / "lsk" / "naif0012.tls")
    spiceypy.furnsh(lsk_file)
    yield
    spiceypy.unload(lsk_file) # Cleanup after the test finishes

@pytest.fixture
def m2020_fk():
    """Provides the M2020 Frame Kernel."""
    kernel = str(KERNELS / "fk" / "m2020_v04.tf")
    spiceypy.furnsh(kernel)
    yield kernel
    spiceypy.unload(kernel)

@pytest.mark.parametrize("creation_format, expected", [
    ("maklabel", "2024-08-31T12:10:18"),
    ("infomod2", "2024-08-31T12:10:18.214Z"),
])
def test_creation_time(monkeypatch, creation_format, expected):
    """Test creation time function using pytest.
    Uses monkeypatch to make a fake creation_time to test expected output."""
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2024, 8, 31, 12, 10, 18, 214000)
    monkeypatch.setattr(time.datetime, "datetime", MockDatetime)

    result = time.creation_time(creation_format)
    assert result == expected


@pytest.mark.parametrize("date_input, expected", [
    ("2015-12-23T12:10:23", "December 23, 2015"),
    ("", "November 23, 2015"),
    ("2016-10-02T10:10:10", "October 2, 2016"),
])
def test_current_date(monkeypatch, date_input, expected):
    """Test current date function using pytest.
        Uses monkeypatch to make a fake current_date to test expected output."""
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2015, 11, 23, 12, 10, 18, 214000)
    monkeypatch.setattr(time.datetime, "datetime", MockDatetime)

    result = time.current_date(date_input)
    assert result == expected


@pytest.mark.parametrize("time_format, expected", [
    ("maklabel", "2010-04-19T12:07:50"),
    ("infomod2", "2010-04-19T12:07:50.244Z"),
])
def test_current_time(monkeypatch, time_format, expected):
    """Test current time function using pytest.
    Uses monkeypatch to make a fake current_time to test expected output."""
    class MockDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2010, 4, 19, 12, 7 , 50 , 244000)
    monkeypatch.setattr(time.datetime, "datetime", MockDatetime) #module, class, new class

    result = time.current_time(time_format)
    assert result == expected


def test_dsk_coverage(lsk):
    """Test DSK coverage function using pytest."""
    dsk_file = str( KERNELS/ "dsk" / "DEIMOS_K005_THO_V01.BDS")

    start_time_cal, stop_time_cal = time.dsk_coverage(dsk_file)

    assert (start_time_cal, stop_time_cal) == (
        "1950-01-01T00:00:00.000Z",
        "2049-12-31T23:59:59.000Z"
    )


@pytest.mark.parametrize("input_format, beget, endet, expected", [
    ("maklabel", "2461149.5432804353","2461150.0084750415", ["2026-04-19T01:01:10", "2026-04-19T12:11:03"]),
    ("infomod2", "2461149.5432804353", "2461150.0084750415", ["2026-04-19T01:01:10", "2026-04-19T12:11:03"]),
])
def test_et_to_date(monkeypatch, input_format, beget, endet, expected):
    lsk_file = str(KERNELS / "lsk" / "naif0012.tls") #not sure what to do with this


    def mock_timout(): #This seems incomplete - do I add the conversion step in this function?
        return datetime(2026, 4, 19, 1, 1, 10, 244000)

    monkeypatch.setattr(time.datetime, "datetime", mock_timout)

    #I know I need to do time conversion and feed it lsk but not sure how

    result = time.et_to_date(float(beget), float(endet), input_format)
    assert result == expected


@pytest.mark.parametrize("start_time, stop_time, expected", [
    ("2026-02-11T12:00:00", "2026-02-12T12:00:00", ["2026"]),
    ("2023-05-12T12:00:00", "2025-05-12T12:00:00", ["2023", "2024", "2025"]),
    ("2025-05-12T12:00:00", "2023-05-12T12:00:00", []),
])
def test_get_years(start_time, stop_time, expected):
    result = time.get_years(start_time, stop_time)
    assert result == expected


@pytest.mark.parametrize("date_input, expected", [
    ("2021-02-18T21:52:40", datetime(2021, 2, 18, 21, 52, 40)),
    ("2021-FEB-18-21:52:40", datetime(2021, 2, 18, 21, 52, 40)),
])
def test_parse_date(date_input, expected):
    """Test that different formats of date strings are parsed to the correct
    datetime object."""
    result = time.parse_date(date_input)

    assert isinstance(result, datetime)
    assert result == expected


@pytest.mark.parametrize("inputs, expected", [
    ("PRODUCT_CREATION_TIME        = 2026-03-10T11:08:04", "2026-03-10T11:08:04"),
 ])
def test_pds3_label_gen_date(monkeypatch, inputs, expected):
    inputs = "PRODUCT_CREATION_TIME        = 2026-03-10T11:08:04"

    def mock_open(*args, **kwargs):
        return io.StringIO(inputs)

    monkeypatch.setattr("builtins.open", mock_open)

    result = time.pds3_label_gen_date(str(inputs))
    assert result == expected


def test_spk_coverage(lsk, m2020_fk):
    """Test SPK coverage function."""
    spk_file = str( KERNELS/ "spk" / "m2020_surf_rover_loc_0000_0089_v1.bsp")
    [start_time_cal, stop_time_cal] = time.spk_coverage(spk_file, main_name="M2020")

    assert (start_time_cal, stop_time_cal) == (
        "2021-02-18T21:52:40.482Z",
        "2021-05-21T15:47:07.765Z"
    )