"""Implementation of the Product base class."""
import os

from ...utils import checksum_from_label
from ...utils import checksum_from_registry
from ...utils import creation_time
from ...utils import md5


class Product:
    """Class that defines a generic archive product (or file).

    Assigns value to the common attributes for all Products: file size,
    creation time and date, and file extension.

    Subclasses must call ``register()`` once the product file exists on disk.
    """

    # TODO: update this method to have path and setup as input arguments.
    #
    #   def __init__(self, path: str, setup) -> None:
    #       """Constructor. Initialises attributes derivable without I/O.
    #
    #       :param path:  Absolute path to the product file
    #       :param setup: NPB execution setup object
    #       """
    def __init__(self) -> None:
        """Constructor."""
        if hasattr(self.setup, "creation_date_time"):
            self.creation_time = self.setup.creation_date_time
        else:
            self.creation_time = creation_time(time_format=self.setup.date_format)

        self.creation_date = self.creation_time.split("T")[0]
        self.extension = self.path.split(os.sep)[-1].split(".")[-1]

        # These attributes will be assigned (computed) by the register method.
        self.checksum = None
        self._size = None

        # TODO: remove this call. It should be done by the subclasses instead.
        self.register()

    def register(self) -> None:
        """Finalize file-derived attributes and register the product.

        Must be called once the product file exists on disk. Reads file size,
        resolves or computes the checksum, and registers the file and checksum
        with the pipeline.
        """
        stat_info = os.stat(self.path)
        self._size = str(stat_info.st_size)

        #
        # If specified via configuration, try to obtain the checksum from a
        # checksum registry file, if not present, try to obtain it from the
        # label if the product is in the staging area. Otherwise, compute the
        # checksum.
        #
        # Checksums for checksum files are always re-calculated.
        #
        if self.__class__.__name__ != "ChecksumProduct":
            if self.setup.args.checksum:
                checksum = checksum_from_registry(
                    self.path, self.setup.working_directory
                )
                if not checksum:
                    checksum = checksum_from_label(self.path)
            else:
                checksum = ""
            if not checksum:
                checksum = str(md5(self.path))
        else:
            checksum = str(md5(self.path))

        self.checksum = checksum

        if self.new_product:

            if self.setup.pds_version == "4":
                archive_dir = f"{self.setup.mission_acronym}_spice/"
            else:
                archive_dir = f"{self.setup.volume_id}/"

            self.setup.add_file(self.path.split(archive_dir)[-1])
            self.setup.add_checksum(self.path, checksum)

    @property
    def size(self) -> str:
        """Returns the size of the product."""
        return self._size
