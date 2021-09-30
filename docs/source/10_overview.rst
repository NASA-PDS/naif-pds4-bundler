********
Overview
********

This document is a piece of the NAIF PDS4 Bundler package (NPB)
that NAIF enables SPICE archive producers to understand, design,
and generate a Planetary Data System (PDS) SPICE archive from end
to end.


Applicability
=============

This document is written for anyone who will be preparing a new or
augmented SPICE data archive either for submission to the NAIF Node of the PDS.
However, following the standards and indications provided in this document
is highly encouraged for any entity involved in archiving SPICE ancillary
data at some other archive facility.


Motivation
==========

This document should be seen as something more than a user software guide since
it describes the whole process to prepare SPICE archives and it also
describes the NAIF approach to PDS standards in great detail (These
are the standards adopted by the consortium of agencies comprising the
International Planetary Data Alliance.) Some of the standards may seem rather
"picky" or unnecessary, and indeed there are a few items included that are not
really used/useful. But adhering to all of these details is critical to the
current and future use of archived SPICE data, especially to achieve
interoperability across national archives, and, to facilitate use of archived
SPICE data in data search, retrieval and processing tools that are, or will be,
part of archive systems.

It is imperative that archive preparers carefully check and re-check all
components of an archive -- whether it is a new one or an augmentation
to an existing one -- before it is submitted for ingestion. NAIF
through the NAIF PDS4 Bundler package and this document, provides
guidance, recommendations, and tools to generate and to validate
the archives. These can help a great deal, but there is much that only the
archive preparer can do.


Code of Conduct
===============

All users and developers of the NASA-PDS software are expected to abide by our
`Code of Conduct <https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md>`_.
Please read this to ensure you understand the expectations of our community.


NAIF's Approach to SPICE Kernel Archive Preparation
===================================================

NAIF's approach to creating SPICE kernel archives can be summarized by this
statement:

**All SPICE data for a given mission are archived as UNIX text and binary
files in a single, accumulating data set on a single virtual volume having
the same directory structure, the same set of meta information files, data
file labels with the same structure, and archive documents with the same
structure as all SPICE archives produced by NAIF.**

Each time that an accumulating data set is released we either refer this to
a release of the archive or to an archive increment. In this document you
will find both terms used interchangeably.


How to Read This Document?
==========================

We are glad that you got this far, unfortunately you are still a long way
to go. You might not have to look into each section of this document. In fact
if you already know about SPICE you can skip the rest of this chapter. If
you are very familiar with PDS SPICE kernel archives you can skip the
:ref:`source/20_spice_kernel_archive_description:SPICE Kernel Archive Description`
chapter and jump directly to
:ref:`source/30_spice_kernel_archive_preparation_guide:SPICE Kernel Archive Preparation Guide`.

Needless to say, the chapter
:ref:`source/50_api_docs:Functions and Modules Documentation`
dedicated to the description of functions and
modules are aimed to potential contributors to the development of the
software package, if you are not planning to do so, don't bother to take a look
at the chapter.


A Very Brief Introduction to SPICE
==================================

The SPICE (Spacecraft Planets Instrument C- Matrix Events) information
system uses ancillary data to provide Solar System geometry information
to scientists and engineers for planetary missions in order to plan and
analyze scientific observations from space-born instruments.

A SPICE archive includes the complete set of SPICE data files
(kernel files) for a given mission, which can be accessed using SPICE
software. The SPICE data contain geometric and other ancillary information
needed to recover the full value of science instrument data. In particular
SPICE kernels provide spacecraft and planetary ephemerides,
spacecraft and instrument orientation, instrument mounting
alignments, and data needed for relevant time conversions. Data in
the SPICE kernel files must be accessed using the software called
the SPICE Toolkit produced and distributed by the Navigation and
Ancillary Information Facility (NAIF) Node of the Planetary Data
System.

The SPICE toolkit is available in FORTRAN, C at the
`NAIF web site <https://naif.jpl.nasa.gov>`_.
Interfaces to higher-level data analysis software in the Interactive Data
Language (IDL), Matlab and JAVA are also provided. There are several other
wrappers amongst which we highlight the Python wrapper SpiceyPy.


SPICE Kernels Organization
--------------------------

SPICE kernels in a SPICE archive are grouped into a set of subdirectories.
Each subdirectory contains different SPICE kernel types that are used to
store different kinds of ancillary data. These kernel types are briefly
described hereunder.

 * **SPK** (Spacecraft Planet Kernel) files contain ephemerides (position
   and velocity) for spacecraft, planets, satellites, comets and
   asteroids as well as for moving or fixed spacecraft and instrument
   structures.

 * **PCK** (Planetary Constants Kernel) files contain certain physical,
   dynamical and cartographic constants for target bodies, such as size
   and shape specifications, and orientation of the spin axis and prime
   meridian.

 * **IK** (Instrument Kernel) files contain instrument parameters relevant
   for computing an instrument's geometry such as field-of-view
   definitions, CCD and optical distortion characteristics, and internal
   timing parameters.

 * **CK** (C-matrix Kernel) files contain time varying orientations for
   spacecraft, spacecraft structures, and articulating science
   instruments.

 * **LSK** (Leapseconds Kernel) files contain the leapseconds and the
   values of other constants required to perform a transformation
   between Universal Time Coordinated (UTC) and Ephemeris time (ET),
   which is also known as Barycentric Dynamical Time (TDB).

 * **SCLK** (Spacecraft Clock Kernel) files contain on-board clock
   calibration data required to perform a transformation between
   Ephemeris time (ET) and spacecraft on-board time (SCLK).

 * **FK** (Frame definitions Kernel) files contain information required to
   define reference frames, sources of frame orientation data and
   connections between these frames and other frames supported within
   the SPICE system. The science instrument frame definitions provided
   in the FK files include mounting alignment information for the
   instruments.

 * **DSK** (Digital Shape Kernel) files contain detailed shape models for
   extended objects such as planets, natural satellites, asteroids, and
   comet nuclei.

 * **MK** (Meta-Kernel) files list sets of related SPICE kernels that
   should be used together, providing an easy way to make data from
   these kernel sets available to a SPICE-based application by loading
   meta-kernels into the program using the high level SPICE data loader
   routine FURNSH.


Reporting Bugs
==============

In order to report a bug either in this document or the NAIF PDS4 Bundler
software package you can open a issue in the ``naif-pds4-bundler`` `GitHub
repository Issues section <https://github.com/NASA-PDS/naif-pds4-bundler/issues>`_.

Click on the "New issue" button and follow the instructions provided in the
issue template.


Contact Information
===================

If you have any questions on any aspect of the generation
of a SPICE kernel archive please contact Marc Costa Sitja (Marc.Costa.Sitja@jpl.nasa.gov)

at the

     **PDS Navigation and Ancillary Information Facility (NAIF)**,
     MAIL STOP 301-121,
     Jet Propulsion Laboratory,
     California Institute of Technology,
     4800 Oak Grove Drive,
     Pasadena, CA, 91109-8099

     WWW Site: https://naif.jpl.nasa.gov


References
==========

.. [PDS4STD] Planetary Data System Standards Reference, Version 1.16.0
             April 21, 2021, Jet Propulsion Laboratory, California Institute of
             Technology Pasadena, California

.. [PDS3GUIDE] PDS Navigation and Ancillary Information Facility (NAIF)
             `SPICE Archive Preparation Guide <https://naif.jpl.nasa.gov/pub/naif/pds/doc/archiving_guide/spice_archiving_guide.txt>`_

.. [KERNELS] PDS Navigation and Ancillary Information Facility (NAIF)
             `Introduction to Kernels Tutorial<https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Tutorials/pdf/individual_docs/12_intro_to_kernels.pdf>`_

.. [MAKLABEL] PDS Navigation and Ancillary Information Facility (NAIF)
             `MAKLABEL Users's Guide <https://naif.jpl.nasa.gov/pub/naif/utilities/MacIntel_OSX_64bit/maklabel.ug>`_

.. [SPICEYPY] Annex et al., (2020). SpiceyPy: a Pythonic Wrapper for the SPICE
              Toolkit. Journal of Open Source Software, 5(46), 2050,
              https://doi.org/10.21105/joss.02050


Utility Programs
----------------

The executables and User's Guides for the following utility programs::

   ARCHTYPE  BINGO     BRIEF     CKBRIEF   CKSLICER  CKSMRG
   COMMNT    DAFCAT    MAKLABEL  ORBNUM    SPACIT    SPKDIFF
   SPY       BFF       FRMDIFF   OPTIKS

mentioned in this document are available from the "Utilities" page on
the NAIF web site, `NAIF Utilities <https://naif.jpl.nasa.gov/naif/utilities.html>`_

Note that for some environments (e.g. Linux, Mac/OSX) these utilities
can not be statically linked and require certain shared object libraries
in order to run. Usually these libraries can be installed on your
computer by installing the compiler used to compile the executables
(e.g. gfortran/gcc).


Tutorials
---------

A collection of tutorials covering most aspects of using SPICE kernel
files and allied Toolkit software is available from the "Tutorials"
page on the NAIF web site, `NAIF Tutorials <https://naif.jpl.nasa.gov/naif/tutorials.html>`_.


SPICE Kernel Archives
---------------------

Archived SPICE archives are available on the NAIF server either directly,
from the `FTP-like HTTP page <https://naif.jpl.nasa.gov/pub/naif/pds/pds4/>`_,
or from the `NAIF Data page <https://naif.jpl.nasa.gov/naif/data_archived.html>`_.

They are useful as examples.


PDS Standards
-------------

The PDS standards Documents are available on the PDS documents web site,
`PDS4 web site Data Standards <https://pds.nasa.gov/datastandards/documents/>`_
among them the following might be more useful:

   * Concepts Document
   * Data Provider's Handbook
   * Standard's Reference
   * Context Products


PDS Validate Tool
-----------------

The PDS Validate tool is available at the
`validate tool documentation <https://nasa-pds.github.io/validate/>`_.
