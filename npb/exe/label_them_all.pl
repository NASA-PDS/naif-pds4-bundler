#!/usr/bin/perl
#
#
#- Version --------------------------------------------------
#
$version = "Version 2.5.0 -- BVS/NAIF, May 16, 2019";
#
#  Version 2.5.0 -- BVS/NAIF, May 16, 2019
#
#     Relaxed the file name length restriction from 35.3 to 41.3
#     (limited by the 78 char width of the unwrapped label lines
#     including the file name, e.g. ^SPICE_KERNEL and PRODUCT_ID).
#
#  Version 2.4.0 -- BVS/NAIF, April 23, 2015
#
#     Added a hard-coded flag to not insert labels in the comments.
#     Changed to skip but not stop for MKs provided in the list.
#
#  Version 2.3.0 -- BVS/NAIF, December 27, 2012
#
#     Updated to allow extension BPE (from NEAR archive).
#
#  Version 2.2.0 -- BVS/NAIF, November 30, 2009
#
#     Updated to allow longer 36.3 file names.
#
#  Version 2.1.0 -- BVS/NAIF, January 28, 2008
#
#     Bug fix: in the previous version the $CLCOMMNT variable pointing
#     to the SPICE "commnt" utility program was set but not used;
#     instead the obsolete "clcommnt" program was invoked to
#     add/deleted comments. This variable was renamed to $COMMNT and is
#     now used in all places where the "commnt" executable is invoked.
#
#  Version 2.0.0 -- BVS/NAIF, January 26, 2006
#
#     Changed script interface; it now requires template, LSK
#     and SCLK names to be provided on the command line. Cleaned up
#     header comments a bit. Changed the script to not leave 
#     comment files behind.
#
#  Version 1.8.0 -- LSE/NAIF, June 15, 2005
#
#     Added the following filename extension.
#
#     .BEP     binary EK science plan files
#
#  Version 1.7.0 -- LSE/NAIF, June 15, 2005
#
#     Allow first character of any filename to be a number. This
#     has been confirmed as PDS compliant by Elizabeth Rye. Change default
#     label and comment file suffixes to lower case (.lbl & .cmt). Fix
#     test for determining whether to lower case label and comment file names.
#
#  Version 1.6.0 -- LSE/NAIF, May 21, 2002
#
#     Allow either upper or lower case files. Check for case is done
#     in input file.
#
#  Version 1.5.0 -- BVS/NAIF, April 21, 2000
#
#     Added check/correction for label lines longer than 78 characters.
#
#  Version 1.4.0 -- BVS/NAIF, January 14, 2000
#
#     Updated description to make sure that if description is one short
#     line it's wrapped correctly.
#
#  Version 1.3.0 -- BVS/NAIF, January 10, 2000
#
#     Updated description wrapping to shorten the lines to be less than
#     than 78 characters rather than 80.
#
#  Version 1.2.0 -- BVS/NAIF, January 3, 2000
#
#     Converted kernel file extensions to uppercase. Added ISO 9660 Level
#     file name compliance check.
#
#  Version 1.1.0 -- BVS/NAIF, September 27, 1999
#
#     Updated to add END at the end of each detached label file.
#
#  Version 1.0.0 -- BVS/NAIF, April 12, 1999
#
#     Initial version
#
#----------------------------------------------------------------------
#
#  PLEASE, READ INFORMATION IN THE SCRIPT HEADER FROM THE VERY BEGINNING TO
#  THE VERY END BEFORE RUNNING THE SCRIPT :)
#
#- WHAT DOES THE SCRIPT DO? -------------------------------------------
#
#  This script consistently labels a complete collection of SPICE
#  kernels for a particular mission. It takes list of the file names,
#  MAKLABEL label options and description for each file from an text file
#  of special format (see below) and processes each file in the list.
#
#- WHAT DOES THE SCRIPT DO FOR EACH KERNEL FILE? ----------------------
#
#  1) Runs MAKLABEL to generate PDS label in accordance with specified
#     set of MAKLABEL options;
#
#  2) Inserts provided file description into the corresponding field of
#     of the label;
#
#  3) extracts comments from the comments area of binary files; adds label
#     at the beginning of the comment area contents (for binary kernels)
#     or after ARCH/TYPE word at the beginning of the file (for text
#     kernels; inserts comments with label back into the comment area of
#     binary files;
#
#  The script does NOT create backup copy of unlabeled kernels. After
#  it finished, it leaves *.lbl files for each of processes kernel
#  file.
#
#  Note that the script will not do any processing on any kernel file
#  for which *.lbl were present before the run.
#
#  Note that if label was present in the text file body or in the comment ares
#  of a binary file, the script tries to delete it before inserting a new
#  label.
#
#- SPICE KERNEL FILE FORMAT -------------------------------------------
#
#  SPICE kernel files must be in binary (SPK, CK, binary PCK and
#  sequence/database EK) or text (LSK, SCLK, text PCK, FK, IK) format
#  depending on kernel type. All binary files must contain complete
#  final comments in the comment area. External comment files must NOT
#  be provided.
#
#- SPICE KERNEL FILE EXTENSIONS ---------------------------------------
#
#  SPICE kernels file that will be processed must follow 27.3 file
#  naming schema and have the following extensions depending on their
#  type:
#
#     .bsp     binary SPK files
#     .bc      binary CK files
#     .bpc     binary PCK files
#     .bes     binary EK sequence files
#     .bep     binary EK plan files
#     .bdb     binary EK data base files
#     .ti      text IK files
#     .tf      text FRAME fileS
#     .tls     text LSK files
#     .tpc     text PCK files
#     .tsc     text SCLK files
#
#  To add other extension to this list updated corresponding check in the
#  script code.
#  Lower case files are preserved as lower case. LSE 5/21/02
#  Note: case determination is made by examining the case
#  for the "FILE" line below.
#
#- INPUT FILE FORMAT --------------------------------------------------
#
#     DATE = <date>
#     SPACECRAFT = <s/c>
#     NAIFER = <full name>
#     PHONE = <phone>
#     EMAIL = <e-mail>
#     VOLUMEID = <volume id>
#     RELEASE_ID   = <number>
#     RELEASE_DATE = <YYYY-MM-DD>
#     $EOH
#     FILE             = <name of file 1>
#     MAKLABEL_OPTIONS = <MAKLABEL options for file 1>
#     DESCRIPTION      = <description of file 1, on a single line!>
#     FILE             = <name of file 2>
#     MAKLABEL_OPTIONS = <MAKLABEL options for file 2>
#     DESCRIPTION      = <description of file 2, on a single line!>
#     ...
#     FILE             = <name of file N>
#     MAKLABEL_OPTIONS = <MAKLABEL options for file N>
#     DESCRIPTION      = <description of file N, on a single line!>
#
#  Any set of keywords can be present in the header -- the script doesn't check
#  them. It skips them until it finds the first line that matches pattern
#  /^FILE\s*=\s*/. But once it found such line, it assumes that the rest of the
#  file after that line contains triplets of lines (file name, MAKLABEL options,
#  description) with no other types of lines present between or after them
#  (even blank lines are not allowed.)
#
#  File names must be given with respect to the directory from which the
#  script in executed. MAKLABEL options must be the ones registered in the
#  mission template file specified in the $TEMPLATE variable at the
#  beginning of the script. Description must be on a single line but it
#  can be on of any length -- it will be wrapped by column 80 before being
#  into the label.
#
#- MAKLABEL NOTE ------------------------------------------------------
#
#  Think carefully regarding pre-set keyword values and recognizable MAKLABEL
#  options. Make sure that all possible values for PRODUCER_ID, NOTE,
#  SOURCE_PRODUCT_ID, MISSION_PHASE_NAME, PRODUCT_VERSION_TYPE,
#  INSTRUMENT_NAME and PLATFORM_OR_MOUNTING_NAME are covered. Make sure that
#  value of such keywords as MISSION_NAME, SPACECRAFT_NAME, MISSION_PHASE_NAME,
#  are the same as used by the project. Make sure that DATA_SET_ID value
#  pattern follows standard for the project (normally aaa-b-SPICE-6-V1.0,
#  where aaa is project ID, b is target id; ex: MGS-M-SPICE-6-V1.0).
#
#- MISCELLANEOUS SETUPS ------------------------------------------------
#
#  Paths to the following files must be specified in the variables at the
#  begnning of the script:
#
#     -  MAKLABEL executable;
#     -  ARCHTYPE executable;
#     -  COMMNT executable;
#
#- MISCELLANEOUS SETUP VARIABLES ---------------------------------------
#
$scriptname = "label_them_all.pl";

#
# Insert or not insert labels in the comments.
#
$insertlbl = "yes";
$insertlbl = "no";

#
# Executable invoked by the script.
#
#$MAKLABEL   = "/naif/toolkit/exe/maklabel";
#
# 03/18/18: Switched to used local MAKLABEL with increased instrument
# ID buffer in order to be able to label OCAMS IK.
#
$MAKLABEL   = "/home/bsemenov/misc/programs/maklabel/maklabel";
$ARCHTYPE   = "/naif/toolkit/exe/archtype";
$COMMNT   = "/naif/toolkit/exe/commnt";

#
#  Display version.
#
print "\nScript that labels a collection of SPICE kernels listed in a text ".
      "file.\n".
      "Version $version.\n";

#
#  Get from the command line the names of the list file, MAKLABEL template,
#  LSK and SCLK.
#
#
if ( @ARGV == 4 ) {
   $TEMPLATE = shift @ARGV;
   if ( ! -e $TEMPLATE ) {
      die "\nERROR:$scriptname: the file '$TEMPLATE' doesn't exist.\n\n";
   }
   $LSKFILE = shift @ARGV;
   if ( ! -e $LSKFILE ) {
      die "\nERROR:$scriptname: the file '$LSKFILE' doesn't exist.\n\n";
   }
   $SCLKFILE = shift @ARGV;
   if ( ! -e $SCLKFILE ) {
      die "\nERROR:$scriptname: the file '$SCLKFILE' doesn't exist.\n\n";
   }
   $filelist = shift @ARGV;
   if ( ! -e $filelist ) {
      die "\nERROR:$scriptname: the file '$filelist' doesn't exist.\n\n";
   }
} else {
   die "\nUsage: > $scriptname <template> <lsk> <sclk> <kernel_list_file>\n\n";
}

#
#  Check whether MAKLABEL, ARCHTYPE and COMMNT are execuable
#  under current accocunt and check existence of TEMPLATE, LSK and
#  SCLK files and set required MAKLABEL environment variables.
#
( -x $MAKLABEL ) || die "\nERROR:$scriptname: '$MAKLABEL' is not executable.\n\n";
( -x $ARCHTYPE ) || die "\nERROR:$scriptname: '$ARCHTYPE' is not executable.\n\n";
( -x $COMMNT )   || die "\nERROR:$scriptname: '$COMMNT' is not executable.\n\n";
( -e $TEMPLATE ) || die "\nERROR:$scriptname: '$TEMPLATE' doesn't exist.\n\n";
( -e $LSKFILE )  || die "\nERROR:$scriptname: '$LSKFILE' doesn't exist.\n\n";
( -e $SCLKFILE ) || die "\nERROR:$scriptname: '$SCLKFILE' doesn't exist.\n\n";
$ENV{'MISSION_TEMPLATE'} = "$TEMPLATE" ||
  die "\nERROR:$scriptname: couldn't set MISSION_TEMPLATE environment variable for MAKLABEL.\n\n";
$ENV{'LEAPSECONDS'} = "$LSKFILE" ||
  die "\nERROR:$scriptname: couldn't set LEAPSECONDS environment variable for MAKLABEL.\n\n";
$ENV{'SCLK'} = "$SCLKFILE" || 
  die "\nERROR:$scriptname: couldn't set SCLK environment variable for MAKLABEL.\n\n";

#
#  Open list file and get triplets of lines from it.
#
open( LIST, "< $filelist" ) ||
   die "\nERROR:$scriptname: cannot open '$filelist'.\n\n";

while( $kernelfile = <LIST> ) {

   chop( $kernelfile );

   if ( $kernelfile =~ /^FILE\s*=\s*/ ) {

      #
      #  Extract file name from the line.
      #
      $kernelfile =~ s/^FILE\s*=\s*//;

      print "\nProcessing '$kernelfile':\n";

      #
      #  Get next line and pull out maklabel options from it.
      #
      $options = <LIST> || die "\nERROR:$scriptname: cannot get next line from ".
                                 "input file.\n";
      chop( $options );
      if ( $options =~ /^MAKLABEL_OPTIONS\s*=\s*/ ) {
         $options =~ s/^MAKLABEL_OPTIONS\s*=\s*//;
      } else {
         die "\nERROR:$scriptname:the line:\n   $kernelfile\nfrom the input file".
               "doesn't contain MAKLABEL options in the following format:\n".
               "   MAKLABEL_OPTIONS = <maklabel options list>\n\n";
      }

      #
      #  Get next line and pull out description from it.
      #
      $description = <LIST> || die "\nERROR:$scriptname: cannot get next line ".
                                    "from input file.\n";;
      chop( $description );
      if ( $description =~ /DESCRIPTION\s*=\s*/ ) {
         $description =~ s/DESCRIPTION\s*=\s*//;
      } else {
         die "\nERROR:$scriptname:the line:\n   $kernelfile\nfrom the input file".
               "doesn't contain file description in the following format:\n".
               "   DESCRIPTION = <description line>\n\n";
      }

      #
      #  Parse description to replace quotes and wrap it by less than 78 columns.
      #
      if ( ! ( $description =~ /^\s*$/ ) ) {

         #
         #  Replace plain double quotes with smart double quotes.
         #
         $description =~ s/ \"/ \`\`/g;
         $description =~ s/\" /\'\' /g;

         #
         #  Add one space to the end of the descritpion to make sure
         #  that short descriptions are wrapped correctlt too.
         #
         $description = $description." ";

         #
         #  First line must be wrapped about 44 characters.
         #
         $pos = 0;
         while ( index( $description, " ", $pos ) < 44 &&
                  index( $description, " ", $pos ) >= $pos ) {
            $pos = index( $description, " ", $pos ) + 1;
         }
         if ( index( $description, " ", $pos ) >= $pos ) {
            substr( $description, $pos-1, 1 ) = "\n";
            $ppos = $pos;
         }

         #
         #  The rest of the lines must be wrapped by 77 characters (not 80 to save
         #  space for double quote at the very end of the description.
         #
         while ( index( $description, " ", $pos ) >= $pos ) {
            while ( index( $description, " ", $pos ) - $ppos < 77 &&
                     index( $description, " ", $pos ) >= $pos         ) {
               $pos = index( $description, " ", $pos ) + 1;
            }
            if ( index( $description, " ", $pos ) >= $pos ) {
               substr( $description, $pos-1, 1 ) = "\n";
            } else {
               if ( length( $description ) - $ppos >= 77 ) {
                  substr( $description, $pos-1, 1 ) = "\n";
               }
            }
            $ppos = $pos;
         }

      } else {
         $description = "N/A";
      }

      #
      #  Check if kernel file exists and proceed if so.
      #
      if ( -e $kernelfile && $description ) {

         #
         #  Check whether we can recognize file extension as ligitimate
         #  SPICE kernel extension and the name is not too long (41.3)
         #  (limited by the 78 char width of the unwrapped label lines
         #  including the file name, e.g. ^SPICE_KERNEL and PRODUCT_ID).
         #  Ignore case. Note \/ has been removed from kernelfile pattern match.
         #
         if ( ( $kernelfile =~ /\.BSP$/i ||
                $kernelfile =~ /\.BC$/i  ||
                $kernelfile =~ /\.BPC$/i ||
                $kernelfile =~ /\.BES$/i ||
                $kernelfile =~ /\.BEP$/i ||
                $kernelfile =~ /\.BPE$/i ||
                $kernelfile =~ /\.BDB$/i ||
                $kernelfile =~ /\.BDS$/i ||
                $kernelfile =~ /\.TI$/i  ||
                $kernelfile =~ /\.TF$/i  ||
                $kernelfile =~ /\.TLS$/i ||
                $kernelfile =~ /\.TPC$/i ||
                $kernelfile =~ /\.TSC$/i    ) &&
                $kernelfile =~ /\b[A-Z0-9]{1,1}[A-Z_0-9]{1,41}\.[A-Z]{1,3}$/i) {

            #
            #  Set label and comments file names. Check if they already
            #  exist.
            #
            $labelfile  = $kernelfile;
            $labelfile  =~ s/\.\w+$/\.lbl/;
            $commntfile = $labelfile;
            $commntfile =~ s/\.lbl$/\.cmt/;
            #
            #  If there are no upper case letters in original, lower case everything.

            if (!  $kernelfile =~ /[A-Z]/ ) {
                 $labelfile  =~ tr/A-Z/a-z/ ;
                 $commntfile  =~ tr/A-Z/a-z/ ;
            }
            print "   label file name: '$labelfile'\n";
            print "   comments file name: '$commntfile'\n";

            if ( ! -e $labelfile && ! -e $commntfile ) {

               #
               #  Run maklabel.
               #
               print "   running maklabel ...\n";
               $result = `$MAKLABEL pds $options $kernelfile $labelfile`;
               $status = ( $? >> 8 );

               if ( ! $status && -e $labelfile ) {

                  print "   maklabel finished OK\n";

                  #
                  #  "Ingest" just created label file into the program
                  #  line-by-line.
                  #
                  $labeltext = "";

                  open( LBLFIL, "< $labelfile" ) ||
                     die "\nERROR:$scriptname: cannot open '$labelfile'.\n\n";

                  while( $lblline = <LBLFIL> ) {

                     #
                     #  Make sure that the line is no longer than 78 characters.
                     #  if it is, remove one space at a time until it becomes
                     #  short enough ...
                     #
                     chop( $lblline );

                     while( length($lblline) > 78 ) {
                        if( $lblline =~ / / ) {
                           $lblline =~ s/ //;
                        } else {
                           chop( $lblline );
                           print "WARNING:$scriptname: no blanks to remove, chopped last char\n";
                        }
                     }

                     #
                     #  Add line to the label buffer.
                     #
                     $labeltext = $labeltext.$lblline."\n";

                  }

                  close( LBLFIL ) ||
                     die "\nERROR:$scriptname: cannot close '$labelfile'.\n\n";

                  #
                  #  Replace blank description field with the one from input
                  #  file.
                  #
                  $labeltext =~ s/  DESCRIPTION                = " "/  DESCRIPTION                = "$description"/;

		  #
		  #  Rewriting label file to make sure that
		  #  our description ended up there.
		  #
		  print "   re-writing label file ...\n";
		  open( LABEL, ">$labelfile" ) ||
		     die "   ERROR: cannot open label file '$labelfile".
			   "for write.\n";
		  print LABEL $labeltext;
		  print LABEL "END\n";
		  close( LABEL ) ||
		     die "   ERROR: cannot close '$labelfile'.\n";
		  print "   done.\n";

		  #
		  # If requested, insert label in the comments.
		  #
                  if ( $insertlbl eq "yes" ) {

                     #
                     #  Now we need to check whether we have to insert this label
                     #  at the beginning of the file itself (for text kernels) or
                     #  at the beginning of the comment area. To do that, we run
                     #  archtype to detect what the file type is.
                     #
                     print "   running archtype ...\n";
                     $type = `$ARCHTYPE $kernelfile`;
                     $status = ( $? >> 8 );

                     if ( ! $status && ! ( $type =~ /UNK/ ) ) {

                        chop( $type );
                        $type =~ s/ /\//;
                        print "   archtype finished OK. File architecture/type ".
                              "is '$type'.\n";

                        print "   extracting existing comments from the file ...\n";
                        if      ( $type =~ /DAS/ || $type =~ /DAF/ ) {

                           #
                           #  Run clcommnt to extract contents of the comment area
                           #  of the file.
                           #
                           $commenttext = `$COMMNT -e $kernelfile $commntfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: '$COMMNT -e' failed to extract ".
                                    "comments from the file. Cannot proceed further.\n";
                           }

                           $commenttext = `cat $commntfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: 'cat' failed to dump contents of the ".
                                    "file '$commntfile'. Cannot proceed further.\n";
                           }

                        } else {

                           $commenttext = `cat $kernelfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: 'cat' failed to dump contents of the ".
                                    "file '$kernelfile'. Cannot proceed further.\n";
                           }

                        }
                        print "   done.\n";

                        #
                        #  If comments already have label(s), we have to clean it
                        #  (them) out.
                        #
                        if ( $commenttext =~
                                 /\\beginlabel\n(.|\n)*\n\\endlabel\n/ ) {
                           print "   Found old label(s), cleaning it(them) up ...\n";
                           $commenttext =~
                                 s/\\beginlabel\n(.|\n)*\n\\endlabel\n//g;
                           print "   done\n";
                        }

                        print "   inserting new label into the comments ...\n";
                        #
                        #  Now we need to insert new label into the comments.
                        #
                        if      ( $type =~ /DAS/ || $type =~ /DAF/ ) {

                           #
                           #  Add label at the beginning of the comments.
                           #
                           $commenttext = "\\beginlabel\n$labeltext\\endlabel\n".
                                          $commenttext;

                           #
                           #  Adjust number of blank lines after the label.
                           #
                           $commenttext =~ s/\\endlabel(\s*\n)*/\\endlabel\n\n\n/;

                        } else {

                           #
                           #  Check whether we can find architecture/type ID at the
                           #  beginning of the file before trying to insert label.
                           #
                           if( $commenttext =~ /^$type/ ) {

                              #
                              #  Insert label after architecture/type sctring.
                              #
                              $commenttext =~
                              s/^$type\s*\n/$type\n\n\\beginlabel\n$labeltext\\endlabel\n/;

                              #
                              #  Adjust number of blank lines after the label.
                              #
                              $commenttext =~ s/\\endlabel(\s*\n)*/\\endlabel\n\n\n/;


                           } else {
                              die "   ERROR: achitecture/type string at the ".
                                    "beginning of the file doesn't match the one ".
                                    "returned by archtype ('$type'). Cannot ".
                                    "proceed further.\n";
                           }

                        }
                        print "   done.\n";

                        #
                        #  Write updated comments to the commments file.
                        #
                        print "   writing updated comments and inserting them ".
                              "into the file ...\n";
                        open( COMMENTS, ">$commntfile" ) ||
                           die "   ERROR: cannot open comments file '$commntfile".
                                 "for write.\n";
                        print COMMENTS $commenttext;
                        close( COMMENTS ) ||
                           die "   ERROR: cannot close '$commntfile'.\n";

                        #
                        #  Inserting comments into the file.
                        #
                        if      ( $type =~ /DAS/ || $type =~ /DAF/ ) {

                           #
                           #  Run clcommnt to delete old comments and insert updated
                           #  comments.
                           #
                           $commenttext = `$COMMNT -d $kernelfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: '$COMMNT -d' failed to delete old ".
                                    "comments from the file. Cannot proceed further.\n";
                           }

                           $commenttext = `$COMMNT -a $kernelfile $commntfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: '$COMMNT -a' failed to add updated ".
                                    "comments the file. Cannot proceed further.\n";
                           }

                        } else {

                           $result = `cp $commntfile $kernelfile`;
                           $status = ( $? >> 8 );
                           if ( $status ) {
                              die "   ERROR: 'cp' failed to copy updated file ".
                                    "(with new label included) to original file.\n";
                           }

                        }
                        print "   done.\n";

                        #
                        #  We don't need commnent file anymore; delete it.
                        #
                        unlink ( $commntfile ) ||
                           die "   ERROR: cannot remove comment file '$commntfile'.";

                        #
                        #  All done.
                        #
                        print "processing completed.\n";

                     } else {
                        print "   ERROR: archtype failed or couldn't recognize ".
                              "architecture and type of the file.\n";
                     }

		  }

               } elsif ( $status || ! -e $labelfile ) {
                  print "   ERROR: maklabel failed. Messages were:\n$result\n";
               }

            } else {
               print "   ERROR: '$labelfile' or '$commntfile' already exists.\n";
            }

         } elsif ( $kernelfile =~ /\.TM$/i &&
                   $kernelfile =~ /\b[A-Z0-9]{1,1}[A-Z_0-9]{1,35}\.[A-Z]{1,3}$/i) {

            print "   Skipping an MK. MAKLABEL doesn't know how to label MKs.\n   Done\n"

         } else {
            print "   ERROR: Cannot recognize extension of '$kernelfile' \n".
                  "         or file name doesn't comply with the PDS  \n".
                  "         standard: [A-Z0-9]{1,1}[A-Z_0-9]{1,35}\.[A-Z]{1,3}\n";
         }

      } else {
         print "   ERROR: '$kernelfile' doesn't exist or file description \n".
               "          wasn't provided in the setup file.\n";
      }
   }
}

#
#  Close list file.
#
close( LIST ) ||
   die "\nERROR:$scriptname: cannot close '$filelist'.\n\n";

print "\n";
exit;

