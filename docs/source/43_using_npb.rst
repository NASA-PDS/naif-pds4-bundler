Using NPB
=========

The functionality of NPB is to generate SPICE kernel archives (new archives or
archive increments, and achieves it by using as inputs a release plan and a
configuration file, that specifies the location of some other input elements:
input files directories, the directory with the current archive, the SPICEDS
file, etc.

Because of the nature of its functionality and the way it operates NPB can be
considered a software pipeline. More details on how NPB works are provided in
the next section.


NPB Functional Scheme
---------------------

This section provides a very high-level overview of NPBs functional design
and operation. If you need more details you might want to go to
:ref:`source/50_api_docs:Functions and Modules Documentation` or to take a
look at the source code itself. The following text is extracted directly from
the inline comments of the ``naif_pds4_bundler.__main__`` module.

  * Generate the Setup object
     * This object will be used by all the other objects
     * Parse JSON into an object with attributes corresponding
       to dict keys.

  * Start the Log object
     * The log will always be displayed on screen unless the silent
       option is chosen.
     * The log file will be written in the working directory

  * Check the existence of a previous archive version.

  * If the pipeline is running to clean-up a previous run, remove all the
    files in the bundle and staging area indicated by the file list and
    clean-up the kernel list and log from the previous run.
     * The pipeline can be stopped after cleaning up the previous run
       by setting ``-f, --faucet`` to ``clear``.

  * Generate the Kernel List object.
     * If a plan file is provided it is processed otherwise a plan is
       generated from the kernels directory.
     * The pipeline can be stopped after generating or reading the release
       plan by setting ``-f, --faucet`` to ``plan``.
     * The pipeline can be stopped after generating or reading the kernel
       list plan by setting ``-f, --faucet`` to ``list``.

  * Generate the PDS4 Bundle structure.

  * Load LSK, FK and SCLK kernels for time conversions and coverage
    computations.

  * Initialise the SPICE Kernels Collection.

  * Initialise the Miscellaneous Collection.

  * Generate the labels for each SPICE kernel or ORBNUM product and
    populate the SPICE kernels collection or the Miscellaneous collection
    accordingly.
     * Each label is validated after generation.

  * Generate the Meta-kernel(s).

  * Determine the SPICE kernels Collection increment times and VID.

  * Validate the SPICE Kernels collection:
     * Note the validation of products is performed after writing the
       product itself and therefore it is not explicitly executed
       from at object initialization.
     * Check that there is a XML label for each file under spice_kernels.

  *  Generate the SPICE Kernels Collection Inventory product (if the
     collection has been updated.)

  * Generate the Document Collection.

  * Generate of SPICEDS document.
     * If the SPICEDS document is generated, generate the
       Documents Collection Inventory.

  * Add the SPICE Kernels Collection to the Bundle.
    Note that the Collections are provided to the Bundle Object
    in a given order.

  * Generate the Miscellaneous collection. The Checksum product
    is initialised in such a way that its name can be obtained.

  * The first thing that is checked is whether if the current
    Bundle has checksums, if not, all the checksums are generated,
    including the corresponding Miscellaneous Collection Inventories
    and labels.

  * Set the Miscellaneous collection VID.

  * Add the Miscellaneous and Document Collections to the Bundle object.

  * Generate Miscellaneous Collection and initialize the Checksum
    product for the current release.
     * The miscellaneous collection is the one to be guaranteed to be
       updated.

  * Generate the Bundle label and if necessary the readme file.

  * Generate the Checksum product a posteriori in such a way
    that the miscellaneous collection inventory includes the
    checksum and the checksum includes the md5 hash of the
    Miscellaneous Collection Inventory.

  * List the files present in the staging area.

  * The pipeline can be stopped after generating the products and before
    moving them to the ``bundle_directory`` by setting ``-f, --faucet``
    to ``staging``.

  * Copy files to the bundle area.

  * The pipeline can be stopped after generating the moving the products
    ``bundle_directory`` by setting ``-f, --faucet`` to ``bundle``.

  * Validate Meta-kernel(s).

  * Validate Checksum files against the updated Bundle history.


There is a significant number of steps that are not reflected in the
bullets above, such as some validation steps performed by NPB. These validation
steps are summarised in section
:ref:`source/44_npb_implementation:NPB Validation methods`.


Running NPB from the command line
---------------------------------

Once installed, you can run NPB in help mode with the following command in a
terminal::

   $ naif-pds4-bundler --help

or::

   $ naif-pds4-bundler -h

You should expect the following result:

.. automodule:: naif_pds4_bundler.__main__

The execution of NPB has one positional argument, ``CONFIG``. This argument
must provide the path of the Configuration File. More information on the
Configuration File generation is available in section
:ref:`source/42_npb_configuration_file:The Configuration File`.

In addition there are a number of optional arguments that are detailed in
section :ref:`source/43_using_npb:Optional Arguments Description`.


Calling NPB from Python
-----------------------

In addition to using NPB from the command line you can also launch NPB from
a Python script/module. In fact, this is the way that the NPB tests are
implemented. To do so you will need to import the main function from the
package and provide the adequate arguments for the parameter list. The
parameter list mimics the command line parameters. Only the ``config``
parameter is mandatory. Here's an example::

   from naif_pds4_bundler.__main__ import main

   config = "working/dart_release_01.xml"

   main(config, plan=False, faucet="bundle", silent=True, log=True)


See :ref:`source/51_main:main function` for more information on NPB main
function.


Optional Arguments Description
------------------------------

This section provides a description of the optional arguments that can be
provided to NPB. The format with which this section is presented assumes that
you are using NPB from the command line, nevertheless everything also applies
when calling NPB from another Python script.


``-p PLAN, --plan PLAN``
^^^^^^^^^^^^^^^^^^^^^^^^

Indicates the path of the Release Plan. The input is a string. If provided,
NPB will scan the directories specified by the ``kernels_directory`` elements
of the Configuration File to obtain the files specified by the release plan.
These files are the main input for the generation of the archive release.

Since ``--plan`` is an optional argument, this means that you can run NPB
without providing a release plan. If you choose to do so, NPB will take as
inputs all the kernel files that it finds in the kernels directory(ies) and
will generate a release plan for you. This option is useful when the kernel
directory(ies) are generated ad-hoc for each release or for first releases of
small archives. The resulting release plan will following this naming scheme::

   <sc>_release_??.plan

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 plan would be::

   maven_release_26.plan

Please note that in general this is also the recommended naming scheme for
release plans. NPB determines the archive release version as described in
section :ref:`source/43_using_npb:Determination of the Archive Release Version`

The provision of this argument is highly recommended,
All the information to generate the Release Plan is provided in section
:ref:`source/31_step_1_preparing_data:Writing the Release Plan`

Oh, by the way, a release plan will **not** be generated if the ``-k --kerlist``
argument is provided.


``-f FAUCET, --faucet FAUCET``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pipelines in real world can have different faucets in such a way that you might
not have to wait until the end of the pipeline to get water. Similarly you
can chose where to stop the pipeline execution before its complete execution.
The options are:

   * ``clear``: stop after clearing the previous run see the ``-c --clear``
     argument subsection for more information.

   * ``plan``: stop after generating and/or reading the release plan. No
     products are written in the staging area (``staging_directory``.)

   * ``list``: stop after generating and/or reading the kernel list.
     If the Kernel List has not been provided (via the ``-k --kerlist``
     argument), the release plan will be generated.

   * ``staging``: stop after generating the archive increment products.
     The product list file is described in
     the ``-c --clear`` argument subsection.

   * ``bundle``: stop after moving the products to the bundle directory but
     before performing the last checks.

Using these faucets might be useful in different phases of the archive
generation, especially when the archive producer is not fully confident with
the state of the files in the plan or with the state of the configuration file.

You might also want to use the ``bundle`` option to prevent the checks from
being performed if you are confident with you reason to do so (e.g. a
meta-kernel not following NAIF's convention.)


``-l --log``
^^^^^^^^^^^^

This argument indicates NPB whether if the execution log should be written into
a file or not. If provided, the log will be written in the ``working_directory``
specified in the configuration file with the following naming scheme:

  <sc>_release_??.log

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 log would be::

   maven_release_26.log

More information on NPB logging is provided here
:ref:`source/44_npb_implementation:NPB Logging`.


``-s, --silent``
^^^^^^^^^^^^^^^^

If provided NPB execution will be silent without any prompt. This argument is
not recommended and was implemented mostly to avoid prompts during NPB
testing.


``-v, --verbose``
^^^^^^^^^^^^^^^^^

If provided NPB execution will be verbose and will be similar to the output
provided in the log file. If not specified, NPB provides a summarised log on
the terminal. Here's an example of the non-verbose terminal output for the first
release of the LADEE archive::

   naif-pds4-bundle-0.12.0 for LADEE
   =================================
   -- Executed on MT-308302 at 2021-09-28 12:57:41
   -- Setup the archive generation.
   -- Kernel List generation.
   -- Bundle/data set structure generation at staging area.
   -- Load LSK, PCK, FK and SCLK kernels.
   -- SPICE kernel collection/data processing.
      * Created spice_kernels/ck/ladee_13250_13330_v04.xml.
      * Created spice_kernels/spk/ladee_r_14108_99001_imp_v01.xml.
   -- Generation of meta-kernel(s).
      * Created spice_kernels/mk/ladee_v01.xml.
   -- Determine archive increment start and finish times.
   -- Validate SPICE kernel collection generation.
   -- Generation of spice_kernels collection.
      * Created /spice_kernels/collection_spice_kernels_inventory_v001.csv.
      * Created spice_kernels/collection_spice_kernels_v001.xml.
   -- Processing spiceds file.
      * Created document/spiceds_v001.xml.
   -- Generation of document collection.
      * Created /document/collection_document_inventory_v001.csv.
      * Created document/collection_document_v001.xml.
   -- Generation of miscellaneous collection.
      * Created /miscellaneous/collection_miscellaneous_inventory_v001.csv.
      * Created miscellaneous/collection_miscellaneous_v001.xml.
   -- Generation of bundle products.
      * Created readme file.
      * Created bundle_ladee_spice_v001.xml.
   -- Generate checksum file.
      * Created miscellaneous/checksum/checksum_v001.xml.
   -- Recap files in staging area.
   -- Copy files to the bundle area.
   -- Meta-kernel ladee_v01.tm validation.
   -- Validate bundle history with checksum files.
   Execution finished at 2021-09-28 12:57:43


``-d DIFF, --diff DIFF``
^^^^^^^^^^^^^^^^^^^^^^^^

If this argument is provided, NPB generates Diff files for the archive increment
files. NPB's Diff files are HTML files or plain text snippets that record
differences in between two files highlighting differences similar to the output
of a GUI diff tool such as TKDIFF. These files are useful to check and validate
the archive increment. More information on how these files are generated are
available at :ref:`source/44_npb_implementation:NPB Diff Files`.

The options for this argument determines the destination of these diff files.

   * ``files``: Diff files are HTML files that are written in the
                ``working_directory``, each diff'ed file is provided as a
                separate file.

   * ``log``: Diff plan text snippets are provided in the NPB log. This argument
              will force the ``-l --log``.

   * ``all``: Combines both ``files`` and ``log`` effects.


``-c CLEAR, --clear CLEAR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This argument allows you to clear the resulting products of a run from your
workspace. As you can tell is a very useful argument. Executing NPB with this
argument will clear the files listed in the input file from the staging and
bundle directories and the kernel list from the working area.

After you run NPB (successfully or not) one of the by-products that it generates
is the File List. The File List has the following naming scheme::

  <sc>_release_??.file_list

where <sc> is the spacecraft acronym and ?? is the archive's release
version. The MAVEN release 26 file list would be::

   maven_release_26.file_list

This file contains a list of all the products that have been generated from
a run with relative paths.

If this argument is provided it overwrites ``-f FAUCET, --faucet FAUCET`` to
``plan``, in such a way that the NPB execution will be stopped after cleaning
up the workspace. This said, you can still provide a different value to
``-f FAUCET, --faucet FAUCET`` in order to indicate NPB to continue with the
execution after clearing up the workspace.


``-k KERLIST, --kerlist KERLIST``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Indicates the path of a user generated Kernel List. The input is a string.
If provided, NPB will scan the directories specified by the
``kernels_directory`` elements of the Configuration File to obtain the files
specified by the kernel list and will by-pass the kernel list generation.

The provision of this argument is highly discouraged and should only be used
in special cases where the automated generation of the kernel list via
configuration is not possible. Please contact the NAIF NPB developer before
using this argument.

If this argument is provided no release plan file will be generated.


Execution by-products
=====================

   * <sc>_release_??.plan
   * <sc>_release_??.kernel_list
   * <sc>_release_??.log
   * <sc>_release_??.file_list
   * <sc>_release_??.checksum
   * diff_<new_file>_<old_file>.html


Checksum Registry File
----------------------

bla bla bla


Determination of the Archive Release Version
============================================




Bundle label construction
=========================

The creation_date_time tag of the readme.txt file is set to the bundle
increment generation time, rather than the readme.txt file time

And because this is the only way to embed the creation date within the
bundle .xml file -- from a quick look through IM I don't see any other
ways -- I would continue doing this and would not even bother to mention
this in errata.

The creation_date_time tag can be set to the readme.txt product creation
time by providina a modified label for the bundle using the configuration.
Instead of:


Multiple spacecrafts and mutliple targets. NPB incorporates the possibility to
have mutliple spacecrafts and targets in a Bundle. This is provided via
configuration. If so, the default spacecraft will be the primary spacecraft
which is specified in the configuration file. Otherwise it needs to be
specified in the Kernel List section of the configuration file. The non-kernels
bundle products will include all the targets and all the spacecrafts in the
labels.



When no list is provided as an input, the mapping of kernel does not occur and
the kernels present in the kernels directories need to have their final names
(and therefore they should not be expected to be mapped).


The value of PREC, the number of digits used
to report fractional seconds, must be
non-negative.  The value input was #.'

Fractional seconds, or for Julian dates, fractional
                  days, are rounded to the precision level specified
                  by the input argument PREC.


Coverage times determination
============================

bla bla bla

Checks performed by NPB
=======================

bla bla bla




spiceds
=======

-- why did you remove

       with a carriage return (ASCII 13) and

from

    All text documents and other meta information files such as
    descriptions, detached PDS4 labels, and inventory tables are stream
    format files, with a carriage return (ASCII 13) and a line feed
    character (ASCII 10) at the end of the records.  This allows the
    files to be read by most operating systems.

We are going to continue adding CRs to all text, XML, and other PDS
meta-files that we have in PDS4 archives as dictated by the standard, right?

And we should add CRs to checksum tables as well.

So please restore this.

The only files we will not add CRs to are text kernels and ORBNUM files
in bundles created using 1.G+ IM. So such bundles we should just add
ORBNUMs to the next paragraph that talks about text kernels, i.e.

    All text kernel files -- LSKs, PCKs, SCLKs, IKs, and FKs, -- and
    ORBNUM files in this archive are UNIX text files, with a line feed
    character (ASCII 10) at ...

For pre-1.G bundles we should add ORBNUMs to the paragraph above, i.e.

    All text documents and other meta information files such as
    descriptions, detached PDS4 labels, and inventory tables as well as
    ORBNUM files are stream format files, with a carriage return (ASCII
    13) and a line feed ...
