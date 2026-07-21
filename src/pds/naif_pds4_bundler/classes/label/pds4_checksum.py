"""Implementation of the PDS4 version of a label for Checksum files.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class ChecksumPDS4Label(PDS4Label):
    """Class to generate a PDS4 Checksum Label.

    :param setup: NPB execution Setup object
    :param product: Checksum product to label
    """

    _mission_reference_type = "ancillary_to_investigation"
    _target_reference_type = "ancillary_to_target"

    def __init__(self, setup, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        self._template = str(Path(setup.templates_directory)
                             / "template_product_checksum_table.xml")

        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = "Character"
        self.START_TIME = self.product.start_time
        self.STOP_TIME = self.product.stop_time
        self.name = Path(product.name).with_suffix(".xml").name

        self.write_label()
