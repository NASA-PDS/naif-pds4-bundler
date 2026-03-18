"""Implementation of the PDS3 version of a label for Index files.
"""
from .label import PDSLabel


class InventoryPDS3Label(PDSLabel):
    """PDS Label child class to generate a PDS3 Index Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Index Collection
    :type product: object
    :param inventory: Index Product
    :type inventory: object
    """

    def __init__(
        self, mission: object, collection: object, inventory: object
    ) -> object:
        """Constructor."""
        PDSLabel.__init__(self, mission, inventory)

        self.collection = collection
        self.template = (
            self.root_dir
            + "/templates/pds3/template_collection_{}.lbl".format(collection.type)
        )

        self.VOLUME_ID = self.setup.volume_id
        self.ROW_BYTES = str(self.product.row_bytes)
        self.ROWS = str(self.product.rows)

        for i, bytes in enumerate(self.product.column_bytes):

            setattr(
                self, f"START_BYTE_{i + 1:02d}", str(self.product.column_start_bytes[i])
            )
            setattr(self, f"BYTES_{i + 1:02d}", str(bytes))

        file_types = self.product.file_types
        if len(file_types) == 1:
            indexed_file_name = f"*.{file_types}"
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

        self.INDEXED_FILE_NAME = indexed_file_name

        self.write_label()
