import os
import glob
import logging
import shutil
import difflib
import fileinput
import spiceypy
import subprocess

import numpy as np

from npb.classes.label import SpiceKernelPDS4Label
from npb.classes.label import MetaKernelPDS4Label
from npb.classes.label import InventoryPDS4Label
from npb.classes.label import InventoryPDS3Label
from npb.classes.label import DocumentPDS4Label
from npb.classes.label import BundlePDS4Label

from npb.classes.log   import error_message
from npb.utils.time    import creation_time
from npb.utils.time    import creation_date
from npb.utils.time    import current_date
from npb.utils.files   import md5
from npb.utils.files   import add_carriage_return
from npb.utils.files   import add_crs_to_file
from npb.utils.files   import extension2type
from npb.utils.files   import safe_make_directory
from npb.utils.files   import mk2list
from npb.utils.files   import get_latest_kernel
from npb.utils.files   import type2extension
from npb.utils.files   import compare_files

from collections import OrderedDict


class Product(object):
    
    def __init__(self):

        stat_info          = os.stat(self.path)
        self.size          = str(stat_info.st_size)
        self.checksum      = str(md5(self.path))
        self.creation_time = creation_time(self.path)[:-5]
        self.creation_date = creation_date(self.path)

    #
    # Obtain the product (kernel or mk) description information
    #
    def get_description(self):

        kernel_list_file = self.setup.working_directory + os.sep + \
                           f'{self.setup.mission_accronym}_release_' \
                           f'{int(self.setup.release):02d}.kernel_list'

        get_descr   = False
        description = False

        for line in fileinput.input(kernel_list_file):
            if self.name in line:
                get_descr = True
            if  get_descr and 'DESCRIPTION' in line:
                description = line.split('=')[-1].strip()
                get_descr = False

        if not description:
            error_message(f'{self.name} does not have '
                          f'a description on {kernel_list_file}')

        return description


class SpiceKernelProduct(Product):

    def __init__(self, setup, name, collection):

        self.collection = collection
        self.setup      = setup
        self.name       = name
        self.extension  = name.split('.')[-1].strip()
        self.type       = extension2type(self)


        self.path      = setup.kernels_directory + os.sep + self.type


        if self.extension[0].lower() == 'b':
            self.file_format = 'Binary'
        else:
            self.file_format = 'Character'


        self.coverage()

        if setup.pds == '3':
            print('HOLD IT')


        self.description = self.get_description()

        self.collection_path = setup.staging_directory + os.sep + \
                       'spice_kernels' + os.sep

        product_path = self.collection_path + self.type + os.sep

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # We generate the kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # We copy the kernel to the staging directory.
        #
        logging.info('')
        logging.info(f'-- Copying  {self.name} to staging directory.')
        if not os.path.isfile(product_path + self.name):
            try:
                shutil.copy2(self.path + os.sep + self.name,
                             product_path + os.sep + self.name)
                self.new_product = True
            except:
                error_message(f'{self.name} not present in {self.path}')
        else:
            logging.error('     {} already present in staging directory'.format(self.name))

            if self.setup.interactive:
                input(">> Press Enter to continue...")

            self.new_product = False
            return

        #
        # We update the path after having copied the kernel.
        #
        self.path = product_path + self.name


        Product.__init__(self)

        #
        # The kernel is labeled.
        #
        logging.info(f'-- Labeling {self.name}')
        self.label = SpiceKernelPDS4Label(setup, self)


        return


    def product_lid(self):

        product_lid = \
            'urn:nasa:pds:{}.spice:spice_kernels:{}_{}'.format(
                    self.setup.mission_accronym,
                    self.type,
                    self.name)

        return product_lid

    def product_vid(self):

        product_vid = '1.0'


        return product_vid


    def coverage(self):
        if self.type.lower() == 'spk':
            (self.start_time, self.stop_time) = self.spk_coverage()
        elif self.type.lower() == 'ck':
            (self.start_time, self.stop_time) = self.ck_coverage()
        elif self.extension.lower() == 'bpc':
            (self.start_time, self.stop_time) = self.pck_coverage()
        elif self.type.lower() == 'sclk':
            (self.start_time, self.stop_time) = self.sclk_coverage()

        else:
            self.start_time = self.setup.mission_start
            self.stop_time = self.setup.mission_stop


    def spk_coverage(self):

        ids = spiceypy.spkobj(self.path)

        MAXIV = 1000
        WINSIZ = 2 * MAXIV
        TIMLEN = 62

        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

        start_points_list = list()
        end_points_list = list()

        for id in ids:

            spiceypy.scard, 0, coverage
            spiceypy.spkcov(spk=self.path, idcode=id, cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for i in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, i)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])


        start_time = min(start_points_list)
        stop_time = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time,
                                         "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time,
                                        "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'

        return [start_time_cal, stop_time_cal]


    def ck_coverage(self):


        start_points_list = list()
        end_points_list = list()

        MAXIV = 10000
        WINSIZ = 2 * MAXIV
        TIMLEN = 500
        MAXOBJ = 10000

        ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)
        ids = spiceypy.ckobj(ck=f'{self.path}/{self.name}', out_cell=ids)

        for id in ids:

            coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)
            spiceypy.scard, 0, coverage
            coverage = spiceypy.ckcov(ck=f'{self.path}/{self.name}', idcode=id, needav=False,
                                    level='SEGMENT', tol=0.0, timsys='TDB',
                                    cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for j in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, j)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])


        start_time = min(start_points_list)
        stop_time = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time,
                                       "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time, "YYYY-MM-DDTHR:MN:SC.###::UTC",
                                      TIMLEN) + 'Z'

        return [start_time_cal, stop_time_cal]

    #
    # PCK kernel processing
    #
    def pck_coverage(self):

        MAXIV = 1000
        WINSIZ = 2 * MAXIV
        TIMLEN = 62
        MAXOBJ = 1000

        ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)

        spiceypy.pckfrm(f'{self.path}/{self.name}', ids)

        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

        start_points_list = list()
        end_points_list = list()

        for id in ids:

            spiceypy.scard, 0, coverage
            spiceypy.pckcov(pck=f'{self.path}/{self.name}', idcode=id, cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for i in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, i)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])

        start_time_tbd = min(start_points_list)
        stop_time_tbd = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time_tbd,
                                       "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time_tbd,
                                      "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'


        return [start_time_cal, stop_time_cal]

    #
    # SCLK kernel processing
    #
    def sclk_coverage(self):

        start_time_cal = self.setup.mission_start
        stop_time_cal  = self.setup.mission_stop

        return [start_time_cal, stop_time_cal]

    #
    # IK kernel processing
    #
    def ik_kernel_ids(self):

        with open(f'{self.path}/{self.name}', "r") as f:

            id_list = list()
            parse_bool = False

            for line in f:

                if 'begindata' in line:
                    parse_bool = True

                if 'begintext' in line:
                    parse_bool = False

                if 'INS-' in line and parse_bool == True:
                    line = line.lstrip()
                    line = line.split("_")
                    id_list.append(line[0][3:])

        id_list = list(set(id_list))

        return [id_list]


    def kernel_setup_phase(self):

        # avoid reading the Z at the end of UTC tag
        start_time = self.start_time[0:-1] if self.start_time != 'N/A' else 'N/A'
        stop_time = self.stop_time[0:-1] if self.stop_time != 'N/A' else 'N/A'

        setup_phase_map = self.setup.root_dir + \
                            '/config/{}.phases'.format(self.setup.accronym.lower())

        with open(setup_phase_map, 'r') as f:
            setup_phases = list()

            if start_time == 'N/A' and stop_time == 'N/A':

                for line in f:
                    setup_phases.append(line.split('   ')[0])

            if start_time != 'N/A' and stop_time == 'N/A':

                next_phases_bool = False
                start_tdb = spiceypy.str2et(start_time)  # + ' TDB')

                for line in f:
                    start_phase_date = line.rstrip().split(' ')[-2]
                    start_phase_tdb = spiceypy.str2et(start_phase_date)

                    stop_phase_date = line.rstrip().split(' ')[-1]
                    stop_phase_tdb = spiceypy.str2et(stop_phase_date)

                    if next_phases_bool == True:
                        setup_phases.append(line.split('   ')[0])

                    elif start_tdb >= start_phase_tdb:
                        setup_phases.append(line.split('   ')[0])
                        next_phases_bool = True

            if start_time != 'N/A' and stop_time != 'N/A':

                next_phases_bool = False
                start_tdb = spiceypy.str2et(start_time)  # + ' TDB')
                stop_tdb = spiceypy.str2et(stop_time)  # + ' TDB')

                for line in f:

                    start_phase_date = line.rstrip().split(' ')[-2]
                    start_phase_tdb = spiceypy.str2et(
                        start_phase_date)  # + ' TDB')

                    stop_phase_date = line.rstrip().split(' ')[-1]
                    stop_phase_tdb = spiceypy.str2et(stop_phase_date)
                    stop_phase_tdb += 86400
                    #  One day added to account for gap between phases.

                    if next_phases_bool == True and start_phase_tdb >= stop_tdb:
                        break
                    # if next_phases_bool == True:
                    #     setup_phases.append(line.split('   ')[0])
                    # if start_phase_tdb <= start_tdb <= stop_phase_tdb:
                    #     setup_phases.append(line.split('   ')[0])
                    #     next_phases_bool = True
                    if start_tdb <= stop_phase_tdb:
                        setup_phases.append(line.split('   ')[0])
                        next_phases_bool = True

        setup_phases_str = ''
        for phase in setup_phases:
            setup_phases_str += '                                 ' + phase + ',\r\n'

        setup_phases_str = setup_phases_str[0:-3]

        self.setup_phases = setup_phases_str

        return


class MetaKernelProduct(Product):

    def __init__(self, setup, kernel, spice_kernels_collection, product=False):
        '''

        :param mission:
        :param spice_kernels_collection:
        :param product: We can input a meta-kernel such that the meta-kernel does not have to be generated
        '''

        logging.info('')
        logging.info(f'-- Generating meta-kernel: {kernel}')

        self.new_product = True
        self.template    = setup.root_dir + f'/config/{setup.mission_accronym}_metakernel.tm'
        self.path        = self.template
        self.setup       = setup
        self.name        = kernel
        self.version     = int(self.name.split('.')[0][-1])
        self.extension   = self.path.split('.')[1]
        self.collection  = spice_kernels_collection

        self.type = extension2type(self)

        if setup.pds == '3':
            self.collection_path = setup.staging_directory + os.sep + \
                                   'EXTRAS' + os.sep
        elif setup.pds == '4':
            self.collection_path = setup.staging_directory + os.sep + \
                                   'spice_kernels' + os.sep

        if self.setup.pds == '3':
            product_path = self.collection_path + self.type.upper() + os.sep
            self.KERNELPATH = './DATA'
        else:
            product_path = self.collection_path + self.type + os.sep
            self.KERNELPATH = '..'

        self.start_time = self.setup.mission_start
        self.stop_time = self.setup.increment_stop

        if self.setup.pds == '4':
            self.AUTHOR = self.setup.author
        else:
            self.AUTHOR = self.setup.author

        self.PDS4_MISSION_NAME = self.setup.mission_name

        self.CURRENT_DATE = current_date()

        #
        # Generate the meta-kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # Name the metakernel; if the meta-kernel is manually provided this
        # step is skipped.
        #
        if product:
            self.name = product.split(os.sep)[-1]
            self.path = product
        else:
            self.path = product_path + self.name

        self.FILE_NAME = self.name

        #
        # Check product version. Note that the meta-kernel version is provided
        # in the kernel list. The version is checked.
        #
        self.check_version()

        #
        # Generate the product LIDVID.
        #
        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # The meta-kernel must be named before fetching the description.
        #
        self.description = self.get_description()
        #
        # Generate the meta-kernel.
        #
        if not product:
            self.write_product()

        #
        # Following the product generation we read the kernels again to
        # include all the kernels present.
        #
        self.collection_metakernel = mk2list(self.path)


        Product.__init__(self)

        if self.setup.pds == '4':
            logging.info('')
            logging.info(f'-- Labeling meta-kernel: {kernel}')
            self.label = MetaKernelPDS4Label(setup, self)

        return


    def check_version(self):

        logging.info(f'-- Meta-kernel version {self.version} from kernel list.')

        if not self.setup.increment:
            return

        logging.info(f'-- Check version from previous increment.')

        #
        # Collection versions are not equal to the release number,
        #
        if self.setup.pds == '4':
            versions = glob.glob(f'{self.setup.final_directory}/'
                                 f'{self.setup.mission_accronym}_spice/'
                                 f'spice_kernels/mk/'
                                 f'{self.name.split("v")[0]}*.tm')
        else:
            #TODO: adapt to PDS3
            versions = glob.glob(f'{self.setup.final_directory}/'
                                 f'{self.setup.mission_accronym}_spice/'
                                 f'spice_kernels/mk/'
                                 f'{self.name.split("v")[0]}*')

        versions.sort()
        try:
            version = int(versions[-1].split('v')[-1].split('.')[0]) + 1
        except:
            logging.error(f'    Meta-kernel from previous increment is not available.')
            logging.error(f'    It is recommended to stop the execution and fix the issue.')
            logging.error(f'    Version from kernel list will be used: {self.version}.')

            if self.setup.interactive:
                input(">> Press Enter to continue...")

            return

        if version == self.version:
            logging.info(f'     Version from kernel list and from previous increment agree: {version}.')
        else:
            logging.error(f'    Version discrepancy. From kernel list: {self.version}. From increment: {version}.')
            logging.error(f'    It is recommended to stop the execution and fix the issue.')
            logging.error(f'    Version from kernel list will be used: {self.version}.')

        if self.setup.interactive:
            input(">> Press Enter to continue...")


        return


    def product_lid(self):

        if self.type == 'mk':
            name = self.name.split('_v')[0]
        else:
            name = self.name

        product_lid = 'urn:nasa:pds:{}.spice:spice_kernels:{}_{}'.format(
                        self.setup.mission_accronym,
                        self.type,
                        name)


        return product_lid


    def product_vid(self):

        try:
            product_vid = str(self.version) + '.0'
        except:
            logging.warning(f'{self.name} No vid explicit in kernel name: set to 1.0')
            product_vid = '1.0'

        return product_vid


    def write_product(self):

        #
        # Parse the meta-kernel grammar to obtain the kernel grammar.
        #
        mk_grammar = self.setup.root_dir + \
                     f'/config/{self.setup.mission_accronym}_metakernel.grammar'
        logging.info(f'-- Writing meta-kernel using: {mk_grammar}')


        with open(mk_grammar, 'r') as kg:
            kernel_grammar_list = []

            for line in kg:

                if line.strip() != '':
                    line = line.split("\n")[0]
                    kernel_grammar_list.append(line)

        #
        # We scan the kernel directory to obtain the list of available kernels
        #
        kernel_type_list = ['lsk', 'pck', 'fk', 'ik', 'sclk', 'spk', 'ck', 'dsk']

        #
        # All the files of the directory are read into a list
        #
        mkgen_kernels = []
        excluded_kernels = []

        for kernel_type in kernel_type_list:

            #
            # First we build the list of excluded kernels
            #
            for kernel_grammar in kernel_grammar_list:
                if 'exclude:' in kernel_grammar:
                    excluded_kernels.append(
                            kernel_grammar.split('exclude:')[-1])

            logging.info(f'     Matching {kernel_type} with meta-kernel grammar.')
            for kernel_grammar in kernel_grammar_list:

                if 'date:' in kernel_grammar:
                    kernel_grammar = kernel_grammar.split('date:')[-1]
                    dates = True
                else:
                    dates = False


                #
                # Kernels can come from several kernel directories or from the
                # previous meta-kernel. Paths are provided by the parameter
                # paths and meta-kernels with mks.
                #
                paths = []
                mks   = []
                if kernel_grammar.split('.')[-1].lower() in type2extension(kernel_type):
                    try:
                        if self.setup.pds == '3':
                            paths.append(self.setup.staging_directory + '/DATA')

                        else:
                            paths.append(self.setup.staging_directory+'/spice_kernels')
                        #paths.append(self.setup.kernels_directory)

                        #
                        # Try to look for meta-kernels from previous
                        # increments.
                        #
                        try:
                            mks = glob.glob(f'{self.setup.final_directory}/'
                                            f'{self.setup.mission_accronym}'
                                            f'_spice/spice_kernels/mk/{self.name.split("_v")[0]}*.tm')
                        except:
                            if self.setup.increment:
                                logging.warning('-- No meta-kernels from previous increment available.')

                        latest_kernel = get_latest_kernel(kernel_type, paths,
                                                          kernel_grammar, dates=dates,
                                                          excluded_kernels=excluded_kernels,
                                                          mks=mks)
                    except Exception as e:
                        logging.error(f'-- Exception: {e}')
                        latest_kernel = []

                    if latest_kernel:
                        if not isinstance(latest_kernel, list):
                            latest_kernel = [latest_kernel]

                        for kernel in latest_kernel:
                            logging.info(f'        Matched: {kernel}')
                            mkgen_kernels.append(kernel_type + '/' + kernel)


        #
        # Remove duplicate entries from the kernel list (possible depending on
        # the grammar).
        #
        mkgen_kernels = list(OrderedDict.fromkeys(mkgen_kernels))

        #
        # Subset the SPICE kernels collection with the kernels in the MK
        # only.
        #
        collection_metakernel     = []
        for spice_kernel in self.collection.product:
            for name in mkgen_kernels:
                if spice_kernel.name in name:
                    collection_metakernel.append(spice_kernel)

        self.collection_metakernel = collection_metakernel

        #
        # Report kernels present in meta-kernel
        #
        logging.info('')
        logging.info(f'-- Archived kernels present in meta-kernel')
        for kernel in collection_metakernel:
            logging.info(f'     {kernel.name}')
        logging.info('')

        num_ker_total = len(self.collection.product)
        num_ker_mk    = len(collection_metakernel)

        logging.warning(f'-- Archived kernels:           {num_ker_total}')
        logging.warning(f'-- Kernels in meta-kernel:     {num_ker_mk}')

        #
        # The kernel list for the new mk is formatted accordingly
        #
        kernels = ''
        kernel_dir_name = None
        for kernel in mkgen_kernels:

            if kernel_dir_name:
                if kernel_dir_name != kernel.split('.')[1]:
                    kernels += '\n'

            kernel_dir_name = kernel.split('.')[1]


            kernels += f"{' '*26}'$KERNELS/{kernel}'\n"

        self.KERNELS_IN_METAKERNEL = kernels[:-1]

        metakernel_dictionary = vars(self)

        with open(self.path, "w+") as f:

            for line in fileinput.input(self.template):
                line = line.rstrip()
                for key, value in metakernel_dictionary.items():
                    if isinstance(value, str) and key.isupper() and key in \
                            line and '$' in line:
                        line = line.replace('$', '')
                        line = line.replace(key, value)
                for key, value in metakernel_dictionary.items():
                    if isinstance(value, str) and key.isupper() and key in \
                            line and '#' in line:
                        line = line.replace('#', '')
                        line = line.replace(key, value)
                f.write(line + '\n')

        self.product = self.path

        logging.info(f'-- Meta-kernel generated.')
        if self.setup.interactive:
            input(">> Press Enter to continue...")

        self.validate_diff()

        return


    def validate_diff(self):

        #
        # Compare meta-kernel with latest. First try with previous increment.
        #
        val_mk = ''
        try:

            match_flag = True
            val_mk_path = f'{self.setup.final_directory}/' \
                          f'{self.setup.mission_accronym}_spice/' + \
                          f'spice_kernels/mk/'

            val_mk_name = self.name.split(os.sep)[-1]
            i = 1

            while match_flag:
                if i < len(val_mk_name) - 1:
                    val_mks = glob.glob(val_mk_path + val_mk_name[0:i] + '*.tm')
                    if val_mks:
                        val_mks = sorted(val_mks)
                        val_mk = val_mks[-1]
                        match_flag = True
                    else:
                        match_flag = False
                    i += 1

            if not val_mk:
                raise Exception("No label for comparison found.")

        except:
            #
            # If previous increment does not work, compare with template.
            #
            logging.warning(f'-- No other version of {self.name} has been found.')
            logging.warning(f'-- Comparing with meta-kernel template.')

            val_mk = f'{self.setup.root_dir}/config/{self.setup.mission_accronym}' \
                     f'_metakernel.tm'

        logging.info('')
        fromfile = val_mk
        tofile = self.path
        dir = self.setup.working_directory

        compare_files(fromfile, tofile, dir)

        if self.setup.interactive:
            input(">> Press enter to continue...")


    def validate(self):


        line = f'Step {self.setup.step} - Meta-kernel validation'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

        rel_path = self.path.split(f'/{self.setup.mission_accronym}_spice/')[-1]
        path = self.setup.final_directory.split(f'{self.setup.mission_accronym}_spice')[0] + f'/{self.setup.mission_accronym}_spice/' + rel_path

        cwd   = os.getcwd()
        mkdir = os.sep.join(path.split(os.sep)[:-1])
        os.chdir(mkdir)

        spiceypy.kclear()
        spiceypy.furnsh(path)

        #
        # In KTOTAL, all meta-kernels are counted in the total; therefore
        # we need to substract 1 kernel.
        #
        ker_num_fr = spiceypy.ktotal('ALL') - 1
        ker_num_mk = self.collection_metakernel.__len__()

        logging.info(f'-- Kernels loaded with FURNSH: {ker_num_fr}')
        logging.info(f'-- Kernels present in {self.name}: {ker_num_mk}')
        logging.info('')

        if (ker_num_fr != ker_num_mk):
            spiceypy.kclear()
            error_message('Number of kernels loaded is not equal to kernels present in meta-kernel.')

        spiceypy.kclear()

        os.chdir(cwd)

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


    def log(setup):

        line = f'Step {setup.step} - Generation of meta-kernel(s)'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        setup.step += 1

        return


class InventoryProduct(Product):

    def __init__(self, setup, collection):


        line = f'Step {setup.step} - Generation of {collection.name} collection'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        setup.step += 1

        self.setup = setup
        self.collection = collection

        if setup.pds == '3':
            self.path = setup.final_directory + os.sep + 'INDEX' \
                        + os.sep + 'INDEX.TAB'

        elif setup.pds == '4':

            #
            # Determine the inventory version
            #
            if self.setup.increment:
                inventory_files = glob.glob(self.setup.final_directory + \
                                            f'/{self.setup.mission_accronym}_spice/' + \
                                            os.sep + collection.name + os.sep +  \
                                            f'collection_{collection.name}_inventory_v*.csv')
                inventory_files.sort()
                try:
                    latest_file = inventory_files[-1]

                    #
                    # We store the previous version to use it to validate the
                    # generated one.
                    #
                    self.path_current = latest_file

                    latest_version = latest_file.split('_v')[-1].split('.')[0]
                    self.version = int(latest_version) + 1

                    logging.info(f'-- Previous inventory file is: {latest_file}')
                    logging.info(f'-- Generate version {self.version}.')

                except:
                    self.version = 1
                    self.path_current = ''

                    logging.error(f'-- Previous inventory file not found.')
                    logging.error(f'-- Default to version {self.version}.')
                    logging.error(f'-- The version of this file might be incorrect.')

                    if self.setup.interactive:
                        input(">> Press Enter to continue...")

            else:
                self.version = 1
                self.path_current = ''

                logging.warning(f'-- Default to version {self.version}.')
                logging.warning(f'-- Make sure this is the first release of the archive.')

                if self.setup.interactive:
                    input(">> Press Enter to continue...")


            self.name = f'collection_{collection.name}_inventory_v{self.version:03}.csv'
            self.path = setup.staging_directory + os.sep + collection.name \
                        + os.sep + self.name

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # Kernels are already generated products but Inventories are not.
        #
        self.write_product()
        Product.__init__(self)


        if setup.pds == '3':
            self.label = InventoryPDS3Label(setup, collection, self)
        elif setup.pds == '4':
            self.label = InventoryPDS4Label(setup, collection, self)

        return


    def product_lid(self):

        product_lid = \
            'urn:esa:psa:{}_spice:document:spiceds'.format(
                    self.setup.mission_accronym)

        return product_lid


    def product_vid(self):

        return '{}.0'.format(int(self.version))


    def write_product(self):

        #
        # PDS4 collection file generation
        #
        with open(self.path, "w+") as f:
            #
            # If there is an existing version we need to add the items from
            # the previous version as SECONDARY members
            #
            if self.setup.increment:
                try:
                    prev_collection_path = self.setup.final_directory + os.sep + self.setup.mission_accronym + \
                                           '_spice/' + self.collection.name + os.sep + \
                                           self.name.replace(str(self.version), str(self.version-1))
                    with open(prev_collection_path, "r") as r:
                        for line in r:
                            if 'P,urn' in line:
                                # All primary items in previous version shall be included as secondary in the new one
                                line = line.replace('P,urn', 'S,urn')
                            line = add_carriage_return(line)
                            f.write(line)
                except:
                    logging.error('-- A previous collection was expected. The generated collection might be incorrect.')

            for product in self.collection.product:
                if product.new_product:
                    line = '{},{}::{}\r\n'.format('P', product.label.PRODUCT_LID, product.label.PRODUCT_VID)
                    line = add_carriage_return(line)
                    f.write(line)

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        logging.info(f'-- Generated {self.path}')



        self.validate()

        return


    def validate(self):
        '''
        The label is validated by checking that all the products are present
        and by comparing the Inventory Product with the previous version and
        if it does not exist with the sample inventory product.

        :return:
        '''

        logging.info(f'-- Validating {self.name}')


        #
        # Check that all the products are listed in the collection product.
        #
        logging.info('      Check that all the products are in the collection.')

        with open(self.path, 'r') as c:
            for product in self.collection.product:
                product_found = False
                for line in c:
                    if product.lid in line:
                        product_found = True
                if not product_found:
                    logging.error(f'      Product {product.lid} not found. Consider increment re-generation.')

        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")


        #
        # Use the prior version of the same product, if it does not
        # exist use the sample.
        #
        if self.path_current:

            fromfile = self.path_current
            tofile   = self.path
            dir      = self.setup.working_directory

            compare_files(fromfile, tofile, dir)

        else:

            logging.warning('-- Comparing with InSight test inventory product.')
            fromfiles = glob.glob(f'{self.setup.root_dir}tests/functional/data/insight/' \
                        f'insight_spice/{self.collection.type}/collection_{self.collection.name}_inventory_*.csv')
            fromfiles.sort()
            fromfile  = fromfiles[-1]
            tofile    = self.path
            dir       = self.setup.working_directory

            compare_files(fromfile, tofile, dir)

        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


    def write_index(self):

        line = f'Step {self.setup.step} - Generation of index files'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

        cwd = os.getcwd()
        os.chdir(self.setup.staging_directory)

        list   = f'{self.setup.working_directory}/{self.collection.list.complete_list}'
        command = f'perl {self.setup.root_dir}exe/xfer_index.pl {list}'
        logging.info(f'-- Executing: {command}')

        command_process = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

        process_output, _ = command_process.communicate()
        text = process_output.decode('utf-8')

        os.chdir(cwd)

        for line in text.split('\n'):
            logging.info('   ' + line)

        #
        # The Perl script returns an error message if there is a problem.
        #
        if ('ERROR' in text) or ('command not found' in text):
            error_message(text)

        #
        # Move index files to appropriate directory
        #
        index       = f'{self.setup.staging_directory}/index.tab'
        index_lbl   = f'{self.setup.staging_directory}/index.lbl'
        dsindex     = f'{self.setup.staging_directory}/dsindex.tab'
        dsindex_lbl = f'{self.setup.staging_directory}/dsindex.lbl'

        #
        # Add CRS to the index files.
        #

        if self.setup.pds == '4':
            os.remove(index)
            os.remove(index_lbl)

            dsindex     = shutil.move(dsindex, self.setup.staging_directory + '/../')
            dsindex_lbl = shutil.move(dsindex_lbl, self.setup.staging_directory + '/../')

            logging.info('-- Adding CRs to index files.')
            logging.info('')
            add_crs_to_file(dsindex)
            add_crs_to_file(dsindex_lbl)

            self.index       = ''
            self.index_lbl   = ''
            self.dsindex     = dsindex
            self.dsindex_lbl = dsindex_lbl

        self.validate_index()

        return


    def validate_index(self):
        '''
        The index and the index label are validated by comparing with
        the previous versions

        :return:
        '''

        #
        # Compare with previous index file, if exists. Otherwise it is
        # not compared.
        #
        indexes = [self.index, self.index_lbl, self.dsindex, self.dsindex_lbl]

        for index in indexes:
            if index:
                try:
                    current_index = self.setup.final_directory + os.sep + index.split(os.sep)[-1]
                    compare_files(index, current_index, self.setup.working_directory)
                except:
                    logging.warning(f'-- File to compare with does not exist: {index}')

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


class SpicedsProduct(object):

    def __init__(self, setup, collection):

        self.new_product  = True
        self.setup        = setup
        self.collection   = collection
        #
        # - Obtain the previous spiceds file if it exists
        #
        path = setup.final_directory + os.sep + \
               setup.mission_accronym + '_spice' + os.sep + \
                collection.name
        if self.setup.increment:
            spiceds_files = glob.glob(path + os.sep + 'spiceds_v*.html')
            spiceds_files.sort()
            try:
                latest_spiceds = spiceds_files[-1]
                latest_version = latest_spiceds.split('_v')[-1].split('.')[0]
                self.latest_spiceds = latest_spiceds
                self.latest_version = latest_version
                self.version = int(latest_version) + 1
            except:
                logging.error('-- No previous version of spiceds_v*.html file found. Generated file might be incorrect.')
                self.version = 1
                self.latest_spiceds = ''
        else:
            self.version = 1
            self.latest_spiceds = ''

        self.name = 'spiceds_v{0:0=3d}.html'.format(self.version)
        self.path = setup.staging_directory + os.sep + collection.name \
                    + os.sep + self.name
        self.template = setup.root_dir + f'/config/{self.setup.mission_accronym}_spiceds.html'
        self.mission = setup

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # We provide the values as if it was a label
        #
        self.PRODUCT_CREATION_DATE = current_date()
        self.PRODUCER_NAME = setup.author
        self.PRODUCER_EMAIL = setup.email
        self.PRODUCER_PHONE = setup.phone

        self.generated = self.write_product()
        if not self.generated:
            return

        #
        # Kernels are already generated products but Inventories are not.
        #
        Product.__init__(self)


        #
        # Validate the product and then generate the label.
        #
        self.validate()

        self.label = DocumentPDS4Label(setup, collection, self)


        return


    def product_lid(self):

        product_lid = \
            'urn:nasa:pds:{}.spice:document:spiceds'.format(
                    self.setup.mission_accronym)

        return product_lid

    def product_vid(self):

        return '{}.0'.format(int(self.version))


    def write_product(self):

        with open(self.path, "w+") as f:

            spiceds_dictionary = vars(self)

            for line in fileinput.input(self.template):
                for key, value in spiceds_dictionary.items():
                    if isinstance(value, str) and key in line and '$' in line:
                        line = line.replace(key, value)
                        line = line.replace('$', '')

                line = add_carriage_return(line)

                f.write(line)

        #
        # If the previous spiceds document is the same then it does not
        # need to be generated.
        #
        generate_spiceds = True
        if self.latest_spiceds:
            with open(self.path) as f:
                spiceds_current = f.readlines()
            with open(self.latest_spiceds) as f:
                spiceds_latest = f.readlines()

            differ = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
            diff = list(differ.compare(spiceds_current, spiceds_latest))

            generate_spiceds = False
            for line in diff:
                if line[0] == '-':
                    if 'Last update' not in line and line.strip() != '-' and line.strip() != '-\n':
                        generate_spiceds = True

            if not generate_spiceds:
                os.remove(self.path)
                logging.warning('-- SPICEDS document does not need to be updated')
                logging.warning('')

        return generate_spiceds


    def validate(self):

        #
        # Compare spiceds with latest. First try with previous increment.
        #
        val_spd = ''
        try:

            val_spd_path = f'{self.setup.final_directory}/' \
                           f'{self.setup.mission_accronym}_spice/' + \
                          f'document'

            val_spds     = glob.glob(f'{val_spd_path}/spiceds_v*.html')
            val_spds.sort()
            val_spd  = val_spds[-1]


        except:
            #
            # If previous increment does not work, compare with template.
            #
            logging.warning(f'-- No other version of {self.name} has been found.')
            logging.warning(f'-- Comparing with spiceds template.')

            val_spd = f'{self.setup.root_dir}/config/{self.setup.mission_accronym}' \
                      f'_spiceds.html'

        logging.info('')
        fromfile = val_spd
        tofile = self.path
        dir = self.setup.working_directory

        compare_files(fromfile, tofile, dir)

        logging.info('')

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


class ReadmeProduct(Product):

    def __init__(self, setup, bundle):

        logging.info('')
        logging.info(f'Step {setup.step} - Generate bundle products')
        logging.info('---------------------------------')
        logging.info('')
        setup.step += 1

        self.name = 'readme.txt'
        self.bundle = bundle
        self.path = setup.staging_directory + os.sep + self.name
        self.setup = setup
        self.vid = bundle.vid
        self.collection = Object()
        self.collection.name = ''

        logging.info('-- Generating readme file')
        self.write_product()
        Product.__init__(self)

        try:
            os.path.exists(self.setup.final_directory +
                           f'/{self.setup.mission_accronym}_spice/readme.txt')
            logging.info('-- Readme file already exists in final; file is removed from staging.')
            os.remove(self.path)
        except:
            pass

        logging.info('')

        #
        # Now we change the path for the difference of the name in the label
        #
        self.path = setup.staging_directory + os.sep + bundle.name

        logging.info('-- Generating bundle label.')
        self.label = BundlePDS4Label(setup, self)

        return

    def write_product(self):

        line_length = 0

        if not os.path.isfile(self.path):
            with open(self.path, "w+") as f:

                for line in fileinput.input(self.setup.root_dir + '/etc/template_readme.txt'):
                    if '$SPICE_NAME' in line:
                        line = line.replace('$SPICE_NAME', self.setup.spice_name)
                    if '$AUTHOR' in line:
                        line = line.replace('$AUTHOR', self.setup.author)
                    if '$UNDERLINE' in line:
                        line = line.replace('$UNDERLINE', '='*line_length)

                    line_length = len(line)-1
                    line        = add_carriage_return(line)


                    f.write(line)

        return


class Object(object):
    pass
