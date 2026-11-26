"""Collection Class amd Child Classes Implementation."""
from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ..exceptions import NPBInternalError
from ...utils import find_latest_versioned_file

# Imported for the type hints only, so it isn't loaded when NPB runs.
if TYPE_CHECKING:
    from ..product.product import Product


class Collection:
    """Class to generate a PDS4 Collection.

    :param c_type:   Collection type: kernels, documents or miscellaneous
    :param setup:  Setup object
    """

    def __init__(self, c_type: str, setup, bundle) -> None:
        """Constructor."""
        self.bundle = bundle
        self.name = c_type
        self.product = []
        self.setup = setup
        self.vid = ''

        #
        # To know whether if the collection has been updated or not.
        #
        self.updated = False

        if setup.pds_version == "4":
            self.set_collection_lid()

    def add(self, element):
        """Add a Product to the Collection.

        :param element: Product to add to Collection
        """
        self.product.append(element)

        #
        # If an element has been added to the collection then, the collection
        # must be updated.
        #
        self.updated = True

    def replace(self, old: Product, new: Product) -> None:
        """Replace a Product of the Collection with another one.

        The new product takes the position of the old one. The collection is
        not marked as updated, since nothing is added to it.

        :param old: Product to replace, matched by identity
        :param new: Product that takes its place
        :raises NPBInternalError: If the old product is not in the collection
        """
        # Compare with 'is' to find that exact object. list.index() would also
        # accept a different product that is equal to it.
        for position, product in enumerate(self.product):
            if product is old:
                self.product[position] = new
                return

        # The loop ended without a match, so the product was never there.
        raise NPBInternalError(
            f"product to replace not found in the {self.name} collection.")

    def set_collection_lid(self):
        """Set the Bundle LID."""
        if self.setup.pds_version != "3":
            self.lid = f"{self.setup.logical_identifier}:{self.type}"

    def set_collection_vid(self):
        """Set the Bundle VID.

        In general Collection versions are not equal to the release number.
        If the collection has been updated we obtain the increased version, but
        if it has not been updated we use the previous version.

        Given the case that the version cannot be determined: if it is the SPICE
        kernels collection assume is the same version as the bundle, otherwise
        we set it to 1.
        """
        if self.setup.increment:

            candidate_dirs = [
                Path(f"{self.setup.bundle_directory}/"
                     f"{self.setup.mission_acronym}_spice/{self.name}"),
                Path(f"{self.setup.staging_directory}/{self.name}"),
            ]
            latest_file, latest_version = find_latest_versioned_file(
                candidate_dirs, f"*{self.name}*"
            )

            # latest_version is None either when no file matched, or when a file
            # matched but its name didn't parse as expected.
            if latest_version is not None:

                # A collection that hasn't changed keeps its previous version;
                # only an updated collection bumps it.
                version = latest_version + 1 if self.updated else latest_version

                vid = f'{version}.0'

                logging.info(
                    '-- Collection of %s version set to %s, derived from:',
                    self.type, version)
                logging.info('   %s', latest_file)
                logging.info('')

            else:

                # No usable previous version found: fall back to the bundle
                # release number for the SPICE kernels collection (it always
                # tracks the release), or to 1 for any other collection.
                if self.name == "spice_kernels":
                    ver = int(self.setup.release)

                else:
                    ver = 1

                logging.warning(
                    '-- No %s collection available in previous increment.',
                    self.type)
                logging.warning('-- Collection of %s version set to: %d.',
                                self.type, ver)

                vid = f'{ver}.0'
                logging.info("")

        else:
            logging.warning('-- Collection of %s version set to: %d.',
                            self.type, int(self.setup.release))

            vid = f'{int(self.setup.release)}.0'
            logging.info('')

        self.vid = vid
