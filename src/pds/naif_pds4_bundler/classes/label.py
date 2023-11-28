"""PDS Label Class and Child Classes Implementation."""
import glob
import logging
import os

import spiceypy

from ..utils import add_carriage_return
from ..utils import ck_coverage
from ..utils import compare_files
from ..utils import extension_to_type
from ..utils import extract_comment
from ..utils import format_multiple_values
from ..utils import spice_exception_handler
from ..utils import type_to_pds3_type
from .log import error_message


class PDSLabel(object):
    """Class to generate a PDS Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: Product to be labeled
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        if setup.pds_version == "4":
            try:
                context_products = product.collection.bundle.context_products
                if not context_products:
                    raise Exception("No context products from bundle in collection")
            except BaseException:
                context_products = product.bundle.context_products

        self.product = product
        self.setup = setup

        #
        # Fields from setup
        #
        self.root_dir = setup.root_dir
        self.mission_acronym = setup.mission_acronym
        self.MISSION_NAME = setup.mission_name

        if setup.pds_version == "4":
            self.XML_MODEL = setup.xml_model
            self.SCHEMA_LOCATION = setup.schema_location
            self.INFORMATION_MODEL_VERSION = setup.information_model

            #
            # Needs to be built for several observers.
            #
            if hasattr(setup, "secondary_observers"):
                if len(setup.secondary_observers) == 1:
                    observers_text = (
                        f"{setup.observer} and {setup.secondary_observers[0]}"
                    )
                else:
                    observers_text = f"{setup.observer}, "
                    for i in range(len(setup.secondary_observers)):
                        if i == len(setup.secondary_observers) - 1:
                            observers_text += f"and {setup.secondary_observers[i]}"
                        else:
                            observers_text += f"{setup.secondary_observers[i]}, "

                self.PDS4_OBSERVER_NAME = f"{observers_text} spacecraft and their"
            else:
                self.PDS4_OBSERVER_NAME = f"{setup.observer} spacecraft and its"

            self.END_OF_LINE_PDS4 = "Carriage-Return Line-Feed"
            if setup.end_of_line == "CRLF":
                self.END_OF_LINE = "Carriage-Return Line-Feed"
            elif setup.end_of_line == "LF":
                self.END_OF_LINE = "Line-Feed"
            else:
                error_message(
                    "End of Line provided via configuration is not CRLF nor LF.",
                    setup=self.setup,
                )

            self.BUNDLE_DESCRIPTION_LID = f"{setup.logical_identifier}:document:spiceds"

            try:
                self.PDS4_MISSION_LID = product.collection.bundle.lid_reference
            except BaseException:
                self.PDS4_MISSION_LID = product.bundle.lid_reference

        if hasattr(self.setup, "creation_date_time"):
            creation_dt = self.setup.creation_date_time
            self.PRODUCT_CREATION_TIME = creation_dt
            self.PRODUCT_CREATION_DATE = creation_dt.split("T")[0]
            self.PRODUCT_CREATION_YEAR = creation_dt.split("-")[0]
        else:
            self.PRODUCT_CREATION_TIME = product.creation_time
            self.PRODUCT_CREATION_DATE = product.creation_date
            self.PRODUCT_CREATION_YEAR = product.creation_date.split("-")[0]

        self.FILE_SIZE = product.size
        self.FILE_CHECKSUM = product.checksum

        #
        # For labels that need to include all observers and targets of the
        # setup.
        #
        if (
            type(self).__name__ != "SpiceKernelPDS4Label"
            and type(self).__name__ != "MetaKernelPDS4Label"
            and type(self).__name__ != "OrbnumFilePDS4Label"
        ):
            #
            # Obtain all observers.
            #
            obs = ["{}".format(self.setup.observer)]

            if hasattr(self.setup, "secondary_observers"):
                sec_obs = self.setup.secondary_observers
                if not isinstance(sec_obs, list):
                    sec_obs = [sec_obs]
            else:
                sec_obs = []

            self.observers = obs + sec_obs

            #
            # Obtain all targets.
            #
            tar = [self.setup.target]

            if hasattr(self.setup, "secondary_targets"):
                sec_tar = self.setup.secondary_targets
                if not isinstance(sec_tar, list):
                    sec_tar = [sec_tar]
            else:
                sec_tar = []

            self.targets = tar + sec_tar
        else:
            self.observers = product.observers
            self.targets = product.targets

        if setup.pds_version == "4":
            self.OBSERVERS = self.get_observers()
            self.TARGETS = self.get_targets()

    def get_observers(self):
        """Get the label observers from the context products.

        :return: List of Observers to be included in the label
        :rtype: list
        """
        obs = self.observers
        if not isinstance(obs, list):
            obs = [obs]

        obs_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        for ob in obs:
            if ob:
                ob_lid = ""
                ob_name = ob.split(",")[0]
                for product in context_products:
                    if product["name"][0] == ob_name and (
                        product["type"][0] == "Spacecraft"
                        or product["type"][0] == "Rover"
                        or product["type"][0] == "Lander"
                        or product["type"][0] == "Host"
                    ):
                        ob_lid = product["lidvid"].split("::")[0]
                        ob_type = product["type"][0]

                if not ob_lid:
                    error_message(
                        f"LID has not been obtained for observer {ob}.",
                        setup=self.setup,
                    )

                obs_list_for_label += (
                    f"{' ' * 3*tab}<Observing_System_Component>{eol}"
                    + f"{' ' * (3+1)*tab}<name>{ob_name}</name>{eol}"
                    + f"{' ' * (3+1)*tab}<type>{ob_type}</type>{eol}"
                    + f"{' ' * (3+1)*tab}<Internal_Reference>{eol}"
                    + f"{' ' * (3 + 2)*tab}<lid_reference>{ob_lid}"
                    f"</lid_reference>{eol}"
                    + f"{' ' * (3 + 2)*tab}<reference_type>is_instrument_host"
                    f"</reference_type>{eol}"
                    + f"{' ' * (3+1)*tab}</Internal_Reference>{eol}"
                    + f"{' ' * 3*tab}</Observing_System_Component>{eol}"
                )

        if not obs_list_for_label:
            error_message(
                f"{self.product.name} observers not defined.", setup=self.setup
            )
        obs_list_for_label = obs_list_for_label.rstrip() + eol

        return obs_list_for_label

    def get_targets(self):
        """Get the label targets from the context products.

        :return: List of Targets to be included in the label
        :rtype: list
        """
        tars = self.targets
        if not isinstance(tars, list):
            tars = [tars]

        tar_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        for tar in tars:
            if tar:
                target_name = tar
                for product in context_products:
                    if product["name"][0].upper() == target_name.upper():
                        target_lid = product["lidvid"].split("::")[0]
                        target_type = product["type"][0].capitalize()

                tar_list_for_label += (
                    f"{' ' * 2*tab}<Target_Identification>{eol}"
                    + f"{' ' * 3 * tab}<name>{target_name}</name>{eol}"
                    + f"{' ' * 3 * tab}<type>{target_type}</type>{eol}"
                    + f"{' ' * 3 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 4  *  tab}<lid_reference>{target_lid}"
                    f"</lid_reference>{eol}" + f"{' ' * 4  *  tab}<reference_type>"
                    f"{self.get_target_reference_type()}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2*tab}</Target_Identification>{eol}"
                )

        if not tar_list_for_label:
            error_message(f"{self.product.name} targets not defined.", setup=self.setup)
        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label

    def get_target_reference_type(self):
        """Get the target reference type.

        :return: Target_Reference_Type value for PDS4 label
        :rtype: str
        """
        if self.__class__.__name__ == "ChecksumPDS4Label":
            type = "ancillary_to_target"
        elif self.__class__.__name__ == "BundlePDS4Label":
            type = "bundle_to_target"
        elif self.__class__.__name__ == "InventoryPDS4Label":
            type = "collection_to_target"
        elif self.__class__.__name__ == "OrbnumFilePDS4Label":
            if self.setup.information_model_float >= 1014000000.0:
                type = "ancillary_to_target"
            else:
                type = "data_to_target"
        else:
            type = "data_to_target"

        return type

    def write_label(self):
        """Write the Label."""
        label_dictionary = vars(self)

        if self.setup.pds_version == "4":
            label_extension = ".xml"
            eol = self.setup.eol_pds4
        else:
            label_extension = ".lbl"
            eol = self.setup.eol_pds3

        if label_extension not in self.product.path:
            label_name = (
                self.product.path.split(f".{self.product.extension}")[0]
                + label_extension
            )
        else:
            #
            # This accounts for the bundle label, that doest not come
            # from the bundle product itself.
            #
            label_name = self.product.path

        if "inventory" in label_name:
            label_name = label_name.replace("inventory_", "")

        with open(label_name, "w+") as f:
            with open(self.template, "r") as t:
                for line in t:
                    line = line.rstrip()
                    for key, value in label_dictionary.items():
                        if isinstance(value, str) and key in line and "$" in line:
                            line = line.replace("$" + key, value)

                    #
                    # The checksum label for PDS3 in order to be equivalent to
                    # the one generated by mkpdssum.pl must have the same
                    # line length as the checksum file.
                    #
                    if label_name.split(os.sep)[-1] == "checksum.lbl":
                        line += " " * (self.product.record_bytes - len(line) - 2)
                    line = add_carriage_return(line, eol, self.setup)

                    f.write(line)

        self.name = label_name

        stag_dir = self.setup.staging_directory
        logging.info(f'-- Created {label_name.split(f"{stag_dir}{os.sep}")[-1]}')
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(f'   * Created {label_name.split(f"{stag_dir}{os.sep}")[-1]}.')

        #
        # Add label to the list of generated files.
        #
        self.setup.add_file(label_name.split(f"{stag_dir}{os.sep}")[-1])

        #
        # Wrap lines for PDS3 labels.
        #
        if self.setup.diff:
            self.compare()

        if self.__class__.__name__ != "SpiceKernelPDS3Label":
            logging.info("")

    def compare(self):
        """**Compare the Label with another label**.

        The product label is compared to a similar label. The label with which
        the generated label is compared to is determined
        by the first criteria that is met from the following list:

           * find a different version of the same label
           * find the label of a product of the same kind (e.g.: same kernel
             type)
           * use a label of a product of the same kind from INSIGHT available
             from the NPB package.
        """
        logging.info("-- Comparing label...")

        #
        # 1-Look for a different version of the same file.
        #
        # What we do is that we keep trying to match the label name
        # advancing one character each iteration, in such a way that
        # we find, in order, the label that has the closest name to the
        # one we are generating.
        #
        val_label = ""
        try:

            match_flag = True
            val_label_path = (
                self.setup.bundle_directory
                + f"/{self.setup.mission_acronym}_spice/"
                + self.product.collection.name
                + os.sep
            )

            #
            # If this is the spice_kernels collection, we need to add the
            # kernel type directory. If it is the miscellaneous collection,
            # add the product type.
            #
            if (self.product.collection.name == "spice_kernels") and (
                "collection" not in self.name
            ):
                val_label_path += self.name.split(os.sep)[-2] + os.sep
            elif (self.product.collection.name == "miscellaneous") and (
                "collection" not in self.name
            ):
                val_label_path += self.name.split(os.sep)[-2] + os.sep

            val_label_name = self.name.split(os.sep)[-1]
            i = 1

            while match_flag:
                if i < len(val_label_name) - 1:
                    val_labels = glob.glob(
                        f"{val_label_path}{val_label_name[0:i]}*.xml"
                    )
                    if val_labels:
                        val_labels = sorted(val_labels)
                        val_label = val_labels[-1]
                        match_flag = True
                    else:
                        match_flag = False
                    i += 1

            if not val_label:
                raise Exception("No label for comparison found.")

        except BaseException:
            logging.warning("-- No other version of the product label has been found.")

            #
            # 2-If a prior version of the same file cannot be found look for
            #   the label of a product of the same type.
            #
            try:
                val_label_path = (
                    self.setup.bundle_directory
                    + f"/{self.setup.mission_acronym}_spice/"
                    + self.product.collection.name
                    + os.sep
                )

                #
                # If this is the spice_kernels collection, we need to add the
                # kernel type directory.
                #
                if (self.product.collection.name == "spice_kernels") and (
                    "collection" not in self.name
                ):
                    val_label_path += self.name.split(os.sep)[-2] + os.sep
                elif (self.product.collection.name == "miscellaneous") and (
                    "collection" not in self.name
                ):
                    val_label_path += self.name.split(os.sep)[-2] + os.sep

                product_extension = self.product.name.split(".")[-1]
                val_products = glob.glob(f"{val_label_path}*.{product_extension}")
                val_products.sort()

                #
                # Simply pick the last one
                #
                if "collection" in self.name.split(os.sep)[-1]:
                    val_label = glob.glob(
                        val_products[-1].replace("inventory_", "").split(".")[0]
                        + ".xml"
                    )[0]
                elif "bundle" in self.name.split(os.sep)[-1]:
                    val_labels = glob.glob(f"{val_label_path}bundle_*.xml")
                    val_labels.sort()
                    val_label = val_labels[-1]
                else:
                    val_label = glob.glob(val_products[-1].split(".")[0] + ".xml")[0]

                if not val_label:
                    raise Exception("No label for comparison found.")

            except BaseException:

                logging.warning("-- No similar label has been found.")
                #
                # 3-If we cannot find a kernel of the same type; for example
                #   is a first version of an archive, we compare with
                #   a label available in the test data directories.
                #
                try:
                    val_label_path = (
                        f"{self.setup.root_dir}"
                        f"/data/insight_spice/"
                        f"{self.product.collection.name}/"
                    )

                    #
                    # If this is the spice_kernels collection, we need to
                    # add the kernel type directory.
                    #
                    if (self.product.collection.name == "spice_kernels") and (
                        "collection" not in self.name
                    ):
                        val_label_path += self.name.split(os.sep)[-2] + os.sep
                    elif (self.product.collection.name == "miscellaneous") and (
                        "collection" not in self.name
                    ):
                        val_label_path += self.name.split(os.sep)[-2] + os.sep

                    #
                    # Simply pick the last one
                    #
                    product_extension = self.product.name.split(".")[-1]
                    val_products = glob.glob(f"{val_label_path}*.{product_extension}")
                    val_products.sort()

                    if "collection" in self.name.split(os.sep):
                        val_label = glob.glob(
                            val_products[-1].replace("inventory_", "").split(".")[0]
                            + ".xml"
                        )[0]
                    elif "bundle" in self.name.split(os.sep):
                        val_labels = glob.glob(f"{val_label_path}bundle_*.xml")
                        val_labels.sort()
                        val_label = val_labels[-1]
                    else:
                        val_label = glob.glob(val_products[-1].split(".")[0] + ".xml")[
                            0
                        ]

                    if not val_label:
                        raise Exception("No label for comparison found.")

                    logging.warning("-- Comparing with InSight test label.")
                except BaseException:
                    logging.warning("-- No label for comparison found.")

        #
        # If a similar label has been found the labels are compared and a
        # diff is being shown in the log. On top of that an HTML file with
        # the comparison is being generated.
        #
        if val_label:
            logging.info("")
            fromfile = val_label
            tofile = self.name
            dir = self.setup.working_directory

            compare_files(fromfile, tofile, dir, self.setup.diff)


class BundlePDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Bundle Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param readme: Readme product
    :rype readme: object
    """

    def __init__(self, setup: object, readme: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, readme)

        self.template = f"{setup.templates_directory}/template_bundle.xml"

        self.BUNDLE_LID = self.product.bundle.lid
        self.BUNDLE_VID = self.product.bundle.vid

        self.AUTHOR_LIST = setup.author_list
        self.START_TIME = setup.increment_start
        self.STOP_TIME = setup.increment_finish
        self.FILE_NAME = readme.name
        self.DOI = self.setup.doi
        self.BUNDLE_MEMBER_ENTRIES = ""

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        #
        # There might be more than one miscellaneous collection added in
        # an increment (especially if it is the first time that the collection
        # is generated and there have been previous releases.)
        #
        for collection in self.product.bundle.collections:
            if collection.name == "spice_kernels":
                self.COLL_NAME = "spice_kernel"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"
            if collection.name == "miscellaneous":
                if setup.information_model_float >= 1011001000.0:
                    self.COLL_NAME = "miscellaneous"
                else:
                    self.COLL_NAME = "member"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"
            if collection.name == "document":
                self.COLL_NAME = "document"
                self.COLL_LIDVID = collection.lid + "::" + collection.vid
                if collection.updated:
                    self.COLL_STATUS = "Primary"
                else:
                    self.COLL_STATUS = "Secondary"

            self.BUNDLE_MEMBER_ENTRIES += (
                f"{' ' * tab}<Bundle_Member_Entry>{eol}"
                f"{' ' * 2*tab}<lidvid_reference>"
                f"{self.COLL_LIDVID}</lidvid_reference>{eol}"
                f"{' ' * 2*tab}<member_status>"
                f"{self.COLL_STATUS}</member_status>{eol}"
                f"{' ' * 2*tab}<reference_type>"
                f"bundle_has_{self.COLL_NAME}_collection"
                f"</reference_type>{eol}"
                f"{' ' * tab}</Bundle_Member_Entry>{eol}"
            )

        self.write_label()

    def get_target_reference_type(self):
        """Get target reference type.

        :return: Literally ``bundle_to_target``
        :rtype: str
        """
        return "bundle_to_target"


class SpiceKernelPDS4Label(PDSLabel):
    """PDS Label child class to generate a non-MK PDS4 SPICE Kernel Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: SPICE Kernel product to be labeled
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{self.setup.templates_directory}/template_product_spice_kernel.xml"
        )

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = product.file_format
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        self.write_label()


class SpiceKernelPDS3Label(PDSLabel):
    """PDS Label child class to generate a PDS3 SPICE Kernel Label."""

    def __init__(self, mission, product):
        """Constructor."""
        PDSLabel.__init__(self, mission, product)

        self.template = (
            f"{self.setup.templates_directory}/template_product_spice_kernel.lbl"
        )

        self.FILE_NAME = f'"{product.name}"'
        self.INTERCHANGE_FORMAT = product.file_format
        self.START_TIME = product.start_time.split("Z")[0]
        self.STOP_TIME = product.stop_time.split("Z")[0]
        self.KERNEL_TYPE_ID = product.type.upper()
        self.KERNEL_TYPE = type_to_pds3_type(product.type.upper())
        self.RECORD_TYPE = product.record_type
        self.RECORD_BYTES = product.record_bytes
        self.SPICE_KERNEL_DESCRIPTION = self.format_description(product.description)

        self.set_kernel_ids(product)
        self.set_sclk_times(product)

        #
        # Values from template defaults first.
        #
        for item in self.setup.pds3_mission_template.items():
            if item[0] != "maklabel_options":
                maklabel_key = item[0]
                maklabel_val = item[1]
                self.__setattr__(maklabel_key, maklabel_val)

        #
        # Values extracted from the mission template.
        #
        for option in product.maklabel_options:
            values = self.setup.pds3_mission_template["maklabel_options"][option]

            for item in values.items():
                maklabel_key = item[0]
                maklabel_val = item[1]

                maklabel_val = format_multiple_values(maklabel_val)

                self.__setattr__(maklabel_key, maklabel_val)

        #
        # Remove the quotes from the target name and product version type.
        #
        if hasattr(self, "TARGET_NAME"):
            if '"' in self.TARGET_NAME:
                self.TARGET_NAME = self.TARGET_NAME.split('"')[1]
        if hasattr(self, "PRODUCT_VERSION_TYPE"):
            if '"' in self.PRODUCT_VERSION_TYPE:
                self.PRODUCT_VERSION_TYPE = self.PRODUCT_VERSION_TYPE.split('"')[1]
        if hasattr(self, "PLATFORM_OR_MOUNTING_NAME"):
            if (
                '"' in self.PLATFORM_OR_MOUNTING_NAME
                and self.PLATFORM_OR_MOUNTING_NAME != '"N/A"'
            ):
                self.PLATFORM_OR_MOUNTING_NAME = self.PLATFORM_OR_MOUNTING_NAME.split(
                    '"'
                )[1]

        self.write_label()

        if self.product.record_type == "STREAM":
            self.insert_text_label()
        else:
            self.insert_binary_label()

        logging.info("")

    @spice_exception_handler
    def set_sclk_times(self, product, system="UTC"):
        """Calculates the SCLK times for PDS3 labels."""
        if product.type.upper() == "CK":
            spice_id = spiceypy.bodn2c(self.setup.spice_name)

            (start_ticks, stop_ticks) = ck_coverage(
                product.path, timsys="SCLK", system=system
            )

            sclk_start = spiceypy.scdecd(spice_id, start_ticks)
            sclk_stop = spiceypy.scdecd(spice_id, stop_ticks)
        else:
            sclk_start = "N/A"
            sclk_stop = "N/A"

        self.SPACECRAFT_CLOCK_START_COUNT = f'"{sclk_start}"'
        self.SPACECRAFT_CLOCK_STOP_COUNT = f'"{sclk_stop}"'

    def set_kernel_ids(self, product):
        """Set the SPICE Kernel ID field of the label."""
        if product.type.upper() == "CK":
            naif_instrument_id = product.ck_kernel_ids()
        elif product.type.upper() == "IK":
            naif_instrument_id = product.ik_kernel_ids()
        else:
            naif_instrument_id = '"N/A"'

        self.NAIF_INSTRUMENT_ID = format_multiple_values(naif_instrument_id)

    def format_description(self, description):
        """Format the SPICE kernel description appropriately.

        The first line goes from character 33 to 78.
        Successive lines go from character  1 to 78.
        Last line has a blank space after the full stop.

        :return: Formatted label description
        :rtype: str
        """
        description = description.split()

        desc = ""
        line_len = 32
        for word in description:
            if line_len + len(word + " ") < 77:
                if not desc:
                    desc += '"' + word
                else:
                    desc += " " + word
                line_len += len(" " + word)
            else:
                desc += "\n"
                desc += word
                line_len = len(word)

        if line_len < 77:
            desc += ' "\n'

        return desc

    def insert_text_label(self):
        """Insert or update a label in a text kernel.

        The routine inserts the label, after the first line containing the
        kernel architecture specification and removes extra empty lines at the
        end of the kernel file.
        """
        with open(self.name, "r") as label:
            label_lines = label.readlines()

        with open(self.product.path, "r+") as kernel:
            kernel_lines = kernel.readlines()

        with open(self.product.path, "w") as kernel:

            if "KPL/" in kernel_lines[0]:
                kernel.write(kernel_lines[0])
            else:
                error_message(
                    f"Kernel {self.product.name} does not have "
                    f"architecture spec as first line."
                )

            kernel.write("\n\\beginlabel\n")

            for line in label_lines:
                if line.strip() != "END":
                    kernel.write(line)

            kernel.write("\\endlabel")

            write_line = True

            kernel_lines[-1] += "\n"

            #
            # If the kernel does not have a label add an empty line.
            #
            label_in_kernel = False
            for line in kernel_lines:
                if "\\beginlabel" in line:
                    label_in_kernel = True
            if not label_in_kernel:
                kernel.write("\n")

            #
            # Remove empty lines at the end of the kernel, add a new line
            # character in the last line.
            #
            lines_to_remove = 0
            for line in reversed(kernel_lines):
                if not line.strip():
                    lines_to_remove += 1
                if line.strip():
                    break
            lines_to_remove *= -1
            if lines_to_remove:
                kernel_lines = kernel_lines[:lines_to_remove]

            #
            # Add kernel list to kernel.
            #
            for line in kernel_lines:
                if "\\beginlabel" in line:
                    write_line = False
                    logging.info("-- Updating label in kernel.")

                if write_line:
                    if line != kernel_lines[0]:
                        kernel.write(line.rstrip() + "\n")

                if "\\endlabel" in line:
                    write_line = True

        logging.info("-- Label inserted to text kernel.")

    @spice_exception_handler
    def insert_binary_label(self):
        """Insert or update a label in a binary kernel.

        The routine inserts the label in the kernel comment.
        """
        label_lines = []
        with open(self.name, "r") as label:
            for line in label:
                if line.strip() != "END":
                    label_lines.append(line.rstrip())

        handle = spiceypy.dafopw(self.product.path)

        #
        # Extract comment from the kernel.
        #
        commnt = extract_comment(self.product.path, handle=handle)

        #
        # Remove the first N blank lines.
        #
        j = 0
        for line in commnt:
            if line.strip():
                break
            j += 1
        if j > 0:
            commnt = commnt[j:]

        #
        # Add a blank character in each empty line.
        #
        for i, line in enumerate(commnt):
            if not line:
                commnt[i] = " "

        #
        # Add or replace label to comment list.
        #
        new_commnt = ["\\beginlabel"] + label_lines + ["\\endlabel"] + 2 * [" "]

        if "\\endlabel" in commnt:
            index = commnt.index("\\endlabel")
            commnt = commnt[index + 1 :]

        new_commnt += commnt

        #
        # Delete comment from the kernel.
        #
        spiceypy.dafdc(handle)

        #
        # Insert updated comment to kernel.
        #
        spiceypy.dafac(handle, new_commnt)

        #
        # Close file handle.
        #
        spiceypy.dafcls(handle)

        logging.info("-- Label inserted to binary kernel.")


class MetaKernelPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 SPICE Kernel MK Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: MK product to label
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{setup.templates_directory}/template_product_spice_kernel_mk.xml"
        )

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = "Character"
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        self.KERNEL_INTERNAL_REFERENCES = self.get_kernel_internal_references()

        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()

    def get_kernel_internal_references(self):
        """Get the MK label internal references.

        :return: PDS4 formatted Kernel list used by the label for internal
                 references.
        :rtype: str
        """
        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        #
        # From the collection we only use kernels in the MK
        #
        kernel_list_for_label = ""
        for kernel in self.product.collection_metakernel:
            #
            # The kernel lid cannot be obtained from the list; it is
            # merely a list of strings.
            #
            kernel_type = extension_to_type(kernel)
            kernel_lid = "{}:spice_kernels:{}_{}".format(
                self.setup.logical_identifier, kernel_type, kernel.lower()
            )

            kernel_list_for_label += (
                    f"{' ' * 2 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 3 * tab}<lid_reference>{kernel_lid}"
                      f"</lid_reference>{eol}"
                    + f"{' ' * 3 * tab}<reference_type>data_to_associate"
                      f"</reference_type>{eol}"
                    + f"{' ' * 2 * tab}</Internal_Reference>{eol}"
            )

        kernel_list_for_label = kernel_list_for_label.rstrip() + eol

        return kernel_list_for_label


class OrbnumFilePDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Orbit Number File Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: ORBNUM product to label
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = f"{setup.templates_directory}/template_product_orbnum_table.xml"

        #
        # Fields from orbnum object.
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = "Character"
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.DESCRIPTION = product.description
        self.HEADER_LENGTH = str(product.header_length)
        self.TABLE_CHARACTER_DESCRIPTION = product.table_char_description

        #
        # The orbnum table data starts one byte after the header section.
        #
        self.TABLE_OFFSET = str(product.header_length)
        self.TABLE_RECORDS = str(product.records)

        #
        # The ORBNUM utility produces an information ground set regardless
        # of the parameters listed in ORBIT_PARAMS. This set consists of 4
        # parameters.
        #
        self.NUMBER_OF_FIELDS = str(len(product.params.keys()))
        if self.END_OF_LINE == "Carriage-Return Line-Feed":
            eol_length = 1
        else:
            eol_length = 0
        self.FIELDS_LENGTH = str(product.record_fixed_length + eol_length)
        self.FIELDS = self.get_table_character_fields()

        if self.TABLE_CHARACTER_DESCRIPTION:
            self.TABLE_CHARACTER_DESCRIPTION = self.get_table_character_description()

        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()

    def get_table_character_fields(self):
        """Get the Table Character fields.

        :return: Table Character fields
        :rytpe: str
        """
        fields = ""
        for param in self.product.params.values():
            field = self.field_template(
                param["name"],
                param["number"],
                param["location"],
                param["type"],
                param["length"],
                param["format"],
                param["description"],
                param["unit"],
                self.product.blank_records,
            )
            fields += field

        return fields

    def get_table_character_description(self):
        """Get The description of the Table Character.

        :return: Table Character description
        :rytpe: str
        """
        description = (
            f"{self.setup.eol_pds4}{' ' * 6*self.setup.xml_tab}<description>"
            f"{self.product.table_char_description}"
            f"</description>{self.setup.eol_pds4}"
        )

        return description

    def field_template(
        self, name, number, location, type, length, format, description, unit, blanks
    ):
        """For a label provide all the parameters required for an ORBNUM field character.

        :param name: Name field
        :type name: str
        :param number: Number field
        :type number: str
        :param location: Location field
        :type location: str
        :param type: Type field
        :type type: str
        :param length: Length field
        :type length: str
        :param format: Format field
        :type format: str
        :param description: Description field
        :type description: str
        :param unit: Unit field
        :type unit: str
        :param blanks: Blank space missing constant indication
        :type blanks: str
        :return: Field Character for ORBNUM PDS4 label
        :rtype: str
        """
        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        field = (
            f'{" " * (4*tab)}<Field_Character>{eol}'
            f'{" " * (4*tab + 1*tab)}<name>{name}</name>{eol}'
            f'{" " * (4*tab + 1*tab)}<field_number>{number}</field_number>{eol}'
            f'{" " * (4*tab + 1*tab)}<field_location unit="byte">{location}'
            f"</field_location>{eol}"
            f'{" " * (4*tab + 1*tab)}<data_type>{type}</data_type>{eol}'
            f'{" " * (4*tab + 1*tab)}<field_length unit="byte">{length}'
            f"</field_length>{eol}"
            f'{" " * (4*tab + 1*tab)}<field_format>{format}</field_format>{eol}'
        )
        if unit:
            field += f'{" " * (4*tab + 1*tab)}<unit>{unit}</unit>{eol}'
        field += f'{" " * (4*tab + 1*tab)}<description>{description}</description>{eol}'
        if blanks and name != "No.":
            field += (
                f'{" " * (4*tab + 1*tab)}<Special_Constants>{eol}'
                f'{" " * (4*tab+ 2 * tab)}<missing_constant>blank space'
                f"</missing_constant>{eol}"
                f'{" " * (4*tab + 1*tab)}</Special_Constants>{eol}'
            )
        field += f'{" " * (4*tab)}</Field_Character>{eol}'

        return field


class InventoryPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Collection Inventory Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Collection to label
    :type product: object
    :param inventory: Inventory Product of the Collection
    :type inventory: object
    """

    def __init__(self, setup: object, collection: object, inventory: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, inventory)

        self.collection = collection
        self.template = (
            f"{setup.templates_directory}/template_collection_{collection.type}.xml"
        )

        self.COLLECTION_LID = self.collection.lid
        self.COLLECTION_VID = self.collection.vid

        #
        # The start and stop time of the miscellaneous collection
        # differs from the SPICE kernels collection; the document
        # collection does not have start and stop times.
        #
        if collection.name == "miscellaneous":
            #
            # Obtain the latest checksum product and extract the start and stop
            # times.
            #
            start_times = []
            stop_times = []
            for product in collection.product:
                if "checksum" in product.name:
                    start_times.append(product.start_time)
                    stop_times.append(product.stop_time)
            start_times.sort()
            stop_times.sort()

            self.START_TIME = start_times[0]
            self.STOP_TIME = stop_times[-1]

        else:
            #
            # The increment start and stop times are still defined by the
            # spice_kernels collection.
            #
            self.START_TIME = setup.increment_start
            self.STOP_TIME = setup.increment_finish

        self.FILE_NAME = inventory.name

        #
        # Count number of lines in the inventory file
        #
        f = open(self.product.path)
        self.N_RECORDS = str(len(f.readlines()))
        f.close()

        self.name = collection.name.split(".")[0] + ".xml"
        self.write_label()

    def get_target_reference_type(self):
        """Get target reference type.

        :return: Literally ``collection_to_target``
        :rtype: str
        """
        return "collection_to_target"


class InventoryPDS3Label(PDSLabel):
    """PDS Label child class to generate a PDS3 Index Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Index Collection
    :type product: object
    :param inventory: Index Product
    :type inventory: object
    """

    def __init__(
        self, mission: object, collection: object, inventory: object
    ) -> object:
        """Constructor."""
        PDSLabel.__init__(self, mission, inventory)

        self.collection = collection
        self.template = (
            self.root_dir
            + "/templates/pds3/template_collection_{}.lbl".format(collection.type)
        )

        self.VOLUME_ID = self.setup.volume_id
        self.ROW_BYTES = str(self.product.row_bytes)
        self.ROWS = str(self.product.rows)

        for i, bytes in enumerate(self.product.column_bytes):

            setattr(
                self, f"START_BYTE_{i+1:02d}", str(self.product.column_start_bytes[i])
            )
            setattr(self, f"BYTES_{i+1:02d}", str(bytes))

        file_types = self.product.file_types
        if len(file_types) == 1:
            indexed_file_name = f"*.{file_types}"
        else:
            file_types.sort()
            indexed_file_name = "{" + self.setup.eol_pds3
            for file_type in file_types:
                indexed_file_name += f'{29*" "}  "*.{file_type}",{self.setup.eol_pds3}'

            indexed_file_name = (
                indexed_file_name[:-3] + self.setup.eol_pds3 + 29 * " " + "}\n"
            )

        self.INDEXED_FILE_NAME = indexed_file_name

        self.write_label()


class DocumentPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Document Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Collection to label
    :type collection: object
    :param inventory: Inventory Product of the Collection
    :type inventory: object
    """

    def __init__(self, setup: object, collection: object, inventory: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, inventory)

        self.setup = setup
        self.collection = collection
        self.template = (
            f"{setup.templates_directory}/template_product_html_document.xml"
        )

        self.PRODUCT_LID = inventory.lid
        self.PRODUCT_VID = inventory.vid
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish
        self.FILE_NAME = inventory.name

        self.name = collection.name.split(".")[0] + ".xml"

        self.write_label()


class ChecksumPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Checksum Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: Checksum product to label
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{setup.templates_directory}/template_product_checksum_table.xml"
        )

        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = "Character"
        self.START_TIME = self.product.start_time
        self.STOP_TIME = self.product.stop_time
        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()


class ChecksumPDS3Label(PDSLabel):
    """PDS Label child class to generate a PDS3 Checksum Label.

    :param setup: NPB  execution Setup object
    :type setup: object
    :param product: Checksum product to label
    :type product: object
    """

    def __init__(self, setup, product):
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{setup.templates_directory}/template_product_checksum_table.lbl"
        )

        self.VOLUME_ID = self.setup.volume_id.upper()
        self.PRODUCT_CREATION_TIME = product.creation_time
        self.RECORD_BYTES = str(self.product.record_bytes)
        self.FILE_RECORDS = str(self.product.file_records)
        self.BYTES = str(self.product.bytes)

        self.name = "checksum.lbl"

        self.write_label()
