import os
import re
import glob
import logging
import shutil
import filecmp
import difflib
import fileinput
import spiceypy
import subprocess
from collections import OrderedDict
from datetime import date
from npb.classes.label import SpiceKernelPDS4Label
from npb.classes.label import MetaKernelPDS4Label
from npb.classes.label import InventoryPDS4Label
from npb.classes.label import InventoryPDS3Label
from npb.classes.label import DocumentPDS4Label
from npb.classes.label import BundlePDS4Label
from npb.classes.log import error_message
from npb.utils.time import creation_time
from npb.utils.time import creation_date
from npb.utils.time import current_date
from npb.utils.time import spk_coverage
from npb.utils.time import ck_coverage
from npb.utils.time import pck_coverage
from npb.utils.time import dsk_coverage
from npb.utils.files import md5
from npb.utils.files import add_carriage_return
from npb.utils.files import add_crs_to_file
from npb.utils.files import extension2type
from npb.utils.files import safe_make_directory
from npb.utils.files import mk2list
from npb.utils.files import get_latest_kernel
from npb.utils.files import type2extension
from npb.utils.files import compare_files
from npb.utils.files import match_patterns


class Product(object):

    def __init__(self):
        stat_info = os.stat(self.path)
        self.size = str(stat_info.st_size)
        self.checksum = str(md5(self.path))
        self.creation_time = creation_time(self.path)[:-5]
        self.creation_date = creation_date(self.path)
        self.extension = self.path.split(os.sep)[-1].split('.')[-1]


class SpiceKernelProduct(Product):

    def __init__(self, setup, name, collection):

        self.collection = collection
        self.setup = setup
        self.name = name
        self.extension = name.split('.')[-1].strip()
        self.type = extension2type(self)

        self.path = setup.kernels_directory + os.sep + self.type

        if self.extension[0].lower() == 'b':
            self.file_format = 'Binary'
        else:
            self.file_format = 'Character'

        self.description = self.get_description()

        self.coverage()

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
        logging.info(f'-- Copy {self.name} to staging directory.')
        if not os.path.isfile(product_path + self.name):
            try:
                shutil.copy2(self.path + os.sep + self.name,
                             product_path + os.sep + self.name)
                self.new_product = True

            except:
                try:
                    shutil.copy2(self.path + os.sep + self.product_mapping(),
                                 product_path + os.sep + self.name)
                    self.new_product = True
                    logging.info(f'-- Mapping {self.product_mapping()} '
                                 f'with {self.name}')
                except:
                    error_message(f'{self.name} not present in {self.path}')
        else:
            logging.error(f'     {self.name} already present in staging '
                          f'directory.')

            if self.setup.interactive:
                input(">> Press Enter to continue...")

            self.new_product = False

        #
        # We update the path after having copied the kernel.
        #
        self.path = product_path + self.name

        Product.__init__(self)

        #
        # The kernel is labeled.
        #
        logging.info(f'-- Labeling {self.name}...')
        self.label = SpiceKernelPDS4Label(setup, self)

        return

    def product_lid(self):

        product_lid = \
            '{}:spice_kernels:{}_{}'.format(
                self.setup.logical_identifier,
                self.type,
                self.name)

        return product_lid

    def product_vid(self):

        product_vid = '1.0'

        return product_vid

    #
    # Obtain the kernel product description information
    #
    def get_description(self):

        kernel_list_file = self.setup.working_directory + os.sep + \
                           f'{self.setup.mission_accronym}_release_' \
                           f'{int(self.setup.release):02d}.kernel_list'

        get_descr = False
        description = False

        for line in fileinput.input(kernel_list_file):
            if self.name in line:
                get_descr = True
            if get_descr and 'DESCRIPTION' in line:
                description = line.split('=')[-1].strip()
                get_descr = False

        if not description:
            error_message(f'{self.name} does not have '
                          f'a description on {kernel_list_file}')

        return description

    def coverage(self):
        if self.type.lower() == 'spk':
            (self.start_time, self.stop_time) = \
                spk_coverage(self.path + os.sep + self.name,
                             date_format=self.setup.date_format)
        elif self.type.lower() == 'ck':
            (self.start_time, self.stop_time) = \
                ck_coverage(self.path + os.sep + self.name,
                            date_format=self.setup.date_format)
        elif self.extension.lower() == 'bpc':
            (self.start_time, self.stop_time) = \
                pck_coverage(self.path + os.sep + self.name,
                             date_format=self.setup.date_format)
        elif self.type.lower() == 'dsk':
            (self.start_time, self.stop_time) = \
                dsk_coverage(self.path + os.sep + self.name,
                             date_format=self.setup.date_format)
        else:
            self.start_time = self.setup.mission_start
            self.stop_time = self.setup.mission_stop

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
        start_time = \
            self.start_time[0:-1] if self.start_time != 'N/A' else 'N/A'
        stop_time = \
            self.stop_time[0:-1] if self.stop_time != 'N/A' else 'N/A'

        setup_phase_map = f'{self.setup.root_dir}/config/' \
                          f'{self.setup.accronym.lower()}.phases'

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

                    if next_phases_bool == True and \
                            start_phase_tdb >= stop_tdb:
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
            setup_phases_str += '                                 ' \
                                '' + phase + ',\r\n'

        setup_phases_str = setup_phases_str[0:-3]

        self.setup_phases = setup_phases_str

        return

    def product_mapping(self):

        '''Obtain the kernel mapping.'''
        kernel_list_file = self.setup.working_directory + os.sep + \
                           f'{self.setup.mission_accronym}_release_' \
                           f'{int(self.setup.release):02d}.kernel_list'

        get_map = False
        mapping = False

        for line in fileinput.input(kernel_list_file):
            if self.name in line:
                get_map = True
            if get_map and 'MAPPING' in line:
                mapping = line.split('=')[-1].strip()
                get_map = False

        if not mapping:
            error_message(f'{self.name} does not have '
                          f'mapping on {kernel_list_file}')

        return mapping


class MetaKernelProduct(Product):

    def __init__(self, setup, kernel, spice_kernels_collection,
                 user_input=False):
        '''

        :param mission:
        :param spice_kernels_collection:
        :param product: We can input a meta-kernel such that the meta-kernel
                        does not have to be generated
        '''
        if user_input:
            logging.info(f'-- Copy meta-kernel: {kernel}')
            self.path = kernel
        else:
            logging.info(f'-- Generate meta-kernel: {kernel}')
            self.template = \
                f'{setup.root_dir}templates/template_metakernel.tm'
            self.path = self.template

        self.new_product = True
        self.setup = setup
        self.collection = spice_kernels_collection

        if os.sep in kernel:
            self.name = kernel.split(os.sep)[-1]
        else:
            self.name = kernel

        self.extension = self.path.split('.')[1]

        self.type = extension2type(self.name)

        #
        # Add the configuration items for the meta-kernel.
        # This includes sorting out the meta-kernel name.
        #
        if setup.mk:
            for mk in setup.mk:

                patterns_dict = mk['name']['pattern']
                if not isinstance(patterns_dict, list):
                    patterns = []
                    dictionary_copy = patterns_dict.copy()
                    patterns.append(dictionary_copy)
                else:
                    patterns = patterns_dict

                try:
                    values = match_patterns(self.name, mk['@name'], patterns)
                    self.mk_setup = mk
                    self.version = values['VERSION']
                    self.values = values
                    #
                    # If it is a yearly meta-kernel we need the year to set
                    # set the coverage of the meta-kenrel.
                    #
                    if 'YEAR' in values:
                        self.year = values['YEAR']
                except:
                    pass

            if not hasattr(self, 'mk_setup'):
                error_message(f'Meta-kernel {self.name} has not been matched '
                              f'in configuration')

        if setup.pds_version == '3':
            self.collection_path = setup.staging_directory + os.sep + \
                                   'EXTRAS' + os.sep
        elif setup.pds_version == '4':
            self.collection_path = setup.staging_directory + os.sep + \
                                   'spice_kernels' + os.sep

        if self.setup.pds_version == '3':
            product_path = self.collection_path + self.type.upper() + os.sep
            self.KERNELPATH = './DATA'
        else:
            product_path = self.collection_path + self.type + os.sep
            self.KERNELPATH = '..'

        self.start_time = self.setup.increment_start
        self.stop_time = self.setup.increment_finish

        if self.setup.pds_version == '4':
            self.AUTHOR = self.setup.producer_name
        else:
            self.AUTHOR = self.setup.producer_name

        self.PDS4_MISSION_NAME = self.setup.mission_name

        self.CURRENT_DATE = current_date()

        #
        # Generate the meta-kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # Name the meta-kernel; if the meta-kernel is manually provided this
        # step is skipped.
        #
        if user_input:
            self.name = kernel.split(os.sep)[-1]
            self.path = kernel
        else:
            self.path = product_path + self.name

        self.FILE_NAME = self.name

        #
        # Check product version.
        #
        if self.setup.increment:
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
        if not user_input:
            if os.path.exists(self.path):
                logging.error(f'-- Meta-kernel already exists: {self.path}')
                logging.warning(
                    f'-- The meta-kernel will be generated and the one '
                    f'present in the staging are will be overwtitten.')
                logging.warning(
                    f'-- Note that to provide a meta-kernel as an input, '
                    f'it must be provided via configuration file.')
            self.write_product()
        else:
            # Implement manual provision of meta-kernel.
            shutil.copy2(self.path, f'{product_path}{self.name}')
            self.path = f'{product_path}{self.name}'

        #
        # Following the product generation we read the kernels again to
        # include all the kernels present.
        #
        self.collection_metakernel = mk2list(self.path)

        #
        # Set the meta-kernel times
        #
        self.coverage()

        Product.__init__(self)

        if self.setup.pds_version == '4':
            logging.info('')
            logging.info(f'-- Labeling meta-kernel: {self.name}...')
            self.label = MetaKernelPDS4Label(setup, self)

            if self.setup.interactive:
                input(">> Press Enter to continue...")

        return

    def check_version(self):

        #
        # Distinguish in between the different kernels we can find in the
        # previous increment.
        #
        pattern = self.mk_setup['@name']
        for key in self.values:

            if key == 'YEAR':
                pattern = pattern.replace('$' + key, self.year)
            else:
                pattern = pattern.replace(
                    '$' + key, '?' * len(self.values[key]))

        versions = glob.glob(f'{self.setup.final_directory}/'
                             f'{self.setup.mission_accronym}_spice/'
                             f'spice_kernels/mk/{pattern}')

        versions.sort()
        try:
            version_index = pattern.find('?')

            version = versions[-1].split(os.sep)[-1]
            version = \
                version[version_index:version_index + len(self.values[key])]
            version = int(version) + 1

        except:
            logging.warning(f'-- Meta-kernel from previous increment is '
                            f'not available.')
            logging.warning(f'   Version will be set to: {self.version}.')

            if self.setup.interactive:
                input(">> Press Enter to continue...")

            return

        if version == int(self.version):
            logging.info(f'-- Version from kernel list and from previous '
                         f'increment agree: {version}.')
        else:
            logging.error(f'-- The meta-kernel version is not as expected '
                          f'from previous increment.')
            logging.error(f'   Version set to: {int(self.version)}, whereas '
                          f'it is expected to be: {version}.')
            logging.error(f'   It is recommended to stop the execution and '
                          f'fix the issue.')

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        return

    def product_lid(self):

        if self.type == 'mk':
            name = self.name.split('_v')[0]
        else:
            name = self.name

        product_lid = '{}:spice_kernels:{}_{}'.format(
            self.setup.logical_identifier,
            self.type,
            name)

        return product_lid

    def product_vid(self):

        try:
            product_vid = str(self.version).lstrip("0") + '.0'
        except:
            logging.warning(f'-- {self.name} No vid explicit in kernel name: '
                            f'set to 1.0')
            product_vid = '1.0'

        return product_vid

    #
    # Obtain the kernel product description information,
    #
    def get_description(self):

        description = ''
        self.json_config = self.setup.kernel_list_config

        kernel = self.name
        for pattern in self.setup.re_config:

            if pattern.match(kernel):

                options = self.json_config[pattern.pattern]['mklabel_options']
                description = self.json_config[pattern.pattern]['description']
                try:
                    patterns = self.json_config[pattern.pattern]['patterns']
                except:
                    patterns = False
                try:
                    mapping = self.json_config[pattern.pattern]['mapping']
                except:
                    mapping = ''

                #
                # ``options'' and ``descriptions'' require to
                # substitute parameters derived from the filenames
                # themselves.
                #
                if patterns:
                    for el in patterns:
                        if ("$" + el) in description:
                            value = patterns[el]

                            #
                            # There are two distinct patterns:
                            #    * extracted form the filename
                            #    * defined in the configuration file.
                            #
                            if '@pattern' in patterns[el] and \
                                    patterns[el]['@pattern'].lower() == \
                                    'kernel':
                                #
                                # When extracted from the filename, the
                                # keyword is matched in between patterns.
                                #

                                #
                                # First Turn the regex set into a single
                                # character to be able to know were in the
                                # filename is.
                                #
                                patt_ker = value['#text'].replace(
                                    '[0-9]', '$')
                                patt_ker = patt_ker.replace('[a-z]', '$')
                                patt_ker = patt_ker.replace('[A-Z]', '$')
                                patt_ker = patt_ker.replace('[a-zA-Z]', '$')

                                #
                                # Split the resulting pattern to build up the
                                # indexes to extract the value from the kernel
                                # name.
                                #
                                patt_split = patt_ker.split(f'${el}')

                                #
                                # Create a list with the length of each part.
                                #
                                indexes = []
                                for element in patt_split:
                                    indexes.append(len(element))

                                #
                                # Extract the value with the index from the
                                # kernel name.
                                #
                                if len(indexes) == 2:
                                    value = \
                                        kernel[
                                        indexes[0]:len(kernel) - indexes[1]]
                                    if patterns[el]['@pattern'].isupper():
                                        value = value.upper()
                                        #
                                        # Write the value of the pattern for
                                        # future use.
                                        #
                                        patterns[el]['&value'] = value
                                else:
                                    error_message('Kernel pattern not adept '
                                                  'to write description. '
                                                  'Remember a metacharacter '
                                                  'cannot start or finish '
                                                  'a kernel pattern')
                            else:
                                #
                                # For non-kernels the value is based on the
                                # value within the tag that needs to be
                                # provided by the user; there is no way this
                                # can be done automatically.
                                #
                                for val in patterns[el]:
                                    if kernel == val['@value']:
                                        value = val['#text']
                                        #
                                        # Write the value of the pattern for
                                        # future use.
                                        #
                                        patterns[el]['&value'] = value

                                if isinstance(value, list):
                                    error_message('-- Kernel description '
                                                  'could not be updated with '
                                                  'pattern')

                            description = description.replace('$' + el, value)

        description = description.replace('\n', '')
        while '  ' in description:
            description = description.replace('  ', ' ')

        if not description:
            error_message(f'{self.name} does not have '
                          f'a description on configuration file.')

        return description

    def write_product(self):

        #
        # Obtain meta-kernel grammar from configuration.
        #
        kernel_grammar_list = self.setup.mk_grammar['pattern']

        #
        # We scan the kernel directory to obtain the list of available kernels
        #
        kernel_type_list = \
            ['lsk', 'pck', 'fk', 'ik', 'sclk', 'spk', 'ck', 'dsk']

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

            logging.info(
                f'     Matching {kernel_type} with meta-kernel grammar.')
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
                mks = []
                if kernel_grammar.split('.')[-1].lower() in \
                        type2extension(kernel_type):
                    try:
                        if self.setup.pds_version == '3':
                            paths.append(self.setup.staging_directory +
                                         '/DATA')

                        else:
                            paths.append(self.setup.staging_directory +
                                         '/spice_kernels')
                        # paths.append(self.setup.kernels_directory)

                        #
                        # Try to look for meta-kernels from previous
                        # increments.
                        #
                        try:
                            mks = glob.glob(f'{self.setup.final_directory}/'
                                            f'{self.setup.mission_accronym}'
                                            f'_spice/spice_kernels/mk/'
                                            f'{self.name.split("_v")[0]}*.tm')
                        except:
                            if self.setup.increment:
                                logging.warning('-- No meta-kernels from '
                                                'previous increment '
                                                'available.')

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
        collection_metakernel = []
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
        num_ker_mk = len(collection_metakernel)

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

            kernels += f"{' ' * 26}'$KERNELS/{kernel}'\n"

        self.KERNELS_IN_METAKERNEL = kernels[:-1]

        #
        # Introduce and curate the rest of fields from configuration
        #
        data = self.setup.mk_metadata['data']
        desc = self.setup.mk_metadata['description']

        curated_data = ''
        curated_desc = ''

        for line in data.split('\n'):
            #
            # We want to remove the blanks if the line is empty.
            #
            if line.strip() == '':
                curated_data += ''
            else:
                curated_data += ' ' * 6 + line.strip() + '\n'

        for line in desc.split('\n'):
            #
            # We want to remove the blanks if the line is empty.
            #
            if line.strip() == '':
                curated_desc += ''
            else:
                curated_desc += ' ' * 3 + line.strip() + '\n'

        self.DATA = curated_data
        self.DESCRIPTION = curated_desc

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
        if not self.setup.args.silent and not self.setup.args.verbose: print(
            f'   * Created '
            f'{self.product.split(self.setup.staging_directory)[-1]}.')
        if self.setup.interactive:
            logging.info(
                f'-- You might take a moment to double-check the metakernel '
                f'and to do manual edits before proceeding.')
            input(">> Press Enter to continue...")

        self.compare()
        logging.info('')

        return

    def compare(self):

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
                    val_mks = \
                        glob.glob(val_mk_path + val_mk_name[0:i] + '*.tm')
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
            # If previous increment does not work, compare with insight
            # example.
            #
            logging.warning(f'-- No other version of {self.name} has been '
                            f'found.')
            logging.warning(f'-- Comparing with meta-kernel template.')

            val_mk = f'{self.setup.root_dir}/templates/template_metakernel.tm'

        fromfile = self.path
        tofile = val_mk
        dir = self.setup.working_directory

        logging.info(f'-- Comparing '
            f'{self.name.split(f"{self.setup.mission_accronym}_spice/")}...')
        compare_files(fromfile, tofile, dir, 'all')

        if self.setup.interactive:
            input(">> Press enter to continue...")

    def validate(self):

        line = f'Step {self.setup.step} - Meta-kernel validation'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        rel_path = \
            self.path.split(f'/{self.setup.mission_accronym}_spice/')[-1]
        path = \
            self.setup.final_directory.split(f'{self.setup.mission_accronym}'
                                             f'_spice')[
                   0] + f'/{self.setup.mission_accronym}_spice/' + rel_path

        cwd = os.getcwd()
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

        if (ker_num_fr != ker_num_mk):
            spiceypy.kclear()
            error_message('Number of kernels loaded is not equal to kernels '
                          'present in meta-kernel')

        spiceypy.kclear()

        os.chdir(cwd)

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return

    def coverage(self):
        '''
        Meta-kernel coverage is determined by:

        -  for whole mission meta-kernels start_date_time and stop_date_time
           are set to the coverage provided by spacecraft SPK or CKs, at the
           discretion of the archive producer.

        -  for yearly mission meta-kernels start_date_time and stop_date_time
           are set to the coverage from Jan 1 00:00 of the year to either the
           end of coverage provided by spacecraft SPK or CKs, or the end of
           the year (whichever is earlier)

        :return:
        '''

        #
        # Match the pattern with the kernels in the meta-kernel.
        #
        kernels = []
        if isinstance(self.setup.coverage_kernels, list):
            coverage_kernels = self.setup.coverage_kernels[0]['pattern']
        else:
            coverage_kernels = self.setup.coverage_kernels['pattern']
        for pattern in coverage_kernels:
            for kernel in self.collection_metakernel:
                if re.match(pattern, kernel):
                    kernels.append(kernel)

        start_times = []
        finish_times = []
        if kernels:
            #
            # Look for the identified kernel in the collection, if the kernel
            # is not present the coverage will have to be computed.
            #
            if kernels:
                for kernel in kernels:
                    ker_found = False
                    for product in self.collection.product:
                        if kernel == product.name:
                            start_times.append(
                                spiceypy.utc2et(product.start_time[:-1]))
                            finish_times.append(
                                spiceypy.utc2et(product.stop_time[:-1]))
                            ker_found = True

                    #
                    # When the kernels are not present in the current
                    # collection, the coverage is computed.
                    #
                    if not ker_found:
                        path = f'{self.setup.final_directory}/' \
                               f'{self.setup.mission_accronym}_spice/' \
                               f'spice_kernels/' \
                               f'{extension2type(kernel)}/{kernel}'

                        try:
                            if extension2type(kernel) == 'spk':
                                (start_time, stop_time) = spk_coverage(path)
                            elif extension2type(kernel) == 'ck':
                                (start_time, stop_time) = ck_coverage(path)
                            else:
                                error_message('Kernel used to determine '
                                              'coverage is not a SPK or CK '
                                              'kernel')

                            start_times.append(
                                spiceypy.utc2et(start_time[:-1]))
                            finish_times.append(
                                spiceypy.utc2et(stop_time[:-1]))

                        except:
                            #
                            # If the kernels are not available it has to be
                            # signaled.
                            #
                            logging.error(f'-- File not present in final '
                                          f'area: {path}')

        #
        # If it is a yearly meta-kernel; we need to handle it separately.
        #
        if hasattr(self, 'year') and start_times and finish_times:

            #
            # The date can be January 1st, of the year or the mission start
            # date, but it should not be later or earlier than that.
            #
            et_mission_start = spiceypy.utc2et(self.setup.mission_start[:-1])
            et_year_start = spiceypy.utc2et(f'{self.year}-01-01T00:00:00')

            if (et_year_start > et_mission_start):
                start_times = [et_year_start]
            else:
                start_times = [et_mission_start]

            #
            # Update the end time of the meta-kernel
            #
            et_year_stop = \
                spiceypy.utc2et(f'{int(self.year) + 1}-01-01T00:00:00')

            if max(finish_times) > et_year_stop:
                finish_times = [et_year_stop]

        try:

            start_time = \
                spiceypy.et2utc(min(start_times), 'ISOC', 0, 80) + 'Z'
            stop_time = \
                spiceypy.et2utc(max(finish_times), 'ISOC', 0, 80) + 'Z'
            logging.info(f'-- Meta-kernel coverage: '
                         f'{start_time} - {stop_time}')

        except:
            #
            # The alternative is to set the increment stop time to the
            # end time of the mission.
            #
            start_time = self.setup.mission_start
            stop_time = self.setup.mission_stop
            logging.error(f'-- No kernel(s) found to determine meta-kernel '
                          f'coverage. Mission times will be used:')
            logging.info(f'   {start_time} - {stop_time}')

        self.start_time = start_time
        self.stop_time = stop_time

        return


class InventoryProduct(Product):

    def __init__(self, setup, collection):

        line = f'Step {setup.step} - Generation of {collection.name} ' \
               f'collection'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        self.setup = setup
        self.collection = collection

        if setup.pds_version == '3':
            self.path = setup.final_directory + os.sep + 'INDEX' \
                        + os.sep + 'INDEX.TAB'

        elif setup.pds_version == '4':

            #
            # Determine the inventory version
            #
            if self.setup.increment:
                inventory_files = glob.glob(self.setup.final_directory + \
                    f'/{self.setup.mission_accronym}_spice/' + \
                    os.sep + collection.name + os.sep + \
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

                    logging.info(f'-- Previous inventory file is: '
                                 f'{latest_file}')
                    logging.info(f'-- Generate version {self.version}.')

                except:
                    self.version = 1
                    self.path_current = ''

                    logging.error(f'-- Previous inventory file not found.')
                    logging.error(f'-- Default to version {self.version}.')
                    logging.error(f'-- The version of this file might be '
                                  f'incorrect.')

                    if self.setup.interactive:
                        input(">> Press Enter to continue...")

            else:
                self.version = 1
                self.path_current = ''

                logging.warning(f'-- Default to version {self.version}.')
                logging.warning(f'-- Make sure this is the first release of '
                                f'the archive.')

                if self.setup.interactive:
                    input(">> Press Enter to continue...")

            self.name = f'collection_{collection.name}_' \
                        f'inventory_v{self.version:03}.csv'
            self.path = setup.staging_directory + os.sep + collection.name \
                        + os.sep + self.name

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # Kernels are already generated products but Inventories are not.
        #
        self.write_product()
        Product.__init__(self)

        if setup.pds_version == '3':
            self.label = InventoryPDS3Label(setup, collection, self)
        elif setup.pds_version == '4':
            self.label = InventoryPDS4Label(setup, collection, self)

        return

    def product_lid(self):

        product_lid = \
            f'{self.setup.logical_identifier}:document:spiceds'

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
                    prev_collection_path = \
                        self.setup.final_directory + os.sep + \
                        self.setup.mission_accronym + \
                        '_spice/' + self.collection.name + os.sep + \
                        self.name.replace(str(self.version),
                                          str(self.version - 1))
                    with open(prev_collection_path, "r") as r:
                        for line in r:
                            if 'P,urn' in line:
                                #
                                # All primary items in previous version shall
                                # be included as secondary in the new one
                                #
                                line = line.replace('P,urn', 'S,urn')
                            line = add_carriage_return(line)
                            f.write(line)
                except:
                    logging.error('-- A previous collection was expected. '
                                  'The generated collection might be '
                                  'incorrect.')

            for product in self.collection.product:
                if product.new_product:
                    line = f'P,' \
                           f'{product.label.PRODUCT_LID}::' \
                           f'{product.label.PRODUCT_VID}\r\n'
                    line = add_carriage_return(line)
                    f.write(line)

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        logging.info(f'-- Generated {self.path}')
        if not self.setup.args.silent and not self.setup.args.verbose: print(
            f'   * Created '
            f'{self.path.split(self.setup.staging_directory)[-1]}.')

        self.validate()

        if self.setup.diff:
            self.compare()
            logging.info('')

        return

    def validate(self):
        '''
        The label is validated by checking that all the products are present
        and by comparing the Inventory Product with the previous version and
        if it does not exist with the sample inventory product.

        :return:
        '''

        logging.info(f'-- Validating {self.name}...')

        #
        # Check that all the products are listed in the collection product.
        #
        logging.info('      Check that all the products are in the '
                     'collection.')

        for product in self.collection.product:
            product_found = False
            with open(self.path, 'r') as c:
                for line in c:
                    if product.lid in line:
                        product_found = True
                if not product_found:
                    logging.error(f'      Product {product.lid} not found. '
                                  f'Consider increment re-generation.')

        logging.info('      OK')
        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        return

    def compare(self):
        '''
        The label is compared the Inventory Product with the previous
        version and
        if it does not exist with the sample inventory product.

        :return:
        '''
        mission_accronym = self.setup.mission_accronym
        logging.info(f'-- Comparing '
                     f'{self.name.split(f"{mission_accronym}_spice/")}'
                     f'...')

        #
        # Use the prior version of the same product, if it does not
        # exist use the sample.
        #
        if self.path_current:

            fromfile = self.path_current
            tofile = self.path
            dir = self.setup.working_directory

            compare_files(fromfile, tofile, dir, self.setup.diff)

        else:

            logging.warning('-- Comparing with InSight test inventory '
                            'product.')
            fromfiles = glob.glob(f'{self.setup.root_dir}tests/data/insight/'
                                  f'insight_spice/{self.collection.type}/'
                                  f'collection_{self.collection.name}'
                                  f'_inventory_*.csv')
            fromfiles.sort()
            fromfile = fromfiles[-1]
            tofile = self.path
            dir = self.setup.working_directory

            compare_files(fromfile, tofile, dir, self.setup.diff)

        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        return

    def write_index(self):

        line = f'Step {self.setup.step} - Generation of index files'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        cwd = os.getcwd()
        os.chdir(self.setup.staging_directory)

        list = f'{self.setup.working_directory}/' \
               f'{self.collection.list.complete_list}'
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
        index = f'{self.setup.staging_directory}/index.tab'
        index_lbl = f'{self.setup.staging_directory}/index.lbl'
        dsindex = f'{self.setup.staging_directory}/dsindex.tab'
        dsindex_lbl = f'{self.setup.staging_directory}/dsindex.lbl'

        #
        # Add CRS to the index files.
        #

        if self.setup.pds_version == '4':
            os.remove(index)
            os.remove(index_lbl)

            dsindex = \
                shutil.move(dsindex, self.setup.staging_directory + '/../')
            dsindex_lbl = \
                shutil.move(dsindex_lbl, self.setup.staging_directory +
                            '/../')

            logging.info('-- Adding CRs to index files.')
            logging.info('')
            add_crs_to_file(dsindex)
            add_crs_to_file(dsindex_lbl)

            self.index = ''
            self.index_lbl = ''
            self.dsindex = dsindex
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
                    current_index = self.setup.final_directory + os.sep + \
                                    index.split(os.sep)[-1]
                    compare_files(index, current_index,
                                  self.setup.working_directory, 'all')
                except:
                    logging.warning(f'-- File to compare with does not '
                                    f'exist: {index}')

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


class SpicedsProduct(object):

    def __init__(self, setup, collection):

        self.setup = setup
        self.collection = collection
        self.new_product = True
        spiceds = self.setup.spiceds

        line = f'Step {self.setup.step} - Processing spiceds file'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        if not spiceds:
            logging.info('-- No spiceds file provided.')

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

                if not spiceds:
                    logging.info(f'-- Previous spiceds found: {latest_spiceds}')
                    self.generated = False
                    return

            except:
                logging.warning('-- No previous version of spiceds_v*.html '
                                'file found.')
                if not spiceds:
                    error_message('spiceds not provided and not available '
                                  'from previous releases')
                self.version = 1
                self.latest_spiceds = ''
        else:
            self.version = 1
            self.latest_spiceds = ''
            if not spiceds:
                error_message('spiceds not provided and not available from '
                              'previous releases')

        self.name = 'spiceds_v{0:0=3d}.html'.format(self.version)
        self.path = setup.staging_directory + os.sep + collection.name \
                    + os.sep + self.name
        self.mission = setup

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        logging.info(f'-- spiceds file provided as input moved to staging '
                     f'area as {self.name}')

        #
        # The provuided spiceds file is moved to the staging area.
        #
        shutil.copy2(spiceds, self.path)

        #
        # The appropriate line endings are provided to the spiceds file,
        # If line endings did not have Carriage Return (CR), they are
        # added and the file timestamp is updated. Note that if the file
        # already had CRs the original timestamp is preserved.
        #
        self.check_cr()

        #
        # Kernels are already generated products but Inventories are not.
        #
        Product.__init__(self)

        #
        # Check if the spiceds has not changed.
        #
        self.generated = self.check_product()

        #
        # Validate the product by comparing it and then generate the label.
        #
        if self.generated:
            self.compare()

            self.label = DocumentPDS4Label(setup, collection, self)

        return

    def product_lid(self):

        return f'{self.setup.logical_identifier}:document:spiceds'

    def product_vid(self):

        return '{}.0'.format(int(self.version))

    def check_cr(self):

        #
        # We add the date to the temporary file to have a unique name.
        #
        today = date.today()
        time_string = today.strftime('%Y-%m-%dT%H:%M:%S.%f')
        temporary_file = f'{self.path}.{time_string}'

        with open(self.path, "r") as s:
            with open(temporary_file, "w+") as t:
                for line in s:
                    line = add_carriage_return(line)
                    t.write(line)

        #
        # If CRs have been added then we update the spiceds file.
        # The operator is notified.
        #
        if filecmp.cmp(temporary_file, self.path):
            os.remove(temporary_file)
        else:
            shutil.move(temporary_file, self.path)
            logging.info('-- Carriage Return has been added to lines in '
                         'the spiceds file.')

        return

    def check_product(self):

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
                    if 'Last update' not in line and line.strip() != \
                            '-' and line.strip() != '-\n':
                        generate_spiceds = True

            if not generate_spiceds:
                os.remove(self.path)
                logging.warning('-- spiceds document does not need to be '
                                'updated.')
                logging.warning('')

        return generate_spiceds

    def compare(self):

        #
        # Compare spiceds with latest. First try with previous increment.
        #
        try:

            val_spd_path = f'{self.setup.final_directory}/' \
                           f'{self.setup.mission_accronym}_spice/' + \
                           f'document'

            val_spds = glob.glob(f'{val_spd_path}/spiceds_v*.html')
            val_spds.sort()
            val_spd = val_spds[-1]


        except:

            #
            # If previous increment does not work, compare with InSight example.
            #
            logging.warning(f'-- No other version of {self.name} has been '
                            f'found.')
            logging.warning(f'-- Comparing with default InSight example.')

            val_spd = f'{self.setup.root_dir}tests/data/spiceds_insight.html'

        logging.info('')
        fromfile = val_spd
        tofile = self.path
        dir = self.setup.working_directory

        compare_files(fromfile, tofile, dir, 'all')

        if self.setup.interactive:
            input(">> Press enter to continue...")

        # TODO: Implement a smart comparison of spiceds files in such way
        # that a warning is provided if something looks fishy (type of file
        # not present for example)

        return


class ReadmeProduct(Product):

    def __init__(self, setup, bundle):

        line = f'Step {setup.step} - Generation of bundle products'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        self.name = 'readme.txt'
        self.bundle = bundle
        self.path = setup.staging_directory + os.sep + self.name
        self.setup = setup
        self.vid = bundle.vid
        self.collection = Object()
        self.collection.name = ''

        path = self.setup.final_directory + \
               f'/{self.setup.mission_accronym}_spice/readme.txt'

        if os.path.exists(path):
            self.path = path
            logging.info('-- Readme file already exists in final area.')
        else:
            logging.info('-- Generating readme file...')
            self.write_product()

        Product.__init__(self)

        logging.info('')

        #
        # Now we change the path for the difference of the name in the label
        #
        self.path = setup.staging_directory + os.sep + bundle.name

        logging.info('-- Generating bundle label...')
        self.label = BundlePDS4Label(setup, self)

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return

    def write_product(self):

        line_length = 0

        if not os.path.isfile(self.path):
            with open(self.path, "w+") as f:
                for line in fileinput.input(self.setup.root_dir +
                                            '/templates/template_readme.txt'):
                    if '$SPICE_NAME' in line:
                        line = line.replace('$SPICE_NAME',
                                            self.setup.readme['spice_name'])
                        line_length = len(line) - 1
                        line = add_carriage_return(line)
                        f.write(line)
                    elif '$UNDERLINE' in line:
                        line = line.replace('$UNDERLINE', '=' * line_length)
                        line_length = len(line) - 1
                        line = add_carriage_return(line)
                        f.write(line)
                    elif '$OVERVIEW' in line:
                        overview = self.setup.readme['overview']
                        for line in overview.split('\n'):
                            line = ' ' * 3 + line.strip() + '\n'
                            line = add_carriage_return(line)
                            f.write(line)
                    elif '$COGNISANT_PERSONS' in line:
                        cognisant = self.setup.readme['cognisant_persons']
                        for line in cognisant.split('\n'):
                            line = ' ' * 3 + line.strip() + '\n'
                            line = add_carriage_return(line)
                            f.write(line)
                    else:
                        line_length = len(line) - 1
                        line = add_carriage_return(line)
                        f.write(line)

        logging.info('-- readme file generated.')
        if not self.setup.args.silent and not self.setup.args.verbose: print(
            f'   * readme file generated.')

        return


class Object(object):
    pass
