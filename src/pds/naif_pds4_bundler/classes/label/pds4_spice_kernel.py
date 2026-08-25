"""Implementation of the PDS4 version of a label for SPICE kernel files.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class SpiceKernelPDS4Label(PDS4Label):
    """Class to generate a non-MK PDS4 SPICE Kernel Label.

    :param product: SPICE Kernel product to be labeled
    """

    def __init__(self, product) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup.
        super().__init__(product)

        # Template path now reads templates_directory via self.setup instead of
        # a separate setup argument.
        self._template = str(Path(self.setup.templates_directory)
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
