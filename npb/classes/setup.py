import os
import re
import glob
import logging
import spiceypy
import datetime

from pathlib import Path
from xml.etree import cElementTree as ET

from npb.utils.files import etree_to_dict
from npb.classes.log import error_message


class Setup(object):

    def __init__(self, config, version, interact,
                 faucet, diff, release_date, start, finish):

        #
        # Converting XML setup file into a dictionary and then into
        # attributes for the object
        #
        config = Path(config).read_text()
        entries = etree_to_dict(ET.XML(config))

        #
        # Re-arrange the resulting dictionary into one-level attributes
        # adept to be used (as if we were loading a JSON file prior to
        # v0.5.0).
        #
        config = entries['naif-pds4-bundle_configuration']

        self.__dict__.update(config['pds_parameters'])
        self.__dict__.update(config['bundle_parameters'])
        self.__dict__.update(config['mission_parameters'])
        self.__dict__.update(config['directories'])

        #
        # Kernel list configuration needs refractoring.
        #
        self.__dict__.update(config['kernel_list'])

        kernel_list_config = {}
        for ker in self.kernel:
            kernel_list_config[ker['@pattern']] = ker

        self.kernel_list_config = kernel_list_config
        del self.kernel

        self.__dict__.update(config['meta-kernel'])

        #
        # Populate the setup object with attributes beyond the
        # configuration file.
        #
        self.root_dir           = os.path.dirname(__file__)[:-7]
        self.step               = 1
        self.version            = version
        self.interactive        = interact
        self.faucet             = faucet.lower()
        self.diff               = diff.lower()
        self.today              = datetime.date.today().strftime("%Y%m%d")
        self.increment_start    = start
        self.increment_finish   = finish

        #
        # If a release date is not specified it is set to today.
        #
        if not release_date:
            self.release_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            self.release_date = release_date

        #
        # Sort out if directories are provided as relative paths and
        # if so convert them in absolute for the execution
        #
        cwd = os.getcwd()

        os.chdir('/')

        if os.path.isdir(cwd + os.sep + self.working_directory):
            self.working_directory = cwd + os.sep + self.working_directory
        if not os.path.isdir(self.working_directory):
            error_message(f'Directory does not exist: {self.working_directory}')

        if os.path.isdir(cwd + os.sep + self.staging_directory):
            self.staging_directory = cwd + os.sep + self.staging_directory + f'/{self.mission_accronym}_spice'
        if not os.path.isdir(self.staging_directory):
            print(f'Creating missing directory: {self.staging_directory}')
            try:
                os.mkdir(self.staging_directory)
            except Exception as e:
                print(e)

        if os.path.isdir(cwd + os.sep + self.final_directory):
            self.final_directory = cwd + os.sep + self.final_directory
        if not os.path.isdir(self.final_directory):
            error_message(f'Directory does not exist: {self.final_directory}')

        if os.path.isdir(cwd + os.sep + self.kernels_directory):
            self.kernels_directory = cwd + os.sep + self.kernels_directory
        if not os.path.isdir(self.kernels_directory):
            error_message(f'Directory does not exist: {self.kernels_directory}')

        os.chdir(cwd)


    def set_release(self):

        line = f'Step {self.step} - self the archive generation'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.step += 1

        #
        # PDS4 release increment (implies inventory and meta-kernel)
        #
        logging.info( '-- Checking existence of previous release' )

        try:
            releases = glob.glob(self.final_directory + os.sep +
                                 self.mission_accronym + '_spice' + os.sep +
                                 f'bundle_{self.mission_accronym}_spice_v*')
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
                releases = glob.glob(self.working_directory +
                                     f'/{self.mission_accronym}_release_*.kernel_list')

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


        self.release         = release
        self.current_release = current_release

        logging.info('')

        if self.interactive:
            input(">> Press Enter to continue...")

        self.increment = increment

        return


    def load_kernels(self):

        logging.info('')
        line = f'Step {self.step} - Load LSK, PCK, FK and SCLK kernels'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.step += 1

        #
        # To get the appropriate kernels, use the meta-kernel grammar.
        # First extract the patterns for each kernel type of interest.
        #
        fk_patterns   = []
        sclk_patterns = []
        pck_patterns = []
        lsk_patterns  = []

        mk_grammar = self.root_dir + \
                     f'/config/{self.mission_accronym}_metakernel.grammar'
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
            lsk_pattern = [f for f in os.listdir(f'{self.kernels_directory}/lsk/') if re.search(pattern, f)]
            if lsk_pattern:
                if len(lsk_pattern) > 1: lsk_pattern.sort()
                lsk.append(lsk_pattern[-1])
                spiceypy.furnsh(f'{self.kernels_directory}/lsk/{lsk_pattern[-1]}')
        if not lsk:
            logging.error(f'-- LSK not found.')
        else:
            logging.info(f'-- LSK     loaded: {lsk}')
        if len(lsk) > 1:
            error_message('Only one LSK should be obtained.')



        pcks = []
        for pattern in pck_patterns:
            pcks_pattern = [f for f in os.listdir(f'{self.kernels_directory}/pck/') if re.search(pattern, f)]
            if pcks_pattern:
                if len(pcks_pattern) > 1: pcks_pattern.sort()
                spiceypy.furnsh(f'{self.kernels_directory}/fk/{pcks_pattern[-1]}')
                pcks.append(pcks_pattern[-1])
        if not pcks:
            logging.warning(f'-- PCK not found.')
        else: logging.info(f'-- PCK(s)   loaded: {pcks}')

        fks = []
        for pattern in fk_patterns:
            fks_pattern = [f for f in os.listdir(f'{self.kernels_directory}/fk/') if re.search(pattern, f)]
            if fks_pattern:
                if len(fks_pattern) > 1: fks_pattern.sort()
                spiceypy.furnsh(f'{self.kernels_directory}/fk/{fks_pattern[-1]}')
                fks.append(fks_pattern[-1])
        if not fks:
            logging.warning(f'-- FK not found.')
        else: logging.info(f'-- FK(s)   loaded: {fks}')

        sclks = []
        for pattern in sclk_patterns:
            sclks_pattern = [f for f in os.listdir(f'{self.kernels_directory}/sclk/') if re.search(pattern, f)]
            if sclks_pattern:
                if len(sclks_pattern) > 1: sclks_pattern.sort()
                sclks.append(sclks_pattern[-1])
                spiceypy.furnsh(f'{self.kernels_directory}/sclk/{sclks_pattern[-1]}')
        if not sclks:
            logging.error(f'-- SCLK not found.')
        else: logging.info(f'-- SCLK(s) loaded: {sclks}')



        logging.info('')

        self.fks   = fks
        self.sclks = sclks
        self.lsk   = lsk

        if self.interactive:
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
