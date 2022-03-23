"""Functional Test Family for LADEE Archive Generation."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.__main__ import main
from xmlschema.validators.exceptions import XMLSchemaValidationError


class TestLADEE(TestCase):
    """Functional Test Family Class for LADEE Archive Generation."""

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

    def test_ladee_update_input_mk_name(self):
        """Test  inappropriate name for input MK.

        This test needs to use the regression test data to be able to perform
        final validation and run the entire pipeline.

        Test is successful if NPB is executed without errors.
        """
        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )
        shutil.move("kernels/mk/ladee_v01.tm", "kernels/mk/ladee_v03.tm")

        config = "../config/ladee.xml"
        updated_config = "working/ladee.xml"

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<file>../data/ladee_v01.tm</file>" in line:
                        n.write("<file>kernels/mk/ladee_v03.tm</file>")
                    else:
                        n.write(line)

        main(updated_config, plan=False, silent=self.silent, log=self.log)

    def test_ladee_checksum_registry(self):
        """Tests obtaining of MD5 sum per product using the checksum registry.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/ladee.xml"

        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        shutil.copy2("../data/ladee_release_01.checksum", "working/")

        main(config, plan=False, silent=self.silent, log=self.log)

    def test_ladee_date_format(self):
        """Tests absence and incorrect date_format element in configuration.

        First section of the test is passed if the following error is raised::
           Reason: value must be one of ['infomod2', 'maklabel']

        The second section, does not provide the configuration element runs
        successfully.

        Test is successful if the conditions described above are met.
        """
        config = "../config/ladee.xml"
        updated_config = "working/ladee.xml"

        shutil.copytree(
            "../data/regression/ladee_spice/spice_kernels",
            "kernels",
            ignore=shutil.ignore_patterns("*.xml", "*.csv"),
        )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<date_format>maklabel</date_format>" in line:
                        n.write("<date_format>makelabel</date_format>")
                    else:
                        n.write(line)

        with self.assertRaises(XMLSchemaValidationError):
            main(updated_config, plan=False, silent=self.silent, log=self.log)

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<date_format>maklabel</date_format>" in line:
                        n.write("")
                    else:
                        n.write(line)

        main(updated_config, plan=False, silent=self.silent, log=self.log)


if __name__ == "__main__":
    unittest.main()
