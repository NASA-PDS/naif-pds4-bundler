"""Implementation of the PDS4 version of a label for the SPICEDS document.
"""
from pathlib import Path

from .pds4_label import PDS4Label


# Labels the SPICEDS document product only -- not a generic document label.
class SpicedsPDS4Label(PDS4Label):
    """Class to generate a PDS4 SPICEDS document Label.

    :param setup:      NPB execution Setup object
    :param collection: Collection to label
    :param product:    SPICEDS Product to label
    """

    _mission_reference_type = "document_to_investigation"

    def __init__(self, setup, collection, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        self.setup = setup
        self.collection = collection

        # Template file used to render this specific SPICEDS label.
        self._template = str(Path(setup.templates_directory)
                             / "template_product_spiceds.xml")

        # Fields pulled from the SPICEDS product being labeled.
        self.PRODUCT_LID = product.lid
        self.PRODUCT_VID = product.vid
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish
        self.FILE_NAME = product.name

        self.name = Path(collection.name).with_suffix(".xml").name

        self.write_label()
