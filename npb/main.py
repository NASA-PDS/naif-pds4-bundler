#
#   NAIF PDS4 Bundle Generator (naif-pds4-bundle)
#
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
The PDS4 Bundle Generator (naif-pds4-bundle) is a a pipeline that
generates a SPICE archive in the shape of a PDS4 Bundle or a PDS3
data set.

The pipeline is constructed by the orchestration of a family of
classes that can also be used independently.


Using naif-pds4-bundle
----------------------
::

usage: naif-pds4-bundle [-h] [-l] [-i] CONFIG [CONFIG ...]

naif-pds4-bundle-0.1.0, PDS4/PDS4 SPICE archive generation pipeline

  naif-pds4-bundle is a command-line utility program that generates PDS4
  Bundles and PDS3 Data Sets for SPICE kernel data sets.

positional arguments:
  CONFIG             Mission specific configuration file
  CONFIG             Release specific plan file

optional arguments:
  -h, --help         show this help message and exit
  -l, --log          Prompt log during execution

"""
from textwrap import dedent
from os.path import isdir
from os.path import dirname
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from .classes.setup import Setup
from .classes.log import Log
from .classes.list import KernelList
from .classes.bundle import Bundle
from .classes.collection import SpiceKernelsCollection
from .classes.product import SpiceKernelProduct
from .classes.product import OrbnumFileProduct
from .classes.product import MetaKernelProduct
from .classes.product import InventoryProduct
from .classes.collection import DocumentCollection
from .classes.collection import MiscellaneousCollection
from .classes.product import SpicedsProduct
from .classes.product import ChecksumProduct
from .classes.product import Object


def main(config=False, plan=False, faucet='', log=False, silent=False,
         verbose=False, diff='', debug=True):
    """
    Main routine for the NAIF PDS4 Bundle Generator (naif-pds4-bundle).
    This routine gets the command line arguments or the parameter
    arbuments and runs the archive generation pipeline.

    :param config: XML Configuration file
    :param plan: Release plan file listing the kernels to be archived.
                 If this argument is not provided, all the kernels found in
                 the kernels directory specified in the configuration file
                 in addition to new meta-kernels will be included in the
                 increment
    :type plan: str
    :param faucet: Optional indication for end point of the pipeline.
                   Allowed values are: `list', `staging', or `final'
    :type faucet: str
    :param log: Write log in file
    :type log: bool
    :param silent: Log will not be prompted on the terminal during execution
    :type silent: bool
    :param verbose: Full log will be prompted on the terminal  during
                    execution. If argument is set to True, silent argument
                    is omitted
    :type verbose: bool
    :param diff: Optional generation of diff reports for products. Allowed
                 values are: `all', `log', or `files'
    :type diff: str
    :param debug: Indicate whether if the pipeline is running in debug mode
    :type debug: bool
    """
    #
    # Load the naif-pds4-bundle version as provided by the version file.
    #
    with open(dirname(__file__) + '/../version',
              'r') as f:
        for line in f:
            version = line

    #
    # Determine whether if the pipeline is being executed directly from
    # the command line of called by another Python function. If this is
    # not the case, then the arguments are taken from the command line.
    #
    if not config and not plan:

        header = dedent(
            f'''\
    
    naif-pds4-bundle-{version}, NAIF PDS4 SPICE archive generation pipeline 
    
      naif-pds4-bundle is a command-line utility program that generates PDS4 
      Bundles and PDS3 data sets for SPICE kernels.
        ''')

        #
        # Build the argument parser.
        #
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                description=header)
        parser.add_argument('config', metavar='CONFIG', type=str, nargs='+',
                            help='XML Configuration file')
        parser.add_argument('-p', '--plan',
                            action='store', type=str,
                            help="Release plan file listing the kernels to "
                                 "be archived. If this argument is not "
                                 "provided, all the kernels found in the "
                                 "kernels directory specified in the "
                                 "configuration file in addition to new "
                                 "meta-kernels will be included in the "
                                 "increment.")
        parser.add_argument('-f', '--faucet',
                            default='',
                            action='store', type=str,
                            help="Optional indication for end point of the "
                                 "pipeline. Allowed values are: `list', "
                                 "`staging', or `final'.")
        parser.add_argument('-l', '--log',
                            help='Write log in file',
                            action='store_true')
        parser.add_argument('-s', '--silent',
                            help="Log will not be prompted on the terminal "
                                 "during execution.",
                            action='store_true')
        parser.add_argument('-v', '--verbose',
                            help="Full log will be prompted on the terminal "
                                 "during execution. If argument is set to "
                                 "True, silent argument is omitted.",
                            action='store_true')
        parser.add_argument('-d', '--diff',
                            default='',
                            action='store', type=str,
                            help="Optional generation of diff reports for "
                                 "products. Allowed values are: `all', "
                                 "`log', or `files'.")

        #
        # Store the arguments in the args object.
        #
        args = parser.parse_args()
        args.config = args.config[0]
        
        #
        # When executing from the command line, debug mode is not available.
        #
        args.debug = False

    #
    # If NPB is not executed from the command line then an args object is
    # initialised and the argument attributes are obtained from the
    # main function argument list.
    #
    else:
        args = Object()
        args.config = config
        args.plan = plan
        args.faucet = faucet
        args.log = log
        args.silent = silent
        args.verbose = verbose
        args.diff = diff
        args.debug = debug

    #
    # Turn lowercase or uppercase arguments that need it.
    #
    args.faucet = args.faucet.lower()
    args.diff = args.diff.lower()

    #
    # Set silent to False if verbose is set to True.
    #
    if args.verbose:
        args.silent = False

    #
    # Check if string optional parameters are correct.
    #
    if args.diff not in ['all', 'log', 'files', '']:
        raise Exception('-d, --diff argument has incorrect value.')
    if args.faucet not in ['list', 'staging', 'final', '']:
        raise Exception('-f, --faucet argument has incorrect value.')

    #
    # The pipeline is executed now
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
    # With the log started we check the current configuration
    #
    setup.check_configuration()

    #
    # -- Check the existence of a previous release
    #
    setup.set_release()

    #
    # -- Generate the kernel list object
    #
    #    * The kernel list object will generate the kernel list
    #      non-archival product.
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
    # -- Generate the PDS4 bundle or PDS3 data set structure.
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
    # -- Initialise the miscellaneous collection
    #
    miscellaneous_collection = MiscellaneousCollection(setup, bundle ,list)

    #
    # -- Populate the SPICE kernels collection from the kernels in
    #    the Kernel list
    #
    for kernel in list.kernel_list:
        #
        # * Each label is validated after generation.
        #
        if ('.nrb' in kernel.lower()) or  ('.orb' in kernel.lower()):
            #
            # The OrbnumFileProduct has to be provided the kernels collection
            # because it might require to update the kernel list if the
            # orbnum file name is updated.
            #
            miscellaneous_collection.add(
                OrbnumFileProduct(setup, kernel, miscellaneous_collection,
                                  spice_kernels_collection))
        elif not '.tm' in kernel.lower():
            spice_kernels_collection.add(
                SpiceKernelProduct(setup, kernel, spice_kernels_collection))

    #
    # -- Generate the meta-kernel(s).
    #
    (meta_kernels, user_input) = \
        spice_kernels_collection.determine_meta_kernels()
    if meta_kernels:
        for mk in meta_kernels:
            meta_kernel = MetaKernelProduct(setup, mk, spice_kernels_collection,
                                            user_input=user_input)
            spice_kernels_collection.add(meta_kernel)

    #
    # -- Set the increment times
    #
    spice_kernels_collection.set_increment_times()
    spice_kernels_collection.set_collection_vid()
    
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
    # -- Generate the SPICE kernels collection inventory product (if the
    #    collection has been updated.)
    #
    if spice_kernels_collection.updated:
        
        spice_kernels_collection.set_collection_vid()
        spice_kernels_collection_inventory = InventoryProduct(setup,
                                             spice_kernels_collection)
        spice_kernels_collection.add(spice_kernels_collection_inventory)

    #
    # -- Generate the document collection
    #
    document_collection = DocumentCollection(setup, bundle)
    document_collection.set_collection_vid()

    #
    # -- Generation of spiceds document
    #
    if setup.pds_version == '4':

        spiceds = SpicedsProduct(setup, document_collection)

        #
        # -- If the spiceds document is generated then the document
        #    collection needs to be updated.
        #
        if spiceds.generated:
            document_collection.add(spiceds)
    
            #
            # -- Generate the documents inventory.
            #
            document_collection.set_collection_vid()
            document_collection_inventory = InventoryProduct(setup,
                                                document_collection)
            document_collection.add(document_collection_inventory)

        #
        # Add spice_kernel Collection to the Bundle. 
        # Note that the collections are provided in a given order.
        #
        bundle.add(spice_kernels_collection)

        #
        # -- Generate the miscellaneous collection. The checksum product
        #    is initialised in such a way that its name can be obtained.
        #
        # -- The first thing that is checked is whether if the current
        #    Bundle has checksums, if so, all the checksums are generated, 
        #    including the corresponding miscellaneous collection inventories 
        #    and labels.
        #
        if setup.increment:
            checksum_dir = setup.final_directory + \
                       f'/{setup.mission_acronym}_spice/miscellaneous/checksum'
            if not isdir(checksum_dir):
                for release in bundle.history.items():
                    release_checksum = ChecksumProduct(setup, 
                                                   miscellaneous_collection)
                    release_checksum.generate(history=release)

                    #
                    # Initialise a miscellaneous collection for this previous
                    # release
                    #
                    release_miscellaneous_collection = \
                        MiscellaneousCollection(setup, bundle, list)
                    
                    #
                    # Add the checksum at the release miscellaneous collection
                    # to generate the adequate inventory file and add it to 
                    # the current miscellaneous collection for it to be 
                    # present at the checksum.
                    #
                    release_miscellaneous_collection.add(release_checksum)
                    
                    miscellaneous_collection.add(release_checksum)

                    release_miscellaneous_collection.set_collection_vid()
                    release_miscellaneous_collection_inventory = \
                        InventoryProduct(setup, 
                                         release_miscellaneous_collection)
                    
                    release_miscellaneous_collection.add(
                        release_miscellaneous_collection_inventory)
                    miscellaneous_collection.add(
                        release_miscellaneous_collection_inventory)

                    #
                    # Add release miscellaneous collection
                    #
                    bundle.add(release_miscellaneous_collection)
                    
                    
            #
            # set miscellaneous collection VID.
            #
            miscellaneous_collection.set_collection_vid()

        #
        # Add miscellaneous collection and document collection
        #
        bundle.add(miscellaneous_collection)
        bundle.add(document_collection)

        
        #
        # From here on now, the checksum and the miscellaneous collection 
        # for the current release are generated.
        #
        # The miscellaneous collection is the one to be guaranteed to be
        # updated.
        #
        checksum = ChecksumProduct(setup, miscellaneous_collection)

        #
        # Before adding the checksum to the current collection
        # we need to specify that is not a new product.
        #
        for product in miscellaneous_collection.product:
            if type(product) == ChecksumProduct:
                product.new_product = False
        
        miscellaneous_collection.add(checksum)
        miscellaneous_collection.set_collection_vid()

        miscellaneous_collection_inventory = InventoryProduct(setup,
                                                miscellaneous_collection)
        miscellaneous_collection.add(miscellaneous_collection_inventory)
    


        #
        # -- Generate bundle label and if necessary readme file.
        #
        bundle.write_readme()

        #
        # -- Generate the checksum product a posteriori in such a way
        #    that the miscellaneous collection inventory includes the
        #    chekcsum and the checksum includes the md5 hash of the
        #    miscellaneous collection inventory.
        #
        checksum.generate()
        miscellaneous_collection.add(checksum)

    elif setup.pds_version == '3':
        pass

    #
    # -- List the files present in the staging area
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

    #
    # -- Generate index files, this includes generating the complete
    #    kernel list.
    #
    # OnlyFor PDS3
    # list.write_complete_list()
    # spice_kernels_collection_inventory.write_index()

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
    # -- Make sure directory and file permissions are correct.
    #

    #
    # -- Validate meta-kernel(s)
    #
    for kernel in spice_kernels_collection.product:
        if type(kernel) == MetaKernelProduct:
            kernel.validate()

    #
    # -- Validate checksum files against the updated bundle history.
    #
    bundle.validate_history()
    
    log.stop()

    return None


if __name__ == '__main__':
    main()
