import shutil
import datetime
import logging
import glob
import json
import re
import os
from naif_pds4_bundle.utils import extension2type
from naif_pds4_bundle.utils import check_list_duplicates
from naif_pds4_bundle.utils import fill_template
from naif_pds4_bundle.utils import check_consecutive
from naif_pds4_bundle.utils import compare_files
from naif_pds4_bundle.classes.log import error_message


class List(object):

    def __init__(self, setup):
        self.files = []
        self.name = type
        self.setup = setup

    def add(self, element):
        self.files.append(element)


class KernelList(List):

    def __init__(self, setup):

        line = f'Step {setup.step} - Kernel List generation'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        List.__init__(self, setup)

        #
        # Object attributes to be replaced in template
        #
        self.CURRENTDATE = str(datetime.datetime.now())[:10]
        self.OBS = setup.observer
        self.AUTHOR = setup.producer_name
        self.PHONE = setup.producer_phone
        self.EMAIL = setup.producer_email
        self.DATASETID = setup.dataset_id
        self.VOLID = setup.volume_id.lower()
        self.RELID = f'{int(setup.release):04d}'
        self.RELDATE = setup.release_date

        self.template = f'{setup.root_dir}/templates/template_kernel_list.txt'
        self.read_config()

        return

    def add(self, kernel):

        List.add(self, kernel)

        return

    def read_config(self):

        json_config = self.setup.kernel_list_config

        #
        # Build a list of computed regular expressions from the JSON config
        #
        re_config = []
        for pattern in json_config:
            re_config.append(re.compile(pattern))

        self.re_config = re_config
        #
        # Also store it in setup for later use in meta-kernel description
        # generation.
        #
        self.setup.re_config = re_config
        self.json_config = json_config

        json_formatted_str = json.dumps(self.json_config, indent=2)
        self.json_formatted_lst = json_formatted_str.split('\n')

        return

    def read_plan(self, plan):

        kernels = []

        #
        # Add mapping kernel patterns in list.
        #
        patterns = []
        for pattern in self.json_config:
            patterns.append(pattern)
            if 'mapping' in self.json_config[pattern]:
                patterns.append(self.json_config[pattern]['mapping'])


        with open(plan, 'r') as f:
            for line in f:
                ker_matched = False
                for pattern in patterns:
                    if re.search(pattern, line):
                        ker_line = re.search(pattern, line)
                        kernels.append(ker_line.group(0))
                        ker_matched = True
                if not ker_matched:
                    #
                    # Add the  orbnum files that need to be added.
                    # Match the pattern with the file.
                    #
                    if hasattr(self.setup, 'orbnum'):
                        for orb in self.setup.orbnum:
                            pattern = orb['pattern']
                            if re.search(pattern, line):
                                ker_line = re.search(pattern, line)
                                kernels.append(ker_line.group(0))
                                ker_matched = True
                    #
                    # Display the lines that have not been match unless
                    # they only contain blank spaces.
                    #
                    if not ker_matched and line.strip():
                        logging.warning('-- The following Plan line has '
                                        'not been matched:')
                        logging.warning(f'   {line[0:-1]}')

        #
        # Report the kernels that will be included in the Kernel List
        #
        logging.info(f'-- Reporting the products in Plan:')

        for kernel in kernels:
            logging.info(f'     {kernel}')

        logging.info("")

        self.kernel_list = kernels

        return

    def write_plan(self):

        kernels = []

        logging.info(f'-- Generate archiving plan from kernels directories:')
        for dir in self.setup.kernels_directory:
            logging.info(f'   {dir}')

        plan_name = f'{self.setup.mission_acronym}_release_' \
                    f'{int(self.setup.release):02d}.plan'

        kernels_in_dir = []
        for dir in self.setup.kernels_directory:
            kernels_in_dir += glob.glob(f'{dir}/**/*.*',
                                   recursive=True)
        #
        # Filter out the meta-kernels from the automatically generated
        # list.
        #
        kernels_in_dir = [item for item in kernels_in_dir if 
                          '.tm' not in item]
        kernels_in_dir.sort()
            
        #
        # Filter the kernels with the patterns in the kernel list from the
        # configuration. The patterns are present in the json_config
        # attribute dictionary.
        #
        patterns = []
        for pattern in self.json_config:
            patterns.append(pattern)
            if 'mapping' in self.json_config[pattern]:
                patterns.append(self.json_config[pattern]['mapping'])

        for kernel in kernels_in_dir:
            for pattern in patterns:
                if re.match(pattern, kernel.split(os.sep)[-1]):
                    kernels.append(kernel.split(os.sep)[-1])

        #
        # Sort the meta-kernels that need to be added.
        #
        # First we look into the configuration file. If a meta-kernel is 
        # present, it is the one that will be used.
        #
        if hasattr(self.setup, 'mk_inputs'):
            if not isinstance(self.setup.mk_inputs['file'], list):
                mks = [self.setup.mk_inputs['file']]
            else:
                mks = self.setup.mk_inputs['file']
            for mk in mks:
                mk_new_name = mk.split(os.sep)[-1]
                mk_path = os.getcwd() + os.sep + mk
                if os.path.isfile(mk_path):
                    kernels.append(mk_new_name)
                else:
                    error_message(f'Meta-kernel provided via configuration '
                                  f'{mk_new_name} does not exist')
        else:
            #
            # If no meta-kernel was provided via configuration, try to 
            # infer the on that needs to be generated.
            # 
            kernels_in_dir = glob.glob(f'{self.setup.final_directory}/**/*',
                                       recursive=True)
            mks_in_dir = []
            for mk in kernels_in_dir:
                if '/mk/' in mk and '.tm' in mk.lower():
                    mks_in_dir.append(mk.split(os.sep)[-1])
    
            mks_in_dir.sort()
    
            if not mks_in_dir:
                logging.warning(f'-- No former meta-kernel found to generate '
                              f'meta-kernel for the list.')
            else:
    
                mk_new_name = ''
                
                #
                # If kernels are present, a meta-kernel might be able to be 
                # generated from the information of the bundle.
                #
                if kernels:
                    for pattern in patterns:
                        mk_name = mks_in_dir[-1]
                        if re.match(pattern, mk_name):
                            version = re.findall(r'_v[0-9]+', mk_name)[0]
                            new_version = \
                                '_v' + \
                                str(int(version[2:]) + 1).zfill(len(version) - 2)
                            mk_new_name = \
                                f'{mk_name.split(version)[0]}' \
                                f'{new_version}{mk_name.split(version)[-1]}'
        
                            logging.warning(f'-- Plan will include {mk_new_name}')
                            kernels.append(mk_new_name)
    
                if not mk_new_name:
                    logging.error(f'-- No former meta-kernel found to generate '
                                  f'meta-kernel for the list.')

        #
        # Add possible orbnum files.
        #  
        if hasattr(self.setup, 'orbnum_directory'):
            orbnums_in_dir = glob.glob(f'{self.setup.orbnum_directory}/*')
            for orbnum_in_dir in orbnums_in_dir:
                for orbnum in self.setup.orbnum:
                    if re.match(
                            orbnum['pattern'], 
                            orbnum_in_dir.split(os.sep)[-1]):
                        logging.warning(
                            f'-- Plan will include {orbnum_in_dir}')
                        kernels.append(orbnum_in_dir.split(os.sep)[-1])
            
        #
        # The kernel list is complete.
        #
        with open(
                self.setup.working_directory + os.sep + plan_name, 'w') as p:
            for kernel in kernels:
                p.write(f'{kernel}\n')

        if not kernels:
            logging.info("")
            logging.warning(f'-- No kernels will be added to the increment.')
            logging.info("")

            self.kernel_list = kernels
        
            return

        logging.info("")
        logging.info(f'-- Reporting the products in Plan:')

        #
        # Report the kernels that will be included in the Kernel List
        #
        for kernel in kernels:
            logging.info(f'     {kernel}')

        logging.info("")

        self.kernel_list = kernels

        return

    #
    # The list is not an archival product, therefore it is not generated
    # by any of the product classes.
    #
    def write_list(self):

        list_name = f'{self.setup.mission_acronym}_release_' \
                    f'{int(self.setup.release):02d}.kernel_list'

        list_dictionary = vars(self)

        fill_template(self, self.setup.working_directory + os.sep +
                      list_name, list_dictionary)

        with open(self.setup.working_directory + os.sep +
                  list_name, "a+") as f:

            for kernel in self.kernel_list:
                ker_added_to_list = False
                #
                # Find the correspondence of the filename in the JSON file
                #
                for pattern in self.re_config:

                    if pattern.match(kernel):

                        #
                        # Description is the only mandatory field.
                        #
                        description = \
                            self.json_config[pattern.pattern]['description']
                        try:
                            options = \
                                self.json_config[
                                    pattern.pattern]['mklabel_options']
                        except:
                            options = ''
                        try:
                            patterns = \
                                self.json_config[pattern.pattern]['patterns']
                        except:
                            patterns = False
                        try:
                            mapping = \
                                self.json_config[pattern.pattern]['mapping']
                        except:
                            mapping = ''

                        #
                        # `options' and `descriptions' require to
                        # substitute parameters derived from the filenames
                        # themselves.
                        #
                        if patterns:
                            for el in patterns:
                                if ("$" + el) in description or \
                                        ("$" + el) in mapping:
                                    value = patterns[el]

                                    #
                                    # There are two distinct patterns:
                                    #    * extracted form the filename
                                    #    * defined in the configuration file.
                                    #
                                    if '@pattern' in patterns[el] and \
                                            patterns[el]['@pattern'].lower() \
                                            == 'kernel':
                                        #
                                        # When extracted from the filename,
                                        # the keyword  is matched in between
                                        # patterns.
                                        #

                                        #
                                        # First Turn the regex set into a
                                        # single character to be able to know
                                        # were int he filename is.
                                        #
                                        patt_ker = value['#text'].replace(
                                            '[0-9]', '$')
                                        patt_ker = patt_ker.replace(
                                            '[a-z]', '$')
                                        patt_ker = patt_ker.replace(
                                            '[A-Z]', '$')
                                        patt_ker = patt_ker.replace(
                                            '[a-zA-Z]', '$')

                                        #
                                        # Split the resulting pattern to build
                                        # up the indexes to extract the value
                                        # from the kernel name.
                                        #
                                        patt_split = patt_ker.split(f'${el}')

                                        #
                                        # Create a list with the length of
                                        # each part.
                                        #
                                        indexes = []
                                        for element in patt_split:
                                            indexes.append(len(element))

                                        #
                                        # Extract the value with the index
                                        # from the kernel
                                        # name.
                                        #
                                        # TODO: This indexes work because the mapping kernel and the resulting kernel are in the same place!
                                        if len(indexes) == 2:
                                            value = \
                                                kernel[
                                                indexes[0]:
                                                len(kernel) - indexes[1]]
                                            if patterns[
                                                el]['@pattern'].isupper():
                                                value = value.upper()
                                        else:
                                            error_message('Kernel pattern '
                                                'not adept to write '
                                                'description. Remember a '
                                                'metacharacter cannot start '
                                                'or finish a kernel pattern')
                                    else:
                                        #
                                        # For non-kernels the value is based
                                        # on the value within the tag that
                                        # needs to be provided by the user;
                                        # there is no way this can be done
                                        # automatically.
                                        #

                                        #
                                        # First we convert into a list in
                                        # case there is just one
                                        #
                                        patterns_el = patterns[el]
                                        if not isinstance(patterns_el, list):
                                            patterns_el = [patterns_el]
                                        for val in patterns_el:
                                            try:
                                                if kernel == val['@value']:
                                                    value = val['#text']
                                            except KeyError:
                                                error_message(f'Error '
                                                      f'generating kernel'
                                                      f' list with {kernel}. '
                                                      f'Consider reviewing '
                                                      f'your NPB setup')
                                                
                                        if isinstance(value, list) or \
                                                isinstance(value, dict):
                                            error_message(f'-- Kernel {kernel}'
                                                ' description could not be '
                                                'updated with pattern')

                                    description = \
                                        description.replace('$' + el, value)

                        if options:
                            for option in options.split():
                                if ('$' + 'PHASES') in option:
                                    if list(self.setup.phases.keys())[0]:
                                        # TODO: Substitute block by mission
                                        #  phase searching function
                                        options = \
                                            options.replace(
                                                '$' + 'PHASES',
                                                self.setup.phases
                                                ['phase']['@name'])                        

                        #
                        # Reformat the description, given that format of the
                        # XML file is not restrictive (spaces or newlines 
                        # might be present).
                        #
                        description = description.replace('\n', ' ')
                        description = ' '.join(description.split())

                        if self.setup.pds_version == '3':
                            kerdir = 'data/' + extension2type(kernel)
                        else:
                            kerdir = 'spice_kernels/' + extension2type(kernel)

                        if not options: options = ''

                        f.write(f'FILE             = {kerdir}/{kernel}\n')
                        f.write(f'MAKLABEL_OPTIONS = {options}\n')
                        f.write(f'DESCRIPTION      = {description}\n')

                        if mapping:
                            #
                            # TODO: We loop all the patterns that have been mapped in the mapping kernel as well.
                            # Currently only one is supported which works for SCLK.
                            #
                            logging.info(f'-- Mapping {kernel}')
                            f.write(f'MAPPING          = '
                                    f'{mapping.replace("$" + el, value)}\n')

                        ker_added_to_list = True

                if not ker_added_to_list:
                    f.write(f'FILE             = miscellaneous/orbnum/'
                            f'{kernel}\n')
                    f.write(f'MAKLABEL_OPTIONS = VOID\n')
                    f.write(f'DESCRIPTION      = VOID\n')

        self.list_name = list_name

        self.validate()

        return

    def read_list(self, kerlist):
        '''
        Note that the format that the kernel list has to follow is very 
        strict, including no whitespace at the end of each line and Line-feed
        EOL.
        :param kerlist: 
        :return: 
        '''
        
        kernel_list  = f'{self.setup.working_directory}/' \
                       f'{self.setup.mission_acronym}_release_' \
                       f'{int(self.setup.release):02d}.kernel_list'

        try:
            shutil.copy2(kerlist, kernel_list)
        except shutil.SameFileError: 
            pass
        
        self.list_name = kernel_list.split(os.sep)[-1]
        
        #
        # Generate the kernel list attribute, necessary for the validation.
        #
        kernels = []
        with open(kernel_list, 'r') as l:
            for line in l:
                if 'FILE             =' in line:
                    kernels.append(line.split(os.sep)[-1][:-1])
        
        self.kernel_list = kernels
        
        self.validate()
        
        return
        

    def write_complete_list(self):

        line = f'Step {self.setup.step} - Generation of complete kernel list'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        kernel_lists = glob.glob(self.setup.working_directory + os.sep + \
                                 f'{self.setup.mission_acronym}_release*'
                                 f'.kernel_list')

        #
        # Sort list in inverse order in such way that the DATASETID is
        # obtained from the header of the latest list.
        #
        kernel_lists.sort(reverse=True)

        complete_list = f'{self.setup.mission_acronym}_complete.kernel_list'

        release_list = []
        with open(
                self.setup.working_directory + os.sep + complete_list, 'w+') \
                as c:
            for kernel_list in kernel_lists:
                logging.info(f'-- Adding {kernel_list}')
                release_list.append(
                    int(kernel_list.replace('_', '.').split('.')[-3]))
                with open(kernel_list, 'r') as l:
                    for line in l:
                        c.write(line)

        if not check_consecutive(release_list):
            logging.warning(f'-- Incomplete Kernel lists available: '
                            f'{release_list}')

        self.complete_list = complete_list

        self.validate_complete()

        return

    # ------------------------------------------------------------------------
    #
    # Validation of the list is performed such that:
    #
    # -- To check that the list has the same number of FILE, MAKLABEL_OPTIONS,
    #    and DESCRIPTION entries.
    #
    # -- To check list against plan
    #
    # -- To check that list for duplicate files
    #
    # -- To check that all files listed in the list are on the ops directory
    #
    # -- To check that the files are not in the archive
    #
    # -- To check all the MAKLABL_OPTIONS used
    #
    # -- To check that the complete kernel list has no duplicates
    #
    # -----------------------------------------------------------------------
    def validate(self):

        present = False

        num_file = 0
        num_opti = 0
        num_desc = 0

        ker_in_list = []
        opt_in_list = []

        with open(self.setup.working_directory + os.sep +
                  self.list_name, 'r') as l:

            #
            # Check that the list has the same number of FILE,
            # MAKLABEL_OPTIONS, and DESCRIPTION entries
            #
            for line in l:

                if ('FILE' in line) and (line.split('=')[-1].strip()):
                    num_file += 1
                    #
                    # We add kernels to compare plan and list and to look
                    # for duplicates.
                    #
                    ker_in_list.append(line.split('/')[-1].strip())

                elif ('OPTIONS' in line):
                    num_opti += 1
                    #
                    # We add options to display and compare to template
                    #
                    options = line.split('=')[-1].split()
                    for option in options:
                        if option != 'None':
                            opt_in_list.append(option)


                elif ('DESCRIPTION' in line) and \
                        (line.split('=')[-1].strip()):
                    num_desc += 1

            if (num_file != num_opti) or (num_opti != num_desc):
                error = 'List does not have the same number of entries'
                logging.critical(f'{error} for:')
                logging.critical(f'   FILE             ({num_file})')
                logging.critical(f'   MAKLABEL_OPTIONS ({num_opti})')
                logging.critical(f'   DESCRIPTION      ({num_desc})')
                logging.critical('')

                logging.critical(
                    f'-- Display {self.setup.mission_name} kernel list '
                    f'configuration file to double-check.')
                for line in self.json_formatted_lst:
                    logging.info(line)
                logging.critical('')

                raise Exception(error)

            #
            # Check list against plan
            #
            for ker in ker_in_list:
                if ker not in self.kernel_list:
                    error_message(f'   {ker} not in list')

            #
            # Check list for duplicate entries
            #
            if check_list_duplicates(ker_in_list):
                error_message('List contains duplicates')

            #
            # Check that all files listed are available in OPS area;
            # This does not raise an error but only a warning.
            #
            logging.info(f'-- Checking that kernels are present in: ')
            
            for dir in self.setup.kernels_directory:
                logging.info(f'   {dir}')
            
            present = False
            all_present = True
            for ker in ker_in_list:
                for dir in self.setup.kernels_directory:
                    #
                    # We cannot assume that the file is under a certain 
                    # directory, it can be in any sub-directory.
                    #
                    file = [os.path.join(root, name)
                            for root, dirs, files in os.walk(dir)
                            for name in files
                            if name == ker]            
                    if file:
                        present = True
                if not present:
                    if '.tm' in ker:
                        logging.info(f'     {ker} not present as expected.')
                    else:
                        logging.warning(f'     {ker} not present. Kernel might '
                                      f'be mapped.')
                        all_present = False
            if all_present:
                logging.info('     All kernels present in directory.')
            logging.info('')

            #
            # Check that no file is in the final area.
            #
            present = False
            logging.info(f'-- Checking that kernels are present in '
                         f'{self.setup.final_directory}:')
            for ker in ker_in_list:
                if os.path.isfile(self.setup.final_directory + \
                                  f'/{self.setup.mission_acronym}_spice/'
                                  f'spice_kernels/' + \
                                  extension2type(ker) + os.sep + ker):
                    present = True
                    logging.error(f'     {ker} present.')
            if not present:
                logging.info('     No kernels present in final area.')
            logging.info('')

            #
            # Display all the MAKLABL_OPTIONS used
            #
            opt_in_list = list(dict.fromkeys(opt_in_list))
            opt_in_list.sort()
            logging.info(f'-- Display all the MAKLABEL_OPTIONS:')
            for option in opt_in_list:
                logging.info(f'     {option}')
            logging.info('')

            #
            # The PDS Mission Template file is not required for PDS4
            #
            # if self.setup.pds_version == '3':
            #    logging.info('-- Check that all template tags used in the list are present in template:')
            #    template = self.setup.root_dir + f'/config/{self.setup.mission_acronym }_mission_template.pds'
            #    with open(template, 'r') as o:
            #        template_lines = o.readlines()
            #
            #
            #    for option in opt_in_list:
            #        present = False
            #        for line in template_lines:
            #            if '--' + option in line:
            #                present = True
            #        if present:
            #            logging.info(f'     {option} is present.')
            #        else:
            #            error_message(f'{option} not in template.')
            #
            #    logging.info('')


            #
            # Check complete list for duplicate entries
            #
            logging.info('-- Checking for duplicates in complete kernel '
                         'list:')

            kernel_lists = glob.glob(self.setup.working_directory + os.sep + \
                                     f'{self.setup.mission_acronym}_release*'
                                     f'.kernel_list')
            kernel_lists.sort()

            ker_in_list = []
            for kernel_list in kernel_lists:

                with open(kernel_list, 'r') as l:

                    #
                    # Check that the list has the same number of FILE,
                    # MAKLABEL_OPTIONS, and DESCRIPTION entries
                    #
                    logging.info(f'     Adding {kernel_list} in check.')

                    for line in l:
                        if ('FILE' in line) and (line.split('=')[-1].strip()):
                            ker_in_list.append(line.split('/')[-1].strip())

            if check_list_duplicates(ker_in_list):
                error_message('List contains duplicates')
            else:
                logging.info(f'     List contains no duplicates.')
            logging.info('')

        if self.setup.diff and self.setup.increment:
            #
            # Compare list with previous list
            #
            logging.info('-- Comparing current list with previous list:')
    
            logging.info('')
            fromfile = kernel_lists[-1]
            try:
                tofile = kernel_lists[-2]
                dir = self.setup.working_directory
                compare_files(fromfile, tofile, dir, self.setup.diff)
            except:
                logging.error('-- Previous list not available.')

        return

    def validate_complete(self):

        present = False

        num_file = 0
        num_opti = 0
        num_desc = 0

        ker_in_list = []
        opt_in_list = []

        with open(self.setup.working_directory + os.sep +
                  self.complete_list, 'r') as l:

            #
            # Check that the list has the same number of FILE,
            # MAKLABEL_OPTIONS, and DESCRIPTION entries
            #
            logging.info('-- Checking list number of entries coherence:')

            for line in l:

                if ('FILE' in line) and (line.split('=')[-1].strip()):
                    num_file += 1
                    #
                    # We add kernels to compare plan and list and to look
                    # for duplicates.
                    #
                    ker_in_list.append(line.split('/')[-1].strip())

                elif ('OPTIONS' in line):
                    num_opti += 1
                    #
                    # We add options to display and compare to template
                    #
                    options = line.split('=')[-1].split()
                    for option in options:
                        opt_in_list.append(option)


                elif ('DESCRIPTION' in line) and (line.split('=')[-1].strip()):
                    num_desc += 1

            if (num_file != num_opti) or (num_opti != num_desc):
                error = 'List does not have the same number of entries'
                logging.critical(f'{error} for:')
                logging.critical(f'   FILE             ({num_file})')
                logging.critical(f'   MAKLABEL_OPTIONS ({num_opti})')
                logging.critical(f'   DESCRIPTION      ({num_desc})')
                logging.critical('')

                logging.critical(
                    f'-- Display {self.setup.mission_name} kernel list '
                    f'configuration file to double-check.')
                for line in self.json_formatted_lst:
                    logging.info(line)
                logging.critical('')

                raise Exception(error)
            else:
                logging.info(f'     PASS with total of {num_file} entries.')
                logging.info('')

            #
            # Check list for duplicate entries
            #
            logging.info('-- Checking for duplicates in kernel list:')
            if check_list_duplicates(ker_in_list):
                error_message('List contains duplicates')
            else:
                logging.info(f'     List contains no duplicates.')
            logging.info('')

            #
            # Display all the MAKLABL_OPTIONS used
            #
            opt_in_list = list(dict.fromkeys(opt_in_list))
            opt_in_list.sort()
            logging.info(f'-- Display all the MAKLABEL_OPTIONS:')
            for option in opt_in_list:
                logging.info(f'     {option}')
            logging.info('')

            #
            # The PDS Mission Template file is not required for PDS4
            #
            if self.setup.pds_version == '3':
                logging.info('-- Check that all template tags used in the '
                             'list are present in template:')
                template = \
                    self.setup.root_dir + \
                    f'/config/{self.setup.mission_acronym}' \
                    f'_mission_template.pds'
                with open(template, 'r') as o:
                    template_lines = o.readlines()

                for option in opt_in_list:
                    present = False
                    for line in template_lines:
                        if '--' + option in line:
                            present = True
                    if present:
                        logging.info(f'     {option} is present.')
                    else:
                        error_message(f'{option} not in template.')

                logging.info('')

        return
