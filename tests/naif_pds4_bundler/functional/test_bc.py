"""Functional Test Family for the BepiColombo Archive Generation."""
import shutil

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils.files import string_in_file


def test_bc_multiple_obs_tar(self):
    """Test Archive with multiple Observers and Targets.

    This test is designed to test the implementation of multiple observers
    and targets in a SPICE Kernel Archive. BepiColombo has three observers and one
    target with kernels using different combinations.

    Test is successful if NPB is executed without errors and if the SPICE
    Kernel collection description is correct.
    """
    config = "../config/bc.xml"
    shutil.copytree("../data/kernels", "kernels")
    shutil.copy("../data/readme_bc.txt", "working/readme.txt")

    main(config, plan=False, faucet="bundle", silent=self.silent, log=self.log)

    line_checks = [
        "<description>This collection contains SPICE kernels for the MPO, MMO, "
        "and MTM spacecraft and their instruments.</description>",
    ]
    for line in line_checks:
        if not string_in_file(
            "bc/bc_spice/spice_kernels/collection_spice_kernels_v001.xml", line, 2
        ):
            raise BaseException
        

def test_bc_orbit_number_multiple_obs_tar(self):
    """Test Archive with multiple Observers and Targets.

    This test is designed to test the implementation of multiple observers
    and targets in a SPICE Kernel Archive. BepiColombo has three observers and one
    target with kernels using different combinations.

    Test is successful if NPB is executed without errors and if the SPICE
    Kernel collection description is correct.
    """
    config = "../config/bc.xml"
    shutil.copytree("../data/kernels", "kernels")
    shutil.copytree("../data/misc", "misc", dirs_exist_ok=True)
    shutil.copy("../data/readme_bc.txt", "working/readme.txt")

    main(config, plan=False, faucet="bundle", silent=self.silent, log=self.log)


    line_checks = [
        "<name>MPO</name>"
    ]
    for line in line_checks:
        if not string_in_file(
            "bc/bc_spice/miscellaneous/orbnum/bc_mpo_mlt_50037_20260314_20280529_v02.xml", line
        ):
            raise BaseException
        
    line_checks = [
        "<name>MMO</name>"
    ]
    for line in line_checks:
        if not string_in_file(
            "bc/bc_spice/miscellaneous/orbnum/bc_mmo_mlt_50038_20251220_20280305_v05.xml", line
        ):
            raise BaseException

