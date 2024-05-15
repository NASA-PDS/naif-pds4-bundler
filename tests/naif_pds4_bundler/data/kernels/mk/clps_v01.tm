KPL/MK

   This meta-kernel lists the CLPS SPICE kernels providing coverage
   for the CLPS missions. All of the kernels listed below are archived
   in the PDS CLPS SPICE kernel archive. This set of files and the order
   in which they are listed were picked to provide the best available data
   and the most complete coverage based on the information about the kernels
   available at the time this meta-kernel was made. For detailed
   information about the kernels listed below refer to the internal
   comments included in the kernels and the documentation accompanying
   the CLPS SPICE kernel archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the CLPS SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on March 5, 2024 by Alyssa Bailey, JPL.
   The original name of this file was clps_v01.tm.

   \begindata

      PATH_VALUES     = ( '..'      )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/pck/moon_pa_de421_1900-2050.bpc'
                          '$KERNELS/pck/earth_000101_240321_231228.bpc'

                          '$KERNELS/fk/moon_080317.tf'
                          '$KERNELS/fk/clps_to_2ab_v00.tf
                          '$KERNELS/fk/clps_to_2im_v00.tf

                          '$KERNELS/ik/clps_to_2ab_pll_v00.ti'
                          '$KERNELS/ik/clps_to_2im_ncll_v00.ti'

                          '$KERNELS/sclk/clps_to_2ab_sclkscet_v000.tsc'
                          '$KERNELS/sclk/clps_to_2im_sclkscet_v000.tsc'

                          '$KERNELS/spk/de421.bsp'
                          '$KERNELS/spk/de430.bsp'
                          '$KERNELS/spk/clps_to_2ab_d_v00.bsp'


                        )

   \begintext

End of MK file.
