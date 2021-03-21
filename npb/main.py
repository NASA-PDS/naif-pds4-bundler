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
from textwrap import dedent

from os.path import dirname
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .classes.setup      import Setup
from .classes.log        import Log
from .classes.list       import KernelsList
from .classes.bundle     import Bundle
from .classes.collection import SpiceKernelsCollection
from .classes.product    import SpiceKernelProduct
from .classes.product    import MetaKernelProduct
from .classes.product    import InventoryProduct
from .classes.collection import DocumentCollection
from .classes.product    import SpicedsProduct


def main(config=False, plan=False, log=False, silent=False, interactive=False):
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
    
         naif-pds4-bundle-{version}, PDS4/PDS3 SPICE archive generation pipeline 
    
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
        parser.add_argument('plan', metavar='PLAN', type=str, nargs='+',
                            help='Release specific plan file')
        parser.add_argument('-l', '--log',
                            help='Write log in file.',
                            action='store_true')
        parser.add_argument('-s', '--silent',
                            help='Log will not be prompted.',
                            action='store_true')
        parser.add_argument('-i', '--interactive',
                            help='Activate interactive execution',
                            action='store_true')

        args     = parser.parse_args()
        config   = args.config[0]
        plan     = args.plan[0]
        log_file = args.log
        silent   = args.silent
        interact = args.interactive
    else:
        config   = config
        plan     = plan
        log_file = log
        silent   = silent
        interact = interactive

    #
    # -- Generate setup object
    #
    #    * This object will be used by all the other objects
    #    * Parse JSON into an object with attributes corresponding
    #      to dict keys.
    #
    setup = Setup(config, version, interact).setup

    #
    # -- Setup the logging
    #
    #    * The log will always be displayed on screen unless the silent
    #      option is chosen.
    #    * The log file will be written in the working directory
    #
    log = Log(setup, log_file, silent)

    #
    #  -- Start the pipeline
    #
    log.start()

    #
    # -- Generate the kernel list object
    #
    #    * The kernel list object will generate the kernel list
    #      non-archivable product.
    #
    list = KernelsList(setup, plan)

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
    # -- Prepare the staging area with the relevant information from the
    #    previous release (do not copy kernels).
    #

    #
    #
    spice_kernels_collection = SpiceKernelsCollection(setup, bundle)

    #
    # -- Populate the SPICE kernels collection from the kernels in
    #    the Kernel list
    #
    for kernel in list.kernel_list:
            if not '.tm' in kernel:
                spice_kernels_collection.add(
                SpiceKernelProduct(setup, kernel, spice_kernels_collection))

            #
            # -- Generate the meta-kernel(s)
            #
            else:

                spice_kernels_collection.add(
                    MetaKernelProduct(setup, kernel, spice_kernels_collection))

    #
    # -- Validate the SPICE Kernels collection:
    #
    #    * Check that there is a XML label for each file under spice_kernels.
    #      That is, we are validating the spice_kernel_collection.
    #
    #    * Check that all labels are within the correct time bounds.
    #
    #spice_kernels_collection.validate()

    #
    # -- Generate the SPICE kernels collection inventory product.
    #
    InventoryProduct(setup, spice_kernels_collection)


    #
    # -- Generate the document collection
    #
    document_collection = DocumentCollection(setup, bundle)


    #
    # -- Generation of SPICEDS document
    #
    if setup.pds == '4':

        spiceds = SpicedsProduct(setup, document_collection)

        #
        # -- If the SPICEDS document is generated then the document
        #    collection needs to be updated.
        #
        if spiceds.generated:
            document_collection.add(spiceds)

            #
            # -- Generation of the documents inventory
            #
            InventoryProduct(setup, document_collection)

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



    log.stop()
    return
