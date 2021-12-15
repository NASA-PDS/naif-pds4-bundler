"""Functional Test Family for Product Checksum Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils.files import string_in_file


class TestSpiceErrors(TestCase):
    """Unit Test Family Class for for Product Checksum Generation."""

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
        shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp", "kernels/spk/")
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

    def test_checksum_from_record(self):
        """Generation of the md5sum values from the checksum record file."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        main(config, plan=plan, silent=self.silent, log=self.log)

        main(config, clear='working/mars2020_release_01.file_list',
             silent=self.silent, log=self.log)

        main(config, plan=plan, silent=self.silent, log=self.log,
             checksum=True)

        line_check = "Checksum obtained from Checksum Registry file: " \
                     "/Users/mcosta/workspace/pds/naif-pds4-bundler/" \
                     "tests/naif_pds4_bundler/unittests/working/" \
                     "mars2020_release_01.checksum"

        if not string_in_file("working/mars2020_release_01.log", line_check, 11):
            raise BaseException

    def test_checksum_from_labels(self):
        """Generation of the md5sum values from labels."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        main(config, plan=plan, silent=self.silent, log=self.log)

        dirs = ["working", "mars2020"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
        os.mkdir("working")
        os.mkdir("mars2020")

        main(config, plan=plan, silent=self.silent, log=self.log,
             checksum=True)

        line_check = "Checksum obtained from existing label:"

        if not string_in_file("working/mars2020_release_01.log", line_check, 7):
            raise BaseException


if __name__ == "__main__":
    unittest.main()
