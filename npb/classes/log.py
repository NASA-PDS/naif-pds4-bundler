import os
import socket
import logging
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
            log_file = setup.log_dir + os.sep + \
                       f'npd_{self.setup.mission_accronym}_{self.setup.today}.log'

            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            formatter = logging.Formatter(log_format)
            fh.setFormatter(formatter)
            logger.addHandler(fh)


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
        logging.info(f'naif-pd4-bundle-{self.setup.version} for {self.setup.mission_name} run on '
                     f'{socket.gethostname()} finished at '
                     f'{str(datetime.datetime.now())[:-7]}')
        logging.info('')
        logging.info('End of log.')

        return

def error_message(message):
    error = f'{message}.'
    logging.error(f'-- {message}')
    raise Exception(error)
