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

    def __init__(self, args, version):

        #
        # Converting XML setup file into a dictionary and then into
        # attributes for the object
        #
        config = Path(args.config).read_text()
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
        self.args               = args
        self.interactive        = args.interactive
        self.faucet             = args.faucet.lower()
        self.diff               = args.diff.lower()
        self.today              = datetime.date.today().strftime("%Y%m%d")

        #
        # Check of optional input
        #
        # If a release date is not specified it is set to today.
        #
        if not self.release_date:
            self.release_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
            if not pattern.match(self.release_date):
                error_message('release_date parameter does not match the required format: YYYY-MM-DD.')

        #
        # Increment (Bundle) start and finish times.
        #

        if self.increment_start:
            pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
            if not pattern.match(self.increment_start):
                error_message('increment_start parameter does not match the required format: YYYY-MM-DDThh:mm:ssZ.')
        if self.increment_finish:
            pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
            if not pattern.match(self.increment_finish):
                error_message('increment_finish does not match the required format: YYYY-MM-DDThh:mm:ssZ.')

        if ((not self.increment_start) and (self.increment_finish)) or ((self.increment_start) and (not self.increment_finish)):
            error_message('If provided via configuration, increment_start and increment_finish parameters need to be provided together.')

        #
        # Fill PDS4 missing fields,
        #
        if self.pds_version == '4':
            self.producer_phone = ''
            self.producer_email = ''
            self.dataset_id     = ''
            self.volume_id      = ''

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
        elif not os.path.isdir(self.staging_directory):
            print(f'Creating missing directory: {self.staging_directory}/{self.mission_accronym}_spice')
            try:
                os.mkdir(self.staging_directory)
            except Exception as e:
                print(e)
        elif f'/{self.mission_accronym}_spice' not in self.staging_directory:
            self.staging_directory += f'/{self.mission_accronym}_spice'

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

        line = f'Step {self.step} - Setup the archive generation'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.step += 1
        if not self.args.silent and not self.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

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

        line = f'Step {self.step} - Load LSK, PCK, FK and SCLK kernels'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.step += 1
        if not self.args.silent and not self.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        #
        # To get the appropriate kernels, use the meta-kernel grammar.
        # First extract the patterns for each kernel type of interest.
        #
        fk_patterns   = []
        sclk_patterns = []
        pck_patterns = []
        lsk_patterns  = []

        for pattern in self.mk_grammar['pattern']:
            if '.tf' in pattern.lower():
                fk_patterns.append(pattern.strip())
            elif '.tsc' in pattern.lower():
                sclk_patterns.append(pattern.strip())
            elif '.tpc' in pattern.lower():
                sclk_patterns.append(pattern.strip())
            elif '.tls' in pattern.lower():
                lsk_patterns.append(pattern.strip())

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
