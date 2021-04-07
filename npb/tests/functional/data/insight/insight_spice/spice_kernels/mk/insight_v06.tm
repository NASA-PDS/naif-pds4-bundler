KPL/MK

   This meta-kernel lists the INSIGHT SPICE kernels providing coverage
   for the whole mission. All of the kernels listed below are archived
   in the PDS INSIGHT SPICE kernel archive. This set of files and the
   order in which they are listed were picked to provide the best
   available data and the most complete coverage for the specified year
   based on the information about the kernels available at the time
   this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the INSIGHT SPICE kernel
   archive.

   This meta-kernel also includes keywords setting the SPICE CHRONOS
   utility configuration parameters (spacecraft ID, planet ID, landing UTC,
   landing SOL index, and Sun GM).

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the INSIGHT SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on September 29, 2020 by Boris Semenov, NAIF/JPL.
   The original name of this file was insight_v06.tm.

   \begindata

      PATH_VALUES       = ( '..'      )

      PATH_SYMBOLS      = ( 'KERNELS' )

      KERNELS_TO_LOAD   = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/fk/insight_v05.tf'
                          '$KERNELS/fk/marcoa_v01.tf'
                          '$KERNELS/fk/marcob_v01.tf'

                          '$KERNELS/ik/insight_ant_v00.ti'
                          '$KERNELS/ik/insight_hp3_rad_v04.ti'
                          '$KERNELS/ik/insight_icc_20190114_c03.ti'
                          '$KERNELS/ik/insight_idc_20190103_c03.ti'

                          '$KERNELS/sclk/nsy_sclkscet_00017.tsc'
                          '$KERNELS/sclk/insight_lmst_ops181206_v1.tsc'
                          '$KERNELS/sclk/marcoa_fake_v01.tsc'
                          '$KERNELS/sclk/marcob_fake_v01.tsc'

                          '$KERNELS/spk/marcoa_180505_190110_200101_v1.bsp'
                          '$KERNELS/spk/marcob_180505_181228_200101_v1.bsp'
                          '$KERNELS/spk/de430s.bsp'
                          '$KERNELS/spk/mar097s.bsp'
                          '$KERNELS/spk/insight_struct_v01.bsp'
                          '$KERNELS/spk/insight_cru_ops_v1.bsp'
                          '$KERNELS/spk/insight_edl_rec_v1.bsp'
                          '$KERNELS/spk/insight_ls_ops181206_iau2000_v1.bsp'
                          '$KERNELS/spk/insight_atls_ops181206_v1.bsp'

                          '$KERNELS/ck/marcoa_cru_rec_181125_181127_v01.bc'
                          '$KERNELS/ck/marcob_cru_rec_181126_181127_v01.bc'
                          '$KERNELS/ck/insight_ida_enc_180505_181127_v1.bc'
                          '$KERNELS/ck/insight_ida_enc_181127_190331_v2.bc'
                          '$KERNELS/ck/insight_ida_enc_190331_190629_v2.bc'
                          '$KERNELS/ck/insight_ida_enc_190629_190918_v2.bc'
                          '$KERNELS/ck/insight_ida_enc_190925_190929_v1.bc'
                          '$KERNELS/ck/insight_ida_enc_190929_191120_v1.bc'
                          '$KERNELS/ck/insight_ida_enc_191120_200321_v1.bc'
                          '$KERNELS/ck/insight_ida_enc_200321_200623_v1.bc'
                          '$KERNELS/ck/insight_cruise2lander_v2.bc'
                          '$KERNELS/ck/insight_lander2cruise_v2.bc'
                          '$KERNELS/ck/insight_cru_rec_180505_181126_v01.bc'
                          '$KERNELS/ck/insight_edl_rec_v1.bc'
                          '$KERNELS/ck/insight_surf_ops_v1.bc'

                          )

      SPACECRAFT_ID     = -189
      CENTER_ID         = 499
      LANDING_TIME      = '2018-11-26T19:44:52.444'
      LANDING_SOL_INDEX = 0
      BODY10_GM         = 1.3271244004193938E+11

   \begintext

End of MK file.
