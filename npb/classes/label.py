import fileinput
import logging
import glob
import os
from npb.utils.time import current_time
from npb.utils.files import add_carriage_return
from npb.utils.files import compare_files
from npb.utils.files import extension2type
from npb.classes.log import error_message

# from npb.utils.files import get_spacecrafts
# from npb.utils.files import get_targets


class PDSLabel(object):

    def __init__(self, setup, product):

        try:
            context_products = product.collection.bundle.context_products
            if not context_products:
                raise Exception("No context products from bundle in "
                                "collection")
        except:
            context_products = product.bundle.context_products

        #
        # The product to be labeled.
        #
        self.product = product
        self.setup = setup

        #
        # Fields from setup
        #
        self.root_dir = setup.root_dir
        self.mission_acronym = setup.mission_acronym
        self.XML_MODEL = setup.xml_model
        self.SCHEMA_LOCATION = setup.schema_location
        self.INFORMATION_MODEL_VERSION = setup.information_model
        self.PDS4_MISSION_NAME = setup.mission_name
        self.PDS4_SPACECRAFT_NAME = setup.spacecraft
        
        if setup.end_of_line == 'CRLF':
            self.END_OF_LINE = 'Carriage-Return Line-Feed'
        elif setup.end_of_line == 'LF':
            self.END_OF_LINE =  'Line-Feed'
        else:
            error_message('End of Line provided via configuration is not '
                          'CRLF nor LF')

        self.CURRENT_YEAR = current_time().split('-')[0]
        self.BUNDLE_DESCRIPTION_LID = \
            f'{setup.logical_identifier}:document:spiceds'

        self.PRODUCT_CREATION_TIME = product.creation_time
        self.PRODUCT_CREATION_DATE = product.creation_date
        self.FILE_SIZE = product.size
        self.FILE_CHECKSUM = product.checksum

        try:
            self.PDS4_MISSION_LID = product.collection.bundle.lid_reference
        except:
            self.PDS4_MISSION_LID = product.bundle.lid_reference

        for context_product in context_products:
            if (context_product['name'][0] == setup.spacecraft) and \
                    (context_product['type'][0].lower() != 'mission'):
                self.PDS4_SPACECRAFT_TYPE = \
                    context_product['type'][0].capitalize()
                self.PDS4_SPACECRAFT_LID = \
                    context_product['lidvid'].split('::')[0]

            #
            # For Bundles with multiple s/c
            #
            if hasattr(setup, 'secondary_spacecraft'):

                #
                # We sort out how many S/C we have
                #
                sec_scs = setup.secondary_spacecraft.split(',')

                for sc in sec_scs:
                    if sc:
                        if sc.lower() in product.name.lower():
                            self.PDS4_SPACECRAFT_NAME = sc

                            for cntxt_prdct in context_products:
                                if (context_product['name'][0] ==
                                    setup.spacecraft) and (
                                        cntxt_prdct['type'][0].lower() !=
                                        'mission'):
                                    self.PDS4_SPACECRAFT_TYPE = \
                                        cntxt_prdct['type'][0].capitalize()
                                    self.PDS4_SPACECRAFT_LID = \
                                        cntxt_prdct['lidvid'].split('::')[0]

            self.PDS4_TARGET_NAME = setup.target.upper()

            for cntxt_prdct in context_products:
                if cntxt_prdct['name'][0].upper() == setup.target.upper():
                    self.PDS4_TARGET_TYPE = \
                        cntxt_prdct['type'][0].capitalize()
                    self.PDS4_TARGET_LID = \
                        cntxt_prdct['lidvid'].split('::')[0]

            #
            # For Bundles with multiple targets
            #
            if hasattr(setup, 'secondary_target'):

                #
                # We sort out how many S/C we have
                #
                sec_tars = setup.secondary_target.split(',')

                for tar in sec_tars:
                    if tar:
                        if tar.lower() in product.name.lower():
                            self.PDS4_TARGET_NAME = tar
                            for cntxt_prdct in setup.context_products:
                                if cntxt_prdct['name'][0].upper() == \
                                        tar.upper():
                                    self.PDS4_TARGET_TYPE = \
                                        cntxt_prdct['type'][0].capitalize()
                                    self.PDS4_TARGET_LID = \
                                        cntxt_prdct['lidvid'].split('::')[0]

            #
            # For labels that need to include all S/C and Targets of the setup
            #
            self.SPACECRAFTS = self.get_spacecrafts()
            self.TARGETS = self.get_targets()

    def get_spacecrafts(self):

        sc = ['{}'.format(self.setup.spacecraft)]

        if hasattr(self.setup, 'secondary_spacecraft'):
            sec_scs = self.setup.secondary_spacecraft.split(',')
            if not isinstance(sec_scs, list):
                sec_scs = [sec_scs]
        else:
            sec_scs = []

        scs = sc + sec_scs

        sc_list_for_label = ''

        try:
            context_products = self.product.collection.bundle.context_products
        except:
            context_products = self.product.bundle.context_products

        eol = self.setup.pds4_eol

        for sc in scs:
            if sc:
                sc_name = sc.split(',')[0]
                for product in context_products:
                    if product['name'][0] == sc_name and \
                            product['type'][0] == 'Spacecraft':
                        sc_lid = product['lidvid'].split('::')[0]

                sc_list_for_label += \
                    f'      <Observing_System_Component>{eol}' + \
                    f'        <name>{sc_name}</name>{eol}' + \
                    f'        <type>Spacecraft</type>{eol}' + \
                    f'        <Internal_Reference>{eol}' + \
                    f'          <lid_reference>{sc_lid}' \
                    f'</lid_reference>{eol}' + \
                    '          <reference_type>is_instrument_host' \
                    f'</reference_type>{eol}' + \
                    f'        </Internal_Reference>{eol}' + \
                    f'      </Observing_System_Component>{eol}'

        sc_list_for_label = sc_list_for_label.rstrip() + eol

        return sc_list_for_label

    def get_targets(self):

        tar = [self.setup.target]

        if hasattr(self.setup, 'secondary_target'):
            sec_tar = self.setup.secondary_target.split(',')
            if not isinstance(sec_tar, list):
                sec_tar = [sec_tar]
        else:
            sec_tar = []

        tars = tar + sec_tar

        tar_list_for_label = ''

        try:
            context_products = self.product.collection.bundle.context_products
        except:
            context_products = self.product.bundle.context_products

        eol = self.setup.pds4_eol

        for tar in tars:
            if tar:

                target_name = tar
                for product in context_products:
                    if product['name'][0].upper() == target_name.upper():
                        target_lid = product['lidvid'].split('::')[0]
                        target_type = product['type'][0].capitalize()

                tar_list_for_label += \
                    f'    <Target_Identification>{eol}' + \
                    f'      <name>{target_name}</name>{eol}' + \
                    f'      <type>{target_type}</type>{eol}' + \
                    f'      <Internal_Reference>{eol}' + \
                    f'        <lid_reference>{target_lid}' \
                    f'</lid_reference>{eol}' + \
                    f'        <reference_type>' \
                    f'{self.get_target_reference_type()}' \
                    f'</reference_type>{eol}' + \
                    f'      </Internal_Reference>{eol}' + \
                    f'    </Target_Identification>{eol}'

        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label

    def get_target_reference_type(self):
            
        if self.product.collection.name == 'miscellaneous':
            type = "ancillary_to_target"
        else:
            type = "data_to_target"
        
        return type

    def write_label(self):

        label_dictionary = vars(self)

        label_extension = '.xml'

        if not '.xml' in self.product.path:
            label_name = self.product.path.split(
                f'.{self.product.extension}')[0] + label_extension
        else:
            #
            # This accounts for the bundle label, that doest not come
            # from the bundle product itself.
            #
            label_name = self.product.path

        if 'inventory' in label_name:
            label_name = label_name.replace('inventory_', '')

        with open(label_name, "w+") as f:

            for line in fileinput.input(self.template):
                line = line.rstrip()
                for key, value in label_dictionary.items():
                    if isinstance(value, str) and key in line and '$' in line:
                        line = line.replace('$' + key, value)

                line = add_carriage_return(line, self.setup.pds4_eol)

                f.write(line)

        self.name = label_name

        stag_dir = self.setup.staging_directory
        logging.info(
            f'-- Created {label_name.split(f"{stag_dir}{os.sep}")[-1]}')
        if not self.setup.args.silent and not self.setup.args.verbose:
            print(f'   * Created {label_name.split(f"{stag_dir}{os.sep}")[-1]}.')

        if self.setup.diff:
            self.compare()

        logging.info('')

        return

    def write_pds3_labels(self):

        return None

    def compare(self):
        '''
        The label is compared to a similar label from the previous release
        of the archive.

        For new archives a 'similar' archive is used.
        :return:
        '''

        logging.info(f'-- Comparing label...')

        #
        # 1-Look for a different version of the same file.
        #
        # What we do is that we keep trying to match the label name
        # advancing one character each iteration, in such a way that
        # we find, in order, the label that has the closest name to the
        # one we are generating.
        #
        val_label = ''
        try:

            match_flag = True
            val_label_path = self.setup.final_directory + \
                             f'/{self.setup.mission_acronym}_spice/' + \
                             self.product.collection.name + os.sep

            #
            # If this is the spice_kernels collection, we need to add the
            # kernel type directory.
            #
            if (self.product.collection.name == 'spice_kernels') and \
                    ('collection' not in self.name):
                val_label_path += self.name.split(os.sep)[-2] + os.sep

            val_label_name = self.name.split(os.sep)[-1]
            i = 1

            while match_flag:
                if i < len(val_label_name) - 1:
                    val_labels = \
                        glob.glob(f'{val_label_path}{val_label_name[0:i]}'
                                  f'*.xml')
                    if val_labels:
                        val_labels = sorted(val_labels)
                        val_label = val_labels[-1]
                        match_flag = True
                    else:
                        match_flag = False
                    i += 1

            if not val_label:
                raise Exception("No label for comparison found.")

        except:
            logging.warning(f'-- No other version of the kernel label has '
                            f'been found.')

            #
            # 2-If a prior version of the same file cannot be found look for
            #   the label of a kernel of the same type.
            #
            try:
                val_label_path = self.setup.final_directory + \
                                 f'/{self.setup.mission_acronym}_spice/' + \
                                 self.product.collection.name + os.sep

                #
                # If this is the spice_kernels collection, we need to add the
                # kernel type directory.
                #
                if (self.product.collection.name == 'spice_kernels') and \
                        ('collection' not in self.name):
                    val_label_path += self.name.split(os.sep)[-2] + os.sep

                product_extension = self.product.name.split('.')[-1]
                val_products = glob.glob(f'{val_label_path}*.'
                                         f'{product_extension}')
                val_products.sort()

                #
                # Simply pick the last one
                #
                if ('collection' in self.name.split(os.sep)[-1]):
                    val_label = glob.glob(
                        val_products[-1].replace(
                            'inventory_', '').split('.')[0] + '.xml')[0]
                elif ('bundle' in self.name.split(os.sep)[-1]):
                    val_labels = glob.glob(f'{val_label_path}bundle_*.xml')
                    val_labels.sort()
                    val_label = val_labels[-1]
                else:
                    val_label = glob.glob(
                        val_products[-1].split('.')[0] + '.xml')[0]

                if not val_label:
                    raise Exception("No label for comparison found.")

            except:

                logging.warning(f'-- No similar label has been found.')
                #
                # 3-If we cannot find a kernel of the same type; for example
                #   is a first version of an archive, we compare with
                #   a label available in the test data directories.
                #
                try:
                    val_label_path = f'{self.setup.root_dir}' \
                                     f'tests/functional/data/insight/' \
                                     f'insight_spice/' \
                                     f'{self.product.collection.name}/'

                    #
                    # If this is the spice_kernels collection, we need to
                    # add the kernel type directory.
                    #
                    if (self.product.collection.name == 'spice_kernels') \
                            and ('collection' not in self.name):
                        val_label_path += self.name.split(os.sep)[-2] + os.sep

                        #
                        # Generate the empty files from the test case.
                        #
                        with open(f'{self.setup.root_dir}' 
                                  f'tests/functional/data/insight.list',
                                  'r') as i:
                            for line in i:
                                with open(f'{self.setup.root_dir}' 
                                          f'tests/functional/data/insight/' 
                                          f'insight_spice/' 
                                          f'{line[0:-1]}', 'w') as fp:
                                    
                                    #TODO: Something has to be added here.
                                    pass

                    #
                    # Simply pick the last one
                    #
                    product_extension = self.product.name.split('.')[-1]
                    val_products = glob.glob(
                        f'{val_label_path}*.{product_extension}')
                    val_products.sort()

                    if ('collection' in self.name.split(os.sep)):
                        val_label = \
                            glob.glob(
                                val_products[-1].replace(
                                    'inventory_', '').split(
                                    '.')[0] + '.xml')[0]
                    elif ('bundle' in self.name.split(os.sep)):
                        val_labels = \
                            glob.glob(f'{val_label_path}bundle_*.xml')
                        val_labels.sort()
                        val_label = val_labels[-1]
                    else:
                        val_label = glob.glob(val_products[-1].split('.')[0] +
                                              '.xml')[0]

                    #
                    # Delete the empty files from the test case.
                    #
                    if (self.product.collection.name == 'spice_kernels') \
                            and ('collection' not in self.name):
                        with open(f'{self.setup.root_dir}tests/functional/'
                                  f'data/insight.list', 'r') as i:
                            for line in i:
                                os.remove(self.setup.root_dir + \
                                          f'tests/functional/data/insight/'
                                          f'insight_spice/{line[0:-1]}')

                    if not val_label:
                        raise Exception("No label for comparison found.")

                    logging.warning('-- Comparing with InSight test label.')
                except:
                    logging.warning("-- No label for comparison found.")

        #
        # If a similar label has been found the labels are compared and a
        # diff is being shown in the log. On top of that an HTML file with
        # the comparison is being generated.
        #
        if val_label:
            logging.info('')
            fromfile = val_label
            tofile = self.name
            dir = self.setup.working_directory

            compare_files(fromfile, tofile, dir, self.setup.diff)

        if self.setup.interactive:
            input(">> Press enter to continue...")

        return


class BundlePDS4Label(PDSLabel):

    def __init__(self, setup, readme):

        PDSLabel.__init__(self, setup, readme)

        self.template = f'{setup.templates_directory}/template_bundle.xml'

        self.BUNDLE_LID = self.product.bundle.lid
        self.BUNDLE_VID = self.product.bundle.vid

        self.AUTHOR_LIST = setup.author_list
        self.START_TIME = setup.increment_start
        self.STOP_TIME = setup.increment_finish
        self.FILE_NAME = readme.name
        self.CURRENT_TIME = current_time(setup.date_format)
        self.CURRENT_DATE = self.CURRENT_TIME.split('T')[0]
        self.DOI = self.setup.doi

        for collection in self.product.bundle.collections:
            if collection.name == 'spice_kernels':
                self.SPICE_COLL_LIDVID = collection.lid + '::' + \
                                         collection.vid
                self.SPICE_COLL_STATUS = 'Primary'
            if collection.name == 'document':
                self.DOC_COLL_LIDVID = collection.lid + '::' + \
                                       collection.vid
                self.DOC_COLL_STATUS = 'Primary'

        self.write_label()

        return

    def get_target_reference_type(self):
        return "bundle_to_target"


class SpiceKernelPDS4Label(PDSLabel):

    def __init__(self, mission, product):
        PDSLabel.__init__(self, mission, product)

        self.template = f'{self.setup.templates_directory}/' \
                        f'template_product_spice_kernel.xml'

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = product.file_format
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        extension = '.xml'
        self.name = product.name.split('.')[0] + extension

        self.write_label()


class MetaKernelPDS4Label(PDSLabel):

    def __init__(self, setup, product):
        PDSLabel.__init__(self, setup, product)

        self.template = f'{setup.templates_directory}/' \
                        f'template_product_spice_kernel_mk.xml'

        #
        # Fields from Kernels
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.FILE_FORMAT = 'Character'
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.KERNEL_TYPE_ID = product.type.upper()
        self.PRODUCT_VID = self.product.vid
        self.SPICE_KERNEL_DESCRIPTION = product.description

        self.KERNEL_INTERNAL_REFERENCES = \
            self.get_kernel_internal_references()

        self.name = product.name.split('.')[0] + '.xml'

        self.write_label()

    def get_kernel_internal_references(self):
        
        eol = self.setup.pds4_eol
        
        #
        # From the collection we only use kernels in the MK
        #
        kernel_list_for_label = ''
        for kernel in self.product.collection_metakernel:
            #
            # The kernel lid cannot be obtained from the list; it is
            # merely a list of strings.
            #
            kernel_type = extension2type(kernel)
            kernel_lid = '{}:spice_kernels:{}_{}'.format(
                self.setup.logical_identifier,
                kernel_type,
                kernel)

            kernel_list_for_label += \
                f'    <Internal_Reference>{eol}' + \
                f'      <lid_reference>{kernel_lid}' \
                f'</lid_reference>{eol}' + \
                f'      <reference_type>data_to_associate' \
                f'</reference_type>{eol}' + \
                f'    </Internal_Reference>{eol}'

        kernel_list_for_label = kernel_list_for_label.rstrip() + eol

        return kernel_list_for_label


class OrbnumFilePDS4Label(PDSLabel):

    def __init__(self, setup, product):
        PDSLabel.__init__(self, setup, product)

        self.template = f'{setup.templates_directory}/' \
                        f'template_product_orbnum_table.xml'

        #
        # Fields from orbnum object.
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = 'Character'
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.DESCRIPTION = product.description
        self.HEADER_LENGTH = str(product.header_length)
        self.TABLE_CHARACTER_DESCRIPTION = product.table_char_description

        #
        # The orbnum table data starts one byte after the header section.
        #
        self.TABLE_OFFSET = str(product.header_length + 1)

        self.TABLE_RECORDS = str(product.records)

        #
        # The ORBNUM utility produces an information ground set regardless
        # of the parameters listed in ORBIT_PARAMS. This set consists of 4
        # parameters.
        #
        self.NUMBER_OF_FIELDS = str(len(product.params.keys()))
        self.FIELDS_LENGTH = str(product.record_fixed_length + 1 )
        self.FIELDS = \
            self.__get_table_character_fields()

        if self.TABLE_CHARACTER_DESCRIPTION:
            self.TABLE_CHARACTER_DESCRIPTION = \
                self.__get_table_character_description()
            

        self.name = product.name.split('.')[0] + '.xml'

        self.write_label()

    def __get_table_character_fields(self):

        fields = ''
        for param in  self.product.params.values():
            field = self.__field_template(param['name'], param['number'],
                                          param['location'], param['type'],
                                          param['length'], param['format'],
                                          param['description'], param['unit'],
                                          self.product.blank_records)
            fields += field

        return fields

    def __get_table_character_description(self):
        
        description = f"{self.setup.pds4_eol}      <description>" \
                      f"{self.product.table_char_description}" \
                      f"</description>{self.setup.pds4_eol}"
    
        return description

    def __field_template(self, name, number, location, type, length, format,
                         description, unit, blanks):

        eol = self.setup.pds4_eol

        field = \
            f'{" " * 8}<Field_Character>{eol}' \
            f'{" " * 8}  <name>{name}</name>{eol}' \
            f'{" " * 8}  <field_number>{number}</field_number>{eol}' \
            f'{" " * 8}  <field_location unit="byte">{location}' \
            f'</field_location>{eol}' \
            f'{" " * 8}  <data_type>{type}</data_type>{eol}' \
            f'{" " * 8}  <field_length unit="byte">{length}' \
            f'</field_length>{eol}' \
            f'{" " * 8}  <field_format>{format}</field_format>{eol}'
        if unit:
            field += \
                f'{" " * 8}  <unit>{unit}</unit>{eol}'   
        field += \
            f'{" " * 8}  <description>{description}</description>{eol}' 
        if blanks and name != 'No.':
            field += f'{" " * 8}  <Special_Constants>{eol}' \
                     f'{" " * 8}    <missing_constant>blank space' \
                     f'</missing_constant>{eol}' \
                     f'{" " * 8}  </Special_Constants>{eol}' 
        field += f'{" " * 8}</Field_Character>{eol}'

        return field


class InventoryPDS4Label(PDSLabel):

    def __init__(self, setup, collection, inventory):
        PDSLabel.__init__(self, setup, inventory)

        self.collection = collection
        self.template = f'{setup.templates_directory}/' \
                        f'template_collection_{collection.type}.xml'

        self.COLLECTION_LID = self.collection.lid
        self.COLLECTION_VID = self.collection.vid
        self.START_TIME = setup.increment_start
        self.STOP_TIME = setup.increment_finish
        self.FILE_NAME = inventory.name

        # Count number of lines in the inventory file
        f = open(self.product.path)
        self.N_RECORDS = str(len(f.readlines()))
        f.close()

        self.name = collection.name.split('.')[0] + '.xml'

        self.write_label()

    def get_target_reference_type(self):
        return "collection_to_target"


class InventoryPDS3Label(PDSLabel):

    def __init__(self, setup, collection, inventory):

        PDSLabel.__init__(self, setup, inventory)

        self.collection = collection
        self.template = self.root_dir + \
                        '/templates/template_collection_{}.LBL'.format(
                            collection.type)

        self.VOLUME = setup.volume
        self.PRODUCT_CREATION_TIME = current_time(setup.date_format)
        self.DATASET = setup.dataset

        indexfile = open(
            setup.bundle_directory + '/INDEX/INDEX.TAB', 'r').readlines()
        self.N_RECORDS = str(len(indexfile))
        self.R_RECORDS = str(len(indexfile[0]) + 1)
        indexfields = indexfile[0].replace('"', '').split(',')
        self.START_BYTE1 = str(2)
        self.START_BYTE2 = str(2 + len(indexfields[0]) + 3)
        self.START_BYTE3 = str(2 + len(indexfields[0]) + 3 +
                               len(indexfields[1]) + 2)
        self.START_BYTE4 = str(2 + len(indexfields[0]) + 3 +
                               len(indexfields[1]) + 2 +
                               len(indexfields[2]) + 2)
        self.BYTES1 = str(len(indexfields[0]))
        self.BYTES2 = str(len(indexfields[1]))
        self.BYTES3 = str(len(indexfields[2]))
        self.BYTES4 = str(len(indexfields[3].split('\n')[0]))

        self.write_label()

    def write_label(self):

        label_dictionary = vars(self)

        with open(
                self.setup.bundle_directory + '/INDEX/INDEX.LBL', "w+") as f:

            for line in fileinput.input(self.template):
                line = line.rstrip()
                for key, value in label_dictionary.items():
                    if isinstance(value, str) and key in line and '$' in line:
                        line = line.replace('$' + key, value)

                line = add_carriage_return(line, self.setup.pds4_eol)

                if 'END_OBJECT' in line and line[:10] != 'END_OBJECT':
                    f.write(line.split('END_OBJECT')[0])
                    f.write('END_OBJECT               = COLUMN\n')
                else:
                    f.write(line)

        self.name = 'INDEX.LBL'

        return


class DocumentPDS4Label(PDSLabel):

    def __init__(self, setup, collection, inventory):
        PDSLabel.__init__(self, setup, inventory)

        self.setup = setup
        self.collection = collection
        self.template = f'{setup.templates_directory}/' \
                        f'template_product_html_document.xml'

        self.PRODUCT_LID = inventory.lid
        self.PRODUCT_VID = inventory.vid
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish
        self.FILE_NAME = inventory.name
        self.CURRENT_TIME = current_time(setup.date_format)
        self.CURRENT_DATE = self.CURRENT_TIME.split('T')[0]

        self.name = collection.name.split('.')[0] + '.xml'

        self.write_label()


class ChecksumPDS4Label(PDSLabel):

    def __init__(self, setup, product):
        PDSLabel.__init__(self, setup, product)

        self.template = f'{setup.templates_directory}/' \
                        f'template_product_checksum_table.xml'

        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = 'Character'
        self.START_TIME = setup.mission_start
        self.STOP_TIME = setup.mission_finish

        self.name = product.name.split('.')[0] + '.xml'

        self.write_label()
