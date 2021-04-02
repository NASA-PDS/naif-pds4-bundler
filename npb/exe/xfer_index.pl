#!/usr/bin/perl
#
# This script generates a volume index table (index.tab) and PDS-D
# index table (dsindex.tab) and corresponding labels (index.lbl and
# dsindex.lbl) containing entries for all SPICE kernels listed in a
# kernel list file (usually a complete kernel list file including all
# releases) provided as a sole argument on the command line. Labels for
# all kernels included in the kernel list must be generated prior to
# running this script and and must reside next to the kernels.
#
# For more information and examples, refer to the SPICE Archiving
# Guide.
#

$scriptname  = "xfer_index.pl";
$version     = "Version 3.0.0 -- MCS/NAIF, April 1, 2021";

#
#  Version 3.0.0 -- April 1, 2021 -- MCS/NAIF
#
#     Script is now able to generate the index with PDS4 labels.
#     DATASETID can be extracted from the kernel list. It can still
#     be extracted from the PDS3 label.
#
#     Enforced lower case for VOLUMEID (against the PDS3 standard but
#     used for all peer-reviwed SPICE PDS3 data sets). Only for PDS3
#     archive indexes.
#
#     Sorting list of INDEXED_FILE_NAME extensions to avoid random
#     order.
#
#  Version 2.7.0 -- May 16, 2019 -- BVS/NAIF
#
#     Updated to recognize DSKs.
#
#  Version 2.6.0 -- May 24, 2015 -- BVS/NAIF
#
#     Updated to ignore MKs is they are present in the list.
#
#  Version 2.5.0 -- December 31, 2008 -- BVS/NAIF
#
#     Updated to handle labels with or without CRs and extraneous line
#     padding. Added brief usage text.
#
#  Version 2.4.0 -- January 26, 2006 -- BVS/NAIF
#
#     Script now makes two pairs of files: dsindex.tab/dsindex.lbl
#     and index.tab/index.lbl. dsindex.tab and index.tab are identical.
#     dsindex.lbl and index.lbl differ by only one line -- the line
#     specifying the index table file name:
#
#        ^INDEX_TABLE               = "DSINDEX.TAB"
#
#     vs.
#
#        ^INDEX_TABLE               = "INDEX.TAB"
#
#
#  Version 2.3.0 -- June 30, 2005 -- LSE/NAIF
#
#     Updated to handle Cassini DATA_SET_ID (CO-S/J/E/V-SPICE-6-V1.0)
#
#  Version 2.2.0 -- April 6, 2005 -- LSE/NAIF
#
#     Updated .lbl file to contain FORMAT keyword.
#
#     This script is a descendant of the script make_index.pl. It
#     relaxes the requirement that a particular kernel file actually
#     exist. See the earlier script for more details.       LSE
#     10/24/02
#
#  Version 1.0.0 -- October 24, 2002 -- LSE/NAIF
#

$PDS         = 3;                        # Default to a PDS3 archvie index

$indexfile   = "dsindex.tab";            # LSE
$indexlabel  = "dsindex.lbl";            # LSE

$indexfile2  = "index.tab";
$indexlabel2 = "index.lbl";

#
#  Display version.
#
print "\nScript that creates an index table file (and a label file for ".
      "it)\nfor a collection of SPICE kernels listed in a text file.\n\n".
      "$version.\n";

#
#
#  Get from the command line the name of the file containing list
#  of labeled kernels and other meta-keywords.
#
if ( @ARGV == 1 ) {
   $filelist = shift @ARGV;
   if ( ! -e $filelist ) {
      die "\nERROR:$scriptname: the file '$filelist' doesn't exist.\n\n";
   }
} else {
   die "\nUsage: > $scriptname <complete_kernel_list_file_name>\n\n";
}

#
#  Check whether dsindex.tab and dsindex.LBL already exist.
#
if ( -e $indexfile ) {
   die "\nERROR:$scriptname: index table file '$indexfile' already exists.\n\n";
}
if ( -e $indexlabel ) {
   die "\nERROR:$scriptname: index label file '$indexlabel' already exists.\n\n";
}
if ( -e $indexfile2 ) {
   die "\nERROR:$scriptname: index table file '$indexfile2' already exists.\n\n";
}
if ( -e $indexlabel2 ) {
   die "\nERROR:$scriptname: index label file '$indexlabel2' already exists.\n\n";
}

#
#  Load list of kernel file(s).
#
print "\nLoading file names and required meta-information ...\n";
open( LIST, "< $filelist" ) ||
   die "\nERROR:$scriptname: cannot open '$filelist'.\n\n";

while ( $line = <LIST> ) {

   chop( $line );
   $line =~ s/\s*\r//g;

#  First find RELEASEID
   if     ( $line =~ /^RELEASE_ID\s*=\s*/ ) {

      $RELEASEID = $line ;
      $RELEASEID =~ s/^RELEASE_ID\s*=\s*//;

   } elsif     ( $line =~ /^RELEASE_DATE\s*=\s*/ ) {

      $RELEASEDATE = $line ;
      $RELEASEDATE =~ s/^RELEASE_DATE\s*=\s*//;

#  This is for PDS4 labels that do not have DATASETID
   } elsif     ( $line =~ /^DATASETID\s*=\s*/ ) {

      $DATASETID = $line ;
      $DATASETID =~ s/^DATASETID\s*=\s*//;

   } elsif     ( $line =~ /^FILE\s*=\s*/ ) {

      #
      #  Current line contains file name. Extract it. No need to check if it
      #  exists.
      #
      $kernelfile = $line;
      $kernelfile =~ s/^FILE\s*=\s*//;

      #
      # If this file is an MK, skip it.
      #
      if ( $kernelfile !~ /\/mk\/.*\.tm$/i ) {

     #
     #  Save it in the buffer, figure out label file name
	 #  and check whether the label file exists.
	 #
	 push( @kernels, $kernelfile );

	 $labelfile  = $kernelfile;
	 $labelfile  =~ s/\.\w+$/\.lbl/;

     unless (-e $labelfile) {
     #
     # We take advantage to determine whether if this is a PDS3 or PDS4
     # archive.
     #
        $labelfile  =~ s/\.\w+$/\.xml/;
        $PDS = 4;
     }

	 if ( -e $labelfile ) {

	    #
	    #  It does too. Then figure out what kernel file extension is.
	    #
	    $kernelname = $kernelfile;
	    $kernelname  =~ s/\.\w+$//;
	    $kernelextension = $kernelfile;
	    $kernelextension =~ s/$kernelname/\*/;

	    #
	    #  Save label name and file extension in the buffers.
	    #
	    $labels{$kernelfile} = $labelfile;
	    $extensions{$kernelextension} = "";

	    #  Save RELEASE_ID and RELEASE_DATE in their buffers.
	    $release_id{$kernelfile} = $RELEASEID ;
	    $release_date{$kernelfile} = $RELEASEDATE ;

	    #  Save DATASETID in the buffer if read from kernel list.
	    if( length $DATASETID ){
	        $DATASETID{$kernelfile} = $DATASETID ;
	    }

	 }  else {
	    print "   ERROR: '$labelfile(or *.lbl)'  doesn't exist.\n";
	 }

      }


   } elsif ( $line =~ /^VOLUMEID\s*=\s*/ ) {

      $VOLUMEID = $line;
      $VOLUMEID =~ s/^VOLUMEID\s*=\s*//;

   } else {

      #
      #  Well ... we do nothing with other lines ... at least in this version.
      #
   }

}

close( LIST ) ||
   die "\nERROR:$scriptname: cannot close '$filelist'.\n\n";
print "done.\n";

#
#  Do consistency check on collected information.
#
print "\nChecking loaded file names ...\n";

if ( @kernels == 0 ) {
   die "\nERROR:$scriptname: didn't collect any kernel file names provided ".
       "using FILE = ... keyword/value assignments in the config file ".
       "'$filelist'.\n\n";
}

@tmparr = values %labels;
if ( $#kernels != $#tmparr ) {
   print  "\nERROR:$scriptname: number of collected kernel file ".
          "names ($#kernels+1) doesn't match number of label file ".
          "names ($#tmparr+1).\n" ;
   print "\nThe following kernel/label names were collected:\n\n";
   foreach $file ( sort @kernels ) {
      printf "   %-37s   %-37s\n", $file, $labels{$file};
   }
   die "\n";
}

if ( ! ( $VOLUMEID =~ /\s*[0-9A-Z]+_\d+\s*/i ) ) {   # ignore case   LSE
   die "\nERROR:$scriptname: volume ID was not provided in the config ".
       "file '$filelist' using VOLUMEID = ... keyword/value assignment ".
       "or it didn't look like CCCC_DDDD, where C is a ".
       "character and D is a digit.\n\n";
}

print "done.\n";

print "\nCollected $#kernels+1 file/label names. Collected the ".
      "following set of file\nextensions:\n";
@tmparr = keys %extensions;
foreach $file ( @tmparr ) {
   print "   $file\n";
}

#
#  Loop through label files and pull out necessary information
#  from them.
#
print "\nCollecting index table values from labels ...\n";

#  The following are lengths of columns. First initialize to 0 except for
#  VOLUMEID, RELEASEIDL, RELEASEDATEL

$STARTTIMEL = "0";
$STOPTIMEL = "0";
$FILENAMEL = "0"; # Note this is the PRODUCTIDL
$DATASETIDL = "0";
$CREATIONTIMEL = "0";
$KERNELTYPEIDL = "0";
$LABELNAMEL = "0";
$VOLUMEIDL = length ($VOLUMEID) ;
$RELEASEDATEL = 10 ;                                      # LSE
$RELEASEIDL = 4     ;                                     # LSE
# $MISSIONPHASENAMEL = "0"; may not implement

#  Note: additional length fields, $RELEASEDATEL and $RELEASEIDL are defined
#  at the beginning of the program.

#
# Enforce lowecase for VOLUMEID if we have a PDS3 archive.
#
if( $PDS == 3 ){
  $VOLUMEID = lc $VOLUMEID
}
else {
  print "\nVOLID lowercase not enforced for PDS4 index files ...\n";
}

foreach $kernelfile ( @kernels ) {

   open( LABEL, "< $labels{$kernelfile}" ) ||
      die "\nERROR:$scriptname: cannot open label file ".
          "'$labels{$kernelfile}'.\n\n";

   while ( $line = <LABEL> ) {

      chop( $line );
      $line =~ s/\s*\r//g;

      if      ( $line =~ /^START_TIME\s*=\s*/ ) {

         $STARTTIME{$kernelfile} = $line;
         $STARTTIME{$kernelfile} =~ s/^START_TIME\s*=\s*//;
         if ( length($STARTTIME{$kernelfile}) > $STARTTIMEL ) {
            $STARTTIMEL = length($STARTTIME{$kernelfile});
         }

      } elsif ( $line =~ /start_date_time/ ) {

         $STARTTIME{$kernelfile} = $line;
         $STARTTIME{$kernelfile} =~ s/\s*<start_date_time>//;
         $STARTTIME{$kernelfile} =~ s/\s*Z<\/start_date_time>//;
         if ( length($STARTTIME{$kernelfile}) > $STARTTIMEL ) {
            $STARTTIMEL = length($STARTTIME{$kernelfile});
         }

      } elsif ( $line =~ /^STOP_TIME\s*=\s*/ ) {

         $STOPTIME{$kernelfile} = $line;
         $STOPTIME{$kernelfile} =~ s/^STOP_TIME\s*=\s*//;
         if ( length($STOPTIME{$kernelfile}) > $STOPTIMEL ) {
            $STOPTIMEL = length($STOPTIME{$kernelfile});
         }

      } elsif ( $line =~ /stop_date_time/ ) {

         $STOPTIME{$kernelfile} = $line;
         $STOPTIME{$kernelfile} =~ s/\s*<stop_date_time>//;
         $STOPTIME{$kernelfile} =~ s/\s*Z<\/stop_date_time>//;
         if ( length($STOPTIME{$kernelfile}) > $STOPTIMEL ) {
            $STOPTIMEL = length($STOPTIME{$kernelfile});
         }

      } elsif ( $line =~ /^PRODUCT_ID\s*=\s*/ ) {

         $FILENAME{$kernelfile} = $line;
         $FILENAME{$kernelfile} =~ s/^PRODUCT_ID\s*=\s*//;
         $FILENAME{$kernelfile} =~ s/\"//g;

      } elsif ( $line =~ /file_name/  ) {

         $FILENAME{$kernelfile} = $line;
         $FILENAME{$kernelfile} =~ s/\s*<file_name>//;
         $FILENAME{$kernelfile} =~ s/\s*<\/file_name>//;

      } elsif ( $line =~ /^DATA_SET_ID\s*=\s*/ ) {

         $DATASETID{$kernelfile} = $line;
         $DATASETID{$kernelfile} =~ s/^DATA_SET_ID\s*=\s*//;
         $DATASETID{$kernelfile} =~ s/\"//g;
         if ( length($DATASETID{$kernelfile}) > $DATASETIDL ) {
            $DATASETIDL = length($DATASETID{$kernelfile});
         }

      } elsif ( $line =~ /^PRODUCT_CREATION_TIME\s*=\s*/ ) {

         $CREATIONTIME{$kernelfile} = $line;
         $CREATIONTIME{$kernelfile} =~ s/^PRODUCT_CREATION_TIME\s*=\s*//;
         if ( length($CREATIONTIME{$kernelfile}) > $CREATIONTIMEL ) {
            $CREATIONTIMEL = length($CREATIONTIME{$kernelfile});
         }

      } elsif ( $line =~ /creation_date_time/ ) {

         $CREATIONTIME{$kernelfile} = $line;
         $CREATIONTIME{$kernelfile} =~ s/\s*<creation_date_time>//;
         $CREATIONTIME{$kernelfile} =~ s/\s*<\/creation_date_time>//;
         if ( length($CREATIONTIME{$kernelfile}) > $CREATIONTIMEL ) {
            $CREATIONTIMEL = length($CREATIONTIME{$kernelfile});
         }

      } elsif ( $line =~ /^KERNEL_TYPE_ID\s*=\s*/ ) {

         $KERNELTYPEID{$kernelfile} = $line;
         $KERNELTYPEID{$kernelfile} =~ s/^KERNEL_TYPE_ID\s*=\s*//;
         if ( length($KERNELTYPEID{$kernelfile}) > $KERNELTYPEIDL ) {
            $KERNELTYPEIDL = length($KERNELTYPEID{$kernelfile});
         }

      } elsif ( $line =~ /kernel_type/ ) {

         $KERNELTYPEID{$kernelfile} = $line;
         $KERNELTYPEID{$kernelfile} =~ s/\s*<kernel_type>//;
         $KERNELTYPEID{$kernelfile} =~ s/\s*<\/kernel_type>//;
         if ( length($KERNELTYPEID{$kernelfile}) > $KERNELTYPEIDL ) {
            $KERNELTYPEIDL = length($KERNELTYPEID{$kernelfile});
         }

#     } elsif ( $line =~ /^MISSION_PHASE_NAME\s*=\s*/ ) {
#
# Needs some work --may not implement!!
#        $MISSIONPHASENAME{$kernelfile} = $line;
#        $MISSIONPHASENAME{$kernelfile} =~ s/^MISSION_PHASE_NAME\s*=s*//;
#        if ( length($MISSIONPHASENAME{$kernelfile}) > $MISSIONPHASENAMEL ) {
#           $MISSIONPHASENAMEL = length($MISSIONPHASENAME{$kernelfile});
#        }

      } else {

         #
         #  We don't use other label keyword in indexes.
         #

      }

   }

   close( LABEL ) ||
      die "\nERROR:$scriptname: cannot close label file  ".
          "'$labels{$kernelfile}'.\n\n";

   #
   #  Check all values that we have collected from the current label.
   #
   if ( ! ( $STARTTIME{$kernelfile} =~
      /^\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2}/ ) &&
        ! ( $STARTTIME{$kernelfile} =~ /\"N\/A\"/ ) ) {
      die "\nERROR:$scriptname: START_TIME '$STARTTIME{$kernelfile}' ".
          "from the label '$labels{$kernelfile}' doesn't match expected ".
          "ISO format YYYY-MM-DDTHR:MN:SC or it wasn't present in ".
          "the label at all.\n\n";
   }

   if ( ! ( $STOPTIME{$kernelfile} =~
      /^\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2}/ ) &&
        ! ( $STOPTIME{$kernelfile} =~ /\"N\/A\"/ ) ) {
      die "\nERROR:$scriptname: STOP_TIME '$STOPTIME{$kernelfile}' ".
          "from the label '$labels{$kernelfile}' doesn't match expected ".
          "ISO format YYYY-MM-DDTHR:MN:SC or it wasn't present in ".
          "the label at all.\n\n";
   }

# Remember that $FILENAME{$kernelfile} is the PRODUCT_ID, i.e. file
# name (no path). $FILENAMEL is it's field length. $labels{$kernelfile}
# is the label file name **with ** path and  $LABELNAMEL is its field
# length.
   $tmpvar = $FILENAME{$kernelfile};
   if ( ! ( $kernelfile =~ /$tmpvar/ ) ) {
      die "\nERROR:$scriptname: PRODUCT_ID '$tmpvar' ".
          "from the label '$labels{$kernelfile}' doesn't contain   ".
          "actual kernel file name.\n\n";
   } else {
      if ( length($FILENAME{$kernelfile}) > $FILENAMEL ) {
         $FILENAMEL = length($FILENAME{$kernelfile});
      }
      if ( ( length($labels{$kernelfile}) ) > $LABELNAMEL ) {
         $LABELNAMEL = length($labels{$kernelfile});
      }
   }

   $tmpvar = $DATASETID{$kernelfile};
   if ( ! ( $tmpvar =~ /^[0-9A-Z\/]+-[A-Z\/]+-SPICE-6-V\d\.\d$/ ) ) { #Case SENSITIVE LSE
      die "\nERROR:$scriptname: DATA_SET_ID '$tmpvar' ".
          "from the label '$labels{$kernelfile}' doesn't match expected ".
          "pattern CCCCCC-C-SPICE-6-CCCC-VD.D.\n\n";
   }

   if ( ! ( $CREATIONTIME{$kernelfile} =~
      /^\d{4,4}-\d{2,2}-\d{2,2}T\d{2,2}:\d{2,2}:\d{2,2}/ ) ) {
      die "\nERROR:$scriptname: PRODUCT_CREATION_TIME ".
          "'$CREATIONTIME{$kernelfile}' ".
          "from the label '$labels{$kernelfile}' doesn't match expected ".
          "ISO format YYYY-MM-DDTHR:MN:SC.### or it wasn't present in ".
          "the label at all.\n\n";
   }

   if ( ! ( $KERNELTYPEID{$kernelfile} =~                       #LSE
      /^CK$|^DSK$|^EK$|^FK$|^IK$|^LSK$|^PCK$|^SCLK$|^SPK$/ ) ){
      die "\nERROR:$scriptname: KERNEL_TYPE_ID ".
          "'$KERNELTYPEID{$kernelfile}' ".
          "from the label '$labels{$kernelfile}' doesn't match expected ".
          "kernel type CK, DSK, EK, FK, IK, LSK, PCK, SCLK, SPK ".
          " or it wasn't present in the label at all.\n\n";
   }

}
print "done.\n";

#
#  Write index table file.
#
print "\nWriting index table file ...\n";

open( TABLE, ">$indexfile" ) ||
   die "\nERROR:$scriptname: cannot open index table file '$indexfile'.\n\n";

foreach $kernelfile ( @kernels ) {
   #
   #  Print records for the data file. - left justifies
   #
#   printf TABLE "\%-${STARTTIMEL}s,\%-${STOPTIMEL}s,\"\%-${FILENAMEL}s\",". #LSE
#          "\"\%-${DATASETIDL}s\",\%-${CREATIONTIMEL}s,\"\%-${RELEASEIDL}s\",". #LSE
#         "\%-${RELEASEDATEL}s,\"\%-${KERNELTYPEIDL}s\"\n",  #LSE
#          $STARTTIME{$kernelfile}, $STOPTIME{$kernelfile},  #LSE
#          $FILENAME{$kernelfile}, $DATASETID{$kernelfile},  #LSE
#          $CREATIONTIME{$kernelfile},$RELEASEID,$RELEASEDATE,       #LSE
#          $KERNELTYPEID{$kernelfile} ;        #LSE
# No need for the data file entry any more.

   #
   #  Write almost identical record for the label.
   #
   $labelfile = $labels{$kernelfile};

   #
   # Rename *.xml labels to *.lbl for the index.
   #
   if (index($labelfile, ".xml") != -1)  {
        $labelfile  =~ s/\.\w+$/\.lbl/;
   }

   printf TABLE "\%-${STARTTIMEL}s,\%-${STOPTIMEL}s,\"\%-${LABELNAMEL}s\",". #LSE
          "\"\%-${DATASETIDL}s\",\%-${CREATIONTIMEL}s,\"\%-${RELEASEIDL}s\",". #LSE
          "\%-${RELEASEDATEL}s,\"\%-${KERNELTYPEIDL}s\",".
          "\"\%-${FILENAMEL}s\",\"\%-${VOLUMEIDL}s\"\n",  #LSE
          $STARTTIME{$kernelfile}, $STOPTIME{$kernelfile},  #LSE
          $labelfile, $DATASETID{$kernelfile},  #LSE
          $CREATIONTIME{$kernelfile},$release_id{$kernelfile},
          $release_date{$kernelfile},
          $KERNELTYPEID{$kernelfile},$FILENAME{$kernelfile},
          $VOLUMEID ;        #LSE
}

close( TABLE ) ||
   die "\nERROR:$scriptname: cannot close index table file '$indexfile'.\n\n";

print "done.\n";

#
#  Values that will be substituted in the index table label text:
#
$VOLUMEID         =  $VOLUMEID;

$RECORDBYTES      =  $STARTTIMEL +
                     $STOPTIMEL +
                     $LABELNAMEL +
                     $DATASETIDL +
                     $CREATIONTIMEL +   #LSE
                     $RELEASEIDL +      #LSE
                     $RELEASEDATEL +    #LSE
                     $KERNELTYPEIDL +
                     $FILENAMEL +
                     $VOLUMEIDL + 23; #LSE Note: number of bytes = (fields) +
                 # (number of ") + (number of ,) + <cr> + <lf> = (fields) + 23

$FILERECORDS      =  ( $#kernels + 1 ); # Mod LSE

$ROWBYTES         = $RECORDBYTES;

$ROWS             = $FILERECORDS;

$COLUMNS          = "10";               #LSE

$FILEEXTENSIONS   = "\n";
@tmparr           = keys %extensions;
foreach $file ( sort @tmparr ) {
  $FILEEXTENSIONS = $FILEEXTENSIONS.
                    "                               \"$file\",\n";
}
chop( $FILEEXTENSIONS );
chop( $FILEEXTENSIONS );
$FILEEXTENSIONS= $FILEEXTENSIONS."\n";

# Note that if there is a " present in the column, the starting position occurs
# afterwards. The column length (e.g. $DATASETIDL) does not include the ".

@STARTPOS =( 1,                                 #LSE
    $STARTTIMEL+2,
    $STARTTIMEL+$STOPTIMEL+4,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+7,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+$DATASETIDL+9,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+$DATASETIDL+$CREATIONTIMEL+11,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+$DATASETIDL+$CREATIONTIMEL+$RELEASEIDL+13,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+$DATASETIDL+
    $CREATIONTIMEL+$RELEASEIDL+$RELEASEDATEL+15,$STARTTIMEL+$STOPTIMEL+$LABELNAMEL+
    $DATASETIDL+$CREATIONTIMEL+$RELEASEIDL+$RELEASEDATEL+$KERNELTYPEIDL+18,
    $STARTTIMEL+$STOPTIMEL+$LABELNAMEL+$DATASETIDL+$CREATIONTIMEL+$RELEASEIDL+
    $RELEASEDATEL+$KERNELTYPEIDL+$FILENAMEL+21 );

@FIELDLENGTH      =( $STARTTIMEL,                               #LSE
                     $STOPTIMEL,
                     $LABELNAMEL,
                     $DATASETIDL,
                     $CREATIONTIMEL,
                     $RELEASEIDL,
                     $RELEASEDATEL,
                     $KERNELTYPEIDL,
                     $FILENAMEL,
                     $VOLUMEIDL ) ;


#
#  Write table label file.
#
print "\nWriting index label file ...\n";

open( TABLELABEL, ">$indexlabel" ) ||
   die "\nERROR:$scriptname: cannot open index label file '$indexlabel'.\n\n";

print TABLELABEL <<"EndOfLabelText";
PDS_VERSION_ID             = PDS3
VOLUME_ID                  = $VOLUMEID
RECORD_TYPE                = FIXED_LENGTH
RECORD_BYTES               = $RECORDBYTES
FILE_RECORDS               = $FILERECORDS
^INDEX_TABLE               = "DSINDEX.TAB"

OBJECT                     = INDEX_TABLE

  INTERCHANGE_FORMAT       = ASCII
  ROW_BYTES                = $ROWBYTES
  ROWS                     = $ROWS
  COLUMNS                  = $COLUMNS
  INDEX_TYPE               = SINGLE
  INDEXED_FILE_NAME        = {$FILEEXTENSIONS                             }

  OBJECT                   = COLUMN
    NAME                   = START_TIME
    DATA_TYPE              = "TIME"
    START_BYTE             = $STARTPOS[0]
    BYTES                  = $FIELDLENGTH[0]
    FORMAT                 = "A$FIELDLENGTH[0]"
    DESCRIPTION            = "Start time of the product."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = STOP_TIME
    DATA_TYPE              = "TIME"
    START_BYTE             = $STARTPOS[1]
    BYTES                  = $FIELDLENGTH[1]
    FORMAT                 = "A$FIELDLENGTH[1]"
    DESCRIPTION            = "Stop time of the product."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = FILE_SPECIFICATION_NAME
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[2]
    BYTES                  = $FIELDLENGTH[2]
    FORMAT                 = "A$FIELDLENGTH[2]"
    DESCRIPTION            = "Unix style path and label file name."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = DATA_SET_ID
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[3]
    BYTES                  = $FIELDLENGTH[3]
    FORMAT                 = "A$FIELDLENGTH[3]"
    DESCRIPTION            = "Data set ID."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = PRODUCT_CREATION_TIME
    DATA_TYPE              = "TIME"
    START_BYTE             = $STARTPOS[4]
    BYTES                  = $FIELDLENGTH[4]
    FORMAT                 = "A$FIELDLENGTH[4]"
    DESCRIPTION            = "Product creation time."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = RELEASE_ID
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[5]
    BYTES                  = $FIELDLENGTH[5]
    FORMAT                 = "A$FIELDLENGTH[5]"
    DESCRIPTION            = "Identifier for product release."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = RELEASE_DATE
    DATA_TYPE              = "DATE"
    START_BYTE             = $STARTPOS[6]
    BYTES                  = $FIELDLENGTH[6]
    FORMAT                 = "A$FIELDLENGTH[6]"
    DESCRIPTION            = "Date on which the product was released."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = KERNEL_TYPE_ID
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[7]
    BYTES                  = $FIELDLENGTH[7]
    FORMAT                 = "A$FIELDLENGTH[7]"
    DESCRIPTION            = "Kernel type."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = PRODUCT_ID
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[8]
    BYTES                  = $FIELDLENGTH[8]
    FORMAT                 = "A$FIELDLENGTH[8]"
    DESCRIPTION            = "Kernel file name."
  END_OBJECT               = COLUMN

  OBJECT                   = COLUMN
    NAME                   = VOLUME_ID
    DATA_TYPE              = "CHARACTER"
    START_BYTE             = $STARTPOS[9]
    BYTES                  = $FIELDLENGTH[9]
    FORMAT                 = "A$FIELDLENGTH[9]"
    DESCRIPTION            = "The volume containing this data file."
  END_OBJECT               = COLUMN

END_OBJECT                 = INDEX_TABLE
END
EndOfLabelText

close( TABLELABEL ) ||
   die "\nERROR:$scriptname: cannot close index label file '$indexlabel'.\n\n";
print "done.\n";

print "\nIndex table file '$indexfile' and index label file ".
      "'$indexlabel' were\nsuccessfully created\n";

#
# Final touch: copy "ds" index table and label to their counter parts
# no contaning "ds" in the names. Tweak the pointer in the label while
# doing this.
#
$result = `cp $indexfile $indexfile2 2>&1`;
$status = ( $? >> 8 );
if ( $status ) {
   die "\nERROR: 'cp' failed to copy $indexfile to $indexfile2.\n";
}



$result = `sed 's/"DSINDEX.TAB"/"INDEX.TAB"/' < $indexlabel > $indexlabel2`;
$status = ( $? >> 8 );
if ( $status ) {
   die "\nERROR: 'sed' failed to copy $indexlabel to $indexlabel2.\n";
}

print "\nIndex table file '$indexfile2' and index label file ".
      "'$indexlabel2' were\nsuccessfully created\n";

#
#  All done.
#
exit;
