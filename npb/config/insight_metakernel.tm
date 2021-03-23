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

   This file was created on $CURRENT_DATE by #AUTHOR, NAIF/JPL.
   The original name of this file was $FILE_NAME.

   \begindata

      PATH_VALUES       = ( '$KERNELPATH'      )

      PATH_SYMBOLS      = ( 'KERNELS' )

      KERNELS_TO_LOAD   = (

$KERNELS_IN_METAKERNEL

                          )

      SPACECRAFT_ID     = -189
      CENTER_ID         = 499
      LANDING_TIME      = '2018-11-26T19:44:52.444'
      LANDING_SOL_INDEX = 0
      BODY10_GM         = 1.3271244004193938E+11

   \begintext

End of MK file.