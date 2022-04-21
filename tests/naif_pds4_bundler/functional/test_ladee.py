"""Functional Test Family for LADEE Archive Generation."""
import os
import shutil
import unittest

from pds.naif_pds4_bundler.__main__ import main
from xmlschema.validators.exceptions import XMLSchemaValidationError


def tearDown(self):
    """Clean-up Test.

    This method will be executed after each test function.
    """
    unittest.TestCase.tearDown(self)

    dirs = ["working", "staging", "ladee", "kernels"]
    for dir in dirs:
        shutil.move(dir, f"{dir}_old")


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

def test_ladee_label_mode(self):
    """Test basic Label mode functionality.

    Test the label generation only, input kernels are all the kernels
    present in the kernels directory. After that remove the labels with the
    ``-c --clear`` argument.

    Test is successful if NPB is executed without errors.
    """
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    config = "../config/ladee.xml"

    main(config, plan=False, faucet="labels", silent=True, log=self.log)

    main(
        config,
        plan=False,
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    )

def test_ladee_label_mode_ker_input(self):
    """Test Label mode functionality with single kernel as input.

    Test the label generation only, input kernel specified as a parameter.
    Also tests for a non-present/wrong kernel input.

    Test is successful if NPB is executed without errors.
    """
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    config = "../config/ladee.xml"

    main(
        config,
        plan="kernels/ck/ladee_14030_14108_v04.bc",
        faucet="labels",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan=False,
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan="ladee_14030_14108_v04.bc",
        faucet="labels",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan=False,
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan="ladee_14030_14108_v04.bsp",
        faucet="labels",
        silent=True,
        log=self.log,
    )

def test_ladee_label_mode_plan_input(self):
    """Test basic Label mode functionality with a list as input.

    Test the label generation only, input kernels are provided in a
    release plan.

    Test is successful if NPB is executed without errors.
    """
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    config = "../config/ladee.xml"

    with open("working/ladee_labels_01.plan", "w") as n:
        n.write(
            "ladee_14030_14108_v04.bc\n" "ladee_ldex_v01.ti\n" "ladee_uvs_v00.ti"
        )

    main(
        config,
        plan="working/ladee_labels_01.plan",
        faucet="labels",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan=False,
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    )

    shutil.move("working/ladee_labels_01.plan", "working/ladee_labels_01.txt")

    main(
        config,
        plan="working/ladee_labels_01.txt",
        faucet="labels",
        silent=True,
        log=self.log,
    )

def test_ladee_label_mode_ker_bun_dir(self):
    """Test Label mode with same bundle and kernel directories.

    Test the label generation only, ``kernel_directory`` and
    ``bundle_directory`` are the same. First tests only provides a single
    kernel input, the second test a list of files.

    Test is successful if NPB is executed without errors.
    """
    shutil.copytree(
        "../data/regression/ladee_spice/spice_kernels",
        "kernels",
        ignore=shutil.ignore_patterns("*.xml", "*.csv"),
    )

    config = "../config/ladee.xml"
    updated_config = "working/ladee.xml"

    with open(config, "r") as c:
        with open(updated_config, "w") as n:
            for line in c:
                if "<bundle_directory>ladee</bundle_directory>" in line:
                    n.write("<bundle_directory>kernels</bundle_directory>")
                else:
                    n.write(line)

    main(
        updated_config,
        plan="ladee_14030_14108_v04.bc",
        faucet="labels",
        silent=True,
        log=self.log,
    )

    main(
        config,
        plan=False,
        clear="working/ladee_labels_01.file_list",
        silent=True,
        log=self.log,
    )

    with open("working/ladee_labels_01.plan", "w") as n:
        n.write(
            "ladee_14030_14108_v04.bc\n" "ladee_ldex_v01.ti\n" "ladee_uvs_v00.ti"
        )

    main(
        updated_config,
        plan="working/ladee_labels_01.plan",
        faucet="labels",
        silent=True,
        log=self.log,
    )
