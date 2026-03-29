"""Implementation of the Metakernel file product class."""
import glob
import logging
import os
import re
import shutil
import subprocess
from collections import OrderedDict

import spiceypy

from .product import Product
from ...pipeline.runtime import handle_npb_error
from ...utils import check_line_length
from ...utils import ck_coverage
from ...utils import compare_files
from ...utils import current_date
from ...utils import et_to_date
from ...utils import extension_to_type
from ...utils import get_latest_kernel
from ...utils import match_patterns
from ...utils import mk_to_list
from ...utils import safe_make_directory
from ...utils import spice_exception_handler
from ...utils import spk_coverage
from ...utils import type_to_extension
from ..label import MetaKernelPDS4Label


class MetaKernelProduct(Product):
    """Class that represents a Metakernel file.

    :param setup:                    NPB execution setup object
    :param kernel:                   Metakernel path
    :param spice_kernels_collection: SPICE Kernel Collection
    :param user_input:               Indicates whether if the metakernel is
                                     provided by the user
    """

    def __init__(
        self,
        setup,
        kernel: str,
        spice_kernels_collection,
        user_input: bool = False,
    ) -> None:
        """Constructor."""
        if user_input:
            logging.info(f"-- Copy meta-kernel: {kernel}")
            self.path = kernel
        else:
            logging.info(f"-- Generate meta-kernel: {kernel}")
            self.template = f"{setup.templates_directory}/template_metakernel.tm"
            self.path = self.template

        self.new_product = True
        self.setup = setup
        self.collection = spice_kernels_collection
        self.file_format = "Character"

        if os.sep in kernel:
            self.name = kernel.split(os.sep)[-1]
        else:
            self.name = kernel

        self.extension = self.path.split(".")[1]

        self.type = extension_to_type(self.name)

        #
        # Add the configuration items for the meta-kernel.
        # This includes sorting out the meta-kernel name.
        #
        for metak in setup.mk:

            patterns = []
            for name in metak["name"]:
                name_pattern = name["pattern"]
                if not isinstance(name_pattern, list):
                    patterns.append(name_pattern)
                else:
                    patterns += name_pattern

            try:
                values = match_patterns(self.name, metak["@name"], patterns)
                self.mk_setup = metak
                self.version = values["VERSION"]
                self.values = values
                #
                # If it is a yearly meta-kernel we need the year to set
                # set the coverage of the meta-kernel.
                #
                if "YEAR" in values:
                    self.year = values["YEAR"]
                    self.YEAR = values["YEAR"]
            except BaseException:
                pass

        if not hasattr(self, "mk_setup"):
            handle_npb_error(
                f"Meta-kernel {self.name} has not been matched in configuration.",
                setup=self.setup,
            )

        if setup.pds_version == "3":
            self.collection_path = setup.staging_directory + os.sep + "extras" + os.sep
            product_path = self.collection_path + self.type + os.sep

            self.KERNELPATH = "./data"
        elif setup.pds_version == "4":
            self.collection_path = (
                setup.staging_directory + os.sep + "spice_kernels" + os.sep
            )
            product_path = self.collection_path + self.type + os.sep

            self.KERNELPATH = ".."

        self.AUTHOR = self.setup.producer_name

        if hasattr(self.setup, "secondary_missions"):
            if len(self.setup.secondary_missions) == 1:
                missions_text = (
                    f"{self.setup.mission_name} and {self.setup.secondary_missions[0]}"
                )
            else:
                missions_text = f"{self.setup.mission_name}, "
                for i in range(len(self.setup.secondary_missions)):
                    if i == len(self.setup.secondary_missions) - 1:
                        missions_text += f"and {self.setup.secondary_missions[i]}"
                    else:
                        missions_text += f"{self.setup.secondary_missions[i]}, "

            self.PDS4_MISSION_NAME = f"{missions_text}"
        else:
            self.PDS4_MISSION_NAME = f"{self.setup.mission_name}"

        if hasattr(self.setup, "creation_date_time"):
            self.MK_CREATION_DATE = current_date(date=self.setup.creation_date_time)
        else:
            self.MK_CREATION_DATE = current_date()
        self.SPICE_NAME = self.setup.spice_name
        self.INSTITUTION = self.setup.institution

        #
        # Generate the meta-kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # Name the meta-kernel; if the meta-kernel is manually provided this
        # step is skipped.
        #
        if user_input:
            self.name = kernel.split(os.sep)[-1]
            self.path = kernel
        else:
            self.path = product_path + self.name

        self.FILE_NAME = self.name

        #
        # Check product version if the current archive is not the
        # first release or if the mk_setup configuration section has been
        # provided.
        #
        if self.setup.increment and hasattr(self.setup, "mk_setup"):
            self.check_version()

        #
        # Generate the product LIDVID.
        #
        if self.setup.pds_version == "4":
            self.set_product_lid()
            self.set_product_vid()

            #
            # The meta-kernel must be named before fetching the description.
            #
            self.description = self.get_description()

        #
        # Generate the meta-kernel.
        #
        if not user_input:
            if os.path.exists(self.path):
                logging.warning(f"-- Meta-kernel already exists: {self.path}")
                logging.warning(
                    "-- The meta-kernel will be generated and the one "
                    "present in the staging are will be overwritten."
                )
                logging.warning(
                    "-- Note that to provide a meta-kernel as an input, "
                    "it must be provided via configuration file."
                )
            self.write_product()
        else:
            # Implement manual provision of meta-kernel.
            shutil.copy2(self.path, f"{product_path}{self.name}")
            self.path = f"{product_path}{self.name}"

        #
        # Compare the meta-kernels.
        #
        if self.setup.diff:
            self.compare()
        logging.info("")

        self.new_product = True

        #
        # Following the product generation we read the kernels again to
        # include all the kernels present.
        #
        self.collection_metakernel = mk_to_list(self.path, self.setup)

        if self.setup.pds_version == "4":
            #
            # Set the meta-kernel times
            #
            self.coverage()

            #
            # Extract the required information from the kernel list read from
            # configuration for the product.
            #
            (missions, observers, targets) = self.get_mission_and_observer_and_target(self.name)

            self.missions = missions
            self.targets = targets
            self.observers = observers

        super().__init__()

        if self.setup.pds_version == "4":
            logging.info("")
            logging.info(f"-- Labeling meta-kernel: {self.name}...")
            self.label = MetaKernelPDS4Label(setup, self)

    def check_version(self) -> None:
        """Check if the provided Meta-kernel version is correct."""
        #
        # Distinguish in between the different kernels we can find in the
        # previous increment.
        #
        pattern = self.mk_setup["@name"]
        for key in self.values:

            #
            # So far, only the pattern key YEAR is incorporated to sort out
            # the version of the meta-kernel name.
            #
            if key == "YEAR":
                pattern = pattern.replace("$" + key, self.year)
            else:
                pattern = pattern.replace("$" + key, "?" * len(self.values[key]))

        versions = glob.glob(
            f"{self.setup.bundle_directory}/"
            f"{self.setup.mission_acronym}_spice/"
            f"spice_kernels/mk/{pattern}"
        )

        versions.sort()
        try:
            version_index = pattern.find("?")

            version = versions[-1].split(os.sep)[-1]
            version = version[version_index : version_index + len(self.values[key])]
            version = int(version) + 1

            if version == int(self.version):
                logging.info(
                    f"-- Version from kernel list and from previous "
                    f"increment agree: {version}."
                )
            else:
                logging.warning(
                    "-- The meta-kernel version is not as expected "
                    "from previous increment."
                )
                logging.warning(
                    f"   Version set to: {int(self.version)}, whereas "
                    f"it is expected to be: {version}."
                )
                logging.warning(
                    "   It is recommended to stop the execution and fix the issue."
                )

        except BaseException:
            logging.warning("-- Meta-kernel from previous increment is not available.")
            logging.warning(f"   Version will be set to: {self.version}.")

    def set_product_lid(self) -> None:
        """Set the Meta-kernel LID."""
        if self.type == "mk":
            name = self.name.split("_v")[0]
        else:
            name = self.name

        product_lid = "{}:spice_kernels:{}_{}".format(
            self.setup.logical_identifier, self.type, name
        ).lower()

        self.lid = product_lid

    def set_product_vid(self) -> None:
        """Set the Meta-kernel VID.

        If the meta-kernel has been automatically generated as indicated in
        the configuration file, it has a version attribute, otherwise it does
        not and its version number must be equal to the expected VID.
        """
        try:
            product_vid = str(self.version).lstrip("0") + ".0"
        except BaseException:
            logging.warning(
                f"-- {self.name} No VID explicit in kernel name: set to 1.0"
            )
            logging.warning(
                "-- Make sure that the MK pattern in the "
                "configuration file is correct, if manually provided make sure "
                "you provided the appropriate name."
            )
            product_vid = "1.0"

            #
            # Implement this exceptional check for first releases of an archive.
            #
            if "01" not in self.name:
                handle_npb_error(
                    f"{self.name} version does not correspond to VID "
                    f"1.0. Rename the MK accordingly.",
                    setup=self.setup,
                )

        self.vid = product_vid

    def get_description(self) -> str:
        """Obtain the kernel product description information."""
        description = ""
        self.json_config = self.setup.kernel_list_config

        kernel = self.name
        for pattern in self.setup.re_config:

            if pattern.match(kernel):

                description = self.json_config[pattern.pattern]["description"]
                try:
                    patterns = self.json_config[pattern.pattern]["patterns"]
                except BaseException:
                    patterns = False
                # try:
                #     options = self.json_config[pattern.pattern]["mklabel_options"]
                # except BaseException:
                #     options = ""
                # try:
                #     mapping = self.json_config[pattern.pattern]["mapping"]
                # except BaseException:
                #     mapping = ""

                #
                # ``options'' and ``descriptions'' require substituting
                # parameters derived from the filenames
                # themselves.
                #
                if patterns:
                    for el in patterns:
                        if ("$" + el) in description:
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
                                # When extracted from the filename, the
                                # keyword is matched in between patterns.
                                #

                                #
                                # First Turn the regex set into a single
                                # character to be able to know were in the
                                # filename is.
                                #
                                patt_ker = value["#text"].replace("[0-9]", "$")
                                patt_ker = patt_ker.replace("[a-z]", "$")
                                patt_ker = patt_ker.replace("[A-Z]", "$")
                                patt_ker = patt_ker.replace("[a-zA-Z]", "$")

                                #
                                # Split the resulting pattern to build up the
                                # indexes to extract the value from the kernel
                                # name.
                                #
                                patt_split = patt_ker.split(f"${el}")

                                #
                                # Create a list with the length of each part.
                                #
                                indexes = []
                                for element in patt_split:
                                    indexes.append(len(element))

                                #
                                # Extract the value with the index from the
                                # kernel name.
                                #
                                if len(indexes) == 2:
                                    value = kernel[
                                        indexes[0] : len(kernel) - indexes[1]
                                    ]
                                    if patterns[el]["@pattern"].isupper():
                                        value = value.upper()
                                        #
                                        # Write the value of the pattern for
                                        # future use.
                                        #
                                        patterns[el]["&value"] = value
                                else:
                                    handle_npb_error(
                                        f"Kernel pattern {patt_ker} "
                                        f"not adept to write "
                                        f"description. Remember a "
                                        f"metacharacter "
                                        f"cannot start or finish "
                                        f"a kernel pattern.",
                                        setup=self.setup,
                                    )
                            else:
                                #
                                # For non-kernels the value is based on the
                                # value within the tag that needs to be
                                # provided by the user; there is no way this
                                # can be done automatically.
                                #
                                for val in patterns[el]:
                                    if kernel == val["@value"]:
                                        value = val["#text"]
                                        #
                                        # Write the value of the pattern for
                                        # future use.
                                        #
                                        patterns[el]["&value"] = value

                                if isinstance(value, list):
                                    handle_npb_error(
                                        f"-- Kernel description "
                                        f"could not be updated with "
                                        f"pattern: {value}.",
                                        setup=self.setup,
                                    )

                            description = description.replace("$" + el, value)

        description = description.replace("\n", "")
        while "  " in description:
            description = description.replace("  ", " ")

        if not description:
            handle_npb_error(
                f"{self.name} does not have a description on configuration file.",
                setup=self.setup,
            )

        return description

    def write_product(self) -> None:
        """Write the Meta-kernel."""
        #
        # Obtain meta-kernel grammar from configuration.
        #
        if "grammar" not in self.mk_setup:
            handle_npb_error(
                f"Meta-kernel grammar not defined in configuration for {self.name}"
            )
        kernel_grammar_list = self.mk_setup["grammar"]["pattern"]

        #
        # Obtain meta-kernel grammar left padding. If not included in
        # configuration padding is set to True.
        #
        if "padding" in self.mk_setup["grammar"]:
            kernel_grammar_padding = self.mk_setup["grammar"]["padding"]
            if kernel_grammar_padding.lower() == "true":
                padding = " "
                logging.info("-- Left padding applied to kernels entries in MK.")
            elif kernel_grammar_padding.lower() == "false":
                padding = ""
                logging.info("-- No left padding applied to kernels entries in MK.")
            else:
                logging.warning(
                    f"-- Padding value in NPB configuration file MK grammar is "
                    f"{kernel_grammar_padding}"
                )
                logging.warning(
                    "   The value should be 'True' or 'False'. Case is not relevant. "
                )
        else:
            padding = " "

        #
        # We scan the kernel directory to obtain the list of available kernels
        #
        kernel_type_list = ["lsk", "pck", "fk", "ik", "sclk", "spk", "ck", "dsk"]

        #
        # Setup the end-of-line character
        #
        eol = self.setup.eol_mk

        #
        # All the files of the directory are read into a list
        #
        mkgen_kernels = []
        excluded_kernels = []

        for kernel_type in kernel_type_list:

            #
            # First we build the list of excluded kernels
            #
            for kernel_grammar in kernel_grammar_list:
                if "exclude:" in kernel_grammar:
                    excluded_kernels.append(kernel_grammar.split("exclude:")[-1])

            logging.info(
                f"     Matching {kernel_type.upper()}(s) with meta-kernel grammar."
            )
            for kernel_grammar in kernel_grammar_list:

                if "date:" in kernel_grammar:
                    kernel_grammar = kernel_grammar.split("date:")[-1]
                    dates = True
                else:
                    dates = False

                #
                # Kernels can come from several kernel directories or from the
                # previous meta-kernel. Paths are provided by the parameter
                # paths and meta-kernels with mks.
                #
                paths = []
                mks = []
                if kernel_grammar.split(".")[-1].lower() in type_to_extension(
                    kernel_type
                ):
                    try:
                        if self.setup.pds_version == "3":
                            paths.append(self.setup.staging_directory + "/DATA")

                        else:
                            paths.append(
                                self.setup.staging_directory + "/spice_kernels"
                            )
                        # paths.append(self.setup.kernels_directory)

                        #
                        # Try to look for meta-kernels from previous
                        # increments.
                        #
                        try:
                            mks = glob.glob(
                                f"{self.setup.bundle_directory}/"
                                f"{self.setup.mission_acronym}"
                                f"_spice/spice_kernels/mk/"
                                f'{self.name.split("_v")[0]}*.tm'
                            )
                        except BaseException:
                            if self.setup.increment:
                                logging.warning(
                                    "-- No meta-kernels from "
                                    "previous increment "
                                    "available."
                                )

                        latest_kernel = get_latest_kernel(
                            kernel_type,
                            paths,
                            kernel_grammar,
                            dates=dates,
                            excluded_kernels=excluded_kernels,
                            mks=mks,
                        )
                    except Exception as e:
                        logging.warning(f"-- Exception: {e}")
                        latest_kernel = []

                    if latest_kernel:
                        if not isinstance(latest_kernel, list):
                            latest_kernel = [latest_kernel]

                        for kernel in latest_kernel:
                            logging.info(f"        Matched: {kernel}")
                            mkgen_kernels.append(kernel_type + "/" + kernel)

        #
        # Remove duplicate entries from the kernel list (possible depending on
        # the grammar).
        #
        mkgen_kernels = list(OrderedDict.fromkeys(mkgen_kernels))

        #
        # Subset the SPICE kernels collection with the kernels in the MK
        # only.
        #
        collection_metakernel = []
        for spice_kernel in self.collection.product:
            for name in mkgen_kernels:
                if spice_kernel.name in name:
                    collection_metakernel.append(spice_kernel)

        self.collection_metakernel = collection_metakernel

        #
        # Report kernels present in meta-kernel
        #
        logging.info("")
        logging.info("-- Archived kernels present in meta-kernel")
        for kernel in collection_metakernel:
            logging.info(f"     {kernel.name}")
        logging.info("")

        num_ker_total = len(self.collection.product)
        num_ker_mk = len(collection_metakernel)

        if num_ker_total != num_ker_mk:
            logging.warning(f"-- Archived kernels:           {num_ker_total}")
            logging.warning(f"-- Kernels in meta-kernel:     {num_ker_mk}")
        else:
            logging.info(f"-- Archived kernels:           {num_ker_total}")
            logging.info(f"-- Kernels in meta-kernel:     {num_ker_mk}")

        #
        # The kernel list for the new mk is formatted accordingly
        #
        kernels = ""
        kernel_dir_name = None
        for kernel in mkgen_kernels:

            if kernel_dir_name:
                if kernel_dir_name != kernel.split(".")[1]:
                    kernels += eol

            kernel_dir_name = kernel.split(".")[1]

            kernels += f"{padding * 26}'$KERNELS/{kernel}'{eol}"

        self.KERNELS_IN_METAKERNEL = kernels

        #
        # Introduce and curate the rest of fields from configuration
        #
        if "data" in self.mk_setup["metadata"]:
            data = self.mk_setup["metadata"]["data"]
        else:
            data = ""
        if "description" in self.mk_setup["metadata"]:
            desc = self.mk_setup["metadata"]["description"]
        else:
            desc = ""

        curated_data = ""
        curated_desc = ""

        first_line = True
        for line in data.split("\n"):
            #
            # We want to remove the blanks if the line is empty.
            #
            if line.strip() == "":
                curated_data += ""
            else:
                if first_line:
                    curated_data += eol
                first_line = False
                curated_data += " " * 6 + line.strip() + eol

        metakernel_dictionary = vars(self)

        for line in desc.split("\n"):
            #
            # We want to remove the blanks if the line is empty, and replace
            # any possible keywords.
            #
            if line.strip() == "":
                curated_desc += eol
            else:
                for key, value in metakernel_dictionary.items():
                    if (
                        isinstance(value, str)
                        and key.isupper()
                        and key in line
                        and "$" in line
                    ):
                        line = line.replace("$" + key, value)
                curated_desc += " " * 3 + line.strip() + eol

        self.DATA = curated_data
        self.DESCRIPTION = curated_desc

        metakernel_dictionary = vars(self)

        with open(self.path, "w+") as f:
            with open(self.template, "r") as t:
                for line in t:
                    line = line.rstrip()
                    for key, value in metakernel_dictionary.items():
                        if (
                            isinstance(value, str)
                            and key.isupper()
                            and key in line
                            and "$" in line
                        ):
                            line = line.replace("$" + key, value)
                    f.write(line + eol)

        self.product = self.path

        logging.info("-- Meta-kernel generated.")
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(
                "   * Created "
                f"{self.product.split(self.setup.staging_directory)[-1]}."
            )

        #
        # If the meta-kernel has been generated by NPB with a given grammar,
        # etc. pause the pipeline to allow the user to introduce changes.
        #
        if hasattr(self, "mk_setup") and not self.setup.args.debug:
            if hasattr(self, "mk_setup"):
                if "interrupt_to_update" in self.mk_setup:
                    if self.mk_setup["interrupt_to_update"].lower() == "true":
                        print(
                            "    * The meta-kernel might need to be updated. You can:"
                        )
                        print(
                            '        - Type "vi" and press ENTER to edit the '
                            "file with the VI text editor."
                        )
                        print(
                            "        - Edit the file with your favorite edit "
                            "and press ENTER and continue."
                        )
                        print("        - Press ENTER to continue.")
                        print(f"      MK path: {self.path}")

                        inp = input(">> Type 'vi' and/or press ENTER to continue... ")
                        if str(inp).lower() == "vi":
                            try:
                                cmd = os.environ.get("EDITOR", "vi") + " " + self.path
                                subprocess.call(cmd, shell=True)
                                logging.warning(
                                    "-- Meta-kernel edited with Vi by the user."
                                )
                            except BaseException:
                                print("Vi text editor is not available.")
                                input(">> Press Enter to continue... ")

    def compare(self) -> None:
        """**Compare the Meta-kernel with the previous version**.

        The MK is compared with a previous version of the MK. If no prior
        MK is found, the new MK is compared to NPB's MK template.
        """
        val_mk = ""

        #
        # Compare meta-kernel with latest. First try with previous increment.
        #
        try:
            match_flag = True
            val_mk_path = (
                f"{self.setup.bundle_directory}/"
                f"{self.setup.mission_acronym}_spice/spice_kernels/mk/"
            )

            val_mk_name = self.name.split(os.sep)[-1]
            i = 1

            while match_flag:
                if i < len(val_mk_name) - 1:
                    val_mks = glob.glob(val_mk_path + val_mk_name[0:i] + "*.tm")
                    if val_mks:
                        val_mks = sorted(val_mks)
                        val_mk = val_mks[-1]
                        match_flag = True
                    else:
                        match_flag = False
                    i += 1

            if not val_mk:
                raise Exception("No label for comparison found.")

        except BaseException:
            #
            # If previous increment does not work, compare with the MK
            # template.
            #
            logging.warning(f"-- No other version of {self.name} has been found.")
            logging.warning("-- Comparing with meta-kernel template.")

            val_mk = f"{self.setup.templates_directory}/template_metakernel.tm"

        fromfile = self.path
        tofile = val_mk
        work_dir = self.setup.working_directory

        logging.info(
            f"-- Comparing "
            f'{self.name.split(f"{self.setup.mission_acronym}_spice/")[-1]}'
            f"..."
        )
        compare_files(fromfile, tofile, work_dir, self.setup.diff)

    def validate(self) -> None:
        """Perform a basic validation of the Meta-kernel.

        The validation consists of:

           * load the kernel with the SPICE API ``FURNSH``
           * count the loaded kernels with SPICE API ``KTOTAL``
           * compare the number of kernels in the kernel pool with the length
             of the MK collection list attribute
           * check that line lengths are less than 80 characters
        """
        line = f"Step {self.setup.step} - Meta-kernel {self.name} validation"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        rel_path = self.path.split(f"/{self.setup.mission_acronym}_spice/")[-1]
        path = (
            self.setup.bundle_directory.split(f"{self.setup.mission_acronym}_spice")[0]
            + f"/{self.setup.mission_acronym}_spice/"
            + rel_path
        )

        cwd = os.getcwd()
        mkdir = os.sep.join(path.split(os.sep)[:-1])
        os.chdir(mkdir)

        spiceypy.kclear()
        try:
            spiceypy.furnsh(path)

            #
            # In KTOTAL, all meta-kernels are counted in the total; therefore
            # we need to subtract 1 kernel.
            #
            ker_num_fr = spiceypy.ktotal("ALL") - 1
            ker_num_mk = self.collection_metakernel.__len__()

            logging.info(f"-- Kernels loaded with FURNSH: {ker_num_fr}")
            logging.info(f"-- Kernels present in {self.name}: {ker_num_mk}")

            if ker_num_fr != ker_num_mk:
                spiceypy.kclear()
                logging.error(
                    "-- Number of kernels loaded is not equal to kernels "
                    "present in meta-kernel.",
                )

        except BaseException:
            logging.error("-- The MK could not be loaded with the SPICE API FURNSH.")

        spiceypy.kclear()

        line_length_errors = check_line_length(path)
        if line_length_errors:
            logging.warning(
                "-- The MK has lines with length longer than 80 characters:"
            )
            for line in line_length_errors:
                logging.warning(f"   {line}")

        os.chdir(cwd)

    @spice_exception_handler
    def coverage(self) -> None:
        """Determine Meta-kernel coverage.

        Meta-kernel coverage is determined by:

        *  for whole mission meta-kernels ``start_date_time`` and ``stop_date_time``
           are set to the coverage provided by spacecraft SPK, CKs, or to other
           dates at the discretion of the archive producer. These other dates might
           be required for missions whose SPks and CKs do not explicitly cover the
           dates required by the archive, e.g.: a lander mission with a fixed
           position provided by an SPK with extended coverage

        *  for yearly mission meta-kernels ``start_date_time`` and ``stop_date_time``
           are set to the coverage from ``Jan 1 00:00`` of the year to either the
           end of coverage provided by spacecraft SPK or CKs, or the end of
           the year (whichever is earlier)
        """
        kernels = []
        self.mk_sets_coverage = False
        #
        # Match the pattern with the kernels in the meta-kernel.
        # Only the kernel patterns identified with the meta-kernel attribute
        # will be used.
        #
        if "coverage_kernels" in self.mk_setup:
            coverage_kernels = self.mk_setup["coverage_kernels"]
            patterns = coverage_kernels["pattern"]
            if not isinstance(patterns, list):
                patterns = [patterns]

            #
            # It is assumed that the coverage kernel is present in the
            # meta-kernel.
            #
            for pattern in patterns:
                #
                # Only match coverage kernels that have the MK pattern in the
                # mk attribute.
                #
                for kernel in self.collection_metakernel:
                    if re.match(pattern, kernel):
                        kernels.append(kernel)
                        self.mk_sets_coverage = True

        start_times = []
        finish_times = []
        if kernels:
            #
            # Look for the identified kernel in the collection, if the kernel
            # is not present the coverage will have to be computed.
            #
            if kernels:
                for kernel in kernels:
                    ker_found = False
                    for product in self.collection.product:
                        if kernel == product.name:
                            start_times.append(spiceypy.utc2et(product.start_time[:-1]))
                            finish_times.append(spiceypy.utc2et(product.stop_time[:-1]))
                            ker_found = True

                    #
                    # When the kernels are not present in the current
                    # collection, the coverage is computed.
                    #
                    if not ker_found:
                        path = (
                            f"{self.setup.bundle_directory}/"
                            f"{self.setup.mission_acronym}_spice/"
                            f"spice_kernels/"
                            f"{extension_to_type(kernel)}/{kernel}"
                        )

                        #
                        # Added check of file size for test cases.
                        #
                        if not os.path.exists(path) or os.path.getsize(path) == 0:
                            logging.warning(
                                f"-- File not present in final area: {path}."
                            )
                            logging.warning(
                                "   It will not be used to determine the coverage."
                            )
                        else:
                            if extension_to_type(kernel) == "spk":
                                (start_time, stop_time) = spk_coverage(
                                    path, main_name=self.setup.spice_name
                                )
                            elif extension_to_type(kernel) == "ck":
                                (start_time, stop_time) = ck_coverage(path)
                            else:
                                handle_npb_error(
                                    "Kernel used to determine "
                                    "coverage is not a SPK or CK "
                                    "kernel.",
                                    setup=self.setup,
                                )

                            start_times.append(spiceypy.utc2et(start_time[:-1]))
                            finish_times.append(spiceypy.utc2et(stop_time[:-1]))

                            logging.info(
                                f"-- File {kernel} used to determine coverage."
                            )

        #
        # If it is a yearly meta-kernel; we need to handle it separately.
        #
        if hasattr(self, "year") and start_times and finish_times:

            #
            # The date can be January 1st, of the year or the mission start
            # date, but it should not be later or earlier than that.
            #
            et_mission_start = spiceypy.utc2et(self.setup.mission_start[:-1])
            et_year_start = spiceypy.utc2et(f"{self.year}-01-01T00:00:00")

            if et_year_start > et_mission_start:
                start_times = [et_year_start]
            else:
                start_times = [et_mission_start]

            #
            # Update the end time of the meta-kernel
            #
            et_year_stop = spiceypy.utc2et(f"{int(self.year) + 1}-01-01T00:00:00")

            if max(finish_times) > et_year_stop:
                finish_times = [et_year_stop]

        if self.mk_sets_coverage:
            logging.info(
                "-- Meta-kernel will be used to determine SPICE Collection coverage."
            )
        else:
            logging.warning(
                (
                    "-- Meta-kernel will not be used to determine "
                    "SPICE Collection coverage."
                )
            )

        try:

            start_time = spiceypy.et2utc(min(start_times), "ISOC", 3, 80) + "Z"
            stop_time = spiceypy.et2utc(max(finish_times), "ISOC", 3, 80) + "Z"
            logging.info(f"-- Meta-kernel coverage: {start_time} - {stop_time}")

        except BaseException:
            #
            # The alternative is to set the increment times to the increment
            # or mission times provided via configuration.
            #
            if hasattr(self, "year"):

                #
                # In the case of yearly kernels the coverage must be constrained
                # within the limits of the year.
                #
                et_mission_start = spiceypy.utc2et(self.setup.mission_start[:-1])
                et_mission_finish = spiceypy.utc2et(self.setup.mission_finish[:-1])
                et_incremn_finish = spiceypy.utc2et(self.setup.increment_finish[:-1])
                et_year_start = spiceypy.utc2et(f"{self.year}-01-01T00:00:00")

                if et_year_start > et_mission_start and (
                    self.year == self.setup.mission_start[:4]
                ):
                    start_time = self.setup.mission_start
                else:
                    start_time = f"{self.year}-01-01T00:00:00Z"

                et_year_stop = spiceypy.utc2et(f"{int(self.year) + 1}-01-01T00:00:00")

                if et_incremn_finish < et_year_stop and (
                    self.year == self.setup.increment_finish[:4]
                ):
                    stop_time = self.setup.increment_finish
                elif et_mission_finish < et_year_stop:
                    stop_time = self.setup.mission_finish
                else:
                    stop_time = f"{int(self.year) + 1}-01-01T00:00:00Z"

                logging.warning(
                    f"-- No kernel(s) found to determine MK coverage. "
                    f"Times from configuration in accordance to yearly MK "
                    f"will be used: {start_time} - {stop_time}"
                )

                self.start_time = start_time
                self.stop_time = stop_time

                return
            else:
                if hasattr(self.setup, "increment_start"):
                    start_time = self.setup.increment_start
                else:
                    start_time = self.setup.mission_start

                if hasattr(self.setup, "increment_finish"):
                    stop_time = self.setup.increment_finish
                else:
                    stop_time = self.setup.mission_finish

                logging.warning(
                    f"-- No kernel(s) found to determine MK coverage. "
                    f"Times from configuration will be used: {start_time} - {stop_time}"
                )

                self.start_time = start_time
                self.stop_time = stop_time

        else:

            #
            # The obtained start and stop times for the meta-kernel might need
            # to be corrected for the increment start and stop times provided
            # via configuration.
            #
            if hasattr(self.setup, "increment_start"):
                if hasattr(self, "year"):
                    #
                    # Check if the increment start year is the same as the yearly
                    # MK. If so update it.
                    #
                    if self.setup.increment_start[0:4] == start_time[0:4]:
                        start_time = self.setup.increment_start
                        logging.warning(
                            f"-- Coverage start time corrected with "
                            f"increment start from configuration file to: {start_time}"
                        )
                else:
                    start_time = self.setup.increment_start
                    logging.warning(
                        f"-- Coverage start time corrected with "
                        f"increment start from configuration file to: {start_time}"
                    )

            if hasattr(self.setup, "increment_finish"):
                if hasattr(self, "year"):
                    #
                    # Check if the increment finish year is the same as the yearly
                    # MK. If so update it.
                    #
                    if self.setup.increment_finish[0:4] == stop_time[0:4]:
                        stop_time = self.setup.increment_finish
                        logging.warning(
                            f"-- Coverage finish time corrected with "
                            f"increment finish from configuration file to: {stop_time}"
                        )
                else:
                    stop_time = self.setup.increment_finish
                    logging.warning(
                        f"-- Coverage finish time corrected with "
                        f"increment finish from configuration file to: {stop_time}"
                    )

            #
            # Re-format the time accordingly. The 'Z' is removed from the UTC
            # string since it is not supported until the SPICE Toolkit N0067.
            #
            if self.setup.pds_version == "3":
                system = "TDB"
            else:
                system = "UTC"
            (start_time, stop_time) = et_to_date(
                spiceypy.utc2et(start_time[:-1]),
                spiceypy.utc2et(stop_time[:-1]),
                self.setup.date_format,
                system=system,
            )

            self.start_time = start_time
            self.stop_time = stop_time
