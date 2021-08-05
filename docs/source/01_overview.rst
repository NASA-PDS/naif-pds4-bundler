***********************************
NAIF PDS4 Bundle Generator overview
***********************************

The NAIF Development Toolkit (NPB) has been designed to support the following
processes:

   * Automatic generation of a NAIF compliant lesson's FTM file from the
     lesson' solutions source code, using the associated meta-kernels and
     kernels set. :ref:`AC2LP` provides further details.

   * Automatic processing of the Examples section of a SPICE source header
     file.  This processing includes the extraction, insertion and/or
     validation of full examples code for SPICELIB, CSPICE, ICY and MICE.
     Please refer to :ref:`AHEP` for further details.

   * Automatic translation of SPICE headers from SPICELIB or CSPICE source
     files to all other NAIF supported languages (CSPICE, from SPICELIB;
     SPICELIB, from CSPICE; and Icy/Mice from both).  Please refer to
     :ref:`ASHT` for further details.

   * Automatic conversion of SPICE code examples, from SPICELIB or CSPICE, to
     all other NAIF supported languages (CSPICE, from SPICELIB; SPICELIB,
     from CSPICE; and Icy/Mice from both).  Please refer to :ref:`EC2` for
     further details.

Prerequisites
=============
In order to run the NAIF PDS4 Bundle Generator, the following software must be
available on the user's machine:

   - Python 3.5 (or higher)
   - SpiceyPy
   - beautifulsoup4>=4.9.3
   - NumPy
   - SetupTools
   - Coverage
   - HTML-testRunner

Installation and setup
======================
In order to run the NAIF Development Toolkit from any location, the environment
variable PYTHONPATH must be properly set to the directory where the NDT
distribution is available. If the NDT has been deployed on::

   /local/user/NDT

then, the source file should has the PYTHONPATH environment variable pointing
to the /local/user directory::

   export PYTHONPATH=$PYTHONPATH:/local/user/NDT

or::

   setenv PYTHONPATH "/local/user/NDT"

Other useful aliases and required environment variables are::

   alias ac2lp.py 'python3.5 /local/user/ndt/ndt/ac2lp.py'
   setenv MATLABPATH "/naif/mice/lib:/naif/mice/src/mice"

Some IDL/Icy lessons or code examples may require the use additional IDL
scripts. Such scripts define constant expressions (similar to include or
header files in other languages) or alter the capabilities of an interface
routine.  In order to use such scripts, set the IDL_PATH environment
variable to the directory containing the Icy script files::

   setenv IDL_PATH "/naif/icy/src/icy:<IDL_DEFAULT>"


Should Octave be the software selected for executing Matlab code, Mice
would need to be (re-)compiled following the instructions listed in the
Mice required reading section "Use of Mice with Octave." Once Mice is
ready for Octave, the octave path shall be configured.  In order to not
use the "addpath" command every time a script is executed, run Octave
from the command line and execute the following **octave commands**::

    >> addpath('/naif/mice/lib/octave')
    >> addpath('/naif/mice/src/mice' )
    >> savepath
    >> exit

These commands will create/update the ".octaverc" file (which will be
located in the user's home directory). This file is loaded by default
every time octave is executed, and it will make Mice readily available
to the user and the NDT without the need for running the "addpath"
commands.

Kernel List Configuration
=========================



The pattern tags from the kernel list configuration can have three
different behaviors:

   * Keyword $KERNEL is present in the description.

   * Keyword information is extracted from the filename.

   * Keyword information is directly provided in the configuration
     file.

The three types can be present in a description.

The keyword $KERNEL corresponds to the complete kernel file nam. This
typically happens when the archived kernel file name is different from
the original kernel name. For example the InSight SCLK used in operations
is NSY_SCLKSCET.[0-9][0-9][0-9][0-9][0-9].tsc whereas is archvied as
nsy_sclkscet_[0-9][0-9][0-9][0-9][0-9].tsc; sometimes the description of
these kernels will include the original name of the file.

When the Keyword information is extracted from the filename then
the tag has the attribute pattern="kernel", the value of the tag will
include the tag name with a dollar sign in the relevant position of the
regular expression pattern to match the kernel name.

When the keyword information is provided directly via configuration
then the tag present is value and is equal to the kernel name that
provides a given value to the tag.

Kernel mapping only happens if the kernel is provided in the input plan
with the archived name; not with the original name of the file.

Requirements
============

The KERNEL pattern in the kernel list configuration can only incude the []
metacharacter to describe a character at a time; the number of occurences
cannot be specified in any other way (for example with {}).

If the number of characters for a given character set is not known in advance
then multiple entries in the kernel list should be used in the configuration
file. For example, if you do not know whether you will have one of the
following files:

    * msl_76_sclkscet_refit_j5.tsc
    * msl_76_sclkscet_refit_k13.lbl

Then the two entries specified hereunder must be provided in the kernel list:

``<kernel pattern="msl_76_sclkscet_refit_[a-z][0-9].tsc"> (...)``
``<kernel pattern="msl_76_sclkscet_refit_[a-z][0-9][0-9].tsc"> (...)``

Remember meta-kernels are ignored if provided with the kernel list.

For metakernels this does not work: insight_$YEAR$VERSION.tm


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

    <File>
      <file_name>$FILE_NAME</file_name>
      <creation_date_time>$CURRENT_TIME</creation_date_time>
      <file_size unit="byte">$FILE_SIZE</file_size>
      <md5_checksum>$FILE_CHECKSUM</md5_checksum>
    </File>

the template should contain:

    <File>
      <file_name>$FILE_NAME</file_name>
      <creation_date_time>$PRODUCT_CREATION_TIME</creation_date_time>
      <file_size unit="byte">$FILE_SIZE</file_size>
      <md5_checksum>$FILE_CHECKSUM</md5_checksum>
    </File>


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

Configuration
=============

Configuration file

The value of PREC, the number of digits used
to report fractional seconds, must be
non-negative.  The value input was #.'

Fractional seconds, or for Julian dates, fractional
                  days, are rounded to the precision level specified
                  by the input argument PREC.


Multiple spacecrafts and mutliple targets. NPB incorporates the possibility to
have mutliple spacecrafts and targets in a Bundle. This is provided via 
configuration. If so, the default spacecraft will be the primary spacecraft
which is specified in the configuration file. Otherwise it needs to be 
specified in the Kernel List section of the configuration file. The non-kernels
bundle products will include all the targets and all the spacecrafts in the 
labels.

Please note that specifying secondary targets and spacecrafts is not a requirement
and it is valid to only include the primary spacecraft and target and label oll the
products in such  a way (for example MAVEN). This is especially convenient for 
these missions that clearly have a spacecraft or target that is clearly identifiable
as main. For other mission such as BepiColombo it is mandatory to include two 
spacecrafts, given that the relevance of the two spacecrafts is of the same order
and the mission cannot be uniquely identified with one of them. 


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

Tests
=====

Run tests with

coverage run -m nose --cover-package=.

under naif-pds4-bundle/npb

