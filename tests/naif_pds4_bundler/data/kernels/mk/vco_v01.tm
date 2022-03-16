KPL/MK

   This meta-kernel lists the Venus Climate Orbiter (VCO, also known as
   PLANET-C and AKATSUKI) SPICE kernels providing coverage from launch
   until the end time of the last Venus Climate Orbiter orbit SPK kernel. 
   All of the kernels listed below are archived in the Venus Climate 
   Orbiter SPICE data set (DATA_SET_ID = "VCO-V-SPICE-6-V1.0"). This set 
   of files and the order in which they are listed were picked to provide 
   the best available data and the most complete coverage based on the
   information about the kernels available at the time this meta-kernel
   was made. For detailed information about the kernels listed below
   refer to the internal comments included in the kernels and the
   documentation accompanying the Venus Climate Orbiter SPICE data set.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the Venus Climate Orbiter SPICE data set's ``data''
   directory on their system. Converting line terminators to the format
   native to the user's system may also be required if this meta-kernel
   is to be used on a non-UNIX workstation.

   This file was created on 2017-05-25 by Shin-ya Murakami, ISAS/JAXA,
   using vco_mk_meta_kernel.plx originally written by Manabu Yamada,
   PERC/Chiba Institute of Technology.

   The original name of this file was vco_v01.tm.

\begindata

PATH_VALUES = ( 
  './data'
)

PATH_SYMBOLS = ( 
  'KERNELS'
)

KERNELS_TO_LOAD = ( 
  '$KERNELS/lsk/naif0012.tls',
  '$KERNELS/pck/pck00010.tpc',
  '$KERNELS/pck/vco_gm_de431_v01.tpc',
  '$KERNELS/spk/vco_de423_de430.bsp',
  '$KERNELS/fk/rssd0002.tf',
  '$KERNELS/fk/vco_spacecraft_v26.tf',
  '$KERNELS/ik/vco_uvi_v12.ti',
  '$KERNELS/ik/vco_ir1_v11.ti',
  '$KERNELS/ik/vco_ir2_v10.ti',
  '$KERNELS/ik/vco_lac_v13.ti',
  '$KERNELS/ik/vco_lir_v08.ti',
  '$KERNELS/sclk/vco_v01.tsc',
  '$KERNELS/spk/vco_2010_v01.bsp',
  '$KERNELS/spk/vco_2011_v01.bsp',
  '$KERNELS/spk/vco_2012_v01.bsp',
  '$KERNELS/spk/vco_2013_v01.bsp',
  '$KERNELS/spk/vco_2014_v01.bsp',
  '$KERNELS/spk/vco_2015_v01.bsp',
  '$KERNELS/spk/vco_2016_v01.bsp',
  '$KERNELS/ck/vco_2010_pred_v02.bc',
  '$KERNELS/ck/vco_2010_v02.bc',
  '$KERNELS/ck/vco_2011_pred_v02.bc',
  '$KERNELS/ck/vco_2011_v02.bc',
  '$KERNELS/ck/vco_2012_v02.bc',
  '$KERNELS/ck/vco_2013_v02.bc',
  '$KERNELS/ck/vco_2014_pred_v02.bc',
  '$KERNELS/ck/vco_2014_v02.bc',
  '$KERNELS/ck/vco_2015_pred_v02.bc',
  '$KERNELS/ck/vco_2015_v02.bc',
  '$KERNELS/ck/vco_2016_pred_v02.bc',
  '$KERNELS/ck/vco_2016_v02.bc',
  '$KERNELS/ck/vco_sap_nominal_v01.bc',
  '$KERNELS/ck/vco_sap_2010_v02.bc',
  '$KERNELS/ck/vco_sap_2011_v02.bc',
  '$KERNELS/ck/vco_sap_2012_v02.bc',
  '$KERNELS/ck/vco_sap_2013_v02.bc',
  '$KERNELS/ck/vco_sap_2014_v02.bc',
  '$KERNELS/ck/vco_sap_2015_v02.bc',
  '$KERNELS/ck/vco_sap_2016_v02.bc',
  '$KERNELS/ck/vco_xmga_2010_v01.bc',
  '$KERNELS/ck/vco_xmga_2011_v01.bc',
  '$KERNELS/ck/vco_xmga_2012_v01.bc',
  '$KERNELS/ck/vco_xmga_2013_v01.bc',
  '$KERNELS/ck/vco_xmga_2014_v01.bc',
  '$KERNELS/ck/vco_xmga_2015_v01.bc',
  '$KERNELS/ck/vco_xmga_2016_v01.bc'
)

\begintext

EOF
