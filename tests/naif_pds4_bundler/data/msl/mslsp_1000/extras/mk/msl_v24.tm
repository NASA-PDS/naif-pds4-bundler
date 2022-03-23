KPL/MK

   This meta-kernel lists the MSL SPICE kernels providing coverage for
   the whole mission up to the end of coverage of the latest rover path
   SPK provided in the data set at the time when this MK was created.
   All of the kernels listed below are archived in the MSL SPICE data
   set (DATA_SET_ID = "MSL-M-SPICE-6-V1.0"). This set of files and the
   order in which they are listed were picked to provide the best
   available data and the most complete coverage based on the
   information about the kernels available at the time this meta-kernel
   was made. For detailed information about the kernels listed below
   refer to the internal comments included in the kernels and the
   documentation accompanying the MSL SPICE data set.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the MSL SPICE data set's ``data'' directory on their
   system. Replacing ``/'' with ``\'' and converting line terminators
   to the format native to the user's system may also be required if
   this meta-kernel is to be used on a non-UNIX workstation.

   This file was created on July 28, 2020 by Boris Semenov, NAIF/JPL.
   The original name of this file was msl_v24.tm.

   \begindata

      PATH_VALUES     = ( './data' )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00008.tpc'

                          '$KERNELS/sclk/msl_lmst_ops120808_v1.tsc'

                          '$KERNELS/sclk/msl_76_sclkscet_refit_s2.tsc'

                          '$KERNELS/fk/msl_v08.tf'

                          '$KERNELS/ik/msl_aux_v00.ti'
                          '$KERNELS/ik/msl_chrmi_20120731_c03.ti'
                          '$KERNELS/ik/msl_hbla_20120731_c03.ti'
                          '$KERNELS/ik/msl_hblb_20120731_c03.ti'
                          '$KERNELS/ik/msl_hbra_20120731_c03.ti'
                          '$KERNELS/ik/msl_hbrb_20120731_c03.ti'
                          '$KERNELS/ik/msl_hfla_20120731_c03.ti'
                          '$KERNELS/ik/msl_hflb_20120731_c03.ti'
                          '$KERNELS/ik/msl_hfra_20120731_c03.ti'
                          '$KERNELS/ik/msl_hfrb_20120731_c03.ti'
                          '$KERNELS/ik/msl_mahli_20120731_c02.ti'
                          '$KERNELS/ik/msl_mardi_20120731_c02.ti'
                          '$KERNELS/ik/msl_ml_20120731_c03.ti'
                          '$KERNELS/ik/msl_mr_20120731_c03.ti'
                          '$KERNELS/ik/msl_nla_20120731_c04.ti'
                          '$KERNELS/ik/msl_nlb_20130530_c05.ti'
                          '$KERNELS/ik/msl_nra_20120731_c04.ti'
                          '$KERNELS/ik/msl_nrb_20130530_c05.ti'
                          '$KERNELS/ik/msl_struct_v01.ti'

                          '$KERNELS/spk/msl_struct_v02.bsp'

                          '$KERNELS/spk/de425s.bsp'
                          '$KERNELS/spk/mar085s.bsp'

                          '$KERNELS/spk/msl_cruise_v1.bsp'

                          '$KERNELS/spk/msl_edl_v01.bsp'

                          '$KERNELS/spk/msl_ls_ops120808_iau2000_v1.bsp'

                          '$KERNELS/spk/msl_surf_rover_loc_0000_2003_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2003_2127_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2127_2224_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2224_2358_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2358_2482_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2482_2579_v1.bsp'
                          '$KERNELS/spk/msl_surf_rover_loc_2579_2713_v1.bsp'

                          '$KERNELS/ck/msl_ra_toolsref_v1.bc'

                          '$KERNELS/ck/msl_cruise_recon_rawrt_v2.bc'
                          '$KERNELS/ck/msl_cruise_recon_raweng_v1.bc'

                          '$KERNELS/ck/msl_edl_v01.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0000_0089_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0000_0089_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0000_0089_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0000_0089_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0000_0089_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0000_0089_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0089_0179_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0089_0179_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0089_0179_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0089_0179_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0089_0179_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0089_0179_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0179_0269_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0179_0269_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0179_0269_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0179_0269_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0179_0269_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0179_0269_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0269_0359_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0269_0359_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0269_0359_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0269_0359_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0269_0359_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0269_0359_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0359_0449_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0359_0449_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0359_0449_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0359_0449_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0359_0449_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0359_0449_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0449_0583_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0449_0583_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0449_0583_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0449_0583_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0449_0583_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0449_0583_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0583_0707_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0583_0707_v2.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0583_0707_v2.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0583_0707_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0583_0707_v2.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0583_0707_v2.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0707_0804_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0707_0804_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0707_0804_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0707_0804_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0707_0804_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0707_0804_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0804_0938_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0804_0938_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0804_0938_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0804_0938_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0804_0938_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0804_0938_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_0938_1062_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_0938_1062_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_0938_1062_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_0938_1062_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_0938_1062_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_0938_1062_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1062_1159_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1062_1159_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1062_1159_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1062_1159_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1062_1159_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1062_1159_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1159_1293_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1159_1293_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1159_1293_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1159_1293_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1159_1293_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1159_1293_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1293_1417_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1293_1417_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1293_1417_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1293_1417_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1293_1417_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1293_1417_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1417_1514_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1417_1514_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1417_1514_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1417_1514_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1417_1514_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1417_1514_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1514_1648_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1514_1648_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1514_1648_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1514_1648_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1514_1648_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1514_1648_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1648_1772_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1648_1772_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1648_1772_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1648_1772_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1648_1772_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1648_1772_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1772_1869_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1772_1869_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1772_1869_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1772_1869_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1772_1869_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1772_1869_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_1869_2003_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_1869_2003_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_1869_2003_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_1869_2003_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_1869_2003_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_1869_2003_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2003_2127_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2003_2127_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2003_2127_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2003_2127_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2003_2127_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2003_2127_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2127_2224_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2127_2224_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2127_2224_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2127_2224_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2127_2224_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2127_2224_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2224_2358_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2224_2358_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2224_2358_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2224_2358_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2224_2358_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2224_2358_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2358_2482_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2358_2482_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2358_2482_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2358_2482_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2358_2482_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2358_2482_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2482_2579_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2482_2579_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2482_2579_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2482_2579_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2482_2579_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2482_2579_v1.bc'

                          '$KERNELS/ck/msl_surf_hga_tlm_2579_2713_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmenc_2579_2713_v1.bc'
                          '$KERNELS/ck/msl_surf_ra_tlmres_2579_2713_v1.bc'
                          '$KERNELS/ck/msl_surf_rover_tlm_2579_2713_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmenc_2579_2713_v1.bc'
                          '$KERNELS/ck/msl_surf_rsm_tlmres_2579_2713_v1.bc'

                        )

   \begintext

End of MK file.
