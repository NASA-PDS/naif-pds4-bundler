"""Private utility to slice INSIGHT data for the tests."""


def slice_mro_release_59_ck():
    """Private utility to slice MRO data for the tests."""
    from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels

    kernels_dir = (
        "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/ck"
    )
    out_kernels_dir = "spice_kernels_3"
    lsk_file = "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/lsk/naif0012.tls"
    sclk_file = "/Users/mcosta/mro_transfer/data/sclk/mro_sclkscet_00099_65536.tsc"
    start_time = "2021 JUL 06 04:00:00.000"
    stop_time = "2021 JUL 06 04:10:00.000"

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


def slice_mro_release_59_spk():
    """Private utility to slice MRO data for the tests."""
    from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels

    kernels_dir = (
        "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/spk"
    )
    out_kernels_dir = "spice_kernels_3"
    lsk_file = "/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/data/kernels/lsk/naif0012.tls"
    sclk_file = "/Users/mcosta/mro_transfer/data/sclk/mro_sclkscet_00099_65536.tsc"
    start_time = "2021 JUL 06 04:00:00.000"
    stop_time = "2021 JUL 06 04:10:00.000"

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


slice_mro_release_59_spk()
