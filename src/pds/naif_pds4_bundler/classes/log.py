"""Log Class Implementation."""
import datetime
import logging
import os
import platform
import shutil
import socket

import spiceypy

from ..utils.types.datatypes import PipelineArgs


class Log:
    """Log class to write and output NPB's log.

    :param setup: Setup object from NPB's main function.
    :param args:  Command line arguments from NPB's main function.
    """

    def __init__(self, setup: "Setup", args: PipelineArgs) -> None:
        """Constructor."""
        self.setup = setup
        self.args = args

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        if args.debug:
            log_format = (
                "%(module)-12s %(funcName)-23s || " "%(levelname)-8s: %(message)s"
            )
        else:
            log_format = "%(levelname)-8s: %(message)s"

        ch = logging.StreamHandler()

        if not args.silent and args.verbose:
            ch.setLevel(logging.INFO)
        else:
            ch.setLevel(logging.CRITICAL)

        formatter = logging.Formatter(log_format)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        if args.log:

            log_file = (
                setup.working_directory
                + os.sep
                + f"{setup.mission_acronym}_{setup.run_type}_temp.log"
            )

            if os.path.exists(log_file):
                os.remove(log_file)

            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            self.log_file = log_file
        else:
            self.log_file = ""

    def start(self) -> None:
        """Start the generation of the log for the execution."""
        start_message = (
            f"naif-pds4-bundler-{self.setup.version} for {self.setup.mission_name}"
        )
        exec_message = (
            "-- Executed on "
            f"{socket.gethostname()} at "
            f"{str(datetime.datetime.now())[:-7]}"
        )
        logging.info("")
        logging.info(start_message)
        logging.info("=" * len(start_message))
        logging.info("")
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("")
            print(start_message + "\n" + "=" * len(start_message))
            print(exec_message)

        #
        # Display execution platform and time.
        #
        logging.info(exec_message)
        logging.info(f"-- Platform: {platform.platform()}")
        logging.info(
            f"-- Python version: {platform.python_version()} "
            f"(Build: {platform.python_build()[1]})"
        )

        #
        # Display the arguments
        #
        logging.info("")
        logging.info("-- The following arguments have been provided:")
        argument_dict = self.args.__dict__
        whitespaces = len(max(argument_dict.keys(), key=len))

        for attribute in argument_dict:
            if argument_dict[attribute]:
                logging.info(
                    f"     {attribute}: "
                    f'{" " * (whitespaces - len(attribute))}'
                    f"{argument_dict[attribute]}"
                )

        if self.args.faucet == "labels":
            logging.info(
                "-- Running in labeling mode. Only label products are generated."
            )

        logging.info("")

    def stop(self) -> None:
        """Write log, file list, and checksum registry files when NPB stops.

        Side effects:
            - Removes template files
            - Writes the run-by product file list and checksum record
            - Writes a PDS validate tool configuration file, if applicable
            - Clears SPICE kernel pool
            - Renames the temporary log file
        """
        # Remove the templates. Make sure they exist before attempting the
        # deletion.
        for template in self.setup.template_files:
            if os.path.exists(template):
                os.remove(template)

        #
        # Generate the file list, the checksum registry, and the PDS validate
        # configuration file.
        #
        step_message = f"Step {self.setup.step} - Generate run by-product files"
        logging.info("")
        logging.info(step_message)
        logging.info("-" * len(step_message))
        logging.info("")
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print("-- " + step_message.split(" - ")[-1] + ".")

        self.setup.write_file_list()
        self.setup.write_checksum_registry()

        #
        # The validate file is not generated for an NPB clear run.
        #
        if self.setup.pds_version == "4" and self.setup.args.faucet != "clear":
            self.setup.write_validate_config()

        #
        # Clear the kernel pool
        #
        spiceypy.kclear()

        stop_message = f"Execution finished at {str(datetime.datetime.now())[:-7]}"
        logging.info("")
        logging.info(stop_message)
        logging.info("")
        logging.info("End of log.")
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(stop_message)
            print("")

        # Rename the log file according to the version.
        self._rename_log_file()

    def _rename_log_file(self) -> None:
        """Rename temporary log file according to release version."""
        if self.log_file:
            shutil.move(
                self.log_file,
                self.log_file.replace("temp", f"{int(self.setup.release):02d}"),
            )
