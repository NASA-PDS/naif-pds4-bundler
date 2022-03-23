"""Private utility to slice INSIGHT data for the tests."""

lsk_file = "/Users/mcosta/ftp/pub/naif/MSL/kernels/lsk/naif0012.tls"
sclk_file = "/Users/mcosta/ftp/pub/naif/pds/data/msl-m-spice-6-v1.0/mslsp_1000/data/sclk/msl_76_sclkscet_refit_s4.tsc"
start_time = "2021-10-11T06:17:20.816"
stop_time = "2021-10-11T07:17:20.816"

def slice_msl_release_29_ck():
    """Private utility to slice MRO data for the tests."""
    from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels

    kernels_dir = "/Users/mcosta/ftp/pub/naif/MSL/kernels/ck"
    out_kernels_dir = "msl_ck"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)



def slice_msl_release_29_spk():
    """Private utility to slice MRO data for the tests."""
    from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels

    kernels_dir = "/Users/mcosta/ftp/pub/naif/pds/data/msl-m-spice-6-v1.0/mslsp_1000/data/spk"
    out_kernels_dir = "msl_spk"

    slice_kernels(kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time, timetype='UTC', log=True)


slice_msl_release_29_ck()
#slice_msl_release_29_spk()
