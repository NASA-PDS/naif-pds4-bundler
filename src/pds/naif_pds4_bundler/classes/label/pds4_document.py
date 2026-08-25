"""Implementation of the PDS4 version of a label for Documents.
"""
from pathlib import Path

from .pds4_label import PDS4Label
from ..exceptions import NPBError


class DocumentPDS4Label(PDS4Label):
    """Class to generate a PDS4 Document Label.

    :param product: Document product to label (e.g. the SPICEDS product)
    """

    _mission_reference_type = "document_to_investigation"

    def __init__(self, product) -> None:
        """Constructor."""
        # Collection-level labels depend on product.collection already being
        # populated; check it before super().__init__() runs, since
        # PDS4Label.__init__ itself dereferences product.collection.bundle --
        # a check placed after that call would never be reached.
        if product.collection is None:
            raise NPBError(
                "product.collection must be set before constructing this label."
            )

        # PDSLabel.__init__ sets self.setup from product.setup; no need to
        # assign it again here.
        super().__init__(product)

        self.collection = product.collection

        self._template = str(Path(self.setup.templates_directory)
                             / "template_product_html_document.xml")

        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.START_TIME = self.setup.mission_start
        self.STOP_TIME = self.setup.mission_finish
        self.FILE_NAME = self.product.name

        self.name = Path(self.collection.name).with_suffix(".xml").name

        self.write_label()
