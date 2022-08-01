"""File and Text Management Functions to support NPB Classes."""
import difflib
import errno
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import stat
from collections import defaultdict

import spiceypy

from ..classes.log import error_message


def etree_to_dict(etree):
    """Convert between XML and JSON.

    The following XML-to-Python-dict snippet parses entities as well as
    attributes following this XML-to-JSON "specification". It is the most
    general solution handling all cases of XML.

    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html

    :param etree: Element Tree read from XML file
    :type etree: dict
    :return: XML File converted into a JSON file
    :rtype: dict
    """
    jtree = {etree.tag: {} if etree.attrib else None}
    children = list(etree)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        jtree = {etree.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if etree.attrib:
        jtree[etree.tag].update(("@" + k, v) for k, v in etree.attrib.items())
    if etree.text:
        text = etree.text.strip()
        if children or etree.attrib:
            if text:
                jtree[etree.tag]["#text"] = text
        else:
            jtree[etree.tag] = text

    return jtree


def md5(fname):
    """Returns the MD5 sum (checksum) of the provided file.

    :param fname: Filename
    :type fname: str
    :return: Checksum value of the file
    :rtype: str
    """
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def copy(src, dest):
    """Creates a directory and raises an error if the directory exists.

    :param src: Source directory with path.
    :type src: str
    :param dest: Destination directory with path.
    :type dest: str
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
            logging.warning(
                f"-- Directory {src.split(os.sep)[-1]} not "
                f"copied, probably because the increment "
                "directory exists.\n Error: %s" % e
            )


def safe_make_directory(dir):
    """Creates a directory if not present.

    :param dir: Directory path.
    :type dir: str
    """
    try:
        os.mkdir(dir)
        logging.info(f"-- Generated directory: {dir}  ")
        logging.info("")
    except BaseException:
        pass


def extension_to_type(kernel):
    """Given a SPICE kernel provide the SPICE kernel type.

    :param kernel: SPICE Kernel name
    :type kernel: str
    :return: SPICE Kernel type of the input SPICE kernel name
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
        "NRB": "ORB",
    }

    try:
        #
        # Kernel is an object
        #
        kernel_type = kernel_type_map[kernel.extension.upper()].lower()
    except BaseException:
        #
        # Kernel is a string
        #
        kernel_type = kernel_type_map[kernel.split(".")[-1].upper()].lower()

    return kernel_type


def type_to_pds3_type(kernel):
    """Given a SPICE kernel provide the PDS3 SPICE kernel type.

    :param kernel: SPICE Kernel name
    :type kernel: str
    :return: PDS3 SPICE Kernel type of the input SPICE kernel name
    :rtype: str
    """
    kernel_type_map = {
        "IK": "INSTRUMENT",
        "FK": "FRAMES",
        "SCLK": "CLOCK_COEFFICIENTS",
        "LSK": "LEAPSECONDS",
        "PCK": "TARGET_CONSTANTS",
        "CK": "POINTING",
        "SPK": "EPHEMERIS",
        "DSK": "SHAPE",
    }

    try:
        #
        # Kernel is an object
        #
        kernel_type = kernel_type_map[kernel.extension.upper()]
    except BaseException:
        #
        # Kernel is a string
        #
        kernel_type = kernel_type_map[kernel.split(".")[-1].upper()]

    return kernel_type


def type_to_extension(kernel_type):
    """Given a SPICE kernel type provide the SPICE kernel extension.

    :param kernel_type: SPICE kernel type
    :type kernel_type: str
    :return: SPICE Kernel extension
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
        "DSK": ["bds"],
    }

    kernel_extension = kernel_type_map[kernel_type]

    return kernel_extension


def add_carriage_return(line, eol, setup=False):
    """Adds Carriage Return (``<CR>``) to a line.

    :param line: Input line
    :type line: str
    :param eol: EOL defined by the configuration file
    :type eol: str
    :return: Input line with CR
    :rtype: str
    """
    if eol == "\r\n" and "\r\n" not in line:
        line = line.replace("\n", "\r\n")
    if eol == "\r\n" and "\r\n" not in line:
        if "\r\n" not in line:
            line += "\r\n"
        else:
            error_message(f"File has incorrect CR at line: {line}.", setup=setup)
    if eol == "\n" and "\r\n" in line:
        line = line.replace("\r\n", "\n")
    elif eol == "\n" and "\n" not in line:
        line += "\n"
    else:
        if "\n" not in line:
            error_message(f"File has incorrect CR at line: {line}.", setup=setup)

    return line


def add_crs_to_file(file, eol, setup=False):
    """Adds Carriage Return (``<CR>``) to a file.

    :param line: Input file
    :type line: str
    :param eol: End of Line character as indicated by the configuration file
    :type eol: str
    :raise: If CR cannot be added to the file
    """
    try:
        file_crs = file.split(".")[0] + "crs_tmp"
        with open(file, "r") as r:
            with open(file_crs, "w+") as f:
                for line in r:
                    line = add_carriage_return(line, eol, setup)
                    f.write(line)
        shutil.move(file_crs, file)

    except BaseException:
        error_message(f"Carriage return adding error for {file}.", setup)


def check_list_duplicates(list_of_elements):
    """Check if given list contains any duplicates.

    :param list_of_elements: List of SPICE kernel names
    :type list_of_elements: list
    :return: True if the input list contains
             duplicates, False otherwise
    :rtype: bool
    """
    for elem in list_of_elements:
        if list_of_elements.count(elem) > 1:
            return True

    return False


def fill_template(object, product_file, product_dictionary):
    """Fill a template with uppercase keywords preceded with ``$``.

    :param object: List object
    :type object: object
    :param product_file: Resulting file
    :type product_file: str
    :param product_dictionary: Dictionary of keys to replace
    :type product_dictionary: dict
    """
    with open(product_file, "w") as f:

        with open(object.template, "r") as t:
            for line in t:
                line = line.rstrip()
                for key, value in product_dictionary.items():
                    if isinstance(value, str) and key in line and "$" in line:
                        line = line.replace("$" + key, value)
                f.write(f"{line}\n")


def get_context_products(setup):
    """Obtain PDS4 Context Products.

    Obtain the context products from the PDS4 registered context products
    template or from the XML configuration file.

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
    registered_context_products_file = (
        f"{setup.root_dir}data/registered_context_products.json"
    )
    with open(registered_context_products_file, "r") as f:
        context_products = json.load(f)["Product_Context"]

    #
    # Overwrite the default context products with the ones provided in the
    # configuration file.
    #
    appended_products = []
    if hasattr(setup, "context_products"):
        if not isinstance(setup.context_products["product"], list):
            context_products_list = [setup.context_products["product"]]
        else:
            context_products_list = setup.context_products["product"]
        for product in context_products_list:
            if product:
                updated_product = False
                index = 0
                for registered_product in context_products:
                    if registered_product["name"][0] == product["@name"]:
                        updated_product = True
                        context_products[index]["type"] = [product["type"]]
                        context_products[index]["lidvid"] = product["lidvid"]
                    index += 1
                if not updated_product:
                    appended_products.append(
                        {
                            "name": [product["@name"]],
                            "type": [product["type"]],
                            "lidvid": product["lidvid"],
                        }
                    )

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
    if hasattr(setup, "secondary_observers"):
        for sc in setup.secondary_observers:
            config_context_products.append(sc)

    #
    # Check the secondary targets and if present add them to the
    # Configuration for context products.3
    #
    if hasattr(setup, "secondary_targets"):
        for tar in setup.secondary_targets:
            config_context_products.append(tar)

    for context_product in context_products:
        for config_product in config_context_products:
            #
            # For the conditional statement we need to put both names lower case.
            #
            if context_product["name"][0].lower() == config_product.lower():
                bundle_context_products.append(context_product)

    return bundle_context_products


def mk_to_list(mk, setup):
    """Generate a list of kernels from a Meta-kernel.

    This function assumes that the meta-kernel will contain a PATH_SYMBOLS
    definition that will be present in each kernel entry preceded by a dollar
    sign ``$``.

    If no kernel is found an error is raised.

    :param mk: Meta-kernel path from which the list of kernels is generated
    :type mk: str
    :param setup: NPB run Setup Object
    :type setup: object
    :return: List of kernels present in the meta-kernel
    :rtype: list
    """
    path_symbol = ""
    get_symbol = False
    ker_mk_list = []
    with open(mk, "r") as f:
        for line in f:
            if path_symbol:
                if path_symbol in line:
                    kernel = line.split("'")[1]
                    kernel = kernel.split(path_symbol)[1]
                    kernel = kernel.strip()
                    kernel = kernel.split("\n")[0]
                    kernel = kernel.split("\r")[0]
                    kernel = kernel.split("/")[-1]
                    if kernel:
                        ker_mk_list.append(kernel)

            if "PATH_SYMBOLS" in line.upper():
                get_symbol = True
            if get_symbol:
                try:
                    #
                    # General case, the value is in the same line. e.g.:
                    #
                    # PATH_SYMBOLS = ( 'KERNELS' )
                    #
                    # but also get the VCO particular case:
                    #
                    # PATH_SYMBOLS = (
                    # 'KERNELS'
                    # )
                    #
                    path_symbol = "$" + line.split("'")[1]
                    get_symbol = False
                except BaseException:
                    pass

    if not ker_mk_list:
        error_message(
            f"No kernels present in {mk}. " f"Please review MK generation.", setup=setup
        )

    return ker_mk_list


def get_latest_kernel(
    kernel_type, paths, pattern, dates=False, excluded_kernels=False, mks=False
):
    """Get the latest kernel given a type and a pattern.

    Returns the name of the latest SPICE kernel of a given type present
    in the path. This function is exclusively used find the latest version
    of the kernels to be included in a meta-kernel.

    :param kernel_type: SPICE Kernel type which also defines
                        the subdirectory name.
    :type kernel_type: str
    :param paths: List of paths to the roots of the SPICE Kernels directories
                  where the kernels are store in a subdirectory named "type".
    :type paths: str
    :param pattern: Patterns to search for that defines the kernel "type"
                    file naming scheme. This pattern follows the format of
                    the meta-kernel grammar provided in the XML configuration
                    file
    :type pattern: str
    :param dates: Indicates that the pattern of the kernel includes dates
                  and that the last version of each kernel with a date has
                  to be included. If this parameter is set to False then
                  only the latest date and latest version is included
    :type dates: bool
    :param excluded_kernels: Indicates that a specific kernel might have
                             to be excluded from the search.
    :type excluded_kernels: list
    :param mks: Indicates that the kernels present in the list of provided
          meta-kernels have to be included for consideration to obtain
          the latest version of the given kernel
    :type mks: list
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
            kernels_with_path += [
                f for f in os.listdir(f"{kernel_path}/") if re.search(pattern, f)
            ]
        except BaseException:
            pass

    if mks:
        for mk in mks:
            with open(mk, "r") as m:
                for line in m:
                    if re.findall(pattern, line):
                        kernels_with_path.append(line.strip())

    kernels_with_path = list(dict.fromkeys(kernels_with_path))

    for kernel in kernels_with_path:
        kernel = kernel.split("/")[-1].split("'")[0]
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
                if excluded_kernel.split("*")[0] in kernel:
                    kernels.remove(kernel)

    if not dates:
        #
        # Return the latest kernel
        #
        try:
            return kernels.pop()
        except BaseException:
            logging.warning(
                "        No kernels found with pattern " "{}".format(pattern)
            )
            return []
    else:
        #
        # Return all the kernels with a given date
        #
        previous_kernel = ""
        kernels_date = []
        for kernel in kernels:
            if (
                previous_kernel
                and re.split("_V[0-9]*", previous_kernel.upper())[0]
                == re.split("_V[0-9]*", kernel.upper())[0]
            ):
                kernels_date.remove(previous_kernel)

            previous_kernel = kernel
            kernels_date.append(kernel)

        return kernels_date


def check_consecutive(lst):
    """Check if a list has consecutive numbers.

    Check if a list of names with enumeration include all the elements
    in such a way that the enumeration contains all expected numbers.

    :param lst: List of names that include an enumeration
    :type lst: list
    :return: Check if the list has a complete enumeration
    :rtype: bool
    """
    return sorted(lst) == list(range(1, max(lst) + 1))


def compare_files(fromfile, tofile, dir, display):
    """Compare two files.

    Compares two files and provides the logic to determine whether if the
    comparison should be added to the log or to an individual file with the
    comparison. The default name of the possible resulting file is::

       diff_`fromfile'[extension removed]_`tofile'[extension_removed].html

    The format for the log output is ASCII and follows a simplified Unix
    diff format.

    The format for the file output is HTML and mocks a simplified Unix
    GUI diff tool such as tkdiff.

    :param fromfile: Path of first file to be compared
    :type fromfile: str
    :param tofile: Path of second file to be compared
    :type tofile: str
    :param dir: Resulting diff files destination directory
    :type dir: str
    :param display: Indication if the fie will only be written in log or
                    if a specific diff file will be generated
    :type display: str
    :return: True if the files are different, False if they are the same.
    :rtype: bool
    """
    with open(fromfile) as ff:
        fromlines = ff.readlines()
    with open(tofile) as tf:
        tolines = tf.readlines()

    if fromlines == tolines:
        logging.info("-- The following files have the same content:")
        logging.info(f"   {fromfile}")
        logging.info(f"   {tofile}")
        if md5(fromfile) == md5(tofile):
            logging.info("   And have the same MD5Sum.")
            return False

    if display in ["all", "log"]:

        diff = difflib.Differ()
        diff_list = list(diff.compare(fromlines, tolines))
        for line in diff_list:
            if (line[0] == "+") or (line[0] == "-") or (line[0] == "?"):
                logging.info(line[:-1])

    if display in ["all", "files"]:
        diff = difflib.HtmlDiff().make_file(
            fromlines, tolines, fromfile, tofile, context=False, numlines=False
        )

        diff_html = open(
            dir + f"/diff_"
            f"{fromfile.split(os.sep)[-1].replace('.', '_')}_"
            f"{tofile.split(os.sep)[-1].replace('.', '_')}"
            f".html",
            "w",
        )
        diff_html.writelines(diff)
        diff_html.close()

    return True


def match_patterns(name, name_w_pattern, patterns):
    """March patterns to filename.

    Given a SPICE kernel name, a SPICE Kernel name with patterns, and the
    possible patterns, provide a dictionary with the patterns as keys and
    the patterns values as value after matching it between the SPICE Kernel
    name with patterns and without patterns.

    For example, given the following arguments:

         * name: ``insight_v01.tm``
         * name_w_pattern: ``insight_v$VERSION.tm``

    The function will return: ``{VERSION: '01'}``

    :param name: Name of the SPICE Kernel
    :type name: str
    :param name_w_pattern: Name of the SPICE Kernel with patterns
    :type name_w_pattern: str
    :param patterns: List of the possible patterns present in the
                     SPICE Kernel name with patterns
    :type patterns: list
    :return: Dictionary providing the patterns and their value as defined
             by the SPICE kernel
    :rtype: dict
    """
    #
    # This list will help us determine the order of the patterns in the file
    # name because later on the patterns need to be correlated with the
    # pattern values.
    #
    pattern_name_order = {}
    name_check = name_w_pattern

    for pattern in patterns:
        pattern_name_order[pattern["#text"]] = name_w_pattern.find(pattern["#text"])
        name_check = name_check.replace(
            "$" + pattern["#text"], "$" * int(pattern["@length"])
        )

    #
    # Convert the pattern_name_order_dictionary into an ordered lis
    #
    pattern_name_order = list(
        {
            k: v
            for k, v in sorted(pattern_name_order.items(), key=lambda item: item[1])
        }.keys()
    )

    #
    # Generate a list of values extracted from the comparison of the
    # original file and the file with patterns.
    #
    values_list = []
    value = ""
    value_bool = False

    for i in range(len(name_check)):
        if (name_check[i] == name[i]) and (not value_bool):
            continue
        if (name_check[i] == name[i]) and value_bool:
            value_bool = False
            values_list.append(value)
            value = ""
        elif (name_check[i] == "$") and (not value_bool):
            value_bool = True
            value += name[i]
        elif (name_check[i] == "$") and value_bool:
            value += name[i]
        else:
            raise

    #
    # Correlate the values with their position in the file name with
    # patterns.
    #
    values = {}
    for i in range(len(values_list)):
        values[pattern_name_order[i]] = values_list[i]

    return values


def utf8len(strn):
    """Length of a string in bytes.

    :param strn: string
    :type strn: str
    :return: length of string in bytes
    :rtype: int
    """
    return len(strn.encode("utf-8"))


def kernel_name(path):
    """List sorting function.

    :param path: path to be sorted
    :type path: str
    :return: sorting result
    :rtype: str
    """
    return path.split(os.sep)[-1]


def checksum_from_registry(path, working_directory):
    """Extract checksum from the checksum registry.

    All the checksum registries will be checked.

    :param path: Product path
    :type path: str
    :param working_directory: checksum registry path
    :type working_directory: str
    :return: MD5 Sum for the file indicated by path
    :rtype: str
    """
    checksum = ""
    checksum_registries = glob.glob(f"{working_directory}/*.checksum")
    checksum_found = False

    for checksum_registry in checksum_registries:
        if not checksum_found:
            with open(checksum_registry, "r") as lbl:
                for line in lbl:
                    if path in line:
                        checksum = line.split()[-1]
                        logging.warning(
                            f"-- Checksum obtained from Checksum "
                            f"Registry file: {checksum_registry}"
                        )
                        checksum_found = True
                        break

    return checksum


def checksum_from_label(path):
    """Extract checksum from a label rather than calculating it.

    :param path: Product path
    :type path: str
    :return: MD5 Sum for the file indicated by path
    :rtype: str
    """
    checksum = ""
    product_label = path.split(".")[0] + ".xml"
    if os.path.exists(product_label):
        with open(product_label, "r") as lbl:
            for line in lbl:
                if "<md5_checksum>" in line:
                    checksum = line.split("<md5_checksum>")[-1]
                    checksum = checksum.split("</md5_check")[0]
                    logging.warning(
                        f"-- Checksum obtained from existing label:"
                        f" {product_label.split(os.sep)[-1]}"
                    )
                    break

    return checksum


def extract_comment(path, handle=False):
    """Extract comment from SPICE DAF file.

    :param path: Path of SPICE kernel
    :type path: str
    :return: SPICE kernel comment
    :rtype: list
    """
    if not handle:
        close_file = True
        handle = spiceypy.dafopr(path)
    else:
        close_file = False

    linlen = 1001
    buffsz = 100000

    (lincmt, commnt, done) = spiceypy.dafec(handle, buffsz, linlen)
    if lincmt > buffsz:
        spiceypy.dafcls(handle)
        error_message(f"Comment from {path} is longer than buffer size.")

    #
    # Remove empty lines at the end of the comment.
    #
    lines_to_remove = 0
    for line in reversed(commnt):
        if not line.strip():
            lines_to_remove += 1
        if line.strip():
            break
    if lines_to_remove > 0:
        lines_to_remove *= -1
        commnt = commnt[: lines_to_remove + 1]

    if close_file:
        spiceypy.dafcls(handle)

    return commnt


def string_in_file(file, str_to_check, repetitions=1):
    """Check if a string is present in a file.

    You can also provide the number of times that string is repeated.

    :param file: File where the string is searched
    :type file: str
    :param str_to_check: String to search
    :type str_to_check: str
    :param repetitions: Number of repetitions, default is 1
    :type repetitions: int
    :return: True if the string is present in the file, False otherwise
    :rtype: bool
    """
    lines_with_string = 0
    with open(file, "r") as r:
        for line in r:
            if str_to_check in line:
                lines_with_string += 1

    if lines_with_string != repetitions:
        return False

    return True


def replace_string_in_file(file, old_string, new_string, setup):
    """Replace string in a file.

    :param file: File to replace the string from
    :type file: str
    :param old_string: String present in file to be substituted
    :type old_string: str
    :param new_string: String to be replaced
    :type new_string: str
    :param setup: NPB run Setup Object
    :type setup: object
    """
    reading_file = open(file, "r")

    new_file_content = ""
    for line in reading_file:
        new_line = line.replace(old_string, new_string)
        new_file_content += add_carriage_return(new_line, setup.eol_pds3, setup)
    reading_file.close()

    writing_file = open("temp.file", "w")
    writing_file.write(new_file_content)
    writing_file.close()

    shutil.move("temp.file", file)


def format_multiple_values(value):
    """Reformat multi-line key value for PDS3 labels.

    For example if the ``MAKLABEL`` key value has multiple entries, it needs to
    be reformatted.

    :param value: PDS3 key value
    :type value: str
    :return: PDS3 key value reformatted
    :rtype: str
    """
    if "," in value:
        values = value.split(",")
        value = "{\n"
        for val in values:
            value += f"{' ' * 31}{val},\n"
        value = value[:-2] + "\n" + " " * 31 + "}\n"

    return value


def product_mapping(name, setup, cleanup=True):
    """Obtain the kernel mapping.

    :return: Kernel Mapping
    :rtype: str
    """
    kernel_list_file = (
        setup.working_directory + os.sep + f"{setup.mission_acronym}_{setup.run_type}_"
        f"{int(setup.release):02d}.kernel_list"
    )

    get_map = False
    mapping = False

    with open(kernel_list_file, "r") as lst:
        for line in lst:
            if name in line:
                get_map = True
            if get_map and "MAPPING" in line:
                mapping = line.split("=")[-1].strip()
                get_map = False

    if not cleanup:
        setup = False
    #
    # If cleanup is not being performed this is an indication that if the kernel
    # mapping does not exist, this can be intentional and therefore an error
    # does not have to be reported.
    #
    if not mapping and cleanup:
        error_message(
            f"{name} does not have mapping on {kernel_list_file}.",
            setup=setup,
        )

    return mapping


def check_kernel_integrity(path):
    """Check if the SPICE Kernel has the adequate architecture.

    All SPICE kernels must have a NAIF file ID word as the first "word" on
    the first line of the kernel. This "word" describes the architecture
    of the kernel.

    A binary kernel could have the following architectures:

      * ``DAF``: The file is based on the DAF architecture.
      * ``DAS``: The file is based on the DAS architecture.
      * ``XFR``: The file is in a SPICE transfer file format.

    For an archive only ``DAF`` is acceptable.

    Text kernels must have ``KPL`` (Kernel Pool File) architecture.

    NPB checks if binary kernels have a ``DAF`` architecture and text kernels
    a ``KPL`` architecture.

    :param path: SPICE Kernel or ORBNUM path
    :type path: str
    :return: Error message if error present
    :rtype: str
    """
    error = ""
    name = path.split(os.sep)[-1].strip()
    extension = path.split(".")[-1].strip()
    type_file = extension_to_type(name).upper()

    #
    # Determine if it is a binary or a text kernel.
    #
    if extension[0].lower() == "b":
        file_format = "Binary"
    else:
        file_format = "Character"

    #
    # All files that are to have labels generated must have a NAIF
    # file ID word as the first "word" on the first line of the
    # file. Check if it is the case.
    #
    (arch, type) = spiceypy.getfat(path)

    if file_format == "Binary":

        #
        # A binary file could have the following architectures:
        #
        #   DAF - The file is based on the DAF architecture.
        #   DAS - The file is based on the DAS architecture.
        #   XFR - The file is in a SPICE transfer file format.
        #
        # But for an archive only DAF is acceptable.
        #
        if (arch != "DAF") and (arch != "DAS"):
            error = f"Kernel {name} architecture {arch} is invalid."
        else:
            pass

    elif file_format == "Character":

        #
        # Text kernels must have KPL architecture:
        #
        #    KPL -- Kernel Pool File (i.e., a text kernel)
        #
        if arch != "KPL":
            error = f"Kernel {name} architecture {arch} is invalid."

    if type != type_file:
        error = f"Kernel {name} type {type_file} is not the one expected: {type}."

    return error


def check_binary_endianness(path):
    """Check if the SPICE Kernel has the adequate architecture.

    PDS4 Bundles require LTL-IEEE binary kernels and PDS3 data sets require
    BIG-IEEE binary kernels. This behavior can be changed via configuration.

    This method ensures that the endianness of binary kernels is the
    appropriate one according to the configuration.

    :param path: Binary SPICE kernel path
    :type path: str
    :return: Error message if error present
    :rtype: list
    """
    error = ""

    if path.split(".")[-1].lower() == "bds":
        arch = "das"
    else:
        arch = "daf"
    try:
        if arch == "daf":
            handle = spiceypy.dafopw(path)
            spiceypy.dafcls(handle)
        elif arch == "das":
            handle = spiceypy.dasopw(path)
            spiceypy.dascls(handle)
        else:
            error = "The binary kernel does not have the a DAF or DAS architecture."

    except BaseException:
        error = "The kernel cannot be loaded because of its endianness. Use NAIF's utility BINGO to convert the file."

    return error


def check_badchar(file):
    """Check NON-ASCII characters for a file.

    :param file: Path to file to check
    :return: Resulting error messages
    :rtype: list
    """
    error = []
    line_num = 1
    with open(file, "r") as f:
        for line in f:
            if not line.isascii():
                char_count = 0
                badchars = []
                for char in line:
                    if not char.isascii():
                        badchars.append(char_count)
                    char_count += 1

                error.append(f"NON-ASCII character(s) in line {line_num}:")
                error.append(f"{line.rstrip()}")
                badchar_line = " " * len(line.rstrip())
                for badchar in badchars:
                    badchar_line = (
                        badchar_line[:badchar] + "^" + badchar_line[badchar + 1 :]
                    )
                error.append(badchar_line)
            line_num += 1

    return error


def check_eol(file, eol):
    """Check file EOL.

    :param file: Path to file to check
    :param eol: Expected End of Line
    :return: Resulting error messages
    :rtype: str
    """
    error = ""

    with open(file, "rb") as open_file:
        content = open_file.read()

    if eol == "\n":
        if b"\r\n" in content:
            error = "Incorrect EOL in file, LF (\\n) expected."
    elif eol == "\r\n":
        if content.count(b"\r\n") != content.count(b"\n"):
            error = "Incorrect EOL in file, CRLF (\\r\\n) expected."
    else:
        error_message(f"Incorrect EOL in configuration: {eol}")

    return error


def check_line_length(file):
    """Check SPICE text kernel line length.

    :param file: Path to file to check
    :return: Resulting error messages
    :rtype: str
    """
    error = []
    line_num = 1
    with open(file, "r") as f:
        for line in f:
            if len(line) > 80:
                error.append(f"Line {line_num} is longer than 80 characters")
            line_num += 1

    return error


def check_permissions(path):
    """Check if the file has read permissions.

    This method ensures that the file has the adequate file permissions.

    :param path: file path
    :type path: str
    :return: Error message if error present
    :rtype: none
    """

    #
    # This provides the usual chmod style file permissions.
    #
    permissions = oct(os.stat(path)[stat.ST_MODE])[-3:]

    #
    # The first two digits must be at least 4.
    #
    if int(permissions[0]) < 4 or int(permissions[1]) < 4:
        error_message(
            f"File {path} is not readable by the account that runs NPB. "
            f"Update permissions."
        )
