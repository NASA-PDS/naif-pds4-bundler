import logging
import os
from typing import Optional

import spiceypy


def handle_npb_error(message: str, setup: Optional["Setup"] = None) -> None:
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
