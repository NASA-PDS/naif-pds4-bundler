"""Unit tests for kernel list generation."""
import shutil

from pds.naif_pds4_bundler.__main__ import main


def test_mro_basic(self):
    """Basic test for MRO PDS3 data set."""
    config = "../config/mro.xml"
    plan = "../data/mro_release_59.plan"
    faucet = "bundle"

    shutil.copy2(
        "../data/mro_release_58.kernel_list",
        "working/mro_release_58.kernel_list"
    )

    shutil.copytree("../data/kernels", "kernels")
    shutil.rmtree("misc")
    shutil.copytree("../data/misc", "misc")
    shutil.copytree("../data/mro", "bundle")
    shutil.rmtree("staging")
    shutil.copytree("../data/mro", "staging")

    shutil.copy2(
        "../data/release_mro.cat",
        "staging/mrosp_1000/catalog/release.cat"
    )

    shutil.copy2(
        "../data/spiceds_mro.cat",
        "staging/mrosp_1000/catalog/spiceds.cat"
    )

    main(config, plan, faucet, log=True, silent=True)
