"""Implementation of the Release Plan class.
"""
import glob
import logging
import os
from pathlib import Path
import re

from pds.naif_pds4_bundler.pipeline.runtime import handle_npb_error


class ReleasePlan:
    """Class to represent the release plan.

    :param setup: NPB execution setup object.
    """
    def __init__(self, setup):
        """Constructor."""
        self.setup = setup
        self.json_config = self.setup.kernel_list_config
        self._kernel_list = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def kernel_list(self) -> list:
        """List of kernel filenames included in the release plan.

        Populated by :meth:`read_plan` or :meth:`write_plan` once the plan
        has been processed.
        """
        return self._kernel_list

    def read_plan(self, plan: Path) -> None:
        """Read Release Plan from the main module input.

        :param plan: Release Plan name
        """
        kernels = []

        # Add mapping kernel patterns in list.
        patterns = self._get_patterns()

        # If NPB runs in labeling mode, a single file can be specified
        # as a release plan. If so, a plan is generated.
        if plan.suffix != ".plan" and self.setup.args.faucet == "labels":
            plan = os.path.join(self.setup.working_directory, self._plan_name())
            with open(plan, "w") as pl:
                pl.write(plan.split(os.sep)[-1])

        elif plan.suffix != ".plan":
            handle_npb_error(
                "Release plan requires *.plan extension. Single "
                "kernels are only allowed in labeling mode."
            )

        with open(plan, "r") as f:
            for line in f:
                ker_matched = False
                for pattern in patterns:
                    if ker_line := re.search(pattern, line):

                        # The kernel is not matched if there is a comment character in front.
                        if line.lstrip()[0] != "#":
                            kernels.append(ker_line.group(0))
                            ker_matched = True

                if not ker_matched:
                    #
                    # Add the ORBNUM files that need to be added.
                    # Match the pattern with the file.
                    #
                    if hasattr(self.setup, "orbnum"):
                        for orb in self.setup.orbnum:
                            pattern = orb["pattern"]
                            if ker_line := re.search(pattern, line):
                                kernels.append(ker_line.group(0))
                                ker_matched = True
                    #
                    # Display the lines that have not been matched unless
                    # they only contain blank spaces.
                    #
                    if not ker_matched and line.strip():
                        logging.warning(
                            "-- The following release plan line has not been matched:"
                        )
                        logging.warning(f"   {line.rstrip()}")

        # Report the kernels that are included in the release plan.
        self._log_kernels_in_release_plan(kernels)
        self._kernel_list = kernels

    def write_plan(self):
        """Write the Release Plan if not provided.

        :return: True if a release plan has been generated, False if it has
                 been provided as input
        :rtype: bool
        """
        # The release plan is generated from the kernel directory unless
        # the parameter ``labels`` is provided by the ``-f --faucet`` argument.
        # In such case only the input file is provided in the release plan.
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

        # Filter the kernels with the patterns in the kernel list from the
        # configuration.
        patterns = self._get_patterns()

        kernels = []
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
            kernels_in_dir = Path(self.setup.bundle_directory).rglob("*")
            mks_in_dir = [
                p.name
                for p in kernels_in_dir
                if "mk" in p.parts and p.suffix.lower() == ".tm"
            ]

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

        # Add possible orbnum files if not running in label generation
        # mode.
        kernels.extend(self._collect_orbnum_files())

        # The kernel list is complete.
        plan_name = self._plan_name()
        self._write_plan_file(plan_name, kernels)

        if not kernels:

            line = "Inputs for the release not found"
            logging.warning(f"-- {line}.")
            logging.info("")
            if not self.setup.args.silent and not self.setup.args.verbose:
                print("-- " + line.split(" - ", maxsplit=1)[-1] + ".")

            return False

        # Report the kernels that are included in the release plan.
        self._log_kernels_in_release_plan(kernels)
        self._kernel_list = kernels

        # Add plan to the list of generated files.
        self.setup.add_file(f"{Path(self.setup.working_directory, plan_name)}")

        return True

    # ------------------------------------------------------------------
    # Private helpers shared by read_plan and write_plan
    # ------------------------------------------------------------------

    def _get_patterns(self) -> list:
        """Return a flat list of all config patterns, including mapping patterns.

        Both primary patterns and their associated mapping patterns are
        included so that either form of a kernel name can be matched.

        :return: List of regex pattern strings.
        """
        patterns = []
        for pattern in self.json_config:
            patterns.append(pattern)
            if "mapping" in self.json_config[pattern]:
                patterns.append(self.json_config[pattern]["mapping"])
        return patterns

    def _plan_name(self) -> str:
        """Return the canonical .plan filename for the current release.

        :return: Filename of the form ``<mission>_<run_type>_NN.plan``.
        """
        return (f"{self.setup.mission_acronym}_{self.setup.run_type}_"
                f"{int(self.setup.release):02d}.plan")

    @staticmethod
    def _log_kernels_in_release_plan(kernels: list) -> None:
        """Log the kernels that are included in the release plan.

        :param kernels: List of kernel filenames to report.
        """
        logging.info("")
        logging.info("-- Reporting the products in Plan:")
        for kernel in kernels:
            logging.info(f"     {kernel}")
        logging.info("")

    # ------------------------------------------------------------------
    # Private helpers for write_plan
    # ------------------------------------------------------------------

    def _collect_orbnum_files(self) -> list:
        """Collect orbnum files from the orbnum directory.

        Skipped entirely in labeling mode or when ``orbnum_directory``
        is not set.

        :return: List of matched orbnum filenames to append to the plan.
        """
        if not self.setup.orbnum_directory or self.setup.args.faucet == "labels":
            return []

        result = []
        for orbnum_path in glob.glob(f"{self.setup.orbnum_directory}/*"):
            for orbnum in self.setup.orbnum:
                if re.match(orbnum["pattern"], orbnum_path.split(os.sep)[-1]):
                    logging.warning(f"-- Plan will include {orbnum_path}")
                    result.append(orbnum_path.split(os.sep)[-1])

        return result

    def _write_plan_file(self, plan_name: str, kernels: list) -> None:
        """Write kernel names to the .plan file, one per line.

        :param plan_name: Filename (not full path) of the plan file.
        :param kernels:   Ordered list of kernel filenames to write.
        """
        plan_path = Path(self.setup.working_directory) / plan_name
        with open(plan_path, "wt", encoding='utf-8') as handle:
            handle.write('\n'.join(kernels) + '\n')
