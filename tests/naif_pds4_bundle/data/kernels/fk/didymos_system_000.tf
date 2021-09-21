KPL/FK

Didymos System Frames Kernel
========================================================================

   This frame kernel contains a complete set of frame definitions for 
   the Didymos system including NAIF ID/name mapping for the the 
   asteroid system and, the name to ID mappings for the DART target body 
   DSK surfaces.


Version and Date
------------------------------------------------------------------------

   Version 000 -- September 1, 2021 - Marc Costa Sitja, NAIF/JPL

      First version. 


References
------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``DS-Kernel Required Reading''


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


Asteroid NAIF ID Codes -- Summary Section
------------------------------------------------------------------------

   The following names and NAIF ID codes are assigned to the Didymos 
   system (the keywords implementing these definitions are located in 
   the section "Didymos System NAIF ID Codes -- Definition Section" 
   later in this file):

   Asteroid Binary System names/IDs*:
            
            DIDYMOS BARYCENTER      20065803
            DIDYMOS                920065803
            DIMORPHOS              120065803
    
   (*) The Minor Planet Designation (MPC) for the Didymos system is 65803.  
       The NAIF ID of the system barycenter is 20065803. The NAIF ID of the 
       primary (Didymos) is 920065803. The NAIF ID of the secondary 
       (Dimorphos) is 120065803.


Asteroid Frames
------------------------------------------------------------------------

   The following Didymos system frames are defined in this kernel file:

           Name                    Relative to           Type        NAIF ID
      ======================    ===================  ============   =========
      IAU_DIDYMOS                 J2000                  PCK            10113 
      DIDYMOS_FIXED               IAU_DIDYMOS            FIXED      920065803
      
      IAU_DIMORPHOS               J2000                  PCK            10114
      DIMORPHOS_FIXED             IAU_DIDYMOS            FIXED      120065803    


Asteroid Body Fixed Frames
------------------------------------------------------------------------

   This section of the file contains the body-fixed frame definition
   for one of the DART mission targets: asteroid Didymos and Dimorphos.


Didymos frames
--------------------------------------

   The asteroid Didymos body-fixed frame -- IAU_DIDYMOS -- is defined
   as follows:

      -  +Z axis is the asteroid rotation axis pointed towards the
         positive pole

      -  +X axis points towards the prime meridian

      -  +Y axis completes the right handed frame

      -  the origin of the frame is at the asteroid center of mass.


   Since the asteroid rotation data is expected to be provided in a text PCK 
   in the form compliant with the IAU rotation model, the IAU_DIDYMOS frame 
   is defined as a PCK based frame. This definition is included in all SPICE 
   Toolkits version N0067 or superior.

   \begindata

      FRAME_IAU_DIDYMOS          =  10113
      FRAME_10113_NAME           = 'IAU_DIDYMOS'
      FRAME_10113_CLASS          =  2
      FRAME_10113_CLASS_ID       =  920065803
      FRAME_10113_CENTER         =  920065803

      OBJECT_920065803_FRAME     = 'IAU_DIDYMOS'

   \begintext


   In addition, the DIDYMOS_FIXED frame is defined as a reference frame 
   alias of IAU_DIDYMOS.

   \begindata

        FRAME_DIDYMOS_FIXED            = 920065803
        FRAME_920065803_NAME           = 'DIDYMOS_FIXED'
        FRAME_920065803_CLASS          = 4
        FRAME_920065803_CLASS_ID       = 920065803
        FRAME_920065803_CENTER         = 920065803

        TKFRAME_920065803_RELATIVE     = 'IAU_DIDYMOS'
        TKFRAME_920065803_SPEC         = 'MATRIX'
        TKFRAME_920065803_MATRIX       = ( 1   0   0
                                           0   1   0
                                           0   0   1 )
   
   \begintext


Dimorphos frames
--------------------------------------

   The asteroid satellite Dimorphos body-fixed frame -- IAU_DIMORPHOS -- is 
   defined as follows:

      -  +Z axis is the asteroid satellite rotation axis pointed towards the
         positive pole

      -  +X axis points towards the prime meridian

      -  +Y axis completes the right handed frame

      -  the origin of the frame is at the asteroid satellite center of mass.


   Since the asteroid rotation data is expected to be provided in a text PCK 
   in the form compliant with the IAU rotation model, the IAU_DIMORPHOS frame 
   is defined as a PCK based frame. This definition is included in all SPICE 
   Toolkits version N0067 or superior.

   \begindata

        FRAME_IAU_DIMORPHOS    =  10114
        FRAME_10114_NAME       = 'IAU_DIMORPHOS'
        FRAME_10114_CLASS      =  2
        FRAME_10114_CLASS_ID   =  120065803
        FRAME_10114_CENTER     =  120065803
        
        OBJECT_120065803_FRAME = 'IAU_DIMORPHOS'

   \begintext


   In addition, the DIMORPHOS_FIXED frame is defined as a reference frame 
   alias of IAU_DIMORPHOS.

   \begindata

        FRAME_DIMORPHOS_FIXED          = 120065803
        FRAME_120065803_NAME           = 'DIMORPHOS_FIXED'
        FRAME_120065803_CLASS          = 4
        FRAME_120065803_CLASS_ID       = 120065803
        FRAME_120065803_CENTER         = 120065803

        TKFRAME_120065803_RELATIVE     = 'IAU_DIMORPHOS'
        TKFRAME_120065803_SPEC         = 'MATRIX'
        TKFRAME_120065803_MATRIX       = ( 1   0   0
                                           0   1   0
                                           0   0   1 )
   
   \begintext


Didymos System NAIF ID Codes -- Definitions
======================================================================== 

   This section contains name to NAIF ID mappings for the Didymos system.
   Once the contents of this file are loaded into the KERNEL POOL, these
   mappings become available within SPICE, making it possible to use
   names instead of ID code in high level SPICE routine calls. This 
   mappings are included in all version N0067 or superior SPICE Toolkits.

   \begindata
   
      NAIF_BODY_NAME += ( 'DIDYMOS BARYCENTER' )     
      NAIF_BODY_CODE += ( 20065803             )
      
      NAIF_BODY_NAME += ( 'DIDYMOS' )                
      NAIF_BODY_CODE += ( 920065803 )
      
      NAIF_BODY_NAME += ( 'DIMORPHOS' )              
      NAIF_BODY_CODE += ( 120065803   )  
   
   \begintext


Didymos System DSK Surface ID Codes -- Definitions
========================================================================   

   This section contains name to ID mappings for the DART target
   body DSK surfaces. These mappings are supported by all SPICE
   toolkits with integrated DSK capabilities (version N0066 or later).


   Asteroid Didymos Surface name/IDs:

          DSK Surface Name           ID        Body ID
      ==========================   =========  =========
      DIDYMOS_50680MM_RDR_V001     250680001  920065803


   Name-ID Mapping keywords:

   \begindata

      NAIF_SURFACE_NAME += 'DIDYMOS_50680MM_RDR_V001'
      NAIF_SURFACE_CODE += 250680001
      NAIF_SURFACE_BODY += 920065803

   \begintext    
     

   Satellite asteroid Dimorphos Surface name/IDs:

          DSK Surface Name           ID        Body ID
      ==========================   =========  =========
      DIMORPHOS_06650MM_RDR_V001   206650001  120065803
      
      
   Name-ID Mapping keywords:

   \begindata

      NAIF_SURFACE_NAME += 'DIMORPHOS_06650MM_RDR_V001'
      NAIF_SURFACE_CODE += 206650001
      NAIF_SURFACE_BODY += 120065803

   \begintext  


End of FK.
