"""Private utility to slice INSIGHT data for the tests."""
from pds.naif_pds4_bundler.utils import slice_kernels


kernels_dir = "/Users/mcosta/workspace/pds/npb_workspace/mars2020_area/" \
              "mars2020/mars2020_spice/spice_kernels"
out_kernels_dir = "spice_kernels_cruise"
lsk_file = "../data/kernels/lsk/naif0012.tls"
sclk_file = "/Users/mcosta/workspace/pds/npb_workspace/mars2020_area/" \
            "mars2020/mars2020_spice/spice_kernels/sclk/" \
            "m2020_168_sclkscet_refit_v02.tsc"

out_kernels_dir = "spice_kernels_cruise"
start_time = "2021 FEB 08 20:10:00"
stop_time = "2021 FEB 09 21:20:00"

slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC',log=True)

out_kernels_dir = "spice_kernels_edl"
start_time = "2021 FEB 18 20:10:00"
stop_time = "2021 FEB 18 21:20:00"

slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC',log=True)

out_kernels_dir = "spice_kernels_early_sols"
start_time = "2021-MAY-10 14:00:00"
stop_time = "2021-MAY-11 14:00:00"

slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)

out_kernels_dir = "spice_kernels_late_sols"
start_time = "2021-JUL-20 15:05:00"
stop_time = "2021-JUL-21 15:05:00"

slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)
