"""Implementation of the PDS4 version of a label for SPICE kernel files.
"""
from .label import PDSLabel


class SpiceKernelPDS4Label(PDSLabel):
    """PDS Label child class to generate a non-MK PDS4 SPICE Kernel Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: SPICE Kernel product to be labeled
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = (
            f"{self.setup.templates_directory}/template_product_spice_kernel.xml"
        )

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
