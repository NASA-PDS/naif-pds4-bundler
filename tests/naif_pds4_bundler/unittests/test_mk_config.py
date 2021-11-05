"""Unit tests for the MK configuration."""
import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestMetaKernelConfiguration(TestCase):
    """Test Family for MK configuration."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Chose the appropriate working directory.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "insight", "kernels", "orex"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True
        cls.faucet = "list"

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "orex", "insight"]
        for directory in dirs:
            os.mkdir(directory)

        shutil.copytree("../data/kernels/", "kernels")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels", "orex"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_insight_mk_error_extra_pattern(self):
        """Test for meta-kernel configuration loading error cases.

        Test is successful if it signals this run time error::
            The MK patterns insight_$YEAR_v$VERSION.tm do not correspond to the present MKs.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('<mk name="insight_$YEAR_v$VERSION.tm">\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet="staging", silent=self.silent, log=True)

    def test_insight_mk_error_wrong_name(self):
        """Test incorrect MK name in configuration.

        Test is successful if it signals this run time error::
            RuntimeError: The meta-kernel pattern VERSION is not provided.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        <mk name="insight.tm">\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, self.faucet, silent=self.silent, log=True)

    def test_insight_mk_double_keyword_in_pattern(self):
        """Test double keyword MK pattern in configuration."""
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        updated_plan = "working/insight_release_08.plan"

        with open(plan, "r") as c:
            with open(updated_plan, "w") as n:
                for line in c:
                    if "insight_v08.tm" in line:
                        n.write("insight_2021_v08.tm \\\n")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('           <mk name="insight_$YEAR_v$VERSION.tm">\n')
                    elif '<kernel pattern="insight_v[0-9][0-9].tm">' in line:
                        n.write(
                            '<kernel pattern="insight_[0-9][0-9][0-9][0-9]_v[0-9][0-9].tm">'
                        )
                    elif '<pattern length="2">VERSION</pattern>' in line:
                        n.write(
                            '                   <pattern length="2">VERSION</pattern>\n'
                        )
                        n.write(
                            '                   <pattern length="4">YEAR</pattern>\n'
                        )
                    else:
                        n.write(line)

        main(updated_config, updated_plan, self.faucet, silent=self.silent, log=True)

    def test_insight_mk_double_keyword_in_pattern_no_gen(self):
        """Test double keyword MK pattern in configuration with no generation.

        Note that given that the MK pattern has multiple keywords a MK will not
        be generated by default if not provided in the release plan.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('           <mk name="insight_$YEAR_v$VERSION.tm">\n')
                    elif '<pattern length="2">VERSION</pattern>' in line:
                        n.write(
                            '                   <pattern length="2">VERSION</pattern>\n'
                        )
                        n.write(
                            '                   <pattern length="4">YEAR</pattern>\n'
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent, log=True)

    def test_orex_mk_multiple_mks(self):
        """Test MK configuration section with multiple MKs to generate."""
        config = "../config/orex.xml"
        plan = "../data/orex_release_10.plan"

        main(config, plan, self.faucet, silent=self.silent, log=True)


if __name__ == "__main__":
    unittest.main()
