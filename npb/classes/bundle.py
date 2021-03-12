import os

from npb.utils.files import safe_make_directory
from npb.utils.files import get_context_products

from npb.classes.product import ReadmeProduct

class Bundle(object):

    def __init__(self, setup):

        self.collections = []

        #
        # Generate the bundle or data set structure
        #
        if setup.pds == '3':

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + 'CATALOG')
            safe_make_directory(setup.staging_directory + os.sep + 'DATA')
            safe_make_directory(setup.staging_directory + os.sep + 'DOCUMENT')
            safe_make_directory(setup.staging_directory + os.sep + 'EXTRAS')
            safe_make_directory(setup.staging_directory + os.sep + 'INDEX')

        elif setup.pds == '4':

            self.name = f'bundle_{setup.mission_accronym}' \
                        f'_spice_v{setup.release}.xml'

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + 'spice_kernels')
            safe_make_directory(setup.staging_directory + os.sep + 'document')

        #
        # Assign the Bundle LID and VID and the Internal Reference LID
        #
        self.setup = setup
        self.vid = self.bundle_vid()
        self.lid = self.bundle_lid()

        self.lid_reference = \
            f'urn:nasa:pds:context:investigation:mission.{setup.mission_accronym}'

        #
        #  Get the context products
        #
        if setup.pds == '4':

#             self.errata                 = setup.errata
             self.context_products       = get_context_products(self.setup)
#             self.producer_name          = setup.producer_name
#             self.producer_email         = setup.email
#             self.producer_phone         = setup.phone
             #self.doi                    = setup.doi

        #else: # PDS3 specific fields
        #     self.dataset                = config['dataset']
        #     self.dataset_name           = config['dataset_name']
        #     self.volume                 = config['volume_id']
        #
        # Determine if the Bundle is an increment
        #


        #
        #             #
        #             # PDS4 version increment (implies inventory and meta-kernel)
        #             #
        #             if self.increment:
        #                 copy(self.increment + os.sep, self.bundle_directory + os.sep)
        #
        #                 versions = glob.glob(self.increment + os.sep +
        #                                  f'bundle_{self.accronym}_spice_v*')
        #                 versions.sort()
        #                 version = int(versions[-1].split('_spice_v')[-1].split('.')[0]) + 1
        #                 version = '{:03}'.format(version)
        #
        #                 current_version = int(versions[-1].split('_spice_v')[-1].split('.')[0])
        #                 current_version = '{:03}'.format(current_version)
        #
        #             else:
        #                 version = '001'
        #                 current_version = ''
        #
        #             self.version = version
        #             self.current_version = current_version
        #


        return


    def add(self, element):
        self.collections.append(element)


    def write_readme(self):
        ReadmeProduct(self.setup, self)


    def bundle_vid(self):

        return f'{int(self.setup.release)}.0'


    def bundle_lid(self):

        product_lid = f'urn:nasa:pds:{self.setup.mission_accronym}.spice'

        return product_lid


    def increment(self):

        return