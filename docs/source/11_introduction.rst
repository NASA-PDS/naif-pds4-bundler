Applicability
=============

This document is written for anyone who will be preparing a new or
augmented SPICE data archive for submission to the NAIF Node of the PDS.
However, following the standards and procedures provided in this document
is highly encouraged for any entity involved in archiving SPICE ancillary
data at some other archive facility.


Motivation
==========

This document should be seen as something more than a user's software guide
since it describes the whole process to prepare SPICE archives and it also
describes the NAIF approach to using PDS4 standards in great detail (These
are the standards adopted by the consortium of agencies comprising the
International Planetary Data Alliance.) Some of the standards may seem rather
"picky" or unnecessary, and indeed there are a few items included that are not
currently used/useful. But adhering to all of these details is critical to the
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


NAIF's Approach to SPICE Kernel Archive Preparation
===================================================

NAIF's approach to creating SPICE kernel archives can be summarized by this
statement:

**All SPICE data for a given mission are archived as UNIX text and binary
files in a single, accumulating archive on a single virtual volume having
the same directory structure, the same set of meta information files, data
file labels with the same structure, and archive documents with the same
structure as all SPICE archives produced by NAIF.**

Each time that an accumulating archive is released we either refer this to
a release of the archive or to an archive increment. In this document you
will find both terms used interchangeably.


How to Read This Document?
==========================

We are glad that you got this far, but you’ve got a ways to go.
You might not have to look into each section of this document.
If you already know about SPICE you can skip the rest of this chapter. If
you are very familiar with PDS SPICE kernel archives you can skip the
:ref:`20_spice_kernel_archive_description:SPICE Kernel Archive Description`
chapter and jump directly to
:ref:`30_spice_kernel_archive_preparation_guide:SPICE Kernel Archive Preparation Guide`.

Needless to say, the chapter
:ref:`50_api_docs:Modules, Classes, and Functions Documentation`
dedicated to the description of functions and
modules is aimed at potential contributors to the further development of this
NPB software package, if you are not planning to do so, don't bother to take a
look at that chapter.


A Very Brief Introduction to SPICE
==================================

The SPICE (Spacecraft Planets Instrument C- Matrix Events) information
system uses ancillary data to provide solar system geometry information
to scientists and engineers for planetary missions in order to plan and
analyze scientific observations from space-born instruments.

A SPICE archive includes the complete set of SPICE data files
(kernel files) for a given mission, which can be accessed using SPICE
software. The SPICE data contain geometric and other ancillary information
needed to recover the full value of science instrument data. In particular
SPICE kernels provide spacecraft and planetary ephemerides,
spacecraft and instrument orientation, instrument mounting
alignments, data specifying target body size, shape and orientation,
and data needed for relevant time conversions. Data in
SPICE kernel files must be accessed using the software called
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
Each subdirectory contains one specific kernel type; those types are briefly
described here.

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

A SPICE archive contains one additional subdirectory holding meta-kernels,
described here.

 * **MK** (Meta-Kernel) files list sets of related SPICE kernels that
   should be used together, providing an easy way to make data from
   these kernel sets available to a SPICE-based application by loading
   meta-kernels into the program using the high level SPICE data loader
   routine ``FURNSH``.
