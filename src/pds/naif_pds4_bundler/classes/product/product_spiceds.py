"""Implementation of the SPICE DS file product class."""
import difflib
import filecmp
import glob
import logging
import os
import shutil
from datetime import date

from .product import Product
from ...pipeline.runtime import handle_npb_error
from ...utils import add_carriage_return
from ...utils import compare_files
from ..label import DocumentPDS4Label


class SpicedsProduct(Product):
    """Class to process the SPICEDS file.

    :param setup:      NPB execution setup object
    :param collection: Collection that the inventory product belongs to
    """

    def __init__(self, setup, collection) -> None:
        """Constructor."""
        self.setup = setup
        self.collection = collection
        self.new_product = True
        try:
            spiceds = self.setup.spiceds
        except BaseException:
            spiceds = ""

        if not spiceds:
            logging.info("-- No spiceds file provided.")

        #
        # Obtain the previous spiceds file if it exists
        #
        path = (
            setup.bundle_directory
            + os.sep
            + setup.mission_acronym
            + "_spice"
            + os.sep
            + collection.name
        )
        if self.setup.increment:
            spiceds_files = glob.glob(path + os.sep + "spiceds_v*.html")
            spiceds_files.sort()
            try:
                latest_spiceds = spiceds_files[-1]
                latest_version = latest_spiceds.split("_v")[-1].split(".")[0]
                self.latest_spiceds = latest_spiceds
                self.latest_version = latest_version
                self.version = int(latest_version) + 1

                if not spiceds:
                    logging.info(f"-- Previous spiceds found: {latest_spiceds}")
                    self.generated = False
                    return

            except BaseException:
                logging.warning("-- No previous version of spiceds_v*.html file found.")
                if not spiceds:
                    handle_npb_error(
                        "spiceds not provided and not available "
                        "from previous releases.",
                        setup=self.setup,
                    )
                self.version = 1
                self.latest_spiceds = ""
        else:
            self.version = 1
            self.latest_spiceds = ""
            if not spiceds:
                handle_npb_error(
                    "spiceds not provided and not available from previous releases.",
                    setup=self.setup,
                )

        #
        # Compare the previous SPICEDS file and the provided one. A user might
        # not remove a previously provided SPICEDS file from the configuration
        # file, if so, the user must be warned.
        #
        self.name = "spiceds_v{0:0=3d}.html".format(self.version)
        self.path = (
            setup.staging_directory + os.sep + collection.name + os.sep + self.name
        )
        self.mission = setup

        self.set_product_lid()
        self.set_product_vid()

        logging.info(
            f"-- spiceds file provided as input moved to staging "
            f"area as {self.name}"
        )

        #
        # The provided spiceds file is moved to the staging area.
        #
        shutil.copy2(spiceds, self.path)

        #
        # The appropriate line endings are provided to the spiceds file,
        # If line endings did not have Carriage Return (CR), they are
        # added and the file timestamp is updated. Note that if the file
        # already had CRs the original timestamp is preserved.
        #
        self._check_cr()

        #
        # Kernels are already generated products but Inventories are not.
        #
        self.new_product = True
        super().__init__()

        #
        # Check if the spiceds has not changed.
        #
        self.generated = self._check_product()

        #
        # Validate the product by comparing it and then generate the label.
        #
        if self.generated:
            if self.setup.diff:
                self._compare()

            self.label = DocumentPDS4Label(setup, collection, self)

    def set_product_lid(self) -> None:
        """Set the Product LID."""
        self.lid = f"{self.setup.logical_identifier}:document:spiceds".lower()

    def set_product_vid(self) -> None:
        """Set the Product VID."""
        self.vid = "{}.0".format(int(self.version))

    def _check_cr(self) -> None:
        """Determine whether if ``<CR>`` has to be added to the SPICEDS."""
        #
        # We add the date to the temporary file to have a unique name.
        #
        today = date.today()
        time_string = today.strftime("%Y-%m-%dT%H:%M:%S.%f")
        temporary_file = f"{self.path}.{time_string}"

        with open(self.path, "r") as s:
            with open(temporary_file, "w+") as t:
                for line in s:
                    line = add_carriage_return(line, self.setup.eol_pds4, self.setup)
                    t.write(line)

        #
        # If CRs have been added then we update the spiceds file.
        # The operator is notified.
        #
        if filecmp.cmp(temporary_file, self.path):
            os.remove(temporary_file)
        else:
            shutil.move(temporary_file, self.path)
            logging.info(
                "-- Carriage Return has been added to lines in the spiceds file."
            )

    def _check_product(self) -> bool:
        """Check if the SPICEDS product needs to be generated.

        :return: True if the SPICEDS products needs to be generated, False otherwise
        """
        #
        # If the previous spiceds document is the same then it does not
        # need to be generated.
        #
        generate_spiceds = True
        if self.latest_spiceds:
            with open(self.path) as f:
                spiceds_current = f.readlines()
            with open(self.latest_spiceds) as f:
                spiceds_latest = f.readlines()

            differ = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
            diff = list(differ.compare(spiceds_current, spiceds_latest))

            generate_spiceds = False
            for line in diff:
                if line[0] == "-":
                    if (
                        "Last update" not in line
                        and line.strip() != "-"
                        and line.strip() != "-\n"
                    ):
                        generate_spiceds = True

            if not generate_spiceds:
                os.remove(self.path)
                logging.warning("-- spiceds document does not need to be updated.")
                logging.warning("")

        return generate_spiceds

    def _compare(self) -> None:
        """**Compare the SPICEDS Product with another SPICEDS**.

        The SPICEDS Product is compared with the previous
        version and if it does not exist with the sample INSIGHT SPICEDS
        product.
        """
        #
        # Compare spiceds with latest. First try with previous increment.
        #
        try:

            val_spd_path = (
                f"{self.setup.bundle_directory}/"
                f"{self.setup.mission_acronym}_spice/document"
            )

            val_spds = glob.glob(f"{val_spd_path}/spiceds_v*.html")
            val_spds.sort()
            val_spd = val_spds[-1]

        except BaseException:

            #
            # If previous increment does not work, compare with InSight
            # example.
            #
            logging.warning(f"-- No other version of {self.name} has been found.")
            logging.warning("-- Comparing with default InSight example.")

            val_spd = (
                f"{self.setup.root_dir}/data/insight_spice/document/spiceds_v002.html"
            )

        logging.info("")
        fromfile = val_spd
        tofile = self.path
        work_dir = self.setup.working_directory

        compare_files(fromfile, tofile, work_dir, self.setup.diff)
