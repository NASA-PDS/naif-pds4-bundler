"""Unit tests for the pds.naif_pds4_bundler.utils.time module."""
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

def test_dsk_coverage(lsk):
    """Test DSK coverage function using pytest."""
    dsk_file = str( KERNELS/ "dsk" / "DEIMOS_K005_THO_V01.BDS")

    start_time_cal, stop_time_cal = time.dsk_coverage(dsk_file)

    assert (start_time_cal, stop_time_cal) == (
        "1950-01-01T00:00:00.000Z",
        "2049-12-31T23:59:59.000Z"
    )


def test_spk_coverage(lsk, m2020_fk):
    """Test SPK coverage function."""
    spk_file = str( KERNELS/ "spk" / "m2020_surf_rover_loc_0000_0089_v1.bsp")
    [start_time_cal, stop_time_cal] = time.spk_coverage(spk_file, main_name="M2020")

    assert (start_time_cal, stop_time_cal) == (
        "2021-02-18T21:52:40.482Z",
        "2021-05-21T15:47:07.765Z"
    )


def test_parse_dates():
    """Test parse_dates function."""
    
    isoc_str = "2021-02-18T21:52:40"
    date_str  = "2021-FEB-18-21:52:40"

    isoc_date = time.parse_date(isoc_str)
    date = time.parse_date(date_str)

    assert isoc_date == date
