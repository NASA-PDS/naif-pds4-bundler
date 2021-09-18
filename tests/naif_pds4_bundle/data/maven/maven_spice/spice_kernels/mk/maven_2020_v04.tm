KPL/MK

   This meta-kernel lists the MAVEN SPICE kernels providing coverage
   for 2020. All of the kernels listed below are archived in the PDS
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

   This file was created on February 8, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was maven_2020_v04.tm.

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

                          '$KERNELS/sclk/mvn_sclkscet_00086.tsc'

                          '$KERNELS/spk/de430s.bsp'
                          '$KERNELS/spk/mar097s.bsp'

                          '$KERNELS/spk/maven_struct_v01.bsp'

                          '$KERNELS/spk/maven_orb_rec_200101_200401_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_200401_200701_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_200701_201001_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_201001_210101_v1.bsp'

                          '$KERNELS/ck/mvn_iuvs_rem_200101_200331_v01.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_200401_200630_v01.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_200701_200930_v01.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_201001_201231_v01.bc'

                          '$KERNELS/ck/mvn_app_rel_191230_200105_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200106_200112_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200113_200119_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200120_200126_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200127_200202_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200203_200209_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200210_200216_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200217_200223_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200224_200301_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200302_200308_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200309_200315_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200316_200322_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200323_200329_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200330_200405_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200406_200412_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200413_200419_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200420_200426_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200427_200503_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200504_200510_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200511_200517_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200518_200524_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200525_200531_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200601_200607_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200608_200614_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200615_200621_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200622_200628_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200629_200705_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200706_200712_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200713_200719_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200720_200726_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200727_200802_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200803_200809_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200810_200816_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200817_200823_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200824_200830_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200831_200906_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200907_200913_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200914_200920_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_200921_200927_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_200928_201004_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201005_201011_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201012_201018_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201019_201025_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201026_201101_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201102_201108_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201109_201115_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201116_201122_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201123_201129_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201130_201206_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_201207_201213_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201214_201220_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201221_201227_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_201228_210103_v02.bc'                         

                          '$KERNELS/ck/mvn_swea_nom_131118_300101_v02.bc'

                          '$KERNELS/ck/mvn_sc_rel_191230_200105_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200106_200112_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200113_200119_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200120_200126_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200127_200202_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200203_200209_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200210_200216_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200217_200223_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200224_200301_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200302_200308_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200309_200315_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200316_200322_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200323_200329_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200330_200405_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200406_200412_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200413_200419_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200420_200426_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200427_200503_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200504_200510_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200511_200517_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200518_200524_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200525_200531_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200601_200607_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200608_200614_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200615_200621_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200622_200628_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200629_200705_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200706_200712_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200713_200719_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200720_200726_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200727_200802_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200803_200809_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200810_200816_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200817_200823_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200824_200830_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200831_200906_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200907_200913_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200914_200920_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_200921_200927_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_200928_201004_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_201005_201011_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201012_201018_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201019_201025_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_201026_201101_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_201102_201108_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201109_201115_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201116_201122_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_201123_201129_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201130_201206_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_201207_201213_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201214_201220_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201221_201227_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_201228_210103_v02.bc'

                        )

   \begintext

End of MK file.
