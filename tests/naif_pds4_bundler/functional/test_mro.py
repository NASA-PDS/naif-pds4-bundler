"""Unit tests for kernel list generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestMRO(TestCase):
    """Unit Test Family Class for kernel list generation."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = [
            "working",
            "staging",
            "bundle",
            "kernels",
            "misc",
        ]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = [
            "working",
        ]
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = [
            "working",
            "staging",
            "bundle",
            "kernels",
            "misc",
        ]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

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
        shutil.copytree("../data/misc", "misc")
        shutil.copytree("../data/mro", "bundle")
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

#    def test_mro_mapping_from_list(self):
#        """Basic test for MRO PDS3 data set."""
#        config = "../config/mro.xml"
#        plan = "../data/mro_release_59.plan"
#        faucet = "bundle"
#
#        shutil.copy2(
#            "../data/mro_release_58.kernel_list",
#            "working/mro_release_58.kernel_list"
#        )
#
#        shutil.copytree("../data/kernels", "kernels")
#        shutil.copytree("../data/misc", "misc")
#        shutil.copytree("../data/mro", "bundle")
#        shutil.copytree("../data/mro", "staging")
#
#        shutil.copy2(
#            "../data/release_mro.cat",
#            "staging/mrosp_1000/catalog/release.cat"
#        )
#
#        shutil.copy2(
#            "../data/spiceds_mro.cat",
#            "staging/mrosp_1000/catalog/spiceds.cat"
#        )
#
#        main(config, plan, faucet, log=True, verbose=False)

if __name__ == "__main__":
    unittest.main()
