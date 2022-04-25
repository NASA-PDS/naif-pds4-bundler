KPL/FK

KPLO Frame Definitions Kernel
==============================================================================

   This frame kernel contains the KPLO spacecraft and science instrument
   frame definitions. This frame kernel also contains name - to - NAIF
   ID mappings for KPLO science instruments and s/c structures (see the
   last section of the file.)


Version and Date
--------------------------------------------------------
   Version 20200918 (draft) -- September 18, 2020 --  Jo Ryeong Yim

      Corrected KPLO_SHADOWCAM Name in description --> KPLO_SHC

      Added SHC_A frame definition for SHC requested by ASU:
      e-mail dated Sep. 15 2020, (Two separate IDs for ShadowCam -
      We would like two separate frame IDs. One fixed frame ID
      will be used to remove the ~45 rotation and the second
      (CK derived) will be used to adjust the orientation
      during bundle adjustment. )


   Version 20200609 (draft) -- June 09, 2020 --  Jo Ryeong Yim

      Corrected (exchanged) LUTIA (-1.35 deg --> +1.35 deg),
      LUTIB(+1.35 deg --> -1.35 deg) rotation angles
      with respect to LUTI refernece frame.

      Name changed: LUTI1 --> LUTIA, LUTI2 --> LUTIB

      Corrected the LUTIA, LUTIB reference frame in instrument
      frame descriptions


   Version 20200331 (draft) -- March 31, 2020 --  Jo Ryeong Yim

      Corrected LUTI1, LUTI2 reference frame from spacecraft body
      to LUTI. LUTI refernece frame is the spacecraft body frame.

   Version 20191202 (draft) -- December 02, 2019 --  Boris Semenov

      Corrected LUTI2 frame description to match the rotation formula
      and the angles in the definition keywords.

   Version 20190828 (draft) -- August 28, 2019 --  Boris Semenov

      Corrected seconds axis in KPLO_LUTI1 and KPLO_LUTI2 definitions
      to match descriptions.

      Corrected angles in the KPLO_STA1 and KPLO_STA2 definitions to
      match descriptions.

      Adjusted LUTI and STA frames ASCII diagrams to match definitions.

   Version 20190808 (draft) -- August 08, 2019 --  Jo Ryeong Yim

      Updated the KPLO_LVLH followed by the KPLO reference frame definition.

      Updated the KPLO_LUTI1 and KPLO_LUTI2 rotation from body
      to be - 45 deg yaw in order to reflect the CCD direction and
      accordingly definitions for the
      -1.35 and +1.35 degree offset rotations to be X from Y.

      Updated KPLO_STA1 and KPLO_STA2 designation number changed
      and accordingly rotation angles so as to consider the CCD alignment

   Version 20190728 (draft) -- July 28, 2019 --  Boris Semenov

      Updated the KPLO_LUTI1 and KPLO_LUTI2 definitions to include
      +1.35 and -1.35 degree offset rotations about Y correspondingly.

      Updated the KPLO_POLCAM-L and KPLO_POLCAM-R definitions to have
      the second rotations about Z, to make the frames' +Y axes
      (boresights) look left and right and have frames' +X axes be
      across track.

      Removed DTNPL and GRA frames and name/ID mappings.

   Version 20190411 (draft) -- April 11, 2019 --  Boris Semenov

      Changed _ANGLES in the KPLO_LGA_B definition (160.0 -> 70.0)

      Changed _CENTER to -155 in the KPLO_HGA KPLO_SA1, and KPLO_SA2
      definitions.

      Changed _ANGLES in the KPLO_SA2_ZERO definition (0.0,0.0,0.0 ->
      -90.0,0.0,0.0)

      Changed _ANGLES in the KPLO_SA1_ZERO definition (0.0,0.0,0.0 ->
      90.0,0.0,0.0)

      Fixed _SPEC in the KPLO_KGRS definition ('MATRIX' -> 'ANGLES')

      Fixed keywords in the KPLO_SHC (TKFRAME_-155`50_SPEC ->
      TKFRAME_-155150_SPEC) and KPLO_LVLH (FRAME_-1552007_PRI_ABCORR ->
      FRAME_-155200_PRI_ABCORR) definitions

      Fixed _NAME in the POLCAM-R definition ('KPLO_POLCAM-L' ->
      'KPLO_POLCAM-R')

      Fixed _AXES in the KPLO_GRA definition (1,2,3 -> 1,3,2)

      Reformatted/augmented all frame descriptions to look similar to
      each other.

      Added frame diagrams to most frame descriptions.

      Reformatted frame tree diagram to fit into 80 character page
      width and added POLCAM-L and POLCAM-R frames.

      Removed comment section describing star tracker mechanical,
      alignment, and  measurement frames that are not defined in the
      FK.

      Removed PDS3 label from the beginning of the file.

      Filled in Versions section entries for this and all previous
      versions.


   Version 20190329 (draft) -- March 29, 2019 -- Jo Ryeong Yim

      Corrected s/c frame name (KPLO_SPACECRFT -> KPLO_SPACECRAFT).


   Version 20190328 (draft) -- March 28, 2019 -- Jo Ryeong Yim

      Added frame descriptions.


   Version 20180607 (draft) -- June 07, 2018 -- Jo Ryeong Yim

      Initial Release. Contains Euler angles from KPLO I-Kernel
      files. Does not contain a description for any of the frames.


References
--------------------------------------------------------

   1. C-kernel Required Reading

   2. Kernel Pool Required Reading

   3. Frames Required Reading

   4. KPLO-OOM-010 KPLO Reference Frame and Coordinate System Definition_v0 (TBD)


Contact Information
--------------------------------------------------------

   Jo Ryeong Yim, (82)-42-860-2874,  jryim@kari.re.kr


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


KPLO Frames
----------------------------------------------------------------------------

   The following KPLO frames are defined in this kernel file:

        Frame Name                   Relative to            Type    NAIF ID
   =========================   =========================   =======  =======

   Spacecraft Bus and Spacecraft Structure Frames:
   -----------------------------------------------
      KPLO_SPACECRAFT           rel.to J2000                CK       -155000

      KPLO_SA1                  rel.to SA1_ZERO             CK       -155421

      KPLO_SA1_ZERO             rel.to KPLO_SPACECRAFT      FIXED    -155561

      KPLO_SA2                  rel.to SA2_ZERO             CK       -155422

      KPLO_SA2_ZERO             rel.to KPLO_SPACECRAFT      FIXED    -155562

      KPLO_LGA_A                rel.to KPLO_SPACECRAFT      FIXED    -155831

      KPLO_LGA_B                rel.to KPLO_SPACECRAFT      FIXED    -155832

      KPLO_HGA                  rel.to HGA_ZERO             CK       -155191

      KPLO_HGA_ZERO             rel.to KPLO_SPACECRAFT      FIXED    -155190

      KPLO_STA1                 rel.to KPLO_SPACECRAFT      FIXED    -155501

      KPLO_STA2                 rel.to KPLO_SPACECRAFT      FIXED    -155502


   Instrument Frames:
   ------------------
      KPLO_LUTI                rel.to KPLO_SPACECRAFT       FIXED    -155100

      KPLO_LUTIA               rel.to KPLO_LUTI             FIXED    -155101

      KPLO_LUTIB               rel.to KPLO_LUTI             FIXED    -155102

      KPLO_POLCAM              rel.to KPLO_SPACECRAFT       FIXED    -155110

      KPLO_POLCAM-L            rel.to KPLO_POLCAM           FIXED    -155111

      KPLO_POLCAM-R            rel.to KPLO_POLCAM           FIXED    -155112

      KPLO_KMAG                rel.to KPLO_SPACECRAFT       FIXED    -155120

      KPLO_KGRS                rel.to KPLO_SPACECRAFT       FIXED    -155130

      KPLO_SHC                 rel.to KPLO_SPACECRAFT       FIXED    -155150

      KPLO_SHC_A               rel.to SHC                   CK       -155151


   Dynamic Frames:
   ---------------

      KPLO_LVLH                rel.to J2000                 DYNAMIC  -155200


KPLO Frames Hierarchy
--------------------------------------------------------

   The diagram below shows KPLO frames hierarchy:


                               "J2000" INERTIAL
               +--------------------------------------------+
               |            |                               |
               | <--ck      |<--dyn                         | <--pck
               |            |                               |
               |            V                               V
               |        "KPLO_LVLH"                     "IAU_EARTH"
               |        -----------                     EARTH BFR(*)
               |                                        ------------
               |
               |
               |
               |
               |
               |
               V
          "KPLO_SC_BUS"
      +---------------------------------------------------------------------+
      |             |             |                           |             |
      |<--fixed     |<--fixed     |<-fixed                    |<--fixed     |
      |             |             |                           |             |
      V             V             V                           V             |
   "KPLO_KGRS"  "KPLO_POLCAM"  "KPLO_KMAG"                 "KPLO_SHC"       |
   -----------  +-----------+  -----------                 -----------      |
                |           |                                  |            |
                |<--fixed   |<--fixed                          |<--ck       |
                |           |                                  |            |
                V           V                                  V            |
       "KPLO_POLCAM-L"  "KPLO_POLCAM-R"                   "KPLO_SHC_A"      |
       ---------------  ---------------                   ------------      |
                                                                            |
      +---------------------------------------------------------------------+
      |    |               |           .<?>      |         .<?>
      |    |<--fixed       |<--fixed   .         |<--fixed .
      |    |               |           .         |         .
      |    V               V           .         V         .
      | "KPLO_LGA"  "KPLO_HGA_ZERO"    .    "KPLO_LUTI"    .
      | ----------  ---------------    .  +-------------+  .
      |                    |           .  |             |  .
      |                    |<--ck      .  |<--fixed     |  .<--fixed
      |                    |           .  |             |  .
      |                    V           V  V             V  V
      |                "KPLO_HGA"     "KPLO_LUTIA"  "KPLO_LUTIB"
      |                ----------     ------------  ------------
      |
      +-------------------------------------------------------------+
           |               |                     |                  |
           |<--fixed       |<--fixed             |<--fixed          |<--fixed
           V               V                     V                  V
       "KPLO_STA1"    "KPLO_STA2"         "KPLO_SA1_ZERO"    "KPLO_SA2_ZERO"
       -----------    -----------         ---------------    ---------------
                                                 |                  |
                                                 |<--ck             |<--ck
                                                 |                  |
                                                 V                  V
                                             "KPLO_SA1"         "KPLO_SA1"
                                             ----------         ----------


KPLO Spacecraft Bus Reference Frame
--------------------------------------------------------

   It is a coordinate system fixed to the body of the spacecraft. The
   Spacecraft Bus Reference Frame is defined by the spacecraft design
   as follows:

      *  The origin is placed at the center point of interface between
         the propulsion rail and top of the spacecraft adapter;

      *  The +X axis includes the origin and it is the axis toward the
         opposite direction from the thruster module installed on the
         spacecraft;

      *  The +Z axis includes the origin and is parallel to the axis
         with Optical camera and payload instruments facing vector;

      *  The +Y axis completes the right-handed Cartesian system with X
         axis and Z axis;


   This diagram illustrates the spacecraft bus frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                               |||     |/ \
         _______________      _|||     |\_/      _______________
        |             | \    |             |    / |             |
        |             |  \   |             |   /  |             |
        |             |   `. |             | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc is out of
                                     LGA-B              the page.


      +X s/c side (top) view:
      -----------------------
                                    .
                                   / \  HGA
                                  -----
                                  `-o-'
                              _____/_\_____
                             |   |     | _ |
                                 |     || ||
                          +Ysc   | +Xsc|| ||
        o===================o <-----o  || ||o===================o
     +Y Solar Array          |   |  |  || ||        -Y Solar Array
                             |   |  |  || ||
                             |___|__|__||_||
                                 |__V__|
                                +Zsc |               +Xsc is out of
                                     |                  the page.
                                 KMAG


   The Spacecraft bus attitude with respect to an inertial frame is
   provided by a C kernel (see [1] for more information).

   \begindata

      FRAME_KPLO_SPACECRAFT         = -155000
      FRAME_-155000_NAME            = 'KPLO_SPACECRAFT'
      FRAME_-155000_CLASS           = 3
      FRAME_-155000_CLASS_ID        = -155000
      FRAME_-155000_CENTER          = -155
      CK_-155000_SCLK               = -155
      CK_-155000_SPK                = -155

   \begintext


KPLO Local Vertical/Local Horizontal (KPLO_LVLH) Frame
--------------------------------------------------------

   According to [4] the Local Vertical/Local Horizontal (KPLO_LVLH) is
   defined as follows

      -  The origin is placed at the satellite center of mass

      -  The Z axis is the direction toward the planet center.
         (Anti-radial track)

      -  The Y axis can be chosen as the vector perpendicular to the Z
         and satellite velocity direction.

      -  The X axis completes the right-handed Cartesian system with Z
         and Y (Along track or In-track)

   The KPLO_LVLH is defined below as a dynamic frame.

   \begindata

      FRAME_KPLO_LVLH               = -155200
      FRAME_-155200_NAME            = 'KPLO_LVLH'
      FRAME_-155200_CLASS           =  5
      FRAME_-155200_CLASS_ID        = -155200
      FRAME_-155200_CENTER          = -155
      FRAME_-155200_RELATIVE        = 'J2000'
      FRAME_-155200_DEF_STYLE       = 'PARAMETERIZED'
      FRAME_-155200_FAMILY          = 'TWO-VECTOR'
      FRAME_-155200_PRI_AXIS        = 'Z'
      FRAME_-155200_PRI_VECTOR_DEF  = 'OBSERVER_TARGET_POSITION'
      FRAME_-155200_PRI_OBSERVER    = 'KPLO'
      FRAME_-155200_PRI_TARGET      = 'MOON'
      FRAME_-155200_PRI_ABCORR      = 'NONE'
      FRAME_-155200_SEC_AXIS        = 'X'
      FRAME_-155200_SEC_VECTOR_DEF  = 'OBSERVER_TARGET_VELOCITY'
      FRAME_-155200_SEC_OBSERVER    = 'MOON'
      FRAME_-155200_SEC_TARGET      = 'KPLO'
      FRAME_-155200_SEC_ABCORR      = 'NONE'
      FRAME_-155200_SEC_FRAME       = 'J2000'

   \begintext


KPLO Lunar Terrain Imager (LUTI) Frame
--------------------------------------------------------

   The LUTI instrument frame is defined by the instrument design as
   follows:

      *  +Z axis is along the LUTIA boresight;

      *  +Y axis is parallel to the LUTIA CCD lines;

      *  +X axis completes the right handed frame;

      *  the origin of this frame is at the instrument to spacecraft
         interface, at [982.0, 9.1, 484.4] in millimeters.

   Nominally, the LUTI frame is fixed with respect to and is rotated
   by -45 degrees about Z from the spacecraft frame:

      Mspacecraft->luti = [0]X [0]Y [-45]Z

      Vluti = Mspacecraft->luti * Vspacecraft

   This diagram illustrates the LUTI frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_
                          +Yluti |        +Xluti
         _______________       <.       .>_      _______________
        |             | \    |   `.   .'   |    / |             |
        |             |  \   |     `o'     |   /  |             |
        |             |   `. |        o    | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |               +Zsc and +Zluti are
                                     LGA-B            out of the page.


   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_LUTI               = -155100
      FRAME_-155100_NAME            = 'KPLO_LUTI'
      FRAME_-155100_CLASS           = 4
      FRAME_-155100_CLASS_ID        = -155100
      FRAME_-155100_CENTER          = -155
      TKFRAME_-155100_SPEC          = 'ANGLES'
      TKFRAME_-155100_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155100_ANGLES        = ( 45.0, 0.0, 0.0 )
      TKFRAME_-155100_AXES          = (  3,   2,   1   )
      TKFRAME_-155100_UNITS         = 'DEGREES'

   \begintext


KPLO Lunar Terrain Imager A and B (LUTIA, LUTIB) Frame
--------------------------------------------------------

   The LUTIA and LUTIB instrument frames are defined by the instrument
   design as follows:

      *  +Z axis is along the camera boresight;

      *  +Y axis is parallel to the camera CCD lines;

      *  +X axis completes the right handed frame;

      *  <?> the origin of both frames is at the spacecraft to instrument
         interface, at [982.0, 9.1, 484.4] in millimeters.

   Nominally, the LUTIA frame is fixed with respect to, and
   by +1.35 degrees about X from the LUTI frame:

      Mluti->lutiA = [0]Y [+1.35]X [0]Z

      VlutiA = Mluti->lutiA * Vluti

   Nominally, the LUTIB frame is fixed with respect to, and
   by -1.35 degrees about X from the LUTI frame:

      Mluti->lutiB = [0]Y [-1.35]X [0]Z

      VlutiB = Mluti->lutiB * Vluti

   This diagram illustrates the LUTIA and LUTIB frames:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_
                        +YlutiA  |     |  +XlutiA
         _______________       <.       .>           ___________
        |             | \+YlutiB <.   .'  .> +XlutiB            |
        |             |  \   |     `o'  .' |                    |
        |             |   `. |       `o'   | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |            +Zsc, +ZlutiA, and +ZlutiB
                                     LGA-B           are out of the page.


   The angles provided in the frame definitions below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_LUTIA              = -155101
      FRAME_-155101_NAME            = 'KPLO_LUTIA'
      FRAME_-155101_CLASS           = 4
      FRAME_-155101_CLASS_ID        = -155101
      FRAME_-155101_CENTER          = -155
      TKFRAME_-155101_SPEC          = 'ANGLES'
      TKFRAME_-155101_RELATIVE      = 'KPLO_LUTI'
      TKFRAME_-155101_ANGLES        = (  0.0,  -1.35, 0.0 )
      TKFRAME_-155101_AXES          = (   3,    1,    2   )
      TKFRAME_-155101_UNITS         = 'DEGREES'

      FRAME_KPLO_LUTIB              = -155102
      FRAME_-155102_NAME            = 'KPLO_LUTIB'
      FRAME_-155102_CLASS           = 4
      FRAME_-155102_CLASS_ID        = -155102
      FRAME_-155102_CENTER          = -155
      TKFRAME_-155102_SPEC          = 'ANGLES'
      TKFRAME_-155102_RELATIVE      = 'KPLO_LUTI'
      TKFRAME_-155102_ANGLES        = (  0.0, 1.35, 0.0 )
      TKFRAME_-155102_AXES          = (   3,    1,    2   )
      TKFRAME_-155102_UNITS         = 'DEGREES'

   \begintext


KPLO Polarization Camera (PolCam) Frame
--------------------------------------------------------

   The PolCam instrument frame is defined by the instrument design as
   follows:

      *  +X axis is nominally parallel to the spacecraft +X axis;

      *  +Y axis is nominally parallel to the spacecraft +Z axis;

      *  +Z axis completes the right-handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1301.7, -132.8, 446.3] in millimeters.

   Nominally, the PolCam frame is fixed with respect to, and is rotated
   by +90 degrees about X from the spacecraft frame:

      Mspacecraft-> polcam = [0]Z [0]Y [+90]X

      Vpolcam = Mspacecraft-polcam * Vspacecraft

   This diagram illustrates the PolCam frame:

      +Z s/c side (science deck) view:
      --------------------------------


                              +Xpolcam
                                  ___ ^  _
                               |||    ||/ \
         _______________      _|||    ||\_/           __________
        |             | \    |        |    | +Zpolcam           |
        |             |  \   |        o----->                   |
        |             |   `. |             | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Ypolcam are
                                     LGA-B              out of the page.


   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_POLCAM             = -155110
      FRAME_-155110_NAME            = 'KPLO_POLCAM'
      FRAME_-155110_CLASS           = 4
      FRAME_-155110_CLASS_ID        = -155110
      FRAME_-155110_CENTER          = -155
      TKFRAME_-155110_SPEC          = 'ANGLES'
      TKFRAME_-155110_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155110_ANGLES        = ( -90.0, 0.0, 0.0 )
      TKFRAME_-155110_AXES          = (   1,   2,   3   )
      TKFRAME_-155110_UNITS         = 'DEGREES'

   \begintext


KPLO Polarization Camera (PolCam-L, PolCam-R) Frames
--------------------------------------------------------

   The PolCam-L and PolCam-R instrument frames are defined by the
   instrument design as follows:

      *  +Y axis is along the camera boresight;

      *  +X axis is parallel to the camera CCD lines;

      *  +Z axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1301.7, -132.8, 446.3] in millimeters.

   <?> Nominally, the PolCam-L frame is fixed with respect to, and is
   rotated first by <?> +45 degrees about Y, then by +45 degrees about Z
   from the PolCam frame:

      Mpolcam-> polcamL = [0]Z [+45]Z [+45]Y

      VpolcamL = Mpolcam->polcamL * Vpolcam

   <?> Nominally, the PolCam-R frame is fixed with respect to, and is
   rotated first by +45 degrees about Y, then by -45 degrees about Z
   from the PolCam frame:

      Mpolcam-> polcamR = [0]Z [-45]Z [+45]Y

      VpolcamR = Mpolcam->polcamR * Vpolcam

   This diagram illustrates the PolCam-L and PolCam-R frames:

      +Z s/c side (science deck) view:
      --------------------------------


                              +Xpolcam
                                  ___ ^ +Zpolcamr
                        +Ypolcamr     |    ^   +Zpolcaml
         _______________          ^.  |  .'   ^  _ _____________
        |             | \    |      `.|.'   .'  / |             |
        |             |  \   |        o----->                   |
        |             |   `. |         `o' | +Zpolcam           |
        |             |   | o|    _      `.                     |
        |             |   .' |   |  ^+Xsc  v `.   |             |
        |             |  /   |   |  |  |   +Ypolcaml            |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Ypolcam are
                                     LGA-B              out of the page.

                                                 +Ypolcaml, +Ypolcamr and
                                               +Xpolcaml point 45 degrees
                                                     above the page.

                                                   +Xpolcamr points 45
                                                  degrees below the page.

   The angles provided in the frame definitions below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_POLCAM-L           = -155111
      FRAME_-155111_NAME            = 'KPLO_POLCAM-L'
      FRAME_-155111_CLASS           = 4
      FRAME_-155111_CLASS_ID        = -155111
      FRAME_-155111_CENTER          = -155
      TKFRAME_-155111_SPEC          = 'ANGLES'
      TKFRAME_-155111_RELATIVE      = 'KPLO_POLCAM'
      TKFRAME_-155111_ANGLES        = ( -45.0, -45.0, 0.0 )
      TKFRAME_-155111_AXES          = (   2,     3,   1   )
      TKFRAME_-155111_UNITS         = 'DEGREES'

      FRAME_KPLO_POLCAM-R           = -155112
      FRAME_-155112_NAME            = 'KPLO_POLCAM-R'
      FRAME_-155112_CLASS           = 4
      FRAME_-155112_CLASS_ID        = -155112
      FRAME_-155112_CENTER          = -155
      TKFRAME_-155112_SPEC          = 'ANGLES'
      TKFRAME_-155112_RELATIVE      = 'KPLO_POLCAM'
      TKFRAME_-155112_ANGLES        = ( -45.0,  45.0, 0.0 )
      TKFRAME_-155112_AXES          = (   2,     3,   1   )
      TKFRAME_-155112_UNITS         = 'DEGREES'

   \begintext


KPLO Gamma-Ray Spectrometer (KGRS) Frame
--------------------------------------------------------

   The KGRS instrument frame is defined by the instrument design as
   follows:

      *  +X axis is nominally aligned with the spacecraft +Z axis;

      *  +Y axis is nominally aligned with the spacecraft +Y axis;

      *  +Z axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1367.7, 139.5, 500.0] in millimeters.

   Nominally, the KGRS frame is fixed with respect to, and is rotated
   by -90 degrees about Y from the spacecraft frame:

      Mspacecraft-> kgrs = [0]Z [-90]Y [0]X

      Vkgrs = Mspacecraft->kgrs * Vspacecraft

   This diagram illustrates the KGRS frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                               |||     |/ \
         ___________          _|        \_/      _______________
        |            +Ykgrs  |   +Xkgrs    |    / |             |
        |                 <-----o          |   /  |             |
        |             |    . |  |          | .'   |             |
        |             |   | o|  |          |o |   |             |
        |             |   .' |  |   ^+Xsc  | `.   |             |
        |             |  /      v   |  |   |   \  |             |
        |_____________|_/ +Zkgrs    |  |   |    \_|_____________|
     +Y Solar Array           ___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Xkgrs are
                                     LGA-B             out of the page.


   The angles provided in the frame definitions below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_KGRS               = -155130
      FRAME_-155130_NAME            = 'KPLO_KGRS'
      FRAME_-155130_CLASS           = 4
      FRAME_-155130_CLASS_ID        = -155130
      FRAME_-155130_CENTER          = -155
      TKFRAME_-155130_SPEC          = 'ANGLES'
      TKFRAME_-155130_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155130_SPEC          = 'ANGLES'
      TKFRAME_-155130_ANGLES        = ( 0.0, 90.0, 0.0 )
      TKFRAME_-155130_AXES          = ( 1,    2,   3   )
      TKFRAME_-155130_UNITS         = 'DEGREES'

  \begintext


KPLO Magnetometer (KMAG) Frame
--------------------------------------------------------

   The KMAG instrument frame is defined by the instrument design as
   follows:

      *  +X axis is nominally aligned with the spacecraft +X axis;

      *  +Y axis is nominally aligned with the spacecraft +Y axis;

      *  +Z axis completes the right handed frame;

      *  the origin of this frame is at the instrument to spacecraft
         interface, at [1887.1, -24.5, 791.7] in millimeters.

   The KMAG frame is fixed with respect to, and is nominally co-aligned
   the spacecraft frame.

   This diagram illustrates the KMAG frame:

      +Z s/c side (science deck) view:
      --------------------------------

                                     ^ +Xkmag
                                     |
                                     |
                         +Ykmag      |
                               <-----o   _
                                 |+Zkmag/ \
         _______________      _|||     |\_/      _______________
        |             | \    |             |    / |             |
        |             |  \   |             |   /  |             |
        |             |   `. |             | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |            +Zsc and +Zkmag are
                                     LGA-B          out of the page.


   \begindata

      FRAME_KPLO_KMAG               = -155120
      FRAME_-155120_NAME            = 'KPLO_KMAG'
      FRAME_-155120_CLASS           = 4
      FRAME_-155120_CLASS_ID        = -155120
      FRAME_-155120_CENTER          = -155
      TKFRAME_-155120_SPEC          = 'ANGLES'
      TKFRAME_-155120_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155120_ANGLES        = ( 0.0, 0.0, 0.0 )
      TKFRAME_-155120_AXES          = ( 3,   2,   1   )
      TKFRAME_-155120_UNITS         = 'DEGREES'

   \begintext


KPLO SHADOWCAM (SHC) Frame
--------------------------------------------------------

   The SHC instrument frame is defined by the instrument design as
   follows:

      *  +Z axis is along the SHC boresight;

      *  <?> +X axis is parallel to the SHC CCD lines;

      *  +Y axis completes the right handed frame;

      *  The SHC offset is identified as the distance from the
         spacecraft bus frame to the SHC reference cg point,
         at [1537.0, -520.0, -143.2] in millimeters.

   Nominally, the SHC frame is fixed with respect to, and is rotated
   by +45 degrees about Z from the spacecraft frame:

      Mspacecraft->shc = [0]X [0]Y [+45]Z

      Vshc = Mspacecraft->shc * Vspacecraft

   This diagram illustrates the SHC frame:

      +Z s/c side (science deck) view:
      --------------------------------

                              +Xshc
                                    <.
                                  ___ `. _+Zshc
                               |||      `o\
         _______________      _|||     .'_/      _______________
        |             | \    |       .'    |    / |             |
        |             |  \   |      <      |   /  |             |
        |             |   `. | +Yshc       | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Zshc are
                                     LGA-B             out of the page.

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_SHC                = -155150
      FRAME_-155150_NAME            = 'KPLO_SHC'
      FRAME_-155150_CLASS           = 4
      FRAME_-155150_CLASS_ID        = -155150
      FRAME_-155150_CENTER          = -155
      TKFRAME_-155150_SPEC          = 'ANGLES'
      TKFRAME_-155150_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155150_ANGLES        = ( -45.0, 0.0, 0.0 )
      TKFRAME_-155150_AXES          = (   3,   2,   1   )
      TKFRAME_-155150_UNITS         = 'DEGREES'

   \begintext


KPLO Star Tracker #1 (STA1) Frame
--------------------------------------------------------

   The Star Tracker #1 frame is defined by the instrument design as
   follows:

      *  +Z axis is along the star tracker boresight;

      *  +Y axis is nominally aligned with the spacecraft +Y axis;

      *  +X axis completes the right-handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1538.8, 506.8, -61.8] in millimeters.

   Nominally, the Star Tracker #1 frame is fixed with respect to, and is
   rotated by +90 degree about Z, then +125 degree about Y, and then
   -90 degree about Z from the spacecraft frame:

      Mspacecraft->sta1 = [-90]Z [+125]Y [+90]Z

      Vsta1 = Mspacecraft->sta1 * Vspacecraft

   This diagram illustrates the Star Tracker #1 frame:

      +X s/c side (top) view:
      -----------------------
                                    .
                              HGA  / \
                                  ----  +Ysta1
                        +Zsta1    `-o ^
                              <.  _/ / ____
                             |  `.  /  | _ |
                                  `o   || ||
                          +Ysc   |  +Xsc| ||
        o===================o <-----o  || ||o===================o
     +Y Solar Array          |   |  |  || ||        -Y Solar Array
                             |   |  |  || ||
                             |___|__|__||_||
                                 |__V__|
                                +Zsc |                 +Xsc and +Xsta1 are
                                     |                  out of the page.
                                 KMAG


   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_STA1               = -155501
      FRAME_-155501_NAME            = 'KPLO_STA1'
      FRAME_-155501_CLASS           = 4
      FRAME_-155501_CLASS_ID        = -155501
      FRAME_-155501_CENTER          = -155
      TKFRAME_-155501_SPEC          = 'ANGLES'
      TKFRAME_-155501_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155501_ANGLES        = ( -90.0, -125.0, +90.0 )
      TKFRAME_-155501_AXES          = (   3,      2,     3   )
      TKFRAME_-155501_UNITS         = 'DEGREES'

   \begintext


KPLO Star Tracker #2 (STA2) Frame
--------------------------------------------------------

   The Star Tracker #2 frame is defined by the instrument design as
   follows:

      *  +Z axis is along the star tracker boresight;

      *  +X axis is nominally aligned with the spacecraft +X axis;

      *  +Y axis completes the right-handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1696.4, 39.1, -298.8] in millimeters.

   Nominally, the Star Tracker #2 frame is fixed with respect to, and
   is rotated by +125 degrees about Y and then +90 degree about Z from
   the spacecraft frame:

      Mspacecraft->sta2 = [+90]Z [+125]Y [0]Z

      Vsta2 = Mspacecraft->sta2 * Vspacecraft

   This diagram illustrates the Star Tracker #2 frame:

      +X s/c side (top) view:
      -----------------------

                                    .
                                   / \  HGA
                                  -----
                                  `-o-'
                         +Zsta2 _ __/_\_____
                             | ^ |     | _ |
                     +Xsta2  | | |     || ||
                         <-----o | +Xsc|| ||
        o===================o|<|----o  || ||o===================o
     +Y Solar Array       +Ysc | |  |  || ||        -Y Solar Array
                             | v |  |  || ||
                          Ysta2 _|__|__||_||
                                 |__V__|
                                +Zsc |           +Xsc is out of the page.
                                     |
                                 KMAG       +Zsta2 is 55 deg above the page

                                            +Ysta2 is 35 deg above the page


   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_STA2               = -155502
      FRAME_-155502_NAME            = 'KPLO_STA2'
      FRAME_-155502_CLASS           = 4
      FRAME_-155502_CLASS_ID        = -155502
      FRAME_-155502_CENTER          = -155
      TKFRAME_-155502_SPEC          = 'ANGLES'
      TKFRAME_-155502_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155502_ANGLES        = (  0.0, -125.0, -90.0 )
      TKFRAME_-155502_AXES          = (  3,      2,     3   )
      TKFRAME_-155502_UNITS         = 'DEGREES'

   \begintext


KPLO High Gain Antenna Zero Position (HGA_ZERO) Frame
--------------------------------------------------------

   The HGA Zero Position frame is defined by the antenna design as
   follows:

      *  +Z axis is nominally aligned with the -Z of the spacecraft;

      *  +X axis is parallel to the <?>(inner or outer) HGA gimbal axis;

      *  +Y axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1282.0, -54.9, -1030.3] in millimeters.

   Nominally, the HGA Zero Position frame is fixed with respect to, and is
   rotated first by 180 degrees about X, then by -45 degrees about Z
   from the spacecraft frame:

      Mspacecraft->hga0 = [0]Y [-45]Z [180]X

      Vhga = Mspacecraft->hga0 * Vspacecraft

   This diagram illustrates the HGA Zero Position frame:

      -Z s/c side (HGA side) view:
      ----------------------------

                              KMAG | LGA-A
                                   ||
                                  _||__
                         +Yhga0  |     |  +Xhga0
         _______________       ^ |     | ^       _______________
        |             | \    |  `.     .'  |    / |             |
        |             |  \   |    `. .'    |   /  |             |
        |             |   `. |      o      | .'   |             |
        |             |   | o|+Zhga0       |o |   |             |
        |             |   .' |      ^+Xsc  | `.   |             |
        |             |  /   |      |      |   \  |             |
        |_____________|_/    |      |      |    \_|_____________|
     -Y Solar Array          |______|__ ___|       +Y Solar Array
                               |____x----->
                                    +Zsc   +Ysc
                                    |                +Zsc is into
                                     LGA-B              the page.

                                               +Zhga0 is out of the page.

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_HGA_ZERO           = -155190
      FRAME_-155190_NAME            = 'KPLO_HGA_ZERO'
      FRAME_-155190_CLASS           = 4
      FRAME_-155190_CLASS_ID        = -155190
      FRAME_-155190_CENTER          = -155
      TKFRAME_-155190_SPEC          = 'ANGLES'
      TKFRAME_-155190_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155190_ANGLES        = ( 180.0, 45.0, 0.0 )
      TKFRAME_-155190_AXES          = (   1,    3,   2   )
      TKFRAME_-155190_UNITS         = 'DEGREES'

   \begintext


KPLO High Gain Antenna (HGA) Frame
--------------------------------------------------------

   The HGA frame is defined by the antenna design as follows:

      *  +Z axis is along the HGA boresight;

      *  +Y axis is parallel to the <?>(inner or outer) HGA gimbal axis;

      *  +X axis completes the right handed frame;

      *  <?> the origin of this frame is at the spacecraft to instrument
         interface, at <?> [1282.0, -54.9, -1030.3] in millimeters.

   Since the HGA frame rotates with respect to the HGA Zero Position
   frame, its orientation is provided in CK files.

   In zero gimbal position this frame is co-aligned with the HGA Zero
   Position frame.

   This diagram illustrates the HGA frame in zero position:

      -Z s/c side (HGA side) view:
      ----------------------------

                              KMAG | LGA-A
                                   ||
                         +Yhga    _||__   +Xhga
                         +Yhga0  |     |  +Xhga0
         _______________       ^ |     | ^       _______________
        |             | \    |  `.     .'  |    / |             |
        |             |  \   |    `. .'    |   /  |             |
        |             |   `. |+Zhga o      | .'   |             |
        |             |   | o|+Zhga0       |o |   |             |
        |             |   .' |      ^+Xsc  | `.   |             |
        |             |  /   |      |      |   \  |             |
        |_____________|_/    |      |      |    \_|_____________|
     -Y Solar Array          |______|__ ___|       +Y Solar Array
                               |____x----->
                                    +Zsc   +Ysc
                                    |                +Zsc is into
                                     LGA-B              the page.

                                               +Zhga0 and +Zhga are
                                                 out of the page.

   The keywords below define the HGA frame as a CK-based frame.

   \begindata

      FRAME_KPLO_HGA                = -155191
      FRAME_-155191_NAME            = 'KPLO_HGA'
      FRAME_-155191_CLASS           = 3
      FRAME_-155191_CLASS_ID        = -155191
      FRAME_-155191_CENTER          = -155
      CK_-155191_SCLK               = -155
      CK_-155191_SPK                = -155

   \begintext


KPLO Solar Array #1 ZERO (SA1_ZERO) Frame
--------------------------------------------------------

   The SA1 Zero Position frame is defined by the array design as
   follows:

      *  +Z axis is nominally along the spacecraft +Y axis and is
         parallel to the array rotation axis;

      *  +X axis is nominally along the spacecraft +X axis;

      *  +Y axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [790.9, 634.9, 0.0] in millimeters.

   Nominally, the SA1 frame is fixed with respect to, and is rotated by
   -90 degrees about X from the spacecraft frame:

      Mspacecraft->sa1_0 = [-90]X [0]Y [0]Z

      Vsa1_0 = Mspacecraft->sa1_0 * Vspacecraft

   This diagram illustrates the SA1 Zero Position frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                     +Xsa1_0   |||     |/ \  +Xsa2_0
                            ^ _|||     |\_/ ^
                            ||             ||
                            ||             ||
      +Y Solar Array        ||             ||        -Y Solar Array
        o============ <-----x|    _        |o-----> ============o
               +Zsa1_0       |   |  ^+Xsc  |       +Zsa2_0
                             |   |  |  |   |
                             |   |  |  |   |
                             |___|__|__|___|
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Ysa2_0 are
                                     LGA-B             out of the page.

                                                   +Ysa1_0 is into the page.

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_SA1_ZERO           = -155561
      FRAME_-155561_NAME            = 'KPLO_SA1_ZERO'
      FRAME_-155561_CLASS           = 4
      FRAME_-155561_CLASS_ID        = -155561
      FRAME_-155561_CENTER          = -155
      TKFRAME_-155561_SPEC          = 'ANGLES'
      TKFRAME_-155561_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155561_ANGLES        = ( 90.0, 0.0, 0.0 )
      TKFRAME_-155561_AXES          = (  1,   2,   3   )
      TKFRAME_-155561_UNITS         = 'DEGREES'

   \begintext


KPLO Solar Array #1 (SA1) Frame
--------------------------------------------------------

   The SA1 frame is defined by the array design as follows:

      *  -X axis is along the normal on the solar array active cell side;

      *  +Z axis is nominally along the spacecraft +Y axis and is
         parallel to the array rotation axis;

      *  +Y axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [790.9, 634.9, 0.0] in millimeters.

   Since the SA1 frame rotates with respect to the SA1 Zero Position
   frame, its orientation is provided in CK files.

   In zero gimbal position this frame is co-aligned with the SA1 Zero
   Position frame.

   This diagram illustrates the SA1 frame in zero position:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                     +Xsa1_0   |||     |/ \  +Xsa2_0
                     +Xsa1  ^ _|||     |\_/ ^+Xsa2
                            ||             ||
                            ||             ||
      +Y Solar Array        ||             ||        -Y Solar Array
        o============ <-----x|    _        |o-----> ============o
               +Zsa1_0       |   |  ^+Xsc  |       +Zsa2_0
               +Zsa1         |   |  |  |   |       +Zsa2
                             |   |  |  |   |
                             |___|__|__|___|
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc, +Ysa2_0, and +Ysa2
                                     LGA-B              are out of the page.

                                                       +Ysa1_0 and +Ysa1 are
                                                            into the page.

   The keywords below define the SA1 frame as a CK-based frame.

   \begindata

      FRAME_KPLO_SA1                = -155421
      FRAME_-155421_NAME            = 'KPLO_SA1'
      FRAME_-155421_CLASS           = 3
      FRAME_-155421_CLASS_ID        = -155421
      FRAME_-155421_CENTER          = -155
      CK_-155421_SCLK               = -155
      CK_-155421_SPK                = -155

   \begintext


KPLO Solar Array #2 ZERO (SA2_ZERO) Frame
--------------------------------------------------------

   The SA2 Zero Position frame is defined by the array design as
   follows:

      *  +Z axis is nominally along the spacecraft -Y axis and is
         parallel to the array rotation axis;

      *  +X axis is nominally along the spacecraft +X axis;

      *  +Y axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [790.9, -634.9, 0.0] in millimeters.

   Nominally, the SA2 frame is fixed with respect to, and is rotated by
   +90 degrees about X from the spacecraft frame:

      Mspacecraft->sa2_0 = [+90]X [0]Y [0]Z

      Vsa2_0 = Mspacecraft->sa2_0 * Vspacecraft

   This diagram illustrates the SA2 Zero Position frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                     +Xsa1_0   |||     |/ \  +Xsa2_0
                            ^ _|||     |\_/ ^
                            ||             ||
                            ||             ||
      +Y Solar Array        ||             ||        -Y Solar Array
        o============ <-----x|    _        |o-----> ============o
               +Zsa1_0       |   |  ^+Xsc  |       +Zsa2_0
                             |   |  |  |   |
                             |   |  |  |   |
                             |___|__|__|___|
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc and +Ysa2_0 are
                                     LGA-B             out of the page.

                                                   +Ysa1_0 is into the page.

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_SA2_ZERO           = -155562
      FRAME_-155562_NAME            = 'KPLO_SA2_ZERO'
      FRAME_-155562_CLASS           = 4
      FRAME_-155562_CLASS_ID        = -155562
      FRAME_-155562_CENTER          = -155
      TKFRAME_-155562_SPEC          = 'ANGLES'
      TKFRAME_-155562_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155562_ANGLES        = ( -90.0, 0.0, 0.0 )
      TKFRAME_-155562_AXES          = (   1,   2,   3   )
      TKFRAME_-155562_UNITS         = 'DEGREES'

   \begintext


KPLO Solar Array #2 (SA2) Frame
--------------------------------------------------------

   The SA2 frame is defined by the array design as follows:

      *  -X axis is along the normal on the solar array active cell side;

      *  +Z axis is nominally along the spacecraft -Y axis and is
         parallel to the array rotation axis;

      *  +Y axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [790.9, -634.9, 0.0] in millimeters.

   Since the SA2 frame rotates with respect to the SA2 Zero Position
   frame, its orientation is provided in CK files.

   In zero gimbal position this frame is co-aligned with the SA2 Zero
   Position frame.

   This diagram illustrates the SA2 frame in zero position:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                     +Xsa1_0   |||     |/ \  +Xsa2_0
                     +Xsa1  ^ _|||     |\_/ ^+Xsa2
                            ||             ||
                            ||             ||
      +Y Solar Array        ||             ||        -Y Solar Array
        o============ <-----x|    _        |o-----> ============o
               +Zsa1_0       |   |  ^+Xsc  |       +Zsa2_0
               +Zsa1         |   |  |  |   |       +Zsa2
                             |   |  |  |   |
                             |___|__|__|___|
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc, +Ysa2_0, and +Ysa2
                                     LGA-B              are out of the page.

                                                       +Ysa1_0 and +Ysa1 are
                                                            into the page.

   The keywords below define the SA2 frame as a CK-based frame.

   \begindata

      FRAME_KPLO_SA2                = -155422
      FRAME_-155422_NAME            = 'KPLO_SA2'
      FRAME_-155422_CLASS           = 3
      FRAME_-155422_CLASS_ID        = -155422
      FRAME_-155422_CENTER          = -155
      CK_-155422_SCLK               = -155
      CK_-155422_SPK                = -155

   \begintext


Low Gain Antenna Upper (LGA_A) Frame
--------------------------------------------------------

   The LGA upper (LGA_A) frame is defined by the antenna design as
   follows:

      *  +Z axis is along the antenna boresight;

      *  +Y axis is nominally parallel to the spacecraft +Y axis;

      *  +X axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [1939.1, -143.0, -270.2] in millimeters.

   Nominally, the LGA Upper frame is fixed with respect to, and is
   rotated by +110 degrees about Y from the spacecraft frame:

      Mspacecraft->lgaa = [0]X [+110]Y [0]Z

      Vlgaa = Mspacecraft->lgaa * Vspacecraft

   This diagram illustrates the LGA Upper frame:

      +Z s/c side (science deck) view:
      --------------------------------

                                     +Zlgaa
                                    ^
                                    |
                                    |
                              <-----*| KMAG
                        +Ylgaa      ||
                                  __||_  _
                               |||     |/ \
         _______________      _|||     |\_/      _______________
        |             | \    |             |    / |             |
        |             |  \   |             |   /  |             |
        |             |   `. |             | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc is out of
                                     LGA-B              the page.

                                                  +Zlgaa points 20 deg
                                                     below the page.

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_LGA_A              = -155831
      FRAME_-155831_NAME            = 'KPLO_LGA_A'
      FRAME_-155831_CLASS           = 4
      FRAME_-155831_CLASS_ID        = -155831
      FRAME_-155831_CENTER          = -155
      TKFRAME_-155831_SPEC          = 'ANGLES'
      TKFRAME_-155831_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155831_ANGLES        = ( 0.0, -110.0, 0.0 )
      TKFRAME_-155831_AXES          = ( 1,      2,   3   )
      TKFRAME_-155831_UNITS         = 'DEGREES'

   \begintext


Low Gain Antenna Lower (LGA_B) Frame
--------------------------------------------------------

   The LGA Lower (LGA_B) frame is defined by the antenna design as
   follows:

      *  +Z axis is along the antenna boresight;

      *  +Y axis is nominally parallel to the spacecraft +Y axis;

      *  +X axis completes the right handed frame;

      *  the origin of this frame is at the spacecraft to instrument
         interface, at [-24.3, 0.0, 941.7] in millimeters.

   Nominally, the LGA Lower frame is fixed with respect to, and is
   rotated by -70 degrees about Y from the spacecraft frame:

      Mspacecraft->lgab = [0]X [-70]Y [0]Z

      Vlgab = Mspacecraft->lgab * Vspacecraft

   This diagram illustrates the LGA Lower frame:

      +Z s/c side (science deck) view:
      --------------------------------

                               LGA-A | KMAG
                                    ||
                                  __||_  _
                               |||     |/ \
         _______________      _|||     |\_/      _______________
        |             | \    |             |    / |             |
        |             |  \   |             |   /  |             |
        |             |   `. |             | .'   |             |
        |             |   | o|    _        |o |   |             |
        |             |   .' |   |  ^+Xsc  | `.   |             |
        |             |  /   |   |  |  |   |   \  |             |
        |_____________|_/    |   |  |  |   |    \_|_____________|
     +Y Solar Array          |___|__|__|___|       -Y Solar Array
                              <-----o____|
                          +Ysc     +Zsc
                                    |                +Zsc is out of
                              <-----* LGA-B              the page.
                        +Ylgab      |
                                    |              +Zlgaa points 20 deg
                                    v                 above the page.
                                     +Zlgab

   The angles provided in the frame definition below are the nominal
   values.

   Because SPICE fixed offset frame definitions provide the rotations
   from the fixed offset frame to its reference frame, in the
   definition below the order of axes is reversed and the angle signs
   are negated compared to what's specified in the description above.

   \begindata

      FRAME_KPLO_LGA_B              = -155832
      FRAME_-155832_NAME            = 'KPLO_LGA_B'
      FRAME_-155832_CLASS           = 4
      FRAME_-155832_CLASS_ID        = -155832
      FRAME_-155832_CENTER          = -155
      TKFRAME_-155832_SPEC          = 'ANGLES'
      TKFRAME_-155832_RELATIVE      = 'KPLO_SPACECRAFT'
      TKFRAME_-155832_ANGLES        = ( 0.0, 70.0, 0.0 )
      TKFRAME_-155832_AXES          = ( 1,    2,   3   )
      TKFRAME_-155832_UNITS         = 'DEGREES'

   \begintext


KPLO NAIF ID Codes -- Definitions
--------------------------------------------------------

   This section contains name to NAIF ID mappings for the KPLO mission.
   Once the contents of this file is loaded into the KERNEL POOL, these
   mappings become available within SPICE, making it possible to use
   names instead of ID code in the high level SPICE routine calls.

   The set of codes below is not complete. Additional ID codes for some
   KPLO instruments are defined in the IK files.

   Spacecraft:
   -----------

      KPLO                            -155
      KOREA PATHFINDER LUNAR ORBITER  -155
      KPLO_SPACECRAFT                 -155000
      KPLO_SC_BUS                     -155000


   Spacecraft structures:
   ----------------------

      KPLO_SA1                        -155421
      KPLO_SA1_ZERO                   -155561
      KPLO_SA2                        -155422
      KPLO_SA2_ZERO                   -155562
      KPLO_LGA_A                      -155831
      KPLO_LGA_B                      -155832
      KPLO_HGA                        -155191
      KPLO_HGA_ZERO                   -155190
      KPLO_STA1                       -155501
      KPLO_STA2                       -155502

   Science Instruments:
   --------------------

      KPLO_LUTI                       -155100
      KPLO_LUTIA                      -155101
      KPLO_LUTIB                      -155102
      KPLO_POLCAM                     -155110
      KPLO_POLCAM-L                   -155111
      KPLO_POLCAM-R                   -155112
      KPLO_KGRS                       -155130
      KPLO_KMAG                       -155120
      KPLO_SHC                        -155150
      KPLO_SHC_A                      -155151

   The mappings summarized in this table are implemented by the keywords
   below.

   \begindata

      NAIF_BODY_NAME += ( 'KPLO' )
      NAIF_BODY_CODE += ( -155 )

      NAIF_BODY_NAME += ( 'KOREA PATHFINDER LUNAR ORBITER' )
      NAIF_BODY_CODE += ( -155 )

      NAIF_BODY_NAME += ( 'KPLO_SPACECRAFT' )
      NAIF_BODY_CODE += ( -155000 )

      NAIF_BODY_NAME += ( 'KPLO_SC_BUS' )
      NAIF_BODY_CODE += ( -155000 )

      NAIF_BODY_NAME += ( 'KPLO_SA1' )
      NAIF_BODY_CODE += ( -155421 )

      NAIF_BODY_NAME += ( 'KPLO_SA1_ZERO' )
      NAIF_BODY_CODE += ( -155561 )

      NAIF_BODY_NAME += ( 'KPLO_SA2' )
      NAIF_BODY_CODE += ( -155422 )

      NAIF_BODY_NAME += ( 'KPLO_SA2_ZERO' )
      NAIF_BODY_CODE += ( -155562 )

      NAIF_BODY_NAME += ( 'KPLO_LGA_A' )
      NAIF_BODY_CODE += ( -155831 )

      NAIF_BODY_NAME += ( 'KPLO_LGA_B' )
      NAIF_BODY_CODE += ( -155832 )

      NAIF_BODY_NAME += ( 'KPLO_HGA' )
      NAIF_BODY_CODE += ( -155040 )

      NAIF_BODY_NAME += ( 'KPLO_HGA' )
      NAIF_BODY_CODE += ( -155191 )

      NAIF_BODY_NAME += ( 'KPLO_HGA_ZERO' )
      NAIF_BODY_CODE += ( -155190 )

      NAIF_BODY_NAME += ( 'KPLO_STA1' )
      NAIF_BODY_CODE += ( -155501 )

      NAIF_BODY_NAME += ( 'KPLO_STA2' )
      NAIF_BODY_CODE += ( -155502 )

      NAIF_BODY_NAME += ( 'KPLO_LUTI' )
      NAIF_BODY_CODE += ( -155100 )

      NAIF_BODY_NAME += ( 'KPLO_LUTIA' )
      NAIF_BODY_CODE += ( -155101 )

      NAIF_BODY_NAME += ( 'KPLO_LUTIB' )
      NAIF_BODY_CODE += ( -155102 )

      NAIF_BODY_NAME += ( 'KPLO_POLCAM' )
      NAIF_BODY_CODE += ( -155110 )

      NAIF_BODY_NAME += ( 'KPLO_POLCAM-L' )
      NAIF_BODY_CODE += ( -155111 )

      NAIF_BODY_NAME += ( 'KPLO_POLCAM-R' )
      NAIF_BODY_CODE += ( -155112 )

      NAIF_BODY_NAME += ( 'KPLO_KGRS' )
      NAIF_BODY_CODE += ( -155130 )

      NAIF_BODY_NAME += ( 'KPLO_KMAG' )
      NAIF_BODY_CODE += ( -155120 )

      NAIF_BODY_NAME += ( 'KPLO_SHC' )
      NAIF_BODY_CODE += ( -155150 )

      NAIF_BODY_NAME += ( 'KPLO_SHC_A' )
      NAIF_BODY_CODE += ( -155151 )

   \begintext

End of FK file.
