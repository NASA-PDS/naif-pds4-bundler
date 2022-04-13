Step 1: Preparing Data
======================

Ideally a SPICE kernel archive for a mission should include a comprehensive
set of kernels allowing a scientist to compute geometry for any of the
mission instruments in regards to any of the mission targets at all
applicable times during the mission.

To achieve this the archive would normally include all types of kernels
needed to provide ephemerides (SPKs), orientation (PCK) and shape (PCK
or DSK) of targets, trajectory (SPK) and orientation (CK) of the
spacecraft, orientation (CK) and geometric parameters (IK) of the
instruments, definitions of the spacecraft and instrument frames (FK),
and data for various time conversions (LSK and SCLK). If the project
produced Event Kernel (EK) files of any kind, they should also be
included in the archive.

If as a SPICE kernel archive producer you have been provided the data to be
archived, if all data are present in a given directory structure or in a
release plan, you might as well jump to
:ref:`32_step_2_npb_setup:Step 2: Preparing the NAIF PDS4 Bundler Setup`.


Identifying Data
----------------

Usually identifying data that should go into the archive is not very
difficult, especially when SPICE kernels were produced and used by the
project during operations. In such cases the following kernels used
during operations -- independent of whether if they were produced by the
project teams or obtained from NAIF or other sources -- should be
included in the archive:

  * SPKs

       *  planetary ephemeris SPK file(s), officially accepted by
          the project

       *  any natural satellite ephemeris SPK file(s), officially
          accepted by the project

       *  latest SPK file(s) for other types of mission targets
          (e.g. comets, asteroids)

       *  latest reconstructed spacecraft trajectory SPK file(s)

       *  target and/or spacecraft trajectory SPK file(s) produced
          by science team(s) (for example Gravity or Radio
          science); if any

       *  latest ground stations locations SPK file(s); if any

       *  latest structures/instrument locations SPK file(s); if
          any

       *  predicted SPK(s); only if they are needed as gap-fillers
          for reconstructed data, or must be archived for the
          record; if any

       *  nominal/special SPK(s); only if they are needed to
          complete the position chains (such as M2020-at-landing
          site SPK); if any

  * PCK

       *  latest generic text PCK file officially used by the project

       *  latest generic binary PCK file(s) officially used by the
          project

       *  latest project-specific PCK file(s) providing the
          rotational, shape and possibly additional constants for all
          of the mission targets; if any

  * IK

       *  latest IK file for each of the instruments

       *  latest IK file for auxiliary s/c subsystems, the data
          from which might be used for science purposes (antennas,
          star trackers, horizon sensors, etc); if any

  * CK

       *  the latest reconstructed spacecraft attitude CK files

       *  possibly latest predicted spacecraft attitude CK
          files if they provide a reasonably good prediction
          and are needed to fill gaps in the reconstructed CK
          files and/or for some other reason

       *  latest reconstructed spacecraft appendage (solar arrays,
          HGA, etc.) attitude CK files; if any

       *  possibly latest predicted spacecraft appendage
          (solar array, HGA, etc.) attitude CK files if they
          provide a reasonably good prediction and are needed to
          fill gaps in the reconstructed CK files and/or for some
          other reason

       *  latest reconstructed instrument orientation CK files for
          each of the articulating instruments; if any

       *  possibly latest predicted instrument orientation CK
          files if they provide a reasonably good prediction
          and are needed to fill gaps in the reconstructed CK files
          and/or for some other reason

       *  spacecraft and/or instrument CK files produced by
          science teams as part of C-smithing or other pointing
          reconstruction process; if any

       *  nominal/special CK files, only if they are needed to
          complete the orientation chains (for example, an
          instrument parking position orientation CK file); if
          any

  * LSK

       *  last generic LSK file used by the project.

  * SCLK

       *  latest spacecraft on-board clock(s) correlation SCLK
          file(s)

       *  additional latest SCLK files if the project and/or
          science teams produced special SCLKs for instrument or
          other hardware clocks or if more than one kind of SCLK
          kernel was made for the same clock; if any

       *  special SCLK file implementing mean local time or other
          SCLK-like time systems (see MER for examples); if any

  * FK

       *  latest version of the main mission FK file(s)

       *  latest version of special mission FK file(s) (separate
          landing site FKs, etc); if any

       *  latest versions of separate instrument FK file(s); if any

       *  latest versions of generic FK file(s) for natural bodies
          (Moon, Earth, etc); if any

       *  latest versions of dynamic frames FK file(s); if any

  * DSK

       *  latest DSK file (or files if multiple kernels with different
          resolutions and/or for different parts of the surface were
          produced) for each of the mission targets; if any

       *  latest DSK file (or files if multiple kernels with different
          resolutions and/or for different parts of the surface were
          produced) for the mission s/c(s); if any


  * EK (Note: the EK subsystem is rarely used on modern missions.)

       *  PEF2EK-type sequence and command dictionary EK files
          (see SDU, Deep Impact for examples); if any

       *  database EK files (see CLEM for examples); if any

       *  CASSINI-style sequence, noise, plan, status EK files
          (see CASSINI for examples); if any

       *  ENB EK files (see MGS, SDU for examples); if any

While no mission produces all kernels from the list above, most missions
produce kernels of all types (maybe except EKs and DSKs) and most of these
kernels are needed to compute observation geometry for the mission
instruments and, therefore, should be included in the archive.

Once the types of kernels that should go into the archive have been
identified it is usually fairly easy to decide which actual individual
kernels belonging to each "category" should be included. Considering
these points may help to make this selection:

  * For the kernel types that don't cover specific time intervals,
    cover the whole mission and/or change rarely during the mission
    -- such as planetary, satellite, structures SPKs, DSK, LSK,
    PCK, FK, IK, and SCLK -- the latest version of each file at the
    time of archive preparation should be included.

    For the first archive release all latest kernels of these types
    should be included, while for subsequent releases only those
    kernels that had been updated or improved compared to the
    already archived files should be included.

    For example, if the project initially used the Martian
    Satellite Ephemerides MAR033 SPK file (which was included in
    the first archive release) but later switched to using the
    MAR066 SPK file, the MAR066 SPK file should be added to the
    archive at the next release opportunity. Another example is
    when the main project FK file was updated to include improved
    instrument alignment data; if this happened it should be added
    to the next archive release.

  * For the kernel types that provide data for specific time
    intervals that are normally much shorter than the whole
    duration of the mission -- such as spacecraft SPK, spacecraft,
    structure, and instrument orientation CKs, and EK -- the set of
    files providing complete coverage for the applicable interval
    should be included.

    If the archive preparation takes place at the end of the
    mission then all kernels of these types needed to provide data
    coverage for the whole mission should be included. If the
    mission is on-going and data is added to the archive at regular
    releases, each intended to cover a specific time
    interval, then each release should contain the set of these
    files providing complete coverage for the interval of interest.

  * In most cases including duplicate data should be avoided. For
    example, if the project is producing two strings of
    reconstructed spacecraft orientation CK files from the same
    telemetry input (daily "quick look" files and weekly
    "final" files) only the "final" CK files should be
    included. Another example is if the project used the same
    generic LSK file under two different names -- its original name
    and a short-cut default name, -- which is done sometimes to
    simplify operations infrastructure, then only the file with the
    original, actual name should be included in the archive.

    There are a few cases in which duplicate data should be
    included. The most common of these cases is when the data comes
    from two different producers, for example two sets of
    reconstructed spacecraft trajectory SPK files, one generated by
    the project NAV team and the other by the Gravity team. In such
    cases a determination of which set is "better" usually cannot
    be made and both sets should be archived.

  * Normally it is also not advisable to include obsolete or
    superseded data. There are numerous examples of cases when a
    kernel produced and used for some period in operation becomes
    obsolete when another version of the same data is released at a
    later time. The most common of these cases are predicted and
    quick-look reconstructed spacecraft trajectory SPK files that
    get superseded by the final reconstructed solution, and earlier
    versions of SCLK kernels that get superseded by the later
    versions.

    Exceptions to this suggestion include cases when superseded
    data is applicable as gap-filler (for example, predicted CKs
    used to fill gaps in telemetry based reconstructed CKs) or when
    an obsolete version needs to be archived to provide consistent
    access to other archived data (for example archiving an earlier
    version of SCLK that was used to make a predicted CK also
    included in the archive).

  * No kernel file or meta-kernel file already in the archive
    should ever be removed or replaced with a new version with the
    same name. Instead, any kernel or meta-kernel file added to the
    archive should have a name that is distinct from the names of
    all files already in the archive. If a kernel file supersedes
    one or more files already in the archive, this fact should be
    reflected in the SPICE Archive Description file (SPICEDS) and another
    version of the meta-kernel(s) should be created including this kernel
    file instead of the kernel file(s) that it supersedes.


Collecting and Preparing Data
-----------------------------

Once the data files have been identified it makes sense to collect them
in a single area (the ``kernels_directory``) because frequently the kernels
need to be pre-processed before they can go into the archive. Such
pre-processing may involve merging or sub-setting files, renaming files
to make their names PDS compliant, and augmenting files with internal
comments. It should also include validating the final products that will
go into the archive.

The kernel area must be structured as the ``spice_kernel`` collection, with
a subdirectory for each kernel type. It can virtually reside on more than
one location given that more than one directory can be provided to
the NAIF PDS4 Bundler via configuration, but having it on a single directory
simplifies pre-processing and validation tasks. It does not have to include
kernels that don't require pre-processing (merging, renaming or additional
comments) and can go into the archive "as is" **but** including these kernels
might also simplify pre-processing and validation tasks that require multiple
kernel types.

The kernels that do need to be pre-processed should be copied or
"binary FTP"-ed or "scp"-ed to the work area.

The ways in which the files should be modified usually include one or more of
the following:

   * merging files
   * sub-setting files
   * augmenting file with comments
   * renaming files

Some rationale for each of these modifications are provided hereunder.


Merging Files
^^^^^^^^^^^^^

The data from two or more files may need to be merged together
for a number of reasons: to reduce the number of files included
in the archive, to eliminate gaps in coverage at the file
boundaries, to produce a file that segregates data pieces that
must be used together, or to integrate data from updated
un-official versions of a file into the official version.

Merging to reduce the number of files is usually desirable for
the project-generated CKs or SPKs covering short periods of
time, for example daily or weekly files, when these files are
not very large in size. Merging such files together into a
single file covering the whole archive release time span --
monthly, tri-monthly, etc. -- or a few files covering parts of
that span will result in substantially reduced number of files,
which in turn will reduce the amount of processing needed to
put this data into the archive and make access to the archive
data more efficient.

Merging files to eliminate gaps at file boundaries is usually
desirable when the project generates a large number of CK files
of the same kind with short coverages not overlapping each
other. If the merged file is created from these individual CKs
in such a way that data from multiple source segments is
aggregated together in the new set of segments, the gaps at the
original file boundary times will not be present in the new
file.

Merging files to produce a file that aggregates data pieces
that must be used together in one place may be needed when the
spacecraft trajectory SPK and the target ephemeris SPK used to
determine it are delivered by the project in two separate
files. When this happens it leaves a possibility for the users
to use the spacecraft data with a different target trajectory
resulting in the wrong relative geometry being computed. This
situation happens very rarely but it needs to be checked and
addressed.

Merging files to integrate data from an updated un-official
version of a file into the official version is usually needed
when science teams keep a local copy of the main project FK and
change it by modifying alignment of a previously defined
frame(s) and/or introducing a new frame(s) for their
instruments. It is important to inquire about such "local"
updated copies and, if they exist, collect them and carefully
incorporate the data from them into the new version of the
official project FK file.

When selecting how many files to merge together the size of the
merged file should be one of the factors to consider. While
SPICE does not impose a "hard" limit of a number of megabytes
under which this size should be kept -- except, of course, for
the 2.1 GB which is the limit for 4-byte integer address space,
-- is it probably wise to keep the file size under 200-300 MB.

NAIF distributes a few utility programs that can be used to
merge various types of kernels. ``SPKMERGE`` provided in the
generic Toolkit can be used to merge SPK files. ``DAFCAT`` and
``CKSMRG`` available on the
`NAIF server <http://naif.jpl.nasa.gov/naif/utilities.html>`_ can be used to
merge CK files. In some cases NAIF puts together scripts
wrapped around these merge utilities to facilitate file merge
tasks that have to be repeated for each archive release.


Sub-setting Files
^^^^^^^^^^^^^^^^^

Sub-setting source files to produce archival files with reduced
scope or coverage is needed very rarely. In general it is
better to include data files with coverage that extends beyond
the current archive release interval rather than to try
"chopping" the file's coverage to line up with that boundary.
But if the project archiving policies or other considerations
require such "lining up" the ``SPKMERGE`` utility (provided in
the generic Toolkit) can be used to subset SPK files and the
``CKSLICER`` utility (available on the
`NAIF server <http://naif.jpl.nasa.gov/naif/utilities.html>`_ ) can be used to
subset CK files.


Augmenting Files with Comments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is absolutely crucial that every kernel included in the
archive contains comprehensive internal comments describing its
contents, source(s) of the data, applicability of the data,
etc. This means that all kernels intended for the archive --
binary and text ones, those that should be archived "as is"
and those that were created by merging or sub-setting other
files -- should be checked to verify that they contain adequate
comments and, if not, augmented with such comments.

Kernels included in the archive must contain comprehensive internal comments
that describe:

   * contents of the file

   * version and revision history

   * status and purpose of the file

   * source(s) of the data (including names of the original files if the file
     was created by merging or sub-setting other files)

   * processing that was done on the data

   * setup parameters and output logs for utility(ies) used to
     create the file

   * applicability of the data

   * data coverage

   * data accuracy

   * other kernels needed to use the file

   * references

   * data producer and contact information

The comments for a particular file should address all of the categories
from this list that are applicable to the kind of data stored in the
file.

The best approach to writing comments for a SPICE kernel is to start
with the comments from a kernel of the same type containing the same or
similar kind of information and modify these comments to describe the
file in hand. These comments should be used as a reference or even the
starting point for comments for the kernels intended for archiving.

In binary kernels internal comments reside in the special area
of the file called the "comment area". The comments provided
in this area can be accessed -- displayed, added to, or deleted --
using the ``COMMNT`` utility program. To add new comments to a
binary kernel file that does not have any comments, one would
first write a text file containing these comments and then add
the contents of this file to the comment area using ``commnt -a``.
To replace existing comments in a binary kernel file, one
would first view existing comments using ``commnt -r`` (or save
them to a text file ``commnt -e``), write a text file
containing new comments (or edit the text file containing
existing comments), delete existing comments from the file
using ``commnt -d``, and finally add new or updated comments to
the file using ``commnt -a``.

In text kernels comments are located at the top part of the
file, up to the first ``\begindata`` token on a line by itself,
and in the file sections delimited by ``\begintext`` and
``\begindata`` tokens, each on a line by itself. Any number of
comment sections intermixed with the data sections can be
included in the file. Modifying comments in a text file can be
done using any text editor. When modifications are made to the
file comments, the file version should be increased and the
scope of the comment modifications should be mentioned in the
version section of the comments.

Comments in both binary and text kernels should contain only
printable ASCII characters (no TABs); it is also strongly
recommended that comment lines should be no longer than 80
characters.

All archived kernels have a NAIF file ID architecture/type token as the first
"word" on the first line of the file. The SPICE binary kernel
files are guaranteed to have this ID word, but the ASCII text
kernels: FK, IK, LSK, PCK, SCLK, are not. For completeness,
the appropriate ID words are listed hereunder, so that they may be
inserted into the ASCII text kernel files if necessary.

.. list-table:: NAIF File ID Words
   :widths: 25 25
   :header-rows: 1

   * - ASCII Text File Type
     - ID Word
   * - IK
     - KPL/IK
   * - LSK
     - KPL/LSK
   * - PCL
     - KPL/PCL
   * - SCLK
     - KPL/SCLK
   * - FRAMES
     - KPL/FK
   * - MK
     - KPL/MK

While it is not possible to automate writing comments -- as
with any other documentation this is the task that needs to be
done by the person who puts the archive together by hand or by
"recruiting" the people/teams who provided the data -- it is
certainly possible to automate generating comments for a string
of files of a certain type using a template and inserting these
comments into the files.


Renaming Files
^^^^^^^^^^^^^^

The names of the files to be included in the archive must comply with the PDS4
file name rules. Rules for forming file and directory names are given in the
PDS4 Standards Reference [PDS4STD]_. Here are a few things to keep in mind:

  * The file name -excluding the extension- must be unique within its parent
    directory (it is common to have SPKs and ORBNUMs with the same name but
    they are in different directories.)

  * File names must be no longer than 255 characters, including the extension.

  * File names must be case-insensitive; for example, ``MyFile.txt`` and
    ``myfile.txt`` are not permitted in the same directory.

  * File names must be constructed from the character set:

       * ``A-Z`` ASCII ``0x41`` through ``0x5A``
       * ``a-z`` ASCII ``0x61`` through ``0x7A``
       * ``0-9`` ASCII ``0x30`` through ``0x39``
       * dash ``-`` ASCII ``0x2D``
       * underscore ``_`` ASCII ``0x5F``
       * period ``.`` ASCII ``0x2E``

  * File names must not begin or end with a dash, underscore, or period.

  * The file name must include at least one period followed by an extension.
    A file name may have more than one period, but PDS will consider all
    periods other than the final one to be part of the base name.

The requirement that NAIF imposes in addition to these general PDS requirements
is that the extensions of the kernel files must follow the established
convention for SPICE kernels:

.. list-table:: SPICE kernels extensions
   :widths: 25 25
   :header-rows: 1

   * - Kernel type
     - Extension
   * - Binary SPKs
     - ``.bsp``
   * - Binary PCKs
     - ``.bpc``
   * - Binary DSKs
     - ``.bds``
   * - Binary CKs
     - ``.bc``
   * - Binary Sequence EKs
     - ``.bes``
   * - Binary Database EKs
     - ``.bdb``
   * - Binary Plan EKs
     - ``.bep``
   * - Text PCKs
     - ``.tpc``
   * - Text IKs
     - ``.ti``
   * - Text FKs
     - ``.tf``
   * - Text LSKs
     - ``.tls``
   * - Text SCLKs
     - ``.tsc``
   * - Text Notebook EKs
     - ``.ten``
   * - Text Meta-kernels
     - ``.tm``

ORBNUM files must have either a ``.orb`` or ``.nrb`` extension.

All names that don't comply with these requirements must be changed.

On top of the PDS4 Standard rules, NAIF highly recommends to:

       * ``a-z`` ASCII ``0x61`` through ``0x7A`` (only lowercase)
       * ``0-9`` ASCII ``0x30`` through ``0x39``
       * underscore ``_`` ASCII ``0x5F``
       * only one period ``.`` ASCII ``0x2E`` to separate the extension
       * limit the length of the file to a 36.3 form: 1-36 character long name + 1-3 character long extension

It is especially important to have lowercase SPICE Kernels names given that
LIDs -and therefore Kernel Internal References in meta-kernel labels- must be
lowercase.

NAIF also strongly recommends that the names of all mission
specific kernels start with the acronym of the spacecraft or
the mission (if a data file contains data for more than one
spacecraft associated with the same mission). For example, the
names of Mars 2020 kernels start with ``m2020_``, the names of ExoMars2016
kernels start with ``em16_``, and so on. It is also recommended to exclude
redundant information from the filename such as the kernel type.

Because of the reasons explained above, very frequently the name of kernels
to archive has to be updated. The update can be done manually simply by
updating the file name or NPB can be configured to do so for you. For more
information on how to implement kernel file name mapping see
:ref:`42_npb_configuration_file:Mapping kernels` from the NPB
Configuration File description.

In order to preserve traceability with the original SPICE kernel name
-especially if that kernel is stored in a publicly accessible storage-, you can
provide the original file name in the PDS4 label description field or in the
kernel internal comments (See section :ref:`42_npb_configuration_file:Kernel Descriptions`.)

For example the following kernel for the MAVEN mission::

     spk_MAVEN_20210101-20220101_v01.oem.bsp

could be renamed to::

     maven_202210101_20220101_v01.bsp

Validating Data
---------------

Although the majority of the source kernels (both those that go into the
archive "as is" and those that have been used to make the merged
archive files) have been used in operations and have been validated by
this use, the final complete set of archival files must be validated by
checking the files' coverages, data scope, correctness of comments, data
accessibility, integrity, and consistency. The following validation
approaches complementing each other are suggested:

   * summarizing individual binary kernels (binary SPK, DSK, CK,
     PCK, EK) and meta-kernels using ``BRIEF``, ``DSKBRIEF``, ``CKBRIEF``, and
     ``SPACIT`` utilities to verify that they are accessible, provide
     data for the right set of bodies/structures, and have expected
     coverage

   * summarizing FOV definitions in IKs -- directly or via
     meta-kernels -- using ``OPTIKS`` to verify that the IKs are
     accessible and provide data for the right set of
     instruments/detectors

   * checking comments in the kernels -- both text and binary -- for
     completeness, correctness and consistency with the summaries of
     the data produced by summary tools

   * comparing files with similar data (for example spacecraft SPKs
     from different producers) and examining differences to see that
     they look reasonable; for SPK files this can be done using the
     ``SPKDIFF`` utility, for CK and FK files this can be done using the
     ``FRMDIFF`` utility

   * comparing later versions of kernels that need to be added to
     the archive with already archived earlier versions; for text
     kernels this can be done by analyzing differences shown by Unix
     utilities ``diff`` or ``tkdiff``

   * comparing merged archival products with the source operational
     files; for SPK files this can be done using the ``SPKDIFF``
     utility, for CK files this can be done using the ``FRMDIFF``
     utility

   * checking file data integrity by running utilities like ``SPY``
     (currently works only on SPK files)

   * checking file data integrity by running a local instance of
     WebGeocalc or SPICE-Enhanced Cosmographia

   * writing an application to compute geometry using the archival
     data and comparing that geometry to known values, for example
     from the geometry keywords in the science data labels; ideally
     such computations should be done for each of the instruments,
     for the quantities that require data from kernels of all types
     to be accessed, and over the whole span covered by the archive
     or a particular archive release

   * asking the project SPICE users to re-run some of the geometry
     computations that they have done with source operational files
     using the final set of kernels and verify that they obtained
     the same results

While some of the validation tasks can be scripted (for example checking
coverage based on file summaries or running ``SPY`` to check file data
integrity), many others have to be done by hand (for example assessing
comments in new version of text kernels) in many cases making validation
a time and effort consuming activity. Still, the person preparing the
archive should try to give their best effort to make sure that each
archive release contains the complete set of files (in terms of scope
and coverage) that are well documented with internal comments.


Binary Kernels Endianness
-------------------------

As specified in :ref:`21_naif_approach:NAIF's Approach to SPICE Kernel Archive Preparation`,
NAIF requires all binary kernels to be in ``LTL-IEEE`` (little-endian, also
known as IEEE LSB) binary format. By default NPB will enforce binary kernels to
be ``LTL-IEEE`` and the execution will stop in case any binary kernel is
``BIG-IEEE`` (big-endian, also known as IEEE MSB). You can force
NPB to accept ``BIG-IEEE`` binary kernels by specifying it via configuration
as described in :ref:`42_npb_configuration_file:Bundle Parameters`.

In order to determine the endianness of a binary kernel you can use
NAIF's utility ``BFF``. ``BFF`` is a command line program that displays the
binary file format ID for one or more binary kernel files. E.g.::

      $ bff mer2_surf_rover.bsp
      BIG-IEEE

If a binary kernel has been generated with a ``BIG-IEEE`` machine you can use
the NAIF utility ``BINGO`` to change its endianness. E.g.::

      $ bingo mer2_surf_rover.bsp mer2_surf_rover.little.bsp
      $ mv mer2_surf_rover.little.bsp mer2_surf_rover.bsp
      $ bff mer2_surf_rover.bsp
      LTL-IEEE

The endianness of the binary kernels of the archive should be indicated in the
**File Formats** section of the SPICEDS file.


Preparing Meta-kernels
----------------------

Meta-kernel files (MKs, a.k.a "furnsh" files) provide a list of the
kernels included in the archive suitable for loading
into a SPICE-based application via the high level SPICE data
loader routine ``FURNSH``. Using meta-kernels makes it easy to
load, with one call, a comprehensive SPICE data collection for
a given period, which, given that SPICE archives can contain
large number of files, is extremely helpful for users.

For missions with a small number of archived kernels NAIF
recommends creating a single meta-kernel providing data for the
whole mission. The name of this meta-kernel should follow the
``<sc>_v??.tm`` pattern where ``<sc>`` is the mission acronym and
``??`` is the version number. The version number can have two or
three digits, the number of digits must be the same for all the
different meta-kernels included. If/when new kernels are added to
the archive, a meta-kernel with the next version number,
including the new kernels and leaving out superseded kernels
should be created and added to the archive.

For missions with a large number of archived kernels NAIF
recommends creating a set of meta-kernels each covering one
year of the mission. The names of these meta-kernels should
follow the ``<sc>_yyyy_v??.tm`` pattern where ``<sc>`` is the
mission acronym, ``yyyy`` is the year covered by this data, and
``??`` is the version number. If/when new kernels are added to
the archive, meta-kernels for all applicable years with the
next version number, including the new kernels and leaving out
superseded kernels should be created and added to the archive.

In general, though there can be more kinds of MKs in an archive and
therefore in general MKs follow the ``<sc><_type>_v??.tm`` pattern.
For example, the OSIRIS-REx archive includes a MK that includes a
particular type of CK and another MK that excludes it; for a given
release of a given year the added MKs are::

   orx_2021_v01.tm
   orx_noola_2021_v01.tm

MKs can either be manually generated by the archive producer (or by the
operations team) or can be automatically generated (or assisted) by NPB.


Generating MKs Manually
^^^^^^^^^^^^^^^^^^^^^^^

If you chose to generate MKs manually, we recommend that as a starting point
you use a MK from a similar archive or if you are incrementing an already
existing archive to use the latest archived MK.

You will need to specify the location of the new MK in the NPB configuration
file as indicated in :ref:`42_npb_configuration_file:Meta-kernel`,
alternatively you can place the MK in the MK subdirectory of your input
kernels directory and then include it in the release plan as indicated in
:ref:`31_step_1_preparing_data:Meta-kernels in the release plan`.

More information on how to generate adequate MKs is available at [KERNELS]_.


Generating MKs Automatically
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The generation of MKs can be automatized by providing to the NPB configuration
file the appropriate parameters. This is described in detail in
:ref:`42_npb_configuration_file:Automatic generation of Meta-kernels`.

Please note that depending on the complexity and particulars of the MK(s) you
need to archive, setting up the automatic generation might not be possible. If
so please contact the NAIF NPB developer or, if reasonable, try to generate the
MKs manually.

The main advantage of generating MKs automatically is that you decrease the
possibilities of a human error. We know by experience that introducing errors
in manually generated MKs is very common.

Regardless of the method that you chose to generate MKs be especially careful
when reviewing and validating them.


Bundle coverage and MKs
^^^^^^^^^^^^^^^^^^^^^^^

In general, MKs will determine the archive increment start and finish times as
described in section :ref:`22_pds4_spice_archive:Product Coverage Assignment Rules`.

The coverage will be determined by either a CK or a SPK kernel as specified
via configuration --more information in section
:ref:`42_npb_configuration_file:Coverage determination`--, but the MK
coverage can also be defined explicitly via configuration if necessary. This
could be useful for example when SPks and CKs do not explicitly cover the
dates required by the archive, e.g.: a lander mission with a fixed
position provided by an SPK with extended coverage --this is the case for
InSight--. This configuration parameter is explained in section
:ref:`42_npb_configuration_file:Increment Start and Finish Times`.


Releases without MKs
^^^^^^^^^^^^^^^^^^^^

But what if the release does not have any MK? This is perfectly fine, but
NPB will lose the ability to compute the increment coverage from the MK and if
the increment coverage is not provided via configuration as explained in section
:ref:`42_npb_configuration_file:Increment Start and Finish Times`, then
the increment times will be set to the mission start and finish times specified
in the configuration file as described in section
:ref:`42_npb_configuration_file:Mission Parameters`.


A Word on Orbit Number Files
----------------------------

For some of the orbiter-style missions NAIF has created a derived geometry
product known as an Orbit Number File (ORBNUM). The primary purpose of such a
file is to provide SPICE users a means to determine the time boundaries for
each orbit. Some additional orbit geometry information is also provided.

ORBNUM files are plain ASCII text files consisting of two header lines
(column labels)
followed by one line of data per orbit. ORBNUM files can be generated with
NAIF's ``ORBNUM`` utility program. One of the required inputs to generate
ORBNUM files are SPKs.

Normally the orbit number files have the same names as the
corresponding SPK files but with the extension ``.bsp`` replaced by
``.orb`` or ``.nrb``. In a few cases more than one orbit number file
may exist for a given SPK, with only one file having the same name
as the SPK and other files having a version token appended to the
SPK name.

ORBNUM files with the ``.orb`` extension contain data that
follow the "periapsis-to-periapsis" orbit numbering scheme -- with
the orbit number changing at periapsis.

ORBNUM files with the ``.nrb`` extension contain data that
follow the "node-to-node" orbit numbering scheme -- with the orbit
number changing at the descending node.

The information contained in ORBNUM files includes the
orbit number (``No.``), periapsis or descending node UTC time
(``Event UTC PERI`` or ``Event UTC D-NODE``) and SCLK time (``Event
SCLK PERI`` or ``Event SCLK D-NODE`` ), apoapsis or ascending UTC
time (``OP-Event UTC APO`` or ``OP-Event UTC A-NODE``). It also
includes a few additional items computed at the time of periapsis or
descending node such as planetocentric subsolar longitude and
latitude (``SolLon`` and ``SolLat``) in the given central body body-fixed
frame.

If ORBNUM files are (or can be generated) for a mission, they should be
included in the archive.

NPB includes several examples of ORBNUM files that can be found at
``naif-pds4-bundler/tests/naif_pds4_bundler/data/misc/orbnum``


A Word on Other Files
---------------------

If the project produces other value-added files closely related to
kernels and "insists" on archiving them, these files can also be added
to the archive's Miscellaneous collection, but will require a deviation from
the current specification of a NAIF archive. For example, the CASSINI project
produces comparison plots and pointing correction plots for its
reconstructed and C-smithed CK files. CASSINI requests these plots be
included in the archive.

NAIF neither objects to nor recommends practices like this. If this is required
we recommend you contact NAIF.


Obtaining a DOI
---------------

DOIs are not mandatory for SPICE kernel archives but are desirable.
The DOI is provided in the NPB configuration file.

If the archive uses IM 1.5.0.0, it will not be able to include the DOI tag in
the bundle label (the IM does not allow it), if IM 1.14.0.0 or higher is used,
the DOI will be able to be included it in the bundle label.

Obtaining a DOI depends on the archive producer's archiving authority.
If you are producing a NASA SPICE Kernel bundle see the
`PDS Citation indications <https://pds.jpl.nasa.gov/datastandards/citing/>`_.
Note that a DOI will need a landing page, Below are a couple of examples
of DOIs and landing pages:

.. list-table:: DOI Examples
   :widths: 25 15 60
   :header-rows: 1

   * - Archive
     - DOI
     - Landing Page
   * - InSight
     - 10.17189/1520436
     - https://pds.nasa.gov/ds-view/pds/viewBundle.jsp?identifier=urn%3Anasa%3Apds%3Ainsight.spice
   * - ExoMars 2016
     - 10.5270/esa-pwviqkg
     - https://www.cosmos.esa.int/web/spice/exomars2016


Again coordinate with your archiving authority. To resolve a DOI to its Landing
Page you can use the following web: `DOI resolution resource <https://dx.doi.org/>`_.


Writing the Release Plan
------------------------

After having gathered all the SPICE kernels and ORBNUM files (if applicable),
you can (and probably must) write an Archive **Release Plan**, this release
plan is a text file that will list all the kernels to be included in the archive
**including Meta-Kernels and ORBNUM files**. Each kernel must be listed in a
separate line using its file name. Additional trailing characters can be present
as long as there are blank spaces between them and the kernel name. Lines
containing text of any other kind are also acceptable.

If the file names need to be modified, you must use the updated file name in
the release plan and have the file name mapping properly specified by the NPB
configuration file (this is described in :ref:`42_npb_configuration_file:Mapping kernels`.)

Here's three different extracts of release plan samples::

   nsy_sclkscet_00019.tsc
   insight_ida_enc_200829_201220_v1.bc
   insight_ida_pot_200829_201220_v1.bc

::

   NSY_SCLKSCET.00019.tsc \
   insight_ida_enc_200829_201220_v1.bc \
   insight_ida_pot_200829_201220_v1.bc \

::

   --- SCLK

   nsy_sclkscet_00019.tsc \

   --- CK

   insight_ida_enc_200829_201220_v1.bc \
   insight_ida_pot_200829_201220_v1.bc \

   No Cruise CKs in this release.


We recommend one follows this file name scheme for release plan files::

   <sc>_release_??.plan

where ``<sc>`` is the mission acronym and ``??`` is the archive's release
version. The MAVEN release 24 plan will be::

   maven_release_24.plan

For archive increments after the first or second release, we recommend that
you use the previous release plan as the starting point or the release plan
(copy the previous one and update it.)

Please note you can run NPB without providing a release plan. If you choose to
do so, NPB will take as inputs all the kernel files that it finds in the
kernels directory(ies) and will generate a release plan for you. This option is
useful when the kernel directory(ies) are generated ad-hoc for each release
or for first releases of small archives.


Meta-kernels in the release plan
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The inclusion of Meta-kernels in the release plan is optional if you have
already specified their location via configuration
(see :ref:`42_npb_configuration_file:Meta-kernel`).
