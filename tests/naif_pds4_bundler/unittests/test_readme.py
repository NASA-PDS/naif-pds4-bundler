"""Unit tests for format differences for PDS4 Information Models."""
import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestIMFormat(TestCase):
    """Unit tests class for format differences for PDS4 Information Models.

    The usage of different IM will lead to changes in the format and
    values of the PDS4 artifacts. This test family checks that these
    changes are as expected.
    """

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        cls.faucet = "list"
        cls.config = "../config/insight.xml"
        cls.updated_config = "working/insight.xml"

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        os.mkdir("kernels/lsk")
        shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_im_format(self):
        """IM input format test.

        Tests if the IM input format in the NPB configuration file
        is adequate.

        Test is successful if the following error message is provided::
            RuntimeError: PDS4 Information Model 1.A.0.0 format from configuration is incorrect.
        """
        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write("<information_model>1.A.0.0" "</information_model>\n")
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(self.updated_config, faucet=self.faucet, silent=True)

    def test_im_xml_incoherent(self):
        """IM input configuration incoherence test.

        Tests if the IM input in the NPB configuration file is coherent
        with other elements of the configuration.

        Test is successful if the following error message is provided::
            RuntimeError: PDS4 Information Model 1600 is incoherent with the XML Model version: http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.sch.
        """
        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write("<information_model>1.6.0.0</information_model>\n")
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(self.updated_config, faucet=self.faucet, silent=True)

    def test_im_schema_incoherent(self):
        """Schema input configuration incoherence test.

        Tests if the schema input in the NPB configuration file is coherent
        with other elements of the configuration.

        Test is successful if the following error message is provided::
            RuntimeError: PDS4 Information Model 1500 is incoherent with the Schema location: http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1A00.xsd.
        """
        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if (
                        "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                        "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd" in line
                    ):
                        n.write(
                            "<schema_location>http://pds.nasa.gov/pds4/pds/"
                            "v1 http://pds.nasa.gov/pds4/pds/v1/"
                            "PDS4_PDS_1A00.xsd\n"
                        )
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(self.updated_config, faucet=self.faucet, silent=True)

    def test_im_version_ascii(self):
        """IM version test.

        Tests if the IM version in the NPB configuration file is coherent
        with other elements of the configuration.
        """
        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write("<information_model>1.16.0.0" "</information_model>\n")
                    elif (
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1500.sch</xml_model>\n" in line
                    ):
                        n.write(
                            "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                            "PDS4_PDS_1G00.sch</xml_model>\n"
                        )
                    elif (
                        "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                        "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd" in line
                    ):
                        n.write(
                            "<schema_location>http://pds.nasa.gov/pds4/pds/"
                            "v1 http://pds.nasa.gov/pds4/pds/v1/"
                            "PDS4_PDS_1G00.xsd\n"
                        )
                    else:
                        n.write(line)

        main(self.updated_config, faucet=self.faucet, silent=True)

    def test_im_version_ascii_incorrect(self):
        """IM version incoherent test.

        Tests if the IM version in the NPB configuration file is coherent
        with other elements of the configuration.

        Test is successful if the following error message is provided::
            RuntimeError: PDS4 Information Model AGBK is incoherent with the XML Model version: http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1G00.sch.
        """
        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write(
                            "<information_model>10.16.11.20" "</information_model>\n"
                        )
                    elif (
                        "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                        "PDS4_PDS_1500.sch</xml_model>\n" in line
                    ):
                        n.write(
                            "<xml_model>http://pds.nasa.gov/pds4/pds/v1/"
                            "PDS4_PDS_1G00.sch</xml_model>\n"
                        )
                    elif (
                        "<schema_location>http://pds.nasa.gov/pds4/pds/v1 "
                        "http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd" in line
                    ):
                        n.write(
                            "<schema_location>http://pds.nasa.gov/pds4/pds/"
                            "v1 http://pds.nasa.gov/pds4/pds/v1/"
                            "PDS4_PDS_1G00.xsd\n"
                        )
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(self.updated_config, faucet=self.faucet, silent=True)


if __name__ == "__main__":
    unittest.main()
