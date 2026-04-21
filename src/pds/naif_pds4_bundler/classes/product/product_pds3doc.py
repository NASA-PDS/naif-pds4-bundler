"""Implementation of the PDS3 Document product class."""
import logging
import os

from .product import Product
from ...utils import compare_files
from ...utils import string_in_file


class PDS3DocumentProduct(Product):
    """Class that represents a PDS3 Document Product.

    :param setup: NPB execution setup object
    :param path:  PDS3 Document path
    """

    def __init__(self, setup, path: str) -> None:
        """Constructor."""
        self.path = path
        self.setup = setup
        self.name = path.split(os.sep)[-1]

        #
        # Compare with the already existing file -that has the same name-, if
        # files are the same do not include as an updated file.
        #
        existing_path = (
            self.setup.bundle_directory
            + os.sep
            + self.setup.volume_id
            + path.split(self.setup.volume_id)[-1]
        )

        same_files = compare_files(
            existing_path, path, self.setup.working_directory, self.setup.diff
        )
        if not same_files:
            self.new_product = False
        else:
            self.new_product = True

            self._validate()

        super().__init__()

    def _validate(self) -> None:
        """Try to validate the PDS3 document.

        The outcome of the validation is an INFO or a WARNING log message.
        """
        if self.name == "release.cat":
            release_strings = [
                f'RELEASE_ID                      = "0{self.setup.release}"',
                f"RELEASE_DATE                    = {self.setup.release_date}",
                f'RELEASE_PARAMETER_TEXT          = "&RELEASE_ID=0{self.setup.release}"',
            ]
        else:
            release_strings = [self.setup.release_date]

        for string in release_strings:
            logging.info("")
            present = string_in_file(self.path, string)
            if not present:
                logging.warning('-- The following string:')
                logging.warning('   %s', string)
                logging.warning('   Is not present in: %s', self.name)

            else:
                logging.info('-- The following string:')
                logging.info('   %s', string)
                logging.info('   Is present in: %s', self.name)

        logging.info("")
