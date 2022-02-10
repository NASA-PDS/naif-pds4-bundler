KPL/FK

Topocentric Frame kernel for the Russian ground stations
========================================================

   This is a frame kernel defining a topocentric reference frame
   for the Russian ground stations. Location data used to define
   this frame are taken from the EXOMARS 2016 Navigation ICD
   ESOC/RKPNI (EXM-GS-ICD-ESC-50005).


References
-----------------------------------------------------------------------------

   1. ``Frames Required Reading'', NAIF

   2. ``Kernel Pool Required Reading'', NAIF

   3. ``C-Kernel Required Reading'', NAIF

   4. EXOMARS 2016 Navigation ICD ESOC/RKPNI (EXM-GS-ICD-ESC-50005)


Contact Information
-----------------------------------------------------------------------------

   If you have any questions regarding this file contact the ESA SPICE
   Service at ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           alfredo.escalante@esa.int

   or SPICE support at IKI:

           Alexander Abbakumov
           +7 (495) 333-40-13
           aabbakumov@romance.iki.rssi.ru


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


Stations Frames
-----------------------------------------------------------------------------

   The topocentric frame defines the z axis as the normal outward at the
   station site, the x axis points at local north (geographic) with the
   y axis completing the right handed frame.  Positive azimuth is measured
   counter clockwise from the x axis.

   The equatorial radius and flattening factor for the ITRF93
   reference ellipsoid are

      radius      = 6378.1363
      flattening  = 1.0/298.257

   Please note that all rotations mean the rotation of the coordinate
   frames about an axis and not of the vectors.

   The rotation defined in this file transforms vectors from
   the topocentric frame defined as

      z - normal to the surface at the site
      x - local north
      y - local west

   to an earth-fixed frame defined as

      x - along the line of zero longitude intersecting the equator
      z - along the spin axis
      y - completing the right hand coordinate frame

   This is a 3-2-3 rotation with angles defined as the negative of the site
   longitude, the negative of the site colatitude, 180 degrees.

   This file uses the reference frame alias EARTH_FIXED.
   In order to use this file in a SPICE-based program,
   the alias must be mapped to the frames ITRF93 or IAU_EARTH
   by a text kernel.  An example of the text kernel assignments
   mapping EARTH_FIXED to ITRF93 is:

      TKFRAME_EARTH_FIXED_RELATIVE = 'ITRF93'
      TKFRAME_EARTH_FIXED_SPEC     = 'MATRIX'
      TKFRAME_EARTH_FIXED_MATRIX   = ( 1   0   0
                                       0   1   0
                                       0   0   1 )


   These assignments must be preceded by the \begindata marker
   alone on a line.

   See the Frames Required Reading for details.

   The ITRF93 frame should be used for high-accuracy work.  A binary
   high-precision earth PCK file should be used to convert the station
   location from terrestrial to inertial coordinates.


\begindata

   NAIF_BODY_NAME                      += 'BEAR_LAKES'
   NAIF_BODY_CODE                      += 399603

   NAIF_BODY_NAME                      += 'KALYAZIN'
   NAIF_BODY_CODE                      += 399604

\begintext


   Reference frame specifications follow:


   Topocentric frame BL_TOPO

      The Z axis of this frame points toward the zenith.
      The X axis of this frame points North.

      Topocentric frame BL_TOPO is centered at the
      site BEAR_LAKES, which at the epoch

          2005 JAN 01 00:00:00.000 TDB

      has Cartesian coordinates

         X (km):                  0.2828547498000E+04
         Y (km):                  0.2206064086000E+04
         Z (km):                  0.5256395991000E+04

      and planetodetic coordinates

         Longitude (deg):        37.9516746689565
         Latitude  (deg):        55.8682066148442
         Altitude   (km):         0.2097967323084E+00

      These planetodetic coordinates are expressed relative to
      a reference spheroid having the dimensions

         Equatorial radius (km):  6.3781366000000E+03
         Polar radius      (km):  6.3567519000000E+03

      All of the above coordinates are relative to the frame ITRF93.


\begindata

   FRAME_BL_TOPO                       =  1399603
   FRAME_1399603_NAME                  =  'BL_TOPO'
   FRAME_1399603_CLASS                 =  4
   FRAME_1399603_CLASS_ID              =  1399603
   FRAME_1399603_CENTER                =  399603

   OBJECT_399603_FRAME                 =  'BL_TOPO'

   TKFRAME_1399603_RELATIVE            =  'ITRF93'
   TKFRAME_1399603_SPEC                =  'ANGLES'
   TKFRAME_1399603_UNITS               =  'DEGREES'
   TKFRAME_1399603_AXES                =  ( 3, 2, 3 )
   TKFRAME_1399603_ANGLES              =  (  -37.9516746689565,
                                             -34.1317933851558,
                                             180.0000000000000 )


\begintext

   Topocentric frame KLZ_TOPO

      The Z axis of this frame points toward the zenith.
      The X axis of this frame points North.

      Topocentric frame KLZ_TOPO is centered at the
      site KALYAZIN, which at the epoch

          2005 JAN 01 00:00:00.000 TDB

      has Cartesian coordinates

         X (km):                  0.2731191749000E+04
         Y (km):                  0.2126199292000E+04
         Z (km):                  0.5339538091000E+04

      and planetodetic coordinates

         Longitude (deg):        37.9003203524384
         Latitude  (deg):        57.2230158501456
         Altitude   (km):         0.1814397680015E+00

      These planetodetic coordinates are expressed relative to
      a reference spheroid having the dimensions

         Equatorial radius (km):  6.3781366000000E+03
         Polar radius      (km):  6.3567519000000E+03

      All of the above coordinates are relative to the frame ITRF93.


\begindata

   FRAME_KLZ_TOPO                      =  1399604
   FRAME_1399604_NAME                  =  'KLZ_TOPO'
   FRAME_1399604_CLASS                 =  4
   FRAME_1399604_CLASS_ID              =  1399604
   FRAME_1399604_CENTER                =  399604

   OBJECT_399604_FRAME                 =  'KLZ_TOPO'

   TKFRAME_1399604_RELATIVE            =  'ITRF93'
   TKFRAME_1399604_SPEC                =  'ANGLES'
   TKFRAME_1399604_UNITS               =  'DEGREES'
   TKFRAME_1399604_AXES                =  ( 3, 2, 3 )
   TKFRAME_1399604_ANGLES              =  (  -37.9003203524384,
                                             -32.7769841498544,
                                             180.0000000000000 )

\begintext


End of FK file.
