"""Implementation of the PDS4 Miscellaneous Collection Class."""
import logging

from .collection import Collection


class MiscellaneousCollection(Collection):
    """Class to generate a PDS4 or PDS3 Document Collection.

    :param setup:   NPB execution setup object
    :param bundle:  Bundle object
    :param kernels: Kernel List object
    """

    def __init__(self, setup, bundle, kernels) -> None:
        """Constructor."""
        if setup.pds_version == "4":
            self.type = "miscellaneous"
        else:
            self.type = "extras"

        #
        # Included for OrbNum files observers and targets.
        #
        self.list = kernels

        super().__init__(self.type, setup, bundle)

    @property
    def kind(self) -> str:
        """Type of PDS Miscellaneous Collection.
        """
        return self.type

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
