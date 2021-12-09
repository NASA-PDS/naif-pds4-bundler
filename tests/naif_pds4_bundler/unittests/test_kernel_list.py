"""Unit tests for kernel list generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestKernelList(TestCase):
    """Unit Test Family Class for kernel list generation."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = [
            "working",
            "staging",
            "final",
            "kernels",
            "insight",
            "maven",
            "mars2020",
            "orex",
        ]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = [
            "working",
            "staging",
            "final",
            "kernels",
            "insight",
            "maven",
            "mars2020",
            "orex",
        ]
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = [
            "working",
            "staging",
            "final",
            "kernels",
            "insight",
            "maven",
            "mars2020",
            "orex",
        ]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_pds3_msl_list(self):
        """Basic test for MSL kernel list generation.

        MSL is a PDS3 data set. This test was implemented to support
        the generation of the kernel list for release 26.
        """
        config = "../config/msl.xml"
        plan = "../data/msl_release_26.plan"
        faucet = "list"

        shutil.copy2(
            "../data/msl_release_25.kernel_list", "working/msl_release_25.kernel_list"
        )

        main(config, plan, faucet, silent=self.silent)

        new_file = ""
        with open("working/msl_release_26.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/msl_release_26.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds3_m01_list(self):
        """Basic test for M01 kernel list generation.

        MSL is a PDS3 data set. This test was implemented to support
        the generation of the kernel list for release 75.
        """
        config = "../config/m01.xml"
        plan = "../data/m01_release_75.plan"
        faucet = "list"

        shutil.copy2(
            "../data/m01_release_74.kernel_list", "working/m01_release_74.kernel_list"
        )

        main(config, plan, faucet, silent=self.silent)

        new_file = ""
        with open("../data/m01_release_75.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/m01_release_75.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds3_mro_list(self):
        """Basic test for MRO kernel list generation.

        MRO is a PDS3 data set. This test was implemented to support
        the generation of the kernel list for release 59.
        """
        config = "../config/mro.xml"
        plan = "../data/mro_release_59.plan"
        faucet = "list"

        shutil.copy2(
            "../data/mro_release_58.kernel_list",
            "working/mro_release_58.kernel_list"
        )

        shutil.copytree(
            "../data/kernels/ck",
            "kernels/ck"
        )

        main(config, plan, faucet, silent=self.silent)

        new_file = ""
        with open("working/mro_release_59.kernel_list", "r") as f:
            for line in f:
                if "DATE =" not in line:
                    new_file += line

        old_file = ""
        with open("../data/mro_release_59.kernel_list", "r") as f:
            for line in f:
                if "DATE =" not in line:
                    old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds4_insight_list(self):
        """Basic test for InSight kernel list generation.

        This test was implemented to support the generation of the kernel
        list for release 8.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "list"

        shutil.copy2(
            "../data/insight_release_07.kernel_list",
            "working/insight_release_07.kernel_list",
        )

        main(config, plan, faucet, silent=self.silent)

        new_file = ""
        with open("working/insight_release_08.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/insight_release_08.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds4_maven_list(self):
        """Basic test for MAVEN kernel list generation.

        This test was implemented to support the generation of the kernel
        list for release 24.
        """
        config = "../config/maven.xml"
        plan = "../data/maven_release_24.plan"
        faucet = "list"

        main(config, plan, faucet, silent=self.silent)

        new_file = ""
        with open("working/maven_release_01.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/maven_release_24.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds4_mars2020_list(self):
        """Basic test for MAVEN kernel list generation.

        This test was implemented to support the generation of the kernel
        list for the first release.

        The particularity of this test is that it includes two meta-kernels
        provided as inputs.
        """
        config = "../config/mars2020.xml"
        plan = "../data/mars2020_release_10.plan"
        faucet = "list"

        main(config, plan, faucet=faucet, silent=True)

        new_file = ""
        with open("working/mars2020_release_01.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/mars2020_release_10.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])

    def test_pds4_orex_list(self):
        """Basic test for OSIRISReX kernel list generation.

        This test was implemented to support the generation of the kernel
        list for release 12.
        """
        config = "../config/orex.xml"
        plan = "../data/orex_release_12.plan"
        faucet = "list"

        main(config, plan, faucet=faucet, silent=True)

        new_file = ""
        with open("working/orex_release_01.kernel_list", "r") as f:
            for line in f:
                new_file += line

        old_file = ""
        with open("../data/orex_release_12.kernel_list", "r") as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])


if __name__ == "__main__":
    unittest.main()
