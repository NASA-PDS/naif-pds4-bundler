"""Collection Class amd Child Classes Implementation."""
import glob
import logging
import os

import spiceypy

from ..utils import et_to_date
from ..utils import extension_to_type
from .log import error_message
from .product import PDS3DocumentProduct


class Collection(object):
    """Class to generate a PDS4 Collection.

    :param type: Collection type: kernels, documents or miscellaneous
    :type type: str
    :param setup: Setup Object
    :type setup: object
    :param bundle: Bundle Object to which the Collection belongs to
    :type bundle: object
    """

    def __init__(self, type: str, setup: object, bundle: object) -> object:
        """Constructor."""
        self.product = []
        self.name = type
        self.setup = setup
        self.bundle = bundle

        #
        # To know whether if the collection has been updated or not.
        #
        self.updated = False

        if setup.pds_version == "4":
            self.set_collection_lid()

    def add(self, element):
        """Add a Product to the Collection.

        :param element: Product to add to Collection
        :type element: object
        """
        self.product.append(element)

        #
        # If an element has been added to the collection then, the collection
        # must be updated.
        #
        self.updated = True

    def set_collection_lid(self):
        """Set the Bundle LID."""
        if self.setup.pds_version != "3":
            self.lid = f"{self.setup.logical_identifier}:{self.type}"

    def set_collection_vid(self):
        """Set the Bundle VID.

        In general Collection versions are not equal to the release number.
        If the collection has been updated we obtain the increased
        version, but if it has not been updated we use the previous
        version.

        Given the case thatt he version cannot be determined: if it is the
        SPICE kernels collection assume is the same version as the bundle,
        otherwise we set it to 1.
        """
        if self.setup.increment:
            try:
                versions = glob.glob(
                    f"{self.setup.bundle_directory}/"
                    f"{self.setup.mission_acronym}_spice/"
                    f"{self.name}/*{self.name}*"
                )
                versions += glob.glob(
                    f"{self.setup.staging_directory}/{self.name}/*{self.name}*"
                )

                versions.sort()

                if self.updated:
                    version = int(versions[-1].split("v")[-1].split(".")[0]) + 1
                else:
                    version = int(versions[-1].split("v")[-1].split(".")[0])

                vid = "{}.0".format(version)
                logging.info(
                    f"-- Collection of {self.type} version set to "
                    f"{version}, derived from:"
                )
                logging.info(f"   {versions[-1]}")
                logging.info("")

            except BaseException:
                if self.name == "spice_kernel":
                    ver = int(self.setup.release)
                else:
                    ver = 1

                logging.warning(
                    f"-- No {self.type} collection available in previous increment."
                )
                logging.warning(f"-- Collection of {self.type} version set to: {ver}.")
                vid = "{}.0".format(ver)
                logging.info("")

        else:
            logging.warning(
                f"-- Collection of {self.type} version set "
                f"to: {int(self.setup.release)}."
            )
            vid = "{}.0".format(int(self.setup.release))
            logging.info("")

        self.vid = vid


class SpiceKernelsCollection(Collection):
    """Collection child class to generate a PDS4 SPICE Kernels Collection.

    :param setup: NPB execution setup object
    :type setup: object
    :param bundle: Bundle object
    :type bundle: object
    :param list: Kernel List object
    :type list: object
    """

    def __init__(self, setup: object, bundle: object, list: object) -> object:
        """Constructor."""
        line = f"Step {setup.step} - SPICE kernel collection/data processing"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        self.bundle = bundle
        self.list = list
        self.type = "spice_kernels"
        """Collection type (`str`)."""

        if setup.pds_version == "4":
            self.start_time = setup.mission_start
            self.stop_time = setup.mission_finish

        Collection.__init__(self, self.type, setup, bundle)

    def determine_meta_kernels(self):
        """Determine the name of the Meta-kernel(s) to be generated.

        :return: Dictionary of meta-kernels to be generated. The keys list the
                 meta-kernels and the values whether if they are provided by the
                 user or not.
        :rtype: dictionary.
        """
        line = f"Step {self.setup.step} - Generation of meta-kernel(s)"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        meta_kernels = {}
        #
        # First check if a meta-kernel has been provided via configuration by
        # the user. If so, only the provided meta-kernels will be taken into
        # account (there is no hybrid possibility but NPB provides a warning
        # message if more meta-kernels are expected).
        #
        if hasattr(self.setup, "mk_inputs") and (self.setup.args.faucet != "labels"):
            if "file" in self.setup.mk_inputs:
                mks = self.setup.mk_inputs["file"]
                if not isinstance(mks, list):
                    mks = [mks]
                for mk in mks:
                    if not os.path.exists(mk):
                        logging.info("")
                        error_message(
                            f"Meta-kernel provided via"
                            f" configuration"
                            f" does not exist: {mk}"
                        )
                    else:
                        meta_kernels[mk] = True
            else:
                logging.warning("-- Configuration item mk_inputs is empty.")

        #
        # Second we check if meta-kernels are indicated with the kernel list.
        # Note that if kernels are provided as input, the ones present in the
        # kernel list are ignored.
        #
        # It is assumed that these kernels will be in the kernels_directory,
        # under the mk subdirectory.
        #
        if not meta_kernels:
            for kernel in self.list.kernel_list:
                kernel_present = False
                if ".tm" in kernel:
                    for kernel_dir in self.setup.kernels_directory:
                        path = f"{kernel_dir}/mk/{kernel}"
                        if os.path.exists(path):
                            meta_kernels[path] = True
                            kernel_present = True
                            break
                    if not kernel_present:
                        #
                        # If the kernel is not present we don't provide the path.
                        #
                        logging.info(
                            f"-- {kernel} not provided as input in kernels directory."
                        )
                        meta_kernels[kernel] = False

        #
        # If no meta-kernels are provided as inputs or in the kernel list,
        #
        if not meta_kernels:
            if self.setup.args.faucet == "labels":
                logging.info(
                    "-- No meta-kernel provided as input in the plan in labeling mode."
                )
            else:
                logging.info(
                    "-- No meta-kernel provided in the kernel list or via configuration."
                )

            #
            # NPB will try to determine if a meta-kernel can be generated
            # only using the information from the configuration file.
            # This will only work if the bundle only includes one meta-kernel
            # and the only pattern in the filename is the VERSION.
            #
            # This will happen only if there are kernels in the collection.
            #
            # If the kernel already exists, it will not be generated.
            #
            if (
                (hasattr(self.setup, "mk"))
                and (self.product)
                and (self.setup.args.faucet != "labels")
            ):
                if (
                    self.setup.mk.__len__() == 1
                    and self.setup.mk[0]["name"].__len__() == 1
                    and self.setup.mk[0]["name"][0].__len__() == 1
                    and self.setup.mk[0]["name"][0]["pattern"].__len__() == 2
                    and not isinstance(self.setup.mk[0]["name"][0]["pattern"], list)
                ):
                    if self.setup.mk[0]["name"][0]["pattern"]["#text"] == "VERSION":
                        version_length = int(
                            self.setup.mk[0]["name"][0]["pattern"]["@length"]
                        )

                        version = "1"
                        meta_kernel = self.setup.mk[0]["@name"].replace(
                            "$VERSION", version.zfill(version_length)
                        )
                        existing_path = f"{self.setup.bundle_directory}/{self.setup.mission_acronym}_spice/spice_kernels/mk/{meta_kernel}"
                        if not os.path.exists(existing_path):
                            meta_kernels[meta_kernel] = False

        if not meta_kernels:
            logging.info("")
            logging.warning("-- No Meta-kernel will be generated.")
        else:
            #
            # Check that the meta-kernels are not present. If a meta-kernel is
            # present stop the execution.
            #
            for meta_kernel in sorted(meta_kernels):
                if self.setup.pds_version == "4":
                    existing_path = f"{self.setup.bundle_directory}/{self.setup.mission_acronym}_spice/spice_kernels/mk/{meta_kernel}"
                else:
                    existing_path = f"{self.setup.bundle_directory}/{self.setup.volume_id}/extras/mk/{meta_kernel}"
                if os.path.exists(existing_path):
                    error_message(f"MK already exists in the archive: {existing_path}")

        return meta_kernels

    def set_increment_times(self):
        """Determine the archive increment start and finish times.

        This is done based on the identification of the coverage of a given
        SPK or CK kernel. Alternatively it can be provided as a parameter of the
        execution.
        """
        line = (
            f"Step {self.setup.step} - Determine archive increment "
            f"start and finish times"
        )
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        increment_start = ""
        increment_finish = ""
        #
        # The increment start and finish times are to be set with the MK.
        # This is the first step taken.
        #
        # Match the pattern with the kernels in the meta-kernel.
        #
        try:
            increment_starts = []
            increment_finishs = []
            for prod in self.product:
                if hasattr(prod, "mk_sets_coverage"):
                    if prod.mk_sets_coverage:
                        increment_starts.append(prod.start_time)
                        increment_finishs.append(prod.stop_time)
                        logging.info(
                            f"-- Using MK: {prod.name} to determine "
                            f"increment coverage."
                        )

            increment_start = min(increment_starts)
            increment_finish = max(increment_finishs)

        except BaseException:
            #
            # If no MKs are provided in the increment. First check if an
            # increment stop time has been provided as an input
            # parameter.
            #
            logging.warning("-- No Meta-kernels found to determine increment " "times.")

            if hasattr(self.setup, "increment_start"):
                logging.info(
                    f"   Increment stop time set to: "
                    f"{self.setup.increment_start} "
                    f"as provided from configuration file"
                )
                increment_start = self.setup.increment_start

            if hasattr(self.setup, "increment_finish"):
                logging.info(
                    f"   Increment finish time set to: "
                    f"{self.setup.increment_finish} "
                    f"as provided from configuration file"
                )
                increment_finish = self.setup.increment_finish

            #
            # The alternative is to set the increment stop time to the
            # end time of the mission.
            #
            if not increment_start:
                increment_start = self.setup.mission_start
                logging.warning(
                    "-- No increment start time provided via configuration. "
                    "Mission start time will be used:"
                )
                logging.warning(f"   {increment_start}")

            if not increment_finish:
                increment_finish = self.setup.mission_finish
                logging.warning(
                    "-- No increment finish time provided via configuration. "
                    "Mission stop time will be used:"
                )
                logging.warning(f"   {increment_finish}")

        #
        # We check the coverage with the previous increment.
        #
        try:
            #
            # The first alternative option is to set the time to the time of
            # the previous increment since we might be generating an increment
            # that does not extend the coverage.
            #
            bundles = glob.glob(
                self.setup.bundle_directory
                + os.sep
                + self.setup.mission_acronym
                + "_spice"
                + os.sep
                + f"bundle_{self.setup.mission_acronym}"
                f"_spice_v*"
            )
            bundles.sort()

            with open(bundles[-1], "r") as b:
                for line in b:
                    if "<start_date_time>" in line:
                        prev_increment_start = line.split(">")[-2].split("<")[0]
                    if "<stop_date_time>" in line:
                        prev_increment_finish = line.split(">")[-2].split("<")[0]

            #
            # Provide different logging level depending on the times
            # combination.
            #
            logging.info("-- Previous bundle increment interval is:")
            logging.info(f"   {prev_increment_start} - {prev_increment_finish}")

            #
            # Correct the increment interval with previous interval if
            # required.
            #
            if prev_increment_start < increment_start:
                increment_start = prev_increment_start
                logging.info("-- Increment start corrected from previous bundle.")
            elif prev_increment_start > increment_start:
                logging.warning("-- Increment start from previous bundle not used.")

            if prev_increment_finish > increment_finish:
                increment_finish = prev_increment_finish
                logging.warning("-- Increment finish corrected form previous bundle.")

        except BaseException:
            logging.warning("-- Previous bundle not found.")

        #
        # Check the format of the previous bundle and correct it. The 'Z' is
        # removed from the UTC string since it is not supported until the
        # SPICE Toolkit N0067.
        #
        try:
            (increment_start, increment_finish) = et_to_date(
                spiceypy.utc2et(increment_start[:-1]),
                spiceypy.utc2et(increment_finish[:-1]),
                self.setup.date_format,
            )
        except BaseException:
            logging.warning(
                "-- A leapseconds kernel (LSK) has not been loaded. "
                "Increment start/finish times will not be corrected."
            )

        logging.info("-- Increment interval for collection and bundle set to:")
        logging.info(f"   {increment_start} - {increment_finish}")
        logging.info("")

        self.setup.increment_finish = increment_finish
        self.setup.increment_start = increment_start

    def validate(self):
        """Validate the SPICE Kernels collection.

        The SPICE Kernels collection validation performs the following checks:

           * check that all the kernels from the kernel list are present
           * check that all the kernels have been labeled
           * display the key elements of the labels for the user to do a visual
             inspection. The key elements are: ``logical_identifier``, ``version_id``,
             ``title``, ``description``, ``start_date_time``, ``stop_date_time``,
             ``file_name``, ``file_size``, ``md5_checksum``, ``object_length``,
             ``kernel_type``, and ``encoding_type``.
        """
        line = f"Step {self.setup.step} - Validate SPICE kernel collection generation"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # Check that all the kernels from the list are present
        #
        logging.info("-- Checking that all the kernels from list are present...")

        if self.setup.pds_version == "3":
            ker_dir = "/data/"
            orbnum_dir = "/extras/orbnum/"
            mk_dir = "/extras/mk/"
            lbl_ext = ".lbl"
        else:
            ker_dir = "/spice_kernels/"
            orbnum_dir = "/miscellaneous/orbnum/"
            mk_dir = "/spice_kernels/mk/"
            lbl_ext = ".xml"

        non_present_products = []
        for product in self.list.kernel_list:
            if (
                not os.path.exists(
                    self.setup.staging_directory
                    + ker_dir
                    + extension_to_type(product)
                    + os.sep
                    + product
                )
                and not os.path.exists(
                    self.setup.staging_directory + orbnum_dir + product
                )
                and not os.path.exists(self.setup.staging_directory + mk_dir + product)
            ):
                non_present_products.append(product)

        if non_present_products:
            logging.error("-- The following products from the list are not present:")
            for product in non_present_products:
                logging.error(f"   {product}")
                error_message(
                    "Some products from the list are not present.",
                    setup=self.setup,
                )

        else:
            logging.info("   OK")
        logging.info("")

        #
        # Check that all the kernels have been labeled.
        #
        logging.info("-- Checking that all the kernels have been labeled...")

        non_labeled_products = []
        for product in self.product:
            if not os.path.exists(
                self.setup.staging_directory
                + ker_dir
                + product.type
                + os.sep
                + product.name
            ) or not os.path.exists(
                self.setup.staging_directory
                + ker_dir
                + product.type
                + os.sep
                + product.name.split(".")[0]
                + lbl_ext
            ):
                if self.setup.pds_version == "3" and ".tm" not in product.name:
                    non_labeled_products.append(product.name)

        if non_labeled_products:
            logging.error("-- The following products have not been labeled:")
            for product in non_labeled_products:
                logging.error(f"   {product}")
                # TODO: This IF statement goes after implementing PDS3 labeling.
                if self.setup.pds_version == "4":
                    error_message(
                        "Some products have not been labeled.", setup=self.setup
                    )

        else:
            logging.info("   OK")

        #
        # Exit the method if no products are present in collection
        #
        if not self.product:
            return None

        #
        # Display the key elements of the labels for the user to do a visual
        # check. The key elements are: logical_identifier, version_id, title,
        # description, start_date_time, stop_date_time, file_name, file_size,
        # md5_checksum, object_length, kernel_type, and encoding_type.
        #
        if self.setup.pds_version == "4":
            elements = [
                "logical_identifier",
                "version_id",
                "title",
                "description",
                "start_date_time",
                "stop_date_time",
                "file_name",
                "file_size",
                "md5_checksum",
                "object_length",
                "kernel_type",
                "encoding_type",
            ]
        else:
            elements = [
                "RECORD_TYPE",
                "RECORD_BYTES",
                "SPICE_KERNEL",
                "DESCRIPTION",
            ]

        elements_dict = dict.fromkeys(elements)

        products = self.product
        for product in products:
            label_name = product.label.name
            with open(label_name, "r") as p:
                for line in p:
                    for element in elements:
                        if element in line:
                            if not elements_dict[element]:
                                elements_dict[element] = [line.strip()]
                            else:
                                elements_dict[element].append(line.strip())

        logging.info("")
        logging.info("-- Providing relevant fields of labels for visual inspection.")
        logging.info("")
        for key in elements_dict.keys():
            for element in elements_dict[key]:
                logging.info(f"   {element}")
            logging.info("")
        logging.info("")

        return None


class DocumentCollection(Collection):
    """Collection child class to generate a PDS3 or PDS4 Document Collection.

    :param setup: NPB execution setup object
    :type setup: object
    :param bundle: Bundle object
    :type bundle: object
    """

    def __init__(self, setup: object, bundle: object) -> object:
        """Constructor."""
        if setup.pds_version == "3":
            self.type = "DOCUMENT"
        elif setup.pds_version == "4":
            self.type = "document"

        Collection.__init__(self, self.type, setup, bundle)

    def get_pds3_documents(self):
        """Collects the updated PDS3 documents for the increment."""
        line = f"Step {self.setup.step} - Generation of PDS3 products"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        for file in glob.glob(
            f"{self.setup.staging_directory}/**/*[.]*", recursive=True
        ):
            if ".txt" in file or ".cat" in file or "aareadme." in file:
                document = PDS3DocumentProduct(self.setup, file)

                if document.new_product:
                    self.add(document)


class MiscellaneousCollection(Collection):
    """Collection child class to generate a PDS4 Document Collection.

    :param setup: NPB execution setup object
    :type setup: object
    :param bundle: Bundle object
    :type bundle: object
    :param list: Kernel List object
    :type list: object
    """

    def __init__(self, setup: object, bundle: object, list: object) -> object:
        """Constructor."""
        if setup.pds_version == "4":
            self.type = "miscellaneous"
        else:
            self.type = "extras"

        #
        # Included for ORBNUM files observers and targets.
        #
        self.list = list

        Collection.__init__(self, self.type, setup, bundle)

    def report(self):
        """Report the Collection generation step."""
        line = f"Step {self.setup.step} - Generation of {self.type} collection"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")
