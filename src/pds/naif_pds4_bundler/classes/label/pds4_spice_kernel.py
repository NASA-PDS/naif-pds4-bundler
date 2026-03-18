"""Implementation of the PDS4 version of a label for SPICE kernel files.
"""
from pathlib import Path

from .label import PDSLabel


class SpiceKernelPDS4Label(PDSLabel):
    """Class to generate a non-MK PDS4 SPICE Kernel Label.

    :param setup:   NPB execution Setup object
    :param product: SPICE Kernel product to be labeled
    """

    def __init__(self, setup, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        self.template = str(Path(setup.templates_directory)
                            / "template_product_spice_kernel.xml")

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = product.file_format
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        self.write_label()
