KPL/MK

Meta-kernel for BepiColombo Archived Kernels
==========================================================================

   This meta-kernel lists the BepiColombo Archived SPICE kernels
   providing information for the full mission. All of the kernels listed
   below are archived in the PSA BepiColombo SPICE kernel archive.

   This set of files and the order in which they are listed were picked to
   provide the best available data and the most complete coverage for the
   specified year based on the information about the kernels available at
   the time this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the BepiColombo
   SPICE kernel archive.


Usage of the Meta-kernel
-------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make
   use of this kernel must "load" the kernel normally during program
   initialization. Loading the kernel associates the data items with
   their names in a data structure called the "kernel pool".
   The SPICELIB routine FURNSH loads a kernel into the pool.


Implementation Notes
-------------------------------------------------------------------------

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the BepiColombo SPICE data set's ``data'' directory
   on their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.


-------------------

   This file was created on July 6, 2022 by Alfredo Escalante Lopez ESAC/ESA.
   The original name of this file was bc_v001.tm.


   \begindata

     PATH_VALUES       = ( '..' )

     PATH_SYMBOLS      = ( 'KERNELS' )

     KERNELS_TO_LOAD   = (

                          '$KERNELS/lsk/naif0012.tls'

                          '$KERNELS/pck/pck00010.tpc'
                          '$KERNELS/pck/gm_de431.tpc'

                          '$KERNELS/pck/earth_000101_220426_220131.bpc'

                          '$KERNELS/fk/bc_mpo_v31.tf'
                          '$KERNELS/fk/bc_mtm_v10.tf'
                          '$KERNELS/fk/bc_mmo_v10.tf'
                          '$KERNELS/fk/bc_sci_v11.tf'
                          '$KERNELS/fk/bc_dsk_surfaces_v02.tf'
                          '$KERNELS/fk/rssd0002.tf'
                          '$KERNELS/fk/earth_topo_201023.tf'
                          '$KERNELS/fk/estrack_v04.tf'

                          '$KERNELS/ik/bc_mpo_bela_v07.ti'
                          '$KERNELS/ik/bc_mpo_mertis_v08.ti'
                          '$KERNELS/ik/bc_mpo_mgns_v02.ti'
                          '$KERNELS/ik/bc_mpo_mixs_v05.ti'
                          '$KERNELS/ik/bc_mpo_phebus_v06.ti'
                          '$KERNELS/ik/bc_mpo_serena_v07.ti'
                          '$KERNELS/ik/bc_mpo_simbio-sys_v08.ti'
                          '$KERNELS/ik/bc_mpo_sixs_v08.ti'
                          '$KERNELS/ik/bc_mpo_str_v02.ti'
                          '$KERNELS/ik/bc_mpo_aux_v01.ti'
                          '$KERNELS/ik/bc_mtm_mcam_v05.ti'
                          '$KERNELS/ik/bc_mmo_mppe_v03.ti'
                          '$KERNELS/ik/bc_mmo_msasi_v03.ti'

                          '$KERNELS/sclk/bc_mpo_fict_20181127.tsc'
                          '$KERNELS/sclk/bc_mpo_step_20220125.tsc'
                          '$KERNELS/sclk/bc_mmo_fict_20170228.tsc'

                          '$KERNELS/spk/de432s.bsp'
                          '$KERNELS/spk/earthstns_itrf93_201023.bsp'
                          '$KERNELS/spk/estrack_v04.bsp'
                          '$KERNELS/spk/bc_sci_v02.bsp'
                          '$KERNELS/spk/bc_mmo_struct_v01.bsp'
                          '$KERNELS/spk/bc_mmo_cruise_v01.bsp'
                          '$KERNELS/spk/bc_mtm_struct_v06.bsp'
                          '$KERNELS/spk/bc_mtm_cruise_v01.bsp'
                          '$KERNELS/spk/bc_mpo_cog_v03.bsp'
                          '$KERNELS/spk/bc_mpo_cog_00117_20181118_20211211_v01.bsp'
                          '$KERNELS/spk/bc_mpo_struct_v07.bsp'
                          '$KERNELS/spk/bc_mpo_prelaunch_v01.bsp'
                          '$KERNELS/spk/bc_mpo_fcp_00117_20181020_20251101_v01.bsp'

                          '$KERNELS/ck/bc_mpo_magboom_v01.bc'
                          '$KERNELS/ck/bc_mpo_hga_scm_20181020_20190101_s20201020_v02.bc'
                          '$KERNELS/ck/bc_mpo_hga_scm_20190101_20200101_s20201020_v02.bc'
                          '$KERNELS/ck/bc_mpo_hga_scm_20200101_20210101_s20210618_v01.bc'
                          '$KERNELS/ck/bc_mpo_hga_scm_20210101_20220101_s20220106_v01.bc'
                          '$KERNELS/ck/bc_mpo_mga_scm_20181020_20190101_s20200109_v02.bc'
                          '$KERNELS/ck/bc_mpo_mga_scm_20190101_20200101_s20200109_v02.bc'
                          '$KERNELS/ck/bc_mpo_mga_scm_20200101_20210101_s20210618_v01.bc'
                          '$KERNELS/ck/bc_mpo_mga_scm_20210101_20220101_s20220106_v01.bc'
                          '$KERNELS/ck/bc_mpo_sa_scm_20181020_20190101_s20211202_v01.bc'
                          '$KERNELS/ck/bc_mpo_sa_scm_20190101_20200101_s20211202_v01.bc'
                          '$KERNELS/ck/bc_mpo_sa_scm_20200101_20210101_s20211202_v01.bc'
                          '$KERNELS/ck/bc_mpo_sa_scm_20210101_20220101_s20220106_v01.bc'
                          '$KERNELS/ck/bc_mtm_sa_scm_20181020_20190101_s20200109_v02.bc'
                          '$KERNELS/ck/bc_mtm_sa_scm_20190101_20200101_s20200109_v02.bc'
                          '$KERNELS/ck/bc_mtm_sa_scm_20200101_20210101_s20210618_v01.bc'
                          '$KERNELS/ck/bc_mtm_sa_scm_20210101_20220101_s20220106_v01.bc'
                          '$KERNELS/ck/bc_mmo_sc_cruise_v01.bc'
                          '$KERNELS/ck/bc_mtm_sc_cruise_v01.bc'
                          '$KERNELS/ck/bc_mtm_sep_scp_20181019_20251205_f20181127_v02.bc'
                          '$KERNELS/ck/bc_mpo_sc_prelaunch_v01.bc'
                          '$KERNELS/ck/bc_mpo_sc_fcp_00117_20181020_20220228_f20181127_v01.bc'
                          '$KERNELS/ck/bc_mpo_sc_scm_20181020_20190101_s20200109_v01.bc'
                          '$KERNELS/ck/bc_mpo_sc_scm_20190101_20200101_s20200109_v01.bc'
                          '$KERNELS/ck/bc_mpo_sc_scm_20200101_20210101_s20210618_v01.bc'
                          '$KERNELS/ck/bc_mpo_sc_scm_20210101_20220101_s20220106_v01.bc'

                         )

   \begintext


Contact Information
-------------------------------------------------------------------------------

   If you have any questions regarding this file contact the
   ESA SPICE Service at ESAC:

           Alfredo Escalante Lopez
           (+34) 91 813 14 29
           spice@sciops.esa.int

   or NAIF at JPL:

           Boris Semenov
           +1 (818) 354-8136
           Boris.Semenov@jpl.nasa.gov


End of MK file.
