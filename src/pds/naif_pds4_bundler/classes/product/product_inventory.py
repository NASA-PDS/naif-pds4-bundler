"""Implementation of the Inventory product class."""
import glob
import logging
import shutil
from pathlib import Path

from .product import Product
from .product_metakernel import MetaKernelProduct
from ..exceptions import NPBError
from ...utils import add_carriage_return
from ...utils import compare_files
from ...utils import replace_string_in_file
from ...utils import type_to_extension


class InventoryProduct(Product):
    """Class that defines a Collection Inventory product.

    :param setup:      NPB execution setup object
    :param run_state:  State of the current pipeline execution
    :param collection: Collection that the inventory product belongs to
    """

    def __init__(self, setup, run_state, collection) -> None:
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

        super().__init__(run_state)

        # Labeling used to happen here (PDS3/PDS4 label picked and built), and
        # so did the PDS3 dsindex-file copy below it. Both moved out:
        # labeling to the pipeline, dsindex copying to its own method,
        # generate_dsindex_files(), also called from the pipeline.

    def _set_location(self) -> None:
        """Set the path and name of the inventory file."""
        # PDS3 only for now, same as write_product().
        self._set_pds3_location()

    def _set_pds3_location(self) -> None:
        """Set the path and name of the PDS3 index file."""
        self.path = f"{self.setup.staging_directory}/index/index.tab"
        self.name = "index.tab"

    def generate_dsindex_files(self) -> None:
        """Copy the PDS3 index file and its label to dsindex.tab/.lbl.

        PDS3 only. This is a separate method, not folded into __init__,
        because it copies ``index.lbl`` -- a file this class doesn't write.
        ``InventoryPDS3Label`` writes it, and the pipeline now builds and
        writes that label after this product's __init__ returns. Call this
        only after that write, or the copy fails with a FileNotFoundError.

        TODO: this ordering is only enforced by the comment in npb.py next to
              the call site and by a pipeline test, not by the type system. If
              the pipeline is ever reordered, this will fail with a
              FileNotFoundError that gives no hint the real cause is ordering.
        """
        shutil.copy2(self.path, self.setup.staging_directory + "/../dsindex.tab")
        shutil.copy2(
            self.path.replace(".tab", ".lbl"),
            self.setup.staging_directory + "/../dsindex.lbl")

        replace_string_in_file(
            self.setup.staging_directory + "/../dsindex.lbl",
            '"INDEX.TAB"',
            '"DSINDEX.TAB"',
            self.setup)

    def write_product(self) -> None:
        """Write and validate the Collection inventory."""
        # PDS3 only for now: the PDS4 class overrides this, and it moves to
        # the PDS3 class next.
        self.write_pds3_index_product()

        self._finish_product()

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
        """Validate the inventory."""
        # PDS3 only for now, same as write_product().
        self.validate_pds3()

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
                            if "\r\n" in col:
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
            if not isinstance(kernel, MetaKernelProduct):
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

                line = add_carriage_return(line, self.setup.eol_pds3)
                file_types.append(
                    type_to_extension(line.split(",")[7].split('"')[1].strip())[0]
                )
                f.write(line)

            #
            # Bytes of each column is necessary to write the index label.
            #
            if not line_for_length:
                raise NPBError(
                    "The index file is incomplete since no binary "
                    "kernel is present in the archive."
                )
            columns = line.split(",")
            column_start_bytes = []
            start_bytes = 1
            for column in columns:

                column_length = len(column)

                if "\r\n" in column:
                    column_length -= 2
                elif "\n" in column:
                    column_length -= 1
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

    def validate_pds3(self) -> None:
        """Validate the PDS3 Index.

        The Inventory is validated by checking that all the products listed
        are present in the archive and comparing the index file with the
        previous one.
        """
        logging.info('-- Validating %s...', self.name)

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
