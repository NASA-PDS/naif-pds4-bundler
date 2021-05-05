import os
import shutil
import socket
import logging
import spiceypy
import datetime

class Log(object):

    def __init__(self, setup, args, debug = True):

        self.setup = setup
        self.args = args

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        if debug:
            log_format = '%(module)-12s %(funcName)-23s || %(levelname)-8s: %(message)s'
        else:
            log_format = '%(levelname)-8s: %(message)s'

        if args.verbose:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(log_format)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        if args.log:

            log_file = setup.working_directory + os.sep + \
                       f'{setup.mission_accronym}_release_temp.log'

            if os.path.exists(log_file):
                os.remove(log_file)

            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter(log_format)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            self.log_file = log_file
        else:
            self.log_file = ''


    def start(self):
        start_message = f'naif-pd4-bundle-{self.setup.version} for ' \
                        f'{self.setup.mission_name} run on '     \
                        f'{socket.gethostname()} started  at '        \
                        f'{str(datetime.datetime.now())[:-7]}'
        logging.info(start_message)
        logging.info('='*len(start_message))
        logging.info('')
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(start_message + '\n'  + '=' * len(start_message))

        #
        # Display the arguments
        #
        logging.info('-- The following arguments have been provided:')
        argument_dict = self.args.__dict__
        whitespaces = len(max(argument_dict.keys(), key=len))

        for attribute in argument_dict:
            if argument_dict[attribute]:
                logging.info(f'     {attribute}: {" "*(whitespaces-len(attribute))}{argument_dict[attribute]}')

        logging.info('')

        return


    def stop(self):
        stop_message = f'naif-pd4-bundle-{self.setup.version} for {self.setup.mission_name} run on ' \
                       f'{socket.gethostname()} finished at '                                        \
                       f'{str(datetime.datetime.now())[:-7]}'
        logging.info('')
        logging.info('')
        logging.info(stop_message)
        logging.info('')
        logging.info('End of log.')
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('=' * len(stop_message))
            print(stop_message)

        #
        # Rename the log file according to the version
        #
        if self.log_file:
            shutil.move(self.log_file, self.log_file.replace('temp', f'{int(self.setup.release):02d}'))

        #
        # Clear the kernel pool
        #
        spiceypy.kclear()

        return


def error_message(message):

    error = f'{message}.'
    logging.error(f'-- {message}')

    spiceypy.kclear()

    raise RuntimeError(error)

