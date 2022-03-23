"""Functional Test Family for DART Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestDART(TestCase):
    """Functional Test Family Class for DART Archive Generation."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ["working", "staging", "dart", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True
        cls.log = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "dart"]
        for dir in dirs:
            try:
                os.makedirs(dir, exist_ok=True)
            except BaseException:
                pass


    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "dart", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists("staging"):
            os.remove("staging")

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


if __name__ == "__main__":
    unittest.main()
