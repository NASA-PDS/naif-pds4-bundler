import os
import re
import glob
import logging
import spiceypy

from npb.classes.log   import error_message
from npb.utils.files   import extension2type


class Collection(object):

    def __init__(self, type, setup, bundle):

        self.product = []
        self.name = type
        self.setup = setup
        self.bundle = bundle

        self.lid = self.collection_lid()
        self.vid = self.collection_vid()

        return


    def add(self, element):
        
        self.product.append(element)

    def collection_lid(self):

        collection_lid = f'{self.setup.logical_identifier}:{self.type}'

        return collection_lid


    def collection_vid(self):

        #
        # Collection versions are not equal to the release number,
        #
        if self.setup.increment:

            try:
                versions = glob.glob(f'{self.setup.final_directory}/'
                                     f'{self.setup.mission_accronym}_spice/'
                                     f'{self.name}/*{self.name}*')

                versions.sort()
                version = int(versions[-1].split('v')[-1].split('.')[0]) + 1
                vid = '{}.0'.format(version)
                logging.info(f'-- Collection of {self.type} version set to {version}, derived from:')
                logging.info(f'   {versions[-1]}')
                logging.info('')

            except:
                logging.warning(f'-- No {self.type} collection available in previous increment.')
                logging.warning(f'-- Collection of {self.type} version set to: {int(self.setup.release)}.')
                vid = '{}.0'.format(int(self.setup.release))
                logging.info('')

                if self.setup.interactive:
                    input(">> Press Enter to continue...")

        else:
            logging.warning(f'-- Collection of {self.type} version set to: {int(self.setup.release)}.')
            vid = '{}.0'.format(int(self.setup.release))
            logging.info('')

            if self.setup.interactive:
                input(">> Press Enter to continue...")

        return vid


class SpiceKernelsCollection(Collection):

    def __init__(self, setup, bundle, list):

        line = f'Step {setup.step} - SPICE kernel collection/data processing'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        self.bundle      = bundle
        self.list        = list
        self.type        = 'spice_kernels'
        self.start_time  = setup.mission_start
        self.stop_time   = setup.mission_stop

        Collection.__init__(self, self.type, setup, bundle)

        return


    def determine_meta_kernels(self):

        line = f'Step {self.setup.step} - Generation of meta-kernel(s)'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        meta_kernels = []

        #
        # First check if meta-kernel has been provided via configuration by
        # the user. If so, only the provided meta-kernels will be taken into
        # account (there is no hybrid possibility but npb provides a warning
        # message if more meta-kernels are expected).
        #
        for mk_input in self.setup.mk_inputs:
            if not mk_input['file'] == None:
                if not os.path.exists(mk_input['file']):
                    logging.info('')
                    logging.error(f'-- Meta-kernel provided via configuration'
                                  f' does not exist: {mk_input["file"]}')
                else:
                    meta_kernels.append(mk_input['file'])

        if meta_kernels:
            user_input = True
        else:
            user_input = False

        #
        # Although the kernels that will be used are already known, generate
        # list of expected meta-kernels to generate to be compared to the
        # input meta-kernels, if the meta-kernels diverge, a warning message
        # will be displayed.
        #
        #
        # Generate automatically the required meta-kernels
        #
        #
        # First check if any of the increment are present in
        # each meta-kernel configuration.
        #
        if self.setup.mk:
            for kernel_product in self.product:
                for mk in self.setup.mk:
                    #
                    # Boolean to determine whether if the meta-kernel needs to
                    # be generated.
                    #
                    generate_mk = False
                    for pattern in mk['grammar']['pattern']:
                        #
                        # meta-kernel grammars might have prefixes followed by
                        # a colon, so we need to make sure we only use the name
                        # and we do not use the ones with 'exclude:'.
                        #
                        if  ('excluded:' not in pattern) and re.match(pattern.split(':')[-1], kernel_product.name):
                            generate_mk = True

                    #
                    # Now we need to determine whether if this is a
                    # meta-kernel that needs to be generated multiple times.
                    #
                    # In addition the patterns of the meta-kernel name need to
                    # be completed. Currently there are two supported patterns:
                    #    - VERSION
                    #    - YEAR
                    #
                    if generate_mk:

                        #
                        # Loop the patterns.
                        #
                        if not isinstance(mk['name'], list):
                            patterns = [mk['name']]
                        else:
                            patterns = mk['name']

                        #
                        # First we need to determine if multiple instances of this
                        # meta-kernel are required; yearly meta-kernel.
                        #

                        for pattern in mk['name']:
                            #
                            # If present, determine the version.
                            #
                            #if pattern['#text'] == "VERSION":
                            pass

                        #meta_kernels.append(mk['@name'])

                #
                # First check if any of the increment are present in
                # each meta-kernel configuration.
                #


        return (meta_kernels, user_input)


    def validate(self):
        #
        # -- Validate the SPICE Kernels collection:
        #
        #    * Check that there is a XML label for each file under spice_kernels.
        #      That is, we are validating the spice_kernel_collection.
        #
        line = f'Step {self.setup.step} - Validate SPICE kernel collection generation'
        logging.info('')
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        #
        # Check that all the kernels from the list are present
        #
        logging.info('-- Checking that all the kernels from list are present...')


        for product in self.product:
            try:
                os.path.exists(self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name)
                os.path.exists(
                    self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name.split('.')[
                        0] + '.xml')
            except:
                error_message(f'-- {product.name} has not been labeled.')
        logging.info('   OK')
        logging.info('')

        #
        # Check that all the kernels have been labeled.
        #
        logging.info('-- Checking that all the kernels have been labeled...')

        for product in self.product:
            try:
                os.path.exists(self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name)
                os.path.exists(self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name.split('.')[0] + '.xml')
            except:
                error_message(f'-- {product.name} has not been labeled.')
        logging.info('   OK')

        logging.info('')
        if self.setup.interactive:
            input(">> Press Enter to continue...")

        return


class DocumentCollection(Collection):

    def __init__(self, setup, bundle):

        if setup.pds_version == '3':
            self.type = 'DOCUMENT'
        elif setup.pds_version == '4':
            self.type = 'document'

        Collection.__init__(self, self.type, setup, bundle)

        return