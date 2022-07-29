"""Setup Class Implementation."""
import datetime
import glob
import logging
import os
import re
import shutil
import sys
from os.path import dirname
from pathlib import Path
from xml.etree import cElementTree as ET

import requests
import spiceypy
import xmlschema

from ..utils import etree_to_dict
from ..utils import kernel_name
from ..utils import spice_exception_handler
from .log import error_message
from .object import Object


class Setup(object):
    """Class that parses and processes the NPB XML configuration file.

    :param args: Parameters arguments from NPB main function
    :type args: object
    :param version: NPB version
    :type version: str
    """

    def __init__(self, args: Object, version: str) -> object:
        """Constructor."""
        try:
            #
            # Check that the configuration file validates with its schema
            #
            schema = xmlschema.XMLSchema11(
                dirname(__file__) + "/../data/configuration.xsd"
            )
            schema.validate(args.config)

        except Exception as inst:
            if not args.debug:
                print(inst)
            raise

        #
        # Converting XML setup file into a dictionary and then into
        # attributes for the object.
        #
        config = Path(args.config).read_text()
        entries = etree_to_dict(ET.XML(config))

        #
        # Re-arrange the resulting dictionary into one-level attributes
        # adept to be used (as if we were loading a JSON file).
        #
        config = entries["naif-pds4-bundler_configuration"]

        self.__dict__.update(config["pds_parameters"])
        self.__dict__.update(config["bundle_parameters"])
        self.__dict__.update(config["mission_parameters"])
        self.__dict__.update(config["directories"])

        #
        # Re-arrange secondary spacecrafts and secondary targets parameters.
        #
        if hasattr(self, "secondary_observers"):
            if not isinstance(self.secondary_observers["observer"], list):
                self.secondary_observers = [self.secondary_observers["observer"]]
            else:
                self.secondary_observers = self.secondary_observers["observer"]

        if hasattr(self, "secondary_targets"):
            if not isinstance(self.secondary_targets["target"], list):
                self.secondary_targets = [self.secondary_targets["target"]]
            else:
                self.secondary_targets = self.secondary_targets["target"]

        #
        # Kernel directory needs to be turned into a list.
        #
        if not isinstance(self.kernels_directory, list):
            self.kernels_directory = [self.kernels_directory]

        #
        # Generate empty orbnum directory if not present.
        #
        if not hasattr(self, "orbnum_directory"):
            self.orbnum_directory = ""

        #
        # Kernel list configuration needs refactoring.
        #
        self.__dict__.update(config["kernel_list"])

        kernel_list_config = {}
        for ker in self.kernel:
            kernel_list_config[ker["@pattern"]] = ker

        self.kernel_list_config = kernel_list_config
        del self.kernel

        #
        # Meta-kernel configuration; if there is one meta-kernel
        # mk is a dictionary, otherwise it is a list of dictionaries.
        # It is processed in such a way that it is always a list of
        # dictionaries. Same applies to meta-kernels from configuration
        # as user input.
        #
        self.__dict__.update(config["meta-kernel"])

        if hasattr(self, "mk"):
            if isinstance(self.mk, dict):
                self.mk = [self.mk]

        #
        # Meta-kernel configuration; if there is one pattern for
        # the meta-kernel name, convert it into a list of
        # dictionaries.
        #
        if hasattr(self, "mk"):
            for i in range(len(self.mk)):
                if isinstance(self.mk[i]["name"], dict):
                    self.mk[i]["name"] = [self.mk[i]["name"]]

        #
        # Meta-kernel configuration; if there is one coverage kernel, convert
        # it into a list of coverage kernels.
        #
        if hasattr(self, "coverage_kernels"):
            if isinstance(self.coverage_kernels, dict):
                self.coverage_kernels = [self.coverage_kernels]

        #
        # ORBNUM configuration: if there is one orbnum file orbnum is a
        # dictionary, otherwise it is a list of dictionaries. It is
        # processed in such a way that it is always a list of dictionaries
        #
        if "orbit_number_file" in config:
            self.__dict__.update(config["orbit_number_file"])
            if isinstance(self.orbnum, dict):
                self.orbnum = [self.orbnum]

        #
        # Set run type for the NPB by-products file name. So far this only
        # deviates from the default *_release_* for label generation run only
        # *_labels_*
        #
        if args.faucet == "labels" or (
            args.faucet == "clear" and "_labels_" in args.clear
        ):
            self.run_type = "labels"
        else:
            self.run_type = "release"

        #
        # Populate the setup object with attributes not present in the
        # configuration file.
        #
        self.root_dir = os.path.dirname(os.path.abspath(__file__))[:-7]
        self.step = 1
        self.version = version
        self.args = args
        self.faucet = args.faucet.lower()
        self.diff = args.diff.lower()
        self.today = datetime.date.today().strftime("%Y%m%d")
        self.file_list = []
        self.checksum_registry = []

        #
        # If a release date is not specified it is set to today.
        #
        if not hasattr(self, "release_date"):
            self.release_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            pattern = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")
            if not pattern.match(self.release_date):
                error_message(
                    "release_date parameter does not match "
                    "the required format: YYYY-MM-DD."
                )

        #
        # Check date format, if is not provided it is set to the format
        # proposed for the PDS4 Information Model 2.0.
        #
        if not hasattr(self, "date_format"):
            self.date_format = "maklabel"

        #
        # Check text End of Line format and set EoL length.
        #
        # CRs are added to all text, XML, and other PDS meta-files
        # present in PDS4 archives as dictated by the standard.
        # CRs are added to checksum tables as well.
        #
        # If the parameter is not provided via configuration is set by default
        # to CRLF.
        #
        if not hasattr(self, "end_of_line"):
            self.end_of_line = "CRLF"
        if self.end_of_line == "CRLF":
            self.eol = "\r\n"
            self.eol_len = 2
        elif self.end_of_line == "LF":
            self.eol = "\n"
            self.eol_len = 1
        else:
            error_message("End of Line provided via configuration is not CRLF nor LF.")

        self.end_of_line_pds4 = "CRLF"
        self.eol_pds4 = "\r\n"
        self.eol_pds4_len = 1
        self.eol_mk = "\n"
        self.eol_mk_len = 1
        self.eol_pds3 = "\r\n"

        #
        # Check and determine endianness.
        #
        if not hasattr(self, "binary_endianness"):
            #
            # Placeholder for when PDS3 is fully implemented.
            #
            # if self.pds_version == "4":
            #    self.kernel_endianness = "little"
            # else:
            #    self.kernel_endianness = "big"
            self.kernel_endianness = "little"
        else:
            if (
                self.binary_endianness.lower() == "little"
                or self.binary_endianness.lower() == "ltl-ieee"
            ):
                self.kernel_endianness = "little"
            elif (
                self.binary_endianness.lower() == "big"
                or self.binary_endianness.lower() == "big-ieee"
            ):
                self.kernel_endianness = "big"
            else:
                error_message(
                    "binary_endianness configuration parameter value must be"
                    " 'big', 'BIG-IEEE', 'little' or 'LTL-IEEE'. Case is not"
                    " sensitive."
                )

        if sys.byteorder != self.kernel_endianness:
            error_message(
                f"binary_endianness configuration parameter value must be "
                f"the same as your system endianness: {sys.byteorder}."
            )

        #
        # Fill missing fields.
        #
        if self.pds_version == "4":
            self.producer_phone = ""
            self.producer_email = ""
            self.dataset_id = ""
            self.volume_id = ""

    def check_configuration(self):
        """Performs the following checks to the loaded configuration items:

        * IM, Line Feed, and Date Time format NAIF recommendations
        * Archive increment start and finish times
        * Transform relative to absolute paths
        * Existence of kernel directories
        * IM, XML model, and Schema Location coherence
        * Check existence of templates according to the IM
        * Meta-kernel configuration
        * Presence of uppercase characters in the kernel list configuration
        """
        #
        # Check IM, Line Feed, and Date Time format NAIF recommendations.
        #
        if self.date_format == "infomod2":

            #
            # Warn the user if the End of Line character is not the one
            # corresponding to the one recommended by NAIF for the selected
            # date format.
            #
            if self.end_of_line != "LF":
                logging.warning(
                    f"-- NAIF recommends to use `LF' End-of-Line while using"
                    f" the `{self.date_format}' parameter instead of "
                    f"`{self.end_of_line}'."
                )

            #
            # Set the time format for the Date format selected.
            #
            pattern = re.compile(
                "[0-9]{4}-[0-9]{2}-[0-9]{2}T" "[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}Z"
            )
            format = "YYYY-MM-DDThh:mm:ss.sssZ"
        elif self.date_format == "maklabel":

            #
            # Warn the user if the End of Line character is not the one
            # corresponding to the one recommended by NAIF for the selected
            # date format.
            #
            if self.end_of_line != "CRLF":
                logging.warning(
                    f"-- NAIF recommends to use `CRLF' End-of-Line while using"
                    f" the `{self.date_format}' parameter instead of "
                    f"`{self.end_of_line}'."
                )

            #
            # Set the time format for the Date format selected.
            #
            pattern = re.compile(
                "[0-9]{4}-[0-9]{2}-[0-9]{2}T" "[0-9]{2}:[0-9]{2}:[0-9]{2}Z"
            )
            format = "YYYY-MM-DDThh:mm:ssZ"

        #
        # Check binary kernels endianness.
        #
        if self.pds_version == "4":
            if self.kernel_endianness == "little":
                logging.info(
                    "-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format."
                )
            else:
                logging.info(
                    "-- Binary SPICE kernels expected to have BIG-IEEE (little endian) binary format."
                )
                logging.warning(
                    "-- NAIF strongly recommends to use LTL-IEEE (little endian) for binary kernels in PDS4 archives "
                )
                logging.warning("   and enforces it if the archive is hosted by NAIF.")
        else:
            if self.kernel_endianness == "little":
                logging.info(
                    "-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format."
                )

                logging.warning(
                    "-- NAIF strongly recommends to use BIG-IEEE (big endian) for binary kernels in PDS3 archives "
                )
                logging.warning("   and enforces it if the archive is hosted by NAIF.")
                if sys.byteorder == "big":
                    logging.warning(
                        "   Your system is BIG-IEEE (big endian): PDS3 Labels cannot be attached to binary kernels."
                    )
                    logging.warning(
                        "   If binary kernels are present this will result in an error."
                    )
            else:
                logging.info(
                    "-- Binary SPICE kernels expected to have BIG-IEEE (big endian) binary format."
                )
                if sys.byteorder != "big":
                    logging.warning(
                        "   Your system is LTL-IEEE (little endian): PDS3 Labels cannot be attached to binary kernels."
                    )
                    logging.warning(
                        "   If binary kernels are present this will result in an error."
                    )

        #
        # Check Bundle increment start and finish times. For the two accepted
        # formats.
        #
        if hasattr(self, "mission_start") and self.mission_start:
            if not pattern.match(self.mission_start):
                error_message(
                    f"mission_start parameter does not match the "
                    f"required format: {format}."
                )
        if hasattr(self, "mission_finish") and self.mission_finish:
            if not pattern.match(self.mission_finish):
                error_message(
                    f"mission_finish does not match the required format: {format}."
                )
        if hasattr(self, "increment_start") and self.increment_start:
            if not pattern.match(self.increment_start):
                error_message(
                    f"increment_start parameter does not match the "
                    f"required format: {format}."
                )
        if hasattr(self, "increment_finish") and self.increment_finish:
            if not pattern.match(self.increment_finish):
                error_message(
                    f"increment_finish does not match the required "
                    f"format: {format}."
                )
        if hasattr(self, "increment_start") and hasattr(self, "increment_finish"):
            if ((not self.increment_start) and (self.increment_finish)) or (
                (self.increment_start) and (not self.increment_finish)
            ):
                error_message(
                    "If provided via configuration, increment_start and "
                    "increment_finish parameters need to be provided "
                    "together."
                )

        #
        # Check that directories are not the same.
        #
        if (
            (self.working_directory == self.staging_directory)
            or (self.bundle_directory == self.staging_directory)
            or (self.bundle_directory == self.working_directory)
        ):
            logging.error(
                "--The working, staging, and bundle directories must be different:"
            )
            logging.error(f"  working: {self.working_directory}")
            logging.error(f"  staging: {self.staging_directory}")
            logging.error(f"  bundle:  {self.bundle_directory}")
            error_message("Update working, staging, or bundle directory.")

        #
        # Sort out if directories are provided as relative paths and
        # if so convert them in absolute for the execution
        #
        cwd = os.getcwd()

        os.chdir("/")

        #
        # Set the staging directory WRT PDS3 or PDS4
        #
        if self.pds_version == "4":
            mission_dir = f"{self.mission_acronym}_spice"
        else:
            mission_dir = f"{self.volume_id.lower()}"

        if os.path.isdir(cwd + os.sep + self.working_directory):
            self.working_directory = cwd + os.sep + self.working_directory
        if not os.path.isdir(self.working_directory):
            error_message(f"Directory does not exist: {self.working_directory}.")

        if os.path.isdir(cwd + os.sep + self.staging_directory):
            self.staging_directory = (
                cwd + os.sep + self.staging_directory + f"/{mission_dir}"
            )
        elif not os.path.isdir(self.staging_directory):
            logging.warning(
                f"-- Creating staging directory: {self.staging_directory}/{mission_dir}."
            )
            #
            # If the faucet is set to plan, kerlist, or checks, this is just
            # fine. Otherwise the non-existence must trigger an error.
            #
            try:
                os.mkdir(cwd + os.sep + self.staging_directory)
            except BaseException:
                if self.faucet in ["plan", "list", "checks"]:
                    logging.warning(
                        f"-- Staging directory cannot be created but is not used with {self.faucet} faucet."
                    )
                else:
                    error_message(
                        f"Staging directory cannot be created: {self.staging_directory}."
                    )

        elif f"/{mission_dir}" not in self.staging_directory:
            self.staging_directory += f"/{mission_dir}"

        if os.path.isdir(cwd + os.sep + self.bundle_directory):
            self.bundle_directory = cwd + os.sep + self.bundle_directory

        #
        # If the faucet is set to plan, kerlist, or checks, this is just
        # fine. Otherwise the non-existence must trigger an error.
        #
        if not os.path.isdir(self.bundle_directory):
            if self.faucet in ["plan", "list", "checks"]:
                logging.warning(
                    f"-- Bundle directory does not exist but is not used with {self.faucet} faucet."
                )
            else:
                error_message(
                    f"Bundle directory does not exist: {self.bundle_directory}."
                )

        #
        # There might be more than one kernel directory
        #
        for i in range(len(self.kernels_directory)):
            if os.path.isdir(cwd + os.sep + self.kernels_directory[i]):
                self.kernels_directory[i] = cwd + os.sep + self.kernels_directory[i]
            if not os.path.isdir(self.kernels_directory[i]):
                error_message(f"Directory does not exist: {self.kernels_directory[i]}.")

        os.chdir(cwd)

        #
        # Check IM, XML model, and Schema Location coherence (given that is not
        # checked by the PDS Validate tool.
        #
        if hasattr(self, "information_model"):
            if re.match(r"[0-9]+[.][0-9]+[.][0-9]+[.][0-9]+", self.information_model):

                major = int(self.information_model.split(".")[0])
                minor = int(self.information_model.split(".")[1])
                maint = int(self.information_model.split(".")[2])
                build = int(self.information_model.split(".")[3])

                if major >= 10:
                    major = chr(major + 55)
                if minor >= 10:
                    minor = chr(minor + 55)
                if maint >= 10:
                    maint = chr(maint + 55)
                if build >= 10:
                    build = chr(build + 55)

                short_version = f"{major}{minor}{maint}{build}"

                #
                # Check if xml_model is provided via configuration, if so check
                # its validity and if not generate it.
                #
                if hasattr(self, "xml_model"):
                    xml_model_version = self.xml_model.split("PDS4_PDS_")[-1]
                    xml_model_version = xml_model_version.split(".sch")[0]

                    if xml_model_version != short_version:
                        error_message(
                            f"PDS4 Information Model "
                            f"{short_version} "
                            f"is incoherent with the XML Model version: "
                            f"{self.xml_model}."
                        )
                else:
                    self.xml_model = (
                        f"http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_{short_version}.sch"
                    )
                    logging.info(
                        "-- Schema XML Model (xml_model) not provided with configuration file. Set to:"
                    )
                    logging.info(f"   {self.xml_model}")

                #
                # Check if schema_location is provided via configuration, if so check
                # its validity and if not generate it.
                #
                if hasattr(self, "schema_location"):
                    schema_loc_version = self.schema_location.split("/PDS4_PDS_")[-1]
                    schema_loc_version = schema_loc_version.split(".xsd")[0]

                    if schema_loc_version != short_version:
                        error_message(
                            f"PDS4 Information Model "
                            f"{short_version} "
                            f"is incoherent with the Schema location: "
                            f"{self.schema_location}."
                        )
                else:
                    self.schema_location = (
                        f"http://pds.nasa.gov/pds4/pds/v1 "
                        f"http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_{short_version}.xsd"
                    )
                    logging.info(
                        "-- Schema Location (schema_location) not provided with configuration file. Set to:"
                    )
                    logging.info(f"   {self.schema_location}")

            else:
                error_message(
                    f"PDS4 Information Model {self.information_model}"
                    f" format from configuration is incorrect."
                )

        #
        # Check existence of templates according to the information_model
        # or user-defined templates.
        #
        if self.pds_version == "4":

            config_schema = self.information_model.split(".")
            config_schema = float(
                f"{int(config_schema[0]):03d}"
                f"{int(config_schema[1]):03d}"
                f"{int(config_schema[2]):03d}"
                f"{int(config_schema[3]):03d}"
            )

            #
            # Store the float value of the schema to evaluate element values
            # that depend on the IM.
            #
            self.information_model_float = config_schema

            schemas = [
                os.path.basename(x[:-1])
                for x in glob.glob(f"{self.root_dir}templates/*/")
            ]
            schemas.remove("pds3")

            schemas_eval = []
            for schema in schemas:
                schema = schema.split(".")
                schema = float(
                    f"{int(schema[0]):03d}"
                    f"{int(schema[1]):03d}"
                    f"{int(schema[2]):03d}"
                    f"{int(schema[3]):03d}"
                )
                schemas_eval.append(schema)

            #
            # Reorder the schema list according to their value.
            #
            schemas_index = sorted(
                range(len(schemas_eval)), key=schemas_eval.__getitem__, reverse=True
            )
            schemas_eval.sort(reverse=True)
            schemas = [schemas[i] for i in schemas_index]

            i = 0
            while i < len(schemas_eval):
                if config_schema < schemas_eval[i]:
                    try:
                        schema = schemas[i - 1]
                    except:
                        schema = schemas[0]
                if config_schema >= schemas_eval[i]:
                    schema = schemas[i]
                    break
                i += 1

            templates_directory = f"{self.root_dir}templates/{schema}/"
        #
        # If a templates' directory is not provided, determine the templates
        # to be used based on the IM.
        #
        else:
            templates_directory = f"{self.root_dir}templates/pds3/"

        template_files = []
        if not hasattr(self, "templates_directory") and self.pds_version == "4":

            self.templates_directory = self.working_directory

            templates = os.listdir(templates_directory)
            for template in templates:
                shutil.copy2(
                    os.path.join(templates_directory, template),
                    self.templates_directory,
                )
                template_files.append(self.working_directory + os.sep + template)

            if config_schema in schemas_eval:
                logging.info(
                    f"-- Label templates will use the ones from "
                    f"information model {schema}."
                )
            else:
                logging.warning(
                    f"-- Label templates will use the ones from "
                    f"information model {schema}."
                )
        elif self.pds_version == "4":
            if not os.path.isdir(self.templates_directory):
                error_message("Path provided/derived for templates is not available.")
            labels_check = [
                os.path.basename(x)
                for x in glob.glob(f"{self.root_dir}templates/1.5.0.0/*")
            ]

            labels = [
                os.path.basename(x) for x in glob.glob(f"{self.templates_directory}/*")
            ]

            #
            # Copy the templates to the working directory.
            #
            for label in labels_check:
                if label not in labels:
                    logging.warning(
                        f"-- Template {label} has not been provided. "
                        f"Using label from: "
                    )
                    logging.warning(f"   {templates_directory}")
                    shutil.copy(
                        templates_directory + os.sep + label, self.working_directory
                    )
                    template_files.append(self.working_directory + os.sep + label)
                else:
                    shutil.copy(
                        self.templates_directory + os.sep + label,
                        self.working_directory,
                    )
                    template_files.append(self.working_directory + os.sep + label)
        else:
            #
            # PDS3 templates
            #
            self.templates_directory = f"{self.root_dir}templates/pds3"
            templates = os.listdir(self.templates_directory)
            for template in templates:
                shutil.copy2(
                    os.path.join(self.templates_directory, template),
                    self.working_directory,
                )
                template_files.append(self.working_directory + os.sep + template)

        logging.info(f"-- Label templates directory: {self.templates_directory}")

        self.templates_directory = self.working_directory
        self.template_files = template_files

        #
        # Extract the XML files line tabs and line spaces for the element added
        # to the templates. The default for the built-in templates is 2.
        #
        xml_tab = 0
        if self.pds_version == "4":
            try:
                xml_tag = "<Identification_Area>"
                with open(
                    self.templates_directory + os.sep + "template_bundle.xml", "r"
                ) as t:
                    for line in t:
                        if xml_tag in line:
                            line = line.rstrip()
                            xml_tab = len(line) - len(xml_tag)
            except:
                logging.warning(
                    "-- XML Template not found to determine XML Tab. It has been set to 2."
                )
                xml_tab = 2

            if xml_tab <= 0:
                logging.warning(
                    "-- XML Template not useful to determine XML Tab. It has been set to 2."
                )
                xml_tab = 2

        self.xml_tab = xml_tab

        #
        # Check meta-kernel configuration
        #
        if hasattr(self, "mk"):
            for metak in self.mk:

                metak_name_check = metak["@name"]

                #
                # Fix no list or list of lists.
                #
                patterns = []
                for name in metak["name"]:

                    if not isinstance(name["pattern"], list):
                        patterns = [name["pattern"]]
                    else:
                        for pattern in name["pattern"]:
                            patterns.append(pattern)

                for pattern in patterns:
                    name_pattern = pattern["#text"]
                    if not name_pattern in metak_name_check:
                        error_message(
                            f"The meta-kernel pattern "
                            f"{name_pattern} is not provided."
                        )

                    metak_name_check = metak_name_check.replace("$" + name_pattern, "")

                #
                # If there are remaining $ characters in the metak_name_check
                # this means that there are remaining patterns to define in
                # the configuration file.
                #
                if "$" in metak_name_check:
                    error_message(
                        f"The MK patterns {metak['@name']} do not "
                        f"correspond to the present MKs."
                    )
        else:
            logging.warning("-- There is no meta-kernel configuration to check.")

        #
        # Check coverage kernels configuration (needed if there is only one
        # entry).
        #
        if hasattr(self, "coverage_kernels"):
            if not isinstance(self.coverage_kernels, list):
                self.coverage_kernels = [self.coverage_kernels]

        #
        # If a readme file is present the readme section of the configuration
        # is irrelevant.
        #
        if (
            not os.path.exists(f"{self.bundle_directory}/{mission_dir}/readme.txt")
            and self.pds_version == "4"
        ):
            #
            # Check readme file inputs in configuration. Raise an error immediately
            # if things do not look good.
            #
            if hasattr(self, "readme"):
                if "input" in self.readme and not os.path.exists(self.readme["input"]):
                    if ("cognisant_authority" in self.readme) and (
                        "overview" in self.readme
                    ):
                        logging.warning(
                            "Input readme file not present. "
                            "File will be generated from "
                            "configuration."
                        )
                    else:
                        error_message(
                            "Readme elements not present in configuration file."
                        )
            else:
                error_message("Readme elements not present in configuration file.")

        #
        # Check if there is any uppercase character in the kernel list
        # configuration section.
        #
        kernel_pattern_is_upper = False
        kernel_pattern_upper = []
        for kernel_pattern in self.kernel_list_config.keys():
            if any(ele.isupper() for ele in kernel_pattern):
                kernel_pattern_is_upper = True
                kernel_pattern_upper.append(kernel_pattern)
        if kernel_pattern_is_upper:
            logging.warning(
                "-- Kernel list configuration has entries with uppercase letters:"
            )
            for kernel_pattern in kernel_pattern_upper:
                logging.warning(f"      {kernel_pattern}")
            logging.warning(
                "   Uppercase letters in kernel names are HIGHLY discouraged. "
            )

    def set_release(self):
        """Determine the Bundle release number."""
        line = f"Step {self.step} - Setup the archive generation"
        logging.info("")
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.step += 1
        if not self.args.silent and not self.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # PDS4 release increment (implies inventory and meta-kernel).
        #
        logging.info("-- Checking existence of previous release.")

        if self.args.clear:
            release = self.args.clear
            release = release.split(".file_list")[0]
            release = int(release.split(f"_{self.run_type}_")[-1])
            current_release = int(release) - 1

            release = f"{release:03}"
            current_release = f"{current_release:03}"
            logging.info(
                f"-- Generating release {release} as obtained from "
                f"file list from previous run: {self.args.clear}"
            )
            increment = True

        else:
            try:
                releases = glob.glob(
                    self.bundle_directory
                    + os.sep
                    + self.mission_acronym
                    + "_spice"
                    + os.sep
                    + f"bundle_{self.mission_acronym}_spice_v*"
                )
                releases.sort()
                current_release = int(releases[-1].split("_spice_v")[-1].split(".")[0])
                current_release = f"{current_release:03}"
                release = int(current_release) + 1
                release = f"{release:03}"

                logging.info(f"-- Generating release {release}.")

                increment = True

            except:
                if self.pds_version == "4":
                    logging.warning(
                        "-- Bundle label not found. Checking previous kernel list."
                    )

                try:

                    #
                    # If the kernel list is provided as an argument, we
                    # cannot deduce the release version from it.
                    #
                    if self.args.kerlist:
                        logging.warning(
                            "-- Kernel list provided as input. "
                            "Release number cannot be obtained."
                        )
                        raise

                    releases = glob.glob(
                        self.working_directory + f"/{self.mission_acronym}"
                        f"_{self.run_type}_*.kernel_list"
                    )

                    releases.sort()
                    current_release = int(
                        releases[-1].split(f"_{self.run_type}_")[-1].split(".")[0]
                    )
                    current_release = f"{current_release:03}"
                    release = int(current_release) + 1
                    release = f"{release:03}"

                    logging.info(f"-- Generating release {release}")

                    increment = True
                except:

                    logging.warning("-- This is the first release.")

                    release = "001"
                    current_release = ""

                    increment = False

        self.release = release
        self.current_release = current_release

        logging.info("")

        self.increment = increment

    @spice_exception_handler
    def load_kernels(self):
        """Loads the kernels required to run NPB.

        Note that kernels that
        are not required might be loaded as well, but given that the
        required memory is not much, we stay on the safe side by loading
        additional kernels.
        """
        line = f"Step {self.step} - Load LSK, PCK, FK and SCLK kernels"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.step += 1
        if not self.args.silent and not self.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # To get the appropriate kernels, use the kernel list config.
        # First extract the patterns for each kernel type of interest.
        #
        fk_patterns = []
        sclk_patterns = []
        pck_patterns = []
        lsk_patterns = []

        #
        # We inspect the kernels directory and the bundle directory.
        #
        directories = self.kernels_directory
        if self.pds_version == "4":
            directories.append(
                self.bundle_directory + f"/{self.mission_acronym}_spice/spice_kernels"
            )
        else:
            directories.append(self.bundle_directory + f"{self.volume_id}/data")

        for type in self.kernels_to_load:
            if "fk" in type:
                fks = self.kernels_to_load[type]
                if not isinstance(fks, list):
                    fks = [fks]
                for fk in fks:
                    fk_patterns.append(fk)
            elif "sclk" in type:
                sclks = self.kernels_to_load[type]
                if not isinstance(sclks, list):
                    sclks = [sclks]
                for sclk in sclks:
                    sclk_patterns.append(sclk)
            elif "pck" in type:
                pcks = self.kernels_to_load[type]
                if not isinstance(pcks, list):
                    pcks = [pcks]
                for pck in pcks:
                    pck_patterns.append(pck)
            elif "lsk" in type:
                lsks = self.kernels_to_load[type]
                if not isinstance(lsks, list):
                    lsks = [lsks]
                for lsk in lsks:
                    lsk_patterns.append(lsk)

        #
        # Search the latest version for each pattern of each kernel type.
        #
        lsks = []
        for pattern in lsk_patterns:
            if os.path.exists(pattern):
                lsks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                for dir in directories:
                    lsk_pattern = [
                        os.path.join(root, name)
                        for root, dirs, files in os.walk(dir)
                        for name in files
                        if re.fullmatch(pattern, name)
                    ]
                    if lsk_pattern:
                        lsk_pattern.sort(key=kernel_name)
                        spiceypy.furnsh(lsk_pattern[-1])
                        lsks.append(lsk_pattern[-1])
                        break
        if not lsks:
            logging.error(f"-- LSK not found.")
        else:
            logging.info(f"-- LSK     loaded: {lsks}")
        if len(lsks) > 1:
            error_message("Only one LSK should be obtained.")

        pcks = []
        for pattern in pck_patterns:
            if os.path.exists(pattern):
                pcks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                for dir in directories:
                    pcks_pattern = [
                        os.path.join(root, name)
                        for root, dirs, files in os.walk(dir)
                        for name in files
                        if re.fullmatch(pattern, name)
                    ]
                    if pcks_pattern:
                        pcks_pattern.sort(key=kernel_name)
                        spiceypy.furnsh(pcks_pattern[-1])
                        pcks.append(pcks_pattern[-1])
                        break
        if not pcks:
            logging.info(f"-- PCK not found.")
        else:
            logging.info(f"-- PCK(s)   loaded: {pcks}")

        fks = []
        for pattern in fk_patterns:
            if os.path.exists(pattern):
                fks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                for dir in directories:
                    fks_pattern = [
                        os.path.join(root, name)
                        for root, dirs, files in os.walk(dir)
                        for name in files
                        if re.fullmatch(pattern, name)
                    ]

                    if fks_pattern:
                        fks_pattern.sort(key=kernel_name)
                        spiceypy.furnsh(fks_pattern[-1])
                        fks.append(fks_pattern[-1])
                        break
        if not fks:
            logging.warning(f"-- FK not found.")
        else:
            logging.info(f"-- FK(s)   loaded: {fks}")

        sclks = []
        for pattern in sclk_patterns:
            if os.path.exists(pattern):
                sclks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                for dir in directories:
                    sclks_pattern = [
                        os.path.join(root, name)
                        for root, dirs, files in os.walk(dir)
                        for name in files
                        if re.fullmatch(pattern, name)
                    ]
                    if sclks_pattern:
                        sclks_pattern.sort(key=kernel_name)
                        spiceypy.furnsh(sclks_pattern[-1])
                        sclks.append(sclks_pattern[-1])
                        break
        if not sclks:
            logging.error(f"-- SCLK not found.")
        else:
            logging.info(f"-- SCLK(s) loaded: {sclks}")

        logging.info("")

        self.fks = fks
        self.sclks = sclks
        self.lsk = lsk

    def information_model_setup(self):
        """Setup and check PDS4 Information Model related things."""

    def clear_run(self, debug=False):
        """Clears the files generated by a previous run.

        Clears the files generated by a previous run when specified with the
        clear argument and the kernel list of the previous run.

        Please note that newly created directories will not be erased.

        :param debug: If True, the by-product files are not cleaned up. This is
                      useful when testing
        :type debug: bool
        """
        if debug:
            logging.warning(
                f"-- Running in DEBUG mode, by-product files are not cleaned up."
            )

        if os.path.isfile(self.args.clear):

            #
            # Remove files from the staging area.
            #
            path = self.staging_directory
            logging.info(f"-- Removing files from staging area: {path}.")
            with open(self.args.clear, "r") as c:
                for line in c:
                    if (".plan" not in line) and (".kernel_list" not in line):
                        try:
                            stag_file = path + os.sep + line.strip()
                            os.remove(stag_file)
                        except:
                            logging.warning(f"     File {stag_file} not found.")

            #
            # Remove files from the final area.
            #
            path = self.bundle_directory + os.sep + self.mission_acronym + "_spice/"

            logging.info(f"-- Removing files from final area: {path}.")
            with open(self.args.clear, "r") as c:
                for line in c:
                    if (".plan" not in line) and (".kernel_list" not in line):
                        try:
                            #
                            # When NPB has been executed in label mode the final
                            # area does not replicate the bundle directory structure
                            # but kernels operations area.
                            #
                            if not os.path.exists(path):
                                os.remove(
                                    self.bundle_directory
                                    + line.split("spice_kernels")[-1].strip()
                                )
                            #
                            # Default case.
                            #
                            else:
                                os.remove(path + line.strip())
                        except:
                            logging.warning(f"     File {line.strip()} not found.")

            #
            # Remove generated by-products from the working_directory.
            #
            path = self.working_directory
            if self.args.kerlist:
                try:
                    byproduct = self.args.clear.split(".")[0] + ".plan"
                    logging.info(f"-- Removing previous run by-product: {byproduct}.")
                    os.remove(path + os.sep + byproduct.split(os.sep)[-1])
                except:
                    logging.warning(f"     File {byproduct} not found.")
            if self.args.plan:
                try:
                    byproduct = self.args.clear.split(".")[0] + ".kernel_list"
                    logging.info(f"-- Removing previous run by-product: {byproduct}.")
                    os.remove(path + os.sep + byproduct.split(os.sep)[-1])
                except:
                    logging.warning(f"     File {byproduct} not found.")

        else:
            error_message(
                f'The file provided with the "clear" argument does '
                f"not exist or is not readable. Make sure that the "
                f"file follows the name pattern: "
                f"{self.mission_acronym}_{self.run_type}_NN.file_list."
                f" where NN is the release number."
            )

    def add_file(self, file):
        """Add file fo Product List.

        Adds a product to the run by-product Product List.

        :param file: Product to be added
        :type file: str
        """
        self.file_list.append(file)

    def add_checksum(self, path, checksum):
        """Add checksum to Checksum record.

        Adds a MD5sum entry with the product it corresponds to for the run
        by-product Checksum record file.

        :param path: File path for checksum
        :type path: str
        :param checksum: Checksum value for checksum
        :type checksum: str
        """
        self.checksum_registry.append(f"{path} {checksum}")

    def write_file_list(self):
        """Write the run by-product File List."""
        if self.file_list:
            with open(
                self.working_directory
                + os.sep
                + f"{self.mission_acronym}_{self.run_type}_"
                f"{int(self.release):02d}.file_list",
                "w",
            ) as l:
                for file in self.file_list:
                    l.write(file + "\n")
            logging.info("-- Run File List file written in working area.")

    def write_checksum_registry(self):
        """Write the run by-product Checksum Record."""
        if self.checksum_registry:
            with open(
                self.working_directory
                + os.sep
                + f"{self.mission_acronym}_{self.run_type}_"
                f"{int(self.release):02d}.checksum",
                "w",
            ) as l:
                for element in self.checksum_registry:
                    l.write(element + "\n")
            logging.info("-- Run Checksum Registry file written in working area.")

    def write_validate_config(self):
        """Write a PDS validate tool configuration file.

        NPB will write a PDS validate tool configuration file for convenience
        of the user. The following validate example command for ExoMars2016::

           $ validate -v 1 -t em16/em16_spice –-skip-context-validation \
           -R pds4.bundle -x working/PDS4_PDS_1B00.xsd -S working/PDS4_PDS_1B00.sch \
           -–strict-field-checks -r working/em16_release_03.validate

        Would be equivalent to the following resulting Validate configuration
        file::

           # Run the PDS validate tool where the NPB working directory resides:
           # $ validate -c working/em16_release_03.config.validate
           validate.target = em16/em16_spice
           validate.verbose = 1
           validate.skip-context-validation = true
           validate.rule = pds4.bundle
           validate.schema = working/PDS4_PDS_1B00.xsd
           validate.schematron = working/PDS4_PDS_1B00.sch
           validate.strictFieldChecks = true
           validate.report = working/em16_release_03.validate_report

        If there is an issue during the generation of this file --e.g.: no
        internet connection-- the process will silently fail but the NPB run
        will be successful.
        """
        pds_schematron_location = self.xml_model
        pds_schematron = pds_schematron_location.split("/")[-1]
        try:
            r = requests.get(pds_schematron_location, allow_redirects=True)
        except BaseException:
            logging.warning("-- PDS Validate Tool configuration file not written.")
            logging.warning(f"   PDS Schematron not reachable: {pds_schematron}")
            return
        with open(f"{self.working_directory}/{pds_schematron}", "wb") as f:
            f.write(r.content)

        pds_schema_location = self.schema_location.split()[-1]
        pds_schema = pds_schema_location.split("/")[-1]
        try:
            r = requests.get(pds_schema_location, allow_redirects=True)
        except BaseException:
            logging.warning("-- PDS Validate Tool configuration file not written.")
            logging.warning(
                f"   PDS Schema location not reachable: {pds_schema_location}"
            )
            return
        with open(f"{self.working_directory}/{pds_schema}", "wb") as f:
            f.write(r.content)

        filename = f"{self.mission_acronym}_{self.run_type}_{int(self.release):02d}"

        with open(f"{self.working_directory}/{filename}.validate_config", "w") as l:
            l.write(
                "# Run the PDS validate tool where the NPB working directory resides:\n"
            )
            l.write(
                f"# $ validate -t {self.bundle_directory}/{self.mission_acronym}_spice "
                f"-c {self.working_directory}/{filename}.validate_config "
                f"-r {self.working_directory}/{filename}.validate_report\n#\n"
            )
            l.write(f"validate.schema = {self.working_directory}/{pds_schema}\n")
            l.write(
                f"validate.schematron = {self.working_directory}/{pds_schematron}\n"
            )
            l.write(f"validate.verbose = 1\n")
            l.write(f"validate.skipContextValidation = true\n")
            l.write(f"validate.rule = pds4.bundle\n")
            l.write(f"validate.strictFieldChecks = true\n")

        logging.info("-- PDS Validate Tool configuration file written in working area:")
        logging.info(f"   {self.working_directory}/{filename}.validate_config")
