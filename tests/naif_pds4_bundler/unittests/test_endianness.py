"""Unit tests for binary kernel endianness.

Binary kernel endianness of binary kernels needs to be the one specified via
configuration and must be compatible with the machine being used. These tests
ensure that this is the case.
"""
import os
import shutil
import sys

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils.files import string_in_file


def post_setup(self):
    """Setup Test.

    This method will be executed before each test function.
    """
    dirs = ["kernels/fk",
            "kernels/lsk",
            "kernels/spk",
            "kernels/mk"
            ]
    for dir in dirs:
        os.mkdir(dir)

    shutil.copy2("../data/kernels/lsk/naif0012.tls", "kernels/lsk/")
    shutil.copy2("../data/kernels/mk/m2020_v01.tm", "kernels/mk/")
    shutil.copy2("../data/kernels/mk/m2020_chronos_v01.tm", "kernels/mk/")
    shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp", "kernels/spk/")


def test_pds4_big_endianness(self):
    """Test BIG-IEEE basic.

    The test has a different logic depending on whether if the host machine is
    LTL-IEEE or BIG-IEEE.
    """
    post_setup(self)

    config = "../config/mars2020.xml"

    shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.big.bsp",
                 "kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp")

    try:
        main(config, silent=True, log=True, faucet="Bundle")
    except BaseException:
        line_check = "Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format."
        if not string_in_file("working/mars2020_release_temp.log", line_check, 1):
            raise BaseException

        line_check = "The binary kernel is not readable by your machine."
        if not string_in_file("working/mars2020_release_temp.log", line_check, 3):
            raise BaseException
    else:
        raise BaseException



def test_pds4_big_endianness_config(self):
    """Test BIG-IEEE when indicated via configuration."""
    post_setup(self)

    config = "../config/mars2020.xml"
    updated_config = 'working/mars2020.xml'
    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<end_of_line>CRLF</end_of_line>" in line:
                    n.write(line)
                    n.write("<binary_endianness>BIG-IEEE</binary_endianness>\n")
                else:
                    n.write(line)

    shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.big.bsp",
                 "kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp")

    main(updated_config, silent=True, log=True, faucet="Bundle")

    line_check = "The binary kernel is big endian; this endianness is not supported by your machine."
    if not string_in_file("working/mars2020_release_01.log", line_check, 1):
        raise BaseException


def test_pds4_ltl_endianness(self):
    """Test LTL-IEEE basic.

    The test has a different logic depending on whether if the host machine is
    LTL-IEEE or BIG-IEEE.
    """
    post_setup(self)

    config = "../config/mars2020.xml"

    shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp",
                 "kernels/spk/")

    main(config, silent=True, log=True)

    line_check = "Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format"
    if not string_in_file("working/mars2020_release_01.log", line_check, 1):
        raise BaseException


def test_pds4_ltl_endianness_config(self):
    """Test LTL-IEEE when indicated via configuration."""
    post_setup(self)

    config = "../config/mars2020.xml"
    updated_config = 'working/mars2020.xml'
    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<end_of_line>CRLF</end_of_line>" in line:
                    n.write(line)
                    n.write("<binary_endianness>LTL-IEEE</binary_endianness>\n")
                else:
                    n.write(line)

    shutil.copy2("../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp",
                 "kernels/spk/")

    main(updated_config, silent=True, log=True, faucet="Bundle")

    line_check = "Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format"
    if not string_in_file("working/mars2020_release_01.log", line_check, 1):
        raise BaseException


def test_pds3_ltl_endianness(self):
    """Test LTL-IEEE basic for PDS3 data sets.

    The test has a different logic depending on whether if the host machine is
    LTL-IEEE or BIG-IEEE.
    """
    post_setup(self)
    config = "../config/mro.xml"

    shutil.copy2(
        "../data/kernels/spk/mro_psp60.bsp",
        "kernels/spk/"
    )
    shutil.move("bundle", "bundle_old")
    shutil.copytree("../data/mro", "bundle")

    try:
        main(config, silent=True, log=True, faucet="Bundle")
    except BaseException:
        line_check = "The binary kernel is little endian; this endianness is not the one specified via configuration"
        if not string_in_file("working/mro_release_temp.log", line_check, 2):
            raise BaseException


def test_pds3_ltl_endianness_config(self):
    """Test LTL-IEEE for PDS3 when indicated via configuration.

    The test has a different logic depending on whether if the host machine is
    LTL-IEEE or BIG-IEEE.
    """
    post_setup(self)
    shutil.copy2(
        "../data/kernels/spk/mro_psp60.bsp",
        "kernels/spk/"
    )
    shutil.move("bundle", "bundle_old")
    shutil.copytree("../data/mro", "bundle")

    config = "../config/mro.xml"
    updated_config = 'working/mro.xml'
    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<spice_name>MRO</spice_name>" in line:
                    n.write(line)
                    n.write("<binary_endianness>LTL-IEEE</binary_endianness>\n")
                else:
                    n.write(line)

    main(updated_config, silent=True, log=True, faucet="Bundle")


def test_pds3_big_endianness(self):
    """Test BIG-IEEE basic for PDS3 data sets.

    The test has a different logic depending on whether if the host machine is
    LTL-IEEE or BIG-IEEE.
    """
    post_setup(self)
    config = "../config/mro.xml"

    shutil.copy2(
        "../data/kernels/spk/mro_psp60.big.bsp",
        "kernels/spk/mro_psp60.bsp"
    )
    shutil.move("bundle", "bundle_old")
    shutil.copytree("../data/mro", "bundle")

    try:
        main(config, silent=True, log=True, faucet="Bundle")
    except BaseException:
        line_check = "The binary kernel is big endian; this endianness is not supported by your machine."
        if not string_in_file("working/mro_release_temp.log", line_check, 1):
            raise BaseException
