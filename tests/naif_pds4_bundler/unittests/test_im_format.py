import os
import shutil
import unittest
from unittest import TestCase

from naif_pds4_bundler.__main__ import main


class TestIMFormat(TestCase):
    """
    Test Family for the Information Model.
    """

    @classmethod
    def setUpClass(cls):
        """
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        cls.faucet = "list"
        cls.config = "../config/insight.xml"
        cls.updated_config = "working/insight.xml"

    def setUp(self):
        """
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
        """
        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_im_format(self):
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

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
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

        """

        with open(self.config, "r") as c:
            with open(self.updated_config, "w") as n:
                for line in c:
                    if "<information_model>1.5.0.0</information_model>" in line:
                        n.write("<information_model>1.6.0.0" "</information_model>\n")
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(self.updated_config, faucet=self.faucet, silent=True)

    def test_im_schema_incoherent(self):
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

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
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

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
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

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
