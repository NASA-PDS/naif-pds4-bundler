"""Implementation of the Product base class."""
import os
import re
from typing import Tuple

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

    def get_mission_and_observer_and_target(self) -> Tuple[str, str, str]:
        """Read the configuration to extract the missions, observers and the
        targets.

        :return: missions and observers and targets
        :rtype: tuple
        """
        missions = []
        observers = []
        targets = []

        for pattern in self.collection.list.json_config.values():

            #
            # If the pattern is matched for the kernel name, extract
            # the target and observer from the kernel list
            # configuration.
            #
            if re.match(pattern["@pattern"], self.name):

                ker_config = self.setup.kernel_list_config[pattern["@pattern"]]

                #
                # Check if the kernel has specified missions.
                # Note the 'primary' mission will not be used in this case.
                #
                if "missions" in ker_config:
                    missions = ker_config["missions"]["mission_name"]
                #
                # If the kernel has no other missions then the primary mission
                # is used.
                #
                else:
                    missions = [self.setup.mission_name]

                #
                # Check if the kernel has specified targets.
                # Note that the mission target will not be used in this case.
                #
                if "targets" in ker_config:
                    targets = ker_config["targets"]["target"]
                #
                # If the kernel has no targets then the mission target is used.
                #
                else:
                    targets = [self.setup.target]

                #
                # Check if the kernel has specified observers.
                # Note that the mission observer will not be used in this case.
                #
                if "observers" in ker_config:
                    observers = ker_config["observers"]["observer"]
                #
                # If the kernel has no observers then the mission observer is
                # used.
                #
                else:
                    observers = [self.setup.observer]

                break
            #
            # If the product is not in the kernel list (such as the orbnum
            # file), then use the mission observers and targets.
            #
            else:
                missions = [self.setup.mission_name]
                observers = [self.setup.observer]
                targets = [self.setup.target]

        return missions, observers, targets
