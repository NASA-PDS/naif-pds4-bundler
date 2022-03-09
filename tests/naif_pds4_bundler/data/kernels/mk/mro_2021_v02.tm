KPL/MK

   This meta-kernel lists the MRO SPICE kernels providing coverage for
   2021. All of the kernels listed below are archived in the MRO SPICE
   data set (DATA_SET_ID = "MRO-M-SPICE-6-V1.0"). This set of files and
   the order in which they are listed were picked to provide the best
   available data and the most complete coverage for the specified year
   based on the information about the kernels available at the time
   this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the MRO SPICE data set.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the MRO SPICE data set's ``data'' directory on their
   system. Replacing ``/'' with ``\'' and converting line terminators
   to the format native to the user's system may also be required if
   this meta-kernel is to be used on a non-UNIX workstation.

   This file was created on August 31, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was mro_2021_v02.tm.

   \begindata

      PATH_VALUES     = ( './data' )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00008.tpc'

                          '$KERNELS/sclk/mro_sclkscet_00099_65536.tsc'

                          '$KERNELS/fk/mro_v16.tf'

                          '$KERNELS/ik/mro_crism_v10.ti'
                          '$KERNELS/ik/mro_ctx_v11.ti'
                          '$KERNELS/ik/mro_hirise_v12.ti'
                          '$KERNELS/ik/mro_marci_v10.ti'
                          '$KERNELS/ik/mro_mcs_v10.ti'
                          '$KERNELS/ik/mro_onc_v10.ti'

                          '$KERNELS/spk/mar097.bsp'
                          '$KERNELS/spk/de421.bsp'

                          '$KERNELS/spk/mro_psp58.bsp'
                          '$KERNELS/spk/mro_psp59.bsp'

                          '$KERNELS/spk/mro_psp58_ssd_mro95a.bsp'
                          '$KERNELS/spk/mro_psp59_ssd_mro95a.bsp'

                          '$KERNELS/spk/mro_struct_v10.bsp'

                          '$KERNELS/ck/mro_hga_psp_210308_210320p.bc'
                          '$KERNELS/ck/mro_hga_psp_210322_210403p.bc'

                          '$KERNELS/ck/mro_sa_psp_210308_210320p.bc'
                          '$KERNELS/ck/mro_sa_psp_210322_210403p.bc'

                          '$KERNELS/ck/mro_sc_psp_210308_210320p.bc'
                          '$KERNELS/ck/mro_sc_psp_210322_210403p.bc'

                          '$KERNELS/ck/mro_hga_psp_201229_210104.bc'
                          '$KERNELS/ck/mro_hga_psp_210105_210111.bc'
                          '$KERNELS/ck/mro_hga_psp_210112_210118.bc'
                          '$KERNELS/ck/mro_hga_psp_210119_210125.bc'
                          '$KERNELS/ck/mro_hga_psp_210126_210201.bc'
                          '$KERNELS/ck/mro_hga_psp_210202_210208.bc'
                          '$KERNELS/ck/mro_hga_psp_210209_210215.bc'
                          '$KERNELS/ck/mro_hga_psp_210216_210222.bc'
                          '$KERNELS/ck/mro_hga_psp_210223_210301.bc'
                          '$KERNELS/ck/mro_hga_psp_210302_210308.bc'
                          '$KERNELS/ck/mro_hga_psp_210309_210315.bc'
                          '$KERNELS/ck/mro_hga_psp_210316_210322.bc'
                          '$KERNELS/ck/mro_hga_psp_210323_210329.bc'
                          '$KERNELS/ck/mro_hga_psp_210330_210405.bc'
                          '$KERNELS/ck/mro_hga_psp_210406_210412.bc'
                          '$KERNELS/ck/mro_hga_psp_210413_210419.bc'
                          '$KERNELS/ck/mro_hga_psp_210420_210426.bc'
                          '$KERNELS/ck/mro_hga_psp_210427_210503.bc'
                          '$KERNELS/ck/mro_hga_psp_210504_210510.bc'
                          '$KERNELS/ck/mro_hga_psp_210511_210517.bc'
                          '$KERNELS/ck/mro_hga_psp_210518_210524.bc'
                          '$KERNELS/ck/mro_hga_psp_210525_210531.bc'
                          '$KERNELS/ck/mro_hga_psp_210601_210607.bc'
                          '$KERNELS/ck/mro_hga_psp_210608_210614.bc'
                          '$KERNELS/ck/mro_hga_psp_210615_210621.bc'
                          '$KERNELS/ck/mro_hga_psp_210622_210628.bc'
                          '$KERNELS/ck/mro_hga_psp_210629_210705.bc'

                          '$KERNELS/ck/mro_sa_psp_201229_210104.bc'
                          '$KERNELS/ck/mro_sa_psp_210105_210111.bc'
                          '$KERNELS/ck/mro_sa_psp_210112_210118.bc'
                          '$KERNELS/ck/mro_sa_psp_210119_210125.bc'
                          '$KERNELS/ck/mro_sa_psp_210126_210201.bc'
                          '$KERNELS/ck/mro_sa_psp_210202_210208.bc'
                          '$KERNELS/ck/mro_sa_psp_210209_210215.bc'
                          '$KERNELS/ck/mro_sa_psp_210216_210222.bc'
                          '$KERNELS/ck/mro_sa_psp_210223_210301.bc'
                          '$KERNELS/ck/mro_sa_psp_210302_210308.bc'
                          '$KERNELS/ck/mro_sa_psp_210309_210315.bc'
                          '$KERNELS/ck/mro_sa_psp_210316_210322.bc'
                          '$KERNELS/ck/mro_sa_psp_210323_210329.bc'
                          '$KERNELS/ck/mro_sa_psp_210330_210405.bc'
                          '$KERNELS/ck/mro_sa_psp_210406_210412.bc'
                          '$KERNELS/ck/mro_sa_psp_210413_210419.bc'
                          '$KERNELS/ck/mro_sa_psp_210420_210426.bc'
                          '$KERNELS/ck/mro_sa_psp_210427_210503.bc'
                          '$KERNELS/ck/mro_sa_psp_210504_210510.bc'
                          '$KERNELS/ck/mro_sa_psp_210511_210517.bc'
                          '$KERNELS/ck/mro_sa_psp_210518_210524.bc'
                          '$KERNELS/ck/mro_sa_psp_210525_210531.bc'
                          '$KERNELS/ck/mro_sa_psp_210601_210607.bc'
                          '$KERNELS/ck/mro_sa_psp_210608_210614.bc'
                          '$KERNELS/ck/mro_sa_psp_210615_210621.bc'
                          '$KERNELS/ck/mro_sa_psp_210622_210628.bc'
                          '$KERNELS/ck/mro_sa_psp_210629_210705.bc'

                          '$KERNELS/ck/mro_mcs_psp_210101_210131.bc'
                          '$KERNELS/ck/mro_mcs_psp_210201_210228.bc'
                          '$KERNELS/ck/mro_mcs_psp_210301_210331.bc'
                          '$KERNELS/ck/mro_mcs_psp_210401_210430.bc'
 
                          '$KERNELS/ck/mro_crm_psp_210101_210131.bc'
                          '$KERNELS/ck/mro_crm_psp_210201_210228.bc'
                          '$KERNELS/ck/mro_crm_psp_210301_210331.bc'
                          '$KERNELS/ck/mro_crm_psp_210401_210430.bc'
                          '$KERNELS/ck/mro_crm_psp_210501_210531.bc'
                          '$KERNELS/ck/mro_crm_psp_210601_210630.bc'

                          '$KERNELS/ck/mro_sc_psp_201229_210104.bc'
                          '$KERNELS/ck/mro_sc_psp_210105_210111.bc'
                          '$KERNELS/ck/mro_sc_psp_210112_210118.bc'
                          '$KERNELS/ck/mro_sc_psp_210119_210125.bc'
                          '$KERNELS/ck/mro_sc_psp_210126_210201.bc'
                          '$KERNELS/ck/mro_sc_psp_210202_210208.bc'
                          '$KERNELS/ck/mro_sc_psp_210209_210215.bc'
                          '$KERNELS/ck/mro_sc_psp_210216_210222.bc'
                          '$KERNELS/ck/mro_sc_psp_210223_210301.bc'
                          '$KERNELS/ck/mro_sc_psp_210302_210308.bc'
                          '$KERNELS/ck/mro_sc_psp_210309_210315.bc'
                          '$KERNELS/ck/mro_sc_psp_210316_210322.bc'
                          '$KERNELS/ck/mro_sc_psp_210323_210329.bc'
                          '$KERNELS/ck/mro_sc_psp_210330_210405.bc'
                          '$KERNELS/ck/mro_sc_psp_210406_210412.bc'
                          '$KERNELS/ck/mro_sc_psp_210413_210419.bc'
                          '$KERNELS/ck/mro_sc_psp_210420_210426.bc'
                          '$KERNELS/ck/mro_sc_psp_210427_210503.bc'
                          '$KERNELS/ck/mro_sc_psp_210504_210510.bc'
                          '$KERNELS/ck/mro_sc_psp_210511_210517.bc'
                          '$KERNELS/ck/mro_sc_psp_210518_210524.bc'
                          '$KERNELS/ck/mro_sc_psp_210525_210531.bc'
                          '$KERNELS/ck/mro_sc_psp_210601_210607.bc'
                          '$KERNELS/ck/mro_sc_psp_210608_210614.bc'
                          '$KERNELS/ck/mro_sc_psp_210615_210621.bc'
                          '$KERNELS/ck/mro_sc_psp_210622_210628.bc'
                          '$KERNELS/ck/mro_sc_psp_210629_210705.bc'

                        )

   \begintext
