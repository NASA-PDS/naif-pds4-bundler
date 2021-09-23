import os
import unittest
from unittest import TestCase

from naif_pds4_bundler.utils import extract_comment


class TestExtractComment(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

    def setUp(self):
        """
        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

    def tearDown(self):
        """
        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

    def test_ck(self):

        extract_comment("../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc")


if __name__ == "__main__":

    unittest.main()
