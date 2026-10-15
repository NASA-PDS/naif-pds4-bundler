"""PDS4 version-specific collection inventory product."""

import logging
import os
from pathlib import Path

from .product_inventory import InventoryProduct
from .product_pds4 import PDS4Product
from ...utils import add_carriage_return
from ...utils import find_latest_versioned_file


class InventoryPDS4Product(InventoryProduct, PDS4Product):
    """Collection inventory product of a PDS4 bundle (a CSV file)."""

    def _set_location(self) -> None:
        """Set the version, path, name, LID and VID of the PDS4 inventory."""

        #
        # Determine the inventory version
        #
        if self.setup.increment:
            # Search both the bundle directory (previous increments) and the
            # staging directory (current, in-progress increment) for the
            # latest inventory file already written.
            inventory_dirs = [
                Path(self.setup.bundle_directory)
                / f"{self.setup.mission_acronym}_spice"
                / self.collection.name,

                Path(self.setup.staging_directory) / self.collection.name,
            ]
            latest_file, latest_version = find_latest_versioned_file(
                inventory_dirs,
                f"collection_{self.collection.name}_inventory_v*.csv"
            )

            # latest_version is None either when no file matched, or when
            # a file matched but its name didn't parse as expected.
            if latest_version is not None:

                #
                # We store the previous version to use it to validate the
                # generated one.
                #
                self.path_current = latest_file
                self.version = latest_version + 1

                logging.info('-- Previous inventory file is: %s', latest_file)
                logging.info('-- Generate version %d.', self.version)

            else:
                # No usable previous inventory file: start over at v1 rather
                # than guessing a version from a partial match.
                self.version = 1
                self.path_current = ""

                logging.warning('-- Previous inventory file not found.')
                logging.warning('-- Default to version %d.', self.version)
                logging.warning('-- The version of this file might be incorrect.')

        else:
            self.version = 1
            self.path_current = ""

            logging.warning('-- Default to version %d.', self.version)
            logging.warning(
                '-- Make sure this is the first release of the archive.')

        self.name = (
            f"collection_{self.collection.name}_inventory_v{self.version:03}.csv"
        )
        self.path = (
            self.setup.staging_directory
            + os.sep + self.collection.name
            + os.sep + self.name
        )

        self.set_product_lid()
        self.set_product_vid()

    def set_product_lid(self) -> None:
        """Set the Product LID."""
        self.lid = f"{self.setup.logical_identifier}:document:spiceds"

    def set_product_vid(self) -> None:
        """Set the Product VID."""
        self.vid = f'{int(self.version)}.0'

    def write_product(self) -> None:
        """Write the PDS4 Collection product, then validate it."""
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
                        line = add_carriage_return(line, self.setup.eol_pds4)
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
                        line = add_carriage_return(line, self.setup.eol_pds4)
                        f.write(line)

        self._finish_product()

    def validate(self) -> None:
        """Validate the PDS4 Inventory Product.

        The Inventory is validated by checking that all the products listed
        are present in the archive.
        """
        logging.info('-- Validating %s...', self.name)

        #
        # Check that all the products are listed in the collection product.
        #
        logging.info("      Check that all the products are in the collection.")

        for product in self.collection.product:
            if not isinstance(product, InventoryProduct):
                product_found = False
                with open(self.path, "r", encoding='utf-8') as c:
                    for line in c:
                        if product.lid in line:
                            product_found = True
                    if not product_found:
                        logging.error(
                            '      Product %s not found. '
                            'Consider increment re-generation.', product.lid)

        logging.info("      OK")
        logging.info("")
