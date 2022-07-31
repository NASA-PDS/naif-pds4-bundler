"""List Class and Child Class Implementation."""
import datetime
import glob
import json
import logging
import os
import re
import shutil

from ..utils import check_badchar
from ..utils import check_binary_endianness
from ..utils import check_consecutive
from ..utils import check_eol
from ..utils import check_kernel_integrity
from ..utils import check_line_length
from ..utils import check_list_duplicates
from ..utils import check_permissions
from ..utils import compare_files
from ..utils import extension_to_type
from ..utils import extract_comment
from ..utils import fill_template
from ..utils import product_mapping
from ..utils import spice_exception_handler
from .log import error_message


class List(object):
    """Class to generate the List.

    :param setup: NPB execution setup object
    :type setup: object
    """

    def __init__(self, setup: object) -> object:
        """Constructor."""
        self.files = []
        self.name = type
        self.setup = setup

    def add(self, element):
        """Add file to the list.

        :param element: SPICE Kernel product or ORBNUM product to be added to the list
        :type element: str
        """
        self.files.append(element)


class KernelList(List):
    """List child class to generate the Kernel List.

    :param setup: NPB execution setup object
    :type setup: object
    """

    def __init__(self, setup: object) -> object:
        """Constructor."""
        line = f"Step {setup.step} - Kernel List generation"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        List.__init__(self, setup)

        #
        # Object attributes to be replaced in template
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
        self.read_config()

    def add(self, kernel):
        """Add SPICE kernel or ORBNUM file to the list.

        :param kernel: SPICE kernel or ORBNUM file added to the list
        :type kernel: str
        """
        List.add(self, kernel)

    def read_config(self):
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

    def read_plan(self, plan):
        """Read Release Plan from the main module input.

        :param plan: Release Plan name
        :type plan: str
        """
        kernels = []

        #
        # Add mapping kernel patterns in list.
        #
        patterns = []
        for pattern in self.json_config:
            patterns.append(pattern)
            if "mapping" in self.json_config[pattern]:
                patterns.append(self.json_config[pattern]["mapping"])

        #
        # If NPB runs in labeling mode, a single file can be specified
        # as a release plan. If so, a plan is generated.
        #
        if (plan.split(".")[-1] != "plan") and (self.setup.args.faucet == "labels"):
            plan_name = (
                f"{self.setup.mission_acronym}_{self.setup.run_type}_"
                f"{int(self.setup.release):02d}.plan"
            )
            plan = self.setup.working_directory + os.sep + plan_name
            with open(plan, "w") as pl:
                pl.write(plan.split(os.sep)[-1])
        elif plan.split(".")[-1] != "plan":
            error_message(
                "Release plan requires *.plan extension. Single "
                "kernels are only allowed in labeling mode."
            )

        with open(plan, "r") as f:
            for line in f:
                ker_matched = False
                for pattern in patterns:
                    if re.search(pattern, line):
                        ker_line = re.search(pattern, line)

                        #
                        # The kernel is not matched if there is a comment character in front.
                        #
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
                            if re.search(pattern, line):
                                ker_line = re.search(pattern, line)
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

        #
        # Report the kernels that will be included in the Kernel List
        #
        logging.info("-- Reporting the products in Plan:")

        for kernel in kernels:
            logging.info(f"     {kernel}")

        logging.info("")

        self.kernel_list = kernels

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
            for dir in self.setup.kernels_directory:
                logging.info(f"   {dir}")

            kernels_in_dir = []
            for dir in self.setup.kernels_directory:
                kernels_in_dir += glob.glob(f"{dir}/**/*.*", recursive=True)
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
                    error_message(
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
                            version = re.findall(r"_v[0-9]+", mk_name)[0]
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

    @spice_exception_handler
    def write_list(self):
        """Write the Kernel List product.

        The list is not an archival product but an NPB by-product, therefore
        it is not generated by any of the product classes.
        """
        list_name = (
            f"{self.setup.mission_acronym}_{self.setup.run_type}_"
            f"{int(self.setup.release):02d}.kernel_list"
        )

        list_dictionary = vars(self)

        fill_template(
            self, self.setup.working_directory + os.sep + list_name, list_dictionary
        )

        with open(self.setup.working_directory + os.sep + list_name, "a+") as f:

            for kernel in self.kernel_list:
                ker_added_to_list = False
                #
                # Find the correspondence of the filename in the JSON file
                #
                for pattern in self.re_config:

                    if pattern.match(kernel):

                        #
                        # Description is the only mandatory field.
                        #
                        description = self.json_config[pattern.pattern]["description"]
                        try:
                            options = self.json_config[pattern.pattern][
                                "mklabel_options"
                            ]
                        except BaseException:
                            options = ""
                        try:
                            patterns = self.json_config[pattern.pattern]["patterns"]
                        except BaseException:
                            patterns = False
                        try:
                            mapping = self.json_config[pattern.pattern]["mapping"]
                        except BaseException:
                            mapping = ""

                        #
                        # "options" and "descriptions" require to substitute parameters derived from the filenames
                        # themselves or from the comments of the kernel.
                        #
                        if patterns:
                            for el in patterns:
                                if ("$" + el) in description or ("$" + el) in mapping:
                                    value = patterns[el]

                                    #
                                    # There are two distinct patterns:
                                    #    * extracted form the filename
                                    #    * defined in the configuration file.
                                    #
                                    if (
                                        "@pattern" in patterns[el]
                                        and patterns[el]["@pattern"].lower() == "kernel"
                                    ):
                                        #
                                        # When extracted from the filename, the keyword  is matched in between patterns.
                                        #

                                        #
                                        # First Turn the regex set into a single character to be able to know were in
                                        # the filename is.
                                        #
                                        patt_ker = value["#text"].replace("[0-9]", "$")
                                        patt_ker = patt_ker.replace("[a-z]", "$")
                                        patt_ker = patt_ker.replace("[A-Z]", "$")
                                        patt_ker = patt_ker.replace("[a-zA-Z]", "$")

                                        #
                                        # Split the resulting pattern to build up the indexes to extract the value
                                        # from the kernel name.
                                        #
                                        patt_split = patt_ker.split(f"${el}")

                                        #
                                        # Create a list with the length of each part.
                                        #
                                        indexes = []
                                        for element in patt_split:
                                            indexes.append(len(element))

                                        #
                                        # Extract the value with the index from the kernel name.
                                        #
                                        # TODO: This indexes work because the mapping kernel and the resulting kernel are in the same place!
                                        if len(indexes) == 2:
                                            value = kernel[
                                                indexes[0] : len(kernel) - indexes[1]
                                            ]
                                            if patterns[el]["@pattern"].isupper():
                                                value = value.upper()
                                        else:
                                            error_message(
                                                f"Kernel pattern for {kernel} not adept to write description. Remember a "
                                                "metacharacter cannot start or finish a kernel pattern."
                                            )

                                        if mapping:
                                            mapping = mapping.replace("$" + el, value)

                                    elif (
                                        "@file" in patterns[el]
                                        and patterns[el]["@file"].lower() == "comment"
                                    ):
                                        #
                                        # Extracting the value from the comment
                                        # area of the kernel. This is usually to
                                        # get the original kernel name.
                                        #
                                        # So far this method is implemented to accomodate MRO files
                                        #
                                        comment = extract_comment(
                                            self.setup.kernels_directory[0]
                                            + f"/{ extension_to_type(kernel.split('.')[-1])}/"
                                            + kernel
                                        )

                                        for line in comment:
                                            if patterns[el]["#text"] in line:
                                                value = line.strip()
                                                break

                                        if not isinstance(value, str):
                                            error_message(
                                                f"Kernel pattern not found in comment area of {kernel}."
                                            )

                                    else:
                                        #
                                        # For non-kernels the value is based
                                        # on the value within the tag that
                                        # needs to be provided by the user;
                                        # there is no way this can be done
                                        # automatically.
                                        #

                                        #
                                        # First we convert into a list in
                                        # case there is just one
                                        #
                                        patterns_el = patterns[el]
                                        if not isinstance(patterns_el, list):
                                            patterns_el = [patterns_el]
                                        for val in patterns_el:
                                            try:
                                                if val["@value"] in kernel:
                                                    value = val["#text"]
                                            except KeyError:
                                                error_message(
                                                    f"Error generating kernel list with {kernel}. "
                                                    f"Consider reviewing your NPB setup."
                                                )

                                        if isinstance(value, list) or isinstance(
                                            value, dict
                                        ):
                                            error_message(
                                                f"-- Kernel {kernel} description could not be updated with "
                                                f"pattern."
                                            )

                                    description = description.replace("$" + el, value)

                        if options:
                            for option in options.split():
                                if ("$" + "PHASES") in option:
                                    if hasattr(self.setup, "phases"):
                                        if list(self.setup.phases.keys())[0]:
                                            phases = self.setup.phases["phase"]["@name"]
                                        else:
                                            phases = "N/A"
                                    else:
                                        phases = "N/A"

                                    options = options.replace("$PHASES", phases)

                        #
                        # Reformat the description, given that format of the XML file is not restrictive (spaces or
                        # newlines might be present).
                        #
                        description = description.replace("\n", " ")
                        description = " ".join(description.split())

                        if self.setup.pds_version == "3":
                            kerdir = "data/" + extension_to_type(kernel)
                        else:
                            kerdir = "spice_kernels/" + extension_to_type(kernel)

                        if not options:
                            options = ""

                        f.write(f"FILE             = {kerdir}/{kernel}\n")
                        #
                        # Introduced to avoid trailing white space.
                        #
                        if not options:
                            f.write("MAKLABEL_OPTIONS =\n")
                        else:
                            f.write(f"MAKLABEL_OPTIONS = {options}\n")
                        f.write(f"DESCRIPTION      = {description}\n")

                        if mapping:

                            logging.info(f"-- Mapping {kernel} with {mapping}")
                            f.write(f"MAPPING          = {mapping}\n")

                        ker_added_to_list = True

                if not ker_added_to_list:
                    f.write(f"FILE             = miscellaneous/orbnum/{kernel}\n")
                    f.write("MAKLABEL_OPTIONS = N/A\n")
                    f.write("DESCRIPTION      = N/A\n")

        self.list_name = list_name

        self.validate()

    def read_list(self, kerlist):
        """Read the Kernel List.

        Note that the format that the kernel list has to follow is very
        strict, including no whitespace at the end of each line and Line-feed
        EOL.

        :param kerlist: Kernel List path
        :type kerlist: str
        """
        kernel_list = (
            f"{self.setup.working_directory}/"
            f"{self.setup.mission_acronym}_{self.setup.run_type}_"
            f"{int(self.setup.release):02d}.kernel_list"
        )

        try:
            shutil.copy2(kerlist, kernel_list)
        except shutil.SameFileError:
            pass

        self.list_name = kernel_list.split(os.sep)[-1]

        #
        # Generate the kernel list attribute, necessary for the validation.
        #
        kernels = []
        with open(kernel_list, "r") as lst:
            for line in lst:
                if "FILE             =" in line:
                    kernels.append(line.split(os.sep)[-1][:-1])

        self.kernel_list = kernels

        self.validate()

    def write_complete_list(self):
        """Write the complete Kernel List using the former ones."""
        line = f"Step {self.setup.step} - Generation of complete kernel list"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        kernel_lists = glob.glob(
            self.setup.working_directory
            + os.sep
            + f"{self.setup.mission_acronym}_release*"
            f".kernel_list"
        )

        #
        # Sort list in inverse order in such way that the DATASETID is
        # obtained from the header of the latest list.
        #
        kernel_lists.sort(reverse=True)

        complete_list = f"{self.setup.mission_acronym}_complete.kernel_list"

        release_list = []
        with open(self.setup.working_directory + os.sep + complete_list, "w+") as c:
            for kernel_list in kernel_lists:
                logging.info(f"-- Adding {kernel_list}")
                release_list.append(int(kernel_list.replace("_", ".").split(".")[-3]))
                with open(kernel_list, "r") as lst:
                    for line in lst:
                        c.write(line)

        if not check_consecutive(release_list):
            logging.warning(f"-- Incomplete Kernel lists available: {release_list}")

        self.complete_list = complete_list

        self.validate_complete()

    def validate(self):
        """Validation of the Kernel List.

        The validation of the Kernel List performs the following checks:

         * check that the list has the same number of ``FILE``, ``MAKLABEL_OPTIONS``,
           and ``DESCRIPTION`` entries.
         * check list against plan
         * check that list for duplicate files
         * check that all files listed in the list are on the ``kernels_directory``
         * check that the files are not in the ``bundle_directory``
         * display all the ``MAKLABL_OPTIONS`` used
         * check that all the ``MAKLBL_OPTIONS`` are in the template for PDS3
         * check that the list has no duplicates
         * check that the list has no bad characters
         * if the ``-d DIFF --diff DIFF`` argument is used, compare the kernel
           list with the kernel list of the previous release -if avaialble.
        """
        num_file = 0
        num_opti = 0
        num_desc = 0

        ker_in_list = []
        opt_in_list = []

        list_path = self.setup.working_directory + os.sep + self.list_name

        #
        # Check that the list has no bad characters.
        # This does not raise an error message but does not stop NPB.
        #
        errors = check_badchar(list_path)
        if errors:
            for err in errors:
                logging.error(f"   {err}")

        with open(list_path, "r") as lst:

            #
            # Check that the list has the same number of FILE,
            # MAKLABEL_OPTIONS, and DESCRIPTION entries
            #
            for line in lst:

                if ("FILE" in line) and (line.split("=")[-1].strip()):
                    num_file += 1
                    #
                    # We add kernels to compare plan and list and to look
                    # for duplicates.
                    #
                    ker_in_list.append(line.split("/")[-1].strip())

                elif "OPTIONS" in line:
                    num_opti += 1
                    #
                    # We add options to display and compare to template
                    #
                    options = line.split("=")[-1].split()
                    for option in options:
                        if option != "None":
                            opt_in_list.append(option)

                elif ("DESCRIPTION" in line) and (line.split("=")[-1].strip()):
                    num_desc += 1

            if (num_file != num_opti) or (num_opti != num_desc):
                error = "List does not have the same number of entries"
                logging.error(f"{error} for:")
                logging.error(f"   FILE             ({num_file})")
                logging.error(f"   MAKLABEL_OPTIONS ({num_opti})")
                logging.error(f"   DESCRIPTION      ({num_desc})")
                logging.error("")

                logging.error(
                    f"-- Display {self.setup.mission_name} kernel list "
                    f"configuration file to double-check."
                )
                for line in self.json_formatted_lst:
                    logging.info(line)
                logging.error("")

                raise Exception(error)

            #
            # Check list against plan.
            #
            for ker in ker_in_list:
                if ker not in self.kernel_list:
                    error_message(f"   {ker} not in list.")

            #
            # Check list for duplicate entries.
            #
            if check_list_duplicates(ker_in_list):
                error_message("List contains duplicates.")

            #
            # Check that all files listed are available in OPS area;
            # This does not raise an error but only a warning.
            #
            logging.info("-- Checking that kernels are present in: ")

            for dir in self.setup.kernels_directory:
                logging.info(f"   {dir}")

            present = False
            all_present = True
            for ker in ker_in_list:
                for dir in self.setup.kernels_directory:
                    #
                    # We cannot assume that the file is under a certain
                    # directory, it can be in any sub-directory.
                    #
                    file = [
                        os.path.join(root, name)
                        for root, dirs, files in os.walk(dir)
                        for name in files
                        if name == ker
                    ]
                    if file:
                        present = True
                if not present:
                    if ".tm" in ker:
                        logging.info(f"     {ker} not present as expected.")
                    else:
                        logging.warning(
                            f"     {ker} not present. Kernel might be mapped."
                        )
                        all_present = False
            if all_present:
                logging.info("     All kernels present.")
            logging.info("")

            #
            # Check that no file is in the final area.
            #
            present = False
            logging.info(
                f"-- Checking that kernels are present in "
                f"{self.setup.bundle_directory}:"
            )
            for ker in ker_in_list:
                if os.path.isfile(
                    self.setup.bundle_directory
                    + f"/{self.setup.mission_acronym}_spice/"
                    f"spice_kernels/" + extension_to_type(ker) + os.sep + ker
                ):
                    present = True
                    logging.warning(f"     {ker} present.")
            if not present:
                logging.info("     No kernels present in final area.")
            logging.info("")

            #
            # IF you generate a PDS23 data set, display all the MAKLABL_OPTIONS
            # used
            #
            if self.setup.pds_version == "3":
                opt_in_list = list(dict.fromkeys(opt_in_list))
                opt_in_list.sort()
                logging.info("-- Display all the MAKLABEL_OPTIONS:")
                for option in opt_in_list:
                    logging.info(f"     {option}")
                logging.info("")

            #
            # The PDS Mission Template file is not required for PDS4
            #
            if self.setup.pds_version == "3":
                logging.info(
                    "-- Check that all template tags used in the list are present in template:"
                )

                maklabel_options = self.setup.pds3_mission_template[
                    "maklabel_options"
                ].keys()

                for option in opt_in_list:
                    if option in maklabel_options:
                        logging.info(f"     {option} is present.")
                    else:
                        if option != "N/A":
                            error_message(f"{option} not in configuration.")

                logging.info("")

            #
            # Check complete list for duplicate entries
            #
            logging.info("-- Checking for duplicates in complete kernel list:")

            kernel_lists = glob.glob(
                self.setup.working_directory
                + os.sep
                + f"{self.setup.mission_acronym}_release*"
                f".kernel_list"
            )
            kernel_lists.sort()

            ker_in_list = []
            for kernel_list in kernel_lists:

                with open(kernel_list, "r") as lst:

                    #
                    # Check that the list has the same number of FILE,
                    # MAKLABEL_OPTIONS, and DESCRIPTION entries
                    #
                    logging.info(f"     Adding {kernel_list} in check.")

                    for line in lst:
                        if ("FILE" in line) and (line.split("=")[-1].strip()):
                            ker_in_list.append(line.split("/")[-1].strip())

            if check_list_duplicates(ker_in_list):
                error_message("List contains duplicates.")
            else:
                logging.info("     List contains no duplicates.")
            logging.info("")

        if self.setup.diff and self.setup.increment:
            #
            # Compare list with previous list
            #
            logging.info("-- Comparing current list with previous list:")

            logging.info("")
            fromfile = kernel_lists[-1]
            try:
                tofile = kernel_lists[-2]
                dir = self.setup.working_directory
                compare_files(fromfile, tofile, dir, self.setup.diff)
            except BaseException:
                logging.error("-- Previous list not available.")

    def validate_complete(self):
        """Validation of the complete Kernel List.

        The complete Kernel List is generated by NPB by merging all the
        available Kernel List files. These kernel list files must be located
        in the ``working_directory`` as specified by the NPB configuration.

        In principle all the kernels that have ever been added to the archive
        should be present.

        The validation of the complete Kernel List performs the following checks:

         * check that the list has the same number of ``FILE``, ``MAKLABEL_OPTIONS``,
           and ``DESCRIPTION`` entries
         * check all the ``MAKLABL_OPTIONS`` used
         * check that the list has no duplicates
        """
        num_file = 0
        num_opti = 0
        num_desc = 0

        ker_in_list = []
        opt_in_list = []

        with open(
            self.setup.working_directory + os.sep + self.complete_list, "r"
        ) as lst:

            #
            # Check that the list has the same number of FILE,
            # MAKLABEL_OPTIONS, and DESCRIPTION entries
            #
            logging.info("-- Checking list number of entries coherence:")

            for line in lst:

                if ("FILE" in line) and (line.split("=")[-1].strip()):
                    num_file += 1
                    #
                    # We add kernels to compare plan and list and to look
                    # for duplicates.
                    #
                    ker_in_list.append(line.split("/")[-1].strip())

                elif "OPTIONS" in line:
                    num_opti += 1
                    #
                    # We add options to display and compare to template
                    #
                    options = line.split("=")[-1].split()
                    for option in options:
                        opt_in_list.append(option)

                elif ("DESCRIPTION" in line) and (line.split("=")[-1].strip()):
                    num_desc += 1

            if (num_file != num_opti) or (num_opti != num_desc):
                error = "List does not have the same number of entries"
                logging.error(f"{error} for:")
                logging.error(f"   FILE             ({num_file})")
                logging.error(f"   MAKLABEL_OPTIONS ({num_opti})")
                logging.error(f"   DESCRIPTION      ({num_desc})")
                logging.error("")

                logging.error(
                    f"-- Display {self.setup.mission_name} kernel list "
                    f"configuration file to double-check."
                )
                for line in self.json_formatted_lst:
                    logging.info(line)
                logging.error("")

                raise Exception(error)
            else:
                logging.info(f"     PASS with total of {num_file} entries.")
                logging.info("")

            #
            # Check list for duplicate entries
            #
            logging.info("-- Checking for duplicates in kernel list:")
            if check_list_duplicates(ker_in_list):
                error_message("List contains duplicates.")
            else:
                logging.info("     List contains no duplicates.")
            logging.info("")

            #
            # Display all the MAKLABL_OPTIONS used if archive is PDS3.
            #
            if self.setup.pds_version == "3":
                opt_in_list = list(dict.fromkeys(opt_in_list))
                opt_in_list.sort()
                logging.info("-- Display all the MAKLABEL_OPTIONS:")
                for option in opt_in_list:
                    logging.info(f"     {option}")
                logging.info("")

            #
            # The PDS Mission Template file is not required for PDS4
            #
            if self.setup.pds_version == "3":
                logging.info(
                    "-- Check that all template tags used in the "
                    "list are present in template:"
                )
                template = (
                    self.setup.root_dir + f"/config/{self.setup.mission_acronym}"
                    f"_mission_template.pds"
                )
                with open(template, "r") as o:
                    template_lines = o.readlines()

                for option in opt_in_list:
                    present = False
                    for line in template_lines:
                        if "--" + option in line:
                            present = True
                    if present:
                        logging.info(f"     {option} is present.")
                    else:
                        error_message(f"{option} not in template.")

                logging.info("")

    def check_products(self):
        """Check the SPICE kernel and ORBNUM products from the kernel list.

        The products present in the Kernel List --whether if generated by NPB
        or provided by the user-- will be checked and if issues are found they
        will be reported as ``WARNING`` or ``ERROR`` messages.

        The checks performed to the products are the following:

         * identify if a SPICE kernel is present in multiple kernel directories
         * check End of Line character for text SPICE kernels and ORBNUM files.
         * check text SPICE kernels and ORBNUM files for non-ASCII characters.
         * check if text SPICE kernels have more than 80 characters per line.
         * validate kernel architecture
         * check endianness and permissions of binary kernels
        """
        line = f"Step {self.setup.step} - Check kernel list products"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # A products errors list and a warnings list will be created these
        # will be stored in a product dictionary. The error list will stop
        # the execution while the warnings list will only display warning
        # messages in the log.
        #
        product_errors = {}
        product_warnings = {}

        product_list = self.kernel_list

        for product in product_list:

            product_errors[product] = list()
            product_warnings[product] = list()

            #
            # Check if a product is present in multiple directories
            #
            # The origin_paths is a list that contains all the locations of
            # the product. In the case of an ORBNUM file it can only be one.
            #
            origin_paths = []

            #
            # Identify the path(s) of each product.
            #
            if (".nrb" in product.lower()) or (".orb" in product.lower()):
                origin_paths.append(self.setup.orbnum_directory + os.sep + product)
            else:
                for directory in self.setup.kernels_directory:
                    try:
                        file = [
                            os.path.join(root, ker)
                            for root, dirs, files in os.walk(directory)
                            for ker in files
                            if product == ker
                        ]
                        origin_paths.append(file[0])
                    except BaseException:
                        try:
                            file = [
                                os.path.join(root, ker)
                                for root, dirs, files in os.walk(directory)
                                for ker in files
                                if product_mapping(product, self.setup, cleanup=False)
                                == ker
                            ]
                            origin_paths.append(file[0])
                        except BaseException:
                            pass

            if not origin_paths and ".tm" not in product.lower():
                product_errors[product].append(
                    "Product not present in any kernel directory(ies)"
                )
                continue
            elif not origin_paths and ".tm" in product.lower():
                product_warnings[product].append(
                    "Meta-kernel will be generated during this run."
                )
                continue
            elif len(origin_paths) > 1:
                product_warnings[product].append(
                    "Product present in multiple directories:"
                )
                for path in origin_paths:
                    product_warnings[product].append(f"  {path}")
                product_warnings[product].append(
                    "The product in the first directory will be used."
                )

            #
            # From here on the product present in the first directory from
            # configuration will be checked.
            #
            origin_path = origin_paths[0]

            #
            # Check bad characters and EOL for text kernels and ORBNUM files.
            # Check line length < 80 for text kernels.
            #
            if product.split(".")[-1].strip()[0].lower() != "b":
                if (".nrb" not in product.lower()) and (".orb" not in product.lower()):
                    eol = "\n"
                elif (
                    (".nrb" in product.lower()) or (".orb" in product.lower())
                ) and self.setup.pds_version == "3":
                    eol = "\n"
                else:
                    eol = self.setup.eol

                error = check_eol(origin_path, eol)
                if error:
                    if (".nrb" in product.lower()) or (".orb" in product.lower()):
                        product_warnings[product].append(error)
                    else:
                        product_errors[product].append(error)

                error = check_badchar(origin_path)
                if error:
                    product_warnings[product] += error

                if (".nrb" not in product.lower()) and (".orb" not in product.lower()):
                    error = check_line_length(origin_path)
                    if error:
                        product_warnings[product] += error

            #
            # Check Kernel architecture.
            #
            if not (".nrb" in product.lower()) and not (".orb" in product.lower()):
                error = check_kernel_integrity(origin_path)
                if error:
                    product_errors[product].append(error)

            #
            # Check that file has read permissions.
            #
            check_permissions(origin_path)

            #
            # Check binary kernel endianness.
            #
            if product.split(".")[-1].strip()[0].lower() == "b":
                error = check_binary_endianness(origin_path)
                if error:
                    product_errors[product].append(error)

            #
            # Check kernel permissions
            #
            error = check_permissions(origin_path)
            if error:
                product_warnings[product] += error

        #
        # With all checks performed now they need to be reported.
        # Start for logging and/or verbose mode reporting.
        #
        error_flag = False
        warning_flag = False
        for product in product_list:
            if product_errors[product] or product_warnings[product]:
                logging.warning(f"-- {product}")
                warning_flag = True
                if product_warnings[product]:
                    for line in product_warnings[product]:
                        logging.warning(f"     {line}")
                if product_errors[product]:
                    error_flag = True
                    for line in product_errors[product]:
                        logging.error(f"     {line}")

        #
        # Report in standard output if necessary.
        #
        if not self.setup.args.silent and not self.setup.args.verbose:
            for product in product_list:
                if product_errors[product] or product_warnings[product]:
                    print(f"   * {product}")
                    warning_flag = True
                    if product_warnings[product]:
                        for line in product_warnings[product]:
                            print(f"     {line}")
                    if product_errors[product]:
                        error_flag = True
                        for line in product_errors[product]:
                            print(f"     {line}")

        if error_flag:
            if not self.setup.args.silent and not self.setup.args.verbose:
                print("-- Products listed above require work.")
            logging.error("")
            error_message("Products listed above require work.", self.setup)
        elif not warning_flag:
            logging.info("-- All products checks have succeeded.")
            logging.info("")
            if not self.setup.args.silent and not self.setup.args.verbose:
                print("-- All products checks have succeeded.")
