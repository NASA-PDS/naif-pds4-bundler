NPB Execution by-products
=========================

   * <sc>_release_??.plan
   * <sc>_release_??.kernel_list
   * <sc>_release_??.log
   * <sc>_release_??.file_list
   * <sc>_release_??.checksum
   * diff_<new_file>_<old_file>.html


Checksum Registry File
----------------------

bla bla bla





SPICE kernel names
==================

As per the table above, you can see that, except for meta-kernels, files in
the SPICE kernels collection, are as follows::

    <kernel_name>.<kernel_extension>

where

   * <kernel_name> is the kernel filename,


PDS Information Model
=====================

Currently NPB includes templates for IM 1.5.0.0 and IM 1.16.0.0. Bundles with
schemas versions lower than 1.16.0.0 will use 1.5.0.0 templates. Bundles
with schemas equal or greater than 1.16.0.0 will use 1.16.0.0 templates.

Remember that you are able to provide your own templates by indicating the
directory where they reside via the configuration file. Use your templates
at your own risk and make sure that they pass all PDS Validate tool checks.



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

Kernel List File
================

Preparing Kernel List File

   After the MAKLABEL template has been prepared, the next step is to put
   together a kernel list file that, as the name suggests, lists all
   kernels that will be added to the archive in the release that is being
   prepared. The list file is the main input to the ``label_them_all.pl''
   script and, in addition to listing kernels, provides a set of MAKLABEL
   options (tags from the template) and a description for each of the files
   as well as some general information such as the data set ID, release ID,
   etc. (Note that a concatenation of all kernels lists for an archive is
   used as the primary input to the script that generates index files,
   ``xfer_index.pl'', discussed later in this document.)

   The kernel list file for a particular release must have the following
   content and structure:

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

   The first five keywords -- DATE, SPACECRAFT, NAIFER, PHONE, EMAIL -- and
   the ``EOH'' end-of-the-header marker are optional and are included to
   provide identification information. These keywords are not used by the
   ``label_them_all.pl'' or ``xfer_index.pl'' scripts. They are a ``carry
   over'' required by an earlier incarnation of NAIF's archive scripts.

   The VOLUMEID, RELEASE_ID, and RELEASE_DATE keywords are required and
   must be set as follows: VOLUMEID must be set to the lowercased version
   of the volume ID (for example ``mgsp_1000'' for MGS), RELEASE_ID must be
   set to the release ID number (for example ``0001'' for release 1), and
   RELEASE_DATE must be set to the date on which the data will be released
   to the public (for example ``2007-07-27'' for July 27, 2007.)

   The rest of the kernel list file must provide triplets of lines, one for
   each of the files that constitute the release, containing FILE,
   MAKLABEL_OPTIONS, and DESCRIPTION keywords. The FILE line must always be
   first, followed by the MAKLABEL_OPTIONS line followed by the DESCRIPTION
   line.

   The FILE keyword must provide the file name relative to the volumes's
   root directory (for example ``data/spk/de403.bsp'').

   The MAKLABEL_OPTIONS keyword must provide all MAKLABEL option tags
   applicable to the file named in the preceding FILE keyword. The option
   tags must be delimited by one or more spaces and will be passed ``as
   is'' to the MAKLABEL program. If no options are applicable to a file,
   MAKLABEL_OPTIONS can be set to blank but the line containing it must
   still be present in the list file, following the FILE keyword line.

   The DESCRIPTION keyword must provide a brief description of the file;
   this description will be inserted in the file label to replace the
   generic description generated by the MAKLABEL program. The value must be
   on the same line as the keyword and must not ``spill'' over onto the
   next line(s). The length of the description is not limited. DESCRIPTION
   can be set to blank but the line containing it must still be present in
   the list file, following the MAKLABEL_OPTIONS keyword line. When
   description is set to blank, "N/A" is placed in the label.

   The list file may contain blank lines as long as they are not placed
   between the lines in each of the triplets.

   Normally the kernel list files are kept in the data set root directory
   of the staging area.

   The package accompanying this document contains the
   ``examples/listfiles'' directory with numerous examples of kernel list
   files for various missions. These list files can be used as references
   or even as the starting point for preparing kernel list files for a new
   archive.

NPB Validation methods
======================

bla bla bla

Coverage Times Determination
============================
bla bla bla


NPB Logging
===========

bla bla bla


NPB Diff Files
==============



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

Orbit Number Files
==================

Bla bla bla


Meta-kernels
============

Bla bla bla


PDS Information Model
=====================

Currently NPB includes templates for IM 1.5.0.0 and IM 1.16.0.0. Bundles with
schemas versions lower than 1.16.0.0 will use 1.5.0.0 templates. Bundles
with schemas equal or greater than 1.16.0.0 will use 1.16.0.0 templates.

Remember that you are able to provide your own templates by indicating the
directory where they reside via the configuration file. Use your templates
at your own risk and make sure that they pass all PDS Validate tool checks.

Checksum files
==============

-- as policy we should strive to make archives in which no files that
had been archived are ever altered in any way after that. We could not
do this in PDS3. We can and should do this PDS4. Tools and human can
always find the latest checksum table that should be used for the whole
archive.

-- having previous checksums in the archive is also the best way to
revert to an earlier version of the archive -- just take all the files
listed in particular checksum plus the checksum itself and its label.
