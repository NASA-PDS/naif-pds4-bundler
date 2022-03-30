Topocentric Frame kernel for the ESA ground stations
====================================================

Creation date:              2011 March 8th
Created by:                 J. Vazquez (ESA/ESAC)

This is a frame kernel defining a topocentric reference
frame for the ESA ESA ground stations.
Location data used to define this frame are taken from
the ESA web pages.

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

Disclaimer:
----------

Please note that the accuracy of these coordinates
might not be sufficient for the purposes of your application. A new
definitive version, with more accurate information, shall be provided
in the future. High precision information for the New Norcia ground
station exists and is available in NEW_NORCIA_TOPO.TF, that shall be
used along with NEW_NORCIA.BSP.

Also note that the NAIF ID are provisional and they might change in
the definitive version.



Data for the ground stations topocentric frames follow.

\begindata


   NAIF_BODY_CODE                  += ( 399500 )
   NAIF_BODY_NAME                  += ( 'KIRUNA' )

   FRAME_KIRUNA_TOPO              =  1399500
   FRAME_1399500_NAME               = 'KIRUNA_TOPO'
   FRAME_1399500_CLASS              =  4
   FRAME_1399500_CLASS_ID           =  1399500
   FRAME_1399500_CENTER             =   399500

   OBJECT_399500_FRAME              = 'KIRUNA_TOPO'

   TKFRAME_KIRUNA_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_KIRUNA_TOPO_SPEC     = 'ANGLES'
   TKFRAME_KIRUNA_TOPO_UNITS    = 'DEGREES'
   TKFRAME_KIRUNA_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_KIRUNA_TOPO_ANGLES   = ( -20.964, -22.143, 180.0 )


   NAIF_BODY_CODE                  += ( 399501 )
   NAIF_BODY_NAME                  += ( 'KOUROU' )

   FRAME_KOUROU_TOPO              =  1399501
   FRAME_1399501_NAME               = 'KOUROU_TOPO'
   FRAME_1399501_CLASS              =  4
   FRAME_1399501_CLASS_ID           =  1399501
   FRAME_1399501_CENTER             =   399501

   OBJECT_399501_FRAME              = 'KOUROU_TOPO'

   TKFRAME_KOUROU_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_KOUROU_TOPO_SPEC     = 'ANGLES'
   TKFRAME_KOUROU_TOPO_UNITS    = 'DEGREES'
   TKFRAME_KOUROU_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_KOUROU_TOPO_ANGLES   = ( 52.805, -84.749, 180.0 )



   NAIF_BODY_CODE                  += ( 399502 )
   NAIF_BODY_NAME                  += ( 'MASPALOMAS' )

   FRAME_MASPALOMAS_TOPO              =  1399502
   FRAME_1399502_NAME               = 'MASPALOMAS_TOPO'
   FRAME_1399502_CLASS              =  4
   FRAME_1399502_CLASS_ID           =  1399502
   FRAME_1399502_CENTER             =   399502

   OBJECT_399502_FRAME              = 'MASPALOMAS_TOPO'

   TKFRAME_MASPALOMAS_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_MASPALOMAS_TOPO_SPEC     = 'ANGLES'
   TKFRAME_MASPALOMAS_TOPO_UNITS    = 'DEGREES'
   TKFRAME_MASPALOMAS_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_MASPALOMAS_TOPO_ANGLES   = ( 15.634, -62.237, 180.0 )



   NAIF_BODY_CODE                  += ( 399503 )
   NAIF_BODY_NAME                  += ( 'PERTH' )

   FRAME_PERTH_TOPO              =  1399503
   FRAME_1399503_NAME               = 'PERTH_TOPO'
   FRAME_1399503_CLASS              =  4
   FRAME_1399503_CLASS_ID           =  1399503
   FRAME_1399503_CENTER             =   399503

   OBJECT_399503_FRAME              = 'PERTH_TOPO'

   TKFRAME_PERTH_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_PERTH_TOPO_SPEC     = 'ANGLES'
   TKFRAME_PERTH_TOPO_UNITS    = 'DEGREES'
   TKFRAME_PERTH_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_PERTH_TOPO_ANGLES   = ( -115.885, -121.803, 180.0 )



   NAIF_BODY_CODE                  += ( 399504 )
   NAIF_BODY_NAME                  += ( 'REDU' )

   FRAME_REDU_TOPO              =  1399504
   FRAME_1399504_NAME               = 'REDU_TOPO'
   FRAME_1399504_CLASS              =  4
   FRAME_1399504_CLASS_ID           =  1399504
   FRAME_1399504_CENTER             =   399504

   OBJECT_399504_FRAME              = 'REDU_TOPO'

   TKFRAME_REDU_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_REDU_TOPO_SPEC     = 'ANGLES'
   TKFRAME_REDU_TOPO_UNITS    = 'DEGREES'
   TKFRAME_REDU_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_REDU_TOPO_ANGLES   = ( -5.145, -39.999, 180.0 )



   NAIF_BODY_CODE                  += ( 399505 )
   NAIF_BODY_NAME                  += ( 'STA_MARIA' )

   FRAME_STA_MARIA_TOPO              =  1399505
   FRAME_1399505_NAME               = 'STA_MARIA_TOPO'
   FRAME_1399505_CLASS              =  4
   FRAME_1399505_CLASS_ID           =  1399505
   FRAME_1399505_CENTER             =   399505

   OBJECT_399505_FRAME              = 'STA_MARIA_TOPO'

   TKFRAME_STA_MARIA_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_STA_MARIA_TOPO_SPEC     = 'ANGLES'
   TKFRAME_STA_MARIA_TOPO_UNITS    = 'DEGREES'
   TKFRAME_STA_MARIA_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_STA_MARIA_TOPO_ANGLES   = ( 25.136, -53.003, 180.0 )



   NAIF_BODY_CODE                  += ( 399506 )
   NAIF_BODY_NAME                  += ( 'V_FRANCA' )

   FRAME_V_FRANCA_TOPO              =  1399506
   FRAME_1399506_NAME               = 'V_FRANCA_TOPO'
   FRAME_1399506_CLASS              =  4
   FRAME_1399506_CLASS_ID           =  1399506
   FRAME_1399506_CENTER             =   399506

   OBJECT_399506_FRAME              = 'V_FRANCA_TOPO'

   TKFRAME_V_FRANCA_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_V_FRANCA_TOPO_SPEC     = 'ANGLES'
   TKFRAME_V_FRANCA_TOPO_UNITS    = 'DEGREES'
   TKFRAME_V_FRANCA_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_V_FRANCA_TOPO_ANGLES   = ( 3.952, -49.557, 180.0 )

   NAIF_BODY_CODE                  += ( 399507 )
   NAIF_BODY_NAME                  += ( 'NEW_NORCIA' )

   FRAME_NEW_NORCIA_TOPO              =  1399507
   FRAME_1399507_NAME               = 'NEW_NORCIA_TOPO'
   FRAME_1399507_CLASS              =  4
   FRAME_1399507_CLASS_ID           =  1399507
   FRAME_1399507_CENTER             =   399507

   OBJECT_399507_FRAME              = 'NEW_NORCIA_TOPO'

   TKFRAME_NEW_NORCIA_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_NEW_NORCIA_TOPO_SPEC     = 'ANGLES'
   TKFRAME_NEW_NORCIA_TOPO_UNITS    = 'DEGREES'
   TKFRAME_NEW_NORCIA_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_NEW_NORCIA_TOPO_ANGLES   = ( -116.192, -121.048, 180.0 )

   NAIF_BODY_CODE                  += ( 399508 )
   NAIF_BODY_NAME                  += ( 'CEBREROS' )

   FRAME_CEBREROS_TOPO              =  1399508
   FRAME_1399508_NAME               = 'CEBREROS_TOPO'
   FRAME_1399508_CLASS              =  4
   FRAME_1399508_CLASS_ID           =  1399508
   FRAME_1399508_CENTER             =   399508

   OBJECT_399508_FRAME              = 'CEBREROS_TOPO'

   TKFRAME_CEBREROS_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_CEBREROS_TOPO_SPEC     = 'ANGLES'
   TKFRAME_CEBREROS_TOPO_UNITS    = 'DEGREES'
   TKFRAME_CEBREROS_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_CEBREROS_TOPO_ANGLES   = ( 4.367, -49.547, 180.0 )


   NAIF_BODY_CODE                  += ( 399509 )
   NAIF_BODY_NAME                  += ( 'MALINDI' )

   FRAME_MALINDI_TOPO              =  1399509
   FRAME_1399509_NAME               = 'MALINDI_TOPO'
   FRAME_1399509_CLASS              =  4
   FRAME_1399509_CLASS_ID           =  1399509
   FRAME_1399509_CENTER             =   399509

   OBJECT_399509_FRAME              = 'MALINDI_TOPO'

   TKFRAME_MALINDI_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_MALINDI_TOPO_SPEC     = 'ANGLES'
   TKFRAME_MALINDI_TOPO_UNITS    = 'DEGREES'
   TKFRAME_MALINDI_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_MALINDI_TOPO_ANGLES   = ( -40.196, -92.996, 180.0 )



   NAIF_BODY_CODE                  += ( 399510 )
   NAIF_BODY_NAME                  += ( 'SANTIAGO' )

   FRAME_SANTIAGO_TOPO              =  1399510
   FRAME_1399510_NAME               = 'SANTIAGO_TOPO'
   FRAME_1399510_CLASS              =  4
   FRAME_1399510_CLASS_ID           =  1399510
   FRAME_1399510_CENTER             =   399510

   OBJECT_399510_FRAME              = 'SANTIAGO_TOPO'

   TKFRAME_SANTIAGO_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_SANTIAGO_TOPO_SPEC     = 'ANGLES'
   TKFRAME_SANTIAGO_TOPO_UNITS    = 'DEGREES'
   TKFRAME_SANTIAGO_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_SANTIAGO_TOPO_ANGLES   = ( 70.668, -123.151, 180.0 )



   NAIF_BODY_CODE                  += ( 399511 )
   NAIF_BODY_NAME                  += ( 'SVALBARD' )

   FRAME_SVALBARD_TOPO              =  1399511
   FRAME_1399511_NAME               = 'SVALBARD_TOPO'
   FRAME_1399511_CLASS              =  4
   FRAME_1399511_CLASS_ID           =  1399511
   FRAME_1399511_CENTER             =   399511

   OBJECT_399511_FRAME              = 'SVALBARD_TOPO'

   TKFRAME_SVALBARD_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_SVALBARD_TOPO_SPEC     = 'ANGLES'
   TKFRAME_SVALBARD_TOPO_UNITS    = 'DEGREES'
   TKFRAME_SVALBARD_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_SVALBARD_TOPO_ANGLES   = ( -15.408, -11.77, 180.0 )



   NAIF_BODY_CODE                  += ( 399512 )
   NAIF_BODY_NAME                  += ( 'MALARGUE' )

   FRAME_MALARGUE_TOPO              =  1399512
   FRAME_1399512_NAME               = 'MALARGUE_TOPO'
   FRAME_1399512_CLASS              =  4
   FRAME_1399512_CLASS_ID           =  1399512
   FRAME_1399512_CENTER             =   399512

   OBJECT_399512_FRAME              = 'MALARGUE_TOPO'

   TKFRAME_MALARGUE_TOPO_RELATIVE = 'EARTH_FIXED'
   TKFRAME_MALARGUE_TOPO_SPEC     = 'ANGLES'
   TKFRAME_MALARGUE_TOPO_UNITS    = 'DEGREES'
   TKFRAME_MALARGUE_TOPO_AXES     = ( 3, 2, 3 )
   TKFRAME_MALARGUE_TOPO_ANGLES   = ( 69.39825, -125.77597, 180.0 )



\begintext
