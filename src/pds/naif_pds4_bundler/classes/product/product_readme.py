"""Implementation of the readme file product class."""
import logging
import os
import shutil

from .product import Product
from ...utils import add_carriage_return
from ...utils import md5
from ..label import BundlePDS4Label
from ..log import error_message
from ..object import Object


class ReadmeProduct(Product):
    """Class to generate the Readme Product.

    :param setup:  NPB execution setup object
    :param bundle: Bundle that contains the Readme Product
    """

    def __init__(self, setup, bundle) -> None:
        """Constructor."""
        line = f"Step {setup.step} - Generation of bundle products"
        logging.info("")
        logging.info(line)
        logging.info("-" * len(line))
        logging.info("")
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print("-- " + line.split(" - ")[-1] + ".")

        self.name = "readme.txt"
        self.bundle = bundle
        self.path = setup.staging_directory + os.sep + self.name
        self.setup = setup
        self.vid = bundle.vid
        # TODO: Remove Object from the following lines.
        self.collection = Object()
        self.collection.name = ""

        path = (
            self.setup.bundle_directory
            + f"/{self.setup.mission_acronym}_spice/readme.txt"
        )

        if os.path.exists(path):
            self.path = path
            logging.info("-- Readme file already exists in final area.")
            self.new_product = False
        else:
            logging.info("-- Generating readme file...")
            self.write_product()
            self.new_product = True

            #
            # If the product is generated we define a checksum attribute for
            # the Bundle object.
            #
            self.bundle.checksum = md5(self.path)

        super().__init__()

        logging.info("")

        #
        # Now we change the path for the difference of the name in the label
        #
        self.path = setup.staging_directory + os.sep + bundle.name

        logging.info("-- Generating bundle label...")
        self.label = BundlePDS4Label(setup, self)

    def write_product(self) -> None:
        """Write the Readme product."""
        line_length = 0

        #
        # If the readme file is provided via configuration copy it, otherwise
        # generate it with the template.
        #
        if (not os.path.isfile(self.path)) and ("input" in self.setup.readme):
            if os.path.exists(self.setup.readme["input"]):
                shutil.copy(self.setup.readme["input"], self.path)
            else:
                error_message("Readme file provided via configuration does not exist.")
        elif not os.path.isfile(self.path):
            with open(self.path, "w+") as f:
                with open(
                    self.setup.templates_directory + "/template_readme.txt", "r"
                ) as t:
                    for line in t:
                        if "$SPICE_NAME" in line:
                            line = line.replace("$SPICE_NAME", self.setup.spice_name)
                            line_length = len(line) - 1
                            line = add_carriage_return(
                                line, self.setup.eol_pds4, self.setup
                            )
                            f.write(line)
                        elif "$UNDERLINE" in line:
                            line = line.replace("$UNDERLINE", "=" * line_length)
                            line_length = len(line) - 1
                            line = add_carriage_return(
                                line, self.setup.eol_pds4, self.setup
                            )
                            f.write(line)
                        elif "$OVERVIEW" in line:
                            overview = self.setup.readme["overview"]
                            for line in overview.split("\n"):
                                line = " " * 3 + line.strip() + "\n"
                                line = add_carriage_return(
                                    line, self.setup.eol, self.setup
                                )
                                f.write(line)
                        elif "$COGNISANT_AUTHORITY" in line:
                            cognisant = self.setup.readme["cognisant_authority"]
                            for line in cognisant.split("\n"):
                                line = " " * 3 + line.strip() + "\n"
                                line = add_carriage_return(
                                    line, self.setup.eol, self.setup
                                )
                                f.write(line)
                        else:
                            line_length = len(line) - 1
                            line = add_carriage_return(line, self.setup.eol, self.setup)
                            f.write(line)

        logging.info("-- Created readme file.")
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("   * Created readme file.")
