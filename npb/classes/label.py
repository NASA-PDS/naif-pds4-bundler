import fileinput

from npb.utils.time import current_time
from npb.utils.files import add_carriage_return
#from npb.utils.files import get_skd_spacecrafts
#from npb.utils.files import get_skd_targets

class PDSLabel(object):

    def __init__(self, setup, product):

        #
        # The product to be labeled.
        #
        self.product                    = product
        self.setup                      = setup

        #
        # Fields from setup
        #
        self.root_dir                   = setup.root_dir
        self.setup_accronym             = setup.accronym
        self.XML_MODEL                  = setup.xml_model
        self.SCHEMA_LOCATION            = setup.schema_location
        self.INFORMATION_MODEL_VERSION  = setup.information_model_version
        self.PDS4_setup_NAME            = setup.name
        self.PDS4_setup_LID             = setup.lid
        self.CURRENT_YEAR               = current_time().split('-')[0]
        self.BUNDLE_DESCRIPTION_LID     = \
            'urn:nasa:pds:{}.spice:document:spiceds'.format(self.setup_accronym)
        self.PRODUCT_CREATION_TIME      = product.creation_time
        self.FILE_SIZE                  = product.size
        self.FILE_CHECKSUM              = product.checksum

        self.PDS4_SPACECRAFT_NAME = setup.spacecraft

        for context_product in setup.context_products:
            if context_product['name'][0].upper() == setup.spacecraft.upper():
                self.PDS4_SPACECRAFT_TYPE = context_product['type'][0].capitalize()
                self.PDS4_SPACECRAFT_LID  = context_product['lidvid'].split('::')[0]

            #
            # For Bundles with multiple s/c
            #
            if setup.secondary_spacecrafts:

                #
                # We sort out how many S/C we have
                #
                sec_scs = setup.secondary_spacecrafts.split(',')

                for sc in sec_scs:
                    if sc:
                        if sc.lower() in product.name.lower():
                            self.PDS4_SPACECRAFT_NAME = sc

                            for context_product in setup.context_products:
                                if context_product['name'][0].upper() == sc.upper():
                                    self.PDS4_SPACECRAFT_TYPE = context_product['type'][0].capitalize()
                                    self.PDS4_SPACECRAFT_LID = context_product['lidvid'].split('::')[0]


            self.PDS4_TARGET_NAME = setup.target

            for context_product in setup.context_products:
                if context_product['name'][0].upper() ==  setup.target.upper():

                    self.PDS4_TARGET_TYPE = context_product['type'][0].capitalize()
                    self.PDS4_TARGET_LID  = context_product['lidvid'].split('::')[0]

            #
            # For Bundles with multiple targets
            #
            if setup.secondary_targets:

                #
                # We sort out how many S/C we have
                #
                sec_tars = setup.secondary_targets.split(',')

                for tar in sec_tars:
                    if tar:

                        if tar.lower() in product.name.lower():
                            self.PDS4_TARGET_NAME = tar
                            for context_product in setup.context_products:
                                if context_product['name'][0].upper() == tar.upper():
                                    self.PDS4_TARGET_TYPE = context_product['type'][0].capitalize()
                                    self.PDS4_TARGET_LID = context_product['lidvid'].split('::')[0]

            #
            # For labels that need to include all S/C and Targets of the setup
            #
            self.SKD_SPACECRAFTS = get_skd_spacecrafts(setup)
            self.SKD_TARGETS = get_skd_targets(setup, self.get_target_reference_type())

        return


    def get_target_reference_type(self):
        return "data_to_target"


    def write_label(self):

        label_dictionary = vars(self)

        label_extension = '.xml'

        label_name = self.product.path.split('.')[0] + label_extension

        with open(label_name, "w+") as f:

            for line in fileinput.input(self.template):
                line = line.rstrip()
                for key, value in label_dictionary.items():
                    if isinstance(value, str) and key in line and '$' in line:
                        line = line.replace('$'+key, value)

                line = add_carriage_return(line)

                f.write(line)

        return
    

class BundlePDS4Label(PDSLabel):

    def __init__(self, setup, readme):

        PDSLabel.__init__(self, setup, readme)

        self.template = self.root_dir + \
                        '/etc/template_bundle.xml'

        self.BUNDLE_LID = self.product.bundle.lid
        self.BUNDLE_VID = self.product.bundle.vid

        self.START_TIME = setup.start
        self.STOP_TIME = setup.increment_stop
        self.FILE_NAME = readme.name
        self.CURRENT_TIME = current_time()
        self.CURRENT_DATE =self.CURRENT_TIME.split('T')[0]
        self.DOI =  setup.doi


        for collection in self.product.bundle.collections:
            if collection.name == 'spice_kernels':
                self.SPICE_COLL_LIDVID =  collection.lid + '::' + collection.vid
                self.SPICE_COLL_STATUS = 'Primary'
            if collection.name == 'document':
                self.DOC_COLL_LIDVID =  collection.lid + '::' + collection.vid
                self.DOC_COLL_STATUS = 'Primary'

        self.write_label()

        return

    def get_target_reference_type(self):
        return "bundle_to_target"


class SPICEKernelPDS4Label(PDSLabel):

    def __init__(self, mission, product):

        PDSLabel.__init__(self, mission, product)

        self.template = self.root_dir + \
                        '/etc/template_product_spice_kernel.xml'

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

        return


