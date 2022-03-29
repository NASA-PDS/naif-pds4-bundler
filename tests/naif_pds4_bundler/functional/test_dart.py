"""Functional Test Family for DART Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


def test_dart_multiple_obs_tar(self):
    """Test Archive with multiple Observers and Targets.

    This test is designed to test the implementation of multiple observers
    and targets in a SPICE Kernel Archive. DART has two observers and two
    targets with kernels using different combinations.

    Test is successful if NPB is executed without errors.
    """
    config = "../config/dart.xml"
    shutil.copytree("../data/kernels", "kernels")

    main(config, plan=False, faucet="bundle", silent=self.silent, log=self.log)
