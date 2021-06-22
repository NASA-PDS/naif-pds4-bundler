import os
import time
import shutil
import filecmp
import logging
from npb.utils.files import safe_make_directory
from npb.utils.files import get_context_products
from npb.classes.product import ReadmeProduct


class Bundle(object):
    """
    Class to generate the PDS4 Bundle structure. The class construction
    will generate the top level directory structure as follows::

      maven_spice/
      |-- spice_kernels
      |-- document
      '-- miscellaneous

    """
    def __init__(self, setup):
        """
        Constructor.
        """
        line = f'Step {setup.step} - Bundle/data set structure generation ' \
               f'at staging area'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        setup.step += 1
        if not setup.args.silent and not setup.args.verbose: print('-- ' +
            line.split(' - ')[-1] + '.')

        logging.info('-- Directory structure generation occurs if reported.')
        logging.info('')

        self.collections = []

        #
        # Generate the bundle or data set structure
        #
        if setup.pds_version == '3':

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + 'catalog')
            safe_make_directory(setup.staging_directory + os.sep + 'data')
            safe_make_directory(setup.staging_directory + os.sep + 'document')
            safe_make_directory(setup.staging_directory + os.sep + 'extras')
            safe_make_directory(setup.staging_directory + os.sep + 'index')

        elif setup.pds_version == '4':

            self.name = f'bundle_{setup.mission_accronym}' \
                        f'_spice_v{setup.release}.xml'

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep +
                                'spice_kernels')
            safe_make_directory(setup.staging_directory + os.sep +
                                'document')
            safe_make_directory(setup.staging_directory + os.sep +
                                'miscellaneous')

        self.setup = setup

        if setup.pds_version == '4':

            #
            # Assign the Bundle LID and VID and the Internal Reference LID
            #
            self.vid = self.bundle_vid()
            self.lid = self.bundle_lid()

            self.lid_reference = \
                '{}:context:investigation:mission.{}'.format(
                    ':'.join(setup.logical_identifier.split(':')[0:-1]),
                    self.setup.mission_accronym)

            #
            #  Get the context products.
            #
            self.context_products = get_context_products(self.setup)

            if self.setup.interactive:
                input(">> Press Enter to continue...")

    def add(self, element):
        self.collections.append(element)

    def write_readme(self):
        #
        # Write the readme product if it does not exist.
        #
        self.readme = ReadmeProduct(self.setup, self)

        return None

    def bundle_vid(self):

        return f'{int(self.setup.release)}.0'

    def bundle_lid(self):

        product_lid = self.setup.logical_identifier

        return product_lid

    def files_in_staging(self):
        '''
        This method lists all the files in the staging area.
        :return:
        '''
        line = f'Step {self.setup.step} - Recap files in staging area'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        #
        # A list of the new files in the staging area is generated first.
        #
        new_files = []
        for root, dirs, files in os.walk(self.setup.staging_directory,
                                         topdown=True):
            for name in files:
                new_files.append(os.path.join(root, name))

        self.new_files = new_files

        logging.info(f'-- The following files are present in the staging '
                     f'area:')
        for file in new_files:
            relative_path = \
                f"{os.sep}{self.setup.mission_accronym}_spice{os.sep}"
            logging.info(f'     {file.split(relative_path)[-1]}')
        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        return None

    def copy_to_final(self):

        line = f'Step {self.setup.step} - Copy files to final area'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        #
        # Index files are added to the new_files list.
        #
        if self.setup.pds_version == '3':
            self.new_files.append(self.setup.staging_directory +
                                  '/../dsindex.tab')
            self.new_files.append(self.setup.staging_directory +
                                  '/../dsindex.lbl')

        copied_files = []
        for file in self.new_files:
            src = file
            relative_path = \
                f"{os.sep}{self.setup.mission_accronym}_spice{os.sep}"
            relative_path += file.split(relative_path)[-1]

            dst = self.setup.final_directory + relative_path
            
            if not os.path.exists(os.sep.join(dst.split(os.sep)[:-1])):
                os.mkdir(os.sep.join(dst.split(os.sep)[:-1]))
                os.chmod(os.sep.join(dst.split(os.sep)[:-1]), 0o775)

            if not os.path.exists(dst):
                copied_files.append(file)
                #
                # We do not use copy2 (copy data and metadata) because
                # we want to 'touch' the files for them to have the
                # timestamp of the day the archive increment was generated.
                #
                shutil.copy(src, dst)
                os.chmod(dst, 0o664)

                logging.info(f'-- Copied: {dst.split(os.sep)[-1]}')
            else:
                if not filecmp.cmp(src, dst):
                    logging.warning(f'-- File already exists but content is '
                                    f'different: '
                                    f'{dst.split(os.sep)[-1]}')

                logging.warning(f'-- File already exists and has not been '
                                f'copied: {dst.split(os.sep)[-1]}')

        logging.info('')
        line = f'-- Found {len(self.new_files)} new file(s). Copied ' \
               f'{len(copied_files)} file(s).'
        if len(self.new_files) == len(copied_files):
            logging.info(line)
        else:
            logging.warning(line)
        logging.info('')

        #
        # Cross-check that files with latest timestamp in final correspond
        # to the files copied from staging:
        #
        xdays = 1
        now = time.time()
        newer_file = []

        #
        # List all files newer than 'x' days
        #
        logging.info(f"-- Files in final directory less than {str(xdays)} "
                     f"days old:")
        for root, dirs, files in os.walk(self.setup.final_directory):
            for name in files:
                filename = os.path.join(root, name)
                if os.stat(filename).st_mtime > now - (xdays * 86400):
                    relative_path = f"{self.setup.mission_accronym}_spice/"
                    logging.info(f'   {filename.split(relative_path)[-1]}')
                    newer_file.append(filename)

        logging.info('')
        line = f'-- Found {len(newer_file)} newer file(s), copied ' \
               f'{len(copied_files)} file(s) from staging directory.'
        if len(newer_file) == len(copied_files):
            logging.info(line)
        else:
            logging.warning(line)
        logging.info('')

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return None