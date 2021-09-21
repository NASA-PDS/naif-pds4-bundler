KPL/MK

   This meta-kernel lists the DART SPICE kernels providing coverage
   for the whole DART mission. All kernels listed below are archived
   in the DART SPICE PDS archive at the NAIF node of PDS. This set of
   files and the order in which they are listed were picked to provide
   the best available data and the most complete coverage based on the
   information about the kernels available at the time this meta-kernel
   was made. For detailed information about the kernels listed below
   refer to the internal comments included in the kernels and to the
   documentation accompanying the DART SPICE archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the DART SPICE PDS archive's ``kernels'' directory on
   their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on September 3, 2021 by Marc Costa Sitja,
   NAIF/JPL. The original name of this file was dart_v01.tm.

   \begindata

      PATH_VALUES     = ( '..' )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

          '$KERNELS/lsk/naif0012.tls'

          '$KERNELS/pck/pck00010.tpc'

          '$KERNELS/pck/didymos_system_d300_s101_02.tpc'

          '$KERNELS/fk/dart_005.tf'
          '$KERNELS/fk/licia_002.tf'
          '$KERNELS/fk/didymos_system_000.tf

          '$KERNELS/ik/dart_draco_002.ti'
          '$KERNELS/ik/licia_pl_001.ti'

          '$KERNELS/sclk/dart_sclk_0001.tsc'
          '$KERNELS/sclk/licia_sclk_0001.tsc'

          '$KERNELS/spk/de430.bsp'
          '$KERNELS/spk/didymos_barycenter_d300_v01.bsp'
          '$KERNELS/spk/didymos_d300_s101_v01.bsp'
          '$KERNELS/spk/dimorphos_d300_s101_v01.bsp'

          '$KERNELS/spk/dart_211124_221017_v01.bsp'

          '$KERNELS/ck/dart_sc_pred_211124_221017_v01.bc'

                        )

   \begintext

End of MK file.
