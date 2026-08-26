"""Implementation of the PDS4 version of a label for Documents.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class DocumentPDS4Label(PDS4Label):
    """Class to generate a PDS4 Document Label.

    :param product: Document product to label (e.g. the SPICEDS product)
    :param collection: Collection the product belongs to
    """

    _mission_reference_type = "document_to_investigation"

    def __init__(self, product, collection) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup. Note
        # PDS4Label.__init__ still dereferences product.collection.bundle
        # internally, so product.collection must remain populated even
        # though this class now also takes collection explicitly.
        super().__init__(product)

        self.collection = collection

        self._template = str(Path(self.setup.templates_directory)
                             / "template_product_html_document.xml")

        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.START_TIME = self.setup.mission_start
        self.STOP_TIME = self.setup.mission_finish
        self.FILE_NAME = self.product.name

        self.name = Path(self.collection.name).with_suffix(".xml").name

        self.write_label()
