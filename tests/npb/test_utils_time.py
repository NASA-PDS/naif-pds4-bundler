"""Unit tests for the pds.naif_pds4_bundler.utils.time module."""
from datetime import datetime
from pathlib import Path

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

@pytest.fixture
def m2020_sclk():
    """Provides the M2020 SCLK Kernel."""
    kernel = str( KERNELS/ "sclk" / "m2020_168_sclkscet_refit_v03.tsc")
    spiceypy.furnsh(kernel)
    yield kernel
    spiceypy.unload(kernel)


@pytest.mark.parametrize("time_sys, input_format, end_sys, expected", [
    ("SCLK", "infomod2", "UTC" , ( 45445136693259.0 , 46149106045023.0 )),
    ("SCLK", "infomod2", "SCLK" , ( 45445136693259.0 , 46149106045023.0 )),
    ("TDB", "infomod2", "UTC" , ["2021-12-22T09:40:54.206Z", "2022-04-25T17:30:58.909Z"]),
    ("TDB", "infomod2", "TDB", ["2021-12-22T09:42:03.390Z", "2022-04-25T17:32:08.094Z"]),
    ("SCLK", "maklabel", "UTC" , ( 45445136693259.0 , 46149106045023.0 )),
    ("SCLK", "maklabel", "SCLK" , ( 45445136693259.0 , 46149106045023.0 )),
    ("TDB", "maklabel", "UTC" , ["2021-12-22T09:40:54.205Z", "2022-04-25T17:30:58.910Z"]),
    ("TDB", "maklabel", "TDB", ["2021-12-22T09:42:03.389Z", "2022-04-25T17:32:08.095Z"]),
])
def test_ck_coverage(lsk, m2020_sclk, time_sys, input_format , end_sys , expected ):
    """Test CK coverage function using pytest."""
    ck_file = str( KERNELS/ "ck" / "m2020_surf_rsm_tlmres_0299_0419_v1.big.bc")

    result = time.ck_coverage(ck_file, time_sys, input_format , end_sys)
    assert result == expected


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
    ("","2010-04-19T12:07:50.244000")
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


@pytest.mark.parametrize("input_format, beget, endet, kernel_type, system, expected", [
    ("maklabel", 829832539.429603, 829872732.429599, "text", "UTC", ["2026-04-19T01:01:10Z", "2026-04-19T12:11:03Z"]),
    ("maklabel", 829832539.429603, 829872732.429599, "CK", "TDB", ["2026-04-19T01:02:19.430Z", "2026-04-19T12:12:12.430Z"]),
    ("infomod2", 829832539.429603, 829872732.429599, "text", "UTC", ["2026-04-19T01:01:10.245Z", "2026-04-19T12:11:03.243Z"]),
])
def test_et_to_date(lsk, input_format, beget, endet, kernel_type, system, expected):
    """Test ET to date function using pytest."""

    result = time.et_to_date(beget, endet, input_format, kernel_type, system)
    assert result == expected


def test_et_to_date_date_format_error():
    """Test that ET to date function produces a ValueError if the date format is not
    supported."""
    with pytest.raises(ValueError, match="date_format argument is incorrect."):
        # NOTE: `beget` and `endet` are not relevant for this test.
        time.et_to_date(beget=0, endet=0, date_format="unknown")


@pytest.mark.parametrize("start_time, stop_time, expected", [
    ("2026-02-11T12:00:00", "2026-02-12T12:00:00", ["2026"]),
    ("2023-05-12T12:00:00", "2025-05-12T12:00:00", ["2023", "2024", "2025"]),
    ("2025-05-12T12:00:00", "2023-05-12T12:00:00", []),
])
def test_get_years(start_time, stop_time, expected):
    """Test get_years function using pytest."""
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


def test_parse_date_wrong_date_format():
    """Test that parse_date function produces a ValueError if the input time string
    does not conform to any of the supported formats."""
    with pytest.raises(ValueError, match="The input string does not conform to any "
                                         "of the supported formats."):
        time.parse_date("FEB-18-2025")


def test_pck_coverage(lsk):
    """Test PCK coverage function using pytest."""
    pck_file = str( KERNELS/ "pck" / "earth_000101_260613_260317.bpc")

    [start_time_cal, stop_time_cal] = time.pck_coverage(pck_file)

    assert (start_time_cal, stop_time_cal) == (
        "2000-01-01T00:00:00.000Z",
        "2026-06-13T00:00:00.000Z"
    )


@pytest.mark.parametrize("inputs, expected", [
    ("PRODUCT_CREATION_TIME        = 2026-03-10T11:08:04", "2026-03-10T11:08:04"),
    ("","N/A"),
 ])
def test_pds3_label_gen_date(mocker, inputs, expected):
    """Test pds3 label generation date function."""
    mock_file = mocker.mock_open(read_data=inputs)
    mocker.patch("builtins.open", mock_file)

    result = time.pds3_label_gen_date(inputs)
    assert result == expected


def test_spk_coverage(lsk, m2020_fk):
    """Test SPK coverage function."""
    spk_file = str( KERNELS/ "spk" / "m2020_surf_rover_loc_0000_0089_v1.bsp")
    [start_time_cal, stop_time_cal] = time.spk_coverage(spk_file, main_name="M2020")

    assert (start_time_cal, stop_time_cal) == (
        "2021-02-18T21:52:40.482Z",
        "2021-05-21T15:47:07.765Z"
    )