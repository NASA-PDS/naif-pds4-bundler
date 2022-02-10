KPL/FK

Trace Gas Orbiter (TGO) Relay Locations Frames Kernel
=====================================================

   This frame kernel contains a set of ExoMars 2016 Trace Gas Orbiter
   Spacecraft (TGO) relay locations frame definitions for selected
   Rovers and Landers.


Version and Date
-----------------------------------------------------------------------------

   Version 0.2 -- July 22, 2021 -- Alfredo Escalante Lopez, ESAC/ESA

      Improved descriptions for PDS4 Bundle increment.

   Version 0.1 -- May 18, 2021 -- Bernhard Geiger, ESAC/ESA

      Initial version.


References
-----------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``SP-Kernel Required Reading''


Contact Information
-----------------------------------------------------------------------------

   If you have any questions regarding this file contact the
   ESA SPICE Service at ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           spice@sciops.esa.int


Implementation Notes
-----------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make use
   of this frame kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool".  The SPICELIB
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


Definition Section
------------------------------------------------------------------------
 
   FILE: em16_tgo_relay_locations_v01.tf
 
   This file was created by PINPOINT.
 
   PINPOINT Version 3.1.0 --- July 2, 2014
   PINPOINT RUN DATE/TIME:    2021-05-18T12:28:15
   PINPOINT DEFINITIONS FILE: em16_tgo_relay_locations_v01.txt
   PINPOINT PCK FILE:         pck00010.tpc
   PINPOINT SPK FILE:         em16_tgo_relay_locations_v01.bsp
 
   The input definitions file is appended to this
   file as a comment block.
 
 
   Body-name mapping follows:
 
\begindata
 
   NAIF_BODY_NAME                      += 'MSL'
   NAIF_BODY_CODE                      += -76
 
   NAIF_BODY_NAME                      += 'INSIGHT'
   NAIF_BODY_CODE                      += -189
 
   NAIF_BODY_NAME                      += 'M2020'
   NAIF_BODY_CODE                      += -168
 
\begintext
 
 
   Reference frame specifications follow:
 
 
   Topocentric frame MSL_TOPO
 
      The Z axis of this frame points toward the zenith.
      The Y axis of this frame points North.
 
      Topocentric frame MSL_TOPO is centered at the site MSL
      which has Cartesian coordinates
 
         X (km):                 -0.2489864000000E+04
         Y (km):                  0.2286206000000E+04
         Z (km):                 -0.2713460000000E+03
 
      and planetodetic coordinates
 
         Longitude (deg):       137.4416893405198
         Latitude  (deg):        -4.6438540943152
         Altitude   (km):        -0.4926957870218E+01
 
      These planetodetic coordinates are expressed relative to
      a reference spheroid having the dimensions
 
         Equatorial radius (km):  3.3961900000000E+03
         Polar radius      (km):  3.3762000000000E+03
 
      All of the above coordinates are relative to the frame IAU_MARS.
 
 
\begindata
 
   FRAME_MSL_TOPO                      =  999924
   FRAME_999924_NAME                   =  'MSL_TOPO'
   FRAME_999924_CLASS                  =  4
   FRAME_999924_CLASS_ID               =  999924
   FRAME_999924_CENTER                 =  -76
 
   OBJECT_-76_FRAME                    =  'MSL_TOPO'
 
   TKFRAME_999924_RELATIVE             =  'IAU_MARS'
   TKFRAME_999924_SPEC                 =  'ANGLES'
   TKFRAME_999924_UNITS                =  'DEGREES'
   TKFRAME_999924_AXES                 =  ( 3, 2, 3 )
   TKFRAME_999924_ANGLES               =  ( -137.4416893405198,
                                             -94.6438540943152,
                                             270.0000000000000 )
 
 
\begintext
 
   Topocentric frame INSIGHT_TOPO
 
      The Z axis of this frame points toward the zenith.
      The Y axis of this frame points North.
 
      Topocentric frame INSIGHT_TOPO is centered at the site INSIGHT
      which has Cartesian coordinates
 
         X (km):                 -0.2417750000000E+04
         Y (km):                  0.2365699000000E+04
         Z (km):                  0.2663591000000E+03
 
      and planetodetic coordinates
 
         Longitude (deg):       135.6234382178438
         Latitude  (deg):         4.5556872599941
         Altitude   (km):        -0.2985413656678E+01
 
      These planetodetic coordinates are expressed relative to
      a reference spheroid having the dimensions
 
         Equatorial radius (km):  3.3961900000000E+03
         Polar radius      (km):  3.3762000000000E+03
 
      All of the above coordinates are relative to the frame IAU_MARS.
 
 
\begindata
 
   FRAME_INSIGHT_TOPO                  =  999811
   FRAME_999811_NAME                   =  'INSIGHT_TOPO'
   FRAME_999811_CLASS                  =  4
   FRAME_999811_CLASS_ID               =  999811
   FRAME_999811_CENTER                 =  -189
 
   OBJECT_-189_FRAME                   =  'INSIGHT_TOPO'
 
   TKFRAME_999811_RELATIVE             =  'IAU_MARS'
   TKFRAME_999811_SPEC                 =  'ANGLES'
   TKFRAME_999811_UNITS                =  'DEGREES'
   TKFRAME_999811_AXES                 =  ( 3, 2, 3 )
   TKFRAME_999811_ANGLES               =  ( -135.6234382178438,
                                             -85.4443127400059,
                                             270.0000000000000 )
 
 
\begintext
 
   Topocentric frame M2020_TOPO
 
      The Z axis of this frame points toward the zenith.
      The Y axis of this frame points North.
 
      Topocentric frame M2020_TOPO is centered at the site M2020
      which has Cartesian coordinates
 
         X (km):                  0.7002047000000E+03
         Y (km):                  0.3140206500000E+04
         Z (km):                  0.1074398200000E+04
 
      and planetodetic coordinates
 
         Longitude (deg):        77.4297993589779
         Latitude  (deg):        18.6706323344886
         Altitude   (km):        -0.2190344887703E+01
 
      These planetodetic coordinates are expressed relative to
      a reference spheroid having the dimensions
 
         Equatorial radius (km):  3.3961900000000E+03
         Polar radius      (km):  3.3762000000000E+03
 
      All of the above coordinates are relative to the frame IAU_MARS.
 
 
\begindata
 
   FRAME_M2020_TOPO                    =  999832
   FRAME_999832_NAME                   =  'M2020_TOPO'
   FRAME_999832_CLASS                  =  4
   FRAME_999832_CLASS_ID               =  999832
   FRAME_999832_CENTER                 =  -168
 
   OBJECT_-168_FRAME                   =  'M2020_TOPO'
 
   TKFRAME_999832_RELATIVE             =  'IAU_MARS'
   TKFRAME_999832_SPEC                 =  'ANGLES'
   TKFRAME_999832_UNITS                =  'DEGREES'
   TKFRAME_999832_AXES                 =  ( 3, 2, 3 )
   TKFRAME_999832_ANGLES               =  (  -77.4297993589779,
                                             -71.3293676655115,
                                             270.0000000000000 )
 
\begintext
 
 
Definitions file em16_tgo_relay_locations_v01.txt
--------------------------------------------------------------------------------
 
begindata
 
   SITES     = ( 'MSL', 'INSIGHT', 'M2020' )
 
   MSL_CENTER = 499
   MSL_FRAME  = 'IAU_MARS'
   MSL_IDCODE = -76
   MSL_XYZ    = ( -2489.864, 2286.206, -271.346 )
   MSL_BOUNDS = ( @2001-JAN-01, @2100-JAN-01 )
   MSL_UP     =  'Z'
   MSL_NORTH  =  'Y'
 
   INSIGHT_CENTER = 499
   INSIGHT_FRAME  = 'IAU_MARS'
   INSIGHT_IDCODE = -189
   INSIGHT_XYZ    = ( -2417.750, 2365.699, 266.3591 )
   INSIGHT_BOUNDS = ( @2001-JAN-01, @2100-JAN-01 )
   INSIGHT_UP     =  'Z'
   INSIGHT_NORTH  =  'Y'
 
   M2020_CENTER = 499
   M2020_FRAME  = 'IAU_MARS'
   M2020_IDCODE = -168
   M2020_XYZ    = ( 700.2047, 3140.2065, 1074.3982 )
   M2020_BOUNDS = ( @2001-JAN-01, @2100-JAN-01 )
   M2020_UP     =  'Z'
   M2020_NORTH  =  'Y'
 
begintext
 
[End of definitions file]
 
