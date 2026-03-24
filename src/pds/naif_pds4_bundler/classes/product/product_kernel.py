"""Implementation of the SPICE kernel file product class."""
import logging
import os
import shutil

import spiceypy

from .product import Product
from ...pipeline.runtime import error_message
from ...utils import ck_coverage
from ...utils import dsk_coverage
from ...utils import extension_to_type
from ...utils import pck_coverage
from ...utils import product_mapping
from ...utils import safe_make_directory
from ...utils import spk_coverage
from ..label import SpiceKernelPDS3Label
from ..label import SpiceKernelPDS4Label


class SpiceKernelProduct(Product):
    """Class that defines a SPICE Kernel file archive product.

    :param setup:      NPB run Setup object
    :param name:       SPICE Kernel filename
    :param collection: SPICE Kernel collection that will be a container of
                       the SPICE Kernel Product object
    """

    def __init__(self, setup, name: str, collection) -> None:
        """Constructor."""
        self.collection = collection
        self.setup = setup
        self.name = name

        self.extension = name.split(".")[-1].strip()
        self.type = extension_to_type(self)

        if setup.pds_version == "4":
            #
            # Determine if it is a binary or a text kernel.
            #
            if self.extension[0].lower() == "b":
                self.file_format = "Binary"
            else:
                self.file_format = "Character"

            self.lid = self.product_lid()
            self.vid = self.product_vid()
            ker_dir = "spice_kernels"
        else:
            #
            # Determine if it is a binary or a text kernel.
            #
            if self.extension[0].lower() == "b":
                self.file_format = "BINARY"
                self.record_type = "FIXED_LENGTH"
                self.record_bytes = "1024"
            else:
                self.file_format = "ASCII"
                self.record_type = "STREAM"
                self.record_bytes = '"N/A"'

            ker_dir = "data"

        self.collection_path = setup.staging_directory + os.sep + ker_dir + os.sep

        product_path = self.collection_path + self.type + os.sep

        #
        # We generate the kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # We copy the kernel to the staging directory. If multiple directories
        # are provided, the first one is used.
        #
        logging.info(f"-- Copy {self.name} to staging directory.")
        if not os.path.isfile(product_path + self.name):
            origin_path = ""
            for directory in self.setup.kernels_directory:
                file = [
                    os.path.join(root, ker)
                    for root, dirs, files in os.walk(directory)
                    for ker in files
                    if name == ker
                ]

                #
                # If the file exists save the path and escape the loop.
                #
                if file:
                    origin_path = file[0]
                    self.new_product = True
                    break

            #
            # If after the first loop the file is not present we do another
            # loop to see if the file needs mapping.
            #
            if not origin_path:
                for directory in self.setup.kernels_directory:
                    file = [
                        os.path.join(root, ker)
                        for root, dirs, files in os.walk(directory)
                        for ker in files
                        if product_mapping(self.name, self.setup) == ker
                    ]

                    if file:
                        origin_path = file[0]
                        self.new_product = True
                        logging.info(
                            f"-- Mapping {product_mapping(self.name, self.setup)} "
                            f"with {self.name}"
                        )
                        break

            #
            # If after the two loops the file is not present raise an error.
            #
            if not origin_path:
                error_message(f"{self.name} not present in {directory}.", setup=setup)

            shutil.copy2(origin_path, product_path + os.sep + self.name)

        else:
            logging.warning(f"     {self.name} already present in staging directory.")

            #
            # Even though it is not a 'new' product, the file is present in
            # the staging area because it was generated in a prior run.
            #
            self.new_product = True

        #
        # We update the path after having copied the kernel.
        #
        self.path = product_path + self.name

        self.coverage()
        self.description = self.read_description()

        Product.__init__(self)

        #
        # Extract the required information from the kernel list read from
        # configuration for the product.
        #
        (missions, observers, targets) = self.get_mission_and_observer_and_target()

        self.missions = missions
        self.targets = targets
        self.observers = observers

        #
        # The kernel is labeled.
        #
        logging.info(f"-- Labeling {self.name}...")
        if setup.pds_version == "4":
            self.label = SpiceKernelPDS4Label(setup, self)
        else:
            self.maklabel_options = self.read_maklabel_options()
            self.label = SpiceKernelPDS3Label(setup, self)

    def product_lid(self) -> str:
        """Determine product logical identifier (LID).

        :return: product LID
        """
        product_lid = "{}:spice_kernels:{}_{}".format(
            self.setup.logical_identifier, self.type, self.name
        ).lower()

        return product_lid

    @staticmethod
    def product_vid() -> str:
        """Determine product logical identifier (VID).

        :return: product VID
        """
        product_vid = "1.0"

        return product_vid

    def read_description(self) -> str:
        """Read the kernel list to return the description.

        The generated kernel list file must be used because it contains the
        description.

        :return: Kernel Description from the Kernel List
        """
        kernel_list_file = (
            self.setup.working_directory
            + os.sep
            + f"{self.setup.mission_acronym}_{self.setup.run_type}_"
            f"{int(self.setup.release):02d}.kernel_list"
        )

        get_token = False
        description = False

        with open(kernel_list_file, "r") as lst:
            for line in lst:
                if self.name in line:
                    get_token = True
                if get_token and "DESCRIPTION" in line:
                    description = line.split("=")[-1].strip()
                    break

        if not description:
            error_message(
                f"{self.name} does not have a DESCRIPTION on {kernel_list_file}.",
                setup=self.setup,
            )

        return description

    def read_maklabel_options(self) -> str:
        """Read the kernel list to return the ``MAKLABEL_OPTIONS``.

        The generated kernel list file must be used because it contains the
        ``MAKLABEL_OPTIONS``.

        :return: ``MAKLABEL_OPTIONS`` from kernel list
        """
        kernel_list_file = (
            self.setup.working_directory
            + os.sep
            + f"{self.setup.mission_acronym}_{self.setup.run_type}_"
            f"{int(self.setup.release):02d}.kernel_list"
        )

        get_token = False
        maklabel_options = False

        with open(kernel_list_file, "r") as lst:
            for line in lst:
                if self.name in line:
                    get_token = True
                if get_token and "MAKLABEL_OPTIONS" in line:
                    maklabel_options = line.split("=")[-1].strip().split()
                    get_token = False

        if not maklabel_options:
            error_message(
                f"{self.name} does not have a MAKLABEL_OPTIONS on {kernel_list_file}.",
                setup=self.setup,
            )

        return maklabel_options

    def coverage(self) -> None:
        """Determine the product coverage."""
        system = "UTC"
        #
        # Before computing the coverage we check if the label is already
        # present.
        #
        coverage = []
        product_label = self.path.split(".")[0] + ".xml"
        if os.path.exists(product_label):
            with open(product_label, "r") as lbl:
                start = ""
                stop = ""
                for line in lbl:
                    if "<start_date_time>" in line:
                        start = line.split("<start_date_time>")[-1]
                        start = start.split("</start_date_time>")[0]
                    if "<stop_date_time>" in line:
                        stop = line.split("<stop_date_time>")[-1]
                        stop = stop.split("</stop_date_time>")[0]
                    if start and stop:
                        coverage = [start, stop]
                        logging.warning(
                            f"-- Coverage obtained from existing "
                            f"label: "
                            f"{product_label.split(os.sep)[-1]}"
                        )
                        break

        if not coverage:
            if self.type.lower() == "spk":

                #
                # For PDS3, do not consider the main body for coverage but all
                # bodies, to follow MAKLABEL style.
                #
                if self.setup.pds_version == "3":
                    main_name = False
                else:
                    main_name = self.setup.spice_name

                coverage += spk_coverage(
                    self.path,
                    main_name=main_name,
                    date_format=self.setup.date_format,
                    system=system,
                )
            elif self.type.lower() == "ck":
                coverage += ck_coverage(
                    self.path, date_format=self.setup.date_format, system=system
                )
            elif self.extension.lower() == "bpc":
                coverage += pck_coverage(
                    self.path, date_format=self.setup.date_format, system=system
                )
            elif self.type.lower() == "dsk":
                coverage += dsk_coverage(
                    self.path, date_format=self.setup.date_format, system=system
                )
            else:
                if self.setup.pds_version == "3":
                    coverage = ['"N/A"', '"N/A"']
                else:
                    coverage = [self.setup.mission_start, self.setup.mission_finish]

        self.start_time = coverage[0]
        self.stop_time = coverage[-1]

    def ck_kernel_ids(self) -> str:
        """Extract IDs from CK.

        :return: List of IDs present in the CK
        """
        ids = spiceypy.ckobj(f"{self.path}")

        id_list = []
        for id in ids:
            id_list.append(str(id))

        id_list = sorted(id_list, reverse=True)

        return ",".join(id_list)

    def ik_kernel_ids(self) -> str:
        """Extract IDs from IK.

        :return: List of IDs present in the IK
        :rtype: list
        """
        with open(f"{self.path}", "r") as f:

            id_list = []
            parse_bool = False

            for line in f:

                if "begindata" in line:
                    parse_bool = True

                if "begintext" in line:
                    parse_bool = False

                if "INS-" in line and parse_bool:
                    line = line.lstrip()
                    line = line.split("_")
                    id_list.append(line[0][3:])

        id_list = list(set(id_list))

        return ",".join(id_list)
