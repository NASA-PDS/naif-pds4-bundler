"""Implementation of the Product base class."""
import os
from pathlib import Path

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

        checksum = self._compute_checksum()

        self.checksum = checksum

        if self.new_product:

            if self.setup.pds_version == "4":
                archive_dir = f"{self.setup.mission_acronym}_spice"
            else:
                archive_dir = self.setup.volume_id

            path = Path(self.path)
            archive_dir_index = path.parts.index(archive_dir)
            archive_path = Path(*path.parts[archive_dir_index + 1:])

            self.setup.add_file(str(archive_path))
            self.setup.add_checksum(self.path, checksum)

    def _compute_checksum(self) -> str:
        """Resolve the product checksum.

        If specified via configuration, try to obtain it from a checksum
        registry file and, if not present, from the label (if the product is
        in the staging area). Otherwise, compute it directly. Subclasses
        override this when the checksum must always be recomputed.
        """
        # Reusing a known checksum only makes sense if the user asked for it.
        if self.setup.args.checksum:
            checksum = checksum_from_registry(
                self.path, self.setup.working_directory
            )

            # The registry may not know the file, so fall back to its label.
            if not checksum:
                checksum = checksum_from_label(self.path)

            # Either lookup can come back empty (or None), so only return
            # here when one of them really found something.
            if checksum:
                return checksum

        # Last resort. It never comes back empty, so a checksum is always
        # returned, and it is also the only path taken when reuse is off.
        return str(md5(self.path))

    @property
    def size(self) -> str:
        """Returns the size of the product."""
        return self._size
