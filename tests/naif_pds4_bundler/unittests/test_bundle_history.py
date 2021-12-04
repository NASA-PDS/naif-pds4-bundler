"""Unit tests for the Bundle history generation."""
import os
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.classes.bundle import Bundle
from pds.naif_pds4_bundler.classes.object import Object


class TestBundleHistory(TestCase):
    """Test family for Bundle history generation."""

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

    def test_insight_history(self):
        """Test the generation of the bundle history."""
        test_setup = Object()
        test_setup.bundle_directory = "../data/insight"
        test_setup.mission_acronym = "insight"
        test_setup.xml_model = "http://pds.nasa.gov/pds4/pds/v1/test"

        test_bundle = Object()
        test_bundle.vid = "8.0"
        test_bundle.name = "bundle_insight_spice_v008.xml"
        test_bundle.setup = test_setup
        test_bundle.collections = None

        Bundle.get_history(test_bundle, test_bundle)


if __name__ == "__main__":
    unittest.main()
