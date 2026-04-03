"""Implementation of the Release Plan class.
"""
import datetime
import glob
import json
import logging
import os
import re

from pds.naif_pds4_bundler.pipeline.runtime import handle_npb_error


class ReleasePlan:
    """Class to represent the release plan.

    :param setup: NPB execution setup object.
    """
    def __init__(self, setup):
        """Constructor."""
        self.kernel_list = []

        line = f"Step {setup.step} - Kernel List generation"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        self.files = []
        self.setup = setup

        #
        # Entity attributes to be replaced in template
        #
        self.CURRENTDATE = str(datetime.datetime.now())[:10]
        self.OBS = setup.observer
        self.AUTHOR = setup.producer_name

        if self.setup.pds_version == "3":
            if '"' in setup.pds3_mission_template["DATA_SET_ID"]:
                self.DATA_SET_ID = (
                    setup.pds3_mission_template["DATA_SET_ID"].split('"')[1].upper()
                )
            else:
                self.DATA_SET_ID = setup.pds3_mission_template["DATA_SET_ID"].upper()
            self.VOLID = setup.volume_id.lower()
        else:
            self.DATA_SET_ID = "N/A"
            self.VOLID = "N/A"

        self.RELID = f"{int(setup.release):04d}"
        self.RELDATE = setup.release_date

        self.template = f"{setup.templates_directory}/template_kernel_list.txt"
        self._read_config()

    def write_plan(self):
        """Write the Release Plan if not provided.

        :return: True if a release plan has been generated, False if it has
                 been provided as input
        :rtype: bool
        """
        kernels = []

        plan_name = (
            f"{self.setup.mission_acronym}_{self.setup.run_type}_"
            f"{int(self.setup.release):02d}.plan"
        )

        #
        # The release plan is generated from the kernel directory unless
        # the parameter ``labels`` is provided by the ``-f --faucet`` argument.
        # In such case only the input file is provided in the release plan.
        #
        if self.setup.args.faucet == "labels" and self.setup.args.plan:
            logging.info("-- Generate archiving plan from input kernel:")
            logging.info(f"   {self.setup.args.plan}")
            kernels_in_dir = [self.setup.args.plan]
        else:
            logging.info("-- Generate archiving plan from kernel directory(ies):")
            for k_dir in self.setup.kernels_directory:
                logging.info(f"   {k_dir}")

            kernels_in_dir = []
            for k_dir in self.setup.kernels_directory:
                kernels_in_dir += glob.glob(f"{k_dir}/**/*.*", recursive=True)
            #
            # Filter out the meta-kernels from the automatically generated
            # list.
            #
            kernels_in_dir = [item for item in kernels_in_dir if ".tm" not in item]
            kernels_in_dir.sort()

        #
        # Filter the kernels with the patterns in the kernel list from the
        # configuration. The patterns are present in the json_config
        # attribute dictionary.
        #
        patterns = []
        for pattern in self.json_config:
            patterns.append(pattern)
            if "mapping" in self.json_config[pattern]:
                patterns.append(self.json_config[pattern]["mapping"])

        for kernel in kernels_in_dir:
            for pattern in patterns:
                if re.match(pattern, kernel.split(os.sep)[-1]):
                    kernels.append(kernel.split(os.sep)[-1])

        #
        # Sort the meta-kernels that need to be added if not running
        # in label generation mode.
        #
        # First we look into the configuration file. If a meta-kernel is
        # present, it is the one that will be used.
        #
        if hasattr(self.setup, "mk_inputs") and (self.setup.args.faucet != "labels"):
            if not isinstance(self.setup.mk_inputs["file"], list):
                mks = [self.setup.mk_inputs["file"]]
            else:
                mks = self.setup.mk_inputs["file"]
            for mk in mks:
                mk_new_name = mk.split(os.sep)[-1]
                if os.path.isfile(mk):
                    mk_path = mk
                else:
                    mk_path = os.getcwd() + os.sep + mk

                if os.path.isfile(mk_path):
                    kernels.append(mk_new_name)
                else:
                    handle_npb_error(
                        f"Meta-kernel provided via configuration "
                        f"{mk_new_name} does not exist."
                    )
        elif self.setup.args.faucet != "labels":
            #
            # If no meta-kernel was provided via configuration, try to
            # infer the on that needs to be generated.
            #
            kernels_in_dir = glob.glob(
                f"{self.setup.bundle_directory}/**/*", recursive=True
            )
            mks_in_dir = []
            for mk in kernels_in_dir:
                if "/mk/" in mk and ".tm" in mk.lower():
                    mks_in_dir.append(mk.split(os.sep)[-1])

            mks_in_dir.sort()

            if not mks_in_dir:
                logging.warning(
                    "-- No former meta-kernel found to generate "
                    "meta-kernel for the list."
                )
            else:

                mk_new_name = ""

                #
                # If kernels are present, a meta-kernel might be able to be
                # generated from the information of the bundle.
                #
                if kernels:
                    for pattern in patterns:
                        mk_name = mks_in_dir[-1]
                        if re.match(pattern, mk_name):
                            version = re.findall(r"_v\d+", mk_name)[0]
                            new_version = "_v" + str(int(version[2:]) + 1).zfill(
                                len(version) - 2
                            )
                            mk_new_name = (
                                f"{mk_name.split(version)[0]}"
                                f"{new_version}{mk_name.split(version)[-1]}"
                            )

                            logging.warning(f"-- Plan will include {mk_new_name}")
                            kernels.append(mk_new_name)

                if not mk_new_name:
                    logging.error(
                        "-- No former meta-kernel found to generate "
                        "meta-kernel for the list."
                    )
        else:
            logging.info("-- Meta-kernels not generated in labeling mode.")

        #
        # Add possible orbnum files if not running in label generation
        # mode.
        #
        if self.setup.orbnum_directory and (self.setup.args.faucet != "labels"):
            orbnums_in_dir = glob.glob(f"{self.setup.orbnum_directory}/*")
            for orbnum_in_dir in orbnums_in_dir:
                for orbnum in self.setup.orbnum:
                    if re.match(orbnum["pattern"], orbnum_in_dir.split(os.sep)[-1]):
                        logging.warning(f"-- Plan will include {orbnum_in_dir}")
                        kernels.append(orbnum_in_dir.split(os.sep)[-1])

        #
        # The kernel list is complete.
        #
        with open(self.setup.working_directory + os.sep + plan_name, "w") as p:
            for kernel in kernels:
                p.write(f"{kernel}\n")

        if not kernels:

            line = "Inputs for the release not found"
            logging.warning(f"-- {line}.")
            logging.info("")
            if not self.setup.args.silent and not self.setup.args.verbose:
                print("-- " + line.split(" - ")[-1] + ".")

            self.kernel_list = kernels

            return False

        logging.info("")
        logging.info("-- Reporting the products in Plan:")

        #
        # Report the kernels that will be included in the Kernel List
        #
        for kernel in kernels:
            logging.info(f"     {kernel}")

        logging.info("")

        self.kernel_list = kernels

        #
        # Add plan to the list of generated files.
        #
        self.setup.add_file(f"{self.setup.working_directory}/{plan_name}")

        return True

    def _read_config(self) -> None:
        """Extract the Kernel List information from the configuration file."""
        json_config = self.setup.kernel_list_config

        #
        # Build a list of computed regular expressions from the JSON config
        #
        re_config = []
        for pattern in json_config:
            re_config.append(re.compile(pattern))

        self.re_config = re_config
        #
        # Also store it in setup for later use in meta-kernel description
        # generation.
        #
        self.setup.re_config = re_config
        self.json_config = json_config

        json_formatted_str = json.dumps(self.json_config, indent=2)
        self.json_formatted_lst = json_formatted_str.split("\n")
