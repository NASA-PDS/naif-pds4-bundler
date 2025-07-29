"""Unit tests for kernel list generation."""

# import os
import shutil

# import unittest
from pathlib import Path

# from unittest import TestCase
from xml.etree import cElementTree

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.classes.list import KernelList
from pds.naif_pds4_bundler.classes.object import Object
from pds.naif_pds4_bundler.classes.setup import Setup
from pds.naif_pds4_bundler.utils import etree_to_dict
from pds.naif_pds4_bundler.utils.files import string_in_file


def test_pds3_msl_list(self):
    """Basic test for MSL kernel list generation.

    MSL is a PDS3 data set. This test was implemented to support
    the generation of the kernel list for release 26.
    """
    config = "../config/msl.xml"
    plan = "../data/msl_release_29.plan"
    faucet = "list"

    shutil.copy2(
        "../data/msl_release_28.kernel_list", "working/msl_release_28.kernel_list"
    )

    main(config, plan, faucet, silent=self.silent)

    new_file = ""
    with open("working/msl_release_29.kernel_list", "r") as f:
        for line in f:
            new_file += line

    old_file = ""
    with open("../data/msl_release_29.kernel_list", "r") as f:
        for line in f:
            old_file += line

    #
    # Check that the DATA_SET_ID is in capital letters and without quotes.
    #
    line_check = "DATASETID = MSL-M-SPICE-6-V1.0"
    if not string_in_file("working/msl_release_29.kernel_list", line_check, 1):
        raise BaseException

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
        "../data/mro_release_58.kernel_list", "working/mro_release_58.kernel_list"
    )

    shutil.copytree("../data/kernels/ck", "kernels/ck")

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
    """Basic test for Mars2020 kernel list generation.

    This test was implemented to support the generation of the kernel
    list for the first release.

    The particularity of this test is that it includes a kernel
    commented out.
    """
    config = "../config/mars2020.xml"
    plan = "../data/mars2020_release_10.plan"
    faucet = "list"

    main(config, plan, faucet=faucet, silent=True, log=True)

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


def test_pds3_juno_list(self):
    """Basic test for JUNO kernel list generation.

    This test was implemented to setup JUNO PDS3 data set generation for
    release 18.
    """
    config = "../config/juno.xml"
    plan = "../data/juno_release_18.plan"
    faucet = "list"

    shutil.copy2(
        "../data/juno_release_17.kernel_list", "working/juno_release_17.kernel_list"
    )

    main(config, plan, faucet, silent=self.silent)

    new_file = ""
    with open("working/juno_release_18.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                new_file += line

    old_file = ""
    with open("../data/juno_release_18.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                old_file += line

    self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])


def test_pds4_vco_list(self):
    """Basic test for Venus Climate Orbiter Akatsuki kernel list generation.

    This test was implemented to setup VCO PDS4 bundle generation migrated
    from PDS3 for DARTS/JAXA.
    """
    config = "../config/vco.xml"
    plan = "../data/vco_release_01.plan"
    faucet = "list"

    main(config, plan, faucet, silent=self.silent, log=True)

    new_file = ""
    with open("working/vco_release_01.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                new_file += line

    old_file = ""
    with open("../data/vco_release_01.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                old_file += line

    self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])


def test_pds4_vco_list_badchar(self):
    """Badchar test for Venus Climate Orbiter Akatsuki kernel list generation."""
    config = "../config/vco.xml"
    plan = "../data/vco_release_01.plan"
    faucet = "list"

    updated_config = "vco.xml"
    with open(config, "r") as f:
        with open(updated_config, "w") as u:
            for line in f:
                if (
                    "VCO SPICE reconstructed CK file providing the Venus Climate Orbiter"
                    in line
                ):
                    u.write(
                        "<description>VCO SPICE ± CK file providing the Venus Climate Orbiter "
                        "(VCO, also known as PLANET-C and AKATSUKI)"
                    )
                else:
                    u.write(line)

    main(updated_config, plan, faucet, silent=self.silent, log=True)

    line_checks = ["NON-ASCII character(s) in line"]
    for line in line_checks:
        if not string_in_file("working/vco_release_01.log", line, 12):
            raise BaseException


def test_pds4_hyb2_list(self):
    """Basic test for Hayabusa2 kernel list generation.

    This test was implemented to setup Hayabusa2 PDS4 bundle generation.
    It also tests warning messages for uppercase and mixed case kernel
    names.
    """
    config = "../config/hyb2.xml"
    plan = "../data/hyb2_release_01.plan"
    faucet = "list"

    main(config, plan, faucet, silent=self.silent, log=True)

    new_file = ""
    with open("working/hyb2_release_01.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                new_file += line

    old_file = ""
    with open("../data/hyb2_release_01.kernel_list", "r") as f:
        for line in f:
            if "DATE =" not in line:
                old_file += line

    self.assertEqual(old_file.split("\n")[7:], new_file.split("\n")[7:])


def test_xml_reader(self):
    """Test configuration file parsing.

    First test it with the xml package and then with the NPB
    setup class.
    """
    shutil.copy2("../data/kernels/fk/insight_v05.tf", "kernels/fk")
    shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk")
    shutil.copy2("../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc", "kernels/ck")
    shutil.copy2("../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc", "kernels/ck")
    shutil.copy2("../data/kernels/sclk/NSY_SCLKSCET.00019.tsc", "kernels/sclk")

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
