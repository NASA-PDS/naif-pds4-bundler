KPL/MK

   This meta-kernel lists the M01 SPICE kernels providing coverage for
   2020. All of the kernels listed below are archived in the M01 SPICE
   data set (DATA_SET_ID = "ODY-M-SPICE-6-V1.0"). This set of files and
   the order in which they are listed were picked to provide the best
   available data and the most complete coverage for the specified year
   based on the information about the kernels available at the time
   this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the M01 SPICE data set.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the M01 SPICE data set's ``data'' directory on their
   system. Replacing ``/'' with ``\'' and converting line terminators
   to the format native to the user's system may also be required if
   this meta-kernel is to be used on a non-UNIX workstation.

   This file was created on March 24, 2021 by Marc Costa Sitja,
   NAIF/JPL. The original name of this file was m01_2020_v03.tm.

   \begindata

      PATH_VALUES     = ( './data' )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/fk/m01_v28.tf'

                          '$KERNELS/ik/m01_marie_v10.ti'
                          '$KERNELS/ik/m01_themis_v32.ti'

                          '$KERNELS/sclk/orb1_sclkscet_00265.tsc'

                          '$KERNELS/spk/mar063.bsp'

                          '$KERNELS/spk/m01_struct_v10.bsp'

                          '$KERNELS/spk/m01_ext62.bsp'
                          '$KERNELS/spk/m01_ext63.bsp'
                          '$KERNELS/spk/m01_ext64.bsp'

                          '$KERNELS/spk/m01_ext62_ipng_mgs95j.bsp'
                          '$KERNELS/spk/m01_ext63_ipng_mgs95j.bsp'
                          '$KERNELS/spk/m01_ext64_ipng_mgs95j.bsp'

                          '$KERNELS/ck/m01_hga_ext62.bc'
                          '$KERNELS/ck/m01_hga_ext63.bc'
                          '$KERNELS/ck/m01_hga_ext64.bc'

                          '$KERNELS/ck/m01_sa_ext62.bc'
                          '$KERNELS/ck/m01_sa_ext63.bc'
                          '$KERNELS/ck/m01_sa_ext64.bc'

                          '$KERNELS/ck/m01_sc_ext62_rec_nadir.bc'
                          '$KERNELS/ck/m01_sc_ext63_rec_nadir.bc'
                          '$KERNELS/ck/m01_sc_ext64_rec_nadir.bc'

                          '$KERNELS/ck/m01_sc_ext62.bc'
                          '$KERNELS/ck/m01_sc_ext63.bc'
                          '$KERNELS/ck/m01_sc_ext64.bc'

                        )

   \begintext
