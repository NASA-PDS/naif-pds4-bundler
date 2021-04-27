#!/usr/bin/env python3
#
#   NAIF PDS4 Bundle Generator (naif-pds4-bundle)
#
#   --------------------------------------------------------------------------
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
#   --------------------------------------------------------------------------
"""
The PDS4 Bundle Generator (naif-pds4-bundle) is a a pipeline that
generates a SPICE archive in the shape of a PDS4 Bundle or a PDS3
data set.

The pipeline is constructed by the orchestration of a family of
classes that can also be used independently.

In order to facilitate its usage the pipeline can be run in an
interactive mode that will allow the operator to check the
validity and/or correctness of each step of the process.


Using naif-pds4-bundle
----------------------
::

usage: naif-pds4-bundle [-h] [-l] [-i] CONFIG [CONFIG ...] CONFIG [CONFIG ...]

naif-pds4-bundle-0.1.0, PDS4/PDS4 SPICE archive generation pipeline

  naif-pds4-bundle is a command-line utility program that generates PDS4
  Bundles and PDS3 Data Sets for SPICE kernel data sets.

positional arguments:
  CONFIG             Mission specific configuration file
  CONFIG             Release specific plan file

optional arguments:
  -h, --help         show this help message and exit
  -l, --log          Prompt log during execution
  -i, --interactive  Activate interactive execution

"""
import re

from textwrap import dedent

from os.path import dirname
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .classes.setup      import Setup
from .classes.log        import Log
from .classes.list       import KernelList
from .classes.bundle     import Bundle
from .classes.collection import SpiceKernelsCollection
from .classes.product    import SpiceKernelProduct
from .classes.product    import MetaKernelProduct
from .classes.product    import InventoryProduct
from .classes.collection import DocumentCollection
from .classes.product    import SpicedsProduct
from .classes.product    import Object


def main(config = False, plan   = False, faucet  = '',
         log    = False, silent = False, verbose  = False,
         diff   = '',    interactive  = False ):
    """
    Main routine for the NAIF PDS4 Bundle Generator (naif-pds4-bundle).

    This routine gets the command line arguments and executes the archive
    generation pipeline. This execution can be interactive or not.
    """

    with open(dirname(__file__) + '/../version',
              'r') as f:
        for line in f:
            version = line

    if not config and not plan:

        header  = dedent(
        f'''\
    
         naif-pds4-bundle-{version}, NAIF PDS4/PDS3 SPICE archive generation pipeline 
    
           naif-pds4-bundle is a command-line utility program that generates PDS4 
           Bundles and PDS3 data sets for SPICE kernels.
        ''')

        #
        # Build the argument parser.
        #
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                description=header)
        parser.add_argument('config', metavar='CONFIG', type=str, nargs='+',
                            help='Mission specific configuration file')
        parser.add_argument('-p', '--plan',
                            action='store', type=str,
                            help='Files planned to be included in the increment. If this argument is not provided, '
                                 'all the kernels found in the kernels directory specified in the configuration file '
                                 'in addition to new meta-kernels will be included in the increment.')
        parser.add_argument('-d', '--diff',
                            default= '',
                            action='store', type = str,
                            help='Optional generation of diff reports for '
                                 'products. Allowed values are: "all", '
                                 '"log" or "files".')
        parser.add_argument('-f', '--faucet',
                            default= '',
                            action='store', type = str,
                            help='Optional end point of the pipeline. '
                                 'Allowed values are: "list", "staging" or '
                                 '"final"')
        parser.add_argument('-l', '--log',
                            help='Write log in file',
                            action='store_true')
        parser.add_argument('-s', '--silent',
                            help='Log will not be prompted on the terminal during execution.',
                            action='store_true')
        parser.add_argument('-v', '--verbose',
                            help='Full log will be prompted on the terminal during execution. If argumet is set to True, silent argument is omitted.',
                            action='store_true')
        parser.add_argument('-i', '--interactive',
                            help='Activate interactive execution. If chosen, verbose argument will be set to True.',
                            action='store_true')


        args         = parser.parse_args()
        args.config  = args.config[0]

    else:

        args              = Object()
        args.config       = config
        args.plan         = plan
        args.faucet       = faucet
        args.log          = log
        args.silent       = silent
        args.verbose      = verbose
        args.diff         = diff
        args.interactive  = interactive

    #
    # Turn lowercase or uppercase arguments that need it.
    #
    args.faucet = args.faucet.lower()
    args.diff   = args.diff.lower()

    #
    # Force verbosity if interactive argument is set to true.
    #
    if args.interactive:
        args.verbose = True
        args.silent  = False

    #
    # Set silent to False if verbose is set to true.
    #
    if args.verbose:
        args.silent = False

    #
    # Check if string optional parameters are correct.
    #
    if args.diff not in ['all', 'log', 'files', '']:
        raise  Exception('-d, --diff argument has incorrect value.')
    if args.faucet not in ['list', 'staging', 'final', '']:
        raise  Exception('-f, --faucet argument has incorrect value.')


    #
    # -- Generate setup object
    #
    #    * This object will be used by all the other objects
    #    * Parse JSON into an object with attributes corresponding
    #      to dict keys.
    #
    setup = Setup(args, version)

    #
    # -- Setup the logging
    #
    #    * The log will always be displayed on screen unless the silent
    #      option is chosen.
    #    * The log file will be written in the working directory
    #
    log = Log(setup, args)

    #
    #  -- Start the pipeline
    #
    log.start()

    #
    # -- Check the existence of a previous release
    #
    setup.set_release()

    #
    # -- Generate the kernel list object
    #
    #    * The kernel list object will generate the kernel list
    #      non-archivable product.
    #
    list = KernelList(setup, args.plan)

    #
    #    * Escape if the sole purpose of the execution is to generate
    #      the kernel list.
    #
    if setup.faucet == 'list':
        log.stop()
        return

    #
    # -- Generate the bundle or data set structure.
    #
    bundle = Bundle(setup)


    #
    # -- Load LSK, FK and SCLK kernels for coverage computations
    #
    setup.load_kernels()


    #
    # -- Initialise the SPICE kernels collection.
    #
    spice_kernels_collection = SpiceKernelsCollection(setup, bundle, list)

    #
    # -- Populate the SPICE kernels collection from the kernels in
    #    the Kernel list
    #
    for kernel in list.kernel_list:
        if not '.tm' in kernel:
            #
            # * Each label is validated after generation.
            #
            spice_kernels_collection.add(
            SpiceKernelProduct(setup, kernel, spice_kernels_collection))

    #
    # -- Generate the meta-kernel(s).
    #
    MetaKernelProduct.log(setup)
    for kernel in list.kernel_list:
        if '.tm' in kernel:
             meta_kernel = MetaKernelProduct(setup, kernel, spice_kernels_collection)
             spice_kernels_collection.add(meta_kernel)

    #
    # -- Validate the SPICE Kernels collection:
    #
    #    * Note the validation of products is performed after writing the
    #      product itself and therefore it is not explicitely executed
    #      from the main function.
    #
    #    * Check that there is a XML label for each file under spice_kernels.
    #      That is, we are validating the spice_kernel_collection.
    #
    spice_kernels_collection.validate()

    #
    # -- Generate the SPICE kernels collection inventory product.
    #
    spice_kernels_collection_inventory = InventoryProduct(setup, spice_kernels_collection)

    #
    # -- Generate the document collection
    #
    document_collection = DocumentCollection(setup, bundle)

    #
    # -- Generation of SPICEDS document
    #
    if setup.pds_version == '4':

        spiceds = SpicedsProduct(setup, document_collection)

        #
        # -- If the SPICEDS document is generated then the document
        #    collection needs to be updated.
        #
        if spiceds.generated:
            document_collection.add(spiceds)

            #
            # -- Generate the documents inventory.
            #
            document_collection_inventory = InventoryProduct(setup, document_collection)

        #
        # -- Add Collections to the Bundle
        #
        bundle.add(spice_kernels_collection)
        if spiceds.generated:
            bundle.add(document_collection)

        #
        # -- Generate bundle label and if necessary readme file.
        #
        bundle.write_readme()

    elif setup.pds_version == '3':
        pass

    #
    # -- List the files present in the stagging area
    #
    bundle.files_in_staging()


    #
    # -- Stop the pipeline if you do not want to move the files from the
    #    staging area. Note that the complete list and the index file
    #    will not be generated.
    #
    if setup.faucet == 'staging':
        log.stop()
        return

    #TODO: Armonise the process with the PDS3 archvie generation.

    #
    # -- Generate index files, this includes generating the complete
    #    kernel list.
    #
    # OnlyFor PDS3
    #list.write_complete_list()
    #spice_kernels_collection_inventory.write_index()

    #
    # -- Copy files to final area.
    #
    bundle.copy_to_final()

    #
    # -- Stop the pipeline if you do not want to write checksums and
    #    validate the bundle.
    #
    if setup.faucet == 'final':
        log.stop()
        return

    #
    # -- Generate checksum file at final area.
    #
    bundle.write_checksum()

    #
    # -- Make sure directory and file permissions are correct.
    #

    #
    # -- Validate meta-kernel
    #
    if meta_kernel:
        meta_kernel.validate()

    log.stop()
    return


if __name__ == '__main__':
    main()