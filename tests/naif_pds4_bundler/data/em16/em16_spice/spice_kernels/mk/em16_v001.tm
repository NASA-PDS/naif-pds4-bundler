KPL/MK

Meta-kernel for ExoMars 2016 Archived Kernels
==========================================================================

   This meta-kernel lists the ExoMars 2016 Archived SPICE kernels
   providing information for the full mission. All of the kernels listed
   below are archived in the PSA ExoMars 2016 SPICE kernel archive.

   This set of files and the order in which they are listed were picked to
   provide the best available data and the most complete coverage for the
   specified year based on the information about the kernels available at
   the time this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the ExoMars 2016
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
   location of the ExoMars 2016 SPICE data set's ``data'' directory
   on their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.


-------------------

   This file was created on 2019-08-08 by Marc Costa Sitja ESA/ESAC.
   The original name of this file was em16_v001.tm.


   \begindata

     PATH_VALUES       = ( '..' )

     PATH_SYMBOLS      = ( 'KERNELS' )

     KERNELS_TO_LOAD   = (

'$KERNELS/ck/em16_tgo_hga_scm_20160315_20161101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_hga_spm_20161101_20170301_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_hga_sam_20170301_20180312_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_hga_ssm_20180311_20190101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_hga_ssm_20190101_20190519_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sa_scm_20160315_20161101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sa_spm_20161101_20170301_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sa_sam_20170301_20180312_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sa_ssm_20180311_20190101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sa_ssm_20190101_20190519_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_fpp_014_01_20160314_20170315_s20170201_v01.bc'
'$KERNELS/ck/em16_tgo_sc_fsp_080_01_20180222_20190720_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_scm_20160315_20161101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_spm_20161101_20170301_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_sam_20170301_20180312_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_ssm_20180311_20190101_s20190703_v01.bc'
'$KERNELS/ck/em16_tgo_sc_ssm_20190101_20190519_s20190703_v01.bc'

'$KERNELS/fk/em16_tgo_v18.tf'
'$KERNELS/fk/em16_tgo_ops_v02.tf'
'$KERNELS/fk/rssd0002.tf'
'$KERNELS/fk/earth_topo_050714.tf'
'$KERNELS/fk/earthfixediau.tf'
'$KERNELS/fk/estrack_v01.tf'
'$KERNELS/fk/new_norcia_topo.tf'

'$KERNELS/ik/em16_tgo_acs_v06.ti'
'$KERNELS/ik/em16_tgo_cassis_v07.ti'
'$KERNELS/ik/em16_tgo_frend_v05.ti'
'$KERNELS/ik/em16_tgo_nomad_v04.ti'
'$KERNELS/ik/em16_tgo_str_v03.ti'

'$KERNELS/lsk/naif0012.tls'

'$KERNELS/pck/pck00010.tpc'
'$KERNELS/pck/de-403-masses.tpc'

'$KERNELS/pck/earth_000101_190812_190521.bpc'

'$KERNELS/sclk/em16_tgo_step_20190703.tsc'

'$KERNELS/spk/em16_tgo_struct_v01.bsp'
'$KERNELS/spk/em16_tgo_cog_v01.bsp'
'$KERNELS/spk/em16_tgo_fsp_048_01_20160314_20181231_v02.bsp'
'$KERNELS/spk/em16_tgo_fsp_065_01_20181120_20190429_v02.bsp'
'$KERNELS/spk/em16_tgo_fsp_080_01_20190305_20190817_v02.bsp'
'$KERNELS/spk/de432s.bsp'
'$KERNELS/spk/mar097_20160314_20300101.bsp'
'$KERNELS/spk/new_norcia.bsp'
'$KERNELS/spk/estrack_v01.bsp'

                         )

   \begintext


Contact Information
------------------------------------------------------------------------

   If you have any questions regarding this file contact the
   ESA SPICE Service at ESAC:

           Marc Costa Sitja
           (+34) 91-8131-457
           marc.costa@esa.int, esa_spice@sciops.esa.int


   or NAIF at JPL:

           Boris Semenov
           +1 (818) 354-8136
           Boris.Semenov@jpl.nasa.gov


End of MK file.
