import datetime
import calendar
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
    date = datetime.datetime.strftime(timestamp, '%m %dT, %Y')

    date = calendar.month_name[int(date[0:2])] + date[2:]

    return creation_date


def PDS3_label_gen_date(file):

    generation_date = 'N/A'

    with open(file, 'r') as f:

        for line in f:
            if 'PRODUCT_CREATION_TIME' in line:
                generation_date = line.split('=')[1].strip()

    return generation_date