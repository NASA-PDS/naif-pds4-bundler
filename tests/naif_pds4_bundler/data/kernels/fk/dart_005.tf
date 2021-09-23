KPL/FK

DART Frames Kernel
===========================================================================

   This frame kernel contains a complete set of frame definitions for the
   Double Asteroid Redirection Test (DART) including definitions for
   the DART structures and DART science instrument frames. This kernel
   also contains NAIF ID/name mapping for the DART instruments.


Version and Date
------------------------------------------------------------------------

   Version 005 -- September 20, 2021 -- Marc Costa Sitja, NAIF/JPL

      Added several sections, frame definitions and s/c diagrams.

      Updated solar array and HGA frame names and added frames
      to the frame chain.

   Version 004 -- July 9, 2021 -- Ian Wick Murphy, JHU/APL

      Contains the s/c, SA, HGA and DRACO reference frames.


References
------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``C-Kernel Required Reading''


Contact Information
------------------------------------------------------------------------

   Ian Wick Murphy JHU/APL, ian.murphy@jhuapl.edu
   Marc Costa Sitja, NAIF/JPL, Marc.Costa.Sitja@jpl.nasa.gov


Implementation Notes
------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make
   use of this kernel must ``load'' the kernel, normally during program
   initialization. The SPICE routine FURNSH loads a kernel file into
   the pool as shown below.

      CALL FURNSH ( 'kernel_name; )    -- FORTRAN
      furnsh_c ( "kernel_name" );      -- C
      cspice_furnsh, kernel_name       -- IDL
      cspice_furnsh( 'kernel_name' )   -- MATLAB

   In order for a program or routine to extract data from the pool, the
   SPICELIB routines GDPOOL, GIPOOL, and GCPOOL are used.  See [2] for
   more details.

   This file was created and may be updated with a text editor or word
   processor.


DART NAIF ID Codes -- Summary Section
------------------------------------------------------------------------

   The following names and NAIF ID codes are assigned to the DART s/c,
   its structures and science instruments (the keywords implementing
   these definitions are located in the section "DART NAIF ID Codes --
   Definition Section" at the end of this file):

   DART and DART Structures names/IDs:
   -----------------------------------
            DART                     -135

            DART_SA_PY               -135010
            DART_SA_MY               -135020

            DART_HGA                 -135030

   DRACO names/IDs:
   ----------------
            DART_DRACO               -135100
            DART_DRACO_1X1           -135101
            DART_DRACO_2X2           -135102


DART Frames
------------------------------------------------------------------------

   The following DART frames are defined in this kernel file:

           Name                    Relative to           Type        NAIF ID
      ======================    ===================  ============    =======

   DART Spacecraft and Spacecraft Structures frames:
   -------------------------------------------------
      DART_SPACECRAFT             J2000                  CK          -135000


      DART_SA_PY_ROSA             DART_SPACECRAFT        FIXED       -135011
      DART_SA_PY_GIMBAL           DART_SA_PY_ROSA        FIXED       -135012
      DART_SA_PY                  DART_SA_PY_GIMBAL      CK          -135010

      DART_SA_MY_ROSA             DART_SPACECRAFT        FIXED       -135021
      DART_SA_MY_GIMBAL           DART_SA_MY_ROSA        FIXED       -135022
      DART_SA_MY                  DART_SA_MY_GIMBAL      CK          -135020

      DART_HGA_SELF               DART_SPACECRAFT        FIXED       -135031
      DART_HGA_GIMBAL             DART_HGA_SELF          FIXED       -135032
      DART_HGA                    DART_HGA_GIMBAL        CK          -135030

   DRACO frames:
   ------------------------------------------------
      DART_DRACO                  DART_SPACECRAFT        FIXED       -135100


DART Frames Hierarchy
------------------------------------------------------------------------

  The diagram below shows the DART spacecraft, its structures, and its
  science instrument frame hierarchy.


                               "J2000" INERTIAL
         +-------------------------------------------------------+
         |                          |           |                |
         |<-pck                     |<-ck       |<-pck           |<-pck
         V                          |           V                V
    "EARTH_FIXED"                   |    "IAU_DIMORPHOS"   "IAU_DIDYMOS"
    -------------                   |    ---------------   -------------
                                    |           |                |
                                    |           |<-fixed         |<-fixed
                                    |           |                |
                                    |           V                V
                                    |   "DIMORPHOS_FIXED"  "DIDYMOS_FIXED"
                                    |   -----------------  ---------------
                                    V
                             "DART_SPACECRAFT"
              +-------------------------------------------------+
              |                |             |                  |
              |<-fixed         |<-fixed      |<-fixed           |<-fixed
              V                |             V                  V
        "DART_HGA_SELF"        |     "DART_SA_PY_ROSA"  "DART_SA_PY_ROSA"
        ---------------        |     -----------------  -----------------
              |                |             |                  |
              |<-fixed         |             |<-fixed           |<-fixed
              V                |             V                  V
       "DART_HGA_GIMBAL"       |     "DART_SA_PY_GYMBAL" "DART_SA_PY_GYMBAL"
       -----------------       |     ------------------- -------------------
              |                |              |                  |
              |<-ck            |              |<-ck              |<-ck
              V                |              V                  V
          "DART_HGA"           |         "DART_SA_PY"       "DART_SA_PY"
          ----------           |         ------------       ------------
                               V
                          "DART_DRACO"
                          ------------


DART Spacecraft and Spacecraft Structures Frames
--------------------------------------------------------------------------------

   This section of the file contains the definitions of the spacecraft
   and spacecraft structures frames.


DART Spacecraft Bus Frame
-----------------------------------------------------------

   The spacecraft bus frame -- DART_SPACECRAFT -- is defined by the s/c
   design as follows:

      -  +X axis is parallel to the HGA boresight

      -  +Z axis is normal to the forward (payload) deck

      -  +Y axis completes the right hand frame

      -  the origin of the frame is at the center of the engine deck.


   These diagrams illustrate the s/c frame:

   +X side view:
   -------------

                                    +Zsc ___
                                    |___^___|  Main Engine
                                    /   |   \
                                  .-----|-----.
    .===\ \==========='.        .------ |-------.        .'============\ \===.
    ||  / /           ||        |       |       |        ||            / /  ||
    ||  / /           ||   \.---------- o--------> -./   ||            / /  ||
    ||  / /           ||    |       +Xsc       +Ysc |    ||            / /  ||
    ||  \ \           ||    |                       |    ||            \ \  ||
    ||  / /           ||    |                     .''''. ||            / /  ||
    ||  \ \           ||    |                    '      '||            \ \  ||
    ||  / /           ||===@|                    |  HGA  ||            / /  ||
    ||  \ \           ||    |                    '      '||            \ \  ||
    ||  / /           ||    |                     '....' ||            / /  ||
    ||  \ \           ||    |         :             |    ||            \ \  ||
    ||  / /           ||    |       :::             |    ||            / /  ||
    ||  \ \           ||   /`-----..---.------------'\   ||            \ \  ||
    ||  / /           ||          ||   |      |          ||            / /  ||
    '===\ \===========.'          '-===-------'          '.============\ \==='
       -Y Solar Array               |_______|               +Y Solar Array
                               Payload
                               Deck     |
                                        | toward asteroid
                                        v
                                                 +Xsc is out of the page.
   +Z side view (Main Engine):
   ---------------------------

                             o
                             |.------.               /'@--o============/ /==o
                            .-----------------------.        +Y solar array
                            |                      0|
                            |       .-'''-.         |
                            |    .'    ..   '.      |
                            |   /   +Zsc   `. +Ysc  |
                            |   |   |   o-------->  |
                       Star |   \   '.  |  .'       |
                    Tracker |    '.   ` | '  Main   |    /
                           >|       '---|- engine   |_  /
                            |0          |          0|_=/  HGA
                            `-----------v-----------' /
      o==/ /==========o>--@./         +Xsc           /
         -Y solar array
                                                 +Zsc is out of the page.

   -X side view:
   -------------

                                        ^
                                        | Toward asteroid
                               Payload  |
                               Deck  _______
                                    |       |
    .===\ \==========='.          .-----------.          .'============\ \===.
    ||  / /           ||          |  +Xsc |  ||          ||            / /  ||
    ||  / /           ||   \.---------- x--------> -./   ||            / /  ||
    ||  / /           ||    |           |  ::: +Ysc |    ||            / /  ||
    ||  \ \           ||    |           |    :      |    ||            \ \  ||
    ||  / /           ||    |           |           |''. ||            / /  ||
    ||  \ \           ||    |           v           |HGA'||            \ \  ||
    ||  / /           ||===@|         +Zsc          |@===||            / /  ||
    ||  \ \           ||    |                       |   '||            \ \  ||
    ||  / /           ||    |                       |..' ||            / /  ||
    ||  \ \           ||    |                       |    ||            \ \  ||
    ||  / /           ||    |                       |    ||            / /  ||
    ||  \ \           ||   /`-----------------------'\   ||            \ \  ||
    ||  / /           ||        |               |        ||            / /  ||
    '===\ \===========.'        '---------------'        '.============\ \==='
       -Y Solar Array              '---------'             +Y Solar Array
                                    \_______/
                                    |_______|  Main Engine


                                                 +Xsc is inside the page.

   +Y side view:
   -------------
                                +Y Solar Array
                  :=======================================:
                                  |       |
                    \.____________@=======@____________./
                 .---|                                 |--.   Payload
               .-|   |                                 |--'   deck
        +Zsc .'| |   |                                 |---.
          .--| | |   |                                 |   |--.
          <----------o +Ysc                            |   |  | -----> Toward
          '--| | |   |                                 |   |--'       asteroid
       Main  '.| |   |               ...               |---'
      Engine   '-|   |            .'     '.            |--.
                 '---|___________'   HGA   '___________|--'
                     v           '.       .'            \
                   +Xsc           |' ... '|
                  :======================================:
                                -Y Solar Array
                                                +Ysc is out of the page.


   -Z side view (Payload):
   -----------------------
                                                   o
      o==/ /==========o--@'\               .------.|
       +Y solar array       .-----------------------.
                            |   .---. Battery       |
                            |   |   |               |< Star
                            |   '---'  .. Draco     |  Tracker
                            +Ysc    +Zsc   `.       |
                            |  <--------x   |       |
                            |       '.  |  .'       |
                            |         ` | ' .---.   |
                            |           |   |   |   |
                            |           |   '---'   |
                            `-----------v-----------'
                                       +Xsc          \.@--o============/ /==o
                                                         -Y solar array

                                                 +Zsc is into the page.


   Since the S/C bus attitude is provided by a C kernel (see [3] for
   more information), this frame is defined as a CK-based frame.

   \begindata

        FRAME_DART_SPACECRAFT        = -135000
        FRAME_-135000_NAME           = 'DART_SPACECRAFT'
        FRAME_-135000_CLASS          = 3
        FRAME_-135000_CLASS_ID       = -135000
        FRAME_-135000_CENTER         = -135
        CK_-135000_SCLK              = -135
        CK_-135000_SPK               = -135

   \begintext


Solar Array Frames
------------------------------------------------------------------------

   DART solar arrays are articulated (having one degree of freedom),
   therefore the Solar Array frames, DART_SA_PY and DART_SA_MY, are
   defined as CK frames with their orientation given relative to
   DART_SA_PY_GIMBAL and DART_SA_GIMBAL respectively. The orientation
   of these frames is provided by the mechanical gimbal angle given
   the each SADA potentiometer.

   Given that the solar arrays are initially folded in the ROSA
   (Roll Out Solar Array) mechanism, and are deployed after launch,
   the gimbal reference frames are defined with respect to the ROSA
   reference frames -- DART_SA_PY_ROSA and DART_SA_MY_ROSA.

   The ROSA frames are on opposite sides of the s/c and are not aligned
   relative to the spacecraft body axes. The current position of the ROSA
   frame for each solar array can be computed in terms of the mechanical
   gimbal angle  as follows:

      c(a)  = cos(a); cd(a) = cosd(a)
      s(a)  = sin(a); sd(a) = sind(a)

      ap = +Y SADA angle; am = -Y SADA angle.

      SA-Y:

        .- -.        .-                       -.  .- -.
        | X |        |  0 -s(am-30) -c(am-30)  |  | X |
        | Y |     =  | -1  0           0       |  | Y |
        | Z |        |  0  c(am-30) -s(am-30)  |  | Z |
        `- -' S/C    `-                       -'  `- -' SA-Y

      SA+Y:

        .- -.        .-                       -.  .- -.
        | X |        |  0  s(ap-30)  c(ap-30)  |  | X |
        | Y |     =  |  1  0           0       |  | Y |
        | Z |        |  0  c(ap-30) -s(ap-30)  |  | Z |
        `- -' S/C    `-                       -'  `- -' SA+Y


   Note, the subtraction of 30 accounts for a 30 deg (pi/6 rad) clocking
   applied to each SADA due to mounting restrictions.

   DART_SA_PZ_ROSA and DART_SA_MZ_ROSA are two ``fixed-offset'' frames,
   defined with respect to DART_SPACECRAFT, as follows:

      -  +X is parallel to the longest side of the array, positively
         oriented from the yoke to the end of the wing;

      -  +X is parallel to the spacecraft bus +X axis;

      -  +Y completes the right-handed frame;

      -  the origin of the frame is located at the yoke geometric
         center.


   DART_SA_PZ_GIMBAL and DART_SA_MZ_GIMBAL are two ``fixed-offset'' frames,
   defined with respect to DART_SA_MZ_ROSA and DART_SA_MZ_ROSA frames have
   and nominally are equivalent to them.


   Both Solar Array frames (DART_SA_PZ and DART_SA_MZ) are defined as
   follows:

      -  +X extends along the rotation axis of the gimbal and a
         counter-clockwise rotation about this axis produces a
         positive angle increase relative to the gimbal
         potentiometer;

      -  +Y is the sun-positive normal vector that is to be aligned with
         the spacecraft-to-sun vector;

      -  +Z completes the right-handed frame and is parallel to the s/c;

      -  the origin of the frame is located at the yoke geometric center.


   This diagram illustrates the DART_SA_PY_ROSA, DART_SA_MY_ROSA,
   DART_SA_PZ_GIMBAL, and DART_SA_MZ_GIMBAL frames:

   +Z side view:
   -------------
                                         +Ysa+y_gimbal ^
                                         +Ysa+y_rosa   |
                                                       |
                                                       |      +Xsa+y_gimbal
                            o                          |      +Xsa+y_rosa
                            |.------.  +Zsa+y_gimbal /'o---------> ====/ /==o
                            .--------- +Zsa+y_rosa -.        +Y solar array
                            |                      0|
                            |       .-'''-.         |
                            |    .'    ..   '.      |
                            |   /   +Zsc   `. +Ysc  |
                            |   |   |   o-------->  |
                       Star |   \   `.  |   '       |
                    Tracker |    '.   ` | '  Main   |    /
                           >|       '---|- engine   |_  /
           +Xsa-y_gimbal  +Zsa-y_gimbal |          0|_=/  HGA
           +Xsa-y_rosa    +Zsa-y_rosa --v-----------' /
      o==/ /=== <---------o./         +Xsc           /
         -Y solar array   |
                          |                      +Zsc, +Zsa+y_gimbal,
                          |                      +Zsa+y_rosa, +Zsa-y_gimbal,
                          | +Ysa-y_gimbal        and +Zsa-y_rosa are out of
                          v +Ysa-y_rosa          the page.


   These sets of keywords define solar array frames:

   \begindata

      FRAME_DART_SA_PY_ROSA           = -135011
      FRAME_-135011_NAME              = 'DART_SA_PY_ROSA'
      FRAME_-135011_CLASS             = 4
      FRAME_-135011_CLASS_ID          = -135011
      FRAME_-135011_CENTER            = -135
      TKFRAME_-135011_SPEC            = 'ANGLES'
      TKFRAME_-135011_RELATIVE        = 'DART_SPACECRAFT'
      TKFRAME_-135011_ANGLES          = ( 0.0, 0.0, -90.0 )
      TKFRAME_-135011_AXES            = ( 1,   2,     3   )
      TKFRAME_-135011_UNITS           = 'DEGREES'

      FRAME_DART_SA_PY_GIMBAL         = -135012
      FRAME_-135012_NAME              = 'DART_SA_PY_GIMBAL'
      FRAME_-135012_CLASS             = 4
      FRAME_-135012_CLASS_ID          = -135012
      FRAME_-135012_CENTER            = -135
      TKFRAME_-135012_SPEC            = 'ANGLES'
      TKFRAME_-135012_RELATIVE        = 'DART_SA_PY_ROSA'
      TKFRAME_-135012_ANGLES          = ( 0.0, 0.0, 0.0 )
      TKFRAME_-135012_AXES            = ( 1,   2,   3   )
      TKFRAME_-135012_UNITS           = 'DEGREES'

      FRAME_DART_SA_PY                = -135010
      FRAME_-135010_NAME              = 'DART_SA_PY'
      FRAME_-135010_CLASS             =  3
      FRAME_-135010_CLASS_ID          = -135010
      FRAME_-135010_CENTER            = -135
      CK_-135010_SCLK                 = -135
      CK_-135010_SPK                  = -135

      FRAME_DART_SA_MY_ROSA           = -135021
      FRAME_-135021_NAME              = 'DART_SA_MY_ROSA'
      FRAME_-135021_CLASS             = 4
      FRAME_-135021_CLASS_ID          = -135021
      FRAME_-135021_CENTER            = -135
      TKFRAME_-135021_SPEC            = 'ANGLES'
      TKFRAME_-135021_RELATIVE        = 'DART_SPACECRAFT'
      TKFRAME_-135021_ANGLES          = ( 0.0, 0.0,  90.0  )
      TKFRAME_-135021_AXES            = ( 1,   2,     3    )
      TKFRAME_-135021_UNITS           = 'DEGREES'

      FRAME_DART_SA_MY_GIMBAL         = -135022
      FRAME_-135022_NAME              = 'DART_SA_MY_GIMBAL'
      FRAME_-135022_CLASS             = 4
      FRAME_-135022_CLASS_ID          = -135022
      FRAME_-135022_CENTER            = -135
      TKFRAME_-135022_SPEC            = 'ANGLES'
      TKFRAME_-135022_RELATIVE        = 'DART_SA_MY_ROSA'
      TKFRAME_-135022_ANGLES          = ( 0.0, 0.0, 0.0 )
      TKFRAME_-135022_AXES            = ( 1,   2,   3   )
      TKFRAME_-135022_UNITS           = 'DEGREES'

      FRAME_DART_SA_MY                = -135020
      FRAME_-135020_NAME              = 'DART_SA_MY'
      FRAME_-135020_CLASS             =  3
      FRAME_-135020_CLASS_ID          = -135020
      FRAME_-135020_CENTER            = -135
      CK_-135020_SCLK                 = -135
      CK_-135020_SPK                  = -135

   \begintext


High-Gain Antenna Frames
------------------------------------------------------------------------

   The DART High Gain Antenna is attached to the s/c bus +Y panel by a
   gimbal providing one degree of freedom to articulate during flight to
   track the Earth.

   The HGA frame is first rotated 52.47 degrees counter-clockwise about the
   the s/c +Z axis. This intermediate frame is denoted as the ``self''
   frame -- DART_HGA_SELF --. Then, a second rotation of +30 degrees about
   the DART_HGA_SELF frame +Y axis is performed to reach the final alignment,
   denoted as the ``gimbal'' frame -- DART_HGA_GIMBAL --. As the gimbal
   rotates, the ``HGA'' frame -- DART_HGA --, representing the current
   orientation of the antenna boresight, can be computed in terms of the
   mechanical gimbal angle, a, as follows:

      c(a) = cos(a); cd(a) = cosd(a)
      s(a) = sin(a); sd(a) = sind(a)

      HGA:
                       S2SC                       G2S               HGA2G
      .- -.   .-                     -.    .-              -.   .-           -.
      | X |   | cd(52.47) -sd(52.47) 0 |   | c(30)  0 s(30) |   | c(a) 0 s(a) |
      | Y | = | sd(52.47)  cd(52.47) 0 | * | 0       1 0    | * | 0    1 0    |
      | Z |   | 0           0        1 |   | -s(30) 0 c(30) |   | s(a) 0 c(a) |
      `- -'   `-                      -'   `-              -'   `-           -'
       S/C


   The DART_HGA frame is defined as follows:

      -  +X axis is aligned with the boresight of the antenna and is to
         be aligned with the spacecraft-to-earth vector;

      -  +Y axis extends along the rotation axis of the gimbal, and a
         counter-clockwise motion about this axis produces a positive angle
         increase relative to the gimbal potentiometer;

      -  +Z axis completes the right hand frame;

      -  the origin of the frame is located at the phase center
         (theoretical and nominal location).


   The HGA angle ranges from 0 degrees at the lower hardstop (launch-lock)
   position, to -55 degrees at the upper range of motion. Note, lower and
   upper are used in reference to the s/c +Z axis: in the lower hardstop
   position (0 deg), the antenna boresight has the largest -Z component
   relative to the DART_SPACECRAFT frame. At the upper range of motion
   (-55 deg), the antenna boresight has the largest +Z component relative
   to the DART_SPACECRAFT frame.

   This diagram illustrates the DART HGA frame chain in the zero gimbal
   position:

   +Z side view:
   -------------
                             o
                             |.------.               /'@--o============/ /==o
                            .-----------------------.        +Y solar array
                            |                      0|
                            |       .-'''-.         |
                            |    .'    ..   '.      |
                            |   /   +Zsc   `. +Ysc  |
                            |   |   |   o-------->  |
                       Star |   \   `.  |        ^ +Yself      +Xself
                    Tracker |    '.   ` | ' .'    `.|    /    .>
                           >|       '--.|.-'        `.  / . '
                            |0          |          0|_'o'     HGA
                            `-----------v-----------' / +Zself
      o==/ /==========o>--@./         +Xsc           /
         -Y solar array

                                                 +Zsc and +Zelf are out
                                                 of the page.

   This set of keywords defines the HGA frames:

   \begindata

      FRAME_DART_HGA_SELF             = -135031
      FRAME_-135031_NAME              = 'DART_HGA_SELF'
      FRAME_-135031_CLASS             = 4
      FRAME_-135031_CLASS_ID          = -135031
      FRAME_-135031_CENTER            = -135
      TKFRAME_-135031_SPEC            = 'ANGLES'
      TKFRAME_-135031_RELATIVE        = 'DART_SPACECRAFT'
      TKFRAME_-135031_ANGLES          = ( 0.0, 0.0, -52.47 )
      TKFRAME_-135031_AXES            = ( 1,   2,     3    )
      TKFRAME_-135031_UNITS           = 'DEGREES'

      FRAME_DART_HGA_GIMBAL           = -135032
      FRAME_-135032_NAME              = 'DART_HGA_GIMBAL'
      FRAME_-135032_CLASS             = 4
      FRAME_-135032_CLASS_ID          = -135032
      FRAME_-135032_CENTER            = -135
      TKFRAME_-135032_SPEC            = 'ANGLES'
      TKFRAME_-135032_RELATIVE        = 'DART_HGA_SELF'
      TKFRAME_-135032_ANGLES          = ( 0.0, -30.0,  0.0 )
      TKFRAME_-135032_AXES            = ( 1,     2,    3   )
      TKFRAME_-135032_UNITS           = 'DEGREES'

      FRAME_DART_HGA                  = -135030
      FRAME_-135030_NAME              = 'DART_HGA'
      FRAME_-135030_CLASS             =  3
      FRAME_-135030_CLASS_ID          = -135030
      FRAME_-135030_CENTER            = -135
      CK_-135030_SCLK                 = -135
      CK_-135030_SPK                  = -135

   \begintext


DRACO Frame
------------------------------------------------------------------------

   The Didymos Reconnaissance and Asteroid Camera for OpNav (DRACO) frame
   -- DART_DRACO -- is defined by the camera design as follows:

      -  +Z axis is the camera boresight and is co-aligned with the
         s/c +Z axis

      -  +X axis is nominally rotated 135 degrees around the
          s/c +Z axis

      -  +Y axis completes the right hand frame

      -  the origin of the frame is at the camera focal point.

   This diagram illustrates the camera frames:


   -Z side view (Payload):
   -----------------------
                                                   o
      o==/ /==========o--@'\               .------.|
       +Y solar array      +Xdraco -----------------.
                            |    ^              .> +Ydraco
                            |   | '.          .'    |< Star
                            |   '---'. ..   .'      |  Tracker
                            +Ysc      '.  .'        |
                            |  <--------x' +Zdraco  |
                            |       '.  |  +Zdart   |
                            |         ' | ' .---.   |
                            |           |   |   |   |
                            |           |   '---'   |
                            `-----------v-----------'
                                       +Xsc          \.@--o============/ /==o
                                                         -Y solar array

                                                 +Zsc and +Zdraco are
                                                  into the page.

   +X side view:
   -------------

                                    +Zsc ___
                                    |___^___|  Main Engine
                                    /   |   \
                                  .-----|-----.
    .===\ \==========='.        .------ |-------.        .'============\ \===.
    ||__ / /__________||        |       |       |        ||____________/ /__||
    ||  / /           ||   \.---------- o--------> -./   ||            / /  ||
    ||  / /           ||    |       +Xsc       +Ysc |    ||            / /  ||
    ||  \ \           ||    |                       |    ||            \ \  ||
    ||  / /           ||    |                     .''''. ||            / /  ||
    ||  \ \           ||    |                    '      '||            \ \  ||
    ||  / /           ||===@|                    |  HGA  ||            / /  ||
    ||  \ \           ||    |                    '      '||            \ \  ||
    ||  / /           ||    |                     '._ .' ||            / /  ||
    ||  \ \           ||    |         :  +Zdraco    |    ||            \ \  ||
    ||  / /           ||    |       ::: ^           |    ||            / /  ||
    ||__\ \___________||   /`-----..---.|-----------'\   ||____________\ \__||
    ||  / /           ||          ||   ||     |          ||            / /  ||
    '===\ \===========.'          '-===-|-----'          '.============\ \==='
       -Y Solar Array               |___o___|               +Y Solar Array

                                                 +Xsc is out of the page.

   This set of keywords defines the DRACO frame:

   \begindata

        FRAME_DART_DRACO             = -135100
        FRAME_-135100_NAME           = 'DART_DRACO'
        FRAME_-135100_CLASS          = 4
        FRAME_-135100_CLASS_ID       = -135100
        FRAME_-135100_CENTER         = -135
        TKFRAME_-135100_SPEC         = 'MATRIX'
        TKFRAME_-135100_RELATIVE     = 'DART_SPACECRAFT'
        TKFRAME_-135100_MATRIX       = ( -0.707107,  0.707107, 0.0,
                                         -0.707107, -0.707107, 0.0,
                                          0.0,       0.0,      1.0 )

   \begintext


DART NAIF ID Codes -- Definitions
=====================================================================

   This section contains name to NAIF ID mappings for the DART mission.
   Once the contents of this file are loaded into the KERNEL POOL, these
   mappings become available within SPICE, making it possible to use
   names instead of ID code in high level SPICE routine calls.

   \begindata

      NAIF_BODY_NAME   += ( 'DART' )
      NAIF_BODY_CODE   += ( -135   )


      NAIF_BODY_NAME   += ( 'DART_SPACECRAFT' )
      NAIF_BODY_CODE   += ( -135000           )

      NAIF_BODY_NAME   += ( 'DART_SA_PY' )
      NAIF_BODY_CODE   += ( -135010      )

      NAIF_BODY_NAME   += ( 'DART_SA_MY' )
      NAIF_BODY_CODE   += ( -135020      )

      NAIF_BODY_NAME   += ( 'DART_HGA' )
      NAIF_BODY_CODE   += ( -135030    )


      NAIF_BODY_NAME   += ( 'DART_DRACO' )
      NAIF_BODY_CODE   += ( -135100      )

      NAIF_BODY_NAME   += ( 'DART_DRACO_1X1' )
      NAIF_BODY_CODE   += ( -135101          )

      NAIF_BODY_NAME   += ( 'DART_DRACO_2X2' )
      NAIF_BODY_CODE   += ( -135102          )

   \begintext


End of FK file.
