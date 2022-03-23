"""Functional Test Family for Label execution mode."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestLabel(TestCase):
    """Functional Test Family Class for Label execution mode."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ["working", "staging", "ladee", "kernels"]
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

        dirs = ["working", "staging", "ladee"]
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

        dirs = ["working", "staging", "ladee", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists("staging"):
            os.remove("staging")

    def test_ladee_label_mode(self):
        """Test basic Label mode functionality.

        Test the label generation only, input kernels are all the kernels
        present in the kernels directory. After that remove the labels with the
        ``-c --clear`` argument.

        Test is successful if NPB is executed without errors.
        """
        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        config = "../config/ladee.xml"

        main(config, plan=False, faucet="labels", silent=True, log=self.log)

        main(
            config,
            plan=False,
            clear="working/ladee_labels_01.file_list",
            silent=True,
            log=self.log,
        )

    def test_ladee_label_mode_ker_input(self):
        """Test Label mode functionality with single kernel as input.

        Test the label generation only, input kernel specified as a parameter.
        Also tests for a non-present/wrong kernel input.

        Test is successful if NPB is executed without errors.
        """
        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        config = "../config/ladee.xml"

        main(
            config,
            plan="kernels/ck/ladee_14030_14108_v04.bc",
            faucet="labels",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan=False,
            clear="working/ladee_labels_01.file_list",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan="ladee_14030_14108_v04.bc",
            faucet="labels",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan=False,
            clear="working/ladee_labels_01.file_list",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan="ladee_14030_14108_v04.bsp",
            faucet="labels",
            silent=True,
            log=self.log,
        )

    def test_ladee_label_mode_plan_input(self):
        """Test basic Label mode functionality with a list as input.

        Test the label generation only, input kernels are provided in a
        release plan.

        Test is successful if NPB is executed without errors.
        """
        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        config = "../config/ladee.xml"

        with open("working/ladee_labels_01.plan", "w") as n:
            n.write(
                "ladee_14030_14108_v04.bc\n" "ladee_ldex_v01.ti\n" "ladee_uvs_v00.ti"
            )

        main(
            config,
            plan="working/ladee_labels_01.plan",
            faucet="labels",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan=False,
            clear="working/ladee_labels_01.file_list",
            silent=True,
            log=self.log,
        )

        shutil.move("working/ladee_labels_01.plan", "working/ladee_labels_01.txt")

        main(
            config,
            plan="working/ladee_labels_01.txt",
            faucet="labels",
            silent=True,
            log=self.log,
        )

    def test_ladee_label_mode_ker_bun_dir(self):
        """Test Label mode with same bundle and kernel directories.

        Test the label generation only, ``kernel_directory`` and
        ``bundle_directory`` are the same. First tests only provides a single
        kernel input, the second test a list of files.

        Test is successful if NPB is executed without errors.
        """
        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        config = "../config/ladee.xml"
        updated_config = "working/ladee.xml"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<bundle_directory>ladee</bundle_directory>" in line:
                        n.write("<bundle_directory>kernels</bundle_directory>")
                    else:
                        n.write(line)

        main(
            updated_config,
            plan="ladee_14030_14108_v04.bc",
            faucet="labels",
            silent=True,
            log=self.log,
        )

        main(
            config,
            plan=False,
            clear="working/ladee_labels_01.file_list",
            silent=True,
            log=self.log,
        )

        with open("working/ladee_labels_01.plan", "w") as n:
            n.write(
                "ladee_14030_14108_v04.bc\n" "ladee_ldex_v01.ti\n" "ladee_uvs_v00.ti"
            )

        main(
            updated_config,
            plan="working/ladee_labels_01.plan",
            faucet="labels",
            silent=True,
            log=self.log,
        )


if __name__ == "__main__":
    unittest.main()
