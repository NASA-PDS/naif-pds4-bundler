KPL/FK

ExoMars2016 Target Body DSK Surface ID Codes
========================================================================

   This frame kernel contains a set of ExoMars2016 Target Body DSK Surface ID
   Codes for Phobos, Deimos, Mars and the TGO spacecraft.


Version and Date
------------------------------------------------------------------------

   Version 0.3 -- April 24, 2020 -- Ricardo Valles Blanco, ESAC/ESA

      Fixed typos for PDS4 Bundle release Version 2.0, and updated
      contact information.

   Version 0.2 -- April 24, 2020 -- Marc Costa Sitja, ESAC/ESA

      Added new surfaces for Phobos: PHOBOS_M003_GAS_V01 and
      PHOBOS_K275_DLR_V02.

   Version 0.1 -- March 4, 2020 -- Marc Costa Sitja, ESAC/ESA

      Added TGO S/C-related Surfaces and IDs.

   Version 0.0 -- January 4, 2019 -- Marc Costa Sitja, ESAC/ESA

      First version.


References
------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``DS-Kernel Required Reading''

   4. TGO Frames Kernel.


Contact Information
------------------------------------------------------------------------

   If you have any questions regarding this file contact SPICE support at
   ESAC:

           Alfredo Escalante Lopez
           (+34) 91-8131-429
           spice@sciops.esa.int,

   or SPICE support at IKI:

           Alexander Abbakumov
           +7 (495) 333-40-13
           aabbakumov@romance.iki.rssi.ru

   or NAIF at JPL:

           Boris Semenov
           +1 (818) 354-8136
           Boris.Semenov@jpl.nasa.gov


Implementation Notes
------------------------------------------------------------------------

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


Definition Section
------------------------------------------------------------------------

   This section contains name to ID mappings for the ExoMars2016 target
   body DSK surfaces. These mappings are supported by all SPICE
   toolkits with integrated DSK capabilities (version N0066 or later).

   TGO Spacecraft Surface name/IDs:

          DSK Surface Name           ID      Body ID
      ===========================  =======  ========

      TGO_SC_BUS                  -143000   -143000
      TGO_SC_SA+Z                 -143011   -143011
      TGO_SC_SA-Z                 -143013   -143013
      TGO_SC_HGA                  -143025   -143025

   Name-ID Mapping keywords:

   \begindata

       NAIF_SURFACE_NAME += 'TGO_SC_BUS'
       NAIF_SURFACE_CODE += -143000
       NAIF_SURFACE_BODY += -143000

       NAIF_SURFACE_NAME += 'TGO_SC_SA+Z'
       NAIF_SURFACE_CODE += -143011
       NAIF_SURFACE_BODY += -143011

       NAIF_SURFACE_NAME += 'TGO_SC_SA-Z'
       NAIF_SURFACE_CODE += -143013
       NAIF_SURFACE_BODY += -143013

       NAIF_SURFACE_NAME += 'TGO_SC_HGA'
       NAIF_SURFACE_CODE += -143025
       NAIF_SURFACE_BODY += -143025

   \begintext


   Mars Satellite Phobos Surface name/IDs:

          DSK Surface Name          ID    Body ID
      ===========================  =====  =======

      PHOBOS_M157_GAS_V01          14011      401
      PHOBOS_M003_GAS_V01          14012      401
      PHOBOS_K137_DLR_V01          10041      401
      PHOBOS_K275_DLR_V02          10042      401


   Name-ID Mapping keywords:

   \begindata

      NAIF_SURFACE_NAME += 'PHOBOS_M157_GAS_V01'
      NAIF_SURFACE_CODE += 14011
      NAIF_SURFACE_BODY += 401

      NAIF_SURFACE_NAME += 'PHOBOS_M003_GAS_V01'
      NAIF_SURFACE_CODE += 14012
      NAIF_SURFACE_BODY += 401

      NAIF_SURFACE_NAME += 'PHOBOS_K137_DLR_V01'
      NAIF_SURFACE_CODE += 10041
      NAIF_SURFACE_BODY += 401

      NAIF_SURFACE_NAME += 'PHOBOS_K275_DLR_V02'
      NAIF_SURFACE_CODE += 10042
      NAIF_SURFACE_BODY += 401

   \begintext


   Mars Satellite Deimos Surface name/IDs:

          DSK Surface Name          ID    Body ID
      ===========================  =====  =======

      DEIMOS_K002_THO_V01          14020      402


   Name-ID Mapping keywords:

   \begindata

      NAIF_SURFACE_NAME += 'DEIMOS_K002_THO_V01'
      NAIF_SURFACE_CODE += 14020
      NAIF_SURFACE_BODY += 402

   \begintext


End of FK file.
