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
    """

    def __init__(self) -> None:
        """Constructor."""
        stat_info = os.stat(self.path)
        self.size = str(stat_info.st_size)

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

        if self.setup.pds_version == "4":
            archive_dir = f"{self.setup.mission_acronym}_spice/"
        else:
            archive_dir = f"{self.setup.volume_id}/"

        if hasattr(self.setup, "creation_date_time"):
            self.creation_time = self.setup.creation_date_time
        else:
            self.creation_time = creation_time(format=self.setup.date_format)

        self.creation_date = self.creation_time.split("T")[0]
        self.extension = self.path.split(os.sep)[-1].split(".")[-1]

        if self.new_product:
            self.setup.add_file(self.path.split(archive_dir)[-1])
            self.setup.add_checksum(self.path, checksum)
