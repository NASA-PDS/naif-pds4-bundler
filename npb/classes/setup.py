import os
import os
import json
import glob
import logging
import datetime

from types import SimpleNamespace

from npb.utils.files import copy
from npb.utils.files import get_exe_dir

class Setup(object):

    def __init__(self, config, version, interact):

        step = 1
        logging.info('')
        logging.info(f'Step {step} - Setting up the archive generation')
        logging.info('------------------------------------------------')
        logging.info('')

        with open(config, 'r') as file:
            f = file.read().replace('\n', '')

        setup = json.loads(f, object_hook=lambda d: SimpleNamespace(**d))

        #
        #    *  Populate the setup object with attributes beyond the
        #       configuration file.
        #
        setup.root_dir    = os.path.dirname(__file__)[:-7]
        setup.step        = step + 1
        setup.version     = version
        setup.interactive = interact
        setup.today       = datetime.date.today().strftime("%Y%m%d")
        setup.exe_dir     = get_exe_dir()

        self.setup        = setup


    def get_increment(setup):

        #
        # PDS4 release increment (implies inventory and meta-kernel)
        #
        logging.info( '-- Checking existence of previous release' )

        try:
            releases = glob.glob(setup.final_directory + os.sep +
                                 setup.mission_accronym + '_spice' + os.sep +
                                 f'bundle_{setup.mission_accronym}_spice_v*')
            releases.sort()
            current_release = int(releases[-1].split('_spice_v')[-1].split('.')[0])
            current_release = f'{current_release:03}'
            release         = int(current_release) + 1
            release         = f'{release:03}'

            logging.info(f'     Generating release {release}')

            increment = True

        except:
            logging.warning('-- Bundle label not found. Checking previous kernel list')

            try:
                releases = glob.glob(setup.working_directory +
                                     f'/{setup.mission_accronym}_release_*.kernel_list')

                releases.sort()
                current_release = int(releases[-1].split('_release_')[-1].split('.')[0])
                current_release = f'{current_release:03}'
                release = int(current_release) + 1
                release = f'{release:03}'

                logging.info(f'     Generating release {release}')

                increment = True
            except:

                logging.warning('     This is the first release.')

                release = '001'
                current_release = ''

                increment = False


        setup.release         = release
        setup.current_release = current_release

        logging.info('')

        return increment