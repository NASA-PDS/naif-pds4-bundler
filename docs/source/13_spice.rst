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
alignments, data specifiying target body size, shape and orientation,
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
   routine FURNSH.
