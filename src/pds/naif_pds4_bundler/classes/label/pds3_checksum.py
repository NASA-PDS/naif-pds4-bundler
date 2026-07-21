"""Implementation of the PDS3 version of a label for Checksum files.
"""
from pathlib import Path

from .pds3_label import PDS3Label


class ChecksumPDS3Label(PDS3Label):
    """PDS Label child class to a PDS3 Checksum Label.

    :param setup:   NPB  execution Setup object
    :param product: Checksum product to label
    """

    def __init__(self, setup, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        self._template = str(Path(setup.templates_directory)
                             / "template_product_checksum_table.lbl")

        self.VOLUME_ID = self.setup.volume_id.upper()
        self.PRODUCT_CREATION_TIME = product.creation_time
        self.RECORD_BYTES = str(self.product.record_bytes)
        self.FILE_RECORDS = str(self.product.file_records)
        self.BYTES = str(self.product.bytes)

        self.name = "checksum.lbl"

        self.write_label()
