import os

from npb.utils.files import safe_make_directory
from npb.classes.product import ReadmeProduct

class Bundle(object):

    def __init__(self, setup):

        self.collections = []

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

        self.setup = setup
        self.vid = self.bundle_vid()
        self.lid = self.bundle_lid()

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
