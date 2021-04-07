import os
import time
import shutil
import filecmp
import logging
import datetime
import subprocess

from npb.utils.files     import safe_make_directory
from npb.utils.files     import get_context_products
from npb.utils.files     import compare_files

from npb.classes.product import ReadmeProduct
from npb.classes.log     import error_message


class Bundle(object):

    def __init__(self, setup):

        line = f'Step {setup.step} - Bundle/data set structure generation'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        logging.info('-- Directory structure generation occurs if reported.')
        setup.step += 1

        self.collections = []

        #
        # Generate the bundle or data set structure
        #
        if setup.pds == '3':

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + 'catalog')
            safe_make_directory(setup.staging_directory + os.sep + 'data')
            safe_make_directory(setup.staging_directory + os.sep + 'document')
            safe_make_directory(setup.staging_directory + os.sep + 'extras')
            safe_make_directory(setup.staging_directory + os.sep + 'index')

        elif setup.pds == '4':

            self.name = f'bundle_{setup.mission_accronym}' \
                        f'_spice_v{setup.release}.xml'

            safe_make_directory(setup.staging_directory)
            safe_make_directory(setup.staging_directory + os.sep + 'spice_kernels')
            safe_make_directory(setup.staging_directory + os.sep + 'document')


        self.setup = setup


        if setup.pds == '4':

            #
            # Assign the Bundle LID and VID and the Internal Reference LID
            #
            self.vid = self.bundle_vid()
            self.lid = self.bundle_lid()

            self.lid_reference = \
                f'urn:nasa:pds:context:investigation:mission.{setup.mission_accronym}'

            #
            #  Get the context products.
            #
            self.context_products = get_context_products(self.setup)

            if self.setup.interactive:
                input(">> Press Enter to continue...")

        return


    def add(self, element):
        self.collections.append(element)


    def write_readme(self):
        #
        # Write the readme product if it does not exist.
        #
        ReadmeProduct(self.setup, self)

        return


    def bundle_vid(self):

        return f'{int(self.setup.release)}.0'


    def bundle_lid(self):

        product_lid = f'urn:nasa:pds:{self.setup.mission_accronym}.spice'

        return product_lid


    def copy_to_staging(self):
        '''
        This method copies all the files to staging to proceed with the
        increment.
        :return:
        '''

        logging.info('')
        line = f'Step {self.setup.step} - Copying files to staging area.'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

        # TODO: Update with required PDS3 extensions

        #
        # A list of the new files in the staging area is generated first.
        #
        new_files = []
        for root, dirs, files in os.walk(self.setup.staging_directory, topdown=True):
            for name in files:
                new_files.append(os.path.join(root, name))

        self.new_files = new_files

        #
        # Sort what will be copied, a list is created to be checked
        # afterwards.
        #
        matches = ['.xml', '.csv', '.txt', '.lbl', '.tab', '.html']

        final_files = []
        final_dirs  = []

        for root, dirs, files in os.walk(self.setup.final_directory + f'/{self.setup.mission_accronym}_spice', topdown=True):
            for name in files:
                if any(x in name for x in matches):
                    final_files.append(os.path.join(root, name))
            for name in dirs:
                final_dirs.append(os.path.join(root, name))

        for dir in final_dirs:
            os.makedirs(self.setup.staging_directory + dir.split(f'/{self.setup.mission_accronym}_spice')[-1] , exist_ok=True)

        copied_files = []
        for file in final_files:
            src = file
            dst = self.setup.staging_directory + file.split(f'/{self.setup.mission_accronym}_spice')[-1]
            if not os.path.exists(dst) or not filecmp.cmp(src, dst):
                copied_files.append(file)
                shutil.copy2(src, dst)
                logging.warning(f'-- Copied: {file}')
            else:
                logging.warning(f'-- Not copied: {file}')

        logging.info('')
        line = f'-- Found {len(final_files)} file(s). Copied {len(copied_files)} file(s).'
        if len(final_files) == len(copied_files):
            logging.info(line)
        else:
            logging.warning(line)
        logging.info('')

        return


    def copy_to_final(self):

        logging.info('')
        line = f'Step {self.setup.step} - Copying files to final area.'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

        #
        # Index files are added to the new_files list.
        #
        if self.setup.pds == '4':
            self.new_files.append(self.setup.staging_directory + '/../dsindex.tab')
            self.new_files.append(self.setup.staging_directory + '/../dsindex.lbl')

        copied_files = []
        for file in self.new_files:
            src = file

            rel_path = file.split(f'/{self.setup.mission_accronym}_spice/')[-1]
            rel_path = os.sep.join(rel_path.split(os.sep)[:-1])
            dst = self.setup.final_directory.split(f'{self.setup.mission_accronym}_spice')[0] + f'/{self.setup.mission_accronym}_spice/' + rel_path

            if not os.path.exists(dst) or not filecmp.cmp(src, dst):
                copied_files.append(file)
                shutil.copy2(src, dst)
                logging.info(f'-- Copied: {file}')
            else:
                logging.warning(f'-- Not copied: {file}')

        logging.info('')
        line = f'-- Found {len(self.new_files)} new file(s). Copied {len(copied_files)} file(s).'
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
        logging.info(f"-- Files in final directory newer than {str(xdays)} days:")
        for root, dirs, files in os.walk(self.setup.final_directory):
            for name in files:
                filename = os.path.join(root, name)
                if os.stat(filename).st_mtime > now - (xdays * 86400):
                    logging.info(f'   {filename}')
                    newer_file.append(filename)

        logging.info('')
        line = f'-- Found {len(newer_file)} newer file(s), copied {len(copied_files)} file(s) from staging directory.'
        if len(newer_file) == len(copied_files):
            logging.info(line)
        else:
            logging.warning(line)
        logging.info('')

        return



    def write_checksum(self):

        line = f'Step {self.setup.step} - Generation of checksum files'
        logging.info(line)
        logging.info('-'*len(line))
        logging.info('')
        self.setup.step += 1

        cwd = os.getcwd()
        os.chdir(self.setup.final_directory)

        #
        # First of all we move the current version of the checksum file, if
        # it exists, in order to compare it with the new one afterwards.
        #
        mtime = os.path.getmtime(f'{self.setup.final_directory}/checksum.tab')

        date_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y%m%d")

        self.checksum         =  f'{self.setup.final_directory}/checksum.tab'
        self.current_checksum =  f'{self.setup.final_directory}/checksum.tab.{date_time}'

        logging.info(f'-- Temporarily moving current checksum to {self.current_checksum}')
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


        command = f'perl {self.setup.root_dir}exe/mkpdssum.pl -p {self.setup.final_directory}/{self.setup.mission_accronym}_spice'
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

        self.validate_checksum()

        return


    def validate_checksum(self):

        #
        # Compare with previous checksum file, if exists. Otherwise it is
        # not compared.
        #
        try:
            compare_files(self.current_checksum, self.checksum, self.setup.working_directory)
        except:
            logging.warning(f'-- File to compare with does not exist: {self.checksum}')

        logging.info('')
        if self.setup.interactive:
            input(">> Press enter to continue...")

        logging.info(f'-- Removing: {self.current_checksum}')
        logging.info('')
        #
        # Now we remove the previous checksum version.
        #
        os.remove(self.current_checksum)

        return