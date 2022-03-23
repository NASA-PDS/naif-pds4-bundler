The MSL SPICE Data Archive
========================================================================


Introduction
============

   This document provides an overview of the MSL SPICE data set,
   including a description of the directory structure. Additional
   documents included on this data set provide more details, especially
   the ``spiceds.cat'' dataset description and the various
   kernel-specific ``/data/*/*info.txt'' files.

   This data set contains navigation and related observation geometry
   and other ancillary data in the form of SPICE System kernel files
   for the MSL rover. See the file ``mission.cat'' in the ``/catalog''
   directory for a description of the mission and the file
   ``insthost.cat'' in the same directory for a description of the
   rover.

   The SPICE kernel files contain geometric and other ancillary
   information needed to recover the full value of science instrument
   data. Data in the SPICE kernel files must be accessed using the NAIF
   (Navigation and Ancillary Information Facility) software called the
   SPICE Toolkit. See the file ``softinfo.txt'' in the ``/software''
   directory for instructions on how to obtain this software.

   This data set is contained on a single virtual volume, MSLSP_1000,
   including data from all mission phases and covering from 2011-11-26
   through the end time of the latest rover path SPK file supplied in
   the data set. Until the end of the rover lifespan this data set will
   be accumulating with new data added according to the project
   archiving plan.


File Formats
============

   All text documents and other meta information files such as
   descriptions, PDS object definitions and detached PDS labels are
   stream format files, with a carriage return (ASCII 13) and a line
   feed character (ASCII 10) at the end of the record.  This allows the
   files to be read by MS-DOS/Windows, Unix and MacOS operating
   systems.

   The data files in this data set were prepared to be used under a
   UNIX environment. Therefore all SPICE text kernel files are UNIX
   text files, with a line feed character (ASCII 10) at the end of the
   line, and all SPICE binary kernels files are UNIX binary files in
   which bit pattern structures for double precision and integer
   numbers follow the IEEE standard. While some of the data files on
   this volume can be used 'as is', converting the files to binary or
   text format native to the user's computer may be required. Refer to
   the documentation provided with the SPICE Toolkit to find out
   whether conversion is needed in each specific case.

   NAIF provides a tool (BINGO) that can convert either binary or text
   kernels from one format to another. This means that text files can
   have their line terminator changed and binary files can be converted
   to the native format of the platform of interest. For access to this
   tool, see the reference to the NAIF utilities website in the file
   ``/software/softinfo.txt''.


Volume Contents
===============

   Files on this volume are organized into a set of subdirectories
   below the top-level directory. The following table shows the
   structure and content of these directories. In this table, directory
   names are enclosed in square brackets ([]). See the ``*info.txt''
   files in each directory for specific information on the files in the
   directory, including naming schemes.


   [top-level-directory]
   |
   |-- aareadme.txt        Text version of the aareadme file.
   |-- aareadme.htm        HTML version of the aareadme file.
   |-- aareadme.lbl        PDS label for both aareadme files.
   |-- errata.txt          Comments and errata on this volume.
   |-- voldesc.cat         Description of the contents of this volume.
   |
   |--[catalog]            Directory containing PDS catalog objects.
   |  |
   |  |-- catinfo.txt      Description of files in the catalog directory.
   |  |-- insthost.cat     Description of the rover.
   |  |-- mission.cat      Description of the mission.
   |  |-- person.cat       References for personnel who created this volume.
   |  |-- ref.cat          List of publications mentioned in *.cat files.
   |  |-- release.cat      Description of the data set releases.
   |  |-- spiceds.cat      Description of the SPICE data set.
   |  |-- spice_hsk.cat    Description of housekeeping (browser) information.
   |  +-- spice_inst.cat   Description of SPICE kernels.
   |
   |--[data]               Directory containing SPICE data files (kernels.)
   |  |
   |  |--[ck]              Directory containing CK files.
   |  |  |
   |  |  |-- ckinfo.txt    Description of files in the data/ck directory.
   |  |  |-- *.bc          CK files.
   |  |  +-- *.lbl         PDS labels for CK files.
   |  |
   |  |--[ek]              Directory containing EK files.
   |  |  |
   |  |  +-- ekinfo.txt    Description of files in the data/ek directory.
   |  |
   |  |--[fk]              Directory containing FK file(s).
   |  |  |
   |  |  |-- fkinfo.txt    Description of files in the data/fk directory.
   |  |  |-- *.tf          FK file(s).
   |  |  +-- *.lbl         PDS labels for FK files.
   |  |
   |  |--[ik]              Directory containing IK files.
   |  |  |
   |  |  |-- ikinfo.txt    Description of files in the data/ik directory.
   |  |  |-- *.ti          IK files.
   |  |  +-- *.lbl         PDS labels for IK files.
   |  |
   |  |--[lsk]             Directory containing LSK files.
   |  |  |
   |  |  |-- lskinfo.txt   Description of files in the data/lsk directory.
   |  |  |-- *.tls         LSK file(s).
   |  |  +-- *.lbl         PDS labels for LSK files.
   |  |
   |  |--[pck]             Directory containing PCK file(s).
   |  |  |
   |  |  |-- pckinfo.txt   Description of files in the data/pck directory.
   |  |  |-- *.tpc         Text PCK file(s).
   |  |  +-- *.lbl         PDS labels for PCK files.
   |  |
   |  |--[sclk]            Directory containing SCLK file(s).
   |  |  |
   |  |  |-- sclkinfo.txt  Description of files in the data/sclk directory.
   |  |  |-- *.tsc         SCLK file(s).
   |  |  +-- *.lbl         PDS labels for SCLK files.
   |  |
   |  +--[spk]             Directory containing SPK files.
   |     |
   |     |-- spkinfo.txt   Description of files in the data/spk directory.
   |     |-- *.bsp         SPK files.
   |     +-- *.lbl         PDS labels for SPK files.
   |
   |--[document]           Directory containing volume related documents.
   |  |
   |  |-- docinfo.txt      Description of files in the document directory.
   |  |-- onlabels.txt     Description of PDS labels for SPICE kernels.
   |  +-- lblinfo.txt      Description of PDS label location in this volume.
   |
   |--[extras]             Directory containing extra data elements.
   |  |
   |  |-- extrinfo.txt     Description of files and directories in extras.
   |  |
   |  +--[mk]              Directory containing meta-kernels.
   |     |
   |     |-- mkinfo.txt    Description of meta-kernel files.
   |     +-- *.tm          Meta-kernel files.
   |
   |--[index]              Directory containing index files.
   |  |
   |  |-- indxinfo.txt     Description of files in the index directory.
   |  |-- checksum.tab     Table of MD5 checksums for files in this data set.
   |  |-- checksum.lbl     PDS label for checksum.tab file.
   |  |-- index.tab        Index table of SPICE kernels on this volume.
   |  +-- index.lbl        PDS label for index.tab file.
   |
   +--[software]
      |
      +-- softinfo.txt     Instructions on how to obtain SPICE software.


Whom to Contact for Information
===============================

   PDS Navigation and Ancillary Information Facility (NAIF),
   MAIL STOP 301-121
   Jet Propulsion Laboratory
   California Institute of Technology
   4800 Oak Grove Drive
   Pasadena, CA, 91109-8099
   818-354-3869
   WWW Site:  http://naif.jpl.nasa.gov
   Electronic mail address:  pds_operator@naif.jpl.nasa.gov


Cognizant Persons
=================

   This volume was produced by Boris Semenov and Marc Costa Sitja,
   Planetary Data System Navigation and Ancillary Information
   Facility Node, Jet Propulsion Laboratory, Pasadena, California.

   The kernel files and source data for making kernels in this data set
   were provided by Steven Collins, MSL ACS Team; Tomas Martin-Mur and
   Eric Gustafson, MSL NAV Team; Fred Serricchio, MSL EDL Team; Bob
   Deen, Stirling Algermissen, Helen Mortensen, and Michael Gangl, MSL
   OPGS Team; and Justin Maki, MSL Camera Team.
