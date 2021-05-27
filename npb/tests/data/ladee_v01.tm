KPL/MK

   This meta-kernel lists the LADEE SPICE kernels providing coverage
   for the whole mission. All of the kernels listed below are archived
   in the PDS LADEE SPICE kernel archive. This set of files and the
   order in which they are listed were picked to provide the best
   available data and the most complete coverage based on the information
   about the kernels available at the time this meta-kernel was made.
   For detailed information about the kernels listed below refer to the
   internal comments included in the kernels and the documentation
   accompanying the LADEE SPICE kernel archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the LADEE SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on May 25, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was ladee_v01.tm.

   \begindata

      PATH_VALUES       = ( '..'      )

      PATH_SYMBOLS      = ( 'KERNELS' )

      KERNELS_TO_LOAD   = (

                          '$KERNELS/lsk/naif0010.tls'

                          '$KERNELS/pck/pck00010.tpc'
                          '$KERNELS/pck/moon_pa_de421_1900_2050.bpc'

                          '$KERNELS/fk/moon_assoc_me.tf'
                          '$KERNELS/fk/moon_080317.tf'
                          '$KERNELS/fk/ladee_frames_2021140_v01.tf'

                          '$KERNELS/ik/ladee_ldex_v01.ti'
                          '$KERNELS/ik/ladee_nms_v00.ti'
                          '$KERNELS/ik/ladee_uvs_v00.ti'

                          '$KERNELS/sclk/ladee_clkcor_13250_14108_v01.tsc'

                          '$KERNELS/spk/de432s.bsp'
                          '$KERNELS/spk/ladee_r_13250_13279_pha_v01.bsp'
                          '$KERNELS/spk/ladee_r_13278_13325_loa_v01.bsp'
                          '$KERNELS/spk/ladee_r_13325_14108_sci_v01.bsp'
                          '$KERNELS/spk/ladee_r_14108_99001_imp_v01.bsp'

                          '$KERNELS/ck/ladee_13250_13330_v04.bc'
                          '$KERNELS/ck/ladee_13330_14030_v04.bc'
                          '$KERNELS/ck/ladee_14030_14108_v04.bc'

                          )

   \begintext

End of MK file.
