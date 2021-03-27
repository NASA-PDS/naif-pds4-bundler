import hashlib
import os
import errno
import shutil
import fileinput
import glob
import re
import logging
import json
import platform

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
            logging.warning(f'-- Directory {src.split(os.sep)[-1]} not copied, probably because the increment '
                  'directory exists.\n Error: %s' % e)


def safe_make_directory(i):
    '''Makes a folder if not present'''
    try:  
        os.mkdir(i)
        logging.info(f'-- Generated directory: {i}  ')
        logging.info('')
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

    registered_context_products_file = f'{setup.root_dir}/etc/registered_context_products.json'
    with open(registered_context_products_file, 'r') as f:
            context_products = json.load(f)['Product_Context']

    return context_products


def mk2list(mk):

    path_symbol = ''
    ker_mk_list = []
    with open(mk, 'r') as f:
        for line in f:

            if path_symbol:
                if path_symbol in line:

                    kernel = line.split(path_symbol)[1]
                    kernel = kernel.strip()
                    kernel = kernel[:-1]
                    kernel = kernel.split('/')[-1]

                    ker_mk_list.append(kernel)

            if 'PATH_SYMBOLS' in line.upper():
                path_symbol = '$' + line.split("'")[1]

    return ker_mk_list


def get_latest_kernel(kernel_type, path, pattern, dates=False,
                      excluded_kernels=False,
                      mkgen=False):
    """
    Returns the name of the latest MK, LSK, FK or SCLK present in the path

    :param kernel_type: Kernel type (lsk, sclk, fk) which also defines the subdirectory name.
    :type kernel_type: str
    :param path: Path to the root of the SPICE directory where the kernels are store in a directory named ``type``.
    :type path: str
    :param patterns: Patterns to search for that defines the kernel ``type`` file naming scheme.
    :type patterns: list
    :return: Name of the latest kernel of ``type`` that matches the naming scheme defined in ``token`` present in the ``path`` directory.
    :rtype: strÐ
    :raises:
       KernelNotFound if no kernel of ``type`` matching the naming scheme
       defined in ``token is present in the ``path`` directory
    """
    kernels = []
    kernel_path = os.path.join(path, kernel_type)

    #
    # Get the kernels of type ``type`` from the ``path``/``type`` directory.
    #
    kernels_with_path = glob.glob(kernel_path + '/' + pattern)

    #
    # Include kernels in former_versions if the directory exists except for
    # meta-kernel generation
    #
    if os.path.isdir(kernel_path + '/former_versions') and not mkgen:
        kernels_with_path += glob.glob(kernel_path + '/former_versions/' + pattern )


    for kernel in kernels_with_path:
        kernels.append(kernel.split('/')[-1])

    #
    # Put the kernels in order
    #
    kernels.sort()

    #
    # We remove the kernel if it is included in the excluded kernels list
    #
    if excluded_kernels:
        for excluded_kernel in excluded_kernels:
            for kernel in kernels:
                if excluded_kernel.split('*')[0] in kernel:
                    kernels.remove(kernel)

    if not dates:
        #
        # Return the latest kernel
        #
        try:
            return kernels.pop()
        except:
            logging.warning('     No kernels found with pattern {}'.format(pattern))
            return []
    else:
        #
        # Return all the kernels with a given date
        #
        previous_kernel = ''
        kernels_date = []
        for kernel in kernels:
            if previous_kernel \
                    and re.split('_V\d\d', previous_kernel.upper())[0] == re.split('_V\d\d', kernel.upper())[0]\
                    or re.split('_V\d\d\d', previous_kernel.upper())[0] == re.split('_V\d\d\d', kernel.upper())[0]:
                kernels_date.remove(previous_kernel)

            previous_kernel = kernel
            kernels_date.append(kernel)

        return kernels_date


def get_exe_dir():

    if platform.system() == 'Darwin':
        if platform.machine() == 'x86_64':
            executables_dir = '/exe/macintel_osx_64bit'
    else:
        executables_dir = '/exe/pc_linux_64bit'

    return executables_dir


def check_consecutive(l):
    return sorted(l) == list(range(1, max(l)+1))
