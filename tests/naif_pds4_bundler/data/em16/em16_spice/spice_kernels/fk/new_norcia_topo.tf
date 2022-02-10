
Topocentric Frame kernel for New Norcia
=======================================
 
Updated:                    2004 March 19 05:20:00 PDT (NJB)

   Comments regarding provisional ID code and name for 
   the New Norcia site were removed.

Creation date:              2003 June 24 04:22:00 PDT
Created by:                 Nat Bachman (JPL/NAIF)

This is a frame kernel defining a topocentric reference 
frame for the ESA 35m tracking antenna at New Norcia. 
Location data used to define this frame are taken from
a draft JPL IOM by W. M. Folkner, dated January 6, 2003.

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

Data for the New Norcia topocentric frame follow.

\begindata

   FRAME_NEW_NORCIA_TOPO            =  1398990
   FRAME_1398990_NAME               = 'NEW_NORCIA_TOPO'
   FRAME_1398990_CLASS              =  4
   FRAME_1398990_CLASS_ID           =  1398990
   FRAME_1398990_CENTER             =   398990

   OBJECT_398990_FRAME              = 'NEW_NORCIA_TOPO'

   TKFRAME_NEW_NORCIA_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_NEW_NORCIA_TOPO_SPEC     = 'ANGLES'
   TKFRAME_NEW_NORCIA_TOPO_UNITS    = 'DEGREES'
   TKFRAME_NEW_NORCIA_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_NEW_NORCIA_TOPO_ANGLES   = ( -116.19149821615236, 
                                        -121.04822822665279,
                                         180.0              )

\begintext

