KPL/MK

   This meta-kernel lists the PHOENIX SPICE kernels providing coverage
   for the whole mission. All of the kernels listed below are archived
   in the PDS PHOENIX SPICE kernel archive. This set of files and the
   order in which they are listed were picked to provide the best
   available data and the most complete coverage based on the information
   about the kernels available at the time this meta-kernel was made.
   For detailed information about the kernels listed below refer to the
   internal comments included in the kernels and the documentation
   accompanying the PHOENIX SPICE kernel archive.

   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the PHOENIX SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on May 25, 2021 by Marc Costa Sitja, NAIF/JPL.
   The original name of this file was phoenix_v01.tm.

   \begindata

      PATH_VALUES       = ( '..'      )

      PATH_SYMBOLS      = ( 'KERNELS' )

      KERNELS_TO_LOAD   = (

                          '$KERNELS/lsk/naif0009.tls'

                          '$KERNELS/pck/mars_iau2000_v0.tpc'

                          '$KERNELS/fk/phx_v06.tf'

                          '$KERNELS/ik/phx_ssi_right_20080415.ti'
                          '$KERNELS/ik/phx_rac_20080415.ti'
                          '$KERNELS/ik/phx_ssi_left_20080415.ti'

                          '$KERNELS/sclk/pxh_sclkscet_00010.tsc'
                          '$KERNELS/sclk/phx_lmst_ops080525_v1.tsc'

                          '$KERNELS/spk/de410s.bsp'
                          '$KERNELS/spk/mar033-7.bsp'
                          '$KERNELS/spk/phx_struct_v10.bsp'
                          '$KERNELS/spk/phx_cruise.bsp'
                          '$KERNELS/spk/phx_edl_rec_traj.bsp'
                          '$KERNELS/spk/phx_ls_to_lander_v1.bsp'
                          '$KERNELS/spk/phx_ls_ops080526_iau2000_v1.bsp'

                          '$KERNELS/ck/phx_cruise_sc.bc'
                          '$KERNELS/ck/phx_edl_rec_att.bc'
                          '$KERNELS/ck/phx_surf_frmp.bc'
                          '$KERNELS/ck/phx_surf_ll2p.bc'

                          '$KERNELS/ck/phx_surf_ra.bc'
                          '$KERNELS/ck/phx_surf_rac.bc'
                          '$KERNELS/ck/phx_surf_rag.bc'
                          '$KERNELS/ck/phx_surf_ssil.bc'
                          '$KERNELS/ck/phx_surf_ssir.bc'

                          )

   \begintext

End of MK file.
