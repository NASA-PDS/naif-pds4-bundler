KPL/FK


MARCO-A Frame Definitions Kernel
===============================================================================

   This frame kernel contains definitions for the MARCO-A spacecraft,
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


MARCO-A NAIF ID Codes
-------------------------------------------------------------------------------

   The following names and NAIF ID codes are assigned to the MARCO-A
   spacecraft and its structures (the keywords implementing these
   name-ID mappings are located in the section "MARCO-A NAIF ID Codes
   -- Definition Section" at the end of this file):

   MARCO-A spacecraft:
   -------------------
      MARCO-A                    -65      (MARS CUBE ONE A, WALL-E)
      MARCO-A_SPACECRAFT         -65000

   MARCO-A structures:
   -------------------
      MARCO-A_TCM_ENGINE         -65110
      MARCO-A_RADIATOR           -65120
      MARCO-A_STAR_TRACKER       -65130
      MARCO-A_SA                 -65140

   MARCO-A antennas:
   -----------------
      MARCO-A_HGA                -65210
      MARCO-A_MGA                -65220
      MARCO-A_LGA                -65230
      MARCO-A_UHF                -65240

   MARCO-A instruments:
   --------------------
      MARCO-A_NAC                -65310
      MARCO-A_WAC                -65320


MARCO-A Frames
-------------------------------------------------------------------------------

   The following MARCO-A frames are defined in this kernel file:

      Name                       Relative to                 Type   Frame ID
      ========================== ========================== ======= ========

   Spacecraft frames (-6500x):
   ---------------------------
      MARCO-A_SPACECRAFT         J2000                      CK      -65000

   Structure frames (-651xx):
   --------------------------
      MARCO-A_TCM_ENGINE         MARCO-A_SPACECRAFT         FIXED   -65110
      MARCO-A_RADIATOR           MARCO-A_SPACECRAFT         FIXED   -65120
      MARCO-A_STAR_TRACKER       MARCO-A_SPACECRAFT         FIXED   -65130
      MARCO-A_SA                 MARCO-A_SPACECRAFT         FIXED   -65140

   Antenna frames (-652xx):
   ------------------------
      MARCO-A_HGA                MARCO-A_SPACECRAFT         FIXED   -65210
      MARCO-A_MGA                MARCO-A_SPACECRAFT         FIXED   -65220
      MARCO-A_LGA                MARCO-A_SPACECRAFT         FIXED   -65230
      MARCO-A_UHF                MARCO-A_SPACECRAFT         FIXED   -65240

   Instrument frames (-656xx):
   ---------------------------
      MARCO-A_NAC                MARCO-A_SPACECRAFT         FIXED   -65310
      MARCO-A_WAC                MARCO-A_SPACECRAFT         FIXED   -65320

   The frame descriptions and definitions are provided in the sections
   below.


MARCO-A Frame Hierarchy
-------------------------------------------------------------------------------

   The diagram below shows the MARCO-A frames hierarchy:


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
                            "MARCO-A_SPACECRAFT"
       +-------------------------------------------------------------+
       | | | | | |                                             | | | |      
       | | | | | |<--fixed                            fixed--> | | | |      
       | | | | | V                                             V | | |      
       | | | | | "MARCO-A_HGA"              "MARCO-A_TCM_ENGINE" | | |      
       | | | | | -------------              -------------------- | | |      
       | | | | |                                                 | | |      
       | | | | |<--fixed                                fixed--> | | |      
       | | | | V                                                 V | |      
       | | | | "MARCO-A_MGA"                    "MARCO-A_RADIATOR" | |      
       | | | | -------------                    ------------------ | |      
       | | | |                                                     | |      
       | | | |<--fixed                                    fixed--> | |      
       | | | V                                                     V |      
       | | | "MARCO-A_LGA"                    "MARCO-A_STAR_TRACKER" |      
       | | | -------------                    ---------------------- |      
       | | |                                                         |      
       | | |<--fixed                                        fixed--> |      
       | | V                                                         V      
       | | "MARCO-A_UHF"                                  "MARCO-A_SA"      
       | | -------------                                  ------------
       | |
       | |<--fixed
       | V 
       | "MARCO-A_NAC"
       | -------------
       |
       |<--fixed
       V
       "MARCO-A_WAC"
       -------------


   (1)      BFR -- body-fixed rotating frame.


Spacecraft Frame
-------------------------------------------------------------------------------

   The MARCO-A spacecraft frame is defined as follows:

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

      FRAME_MARCO-A_SPACECRAFT        = -65000
      FRAME_-65000_NAME               = 'MARCO-A_SPACECRAFT'
      FRAME_-65000_CLASS              = 3
      FRAME_-65000_CLASS_ID           = -65000
      FRAME_-65000_CENTER             = -65
      CK_-65000_SCLK                  = -65
      CK_-65000_SPK                   = -65

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

      FRAME_MARCO-A_TCM_ENGINE        = -65110
      FRAME_-65110_NAME               = 'MARCO-A_TCM_ENGINE'
      FRAME_-65110_CLASS              = 4
      FRAME_-65110_CLASS_ID           = -65110
      FRAME_-65110_CENTER             = -65
      TKFRAME_-65110_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65110_SPEC             = 'ANGLES'
      TKFRAME_-65110_UNITS            = 'DEGREES'
      TKFRAME_-65110_AXES             = ( 3,     1,   3   )
      TKFRAME_-65110_ANGLES           = ( 0.0, 180.0, 0.0 )

      FRAME_MARCO-A_RADIATOR          = -65120
      FRAME_-65120_NAME               = 'MARCO-A_RADIATOR'
      FRAME_-65120_CLASS              = 4
      FRAME_-65120_CLASS_ID           = -65120
      FRAME_-65120_CENTER             = -65
      TKFRAME_-65120_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65120_SPEC             = 'ANGLES'
      TKFRAME_-65120_UNITS            = 'DEGREES'
      TKFRAME_-65120_AXES             = ( 3,     1,   3   )
      TKFRAME_-65120_ANGLES           = ( 0.0, -90.0, 0.0 )

      FRAME_MARCO-A_STAR_TRACKER      = -65130
      FRAME_-65130_NAME               = 'MARCO-A_STAR_TRACKER'
      FRAME_-65130_CLASS              = 4
      FRAME_-65130_CLASS_ID           = -65130
      FRAME_-65130_CENTER             = -65
      TKFRAME_-65130_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65130_SPEC             = 'ANGLES'
      TKFRAME_-65130_UNITS            = 'DEGREES'
      TKFRAME_-65130_AXES             = ( 3,     1,   3   )
      TKFRAME_-65130_ANGLES           = ( 0.0, 170.0, 0.0 )

      FRAME_MARCO-A_SA                = -65140
      FRAME_-65140_NAME               = 'MARCO-A_SA'
      FRAME_-65140_CLASS              = 4
      FRAME_-65140_CLASS_ID           = -65140
      FRAME_-65140_CENTER             = -65
      TKFRAME_-65140_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65140_SPEC             = 'ANGLES'
      TKFRAME_-65140_UNITS            = 'DEGREES'
      TKFRAME_-65140_AXES             = ( 3,     1,   3   )
      TKFRAME_-65140_ANGLES           = ( 0.0,  90.0, 0.0 )

   \begintext

   The structure FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -65110  CIRCLE       2.0     MARCO-A_TCM_ENGINE     +Z      n/a
      -65120  CIRCLE       2.0     MARCO-A_RADIATOR       +Z      n/a
      -65130  RECTANGLE 12.0x10.0  MARCO-A_STAR_TRACKER   +Z      +X
      -65140  CIRCLE       2.0     MARCO-A_SA             +Z      n/a

   Note: because the TCM engine, radiator, and solar FOVs are needed
   only to support testing of the corresponding frames, their sizes and
   shapes were chosen arbitrarily.   

   FOV definition keywords:

   \begindata

      INS-65110_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65110_FOV_SHAPE             = 'CIRCLE'
      INS-65110_FOV_FRAME             = 'MARCO-A_TCM_ENGINE'
      INS-65110_BORESIGHT             = ( 0, 0, 1 )
      INS-65110_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65110_FOV_REF_ANGLE         = ( 1.0 )
      INS-65110_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65120_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65120_FOV_SHAPE             = 'CIRCLE'
      INS-65120_FOV_FRAME             = 'MARCO-A_RADIATOR'
      INS-65120_BORESIGHT             = ( 0, 0, 1 )
      INS-65120_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65120_FOV_REF_ANGLE         = ( 1.0 )
      INS-65120_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65130_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65130_FOV_SHAPE             = 'RECTANGLE'
      INS-65130_FOV_FRAME             = 'MARCO-A_STAR_TRACKER'
      INS-65130_BORESIGHT             = ( 0, 0, 1 )
      INS-65130_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65130_FOV_REF_ANGLE         = ( 6.0 )
      INS-65130_FOV_CROSS_ANGLE       = ( 5.0 )
      INS-65130_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65140_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65140_FOV_SHAPE             = 'CIRCLE'
      INS-65140_FOV_FRAME             = 'MARCO-A_SA'
      INS-65140_BORESIGHT             = ( 0, 0, 1 )
      INS-65140_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65140_FOV_REF_ANGLE         = ( 1.0 )
      INS-65140_FOV_ANGLE_UNITS       = ( 'DEGREES' )

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

      FRAME_MARCO-A_HGA               = -65210
      FRAME_-65210_NAME               = 'MARCO-A_HGA'
      FRAME_-65210_CLASS              = 4
      FRAME_-65210_CLASS_ID           = -65210
      FRAME_-65210_CENTER             = -65
      TKFRAME_-65210_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65210_SPEC             = 'ANGLES'
      TKFRAME_-65210_UNITS            = 'DEGREES'
      TKFRAME_-65210_AXES             = ( 3,     1,   3   )
      TKFRAME_-65210_ANGLES           = ( 0.0,  22.7, 0.0 )

      FRAME_MARCO-A_MGA               = -65220
      FRAME_-65220_NAME               = 'MARCO-A_MGA'
      FRAME_-65220_CLASS              = 4
      FRAME_-65220_CLASS_ID           = -65220
      FRAME_-65220_CENTER             = -65
      TKFRAME_-65220_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65220_SPEC             = 'ANGLES'
      TKFRAME_-65220_UNITS            = 'DEGREES'
      TKFRAME_-65220_AXES             = ( 3,     1,   3   )
      TKFRAME_-65220_ANGLES           = ( 0.0,  22.7, 0.0 )

      FRAME_MARCO-A_LGA                = -65230
      FRAME_-65230_NAME               = 'MARCO-A_LGA'
      FRAME_-65230_CLASS              = 4
      FRAME_-65230_CLASS_ID           = -65230
      FRAME_-65230_CENTER             = -65
      TKFRAME_-65230_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65230_SPEC             = 'ANGLES'
      TKFRAME_-65230_UNITS            = 'DEGREES'
      TKFRAME_-65230_AXES             = ( 3,     1,   3   )
      TKFRAME_-65230_ANGLES           = ( 0.0, 180.0, 0.0 )

      FRAME_MARCO-A_UHF               = -65240
      FRAME_-65240_NAME               = 'MARCO-A_UHF'
      FRAME_-65240_CLASS              = 4
      FRAME_-65240_CLASS_ID           = -65240
      FRAME_-65240_CENTER             = -65
      TKFRAME_-65240_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65240_SPEC             = 'ANGLES'
      TKFRAME_-65240_UNITS            = 'DEGREES'
      TKFRAME_-65240_AXES             = ( 3,     1,   3   )
      TKFRAME_-65240_ANGLES           = ( 0.0, -90.0, 0.0 )

   \begintext

   The antenna FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -65210  CIRCLE      10.0     MARCO-A_HGA            +Z      n/a
      -65220  CIRCLE      90.0     MARCO-A_MGA            +Z      n/a
      -65230  CIRCLE     178.0     MARCO-A_LGA            +Z      n/a
      -65240  CIRCLE     178.0     MARCO-A_UHF            +Z      n/a

   Note: because no information about the antenna FOV sizes was
   available, the sizes were chosen arbitrarily.

   FOV definition keywords:

   \begindata

      INS-65210_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65210_FOV_SHAPE             = 'CIRCLE'
      INS-65210_FOV_FRAME             = 'MARCO-A_HGA'
      INS-65210_BORESIGHT             = ( 0, 0, 1 )
      INS-65210_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65210_FOV_REF_ANGLE         = ( 5.0 )
      INS-65210_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65220_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65220_FOV_SHAPE             = 'CIRCLE'
      INS-65220_FOV_FRAME             = 'MARCO-A_MGA'
      INS-65220_BORESIGHT             = ( 0, 0, 1 )
      INS-65220_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65220_FOV_REF_ANGLE         = ( 45.0 )
      INS-65220_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65230_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65230_FOV_SHAPE             = 'CIRCLE'
      INS-65230_FOV_FRAME             = 'MARCO-A_LGA'
      INS-65230_BORESIGHT             = ( 0, 0, 1 )
      INS-65230_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65230_FOV_REF_ANGLE         = ( 89.0 )
      INS-65230_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65240_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65240_FOV_SHAPE             = 'CIRCLE'
      INS-65240_FOV_FRAME             = 'MARCO-A_UHF'
      INS-65240_BORESIGHT             = ( 0, 0, 1 )
      INS-65240_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65240_FOV_REF_ANGLE         = ( 89.0 )
      INS-65240_FOV_ANGLE_UNITS       = ( 'DEGREES' )

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

      FRAME_MARCO-A_NAC               = -65310
      FRAME_-65310_NAME               = 'MARCO-A_NAC'
      FRAME_-65310_CLASS              = 4
      FRAME_-65310_CLASS_ID           = -65310
      FRAME_-65310_CENTER             = -65
      TKFRAME_-65310_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65310_SPEC             = 'ANGLES'
      TKFRAME_-65310_UNITS            = 'DEGREES'
      TKFRAME_-65310_AXES             = ( 3,     1,   3   )
      TKFRAME_-65310_ANGLES           = ( 0.0, -90.0, 0.0 )

      FRAME_MARCO-A_WAC               = -65320
      FRAME_-65320_NAME               = 'MARCO-A_WAC'
      FRAME_-65320_CLASS              = 4
      FRAME_-65320_CLASS_ID           = -65320
      FRAME_-65320_CENTER             = -65
      TKFRAME_-65320_RELATIVE         = 'MARCO-A_SPACECRAFT'
      TKFRAME_-65320_SPEC             = 'ANGLES'
      TKFRAME_-65320_UNITS            = 'DEGREES'
      TKFRAME_-65320_AXES             = ( 3, 1, 3 )
      TKFRAME_-65320_ANGLES           = ( 0.0,  62.0, 0.0 )

   \begintext


   The instrument FOVs are defined as follows:

      Instr.  Shape     Size,deg        Frame           Bsight Cross-axis  
      ------- --------- ---------- -------------------- ------ ----------
      -65310  RECTANGLE  6.8x6.8   MARCO-A_NAC            +Z    +X
      -65320  RECTANGLE  154x154   MARCO-A_WAC            +Z    +X

   FOV definition keywords:

   \begindata

      INS-65310_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65310_FOV_SHAPE             = 'RECTANGLE'
      INS-65310_FOV_FRAME             = 'MARCO-A_NAC'
      INS-65310_BORESIGHT             = ( 0, 0, 1 )
      INS-65310_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65310_FOV_REF_ANGLE         = ( 3.4 )
      INS-65310_FOV_CROSS_ANGLE       = ( 3.4 )
      INS-65310_FOV_ANGLE_UNITS       = ( 'DEGREES' )

      INS-65320_FOV_CLASS_SPEC        = 'ANGLES'
      INS-65320_FOV_SHAPE             = 'RECTANGLE'
      INS-65320_FOV_FRAME             = 'MARCO-A_WAC'
      INS-65320_BORESIGHT             = ( 0, 0, 1 )
      INS-65320_FOV_REF_VECTOR        = ( 1, 0, 0 )
      INS-65320_FOV_REF_ANGLE         = ( 77.0 )
      INS-65320_FOV_CROSS_ANGLE       = ( 77.0 )
      INS-65320_FOV_ANGLE_UNITS       = ( 'DEGREES' )

   \begintext


MARCO-A NAIF ID Codes -- Definition Section
-------------------------------------------------------------------------------

   This section contains name to NAIF ID mappings for MARCO-A.

   \begindata

      NAIF_BODY_NAME                 += ( 'MARS CUBE ONE A' )
      NAIF_BODY_CODE                 += ( -65 )

      NAIF_BODY_NAME                 += ( 'WALL-E' )
      NAIF_BODY_CODE                 += ( -65 )

      NAIF_BODY_NAME                 += ( 'MARCO-A' )
      NAIF_BODY_CODE                 += ( -65 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_SPACECRAFT' )
      NAIF_BODY_CODE                 += ( -65000 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_TCM_ENGINE' )
      NAIF_BODY_CODE                 += ( -65110 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_RADIATOR' )
      NAIF_BODY_CODE                 += ( -65120 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_STAR_TRACKER' )
      NAIF_BODY_CODE                 += ( -65130 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_SA' )
      NAIF_BODY_CODE                 += ( -65140 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_HGA' )
      NAIF_BODY_CODE                 += ( -65210 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_MGA' )
      NAIF_BODY_CODE                 += ( -65220 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_LGA' )
      NAIF_BODY_CODE                 += ( -65230 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_UHF' )
      NAIF_BODY_CODE                 += ( -65240 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_NAC' )
      NAIF_BODY_CODE                 += ( -65310 )

      NAIF_BODY_NAME                 += ( 'MARCO-A_WAC' )
      NAIF_BODY_CODE                 += ( -65320 )

   \begintext

End of FK file.
