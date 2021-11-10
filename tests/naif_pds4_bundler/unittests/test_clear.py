"""Test Family to clear previous execution."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main


class TestClear(TestCase):
    """Test Family to clear previous execution."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Chose the appropriate working directory and cleanup directories.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ["working", "staging", "insight", "kernels"]
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

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists("staging"):
            os.remove("staging")

    def test_insight_basic(self):
        """Test complete clearing basic Insight archive generation.

        This method will be executed after each test function.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "bundle"

        os.makedirs("working", mode=0o777, exist_ok=True)
        os.makedirs("staging", mode=0o777, exist_ok=True)
        shutil.copy2(
            "../data/insight_release_basic.kernel_list",
            "working/insight_release_07.kernel_list",
        )
        shutil.copytree("../data/insight", "insight")
        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree("../data/kernels", "kernels")

        with open("../data/insight.list", "r") as i:
            for line in i:
                with open(f"insight/insight_spice/{line[0:-1]}", "w"):
                    pass

        main(config, plan, faucet, silent=self.silent, log=self.log)

        #
        # Remove the files from the prior run.
        #
        main(
            config,
            plan,
            "plan",
            silent=self.silent,
            log=self.log,
            clear="working/insight_release_08.file_list",
        )

        #
        # Run the pipeline again.
        #
        main(config, plan, faucet, silent=self.silent, log=self.log)

        #
        # Remove the files from the prior run and run the pipeline again.
        #
        main(
            config,
            plan,
            faucet,
            silent=self.silent,
            log=self.log,
            clear="working/insight_release_08.file_list",
        )

    def test_insight_error(self):
        """Test complete clearing basic Insight archive generation with error.

        Test generation of product list when there is an error in the
        execution. Also test cleaning the failed run and running the pipeline
        again. In addition, test an incorrect spice_name.
        """
        config = "../config/insight.xml"
        wrong_config = "working/insight.xml"

        cwd = os.getcwd()
        dirs = ["working", "staging", "insight"]
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        plan = "../data/insight_release_08.plan"

        shutil.rmtree("insight")
        shutil.copytree("../data/insight", "insight")

        try:
            shutil.copytree("../data/kernels", "kernels")
        except BaseException:
            pass

        with open(config, "r") as c:
            with open(wrong_config, "w") as n:
                for line in c:
                    if "<spice_name>INSIGHT</spice_name>" in line:
                        n.write("<spice_name>INSPGHT</spice_name>" "\n")
                    else:
                        n.write(line)

        #
        # Error of checksum validation.
        #
        with self.assertRaises(RuntimeError):
            main(wrong_config, silent=self.silent, log=self.log)

        os.chdir(cwd)
        #
        # Remove the files from the prior run.
        #
        main(
            config,
            plan,
            "plan",
            silent=self.silent,
            log=self.log,
            clear="working/insight_release_08.file_list",
        )

        #
        # Run the pipeline again.
        #
        main(config, plan, "bundle", silent=self.silent, log=self.log)


if __name__ == "__main__":
    unittest.main()
