import datetime
import calendar
import spiceypy
import os


def current_time():

    time = str(datetime.datetime.now())
    time = time.replace(' ', 'T')
    time = time.split('.')[0]

    return time


def current_date():

    time = datetime.datetime.now()
    date = datetime.datetime.strftime(time, '%m %d, %Y')

    date = calendar.month_name[int(date[0:2])] + date[2:]
    return date


def creation_time(path):

    t = os.path.getmtime(path)
    timestamp = datetime.datetime.fromtimestamp(t)
    dt, micro = datetime.datetime.strftime(timestamp, '%Y-%m-%dT%H:%M:%S.%f').split('.')
    creation_time = "%s.%03d" % (dt, int(micro) / 1000) + 'Z'

    return creation_time


def creation_date(path):

    t = os.path.getmtime(path)
    timestamp = datetime.datetime.fromtimestamp(t)
    date = datetime.datetime.strftime(timestamp, '%m %d, %Y')

    creation_date = calendar.month_name[int(date[0:2])] + date[2:]

    return creation_date


def spk_coverage(path):

    ids = spiceypy.spkobj(path)

    MAXIV = 1000
    WINSIZ = 2 * MAXIV
    TIMLEN = 62

    coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

    start_points_list = list()
    end_points_list = list()

    for id in ids:

        spiceypy.scard, 0, coverage
        spiceypy.spkcov(spk=path, idcode=id, cover=coverage)

        num_inter = spiceypy.wncard(coverage)

        for i in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, i)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])


    start_time = min(start_points_list)
    stop_time = max(end_points_list)

    start_time_cal = spiceypy.timout(start_time,
                                     "YYYY-MM-DDTHR:MN:SC.###::UTC::RND", TIMLEN) + 'Z'
    stop_time_cal = spiceypy.timout(stop_time,
                                    "YYYY-MM-DDTHR:MN:SC.###::UTC::RND", TIMLEN) + 'Z'

    return [start_time_cal, stop_time_cal]


def ck_coverage(path):

    start_points_list = list()
    end_points_list = list()

    MAXIV = 10000
    WINSIZ = 2 * MAXIV
    TIMLEN = 500
    MAXOBJ = 10000

    ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)
    ids = spiceypy.ckobj(ck=path, out_cell=ids)

    for id in ids:

        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)
        spiceypy.scard, 0, coverage
        coverage = spiceypy.ckcov(ck=path, idcode=id, needav=False,
                                level='SEGMENT', tol=0.0, timsys='TDB',
                                cover=coverage)

        num_inter = spiceypy.wncard(coverage)

        for j in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, j)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])


    start_time = min(start_points_list)
    stop_time = max(end_points_list)

    start_time_cal = spiceypy.timout(start_time,
                                   "YYYY-MM-DDTHR:MN:SC.###::UTC::RND", TIMLEN) + 'Z'
    stop_time_cal = spiceypy.timout(stop_time, "YYYY-MM-DDTHR:MN:SC.###::UTC::RND",
                                  TIMLEN) + 'Z'

    return [start_time_cal, stop_time_cal]

#
# PCK kernel processing
#
def pck_coverage(path):

    MAXIV = 1000
    WINSIZ = 2 * MAXIV
    TIMLEN = 62
    MAXOBJ = 1000

    ids = spiceypy.support_types.SPICEINT_CELL(MAXOBJ)

    spiceypy.pckfrm(path, ids)

    coverage = spiceypy.support_types.SPICEDOUBLE_CELL(WINSIZ)

    start_points_list = list()
    end_points_list = list()

    for id in ids:

        spiceypy.scard, 0, coverage
        spiceypy.pckcov(pck=path, idcode=id, cover=coverage)

        num_inter = spiceypy.wncard(coverage)

        for i in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, i)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])

    start_time_tbd = min(start_points_list)
    stop_time_tbd = max(end_points_list)

    start_time_cal = spiceypy.timout(start_time_tbd,
                                   "YYYY-MM-DDTHR:MN:SC.###::UTC::RND", TIMLEN) + 'Z'
    stop_time_cal = spiceypy.timout(stop_time_tbd,
                                  "YYYY-MM-DDTHR:MN:SC.###::UTC::RND", TIMLEN) + 'Z'


    return [start_time_cal, stop_time_cal]

#
# DSK kernel processing
#
def dsk_coverage(self):

    start_time_cal = self.setup.mission_start
    stop_time_cal  = self.setup.mission_stop

    return [start_time_cal, stop_time_cal]



def PDS3_label_gen_date(file):

    generation_date = 'N/A'

    with open(file, 'r') as f:

        for line in f:
            if 'PRODUCT_CREATION_TIME' in line:
                generation_date = line.split('=')[1].strip()

    return generation_date