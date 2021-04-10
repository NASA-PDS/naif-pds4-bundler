import os
import re
import json
import glob
import logging
import spiceypy
import datetime

from types import SimpleNamespace

from npb.classes.log import error_message


class Setup(object):

    def __init__(self, config, version, interact,
                 faucet, diff, start, finish):

        with open(config, 'r') as file:
            f = file.read().replace('\n', '')

        setup = json.loads(f, object_hook=lambda d: SimpleNamespace(**d))

        #
        # Populate the setup object with attributes beyond the
        # configuration file.
        #
        setup.root_dir        = os.path.dirname(__file__)[:-7]
        setup.step            = 1
        setup.version         = version
        setup.interactive     = interact
        setup.faucet          = faucet.lower()
        setup.diff            = diff.lower()
        setup.today           = datetime.date.today().strftime("%Y%m%d")
        setup.increment_start = start
        setup.increment_finish  = finish

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

        if os.path.isdir(cwd + os.sep + setup.kernels_directory):
            setup.kernels_directory = cwd + os.sep + setup.kernels_directory
        if not os.path.isdir(setup.kernels_directory):
            error_message(f'Directory does not exist: {setup.kernels_directory}')

        os.chdir(cwd)

        self.setup = setup


    def get_increment(setup):

        line = f'Step {setup.step} - Setup the archive generation'
        logging.info(line)
        logging.info('-'*len(line))
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

            logging.info(f'     Generating release {release}.')

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

        if setup.interactive:
            input(">> Press Enter to continue...")

        return increment


    def load_kernels(setup):

        logging.info('')
        line = f'Step {setup.step} - Load LSK, PCK, FK and SCLK kernels'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        setup.step += 1

        #
        # To get the appropriate kernels, use the meta-kernel grammar.
        # First extract the patterns for each kernel type of interest.
        #
        fk_patterns   = []
        sclk_patterns = []
        pck_patterns = []
        lsk_patterns  = []

        mk_grammar = setup.root_dir + \
                     f'/config/{setup.mission_accronym}_metakernel.grammar'
        with open(mk_grammar, 'r') as m:
            for line in m:
                if '.tf' in line.lower():
                    fk_patterns.append(line.strip())
                elif '.tsc' in line.lower():
                    sclk_patterns.append(line.strip())
                elif '.tpc' in line.lower():
                    sclk_patterns.append(line.strip())
                elif '.tls' in line.lower():
                    lsk_patterns.append(line.strip())

        #
        # Search the latest version for each pattern of each kernel type.
        #
        lsk = []
        for pattern in lsk_patterns:
            lsk_pattern = [f for f in os.listdir(f'{setup.kernels_directory}/lsk/') if re.search(pattern, f)]
            if lsk_pattern:
                if len(lsk_pattern) > 1: lsk_pattern.sort()
                lsk.append(lsk_pattern[-1])
                spiceypy.furnsh(f'{setup.kernels_directory}/lsk/{lsk_pattern[-1]}')
        if not lsk:
            logging.error(f'-- LSK not found.')
        else:
            logging.info(f'-- LSK     loaded: {lsk}')
        if len(lsk) > 1:
            error_message('Only one LSK should be obtained.')



        pcks = []
        for pattern in pck_patterns:
            pcks_pattern = [f for f in os.listdir(f'{setup.kernels_directory}/pck/') if re.search(pattern, f)]
            if pcks_pattern:
                if len(pcks_pattern) > 1: pcks_pattern.sort()
                spiceypy.furnsh(f'{setup.kernels_directory}/fk/{pcks_pattern[-1]}')
                pcks.append(pcks_pattern[-1])
        if not pcks:
            logging.warning(f'-- PCK not found.')
        else: logging.info(f'-- PCK(s)   loaded: {pcks}')

        fks = []
        for pattern in fk_patterns:
            fks_pattern = [f for f in os.listdir(f'{setup.kernels_directory}/fk/') if re.search(pattern, f)]
            if fks_pattern:
                if len(fks_pattern) > 1: fks_pattern.sort()
                spiceypy.furnsh(f'{setup.kernels_directory}/fk/{fks_pattern[-1]}')
                fks.append(fks_pattern[-1])
        if not fks:
            logging.warning(f'-- FK not found.')
        else: logging.info(f'-- FK(s)   loaded: {fks}')

        sclks = []
        for pattern in sclk_patterns:
            sclks_pattern = [f for f in os.listdir(f'{setup.kernels_directory}/sclk/') if re.search(pattern, f)]
            if sclks_pattern:
                if len(sclks_pattern) > 1: sclks_pattern.sort()
                sclks.append(sclks_pattern[-1])
                spiceypy.furnsh(f'{setup.kernels_directory}/sclk/{sclks_pattern[-1]}')
        if not sclks:
            logging.error(f'-- SCLK not found.')
        else: logging.info(f'-- SCLK(s) loaded: {sclks}')



        logging.info('')

        setup.fks   = fks
        setup.sclks = sclks
        setup.lsk   = lsk

        if setup.interactive:
            input(">> Press Enter to continue...")


    def check_times(self):

        try:
            et_msn_strt = spiceypy.utc2et(self.mission_start)
            et_inc_strt = spiceypy.utc2et(self.increment_start)
            et_inc_stop = spiceypy.utc2et(self.increment_finish)
            et_mis_stop = spiceypy.utc2et(self.mission_stop)
            logging.info('-- Provided dates are loadable with current setup.')

        except Exception as e:
            logging.error('-- Provided dates are not loadable with current setup.')
            error_message(e)

        if not (et_msn_strt <  et_inc_strt) or not \
               (et_inc_strt <= et_inc_stop) or not \
               (et_inc_stop <= et_mis_stop) or not \
               (et_msn_strt <  et_mis_stop):
            error_message('-- Provided dates are note correct. Check the archive coverage.')

        return
