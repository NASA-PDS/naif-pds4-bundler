"""Collection Class amd Child Classes Implementation."""
import glob
import logging
import re
from pathlib import Path
from typing import Tuple

from ...utils import find_latest_versioned_file


class Collection:
    """Class to generate a PDS4 Collection.

    :param c_type:   Collection type: kernels, documents or miscellaneous
    :param setup:  Setup object
    """
    list = None

    def __init__(self, c_type: str, setup, bundle) -> None:
        """Constructor."""
        self.bundle = bundle
        self.name = c_type
        self.product = []
        self.setup = setup
        self.vid = ''

        #
        # To know whether if the collection has been updated or not.
        #
        self.updated = False

        if setup.pds_version == "4":
            self.set_collection_lid()

    def add(self, element):
        """Add a Product to the Collection.

        :param element: Product to add to Collection
        """
        self.product.append(element)

        #
        # If an element has been added to the collection then, the collection
        # must be updated.
        #
        self.updated = True

    # TODO: This is probably not the right place for this method, but currently it is
    #       required by the SpiceKernelsCollection and the MiscellaneousCollection.
    #       Further analysis is required to see if it can be removed from the
    #       MiscellaneousCollection class.
    #       NOTE: the "list" class attribute defined in this class will be set to the
    #             appropriated value by the SpiceKernelsCollection and MiscellaneousCollection
    #             init methods. In any other cases, this method is not called, making the
    #             list attribute irrelevant for the DocumentCollection class.
    def get_mission_and_observer_and_target(self, name: str) -> Tuple[str, str, str]:
        """Read the configuration to extract the missions, observers and the
        targets.

        :param name: The name of the kernel or OrbNum file.
        :return: missions and observers and targets
        """
        missions = []
        observers = []
        targets = []

        for pattern in self.list.json_config.values():

            #
            # If the pattern is matched for the kernel name, extract
            # the target and observer from the kernel list
            # configuration.
            #
            if re.match(pattern["@pattern"], name):

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
            missions = [self.setup.mission_name]
            observers = [self.setup.observer]
            targets = [self.setup.target]

        return missions, observers, targets

    def set_collection_lid(self):
        """Set the Bundle LID."""
        if self.setup.pds_version != "3":
            self.lid = f"{self.setup.logical_identifier}:{self.type}"

    def set_collection_vid(self):
        """Set the Bundle VID.

        In general Collection versions are not equal to the release number.
        If the collection has been updated we obtain the increased version, but
        if it has not been updated we use the previous version.

        Given the case that he version cannot be determined: if it is the SPICE
        kernels collection assume is the same version as the bundle, otherwise
        we set it to 1.
        """
        if self.setup.increment:

            # Glob both directories ourselves and hand the resolved paths to
            # find_latest_versioned_file, which just picks the best one.
            candidate_patterns = [
                f"{self.setup.bundle_directory}/"
                f"{self.setup.mission_acronym}_spice/"
                f"{self.name}/*{self.name}*",

                f"{self.setup.staging_directory}/{self.name}/*{self.name}*"
            ]
            candidates = [
                Path(match)
                for pattern in candidate_patterns
                for match in glob.glob(pattern)
            ]
            latest_file, latest_version = find_latest_versioned_file(candidates)

            # latest_version is None either when no file matched, or when a file
            # matched but its name didn't parse as expected.
            if latest_file is not None and latest_version is not None:

                # A collection that hasn't changed keeps its previous version;
                # only an updated collection bumps it.
                version = latest_version + 1 if self.updated else latest_version

                vid = f'{version}.0'

                logging.info(
                    '-- Collection of %s version set to %s, derived from:',
                    self.type, version)
                logging.info('   %s', latest_file)
                logging.info('')

            else:

                # No usable previous version found: fall back to the bundle
                # release number for the SPICE kernels collection (it always
                # tracks the release), or to 1 for any other collection.
                if self.name == "spice_kernels":
                    ver = int(self.setup.release)

                else:
                    ver = 1

                logging.warning(
                    '-- No %s collection available in previous increment.',
                    self.type)
                logging.warning('-- Collection of %s version set to: %d.',
                                self.type, ver)

                vid = f'{ver}.0'
                logging.info("")

        else:
            logging.warning('-- Collection of %s version set to: %d.',
                            self.type, int(self.setup.release))

            vid = f'{int(self.setup.release)}.0'
            logging.info('')

        self.vid = vid
