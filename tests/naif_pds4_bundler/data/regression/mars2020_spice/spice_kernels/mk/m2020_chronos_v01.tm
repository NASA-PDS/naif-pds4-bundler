KPL/MK

   This meta-kernel lists the M2020 SPICE kernels needed for the CHRONOS
   time conversion application. All of the kernels listed below are
   archived in the PDS M2020 SPICE kernel archive. This set of files
   and the order in which they are listed were picked to provide the
   best available data and the most complete coverage based on the
   information about the kernels available at the time this meta-kernel
   was made. For detailed information about the kernels listed below refer
   to the internal comments included in the kernels and the documentation
   accompanying the M2020 SPICE kernel archive.

   This meta-kernel also includes keywords setting the SPICE CHRONOS
   utility configuration parameters (spacecraft ID, planet ID, landing UTC,
   landing SOL index, and Sun GM).

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the M2020 SPICE data set's ``data'' directory on their
   system. Replacing ``/'' with ``\'' and converting line terminators
   to the format native to the user's system may also be required if
   this meta-kernel is to be used on a non-UNIX workstation.

   This file was created on August 19, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was m2020_chronos_v01.tm.

   \begindata

      PATH_VALUES       = ( '..'      )

      PATH_SYMBOLS      = ( 'KERNELS' )

      KERNELS_TO_LOAD   = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/sclk/m2020_168_sclkscet_00007.tsc'
                          '$KERNELS/sclk/m2020_lmst_ops210303_v1.tsc'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/spk/de438s.bsp'
                          '$KERNELS/spk/mar097.bsp'
                          '$KERNELS/spk/m2020_cruise_od138_v1.bsp'
                          '$KERNELS/spk/m2020_edl_v01.bsp'
                          '$KERNELS/spk/m2020_ls_ops210303_iau2000_v1.bsp'
                          '$KERNELS/spk/m2020_atls_ops210303_v1.bsp'

                          '$KERNELS/fk/m2020_v04.tf'

                          )

      SPACECRAFT_ID     = -168
      CENTER_ID         = 499
      LANDING_TIME      = '2021-02-18T20:43:48.8175'
      LANDING_SOL_INDEX = 0
      BODY10_GM         = 132712440041.9394

   \begintext

End of MK file.
