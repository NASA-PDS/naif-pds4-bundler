import os
import logging
import shutil
import fileinput
import spiceypy

from npb.classes.label import BundlePDS4Label
from npb.classes.label import SpiceKernelPDS4Label
from npb.classes.log   import error_message
from npb.utils.files   import md5
from npb.utils.time    import creation_time
from npb.utils.files   import add_carriage_return

from npb.utils.files import extension2type
from npb.utils.files import safe_make_directory


class Product(object):
    
    def __init__(self):

        stat_info          = os.stat(self.path)
        self.size          = str(stat_info.st_size)
        self.checksum      = str(md5(self.path))
        self.creation_time = creation_time(self.path)[:-5]


class SpiceKernelProduct(Product):

    def __init__(self, setup, name, collection):

        self.collection = collection
        self.setup      = setup
        self.name       = name
        self.extension  = name.split('.')[-1].strip()
        self.type       = extension2type(self)


        self.path      = setup.kernel_directory + os.sep + self.type


        if self.extension[0].lower() == 'b':
            self.file_format = 'Binary'
        else:
            self.file_format = 'Character'


        self.coverage()

        if setup.pds == '3':
            print('HOLD IT')


        self.description = self.get_description()

        self.collection_path = setup.staging_directory + os.sep + \
                       'spice_kernels' + os.sep

        product_path = self.collection_path + self.type + os.sep

        self.lid = self.product_lid()
        self.vid = self.product_vid()

        #
        # We generate the kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # We copy the kernel to the staging directory.
        #
        if not os.path.isfile(product_path + self.name):
            try:
                shutil.copy2(self.path + os.sep + self.name,
                             product_path + os.sep + self.name)
                self.new_product = True
            except:
                error_message(f'{self.name} not present in {self.path}')
        else:
            logging.error('{} already present in staging directory'.format(self.name))
            self.new_product = False
            return

        #
        # We update the path after having copied the kernel.
        #
        self.path = product_path + self.name


        Product.__init__(self)

        #
        # The kernel is labeled.
        #
        self.label = SpiceKernelPDS4Label(setup, self)


        return


    def product_lid(self):

        product_lid = \
            'urn:nasa:pds:{}.spice:spice_kernels:{}_{}'.format(
                    self.setup.mission_accronym,
                    self.type,
                    self.name)

        return product_lid

    def product_vid(self):

        product_vid = '1.0'


        return product_vid


    def coverage(self):
        if self.type.lower() == 'spk':
            (self.start_time, self.stop_time) = self.spk_coverage()
        elif self.type.lower() == 'ck':
            (self.start_time, self.stop_time) = self.ck_coverage()
        elif self.extension.lower() == 'bpc':
            (self.start_time, self.stop_time) = self.pck_coverage()
        elif self.type.lower() == 'sclk':
            (self.start_time, self.stop_time) = self.sclk_coverage()

        else:
            self.start_time = self.setup.mission_start
            self.stop_time = self.setup.mission_stop


    def spk_coverage(self):

        ids = spiceypy.spkobj(self.path)

        MAXIV = 1000
        WINSIZ = 2 * MAXIV
        TIMLEN = 62

        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

        start_points_list = list()
        end_points_list = list()

        for id in ids:

            spiceypy.scard, 0, coverage
            spiceypy.spkcov(spk=self.path, idcode=id, cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for i in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, i)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])

                time_str = spiceypy.timout(endpoints,
                                           "YYYY-MM-DDTHR:MN:SC.###::UTC",
                                           TIMLEN)
        start_time = min(start_points_list)
        stop_time = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time,
                                         "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time,
                                        "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'

        return [start_time_cal, stop_time_cal]


    def ck_coverage(self):


        start_points_list = list()
        end_points_list = list()

        MAXIV = 10000
        WINSIZ = 2 * MAXIV
        TIMLEN = 500
        MAXOBJ = 10000

        ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)
        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

        # Note: ckobj param outCell changed to out_cell since version 3.0.0
        spiceypy_version = 2
        if hasattr(spiceypy, '__version__'):
            spiceypy_version = int(spiceypy.__version__[0])

        if spiceypy_version >= 3:
            ids = spiceypy.ckobj(ck=self.path, out_cell=ids)
        else:
            ids = spiceypy.ckobj(ck=self.path, outCell=ids)

        num_ids = spiceypy.card(ids)
        for id in ids:

            coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)
            spiceypy.scard, 0, coverage
            coverage = spiceypy.ckcov(ck=self.path, idcode=id, needav=False,
                                    level='SEGMENT', tol=0.0, timsys='TDB',
                                    cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for j in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, j)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])

                time_str = spiceypy.timout(endpoints,
                                         "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN)

        start_time = min(start_points_list)
        stop_time = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time,
                                       "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time, "YYYY-MM-DDTHR:MN:SC.###::UTC",
                                      TIMLEN) + 'Z'

        return [start_time_cal, stop_time_cal]

    #
    # PCK kernel processing
    #
    def pck_coverage(self):

        MAXIV = 1000
        WINSIZ = 2 * MAXIV
        TIMLEN = 62
        MAXOBJ = 1000

        ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)

        spiceypy.pckfrm(self.path, ids)

        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

        start_points_list = list()
        end_points_list = list()

        for id in ids:

            spiceypy.scard, 0, coverage
            spiceypy.pckcov(pck=self.path, idcode=id, cover=coverage)

            num_inter = spiceypy.wncard(coverage)

            for i in range(0, num_inter):
                endpoints = spiceypy.wnfetd(coverage, i)

                start_points_list.append(endpoints[0])
                end_points_list.append(endpoints[1])

                time_str = spiceypy.timout(endpoints,
                                         "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN)

        start_time_tbd = min(start_points_list)
        stop_time_tbd = max(end_points_list)

        start_time_cal = spiceypy.timout(start_time_tbd,
                                       "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'
        stop_time_cal = spiceypy.timout(stop_time_tbd,
                                      "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'


        return [start_time_cal, stop_time_cal]

    #
    # SCLK kernel processing
    #
    def sclk_coverage(self):

        TIMLEN = 62

        spiceypy.furnsh(self.path)

        with open(self.path, "r") as f:

            for line in f:

                if 'SCLK_DATA_TYPE_' in line:
                    line = line.lstrip()
                    line = line.split("SCLK_DATA_TYPE_")
                    line = line[1].split("=")[0]
                    id = int('-' + line.rstrip())

        partitions = spiceypy.scpart(id)

        #
        # We need to take into account clocks that have more than one partition
        #
        if len(partitions[0]) > 1.0:
            partitions = partitions[0]
        start_time_tdb = spiceypy.sct2e(id, partitions[0])
        if isinstance(start_time_tdb, (list, np.ndarray)):
            start_time_tdb = start_time_tdb[0]
        start_time_cal = spiceypy.timout(start_time_tdb,
                                       "YYYY-MM-DDTHR:MN:SC.###::UTC", TIMLEN) + 'Z'

        stop_time_cal = self.setup.stop

        return [start_time_cal, stop_time_cal]

    #
    # IK kernel processing
    #
    def ik_kernel_ids(self, path):

        with open(path, "r") as f:

            id_list = list()
            parse_bool = False

            for line in f:

                if 'begindata' in line:
                    parse_bool = True

                if 'begintext' in line:
                    parse_bool = False

                if 'INS-' in line and parse_bool == True:
                    line = line.lstrip()
                    line = line.split("_")
                    id_list.append(line[0][3:])

        id_list = list(set(id_list))

        return [id_list]

    #
    # Obtain the kernel description information
    #
    def get_description(self):

        kernel_list_file = self.setup.working_directory + os.sep + \
                           f'{self.setup.mission_accronym}_release_' \
                           f'{self.setup.release}.kernel_list'

        get_descr   = False
        description = False

        for line in fileinput.input(kernel_list_file):
            if self.name in line:
                get_descr = True
            if  get_descr and 'DESCRIPTION' in line:
                description = line.split('=')[-1].strip()
                get_descr = False

        if not description:
            error_message(f'{self.name} does not have '
                          f'a description on {kernel_list_file}')

        return description


    def kernel_setup_phase(self):

        # avoid reading the Z at the end of UTC tag
        start_time = self.start_time[0:-1] if self.start_time != 'N/A' else 'N/A'
        stop_time = self.stop_time[0:-1] if self.stop_time != 'N/A' else 'N/A'

        setup_phase_map = self.setup.root_dir + \
                            '/config/{}.phases'.format(self.setup.accronym.lower())

        with open(setup_phase_map, 'r') as f:
            setup_phases = list()

            if start_time == 'N/A' and stop_time == 'N/A':

                for line in f:
                    setup_phases.append(line.split('   ')[0])

            if start_time != 'N/A' and stop_time == 'N/A':

                next_phases_bool = False
                start_tdb = spiceypy.str2et(start_time)  # + ' TDB')

                for line in f:
                    start_phase_date = line.rstrip().split(' ')[-2]
                    start_phase_tdb = spiceypy.str2et(start_phase_date)

                    stop_phase_date = line.rstrip().split(' ')[-1]
                    stop_phase_tdb = spiceypy.str2et(stop_phase_date)

                    if next_phases_bool == True:
                        setup_phases.append(line.split('   ')[0])

                    elif start_tdb >= start_phase_tdb:
                        setup_phases.append(line.split('   ')[0])
                        next_phases_bool = True

            if start_time != 'N/A' and stop_time != 'N/A':

                next_phases_bool = False
                start_tdb = spiceypy.str2et(start_time)  # + ' TDB')
                stop_tdb = spiceypy.str2et(stop_time)  # + ' TDB')

                for line in f:

                    start_phase_date = line.rstrip().split(' ')[-2]
                    start_phase_tdb = spiceypy.str2et(
                        start_phase_date)  # + ' TDB')

                    stop_phase_date = line.rstrip().split(' ')[-1]
                    stop_phase_tdb = spiceypy.str2et(stop_phase_date)
                    stop_phase_tdb += 86400
                    #  One day added to account for gap between phases.

                    if next_phases_bool == True and start_phase_tdb >= stop_tdb:
                        break
                    # if next_phases_bool == True:
                    #     setup_phases.append(line.split('   ')[0])
                    # if start_phase_tdb <= start_tdb <= stop_phase_tdb:
                    #     setup_phases.append(line.split('   ')[0])
                    #     next_phases_bool = True
                    if start_tdb <= stop_phase_tdb:
                        setup_phases.append(line.split('   ')[0])
                        next_phases_bool = True

        setup_phases_str = ''
        for phase in setup_phases:
            setup_phases_str += '                                 ' + phase + ',\r\n'

        setup_phases_str = setup_phases_str[0:-3]

        self.setup_phases = setup_phases_str

        return


class ReadmeProduct(Product):

    def __init__(self, setup, bundle):

        self.name    = 'readme.txt'
        self.bundle  = bundle
        self.path    = setup.bundle_directory + os.sep+ self.name
        self.setup   = setup
        self.vid     = bundle.vid

        self.write_product()
        Product.__init__(self)

        #
        # Now we change the path for the difference of the name in the label
        #
        self.path  = setup.bundle_directory + os.sep + bundle.name

        self.label = BundlePDS4Label(setup, self)

        return


    def write_product(self):

        if not os.path.isfile(self.path):
            with open(self.path, "w+") as f:

                for line in fileinput.input(self.setup.root_dir+'/etc/template_readme.txt'):
                    if '$PDS4_setup_NAME' in line:
                        line = line.replace('$PDS4_setup_NAME', self.setup.name)
                    if '$AUTHOR' in line:
                        line = line.replace('$AUTHOR', self.setup.author)

                    line = add_carriage_return(line)

                    f.write(line)

        return
    
    
