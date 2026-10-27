"""Implementation of the Release Plan class.
"""
import glob
import logging
import os
from pathlib import Path
import re

from .exceptions import NPBError
from ..utils import normalize_to_list


class ReleasePlan:
    """Class to represent the release plan.

    :param setup: NPB execution setup object.
    :param run_state: State of the current pipeline execution
    """
    def __init__(self, setup, run_state):
        """Constructor."""
        self.setup = setup
        self.run_state = run_state
        self.json_config = self.setup.kernel_list_config
        self._kernel_list = []
        self._plan_path = None

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

    @property
    def plan_path(self) -> Path | None:
        """Path of the plan file written by :meth:`write_plan`.

        ``None`` unless a plan with kernels has been generated. A plan
        written without kernels is not exposed.
        """
        return self._plan_path

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
            with open(plan, "w", encoding='utf-8') as pl:
                pl.write(plan.split(os.sep)[-1])

        elif plan.suffix != ".plan":
            raise NPBError(
                "Release plan requires *.plan extension. Single "
                "kernels are only allowed in labeling mode."
            )

        with open(plan, "r", encoding='utf-8') as f:
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
                        logging.warning('   %s', line.rstrip())

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
        candidates = self._get_candidate_kernels()

        kernels = self._collect_plan_files(candidates)

        # The kernel list is complete.
        plan_name = self._plan_name()
        self._write_plan_file(plan_name, kernels)

        if not kernels:

            line = "Inputs for the release not found"

            logging.warning('-- %s.', line)
            logging.info('')

            if not self.setup.args.silent and not self.setup.args.verbose:
                print("-- " + line.split(" - ", maxsplit=1)[-1] + ".")

            return False

        # Report the kernels that are included in the release plan.
        self._log_kernels_in_release_plan(kernels)
        self._kernel_list = kernels
        self._plan_path = Path(self.setup.working_directory, plan_name)

        # Add plan to the list of generated files.
        self.run_state.add_file(str(self._plan_path))

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
        logging.info('')
        logging.info('-- Reporting the products in Plan:')

        for kernel in kernels:
            logging.info('     %s', kernel)

        logging.info('')

    # ------------------------------------------------------------------
    # Private helpers for write_plan
    # ------------------------------------------------------------------

    def _get_candidate_kernels(self) -> list:
        """Gather the files that the release plan is built from.

        In labeling mode, with an input kernel provided, that kernel is the
        only candidate and is returned as given. Otherwise, every configured
        kernels directory is searched recursively and the paths are sorted.
        Any path containing ``.tm`` is dropped as a meta-kernel, so this also
        leaves out kernels under a directory such as ``foo.tmp``.

        :return: List of paths to the candidate kernel files.
        """
        if self.setup.args.faucet == "labels" and self.setup.args.plan:

            logging.info('-- Generate archiving plan from input kernel:')
            logging.info('   %s', self.setup.args.plan)

            kernels_in_dir = [self.setup.args.plan]

        else:
            logging.info('-- Generate archiving plan from kernel directory(ies):')

            kernels_in_dir = []
            for k_dir in self.setup.kernels_directory:
                logging.info('   %s', k_dir)

                # "**/*.*" digs into every subdirectory but only picks up files
                # that have an extension (a dot in the name).
                kernels_in_dir += glob.glob(f"{k_dir}/**/*.*", recursive=True)
            #
            # Filter out the meta-kernels from the automatically generated
            # list.
            #
            kernels_in_dir = [item for item in kernels_in_dir if ".tm" not in item]
            kernels_in_dir.sort()

        return kernels_in_dir

    def _collect_plan_files(self, candidates: list) -> list:
        """Build the list of files that make up the release plan.

        The candidates are filtered with the configured patterns, then the
        meta-kernel for the release is added (unless running in labeling
        mode) and finally the orbnum files.

        :param candidates: Paths of the kernels found for the release.
        :return: File names, in plan order: kernels, meta-kernels, orbnum.
        :raises NPBError: If a meta-kernel given in the configuration does
                          not exist.
        """
        # Filter the kernels with the patterns in the kernel list from the
        # configuration.
        patterns = self._get_patterns()

        kernels = []
        for kernel in candidates:
            kernel_name = Path(kernel).name

            for pattern in patterns:
                if re.match(pattern, kernel_name):
                    kernels.append(kernel_name)

                    # A kernel can match several patterns (for example its
                    # primary and its mapping one) but is listed only once.
                    break

        # Determine which meta-kernel, if any, gets added to the plan.
        # Skipped entirely in labeling mode. A meta-kernel provided via
        # configuration takes priority; otherwise one is inferred from the
        # existing bundle.
        if self.setup.args.faucet != "labels":
            kernels.extend(self._determine_metakernels(kernels, patterns))

        else:
            logging.info("-- Meta-kernels not generated in labeling mode.")

        # Add possible orbnum files if not running in label generation
        # mode.
        kernels.extend(self._collect_orbnum_files())
        return kernels

    def _determine_metakernels(self, kernels: list, patterns: list) -> list:
        """Return the meta-kernel file(s) to add to the plan.

        A meta-kernel provided via configuration takes priority; otherwise
        one is inferred from the existing bundle.

        :param kernels:  File names already selected for the plan.
        :param patterns: Kernel list patterns from the configuration.
        :return: Meta-kernel file names, in the order they are added.
        :raises NPBError: If a meta-kernel given in the configuration does
                          not exist.
        """
        if hasattr(self.setup, "mk_inputs"):
            return self._metakernel_from_config()

        return self._metakernel_inferred_from_bundle(kernels, patterns)

    def _metakernel_from_config(self) -> list:
        """Return the meta-kernel(s) given in the ``mk_inputs`` configuration.

        :return: File names of the configured meta-kernels.
        :raises NPBError: If a configured meta-kernel does not exist.
        """
        result = []

        mks = normalize_to_list(self.setup.mk_inputs["file"])
        for mk in mks:
            mk_new_name = mk.split(os.sep)[-1]

            # Accept mk as given, or fall back to resolving it against
            # the current working directory.
            if os.path.isfile(mk):
                mk_path = mk

            else:
                mk_path = os.getcwd() + os.sep + mk

            if os.path.isfile(mk_path):
                result.append(mk_new_name)

            else:
                raise NPBError("Meta-kernel provided via configuration "
                               f"{mk_new_name} does not exist."
                               )

        return result

    def _metakernel_inferred_from_bundle(self, kernels: list,
                                         patterns: list) -> list:
        """Return the next version of the latest meta-kernel in the bundle.

        :param kernels:  File names already selected for the plan.
        :param patterns: Kernel list patterns from the configuration.
        :return: The new meta-kernel file name, once per matching pattern,
                 or an empty list if none can be derived.
        """
        result = []

        # If no meta-kernel was provided via configuration, try to infer
        # the one that needs to be generated.
        bundle_files = Path(self.setup.bundle_directory).rglob("*")

        # Meta-kernels live under a directory literally named "mk" and
        # use the ".tm" extension.
        mks_in_dir = [
            p.name
            for p in bundle_files
            if "mk" in p.parts and p.suffix.lower() == ".tm"
        ]

        if not mks_in_dir:
            logging.warning(
                "-- No former meta-kernel found to generate "
                "meta-kernel for the list."
            )

        else:
            # A meta-kernel can only be generated from the bundle
            # information if there are kernels in the plan to base it
            # on.
            if kernels:

                # Filenames are zero-padded by version, so the
                # lexicographically greatest one is also the newest.
                mk_name = max(mks_in_dir)

                for pattern in patterns:
                    if re.match(pattern, mk_name):
                        version = re.findall(r"_v\d+", mk_name)[0]

                        # Strip the "_v" prefix, bump the number, and
                        # zero-pad back to the original width (e.g.
                        # "_v01" -> "_v02", "_v009" -> "_v010").
                        new_version = "_v" + str(int(version[2:]) + 1).zfill(
                            len(version) - 2
                        )

                        # Swap the old version substring for the new one
                        # inside the filename.
                        mk_new_name = mk_name.replace(version, new_version, 1)

                        logging.warning('-- Plan will include %s', mk_new_name)

                        result.append(mk_new_name)

            if not result:
                logging.error(
                    "-- No former meta-kernel found to generate "
                    "meta-kernel for the list."
                )

        return result

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

                    logging.warning('-- Plan will include %s', orbnum_path)

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
