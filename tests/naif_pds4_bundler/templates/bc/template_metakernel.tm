KPL/MK

Meta-kernel for $MISSION_NAME Archived Kernels
==========================================================================

   This meta-kernel lists the $MISSION_NAME Archived SPICE kernels
   providing information for the full mission. All of the kernels listed
   below are archived in the PSA $MISSION_NAME SPICE kernel archive.

   This set of files and the order in which they are listed were picked to
   provide the best available data and the most complete coverage for the
   specified year based on the information about the kernels available at
   the time this meta-kernel was made. For detailed information about the
   kernels listed below refer to the internal comments included in the
   kernels and the documentation accompanying the $MISSION_NAME
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
   location of the $MISSION_NAME SPICE data set's ``data'' directory
   on their system. Replacing ``/'' with ``\'' and converting line
   terminators to the format native to the user's system may also be
   required if this meta-kernel is to be used on a non-UNIX workstation.


-------------------

   This file was created on $MK_CREATION_DATE by $AUTHOR $INSTITUTION.
   The original name of this file was $FILE_NAME.


   \begindata

     PATH_VALUES       = ( '$KERNELPATH' )

     PATH_SYMBOLS      = ( 'KERNELS' )

     KERNELS_TO_LOAD   = (

$KERNELS_IN_METAKERNEL
                         )

   \begintext


Contact Information
------------------------------------------------------------------------

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
