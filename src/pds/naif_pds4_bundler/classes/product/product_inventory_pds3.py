"""PDS3 version-specific collection inventory product."""

import logging
import shutil

from .product_inventory import InventoryProduct
from .product_metakernel import MetaKernelProduct
from .product_pds3 import PDS3Product
from ..exceptions import NPBError
from ...utils import add_carriage_return
from ...utils import replace_string_in_file
from ...utils import type_to_extension


class InventoryPDS3Product(InventoryProduct, PDS3Product):
    """Collection inventory product of a PDS3 archive (the index file)."""

    def _set_location(self) -> None:
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

        self._finish_product()

    def validate(self) -> None:
        """Validate the PDS3 Index.

        The Inventory is validated by checking that all the products listed
        are present in the archive and comparing the index file with the
        previous one.
        """
        logging.info('-- Validating %s...', self.name)
