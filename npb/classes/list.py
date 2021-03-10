import fileinput
import datetime
import logging
import json
import re
import os

from npb.utils.files import extension2type
from npb.utils.files import check_list_duplicates
from npb.utils.files import fill_template
from npb.classes.log import error_message

class List(object):

    def __init__(self, setup):

        self.files = []
        self.name = type
        self.setup = setup


    def add(self, element):
        
        self.files.append(element)


class KernelsList(List):

    def __init__(self, setup, plan):

        List.__init__(self, setup)

        #
        # Object attributes to be replaced in template
        #
        self.CURRENTDATE  = str(datetime.datetime.now())[:10]
        self.SC           = setup.spacecraft
        self.AUTHOR       = setup.author
        self.PHONE        = setup.phone
        self.EMAIL        = setup.email
        self.VOLID        = setup.volume_id
        self.RELID        = f'{int(setup.release):04d}'
        self.RELDATE      = setup.release_date

        self.template = setup.root_dir + '/etc/template_kernel_list.txt'
        self.read_config()
        self.kernel_list = self.read_plan(plan)
        self.write_kernel_list()

        self.validate()

        return
    

    def add(self, kernel):

        List.add(self, kernel)

        return


    def read_config(self):

        config = self.setup.root_dir + f'/config/{self.setup.mission_accronym }_kernel_list.json'
        with open(config, 'r') as f:
            json_config = json.load(f)

        #
        # Build a list of compuled regular expressions from the JSON config
        #
        re_config = []
        for pattern in json_config:
            re_config.append(re.compile(pattern))

        self.re_config = re_config
        self.json_config = json_config

        json_formatted_str = json.dumps(self.json_config, indent=2)
        json_formatted_lst = json_formatted_str.split('\n')

        logging.info(f'-- Display {self.setup.mission_name} kernel list configuration file:')
        for line in json_formatted_lst:
            logging.info(line)
        logging.info('')

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        return


    def read_plan(self, plan):

        kernels = []

        logging.info(f'-- Reporting the lines in Plan that do not contain products:')

        with open(plan, 'r') as f:
            for line in f:
                if '\\' in line:
                    kernels.append(line.split('\\')[0].strip())

                #
                # Report the lines that are not appended in the kernels list
                #
                else:
                    if line.strip():
                        logging.info(line[:-1])

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        logging.info("")
        logging.info(f'-- Reporting the products in Plan:')

        #
        # Report the kernels that will be included in the Kernel List
        #
        for kernel in kernels:
            logging.info(f'     {kernel}')

        logging.info("")
        if self.setup.interactive:
            input(">> Press Enter to continue...")


        return kernels


    #
    # The list is not an archival product, therefore it is not generated
    # by any of the product classes.
    #
    def write_kernel_list(self):

        list_name = f'{self.setup.mission_accronym}_release_{self.setup.release}.kernel_list'

        list_dictionary = vars(self)

        fill_template(self, list_name, list_dictionary)

        with open(list_name, "a+") as f:

            for kernel in self.kernel_list:

                #
                # Find the correspondence of the filename in the JSON file
                #
                for pattern in self.re_config:

                    if pattern.match(kernel):

                        options = self.json_config[pattern.pattern][0]['mklabel_options']
                        description = self.json_config[pattern.pattern][0]['description']
                        try:
                            patterns = self.json_config[pattern.pattern][0]['patterns'][0]
                        except:
                            patterns = False

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
                                    # We test if there is an indication for
                                    # uppercase or lowercase for the pattern
                                    #
                                    try:
                                        (upper, value) = value.split(',')
                                    except:
                                        logging.warning(f"   No upper/lower indication for {el} in {kernel}")
                                        upper = False
                                        pass

                                    (idx_start, idx_stop) = value.split('->')
                                    idx_start = int(idx_start)
                                    try:
                                        idx_stop = int(idx_stop)
                                    except:
                                        idx_stop = kernel[idx_start:].find(idx_stop)
                                        idx_stop = idx_stop[1:]

                                    value = kernel[idx_start:idx_stop]

                                    if upper:
                                        description = description.replace('$' + el, value.upper())
                                    else:
                                        description = description.replace('$' + el, value)


                        for option in options.split():
                            if ('$' + 'PHASES') in option:
                                if self.setup.phase:
                                    options = options.replace( '$' + 'PHASES', self.setup.phase)
# -----------------------------------------------------------------------------
# TODO: Substitute block by mission phase searching function

# -----------------------------------------------------------------------------
                        kerdir = 'data/' + extension2type(kernel)

                        f.write(f'FILE             = {kerdir}/{kernel}\n')
                        f.write(f'MAKLABEL_OPTIONS = {options}\n')
                        f.write(f'DESCRIPTION      = {description}\n')

                        self.list_name = list_name

        return

    # ------------------------------------------------------------------------
    #
    # Validation of the list is perfomed such that:
    #
    # To check that the list has the same number of FILE, MAKLABEL_OPTIONS,
    # and DESCRIPTION entries.
    #
    # To check list against plan
    #
    # To check that list for duplicate files
    #
    # To check that all files listed in the list are on the ops directory
    #
    # To check all the MAKLABL_OPTIONS used
    #
    # -----------------------------------------------------------------------
    def validate(self):

        present = False

        num_file = 0
        num_opti = 0
        num_desc = 0

        ker_in_list = []
        opt_in_list = []

        with open(self.list_name, 'r') as l:


            #
            # Check that the list has the same number of FILE, MAKLABEL_OPTIONS,
            # and DESCRIPTION entries
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

                elif ('OPTIONS' in line) and (line.split('=')[-1].strip()):
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
                logging.error(f'{error} for:')
                logging.error(f'   FILE             ({num_file})')
                logging.error(f'   MAKLABEL_OPTIONS ({num_opti})')
                logging.error(f'   DESCRIPTION      ({num_desc})')
                raise Exception(error)
            else:
                logging.info(f'     PASS with total of {num_file} entries.')
                logging.info('')

            #
            # Check list against plan
            #
            logging.info('-- Checking kernel list against plan:')
            for ker in ker_in_list:
                if ker not in self.kernel_list:
                    error_message(f'   {ker} not in list')

                else:
                    logging.info(f'     {ker} in list.')
            logging.info('')

            #
            # Check list for duplicate entries
            #
            logging.info('-- Checking for duplicates in kernel list:')
            if check_list_duplicates(ker_in_list):
                error_message('List contains duplicates.')
            else:
                logging.info(f'     List contains no duplicates.')
            logging.info('')

            #
            # Check that all files listed are available in OPS area;
            # This does not raise an error but only a warning.
            #
            logging.info(f'-- Checking that are present in {self.setup.kernels_directory}:')
            for ker in ker_in_list:
                if not os.path.isfile(self.setup.kernels_directory + os.sep +
                                      extension2type(ker) + os.sep + ker):
                    present = True
                    logging.warning(f'     {ker} not present.')
            if not present:
                logging.info('     All kernels present in directory.')
            logging.info('')

            if self.setup.interactive:
                input(">> Press Enter to continue...")


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
            if self.setup.pds == 3:
                logging.info('-- Check that all template tags used in the list are present in template:')
                template = self.setup.root_dir + f'/config/{self.setup.mission_accronym }_mission_template_pds.1'
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

                if self.setup.interactive:
                    input(">> Press Enter to continue...")

        return