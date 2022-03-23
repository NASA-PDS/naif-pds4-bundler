"""Functional Test Family for Mars 2020 Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

import spiceypy
from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils.files import string_in_file

class TestMars2020(TestCase):
    """Functional Test Family Class for Mars 2020 Archive Generation."""

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

        os.chdir(os.path.dirname(__file__))

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
        shutil.copy2(
            "../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp", "kernels/spk/"
        )

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "mars2020", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_m2020_mks_inputs_coverage(self):
        """Test when one of the MKs doesn't include kernel to set coverage.

        Test case when one of the MK does not include the SPK/CK
        that determines the coverage of the meta-kernel. This test case was
        implemented for the M2020 Chronos meta-kernel generation implementation.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        main(config, plan=plan, silent=self.silent, log=self.log)

    def test_m2020_kernel_list(self):
        """Test Kernel List as input.

        Usage of kernel list instead of release plan.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/mars2020.xml"
        kerlist = "../data/mars2020_release_00.kernel_list"

        main(config, kerlist=kerlist, silent=self.silent, log=self.log)

    def test_m2020_kernel_list_dir(self):
        """Test usage of kernel list instead of release plan as input.

        The kernel list is provided from the working directory with the same
        resulting name.

        Test is successful if NPB is executed without errors.
        """
        shutil.copy2(
            "../data/mars2020_release_00.kernel_list",
            "working/mars2020_release_01.kernel_list",
        )

        config = "../config/mars2020.xml"
        kerlist = "working/mars2020_release_00.kernel_list"

        with self.assertRaises(FileNotFoundError):
            main(config, kerlist=kerlist, silent=self.silent, log=self.log)

        kerlist = "working/mars2020_release_01.kernel_list"

        main(config, kerlist=kerlist, silent=self.silent, log=self.log)

    def test_m2020_duplicated_kernel(self):
        """Test warning in log for a duplicated product.

        A file with a different filename might have the same md5 sum, this
        check catches that scenario. The bug that lead to this implementation
        was found when designing the regression test in test_pds4.py: test_m2020

        Later on, when testing the generation of the ExoMars2016 PDS4 Bundle,
        and adapting NPB to the ESA SPICE Service/PSA format, kernels with
        duplicated MD5 sums were found. Consequently, the dubplicate MD5 issue
        was relaxed from ERROR to WARNING.

        Previously this error was raised::
            RuntimeError: Two products have the same MD5 sum, the product
            spice_kernels/sclk/m2020_168_sclkscet_refit_v03.tsc might be a
            duplicate.

        Test is successful if NPB is executed without errors.
        """
        shutil.rmtree("kernels")
        shutil.copytree(
            "../data/regression/mars2020_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        config = "../config/mars2020.xml"
        plan = '../data/mars2020_release_01.plan'

        main(config, plan=plan, silent=self.silent)

        updated_config = 'working/mars2020_release_02.xml'

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<file>kernels/mk/m2020_v01.tm</file>" in line:
                        n.write("<file>kernels/mk/m2020_v02.tm</file>\n")
                    elif "<file>kernels/mk/m2020_chronos_v01.tm</file>" in line:
                        n.write("")
                    else:
                        n.write(line)

        plan = '../data/mars2020_release_02.plan'
        main(updated_config, plan=plan, silent=self.silent)

        updated_config = 'working/mars2020_release_03.xml'
        mk_inputs = False
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "mk_inputs" in line and not mk_inputs:
                        mk_inputs = True
                    elif "mk_inputs" in line and mk_inputs:
                        mk_inputs = False
                    elif not mk_inputs:
                        n.write(line)

        plan = "../data/mars2020_release_03.plan"
        shutil.copy2("kernels/sclk/m2020_168_sclkscet_refit_v02.tsc",
                     "kernels/sclk/m2020_168_sclkscet_refit_v03.tsc")

        main(updated_config, plan=plan, silent=self.silent, log=self.log,
             debug=False)

        line_check = 'e95003d6b0ff5fae6c2813c483108b6e'
        if not string_in_file("working/mars2020_release_03.log", line_check, 3):
            raise BaseException


    def test_m2020_spk_with_unrelated_id(self):
        """Test an empty SPK."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        spk = 'kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp'
        if os.path.isfile(spk):
            os.remove(spk)

        handle = spiceypy.spkopn(spk, "test spk file", 5000)
        spiceypy.spk14b(handle, 1, 999, 0, 'J2000', 666952140.1852001,
                        666952240.1852001, 2)

        data = [150.0, 50.0,
                1.0101, 1.0102, 1.0103,
                1.0201, 1.0202, 1.0203,
                1.0301, 1.0302, 1.0303,
                1.0401, 1.0402, 1.0403,
                1.0501, 1.0502, 1.0503,
                1.0601, 1.0602, 1.0603]

        spiceypy.spk14a(handle, 1, data, [666952140.1852001])
        spiceypy.spk14e(handle)
        spiceypy.spkcls(handle)

        main(config, plan=plan, silent=self.silent, log=self.log)

    def test_m2020_incorrect_mission_times(self):
        """Test usage of incorrect mission times."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"
        updated_config = 'working/mars2020.xml'

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<mission_start>" in line:
                        n.write("<mission_start>2023-07-30T12:51:34Z</mission_start>")
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(
                updated_config, plan=plan, silent=self.silent, log=self.log,
                debug=False
            )

    def test_m2020_incorrect_increment_start_time(self):
        """Test increment start time set via configuration with yearly MKs."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"
        updated_config = 'working/mars2020.xml'

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<release_date>2021-08-20</release_date>" in line:
                        n.write(line)
                        n.write("<increment_start>2021-05-25T08:00:00Z</increment_start>\n")
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(
                updated_config, plan=plan, silent=self.silent, log=self.log
            )

    def test_m2020_increment_start_time(self):
        """Test increment start time set via configuration."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"
        updated_config = 'working/mars2020.xml'

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<release_date>2021-08-20</release_date>" in line:
                        n.write(line)
                        n.write("<increment_start>2021-01-25T08:00:00Z</increment_start>\n")
                    else:
                        n.write(line)

        main(updated_config, plan=plan, silent=self.silent, log=self.log)

        line_check = "Coverage start time corrected with increment start from " \
                     "configuration file to: 2021-01-25T08:00:00Z"

        if not string_in_file("working/mars2020_release_01.log", line_check):
            raise BaseException

        line_check = "2021-01-25T08:00:00Z - 2021-05-21T15:47:08Z"

        if not string_in_file("working/mars2020_release_01.log", line_check):
            raise BaseException

    def test_m2020_increment_finish_time(self):
        """Test increment finish time set via configuration."""
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"
        updated_config = 'working/mars2020.xml'

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<release_date>2021-08-20</release_date>" in line:
                        n.write(line)
                        n.write("<increment_finish>2021-04-23T08:00:00Z</increment_finish>\n")
                    else:
                        n.write(line)

        main(updated_config, plan=plan, silent=self.silent, log=self.log)

        line_check = "Coverage finish time corrected with increment finish " \
                     "from configuration file to: 2021-04-23T08:00:00Z"

        if not string_in_file("working/mars2020_release_01.log", line_check):
            raise BaseException

        line_check = "2021-02-18T20:20:00Z - 2021-04-23T08:00:00Z"

        if not string_in_file("working/mars2020_release_01.log", line_check, 1):
            raise BaseException

    def test_m2020_mks_incorrect_path(self):
        """Test when a MK has an incorrect path.

        Test when a MK has an incorrect path, the NPB execution should not be
        stopped because this can be intentional (VCO's MKs.)

        Test is successful if NPB is executed without errors.
        """
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_00.plan"

        shutil.move('kernels/mk/m2020_v01.tm', 'kernels/mk/m2020.tm')
        with open('kernels/mk/m2020.tm', "r") as c:
            with open('kernels/mk/m2020_v01.tm', "w") as n:
                for line in c:
                    if "PATH_VALUES       = ( '..'      )" in line:
                        n.write("PATH_VALUES       = ( './'      )\n")
                    else:
                        n.write(line)

        main(config, plan=plan, silent=self.silent, log=self.log)

        line_check = "The MK could not be loaded with the SPICE API FURNSH."
        if not string_in_file("working/mars2020_release_01.log", line_check, 1):
            raise BaseException

if __name__ == "__main__":
    unittest.main()
