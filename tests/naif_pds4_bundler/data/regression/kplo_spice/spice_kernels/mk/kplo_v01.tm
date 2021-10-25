KPL/MK

   This meta-kernel lists the KPLO SPICE kernels providing coverage
   for the whole mission. All of the kernels listed below are archived
   in the PDS KPLO SPICE kernel archive. This set of files and the
   order in which they are listed were picked to provide the best
   available data and the most complete coverage based on the information
   about the kernels available at the time this meta-kernel was made.
   For detailed information about the kernels listed below refer to the
   internal comments included in the kernels and the documentation
   accompanying the KPLO SPICE kernel archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the KPLO SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on June 25, 2021 by Jo Ryeong Yim, KARI.
   The original name of this file was kplo_v01.tm.

   \begindata

      PATH_VALUES     = ( '..'      )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/fk/kplo_v00.tf'

                          '$KERNELS/ik/kplo_luti_v04.ti'

                          '$KERNELS/sclk/kplo_200926_000100.tsc'

                          '$KERNELS/spk/de432s.bsp'
                          '$KERNELS/spk/kplo_pl_230117_230124_v01.bsp'

                          '$KERNELS/ck/kplo_sc_230117_230121_v01.bc'

                        )

   \begintext

End of MK file.
