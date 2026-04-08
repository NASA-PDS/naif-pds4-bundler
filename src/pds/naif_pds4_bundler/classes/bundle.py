"""Bundle Class Implementation."""
from __future__ import annotations
import filecmp
import logging
import os
from pathlib import Path
import pprint
import shutil
import time
from typing import Optional, TYPE_CHECKING
from xml.etree import ElementTree

import spiceypy

from ..pipeline.runtime import handle_npb_error
from ..utils import (
    check_list_duplicates,
    etree_to_dict,
    get_context_products,
    safe_make_directory,
    spice_exception_handler,
)

# The following imports are only required for type checking.
if TYPE_CHECKING:
    from .product import ReadmeProduct


class Bundle:
    """Class to generate the PDS4 Bundle structure.

    The class construction will generate the top level directory structure for
    a PDS4 bundle or a PDS3 data set.

    :param setup: NPB execution Setup
    """

    def __init__(self, setup) -> None:
        """Constructor."""
        self._bundle_root = Path(setup.bundle_directory,
                                 f"{setup.mission_acronym}_spice")
        self._new_files = []
        self._readme = None

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

            # Assign the Bundle LID and VID and the Internal Reference LID
            self._lid = self.setup.logical_identifier
            self._vid = f"{int(self.setup.release)}.0"

            #
            #  Get the context products.
            #
            self.context_products = get_context_products(self.setup)

            # Generate the bundle history
            self.history = self._get_history()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def lid(self) -> str:
        """Bundle Logical Identifier (LID).

        The Bundle LID is a unique character string that identifies a bundle
        across the entire PDS archive. It stays constant regardless of how
        many times the bundle is updated.
        """
        return self._lid

    @property
    def readme(self) -> Optional[ReadmeProduct]:
        """Bundle Readme Product.

        The readme product (typically a readme.txt file) is an optional,
        human-readable file that provides a general overview of a bundle's
        contents and organization.
        """
        return self._readme

    @property
    def vid(self) -> str:
        """Bundle Version Identifier (VID).

        The Bundle VID identifies the specific version of the bundle.
        """
        return self._vid

    def add(self, element):
        """Add a Collection to the Bundle."""
        self.collections.append(element)

    def add_readme(self, readme: ReadmeProduct):
        """Adds the readme product if it does not exist."""
        self._readme = readme

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
        staging_files = []
        for root, _dirs, files in os.walk(self.setup.staging_directory, topdown=True):
            for name in files:
                if "DS_Store" not in name:
                    staging_files.append(os.path.join(root, name))

        #
        # A list of the new files as extracted form the products in the
        # collections is generated next.
        #
        for collection in self.collections:
            for product in collection.product:
                self._new_files.append(product.path)
                if hasattr(product, "label"):
                    self._new_files.append(product.label.name)
                else:
                    logging.info(
                        f"-- Product {product.name} has no label in staging area."
                    )

        #
        # Include the bundle products if not running in label mode.
        #
        if self.setup.pds_version == "4" and self.setup.faucet != "labels":
            self._new_files.append(self.setup.staging_directory + os.sep + self.name)
            if self._readme and self._readme.new_product:
                self._new_files.append(
                    os.path.join(self.setup.staging_directory, self._readme.name))

        #
        # dsindex files are added to the `_new_files` list. These are the only
        # files that are explicitly added.
        #
        if self.setup.pds_version == "3":
            self._new_files.append(self.setup.staging_directory + "/../dsindex.tab")
            self._new_files.append(self.setup.staging_directory + "/../dsindex.lbl")

        logging.info("-- The following files are present in the staging area:")
        for file in staging_files:
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

        copied_files = []
        for file in self._new_files:
            src = file

            if self.setup.pds_version == "4":
                spice_kernels_dir = "spice_kernels"
                label_extension = "xml"
                relative_path = f"{os.sep}{self.setup.mission_acronym}_spice{os.sep}"
            else:
                spice_kernels_dir = "data"
                label_extension = "lbl"
                relative_path = f"{os.sep}{self.setup.volume_id}{os.sep}"

            relative_path += file.split(relative_path)[-1]

            #
            # If running in label mode, the bundle directory structure is not
            # replicated.
            #
            if self.setup.faucet == "labels":
                relative_path = relative_path.split(spice_kernels_dir)[-1]

            dst = self.setup.bundle_directory + relative_path

            dst_dir = os.sep.join(dst.split(os.sep)[:-1])
            if not os.path.exists(dst_dir):
                Path(dst_dir).mkdir(parents=True, exist_ok=True)
                os.chmod(dst_dir, 0o775)

            #
            # If the file is a label we copy it anyway.
            #
            if (
                (self.setup.pds_version == "3")
                or (not os.path.exists(dst))
                or (dst.split(".")[-1] == label_extension)
            ):
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
                # experience of comparing OREX OLA CKs.)
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
        # Cross-check that files with the latest timestamp in final correspond
        # to the files copied from staging:
        #
        xdays = 1
        now = time.time()
        newer_file = []

        #
        # List all files newer than 'x' days.
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

    def validate(self):
        """Validate the Bundle.

        The two implemented steps are to check checksum files against the
        updated bundle history and checking the bundle times.
        """
        self._check_times()
        self._validate_history()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @spice_exception_handler
    def _check_times(self):
        """Check the correctness of the bundle times."""
        str_msn_strt = self.setup.mission_start
        str_inc_strt = self.setup.increment_start
        str_inc_stop = self.setup.increment_finish
        str_msn_stop = self.setup.mission_finish

        #
        # Remove 'Z' due to a bug in CSPICE N0066. See Header of TPARTV.
        #
        if "Z" in str_msn_strt:
            str_msn_strt = str_msn_strt[:-1]
        if "Z" in str_inc_strt:
            str_inc_strt = str_inc_strt[:-1]
        if "Z" in str_inc_stop:
            str_inc_stop = str_inc_stop[:-1]
        if "Z" in str_msn_stop:
            str_msn_stop = str_msn_stop[:-1]

        et_msn_strt = spiceypy.str2et(str_msn_strt)
        et_inc_strt = spiceypy.str2et(str_inc_strt)
        et_inc_stop = spiceypy.str2et(str_inc_stop)
        et_msn_stop = spiceypy.str2et(str_msn_stop)

        if (
            (et_msn_strt > et_inc_strt)
            or (et_inc_strt > et_inc_stop)
            or (et_inc_stop > et_msn_stop)
            or (et_msn_strt >= et_msn_stop)
        ):
            handle_npb_error(
                "The resulting Mission and Increment start and finish dates "
                "are incoherent."
            )

    @staticmethod
    def _get_collection_versions_from_label(label: dict) -> dict[str, list[int]]:
        """Extract per-collection version numbers from a parsed bundle label.

        :param label: dict returned by :meth:`_read_bundle_label`

        :returns:  a dict with three keys — ``"kernels"``, ``"document"``,
                   ``"miscellaneous"`` — each mapping to a (possibly empty)
                   list of integer version numbers found among the Primary
                   ``Bundle_Member_Entry`` items in ``label``:

                   ``{"kernels": [...], "document": [...], "miscellaneous": [...]}``
        """
        prefix = label["prefix"]
        versions = {
            "kernels": [],
            "document": [],
            "miscellaneous": [],
        }

        for member in label["members"]:
            if member[f"{prefix}member_status"] != "Primary":
                continue
            lidvid = member[f"{prefix}lidvid_reference"]

            if "spice:spice_kernels::" in lidvid:
                ver = int(lidvid.split("spice:spice_kernels::")[-1].split(".0")[0])
                versions["kernels"].append(ver)
            elif "spice:document::" in lidvid:
                ver = int(lidvid.split("spice:document::")[-1].split(".0")[0])
                versions["document"].append(ver)
            elif "spice:miscellaneous::" in lidvid:
                ver = int(lidvid.split("spice:miscellaneous::")[-1].split(".0")[0])
                versions["miscellaneous"].append(ver)

        return versions

    def _get_document_collection_products(self, ver: int) -> list[str]:
        """Return all product paths belonging to a document collection.

        Reads the collection inventory CSV present within the ``document``
        subdirectory of the bundle's root path and returns the relative paths
        for every primary document product (versioned .html) and its XML label,
        plus the collection inventory CSV and label files.

        :param ver: collection version number
        :returns: list of relative product path strings
        """
        products = [
            f"document/collection_document_inventory_v{ver:03d}.csv",
            f"document/collection_document_v{ver:03d}.xml",
        ]

        # The relative path of the collection's inventory CVS file is the first
        # product in the products' list. Read it, and extract all primary
        # document products.
        with (self._bundle_root / products[0]).open("rt") as handle:
            for line in handle:
                if "P" in line:
                    product = (
                        f'document/{line.split(":")[5].replace("_", "/", 1)}_'
                        f'v{ver:03d}.html'
                    )
                    products.append(product)
                    products.append(product.replace(".html", ".xml"))

        return products

    def _get_history(self) -> dict:
        """This method builds the "Archive History".

        The "Archive history" is obtained by extracting the
        previous releases and the Collections that correspond to each release
        from the Bundle labels. The other products' information is extracted
        from the collection inventories.

        The archive history is then provided as a dictionary with releases
        as keys and each key contains a list of files for that release.

        The method checks whether if there is any duplicated element.
        """
        # Determine the number of previous releases.
        #
        # The number of previous releases is obtained from the number/version
        # of Bundle labels. That information is already known as it is
        # specified by the bundle vid.
        number_of_releases = int(self._vid.split(".")[0])

        # When the pipeline has not yet run, the in-progress release does not
        # yet have a label on disk, so we only reconstruct completed releases.
        if not self.collections:
            number_of_releases -= 1

        # Track the most recently seen version of each collection so we can
        # detect when a new version is introduced in a later release.
        ker_col_ver = 0
        doc_col_ver = 0
        mis_col_ver = 0

        history = {}
        for rel in range(1, number_of_releases + 1):
            history[rel] = []

            # Add the readme file, if we are in the first release.
            if rel == 1:
                history[rel].append('readme.txt')

            if not (label := self._read_bundle_label(rel)):
                return {}

            history[rel].append(label['filename'])

            # Extract the version for the spice_kernels, miscellaneous, and
            # document collection of the release.
            versions = self._get_collection_versions_from_label(label)

            # --- Kernel collection -------------------------------------------
            # The SPICE Kernels collection inventory should have the same number
            # of files; the kernels that correspond to each release will be
            # determined from the inventories.
            #
            # If the kernel collection version is not equal to the one in
            # the release, then we add the kernels of the collection.
            for ver in versions['kernels']:
                if ver != ker_col_ver:
                    history[rel].extend(
                        self._get_kernel_collection_products(ver)
                    )
                    ker_col_ver = ver

            # --- Miscellaneous collection -------------------------------------
            # The Miscellaneous collection, if present, should have the same
            # number of files.
            for ver in versions['miscellaneous']:
                if ver != mis_col_ver:
                    history[rel].extend(
                        self._get_misc_collection_products(ver)
                    )
                    mis_col_ver = ver

            # --- Document collection -----------------------------------------
            # The document collection to be included in the release needs to be
            # sorted out from the bundle label, that indicates the version of
            # the document selection.
            for ver in versions['document']:
                if ver != doc_col_ver:
                    history[rel].extend(
                        self._get_document_collection_products(ver)
                    )
                    doc_col_ver = ver

        # Perform a simple check of duplicate elements.
        all_products = [f for release in history.values() for f in release]
        if check_list_duplicates(all_products):
            logging.warning("-- Bundle History contains duplicates.")

        return history

    def _get_kernel_collection_products(self, ver: int) -> list[str]:
        """Return all product paths belonging to a SPICE kernel collection.

        Reads the collection inventory CSV present within the ``spice_kernels``
        subdirectory of the bundle's root path and returns the relative paths
        for every primary kernel and its XML label, plus the collection
        inventory CSV and label files themselves.

        :param ver: collection version number (used to name the CSV/label)
        :returns: list of relative product path strings
        """

        products = [
            f"spice_kernels/collection_spice_kernels_inventory_v{ver:03d}.csv",
            f"spice_kernels/collection_spice_kernels_v{ver:03d}.xml"
        ]

        # The relative path of the collection's inventory CVS file is the first
        # product in the products' list. Read it, and extract all primary
        # document products.
        with (self._bundle_root / products[0]).open("rt") as handle:
            for line in handle:
                if 'P' not in line:
                    continue

                if ":mk_" not in line:
                    # Regular kernel: derive path from LIDVID field [5]
                    product = (
                        f"spice_kernels/{line.split(':')[5].replace('_', '/', 1)}"
                    )
                    ext = product.split(".")[-1]
                    products.append(product)
                    products.append(product.replace(f".{ext}", ".xml"))

                elif ":mk_" in line:
                    # Meta-kernel: version formatting is configuration-dependent
                    mk_ver = int(line.split("::")[-1].split(".")[0])

                    # The meta-kernel version scheme can consist of 2 or 3
                    # digits. It needs to be determined from configuration. All
                    # meta-kernels must have the same number of digits in the
                    # version field.
                    if hasattr(self.setup, "mk"):
                        product = self._get_metakernel_product_from_config(mk_ver, line)
                        products.append(product)
                        products.append(product.replace(".tm", ".xml"))

                    elif hasattr(self.setup, "mk_inputs"):
                        # Try to derive the digits from the MK input.
                        for product in self._get_metakernel_products_from_inputs():
                            if product not in products:
                                products.append(product)
                                products.append(product.replace(".tm", ".xml"))

                    else:
                        # Only three version formats are implemented.
                        product = (
                            f'spice_kernels/{line.split(":")[5].replace("_", "/", 1)}_'
                            f"v{mk_ver:02d}.tm"
                        )
                        products.append(product)
                        products.append(product.replace(".tm", ".xml"))

                        # Default to 2. Might trigger an error.
                        logging.warning(
                            "MK version for history defaulted to version with 2 digits. Might raise an "
                            "exception."
                        )

        return products

    def _get_metakernel_product_from_config(self, ver: int, line: str) -> str:
        """Construct the meta-kernel product path for a given MK version number
        using the information provided in the XML configuration file.

        The version field in MK filenames may be 1, 2, or 3 digits wide. The
        width is resolved in priority order, using the data provided in the
        ``setup.mk`` configuration — reads ``VERSION/@length`` from the
        name-pattern definition.

        :param ver:  integer version number parsed from the inventory LIDVID
        :param line: the raw CSV inventory line (used to extract the base
                     product name)
        :returns: relative product path string, e.g.
                 ``"spice_kernels/mk/insight_v01.tm"``
        """
        base = f"spice_kernels/{line.split(':')[5].replace('_', '/', 1)}_"

        for pattern in self.setup.mk[0]["name"]:
            if not isinstance(pattern, list):
                pattern = [pattern]
            for pattern_word in pattern:
                pattern_key = pattern_word["pattern"]
                if not isinstance(pattern_key, list):
                    pattern_key = [pattern_key]
                for key in pattern_key:
                    if key["#text"] == "VERSION":
                        version_length = int(key["@length"])
                        if version_length in (1,2,3):
                            return f'{base}v{ver:0{version_length}d}.tm'

                        # At this point, we have an issue with the setup configuration.
                        # TODO: Perform these checks elsewhere, probably at setup loading.
                        #       Maybe it is worth using a "derived" attribute similar to
                        #       "version_length".
                        handle_npb_error(
                            f"Meta-kernel version length of {version_length}"
                            "digits is incorrect.")

        # Default to two digits.
        return f"{base}v{ver:02d}.tm"

    def _get_metakernel_products_from_inputs(self) -> list[str]:
        """Return MetaKernel product paths derived from ``setup.mk_inputs``.

        Used as a fallback when ``setup.mk`` is not available and the MK
        version digits must be inferred from the input file list instead.

        :returns: list of relative product paths (e.g.
                  ``["spice_kernels/mk/insight_v01.tm"]``)
        """
        mk_names = self.setup.mk_inputs
        if isinstance(self.setup.mk_inputs, dict):
            mk_names = mk_names["file"]
        if not isinstance(mk_names, list):
            mk_names = [mk_names]

        return [f"spice_kernels/mk/{product.split(os.sep)[-1]}"
                for product in mk_names]

    def _get_misc_collection_products(self, ver: int) -> list[str]:
        """Return all product paths belonging to a miscellaneous collection.

        Reads the collection inventory CSV present within the ``miscellaneous``
        subdirectory of the bundle's root path and returns the relative paths
        for every primary OrbNum or Checksum product and its XML label, plus
        the collection inventory CSV and label files.

        Note: OrbNum products and checksum products are handled separately
        because their filename conventions differ:

        * OrbNum products keep their original extension.
        * Checksum products are versioned with the collection release number.

        :param ver: collection version number
        :returns: list of relative product path strings, or an empty list if
                  the collection inventory CSV file does not exist on disk.
        """
        csv_path = self._bundle_root / 'miscellaneous' / f"collection_miscellaneous_inventory_v{ver:03d}.csv"
        if not csv_path.exists():
            return []

        products = [
            f"miscellaneous/collection_miscellaneous_inventory_v{ver:03d}.csv",
            f"miscellaneous/collection_miscellaneous_v{ver:03d}.xml"
        ]

        with csv_path.open("rt") as handle:
            for line in handle:
                if 'P' not in line:
                    continue

                product_name = line.split(":")[5].replace("_", "/", 1)

                if ":checksum_" not in line:
                    # OrbNums: preserve original extension
                    product = f"miscellaneous/{product_name}"
                    ext = product.split(".")[-1]
                    products.append(product)
                    products.append(product.replace(f".{ext}", ".xml"))

                elif ":checksum_" in line:
                    # Checksum: versioned .tab + label
                    product = f"miscellaneous/{product_name}_v{ver:03d}.tab"
                    products.append(product)
                    products.append(product.replace(".tab", ".xml"))

        return products

    def _read_bundle_label(self, rel: int) -> dict | None:
        """Parse a single bundle label XML file into a dict.

        A ``WARNING`` is logged and, unless running in silent/verbose mode,
        printed to stdout when the file is absent.

        :param rel: integer release number (1-based)
        :returns: parsed label dict, or ``None`` when the label file
                  for release ``rel`` does not exist on disk.
        """
        bundle_label = f"{self.name[:-7]}{rel:03d}.xml"
        bundle_label_path = self._bundle_root / bundle_label

        if not bundle_label_path.is_file():
            msg = "Files from previous releases not available to generate Bundle history."
            logging.warning(f"-- {msg}")
            if not self.setup.args.silent and not self.setup.args.verbose:
                print(f"-- WARNING: {msg}")
            return None

        # Read the XML label file into a dictionary.
        #
        # The bundle label provides the version of the collections present
        # in the bundle and if they have been updated/generated for
        # the current release.
        entries = etree_to_dict(ElementTree.XML(bundle_label_path.read_text()))

        # The resulting dictionary element names are prefixed with
        # the URL of the XML model, e.g.
        #    'http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1',
        prefix = "{" + "/".join(self.setup.xml_model.split("/")[0:-1]) + "}"

        members = entries[f"{prefix}Product_Bundle"][f"{prefix}Bundle_Member_Entry"]

        # TODO: Would this actually simplify the code afterwards.
        # etree_to_dict returns a plain dict when there is only one
        # Bundle_Member_Entry child and a list when there are multiple.
        # Normalize to a list so callers never need to handle both cases.
        # if isinstance(members_raw, dict):
        #     members_raw = [members_raw]

        return {
            "filename": bundle_label,
            "prefix": prefix,
            "members": members
        }

    def _validate_history(self):
        """Validate the bundle updated history with the checksum files.

        This method validates all the archive Checksum files with the "Archive
        History". The "Archive history" is obtained by extracting the
        previous releases and the Collections that correspond to each release
        from the Bundle labels. The other products' information is extracted
        from the collection inventories.

        The archive history is then provided as a dictionary with releases
        as keys and each key contains a list of files for that release.

        The validation is performed by comparing each release entry of the
        dictionary with the release checksum file ``checksum_v???.tab``.

        In parallel the method writes in the execution log the complete bundle
        release history, providing an ordered list of files released for each
        release number.
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

        history = self._get_history()
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
                    #
                    # Need to convert the file names to lower case because this
                    # is the way that the bundle history is generated.
                    #
                    products_in_checksum.append(line.split()[-1].strip().lower())

            #
            # The last checksum and its label have to be added to the products
            # in the checksum list, unless it is the first time that the
            # miscellaneous collection is being generated, and it is not the
            # first release.
            #
            # The checksum is added if it is not the last release and the
            # checksum is present in the archive history.
            #
            checksum_product = f"miscellaneous/checksum/checksum_v{rel:03d}.tab"
            checksum_label = f"miscellaneous/checksum/checksum_v{rel:03d}.xml"

            if checksum_product in history[rel]:
                products_in_checksum.append(checksum_product)
                products_in_checksum.append(checksum_label)

            products_in_checksum.sort()
            products_in_history.sort()

            if products_in_checksum != products_in_history:

                logging.error("")
                logging.error(
                    f"-- Products in {checksum_file} do not "
                    f"correspond to the bundle release history."
                )
                incorrect_products = set(products_in_checksum) ^ set(
                    products_in_history
                )

                incorrect_output = ""
                for product in incorrect_products:
                    incorrect_output += f"{product}\n"
                    logging.error(f"      {product}")
                if not self.setup.args.log:
                    handle_npb_error(
                        f"Products in {checksum_file} do not correspond "
                        f"to the bundle release history: \n {incorrect_output}",
                        setup=self.setup,
                    )
                else:
                    handle_npb_error("Check generation of Checksum files.", self.setup)

        logging.info("")
