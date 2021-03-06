DAFETF NAIF DAF ENCODED TRANSFER FILE
'DAF/CK  '
'2'
'6'
'INSIGHT IDA Encoder-based Orientation                       '
BEGIN_ARRAY 1 19
'INSIGHT IDA Orientation, Encoder-based  '
'2737F6CE9478^C'
'273820FE915E^C'
'-2E2C1'
'-2E2AC'
'3'
'1'
19
'F173A407F68C2^0'
'0^0'
'0^0'
'5512299D222714^0'
'0^0'
'0^0'
'0^0'
'F173A407F68C2^0'
'0^0'
'0^0'
'5512299D222714^0'
'0^0'
'0^0'
'0^0'
'2737F6CE9478^C'
'273820FE915E^C'
'2737F6CE9478^C'
'1^1'
'2^1'
END_ARRAY 1 19
BEGIN_ARRAY 2 19
'INSIGHT IDA Orientation, Encoder-based  '
'2737F6CE9478^C'
'273820FE915E^C'
'-2E2C2'
'-2E2C1'
'3'
'1'
19
'AF33B2A21C598^0'
'-AF33B2A21C597^0'
'-2D85B4A0C5B24A^0'
'2D85B4A0C5B24C^0'
'7A1B0432573B44^-12'
'-6444AD13374D2^-8'
'-181199EA5F43AE^-12'
'AF33B53BCEF008^0'
'-AF33B53BCEF^0'
'-2D85AA9EB150D4^0'
'2D85AA9EB150D4^0'
'7838C07672F948^-12'
'-62B8A8CAD7E2EC^-8'
'-17B28A3A6B0D04^-12'
'2737F6CE9478^C'
'273820FE915E^C'
'2737F6CE9478^C'
'1^1'
'2^1'
END_ARRAY 2 19
BEGIN_ARRAY 3 19
'INSIGHT IDA Orientation, Encoder-based  '
'2737F6CE9478^C'
'273820FE915E^C'
'-2E2C3'
'-2E2C2'
'3'
'1'
19
'C0449CBC37D7B^0'
'0^0'
'0^0'
'-A90610F0459B08^0'
'0^0'
'0^0'
'0^0'
'C0449CBC37D7B^0'
'0^0'
'0^0'
'-A90610F0459B08^0'
'0^0'
'0^0'
'0^0'
'2737F6CE9478^C'
'273820FE915E^C'
'2737F6CE9478^C'
'1^1'
'2^1'
END_ARRAY 3 19
BEGIN_ARRAY 4 19
'INSIGHT IDA Orientation, Encoder-based  '
'2737F6CE9478^C'
'273820FE915E^C'
'-2E2C4'
'-2E2C3'
'3'
'1'
19
'FF9D9EFA6C383^0'
'0^0'
'0^0'
'-E059358270C8F^-1'
'0^0'
'0^0'
'0^0'
'FF9D9EFA6C383^0'
'0^0'
'0^0'
'-E059358270C8F^-1'
'0^0'
'0^0'
'0^0'
'2737F6CE9478^C'
'273820FE915E^C'
'2737F6CE9478^C'
'1^1'
'2^1'
END_ARRAY 4 19
BEGIN_ARRAY 5 19
'INSIGHT IDA Orientation, Encoder-based  '
'2737F6CE9478^C'
'273820FE915E^C'
'-2E2CB'
'-2E2C3'
'3'
'1'
19
'8^0'
'-8^0'
'-8^0'
'-8^0'
'0^0'
'0^0'
'0^0'
'8^0'
'-8^0'
'-8^0'
'-8^0'
'0^0'
'0^0'
'0^0'
'2737F6CE9478^C'
'273820FE915E^C'
'2737F6CE9478^C'
'1^1'
'2^1'
END_ARRAY 5 19
TOTAL_ARRAYS 5
 ~NAIF/SPC BEGIN COMMENTS~

********************************************************************************

 This CK file was created using CKSLICER Utility Ver. 1.3.0, October 28, 2011
 linked against SPICE Toolkit Ver. N0066.

 This file contains a subset of the pointing data between:
       UTC 2020 NOV 07 00:00:00.000
 and
       UTC 2020 NOV 07 03:00:00.000
 for all applicable segments from the source CK file:
       ../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc

 LSK file:
       ../data/kernels/lsk/naif0012.tls
 and SCLK file(s):
       ../data/kernels/sclk/nsy_sclkscet_00018.tsc
 were used by CKSLICER to support required time conversions.

 This file was created on 2021-07-08 16:20:59.

 Text below is the contents of the comment area of the source CK file.

********************************************************************************




********************************************************************************


INSIGHT IDA Encoder-based Orientation CK
===============================================================================

   This CK file contains encoder-based INSIGHT IDA orientation.
   This orientation is "broken down" into five separate segments, four
   providing rotations IDA joints and the fifth providing the fixed
   orientation of the IDA camera reference point frame with respect to
   the IDA elbow frame.


Pedigree
--------------------------------------------------------

   This file has been generated by ``nsyt_idd_ang2ck.pl'' script,
   (Ver. 1.0.0 -- January 3, 2019 -- BVS/NAIF.) that ran the
   MSOPCK program to make segments CK containing IDA joint orientations.


Version and Date
--------------------------------------------------------

   Version 1.0 -- Tue Mar  9 10:28:20 PST 2021


References
--------------------------------------------------------

   1. INSIGHT Frames Kernel, latest version

   2. Final DH parameters in use by the FSW; e-mail from Khaled Ali;
      December 16, 2017

   3. IDA FSW parameters used to point IDC; e-mail from Khaled Ali;
      July 31, 2018


Contact Information
--------------------------------------------------------

   If you have any questions regarding this CK file, contact:

      Boris Semenov, NAIF, x4-8136, Boris.Semenov@jpl.nasa.gov


Appendix 1: MSOPCK Setup Files and Segment Coverage Information
--------------------------------------------------------


********************************************************************************
MSOPCK SETUP FILE: insight_ida_enc_200829_201220_v1.bc.msopck.setup
********************************************************************************


   \begindata

      LSK_FILE_NAME           = '/ftp/pub/naif/INSIGHT/kernels/lsk/naif0012.tls'
      SCLK_FILE_NAME          = '/ftp/pub/naif/INSIGHT/kernels/sclk/NSY_SCLKSCET.00019.tsc'
      FRAMES_FILE_NAME        = '/home/bsemenov/insight/data/fk/insight_v05.tf'

      INTERNAL_FILE_NAME      = 'INSIGHT IDA Encoder-based Orientation'

      CK_TYPE                 = 3
      CK_SEGMENT_ID           = 'INSIGHT IDA Orientation, Encoder-based'
      INSTRUMENT_ID           = -189121
      REFERENCE_FRAME_NAME    = 'INSIGHT_PAYLOAD'
      ANGULAR_RATE_PRESENT    = 'MAKE UP/NO AVERAGING'

      MAXIMUM_VALID_INTERVAL  = 8640000

      INPUT_TIME_TYPE         = 'DSCLK'
      INPUT_DATA_TYPE         = 'EULER ANGLES'
      EULER_ANGLE_UNITS       = 'RADIANS'
      EULER_ROTATIONS_ORDER   = ( 'Z' 'X' 'Y' )

      PRODUCER_ID             = 'NAIF/JPL'

   \begintext

   \begindata

      COMMENTS_FILE_NAME      = 'insight_ida_enc_200829_201220_v1.bc.msopck.comments'

      INCLUDE_INTERVAL_TABLE  = 'NO'

   \begintext


********************************************************************************
RUN-TIME OBTAINED META INFORMATION:
********************************************************************************

PRODUCT_CREATION_TIME = 2021-03-09T10:28:21
START_TIME            = 2020-08-29T21:22:33.165
STOP_TIME             = 2020-12-20T01:09:37.544

********************************************************************************


********************************************************************************
MSOPCK SETUP FILE: insight_ida_enc_200829_201220_v1.bc.msopck.setup
********************************************************************************


   \begindata

      LSK_FILE_NAME           = '/ftp/pub/naif/INSIGHT/kernels/lsk/naif0012.tls'
      SCLK_FILE_NAME          = '/ftp/pub/naif/INSIGHT/kernels/sclk/NSY_SCLKSCET.00019.tsc'
      FRAMES_FILE_NAME        = '/home/bsemenov/insight/data/fk/insight_v05.tf'

      INTERNAL_FILE_NAME      = 'INSIGHT IDA Encoder-based Orientation'

      CK_TYPE                 = 3
      CK_SEGMENT_ID           = 'INSIGHT IDA Orientation, Encoder-based'
      INSTRUMENT_ID           = -189122
      REFERENCE_FRAME_NAME    = 'INSIGHT_IDA_SHOULDER_AZ'
      ANGULAR_RATE_PRESENT    = 'MAKE UP/NO AVERAGING'

      MAXIMUM_VALID_INTERVAL  = 8640000

      INPUT_TIME_TYPE         = 'DSCLK'
      INPUT_DATA_TYPE         = 'EULER ANGLES'
      EULER_ANGLE_UNITS       = 'RADIANS'
      EULER_ROTATIONS_ORDER   = ( 'Z' 'X' 'Y' )

      PRODUCER_ID             = 'NAIF/JPL'

   \begintext

   The offsets are from [2].

   \begindata

      OFFSET_ROTATION_ANGLES  = ( 0.0   0.0   90.0 )
      OFFSET_ROTATION_AXES    = ( 'Y'   'Z'    'X' )
      OFFSET_ROTATION_UNITS   = 'DEGREES'

      INCLUDE_INTERVAL_TABLE  = 'NO'

   \begintext


********************************************************************************
RUN-TIME OBTAINED META INFORMATION:
********************************************************************************

PRODUCT_CREATION_TIME = 2021-03-09T10:28:21
START_TIME            = 2020-08-29T21:22:33.165
STOP_TIME             = 2020-12-20T01:09:37.544

********************************************************************************


********************************************************************************
MSOPCK SETUP FILE: insight_ida_enc_200829_201220_v1.bc.msopck.setup
********************************************************************************


   \begindata

      LSK_FILE_NAME           = '/ftp/pub/naif/INSIGHT/kernels/lsk/naif0012.tls'
      SCLK_FILE_NAME          = '/ftp/pub/naif/INSIGHT/kernels/sclk/NSY_SCLKSCET.00019.tsc'
      FRAMES_FILE_NAME        = '/home/bsemenov/insight/data/fk/insight_v05.tf'

      INTERNAL_FILE_NAME      = 'INSIGHT IDA Encoder-based Orientation'

      CK_TYPE                 = 3
      CK_SEGMENT_ID           = 'INSIGHT IDA Orientation, Encoder-based'
      INSTRUMENT_ID           = -189123
      REFERENCE_FRAME_NAME    = 'INSIGHT_IDA_SHOULDER_EL'
      ANGULAR_RATE_PRESENT    = 'MAKE UP/NO AVERAGING'

      MAXIMUM_VALID_INTERVAL  = 8640000

      INPUT_TIME_TYPE         = 'DSCLK'
      INPUT_DATA_TYPE         = 'EULER ANGLES'
      EULER_ANGLE_UNITS       = 'RADIANS'
      EULER_ROTATIONS_ORDER   = ( 'Z' 'X' 'Y' )

      PRODUCER_ID             = 'NAIF/JPL'

   \begintext

   The offsets are from [2].

   \begindata

      OFFSET_ROTATION_ANGLES  = ( 0.0   0.0   0.0 )
      OFFSET_ROTATION_AXES    = ( 'Y'   'Z'   'X' )
      OFFSET_ROTATION_UNITS   = 'DEGREES'

      INCLUDE_INTERVAL_TABLE  = 'NO'

   \begintext


********************************************************************************
RUN-TIME OBTAINED META INFORMATION:
********************************************************************************

PRODUCT_CREATION_TIME = 2021-03-09T10:28:22
START_TIME            = 2020-08-29T21:22:33.165
STOP_TIME             = 2020-12-20T01:09:37.544

********************************************************************************


********************************************************************************
MSOPCK SETUP FILE: insight_ida_enc_200829_201220_v1.bc.msopck.setup
********************************************************************************


   \begindata

      LSK_FILE_NAME           = '/ftp/pub/naif/INSIGHT/kernels/lsk/naif0012.tls'
      SCLK_FILE_NAME          = '/ftp/pub/naif/INSIGHT/kernels/sclk/NSY_SCLKSCET.00019.tsc'
      FRAMES_FILE_NAME        = '/home/bsemenov/insight/data/fk/insight_v05.tf'

      INTERNAL_FILE_NAME      = 'INSIGHT IDA Encoder-based Orientation'

      CK_TYPE                 = 3
      CK_SEGMENT_ID           = 'INSIGHT IDA Orientation, Encoder-based'
      INSTRUMENT_ID           = -189124
      REFERENCE_FRAME_NAME    = 'INSIGHT_IDA_ELBOW'
      ANGULAR_RATE_PRESENT    = 'MAKE UP/NO AVERAGING'

      MAXIMUM_VALID_INTERVAL  = 8640000

      INPUT_TIME_TYPE         = 'DSCLK'
      INPUT_DATA_TYPE         = 'EULER ANGLES'
      EULER_ANGLE_UNITS       = 'RADIANS'
      EULER_ROTATIONS_ORDER   = ( 'Z' 'X' 'Y' )

      PRODUCER_ID             = 'NAIF/JPL'

   \begintext

   The offsets are from [2].

   \begindata

      OFFSET_ROTATION_ANGLES  = ( 0.0   0.0   0.0 )
      OFFSET_ROTATION_AXES    = ( 'Y'   'Z'   'X' )
      OFFSET_ROTATION_UNITS   = 'DEGREES'

      INCLUDE_INTERVAL_TABLE  = 'NO'

   \begintext


********************************************************************************
RUN-TIME OBTAINED META INFORMATION:
********************************************************************************

PRODUCT_CREATION_TIME = 2021-03-09T10:28:22
START_TIME            = 2020-08-29T21:22:33.165
STOP_TIME             = 2020-12-20T01:09:37.544

********************************************************************************


********************************************************************************
MSOPCK SETUP FILE: insight_ida_enc_200829_201220_v1.bc.msopck.setup
********************************************************************************


   \begindata

      LSK_FILE_NAME           = '/ftp/pub/naif/INSIGHT/kernels/lsk/naif0012.tls'
      SCLK_FILE_NAME          = '/ftp/pub/naif/INSIGHT/kernels/sclk/NSY_SCLKSCET.00019.tsc'
      FRAMES_FILE_NAME        = '/home/bsemenov/insight/data/fk/insight_v05.tf'

      INTERNAL_FILE_NAME      = 'INSIGHT IDA Encoder-based Orientation'

      CK_TYPE                 = 3
      CK_SEGMENT_ID           = 'INSIGHT IDA Orientation, Encoder-based'
      INSTRUMENT_ID           = -189131
      REFERENCE_FRAME_NAME    = 'INSIGHT_IDA_ELBOW'
      ANGULAR_RATE_PRESENT    = 'MAKE UP/NO AVERAGING'

      MAXIMUM_VALID_INTERVAL  = 8640000

      INPUT_TIME_TYPE         = 'DSCLK'
      INPUT_DATA_TYPE         = 'EULER ANGLES'
      EULER_ANGLE_UNITS       = 'RADIANS'
      EULER_ROTATIONS_ORDER   = ( 'Z' 'X' 'Y' )

      PRODUCER_ID             = 'NAIF/JPL'

   \begintext

   The offsets are from [3].

   \begindata

      OFFSET_ROTATION_ANGLES  = ( 90.0  0.0  90.0 )
      OFFSET_ROTATION_AXES    = (  'Y'  'Z'   'X' )
      OFFSET_ROTATION_UNITS   = 'DEGREES'

   \begintext


********************************************************************************
RUN-TIME OBTAINED META INFORMATION:
********************************************************************************

PRODUCT_CREATION_TIME = 2021-03-09T10:28:22
START_TIME            = 2020-08-29T21:22:33.165
STOP_TIME             = 2020-12-20T01:09:37.544

********************************************************************************
INTERPOLATION INTERVALS IN THE FILE SEGMENTS:
********************************************************************************

SEG.SUMMARY: ID -189131, COVERG: 2020-08-29T21:22:33.165 2020-12-20T01:09:37.544
--------------------------------------------------------------------------------
      2020-08-29T21:22:33.165    2020-12-20T01:09:37.544


********************************************************************************


********************************************************************************
 ~NAIF/SPC END COMMENTS~
