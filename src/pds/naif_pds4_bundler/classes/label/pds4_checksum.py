"""Implementation of the PDS4 version of a label for Checksum files.
"""
from .label import PDSLabel


class ChecksumPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Checksum Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: Checksum product to label
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{setup.templates_directory}/template_product_checksum_table.xml"
        )

        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = "Character"
        self.START_TIME = self.product.start_time
        self.STOP_TIME = self.product.stop_time
        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()
