"""Functional Test Family for Mars 2020 Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


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

        os.chdir(os.path.dirname(__file__))

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
        """Test error for a duplicated product.

        A file with a different filename might have the same md5 sum, this
        check catches that scenario. The bug that lead to this implementation
        was found when designing the regression test in test_pds4.py: test_m2020

        Test is successful if the following error is raised::
            RuntimeError: Two products have the same MD5 sum, the product
            spice_kernels/sclk/m2020_168_sclkscet_refit_v03.tsc might be a
            duplicate.
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
        shutil.copy2("kernels/sclk/m2020_168_sclkscet_refit_v02.tsc","kernels/sclk/m2020_168_sclkscet_refit_v03.tsc")

        with self.assertRaises(RuntimeError):
            main(
                updated_config, plan=plan, silent=self.silent, log=self.log,
                debug=False
            )


if __name__ == "__main__":
    unittest.main()
