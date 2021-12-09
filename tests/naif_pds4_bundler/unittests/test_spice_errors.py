"""Functional Test Family for Mars 2020 Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestSpiceErrors(TestCase):
    """Unit Test Family Class for SPICE errors with SpiceyPy."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ["working", "staging", "mars2020", "kernels"]
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

        dirs = [
            "working",
            "staging",
            "kernels",
            "mars2020",
            "kernels/fk",
            "kernels/lsk",
            "kernels/spk",
            "kernels/mk",
        ]
        for dir in dirs:
            os.mkdir(dir)

        shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk/")
        shutil.copy2("../data/kernels/fk/m2020_v04.tf", "kernels/fk/")
        shutil.copy2("../data/kernels/mk/m2020_v01.tm", "kernels/mk/")
        shutil.copy2("../data/kernels/mk/m2020_chronos_v01.tm", "kernels/mk/")
        shutil.copy2("../data/kernels/spk/m2020_cruise_od138_v1.bsp", "kernels/spk/")

        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "mars2020", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_empty_spk(self):
        """Test an empty SPK."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        spk = 'kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp'
        if os.path.isfile(spk):
            os.remove(spk)

        with open(spk, 'w'):
            pass

        with self.assertRaises(BaseException):
            main(config, plan=plan, silent=self.silent, log=self.log)


if __name__ == "__main__":
    unittest.main()
