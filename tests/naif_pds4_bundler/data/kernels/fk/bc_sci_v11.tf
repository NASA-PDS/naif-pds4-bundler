KPL/FK

Frame (FK) SPICE kernel file for BepiColombo-specific Science frames
=============================================================================

   These frames are sorted in two groups: those that are BepiColombo mission
   specific and those that are Mercury generic. The first group contains the
   frames defined by and for the BepiColombo mission, while the second
   provides the frames that are commonly accepted by the scientific
   community for Mercury.

   The IAU body-fixed rotational frames for Mercury and Venus is an exception
   to this grouping, as they are provided in a separate PCK kernel file.

   This kernel also contains NAIF ID/name mapping for the MPO science frames
   ephemeris objects (see the last section of the file).


Version and Date
-------------------------------------------------------------------------------

   Version 1.1 -- June 8, 2022 -- Alfredo Escalante Lopez, ESAC/ESA

      Fixed typos for PDS4 Bundle release version 1.0 and updated
      contact information.

   Version 1.0 -- September 21, 2021 -- Ricardo Valles Blanco, ESAC/ESA
                                        Marc Costa Sitja, ESAC/ESA

      Corrected BC_MSO_AB reference frame angles and typos,
      updated References section, fixed some typos and updated contact
      information.

   Version 0.9 -- June 14, 2021 -- Alfredo Escalante Lopez, ESAC/ESA

      Corrected BC_MSM reference frame origin to new BC_MSM ephemeris
      object (shifted 479 km North).

   Version 0.8 -- October 26, 2020 -- Alfredo Escalante Lopez, ESAC/ESA
                                      Marc Costa Sitja, ESAC/ESA

      Fixed issue with repeated IDs for different frames.

   Version 0.7 -- September 22, 2020 -- Marc Costa Sitja, ESAC/ESA
                                        Johannes Z. D. Mieth, TU Braunschweig

      Updated BepiColombo Geocentric Solar Magnetospheric (BC_GSM) with
      latest IGRF model.

   Version 0.6 -- April 3, 2020 -- Marc Costa Sitja, ESAC/ESA

      Updated BepiColombo Geocentric Solar Magnetospheric frame description.

   Version 0.5 -- November 13, 2019 -- Marc Costa Sitja, ESAC/ESA

      Changed the Frames IDs to avoid clash with MPO Solar Array IDs.

   Version 0.4 -- April 9, 2018 -- Marc Costa Sitja, ESAC/ESA

      Recovered Mercury Mean Equator at J2000 Frame which had been left out.
      Updated IDs for several frames.

   Version 0.3 -- February 12, 2018 -- Marc Costa Sitja, ESAC/ESA

      General update following the indications of the Hermean Environment
      Working Group (HEWG).

   Version 0.2 -- June 20, 2017 -- Marc Costa Sitja, ESAC/ESA

      Added Mercury Solar Magnetospheric frame and Mercury Orbital generic
      frame. Updated some definitions and file outline.

   Version 0.1 -- July 04, 2016 -- Marc Costa Sitja, ESAC/ESA

      Updated BEPICOLOMBO MPO IDs from -69 to -121.

   Version 0.0 -- February 26, 2015 -- Boris Semenov, NAIF

      Initial version.


References
-------------------------------------------------------------------------------

   1. ``Frames Required Reading'', NAIF.

   2. ``Kernel Pool Required Reading'', NAIF.

   3. pck00009.tpc, based on IAU 2006 constants

   4. pck00010.tpc, based on IAU 2009 constants

   5. MERCURY_MME/999999 frame definition provided by Dr. Jonathan
      McAuliffe, ESA, 20 Feb 2015

   6. Planetary Fact Sheets - Mercury Fact Sheet,
      David R. Williams, NASA Goddard Space Flight Center
      https://nssdc.gsfc.nasa.gov/planetary/factsheet/mercuryfact.html
      Accessed on 12th February 2018

   7. E-Mail ``BepiColombo SPICE GSM frame'' from Johannes Z. D. Mieth
      on 12th March 2020.

   8. ``Magnetic North, Geomagnetic and Magnetic Poles'', World Data Center
      for Geomagnetism, Kyoto,
      http://wdc.kugi.kyoto-u.ac.jp/poles/polesexp.html

   9. ``Steady-state field-aligned currents at Mercury'', B. Anderson. 2014.

  10. NASA/Marshall Solar Physics:
      http://solarscience.msfc.nasa.gov/SolarWind.shtml


Contact Information
-----------------------------------------------------------------------------

   If you have any questions regarding this file contact the
   ESA SPICE Service (ESS) at ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           spice@sciops.esa.int

   or NAIF at JPL:

           Boris Semenov
           +1 (818) 354-8136
           Boris.Semenov@jpl.nasa.gov


Implementation Notes
-----------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make use
   of this frame kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool". The SPICELIB
   routine FURNSH loads a kernel into the pool as shown below:

     FORTRAN: (SPICELIB)

       CALL FURNSH ( frame_kernel_name )

     C: (CSPICE)

       furnsh_c ( frame_kernel_name );

     IDL: (ICY)

       cspice_furnsh, frame_kernel_name

     MATLAB: (MICE)

       cspice_furnsh ( 'frame_kernel_name' )

     PYTHON: (SPICEYPY)*

       furnsh( frame_kernel_name )

   In order for a program or routine to extract data from the pool, the
   SPICELIB routines GDPOOL, GIPOOL, and GCPOOL are used.  See [2] for
   more details.

   This file was created and may be updated with a text editor or word
   processor.

   * SPICEYPY is a non-official, community developed Python wrapper for the
     NAIF SPICE toolkit. Its development is managed on Github.
     It is available at: https://github.com/AndrewAnnex/SpiceyPy


BepiColombo Science Frames names and NAIF ID Codes
-------------------------------------------------------------------------------

   The following BepiColombo science frames are defined in this kernel file:

      SPICE Frame Name             Long-name
      --------------------------   ------------------------------------------

   Mercury based frames for the in-orbit phase(**):

      BC_MSO                       Mercury-Centric Solar Orbital
      BC_MSO_AB                    Mercury-Centric Solar Orbital Aberrated
      BC_MSM                       Mercury-Centric Solar Magnetospheric
      BC_MBF                       Mercury Body Fixed
      BC_MME_IAU2006_OF_DATE       Mean Mercury Equator and IAU vector of date
                                   using IAU 2006 Mercury rotation constants
      BC_MME_IAU2006_J2000         BC_MME_IAU2006_OF_DATE frame frozen at
                                   J2000 TDB
      BC_MME_IAU2009_OF_DATE       Mean Mercury Equator and IAU vector of date
                                   using IAU 2009 Mercury rotation constants
      BC_MME_IAU2009_J2000         BC_MME_IAU2009_OF_DATE frame frozen at
                                   J2000 TDB

   Sun based frames for the interplanetary cruise phase:

      BC_MPO_RTN                   MPO Radial-Tangential-Normal Heliocentric
      BC_MMO_RTN                   MMO Radial-Tangential-Normal Heliocentric

   Earth based frames for the interplanetary cruise flybys:

      BC_GSE                       Geocentric Solar Ecliptic
      BC_GSM                       Geocentric Solar Magnetospheric

   Venus based frames for the interplanetary cruise flybys:

      BC_VSO                       Venus Solar Orbital


   (**) These frames are commonly used by other missions for data analysis
        and scientific research. In the future NAIF may include some of them
        in their official generic frames kernel for the Jupiter system.
        When this happens the frames will be removed from this kernel.


   These frames have the following centers, frame class and NAIF
   IDs:

      SPICE Frame Name              Center      Class    NAIF ID
      --------------------------    ----------  -------  ----------
      BC_MSO                        MERCURY     DYNAMIC     -121931
      BC_MSO_AB                     MERCURY     FIXED       -121932
      BC_MSM                        MERCURY     DYNAMIC     -121933
      BC_MBF                        MERCURY     FIXED       -121934
      BC_MME_IAU2006_OF_DATE        MERCURY     DYNAMIC     -121941
      BC_MME_IAU2006_J2000          MERCURY     FIXED       -121942
      BC_MME_IAU2009_OF_DATE        MERCURY     DYNAMIC     -121943
      BC_MME_IAU2009_J2000          MERCURY     FIXED       -121944
      BC_MPO_RTN                    SUN         DYNAMIC     -121951
      BC_MMO_RTN                    SUN         DYNAMIC     -121952
      BC_GSE                        EARTH       DYNAMIC     -121961
      BC_GSM                        EARTH       DYNAMIC     -121962
      BC_VSO                        VENUS       DYNAMIC     -121971

   The keywords implementing these frame definitions are located in the
   section "Frame Definitions."


General Notes About This File
-------------------------------------------------------------------------------

   About Required Data:
   --------------------
   Most of the dynamic frames defined in this file require at least one
   of the following kernels to be loaded prior to their evaluation,
   normally during program initialization:

      -  Planetary ephemeris data (SPK), i.e. de403, de405, etc;
      -  Planetary constants data (PCK);
      -  Earth generic frames definitions (FK).

   Note that loading different kernels will lead to different
   orientations of the same frame at a given epoch, providing different
   results from each other, in terms of state vectors referred to these
   frames.


   About Implementation:
   ---------------------
   The SPICE frames defined within this file and their corresponding
   references in literature might not be equivalent, both due to
   variations in the SPICE kernels on which the SPICE frame depends,
   and due to possible differences in both the frame's definition and
   implementation (e.g. GSE can be defined using the instantaneous
   orbital plane or mean ecliptic; the mean ecliptic is a function of
   the ecliptic model). Please refer to each applicable frame
   description section for particular details on the current SPICE
   kernel implementation.


Frame Definitions
-------------------------------------------------------------------------------

   This section contains the definitions of the Mercury Science frames.

Mercury Based Frames
-------------------------------------------------------------------------------

   These dynamic frames are used for analyzing data in a reference
   frame tied to the dynamics of Mercury.


BepiColombo Mercury-centric Solar Orbital frame (BC_MSO)
------------------------------------------------------------------------

   Definition:
   -----------

   The Mercury-centric solar orbital frame is defined as follows:

      -  +X axis is the position of the Sun relative to
         Mercury; it's the primary vector and points
         from Mercury to Sun;

      -  +Y axis is the component of the inertially referenced
         velocity of Sun relative to Mercury orthogonal
         to the +X axis;

      -  +Z axis completes the right-handed system;

      -  the origin of this frame is the center of mass of
         Mercury.

   All vectors are geometric: no corrections are used.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector. Therefore, the ephemeris data required to compute the
   Mercury-Sun vector in J2000 reference frame have
   to be loaded before using this frame.

   The secondary vector is defined as an 'observer-target velocity'
   vector. Therefore, the ephemeris data required to compute the
   Mercury-Sun velocity vector in the J2000 reference frame
   have to be loaded before using this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Mercury, Sun and the Sun Barycenter
   will lead to a different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   MERCURY_SUN_ORB using de405 ephemerides.


   \begindata

      FRAME_BC_MSO                  = -121931
      FRAME_-121931_NAME            = 'BC_MSO'
      FRAME_-121931_CLASS           =  5
      FRAME_-121931_CLASS_ID        =  -121931
      FRAME_-121931_CENTER          =  199
      FRAME_-121931_RELATIVE        = 'J2000'
      FRAME_-121931_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121931_FAMILY          = 'TWO-VECTOR'
      FRAME_-121931_PRI_AXIS        = 'X'
      FRAME_-121931_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-121931_PRI_OBSERVER    = 'MERCURY'
      FRAME_-121931_PRI_TARGET      = 'SUN'
      FRAME_-121931_PRI_ABCORR      = 'NONE'
      FRAME_-121931_SEC_AXIS        = 'Y'
      FRAME_-121931_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-121931_SEC_OBSERVER    = 'MERCURY'
      FRAME_-121931_SEC_TARGET      = 'SUN'
      FRAME_-121931_SEC_ABCORR      = 'NONE'
      FRAME_-121931_SEC_FRAME       = 'J2000'

   \begintext


BepiColombo Mercury-centric Solar Orbital Aberrated frame (BC_MSO_AB)
---------------------------------------------------------------------

   Definition:
   -----------

   The Mercury-centric solar orbital aberrated frame is defined as follows:

      -  +Z is perpendicular to the orbital plane of Mercury and is
         positive towards North;

      -  +X axis is the component of the solar wind direction vector
         that is orthogonal to the +Z-axis. This axis lies in the
         orbital plane of Mercury and is positive in the direction
         opposite to the solar wind;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of Mercury.


   Remarks:
   --------

   A critical issue to consider in the definition of this
   frame is aberration - the bow shock of Mercury is rotated in
   the plane of the orbit of Mercury by angle Vplanet/Vsolar_wind,
   where Vplanet is the velocity of Mercury in its orbit and
   Vsolar_wind is the solar wind speed. The sense of rotation is
   such the bow shock lags its un-rotated location on the anti-sunward
   side of Mercury. This is the +Y direction for Mercury-centric solar
   orbital frame (BC_MSO). Strictly speaking Vplanet should
   be the component perpendicular to the solar wind.

   Th solar wind streams off of the Sun in all directions at speeds
   of about 400 km/s. Nevertheless, the solar wind is not uniform.
   Although it is always directed away from the Sun, it changes speed
   and carries with it magnetic clouds, interacting regions where high
   speed wind catches up with slow speed wind, and composition
   variations. The solar wind speed can range from high (800 km/s) over
   coronal holes to low velocities (300 km/s) over streamers
   (see [10]).

   Mercury's orbital velocity ranges from 58.98 km/s to 38.86 km/s with an
   average of 47.36 km/s (see [6]).

   For Mercury under normal solar wind conditions (v ~400 km/s) the
   angle of aberration ranges from 8.4483 degrees for the maximum
   orbital velocity to 5.5663 degrees for the minimum orbital
   velocity of Mercury.

   By convention, the average velocity for Mercury in its orbit and for
   the solar wind at Mercury will be used in the definition of this
   frame, which is highly significant for determining magnetopause and
   bow shock locations. This value is determined to be 6.7523 degrees.

   Since the minimum aberration is of approximately 2.7810 degrees
   (maximum solar wind and minimum Mercury orbital velocities) and
   the maximum aberration is of approximately 11.1225 degrees (minimum
   solar wind and maximum Mercury orbital velocities), the error in
   the definition of the +X-axis direction is between -3.9713 to
   4.3702 degrees.

   This frame is defined relative to BC_MSO, which is dynamic. This aspect
   shall be taken into account if/when using this frame to define other
   dynamic frames. For further details, please refer to [1].

   \begindata

      FRAME_BC_MSO_AB            = -121932
      FRAME_-121932_NAME         = 'BC_MSO_AB'
      FRAME_-121932_CLASS        =  4
      FRAME_-121932_CLASS_ID     = -121932
      FRAME_-121932_CENTER       =  599
      TKFRAME_-121932_SPEC       = 'ANGLES'
      TKFRAME_-121932_RELATIVE   = 'BC_MSO'
      TKFRAME_-121932_ANGLES     = (   -6.7523,  0.0,  0.0 )
      TKFRAME_-121932_AXES       = (         3,    2,    3 )
      TKFRAME_-121932_UNITS      = 'DEGREES'

   \begintext


BepiColombo Mercury-centric Solar Magnetospheric (BC_MSM)
------------------------------------------------------------------------

   Definition:
   -----------

   The Mercury-centric solar magnetospheric frame is defined as follows:

      - +Z axis is the projection of the Mercury magnetic dipole axis
        (positive north) on to the plane perpendicular to the +X axis.

      -  +X axis is the position of the Sun relative to Mercury;
         it's the primary vector and points from Mercury to Sun;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of
         Mercury.

   All vectors are geometric: no corrections are used.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector. Therefore, the ephemeris data required to compute the
   Mercury-Sun vector and MSM origin in J2000 reference frame have
   to be loaded before using this frame. Note that the origin of
   the MSM frame is shifted 479 km northward along spin axis [9].

   Note that this frame requires the following SPK file in order to
   obtain the position of the BC_MSM point/center:

         bc_sci_vNN.bsp

            where

               NN         version of the kernel

   The secondary vector is defined as an 'observer-target velocity'
   vector. Therefore, the ephemeris data required to compute the
   Mercury-Sun velocity vector in the J2000 reference frame
   have to be loaded before using this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Mercury, Sun and the Sun Barycenter
   will lead to a different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   MERCURY_SUN_ORB using de405 ephemerides.


   \begindata

      FRAME_BC_MSM                  = -121933
      FRAME_-121933_NAME            = 'BC_MSM'
      FRAME_-121933_CLASS           =  5
      FRAME_-121933_CLASS_ID        = -121933
      FRAME_-121933_CENTER          = -121933
      FRAME_-121933_RELATIVE        = 'J2000'
      FRAME_-121933_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121933_FAMILY          = 'TWO-VECTOR'
      FRAME_-121933_PRI_AXIS        = 'X'
      FRAME_-121933_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-121933_PRI_OBSERVER    = 'BC_MSM'
      FRAME_-121933_PRI_TARGET      = 'SUN'
      FRAME_-121933_PRI_ABCORR      = 'NONE'
      FRAME_-121933_SEC_AXIS        = 'Z'
      FRAME_-121933_SEC_VECTOR_DEF  = 'CONSTANT'
      FRAME_-121933_SEC_SPEC        = 'LATITUDINAL'
      FRAME_-121933_SEC_UNITS       = 'DEGREES'
      FRAME_-121933_SEC_LONGITUDE   =  0.0
      FRAME_-121933_SEC_LATITUDE    =  90.0
      FRAME_-121933_SEC_FRAME       = 'IAU_MERCURY'

   \begintext


BepiColombo Mercury Body Fixed (BC_MBF)
------------------------------------------------------------------------

   Definition:
   -----------

   The Mercury Body Fixed frame is equivalent to the predefined Mercury Body
   Fixed frame (IAU_MERCURY) which is defined as a PCK (body-fixed) frame.
   PCK frames are reference frames whose orientation with respect to inertial
   frames is supplied through either binary or text PCK files.

   \begindata

      FRAME_BC_MBF             = -121934
      FRAME_-121934_NAME       = 'BC_MBF'
      FRAME_-121934_CLASS      = 4
      FRAME_-121934_CLASS_ID   = -121934
      FRAME_-121934_CENTER     = 199
      TKFRAME_-121934_SPEC     = 'MATRIX'
      TKFRAME_-121934_RELATIVE = 'IAU_MERCURY'
      TKFRAME_-121934_MATRIX   = ( 1, 0, 0,
                                   0, 1, 0,
                                   0, 0, 1 )

   \begintext


BepiColombo Mercury Mean Equator of Date Frame based on IAU2006 Constants
-------------------------------------------------------------------------

   The BC_MME_IAU2006_OF_DATE frame is based on Mean Mercury Equator
   and IAU vector of date computed using IAU 2006 Mercury rotation
   constants

   The BC_MME_IAU2006_OF_DATE frame is implemented as an Euler frame
   mathematically identical to the PCK frame IAU_MERCURY based on IAU
   2006 Mercury rotation constants but without prime meridian rotation
   terms.

   The IAU 2006 PCK data from [3] defining the IAU_MERCURY frame are:

      BODY199_POLE_RA          = (  281.01     -0.033      0. )
      BODY199_POLE_DEC         = (   61.45     -0.005      0. )
      BODY199_PM               = (  329.548     6.1385025  0. )

   Here pole RA/Dec terms in the PCK are in degrees and degrees/century;
   the rates here have been converted to degrees/sec ( = (rate deg/cen)/
   (86400.0 * 36525.0)). Prime meridian terms from the PCK are disregarded.

   The 3x3 transformation matrix M defined by the angles is

      M = [    0.0]   [angle_2]   [angle_3]
                   3           1           3

   Vectors are mapped from the J2000 base frame to the
   BC_MME_IAU2006_OF_DATE frame via left multiplication by M.

   The relationship of these Euler angles to RA/Dec for the
   J2000-to-IAU Mercury Mean Equator and IAU vector of date
   transformation is as follows:

      angle_1 is      0.0
      angle_2 is 90 - Dec
      angle_3 is 90 + RA, mapped into the range 0 < angle_3 < 2*pi

   Since when we define the BC_MME_IAU2006_OF_DATE frame we're defining
   the *inverse* of the above transformation, the angles for our Euler
   frame definition are reversed and the signs negated:

      angle_1 is -90 - RA, mapped into the range 0 < angle_3 < 2*pi
      angle_2 is -90 + Dec
      angle_3 is       0.0

   Then our frame definition is:

   \begindata

      FRAME_BC_MME_IAU2006_OF_DATE  = -121941
      FRAME_-121941_NAME            = 'BC_MME_IAU2006_OF_DATE'
      FRAME_-121941_CLASS           =  5
      FRAME_-121941_CLASS_ID        = -121941
      FRAME_-121941_CENTER          =  199
      FRAME_-121941_RELATIVE        = 'J2000'
      FRAME_-121941_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121941_FAMILY          = 'EULER'
      FRAME_-121941_EPOCH           =  @2000-JAN-1/12:00:00
      FRAME_-121941_AXES            =  ( 3  1  3 )
      FRAME_-121941_UNITS           = 'DEGREES'
      FRAME_-121941_ANGLE_1_COEFFS  = (  -11.01
                                          1.0457068978629554e-11 )
      FRAME_-121941_ANGLE_2_COEFFS  = (  -28.55
                                        -1.5844043907014476e-12 )
      FRAME_-121941_ANGLE_3_COEFFS  = (    0.0                     )
      FRAME_-121941_ROTATION_STATE  = 'INERTIAL'

   \begintext


BepiColombo Mercury Mean Equator at J2000 Frame based on IAU2006 Constants
--------------------------------------------------------------------------

   The BC_MME_IAU2006_J2000 frame is the BC_MME_IAU2006_OF_DATE frame
   frozen at J2000 TDB. For efficiency it is defined as a offset frame
   using pre-computed rotation matrix transforming vectors from
   BC_MME_IAU2006_OF_DATE to J2000 at J2000 TDB.

   For consistency with earlier BepiColombo usage the matrix below is
   from [5].

   \begindata

      FRAME_BC_MME_IAU2006_J2000    = -121942
      FRAME_-121942_NAME            = 'BC_MME_IAU2006_J2000'
      FRAME_-121942_CLASS           =  4
      FRAME_-121942_CLASS_ID        = -121942
      FRAME_-121942_CENTER          =  199
      TKFRAME_-121942_RELATIVE      = 'J2000'
      TKFRAME_-121942_SPEC          = 'MATRIX'
      TKFRAME_-121942_MATRIX        = (
         0.981593866044678,      0.190980318733265,      1.45064023353692E-15,
        -0.167757184264224,      0.862232423481673,      0.477925491080635,
         0.0912743626173337,    -0.469128730471140,      0.878400378515027
                                      )

   \begintext


BepiColombo Mercury Mean Equator of Date Frame based on IAU2009 Constants
-------------------------------------------------------------------------

   The BC_MME_IAU2009_OF_DATE frame is based on Mean Mercury Equator
   and IAU vector of date computed using IAU 2009 Mercury rotation
   constants

   The BC_MME_IAU2009_OF_DATE frame is implemented as as Euler frame
   mathematically identical to the PCK frame IAU_MERCURY based on IAU
   2009 Mercury rotation constants but without prime meridian rotation
   terms.

   The IAU 2009 PCK data from [4] defining the IAU_MERCURY frame are:

      BODY199_POLE_RA          = (  281.0097   -0.0328     0. )
      BODY199_POLE_DEC         = (   61.4143   -0.0049     0. )
      BODY199_PM               = (  329.5469    6.1385025  0. )

   Here pole RA/Dec terms in the PCK are in degrees and degrees/century;
   the rates here have been converted to degrees/sec ( = (rate deg/cen)/
   (86400.0 * 36525.0)). Prime meridian terms from the PCK are disregarded.

   The 3x3 transformation matrix M defined by the angles is

      M = [    0.0]   [angle_2]   [angle_3]
                   3           1           3

   Vectors are mapped from the J2000 base frame to the
   BC_MME_IAU2009_OF_DATE frame via left multiplication by M.

   The relationship of these Euler angles to RA/Dec for the
   J2000-to-IAU Mercury Mean Equator and IAU vector of date
   transformation is as follows:

      angle_1 is      0.0
      angle_2 is 90 - Dec
      angle_3 is 90 + RA, mapped into the range 0 < angle_3 < 2*pi

   Since when we define the BC_MME_IAU2009_OF_DATE frame we're defining
   the *inverse* of the above transformation, the angles for our Euler
   frame definition are reversed and the signs negated:

      angle_1 is -90 - RA, mapped into the range 0 < angle_3 < 2*pi
      angle_2 is -90 + Dec
      angle_3 is       0.0

   Then our frame definition is:

   \begindata

      FRAME_BC_MME_IAU2009_OF_DATE  = -121943
      FRAME_-121943_NAME            = 'BC_MME_IAU2009_OF_DATE'
      FRAME_-121943_CLASS           =  5
      FRAME_-121943_CLASS_ID        = -121943
      FRAME_-121943_CENTER          =  199
      FRAME_-121943_RELATIVE        = 'J2000'
      FRAME_-121943_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121943_FAMILY          = 'EULER'
      FRAME_-121943_EPOCH           =  @2000-JAN-1/12:00:00
      FRAME_-121943_AXES            =  ( 3  1  3 )
      FRAME_-121943_UNITS           = 'DEGREES'
      FRAME_-121943_ANGLE_1_COEFFS  = (  -11.0097
                                          1.0393692803001496e-11 )
      FRAME_-121943_ANGLE_2_COEFFS  = (  -28.5857
                                         -1.5527163028874185e-12 )
      FRAME_-121943_ANGLE_3_COEFFS  = (    0.0                     )
      FRAME_-121943_ROTATION_STATE  = 'INERTIAL'

   \begintext


Mercury Mean Equator at J2000 Frame based on IAU2009 Constants
--------------------------------------------------------------

   The BC_MME_IAU2009_J2000 frame is the BC_MME_IAU2009_OF_DATE frame
   frozen at J2000 TDB. For efficiency it is defined as a offset frame
   using pre-computed rotation matrix transforming vectors from
   BC_MME_IAU2009_OF_DATE to J2000 at J2000 TDB.

   \begindata

      FRAME_BC_MME_IAU2009_J2000    = -121944
      FRAME_-121944_NAME            = 'BC_MME_IAU2009_J2000'
      FRAME_-121944_CLASS           =  4
      FRAME_-121944_CLASS_ID        = -121944
      FRAME_-121944_CENTER          =  199
      TKFRAME_-121944_RELATIVE      = 'J2000'
      TKFRAME_-121944_SPEC          = 'MATRIX'
      TKFRAME_-121944_MATRIX        = (
     +9.8159486600183365E-01 +1.9097517911718839E-01 +0.0000000000000000E+00
     -1.6769576713227249E-01 +8.6194082826998297E-01 +4.7847271421385607E-01
     +9.1376412299678439E-02 -4.6966635979428373E-01 +8.7810242099246349E-01
                                    )

   \begintext


Sun Based Frames
-------------------------------------------------------------------------------


BepiColombo MPO Heliocentric Radial-Tangential-Normal (BC_MPO_RTN)
------------------------------------------------------------------------

   Definition:
   -----------

   The BepiColombo MPO Heliocentric Radial-Tangential-Normal frame is defined
   as follows (from [3]):

      -  the position of MPO relative to the Sun is the primary vector:
         +X axis points from the Sun to MPO;

      -  the projection of the solar rotational axis perpendicular to
         the +X axis defines the frame's +Z axis;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of the Sun.

   All vectors are geometric: no aberration corrections are used.


   Uses and applications (from [5]):
   ---------------------------------

   This frame is used to define the velocity and field direction of the
   plasma environment that the spacecraft finds itself in.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector, therefore, the ephemeris data required to compute the
   Sun-MPO position vector in the J2000 reference frame must be
   loaded before using this frame.

   The secondary vector is defined as a constant vector in the IAU_SUN
   frame, which is a PCK-based frame, therefore a PCK file containing
   the orientation constants for the Sun must be loaded before using
   this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Mercury, the Sun, the Solar System Barycenter and
   MPO spacecraft will lead to different frame orientation at a given time.

   This frame is also defined based on the IAU_SUN frame, whose
   evaluation is based on the data included in the loaded PCK file:
   different orientation constants for the Sun's spin axis will lead to
   different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   BC_RTN using the IAU 2009 constants, the DE432 ephemeris and
   the MPO ephemeris version N.


   \begindata

      FRAME_BC_MPO_RTN               = -121951
      FRAME_-121951_NAME             = 'BC_MPO_RTN'
      FRAME_-121951_CLASS            =  5
      FRAME_-121951_CLASS_ID         = -121971
      FRAME_-121951_CENTER           =  10
      FRAME_-121951_RELATIVE         = 'J2000'
      FRAME_-121951_DEF_STYLE        = 'PARAMETERIZED'
      FRAME_-121951_FAMILY           = 'TWO-VECTOR'
      FRAME_-121951_PRI_AXIS         = 'X'
      FRAME_-121951_PRI_VECTOR_DEF   = 'OBSERVER_TARGET_POSITION'
      FRAME_-121951_PRI_OBSERVER     = 'SUN'
      FRAME_-121951_PRI_TARGET       = 'MPO'
      FRAME_-121951_PRI_ABCORR       = 'NONE'
      FRAME_-121951_SEC_AXIS         = 'Z'
      FRAME_-121951_SEC_VECTOR_DEF   = 'CONSTANT'
      FRAME_-121951_SEC_FRAME        = 'IAU_SUN'
      FRAME_-121951_SEC_SPEC         = 'RECTANGULAR'
      FRAME_-121951_SEC_VECTOR       = ( 0, 0, 1 )

   \begintext


BepiColombo MMO Heliocentric Radial-Tangential-Normal (BC_MMO_RTN)
------------------------------------------------------------------------

   Definition:
   -----------

   The BepiColombo MMO Heliocentric Radial-Tangential-Normal frame is defined
   as follows (from [4]):

      -  the position of MMO relative to the Sun is the primary vector:
         +X axis points from the Sun to MPO;

      -  the projection of the solar rotational axis perpendicular to
         the +X axis defines the frame's +Z axis;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of the Sun.

   All vectors are geometric: no aberration corrections are used.


   Uses and applications (from [5]):
   ---------------------------------

   This frame is used to define the velocity and field direction of the
   plasma environment that the spacecraft finds itself in.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector, therefore, the ephemeris data required to compute the
   Sun-MMO position vector in the J2000 reference frame must be
   loaded before using this frame.

   The secondary vector is defined as a constant vector in the IAU_SUN
   frame, which is a PCK-based frame, therefore a PCK file containing
   the orientation constants for the Sun must be loaded before using
   this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Mercury, the Sun, the Solar System Barycenter and
   MPO spacecraft will lead to different frame orientation at a given time.

   This frame is also defined based on the IAU_SUN frame, whose
   evaluation is based on the data included in the loaded PCK file:
   different orientation constants for the Sun's spin axis will lead to
   different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   BC_RTN using the IAU 2009 constants, the DE432 ephemeris and
   the MMO ephemeris version N.


   \begindata

      FRAME_BC_MMO_RTN               = -121952
      FRAME_-121952_NAME             = 'BC_MMO_RTN'
      FRAME_-121952_CLASS            =  5
      FRAME_-121952_CLASS_ID         = -121952
      FRAME_-121952_CENTER           =  10
      FRAME_-121952_RELATIVE         = 'J2000'
      FRAME_-121952_DEF_STYLE        = 'PARAMETERIZED'
      FRAME_-121952_FAMILY           = 'TWO-VECTOR'
      FRAME_-121952_PRI_AXIS         = 'X'
      FRAME_-121952_PRI_VECTOR_DEF   = 'OBSERVER_TARGET_POSITION'
      FRAME_-121952_PRI_OBSERVER     = 'SUN'
      FRAME_-121952_PRI_TARGET       = 'MMO'
      FRAME_-121952_PRI_ABCORR       = 'NONE'
      FRAME_-121952_SEC_AXIS         = 'Z'
      FRAME_-121952_SEC_VECTOR_DEF   = 'CONSTANT'
      FRAME_-121952_SEC_FRAME        = 'IAU_SUN'
      FRAME_-121952_SEC_SPEC         = 'RECTANGULAR'
      FRAME_-121952_SEC_VECTOR       = ( 0, 0, 1 )

   \begintext


Earth based Frames
-------------------------------------------------------------------------------


BepiColombo Geocentric Solar Ecliptic (BC_GSE)
------------------------------------------------------------------------

   Definition:
   -----------

   The BepiColombo Geocentric Solar Ecliptic frame is defined as follows:

      -  +Z axis is perpendicular to the plane of the Earth's orbit around
         the Sun (positive North);

      -  +X axis is the position of the Sun relative to the Earth;
         it's the primary vector and points from Earth to Sun;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of the Earth.

   All vectors are geometric: no corrections are used.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector. Therefore, the ephemeris data required to compute the
   Earth-Sun vector in J2000 reference frame have
   to be loaded before using this frame.

   The secondary vector is defined as an 'observer-target velocity'
   vector. Therefore, the ephemeris data required to compute the
   Earth-Sun velocity vector in the J2000 reference frame
   have to be loaded before using this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Earth, Sun and the Sun Barycenter
   will lead to a different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   BC_GSE using de405 ephemerides.

   The definition of the BepiColombo Geocentric Solar Ecliptic frame is as
   follows:


   \begindata

      FRAME_BC_GSE                  = -121961
      FRAME_-121961_NAME            = 'BC_GSE'
      FRAME_-121961_CLASS           =  5
      FRAME_-121961_CLASS_ID        = -121961
      FRAME_-121961_CENTER          =  399
      FRAME_-121961_RELATIVE        = 'J2000'
      FRAME_-121961_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121961_FAMILY          = 'TWO-VECTOR'
      FRAME_-121961_PRI_AXIS        = 'X'
      FRAME_-121961_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-121961_PRI_OBSERVER    = 'EARTH'
      FRAME_-121961_PRI_TARGET      = 'SUN'
      FRAME_-121961_PRI_ABCORR      = 'NONE'
      FRAME_-121961_SEC_AXIS        = '-Y'
      FRAME_-121961_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-121961_SEC_OBSERVER    = 'SUN'
      FRAME_-121961_SEC_TARGET      = 'EARTH'
      FRAME_-121961_SEC_FRAME       = 'J2000'
      FRAME_-121961_SEC_ABCORR      = 'NONE

   \begintext


BepiColombo Geocentric Solar Magnetospheric (BC_GSM)
------------------------------------------------------------------------

   Definition:
   -----------

   The BepiColombo Geocentric Solar Magnetospheric frame is defined as follows:

      -  +Z axis is the projection of the Earth's magnetic dipole axis
         (positive North) on to the plane perpendicular to the X axis;

      -  +X axis is the position of the Sun relative to the Earth;
         it's the primary vector and points from Earth to Sun;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the center of mass of the Earth.


   All vectors are geometric: no corrections are used.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector. Therefore, the ephemeris data required to compute the
   Earth-Sun vector in J2000 reference frame have
   to be loaded before using this frame.


   Remarks:
   --------

   The latest estimate location of Earth's north geomagnetic pole as
   calculated from the latest IGRF 14 model (from [8]) is at 80.7 degrees
   North a 287.3 degree East longitude. Please note that when we refer to
   the ``north geomagnetic pole'' we refer to the location of the magnetic
   dipole axis axis penetrating through the surface of Earth on the northern
   hemisphere (from [7]).

   This frame is defined based on SPK data: different planetary ephemerides
   for Earth, Sun and the Sun Barycenter will lead to a different frame
   orientation at a given time.

   It is strongly recommended to indicate what data have been used in the
   evaluation of this frame when referring to it, e.g. BC_GSE using de405
   ephemerides.

   The definition of the BepiColombo Geocentric Solar Magnetospheric
   frame is as follows:

   \begindata

      FRAME_BC_GSM                  = -121962
      FRAME_-121962_NAME            = 'BC_GSM'
      FRAME_-121962_CLASS           =  5
      FRAME_-121962_CLASS_ID        = -121962
      FRAME_-121962_CENTER          =  399
      FRAME_-121962_RELATIVE        = 'J2000'
      FRAME_-121962_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121962_FAMILY          = 'TWO-VECTOR'
      FRAME_-121962_PRI_AXIS        = 'X'
      FRAME_-121962_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-121962_PRI_OBSERVER    = 'EARTH'
      FRAME_-121962_PRI_TARGET      = 'SUN'
      FRAME_-121962_PRI_ABCORR      = 'NONE'
      FRAME_-121962_SEC_AXIS        = 'Z'
      FRAME_-121962_SEC_VECTOR_DEF  = 'CONSTANT'
      FRAME_-121962_SEC_SPEC        = 'LATITUDINAL'
      FRAME_-121962_SEC_UNITS       = 'DEGREES'
      FRAME_-121962_SEC_LONGITUDE   =  287.3
      FRAME_-121962_SEC_LATITUDE    =  80.7
      FRAME_-121962_SEC_FRAME       = 'EARTH_FIXED'

   \begintext


Venus based Frames
-------------------------------------------------------------------------------


BepiColombo Venus-centric Solar Orbital frame (BC_VSO)
------------------------------------------------------------------------

   Definition:
   -----------

   The Venus-centric Solar Orbital frame is defined as follows:

      -  +X axis is the position of the Sun relative to Venus;
         it's the primary vector and points from Venus to Sun;

      -  +Y axis is the component of the inertially referenced
         velocity of Sun relative to Venus, orthogonal to the +X axis;

      -  +Z axis completes the right-handed system;

      -  the origin of this frame is the center of mass of Venus.

   All vectors are geometric: no corrections are used.


   Required Data:
   --------------

   This frame is defined as a two-vector frame using two different
   types of specifications for the primary and secondary vectors.

   The primary vector is defined as an 'observer-target position'
   vector. Therefore, the ephemeris data required to compute the
   Venus-Sun vector in J2000 reference frame have
   to be loaded before using this frame.

   The secondary vector is defined as an 'observer-target velocity'
   vector. Therefore, the ephemeris data required to compute the
   Venus-Sun velocity vector in the J2000 reference frame
   have to be loaded before using this frame.


   Remarks:
   --------

   This frame is defined based on SPK data: different planetary
   ephemerides for Venus, Sun and the Sun Barycenter
   will lead to a different frame orientation at a given time.

   It is strongly recommended to indicate what data have been used
   in the evaluation of this frame when referring to it, e.g.
   BC_VSO using de405 ephemerides.


   \begindata

      FRAME_BC_VSO                  = -121971
      FRAME_-121971_NAME            = 'BC_VSO'
      FRAME_-121971_CLASS           =  5
      FRAME_-121971_CLASS_ID        = -121971
      FRAME_-121971_CENTER          =  299
      FRAME_-121971_RELATIVE        = 'J2000'
      FRAME_-121971_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-121971_FAMILY          = 'TWO-VECTOR'
      FRAME_-121971_PRI_AXIS        = 'X'
      FRAME_-121971_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-121971_PRI_OBSERVER    = 'VENUS'
      FRAME_-121971_PRI_TARGET      = 'SUN'
      FRAME_-121971_PRI_ABCORR      = 'NONE'
      FRAME_-121971_SEC_AXIS        = 'Y'
      FRAME_-121971_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-121971_SEC_OBSERVER    = 'VENUS'
      FRAME_-121971_SEC_TARGET      = 'SUN'
      FRAME_-121971_SEC_ABCORR      = 'NONE'
      FRAME_-121971_SEC_FRAME       = 'J2000'

   \begintext


BepiColombo-specific Science frames  NAIF ID Codes to Name Mapping
------------------------------------------------------------------------------

   This section contains name to NAIF ID mappings for the BepiColombo.
   Once the contents of this file is loaded into the KERNEL POOL,
   these mappings become available within SPICE, making it possible to use
   names instead of ID code in the high level SPICE routine calls.

      ----------------------  --------
       Name                    ID
      ----------------------  --------
       BC_MSM                 -121933
      ----------------------  --------

    Name-ID Mapping keywords:

   \begindata

      NAIF_BODY_NAME   += ( 'BC_MSM'              )
      NAIF_BODY_CODE   += ( -121933               )

   \begintext


End of FK file.
