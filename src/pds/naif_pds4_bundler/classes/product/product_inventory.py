"""Implementation of the Inventory product class."""
import glob
import logging
import os
import shutil

from .product import Product
from ...pipeline.runtime import handle_npb_error
from ...utils import add_carriage_return
from ...utils import compare_files
from ...utils import replace_string_in_file
from ...utils import type_to_extension
from ..label import InventoryPDS3Label, InventoryPDS4Label


class InventoryProduct(Product):
    """Class that defines a Collection Inventory product.

    :param setup:      NPB execution setup object
    :param collection: Collection that the inventory product belongs to
    """

    def __init__(self, setup, collection) -> None:
        """Constructor."""

        self.collection = collection
        self.column_bytes = []
        self.column_start_bytes = []
        self.file_types = []
        self.rows = 0
        self.row_bytes = 0
        self.setup = setup

        if setup.pds_version == "3":
            self.path = f"{setup.staging_directory}/index/index.tab"
            self.name = "index.tab"

        elif setup.pds_version == "4":

            #
            # Determine the inventory version
            #
            if self.setup.increment:
                inventory_files = glob.glob(
                    self.setup.bundle_directory
                    + f"/{self.setup.mission_acronym}_spice"
                    + os.sep
                    + collection.name
                    + os.sep
                    + f"collection_{collection.name}_inventory_v*.csv"
                )
                inventory_files += glob.glob(
                    self.setup.staging_directory
                    + os.sep
                    + collection.name
                    + os.sep
                    + f"collection_{collection.name}_inventory_v*.csv"
                )
                inventory_files.sort()
                try:
                    latest_file = inventory_files[-1]

                    #
                    # We store the previous version to use it to validate the
                    # generated one.
                    #
                    self.path_current = latest_file

                    latest_version = latest_file.split("_v")[-1].split(".")[0]
                    self.version = int(latest_version) + 1

                    logging.info(f"-- Previous inventory file is: {latest_file}")
                    logging.info(f"-- Generate version {self.version}.")

                except BaseException:
                    self.version = 1
                    self.path_current = ""

                    logging.warning("-- Previous inventory file not found.")
                    logging.warning(f"-- Default to version {self.version}.")
                    logging.warning("-- The version of this file might be incorrect.")

            else:
                self.version = 1
                self.path_current = ""

                logging.warning(f"-- Default to version {self.version}.")
                logging.warning(
                    "-- Make sure this is the first release of the archive."
                )

            self.name = f"collection_{collection.name}_inventory_v{self.version:03}.csv"
            self.path = (
                setup.staging_directory + os.sep + collection.name + os.sep + self.name
            )

            self.set_product_lid()
            self.set_product_vid()

        #
        # Kernels are already generated products but Inventories are not.
        #
        self.write_product()
        self.new_product = True

        Product.__init__(self)

        if setup.pds_version == "4":
            self.label = InventoryPDS4Label(setup, collection, self)
        elif setup.pds_version == "3":
            self.label = InventoryPDS3Label(setup, collection, self)

            #
            # Generate dsindex files.
            #
            shutil.copy2(self.path, self.setup.staging_directory + "/../dsindex.tab")
            shutil.copy2(
                self.path.replace(".tab", ".lbl"),
                self.setup.staging_directory + "/../dsindex.lbl",
            )

            replace_string_in_file(
                self.setup.staging_directory + "/../dsindex.lbl",
                '"INDEX.TAB"',
                '"DSINDEX.TAB"',
                self.setup,
            )

    def set_product_lid(self) -> None:
        """Set the Product LID."""
        self.lid = f"{self.setup.logical_identifier}:document:spiceds"

    def set_product_vid(self) -> None:
        """Set the Product VID."""
        self.vid = f'{int(self.version)}.0'

    def write_product(self) -> None:
        """Write and validate the Collection inventory."""
        if self.setup.pds_version == "4":
            self.write_pds4_collection_product()
        else:
            self.write_pds3_index_product()

        logging.info(
            f"-- Generated {self.path.split(self.setup.staging_directory)[-1]}"
        )
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(f"   * Created {self.path.split(self.setup.staging_directory)[-1]}.")

        if self.setup.pds_version == "4":
            self.validate_pds4()
        else:
            self.validate_pds3()

        if self.setup.diff:
            self.compare()

    def write_pds4_collection_product(self) -> None:
        """Write the PDS4 Collection product."""
        #
        # If there is an existing version we need to add the items from
        # the previous version as SECONDARY members
        #
        with open(self.path, "w+", encoding='utf-8') as f:
            if self.path_current:
                with open(self.path_current, "r", encoding='utf-8') as r:
                    for line in r:
                        if "P,urn" in line:
                            #
                            # All primary items in previous version shall
                            # be included as secondary in the new one
                            #
                            line = line.replace("P,urn", "S,urn")
                        line = add_carriage_return(
                            line, self.setup.eol_pds4, self.setup
                        )
                        f.write(line)

            for product in self.collection.product:
                #
                # This conditional is added because miscellaneous inventories
                # are added to the collection before generating the inventory
                # product itself.
                #
                if not isinstance(product, InventoryProduct):
                    if product.new_product:
                        line = f"P,{product.lid}::{product.vid}\r\n"
                        line = add_carriage_return(
                            line, self.setup.eol_pds4, self.setup
                        )
                        f.write(line)

    def write_pds3_index_product(self) -> None:
        """This method uses the previous index file to generate the new one.

        There is a NAIF Perl script that will generate an index file from a
        kernel list file. Please contact the NAIF if you are interested in such
        script.
        """
        current_index = []
        column_length = [0] * 10

        if self.setup.increment:
            existing_index = (
                f"{self.setup.bundle_directory}/{self.setup.volume_id}/index/index.tab"
            )

            with open(existing_index, "r", encoding='utf-8') as f:
                for line in f:
                    if line.strip() != "":
                        index_row = line.split(",")
                        for i, col in enumerate(index_row):
                            if '"' in col:
                                index_row[i] = col.split('"')[1].strip()
                            else:
                                index_row[i] = col.strip()

                            #
                            # Remove EOL characters from last element of the
                            # column.
                            #
                            if "\n\r" in col:
                                col_len = len(col) - 2
                            elif "\n" in col:
                                col_len = len(col) - 1
                            else:
                                col_len = len(col)

                            if column_length[i] < col_len:
                                column_length[i] = col_len

                        current_index.append(index_row)

        new_index = []

        for kernel in self.collection.product:
            if type(kernel).__name__ != "MetaKernelProduct":
                index_row = [
                    kernel.start_time.split("Z")[0],
                    kernel.stop_time.split("Z")[0],
                    "data/" + kernel.path.split("/data/")[-1].split(".")[0] + ".lbl",
                    self.collection.list.DATA_SET_ID,
                    kernel.creation_time,
                    self.collection.list.RELID,
                    self.collection.list.RELDATE,
                    kernel.type.upper(),
                    kernel.name,
                    self.collection.list.VOLID.lower(),
                ]

                new_index.append(index_row)

        #
        # Merge both lists
        #
        index = current_index + new_index

        rows = 0
        column_bytes = []
        file_types = []

        line_for_length = ""
        with open(self.path, "w+", encoding='utf-8') as f:
            for row in index:
                rows += 1
                line = ""
                for i, col in enumerate(row):
                    if i < 2 or i == 4 or i == 6:
                        if col == "N/A":
                            col = '"N/A"'
                        line += f'{col}{" " * (column_length[i] - len(col))}'
                    else:
                        line += f'"{col}{" " * (column_length[i] - len(col) - 2)}"'
                        line_for_length = line
                    if i != 9:
                        line += ","

                line = add_carriage_return(line, self.setup.eol_pds3, self.setup)
                file_types.append(
                    type_to_extension(line.split(",")[7].split('"')[1].strip())[0]
                )
                f.write(line)

            #
            # Bytes of each column is necessary to write the index label.
            #
            if not line_for_length:
                handle_npb_error(
                    "The index file is incomplete since no binary "
                    "kernel is present in the archive."
                )
            columns = line.split(",")
            column_start_bytes = []
            start_bytes = 1
            for column in columns:

                column_length = len(column)

                if "\n\r" in column:
                    column_length -= 3
                elif "\n" in column:
                    column_length -= 2
                if '"' in column:
                    column_length -= 2
                    start_bytes += 1

                column_start_bytes.append(start_bytes)

                if '"' in column:
                    start_bytes += len(column)
                else:
                    start_bytes += len(column) + 1

                column_bytes.append(column_length)

        file_types = list(set(file_types))

        self.file_types = file_types
        self.column_bytes = column_bytes
        self.column_start_bytes = column_start_bytes
        self.row_bytes = len(line)
        self.rows = rows

    def validate_pds4(self) -> None:
        """Validate the PDS4 Inventory Product.

        The Inventory is validated by checking that all the products listed
        are present in the archive.
        """
        logging.info(f"-- Validating {self.name}...")

        #
        # Check that all the products are listed in the collection product.
        #
        logging.info("      Check that all the products are in the collection.")

        for product in self.collection.product:
            if type(product).__name__ != "InventoryProduct":
                product_found = False
                with open(self.path, "r", encoding='utf-8') as c:
                    for line in c:
                        if product.lid in line:
                            product_found = True
                    if not product_found:
                        logging.error(
                            f"      Product {product.lid} not found. "
                            f"Consider increment re-generation."
                        )

        logging.info("      OK")
        logging.info("")

    def validate_pds3(self) -> None:
        """Validate the PDS3 Index.

        The Inventory is validated by checking that all the products listed
        are present in the archive and comparing the index file with the
        previous one.
        """
        logging.info(f"-- Validating {self.name}...")

    def compare(self) -> None:
        """**Compare the Inventory Product with another Inventory**.

        The Inventory Product is compared with the previous
        version and if it does not exist with the sample INSIGHT inventory
        product.
        """
        mission_acronym = self.setup.mission_acronym
        logging.info(
            f"-- Comparing "
            f'{self.name.split(f"{mission_acronym}_spice/")[-1]}'
            f"..."
        )

        #
        # Use the prior version of the same product, if it does not
        # exist use the sample.
        #
        if self.path_current:

            fromfile = self.path_current
            tofile = self.path
            work_dir = self.setup.working_directory

            compare_files(fromfile, tofile, work_dir, self.setup.diff)

        else:

            logging.warning("-- Comparing with InSight test inventory product.")
            fromfiles = glob.glob(
                f"{self.setup.root_dir}data/insight_spice/{self.collection.name}/"
                f"collection_{self.collection.name}_inventory_*.csv"
            )
            fromfiles.sort()
            fromfile = fromfiles[-1]
            tofile = self.path
            work_dir = self.setup.working_directory

            compare_files(fromfile, tofile, work_dir, self.setup.diff)

        logging.info("")
