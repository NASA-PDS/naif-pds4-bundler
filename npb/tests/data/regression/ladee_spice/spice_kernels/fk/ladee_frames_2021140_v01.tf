KPL/FK

LADEE Frame Definitions Kernel
==============================================================================

   This frame kernel contains the LADEE spacecraft and science instrument
   frame definitions. This frame kernel also contains name - to - NAIF
   ID mappings for LADEE science instruments and s/c structures (see the
   last section of the file.)


Version and Date
--------------------------------------------------------

   Version 0.9 -- May 20, 2021 -- Marc Costa Sitja

      Minor corrections in descriptive text and formatting.

   Version 0.8 -- June 8, 2014 -- Mark Shirley

      Added ECLIPDATE, LADEE_SSE, LADEE_MF, and LADEE_LVLH frames.

   Version 0.7 -- December 18, 2013 -- Boris V. Semenov

      Updated the UVS Solar Viewer frame alignment based on the 
      on-orbit calculated UVS Solar Viewer boresight direction.

   Version 0.6 -- October 16, 2013 -- Boris V. Semenov, Joseph A. Hashmall

      Redefined LDEX frames based on the information provided by the
      instrument team.

   Version 0.5 -- October 16, 2013 -- Boris V. Semenov, Joseph A. Hashmall

      Redefined NMS and UVS frames based on the information provided 
      by the instrument teams.

   Version 0.4 -- October 7, 2013 -- Boris V. Semenov

      Changed rotation from BUS to PROP from -45 to +45. Updated the
      diagram showing the relationship between BUS and PROP frames.

   Version 0.3 -- September 20, 2013 -- Boris V. Semenov

      Fixed 'FRAME_<name> = <id>' keyword in the LADEE_SC_PROP frame
      definition. Removed unnecessary CK_*_SCLK and CK_*_SPK in all
      fixed offset (class 4) frames. Reset CENTER_ID in all frames to
      LADEE spacecraft ID (-12). Reinstated the NAIF body name-ID
      mapping section. Corrected frame summary table and frame diagram.
      Indented comments and wrapped them to 72 character page width (for
      consistency with comments in FKs for other missions.)

   Version 0.2 -- April 24, 2013 -- Joseph A. Hashmall

      Adds reference 5 and definitions in it 

   Version 0.1 -- March 20, 2013 -- Joseph A. Hashmall

      Contains corrections identified by Boris Semenov

   Version 0.0 draft -- January 28, 2013 -- Joseph A. Hashmall

      Initial Release. Contains Euler angles from LADEE Engineering diagrams.


References
--------------------------------------------------------

   1. C-kernel Required Reading

   2. Kernel Pool Required Reading

   3. Frames Required Reading

   4. Lunar Atmosphere and Dust Environment Explorer (LADEE) Alignment 
      Plan ("IT.070.LADEE.ALIGN_Rev_A.pdf")

   5. Lunar Atmosphere and Dust Environment Explorer (LADEE) Project
      LADEE GN&C Coordinate System Document ("LADEE GN&C Coordinate Frames 
      Document_RevNC(Draft).docx")

   6. LADEE Metrology Results Spreadsheet ("LADEE post-ship metrology 
      results 6-11.xlsx")

   7. LADEE NMS boresight-to-cube alignment PowerPoint summary slide 
      (LADEE_Alignment.pptx)

   8. UVS frame specification and alignment summary, e-mail from 
      Mark Shirley, NASA/AMES, 10/15/13.

   9. LDEX frame specification, e-mail from Sam Gagnard, LASP, 10/16/13

   10. On-orbit calculated UVS Solar Viewer boresight direction, 
       e-mail from Mark Shirley, NASA/AMES, 12/18/13.


Contact Information
--------------------------------------------------------

   Joseph A. Hashmall, a.i.solutions, Inc., (301)-306-1756X120,
   joseph.hashmall@ai-solutions.com


Implementation Notes
--------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make
   use of this frame kernel must ``load'' the kernel, normally during
   program initialization. The SPICELIB routine FURNSH loads a kernel
   file into the pool as shown below.

      CALL FURNSH ( 'frame_kernel_name; )       -- FORTRAN
      furnsh_c ( "frame_kernel_name" );         -- C
      cspice_furnsh, "frame_kernel_name"        -- IDL
      cspice_furnsh ( 'frame_kernel_name' );    -- MATLAB

   This file was created and may be updated with a text editor or word
   processor.


LADEE Payload Description (for FRAMES)
--------------------------------------------------------

   LDEX:

      The Lunar Dust EXperiment (LDEX) instrument is an impact
      ionization dust detector. Its overall size is comparable to a
      bread box and it consists of three main sections: an Electronics
      Box Assembly, a Front End Detector, and an Aperture Door
      Assembly.

   NMS:

      Neutral Mass Spectometer (NMS) is a high sensitivity quadrupole
      mass spectrometer with a mass range from 2 to 150 Dalton and unit
      mass resolution. For lunar orbits of 50 km or lower NMS can
      detect helium, argon and other species either released from the
      deep lunar interior or from the surface of the moon.


   UVS:

      The Ultraviolet and Visible light Spectrometer (UVS) science
      instrument consists of a spectrometer, a limb viewing telescope,
      and a solar viewing optic. The instrument is operated in two
      modes: 1) limb viewing, using the limb viewing telescope and 2)
      solar occultation viewing, using the solar viewing optic. In limb
      viewing mode, the UVS limb telescope is pointed above the lunar
      surface in the direction of spacecraft (s/c) flight. In
      occultation mode, the UVS uses its solar viewing optic to monitor
      the sun as it sets/rises across the lunar limb.


LADEE Frames
--------------------------------------------------------

   The following LADEE frames are defined in this kernel file:

        Frame Name                 Relative to              Type    NAIF ID
   ======================     =========================    =======  =======

   Spacecraft Bus and Spacecraft Structure Frames:
   -----------------------------------------------

      LADEE_SC_PROP           rel.to J2000                 CK      -12000

      LADEE_SC_BUS            rel.to SC_PROP               FIXED   -12100


   Instrument Frames:
   ------------------

      LADEE_LDEX              rel.to SC_PROP               FIXED   -12200

      LADEE_NMS               rel.to SC_PROP               FIXED   -12300

      LADEE_UVSTEL            rel.to SC_PROP               FIXED   -12400

      LADEE_UVSSOL            rel.to SC_PROP               FIXED   -12500


   Dynamic Frames:
   ---------------

      ECLIPDATE               rel.to J2000                 DYNAMIC -12600

      LADEE_SSE               rel.to ECLIPDATE             DYNAMIC -12605

      LADEE_MF                rel.to J2000                 DYNAMIC -12606

      LADEE_LVLH              rel.to J2000                 DYNAMIC -12607


LADEE Frames Hierarchy
--------------------------------------------------------

   The diagram below shows the LADEE frame hierarchy:


                               "J2000" INERTIAL
               +------------------------------------------------------+
               |          |          |          |          |          |
               |          |<--pck    | <--pck   |<--dyn    |<--dyn    |<--dyn
               |          |          |          |          |          |
               |          V          V          |          V          |
               |      "MOON_ME"   "IAU_EARTH"   |     "ECLIPDATE"     |
               |      ---------   -----------   |     -----------     |
               |                                |          |          |
               |                                |          |<--dyn    |
               |                                |          |          |
               |                                V          V          V
               |                        "LADEE_LVLH"  "LADEE_SSE"  "LADEE_MF"
               |                        ------------  -----------  ----------
               |
               |
               |
               |                      
               |                      
               |                          "LADEE_SC_BUS"
               |                          --------------- 
               |                                ^
               |<--ck                           |<-fixed 
               |                                |
               V                                |
          "LADEE_SC_PROP"                       |
        +-----------------------------------------------+
        |               |               |               |
        |               |               |               |
        |<--fixed       |<--fixed       |<-fixed        |<-fixed
        |               |               |               |
        V               V               V               V
     "LADEE_LDEX"    "LADEE_NMS"    "LADEE_UVSTEL"   "LADEE_UVSSOL"
     ------------    -----------    --------------   --------------


Spacecraft PROP Frame
--------------------------------------------------------

   The Spacecraft Propulsion (PROP) Frame, LADEE_SC_PROP, also known as
   the GNC Frame, is the spacecraft frame the orientation of which
   relative to inertial space is provided in telemetry and stored in
   LADEE CK files (see [1]). It is defined by the spacecraft design as
   follows (see [5]):

      -  +Z axis is perpendicular to the propulsion deck in the
          direction of thrust

      -  +Y axis points towards the edge between solar panels 1 and 2
         (RCS thruster 1 and 2 assembly).

      -  +X axis completes the right handed frame.

   This diagram illustrates the PROP frame:
   
 
                                    |
                                 ..` `..LLCD    
                          `  ..``   |   ``..
                            `   P4     P3  '
                           /  `     |UVS  '  \ 
                    RCS3  / P5  `       '  P2 \  RCS1
                        #/        ` | '        \#   
                       - - - - - - -o--------------> +Yprop
                        #\        . | .        /#
                    RCS4  \ P6  .   |   .  P1 /  RCS2
                           \  . LDEX|     .  / Panel1
                            .   P7  |  P8   .
                             ``..   |   ..``
                              NMS``.|.``       
                                    |    
                                    V
                                     +Xprop
                                                 +Zprop is out of the page.

   The PROP frame is defined below as a CK-based frame.

   \begindata

      FRAME_LADEE_SC_PROP      = -12000
      FRAME_-12000_NAME        = 'LADEE_SC_PROP'
      FRAME_-12000_CLASS       = 3
      FRAME_-12000_CLASS_ID    = -12000
      FRAME_-12000_CENTER      = -12
      CK_-12000_SCLK           = -12
      CK_-12000_SPK            = -12

   \begintext


Spacecraft Bus (BUILD) Frame
--------------------------------------------------------

   The spacecraft bus frame, LADEE_SC_BUS, also known as the BUILD
   frame, is defined by the spacecraft design as follows (see [4] and
   [5]):

      -  +Z axis is perpendicular to the propulsion deck in the
          direction of thrust

      -  +Y axis points towards the edge between solar panels 2 and 3
         (between the low and medium gain antennas).

      -  +X axis completes the right handed frame.

   This diagram shows the relationship between the BUILD frame and the
   PROP frame:

                                    |
                                 ..` `..LLCD    
                          `  ..``   |   ``.. .> +Ybuild
                            `              .'
                           /  `     |UVS .'  \
                          /     `      .'     \
                        #/        ` |.'        \#   +Yprop
                       - - - - - - -o-------------->
                        #\        . |`.        /#
                          \     .   |  `.     /
                           \  . LDEX|    `.  /
                            .       |      `.
                             ``..   |   ..`` `> +Xbuild
                              NMS``.|.``       
                                    |              .
                                    V               >.
                                     +Xprop     ..`   `
                                            ..``
                                        ..``  45 deg
                                    |<``
                                                 +Zprop and +Zbuild are 
                                                   out of the page.

   As seen on the diagram, nominally a single rotation of +45 degrees 
   about Z is needed to align the PROP frame with the BUILD frame:

      Mprop->build = [+45]z

      Vbuild = Mprop->build * Vprop

   The BUILD frame is defined below as a fixed offset frame relative to
   the PROP frame. 

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_LADEE_SC_BUS       = -12100
      FRAME_-12100_NAME        = 'LADEE_SC_BUS'
      FRAME_-12100_CLASS       =  4
      FRAME_-12100_CLASS_ID    = -12100
      FRAME_-12100_CENTER      = -12
      TKFRAME_-12100_SPEC      = 'ANGLES'
      TKFRAME_-12100_RELATIVE  = 'LADEE_SC_PROP'
      TKFRAME_-12100_ANGLES    = (   0.0,   0.0, -45.0  )
      TKFRAME_-12100_AXES      = (   3,     2,     3    )
      TKFRAME_-12100_UNITS     = 'DEGREES'

   \begintext


Lunar Dust EXperiment (LDEX) Frame
--------------------------------------------------------

   According to [9], the LDEX frame, LADEE_LDEX, is defined as follows:

      -  +Z axis is along the instrument boresight

      -  +Y axis is nominally in the direction of the s/c +Z axis

      -  +X axis completes the right handed frame.

   This diagram shows the LDEX frame:

                                    |
                                 ..` `..LLCD    
                          `  ..``   |   ``.. .> +Ybuild
                            `              .'
                           /  `     |UVS .'  \
                          /     `      .'     \
                        #/        ` |.'        \#   +Yprop
                       - - - - - - -o-------------->
                        #\        . |`.        /#
                          \     .   |  `.     /
                           \  . LDEX|    `.  /
                            .   `o./|      `.
                          .  ``./  ``.. ..`` `> +Xbuild
                               /NMS.|. `>      
                              /     |    +Xldex
          +Zldex (boresight) V      V
                                     +Xprop
                            
                            22.5 deg
                         /<-------->|
                             
                                                +Zprop and +Zbuild are 
                                                   out of the page.

                                               +Yldex is out of the page.

   As seen on the diagram, nominally three rotations are needed to 
   to align the PROP frame with the LDEX frame: first by -22.5 degrees 
   about Z, then by +90 degrees about Y, then +90 degrees about Z:

      Mprop->ldex = [+90]z * [+90]y * [-22.5]z

      Vldex = Mprop->ldex * Vprop

   From spreadsheet "LADEE post-ship metrology results 6-11.xlsx", 
   sheet "LADEE Build-Prop-STB CS 6-10", table "Pre-Ship 5-13"

      LDEX front cover for boresight:  0.92395374 -0.38250286 -0.00102228

   Using this direction and aligning +Z exactly with it while keeping
   +Y as close as possible to the PROP frame's Z axis, we get the
   following sequence of rotations aligning the PROP frame with the
   LDEX frame (based on the measured cover face normal direction
   representing the boresight):

      Mprop->ldex = [+90.00000000]z * [+90.05857234]y * [-22.48881442]z

      Vldex = Mprop->ldex * Vprop

   The LDEX frame is defined below as a fixed offset frame relative to
   the PROP frame.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_LADEE_LDEX         = -12200
      FRAME_-12200_NAME        = 'LADEE_LDEX'
      FRAME_-12200_CLASS       = 4
      FRAME_-12200_CLASS_ID    = -12200
      FRAME_-12200_CENTER      = -12
      TKFRAME_-12200_SPEC      = 'ANGLES'
      TKFRAME_-12200_RELATIVE  = 'LADEE_SC_PROP'
      TKFRAME_-12200_ANGLES    = ( +22.48881442, -90.05857234, -90.00000000 )
      TKFRAME_-12200_AXES      = (   3,            2,            3          ) 
      TKFRAME_-12200_UNITS     = 'DEGREES'

   \begintext


Neutral Mass Spectrometer (NMS) Frame
--------------------------------------------------------

   According to [7], the NMS frame, LADEE_NMS, is defined as follows:

      -  +Z axis is along the instrument boresight

      -  +X axis is nominally in the direction of the s/c +Z axis 
          (this is apparent from looking at [7] and actual photos of
          the NMS mounted on the s/c.)

      -  +Y completes the right handed frame.

   This diagram shows the NMS frame:


                                    |    
                                 ..` `..LLCD    
                          `  ..``   |   ``.. .> +Ybuild
                            `              .'
                           /  `     |UVS .'  \
                          /     `      .'     \
                        #/        ` |.'        \#   +Yprop
                       - - - - - - -o-------------->
                        #\        . |`.        /#
                          \     .   |  `.     /
                           \  . LDEX|    `.  /
                            .       |      `.
               +Ynms      . /``..   |   ..`` `> +Xbuild
                     < ..  /  NMS``.|.``       
                         ``..     / |
                             o`../  V
                            /        +Xprop
                           /
                          /
                         V
                          +Znms (boresight)

                         22.5 deg    
                     /<------------>|
                                                +Zprop and +Zbuild are 
                                                   out of the page.

                                                +Xnms is out of the page.

   As seen on the diagram, nominally three rotations are needed to 
   to align the PROP frame with the NMS frame: first by -22.5 degrees 
   about Z, then by +90 degrees about Y, then 180 degrees about Z:

      Mprop->nms = [180]z * [+90]y * [-22.5]z

      Vnms = Mprop->nms * Vprop

   From spreadsheet "LADEE post-ship metrology results 6-11.xlsx", 
   sheet "LADEE Build-Prop-STB CS 6-10", table "Pre-Ship 5-13"

       NMS Cube +X   0.38433103  0.92318405  0.00456912
       NMS Cube -Y   0.92318612 -0.38434148 -0.00300386

   Let's disregard the NMS cube axis assignments used in the metrology and 
   pretend that the cube frame is defined to be nominally co-aligned 
   with the NMS instrument frame. Then the two vectors above will 
   correspond to the following NMS frame axes:

       NMS frame -Y  0.38433103  0.92318405  0.00456912
       NMS frame +Z  0.92318612 -0.38434148 -0.00300386

   or, negating the "NMS frame -Y" vector, to these two axes

       NMS frame +Y -0.38433103 -0.92318405 -0.00456912
       NMS frame +Z  0.92318612 -0.38434148 -0.00300386

   Using these two directions and, because the vectors are slightly
   non-orthogonal, aligning +Z exactly with its vector while keeping +Y
   as close as possible to its vector, we get the following sequence
   of rotations aligning the PROP frame with the NMS frame (based on 
   the measured cube face normal directions):

      Mprop->nmsc = [-179.73821050]z * [+90.17210876]y * [-22.60297214]z

      Vnmsc = Mprop->nmsc * Vprop

   To take into account the offset of the instrument boresight from its
   cube shown in LADEE_Alignment.pptx we build a matrix that rotates
   the cube frame first by -5.202 mrad about X, then by 7.359 mrad
   about Y: 

      Mnmsc->nms = [0.007359]y * [-0.005202]x

      Vnms = Mnmsc->nms * Vnmsc

   (Note although the document does not specify the rotation order or
   even whether these angles are rotation angles or offset angles, we
   can arbitrarily treat them as rotation angles and pick any order of
   rotations, because the angles are very small and uncertainties of
   their measurement are relatively big.)

   Combining these two rotations

      Mprop->nms = Mnmsc->nms * Mprop->nmsc

   and decomposing the resultant matrix into the same sequence of
   rotation angles we get:

      Mprop->nms = [-179.73910809]z * [+89.75183298]y * [-22.90294292]z

      Vnms = Mprop->nms * Vprop

   The NMS frame is defined below as a fixed offset frame relative to
   the PROP frame.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what is specified in the description above.

   \begindata

      FRAME_LADEE_NMS          = -12300
      FRAME_-12300_NAME        = 'LADEE_NMS'
      FRAME_-12300_CLASS       = 4
      FRAME_-12300_CLASS_ID    = -12300
      FRAME_-12300_CENTER      = -12
      TKFRAME_-12300_SPEC      = 'ANGLES'
      TKFRAME_-12300_RELATIVE  = 'LADEE_SC_PROP'
      TKFRAME_-12300_ANGLES    = ( 22.90294292, -89.75183298, 179.73910809 )
      TKFRAME_-12300_AXES      = (  3,            2,            3          )
      TKFRAME_-12300_UNITS     = 'DEGREES'

   \begintext


Ultraviolet Spectrometer (UVS) Frames
--------------------------------------------------------

   The UVS has two detectors -- Solar Occultation Viewer and Telescope.
   The two sections below define two separate frames, one for each of
   the detectors.


UVS Solar Occultation Viewer Reference Frame
 
   According to [8], the UVS Solar frame, LADEE_UVSSOL, is defined as
   follows:

      -  +Z axis is along the instrument boresight

      -  +Y axis is nominally in the direction of the s/c +Z axis 

      -  +X completes the right handed frame.

   This diagram shows the UVS Solar frame:


                                    |  22.5 deg  /
                                    |<--------->/

                         +Xuvs-s    |         ^ +Zuvs-s (boresight)
                                 <. |        /
                                   '.       /
                                 ..` `..   /   
                          `  ..``   |   `.o   .> +Ybuild
                            `           //  .'
                           /  `     |UVS`.'  \
                          /     `      .'     \
                        #/        ` |.'        \#   +Yprop
                       - - - - - - -o-------------->
                        #\        . |`.        /#
                          \     .   |  `.     /
                           \  . LDEX|    `.  /
                            .       |      `.
                          .  ``.    |   ..`` `> +Xbuild
                              NMS``.|.``       
                                    |
                                    V
                                     +Xprop

                                                +Zprop and +Zbuild are 
                                                   out of the page.

                                              +Yuvs-s is out of the page.

   As seen on the diagram, nominally three rotations are needed to to
   align the PROP frame with the UVS Solar frame: first by +157.5
   degrees about Z, then by +90 degrees about Y, then +90 degrees about
   Z:

      Mprop->uvs-s = [+90]z * [+90]y * [+157.5]z

      Vuvs-s = Mprop->uvs-s * Vprop

   According to Mark's e-mail citing the LADEE metrology report and the
   UVS alignment report ([10]), the quaternion (with the the scalar given
   as the last element) relating the LADEE prop frame and the UVS body
   frame is

      {-0.000265, -0.000897, 0.651057, 0.759028}

   and the measured boresight vector of the Solar Viewer in the UVS
   body frame is

      0.228893304, 0.973213346, 0.021532259

   By (a) converting the quaternion to the matrix rotating vectors from
   the PROP frame to the UVS body frame, (b) creating a rotation from
   the UVS body frame to the UVS Solar frame by forcing the UVS
   Solar frame +Z be along the boresight direction given above and
   the UVS Solar frame +Y be aligned as closely as possible with
   the UVS body frame +Z, (c) combining these two rotations, and (d)
   decomposing the resulting matrix into three rotation angles with the
   same sequence as the nominal rotations above, we get:

      Mprop->uvs-s = [+89.92268389]z * [+88.84044315]y * [+158.00931384]z

      Vuvs-s = Mprop->uvs-s * Vprop

   The UVS Solar frame was defined as a fixed offset frame
   relative to the PROP frame using these angles in the FK 
   ladee_frames_2013289_v02.tf with these keywords:

      TKFRAME_-12500_ANGLES    = ( -158.00931384, -88.84044315, -89.92268389 )
      TKFRAME_-12500_AXES      = (    3,            2,            3          )


   Per [10], the on-orbit calculated UVS Solar Viewer boresight
   direction in the LADEE prop frame is

      [-0.924923, 0.380150, -0.001902]

   By (a) creating a rotation from the LADEE prop frame to the UVS
   Solar frame by forcing the UVS Solar frame +Z be along the boresight
   direction given above and the UVS Solar frame +Y be aligned as
   closely as possible with the LADEE prop frame +Z and (b) decomposing
   the resulting matrix into three rotation angles with the same
   sequence as the nominal rotations above, we get:

      Mprop->uvs-s = [+90.00000000]z * [+90.10897663]y * [+157.65698540]z

      Vuvs-s = Mprop->uvs-s * Vprop
  
   The UVS Solar frame is defined below as a fixed offset frame
   relative to the PROP frame using these angles.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_LADEE_UVSSOL       = -12500
      FRAME_-12500_NAME        = 'LADEE_UVSSOL'
      FRAME_-12500_CLASS       = 4
      FRAME_-12500_CLASS_ID    = -12500
      FRAME_-12500_CENTER      = -12
      TKFRAME_-12500_SPEC      = 'ANGLES'
      TKFRAME_-12500_RELATIVE  = 'LADEE_SC_PROP'
      TKFRAME_-12500_ANGLES    = ( -157.65698540, -90.10897663, -90.00000000 )
      TKFRAME_-12500_AXES      = (    3,            2,            3          )
      TKFRAME_-12500_UNITS     = 'DEGREES'

   \begintext


UVS Telescope Reference Frame

   According to [8], the UVS Telescope frame, LADEE_UVSTEL, is defined
   as follows:

      -  +Z axis is along the instrument boresight

      -  +Y axis is nominally in the direction of the s/c +Z axis 

      -  +X completes the right handed frame.

   This diagram shows the UVS Telescope frame:

                                     9.9 deg 
                                    |<----->/


                                           ^ +Zuvs-t (boresight)
                                    |     /    
                                    |         
                      +Xuvs-t  <..  |    /   
                                 .``..       
                          `  ..``   | ``o.    .> +Ybuild
                            `         / /   .'
                           /  `     |UVS`.'  \
                          /     `      .'     \
                        #/        ` |.'        \#   +Yprop
                       - - - - - - -o-------------->
                        #\        . |`.        /#
                          \     .   |  `.     /
                           \  . LDEX|    `.  /
                            .       |      `.
                          .  ``.    |   ..`` `> +Xbuild
                              NMS``.|.``       
                                    |
                                    V
                                     +Xprop

                                                +Zprop and +Zbuild are 
                                                   out of the page.

                                              +Yuvs-t is out of the page.

   As seen on the diagram, nominally three rotations are needed to to
   align the PROP frame with the UVS Telescope frame: first by +170.1
   degrees about Z, then by +90 degrees about Y, then +90 degrees about
   Z:

      Mprop->uvs-t = [+90]z * [+90]y * [+170.1]z

      Vuvs-t = Mprop->uvs-t * Vprop

   According to Mark's e-mail citing the LADEE metrology report and the
   UVS alignment report, the quaternion (with the the scalar given as
   the last element) relating the LADEE prop frame and the UVS body
   frame is

      {-0.000265, -0.000897, 0.651057, 0.759028}

   and the measured boresight vector of the UVS Telescope in the UVS
   body frame is

      0.020317835, 0.99977952, -0.00530061

   By (a) converting the quaternion to the matrix rotating vectors from
   the PROP frame to the UVS body frame, (b) creating a rotation from
   the UVS body frame to the UVS Telescope frame by forcing the UVS
   Telescope frame +Z be along the boresight direction given above and
   the UVS Telescope frame +Y be aligned as closely as possible with
   the UVS body frame +Z, (c) combining these two rotations, and (d)
   decomposing the resulting matrix into three rotation angles with the
   same sequence as the nominal rotations above, we get:

      Mprop->uvs-t = [+89.93993360]z * [+90.39247231]y * [+170.07816048]z

      Vuvs-t = Mprop->uvs-t * Vprop

   The UVS Telescope frame is defined below as a fixed offset frame
   relative to the PROP frame.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_LADEE_UVSTEL       = -12400
      FRAME_-12400_NAME        = 'LADEE_UVSTEL'
      FRAME_-12400_CLASS       = 4
      FRAME_-12400_CLASS_ID    = -12400
      FRAME_-12400_CENTER      = -12
      TKFRAME_-12400_SPEC      = 'ANGLES'
      TKFRAME_-12400_RELATIVE  = 'LADEE_SC_PROP'
      TKFRAME_-12400_ANGLES    = ( -170.07816048, -90.39247231, -89.93993360 )
      TKFRAME_-12400_AXES      = (    3,            2,            3          )
      TKFRAME_-12400_UNITS     = 'DEGREES'

   \begintext


Earth Mean Ecliptic and Equinox of Date frame (ECLIPDATE)
---------------------------------------------------------

   Definition:
   -----------
   The Earth Mean Ecliptic and Equinox of Date frame is defined as follows:

      -  +Z axis is aligned with the north-pointing vector normal to the
         mean orbital plane of the Earth;

      -  +X axis points along the ``mean equinox'', which is defined as the
         intersection of the Earth's mean orbital plane with the Earth's mean
         equatorial plane. It is aligned with the cross product of the
         north-pointing vectors normal to the Earth's mean equator and mean
         orbit plane of date;

      -  +Y axis is the cross product of the Z and X axes and completes the
         right-handed frame;

      -  the origin of this frame is the Earth's center of mass.

   The mathematical model used to obtain the orientation of the Earth's mean
   equator and equinox of date frame is the 1976 IAU precession model, built
   into SPICE.

   The mathematical model used to obtain the mean orbital plane of the Earth
   is the 1980 IAU obliquity model, also built into SPICE.

   The base frame for the 1976 IAU precession model is J2000.

   Required Data:
   --------------
   The usage of this frame does not require additional data since both the
   precession and the obliquity models used to define this frame are already
   built into SPICE.

   Remarks:
   --------
   None.

  \begindata

      FRAME_ECLIPDATE               =  -12600
      FRAME_-12600_NAME             = 'ECLIPDATE'
      FRAME_-12600_CLASS            =  5
      FRAME_-12600_CLASS_ID         =  -12600
      FRAME_-12600_CENTER           =  399
      FRAME_-12600_RELATIVE         = 'J2000'
      FRAME_-12600_DEF_STYLE        = 'PARAMETERIZED'
      FRAME_-12600_FAMILY           = 'MEAN_ECLIPTIC_AND_EQUINOX_OF_DATE
      FRAME_-12600_PREC_MODEL       = 'EARTH_IAU_1976'
      FRAME_-12600_OBLIQ_MODEL      = 'EARTH_IAU_1980'
      FRAME_-12600_ROTATION_STATE   = 'ROTATING'
 
   \begintext


Selenocentric Solar Ecliptic frame (SSE)
----------------------------------------

   Definition:
   -----------
   The Selenocentric Solar Ecliptic frame is defined as follows (from [3]):

      -  X-Y plane is defined by the Earth Mean Ecliptic plane of date:
         the +Z axis, primary vector, is the normal vector to this plane,
         always pointing toward the North side of the invariant plane;

      -  +X axis is the component of the Moon-Sun vector that is orthogonal
         to the +Z axis;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the Moon's center of mass.

   All the vectors are geometric: no aberration corrections are used.

   Required Data:
   --------------
   This frame is defined as a two-vector frame using two different types
   of specifications for the primary and secondary vectors.

   The primary vector is defined as a constant vector in the ECLIPDATE
   frame and therefore, no additional data is required to compute this
   vector.

   The secondary vector is defined as an 'observer-target position' vector,
   therefore, the ephemeris data required to compute the Moon-Sun vector
   in J2000 frame have to be loaded prior to using this frame.

   Remarks:
   --------
   SPICE imposes a constraint in the definition of dynamic frames:

   When the definition of a parameterized dynamic frame F1 refers to a
   second frame F2 the referenced frame F2 may be dynamic, but F2 must not
   make reference to any dynamic frame. For further information on this
   topic, please refer to [1].

   Therefore, no other dynamic frame should make reference to this frame.

   Since the secondary vector of this frame is defined as an
   'observer-target position' vector, the usage of different planetary
   ephemerides conduces to different implementations of this frame,
   but only when these data lead to different projections of the
   Moon-Sun vector on the Earth Ecliptic plane of date.

  \begindata

      FRAME_LADEE_SSE              = -12605
      FRAME_-12605_NAME            = 'LADEE_SSE'
      FRAME_-12605_CLASS           =  5
      FRAME_-12605_CLASS_ID        =  -12605
      FRAME_-12605_CENTER          =  301
      FRAME_-12605_RELATIVE        = 'J2000'
      FRAME_-12605_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-12605_FAMILY          = 'TWO-VECTOR'
      FRAME_-12605_PRI_AXIS        = 'Z'
      FRAME_-12605_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-12605_PRI_FRAME       = 'ECLIPDATE'
      FRAME_-12605_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-12605_PRI_VECTOR      = ( 0, 0, 1 )
      FRAME_-12605_SEC_AXIS        = 'X'
      FRAME_-12605_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-12605_SEC_OBSERVER    = 'MOON'
      FRAME_-12605_SEC_TARGET      = 'SUN'  
      FRAME_-12605_SEC_ABCORR      = 'NONE'

  \begintext


Earth-Centered Moon-Following (LADEE_MF)
---------------------------------------

   Definition:
   -----------
   The Earth-Centered Moon-Following frame is defined as follows (from [3]):

      -  X-Y plane is defined by the Earth Mean Ecliptic plane of date:
         the +Z axis, primary vector, is the normal vector to this plane,
         always pointing toward the North side of the invariant plane;

      -  +X axis is the component of the Earth-Moon vector that is orthogonal
         to the +Z axis;

      -  +Y axis completes the right-handed system;

      -  the origin of this frame is the Moon's center of mass.

   All the vectors are geometric: no aberration corrections are used.

   Required Data:
   --------------
   This frame is defined as a two-vector frame using two different types
   of specifications for the primary and secondary vectors.

   The primary vector is defined as a constant vector in the ECLIPDATE
   frame and therefore, no additional data is required to compute this
   vector.

   The secondary vector is defined as an 'observer-target position' vector,
   therefore, the ephemeris data required to compute the Earth-Moon vector
   in J2000 frame have to be loaded prior to using this frame.

   Remarks:
   --------
   SPICE imposes a constraint in the definition of dynamic frames:

   When the definition of a parameterized dynamic frame F1 refers to a
   second frame F2 the referenced frame F2 may be dynamic, but F2 must not
   make reference to any dynamic frame. For further information on this
   topic, please refer to [1].

   Therefore, no other dynamic frame should make reference to this frame.

   Since the secondary vector of this frame is defined as an
   'observer-target position' vector, the usage of different planetary
   ephemerides conduces to different implementations of this frame,
   but only when these data lead to different projections of the
   Moon-Sun vector on the Earth Ecliptic plane of date.

  \begindata

      FRAME_LADEE_MF               = -12606
      FRAME_-12606_NAME            = 'LADEE_MF'
      FRAME_-12606_CLASS           =  5
      FRAME_-12606_CLASS_ID        =  -12606
      FRAME_-12606_CENTER          =  399
      FRAME_-12606_RELATIVE        = 'J2000'
      FRAME_-12606_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-12606_FAMILY          = 'TWO-VECTOR'
      FRAME_-12606_PRI_AXIS        = 'Z'
      FRAME_-12606_PRI_VECTOR_DEF  = 'CONSTANT'
      FRAME_-12606_PRI_FRAME       = 'ECLIPDATE'
      FRAME_-12606_PRI_SPEC        = 'RECTANGULAR'
      FRAME_-12606_PRI_VECTOR      = ( 0, 0, 1 )
      FRAME_-12606_SEC_AXIS        = 'X'
      FRAME_-12606_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-12606_SEC_OBSERVER    = 'EARTH'
      FRAME_-12606_SEC_TARGET      = 'MOON'  
      FRAME_-12606_SEC_ABCORR      = 'NONE'

      \begintext


Local Vertical/Local Horizontal (LADEE_LVLH)
--------------------------------------------

   The Local Vertical/Local Horizontal (LADEE_LVLH) is defined as follows:

      -  The Z axis is aligned with the vector from the moon's center
         to the spacecraft (negative of nadir direction).

      -  The X axis is aligned with the direction of motion along the
         orbit.

      -  The Y axis completes the right-handed frame and points along
         the instantaneous orbit angular momentum vector

   The LADEE_LVLH is defined below as a dynamic frame.

   \begindata

      FRAME_LADEE_LVLH             = -12607
      FRAME_-12607_NAME            = 'LADEE_LVLH'
      FRAME_-12607_CLASS           =  5
      FRAME_-12607_CLASS_ID        = -12607
      FRAME_-12607_CENTER          = -12
      FRAME_-12607_RELATIVE        = 'J2000'
      FRAME_-12607_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-12607_FAMILY          = 'TWO-VECTOR'
      FRAME_-12607_PRI_AXIS        = 'Z'
      FRAME_-12607_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-12607_PRI_OBSERVER    = 'MOON'
      FRAME_-12607_PRI_TARGET      = 'LADEE'
      FRAME_-12607_PRI_ABCORR      = 'NONE'
      FRAME_-12607_SEC_AXIS        = 'X'
      FRAME_-12607_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-12607_SEC_OBSERVER    = 'MOON'
      FRAME_-12607_SEC_TARGET      = 'LADEE'
      FRAME_-12607_SEC_ABCORR      = 'NONE'
      FRAME_-12607_SEC_FRAME       = 'J2000'

   \begintext


LADEE NAIF ID Codes -- Definitions
--------------------------------------------------------

   This section contains name to NAIF ID mappings for the LADEE mission.
   Once the contents of this file is loaded into the KERNEL POOL, these 
   mappings become available within SPICE, making it possible to use 
   names instead of ID code in the high level SPICE routine calls.

   This table summarizes the LADEE name-ID mappings:

      LADEE              -12
      LADEE_SC_BUS       -12100
      LADEE_LDEX         -12200
      LADEE_NMS          -12300
      LADEE_NMS_CLOSED   -12310
      LADEE_NMS_OPEN     -12320
      LADEE_UVSTEL       -12400
      LADEE_UVSSOL       -12500

   The keywords below defined the name-ID mappings.

   \begindata

      NAIF_BODY_NAME += ( 'LADEE'                     )
      NAIF_BODY_CODE += ( -12                         )

      NAIF_BODY_NAME += ( 'LADEE_SC_BUS'              )
      NAIF_BODY_CODE += ( -12100                      )

      NAIF_BODY_NAME += ( 'LADEE_LDEX'                )
      NAIF_BODY_CODE += ( -12200                      )

      NAIF_BODY_NAME += ( 'LADEE_NMS'                 )
      NAIF_BODY_CODE += ( -12300                      )

      NAIF_BODY_NAME += ( 'LADEE_NMS_CLOSED'          )
      NAIF_BODY_CODE += ( -12310                      )

      NAIF_BODY_NAME += ( 'LADEE_NMS_OPEN'            )
      NAIF_BODY_CODE += ( -12320                      )

      NAIF_BODY_NAME += ( 'LADEE_UVSTEL'              )
      NAIF_BODY_CODE += ( -12400                      )

      NAIF_BODY_NAME += ( 'LADEE_UVSSOL'              )
      NAIF_BODY_CODE += ( -12500                      )

   \begintext


End of FK file.
