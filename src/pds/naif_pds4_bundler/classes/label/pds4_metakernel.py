"""Implementation of the PDS4 version of a label for Metakernel files.
"""
from pathlib import Path

from .label import PDSLabel
from ...utils import extension_to_type


class MetaKernelPDS4Label(PDSLabel):
    """Class to generate a PDS4 SPICE Kernel MK Label.

    :param setup:   NPB execution Setup object
    :param product: MK product to label
    """

    def __init__(self, setup, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        self.template = str(Path(setup.templates_directory)
                            / "template_product_spice_kernel_mk.xml")

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = "Character"
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        self.KERNEL_INTERNAL_REFERENCES = self.get_kernel_internal_references()

        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()

    def get_kernel_internal_references(self):
        """Get the MK label internal references.

        :return: PDS4 formatted Kernel list used by the label for internal
                 references.
        :rtype: str
        """
        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        #
        # From the collection we only use kernels in the MK
        #
        kernel_list_for_label = ""
        for kernel in self.product.collection_metakernel:
            #
            # The kernel lid cannot be obtained from the list; it is
            # merely a list of strings.
            #
            kernel_type = extension_to_type(kernel)
            kernel_lid = "{}:spice_kernels:{}_{}".format(
                self.setup.logical_identifier, kernel_type, kernel.lower()
            )

            kernel_list_for_label += (
                f"{' ' * 2 * tab}<Internal_Reference>{eol}"
                + f"{' ' * 3 * tab}<lid_reference>{kernel_lid}"
                f"</lid_reference>{eol}"
                + f"{' ' * 3 * tab}<reference_type>data_to_associate"
                f"</reference_type>{eol}" + f"{' ' * 2 * tab}</Internal_Reference>{eol}"
            )

        kernel_list_for_label = kernel_list_for_label.rstrip() + eol

        return kernel_list_for_label
