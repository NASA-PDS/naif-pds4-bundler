"""Private utility to slice INSIGHT data for the tests."""
from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels


def slice_m2020_release_02():
    """Private utility to slice INSIGHT data for the tests."""
    kernels_dir = (
        "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler"
        "/data/regression/mars2020_spice/spice_kernels"
    )
    lsk_file = (
        "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler"
        "/data/regression/mars2020_spice/spice_kernels/lsk/naif0012.tls"
    )
    sclk_file = (
        "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler"
        "/data/regression/mars2020_spice/spice_kernels/sclk/m2020_168_sclkscet_refit_v02.tsc"
    )

    out_kernels_dir = "spice_kernels_cruise"
    start_time = "2021 FEB 08 20:10:00"
    stop_time = "2021 FEB 09 21:20:00"

    slice_kernels(
        kernels_dir,
        out_kernels_dir,
        lsk_file,
        sclk_file,
        start_time,
        stop_time,
        timetype="UTC",
        log=True,
    )

    out_kernels_dir = "spice_kernels_edl"
    start_time = "2021 FEB 18 20:27:45"
    stop_time = "2021 FEB 18 20:27:55"

    slice_kernels(
        kernels_dir,
        out_kernels_dir,
        lsk_file,
        sclk_file,
        start_time,
        stop_time,
        timetype="UTC",
        log=True,
    )

    out_kernels_dir = "spice_kernels_early_sols"
    start_time = "2021-MAY-10 14:00:00"
    stop_time = "2021-MAY-11 14:00:00"

    slice_kernels(
        kernels_dir,
        out_kernels_dir,
        lsk_file,
        sclk_file,
        start_time,
        stop_time,
        timetype="UTC",
        log=True,
    )

    out_kernels_dir = "spice_kernels_late_sols"
    start_time = "2021-JUL-30 15:05:00"
    stop_time = "2021-JUL-30 16:05:00"

    slice_kernels(
        kernels_dir,
        out_kernels_dir,
        lsk_file,
        sclk_file,
        start_time,
        stop_time,
        timetype="UTC",
        log=True,
    )


slice_m2020_release_02()
