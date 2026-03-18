"""Implementation of the PDS4 version of a label for Documents.
"""
from .label import PDSLabel


class DocumentPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Document Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Collection to label
    :type collection: object
    :param inventory: Inventory Product of the Collection
    :type inventory: object
    """

    def __init__(self, setup: object, collection: object, inventory: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, inventory)

        self.setup = setup
        self.collection = collection
        self.template = (
            f"{setup.templates_directory}/template_product_html_document.xml"
        )

        self.PRODUCT_LID = inventory.lid
        self.PRODUCT_VID = inventory.vid
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish
        self.FILE_NAME = inventory.name

        self.name = collection.name.split(".")[0] + ".xml"

        self.write_label()
