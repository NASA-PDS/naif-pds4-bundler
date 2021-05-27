import os
import time
import shutil
import filecmp
import logging
import subprocess
from datetime import datetime
from npb.utils.files import safe_make_directory
from npb.utils.files import get_context_products
from npb.utils.files import compare_files
from npb.classes.product import ReadmeProduct
from npb.classes.log import error_message


class Bundle(object):
    """
    Class to generate the PDS4 Bundle.
    """
    def __init__(self, setup):
        """
        Constructor

        :param setup:
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

        return None

    def add(self, element):
        self.collections.append(element)

    def write_readme(self):
        #
        # Write the readme product if it does not exist.
        #
        ReadmeProduct(self.setup, self)

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
            rel_path = file.split(relative_path)[-1]
            rel_path = os.sep.join(rel_path.split(os.sep)[:-1])

            dst = self.setup.final_directory + relative_path
            if not os.path.exists(dst):
                os.mkdir(dst)

            dst += rel_path

            if not os.path.exists(dst) or not filecmp.cmp(src, dst):
                if not os.path.exists(dst):
                    os.mkdir(dst)
                copied_files.append(file)
                shutil.copy2(src, dst)
                logging.info(f'-- Copied: {file.split(relative_path)[-1]}')
            else:
                logging.warning(f'-- Not copied: '
                                f'{file.split(relative_path)[-1]}')

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

        # List all files newer than xdays
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

    def write_checksum(self):

        line = f'Step {self.setup.step} - Generate checksum files'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.setup.step += 1
        if not self.setup.args.silent and not self.setup.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        cwd = os.getcwd()
        os.chdir(self.setup.final_directory)

        #
        # First of all we move the current version of the checksum file, if
        # it exists, in order to compare it with the new one afterwards.
        #
        if os.path.exists(f'{self.setup.final_directory}/checksum.tab'):
            mtime = os.path.getmtime(f'{self.setup.final_directory}'
                                     f'/checksum.tab')

            date_time = datetime.fromtimestamp(mtime).strftime("%Y%m%d")

            self.checksum = f'{self.setup.final_directory}/checksum.tab'
            self.current_checksum = f'{self.setup.final_directory}' \
                                    f'/checksum.tab.{date_time}'

            logging.info(f'-- Temporarily moving current checksum to '
                         f'{self.current_checksum}')
            shutil.move(self.checksum, self.current_checksum)

        #
        # We remove spurious .DS_Store files if we are working with MacOS.
        #
        for root, dirs, files in os.walk(self.setup.final_directory):
            for file in files:
                if file.endswith('.DS_Store'):
                    path = os.path.join(root, file)
                    logging.info(f'-- Removing {file}')
                    os.remove(path)

        command = f'perl {self.setup.root_dir}exe/mkpdssum.pl -p ' \
                  f'{self.setup.final_directory}/' \
                  f'{self.setup.mission_accronym}_spice'
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

        if self.setup.interactive:
            input(">> Press enter to continue...")

        if hasattr(self, 'current_checksum'):
            logging.info('-- Comparing checksum with previous version...')
            self.compare_checksum()

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return None

    def compare_checksum(self):

        #
        # Compare with previous checksum file, if exists. Otherwise it is
        # not compared.
        #
        try:
            compare_files(self.current_checksum, self.checksum,
                          self.setup.working_directory, 'all')
        except:
            logging.warning(f'-- File to compare with does not exist: '
                            f'{self.checksum}')

        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        logging.info(f'-- Removing: {self.current_checksum}')
        logging.info('')
        #
        # Now we remove the previous checksum version.
        #
        os.remove(self.current_checksum)

        return None
