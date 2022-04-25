Using NPB
=========

The purpose of NPB is to generate SPICE kernel archives -- new archives or
archive increments. NPB achieves this by using as inputs a release plan and a
configuration file, that specifies the location of needed input elements:
input files directories, the directory with the current archive, the SPICEDS
file, etc.

Because of the nature of its functionality and the way it operates, NPB can be
considered a software pipeline. More details on how NPB works are provided in
the next section.


NPB Functional Scheme
---------------------

This section provides a very high-level overview of NPBs functional design
and operation. If you need more details you might want to go to
:ref:`50_api_docs:Modules, Classes, and Functions Documentation`, or take a
look at the source code itself. The following text is extracted directly from
the inline comments of the ``naif-pds4-bundler/src/pds/naif_pds4_bundler/__main__.py`` module.

  * Generate the Setup object

    * This object will be used by all the other objects
    * Parse JSON configuration file into an object with attributes
      corresponding to Python dictionary keys.

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

    * If a plan file is provided it is processed; otherwise a plan is
      generated from the kernels directory.
    * The pipeline can be stopped after generating or reading the release
      plan by setting ``-f, --faucet`` to ``plan``.
    * The pipeline can be stopped after generating or reading the kernel
      list plan by setting ``-f, --faucet`` to ``list``.

  * Generate the PDS4 Bundle structure.

  * Load LSK, FK and SCLK kernels for time conversions and coverage
    computations.

  * Initialize the SPICE Kernels Collection.

  * Initialize the Miscellaneous Collection.

  * Generate the labels for each SPICE kernel or ORBNUM product and
    populate the SPICE kernels collection or the Miscellaneous collection
    accordingly.

    * Each label is validated after generation.

  * Generate the Meta-kernel(s).

  * Determine the SPICE kernels Collection increment times and Product
    Version Identifier (VID).

  * Validate the SPICE Kernels collection:

    * Note the validation of individual products is performed after
      writing the product itself.
    * Check that there is a XML label for each file under ``spice_kernels``.

  * Generate the SPICE Kernels Collection Inventory product (if the
    collection has been updated.)

  * Generate the Document Collection.

  * Generate the SPICEDS document.

    * If the SPICEDS document is generated, generate the
      Documents Collection Inventory.

  * Add the SPICE Kernels Collection to the Bundle.
    Note that the Collections are provided to the Bundle Object
    in a given order.

  * Generate the Miscellaneous collection. The Checksum product
    is initialized in such a way that its name can be obtained.

  * The first thing that is checked is whether if the current
    Bundle has checksums; if not, all the checksums are generated,
    including for the corresponding Miscellaneous Collection Inventories
    and labels.

  * Set the Miscellaneous collection VID.

  * Add the Miscellaneous and Document Collections to the Bundle object.

  * Generate Miscellaneous Collection and initialize the Checksum
    product for the current release.

    * The miscellaneous collection is guaranteed to be updated.

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

  * The pipeline can be stopped after generating the moving of the products
    ``bundle_directory`` by setting ``-f, --faucet`` to ``bundle``.

  * Validate the Bundle by checking Checksum files against the updated
    Bundle history and checking the bundle times.

  * Validate Meta-kernel(s).
    This is the last step since it unloads all kernels.


There are a significant number of steps that are not reflected in the
bullets above, such as some validation steps performed by NPB. These validation
steps are summarized in section
:ref:`43_using_npb:Checks performed by NPB`.


Running NPB from the command line
---------------------------------

Once installed, you can run NPB in help mode with the following command in a
terminal::

   $ naif-pds4-bundler --help

or::

   $ naif-pds4-bundler -h

You should expect the following result:

.. automodule:: pds.naif_pds4_bundler.__main__

The execution of NPB has one positional argument, ``CONFIG``. This argument
must provide the path of the Configuration File. More information on the
Configuration File generation is available in section
:ref:`42_npb_configuration_file:The Configuration File`.

In addition there are a number of optional arguments that are detailed in
section :ref:`43_using_npb:Optional Arguments Description`.


Calling NPB from Python
-----------------------

In addition to using NPB from the command line you can also launch NPB from
a Python script/module. In fact, this is the way that the NPB tests are
implemented. To do so you will need to import the main function from the
package and provide arguments for the parameter list. The
parameter list mimics the command line parameters. Only the ``config``
parameter is mandatory. Here's an example::

   from pds.naif_pds4_bundler.__main__ import main

   config = "working/dart_release_01.xml"

   main(config, plan=False, faucet="bundle", silent=True, log=True)


Optional Arguments Description
------------------------------

This section provides a description of the optional arguments that can be
provided to NPB. The format with which this section is presented assumes that
you are using NPB from the command line, nevertheless everything also applies
when calling NPB with Python.


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
small archives.

The resulting release plan will follow this naming scheme::

   <sc>_release_??.plan

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 plan would be::

   maven_release_26.plan

Please note that in general this is also the recommended naming scheme for
release plans.

The provision of this argument is highly recommended.

All the information to generate the Release Plan is provided in section
:ref:`31_step_1_preparing_data:Writing the Release Plan`

A release plan will **not** be generated if the ``-k --kerlist``
argument is provided.

If you run NBP in label mode (that is, only to generate kernel labels), the
``--plan`` parameter can be the name of a single kernel instead of the path of
a file. More information is provided in the section ``-x, --xml``.


``-f FAUCET, --faucet FAUCET``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can chose where to stop the pipeline execution before its complete
execution. The options are:

   * ``clear``: stop after clearing the previous run see the ``-c --clear``
     argument subsection for more information.

   * ``plan``: stop after generating and/or reading the release plan. No
     products are written in the staging area (``staging_directory``.)

   * ``list``: stop after generating and/or reading the kernel list.
     If the Kernel List has not been provided (via the ``-k --kerlist``
     argument), a release plan will be generated.

   * ``checks``: stop after performing a number of checks on the products
     present in the kernel list. These checks are useful to identify issues
     on the SPICE kernels and ORBNUM files to be archived.

   * ``staging``: stop after generating the archive increment products.
     The product list file is described in
     the ``-c --clear`` argument subsection.

   * ``bundle``: stop after moving the products to the bundle directory but
     before performing the last checks.

   * ``labels``: specifies NPB to run in label mode. More information in
     the section :ref:`43_using_npb:Using NPB in label mode`

Using these options might be useful in different phases of the archive
generation, especially when the archive producer is not fully confident with
the state of the files in the plan or with the state of the configuration file.

You might also want to use the ``bundle`` option to prevent the checks from
being performed if you are confident with you reason to do so (e.g. use of a
meta-kernel not following NAIF's convention.)


``-l --log``
^^^^^^^^^^^^

This argument tells NPB if the execution log should be written into
a file or not. If provided, the log will be written in the ``working_directory``
specified in the configuration file with the following naming scheme::

     <sc>_release_??.log

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 log would be::

     maven_release_26.log

More information on NPB logging is provided in the section
:ref:`43_using_npb:Execution Log`.


``-s, --silent``
^^^^^^^^^^^^^^^^

If this option is used, NPB execution will be silent without any prompt. This
argument is not recommended and was implemented mostly to avoid prompts during
NPB testing.


``-v, --verbose``
^^^^^^^^^^^^^^^^^

If this option is used, NPB execution will be verbose and will be similar to the output
provided in the log file. If not specified, NPB provides a summarized log on
the terminal. Here's an example of the non-verbose terminal output for the first
release of the LADEE archive::

   naif-pds4-bundle-0.12.0 for LADEE
   =================================
   -- Executed on MT-308302 at 2021-09-28 12:57:41
   -- Setup the archive generation.
   -- Kernel List generation.
   -- Bundle structure generation at staging area.
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

If this argument is used, NPB generates Diff files for the archive's release
files. NPB's Diff files are HTML files or plain text snippets that record
differences in between two files, highlighting differences similar to the output
of a GUI diff tool such as ``tkdiff``. These files are useful to check and validate
the archive increment. More information on how these files are generated is
provided in section :ref:`43_using_npb:Validation Diff files`.

The options for this argument determine the destination of these diff files.

   * ``files``: Diff files are HTML files that are written in the
     ``working_directory``; each diff'ed file is provided as a separate file.

   * ``log``: Diff plan text snippets are provided in the NPB log. This argument
     will force the ``-l --log``.

   * ``all``: Combines both ``files`` and ``log`` effects.


``-c CLEAR, --clear CLEAR``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This argument allows you to clear the products resulting from a NPB run
from your workspace. Executing NPB with this argument will clear the files
listed in the input file from the staging and bundle directories.

After you run NPB (successfully or not) one of the by-products that it generates
is the File List. The File List has the following naming scheme::

  <sc>_release_??.file_list

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 file list would be::

   maven_release_26.file_list

This file contains a list of all the products that have been generated from
a run with relative paths.

If this argument is provided NPB defaults the argument ``-f FAUCET, --faucet FAUCET`` to
``plan``, in such a way that the NPB execution will be stopped after cleaning
up the workspace. This said, you can still provide a different value to
``-f FAUCET, --faucet FAUCET`` in order to instruct NPB to continue with the
execution after clearing up the workspace.

Note that executing NPB with the clear argument will not delete the kernel list
or the release plan **generated** by the run in the working area unless you
provide the the original value for the ``-p, --plan`` or ``-k, --kerlist``
arguments. If you do so NPB will remove the byproduct generated by the run. For
example, the following command::

 $ naif-pds4-bundler maven_release_26.xml -p working/maven_release_26.plan -c working/maven_release_26.file_list -v

Will remove the ``working/maven_release_26.kernel_list`` byproduct, given that
you are indicating that it has been generated with the original run, whereas::

 $ naif-pds4-bundler maven_release_26.xml -k working/maven_release_26.kernel_list -c working/maven_release_26.file_list -v

would remove the ``working/maven_release_26.plan`` byproduct. Use both arguments
to remove both.

Note that other by-product files such as the
checksums file, run log, file lists, and diff files are not deleted.


``-k KERLIST, --kerlist KERLIST``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifies the path of a user generated Kernel List.
If provided, NPB will scan the directories specified by the
``kernels_directory`` elements of the Configuration File to obtain the files
specified by the kernel list and will by-pass the kernel list generation.

The provision of this argument is highly discouraged and should only be used
in special cases where the automated generation of the kernel list via
configuration is not possible. If you find yourself in this situation
contact the NAIF NPB developer before using this argument.

If this argument is provided no release plan file will be generated.


``-s, --checksum``
^^^^^^^^^^^^^^^^^^

Using this argument indicates NPB to obtain MD5 Sums for products defined
in the Checksum Registry file or from existing product labels instead of
calculating them.

The Checksum Registry file is an NPB run by-product that contains the checksums
of all products. More information is provided in section
:ref:`43_using_npb:Checksum Registry`. This file is generated by a
previous NPB run for the same archive increment and is stored in the
``working_directory`` specified in the configuration, it has a ``*.checksum``
extension.

If no Checksum Registry files are available product labels from the
``staging_directory`` will be used.

This argument is useful if large files have already been processed by a previous
run.


Using NPB in label mode
-----------------------

NPB can also be used to generate SPICE kernels labels rather
than a complete PDS4 Bundle. When using NPB in label mode the same
setup required for a "regular" execution applies and almost complete
configuration file is required. The example configuration file for the
Hubble Space Telescope provides a differentiated example of a configuration
file used to generate labels only. The file is available at
``naif-pds4-bundler/tests/naif_pds4_bundler/config/hst.xml``.

In order to run NPB in label mode you need to set the ``-f FAUCET, --faucet FAUCET``
argument to ``labels``.

When doing so NPB runs in label mode and therefore does not
generate a complete PDS4 Bundle. This option was implemented to meet the needs
of some NPB users. Unless necessary, NAIF advises against its usage.

When using this argument NPB bypasses some execution steps (including certain
checks) in such a way that the only output of the execution is the generation
of the XML labels of the products specified by the ``-p --plan`` argument.

It is recommended to maintain a separate configuration file if NPB is executed
both in "default" mode and in "label" mode. When using "label" mode,
it is common to set the ``bundle_directory`` equal to the ``kernel_directory``
where the operational kernels usually reside.

When using this mode, only kernels can be labeled (no ORBNUM products),
MKs will not be automatically generated, and certain execution by-products
will not be generated either.

Using this mode will also change the file name of the NPB by-product files.
The ``_release_`` part of the name will be changed to ``_labels_`` to indicate
that the run did not generate a release but rather labels for a specific
targeted release (the release number part of these files will be incremented.)


Execution by-products
---------------------

After NPB is executed, a number of files are generated in the ``working_directory``.
These files have different purposes and some of them are generated if specified
via argument parameters. These files are:

   * Release Plan: ``<sc>_release_??.plan``
   * Kernel List: ``<sc>_release_??.kernel_list``
   * Execution Log: ``<sc>_release_??.log``
   * Execution File List: ``<sc>_release_??.file_list``
   * Checksum registry:``<sc>_release_??.checksum``
   * Validation Diff files: ``diff_<new_file>_<old_file>.html``

where

   * ``<sc>`` is the short s/c name or acronym (e.g. maven, em16, etc.)
   * ``??`` is the release version
   * ``<new_file>`` is the name of the file generated by NPB - without extension -
   * ``<old_file>`` is the name of the with which ``<new_file>`` is compared to
     - without extension -.

These files are described in the following sections.


Release Plan
^^^^^^^^^^^^

The release plan can be provided as an input as described in section
:ref:`31_step_1_preparing_data:Writing the Release Plan`. Alternatively, if not
provided as an input, NPB will generate it as an execution by-product.

The release plan is an adequate record that summarizes the kernels and orbnum
files included in each release.

If the release plan is generated by NPB it will follow this naming schema
``<sc>_release_??.plan``.


Kernel List
^^^^^^^^^^^

The kernel list can also be provided as an input - although is highly discouraged -
but in general is an execution by-product that includes a number of important
elements, used by NPB to generate SPICE kernel and orbnum files labels, such as
the kernel description.

The kernel list is an adequate record to check that each kernel description has
been written appropriately.

If the kernel list is generated by NPB it will follow this naming schema
``<sc>_release_??.kernel_list``.


Kernel Lists in PDS3 data sets
''''''''''''''''''''''''''''''

NPB can be used to generate kernel lists for PDS3 data set generation.

For PDS3 data sets, the kernel list is used by the NAIF PDS3 data set archiving
procedure. Because of that the kernel list for a particular release has a
structure similar to::

      DATE = <date>
      SPACECRAFT = <s/c>
      NAIFER = <full name>
      PHONE = <phone>
      EMAIL = <e-mail>
      VOLUMEID = <volume id>
      RELEASE_ID   = <number>
      RELEASE_DATE = <YYYY-MM-DD>
      EOH
      FILE             = <name of file 1>
      MAKLABEL_OPTIONS = <MAKLABEL options for file 1>
      DESCRIPTION      = <description of file 1, on a single line!>
      FILE             = <name of file 2>
      MAKLABEL_OPTIONS = <MAKLABEL options for file 2>
      DESCRIPTION      = <description of file 2, on a single line!>
      ...
      FILE             = <name of file N>
      MAKLABEL_OPTIONS = <MAKLABEL options for file N>
      DESCRIPTION      = <description of file N, on a single line!>

The first five keywords -- ``DATE``, ``SPACECRAFT``, ``NAIFER``, ``PHONE``,
``EMAIL`` -- and
the ``EOH`` end-of-the-header marker are optional and are included to
provide identification information.

The ``VOLUMEID``, ``RELEASE_ID``, and ``RELEASE_DATE`` keywords are required and
must be set as follows: ``VOLUMEID`` must be set to the lowercased version
of the volume ID (for example ``mgsp_1000`` for MGS), RELEASE_ID must be
set to the release ID number (for example ``0001`` for release 1), and
RELEASE_DATE must be set to the date on which the data will be released
to the public (for example ``2007-07-27`` for July 27, 2007.)

The rest of the kernel list file must provide triplets of lines, one for
each of the files that constitute the release, containing ``FILE``,
``MAKLABEL_OPTIONS``, and ``DESCRIPTION`` keywords. The ``FILE`` line must always be
first, followed by the ``MAKLABEL_OPTIONS`` line followed by the ``DESCRIPTION``
line.

The FILE keyword must provide the file name relative to the volumes's
root directory (for example ``data/spk/de403.bsp``).

The ``MAKLABEL_OPTIONS`` keyword must provide all ``MAKLABEL`` option tags
applicable to the file named in the preceding FILE keyword. The option
tags must be delimited by one or more spaces and will be passed "as
is" to the ``MAKLABEL`` program. If no options are applicable to a file,
``MAKLABEL_OPTIONS`` can be set to blank but the line containing it must
still be present in the list file, following the ``FILE`` keyword line.

The ``DESCRIPTION`` keyword must provide a brief description of the file;
this description will be inserted in the file label to replace the
generic description generated by the ``MAKLABEL`` program. The value must be
on the same line as the keyword and must not "spill" over onto the
next line(s). The length of the description is not limited. ``DESCRIPTION``
can be set to blank but the line containing it must still be present in
the list file, following the ``MAKLABEL_OPTIONS`` keyword line. When
description is set to blank, ``N/A`` is placed in the label.

The list file may contain blank lines as long as they are not placed
between the lines in each of the triplets.


Execution Log
^^^^^^^^^^^^^

The NPB execution log provides very useful information to determine whether
if the execution has been successful or not.

NPB uses the ``logging`` Python package to generate the log file. The log
will preface each line with the severity level of the message provided. The
severity levels are: ``INFO``, ``WARNING``, and ``ERROR``.

``INFO`` messages provide general information for the NPB operator to understand
what NPB is doing. ``WARNING`` messages flag unexpected or unusual actions
taken by NPB and require a careful examination by the operator since they might
lead to an undesired result in the archive generation. ``ERROR`` messages are
displayed if the NPB execution has failed -and therefore will only be present in
the temporary log resulting from a failed execution- or if an archived meta-kernel
is not loadable by the SPICE API ``FURNSH``.

The NPB log is structured in such a way that it narrates the archive generation
by providing numbered sections for each "main" action that NPB performs. The
log also includes a preface that provides information on the platform used to
run NPB, the execution parameters, and an epilogue that indicates the end of the
execition. The result of the different checks performed by NPB are also
provided in the log. More information on the checks done by NPB is provided in
section :ref:`43_using_npb:Checks performed by NPB`.
A Mars 2020 execution log extract is provided hereunder::

     INFO    :
     INFO    : naif-pds4-bundle-0.13.1 for Mars 2020 Perseverance Rover Mission
     INFO    : ================================================================
     INFO    :
     INFO    : -- Executed on pepper.rn.jpl.net at 2021-11-19 07:20:24
     INFO    : -- Platform: Linux-3.10.0-1160.45.1.el7.x86_64-x86_64-with-glibc2.17
     INFO    : -- Python version: 3.8.7 (Build: May 12 2021 16:53:18)
     INFO    :
     INFO    : -- The following arguments have been provided:
     INFO    :      config:  working/mars2020_release_02.xml
     INFO    :      plan:    working/mars2020_release_02.plan
     INFO    :      log:     True
     INFO    :      verbose: True
     INFO    :
     INFO    :
     WARNING : -- Label templates will use the ones from information model 1.5.0.0.
     INFO    : -- Label templates directory: /home/mcosta/virtenvs/npb_3.8/naif-pds4-bundler/src/pds/naif_pds4_bundler/templates/1.5.0.0/
     WARNING : -- There is no meta-kernel configuration to check.
     INFO    :
     INFO    :
     INFO    : Step 1 - Setup the archive generation
     INFO    : -------------------------------------
     INFO    :
     INFO    : -- Checking existence of previous release.
     INFO    :      Generating release 002.
     INFO    :
     INFO    :
     INFO    : Step 2 - Kernel List generation
     INFO    : -------------------------------
     (...)
     INFO    :
     INFO    : Execution finished at 2021-11-19 07:20:24
     INFO    :
     INFO    : End of log.


The execution log is only generated if specified via the argument ``-l --log``,
if so, the name will follow this naming convention: ``<sc>_release_??.log``.


Execution File List
^^^^^^^^^^^^^^^^^^^

The execution file list is an adequate record that provides a list of **all**
the files generated by the NPB execution.

This file is used by the ``-c --clear`` argument as the parameter to indicate
the files to be cleared from a previous successful or unsuccessful NPB
execution.

This file is also very useful to be used as input to a procedure to move
the archive increment from one location to the other.

The execution file list follows this naming schema ``<sc>_release_??.file_list``
as described in :ref:`43_using_npb:Execution by-products`.


Checksum Registry
^^^^^^^^^^^^^^^^^

The checksum execution registry is a file that contains a checksum table with
the md5 sum of every product of the increment whose md5 sum is used in the
product's label.

The utility of these files is described in section
:ref:`33_step_3_running_npb:Processing large binary kernels`.

The Checksum Regsitry file follows this naming schema ``<sc>_release_??.checksum``
as described in :ref:`43_using_npb:Execution by-products`.


Validation Diff Files
^^^^^^^^^^^^^^^^^^^^^

Validation Diff files are HTML files that provide a side to side comparison of
a product generated by NPB and another "similar" product in order to facilitate
checking and validating the new product, highlighting differences similar to
the output of a GUI diff tool such as ``tkdiff``.

This by-product is generated if indicated by the ``-d DIFF, --diff DIFF``
argument.


Checks performed by NPB
-----------------------

NPB performs a series of checks to validate certain parts of its execution and
provides means for the NPB operator to check the execution results. These
checks are described hereunder.


Kernel List Validation
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.list.KernelList.validate


Complete Kernel List Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.list.KernelList.validate_complete


SPICE Kernel Integrity Check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.product.SpiceKernelProduct.check_kernel_integrity


Meta-kernel Validation
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.product.MetaKernelProduct.validate


SPICE Kernel Collection Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.collection.SpiceKernelsCollection.validate


Inventory Product Validation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.product.InventoryProduct.validate_pds4


Checksum Validation
^^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.bundle.Bundle.validate_history


Product Comparison
^^^^^^^^^^^^^^^^^^

.. automodule:: pds.naif_pds4_bundler.classes.label.PDSLabel.compare
.. automodule:: pds.naif_pds4_bundler.classes.product.MetaKernelProduct.compare
.. automodule:: pds.naif_pds4_bundler.classes.product.InventoryProduct.compare
.. automodule:: pds.naif_pds4_bundler.classes.product.SpicedsProduct.compare
.. automodule:: pds.naif_pds4_bundler.classes.product.ChecksumProduct.compare


Comparison output
'''''''''''''''''

Depending on the parameter provided to NPB with the argument
``-d DIFF --d DIFF`` the comparison will be provided either as a
separate file, written in the execution log or in both ways.

If the comparison is provided in the log, its format will be similar
to the one provided by the Unix utility ``diff`` whereas if provided as a
separate file, it will be similar to the format provided by the Unix
utility ``tkdiff``: a HTML file that provide a side to side comparison of
the files following this naming scheme::

   diff_<new_file>_<old_file>.html

where

   * <new_file> is the name of the file generated by NPB - without extension -
   * <old_file> is the name of the with which <new_file> is compared to - without extension -.

If the ``-d DIFF --d DIFF`` argument is not provided the comparison
will not happen.
