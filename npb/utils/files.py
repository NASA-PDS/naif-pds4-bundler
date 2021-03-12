import hashlib
import os
import errno
import shutil
import fileinput
import glob
import re
import logging
import json

from os import listdir
from os.path import isfile, join, dirname
from shutil import copyfile


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logging.warning('Directory not copied, probably because the increment '
                  'directory exists.\n Error: %s' % e)


def safe_make_directory(i):
    '''Makes a folder if not present'''
    try:  
        os.mkdir(i)
    except:
        pass


def extension2type(kernel):

    kernel_type_map = {
        "TI":  "IK",
        "TF":  "FK",
        "TM":  "MK",
        "TSC": "SCLK",
        "TLS": "LSK",
        "TPC": "PCK",
        "BC":  "CK",
        "BSP": "SPK",
        "BPC": "PCK",
        "BES": "EK",
        "BDS": "DSK",
        "ORB": "ORB"
    }

    try:
        #
        # Kernel is an object
        #
        kernel_type = kernel_type_map[kernel.extension.upper()].lower()
    except:
        #
        # Kernel is a string
        #
        kernel_type = kernel_type_map[kernel.split('.')[-1].upper()].lower()

    return kernel_type


def type2extension(kernel_type):

    kernel_type = kernel_type.upper()


    kernel_type_map = {
        "IK": ["ti"],
        "FK": ["tf"],
        "MK": ["tm"],
        "SCLK": ["tsc"],
        "LSK": ["tls"],
        "PCK": ["tpc","bpc"],
        "CK": ["bc"],
        "SPK": ["bsp"],
        "DSK": ["bds"]
    }

    kernel_extension = kernel_type_map[kernel_type]

    return kernel_extension


def add_carriage_return(line):
    #
    # Adding CR to line
    #
    if '\r\n' not in line:
        line = line.replace('\n', '\r\n')
    if '\r\n' not in line:
        line += '\r\n'

    return line


def check_list_duplicates(listOfElems):
    ''' Check if given list contains any duplicates '''
    for elem in listOfElems:
        if listOfElems.count(elem) > 1:
            return True
    return False


def fill_template(object, product_file, product_dictionary):

    with open(product_file, "w+") as f:

        for line in fileinput.input(object.template):
            line = line.rstrip()
            for key, value in product_dictionary.items():
                if isinstance(value, str) and key in line and '$' in line:
                    line = line.replace('$' + key, value)
            f.write(f'{line}\n')

    return


def get_context_products(setup):

    registered_context_products_file = f'{setup.root_dir}/config/registered_context_products.json'
    with open(registered_context_products_file, 'r') as f:
            context_products = json.load(f)['Product_Context']

    return context_products