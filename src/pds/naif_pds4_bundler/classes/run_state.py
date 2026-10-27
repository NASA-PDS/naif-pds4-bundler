"""Mutable state of a single pipeline execution."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# Setup is only needed for the type hints, so it is not imported at runtime.
if TYPE_CHECKING:
    from .product import Product
    from .setup import Setup


@dataclass
class RunState:
    """State that changes while the pipeline runs.

    Unlike ``Setup``, which holds the configuration and is not meant to change
    once resolved, this holds what the pipeline updates as it goes.

    :param step: Number of the next pipeline step to be logged.
    :param file_list: Files generated or moved during the run.
    :param checksum_registry: ``<path> <checksum>`` records of the run.
    """

    step: int = 1

    # Each instance needs its own lists; a plain '[]' default would be shared by
    # every RunState.
    file_list: list[str] = field(default_factory=list)
    checksum_registry: list[str] = field(default_factory=list)

    def add_file(self, file: str) -> None:
        """Add a file to the run by-product File List.

        :param file: Path of the file to be added, stored unchanged.
        """
        self.file_list.append(file)

    def register_label_file(self, path: str) -> None:
        """Add a label file to the run by-product File List.

        Every label is registered, whether its product is new.

        :param path: Path of the label relative to the staging directory,
            stored unchanged.
        """
        self.add_file(path)

    def add_checksum(self, path: str, checksum: str) -> None:
        """Add an entry to the run by-product Checksum Registry.

        :param path: Path of the file the checksum corresponds to.
        :param checksum: MD5 checksum of the file.
        """
        self.checksum_registry.append(f"{path} {checksum}")

    def register_product(self, product: Product) -> None:
        """Add a new product to the File List and the Checksum Registry.

        Products that are not new, or that never derived their file
        attributes, are skipped.

        :param product: Product whose file has been written and whose
            checksum is already resolved.
        """
        if not product.is_registrable:
            return

        self.add_file(str(product.archive_path))
        self.add_checksum(product.registered_path, product.checksum)

    def write_file_list(self, setup: Setup) -> None:
        """Write the run by-product File List in the working directory.

        Nothing is written, nor logged, if no file has been added.

        :param setup: Configuration providing the file name and location.
        """
        if self.file_list:

            # The name follows <acronym>_<run type>_<release>.file_list, with
            # the release zero-padded to two digits (e.g. maven_release_03).
            with open(
                setup.working_directory
                + os.sep
                + f"{setup.mission_acronym}_{setup.run_type}_"
                f"{int(setup.release):02d}.file_list",
                "w", encoding='utf-8'
            ) as out_file:

                # One file per line, in the order they were added.
                for file in self.file_list:
                    out_file.write(file + "\n")
            logging.info("-- Run File List file written in working area.")

    def write_checksum_registry(self, setup: Setup) -> None:
        """Write the run by-product Checksum Record in the working directory.

        Nothing is written, nor logged, if no checksum has been added.

        :param setup: Configuration providing the file name and location.
        """
        if self.checksum_registry:

            # Same naming as the File List, with the .checksum extension.
            with open(
                setup.working_directory
                + os.sep
                + f"{setup.mission_acronym}_{setup.run_type}_"
                f"{int(setup.release):02d}.checksum",
                "w", encoding='utf-8'
            ) as out_file:

                # One "<path> <checksum>" record per line, in insertion order.
                for element in self.checksum_registry:
                    out_file.write(element + "\n")
            logging.info(
                "-- Run Checksum Registry file written in working area.")
