"""Private utility to slice INSIGHT data for the tests."""
from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels


def slice_em16_release_04():
    """Private utility to slice INSIGHT data for the tests."""
    kernels_dir = "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/" \
                  "data/regression/em16_spice/spice_kernels"
    lsk_file = "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/" \
                  "data/regression/em16_spice/spice_kernels/lsk/naif0012.tls"
    sclk_file = "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/" \
                  "data/regression/em16_spice/spice_kernels/sclk/em16_tgo_step_20220103.tsc"

    out_kernels_dir = f"spice_kernels_2016"
    start_time = f"2016 MAY 08 20:10:00"
    stop_time = f"2016 MAY 08 21:20:00"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

    out_kernels_dir = f"spice_kernels_2021"
    start_time = f"2021 MAY 08 20:10:00"
    stop_time = f"2021 MAY 08 21:20:00"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

    out_kernels_dir = f"spice_kernels_2019"
    start_time = f"2019 MAY 08 20:10:00"
    stop_time = f"2019 MAY 08 21:20:00"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

    out_kernels_dir = f"spice_kernels_2019"
    start_time = f"2019 NOV 12 20:10:00"
    stop_time = f"2019 NOV 12 21:20:00"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

    out_kernels_dir = f"spice_kernels_2021"
    start_time = f"2021 SEP 08 20:10:00"
    stop_time = f"2021 SEP 08 21:20:00"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

#    for yr in range(16, 21):
#
#        out_kernels_dir = f"spice_kernels_20{yr}"
#        start_time = f"20{yr} DEC 08 20:10:00"
#        stop_time = f"20{yr} DEC 08 21:20:00"
#
#        slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)


slice_em16_release_04()
