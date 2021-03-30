#!/usr/bin/perl

# mkpdssum
#
# Routine to generate a list of MD5 checksums for all files in a PDS volume
# structure.  Output is in the same format as produce by the 'md5sum'
# routine: i.e., 32 bytes for the hex checksum, two blanks, and the file
# path and name relative to the input root_dir, padded and with CR/LF 
# terminators and with an accompanying PDS Label.  
#
# The program can also be run on non-PDS volume directory trees to produce 
# just the checksum listing.
#
#  Format:  % mkpdssum [-p] [-f] [-l|-u] [-v ID] [-x filepart] [ root_dir ]
#
#   where  -f          follow symlinks (uses "follow_fast" option)
#          -p          just produces the plain checksum list (without label
#                      or padding) in the current working directory
#          -l          forces all file names in the output to lower case
#          -u          forces all files names in the output to upper case
#          -v ID       use "ID" as VOLUME_ID in PDS label
#          -x filepart exclude all files matching "filepart" [may be repeated]
#          root_dir    is the root of the volume/directory tree to be checked
#
# Default is to check the current working directory unless another root is
# specified.  The root_dir string is clipped from the beginning of the file
# names.  Output is to a file called "checksum.tab".
#
# 12 Jul 2006, A.C.Raugh
# 18 Jul 2006, A.C.Raugh  Added options and label file writing
# 20 Sep 2006, ACR: Modified to use Getopt::Long to accommodate multiple 
#                   excluded file patterns.
# 16 Nov 2006, ACR: Added "follow symlinks" option and output sort
# 26 Nov 2007, ACR: Removed CHECKSUM_TYPE keyword (never approved)
#
# Procedure:
#
#   Parse arguments and set control flags
#   check for volume format and set flags
#   Open temp file and get ready to count 
#   Create the draft table
#   Rewind temp file and write final table
#   Write label
#
# NOTE: Global variables are used to pass information back and forth from the
#       specialty subroutines.
#
#
#=============================================================================

use File::Find;
use File::Temp;
use Digest::MD5;
use Getopt::Long;

$TRUE  = 1;
$FALSE = 0;

# Collect command line options:

GetOptions("l" => \$opt_l, 
           "u" => \$opt_u,
           "p" => \$opt_p,
           "f" => \$opt_f,
           "v=s" => \$opt_v,
           "x=s" => \@exclude);

# Set default values:

$ROOT  = ".";

if (@ARGV > 0)
  { $ROOT = $ARGV[0]; 
    $ROOT =~ s/\/$//;
  }
if (@ARGV > 1)
  { die "Usage: mkpdssum [-p] [-f] [-l|-u] [-v ID] [-x file] [ root_dir ]\n"; }

$follow = ($opt_f)? 1 : 0;

# Sanity checks:

if ($opt_u && $opt_l)
  { undef $opt_u;
    undef $opt_l;
    printf STDERR "mkpdssum: -u and -l are mutually exclusive.  ";
    printf STDERR "Ignored both.\n";
  }

# Initialize counters.  These are accessed by the 'runmake' subroutine:

$lines      = 0;
$maxpathlen = 0;

# Checking the root directory to make sure it exists and to see if it is in
# a PDS volume-like format, and setting output file names accordingly (the 
# '-p' option overrides this:

if ($opt_p)
  { $volume = 0;
    $sums_file  = ($opt_u)? "CHECKSUM.TAB" : "checksum.tab";
  }
else
  { if (!(-d $ROOT))
    { die "$ROOT is not a directory\n."; }

  if (-d "$ROOT/index")
    { $index_dir  = "$ROOT/index"; 
      $sums_file  = "$index_dir/checksum.tab";
      $sums_label = "$index_dir/checksum.lbl";
      $sums_point = "checksum.tab";
      $volume     = $TRUE;
    }
  elsif (-d "$ROOT/INDEX")
    { $index_dir  = "$ROOT/INDEX"; 
      $sums_file  = "$index_dir/CHECKSUM.TAB";
      $sums_label = "$index_dir/CHECKSUM.LBL";
      $sums_point = "CHECKSUM.TAB";
      $volume     = $TRUE;
    }
  else
    { $volume     = $FALSE;
      $sums_file  = ($opt_u)? "CHECKSUM.TAB" : "checksum.tab";
    }
  }

# If we've got a volume structure, see if we also have a voldesc.cat file:

if ($volume)
  { if (-f "$ROOT/voldesc.cat")
      { $voldesc = "$ROOT/voldesc.cat"; }
    elsif (-f "$ROOT/VOLDESC.CAT")
      { $voldesc = "$ROOT/VOLDESC.CAT"; }
  }

# Get a temporary file handle for the draft checksum file:

$TMP = File::Temp::tempfile();

# Set up the reusable checksum object:

$md5 = Digest::MD5->new;

# Search through the $ROOT directory tree.  Because of the overhead involved
# in forcing case (checking flags for each line), we'll save some execution
# time at the cost of lines of code by having a separate routine for each of
# the three possibilities: force to upper; force to lower; and leave as is:

if ($opt_u)
  { find({wanted=>\&runupper, no_chdir=>1, 
          follow_fast=>$follow},$ROOT); }
elsif ($opt_l)
  { find({wanted=>\&runlower, no_chdir=>1, 
          follow_fast=>$follow},$ROOT); }
else
  { find({wanted=>\&runmake, no_chdir=>1, 
          follow_fast=>$follow},$ROOT); }

# Rewind the temporary file:

seek $TMP, 0, 00;

# Now, if we're not dealing with a volume, we just sort the draft file
# into the output file and we're done:

if (! $volume)
  { open (OUT,"| sort -k 2 >$sums_file") ||
        die "Could not open sorted $sums_file for output ($!)";
    for ($i = 0; $i < $lines; $i++)
      { $rec = <$TMP>;
        printf OUT $rec;
      }
    close OUT;
    exit;
  }

# When we are dealing with a volume, we need to rewrite the records in the
# draft file to generate a fixed-length file, then write the label:

open (OUT,"| sort -k 2 >$sums_file") || 
    die "Could not open sorted $sums_file for output ($!)";
$outlen = $maxpathlen + 34;

for ($i = 0; $i < $lines; $i++)
  { $rec = <$TMP>;
    chop $rec;
    printf OUT "%-*.*s\r\n",$outlen,$outlen,$rec;
  }
close(OUT);

# Before we write the label we'll look for a volume ID to use:

if ($opt_v)
  { $volume_id = $opt_v; }   # Overrides voldesc.cat, if any
elsif ($voldesc)
  { $volume_id = getvolid($voldesc); }

# Get the current time for PRODUCT_CREATION_TIME:

($sec,$min,$hour,$mday,$mon,$year,@junk) = localtime(time);
$mon++;
$year += 1900;
$product_time = sprintf("PRODUCT_CREATION_TIME = %4d-%02d-%02dT%02d:%02d:%02d",
                        $year,$mon,$mday,$hour,$min,$sec);

# Set up the lines that actually depend on the file specifics:

$record_bytes = sprintf("RECORD_BYTES          = %d",34+$maxpathlen+2);
$file_records = sprintf("FILE_RECORDS          = %d",$lines);
$rows         = sprintf("  ROWS               = %d",$lines);
$row_bytes    = sprintf("  ROW_BYTES          = %d",34+$maxpathlen+2);
$bytes        = sprintf("    BYTES         = %d",$maxpathlen);
$format       = sprintf("    FORMAT        = \"A%d\"",$maxpathlen);

# Now we're ready to go:

open(LBL,">$sums_label") || die "Could not open $sum_label for writing ($!)";

$fmt = "%-78.78s\r\n";
printf LBL $fmt, "PDS_VERSION_ID        = PDS3";
printf LBL $fmt, " ";
printf LBL $fmt, "RECORD_TYPE           = \"FIXED_LENGTH\"";
printf LBL $fmt, $file_records;
printf LBL $fmt, $record_bytes;
printf LBL $fmt, " ";
printf LBL $fmt, "^TABLE                = \"$sums_point\"";
printf LBL $fmt, " ";
printf LBL $fmt, "VOLUME_ID             = \"$volume_id\"" if ($volume_id);
if ($volume_id)
  { printf LBL $fmt, "PRODUCT_NAME          = \"MD5 CHECKSUM TABLE FOR VOLUME $volume_id\""; }
else
  { printf LBL $fmt, "PRODUCT_NAME          = \"MD5 CHECKSUM TABLE\""; }
printf LBL $fmt, $product_time;
printf LBL $fmt, "START_TIME            = \"N/A\"";
printf LBL $fmt, "STOP_TIME             = \"N/A\"";
printf LBL $fmt, " ";

printf LBL $fmt, "OBJECT     = TABLE";
printf LBL $fmt, "  INTERCHANGE_FORMAT = \"ASCII\"";
printf LBL $fmt, $rows;
printf LBL $fmt, $row_bytes;
printf LBL $fmt, "  COLUMNS            = 2";
printf LBL $fmt, "  ";
printf LBL $fmt, "  OBJECT     = COLUMN";
printf LBL $fmt, "    COLUMN_NUMBER = 1";
printf LBL $fmt, "    NAME          = \"MD5_CHECKSUM\"";
printf LBL $fmt, "    START_BYTE    = 1";
printf LBL $fmt, "    BYTES         = 32";
printf LBL $fmt, "    DATA_TYPE     = \"CHARACTER\"";
printf LBL $fmt, "    FORMAT        = \"A32\"";
printf LBL $fmt, "    DESCRIPTION   = \"MD5 checksum presented as a 32-character string of";
printf LBL $fmt, "      hexadecimal digits (0-9,a-f)\"";
printf LBL $fmt, "  END_OBJECT = COLUMN";
printf LBL $fmt, "  ";
printf LBL $fmt, "  OBJECT     = COLUMN";
printf LBL $fmt, "    COLUMN_NUMBER = 2";
printf LBL $fmt, "    NAME          = \"FILE_SPECIFICATION_NAME\"";
printf LBL $fmt, "    START_BYTE    = 35";
printf LBL $fmt, $bytes;
printf LBL $fmt, "    DATA_TYPE     = \"CHARACTER\"";
printf LBL $fmt, $format;
printf LBL $fmt, "    DESCRIPTION   = \"File name and path from the volume root\"";
printf LBL $fmt, "  END_OBJECT = COLUMN";
printf LBL $fmt, "  ";
printf LBL $fmt, "END_OBJECT = TABLE";
printf LBL $fmt, "  ";
printf LBL $fmt, "END";

close(LBL);

# And we're done.

#============================================================================

sub runmake               # Same case as on device
  { my ($pathlen);
    my ($sum,$file);

    $file = $File::Find::name;

    # No action if this is a directory:

    return if (-d $File::Find::name);

    # No action if this file matches anything in the exclusion list:

    foreach $string (@exclude)
      { return if ($File::Find::name =~ /$string/); }

    # Otherwise we get the MD5 checksum:

    $md5->new;      # Resets for next file;
    open(CHK,$file) || die "Couldn't open $file for reading ($!)";
    binmode(CHK);
    $sum = $md5->addfile(*CHK)->hexdigest;
    close(CHK);

    # Clip the root directory name from the output file name:

    $file =~ s/^$ROOT\///;

    # Increment counters:

    $lines++;
    $pathlen = length($file);
    $maxpathlen = ($pathlen > $maxpathlen)? $pathlen : $maxpathlen;

    printf $TMP "$sum  $file\n";

    return;
  }

#-----------------------------------------------------------------------------

sub runupper              # Force file spec to upper case
  { my ($pathlen);
    my ($sum,$file);

    $file = $File::Find::name;

    # No action if this is a directory:

    return if (-d $File::Find::name);

    # No action if this file matches anything in the exclusion list:

    foreach $string (@exclude)
      { return if ($File::Find::name =~ /$string/); }

    # Otherwise we get the MD5 checksum:

    $md5->new;      # Resets for next file;
    open(CHK,$file) || die "Couldn't open $file for reading ($!)";
    binmode(CHK);
    $sum = $md5->addfile(*CHK)->hexdigest;
    close(CHK);

    # Clip the root directory name from the output file name and force case:

    $file =~ s/^$ROOT\///;
    $file =~ tr/a-z/A-Z/;

    # Increment counters:

    $lines++;
    $pathlen = length($file);
    $maxpathlen = ($pathlen > $maxpathlen)? $pathlen : $maxpathlen;

    printf $TMP "$sum  $file\n";

    return;
  }

#-----------------------------------------------------------------------------

sub runlower              # Force file spec to lower case
  { my ($pathlen);
    my ($sum,$sile);

    $file = $File::Find::name;

    # No action if this is a directory:

    return if (-d $File::Find::name);

    # No action if this file matches anything in the exclusion list:

    foreach $string (@exclude)
      { return if ($File::Find::name =~ /$string/); }

    # Otherwise we get the MD5 checksum:

    $md5->new;      # Resets for next file;
    open(CHK,$file) || die "Couldn't open $file for reading ($!)";
    binmode(CHK);
    $sum = $md5->addfile(*CHK)->hexdigest;
    close(CHK);

    # Clip the root directory name from the output file name and force case:

    $file =~ s/^$ROOT\///;
    $file =~ tr/A-Z/a-z/;

    # Increment counters:

    $lines++;
    $pathlen = length($file);
    $maxpathlen = ($pathlen > $maxpathlen)? $pathlen : $maxpathlen;

    printf $TMP "$sum  $file\n";

    return;
  }

#-----------------------------------------------------------------------------

sub getvolid
  { local ($voldesc) = $_[0];    # Voldesc.cat file name
    my ($line);
    my ($id);

    open(VOL,$voldesc) || die "Could not open $voldesc for reading ($!)";

    $line = <VOL>;
    while ($line !~ /VOLUME_ID/)
      { $line = <VOL>; }

    $line =~ /VOLUME_ID\s*=\s*"(.+)"/;
    $id = $1;

    # Close the file and return the ID value:

    close(VOL);
    return $id;
  }
