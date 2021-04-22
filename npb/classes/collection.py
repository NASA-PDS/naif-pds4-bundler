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

        collection_lid = \
            'urn:{}:{}:{}.spice:{}'.format(
                self.setup.national_agency,
                self.setup.archiving_agency,
                self.setup.mission_accronym,
                self.type)

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
                logging.info('')
                logging.info(f'-- Collection of {self.type} version set to {version}, derived from:')
                logging.info(f'   {versions[-1]}')
                logging.info('')

            except:
                logging.warning(f'-- No {self.type} collection available in previous increment.')
                logging.warning(f'-- Collection of {self.type} version set to release number: {int(self.setup.release)}.')
                vid = '{}.0'.format(int(self.setup.release))
                logging.info('')

                if self.setup.interactive:
                    input(">> Press Enter to continue...")

        else:
            logging.warning(f'-- Collection of {self.type} version set to release number: {int(self.setup.release)}.')
            vid = '{}.0'.format(int(self.setup.release))
            logging.info('')

            if self.setup.interactive:
                input(">> Press Enter to continue...")

        return vid


class SpiceKernelsCollection(Collection):

    def __init__(self, setup, bundle, list):

        line = f'Step {setup.step} - SPICE kernel collection/data processing'
        logging.info(line)
        logging.info('-'*len(line))
        setup.step += 1

        self.bundle      = bundle
        self.list        = list
        self.type        = 'spice_kernels'
        self.start_time  = setup.mission_start
        self.stop_time   = setup.mission_stop

        Collection.__init__(self, self.type, setup, bundle)

        return


    def validate(self):
        #
        # -- Validate the SPICE Kernels collection:
        #
        #    * Check that there is a XML label for each file under spice_kernels.
        #      That is, we are validating the spice_kernel_collection.
        #
        logging.info('')
        line = f'Step {self.setup.step} - Validate SPICE kernel collection generation'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

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