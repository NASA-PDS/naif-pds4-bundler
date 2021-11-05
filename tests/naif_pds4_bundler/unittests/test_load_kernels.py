"""Unit tests for kernel loading."""
import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestLoadKernels(TestCase):
    """Unit Test Family Class for kernel loading."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.faucet = "staging"
        cls.silent = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "maven"]
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/misc", "misc")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "kernels", "misc", "maven"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_load_kernels(self):
        """Basic kernel load test.

        This test was implemented after an incorrect SCLK was loaded for
        MAVEN and to support the corresponding bug-fix. The test checks
        that the warning message provided by NPB when loading an incorrect
        SCLK is as expected.
        """
        config = "../config/maven.xml"
        plan = "working/maven_orbnum.plan"
        found = False

        with open(plan, "w") as p:
            p.write("maven_orb_rec_210101_210401_v1.orb")
            p.write("\nmaven_orb_rec_210101_210401_v1.nrb")

        shutil.copy2(
            "kernels/sclk/MVN_SCLKSCET.00088.tsc",
            "kernels/sclk/MVN_SCLKSCET.00100.tsc.bad",
        )
        shutil.copy2(
            "kernels/sclk/MVN_SCLKSCET.00088.tsc", "kernels/sclk/MVN_SCLKSCET.00000.tsc"
        )
        os.mkdir("kernels/sclk/zzarchive")
        shutil.copy2(
            "kernels/sclk/MVN_SCLKSCET.00088.tsc",
            "kernels/sclk/zzarchive/MVN_SCLKSCET.00000.tsc",
        )

        main(config, plan, self.faucet, silent=self.silent, log=True)

        log_line = (
            "naif-pds4-bundler/tests/naif_pds4_bundler/unittests/kernels/"
            "sclk/MVN_SCLKSCET.00088.tsc']\n"
        )
        with open("working/maven_release_01.log", "r") as f:
            for line in f.readlines():
                if log_line in line:
                    found = True

        self.assertTrue(found)


if __name__ == "__main__":
    unittest.main()
