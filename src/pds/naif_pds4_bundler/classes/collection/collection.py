"""Collection Class amd Child Classes Implementation."""
import glob
import logging


class Collection:
    """Class to generate a PDS4 Collection.

    :param type:   Collection type: kernels, documents or miscellaneous
    :param setup:  Setup object
    """

    def __init__(self, type: str, setup, bundle) -> None:
        """Constructor."""
        self.product = []
        self.name = type
        self.setup = setup
        self.bundle = bundle

        #
        # To know whether if the collection has been updated or not.
        #
        self.updated = False

        if setup.pds_version == "4":
            self.set_collection_lid()

    def add(self, element):
        """Add a Product to the Collection.

        :param element: Product to add to Collection
        :type element: object
        """
        self.product.append(element)

        #
        # If an element has been added to the collection then, the collection
        # must be updated.
        #
        self.updated = True

    def set_collection_lid(self):
        """Set the Bundle LID."""
        if self.setup.pds_version != "3":
            self.lid = f"{self.setup.logical_identifier}:{self.type}"

    def set_collection_vid(self):
        """Set the Bundle VID.

        In general Collection versions are not equal to the release number.
        If the collection has been updated we obtain the increased
        version, but if it has not been updated we use the previous
        version.

        Given the case thatt he version cannot be determined: if it is the
        SPICE kernels collection assume is the same version as the bundle,
        otherwise we set it to 1.
        """
        if self.setup.increment:
            try:
                versions = glob.glob(
                    f"{self.setup.bundle_directory}/"
                    f"{self.setup.mission_acronym}_spice/"
                    f"{self.name}/*{self.name}*"
                )
                versions += glob.glob(
                    f"{self.setup.staging_directory}/{self.name}/*{self.name}*"
                )

                versions.sort()

                if self.updated:
                    version = int(versions[-1].split("v")[-1].split(".")[0]) + 1
                else:
                    version = int(versions[-1].split("v")[-1].split(".")[0])

                vid = "{}.0".format(version)
                logging.info(
                    f"-- Collection of {self.type} version set to "
                    f"{version}, derived from:"
                )
                logging.info(f"   {versions[-1]}")
                logging.info("")

            except BaseException:
                if self.name == "spice_kernel":
                    ver = int(self.setup.release)
                else:
                    ver = 1

                logging.warning(
                    f"-- No {self.type} collection available in previous increment."
                )
                logging.warning(f"-- Collection of {self.type} version set to: {ver}.")
                vid = "{}.0".format(ver)
                logging.info("")

        else:
            logging.warning(
                f"-- Collection of {self.type} version set "
                f"to: {int(self.setup.release)}."
            )
            vid = "{}.0".format(int(self.setup.release))
            logging.info("")

        self.vid = vid
