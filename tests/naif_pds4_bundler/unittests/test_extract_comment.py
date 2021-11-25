"""Test family for comment extraction."""
import os
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.utils import extract_comment


class TestExtractComment(TestCase):
    """Test family for comment extraction."""

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

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

    def test_ck(self):
        """Test comment extraction from kernel."""
        comment = extract_comment(
            "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc"
        )
        comment_line = " This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011"

        assert comment_line == comment[3]


if __name__ == "__main__":
    unittest.main()
