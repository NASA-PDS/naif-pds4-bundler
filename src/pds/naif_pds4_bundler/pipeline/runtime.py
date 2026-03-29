from __future__ import annotations
import logging
import os
from typing import Optional, TYPE_CHECKING

import spiceypy

if TYPE_CHECKING:
    from ..classes.setup import Setup
    from ..classes.log import Log


def finish_execution(setup: Setup, log_manager: Log) -> None:
    """Coordinator function for the 'stop' sequence."""

    # Business Logic: Cleanup Templates
    for template in setup.template_files:
        if os.path.exists(template):
            os.remove(template)

    step_message = f"Step {setup.step} - Generate run by-product files"
    logging.info("")
    logging.info(step_message)
    logging.info("-" * len(step_message))
    logging.info("")
    setup.step += 1
    if not setup.args.silent and not setup.args.verbose:
        print("-- " + step_message.split(" - ")[-1] + ".")

    # Business Logic: Generate Artifacts
    #
    # Write the run-by product file list and checksum record
    setup.write_file_list()
    setup.write_checksum_registry()

    # The validate file is not generated for an NPB clear run.
    if setup.pds_version == "4" and setup.args.faucet != "clear":
        setup.write_validate_config()

    # Clear the kernel pool
    spiceypy.kclear()

    # Logging Finalization
    log_manager.stop()


def handle_npb_error(message: str, setup: Optional[Setup] = None) -> None:
    """Signal a NPB error and write run artifacts.

    Side effects:
        - Writes file list and checksum registry if setup is provided
        - Removes template files
        - Clears SPICE kernel pool
        - Raises RuntimeError

    :param message: Error message
    :param setup:   Optional Setup object for writing artifacts

    :raises RuntimeError: always, with the provided error message.
    """
    logging.error(f"-- {message}")

    # If files have been generated in the staging area and/or transferred
    # to the final area, generate the file list for the pipeline execution.
    #
    # In addition, generate the checksum registry file
    if setup:
        setup.write_file_list()
        setup.write_checksum_registry()

        # Remove the templates. Make sure they exist before attempting the
        # deletion.
        for template in setup.template_files:
            if os.path.exists(template):
                os.remove(template)

    # Clear the kernel pool.
    spiceypy.kclear()

    raise RuntimeError(message)
