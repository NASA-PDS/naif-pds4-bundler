"""Implementation of the PDS4 version of a label for Collection Inventory
files.
"""
from pathlib import Path

from .pds4_label import PDS4Label


class InventoryPDS4Label(PDS4Label):
    """Class to generate a PDS4 Collection Inventory Label.

    :param product: Inventory Product of the Collection
    :param collection: Collection the product belongs to
    """

    _mission_reference_type = "collection_to_investigation"
    _target_reference_type = "collection_to_target"

    def __init__(self, product, collection) -> None:
        """Constructor."""
        # PDSLabel.__init__ sets self.setup from product.setup. Note
        # PDS4Label.__init__ still dereferences product.collection.bundle
        # internally, so product.collection must remain populated even
        # though this class now also takes collection explicitly.
        super().__init__(product)

        self.collection = collection

        self._template = str(Path(self.setup.templates_directory)
                             / f"template_collection_{self.collection.type}.xml")

        self.COLLECTION_LID = self.collection.lid
        self.COLLECTION_VID = self.collection.vid

        #
        # The start and stop time of the miscellaneous collection
        # differs from the SPICE kernels collection; the document
        # collection does not have start and stop times.
        #
        if self.collection.name == "miscellaneous":
            #
            # Obtain the latest checksum product and extract the start and stop
            # times.
            #
            start_times = []
            stop_times = []
            # Named collection_product, not product: "product" is already the
            # inventory product this label is for, and looping over it here
            # would silently shadow that parameter for the rest of __init__.
            for collection_product in self.collection.product:
                if "checksum" in collection_product.name:
                    start_times.append(collection_product.start_time)
                    stop_times.append(collection_product.stop_time)

            # Without a checksum product there is no time source for this
            # collection; fail loudly instead of IndexError below.
            if not start_times:
                raise ValueError(
                    f'NPB bug: no checksum product found in collection '
                    f'{self.collection.lid}::{self.collection.vid}; START_TIME and '
                    f'STOP_TIME cannot be determined for the PDS4 Collection '
                    f'Inventory label.')

            start_times.sort()
            stop_times.sort()

            self.START_TIME = start_times[0]
            self.STOP_TIME = stop_times[-1]

        else:
            #
            # The increment start and stop times are still defined by the
            # spice_kernels collection.
            #
            self.START_TIME = self.setup.increment_start
            self.STOP_TIME = self.setup.increment_finish

        self.FILE_NAME = self.product.name

        #
        # Count number of lines in the inventory file
        #
        with open(self.product.path, 'r', encoding='utf-8') as f:
            self.N_RECORDS = str(len(f.readlines()))

        self.name = Path(self.collection.name).with_suffix(".xml").name
        self.write_label()
