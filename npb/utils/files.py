#   -------------------------------------------------------------------------
#   @author: Marc Costa Sitja (JPL)
#
#   THIS SOFTWARE AND ANY RELATED MATERIALS WERE CREATED BY THE
#   CALIFORNIA INSTITUTE OF TECHNOLOGY (CALTECH) UNDER A U.S.
#   GOVERNMENT CONTRACT WITH THE NATIONAL AERONAUTICS AND SPACE
#   ADMINISTRATION (NASA). THE SOFTWARE IS TECHNOLOGY AND SOFTWARE
#   PUBLICLY AVAILABLE UNDER U.S. EXPORT LAWS AND IS PROVIDED "AS-IS"
#   TO THE RECIPIENT WITHOUT WARRANTY OF ANY KIND, INCLUDING ANY
#   WARRANTIES OF PERFORMANCE OR MERCHANTABILITY OR FITNESS FOR A
#   PARTICULAR USE OR PURPOSE (AS SET FORTH IN UNITED STATES UCC
#   SECTIONS 2312-2313) OR FOR ANY PURPOSE WHATSOEVER, FOR THE
#   SOFTWARE AND RELATED MATERIALS, HOWEVER USED.
#
#   IN NO EVENT SHALL CALTECH, ITS JET PROPULSION LABORATORY, OR NASA
#   BE LIABLE FOR ANY DAMAGES AND/OR COSTS, INCLUDING, BUT NOT
#   LIMITED TO, INCIDENTAL OR CONSEQUENTIAL DAMAGES OF ANY KIND,
#   INCLUDING ECONOMIC DAMAGE OR INJURY TO PROPERTY AND LOST PROFITS,
#   REGARDLESS OF WHETHER CALTECH, JPL, OR NASA BE ADVISED, HAVE
#   REASON TO KNOW, OR, IN FACT, SHALL KNOW OF THE POSSIBILITY.
#
#   RECIPIENT BEARS ALL RISK RELATING TO QUALITY AND PERFORMANCE OF
#   THE SOFTWARE AND ANY RELATED MATERIALS, AND AGREES TO INDEMNIFY
#   CALTECH AND NASA FOR ALL THIRD-PARTY CLAIMS RESULTING FROM THE
#   ACTIONS OF RECIPIENT IN THE USE OF THE SOFTWARE.
#   -------------------------------------------------------------------------
"""
File and Text Management Functions
------------------------------------
"""
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

    :param t: Element Tree read from XML file
    :return: XML File converted into a JSON file
    '''
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
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
    """
    Returns the MD5 sum (checksum) of the provided file.

    :param fname: Filename
    :type fname: str
    :return: Checksum value of the file
    :rtype str
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def copy(src, dest):
    """
    Creates a directory and raises an error if the directort already
    exists.

    :param src: Source directory with path.
    :param dest: Destination directory with path.
    """
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        #
        # If the error was caused because the source was not a directory.
        #
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            logging.warning(f'-- Directory {src.split(os.sep)[-1]} not '
                            f'copied, probably because the increment '
                            'directory exists.\n Error: %s' % e)

    return None


def safe_make_directory(dir):
    """
    Creates a directory if it is not present

    :param i: Directory with path.
    """
    try:
        os.mkdir(dir)
        logging.info(f'-- Generated directory: {dir}  ')
        logging.info('')
    except:
        pass

    return None


def extension2type(kernel):
    """
    Given a SPICE kernel provide the SPICE kernel type.

    :param kernel: SPICE Kernel name
    :return: SPICE Kernel type of the input SPICE kernel name.
    :rtype: str
    """
    kernel_type_map = {
        "TI": "IK",
        "TF": "FK",
        "TM": "MK",
        "TSC": "SCLK",
        "TLS": "LSK",
        "TPC": "PCK",
        "BC": "CK",
        "BSP": "SPK",
        "BPC": "PCK",
        "BES": "EK",
        "BDS": "DSK",
        "ORB": "ORB",
        "NRB": "ORB"
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
    """
    Given a SPICE kernel type provide the SPICE kernel extension.

    :param kernel_type: SPICE kernel type
    :return: Spice Kernel extension
    :rtype: str
    """
    kernel_type = kernel_type.upper()

    kernel_type_map = {
        "IK": ["ti"],
        "FK": ["tf"],
        "MK": ["tm"],
        "SCLK": ["tsc"],
        "LSK": ["tls"],
        "PCK": ["tpc", "bpc"],
        "CK": ["bc"],
        "SPK": ["bsp"],
        "DSK": ["bds"]
    }

    kernel_extension = kernel_type_map[kernel_type]

    return kernel_extension


def add_carriage_return(line, eol):
    '''
    Adds Carriage Return (CR) to a line

    :param line: Input line
    :type line: str
    :param eol: EOL defined by setup.
    :type eol: str
    :return: Input line with CR
    :rtype: str
    '''
    if eol == '\r\n' and '\r\n' not in line:
        line = line.replace('\n', '\r\n')
    if eol == '\r\n' and '\r\n' not in line:
        if '\r\n' not in line:
            line += '\r\n'
        else:
            error_message(f'File has incorrect CR at line: {line}')
    if eol == '\n' and '\r\n' in line:
        line = line.replace('\r\n', '\n')
    elif eol == '\n'and not '\n' in line:
        line += '\n'
    else:
        if '\n' not in line:
            error_message(f'File has incorrect CR at line: {line}')

    return line


def add_crs_to_file(file, eol):
    '''
    Adds Carriage Return (CR) to a file

    :param line: Input file
    :type line: str
    :param eol: End of Line character as indicated by setup
    :type eol: str
    :raise: If CR cannot be added to the file
    '''
    try:
        file_crs = file.split('.')[0] + 'crs_tmp'
        with open(file, "r") as r:
            with open(file_crs, "w+") as f:
                for line in r:
                    line = add_carriage_return(line, eol)
                    f.write(line)
        shutil.move(file_crs, file)

    except:
        error_message(f'Carriage return adding error for {file}')

    return None


def check_list_duplicates(listOfElems):
    '''
    Check if given list contains any duplicates.

    :param listOfElems: List of SPICE kernel names
    :return: Boolean that indicats if the input list contains
             duplicates or not
    :rtype: bool
    '''
    for elem in listOfElems:
        if listOfElems.count(elem) > 1:
            return True

    return False


def fill_template(object, product_file, product_dictionary):
    """

    :param object:
    :param product_file:
    :param product_dictionary:
    :return:
    """
    with open(product_file, "w+") as f:

        for line in fileinput.input(object.template):
            line = line.rstrip()
            for key, value in product_dictionary.items():
                if isinstance(value, str) and key in line and '$' in line:
                    line = line.replace('$' + key, value)
            f.write(f'{line}\n')

    return None


def get_context_products(setup):
    """
    Obtain the context products from the PDS4 registered context products
    templte or from the XML configuration file.

    :param setup: Setup object already constructed
    :return: dictionary with the JSON structure of the bundle context products
    :rtype: dict
    """
    #
    # First look into the setup object and check if the context product is
    # available, otherwise get it from the json file included in the
    # package.
    #
    # Load the default context products
    #
    registered_context_products_file = \
        f'{setup.root_dir}/templates/registered_context_products.json'
    with open(registered_context_products_file, 'r') as f:
        context_products = json.load(f)['Product_Context']

    #
    # Overwrite the default context products with the ones provided in the
    # configuration file.
    #
    appended_products = []
    if hasattr(setup, 'context_products'):
        if not isinstance(setup.context_products['product'], list):
            context_products_list = [setup.context_products['product']]
        else:
            context_products_list = setup.context_products['product']
        for product in context_products_list:
            if product:
                updated_product = False
                index = 0
                for registered_product in context_products:
                    if registered_product['name'][0] == product['@name']:
                        updated_product = True
                        context_products[index]['type'] = [product['type']]
                        context_products[index]['lidvid'] = product['lidvid']
                    index += 1
                if not updated_product:
                    appended_products.append(
                        {'name': [product['@name']],
                         'type': [product['type']],
                         'lidvid': product['lidvid']})

    if appended_products:
        for product in appended_products:
            context_products.append(product)

    #
    # Return the context products used in the bundle.
    #
    bundle_context_products = []
    config_context_products = [setup.observer, setup.target]
    
    #
    # Check the secondary s/c and if present add them to the
    # Configuration for context products.3
    #
    if hasattr(setup, 'secondary_observers'):
        for sc in setup.secondary_observers:
            config_context_products.append(sc)

    #
    # Check the secondary targets and if present add them to the
    # Configuration for context products.3
    #
    if hasattr(setup, 'secondary_targets'):
        for tar in setup.secondary_targets:
            config_context_products.append(tar)

    for context_product in context_products:
        for config_product in config_context_products:
            #
            # For the conditional statement we need to put both names lower case.
            #
            if context_product['name'][0].lower() == config_product.lower():
                bundle_context_products.append(context_product)

    return bundle_context_products


def mk2list(mk):
    """
    Generate a list of kernels from a meta-kernel. This function assumes
    that the meta-kernel will contain a PATH_SYMBOLS definition that will
    be present in each kernel entry preceeded by a dollar sign ($).

    :param mk: Meta-kernel
    :return: List of kernels present in the meta-kernel
    :rtype: list
    """
    path_symbol = ''
    ker_mk_list = []
    with open(mk, 'r') as f:
        for line in f:

            if path_symbol:
                if path_symbol in line:
                    kernel = line.split("'")[1]
                    kernel = kernel.split(path_symbol)[1]
                    kernel = kernel.strip()
                    kernel = kernel.split('\n')[0]
                    kernel = kernel.split('\r')[0]
                    kernel = kernel.split('/')[-1]

                    ker_mk_list.append(kernel)

            if 'PATH_SYMBOLS' in line.upper():
                path_symbol = '$' + line.split("'")[1]

    return ker_mk_list


def get_latest_kernel(kernel_type, paths, pattern, dates=False,
                      excluded_kernels=False, mks=False):
    """
    Returns the name of the latest SPICE kernel of a given type present
    in the path. This function is exclusively used find the latest version
    of the kernels to be included in a meta-kernel.

    :param kernel_type: SPICE Kernel type which also defines
                        the subdirectory name
    :param paths: List of paths to the roots of the SPICE Kernels directories
                  where the kernels are store in a subdirectory named `type'.
    :param pattern: Patterns to search for that defines the kernel `type'
                    file naming scheme. This pattern follows the format of
                    the meta-kernel grammar provided in the XML configuration
                    file
    :param dates: Indicates that the pattern of the kernel includes dates
                  and that the last version of each kernel with a date has
                  to be included. If this parameter is set to False then
                  only the latest date and latest version is included
    :param excluded_kernels: Indicates that a specific kernel might have
                             to be excluded from the search.
    :mks: Indicates that the kernels present in the list of provided
          meta-kernels have to be incldued for consideration to obtain
          the latest version of the given kernel
    :return: Name of the latest kernels as specified by the pattern.
    :rtype: list
    """
    kernels = []
    kernels_with_path = []

    for path in paths:
        try:
            kernel_path = os.path.join(path, kernel_type)
            #
            # Get the kernels of type `type' from the `path`'/`type`
            # directory.
            #
            kernels_with_path += [f for f in os.listdir(f'{kernel_path}/')
                                  if re.search(pattern, f)]
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
    # Remove the kernel if it is included in the excluded kernels list
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
            logging.warning('        No kernels found with pattern '
                            '{}'.format(pattern))
            return []
    else:
        #
        # Return all the kernels with a given date
        #
        previous_kernel = ''
        kernels_date = []
        for kernel in kernels:
            if previous_kernel \
                    and re.split('_V[0-9]*', previous_kernel.upper())[0] == \
                    re.split('_V[0-9]*', kernel.upper())[0]:
                kernels_date.remove(previous_kernel)

            previous_kernel = kernel
            kernels_date.append(kernel)

        return kernels_date


def check_consecutive(l):
    """
    Check if a list of names with enumeration include all the elements
    in such a way that the enumeartion contains all expected numbers.

    :param l: List of names that include an enumeration
    :return: Check if the list has a complete enumeration
    :rtype: Bool
    """
    return sorted(l) == list(range(1, max(l) + 1))


def compare_files(fromfile, tofile, dir, display):
    """
    Compares two files and provides the logic to determine whether if the
    comparison should be added to the log or to an individual file with the
    comparison. The default name of the possible resuling file is:

    diff_`fromfile'[extension removed]_`tofile'[extension_removed].html

    The format for the log output is ASCII and follows a simplified Unix
    diff format.

    The format for the file output is HTML and mocks a simplified Unix
    GUI diff tool such as tkdiff.

    :param fromfile: Path of first file to be compared
    :type fromfile: str
    :param tofile: Path of second file to be comapred
    :type tofile: str
    :param dir: Resulting diff diles destination directory
    :type dir: str
    :param display: Indication if the fie will only be written in log or
                    if a specific diff file will be generated
    :type display: str
    """
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    if display in ['all', 'log']:

        diff = difflib.Differ()
        diff_list = list(diff.compare(fromlines, tolines))
        for line in diff_list:
            if (line[0] == '+') or (line[0] == '-') or (line[0] == '?'):
                logging.info(line[:-1])

    if display in ['all', 'files']:
        diff = difflib.HtmlDiff().make_file(fromlines, tolines, fromfile,
                                            tofile, context=False,
                                            numlines=False)

        diff_html = open(dir + \
                         f"/diff_"
                         f"{fromfile.split(os.sep)[-1].replace('.', '_')}_"
                         f"{tofile.split(os.sep)[-1].replace('.', '_')}"
                         f".html","w")
        diff_html.writelines(diff)
        diff_html.close()

    return None


def match_patterns(name, name_w_pattern, patterns):
    '''
    Given a SPICE kernel name, a SPICE Kernel name with patterns, and the
    possible patterns, provide a dictionary with the patterns as keys and
    the patterns values as value after matching it between the SPICE Kernel
    name with patterns and without patterns.

    For example, given the following:
       name: insight_v01.tm
       name_w_pattern: insight_v$VERSION.tm

    The function will return:
        {VERSION: '01'}

    :param name: Name of the SPICE Kernel
    :param name_w_pattern: Name of the SPICE Kernel with patterns
    :param patterns: List of the possible patterns present in the
                     SPICE Kernel name with patterns
    :return: Dictionary providing the patterns and their value as defined
             by the SPICE kernel
    :rtype: dict
    '''
    #
    # This list will help us determine the order of the patterns in the file
    # name because later on the patterns need to be correlated with the
    # pattern values.
    #
    pattern_name_order = {}
    name_check = name_w_pattern

    for pattern in patterns:
        pattern_name_order[pattern['#text']] = \
            name_w_pattern.find(pattern['#text'])
        name_check = \
            name_check.replace('$' + pattern['#text'], '$' *
                               int(pattern['@length']))

    #
    # Convert the pattern_name_order_dictionary into an ordered lis
    #
    pattern_name_order = list(
        {k: v for k, v in sorted(pattern_name_order.items(),
                                 key=lambda item: item[1])}.keys())

    #
    # Generate a list of values extracted from the comparison of the
    # original file and the file with patterns.
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
            error_message(f'Missmatch of values in meta-kernel pattern')

    #
    # Correlate the values with their position in the file name with
    # patterns.
    #
    values = {}
    for i in range(len(values_list)):
        values[pattern_name_order[i]] = values_list[i]

    return values

def utf8len(s):
    '''
    Length of a string in bytes

    :param s: string
    :type s: str
    :return: lentht of string in bytes
    :rtype: int
    '''
    return len(s.encode('utf-8'))

def kernel_name(path):
    '''
    List sorting function.
    :param path: 
    :return: 
    '''
    return path.split(os.sep)[-1]

def checksum_from_label(path):
    '''
    Extract checksum from a label rather tan calculating it.
    :param path: 
    :return: 
    '''
    
    checksum = ''
    product_label = path.split('.')[0] + '.xml'
    if os.path.exists(product_label):
        with open(product_label, 'r') as l:
            for line in l:
                if '<md5_checksum>' in line:
                    checksum = line.split('<md5_checksum>')[-1]
                    checksum = checksum.split('</md5_check')[0]
                    logging.warning(f'-- Checksum obtained from existing label:'
                                 f' {product_label.split(os.sep)[-1]}')
                    break
                    
    return checksum
                    