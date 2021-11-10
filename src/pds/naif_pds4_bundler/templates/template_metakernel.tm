KPL/MK

$DESCRIPTION
   It is recommended that users make a local copy of this file and
   modify the value of the PATH_VALUES keyword to point to the actual
   location of the $SPICE_NAME SPICE kernel archives' ``spice_kernels''
   directory on their system. Replacing ``/'' with ``\'' and converting
   line terminators to the format native to the user's system may also
   be required if this meta-kernel is to be used on a non-UNIX
   workstation.

   This file was created on $MK_CREATION_DATE by $AUTHOR, $INSTITUTION.
   The original name of this file was $FILE_NAME.

   \begindata

      PATH_VALUES     = ( '$KERNELPATH'      )

      PATH_SYMBOLS    = ( 'KERNELS' )

      KERNELS_TO_LOAD = (

$KERNELS_IN_METAKERNEL
                        )
$DATA
   \begintext

End of MK file.
