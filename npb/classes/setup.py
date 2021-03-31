import os
import json
import glob
import logging
import datetime

from types import SimpleNamespace

from npb.classes.log import error_message


class Setup(object):

    def __init__(self, config, version, interact):

        with open(config, 'r') as file:
            f = file.read().replace('\n', '')

        setup = json.loads(f, object_hook=lambda d: SimpleNamespace(**d))

        #
        # Populate the setup object with attributes beyond the
        # configuration file.
        #
        setup.root_dir    = os.path.dirname(__file__)[:-7]
        setup.step        = 1
        setup.version     = version
        setup.interactive = interact
        setup.today       = datetime.date.today().strftime("%Y%m%d")

        #
        # Sort out if directories are provided as relative paths and
        # if so convert them in absolute for the execution
        #
        cwd = os.getcwd()

        os.chdir('/')

        if os.path.isdir(cwd + os.sep + setup.working_directory):
            setup.working_directory = cwd + os.sep + setup.working_directory
        if not os.path.isdir(setup.working_directory):
            error_message(f'Directory does not exist: {setup.working_directory}')

        if os.path.isdir(cwd + os.sep + setup.staging_directory):
            setup.staging_directory = cwd + os.sep + setup.staging_directory + f'/{setup.mission_accronym}_spice'
        if not os.path.isdir(setup.staging_directory):
            print(f'Creating missing directory: {setup.staging_directory}')
            try:
                os.mkdir(setup.staging_directory)
            except Exception as e:
                print(e)

        if os.path.isdir(cwd + os.sep + setup.final_directory):
            setup.final_directory = cwd + os.sep + setup.final_directory
        if not os.path.isdir(setup.final_directory):
            error_message(f'Directory does not exist: {setup.final_directory}')

        if os.path.isdir(cwd + os.sep + setup.kernel_directory):
            setup.kernel_directory = cwd + os.sep + setup.kernel_directory
        if not os.path.isdir(setup.kernel_directory):
            error_message(f'Directory does not exist: {setup.kernel_directory}')

        os.chdir(cwd)

        self.setup = setup


    def get_increment(setup):


        logging.info(f'Step {setup.step} - Setting up the archive generation')
        logging.info('------------------------------------------------')
        logging.info('')
        setup.step += 1

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