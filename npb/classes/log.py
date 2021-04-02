import os
import shutil
import socket
import logging
import spiceypy
import datetime

class Log(object):

    def __init__(self, setup, log_file=False, silent=False):

        self.setup = setup

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_format = '%(levelname)-8s %(module)-12s %(funcName)-20s %(message)s'

        if not silent:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            formatter = logging.Formatter(log_format)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        if log_file:

            log_file = setup.working_directory + os.sep + \
                       f'{self.setup.mission_accronym}_release_temp.log'

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
                        f'{self.setup.mission_accronym} run on '     \
                        f'{socket.gethostname()} started at '        \
                        f'{str(datetime.datetime.now())[:-7]}'
        logging.info(start_message)
        logging.info('='*len(start_message))
        logging.info('')

        return


    def stop(self):
        logging.info('')
        logging.info(f'naif-pd4-bundle-{self.setup.version} for {self.setup.mission_name} run on '
                     f'{socket.gethostname()} finished at '
                     f'{str(datetime.datetime.now())[:-7]}')
        logging.info('')
        logging.info('End of log.')

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

    raise Exception(error)

