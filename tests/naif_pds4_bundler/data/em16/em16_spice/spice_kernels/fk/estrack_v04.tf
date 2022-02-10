KPL/FK

Topocentric Frame kernel for the ESA ground stations
====================================================

   This is a frame kernel defining a topocentric reference frame for the ESA
   ground stations. Location data used to define this frame are taken from
   the ESA web pages.


Version and Date
-----------------------------------------------------------------------------

    Version 0.4 -- April 7, 2021 -- Alfredo Escalante Lopez, ESAC/ESA

       Fixed minor typos and updated contact information.

       Added Goonhilly GHY-6 station.

    Version 0.3 -- February 20, 2020 -- Boris Semenov, JPL
                                        Marc Costa Sitja, ESAC/ESA

       Improved ESTRACK stations coordinates for Kiruna 1, Kourou,
       Maspalomas, Perth, Redu, Santa Maria, Villafranca, New Norcia,
       Cebreros and Malargue.

    Version 0.2 -- January 10, 2020 -- Alfredo Escalante Lopez, ESAC/ESA
                                       Marc Costa Sitja, ESAC/ESA

       Improved ESTRACK stations coordinates for Kiruna 1, Kourou,
       Maspalomas, Perth, Redu, Santa Maria, Villafranca, New Norcia,
       Cebreros and Malargue.

       Added Kiruna 2 and New Norcia 2 stations.

    Version 0.1 -- November 21, 2012 -- Jose Luis Vazquez, ESAC/ESA

       Added Malargue definition.

    Version 0.0 -- March 22, 2011 -- Jose Luis Vazquez, ESAC/ESA

       Preliminary Version.


References
-----------------------------------------------------------------------------

   1. ``Frames Required Reading'', NAIF

   2. ``Kernel Pool Required Reading'', NAIF

   3. ``C-Kernel Required Reading'', NAIF

   4. ESTRACK NOW webpage. http://estracknow.esa.int/#/2019-10


Contact Information
-----------------------------------------------------------------------------

   If you have any questions regarding this file contact the ESA SPICE
   Service at ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           alfredo.escalante@esa.int


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


ESTRACK Stations Frames
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

   Disclaimer:
   ~~~~~~~~~~~

      Please note that the accuracy of these coordinates is in accordance with
      the public information provided by ESTRACK. Higher precision information
      for the New Norcia ground station exists and is available in
      NEW_NORCIA_TOPO.TF, that shall be used along with NEW_NORCIA.BSP.


   The data for the ground stations topocentric frames is defined as follows.

   \begindata

      NAIF_BODY_CODE                   += ( 399500 )
      NAIF_BODY_NAME                   += ( 'KI1' )
      NAIF_BODY_CODE                   += ( 399500 )
      NAIF_BODY_NAME                   += ( 'KIRUNA1' )

      FRAME_KIRUNA1_TOPO                =  1399500
      FRAME_1399500_NAME                = 'KIRUNA1_TOPO'
      FRAME_1399500_CLASS               =  4
      FRAME_1399500_CLASS_ID            =  1399500
      FRAME_1399500_CENTER              =   399500

      OBJECT_399500_FRAME               = 'KIRUNA1_TOPO'

      TKFRAME_KIRUNA1_TOPO_RELATIVE     = 'EARTH_FIXED'
      TKFRAME_KIRUNA1_TOPO_SPEC         = 'ANGLES'
      TKFRAME_KIRUNA1_TOPO_UNITS        = 'DEGREES'
      TKFRAME_KIRUNA1_TOPO_AXES         = ( 3, 2, 3 )
      TKFRAME_KIRUNA1_TOPO_ANGLES       = ( -20.964325, -22.1428757, 180.0 )


      NAIF_BODY_CODE                   += ( 399513 )
      NAIF_BODY_NAME                   += ( 'KI2' )
      NAIF_BODY_CODE                   += ( 399513 )
      NAIF_BODY_NAME                   += ( 'KIRUNA2' )

      FRAME_KIRUNA2_TOPO                =  1399513
      FRAME_1399513_NAME                = 'KIRUNA2_TOPO'
      FRAME_1399513_CLASS               =  4
      FRAME_1399513_CLASS_ID            =  1399513
      FRAME_1399513_CENTER              =   399513

      OBJECT_399513_FRAME               = 'KIRUNA2_TOPO'

      TKFRAME_KIRUNA2_TOPO_RELATIVE     = 'EARTH_FIXED'
      TKFRAME_KIRUNA2_TOPO_SPEC         = 'ANGLES'
      TKFRAME_KIRUNA2_TOPO_UNITS        = 'DEGREES'
      TKFRAME_KIRUNA2_TOPO_AXES         = ( 3, 2, 3 )
      TKFRAME_KIRUNA2_TOPO_ANGLES       = ( -20.9668808, -22.141571, 180.0 )


      NAIF_BODY_CODE                   += ( 399501 )
      NAIF_BODY_NAME                   += ( 'KRU' )
      NAIF_BODY_CODE                   += ( 399501 )
      NAIF_BODY_NAME                   += ( 'KOUROU' )

      FRAME_KOUROU_TOPO                 =  1399501
      FRAME_1399501_NAME                = 'KOUROU_TOPO'
      FRAME_1399501_CLASS               =  4
      FRAME_1399501_CLASS_ID            =  1399501
      FRAME_1399501_CENTER              =   399501

      OBJECT_399501_FRAME               = 'KOUROU_TOPO'

      TKFRAME_KOUROU_TOPO_RELATIVE      = 'EARTH_FIXED'
      TKFRAME_KOUROU_TOPO_SPEC          = 'ANGLES'
      TKFRAME_KOUROU_TOPO_UNITS         = 'DEGREES'
      TKFRAME_KOUROU_TOPO_AXES          = ( 3, 2, 3 )
      TKFRAME_KOUROU_TOPO_ANGLES        = ( 52.8046646, -84.7485609, 180.0 )


      NAIF_BODY_CODE                   += ( 399502 )
      NAIF_BODY_NAME                   += ( 'MSP' )
      NAIF_BODY_CODE                   += ( 399502 )
      NAIF_BODY_NAME                   += ( 'MASPALOMAS' )

      FRAME_MASPALOMAS_TOPO               =  1399502
      FRAME_1399502_NAME                = 'MASPALOMAS_TOPO'
      FRAME_1399502_CLASS               =  4
      FRAME_1399502_CLASS_ID            =  1399502
      FRAME_1399502_CENTER              =   399502

      OBJECT_399502_FRAME               = 'MASPALOMAS_TOPO'

      TKFRAME_MASPALOMAS_TOPO_RELATIVE  = 'EARTH_FIXED'
      TKFRAME_MASPALOMAS_TOPO_SPEC      = 'ANGLES'
      TKFRAME_MASPALOMAS_TOPO_UNITS     = 'DEGREES'
      TKFRAME_MASPALOMAS_TOPO_AXES      = ( 3, 2, 3 )
      TKFRAME_MASPALOMAS_TOPO_ANGLES    = ( 15.633800, -62.237111, 180.0 )


      NAIF_BODY_CODE                   += ( 399503 )
      NAIF_BODY_NAME                   += ( 'PER' )
      NAIF_BODY_CODE                   += ( 399503 )
      NAIF_BODY_NAME                   += ( 'PERTH' )

      FRAME_PERTH_TOPO                  =  1399503
      FRAME_1399503_NAME                = 'PERTH_TOPO'
      FRAME_1399503_CLASS               =  4
      FRAME_1399503_CLASS_ID            =  1399503
      FRAME_1399503_CENTER              =   399503

      OBJECT_399503_FRAME               = 'PERTH_TOPO'

      TKFRAME_PERTH_TOPO_RELATIVE       = 'EARTH_FIXED'
      TKFRAME_PERTH_TOPO_SPEC           = 'ANGLES'
      TKFRAME_PERTH_TOPO_UNITS          = 'DEGREES'
      TKFRAME_PERTH_TOPO_AXES           = ( 3, 2, 3 )
      TKFRAME_PERTH_TOPO_ANGLES         = ( -115.885161, -121.802522, 180.0 )


      NAIF_BODY_CODE                   += ( 399504 )
      NAIF_BODY_NAME                   += ( 'RED' )
      NAIF_BODY_CODE                   += ( 399504 )
      NAIF_BODY_NAME                   += ( 'REDU' )

      FRAME_REDU_TOPO                   =  1399504
      FRAME_1399504_NAME                = 'REDU_TOPO'
      FRAME_1399504_CLASS               =  4
      FRAME_1399504_CLASS_ID            =  1399504
      FRAME_1399504_CENTER              =   399504

      OBJECT_399504_FRAME               = 'REDU_TOPO'

      TKFRAME_REDU_TOPO_RELATIVE        = 'EARTH_FIXED'
      TKFRAME_REDU_TOPO_SPEC            = 'ANGLES'
      TKFRAME_REDU_TOPO_UNITS           = 'DEGREES'
      TKFRAME_REDU_TOPO_AXES            = ( 3, 2, 3 )
      TKFRAME_REDU_TOPO_ANGLES          = ( -5.1453438, -39.9995422, 180.0 )


      NAIF_BODY_CODE                   += ( 399505 )
      NAIF_BODY_NAME                   += ( 'SMA' )
      NAIF_BODY_CODE                   += ( 399505 )
      NAIF_BODY_NAME                   += ( 'STA_MARIA' )

      FRAME_STA_MARIA_TOPO              =  1399505
      FRAME_1399505_NAME                = 'STA_MARIA_TOPO'
      FRAME_1399505_CLASS               =  4
      FRAME_1399505_CLASS_ID            =  1399505
      FRAME_1399505_CENTER              =   399505

      OBJECT_399505_FRAME               = 'STA_MARIA_TOPO'

      TKFRAME_STA_MARIA_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_STA_MARIA_TOPO_SPEC       = 'ANGLES'
      TKFRAME_STA_MARIA_TOPO_UNITS      = 'DEGREES'
      TKFRAME_STA_MARIA_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_STA_MARIA_TOPO_ANGLES     = ( 25.1357212, -53.0027504, 180.0 )


      NAIF_BODY_CODE                   += ( 399506 )
      NAIF_BODY_NAME                   += ( 'VFA' )
      NAIF_BODY_CODE                   += ( 399506 )
      NAIF_BODY_NAME                   += ( 'V_FRANCA' )

      FRAME_V_FRANCA_TOPO               =  1399506
      FRAME_1399506_NAME                = 'V_FRANCA_TOPO'
      FRAME_1399506_CLASS               =  4
      FRAME_1399506_CLASS_ID            =  1399506
      FRAME_1399506_CENTER              =   399506

      OBJECT_399506_FRAME               = 'V_FRANCA_TOPO'

      TKFRAME_V_FRANCA_TOPO_RELATIVE    = 'EARTH_FIXED'
      TKFRAME_V_FRANCA_TOPO_SPEC        = 'ANGLES'
      TKFRAME_V_FRANCA_TOPO_UNITS       = 'DEGREES'
      TKFRAME_V_FRANCA_TOPO_AXES        = ( 3, 2, 3 )
      TKFRAME_V_FRANCA_TOPO_ANGLES      = ( 3.9515833, -49.5574361, 180.0 )


      NAIF_BODY_CODE                   += ( 398990 )
      NAIF_BODY_NAME                   += ( 'NNO' )
      NAIF_BODY_CODE                   += ( 398990 )
      NAIF_BODY_NAME                   += ( 'NNORCIA' )
      NAIF_BODY_CODE                   += ( 398990 )
      NAIF_BODY_NAME                   += ( 'NEW_NORCIA' )

      FRAME_NEW_NORCIA_TOPO             =  1398990
      FRAME_1398990_NAME                = 'NEW_NORCIA_TOPO'
      FRAME_1398990_CLASS               =  4
      FRAME_1398990_CLASS_ID            =  1398990
      FRAME_1398990_CENTER              =   398990

      OBJECT_398990_FRAME               = 'NEW_NORCIA_TOPO'

      TKFRAME_NEW_NORCIA_TOPO_RELATIVE  = 'EARTH_FIXED'
      TKFRAME_NEW_NORCIA_TOPO_SPEC      = 'ANGLES'
      TKFRAME_NEW_NORCIA_TOPO_UNITS     = 'DEGREES'
      TKFRAME_NEW_NORCIA_TOPO_AXES      = ( 3, 2, 3 )
      TKFRAME_NEW_NORCIA_TOPO_ANGLES    = (-116.1914978, -121.0482254, 180.0)


      NAIF_BODY_CODE                   += ( 398991 )
      NAIF_BODY_NAME                   += ( 'NNO2' )
      NAIF_BODY_CODE                   += ( 398991 )
      NAIF_BODY_NAME                   += ( 'NNORCIA2' )
      NAIF_BODY_CODE                   += ( 398991 )
      NAIF_BODY_NAME                   += ( 'NEW_NORCIA2' )
      NAIF_BODY_CODE                   += ( 398991 )
      NAIF_BODY_NAME                   += ( 'NEW_NORCIA_2' )

      FRAME_NNORCIA2_TOPO               =  1398991
      FRAME_1398991_NAME                = 'NNORCIA2_TOPO'
      FRAME_1398991_CLASS               =  4
      FRAME_1398991_CLASS_ID            =  1398991
      FRAME_1398991_CENTER              =   398991

      OBJECT_398991_FRAME               = 'NNORCIA2_TOPO'

      TKFRAME_NNORCIA2_TOPO_RELATIVE    = 'EARTH_FIXED'
      TKFRAME_NNORCIA2_TOPO_SPEC        = 'ANGLES'
      TKFRAME_NNORCIA2_TOPO_UNITS       = 'DEGREES'
      TKFRAME_NNORCIA2_TOPO_AXES        = ( 3, 2, 3 )
      TKFRAME_NNORCIA2_TOPO_ANGLES      = (-116.1888123, -121.0488949, 180.0)


      NAIF_BODY_CODE                  += ( 399508 )
      NAIF_BODY_NAME                  += ( 'CEB' )
      NAIF_BODY_CODE                  += ( 399508 )
      NAIF_BODY_NAME                  += ( 'CEBREROS' )

      FRAME_CEBREROS_TOPO              =  1399508
      FRAME_1399508_NAME               = 'CEBREROS_TOPO'
      FRAME_1399508_CLASS              =  4
      FRAME_1399508_CLASS_ID           =  1399508
      FRAME_1399508_CENTER             =   399508

      OBJECT_399508_FRAME              = 'CEBREROS_TOPO'

      TKFRAME_CEBREROS_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_CEBREROS_TOPO_SPEC       = 'ANGLES'
      TKFRAME_CEBREROS_TOPO_UNITS      = 'DEGREES'
      TKFRAME_CEBREROS_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_CEBREROS_TOPO_ANGLES     = ( 4.3675499, -49.5473099, 180.0 )


      NAIF_BODY_CODE                  += ( 399509 )
      NAIF_BODY_NAME                  += ( 'MLI' )
      NAIF_BODY_CODE                  += ( 399509 )
      NAIF_BODY_NAME                  += ( 'MALINDI' )

      FRAME_MALINDI_TOPO               =  1399509
      FRAME_1399509_NAME               = 'MALINDI_TOPO'
      FRAME_1399509_CLASS              =  4
      FRAME_1399509_CLASS_ID           =  1399509
      FRAME_1399509_CENTER             =   399509

      OBJECT_399509_FRAME              = 'MALINDI_TOPO'

      TKFRAME_MALINDI_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_MALINDI_TOPO_SPEC       = 'ANGLES'
      TKFRAME_MALINDI_TOPO_UNITS      = 'DEGREES'
      TKFRAME_MALINDI_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_MALINDI_TOPO_ANGLES     = ( -40.196, -92.996, 180.0 )


      NAIF_BODY_CODE                  += ( 399510 )
      NAIF_BODY_NAME                  += ( 'SGO' )
      NAIF_BODY_CODE                  += ( 399510 )
      NAIF_BODY_NAME                  += ( 'SANTIAGO' )

      FRAME_SANTIAGO_TOPO              =  1399510
      FRAME_1399510_NAME               = 'SANTIAGO_TOPO'
      FRAME_1399510_CLASS              =  4
      FRAME_1399510_CLASS_ID           =  1399510
      FRAME_1399510_CENTER             =   399510

      OBJECT_399510_FRAME              = 'SANTIAGO_TOPO'

      TKFRAME_SANTIAGO_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_SANTIAGO_TOPO_SPEC       = 'ANGLES'
      TKFRAME_SANTIAGO_TOPO_UNITS      = 'DEGREES'
      TKFRAME_SANTIAGO_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_SANTIAGO_TOPO_ANGLES     = ( 70.668, -123.151, 180.0 )


      NAIF_BODY_CODE                  += ( 399511 )
      NAIF_BODY_NAME                  += ( 'SVB' )
      NAIF_BODY_CODE                  += ( 399511 )
      NAIF_BODY_NAME                  += ( 'SVALBARD' )

      FRAME_SVALBARD_TOPO              =  1399511
      FRAME_1399511_NAME               = 'SVALBARD_TOPO'
      FRAME_1399511_CLASS              =  4
      FRAME_1399511_CLASS_ID           =  1399511
      FRAME_1399511_CENTER             =   399511

      OBJECT_399511_FRAME              = 'SVALBARD_TOPO'

      TKFRAME_SVALBARD_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_SVALBARD_TOPO_SPEC       = 'ANGLES'
      TKFRAME_SVALBARD_TOPO_UNITS      = 'DEGREES'
      TKFRAME_SVALBARD_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_SVALBARD_TOPO_ANGLES     = ( -15.408, -11.77, 180.0 )


      NAIF_BODY_CODE                  += ( 399512 )
      NAIF_BODY_NAME                  += ( 'MLG' )
      NAIF_BODY_CODE                  += ( 399512 )
      NAIF_BODY_NAME                  += ( 'MALARGUE' )

      FRAME_MALARGUE_TOPO              =  1399512
      FRAME_1399512_NAME               = 'MALARGUE_TOPO'
      FRAME_1399512_CLASS              =  4
      FRAME_1399512_CLASS_ID           =  1399512
      FRAME_1399512_CENTER             =   399512

      OBJECT_399512_FRAME              = 'MALARGUE_TOPO'

      TKFRAME_MALARGUE_TOPO_RELATIVE   = 'EARTH_FIXED'
      TKFRAME_MALARGUE_TOPO_SPEC       = 'ANGLES'
      TKFRAME_MALARGUE_TOPO_UNITS      = 'DEGREES'
      TKFRAME_MALARGUE_TOPO_AXES       = ( 3, 2, 3 )
      TKFRAME_MALARGUE_TOPO_ANGLES     = ( 69.3981934, -125.7760086, 180.0 )


      NAIF_BODY_CODE                  += ( 399514 )
      NAIF_BODY_NAME                  += ( 'GHY' )
      NAIF_BODY_CODE                  += ( 399514 )
      NAIF_BODY_NAME                  += ( 'GOONHILLY' )

      FRAME_GOONHILLY_TOPO             =  1399514
      FRAME_1399514_NAME               = 'GOONHILLY_TOPO'
      FRAME_1399514_CLASS              =  4
      FRAME_1399514_CLASS_ID           =  1399514
      FRAME_1399514_CENTER             =   399514

      OBJECT_399514_FRAME              = 'GOONHILLY_TOPO'

      TKFRAME_GOONHILLY_TOPO_RELATIVE  = 'EARTH_FIXED'
      TKFRAME_GOONHILLY_TOPO_SPEC      = 'ANGLES'
      TKFRAME_GOONHILLY_TOPO_UNITS     = 'DEGREES'
      TKFRAME_GOONHILLY_TOPO_AXES      = ( 3, 2, 3 )
      TKFRAME_GOONHILLY_TOPO_ANGLES    = ( -5.183271, -39.949564, 180.0 )

   \begintext


End of FK file.
