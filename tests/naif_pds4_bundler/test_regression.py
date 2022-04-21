"""Regression Test Family for InSight Archive Generation."""
import os
import shutil
import tempfile
import unittest
from unittest import TestCase

import regression.test_pds3 as pds3
import regression.test_pds4 as pds4

class TestRegression(TestCase):
    """Regression Test Family Class."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Regression Tests - {cls.__name__}")

        cls.test_dir = os.path.dirname(__file__)
        cls.silent = True
        cls.verbose = False
        cls.log = True
        cls.tmp_dir = tempfile.TemporaryDirectory()

        shutil.copytree(os.sep.join(cls.test_dir.split(os.sep)),
                        cls.tmp_dir.name + '/naif_pds4_bundler')
        shutil.copytree(os.sep.join(cls.test_dir.split(os.sep)[:-2]) +
                        "/src/pds/naif_pds4_bundler/templates/1.5.0.0",
                        cls.tmp_dir.name + '/naif_pds4_bundler/templates/1.5.0.0')
        tests_dir = cls.tmp_dir.name + "/naif_pds4_bundler/regression/"
        print(f"       Tests data on: {cls.tmp_dir.name}")
        os.chdir(tests_dir)

    @classmethod
    def tearDownClass(cls):
        """Destructor.

        Method that will be executed once for this test case class.
        It will execute after all tests methods.

        Clears up the functional test directory.
        """
        cls.tmp_dir.cleanup()

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging"]
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
        test_dir = self.tmp_dir.name + "/naif_pds4_bundler/regression/"
        dirs = next(os.walk('.'))[1]
        for dir in dirs:
            try:
                shutil.rmtree(test_dir + dir)
            except BaseException:
                pass

    #
    # PDS4 regression tests.
    #
    def test_insight(self):
        pds4.test_insight(self)

    def test_ladee(self):
        pds4.test_ladee(self)

    def test_kplo(self):
        pds4.test_kplo(self)

    def test_m2020(self):
        pds4.test_m2020(self)

    def test_em16(self):
        pds4.test_em16(self)

    #
    # PDS3 regression tests.
    #
    def test_msl(self):
        pds3.test_msl(self)


if __name__ == "__main__":
    unittest.main()
