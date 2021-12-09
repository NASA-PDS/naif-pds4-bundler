"""Private utility to slice MRO data for the tests."""
from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels


def slice_insight_release_07():
    """Private utility to slice MRO data for the tests."""
    kernels_dir = "/pds4/insight_release_07/insight_spice/spice_kernels"
    out_kernels_dir = "spice_kernels_1"
    lsk_file = "../data/kernels/lsk/naif0012.tls"
    sclk_file = "../data/kernels/sclk/NSY_SCLKSCET.00019.tsc"
    start_time = "2019 NOV 07 02:00:00.000"
    stop_time = "2019 NOV 07 03:00:00.000"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time)
