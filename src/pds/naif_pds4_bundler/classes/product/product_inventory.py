"""Implementation of the Inventory product class."""
import glob
import logging
from pathlib import Path

from .product import Product
from ...utils import compare_files


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

        self._set_location()

        #
        # Kernels are already generated products but Inventories are not.
        #
        self.write_product()
        self.new_product = True

        super().__init__()
        self.derive_file_attributes()

        # Labeling used to happen here (PDS3/PDS4 label picked and built), and
        # so did the PDS3 dsindex-file copy below it. Both moved out:
        # labeling to the pipeline, dsindex copying to its own method,
        # generate_dsindex_files(), also called from the pipeline.

    def _set_location(self) -> None:
        """Set the path and name of the inventory file."""
        raise NotImplementedError

    def write_product(self) -> None:
        """Write the inventory file and then call _finish_product()."""
        raise NotImplementedError

    def _finish_product(self) -> None:
        """Log the new file, validate it and compare it when requested."""
        logging.info(
            '-- Generated %s', Path(self.path).relative_to(self.setup.staging_directory).name)

        if not self.setup.args.silent and not self.setup.args.verbose:
            print('   * Created %s.', Path(self.path).relative_to(self.setup.staging_directory).name)

        self.validate()

        if self.setup.args.diff:
            self.compare()

    def validate(self) -> None:
        """Check that the inventory lists the products of its collection."""
        raise NotImplementedError

    def compare(self) -> None:
        """**Compare the Inventory Product with another Inventory**.

        The Inventory Product is compared with the previous
        version and if it does not exist with the sample INSIGHT inventory
        product.
        """
        mission_acronym = self.setup.mission_acronym
        logging.info(
            '-- Comparing %s...',
            self.name.split(f'{mission_acronym}_spice/')[-1])

        #
        # Use the prior version of the same product, if it does not
        # exist use the sample.
        #
        if self.path_current:

            fromfile = self.path_current
            tofile = self.path
            work_dir = self.setup.working_directory

            compare_files(fromfile, tofile, work_dir, self.setup.args.diff)

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

            compare_files(fromfile, tofile, work_dir, self.setup.args.diff)

        logging.info("")
