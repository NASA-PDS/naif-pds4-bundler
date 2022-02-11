"""Unit tests for parsing XML documents."""
import os
import shutil
import unittest
from pathlib import Path
from unittest import TestCase
from xml.etree import cElementTree

from pds.naif_pds4_bundler.classes.list import KernelList
from pds.naif_pds4_bundler.classes.object import Object
from pds.naif_pds4_bundler.classes.setup import Setup
from pds.naif_pds4_bundler.utils import etree_to_dict


class TestXML(TestCase):
    """Unit Test Family Class for parsing XML documents."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "kernels"]
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_xml_reader_basic(self):
        """Test configuration file parsing.

        First test it with the xml package and then with the NPB
        setup class.
        """
        shutil.copy2("../data/kernels/fk/insight_v05.tf", "kernels/fk")
        shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk")
        shutil.copy2(
            "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc", "kernels/ck"
        )
        shutil.copy2(
            "../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc", "kernels/ck"
        )
        shutil.copy2("../data/kernels/sclk/NSY_SCLKSCET.00019.tsc", "kernels/sclk")

        os.mkdir("insight")

        #
        # Basic test of XML parsing.
        #
        config = Path("../config/insight.xml").read_text()
        etree_to_dict(cElementTree.XML(config))

        #
        # Dummy initialization values for Setup class
        #
        version = "X.Y.Z"
        args = Object()

        args.config = "../config/insight.xml"
        args.plan = False
        args.faucet = ""
        args.diff = ""
        args.silent = False
        args.verbose = True
        args.debug = False

        setup = Setup(args, version)
        setup.templates_directory = "../templates/1.5.0.0"

        #
        # Testing of the initialisation of the List class
        #
        setup.release = "008"

        KernelList(setup)


if __name__ == "__main__":

    unittest.main()
