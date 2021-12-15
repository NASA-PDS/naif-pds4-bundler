KPL/MK

   This meta-kernel lists the MAVEN SPICE kernels providing coverage
   for 2021. All of the kernels listed below are archived in the PDS
   MAVEN SPICE kernel archive. This set of files and the order in which
   they are listed were picked to provide the best available data and
   the most complete coverage for the specified year based on the
   information about the kernels available at the time this meta-kernel
   was made. For detailed information about the kernels listed below
   refer to the internal comments included in the kernels and the
   documentation accompanying the MAVEN SPICE kernel archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the MAVEN SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on August 12, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was maven_2021_v02.tm.

   \begindata

      PATH_VALUES     = ( '..'      )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'

                          '$KERNELS/fk/maven_v09.tf'

                          '$KERNELS/ik/maven_ant_v10.ti'
                          '$KERNELS/ik/maven_euv_v10.ti'
                          '$KERNELS/ik/maven_iuvs_v11.ti'
                          '$KERNELS/ik/maven_ngims_v10.ti'
                          '$KERNELS/ik/maven_sep_v12.ti'
                          '$KERNELS/ik/maven_static_v11.ti'
                          '$KERNELS/ik/maven_swea_v11.ti'
                          '$KERNELS/ik/maven_swia_v10.ti'

                          '$KERNELS/sclk/mvn_sclkscet_00091.tsc'

                          '$KERNELS/spk/de430s.bsp'
                          '$KERNELS/spk/mar097s.bsp'

                          '$KERNELS/spk/maven_struct_v01.bsp'

                          '$KERNELS/spk/maven_orb_rec_210101_210401_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_210401_210701_v1.bsp'

                          '$KERNELS/ck/mvn_iuvs_rem_210101_210331_v01.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_210401_210630_v01.bc'

                          '$KERNELS/ck/mvn_app_pred_210104_210120_v01.bc'

                          '$KERNELS/ck/mvn_app_rel_201228_210103_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210104_210110_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210111_210117_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210118_210124_v03.bc'
                          '$KERNELS/ck/mvn_app_rel_210125_210131_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210201_210207_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210208_210214_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210215_210221_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210222_210228_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210301_210307_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210308_210314_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210315_210321_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210322_210328_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210329_210404_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210405_210411_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210412_210418_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210419_210425_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210426_210502_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210503_210509_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210510_210516_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210517_210523_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210524_210530_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210531_210606_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210607_210613_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210614_210620_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_210621_210627_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_210628_210704_v02.bc'

                          '$KERNELS/ck/mvn_swea_nom_131118_300101_v02.bc'

                          '$KERNELS/ck/mvn_sc_pred_210104_210120_v01.bc'

                          '$KERNELS/ck/mvn_sc_rel_201228_210103_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210104_210110_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210111_210117_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210118_210124_v04.bc'
                          '$KERNELS/ck/mvn_sc_rel_210125_210131_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210201_210207_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210208_210214_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210215_210221_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210222_210228_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210301_210307_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210308_210314_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210315_210321_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210322_210328_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210329_210404_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210405_210411_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210412_210418_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210419_210425_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210426_210502_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210503_210509_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210510_210516_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210517_210523_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210524_210530_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210531_210606_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210607_210613_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210614_210620_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_210621_210627_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_210628_210704_v02.bc'

                        )

   \begintext

End of MK file.
