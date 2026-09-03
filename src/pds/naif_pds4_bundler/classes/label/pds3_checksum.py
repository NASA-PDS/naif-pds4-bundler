"""Implementation of the PDS3 version of a label for Checksum files.
"""
from pathlib import Path

from .pds3_label import PDS3Label


class ChecksumPDS3Label(PDS3Label):
    """PDS Label child class to a PDS3 Checksum Label.

    :param product: Checksum product to label
    """

    def __init__(self, product) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup.
        super().__init__(product)

        # Template path now reads templates_directory via self.setup instead
        # of a separate setup argument.
        self._template = str(Path(self.setup.templates_directory)
                             / "template_product_checksum_table.lbl")

        self._label_fields["VOLUME_ID"] = self.setup.volume_id.upper()
        self._label_fields["PRODUCT_CREATION_TIME"] = product.creation_time
        self._label_fields["RECORD_BYTES"] = str(self.product.record_bytes)
        self._label_fields["FILE_RECORDS"] = str(self.product.file_records)
        self._label_fields["BYTES"] = str(self.product.bytes)

        self.name = "checksum.lbl"

        self.write_label()
