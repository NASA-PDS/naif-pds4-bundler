"""Unit tests for the files utilities."""
import os
import unittest
from unittest import TestCase

import spiceypy
from pds.naif_pds4_bundler.utils import mk_to_list


class TestFiles(TestCase):
    """Test family for files utilities."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Chose the appropriate working directory.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        lsk_file = "../data/kernels/lsk/naif0012.tls"
        spiceypy.furnsh(lsk_file)

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        spiceypy.kclear()

    def test_mk_to_list(self):
        """Test MK to Python list function."""
        mk = "../data/kernels/mk/vco_v01.tm"

        ker_mk_list = mk_to_list(mk, False)
        self.assertTrue(ker_mk_list)

        mk = "../data/kernels/mk/msl_v29.tm"

        ker_mk_list = mk_to_list(mk, False)
        self.assertTrue(ker_mk_list)

if __name__ == "__main__":

    unittest.main()
