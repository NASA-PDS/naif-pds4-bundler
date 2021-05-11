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
import difflib

from collections import defaultdict

from npb.classes.log import error_message


def etree_to_dict(t):
    '''
    The following XML-to-Python-dict snippet parses entities as well as
    attributes following this XML-to-JSON "specification". It is the most
    general solution handling all cases of XML.

    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html

    :param t:
    :return:
    '''

    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


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


def add_crs_to_file(file):

    try:
        file_crs = file.split('.')[0] + 'crs_tmp'
        with open(file, "r") as r:
            with open(file_crs, "w+") as f:
                for line in r:
                    line = add_carriage_return(line)
                    f.write(line)
        shutil.move(file_crs, file)

    except:
        error_message(f'Carriage return adding error for {file}')

    return


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

    #
    # First look into the setup object and check if the context product is
    # available, otherwise get it from the json file included in the
    # package.
    #

    #
    # Load the default context products
    #
    registered_context_products_file = f'{setup.root_dir}/templates/registered_context_products.json'
    with open(registered_context_products_file, 'r') as f:
            context_products = json.load(f)['Product_Context']

    #
    # Overwrite the default context products with the ones provided in the
    # configuration file.
    #
    appended_products = []
    if not isinstance(setup.context_products['product'], list):
        context_products_list = [setup.context_products['product']]
    else:
        context_products = setup.context_products['product']
    for product in context_products_list:
        updated_product = False
        index = 0
        for registered_product in context_products:
            if registered_product['name'][0] ==  product['@name']:
                updated_product = True
                context_products[index]['type'] = [product['type']]
                context_products[index]['lidvid'] = product['lidvid']
            index += 1
        if not updated_product:
            appended_products.append(
                {'name':[product['@name']],
                 'type':[product['type']],
                 'lidvid':product['lidvid']})

    if appended_products:
        for product in appended_products:
            setup.context_products['product'].append(product)

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


def get_latest_kernel(kernel_type, paths, pattern, dates=False,
                      excluded_kernels=False, mks=False):
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
    kernels_with_path = []

    for path in paths:
        try:
            kernel_path = os.path.join(path, kernel_type)

            #
            # Get the kernels of type ``type`` from the ``path``/``type`` directory.
            #
            kernels_with_path += [f for f in os.listdir(f'{kernel_path}/') if re.search(pattern, f)]

        except:
            pass

    if mks:
        for mk in mks:
            with open(mk, 'r') as m:
                for line in m:
                    if re.findall(pattern, line):
                        kernels_with_path.append(line.strip())

    kernels_with_path = list(dict.fromkeys(kernels_with_path))

    for kernel in kernels_with_path:
        kernel = kernel.split('/')[-1].split("'")[0]
        if "'" in kernel:
            kernels.append(kernel[:-1])
        else:
            kernels.append(kernel)

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
            logging.warning('        No kernels found with pattern {}'.format(pattern))
            return []
    else:
        #
        # Return all the kernels with a given date
        #
        previous_kernel = ''
        kernels_date = []
        for kernel in kernels:
            if previous_kernel \
                    and re.split('_V[0-9]*', previous_kernel.upper())[0] == re.split('_V[0-9]*', kernel.upper())[0]:
                kernels_date.remove(previous_kernel)

            previous_kernel = kernel
            kernels_date.append(kernel)

        return kernels_date


def check_consecutive(l):
    return sorted(l) == list(range(1, max(l)+1))


def compare_files(fromfile, tofile, dir, display):

    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    if display in ['all','log']:

        diff = difflib.Differ()
        diff_list = list(diff.compare(fromlines, tolines))
        for line in diff_list:
            if (line[0] == '+') or (line[0] == '-') or (line[0] == '?'):
                logging.info(line[:-1])

    if display in ['all','files']:
        diff = difflib.HtmlDiff().make_file(fromlines, tolines, fromfile, tofile, context=False, numlines=False)

        diff_html = open(dir + \
                         f"/diff_{fromfile.split(os.sep)[-1].replace('.','_')}_{tofile.split(os.sep)[-1].replace('.','_')}.html",
                         "w")
        diff_html.writelines(diff)
        diff_html.close()

    return


def match_patterns(name, name_w_pattern, patterns):
    '''
    Function to match the meta-kernel names with the patterns provided via
    configuration.
    '''

    #
    # This list will help us determine the order of the patterns in the file
    # name because later on the patterns need to be correlated with the
    # pattern values.
    #
    pattern_name_order = {}
    name_check = name_w_pattern

    for pattern in patterns:
        pattern_name_order[pattern['#text']] = name_w_pattern.find(pattern['#text'])
        name_check = name_check.replace('$' + pattern['#text'], '$'*int(pattern['@lenght']))

    #
    # Convert the pattern_name_order_dictionary into an ordered lis
    #
    pattern_name_order = list({k: v for k, v in sorted(pattern_name_order.items(), key=lambda item: item[1])}.keys())

    #
    # Generate a list of values extracted from the comparison of the original
    # file and the file with patterns.
    #
    values_list = []
    value = ''
    value_bool = False

    for i in range(len(name_check)):
        if (name_check[i] == name[i]) and (not value_bool):
            continue
        if (name_check[i] == name[i]) and value_bool:
            value_bool = False
            values_list.append(value)
            value = ''
        elif (name_check[i] == '$') and (not value_bool):
            value_bool = True
            value += name[i]
        elif (name_check[i] == '$') and value_bool:
            value += name[i]
        else:
            error_message(f'Missmatch of values in meta-kernel pattern.')

    #
    # Correlate the values with their position in the file name with
    # patterns.
    #
    values = {}
    for i in range(len(values_list)):
        values[pattern_name_order[i]] = values_list[i]

    return values

