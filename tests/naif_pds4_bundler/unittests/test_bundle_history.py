"""Functional tests for the List generator.
"""
import os
import unittest
from unittest import TestCase

from naif_pds4_bundler.classes.bundle import Bundle
from naif_pds4_bundler.classes.object import Object


class TestBundleHistory(TestCase):
    """
    Test family for the plan generation.
    """

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

    def test_insight_history(self):
        """ """

        test_setup = Object()
        test_setup.bundle_directory = "../data/insight"
        test_setup.mission_acronym = "insight"

        test_bundle = Object()
        test_bundle.vid = "8.0"
        test_bundle.name = "bundle_insight_spice_v008.xml"
        test_bundle.setup = test_setup
        test_bundle.collections = None

        Bundle.get_history(test_bundle, test_bundle)


if __name__ == "__main__":
    unittest.main()
