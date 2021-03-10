import datetime
import os

def current_time():

    time = str(datetime.datetime.now())
    time = time.replace(' ', 'T')
    time = time.split('.')[0]

    return time


def creation_time(path):

    t = os.path.getmtime(path)
    timestamp = datetime.datetime.fromtimestamp(t)
    dt, micro = datetime.datetime.strftime(timestamp, '%Y-%m-%dT%H:%M:%S.%f').split('.')
    creation_time = "%s.%03d" % (dt, int(micro) / 1000) + 'Z'

    return creation_time


def PDS3_label_gen_date(file):

    generation_date = 'N/A'

    with open(file, 'r') as f:

        for line in f:
            if 'PRODUCT_CREATION_TIME' in line:
                generation_date = line.split('=')[1].strip()

    return generation_date