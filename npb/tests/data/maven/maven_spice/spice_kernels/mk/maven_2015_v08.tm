KPL/MK

   This meta-kernel lists the MAVEN SPICE kernels providing coverage
   for 2015. All of the kernels listed below are archived in the PDS
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

   This file was created on August 9, 2019 by Boris Semenov, NAIF/JPL.
   The original name of this file was maven_2015_v08.tm.

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

                          '$KERNELS/sclk/mvn_sclkscet_00072.tsc'

                          '$KERNELS/spk/de430s.bsp'
                          '$KERNELS/spk/mar097s.bsp'

                          '$KERNELS/spk/maven_struct_v01.bsp'

                          '$KERNELS/spk/maven_orb_rec_150101_150401_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_150401_150701_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_150701_151001_v1.bsp'
                          '$KERNELS/spk/maven_orb_rec_151001_160101_v1.bsp'

                          '$KERNELS/ck/mvn_iuvs_rem_150101_150331_v03.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_150401_150630_v03.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_150701_150930_v03.bc'
                          '$KERNELS/ck/mvn_iuvs_rem_151001_151231_v03.bc'

                          '$KERNELS/ck/mvn_app_rel_141229_150104_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150105_150111_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150112_150118_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150119_150125_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150126_150201_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150202_150208_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150209_150215_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150216_150222_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150223_150301_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150302_150308_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150309_150315_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150316_150322_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150323_150329_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150330_150405_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150406_150412_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150413_150419_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150420_150426_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150427_150503_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150504_150510_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150511_150517_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150518_150524_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150525_150531_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150601_150607_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150608_150614_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150615_150621_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150622_150628_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150629_150705_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150706_150712_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150713_150719_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150720_150726_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150727_150802_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150803_150809_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150810_150816_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150817_150823_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150824_150830_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150831_150906_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150907_150913_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150914_150920_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_150921_150927_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_150928_151004_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151005_151011_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151012_151018_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_151019_151025_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_151026_151101_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151102_151108_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151109_151115_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151116_151122_v02.bc'
                          '$KERNELS/ck/mvn_app_rel_151123_151129_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151130_151206_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151207_151213_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151214_151220_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151221_151227_v01.bc'
                          '$KERNELS/ck/mvn_app_rel_151228_160103_v01.bc'

                          '$KERNELS/ck/mvn_swea_nom_131118_300101_v02.bc'

                          '$KERNELS/ck/mvn_sc_rel_141229_150104_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150105_150111_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150112_150118_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150119_150125_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150126_150201_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150202_150208_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150209_150215_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150216_150222_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150223_150301_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150302_150308_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150302_150308_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150309_150315_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150316_150322_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150323_150329_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150330_150405_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150406_150412_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150413_150419_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150420_150426_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150427_150503_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150504_150510_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150511_150517_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150518_150524_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150525_150531_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150601_150607_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150608_150614_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150615_150621_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150622_150628_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150629_150705_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150706_150712_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150713_150719_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150720_150726_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150727_150802_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150803_150809_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150810_150816_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150817_150823_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150824_150830_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150831_150906_v03.bc'
                          '$KERNELS/ck/mvn_sc_rel_150907_150913_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150914_150920_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_150921_150927_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_150928_151004_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151005_151011_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151012_151018_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_151019_151025_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_151026_151101_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151102_151108_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151109_151115_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_151116_151122_v02.bc'
                          '$KERNELS/ck/mvn_sc_rel_151123_151129_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151130_151206_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151207_151213_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151214_151220_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151221_151227_v01.bc'
                          '$KERNELS/ck/mvn_sc_rel_151228_160103_v01.bc'

                        )

   \begintext

End of MK file.
