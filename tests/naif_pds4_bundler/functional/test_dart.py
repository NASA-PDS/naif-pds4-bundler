"""Functional Test Family for DART Archive Generation."""
import shutil

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.utils.files import string_in_file


def test_dart_multiple_obs_tar(self):
    """Test Archive with two Observers and Targets.

    This test is designed to test the implementation of multiple observers
    and targets in a SPICE Kernel Archive. DART has two observers and two
    targets with kernels using different combinations.

    Test is successful if NPB is executed without errors and if the SPICE
    Kernel collection description is correct.
    """
    config = "../config/dart.xml"
    shutil.copytree("../data/kernels", "kernels")

    main(config, plan=False, faucet="bundle", silent=self.silent, log=self.log)

    line_checks = [
        "<description>This collection contains SPICE kernels for the DART and LICIA "
        "spacecraft and their instruments.</description>",
    ]
    for line in line_checks:
        if not string_in_file(
            "dart/dart_spice/spice_kernels/collection_spice_kernels_v001.xml", line, 2
        ):
            raise BaseException


def test_dart_host_type(self):
    """Test usage of "Host" as Observing System Component Type.

    Test usage of "Host" instead of "Spacecraft" or "Lander" for the
    Observing System Component Type. All NAIF archives use "Spacecraft" but
    is deprecated since IM 1.14.0.0, DARTS/JAXA will use "Host" for their
    archives.

    Test is successful if NPB is executed without errors.
    """
    config = "../config/dart.xml"
    shutil.copytree("../data/kernels", "kernels")
    updated_config = "dart.xml"

    with open(config, "r") as i:
        with open(updated_config, "w") as o:
            for line in i:
                if "<type>Spacecraft</type>" in line:
                    o.write("<type>Host</type>\n")
                else:
                    o.write(line)

    main(updated_config, plan=False, faucet="bundle", silent=self.silent, log=self.log)

    file = "dart/dart_spice/bundle_dart_spice_v001.xml"
    repetitions = 2
    str_to_check = "<type>Host</type>"

    if not string_in_file(file, str_to_check, repetitions):
        raise BaseException
