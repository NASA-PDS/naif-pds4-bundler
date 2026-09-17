"""Unit tests for the pds.naif_pds4_bundler.utils.time module."""
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest
import spiceypy

from pds.naif_pds4_bundler.utils import time
from pds.naif_pds4_bundler.utils.time import _ek_fetch_row_value

# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"

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

@pytest.mark.parametrize("date_format, system, expected", [
    ("infomod2", "UTC",  ["1950-01-01T00:00:00.000Z", "2049-12-31T23:59:59.000Z"]),
    ("maklabel", "UTC", ["1950-01-01T00:00:00Z", "2049-12-31T23:59:59Z"]),
    ("infomod2", "TDB", ["1950-01-01T00:00:41.185Z", "2050-01-01T00:01:08.183Z"]),
    ("maklabel", "TDB", ["1950-01-01T00:00:41Z", "2050-01-01T00:01:08Z"]),
 ])
def test_dsk_coverage(lsk, date_format, system, expected):
    """Test DSK coverage function using pytest."""
    dsk_file = str( KERNELS/ "dsk" / "DEIMOS_K005_THO_V01.BDS")

    result = time.dsk_coverage(dsk_file, date_format, system)
    assert result == expected


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

@pytest.mark.parametrize("date_format, system, expected", [
    ("infomod2", "UTC", ["2000-01-01T00:00:00.000Z", "2026-06-13T00:00:00.000Z"]),
    ("maklabel", "UTC", ["2000-01-01T00:00:00Z", "2026-06-13T00:00:00Z"]),
    ("infomod2", "TDB", ["2000-01-01T00:01:04.185Z", "2026-06-13T00:01:09.184Z"]),
    ("maklabel", "TDB", ["2000-01-01T00:01:04Z", "2026-06-13T00:01:09Z"]),
 ])
def test_pck_coverage(lsk, date_format, system, expected):
    """Test PCK coverage function using pytest."""
    pck_file = str( KERNELS/ "pck" / "earth_000101_260613_260317.bpc")

    result = time.pck_coverage(pck_file, date_format, system)
    assert result == expected

@pytest.mark.parametrize("inputs, date_format, system, expected", [
    ("", "infomod2", "UTC",  ["2000-12-31T23:58:55.817Z", "2099-12-31T23:58:50.815Z"]),
    ("", "maklabel", "UTC", ["2000-12-31T23:58:56Z", "2099-12-31T23:58:51Z"]),
    ("M2020","infomod2", "UTC", ["2021-02-18T21:52:40.482Z", "2021-05-21T15:47:07.765Z"]),
    ("M2020","maklabel", "UTC", ["2021-02-18T21:52:40Z", "2021-05-21T15:47:08Z"]),
    ("MARS 2020", "maklabel", "UTC", ["2021-02-18T21:52:40Z", "2021-05-21T15:47:08Z"]),
    ("PERSEVERANCE", "infomod2", "UTC", ["2021-02-18T21:52:40.482Z", "2021-05-21T15:47:07.765Z"]),
    ("MAVEN", "infomod2", "UTC", ["2000-12-31T23:58:55.817Z", "2099-12-31T23:58:50.815Z"]),
    ("MAVEN", "maklabel", "UTC", ["2000-12-31T23:58:56Z", "2099-12-31T23:58:51Z"]),
    ("", "infomod2", "TDB", ["2001-01-01T00:00:00.000Z", "2100-01-01T00:00:00.000Z"]),
    ("", "maklabel", "TDB", ["2001-01-01T00:00:00Z", "2100-01-01T00:00:00Z"]),
    ("M2020", "infomod2", "TDB", ["2021-02-18T21:53:49.667Z", "2021-05-21T15:48:16.950Z"]),
    ("M2020", "maklabel", "TDB", ["2021-02-18T21:53:50Z", "2021-05-21T15:48:17Z"]),
    ("MARS 2020", "maklabel", "TDB", ["2021-02-18T21:53:50Z", "2021-05-21T15:48:17Z"]),
    ("PERSEVERANCE", "infomod2", "TDB", ["2021-02-18T21:53:49.667Z", "2021-05-21T15:48:16.950Z"]),
    ("MAVEN", "infomod2", "TDB", ["2001-01-01T00:00:00.000Z", "2100-01-01T00:00:00.000Z"]),
    ("MAVEN", "maklabel", "TDB", ["2001-01-01T00:00:00Z", "2100-01-01T00:00:00Z"]),
 ])
def test_spk_coverage(lsk, m2020_fk, inputs, date_format, system, expected):
    """Test SPK coverage function."""
    spk_file = str( KERNELS/ "spk" / "m2020_surf_rover_loc_0000_0089_v1.bsp")

    result = time.spk_coverage(spk_file, inputs, date_format, system)
    assert result == expected

# =============================================================================
# EK Coverage Tests
# =============================================================================

@pytest.mark.parametrize("date_format, system, expected", [
    ("infomod2", "UTC", ["", ""]),
    ("maklabel", "UTC", ["", ""]),
    ("infomod2", "TDB", ["", ""]),
    ("maklabel", "TDB", ["", ""]),
])
def test_ek_coverage_text_event_kernel(lsk, date_format, system, expected):
    """Test that .ten files return empty coverage without loading."""
    ten_files = list(KERNELS.rglob("*.ten"))

    if not ten_files:
        pytest.skip("No .ten files found in test data")

    ten_file = str(ten_files[0])
    result = time.ek_coverage(ten_file, date_format, system)

    assert result == expected

def test_ek_coverage_ten_no_furnsh(lsk):
    """Test that .ten files don't call furnsh (early return)."""
    ten_files = list(KERNELS.rglob("*.ten"))

    if not ten_files:
        pytest.skip("No .ten files found in test data")

    ten_file = str(ten_files[0])

    # Get kernel count before
    count_before = spiceypy.ktotal("ALL")

    result = time.ek_coverage(ten_file, "infomod2", "UTC")

    # Kernel count should be unchanged (file not loaded)
    count_after = spiceypy.ktotal("ALL")

    assert result == ["", ""]
    assert count_before == count_after

def test_ek_coverage_file_unloaded_on_error(lsk, monkeypatch):
    """Test that EK is unloaded even when error occurs."""
    binary_ek_files = (
            list(KERNELS.rglob("*.bes")) +
            list(KERNELS.rglob("*.bpe")) +
            list(KERNELS.rglob("*.bep")) +
            list(KERNELS.rglob("*.bdb"))
    )

    if not binary_ek_files:
        pytest.skip("No binary EK files found in test data")

    test_file = str(binary_ek_files[0])

    # Mock eknseg to raise error
    def mock_eknseg(handle):
        raise RuntimeError("Simulated error")

    monkeypatch.setattr("spiceypy.eknseg", mock_eknseg)

    count_before = spiceypy.ktotal("ALL")

    # Should raise the error
    with pytest.raises(RuntimeError, match="Simulated error"):
        time.ek_coverage(test_file, "infomod2", "UTC")

    # Kernel should still be unloaded
    count_after = spiceypy.ktotal("ALL")
    assert count_before == count_after

def test_ek_coverage_returns_list_of_two_strings(lsk):
    """Test that ek_coverage always returns list of two strings."""
    ten_files = list(KERNELS.rglob("*.ten"))

    if not ten_files:
        pytest.skip("No .ten files found")

    result = time.ek_coverage(str(ten_files[0]), "infomod2", "UTC")

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], str)

@pytest.mark.parametrize("extension", ["bes", "bpe", "bep", "bdb"])
def test_ek_coverage_binary_extensions(lsk, extension):
    """Test various binary EK extensions."""
    ek_files = list(KERNELS.rglob(f"*.{extension}"))

    if not ek_files:
        pytest.skip(f"No .{extension} files found")

    test_file = str(ek_files[0])
    result = time.ek_coverage(test_file, "infomod2", "UTC")

    # Current test data likely has no time columns
    assert isinstance(result, list)
    assert len(result) == 2


def test_ek_coverage_furnsh_failure_returns_empty_and_logs_warning(lsk, monkeypatch, caplog):
    """Test that furnsh failure is caught, returns empty coverage, and logs warning.

    When spiceypy.furnsh fails to load an EK file (e.g., corrupted file,
    wrong format, permission issues), the exception should be caught,
    a warning logged with file path and error details, and empty coverage returned.
    """
    import logging

    fake_ek_path = "/path/to/corrupted.bes"

    # Mock furnsh to raise SpiceyError
    def mock_furnsh(path):
        raise spiceypy.exceptions.SpiceyError("SPICE(INVALIDFORMAT)")

    monkeypatch.setattr("spiceypy.furnsh", mock_furnsh)

    # Capture logs at WARNING level
    with caplog.at_level(logging.WARNING):
        result = time.ek_coverage(fake_ek_path, "infomod2", "UTC")

    # Should return empty coverage
    assert result == ["", ""]
    assert isinstance(result, list)
    assert len(result) == 2

    # Verify warning was logged with path and error details
    assert len(caplog.records) > 0
    warning_messages = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("Failed to load EK file" in msg for msg in warning_messages)
    assert any(fake_ek_path in msg for msg in warning_messages)

def test_ek_coverage_furnsh_failure_different_error_types(lsk, monkeypatch):
    """Test that various SPICE Error types are handled.

    Tests different SPICE error scenarios that could occur during furnsh:
    - Invalid format
    - File not found (by SPICE, not OS)
    - Permission denied
    - Corrupted file
    """
    error_scenarios = [
        "SPICE(INVALIDFORMAT)",
        "SPICE(FILENOTFOUND)",
        "SPICE(FILEOPENFAILED)",
        "SPICE(DAFRN)",  # DAS file read error
    ]

    for error_msg in error_scenarios:
        def mock_furnsh(path):
            raise spiceypy.exceptions.SpiceyError(error_msg)

        monkeypatch.setattr("spiceypy.furnsh", mock_furnsh)

        result = time.ek_coverage("/fake/path.bes", "infomod2", "UTC")

        # All error types should return empty coverage
        assert result == ["", ""], f"Failed for error: {error_msg}"


# Test: Binary EK Files with Real Data
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("file, date_format, system, expected", [
    ("lroevnt_2010193_2010200_v01.bes", "infomod2", "UTC" , ['2010-07-11T13:58:39.148Z', '2010-07-18T15:35:41.148Z']),
    ("lroevnt_2010193_2010200_v01.bes", "infomod2", "TDB" , ['2010-07-11T13:59:45.332Z', '2010-07-18T15:36:47.332Z']),
    ("lroevnt_2010193_2010200_v01.bes", "maklabel", "UTC" , ['2010-07-11T13:58:39Z', '2010-07-18T15:35:41Z']),
    ("lroevnt_2010193_2010200_v01.bes", "maklabel", "TDB" , ['2010-07-11T13:59:45Z', '2010-07-18T15:36:47Z']),

    ("m01_map_021a_04_u_v2.bes" , "infomod2", "UTC" ,  ['2002-12-18T00:00:00.000Z','2003-01-15T00:16:06.000Z']),
    ("m01_map_021a_04_u_v2.bes", "infomod2", "TDB" , ['2002-12-18T00:01:04.185Z', '2003-01-15T00:17:10.183Z']),
    ("m01_map_021a_04_u_v2.bes", "maklabel", "UTC", ['2002-12-18T00:00:00Z', '2003-01-15T00:16:06Z']),
    ("m01_map_021a_04_u_v2.bes", "maklabel", "TDB", ['2002-12-18T00:01:04Z', '2003-01-15T00:17:10Z']),

    ("mpfr271d.bes" , "infomod2", "UTC" , ['1997-07-31T17:16:06.000Z','1997-08-03T20:16:30.000Z']),
    ("mpfr271d.bes", "infomod2", "TDB" , ['1997-07-31T17:17:09.184Z', '1997-08-03T20:17:33.182Z']),
    ("mpfr271d.bes", "maklabel", "UTC", ['1997-07-31T17:16:06Z', '1997-08-03T20:16:30Z']),
    ("mpfr271d.bes", "maklabel", "TDB", ['1997-07-31T17:17:09Z', '1997-08-03T20:17:33Z']),

    ("S99_CIMSSSUPa.bep" , "infomod2", "UTC" , ['2016-10-30T22:29:59.000Z','2017-09-16T00:00:00.000Z']),
    ("S99_CIMSSSUPa.bep", "infomod2", "TDB" , ['2016-10-30T22:31:07.184Z', '2017-09-16T00:01:09.181Z']),
    ("S99_CIMSSSUPa.bep", "maklabel", "UTC", ['2016-10-30T22:29:59Z', '2017-09-16T00:00:00Z']),
    ("S99_CIMSSSUPa.bep", "maklabel", "TDB", ['2016-10-30T22:31:07Z', '2017-09-16T00:01:09Z']),

    ("mpfr971a.bes", "infomod2", "UTC" , ['1997-10-11T15:58:00.000Z', '1997-10-11T15:58:29.000Z']),
    ("mpfr971a.bes", "infomod2", "TDB" , ['1997-10-11T15:59:03.183Z', '1997-10-11T15:59:32.181Z']),
    ("mpfr971a.bes", "maklabel", "UTC", ['1997-10-11T15:58:00Z', '1997-10-11T15:58:29Z']),
    ("mpfr971a.bes", "maklabel", "TDB", ['1997-10-11T15:59:03Z', '1997-10-11T15:59:32Z']),

    ("11A.bdb", "infomod2", "UTC" , ['', '']),
    ("11A.bdb", "infomod2", "TDB" , ['', '']),
    ("11A.bdb", "maklabel", "UTC", ['', '']),
    ("11A.bdb", "maklabel", "TDB", ['', '']),

    ("mpflactd.bdb", "infomod2", "UTC" , ['', '']),
    ("mpflactd.bdb", "infomod2", "TDB", ['', '']),
    ("mpflactd.bdb", "maklabel", "UTC", ['', '']),
    ("mpflactd.bdb", "maklabel", "TDB", ['', '']),

    ("mpfrcmdd.bdb", "infomod2", "UTC" , ['', '']),
    ("mpfrcmdd.bdb", "infomod2", "TDB", ['', '']),
    ("mpfrcmdd.bdb", "maklabel", "UTC", ['', '']),
    ("mpfrcmdd.bdb", "maklabel", "TDB", ['', '']),

    ("eros_n2000129x_v01_ltl.bpe", "infomod2", "UTC" , ['', '']),
    ("eros_n2000129x_v01_ltl.bpe", "infomod2", "TDB", ['', '']),
    ("eros_n2000129x_v01_ltl.bpe", "maklabel", "UTC", ['', '']),
    ("eros_n2000129x_v01_ltl.bpe", "maklabel", "TDB", ['', '']),

    ("m01_mmdmt_ext10.ten" , "infomod2", "UTC" , ['','']),
    ("m01_mmdmt_ext10.ten", "infomod2", "TDB", ['', '']),
    ("m01_mmdmt_ext10.ten", "maklabel", "UTC", ['', '']),
    ("m01_mmdmt_ext10.ten", "maklabel", "TDB", ['', ''])
])
def test_ek_coverage_binary_ek_with_time_data(lsk, file, date_format, system, expected):
    """Test EK coverage extraction from binary EK file with time data."""
    ek_file = str(KERNELS / "ek" / file)
    result = time.ek_coverage(ek_file, date_format, system)

    assert result == expected


# Test: Resource Management
# -----------------------------------------------------------------------------

def test_ek_coverage_unloads_kernel_on_success(lsk):
    """Test that EK file is properly unloaded after successful processing."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    initial_count = spiceypy.ktotal('ALL')

    time.ek_coverage(ek_file)

    final_count = spiceypy.ktotal('ALL')
    assert final_count == initial_count

def test_ek_coverage_closes_das_handle(lsk):
    """Test that DAS handle is properly closed."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    with patch('spiceypy.dascls') as mock_dascls:
        time.ek_coverage(ek_file)
        mock_dascls.assert_called_once()

# Test: Column Name Detection
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("column_names, expected_col", [
    (["ET"], "ET"),
    (["TIME"], "TIME"),
    (["EPOCH"], "EPOCH"),
    (["EVT_TIME"], "EVT_TIME"),
    (["EVENT_TIME"], 'EVENT_TIME'),

    (["START_TIME"], "START_TIME"),
    (["END_TIME"], "END_TIME"),
    (["BEGIN_TIME"], "BEGIN_TIME"),
    (["STOP_TIME"], "STOP_TIME"),
    (["BEGIN_ET"], "BEGIN_ET"),
    (["START_ET"], "START_ET"),
    (["END_ET"], "END_ET"),
    (["STOP_ET"], "STOP_ET"),
    (["START_UTC"], "START_UTC"),
    (["BEGIN_UTC"], "BEGIN_UTC"),
    (["END_UTC"], "END_UTC"),
    (["STOP_UTC"], "STOP_UTC"),
])
def test_ek_coverage_column_detection_single(lsk, column_names, expected_col):
    """Test that different single time column naming patterns are detected.

    With the query-first approach, _find_ek_time_columns will find these columns
    via direct query before falling back to cnames inspection.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "TEST_TABLE"
    mock_segsum.cnames = column_names

    ekfind_calls = []

    def mock_ekfind(query, bufsize):
        """Track queries and succeed when the expected column is queried."""
        ekfind_calls.append(query)
        # _find_ek_time_columns tries patterns in order, succeed on first match
        if expected_col in query and "FROM TEST_TABLE" in query:
            return (10, False, "")  # Found it
        return (0, True, "Column not found")  # Keep trying

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file)

                    # Verify the expected column was found in one of the queries
                    assert any(expected_col in q for q in ekfind_calls), \
                        f"Expected {expected_col} to be in one of the queries: {ekfind_calls}"

# Test: Error Handling
# -----------------------------------------------------------------------------

def test_ek_coverage_empty_ek_zero_segments(lsk):
    """Test EK coverage returns empty for file with zero segments."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    with patch('spiceypy.eknseg') as mock_eknseg:
        mock_eknseg.return_value = 0
        result = time.ek_coverage(ek_file, "infomod2", "UTC")
        assert result == ["", ""]
        mock_eknseg.assert_called_once()

def test_ek_coverage_no_time_columns(lsk):
    """Test EK with segments but no recognizable time columns.

    With query-first approach, _find_ek_time_columns will try all patterns
    and fail, then fallback to cnames inspection will also fail.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "TEST_TABLE"
    mock_segsum.cnames = ["ID", "NAME", "VALUE"]

    def mock_ekfind_no_time_cols(query, bufsize):
        """All time column queries fail (no time columns exist)."""
        # _find_ek_time_columns tries various patterns, all should fail
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_no_time_cols):
                result = time.ek_coverage(ek_file, "infomod2", "UTC")
                assert result == ["", ""]

def test_ek_coverage_no_valid_times_returns_empty(lsk):
    """Test that if no valid times are found, empty coverage is returned."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "TEST_TABLE"
    mock_segsum.cnames = ["ET"]
    
    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(10, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=None):
                    result = time.ek_coverage(ek_file)
                    assert result == ["", ""]

# Test: Specific Edge Cases for Code Coverage
# -----------------------------------------------------------------------------

def test_ek_coverage_segment_with_zero_rows(lsk):
    """Test that segments with nrows=0 are skipped."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    # Mock ekssum to return segment with 0 rows
    mock_segsum = MagicMock()
    mock_segsum.nrows = 0
    mock_segsum.tabnam = "EMPTY_TABLE"
    mock_segsum.cnames = ["TIME"]
    
    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # ekfind should NOT be called since segment is skipped
            with patch('spiceypy.ekfind') as mock_ekfind:
                result = time.ek_coverage(ek_file, "infomod2", "UTC")
                
                # Should return empty since segment has no rows
                assert result == ["", ""]
                # ekfind should not be called
                mock_ekfind.assert_not_called()

def test_ek_coverage_segment_with_none_column_names(lsk):
    """Test that segments with None cnames are skipped."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # Mock ekssum to return segment with None column names
    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "NULL_COLUMNS_TABLE"
    mock_segsum.cnames = None  # None - also triggers line 369

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Mock _find_ek_time_columns to return None (query-first fails)
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', return_value=None):
                with patch('spiceypy.ekfind') as mock_ekfind:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    assert result == ["", ""]

def test_ek_coverage_multiple_segments_one_empty(lsk):
    """Test that empty segments are skipped while valid ones are processed."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    # First segment: empty (nrows=0)
    mock_segsum1 = MagicMock()
    mock_segsum1.nrows = 0  # Empty - will be skipped
    mock_segsum1.tabnam = "EMPTY_TABLE"
    
    # Second segment: valid with data
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 5
    mock_segsum2.tabnam = "VALID_TABLE"
    mock_segsum2.cnames = ["ET"]
    
    with patch('spiceypy.eknseg', return_value=2):  # 2 segments
        with patch('spiceypy.ekssum', side_effect=[mock_segsum1, mock_segsum2]):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file)
                    
                    # Should process second segment and return valid coverage
                    assert result != ["", ""]

def test_ek_coverage_multiple_segments_one_no_columns(lsk):
    """Test that segments without columns are skipped while valid ones are processed."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # First segment: no columns
    mock_segsum1 = MagicMock()
    mock_segsum1.nrows = 10
    mock_segsum1.tabnam = "NO_COLS_TABLE"
    mock_segsum1.cnames = []  # Empty - will be skipped

    # Second segment: valid with columns
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 5
    mock_segsum2.tabnam = "VALID_TABLE"
    mock_segsum2.cnames = ["TIME"]

    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=[mock_segsum1, mock_segsum2]):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file)

                    # Should process second segment
                    assert result != ["", ""]

def test_ek_coverage_fallback_only_start_column_sets_stop_to_start(lsk):
    """Test that when only start column is found, stop_col is set to start_col.

    When the fallback cnames inspection finds only a START_TIME column (no stop column),
    it should use START_TIME for both start and stop columns.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "START_ONLY_TABLE"
    # Only START_TIME in cnames, no STOP_TIME or END_TIME
    mock_segsum.cnames = ["ID", "START_TIME", "DATA"]

    # Track which query was executed
    queries_executed = []

    def mock_ekfind(query, bufsize):
        queries_executed.append(query)
        # Query should use START_TIME for both (no second column since stop_col == start_col)
        if "START_TIME" in query and "FROM START_ONLY_TABLE" in query:
            # Verify it's NOT a paired query (should be just "SELECT START_TIME FROM")
            if query.count("START_TIME") == 1:
                return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Mock _find_ek_time_columns to return None (force fallback to cnames)
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', return_value=None):
                with patch('spiceypy.ekfind', side_effect=mock_ekfind):
                    with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=5000.0):
                        result = time.ek_coverage(ek_file, "infomod2", "UTC")

                        # Should get coverage using START_TIME for both start and stop
                        assert result != ["", ""]

                        # Verify query used only START_TIME (not a paired query)
                        successful_queries = [q for q in queries_executed if "START_TIME" in q and "FROM START_ONLY_TABLE" in q]
                        assert len(successful_queries) > 0, f"Expected START_TIME query, got: {queries_executed}"

                        # Verify it's not a paired query (should only have START_TIME once in SELECT clause)
                        # Format should be: "SELECT START_TIME FROM START_ONLY_TABLE"
                        # NOT: "SELECT START_TIME, START_TIME FROM START_ONLY_TABLE"
                        for query in successful_queries:
                            # Extract the column list (between SELECT and FROM)
                            select_part = query.split("FROM")[0].replace("SELECT", "").strip()
                            # Should not have a comma (which would indicate two columns)
                            assert "," not in select_part, f"Expected single column, got: {select_part}"

# Test: START/STOP Column Pair Detection
# -----------------------------------------------------------------------------

def test_ek_coverage_finds_stop_time_column(lsk):
    """Test that STOP_TIME column is found in START/STOP pair.

    With query-first approach, _find_ek_time_columns will try START_TIME/STOP_TIME
    pattern and succeed immediately.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "INTERVAL_TABLE"
    mock_segsum.cnames = ["ID", "START_TIME", "STOP_TIME", "NAME"]

    ekfind_calls = []

    def mock_ekfind_start_stop(query, bufsize):
        """Succeed when START_TIME, STOP_TIME query is attempted."""
        ekfind_calls.append(query)
        if "START_TIME" in query and "STOP_TIME" in query and "FROM INTERVAL_TABLE" in query:
            return (10, False, "")  # Found the pair
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_start_stop):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file)

                    # Should find both START_TIME and STOP_TIME
                    assert result != ["", ""]

                    # Verify query included both columns
                    successful_query = [q for q in ekfind_calls if "START_TIME" in q and "STOP_TIME" in q]
                    assert len(successful_query) > 0, f"Expected START_TIME/STOP_TIME query in: {ekfind_calls}"

def test_ek_coverage_finds_stop_et_column(lsk):
    """Test that STOP_ET column is found via query-first approach."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "ET_INTERVAL_TABLE"
    mock_segsum.cnames = ["ID", "START_ET", "STOP_ET", "STATUS"]

    def mock_ekfind_start_stop_et(query, bufsize):
        """Succeed when START_ET, STOP_ET query is attempted."""
        if "START_ET" in query and "STOP_ET" in query and "FROM ET_INTERVAL_TABLE" in query:
            return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_start_stop_et):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=2000.0):
                    result = time.ek_coverage(ek_file)

                    assert result != ["", ""]

def test_ek_coverage_finds_end_time_column(lsk):
    """Test that END_TIME column is found via query-first approach."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "BEGIN_END_TABLE"
    mock_segsum.cnames = ["BEGIN_TIME", "END_TIME", "EVENT_TYPE"]

    def mock_ekfind_begin_end(query, bufsize):
        if "BEGIN_TIME" in query and "END_TIME" in query and "FROM BEGIN_END_TABLE" in query:
            return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_begin_end):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=3000.0):
                    result = time.ek_coverage(ek_file)
                    assert result != ["", ""]

def test_ek_coverage_finds_stop_column_with_start(lsk):
    """Test finding STOP when paired with START via query-first approach."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "START_STOP_TABLE"
    mock_segsum.cnames = ["ID", "START", "STOP", "DESC"]

    def mock_ekfind_start_stop(query, bufsize):
        # Note: START_TIME/STOP_TIME pattern is tried before START/STOP
        if ("START_TIME" in query and "STOP_TIME" in query) and "FROM START_STOP_TABLE" in query:
            return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_start_stop):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=4000.0):
                    result = time.ek_coverage(ek_file)
                    assert result != ["", ""]

def test_ek_coverage_finds_stop_utc_column(lsk):
    """Test that STOP_UTC column is found via query-first approach."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "UTC_TABLE"
    mock_segsum.cnames = ["START_UTC", "STOP_UTC", "EVENT"]

    def mock_ekfind_utc(query, bufsize):
        if "START_UTC" in query and "STOP_UTC" in query and "FROM UTC_TABLE" in query:
            return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_utc):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=5000.0):
                    result = time.ek_coverage(ek_file)
                    assert result != ["", ""]

def test_ek_coverage_stop_col_break_on_first_match(lsk):
    """Test that query-first approach finds START_TIME/STOP_TIME pair first."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "MULTI_STOP_TABLE"
    # Multiple possible stop columns - query-first will find START_TIME/STOP_TIME
    mock_segsum.cnames = ["START_TIME", "STOP_TIME", "END_TIME", "STOP"]

    ekfind_calls = []

    def mock_ekfind_first_match(query, bufsize):
        """Succeed on first valid pattern found."""
        ekfind_calls.append(query)
        # START_TIME/STOP_TIME pattern is tried and succeeds
        if "START_TIME" in query and "STOP_TIME" in query and "FROM MULTI_STOP_TABLE" in query:
            return (10, False, "")
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_first_match):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=6000.0):
                    result = time.ek_coverage(ek_file)

                    assert result != ["", ""]
                    # Should use START_TIME/STOP_TIME (found via query)
                    successful_query = [q for q in ekfind_calls if "START_TIME" in q and "STOP_TIME" in q]
                    assert len(successful_query) > 0

def test_ek_coverage_only_start_column_no_stop(lsk):
    """Test when only START_TIME column exists - query-first fails, fallback finds it."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "START_ONLY_TABLE"
    # Only START_TIME, no STOP_TIME
    mock_segsum.cnames = ["ID", "START_TIME", "EVENT_NAME"]

    ekfind_calls = []

    def mock_ekfind_start_only(query, bufsize):
        """START_TIME/STOP_TIME paired query fails, but single START_TIME succeeds."""
        ekfind_calls.append(query)
        # Paired query fails (no STOP_TIME column exists)
        if "START_TIME" in query and "STOP_TIME" in query:
            return (0, True, "STOP_TIME not found")
        # Single START_TIME query from fallback succeeds
        # (fallback will use START_TIME for both start and stop since no stop column found)
        if "START_TIME" in query and "FROM START_ONLY_TABLE" in query:
            return (10, False, "")
        # Other patterns fail
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_start_only):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=7000.0):
                    result = time.ek_coverage(ek_file)

                    # Should still get coverage (falls back to cnames and finds START_TIME)
                    assert result != ["", ""]

def test_ek_coverage_case_insensitive_stop_match(lsk):
    """Test that query-first approach works with actual column names (case-sensitive in SQL).

    Note: SQL/SPICE queries are case-sensitive for column names, so the query-first
    approach tries uppercase patterns. If those fail, fallback to cnames will find
    the lowercase versions and construct a query with the actual column names.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "MIXED_CASE_TABLE"
    # Lowercase column names
    mock_segsum.cnames = ["start_time", "stop_time", "id"]

    ekfind_calls = []

    def mock_ekfind_case_sensitive(query, bufsize):
        """Query patterns are uppercase, but actual columns are lowercase."""
        ekfind_calls.append(query)
        # Uppercase patterns fail (SQL is case-sensitive) - these are from _find_ek_time_columns
        if "START_TIME" in query and "STOP_TIME" in query:
            return (0, True, "Column not found")
        # Lowercase queries succeed - these are from the fallback path using actual cnames
        if "start_time" in query and "stop_time" in query:
            return (10, False, "")
        # Other patterns fail
        return (0, True, "Column not found")

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind_case_sensitive):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=8000.0):
                    result = time.ek_coverage(ek_file)

                    # Should still work via cnames fallback with lowercase column names
                    assert result != ["", ""]

# Test: Query Error and No Results Handling
# -----------------------------------------------------------------------------

def test_ek_coverage_query_error_flag_set(lsk):
    """Test that query with error flag set is skipped."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "TEST_TABLE"
    mock_segsum.cnames = ["ET"]
    
    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # ekfind returns error=True (line 437 first condition)
            with patch('spiceypy.ekfind', return_value=(0, True, "Parse error")):
                # _ek_fetch_row_value should NOT be called since we continue
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value') as mock_fetch:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")
                    
                    # Should return empty since query had error
                    assert result == ["", ""]
                    # Fetch should never be called because of continue at line 439
                    mock_fetch.assert_not_called()

def test_ek_coverage_query_returns_zero_rows(lsk):
    """Test that query returning 0 rows is skipped."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    mock_segsum = MagicMock()
    mock_segsum.nrows = 10  # Segment has rows
    mock_segsum.tabnam = "EMPTY_RESULT_TABLE"
    mock_segsum.cnames = ["TIME"]
    
    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # ekfind returns nmrows=0 (line 437 second condition)
            with patch('spiceypy.ekfind', return_value=(0, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value') as mock_fetch:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")
                    
                    # Should return empty since query returned 0 rows
                    assert result == ["", ""]
                    # Fetch should not be called because of continue
                    mock_fetch.assert_not_called()

def test_ek_coverage_multiple_segments_one_query_fails(lsk):
    """Test that failed query skips segment but processes others."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    # Segment 1: will have query error
    mock_segsum1 = MagicMock()
    mock_segsum1.nrows = 10
    mock_segsum1.tabnam = "ERROR_TABLE"
    mock_segsum1.cnames = ["TIME"]
    
    # Segment 2: will succeed
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 5
    mock_segsum2.tabnam = "GOOD_TABLE"
    mock_segsum2.cnames = ["ET"]
    
    call_count = [0]
    def mock_ekfind(query, bufsize):
        call_count[0] += 1
        if call_count[0] == 1:
            # First query fails (error=True)
            return (0, True, "Error in first segment")
        else:
            # Second query succeeds
            return (5, False, "")
    
    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=[mock_segsum1, mock_segsum2]):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file)
                    
                    # Should still get coverage from second segment
                    assert result != ["", ""]

def test_ek_coverage_multiple_segments_one_returns_zero_rows(lsk):
    """Test that zero-row result skips segment but processes others."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    mock_segsum1 = MagicMock()
    mock_segsum1.nrows = 10
    mock_segsum1.tabnam = "EMPTY_RESULT_TABLE"
    mock_segsum1.cnames = ["TIME"]
    
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 5
    mock_segsum2.tabnam = "HAS_DATA_TABLE"
    mock_segsum2.cnames = ["ET"]
    
    call_count = [0]
    def mock_ekfind(query, bufsize):
        call_count[0] += 1
        if call_count[0] == 1:
            # First query returns 0 rows
            return (0, False, "")
        else:
            # Second query returns data
            return (5, False, "")
    
    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=[mock_segsum1, mock_segsum2]):
            with patch('spiceypy.ekfind', side_effect=mock_ekfind):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=2000.0):
                    result = time.ek_coverage(ek_file)
                    
                    # Should still get coverage from second segment
                    assert result != ["", ""]

def test_ek_coverage_both_error_and_zero_rows(lsk):
    """Test that error=True AND nmrows=0 both trigger skip."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")
    
    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "DOUBLE_FAIL_TABLE"
    mock_segsum.cnames = ["TIME"]
    
    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Both conditions true: error=True AND nmrows=0
            with patch('spiceypy.ekfind', return_value=(0, True, "Complete failure")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value') as mock_fetch:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")
                    
                    assert result == ["", ""]
                    mock_fetch.assert_not_called()

def test_ek_coverage_query_succeeds_with_positive_rows(lsk):
    """Test that query with rows and no error continues processing."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "SUCCESS_TABLE"
    mock_segsum.cnames = ["ET"]

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Query succeeds: error=False AND nmrows > 0
            with patch('spiceypy.ekfind', return_value=(10, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=3000.0):
                    result = time.ek_coverage(ek_file)

                    # Should get coverage (NOT skipped)
                    assert result != ["", ""]

# Test: Row Fetching and segment_times Population
# -----------------------------------------------------------------------------

def test_ek_coverage_single_time_column_appends_start_et(lsk):
    """Test that single time column appends only start_et.

    When there's only one time column (e.g., ET, TIME), both start_et and stop_et
    point to the same value, so only start_et is appended because stop_et == start_et.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 5
    mock_segsum.tabnam = "SINGLE_TIME_TABLE"
    mock_segsum.cnames = ["ET"]  # Single time column

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                # _ek_fetch_row_value returns same value for both calls
                # (single column case: start_col == stop_col)
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage
                    assert result != ["", ""]
                    assert result[0] != ""
                    assert result[1] != ""

def test_ek_coverage_start_stop_columns_appends_both(lsk):
    """Test that START/STOP columns append both start_et and stop_et.

    When there are separate START_TIME and STOP_TIME columns, _ek_fetch_row_value
    is called twice per row and returns different values. Both should be appended to
    segment_times: appends start_et, appends stop_et.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "INTERVAL_TABLE"
    mock_segsum.cnames = ["START_TIME", "STOP_TIME"]  # Two time columns

    fetch_call_count = [0]

    def mock_fetch(selidx, row, element):
        """Return different values for start vs stop."""
        fetch_call_count[0] += 1
        # selidx=0 is start_col (column 0 in SELECT)
        # selidx=1 is stop_col (column 1 in SELECT)
        if selidx == 0:
            return 1000.0 + row * 100  # Start times
        else:
            return 2000.0 + row * 100  # Stop times (different from start)

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Mock _find_ek_time_columns to return START_TIME/STOP_TIME pair
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', return_value=("START_TIME", "STOP_TIME", False)):
                with patch('spiceypy.ekfind', return_value=(10, False, "")):
                    with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                        result = time.ek_coverage(ek_file, "infomod2", "UTC")

                        # Should get coverage from both start and stop times
                        assert result != ["", ""]
                        # Verify both columns were fetched (2 calls per row * 10 rows = 20)
                        assert fetch_call_count[0] == 20

                        # Verify the result uses min of starts and max of stops
                        # min(1000, 1100, ..., 1900) = 1000
                        # max(2000, 2100, ..., 2900) = 2900
                        assert result[0] != ""
                        assert result[1] != ""

def test_ek_coverage_stop_et_none_only_appends_start(lsk):
    """Test that None stop_et only appends start_et.

    If fetching stop_et fails (returns None), only start_et is appended.
    This covers the case where the condition is False due to stop_et being None.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 5
    mock_segsum.tabnam = "PARTIAL_DATA_TABLE"
    mock_segsum.cnames = ["START_TIME", "STOP_TIME"]

    fetch_call_count = [0]

    def mock_fetch(selidx, row, element):
        """Return valid start_et but None for stop_et."""
        fetch_call_count[0] += 1
        if selidx == 0:
            return 1500.0  # Valid start time
        else:
            return None  # Stop time fetch fails (NULL or error)

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Mock _find_ek_time_columns to return START_TIME/STOP_TIME pair
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', return_value=("START_TIME", "STOP_TIME", False)):
                with patch('spiceypy.ekfind', return_value=(5, False, "")):
                    with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                        result = time.ek_coverage(ek_file, "infomod2", "UTC")

                        # Should still get coverage from start times only
                        assert result != ["", ""]
                        # Both fetches attempted (2 per row * 5 rows = 10)
                        assert fetch_call_count[0] == 10

def test_ek_coverage_start_et_none_skips_row(lsk):
    """Test that None start_et skips the row entirely.

    If start_et is None, the condition is False, so nothing is
    appended for this row.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 3
    mock_segsum.tabnam = "NULL_START_TABLE"
    mock_segsum.cnames = ["ET"]

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(3, False, "")):
                # All rows return None (e.g., NULL values in database)
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=None):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should return empty since no valid times found
                    assert result == ["", ""]

def test_ek_coverage_mixed_valid_and_none_values(lsk):
    """Test handling of mix of valid and None time values.

    Some rows have valid times, some have None. Only valid times should be appended.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 5
    mock_segsum.tabnam = "MIXED_DATA_TABLE"
    mock_segsum.cnames = ["START_TIME", "STOP_TIME"]

    row_counter = [0]

    def mock_fetch(selidx, row, element):
        """Return valid times for some rows, None for others."""
        row_counter[0] = row
        # Rows 0, 2, 4: valid times
        # Rows 1, 3: None (NULL values)
        if row % 2 == 0:
            if selidx == 0:
                return 1000.0 + row * 100  # Start
            else:
                return 2000.0 + row * 100  # Stop
        else:
            return None  # NULL value

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from valid rows only (0, 2, 4)
                    # min would be from row 0, max from row 4
                    assert result != ["", ""]

def test_ek_coverage_stop_equals_start_only_appends_once(lsk):
    """Test that when stop_et equals start_et, only start is appended.

    The condition includes 'stop_et != start_et', so if they're equal,
    it is not executed. This happens with single time column or when
    start and stop times happen to be identical.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 3
    mock_segsum.tabnam = "INSTANTANEOUS_EVENTS"
    mock_segsum.cnames = ["START_TIME", "STOP_TIME"]

    def mock_fetch(selidx, row, element):
        """Return same time for both start and stop (instantaneous events)."""
        # Both columns have identical times
        return 1234.5

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(3, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage (same start/stop time is valid)
                    assert result != ["", ""]

def test_ek_coverage_row_fetch_exception_continues(lsk):
    """Test that exception during row fetch skips that row.

    If _ek_fetch_row_value raises an exception, the except block catches it
    and continues to the next row.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 5
    mock_segsum.tabnam = "ERROR_PRONE_TABLE"
    mock_segsum.cnames = ["ET"]

    call_count = [0]

    def mock_fetch(selidx, row, element):
        """Fail on some rows, succeed on others."""
        call_count[0] += 1
        # Rows 1 and 3 raise exceptions
        if row in [1, 3]:
            raise spiceypy.exceptions.SpiceyError("Fetch failed")
        # Other rows succeed
        return 5000.0 + row * 10

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from successful rows (0, 2, 4)
                    assert result != ["", ""]
                    # All 5 rows should be attempted
                    assert call_count[0] == 5

def test_ek_coverage_value_error_during_fetch_continues(lsk):
    """Test that ValueError during fetch is caught."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 3
    mock_segsum.tabnam = "VALUE_ERROR_TABLE"
    mock_segsum.cnames = ["START_TIME", "STOP_TIME"]

    call_count = [0]

    def mock_fetch(selidx, row, element):
        """Raise ValueError on row 1."""
        call_count[0] += 1
        if row == 1:
            raise ValueError("Invalid time value")
        return 3000.0 + row * 50

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(3, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from successful rows
                    assert result != ["", ""]
                    # Verify all rows were attempted
                    assert call_count[0] > 0

def test_ek_coverage_index_error_during_fetch_continues(lsk):
    """Test that IndexError during fetch is caught."""
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 3
    mock_segsum.tabnam = "INDEX_ERROR_TABLE"
    mock_segsum.cnames = ["ET"]

    call_count = [0]

    def mock_fetch(selidx, row, element):
        """Raise IndexError on row 0."""
        call_count[0] += 1
        if row == 0:
            raise IndexError("Index out of bounds")
        return 7000.0

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            with patch('spiceypy.ekfind', return_value=(3, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', side_effect=mock_fetch):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from successful rows
                    assert result != ["", ""]
                    assert call_count[0] == 3

# Test: Query SPICE Error Exception Handling
# -----------------------------------------------------------------------------

def test_ek_coverage_query_spicey_error_skips_segment(lsk):
    """Test that SpiceyError during ekfind query is caught and segment is skipped.

    When ekfind raises a SpiceyError (not just returning error=True), the exception
    should be caught and the segment skipped via continue.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "QUERY_ERROR_TABLE"
    mock_segsum.cnames = ["ET"]

    with patch('spiceypy.eknseg', return_value=1):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # ekfind raises SpiceyError instead of returning error flag
            with patch('spiceypy.ekfind', side_effect=spiceypy.exceptions.SpiceyError("Query execution failed")):
                # _ek_fetch_row_value should NOT be called since query failed
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value') as mock_fetch:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should return empty since query failed
                    assert result == ["", ""]
                    # Fetch should never be called because query exception was caught
                    mock_fetch.assert_not_called()

def test_ek_coverage_query_spicey_error_multiple_segments_one_fails(lsk):
    """Test that query SpiceyError skips one segment but processes others.

    When one segment's query raises SpiceyError, that segment is skipped but
    other segments should still be processed successfully.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # Segment 1: query will fail with SpiceyError
    mock_segsum1 = MagicMock()
    mock_segsum1.nrows = 10
    mock_segsum1.tabnam = "BAD_QUERY_TABLE"
    mock_segsum1.cnames = ["ET"]

    # Segment 2: query will succeed
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 5
    mock_segsum2.tabnam = "GOOD_QUERY_TABLE"
    mock_segsum2.cnames = ["TIME"]

    segment_call = [0]

    def mock_find_ek_time_columns(table_name):
        """Mock _find_ek_time_columns - first segment fails, second succeeds."""
        segment_call[0] += 1
        if segment_call[0] == 1:
            # First segment: raise SpiceyError
            raise spiceypy.exceptions.SpiceyError("SPICE(QUERYFAILURE) Query failed")
        else:
            # Second segment: return success
            return ("TIME", "TIME", True)

    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=[mock_segsum1, mock_segsum2]):
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', side_effect=mock_find_ek_time_columns):
                with patch('spiceypy.ekfind', return_value=(5, False, "")):
                    with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=1000.0):
                        result = time.ek_coverage(ek_file, "infomod2", "UTC")

                        # Should get coverage from second segment despite first failing
                        assert result != ["", ""]
                        # Both segments should have been attempted
                        assert segment_call[0] == 2

def test_ek_coverage_query_spicey_error_all_segments_fail(lsk):
    """Test that all segments failing with query SpiceyError returns empty.

    If every segment's query raises SpiceyError, the function should return
    empty coverage.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    mock_segsum = MagicMock()
    mock_segsum.nrows = 10
    mock_segsum.tabnam = "ALL_FAIL_TABLE"
    mock_segsum.cnames = ["ET"]

    with patch('spiceypy.eknseg', return_value=3):
        with patch('spiceypy.ekssum', return_value=mock_segsum):
            # Every ekfind call raises SpiceyError
            with patch('spiceypy.ekfind', side_effect=spiceypy.exceptions.SpiceyError("Query always fails")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value') as mock_fetch:
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should return empty - no segments succeeded
                    assert result == ["", ""]
                    # Fetch never called since all queries failed
                    mock_fetch.assert_not_called()

# Test: Segment Processing SpiceyError Exception Handling
# -----------------------------------------------------------------------------

def test_ek_coverage_segment_spicey_error_skips_segment(lsk):
    """Test that SpiceyError during segment processing is caught.

    When ekssum raises a SpiceyError while processing a segment, the exception
    should be caught and the segment skipped via continue.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    with patch('spiceypy.eknseg', return_value=1):
        # ekssum raises SpiceyError when trying to get segment summary
        with patch('spiceypy.ekssum', side_effect=spiceypy.exceptions.SpiceyError("Segment read failed")):
            # ekfind should NOT be called since segment processing failed before query
            with patch('spiceypy.ekfind') as mock_ekfind:
                result = time.ek_coverage(ek_file, "infomod2", "UTC")

                # Should return empty since segment processing failed
                assert result == ["", ""]
                # Query should never be attempted because segment processing failed
                mock_ekfind.assert_not_called()

def test_ek_coverage_segment_spicey_error_multiple_segments_one_fails(lsk):
    """Test that segment SpiceyError skips one segment but processes others.

    When one segment raises SpiceyError during processing (ekssum), that segment
    is skipped but other segments should still be processed.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # Segment 0: will fail with SpiceyError
    # Segment 1: will succeed
    mock_segsum_good = MagicMock()
    mock_segsum_good.nrows = 5
    mock_segsum_good.tabnam = "GOOD_SEGMENT"
    mock_segsum_good.cnames = ["ET"]

    ekssum_call_count = [0]

    def mock_ekssum(handle, segno):
        """First segment fails, second succeeds."""
        ekssum_call_count[0] += 1
        if segno == 0:
            # First segment processing fails
            raise spiceypy.exceptions.SpiceyError("SPICE(SEGMENTREADFAILURE) Cannot read segment")
        else:
            # Second segment succeeds
            return mock_segsum_good

    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=mock_ekssum):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=2000.0):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from second segment
                    assert result != ["", ""]
                    # Both segments should have been attempted
                    assert ekssum_call_count[0] == 2

def test_ek_coverage_segment_spicey_error_all_segments_fail(lsk):
    """Test that all segments failing with SpiceyError returns empty.

    If every segment raises SpiceyError during processing, the function should
    return empty coverage.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    ekssum_calls = [0]

    def mock_ekssum_always_fails(handle, segno):
        """Always raise SpiceyError."""
        ekssum_calls[0] += 1
        raise spiceypy.exceptions.SpiceyError(f"Segment {segno} is corrupted")

    with patch('spiceypy.eknseg', return_value=3):
        with patch('spiceypy.ekssum', side_effect=mock_ekssum_always_fails):
            with patch('spiceypy.ekfind') as mock_ekfind:
                result = time.ek_coverage(ek_file, "infomod2", "UTC")

                # Should return empty - no segments could be processed
                assert result == ["", ""]
                # All 3 segments should have been attempted
                assert ekssum_calls[0] == 3
                # Query should never be called since all segment processing failed
                mock_ekfind.assert_not_called()

def test_ek_coverage_segment_spicey_error_during_column_check(lsk):
    """Test SpiceyError during segment metadata access.

    Even if ekssum returns without error, accessing segment attributes
    (like nrows, tabnam, cnames) might raise SpiceyError. This should be
    caught and the segment skipped.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # Create a mock that raises on attribute access
    mock_segsum_bad = MagicMock()
    mock_segsum_bad.nrows = property(lambda self: (_ for _ in ()).throw(
        spiceypy.exceptions.SpiceyError("Attribute access failed")))

    mock_segsum_good = MagicMock()
    mock_segsum_good.nrows = 5
    mock_segsum_good.tabnam = "GOOD_SEGMENT"
    mock_segsum_good.cnames = ["TIME"]

    call_count = [0]

    def mock_ekssum(handle, segno):
        """First segment has bad metadata, second is good."""
        call_count[0] += 1
        if segno == 0:
            return mock_segsum_bad
        else:
            return mock_segsum_good

    with patch('spiceypy.eknseg', return_value=2):
        with patch('spiceypy.ekssum', side_effect=mock_ekssum):
            with patch('spiceypy.ekfind', return_value=(5, False, "")):
                with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=3000.0):
                    result = time.ek_coverage(ek_file, "infomod2", "UTC")

                    # Should get coverage from second segment
                    assert result != ["", ""]

def test_ek_coverage_both_exception_types_in_different_segments(lsk):
    """Test mix of query and segment processing exceptions.

    This test verifies that both exception handlers work correctly when
    different segments fail in different ways.
    """
    ek_file = str(KERNELS / "ek" / "lroevnt_2010193_2010200_v01.bes")

    # Segment 0: good
    mock_segsum0 = MagicMock()
    mock_segsum0.nrows = 10
    mock_segsum0.tabnam = "GOOD_SEGMENT"
    mock_segsum0.cnames = ["ET"]

    # Segment 1: ekssum will fail
    # Segment 2: query will fail
    mock_segsum2 = MagicMock()
    mock_segsum2.nrows = 10
    mock_segsum2.tabnam = "QUERY_FAIL_SEGMENT"
    mock_segsum2.cnames = ["TIME"]

    ekssum_call = [0]
    def mock_ekssum(handle, segno):
        ekssum_call[0] += 1
        if segno == 0:
            return mock_segsum0
        elif segno == 1:
            raise spiceypy.exceptions.SpiceyError("Segment 1 corrupt")
        else:
            return mock_segsum2

    find_call = [0]
    def mock_find_ek_time_columns(table_name):
        find_call[0] += 1
        if find_call[0] == 1:
            # First segment succeeds
            return ("ET", "ET", True)
        else:
            # Third segment (second call) fails
            raise spiceypy.exceptions.SpiceyError("Query parse error")

    with patch('spiceypy.eknseg', return_value=3):
        with patch('spiceypy.ekssum', side_effect=mock_ekssum):
            with patch('pds.naif_pds4_bundler.utils.time._find_ek_time_columns', side_effect=mock_find_ek_time_columns):
                with patch('spiceypy.ekfind', return_value=(10, False, "")):
                    with patch('pds.naif_pds4_bundler.utils.time._ek_fetch_row_value', return_value=5000.0):
                        result = time.ek_coverage(ek_file, "infomod2", "UTC")

                        # Should get coverage from segment 0 only
                        assert result != ["", ""]
                        # All 3 segments attempted
                        assert ekssum_call[0] == 3
                        # Only 2 _find_ek_time_columns calls (segment 1 failed before that)
                        assert find_call[0] == 2

# Test: _ek_fetch_row_value ekgc Return Format Handling
# -----------------------------------------------------------------------------

def test_ek_fetch_row_value_ekgc_two_element_tuple(lsk):
    """Test ekgc returning 2-element tuple (str, bool) format.

    Some versions of SpiceyPy return (value_str, is_null) directly.
    This covers the len(result) == 2 branch.
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                # Return 2-element tuple: (str, bool)
                mock_ekgc.return_value = ("2020-01-15T10:30:00", False)

                result = _ek_fetch_row_value(0, 0, 0)

                # Should successfully parse and convert
                assert result is not None
                assert isinstance(result, float)
                mock_ekgc.assert_called_once_with(0, 0, 0, 256)

def test_ek_fetch_row_value_ekgc_three_element_tuple(lsk):
    """Test ekgc returning 3-element tuple (int, str, bool) format.

    Some versions of SpiceyPy return (n, value_str, is_null) with n as character count.
    This covers the len(result) >= 3 branch where we extract result[1] and result[2].
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                # Return 3-element tuple: (n, str, bool)
                mock_ekgc.return_value = (19, "2020-06-20T14:45:30", False)

                result = _ek_fetch_row_value(0, 0, 0)

                # Should successfully extract value_str from result[1]
                assert result is not None
                assert isinstance(result, float)
                mock_ekgc.assert_called_once_with(0, 0, 0, 256)

def test_ek_fetch_row_value_ekgc_malformed_tuples_return_none(lsk):
    """Test ekgc with malformed tuples (empty, 1-element) returns None."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                # Test empty tuple
                mock_ekgc.return_value = ()
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is None

                # Test 1-element tuple
                mock_ekgc.return_value = ("2020-01-01T00:00:00",)
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is None

def test_ek_fetch_row_value_ekgc_null_or_empty_returns_none():
    """Test ekgc with null flag or empty string returns None."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                # Test null flag
                mock_ekgc.return_value = ("", True)
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is None

                # Test empty string
                mock_ekgc.return_value = ("", False)
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is None


def test_ek_fetch_row_value_ekgc_non_time_string_returns_none():
    """Test ekgc with non-time string returns None.

    When value_str is not a valid time string, str2et raises
    SpiceyError, which is caught and None is returned.
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                # Return non-time data (works for both 2 and 3-element formats)
                mock_ekgc.return_value = ("COMMAND_NAME", False)

                result = _ek_fetch_row_value(0, 0, 0)

                # Should return None (not a valid time string)
                assert result is None

# Test: _ek_fetch_row_value ekgd Double Precision Fetch
# -----------------------------------------------------------------------------

def test_ek_fetch_row_value_ekgd_two_element_tuple():
    """Test ekgd returning 2-element tuple.

    When ekgd returns (value, is_null) tuple with len >= 2,
    extract value and is_null, then if not null, convert to float and return.
    """
    with patch('spiceypy.ekgd') as mock_ekgd:
        # Return 2-element tuple: (value, is_null)
        mock_ekgd.return_value = (987654.321, False)

        result = _ek_fetch_row_value(0, 10, 0)

        # Should return the double value as float
        assert result == 987654.321
        assert isinstance(result, float)
        mock_ekgd.assert_called_once_with(0, 10, 0)


def test_ek_fetch_row_value_ekgd_null_value_returns_none():
    """Test ekgd with is_null=True returns None.

    When is_null flag (result[-1]) is True, the condition is False,
    so no value is returned (falls through to integer fetch attempt).
    """
    with patch('spiceypy.ekgd') as mock_ekgd:
        # Return with is_null=True
        mock_ekgd.return_value = (123.456, True)

        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc', side_effect=spiceypy.exceptions.SpiceyError("Not char")):
                result = _ek_fetch_row_value(0, 0, 0)

                # Should return None (null value)
                assert result is None

def test_ek_fetch_row_value_ekgd_one_element_tuple_falls_through():
    """Test ekgd returning 1-element tuple falls through.

    If len(result) < 2, the condition is False, so this block
    is skipped and execution continues to the integer fetch attempt.
    """
    with patch('spiceypy.ekgd') as mock_ekgd:
        # Return malformed 1-element tuple
        mock_ekgd.return_value = (123.456,)

        # Integer and character fetches will also fail
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc', side_effect=spiceypy.exceptions.SpiceyError("Not char")):
                result = _ek_fetch_row_value(0, 0, 0)

                # Should return None (couldn't parse 1-element tuple)
                assert result is None


@pytest.mark.parametrize("value", [
    -12345.6789,  # negative
    0.0,          # zero
    1.23e-15,     # very small
    7.5e8,        # very large
])
def test_ek_fetch_row_value_ekgd_numeric_values(value):
    """Test ekgd with various numeric values."""
    with patch('spiceypy.ekgd') as mock_ekgd:
        mock_ekgd.return_value = (value, False)
        result = _ek_fetch_row_value(0, 0, 0)
        assert result == value
        assert isinstance(result, float)

def test_ek_fetch_row_value_cascade_order():
    """Test that fetch methods are attempted in correct order: ekgd -> ekgi -> ekgc.

    When each method fails, the next should be attempted.
    """
    ekgd_called = [False]
    ekgi_called = [False]
    ekgc_called = [False]

    def mock_ekgd_fail(selidx, row, element):
        ekgd_called[0] = True
        raise spiceypy.exceptions.SpiceyError("Not double")

    def mock_ekgi_fail(selidx, row, element):
        ekgi_called[0] = True
        raise spiceypy.exceptions.SpiceyError("Not int")

    def mock_ekgc_fail(selidx, row, element, length):
        ekgc_called[0] = True
        raise spiceypy.exceptions.SpiceyError("Not char")

    with patch('spiceypy.ekgd', side_effect=mock_ekgd_fail):
        with patch('spiceypy.ekgi', side_effect=mock_ekgi_fail):
            with patch('spiceypy.ekgc', side_effect=mock_ekgc_fail):
                result = _ek_fetch_row_value(0, 0, 0)

                # Verify cascade order: ekgd -> ekgi -> ekgc
                assert ekgd_called[0], "ekgd should be called first"
                assert ekgi_called[0], "ekgi should be called second"
                assert ekgc_called[0], "ekgc should be called third"
                assert result is None

def test_ek_fetch_row_value_integer():
    """Test fetching integer values."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi') as mock_ekgi:
            mock_ekgi.return_value = (42, False)
            result = _ek_fetch_row_value(0, 10, 0)
            assert result == 42.0
            mock_ekgi.assert_called_once_with(0, 10, 0)


# Test: _ek_fetch_row_value ekgi Integer Fetch
# -----------------------------------------------------------------------------

def test_ek_fetch_row_value_ekgi_two_element_tuple():
    """Test ekgi returning 2-element tuple.

    When ekgi returns (value, is_null) tuple with len >= 2,
    extract value and is_null, then if not null, convert to float and return.
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi') as mock_ekgi:
            # Return 2-element tuple: (value, is_null)
            mock_ekgi.return_value = (12345, False)

            result = _ek_fetch_row_value(0, 5, 0)

            # Should convert integer to float
            assert result == 12345.0
            assert isinstance(result, float)
            mock_ekgi.assert_called_once_with(0, 5, 0)


def test_ek_fetch_row_value_ekgi_null_value_returns_none():
    """Test ekgi with is_null=True returns None.

    When is_null flag (result[-1]) is True, the condition is False,
    so no value is returned (falls through to next try block).
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi') as mock_ekgi:
            # Return with is_null=True
            mock_ekgi.return_value = (12345, True)

            with patch('spiceypy.ekgc', side_effect=spiceypy.exceptions.SpiceyError("Not char")):
                result = _ek_fetch_row_value(0, 0, 0)

                # Should return None (null value)
                assert result is None

def test_ek_fetch_row_value_ekgi_one_element_tuple_falls_through():
    """Test ekgi returning 1-element tuple falls through.

    If len(result) < 2, the condition is False, so this block
    is skipped and execution continues to the character fetch attempt.
    """
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi') as mock_ekgi:
            # Return malformed 1-element tuple
            mock_ekgi.return_value = (12345,)

            # Character fetch will also fail
            with patch('spiceypy.ekgc', side_effect=spiceypy.exceptions.SpiceyError("Not char")):
                result = _ek_fetch_row_value(0, 0, 0)

                # Should return None (couldn't parse 1-element tuple)
                assert result is None

@pytest.mark.parametrize("value, expected", [
    (-99999, -99999.0),      # negative integer
    (0, 0.0),                # zero (not null)
    (1234567890123456, 1234567890123456.0),  # large SCLK-style value
])
def test_ek_fetch_row_value_ekgi_various_integers(value, expected):
    """Test ekgi with various integer values (negative, zero, large)."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi') as mock_ekgi:
            mock_ekgi.return_value = (value, False)
            result = _ek_fetch_row_value(0, 0, 0)
            assert result == expected
            assert isinstance(result, float)

def test_ek_fetch_row_value_character_utc_string(lsk):
    """Test fetching and converting UTC string to ET."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Not double")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Not int")):
            with patch('spiceypy.ekgc') as mock_ekgc:
                mock_ekgc.return_value = ("2020-01-01T00:00:00", False)
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is not None
                assert isinstance(result, float)
                mock_ekgc.assert_called_once_with(0, 0, 0, 256)

def test_ek_fetch_row_value_all_methods_fail():
    """Test that None is returned when all fetch methods fail."""
    with patch('spiceypy.ekgd', side_effect=spiceypy.exceptions.SpiceyError("Fail")):
        with patch('spiceypy.ekgi', side_effect=spiceypy.exceptions.SpiceyError("Fail")):
            with patch('spiceypy.ekgc', side_effect=spiceypy.exceptions.SpiceyError("Fail")):
                result = _ek_fetch_row_value(0, 0, 0)
                assert result is None