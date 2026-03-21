"""Functional Test Family for CLPS Archive Generation."""
import shutil

from pds.naif_pds4_bundler.pipeline.npb import run_pipeline
from pds.naif_pds4_bundler.utils.files import string_in_file
from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs


def test_clps_multiple_missions(self):
    """Test Archive with multiple missions and observers.

    This test is designed to test the implementation of multiple missions
    and observers in a SPICE Kernel Archive. CLPS has many missions and many
    observers with kernels using different combinations.

    Test is successful if NPB is executed without errors and if the SPICE
    Kernel collection description is correct.
    """
    config = "../config/clps.xml"
    shutil.copytree("../data/kernels", "kernels")
    shutil.copy("../data/readme_clps.txt", "working/readme.txt")

    run_pipeline(PipelineArgs(config=config, plan=None, faucet="bundle",
                              silent=self.silent, log=self.log))

    line_checks = [
        "<description>This collection contains SPICE kernels for the Peregrine Lunar Lander and Nova-C Lunar Lander spacecraft and their instruments.</description>",
    ]
    for line in line_checks:
        if not string_in_file(
            "clps/clps_spice/spice_kernels/collection_spice_kernels_v001.xml", line, 2
        ):
            raise BaseException


def test_clps_host_type(self):
    """Test usage of "Host" as Observing System Component Type.

    Test usage of "Host" instead of "Spacecraft" or "Lander" for the
    Observing System Component Type. All NAIF archives use "Spacecraft" but
    is deprecated since IM 1.14.0.0, CLPS will use "Host" for their
    archives.

    Test is successful if NPB is executed without errors.
    """
    config = "../config/clps.xml"
    shutil.copytree("../data/kernels", "kernels")
    updated_config = "clps.xml"

    with open(config, "r") as i:
        with open(updated_config, "w") as o:
            for line in i:
                if "<type>Spacecraft</type>" in line:
                    o.write("<type>Host</type>\n")
                else:
                    o.write(line)

    o.close()

    run_pipeline(PipelineArgs(config=updated_config, plan=None, faucet="bundle",
                              silent=self.silent, log=self.log))

    file = "clps/clps_spice/bundle_clps_spice_v001.xml"
    repetitions = 2
    str_to_check = "<type>Host</type>"

    if not string_in_file(file, str_to_check, repetitions):
        raise BaseException
