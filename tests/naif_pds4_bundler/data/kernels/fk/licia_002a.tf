KPL/FK

LICIA Frames Kernel
===========================================================================

   This frame kernel contains the complete set of frame definitions
   for the LICIACube (LICIA) spacecraft, its structures and instruments.
   This kernel also contains NAIF ID/name mapping for the LICIA instruments.


Version and Date
------------------------------------------------------------------------

   Version 002 -- September 20, 2021 -- Marc Costa Sitja, NAIF/JPL

      Updated LICIA ID from -136 to -210, including all the IDs in
      the LICIA namespace.

      Added several sections, frame definitions and s/c diagrams.

   Version 001 -- July 17, 2021 -- Hari.Nair@jhuapl.edu

      Rename version.

      Includes the following updates by Hari Nair from previous versions:

         Version 0.4 -- Nov. 16, 2020: Revert frame names for LUKE and LEIA
         to be consistent with new instrument kernels.

         Version 0.3 -- Nov. 12, 2020: Fix frame names for LUKE and LEIA.

         Version 0.2 -- Sep. 17, 2020: Change LICIA frame names to be
         consistent with instrument kernels.

         Version 0.1 -- Mar. 26, 2020: Initial release.


References
------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``C-Kernel Required Reading''


Contact Information
------------------------------------------------------------------------

   Hari Nair, JHU/APL, Hari.Nair@jhuapl.edu
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
            LICIA                    -210     (LICIACUBE, LICIA CUBE)

            LICIA_SPACECRAFT         -210000

   PL1 and PL2 names/IDs:
   ----------------------
            LICIA_PL1                -210100
            LICIA_PL2                -210200


LICIA Frames
------------------------------------------------------------------------

   The following LICIA frames are defined in this kernel file:

           Name                    Relative to           Type        NAIF ID
      ======================    ===================  ============    =======

   LICIA Spacecraft and Spacecraft Structures frames:
   --------------------------------------------------
      LICIA_SPACECRAFT           J2000                    CK         -210000

   LICIA frames:
   --------------------------------------------------
      LICIA_PL1                  LICIA_SPACECRAFT         FIXED      -210101
      LICIA_PL2                  LICIA_SPACECRAFT         FIXED      -210102


LICIA Frames Hierarchy
------------------------------------------------------------------------

   The diagram below shows the LICIA frames hierarchy.

                               "J2000" INERTIAL
         +-------------------------------------------------------+
         |               |          |           |                |
         |<-pck          |<-ck      |<-ck       |<-pck           |<-pck
         V               |          |           V                V
    "EARTH_FIXED"        |          |    "IAU_DIMORPHOS"   "IAU_DIDYMOS"
    -------------        |          |    ---------------   -------------
                         |          |           |                |
                         |          |           |<-fixed         |<-fixed
                         |          |           |                |
                         V          |           V                V
                 "DART_SPACECRAFT"  |   "DIMORPHOS_FIXED"  "DIDYMOS_FIXED"
                 -----------------  |   -----------------  ---------------
                              |     |
                       fixed->|     |
                              |     |
                              V     V
                          "LICIA_SPACECRAFT"
             +-----------------------------------------------+
             |                                               |
             |<-fixed                                        |<-fixed
             |                                               |
             V                                               V
         "LICIA_PL1"                                     "LICIA_PL2"
         -----------                                     -----------


Spacecraft Frame
------------------------------------------------------------------------

   Since the S/C bus attitude with respect to an inertial frame is provided
   by a C-kernel (see [1] for more information), this frame is defined as
   a CK-based frame.

   \begindata

      FRAME_LICIA_SPACECRAFT   = -210000
      FRAME_-210000_NAME       = 'LICIA_SPACECRAFT'
      FRAME_-210000_CLASS      = 3
      FRAME_-210000_CLASS_ID   = -210000
      FRAME_-210000_CENTER     = -210
      CK_-210000_SCLK          = -210
      CK_-210000_SPK           = -210

   \begintext


LICIA Camera Frames
------------------------------------------------------------------------

   Assume for now it's the same as the spacecraft frame.

   \begindata

      FRAME_LICIA_PL1           = -210101
      FRAME_-210101_NAME        = 'LICIA_PL1'
      FRAME_-210101_CLASS       = 4
      FRAME_-210101_CLASS_ID    = -210101
      FRAME_-210101_CENTER      = -210
      TKFRAME_-210101_SPEC      = 'MATRIX'
      TKFRAME_-210101_RELATIVE  = 'LICIA_SPACECRAFT'
      TKFRAME_-210101_MATRIX    = ( 1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0,
                                    0.0, 0.0, 1.0 )

      FRAME_LICIA_PL2           = -210102
      FRAME_-210102_NAME        = 'LICIA_PL2'
      FRAME_-210102_CLASS       = 4
      FRAME_-210102_CLASS_ID    = -210102
      FRAME_-210102_CENTER      = -210
      TKFRAME_-210102_SPEC      = 'MATRIX'
      TKFRAME_-210102_RELATIVE  = 'LICIA_SPACECRAFT'
      TKFRAME_-210102_MATRIX    = ( 1.0, 0.0, 0.0,
                                    0.0, 1.0, 0.0,
                                    0.0, 0.0, 1.0 )

   \begintext


LICIA NAIF ID Codes -- Definitions
=====================================================================

   This section contains name to NAIF ID mappings for the LICIA
   spacecraft and its structures.

   Once the contents of this file are loaded into the KERNEL POOL, these
   mappings become available within SPICE, making it possible to use
   names instead of ID code in high level SPICE routine calls.

   \begindata

      NAIF_BODY_NAME   += ( 'LICIA CUBE' )
      NAIF_BODY_CODE   += ( -210         )

      NAIF_BODY_NAME   += ( 'LICIA' )
      NAIF_BODY_CODE   += ( -210    )

      NAIF_BODY_NAME   += ( 'LICIACUBE' )
      NAIF_BODY_CODE   += ( -210        )

      NAIF_BODY_NAME   += ( 'LICIA_SPACECRAFT' )
      NAIF_BODY_CODE   += ( -210000            )


      NAIF_BODY_NAME   += ( 'LICIA_PL1' )
      NAIF_BODY_CODE   += ( -210100     )

      NAIF_BODY_NAME   += ( 'LICIA_PL2' )
      NAIF_BODY_CODE   += ( -210200     )

   \begintext


End of FK file.
