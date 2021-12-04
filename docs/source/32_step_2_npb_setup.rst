Step 2: Preparing the NAIF PDS4 Bundler Setup
=============================================

After having gathered, prepared, and listed the kernels to archive the next
step is to get ready to run the NAIF PDS4 Bundler (NPB). You need to
take the following steps:

   * prepare your workspace
   * write and/or update the SPICEDS file
   * install/update NPB
   * write and/or update the NPB configuration file


Workspace Setup
---------------

NPB requires a directory layout but without a rigid or particular structure
since each directory is specified in the configuration file. Although
this is discussed later under the configuration file section, NPB needs to
know the directories where the input kernels are located (**kernels** directories),
the directory where the ORBNUM files are located (**orbnum** directory,
if applicable), the NPB run final destination (**bundle** directory), the NPB
run staging area (**staging** directory, where NPB will move the input files and
generate PDS artifacts), and the directory where NPB will write the archive
generation logs and by-products (**working** directory).

If you are providing your own templates to NPB then you will also need to
specify a directory for them (**templates** directory.)


Working Directory
^^^^^^^^^^^^^^^^^

NPB requires a directory to generate the execution by-products that include but
are not limited to (depending on the execution arguments): an execution log,
a  kernel list, diff report files, and the file list. These files are described
in detail in the section :ref:`source/43_using_npb:Execution by-products`.

It is always a good idea to use the working directory as a
permanent directory to store the files used and generated for each archive
release: configuration file, validation report, release plan, etc. This allows
you to have a history of all the releases of an archive.


Kernels Directory
^^^^^^^^^^^^^^^^^

NPB needs to know where it will get the input kernels from. You can define as
many kernel directories as you want via configuration: NPB will search all of
them looking for the kernels specified in the **release plan**. As soon as it
finds one, it will short-circuit the search in the other directories for the
given kernel.

These directories must follow the usual SPICE kernel subdirectory structure based
on kernel type. The required subdirectories depend of the input kernel types.

The directory(ies) structure can be created ad-hoc for NPB or can already exist:
you might use your operational SPICE kernel operational directories.

If you call the directory ``kernels`` and you are archiving the following
kernels::

   nsy_sclkscet_00019.tsc
   insight_ida_enc_200829_201220_v1.bc
   insight_ida_pot_200829_201220_v1.bc

your kernels directory structure should be, at least::

   kernels/
   |-- ck
   +-- sclk

Of course it could also be something like this:
https://naif.jpl.nasa.gov/pub/naif/INSIGHT/kernels/

Please note that if you chose to generate MKs automatically (as explained
in section :ref:`source/31_step_1_preparing_data:Generating MKs Automatically`),
you might not need to include a ``mk`` subdirectory in the kernels directory
structure.


ORBNUM Directory
^^^^^^^^^^^^^^^^

ORBNUM files are not stored in the **kernels** directory, therefore
NPB requires you to specify where the ORBNUM files are located. For some
missions these files are under the ``kernels/spk`` directory, for others they
are under ``misc/orbnum``, and for others they are generated for the occasion
and could be anywhere.


Staging Directory
^^^^^^^^^^^^^^^^^

The staging directory is used by NPB to copy the input files to, and to generate
the archive increment. This directory could be empty for every NPB run or could
contain the files of the previous increment.

NAIF recommends you clear this directory for every archive release.


Bundle Directory
^^^^^^^^^^^^^^^^

The bundle directory points to the complete archive. This directory could be
the final, public destination of the archive or not (NAIF recommends
against it being the final destination). In any case this directory must contain
the complete archive.

NPB will copy the resulting files of the run (in the staging area) to this
bundle directory, unless indicated otherwise, as you will be able to learn in
:ref:`source/43_using_npb:Optional Arguments Description`.


Determination of the Archive Release Version
--------------------------------------------

NPB will determine the archive release version by accessing the existing bundle
label from the bundle directory. If no bundle is present NPB will default the
version to 01.


SPICE Kernel descriptions across the archive
--------------------------------------------

Spending the effort to prepare adequate descriptions of the data is
essential to guarantee that the data can be used correctly and efficiently
by future users. NAIF requires that SPICE archives provide kernel data
descriptions in the following three locations in the archive:

 * internal comments included in the kernels

 * SPICE Archive Description file (SPICEDS) provided in the document
   collection of the archive

 * description tag of the SPICE Kernel and ORBNUM labels

Descriptions given in each of these locations have different purposes
and levels of detail. The **comments** in a particular file provide the
most detailed and comprehensive information about the file that they
document and are discussed in great detail in the section
:ref:`source/31_step_1_preparing_data:Augmenting Files with Comments`.
The **SPICEDS** file provides a high level overview of the archive,
covering briefly the types of information provided in, the source data of,
and the accuracy of each type of kernels included in the data set. It also
describes the naming scheme and usage priority of the collection of
files of a particular kernel type in the data subdirectory in which they
reside. The **description tag** in XML *labels* provide a brief description of
the kernel, including its coverage (if relevant), its data source and/or
original name, and their producer.

Descriptions that are expected to be included in the SPICEDS file and in
labels are described in greater detail in the next few sub-sections of this
document.


SPICE Data Set Catalog File
---------------------------

The SPICE Archive Description file (SPICEDS) provides a high level overview of
SPICE, Kernel types, and the archive; covering briefly the type of information
provided in, the source of, and the accuracy of each kind of kernel included in
the data set.

Preparing the SPICEDS file is very easily done by taking an existing
SPICEDS file from an existing archive and changing just a few words
in it (such as mission name and acronym, publication dates, etc). NPB provides
a set of SPICEDS examples that can be found on
``tests/naif_pds4_bundler/data/spiceds_<sc>.html`` where ``<sc>`` is the mission
acronym.

When choosing a starting SPICEDS file make sure that you chose one
for a mission that is similar to the one you are generating the archive for.
For example, if you are generating the archive for a lander mission, you can
start with ``tests/naif_pds4_bundler/data/spiceds_insight.html``, whereas if
you need to include ORBNUM files, it might be interesting to take a look at
``tests/naif_pds4_bundler/data/spiceds_maven.html``. Look at
``tests/naif_pds4_bundler/data/spiceds_orex.html`` for an archive that includes
DSK files, and ``tests/naif_pds4_bundler/data/spiceds_m2020.html`` for a rover
mission.

The SPICEDS should contain a number of sections, many of which remain unchanged
from archive to archive. Below is a description of each of these sections with
recommendations on how to adapt them to your archive:

  * **Introduction** will require an update on the mission name, and if
    the mission has multiple observers you might also want to include them.

  * **Table of Contents** might be updated depending if you are including
    kernel types that are not present in your starting SPICEDS and
    adding or removing the "Orbit Number Files" sub-section.

  * **Overview** provides a high-level description of the archive and a
    paragraph that gives its approximate time coverage. The coverage is usually
    determined by the launch date and a pointer to the kernel that sets
    the end time of the of the archive. The determination of the archive
    coverage is discussed in section :ref:`source/22_pds4_spice_archive:Product Coverage Assignment Rules`.

  * **Errata** contains an enumerated list of errata items. These items are
    generally related either to incompatibilities or issues with the PDS4
    standard or to missing and/or incomplete data or liens. There are two items
    that are likely to be present starting with the first release of the archive.

    The following errata item must be present::

        This document is a simple HTML document. Providing documents in a
        simple mark-up format was allowed by earlier versions of the PDS4
        Standards but became prohibited in later versions starting summer
        2015. Since the document was compliant at the time when its first
        version was released, it will continue to exist in the archive
        as an HTML document.

    If you are using a PDS Information Model (IM) older than version 1.14.0.0
    (in fact NAIF recommends that you use IM version 1.5.0.0), then this item
    must be present as well::

        The XML labels of the ancillary products have the reference_type
        attribute of the Internal_Reference association within the
        Reference_List class of the Context_Area class pointing to the latest
        archive description document set to "ancillary_to_data" which is not
        correct. The correct value "ancillary_to_document" could not be used
        in these labels because it is not available in the PDS4 information
        model (IM) 1.5.0.0 used by this archive. This value was added to IM
        only in the version 1.14.0.0.

  * **Archive Contents** provides a diagram with the archive organization.
    You will need to update the mission acronym and add/remove the
    relevant kernel(s) and/or orbnum files and directories. Make sure that
    files and directory descriptions are properly aligned, since while
    updating them they might become misaligned.

  * **Kernel Types** provides a description of each kernel type. It needs
    to be adapted to the types of kernels present in the archive.

  * **Archived Kernel Details** provides brief general information about
    kernels of that type and describes the naming scheme, the source, and
    use priority for the collection of kernel files contained in each kernel
    subdirectory. This section is the one requiring the most work and it needs
    to be aligned with the descriptions that are discussed in
    :ref:`source/42_npb_configuration_file:Kernel Descriptions`. Each
    kernel type has a common introductory paragraph but the rest of the items
    are mission specific.

  * **Miscellaneous Files**, similar to the previous section it provides
    the information for checksum files and, if applicable, for ORBNUM files.
    The checksum file subsection requires no updates whereas the ORBNUM
    subsection, if present, needs to be adapted. More information on ORBNUM
    files is provided in section :ref:`source/31_step_1_preparing_data:A Word on Orbit Number Files`.

  * **File Formats** provides information on the text and binary files
    format. Although this section is very similar from archive to archive it
    requires adaptation depending on the kernel types and ORBNUM files present
    in the archive, and most importantly on the IM used.

    Archives that use a PDS IM older than 1.14.0.0 will use the following
    text::

       All text documents, checksum files, ORBNUM files, and other meta
       information files such as descriptions, detached PDS4 labels, and
       inventory tables, are stream format files, with a carriage return
       (ASCII 13) and a line feed character (ASCII 10) at the end of the
       records. This allows the files to be read by most operating systems.

       The text kernel files in this archive -- LSKs, PCKs, SCLKs, IKs, FKs,
       and MKs -- are UNIX text files, with a line feed character (ASCII 10)
       at the end of each line. Binary kernel files -- SPKs and CKs -- are
       IEEE LSB binary files. (...)

    Archives that use a PDS IM equal or newer than 1.14.0.0 might decide to use
    a line feed character (ASCII 10) at the end of each record for checksum
    and ORBNUM files. This is specified via configuration as described in
    :ref:`source/42_npb_configuration_file:The Information Model`. If so the
    text for this section should be something like this::

       All text documents and other meta information files such as descriptions,
       detached PDS4 labels, and inventory tables, are stream format files, with
       a carriage return (ASCII 13) and a line feed character (ASCII 10) at the
       end of the records. This allows the files to be read by most operating
       systems.

       The text kernel files in this archive -- LSKs, PCKs, SCLKs, IKs, FKs,
       and MKs --, the ORBNUM files, and the checksum files are UNIX text files,
       with a line feed character (ASCII 10) at the end of each line. Binary
       kernel files -- SPKs and CKs -- are IEEE LSB binary files. (...)

  * **SPICE Software and Documentation** provides a very brief description
    of the SPICE Toolkit and provides links to different resources. This
    section is archive agnostic

  * **Contact Information** provides the full contact information of the
    archiving authority of the organization responsible of the archive
    generation.

  * **Cognizant Persons** identifies the persons that have generated the
    archive along with their affiliation. Note that these are not necessarily
    the person(s) who generated the SPICE kernels.


A well written SPICEDS put together for the first release may not need to be
modified for future releases unless new kinds of kernels not reflected in it
get added to the archive, or the errata section items need to be added, updated
or removed.

NPB does a number of checks on the archive and its data but it does not do
any kind of check in the SPICEDS file. Because of this and given that so many
small changes need to be made by hand it is easy to overlook some corrections
that have to be done. Checking the files that have been updated after all
updates have been made is essential to catch that. The simplest ways to do such
checks is using ``tkdiff`` (or a similar difference visualization tool) to compare
the new version with the original version, and using ``grep`` to look for various
tokens that should and should not appear in the new description such as new and
old mission acronyms, new and old kernels, and so on.


Finally, we recommend lines in a SPICEDS document be no longer than 78
characters with the only exception for lines containing HTML references that
can extend beyond the 78 character limit.


Install and/or update the NAIF PDS4 Bundler
-------------------------------------------

Once the kernels are ready, the kernel list is ready, the meta-kernels have been
identified or have been written, the workspace is in place, and the SPICEDS file
has been generated or updated, it is time for the NAIF PDS4 Bundler (NPB) to
come into play.

The first thing you need to do is to install and/or update NPB. To do so
please follow the instructions provided in
:ref:`source/41_npb_installation:NPB Installation`. Once you are done, come back
here.

At this point you should be able to run the following command in a terminal::

   $ naif-pds4-bundler --help

You should see a result similar to the following one:

.. automodule:: pds.naif_pds4_bundler.__main__


Write and/or update the NPB Configuration File
----------------------------------------------

Writing and/or updating the NPB Configuration File is the most important and
"challenging" step of the archive generation, second only to the collection and
preparation of the data. It requires a considerable effort, especially for the
first release.

Once you get to this point, if you get the configuration wrong
or the NPB run doesn't go right, you will be able to get back to this "starting"
point with no effort.

Follow the instructions provided in
:ref:`source/42_npb_configuration_file:The Configuration File`
to write or update the Configuration File. This process might require a
**considerable** effort. Once you've got the configuration
file in place, we recommend you name it as follows::

   <sc>_release_??.xml

where ``<sc>`` is the spacecraft acronym and ``??`` is the archive's release
version. The MAVEN release 26 configuration file will be::

   maven_release_26.xml

We recommend that you move and keep this file in your **working** directory.
