import os
import logging

from npb.classes.log   import error_message

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
            'urn:nasa:pds:{}.spice:{}'.format(
                    self.setup.mission_accronym,
                    self.type)

        return collection_lid

    def collection_vid(self):

        return '{}.0'.format(int(self.setup.release))


class SpiceKernelsCollection(Collection):

    def __init__(self, setup, bundle):

        logging.info(f'Step {setup.step} - SPICE kernel collection/data processing')
        logging.info('------------------------------------------------')
        logging.info('')
        setup.step += 1

        self.bundle      = bundle
        self.type        = 'spice_kernels'
        self.start_time  = setup.mission_start
        self.stop_time   = setup.mission_stop

        Collection.__init__(self, self.type, setup, bundle)

        return

    def validate(self):

        logging.info(f'Step {self.setup.step} - Validating SPICE kernel collection generation')
        logging.info('-------------------------------------------------------')
        logging.info('')
        self.setup.step += 1

        #
        # Check that all the kernels have been labeled.
        #
        logging.info('-- Checking that all the kernels have been labeled.')
        logging.info('')

        for product in self.product:
            try:
                os.path.exists(self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name)
                os.path.exists(self.setup.staging_directory + '/spice_kernels/' + product.type + os.sep + product.name.split('.')[0] + '.xml')
            except:
                error_message(f'-- {product.name} has not been labeled.')



        return


class DocumentCollection(Collection):

    def __init__(self, setup, bundle):

        if setup.pds == '3':
            self.type = 'DOCUMENT'
        elif setup.pds == '4':
            self.type = 'document'

        Collection.__init__(self, self.type, setup, bundle)

        return