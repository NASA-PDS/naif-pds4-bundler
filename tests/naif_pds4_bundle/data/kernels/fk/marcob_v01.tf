KPL/FK


MARCO-B Frame Definitions Kernel
===============================================================================

   This frame kernel contains definitions for the MARCO-B spacecraft,
   antenna, and other structure frames and FOVs (if applicable).
 

Version and Date
-------------------------------------------------------------------------------

   Version 0.1 -- April 21, 2019 -- Boris Semenov, NAIF

      Initial Release.


Contact Information
-------------------------------------------------------------------------------

   Boris V. Semenov, NAIF/JPL, (818)-354-8136, Boris.Semenov@jpl.nasa.gov


References
-------------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``C-Kernel Required Reading''

   4. MarCO_frame.pptx, provided by Tomas Martin-Mur, JPL NAV on April
      3, 2019


Implementation Notes
-------------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make
   use of this frame kernel must ``load'' the kernel, normally during
   program initialization. The SPICELIB routine FURNSH loads a
   kernel file into the pool as shown below.

      CALL FURNSH ( 'frame_kernel_name; )     (FORTRAN)
      furnsh_c ( "frame_kernel_name" );       (C)
      cspice_furnsh, "frame_kernel_name"      (IDL)
      cspice_furnsh( 'frame_kernel_name' )    (MATLAB)

   This file was created and may be updated with a text editor.


MARCO-B NAIF ID Codes
-------------------------------------------------------------------------------

   The following names and NAIF ID codes are assigned to the MARCO-B
   spacecraft and its structures (the keywords implementing these
   name-ID mappings are located in the section "MARCO-B NAIF ID Codes
   -- Definition Section" at the end of this file):

   MARCO-B spacecraft:
   -------------------
      MARCO-B                    -66      (MARS CUBE ONE B, EVE)
      MARCO-B_SPACECRAFT         -66000

   MARCO-B structures:
   -------------------
      MARCO-B_TCM_ENGINE         -66110
      MARCO-B_RADIATOR           -66120
      MARCO-B_STAR_TRACKER       -66130
      MARCO-B_SA                 -66140

   MARCO-B antennas:
   -----------------
      MARCO-B_HGA                -66210
      MARCO-B_MGA                -66220
      MARCO-B_LGA                -66230
      MARCO-B_UHF                -66240

   MARCO-B instruments:
   --------------------
      MARCO-B_NAC                -66310
      MARCO-B_WAC                -66320


MARCO-B Frames
-------------------------------------------------------------------------------

   The following MARCO-B frames are defined in this kernel file:

      Name                       Relative to                 Type   Frame ID
      ========================== ========================== ======= ========

   Spacecraft frames (-6600x):
   ---------------------------
      MARCO-B_SPACECRAFT         J2000                      CK      -66000

   Structure frames (-661xx):
   --------------------------
      MARCO-B_TCM_ENGINE         MARCO-B_SPACECRAFT         FIXED   -66110
      MARCO-B_RADIATOR           MARCO-B_SPACECRAFT         FIXED   -66120
      MARCO-B_STAR_TRACKER       MARCO-B_SPACECRAFT         FIXED   -66130
      MARCO-B_SA                 MARCO-B_SPACECRAFT         FIXED   -66140

   Antenna frames (-662xx):
   ------------------------
      MARCO-B_HGA                MARCO-B_SPACECRAFT         FIXED   -66210
      MARCO-B_MGA                MARCO-B_SPACECRAFT         FIXED   -66220
      MARCO-B_LGA                MARCO-B_SPACECRAFT         FIXED   -66230
      MARCO-B_UHF                MARCO-B_SPACECRAFT         FIXED   -66240

   Instrument frames (-666xx):
   ---------------------------
      MARCO-B_NAC                MARCO-B_SPACECRAFT         FIXED   -66310
      MARCO-B_WAC                MARCO-B_SPACECRAFT         FIXED   -66320

   The frame descriptions and definitions are provided in the sections
   below.


MARCO-B Frame Hierarchy
-------------------------------------------------------------------------------

   The diagram below shows the MARCO-B frames hierarchy:


                             "J2000" INERTIAL
       +-------------------------------------------------------------+
       |                              |                              |
       | <--pck                       |                              | <--pck
       V                              |                              V
   "IAU_EARTH"                        |                        "IAU_MARS"
   EARTH BFR(1)                       |                        MARS BFR(1)
   ------------                       |                        -----------
                                      |
                                      |  <--ck
                                      V
                            "MARCO-B_SPACECRAFT"
       +-------------------------------------------------------------+
       | | | | | |                                             | | | |      
       | | | | | |<--fixed                            fixed--> | | | |      
       | | | | | V                                             V | | |      
       | | | | | "MARCO-B_HGA"              "MARCO-B_TCM_ENGINE" | | |      
       | | | | | -------------              -------------------- | | |      
       | | | | |                                                 | | |      
       | | | | |<--fixed                                fixed--> | | |      
       | | | | V                                                 V | |      
       | | | | "MARCO-B_MGA"                    "MARCO-B_RADIATOR" | |      
       | | | | -------------                    ------------------ | |      
       | | | |                                                     | |      
       | | | |<--fixed                                    fixed--> | |      
       | | | V                                                     V |      
       | | | "MARCO-B_LGA"                    "MARCO-B_STAR_TRACKER" |      
       | | | -------------                    ---------------------- |      
       | | |                                                         |      
       | | |<--fixed                                        fixed--> |      
       | | V                                                         V      
       | | "MARCO-B_UHF"                                  "MARCO-B_SA"      
       | | -------------                                  ------------
       | |
       | |<--fixed
       | V 
       | "MARCO-B_NAC"
       | -------------
       |
       |<--fixed
       V
       "MARCO-B_WAC"
       -------------


   (1)      BFR -- body-fixed rotating frame.


Spacecraft Frame
-------------------------------------------------------------------------------

   The MARCO-B spacecraft frame is defined as follows:

      *  +Z axis is along the normal to the TCM engine/MGA side of 
         of the s/c structure.

      *  +Y axis is along the normal to the HGA side of the s/c
         structure.

      *  +X axis completes the right-handed frame.

   This diagram illustrates the spacecraft frame:

                                                  | HGA
                                                  |
              HGA                                 ~
             feed                                 ~
                  \\              +Ysc            |
                   \\            ^                |
                 ----------------|----------------o
            MGA |        SA      |                |
           ===========o========= |                |
            TCM |     +Zsc <-----o+Xsc            |
                 ---------------------------------
                       \  /             \  /
                   UHF  \/               \/        
                       =====================           +Xsc is out 
                                                       of the page
                      

   The spacecraft attitude with respect to an inertial frame is
   provided in C kernels therefore this frame is defined as a CK-based
   frame.
   
   \begindata

      FRAME_MARCO-B_SPACECRAFT        = -66000
      FRAME_-66000_NAME               = 'MARCO-B_SPACECRAFT'
      FRAME_-66000_CLASS              = 3
      FRAME_-66000_CLASS_ID           = -66000
      FRAME_-66000_CENTER             = -66
      CK_-66000_SCLK                  = -66
      CK_-66000_SPK                   = -66

   \begintext


Structure Frames and FOVs
-------------------------------------------------------------------------------

   The TCM engine frame is defined as follows:

      *  +Z axis is along engine thrust vector.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The TCM frame is rotated by 180 degrees about X from the s/c
         frame.

   The radiator frame is defined as follows:

      *  +Z axis is along the radiator outward normal.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The radiator frame is rotated by +90 degrees about X from the
         s/c frame.

   The star tracker frame is defined as follows:

      *  +Z axis is along the star tracker boresight.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The star tracker frame is rotated by -170 degrees about X from
         the s/c frame.

   The solar array frame is defined as follows:

      *  +Z axis is along the normal to the array's active cell side.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The solar array frame is rotated by -90 degrees
         about X from the s/c frame.

   This diagram illustrates the structure frames:

                                                  | HGA
                                                  |
                                                  ~
                       +Zsa                       ~
                  \\  ^           +Ysc            |
                   \\ |          ^                |      
                 -----|----------|----------------o      +Zst  
          SA    |     |   +Ysa   |                |    .>     
           ===========o-----> == |                | .-'  10 deg
               o----->     <-----o   +Yrad        o'  ----
               |  +Ztcm  +Zsc --------- <-----o--- \
               |       \  /                   |     \
               |   UHF  \/               \/   |      \
               v       =====================  |       v +Yst
         +Ytcm                                v
                                         +Zrad         

                                                 All +X axes are out 
                                                    of the page

   All structure frames are defined as fixed-offset frames. The angles
   provided in the frame definitions below are the nominal values.

   Frame definition keywords:

   \begindata

      FRAME_MARCO-B_TCM_ENGINE        = -66110
      FRAME_-66110_NAME               = 'MARCO-B_TCM_ENGINE'
      FRAME_-66110_CLASS              = 4
      FRAME_-66110_CLASS_ID           = -66110
      FRAME_-66110_CENTER             = -66
      TKFRAME_-66110_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66110_SPEC             = 'ANGLES'
      TKFRAME_-66110_UNITS            = 'DEGREES'
      TKFRAME_-66110_AXES             = ( 3,     1,   3   )
      TKFRAME_-66110_ANGLES           = ( 0.0, 180.0, 0.0 )

      FRAME_MARCO-B_RADIATOR          = -66120
      FRAME_-66120_NAME               = 'MARCO-B_RADIATOR'
      FRAME_-66120_CLASS              = 4
      FRAME_-66120_CLASS_ID           = -66120
      FRAME_-66120_CENTER             = -66
      TKFRAME_-66120_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66120_SPEC             = 'ANGLES'
      TKFRAME_-66120_UNITS            = 'DEGREES'
      TKFRAME_-66120_AXES             = ( 3,     1,   3   )
      TKFRAME_-66120_ANGLES           = ( 0.0, -90.0, 0.0 )

      FRAME_MARCO-B_STAR_TRACKER      = -66130
      FRAME_-66130_NAME               = 'MARCO-B_STAR_TRACKER'
      FRAME_-66130_CLASS              = 4
      FRAME_-66130_CLASS_ID           = -66130
      FRAME_-66130_CENTER             = -66
      TKFRAME_-66130_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66130_SPEC             = 'ANGLES'
      TKFRAME_-66130_UNITS            = 'DEGREES'
      TKFRAME_-66130_AXES             = ( 3,     1,   3   )
      TKFRAME_-66130_ANGLES           = ( 0.0, 170.0, 0.0 )

      FRAME_MARCO-B_SA                = -66140
      FRAME_-66140_NAME               = 'MARCO-B_SA'
      FRAME_-66140_CLASS              = 4
      FRAME_-66140_CLASS_ID           = -66140
      FRAME_-66140_CENTER             = -66
      TKFRAME_-66140_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66140_SPEC             = 'ANGLES'
      TKFRAME_-66140_UNITS            = 'DEGREES'
      TKFRAME_-66140_AXES             = ( 3,     1,   3   )
      TKFRAME_-66140_ANGLES           = ( 0.0,  90.0, 0.0 )

   \begintext

   The structure FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -66110  CIRCLE       2.0     MARCO-B_TCM_ENGINE     +Z      n/a
      -66120  CIRCLE       2.0     MARCO-B_RADIATOR       +Z      n/a
      -66130  RECTANGLE 12.0x10.0  MARCO-B_STAR_TRACKER   +Z      +X
      -66140  CIRCLE       2.0     MARCO-B_SA             +Z      n/a

   Note: because the TCM engine, radiator, and solar FOVs are needed
   only to support testing of the corresponding frames, their sizes and
   shapes were chosen arbitrarily.   

   FOV definition keywords:

   \begindata

      INS-66110_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66110_FOV_SHAPE             = 'CIRCLE'
      INS-66110_FOV_FRAME             = 'MARCO-B_TCM_ENGINE'
      INS-66110_BORESIGHT             = ( 0, 0, 1 )
      INS-66110_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66110_FOV_REF_ANGLE         = ( 1.0 )
      INS-66110_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66120_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66120_FOV_SHAPE             = 'CIRCLE'
      INS-66120_FOV_FRAME             = 'MARCO-B_RADIATOR'
      INS-66120_BORESIGHT             = ( 0, 0, 1 )
      INS-66120_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66120_FOV_REF_ANGLE         = ( 1.0 )
      INS-66120_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66130_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66130_FOV_SHAPE             = 'RECTANGLE'
      INS-66130_FOV_FRAME             = 'MARCO-B_STAR_TRACKER'
      INS-66130_BORESIGHT             = ( 0, 0, 1 )
      INS-66130_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66130_FOV_REF_ANGLE         = ( 6.0 )
      INS-66130_FOV_CROSS_ANGLE       = ( 5.0 )
      INS-66130_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66140_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66140_FOV_SHAPE             = 'CIRCLE'
      INS-66140_FOV_FRAME             = 'MARCO-B_SA'
      INS-66140_BORESIGHT             = ( 0, 0, 1 )
      INS-66140_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66140_FOV_REF_ANGLE         = ( 1.0 )
      INS-66140_FOV_ANGLE_UNITS       = ( 'DEGREES' )

   \begintext



Antenna Frames and FOVs
-------------------------------------------------------------------------------

   The HGA frame is defined as follows:

      *  +Z axis is along the antenna boresight.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The HGA frame is rotated by -22.7 degrees about X from the s/c
         frame.

   The MGA frame is defined as follows:

      *  +Z axis is along the antenna boresight.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The MGA frame is rotated by -22.7 degrees about X from the s/c
         frame.

   The LGA tracker frame is defined as follows:

      *  +Z axis is along the antenna boresight.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The LGA frame is rotated by 180 degrees about X from the s/c
         frame.

   The UHF frame is defined as follows:

      *  +Z axis is along the antenna boresight.

      *  +X axis is along the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The UHF frame is rotated by +90 degrees about X from the s/c
         frame.

   This diagram illustrates the antenna frames:

                                                      ^ +Yhga
                                       +Zhga   HGA   /
                                            <.    | /
                                    22.7 deg  `-. |/
                      +Ymga                ----  `o
                    ^                             ~
    +Zmga          /              +Ysc            |
          <.      / \            ^                |
   22.7 deg `-.  /---------------|----------------o
        ----   `o            SA  |                |      +Zlga
           ===========o========= |                o-----> 
                |     +Zsc <-----o                |
                 ---------------------------------|
                       \  /             \  /      |
                   UHF  \/               \/       v +Ylga
                       === <-----o =========
                      +Yuhf      |                 
                                 |                 All +X axes are out 
                                 |                     of the page
                                 v +Zuhf

   All antenna frames are defined as fixed-offset frames. The angles
   provided in the frame definitions below are the nominal values.

   Frame definition keywords:

   \begindata

      FRAME_MARCO-B_HGA               = -66210
      FRAME_-66210_NAME               = 'MARCO-B_HGA'
      FRAME_-66210_CLASS              = 4
      FRAME_-66210_CLASS_ID           = -66210
      FRAME_-66210_CENTER             = -66
      TKFRAME_-66210_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66210_SPEC             = 'ANGLES'
      TKFRAME_-66210_UNITS            = 'DEGREES'
      TKFRAME_-66210_AXES             = ( 3,     1,   3   )
      TKFRAME_-66210_ANGLES           = ( 0.0,  22.7, 0.0 )

      FRAME_MARCO-B_MGA               = -66220
      FRAME_-66220_NAME               = 'MARCO-B_MGA'
      FRAME_-66220_CLASS              = 4
      FRAME_-66220_CLASS_ID           = -66220
      FRAME_-66220_CENTER             = -66
      TKFRAME_-66220_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66220_SPEC             = 'ANGLES'
      TKFRAME_-66220_UNITS            = 'DEGREES'
      TKFRAME_-66220_AXES             = ( 3,     1,   3   )
      TKFRAME_-66220_ANGLES           = ( 0.0,  22.7, 0.0 )

      FRAME_MARCO-B_LGA                = -66230
      FRAME_-66230_NAME               = 'MARCO-B_LGA'
      FRAME_-66230_CLASS              = 4
      FRAME_-66230_CLASS_ID           = -66230
      FRAME_-66230_CENTER             = -66
      TKFRAME_-66230_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66230_SPEC             = 'ANGLES'
      TKFRAME_-66230_UNITS            = 'DEGREES'
      TKFRAME_-66230_AXES             = ( 3,     1,   3   )
      TKFRAME_-66230_ANGLES           = ( 0.0, 180.0, 0.0 )

      FRAME_MARCO-B_UHF               = -66240
      FRAME_-66240_NAME               = 'MARCO-B_UHF'
      FRAME_-66240_CLASS              = 4
      FRAME_-66240_CLASS_ID           = -66240
      FRAME_-66240_CENTER             = -66
      TKFRAME_-66240_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66240_SPEC             = 'ANGLES'
      TKFRAME_-66240_UNITS            = 'DEGREES'
      TKFRAME_-66240_AXES             = ( 3,     1,   3   )
      TKFRAME_-66240_ANGLES           = ( 0.0, -90.0, 0.0 )

   \begintext

   The antenna FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -66210  CIRCLE      10.0     MARCO-B_HGA            +Z      n/a
      -66220  CIRCLE      90.0     MARCO-B_MGA            +Z      n/a
      -66230  CIRCLE     178.0     MARCO-B_LGA            +Z      n/a
      -66240  CIRCLE     178.0     MARCO-B_UHF            +Z      n/a

   Note: because no information about the antenna FOV sizes was
   available, the sizes were chosen arbitrarily.

   FOV definition keywords:

   \begindata

      INS-66210_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66210_FOV_SHAPE             = 'CIRCLE'
      INS-66210_FOV_FRAME             = 'MARCO-B_HGA'
      INS-66210_BORESIGHT             = ( 0, 0, 1 )
      INS-66210_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66210_FOV_REF_ANGLE         = ( 5.0 )
      INS-66210_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66220_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66220_FOV_SHAPE             = 'CIRCLE'
      INS-66220_FOV_FRAME             = 'MARCO-B_MGA'
      INS-66220_BORESIGHT             = ( 0, 0, 1 )
      INS-66220_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66220_FOV_REF_ANGLE         = ( 45.0 )
      INS-66220_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66230_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66230_FOV_SHAPE             = 'CIRCLE'
      INS-66230_FOV_FRAME             = 'MARCO-B_LGA'
      INS-66230_BORESIGHT             = ( 0, 0, 1 )
      INS-66230_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66230_FOV_REF_ANGLE         = ( 89.0 )
      INS-66230_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66240_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66240_FOV_SHAPE             = 'CIRCLE'
      INS-66240_FOV_FRAME             = 'MARCO-B_UHF'
      INS-66240_BORESIGHT             = ( 0, 0, 1 )
      INS-66240_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66240_FOV_REF_ANGLE         = ( 89.0 )
      INS-66240_FOV_ANGLE_UNITS       = ( 'DEGREES' )

   \begintext


Instrument Frames and FOVs
-------------------------------------------------------------------------------

   The NAC frame is defined as follows:

      *  +Z axis is along the camera boresight.

      *  +X axis is along the CCD lines (TBD) and is nominally in the
         direction of the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The NAC frame is rotated by +90 degrees about X from the s/c
         frame.


   The WAC frame is defined as follows:

      *  +Z axis is along the camera boresight.

      *  +X axis is along the CCD lines (TBD) and is nominally in the
         direction of the spacecraft +X axis.

      *  +Y axis completes the right-handed frame.

      *  The WAC frame is rotated by -62 degrees about X from the s/c
         frame.

   This diagram illustrates the camera frames:

                                      +Zwac       | HGA
                                            ^     |
                                             \    ~
                                          62  \   ~  .> +Ywac
                  \\              +Ysc   deg   \  .-'
                   \\            ^              o' 
                 ----------------|----------------o
          SA    |                |                |
           ===========o========= |                |
                |     +Zsc <-----o+Xsc  +Ynac     |
                 ------------------------ <-----o-
                       \  /             \       |
                   UHF  \/               \/     |  
                       =====================    |    All +X axes are out
                                                v      of the page.
                                           Znac
 

   All instrument frames are defined as fixed-offset frames. The angles
   provided in the frame definitions below are the nominal values.

   Frame definition keywords:

   \begindata

      FRAME_MARCO-B_NAC               = -66310
      FRAME_-66310_NAME               = 'MARCO-B_NAC'
      FRAME_-66310_CLASS              = 4
      FRAME_-66310_CLASS_ID           = -66310
      FRAME_-66310_CENTER             = -66
      TKFRAME_-66310_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66310_SPEC             = 'ANGLES'
      TKFRAME_-66310_UNITS            = 'DEGREES'
      TKFRAME_-66310_AXES             = ( 3,     1,   3   )
      TKFRAME_-66310_ANGLES           = ( 0.0, -90.0, 0.0 )

      FRAME_MARCO-B_WAC               = -66320
      FRAME_-66320_NAME               = 'MARCO-B_WAC'
      FRAME_-66320_CLASS              = 4
      FRAME_-66320_CLASS_ID           = -66320
      FRAME_-66320_CENTER             = -66
      TKFRAME_-66320_RELATIVE         = 'MARCO-B_SPACECRAFT'
      TKFRAME_-66320_SPEC             = 'ANGLES'
      TKFRAME_-66320_UNITS            = 'DEGREES'
      TKFRAME_-66320_AXES             = ( 3, 1, 3 )
      TKFRAME_-66320_ANGLES           = ( 0.0,  62.0, 0.0 )

   \begintext


   The instrument FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -66310  RECTANGLE  6.8x6.8   MARCO-B_NAC            +Z    +X
      -66320  RECTANGLE  154x154   MARCO-B_WAC            +Z    +X

   FOV definition keywords:

   \begindata

      INS-66310_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66310_FOV_SHAPE             = 'RECTANGLE'
      INS-66310_FOV_FRAME             = 'MARCO-B_NAC'
      INS-66310_BORESIGHT             = ( 0, 0, 1 )
      INS-66310_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66310_FOV_REF_ANGLE         = ( 3.4 )
      INS-66310_FOV_CROSS_ANGLE       = ( 3.4 )
      INS-66310_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-66320_FOV_CLASS_SPEC        = 'ANGLES'
      INS-66320_FOV_SHAPE             = 'RECTANGLE'
      INS-66320_FOV_FRAME             = 'MARCO-B_WAC'
      INS-66320_BORESIGHT             = ( 0, 0, 1 )
      INS-66320_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-66320_FOV_REF_ANGLE         = ( 77.0 )
      INS-66320_FOV_CROSS_ANGLE       = ( 77.0 )
      INS-66320_FOV_ANGLE_UNITS       = ( 'DEGREES' )

   \begintext


MARCO-B NAIF ID Codes -- Definition Section
-------------------------------------------------------------------------------

   This section contains name to NAIF ID mappings for MARCO-B.

   \begindata

      NAIF_BODY_NAME                 += ( 'MARS CUBE ONE B' )
      NAIF_BODY_CODE                 += ( -66 )

      NAIF_BODY_NAME                 += ( 'EVE' )
      NAIF_BODY_CODE                 += ( -66 )

      NAIF_BODY_NAME                 += ( 'MARCO-B' )
      NAIF_BODY_CODE                 += ( -66 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_SPACECRAFT' )
      NAIF_BODY_CODE                 += ( -66000 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_TCM_ENGINE' )
      NAIF_BODY_CODE                 += ( -66110 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_RADIATOR' )
      NAIF_BODY_CODE                 += ( -66120 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_STAR_TRACKER' )
      NAIF_BODY_CODE                 += ( -66130 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_SA' )
      NAIF_BODY_CODE                 += ( -66140 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_HGA' )
      NAIF_BODY_CODE                 += ( -66210 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_MGA' )
      NAIF_BODY_CODE                 += ( -66220 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_LGA' )
      NAIF_BODY_CODE                 += ( -66230 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_UHF' )
      NAIF_BODY_CODE                 += ( -66240 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_NAC' )
      NAIF_BODY_CODE                 += ( -66310 )

      NAIF_BODY_NAME                 += ( 'MARCO-B_WAC' )
      NAIF_BODY_CODE                 += ( -66320 )

   \begintext

End of FK file.
