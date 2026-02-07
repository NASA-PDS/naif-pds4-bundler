"""Unit tests for the time utilities."""
import spiceypy
from pds.naif_pds4_bundler.utils import dsk_coverage
from pds.naif_pds4_bundler.utils import spk_coverage
from pds.naif_pds4_bundler.utils.time import parse_date


def test_dsk_coverage(self):
    """Test DKS coverage function."""
    lsk_file = "../data/kernels/lsk/naif0012.tls"
    spiceypy.furnsh(lsk_file)
    dsk_file = "../data/kernels/dsk/DEIMOS_K005_THO_V01.BDS"

    [start_time_cal, stop_time_cal] = dsk_coverage(dsk_file)

    self.assertEqual(
        (start_time_cal, stop_time_cal),
        ("1950-01-01T00:00:00.000Z", "2049-12-31T23:59:59.000Z"),
    )


def test_spk_coverage(self):
    """Test SPK coverage function."""
    lsk_file = "../data/kernels/lsk/naif0012.tls"
    spiceypy.furnsh(lsk_file)

    spk_file = "../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp"
    spiceypy.furnsh("../data/kernels/fk/m2020_v04.tf")
    [start_time_cal, stop_time_cal] = spk_coverage(spk_file, main_name="M2020")

    self.assertEqual(
        (start_time_cal, stop_time_cal),
        ("2021-02-18T21:52:40.482Z", "2021-05-21T15:47:07.765Z"),
    )


def test_parse_dates(self):
    """Test parse_dates function."""
    
    isoc_str = "2021-02-18T21:52:40"
    date_str  = "2021-FEB-18-21:52:40"

    isoc_date = parse_date(isoc_str)
    date = parse_date(date_str)
    self.assertEqual(
        isoc_date, date
    )
