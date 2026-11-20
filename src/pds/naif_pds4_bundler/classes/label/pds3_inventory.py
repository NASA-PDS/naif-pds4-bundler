"""Implementation of the PDS3 version of a label for Index files.
"""
from .pds3_label import PDS3Label


class InventoryPDS3Label(PDS3Label):
    """PDS Label child class to generate a PDS3 Index Label.

    :param product: Index Product
    """

    def __init__(self, product) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup.
        super().__init__(product)

        self.collection = product.collection

        self._template = self._resolve_template(
            f"template_collection_{self.collection.type}.lbl")

        self._label_fields["VOLUME_ID"] = self.setup.volume_id
        self._label_fields["ROW_BYTES"] = str(self.product.row_bytes)
        self._label_fields["ROWS"] = str(self.product.rows)

        # One START_BYTE_NN/BYTES_NN pair per column, 1-indexed to match the
        # template's own numbering.
        for i, byt in enumerate(self.product.column_bytes):

            self._label_fields[f"START_BYTE_{i + 1:02d}"] = str(
                self.product.column_start_bytes[i])

            self._label_fields[f"BYTES_{i + 1:02d}"] = str(byt)

        # The file types of the product come from a set, so their order
        # changes from run to run; sorted() fixes it without touching the
        # product's own list.
        file_types = sorted(self.product.file_types)
        if len(file_types) == 1:
            indexed_file_name = f"*.{file_types[0]}"
        else:
            eol = self.setup.eol_pds3
            entries = [
                f'{29 * " "}  "*.{file_type}"' for file_type in file_types
            ]

            # The comma goes between the entries, so the last one has none.
            indexed_file_name = (
                "{" + eol + ("," + eol).join(entries) + eol + 29 * " " + "}\n"
            )

        self._label_fields["INDEXED_FILE_NAME"] = indexed_file_name

    def _derive_name(self) -> str:
        """Derive the destination path of the label, without 'inventory_'.

        The label describes the collection, so its name leaves out the
        'inventory_' token of the inventory product.

        :return: Destination path for the label file.
        """
        return super()._derive_name().replace("inventory_", "")
