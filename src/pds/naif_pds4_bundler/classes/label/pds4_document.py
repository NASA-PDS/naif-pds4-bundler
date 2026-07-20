"""Implementation of the PDS4 version of a label for Documents.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class DocumentPDS4Label(PDS4Label):
    """Class to generate a PDS4 Document Label.

    :param setup:      NPB execution Setup object
    :param collection: Collection to label
    :param inventory:  Inventory Product of the Collection
    """

    def __init__(self, setup, collection, inventory) -> None:
        """Constructor."""
        super().__init__(setup, inventory)

        self.setup = setup
        self.collection = collection

        self.template = str(Path(setup.templates_directory)
                            / "template_product_html_document.xml")

        self.PRODUCT_LID = inventory.lid
        self.PRODUCT_VID = inventory.vid
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish
        self.FILE_NAME = inventory.name

        self.name = Path(collection.name).with_suffix(".xml").name

        self.write_label()

    def get_mission_reference_type(self):
        """Get mission reference type.

        :return: Literally ``document_to_investigation``
        :rtype: str
        """
        return "document_to_investigation"
