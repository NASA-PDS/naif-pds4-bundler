"""Implementation of the PDS4 version of a label for Collection Inventory
files.
"""
from .label import PDSLabel


class InventoryPDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Collection Inventory Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param collection: Collection to label
    :type product: object
    :param inventory: Inventory Product of the Collection
    :type inventory: object
    """

    def __init__(self, setup: object, collection: object, inventory: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, inventory)

        self.collection = collection
        self.template = (
            f"{setup.templates_directory}/template_collection_{collection.type}.xml"
        )

        self.COLLECTION_LID = self.collection.lid
        self.COLLECTION_VID = self.collection.vid

        #
        # The start and stop time of the miscellaneous collection
        # differs from the SPICE kernels collection; the document
        # collection does not have start and stop times.
        #
        if collection.name == "miscellaneous":
            #
            # Obtain the latest checksum product and extract the start and stop
            # times.
            #
            start_times = []
            stop_times = []
            for product in collection.product:
                if "checksum" in product.name:
                    start_times.append(product.start_time)
                    stop_times.append(product.stop_time)
            start_times.sort()
            stop_times.sort()

            self.START_TIME = start_times[0]
            self.STOP_TIME = stop_times[-1]

        else:
            #
            # The increment start and stop times are still defined by the
            # spice_kernels collection.
            #
            self.START_TIME = setup.increment_start
            self.STOP_TIME = setup.increment_finish

        self.FILE_NAME = inventory.name

        #
        # Count number of lines in the inventory file
        #
        f = open(self.product.path)
        self.N_RECORDS = str(len(f.readlines()))
        f.close()

        self.name = collection.name.split(".")[0] + ".xml"
        self.write_label()

    def get_mission_reference_type(self):
        """Get mission reference type.

        :return: Literally ``collection_to_investigation``
        :rtype: str
        """
        return "collection_to_investigation"

    def get_target_reference_type(self):
        """Get target reference type.

        :return: Literally ``collection_to_target``
        :rtype: str
        """
        return "collection_to_target"
