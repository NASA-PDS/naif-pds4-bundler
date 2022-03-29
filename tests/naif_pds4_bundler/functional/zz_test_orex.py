"""Functional Test Family for OSIRIS-REx Archive Generation."""
import shutil

from pds.naif_pds4_bundler.__main__ import main


def test_orex_mks(self):
    """Test development in progress.

    Test case to debug:
    INFO    : Step 6 - Generation of meta-kernel(s)
    INFO    : -------------------------------------
    INFO    :
    INFO    : -- Copy meta-kernel: bundle/spice_kernels/mk/orx_2016_v09.tm
    ERROR   : -- Missmatch of values in meta-kernel pattern.
    WARNING : -- orx_2016_v09.tm No vid explicit in kernel name: set to 1.0
    """
    config = "../config/orex.xml"
    faucet = "staging"
    shutil.copytree("../data/kernels", "kernels")

    main(
        config,
        faucet=faucet,
        silent=self.silent,
        verbose=self.verbose,
        log=self.log,
    )
