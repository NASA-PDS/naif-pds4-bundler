"""Unit tests for file permissions.

Products to archive must at least be readable by
the group that NPB belongs to.
"""
import os
import shutil

from pds.naif_pds4_bundler.__main__ import main


def post_setup(self):
    """Setup Test.

    This method will be executed before each test function.
    """
    dirs = ["kernels/fk", "kernels/lsk", "kernels/spk", "kernels/mk"]
    for dir in dirs:
        os.mkdir(dir)
    shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk/")
    shutil.copy2("../data/kernels/mk/m2020_v01.tm", "kernels/mk/")
    shutil.copy2("../data/kernels/mk/m2020_chronos_v01.tm", "kernels/mk/")


def test_binary_permissions(self):
    """Test permissions of binary files.

    For this test case we use the BIG-ENDIAN binary file.
    """
    post_setup(self)

    config = "../config/mars2020.xml"

    shutil.copy2(
        "../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.big.bsp",
        "kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp",
    )
    os.chmod("kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp", 330)

    with self.assertRaises(RuntimeError) as cm:
        main(config, silent=True, log=True, faucet="Bundle")
    if (
        "/naif_pds4_bundler/unittests/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp "
        "is not readable by the account that runs NPB. Update permissions."
        not in str(cm.exception)
    ):
        raise Exception("Test error.")
