import datetime
import logging
import os
import platform
import shutil
import socket

import spiceypy


class Log(object):
    """Class that parses and processes the NPB XML configuration file
    and makes it available to all other classes.

    :param args: Parameters arguments from NDT's main function.
    :param version: NDT version.
    """

    def __init__(self, setup, args):
        """
        Constructor method.
        """
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
                + f"{setup.mission_acronym}_release_temp.log"
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

    def start(self):
        """

        :return:
        """
        start_message = (
            f"naif-pds4-bundle-{self.setup.version} for " f"{self.setup.mission_name}"
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

        logging.info("")

        return

    def stop(self):
        """

        :return:
        """
        stop_message = f"Execution finished at " f"{str(datetime.datetime.now())[:-7]}"
        logging.info("")
        logging.info(stop_message)
        logging.info("")
        logging.info("End of log.")
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(stop_message)
            print("")

        #
        # Rename the log file according to the version.
        #
        if self.log_file:
            shutil.move(
                self.log_file,
                self.log_file.replace("temp", f"{int(self.setup.release):02d}"),
            )

        #
        # Generate the file list and the checksum regsitry.
        #
        self.setup.write_file_list()
        self.setup.write_checksum_regsitry()

        #
        # Clear the kernel pool
        #
        spiceypy.kclear()

        return


def error_message(message, setup=False):
    """

    :param message:
    """
    error = f"{message}."
    logging.error(f"-- {message}.")

    #
    # If files have been generated in the staging are and/or transfered
    # to the final area, generate the file list for the pipeline execution.
    #
    # In addition, generate the checksum registry file
    #
    if setup:
        setup.write_file_list()
        setup.write_checksum_regsitry()

    spiceypy.kclear()

    raise RuntimeError(error)
