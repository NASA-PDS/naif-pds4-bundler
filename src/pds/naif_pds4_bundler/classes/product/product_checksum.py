"""Implementation of the Checksum product class."""
import glob
import logging
import os
from collections import defaultdict

from .product import Product
from ..label import ChecksumPDS3Label
from ..label import ChecksumPDS4Label
from ...pipeline.runtime import handle_npb_error
from ...utils import add_carriage_return
from ...utils import checksum_from_label
from ...utils import checksum_from_registry
from ...utils import compare_files
from ...utils import md5
from ...utils import safe_make_directory


class ChecksumProduct(Product):
    """Class to generate a Checksum Product.

    :param setup:                 NPB execution setup object
    :param collection:            Miscellaneous Collection
    :param add_previous_checksum: True if there is a previous checksum file to
                                  be added, False otherwise
    """

    def __init__(self, setup, collection, add_previous_checksum: bool = True) -> None:
        """Constructor."""
        #
        # The initialisation of the checksum class is lighter than the
        # initialisation of the other products because the purpose is
        # solely to obtain the LID and the VID of the checksum in order
        # to be able to include it in the miscellaneous collection
        # inventory file; the checksum file needs to be included in the
        # inventory file before the actual checksum file is generated.
        #
        self.bytes = 0
        self.setup = setup
        self.collection = collection
        self.collection_path = (
            self.setup.staging_directory + os.sep + "miscellaneous" + os.sep
        )
        self.file_records = 0
        self.label = None
        self.new_product = True
        self.record_bytes = 0
        self.start_time = ''
        self.stop_time = ''

        #
        # We generate the kernel directory if not present
        #
        if setup.pds_version == "4":
            product_path = self.collection_path + "checksum/"
        else:
            product_path = f"{setup.staging_directory}/index/"

        safe_make_directory(product_path)

        #
        # Initialise the checksum dictionary; we use a dictionary to be
        # able to sort it by value into a list to generate the checksum
        # table.
        #
        self.md5_dict = {}

        self.read_current_product(add_previous_checksum=add_previous_checksum)

        if setup.pds_version == "4":
            self.set_product_lid()
            self.set_product_vid()

    def set_coverage(self) -> None:
        """Determine the coverage of the Checksum file."""
        #
        # The coverage is set by generating the checksum file but without
        # writing it.
        #
        self.write_product(history=False, set_coverage=True)

    def generate(self, history: bool = False) -> None:
        """Write and label the Checksum file.

        :param history: True if the checksum will be generated with the archive
                        history, False otherwise
        """
        #
        # This acts as the second part of the Checksum product initialization.
        #
        self.write_product(history=history)

        #
        # Call the constructor of the parent class to fill the common
        # attributes.
        #
        self.new_product = True
        Product.__init__(self)

        #
        # The checksum is labeled.
        #
        logging.info(f"-- Labeling {self.name}...")
        if self.setup.pds_version == "4":
            self.label = ChecksumPDS4Label(self.setup, self)
        else:
            self.label = ChecksumPDS3Label(self.setup, self)

    def read_current_product(self, add_previous_checksum: bool = True) -> None:
        """Reads the current checksum file.

        Reads the current checksum file, determines the version of the
        new checksum file, and adds the checksum file itself and its label.

        :param add_previous_checksum: True if there is a previous checksum file to
                                  be added, False otherwise
        :type add_previous_checksum: bool
        """
        #
        # Determine the checksum version
        #
        if self.setup.pds_version == "4":
            if self.setup.increment:
                checksum_files = glob.glob(
                    self.setup.bundle_directory
                    + f"/{self.setup.mission_acronym}_spice/"
                    + self.collection.name
                    + os.sep
                    + "/checksum/checksum_v*.tab"
                )

                checksum_files += glob.glob(
                    self.setup.staging_directory
                    + os.sep
                    + self.collection.name
                    + "/checksum/checksum_v*.tab"
                )
                checksum_files.sort()
                try:
                    latest_file = checksum_files[-1]

                    #
                    # Store the previous version to use it to validate the
                    # generated one.
                    #
                    self.path_current = latest_file
                    self.name_current = latest_file.split(os.sep)[-1]

                    latest_version = latest_file.split("_v")[-1].split(".")[0]
                    self.version = int(latest_version) + 1

                    logging.info(f"-- Previous checksum file is: {latest_file}")
                    logging.info(f"-- Generate version {self.version}.")
                    logging.info("")

                except BaseException:
                    self.version = 1
                    self.path_current = ""

                    logging.warning("-- Previous checksum file not found.")
                    logging.warning(f"-- Default to version {self.version}.")
                    logging.warning("-- The version of this file might be incorrect.")

            else:
                self.version = 1
                self.path_current = ""

                logging.warning(f"-- Default to version {self.version}.")
                logging.warning(
                    "-- Make sure this is the first release of the archive."
                )
                logging.warning("")

            self.name = f"checksum_v{self.version:03}.tab"
            self.path = (
                self.setup.staging_directory
                + os.sep
                + self.collection.name
                + os.sep
                + "checksum"
                + os.sep
                + self.name
            )
        else:

            self.name_current = "checksum.tab"
            self.path_current = (
                self.setup.bundle_directory
                + os.sep
                + self.setup.volume_id
                + "/index/checksum.tab"
            )

            self.name = "checksum.tab"
            self.path = (
                self.setup.staging_directory + os.sep + "index" + os.sep + self.name
            )

        #
        # Add each element of current checksum into the md5_sum attribute if
        # the miscellaneous collection was present in the release.
        #
        if self.path_current:
            with open(self.path_current, "r", encoding='utf-8') as c:
                for line in c:
                    #
                    # Check the format of the current checksum file.
                    #
                    try:
                        (md5_file, filename) = line.split()
                    except BaseException:
                        handle_npb_error(
                            f"Checksum file {self.path_current} is corrupted.",
                            setup=self.setup,
                        )

                    if len(md5_file) == 32:
                        self.md5_dict[filename] = md5_file
                    else:
                        handle_npb_error(
                            f"Checksum file {self.path_current} "
                            f"corrupted entry: {line}.",
                            setup=self.setup,
                        )

            #
            # Add the previous checksum file itself and its label, as specified
            # by the parameter. Checksum is not added if the corresponding
            # release did not have the miscellaneous collection.
            #
            if add_previous_checksum:

                if self.setup.pds_version == "4":
                    checksum_dir = f"{self.collection.name}/checksum/"
                    label_current = self.path_current.replace(".tab", ".xml")
                else:
                    checksum_dir = "index/"
                    label_current = self.path_current.replace(".tab", ".lbl")

                md5_current = md5(self.path_current)
                self.md5_dict[checksum_dir + self.path_current.split(os.sep)[-1]] = (
                    md5_current
                )

                md5_label = md5(label_current)
                self.md5_dict[checksum_dir + label_current.split(os.sep)[-1]] = (
                    md5_label
                )

        self.new_product = True

    def set_product_lid(self) -> None:
        """Set Product LID."""
        self.lid = (
            f"{self.setup.logical_identifier}:miscellaneous:checksum_checksum".lower()
        )

    def set_product_vid(self) -> None:
        """Set Product VID."""
        self.vid = f'{int(self.version)}.0'

    def write_product(self, history: bool=False, set_coverage: bool=False) -> None:
        """Write the Checksum file and determine its start and stop time.

        This method can also be used to determine the start and stop time of
        the checksum file, necessary to determine these times for the
        miscellaneous collection before the checksum is actually written.

        :param history:      Archive History
        :param set_coverage: Determines the start and stop of the checksum file
                             if set to True, False otherwise
        """
        msn_acr = self.setup.mission_acronym

        #
        # The checksum file of the current run is generated without the
        # bundle history and using the checksum hashes obtained during
        # the pipeline execution.
        #
        if not history:
            #
            # Iterate the collections to obtain the checksum of each product.
            #
            for collection in self.collection.bundle.collections:
                for product in collection.product:
                    if self.setup.pds_version == "4":
                        archive_dir = f"/{msn_acr}_spice/"
                    else:
                        archive_dir = f"/{self.setup.volume_id}/"

                    product_name = product.path.split(archive_dir)[-1]
                    if hasattr(product, "checksum"):

                        #
                        # If a product MD5 sum is duplicated by a product with
                        # a different name raise an error unless you are
                        # running NPB in debug mode.
                        #
                        if (
                            product.checksum in list(self.md5_dict.keys())
                            and self.md5_dict[product_name] != product.checksum
                        ):
                            msg = (
                                f"Two products have the same MD5 sum, "
                                f"the product {product_name} might be a duplicate."
                            )
                            if not self.setup.args.debug:
                                handle_npb_error(msg)
                            else:
                                logging.debug(msg)
                        self.md5_dict[product_name] = product.checksum
                    else:
                        #
                        # For the current checksum product that does not have
                        # a checksum.
                        #
                        pass
                    #
                    # Generate the MD5 checksum of the label.
                    #
                    # TODO: hasattr(product, "label") will need to be removed.
                    if hasattr(product, "label") and product.label is not None:
                        label_checksum = md5(product.label.name)
                        self.md5_dict[product.label.name.split(archive_dir)[-1]] = (
                            label_checksum
                        )

                    else:
                        logging.warning(f"-- {product_name} does not have a label.")
                        logging.info("")

            #
            # Include the readme file checksum if it has been generated in
            # this run. This is a bundle level product.
            #
            if hasattr(self.collection.bundle, "checksum"):
                self.md5_dict["readme.txt"] = self.collection.bundle.checksum

            #
            # Include the bundle label, that is paired to the readme file.
            #
            if self.setup.pds_version == "4" and not set_coverage:
                label_checksum = md5(self.collection.bundle.readme.label.name)
                self.md5_dict[
                    self.collection.bundle.readme.label.name.split(
                        f"/{msn_acr}_spice/"
                    )[-1]
                ] = label_checksum

        #
        # The missing checksum files for PDS4 are generated from the bundle
        # history.
        #
        if history and self.setup.pds_version == "4":
            for product in history[1]:
                path = (
                    self.setup.bundle_directory
                    + f"/{self.setup.mission_acronym}_spice/"
                    + product
                )
                #
                # Computing checksums is resource consuming; let's see if the
                # product has the checksum in its label already. Otherwise,
                # compute the checksum.
                #
                checksum = ""
                if ".xml" not in product:
                    checksum = checksum_from_registry(
                        path, self.setup.working_directory
                    )
                    if not checksum:
                        checksum = checksum_from_label(path)
                if not checksum:
                    checksum = md5(path)

                self.md5_dict[product] = checksum

        #
        # The resulting dictionary needs to be transformed into a list
        # sorted by filename alphabetical order (second column of the
        # resulting table)
        #
        md5_list = []

        #
        # Check if two items of the dictionary have the same value (same
        # MD5 sum.) This happened for the ExoMars2016 bundle release 004
        # where 3 products had the same MD5 sum values.
        #
        md5_check_dict = defaultdict(set)

        for k, v in self.md5_dict.items():
            md5_check_dict[v].add(k)

        md5_check_dict = {k: v for k, v in md5_check_dict.items() if len(v) > 1}

        if md5_check_dict:
            logging.warning("-- The following products have the same MD5 sum:")
            for k, v in md5_check_dict.items():
                logging.warning(f"   {k}")
                for file in v:
                    logging.warning(f"      {file}")

        #
        # The resulting dictionary needs to be transformed into a list
        # sorted by filename alphabetical order (second column of the
        # resulting table)
        #
        if self.setup.pds_version == "4":
            md5_dict_keys = list(self.md5_dict.keys())
            for key in sorted(md5_dict_keys):
                md5_list.append(f"{self.md5_dict[key]}  {key}")
        else:
            #
            # PDS3 checksums have trailing whitespaces to fill the number of
            # characters of the longest entry. This value is also used for the
            # label generation.
            #
            max_key_len = len(max(self.md5_dict.keys(), key=len))

            #
            # Python sorting algorythm sorts the characters using their ASCII
            # index. The original Checksum generation script mkpdssum.pl did not
            # use this sorting order; '.' and '_' did not have precedence over
            # alphabetical characters.
            #
            # In order to preserve the order provided by mkpdssum.pl, it is
            # necessary to "trick" Python sorting or implement a customised
            # sorting function. The order in ASCII is as follows:
            #
            #    index     char
            #   -------------------
            #    42        *
            #    46        .
            #    47        /
            #    48-57     0-9
            #    58        :
            #    95        _
            #    96        `
            #    65-90     A-Z
            #    97-122    a-z
            #    124       |
            #    126       ~
            #
            # In order to correct the issue there will be a modified of keys
            # list -with file names- that will have '.' replaced by '~' and
            # '_' replaced by '|'. This is safe since filenames do not use
            # these characters.
            #
            md5_dict_keys = list(self.md5_dict.keys())
            for i, s in enumerate(md5_dict_keys):
                md5_dict_keys[i] = s.replace("_", "~").replace(".", "|")

            for key in sorted(md5_dict_keys):
                key = key.replace("~", "_").replace("|", ".")
                md5_list.append(
                    f"{self.md5_dict[key]}  {key}{' ' * (max_key_len - len(key))}"
                )

            self.bytes = max_key_len
            self.record_bytes = 32 + 4 + max_key_len
            self.file_records = len(md5_dict_keys)

        #
        # We remove spurious .DS_Store files if we are working with MacOS.
        #
        for root, _dirs, files in os.walk(self.setup.bundle_directory):
            for file in files:
                if file.endswith(".DS_Store"):
                    path = os.path.join(root, file)
                    logging.info(f"-- Removing {file}")
                    os.remove(path)

        #
        # Checksum start and stop times are the same as the ones defined
        # by the spice_kernel collection and the orbnum files in the
        # miscellaneous collection.
        #
        if self.setup.pds_version == "4":
            coverage_list = []

            #
            # Gather all the relevant products that define the coverage of the
            # checksum file: orbnum labels and spice_kernels collection labels.
            #
            for product in md5_list:
                if ("spice_kernels/collection_spice_kernels_v" in product) or (
                    "miscellaneous/orbnum/" in product and ".xml" in product):
                    coverage_list.append(product.split()[-1])

            start_times = []
            stop_times = []
            for product in coverage_list:
                #
                # The files can either be in the staging or the final area.
                #
                path = (
                    f"{self.setup.bundle_directory}/"
                    f"{self.setup.mission_acronym}_spice/" + product
                )
                if not os.path.isfile(path):
                    path = f"{self.setup.staging_directory}/" + product
                    if not os.path.isfile(path):
                        logging.error(
                            f"-- Product required to determine "
                            f"{self.name} coverage: {product} not found."
                        )

                if os.path.isfile(path):
                    with open(path, "r", encoding='utf-8') as lbl:
                        for line in lbl:
                            if "<start_date_time>" in line:
                                start_time = line.split("<start_date_time>")[-1].split(
                                    "</"
                                )[0]
                                start_times.append(start_time)
                            if "<stop_date_time>" in line:
                                stop_time = line.split("<stop_date_time>")[-1].split(
                                    "</"
                                )[0]
                                stop_times.append(stop_time)

            if not start_times:
                logging.warning(
                    f"-- Start time set to "
                    f"mission start time: {self.setup.mission_start}"
                )
                start_times.append(self.setup.mission_start)

            if not stop_times:
                logging.warning(
                    f"-- Stop time set to "
                    f"mission finish time: {self.setup.mission_finish}"
                )
                stop_times.append(self.setup.mission_finish)

            start_times.sort()
            stop_times.sort()

            self.start_time = start_times[0]
            self.stop_time = stop_times[-1]

        if not set_coverage:
            #
            # Write the checksum file.
            #
            with open(self.path, "w", encoding='utf-8') as c:
                for entry in md5_list:
                    entry = add_carriage_return(entry, self.setup.eol, self.setup)
                    c.write(entry)

            if self.setup.diff:
                logging.info("-- Comparing checksum with previous version...")
                self.compare()

    def compare(self) -> None:
        """**Compare the Checksum with the previous Checksum file**.

        The Checksum file is compared with the previous version.
        """
        try:
            logging.info("")
            compare_files(
                self.path_current,
                self.path,
                self.setup.working_directory,
                self.setup.diff,
            )
        except BaseException:
            logging.warning("-- Checksum from previous increment does not exist.")

        logging.info("")
