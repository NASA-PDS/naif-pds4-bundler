"""Unit tests for kernel list generation."""
import glob
import shutil
import sys

from pds.naif_pds4_bundler.__main__ import main


def post_setup(self):
    """Setup Test.

    This method will be executed before each test function.
    """
    if sys.byteorder == "little":
        updated_config = 'working/mro.xml'
        with open(self.config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spice_name>MRO</spice_name>" in line:
                        n.write(line)
                        n.write("<binary_endianness>LTL-IEEE</binary_endianness>\n")
                    else:
                        n.write(line)
    else:
        kernels = glob.glob("kernels/**/*.*")
        for kernel in kernels:
            if ".big." in kernel:
                shutil.move(kernel, kernel.split('.')[0] + '.' + kernel.split('.')[-1])

        updated_config = self.config

    self.config = updated_config


def test_mro_basic(self):
    """Basic test for MRO PDS3 data set."""
    self.config = "../config/mro.xml"
    plan = "../data/mro_release_59.plan"
    faucet = "bundle"

    shutil.copy2(
        "../data/mro_release_58.kernel_list",
        "working/mro_release_58.kernel_list"
    )

    shutil.copytree("../data/kernels", "kernels")
    shutil.move("misc", "misc_old")
    shutil.copytree("../data/misc", "misc")
    shutil.copytree("../data/mro", "bundle")
    shutil.move("staging", "staging_old")
    shutil.copytree("../data/mro", "staging")

    shutil.copy2(
        "../data/release_mro.cat",
        "staging/mrosp_1000/catalog/release.cat"
    )

    shutil.copy2(
        "../data/spiceds_mro.cat",
        "staging/mrosp_1000/catalog/spiceds.cat"
    )

    post_setup(self)

    main(self.config, plan, faucet, log=True, silent=True)
