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
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        meta_kernels = []

        #
        # First check if meta-kernel has been provided via configuration by
        # the user. If so, only the provided meta-kernels will be taken into
        # account (there is no hybrid possibility but npb provides a warning
        # message if more meta-kernels are expected).
        #
        if not self.setup.mk_inputs[0]['file'] == None:
            mks = self.setup.mk_inputs[0]['file']
            if not isinstance(mks, list):
                mks = [mks]
            for mk in mks:
                if not os.path.exists(mk):
                    logging.info('')
                    logging.error(f'-- Meta-kernel provided via configuration'
                                  f' does not exist: {mk}')
                else:
                    meta_kernels.append(mk)

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


    def set_increment_times(self):
        '''
        Determine the archive increment start and finish times; this is done
        based on the identification of the coverage of a given SPK or CK
        kernel. Alternatively it can be provided as a parameter of the
        execution.

        :return:
        '''
        logging.info('')
        line = f'Step {self.setup.step} - Determine archive increment start and finish times'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose: print('-- ' + line.split(' - ')[-1] + '.')

        #
        # Check if an increment stop time has been provided as an input
        # parameter.
        #
        if self.setup.increment_start:
            logging.info(f'-- Increment stop time set to: {self.setup.increment_start} '
                         f'as provided with configuration file')

        if self.setup.increment_finish:
            logging.info(f'-- Increment finish time set to: {self.setup.increment_finish} '
                         f'as provided with configuration file')

        if self.setup.increment_finish and self.setup.increment_start:
            return

        #
        # Match the pattern with the kernels in the meta-kernel.
        #
        try:
            increment_starts = []
            increment_finishs = []
            for prod in self.product:
                if prod.type == 'mk':
                    increment_starts.append(prod.start_time)
                    increment_finishs.append(prod.stop_time)

            increment_start = min(increment_starts)
            increment_finish = max(increment_finishs)

        except:
            #
            # The alternative is to set the increment stop time to the
            # end time of the mission.
            #
            increment_start = self.setup.mission_start
            increment_finish = self.setup.mission_stop
            logging.error(f'-- No kernel(s) found to determine increment stop time. Mission times will be used.')

        #
        # We check the coverage with the previous increment.
        #
        try:
            #
            # The first alternative option is to set the time to the time of
            # the previous increment since we might be generating an increment
            # that does not extend the coverage.
            #
            bundles = glob.glob(self.setup.final_directory + os.sep +
                                self.setup.mission_accronym + '_spice' + os.sep +
                                f'bundle_{self.setup.mission_accronym}_spice_v*')
            bundles.sort()

            with open(bundles[-1], 'r') as b:
                for line in b:
                    if '<start_date_time>' in line:
                        prev_increment_start = line.split('>')[-2].split('<')[0]
                    if '<stop_date_time>' in line:
                        prev_increment_finish = line.split('>')[-2].split('<')[0]

            #
            # Provide different logging level depending on the times
            # combination.
            #
            logging.info('-- Previous bundle increment interval is:')
            logging.info(f'   {prev_increment_start} - {prev_increment_finish}')

            #
            # Correct the increment interval with previous interval if required.
            #
            if prev_increment_start < increment_start:
                increment_start = prev_increment_start
                logging.warning('-- Increment start corrected form previous bundle')

            if prev_increment_finish > increment_finish:
                increment_finish = prev_increment_sinish
                logging.warning('-- Increment finish corrected form previous bundle')

        except:
            logging.warning(f'-- Previous bundle not found.')

        logging.info('-- Increment interval for collection and bundle set to:')
        logging.info(f'   {increment_start} - {increment_finish}')
        logging.info('')

        if self.setup.interactive:
            input(">> Press Enter to continue...")

        self.setup.increment_finish = increment_finish
        self.setup.increment_start = increment_start

        return

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