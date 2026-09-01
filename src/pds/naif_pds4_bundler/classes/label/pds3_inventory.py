"""Implementation of the PDS3 version of a label for Index files.
"""
from .pds3_label import PDS3Label


class InventoryPDS3Label(PDS3Label):
    """PDS Label child class to generate a PDS3 Index Label.

    :param product: Index Product
    :param collection: Collection the product belongs to
    """

    def __init__(self, product, collection) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup.
        super().__init__(product)

        self.collection = collection

        # TODO: Check why this template path is not following the approach of all
        #       other labels.
        self._template = f'{self.root_dir}/templates/pds3/template_collection_{self.collection.type}.lbl'

        self._label_fields["VOLUME_ID"] = self.setup.volume_id
        self._label_fields["ROW_BYTES"] = str(self.product.row_bytes)
        self._label_fields["ROWS"] = str(self.product.rows)

        # One START_BYTE_NN/BYTES_NN pair per column, 1-indexed to match the
        # template's own numbering.
        for i, byt in enumerate(self.product.column_bytes):

            self._label_fields[f"START_BYTE_{i + 1:02d}"] = str(
                self.product.column_start_bytes[i])

            self._label_fields[f"BYTES_{i + 1:02d}"] = str(byt)

        file_types = self.product.file_types
        if len(file_types) == 1:
            indexed_file_name = f"*.{file_types[0]}"
        else:
            file_types.sort()
            indexed_file_name = "{" + self.setup.eol_pds3
            for file_type in file_types:
                indexed_file_name += (
                    f'{29 * " "}  "*.{file_type}",{self.setup.eol_pds3}'
                )

            indexed_file_name = (
                indexed_file_name[:-3] + self.setup.eol_pds3 + 29 * " " + "}\n"
            )

        self._label_fields["INDEXED_FILE_NAME"] = indexed_file_name

        self.write_label()
