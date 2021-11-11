"""Bundle Class Implementation."""
import filecmp
import logging
import os
import pprint
import shutil
import time

from ..utils import check_list_duplicates
from ..utils import get_context_products
from ..utils import safe_make_directory
from .log import error_message
from .product import ReadmeProduct


class Bundle(object):
    """Class to generate the PDS4 Bundle structure.

    The class construction will generate the top level directory structure as
    follows::

         maven_spice/
         |-- spice_kernels
         |-- document
         '-- miscellaneous
    """

    def __init__(self, setup):
        """Constructor."""
        line = (
            f"Step {setup.step} - Bundle/data set structure generation "
            f"at staging area"
        )
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        logging.info("-- Directory structure generation occurs if reported.")
        logging.info("")

        self.collections = []

        #
        # Generate the bundle or data set structure
        #
        if setup.pds_version == "3":

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + "catalog")
            safe_make_directory(setup.staging_directory + os.sep + "data")
            safe_make_directory(setup.staging_directory + os.sep + "document")
            safe_make_directory(setup.staging_directory + os.sep + "extras")
            safe_make_directory(setup.staging_directory + os.sep + "index")

        elif setup.pds_version == "4":

            self.name = f"bundle_{setup.mission_acronym}_spice_v{setup.release}.xml"

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + "spice_kernels")
            safe_make_directory(setup.staging_directory + os.sep + "document")
            safe_make_directory(setup.staging_directory + os.sep + "miscellaneous")

        self.setup = setup

        if setup.pds_version == "4":

            #
            # Assign the Bundle LID and VID and the Internal Reference LID
            #
            self.set_bundle_vid()
            self.set_bundle_lid()

            self.lid_reference = "{}:context:investigation:mission.{}".format(
                ":".join(setup.logical_identifier.split(":")[0:-1]),
                self.setup.mission_acronym,
            )

            #
            #  Get the context products.
            #
            self.context_products = get_context_products(self.setup)

            #
            # Generate the bundle history
            #
            self.history = self.get_history(self)

    def add(self, element):
        """Add a Collection to the Bundle."""
        self.collections.append(element)

    def write_readme(self):
        """Write the readme product if it does not exist."""
        self.readme = ReadmeProduct(self.setup, self)

    def set_bundle_lid(self):
        """Set the Bundle LID."""
        self.lid = self.setup.logical_identifier

    def set_bundle_vid(self):
        """Set the Bundle VID."""
        self.vid = f"{int(self.setup.release)}.0"

    def files_in_staging(self):
        """Lists all the files in the staging area."""
        line = f"Step {self.setup.step} - Recap files in staging area"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # A list of the new files in the staging area is generated first.
        #
        new_files = []
        for root, _dirs, files in os.walk(self.setup.staging_directory, topdown=True):
            for name in files:
                new_files.append(os.path.join(root, name))

        self.new_files = new_files

        logging.info("-- The following files are present in the staging area:")
        for file in new_files:
            relative_path = f"{os.sep}{self.setup.mission_acronym}_spice{os.sep}"
            logging.info(f"     {file.split(relative_path)[-1]}")
        logging.info("")

    def copy_to_bundle(self):
        """Copy files from ``staging_directory`` to the ``bundle_directory``."""
        line = f"Step {self.setup.step} - Copy files to the bundle area"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        #
        # Index files are added to the new_files list.
        #
        if self.setup.pds_version == "3":
            self.new_files.append(self.setup.staging_directory + "/../dsindex.tab")
            self.new_files.append(self.setup.staging_directory + "/../dsindex.lbl")

        copied_files = []
        for file in self.new_files:
            src = file

            relative_path = f"{os.sep}{self.setup.mission_acronym}_spice{os.sep}"
            relative_path += file.split(relative_path)[-1]

            #
            # If running in label mode, the bundle directory structure is not
            # replicated.
            #
            if self.setup.faucet == "labels":
                relative_path = relative_path.split("spice_kernels")[-1]

            dst = self.setup.bundle_directory + relative_path

            if not os.path.exists(os.sep.join(dst.split(os.sep)[:-1])):
                os.mkdir(os.sep.join(dst.split(os.sep)[:-1]))
                os.chmod(os.sep.join(dst.split(os.sep)[:-1]), 0o775)

            #
            # If the file is a label we copy it anyway.
            #
            if not os.path.exists(dst) or dst.split(".")[-1] == "xml":
                copied_files.append(file)
                #
                # We do not use copy2 (copy data and metadata) because
                # we want to 'touch' the files for them to have the
                # timestamp of the day the archive increment was generated.
                #
                shutil.copy(src, dst)
                os.chmod(dst, 0o664)

                logging.info(f"-- Copied: {dst.split(os.sep)[-1]}")
            else:

                #
                # Comparison for Binary files is disabled (following the
                # experience of comapring OREX OLA CKs.)
                #
                if src.split(".")[-1][0] != "b":

                    if not filecmp.cmp(src, dst):
                        logging.warning(
                            f"-- File already exists but content is "
                            f"different: "
                            f"{dst.split(os.sep)[-1]}"
                        )

                logging.warning(
                    f"-- File already exists and has not been "
                    f"copied: {dst.split(os.sep)[-1]}"
                )

        #
        # Cross-check that files with latest timestamp in final correspond
        # to the files copied from staging:
        #
        xdays = 1
        now = time.time()
        newer_file = []

        #
        # List all files newer than 'x' days
        #
        for root, _dirs, files in os.walk(self.setup.bundle_directory):
            for name in files:
                filename = os.path.join(root, name)
                if os.stat(filename).st_mtime > now - (xdays * 86400):
                    newer_file.append(filename)

        logging.info("")
        line = (
            f"-- Found {len(newer_file)} new file(s), copied "
            f"{len(copied_files)} file(s) from staging directory."
        )
        if len(newer_file) == len(copied_files):
            logging.info(line)
        else:
            logging.warning(line)
        logging.info("")

    def get_history(self, object):
        """This method builds the "Archive History".

        The "Archive history" is obtained by extracting the
        previous releases and the Collections that correspond to each release
        from the Bundle labels. The other products' information is extracted
        from the collection inventories.

        The archive history is then provided as a dictionary with releases
        as keys and each key contains a list of files for that release.

        The method checks whether if there is any duplicated element.

        :return: archive history
        :rtype: dict
        """
        #
        # Determine the number of previous releases.
        #
        # The number of previous releases is obtained from the number/version
        # of Bundle labels. That information is already known as it is
        # specified by the bundle vid
        #
        number_of_releases = int(object.vid.split(".")[0])

        #
        # If the pipeline has not yet been executed, the current
        # version is substracted.
        #
        if not object.collections:
            number_of_releases -= 1

        ker_col_ver = 0
        doc_col_ver = 0
        mis_col_ver = 0

        #
        # The version extracted from the labels is initialised because the
        # miscellaneous collection might not be present
        #
        rel_ker_col_ver = 0
        rel_doc_col_ver = 0
        rel_mis_col_ver = 0

        #
        # Boolean to record all the misc collections if they were not
        # generated from the first version of the bundle
        #
        first_misc = True

        #
        # Initialise the history dictionary.
        #
        history = {}

        for rel in range(1, number_of_releases + 1):
            history[rel] = []

            if rel == 1:
                history[rel].append("readme.txt")

            bundle_label = f"{object.name[:-7]}{rel:03d}.xml"

            #
            # Check if the bundle label for the release exists, if not, signal
            # an error but do not throw an exception.
            #
            if not os.path.isfile(
                object.setup.bundle_directory
                + f"/{object.setup.mission_acronym}_spice/"
                + bundle_label
            ):
                line = (
                    "Files from previous releases not available "
                    "to generate Bundle history"
                )
                logging.warning(f"-- {line}.")
                if not object.setup.args.silent and not object.setup.args.verbose:
                    print("-- " + "WARNING: " + line + ".")
                return {}

            history[rel].append(bundle_label)

            #
            # Reading XML label file into a dictionary.
            #
            # The bundle label provides the version of the collections present
            # in the bundle.
            #
            with open(
                object.setup.bundle_directory
                + f"/{object.setup.mission_acronym}_spice/"
                + bundle_label,
                "r",
            ) as lbl:
                for line in lbl:
                    if "spice:spice_kernels::" in line:
                        rel_ker_col_ver = int(
                            line.split("spice:spice_kernels::")[-1].split(
                                ".0</lidvid_reference>"
                            )[0]
                        )
                    elif "spice:document::" in line:
                        rel_doc_col_ver = int(
                            line.split("spice:document::")[-1].split(
                                ".0</lidvid_reference>"
                            )[0]
                        )
                    elif "spice:miscellaneous::" in line:
                        rel_mis_col_ver = int(
                            line.split("spice:miscellaneous::")[-1].split(
                                ".0</lidvid_reference>"
                            )[0]
                        )

            #
            # The SPICE Kernels collection inventory should have the same number
            # of files; the kernels that correspond to each release will be
            # determined from the inventories.
            #
            # If the kernel collection version is not equal to the one in
            # the release, then we add the kernels of the collection.
            #
            if rel_ker_col_ver != ker_col_ver:
                ver = rel_ker_col_ver
                ker_collection = (
                    f"spice_kernels/"
                    f"collection_spice_kernels_inventory_v{ver:03d}.csv"
                )
                history[rel].append(ker_collection)

                ker_collection_lbl = (
                    f"spice_kernels/collection_spice_kernels_v{ver:03d}.xml"
                )
                history[rel].append(ker_collection_lbl)

                with open(
                    object.setup.bundle_directory
                    + f"/{object.setup.mission_acronym}_spice/"
                    + ker_collection,
                    "r",
                ) as c:
                    for line in c:

                        if ("P" in line) and (":mk_" not in line):
                            product = (
                                f"spice_kernels/"
                                f'{line.split(":")[5].replace("_","/",1)}'
                            )
                            history[rel].append(product)

                            ext = product.split(".")[-1]
                            lbl = product.replace("." + ext, ".xml")

                            history[rel].append(lbl)

                        elif ("P" in line) and (":mk_" in line):
                            mk_ver = line.split("::")[-1]
                            mk_ver = int(mk_ver.split(".")[0])

                            #
                            # The meta-kernel version scheme can consist of 2 or
                            # 3 digits. It needs to be determined from
                            # configuration. All meta-kernels must have the same
                            # number of digits in the version field.
                            #
                            if hasattr(self.setup, "mk"):
                                for pattern in self.setup.mk[0]["name"]:
                                    if pattern["pattern"]["#text"] == "VERSION":
                                        version_length = int(
                                            pattern["pattern"]["@length"]
                                        )
                                        if version_length == 1:
                                            product = (
                                                f"spice_kernels/"
                                                f'{line.split(":")[5].replace("_", "/", 1)}_'
                                                f"v{mk_ver:01d}.tm"
                                            )
                                        elif version_length == 2:
                                            product = (
                                                f"spice_kernels/"
                                                f'{line.split(":")[5].replace("_", "/", 1)}_'
                                                f"v{mk_ver:02d}.tm"
                                            )
                                        elif version_length == 3:
                                            product = (
                                                f"spice_kernels/"
                                                f'{line.split(":")[5].replace("_", "/", 1)}_'
                                                f"v{mk_ver:03d}.tm"
                                            )
                                        else:
                                            error_message(f"Meta-kernel version "
                                                          f"length of {version_length}"
                                                          f"digits is incorrect.")

                                        history[rel].append(product)
                                        history[rel].append(
                                            product.replace(".tm", ".xml")
                                        )

                                        break

                            elif hasattr(self.setup, "mk_inputs"):
                                #
                                # Try to derive the digits from the MK input.
                                #
                                if isinstance(self.setup.mk_inputs, dict):
                                    mk_names = self.setup.mk_inputs['file']
                                if not isinstance(mk_names, list):
                                    mk_names = [mk_names]

                                for mk in mk_names:
                                    product = mk

                                    product = product.split(os.sep)[-1]
                                    product = f"spice_kernels/mk/{product}"

                                    if product not in history[rel]:
                                        history[rel].append(product)
                                        history[rel].append(product.replace(".tm", ".xml"))
                            else:
                                #
                                # Default to 2. Might trigger an error.
                                #
                                logging.warning(
                                    "MK version for history "
                                    "defaulted to version with "
                                    "2 digits. Might raise an "
                                    "exception."
                                )

                                #
                                # Only three version formats are implemented.
                                #
                                product = (
                                    f"spice_kernels/"
                                    f'{line.split(":")[5].replace("_", "/", 1)}_'
                                    f"v{mk_ver:02d}.tm"
                                )
                                history[rel].append(product)
                                history[rel].append(product.replace(".tm", ".xml"))

            #
            # The Miscellaneous collection, if present, should have the same
            # number of files.
            #
            if rel_mis_col_ver != mis_col_ver:
                ver = rel_mis_col_ver

                #
                # If this is the first miscellaneous collection, add all
                # the previous ones (which will have been generated in this
                # release).
                #
                if first_misc:
                    if ver != 1:
                        misc_releases = range(1, number_of_releases + 1)
                    else:
                        misc_releases = [ver]

                for mver in misc_releases:

                    mis_collection = (
                        f"miscellaneous/"
                        f"collection_miscellaneous_inventory_v{mver:03d}.csv"
                    )

                    if os.path.exists(
                        object.setup.bundle_directory
                        + f"/{object.setup.mission_acronym}_spice/"
                        + mis_collection
                    ):
                        history[rel].append(mis_collection)

                        mis_collection_lbl = (
                            f"miscellaneous/"
                            f"collection_miscellaneous_v{mver:03d}.xml"
                        )
                        history[rel].append(mis_collection_lbl)

                        with open(
                            object.setup.bundle_directory
                            + f"/{object.setup.mission_acronym}_spice/"
                            + mis_collection,
                            "r",
                        ) as c:
                            for line in c:
                                if ("P" in line) and (":checksum_" not in line):
                                    product = (
                                        f"miscellaneous/"
                                        f'{line.split(":")[5].replace("_", "/", 1)}'
                                    )
                                    history[rel].append(product)
                                    orbnum_extension = f'.{product.split(".")[-1]}'
                                    history[rel].append(
                                        product.replace(orbnum_extension, ".xml")
                                    )

                                elif ("P" in line) and (":checksum_" in line):
                                    product_name = line.split(":")[5].replace(
                                        "_", "/", 1
                                    )
                                    product = (
                                        f"miscellaneous/"
                                        f"{product_name}_v{mver:03d}.tab"
                                    )
                                    history[rel].append(product)
                                    history[rel].append(product.replace(".tab", ".xml"))

                first_misc = False

            #
            # The document collection to be included in the release needs to be
            # sorted out by from the bundle label, that indicates the
            # version of the document selection.
            #
            if rel_doc_col_ver != doc_col_ver:
                ver = rel_doc_col_ver
                doc_collection = (
                    f"document/collection_document_inventory_v{ver:03d}.csv"
                )
                history[rel].append(doc_collection)

                doc_collection_lbl = f"document/collection_document_v{ver:03d}.xml"
                history[rel].append(doc_collection_lbl)

                with open(
                    object.setup.bundle_directory
                    + f"/{object.setup.mission_acronym}_spice/"
                    + doc_collection,
                    "r",
                ) as c:
                    for line in c:
                        if "P" in line:
                            product = (
                                f"document/"
                                f'{line.split(":")[5].replace("_", "/", 1)}_'
                                f"v{ver:03d}.html"
                            )
                            history[rel].append(product)
                            history[rel].append(product.replace(".html", ".xml"))

            ker_col_ver = rel_ker_col_ver
            doc_col_ver = rel_doc_col_ver
            mis_col_ver = rel_mis_col_ver

        #
        # Perform a simple check of duplicate elements.
        #
        all_products = []
        for release in history.values():
            all_products += release
        duplicates = check_list_duplicates(all_products)

        if duplicates:
            logging.warning("-- Bundle History contains duplicates.")

        return history

    def validate_history(self):
        """Validate the bundle updated history with the checksum files.

        This method validates all the archive Checksum files with the "Archive
        History". The "Archive history" is obtained by extracting the
        previous releases and the Collections that correspond to each release
        from the Bundle labels. The other products' information is extracted
        from the collection inventories.

        The archive history is then provided as a dictionary with releases
        as keys and each key contains a list of files for that release.

        The validation is performed by comparing each release entry of the4
        dictionary with the release checksum file ``checksum_v???.tab``.

        In parallel the method writes in the log the complete bundle release
        4history.
        """
        logging.info("")
        line = f"Step {self.setup.step} - Validate bundle history with checksum files"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        logging.info("")
        logging.info("-- Display the list of files that belong to each release.")
        logging.info("")

        history = self.get_history(self)
        if history:
            history_string = pprint.pformat(history, indent=2)
            for line in history_string.split("\n"):
                logging.info(f"    {line}")

        products_in_history = []
        for rel in history:

            products_in_history += history[rel]
            products_in_history = sorted(products_in_history)
            products_in_checksum = []
            checksum_file = (
                f"{self.setup.bundle_directory}"
                f"/{self.setup.mission_acronym}_spice"
                f"/miscellaneous"
                f"/checksum/checksum_v{rel:03d}.tab"
            )
            with open(checksum_file) as c:
                for line in c:
                    products_in_checksum.append(line.split()[-1].strip())

            #
            # The last checksum and its label has to be added to the products in
            # the checksum list
            #
            if rel == list(history)[-1]:
                products_in_checksum.append(
                    f"miscellaneous/checksum/checksum_v{rel:03d}.tab"
                )
                products_in_checksum.append(
                    f"miscellaneous/checksum/checksum_v{rel:03d}.xml"
                )

            products_in_checksum = sorted(products_in_checksum)

            if not (products_in_checksum == products_in_history):

                logging.error("")
                logging.error(
                    f"-- Products in {checksum_file} do not "
                    f"correspond to the bundle release history"
                )
                incorrect_products = set(products_in_checksum) ^ set(
                    products_in_history
                )

                incorrect_output = ""
                for product in incorrect_products:
                    incorrect_output += f"{product}\n"
                    logging.error(f"      {product}")
                if not self.setup.args.log:
                    error_message(
                        f"Products in {checksum_file} do not correspond "
                        f"to the bundle release history: \n {incorrect_output}",
                        setup=self.setup,
                    )
                else:
                    error_message("Check generation of Checksum files", self.setup)

        logging.info("")

        return
