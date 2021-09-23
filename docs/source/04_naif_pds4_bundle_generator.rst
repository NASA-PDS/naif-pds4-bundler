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

All files that are to have labels generated must have a NAIF
file ID word as the first "word" on the first line of the
file.The SPICE binary kernel files are guaranteed to have
this ID word, but the ASCII text kernels, IK, LSK, PCK, SCLK,
are not. for completeness, the appropriate ID words are listed
here, so that they may be inserted into the ASCII text kernel
files if necessary.

        ASCII Text File Type      ID Word
        --------------------      --------
        IK                        KPL/IK
        LSK                       KPL/LSK
        PCK                       KPL/PCK
        SCLK                      KPL/SCLK
        FRAMES                    KPL/FK

When no list is provided as an input, the mapping of kernel does not occur and
the kernels present in the kernels directories need to have their final names
(and therefore they should not be expected to be mapped).


The value of PREC, the number of digits used
to report fractional seconds, must be
non-negative.  The value input was #.'

Fractional seconds, or for Julian dates, fractional
                  days, are rounded to the precision level specified
                  by the input argument PREC.


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