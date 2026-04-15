"""PDS Label Class and Child Classes Implementation."""

import glob
import logging
import os

from ...pipeline.runtime import handle_npb_error
from ...utils import add_carriage_return, compare_files


class PDSLabel:
    """Class to generate a PDS Label.

    :param setup:   NPB execution Setup object
    :param product: Product to be labeled
    """

    def __init__(self, setup, product) -> None:
        """Constructor."""
        if setup.pds_version == "4":
            try:
                context_products = product.collection.bundle.context_products
                if not context_products:
                    raise Exception("No context products from bundle in collection")
            except BaseException:
                context_products = product.bundle.context_products

        self.name = ''
        self.product = product
        self.setup = setup

        #
        # Fields from setup
        #
        self.root_dir = setup.root_dir
        self.mission_acronym = setup.mission_acronym

        if setup.pds_version == "4":
            self.XML_MODEL = setup.xml_model
            self.SCHEMA_LOCATION = setup.schema_location
            self.INFORMATION_MODEL_VERSION = setup.information_model

            #
            # Needs to be built for several Missions.
            #
            if hasattr(setup, "secondary_missions"):
                if len(setup.secondary_missions) == 1:
                    missions_text = (
                        f"{setup.mission_name} and {setup.secondary_missions[0]}"
                    )
                else:
                    missions_text = f"{setup.mission_name}, "
                    for i in range(len(setup.secondary_missions)):
                        if i == len(setup.secondary_missions) - 1:
                            missions_text += f"and {setup.secondary_missions[i]}"
                        else:
                            missions_text += f"{setup.secondary_missions[i]}, "

                self.PDS4_MISSION_NAME = f"{missions_text}"
            else:
                self.PDS4_MISSION_NAME = f"{setup.mission_name}"

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
                handle_npb_error(
                    "End of Line provided via configuration is not CRLF nor LF.",
                    setup=self.setup,
                )

            self.BUNDLE_DESCRIPTION_LID = f"{setup.logical_identifier}:document:spiceds"

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
        # For labels that need to include all missions, observers and targets
        # of the setup.
        #
        if (
            type(self).__name__ != "SpiceKernelPDS4Label"
            and type(self).__name__ != "MetaKernelPDS4Label"
            and type(self).__name__ != "OrbnumFilePDS4Label"
        ):
            #
            # Obtain all Missions
            #
            mis = [self.setup.mission_name]

            if hasattr(self.setup, "secondary_missions"):
                sec_mis = self.setup.secondary_missions
                if not isinstance(sec_mis, list):
                    sec_mis = [sec_mis]
            else:
                sec_mis = []

            self.missions = mis + sec_mis

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
            self.missions = product.missions
            self.observers = product.observers
            self.targets = product.targets

        if setup.pds_version == "4":
            self.MISSIONS = self.get_missions()
            self.OBSERVERS = self.get_observers()
            self.TARGETS = self.get_targets()

    def get_missions(self):
        """Get the label mission from the context products.

        :return: List of missions to be included in the label
        :rtype: list
        """
        miss = self.missions

        if not isinstance(miss, list):
            miss = [miss]

        mis_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab
        for mis in miss:
            if mis:
                mis_name = mis
                for product in context_products:
                    if product["name"][0] == mis_name and (
                        product["type"][0] == "Mission"
                        or product["type"][0] == "Other Investigation"
                    ):
                        mission_lid = product["lidvid"].split("::")[0]
                        mission_type = product["type"][0]

                if not mission_lid:
                    handle_npb_error(
                        f"LID has not been obtained for mission {mis}.",
                        setup=self.setup,
                    )

                mis_list_for_label += (
                    f"{' ' * 2 * tab}<Investigation_Area>{eol}"
                    + f"{' ' * 3 * tab}<name>{mis_name}</name>{eol}"
                    + f"{' ' * 3 * tab}<type>{mission_type}</type>{eol}"
                    + f"{' ' * 3 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 4 * tab}<lid_reference>{mission_lid}"
                    f"</lid_reference>{eol}" + f"{' ' * 4 * tab}<reference_type>"
                    f"{self.get_mission_reference_type()}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2 * tab}</Investigation_Area>{eol}"
                )
        if not mis_list_for_label:
            handle_npb_error(
                f"{self.product.name} missions not defined.", setup=self.setup
            )
        mis_list_for_label = mis_list_for_label.rstrip() + eol

        return mis_list_for_label

    def get_mission_reference_type(self):
        """Get the mission reference type.

        :return: Mission_Reference_Type value for PDS4 label
        :rtype: str
        """
        if self.__class__.__name__ == "ChecksumPDS4Label":
            ref_type = "ancillary_to_investigation"
        elif self.__class__.__name__ == "BundlePDS4Label":
            ref_type = "bundle_to_investigation"
        elif self.__class__.__name__ == "DocumentPDS4Label":
            ref_type = "document_to_investigation"
        elif self.__class__.__name__ == "InventoryPDS4Label":
            ref_type = "collection_to_investigation"
        elif self.__class__.__name__ == "OrbnumFilePDS4Label":
            if self.setup.information_model_float >= 1014000000.0:
                ref_type = "ancillary_to_investigation"
            else:
                ref_type = "data_to_investigation"
        else:
            ref_type = "data_to_investigation"

        return ref_type

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
                    handle_npb_error(
                        f"LID has not been obtained for observer {ob}.",
                        setup=self.setup,
                    )

                obs_list_for_label += (
                    f"{' ' * 3 * tab}<Observing_System_Component>{eol}"
                    + f"{' ' * (3+1) * tab}<name>{ob_name}</name>{eol}"
                    + f"{' ' * (3+1) * tab}<type>{ob_type}</type>{eol}"
                    + f"{' ' * (3+1) * tab}<Internal_Reference>{eol}"
                    + f"{' ' * (3 + 2) * tab}<lid_reference>{ob_lid}"
                    f"</lid_reference>{eol}"
                    + f"{' ' * (3 + 2) * tab}<reference_type>is_instrument_host"
                    f"</reference_type>{eol}"
                    + f"{' ' * (3+1) * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 3 * tab}</Observing_System_Component>{eol}"
                )

        if not obs_list_for_label:
            handle_npb_error(
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
                    f"{' ' * 2 * tab}<Target_Identification>{eol}"
                    + f"{' ' * 3 * tab}<name>{target_name}</name>{eol}"
                    + f"{' ' * 3 * tab}<type>{target_type}</type>{eol}"
                    + f"{' ' * 3 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 4 * tab}<lid_reference>{target_lid}"
                    f"</lid_reference>{eol}" + f"{' ' * 4 * tab}<reference_type>"
                    f"{self.get_target_reference_type()}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2 * tab}</Target_Identification>{eol}"
                )

        if not tar_list_for_label:
            handle_npb_error(f"{self.product.name} targets not defined.", setup=self.setup)
        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label

    def get_target_reference_type(self):
        """Get the target reference type.

        :return: Target_Reference_Type value for PDS4 label
        :rtype: str
        """
        if self.__class__.__name__ == "ChecksumPDS4Label":
            ref_type = "ancillary_to_target"
        elif self.__class__.__name__ == "BundlePDS4Label":
            ref_type = "bundle_to_target"
        elif self.__class__.__name__ == "InventoryPDS4Label":
            ref_type = "collection_to_target"
        elif self.__class__.__name__ == "OrbnumFilePDS4Label":
            if self.setup.information_model_float >= 1014000000.0:
                ref_type = "ancillary_to_target"
            else:
                ref_type = "data_to_target"
        else:
            ref_type = "data_to_target"

        return ref_type

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
            work_dir = self.setup.working_directory

            compare_files(fromfile, tofile, work_dir, self.setup.diff)
