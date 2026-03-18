"""Implementation of the PDS4 Miscellaneous Collection Class."""
import logging

from .collection import Collection


class MiscellaneousCollection(Collection):
    """Collection child class to generate a PDS4 Document Collection.

    :param setup: NPB execution setup object
    :type setup: object
    :param bundle: Bundle object
    :type bundle: object
    :param list: Kernel List object
    :type list: object
    """

    def __init__(self, setup: object, bundle: object, list: object) -> object:
        """Constructor."""
        if setup.pds_version == "4":
            self.type = "miscellaneous"
        else:
            self.type = "extras"

        #
        # Included for ORBNUM files observers and targets.
        #
        self.list = list

        Collection.__init__(self, self.type, setup, bundle)

    def report(self):
        """Report the Collection generation step."""
        line = f"Step {self.setup.step} - Generation of {self.type} collection"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")
