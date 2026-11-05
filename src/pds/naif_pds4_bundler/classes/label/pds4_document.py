"""Implementation of the PDS4 version of a label for Documents.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class DocumentPDS4Label(PDS4Label):
    """Class to generate a PDS4 Document Label.

    :param product: Document product to label (e.g. the SPICEDS product)
    """

    _mission_reference_type = "document_to_investigation"

    def __init__(self, product) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup.
        super().__init__(product)

        self._template = str(Path(self.setup.templates_directory)
                             / "template_product_html_document.xml")

        self._label_fields["PRODUCT_LID"] = self.product.lid
        self._label_fields["PRODUCT_VID"] = self.product.vid
        self._label_fields["START_TIME"] = self.setup.mission_start
        self._label_fields["STOP_TIME"] = self.setup.mission_finish
        self._label_fields["FILE_NAME"] = self.product.name
