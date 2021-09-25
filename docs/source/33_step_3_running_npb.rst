Step 3: Running NAIF PDS4 Bundler
=================================







   Brief guidelines on how to set up a template for the keywords that
   cannot (or should not) be set using the file data are provided below.
   While reading these guidelines, it may be helpful to look at the
   examples of MAKLABEL templates for various missions that are included in
   the ``examples/templates'' directory of this package.

       --   MISSION_NAME

            MISSION_NAME must be set in the default section to the value of
            MISSION_NAME specified in ``mission.cat''. (See MRO template
            for examples.)

       --   DATA_SET_ID

            DATA_SET_ID must be set in the default section to the value of
            DATA_SET_ID specified in ``spiceds.cat''. (See MRO template for
            examples.)

       --   TARGET_NAME

            TARGET_NAME must be set in the default section to the name or
            the list of names of the mission's primary target(s) as
            specified in the target catalog files. (See MRO, DS1 and SDU
            templates for examples.)

            If the mission does not have a primary target or it has too
            many targets, TARGET_NAME can be set in the default section to
            "N/A". (See the CASSINI template for an example.)

       --   SOURCE_PRODUCT_ID

            SOURCE_PRODUCT_ID can be set in the default section to "N/A".

       --   NOTE

            NOTE can be set in the default section to "See comments in the
            file for details".

       --   PRODUCT_VERSION_TYPE

            Since the majority of archived kernels usually contain
            reconstructed data, PRODUCT_VERSION_TYPE should be set in the
            default section to "ACTUAL". An optional section with tag
            PREDICT setting PRODUCT_VERSION_TYPE to "PREDICT" can be
            included to allow putting this value into the labels for files
            with predicted data. (See MRO template for examples.)

       --   SPACECRAFT_NAME

            If a single spacecraft is associated with the mission,
            SPACECRAFT_NAME must be set in the default section to the value
            of INSTRUMENT_HOST_NAME specified in ``insthost.cat''. (See MRO
            template for examples.)

            If more than one spacecraft is associated with the mission,
            SPACECRAFT_NAME must be set in the default section to a list of
            values of INSTRUMENT_HOST_NAME specified in all instrument host
            catalog files. Then a set of optional sections, in each of
            which SPACECRAFT_NAME is set to an individual
            INSTRUMENT_HOST_NAME, should be added; the spacecraft acronyms
            can be used as tags for these sections. One of these tags
            should be used when MAKLABEL is run to make labels for kernels
            that apply for only one spacecraft. For the kernels that apply
            to all spacecraft, these tags will be omitted resulting in the
            list of all spacecraft names specified in the default section
            being put into the label. (See the Deep Impact template for
            examples.)

       --   PRODUCER_ID

            A set of optional sections, in each of which PRODUCER_ID is set
            to a particular producer ID, must be set up; the producer
            acronyms can be used as tags for these sections. One of these
            tags should be used when MAKLABEL is run to make labels for
            kernels created by a particular producer. (See the MRO template
            for examples.)

       --   INSTRUMENT_NAME and PLATFORM_OR_MOUNTING_NAME

            A set of optional sections, one for each instrument, setting
            INSTRUMENT_NAME to the value of INSTRUMENT_NAME from that
            instrument's catalog file and setting PLATFORM_OR_MOUNTING_NAME
            to the name of the platform on which the instrument is mounted,
            must be set up; the instrument acronyms can be used as tags for
            these sections. One of these tags should be used when MAKLABEL
            is run to make labels for kernels that apply to a particular
            instrument (normally only for IKs). (See the Cassini template
            for examples.)

       --   MISSION_PHASE_NAME

            MISSION_PHASE_NAME should be set in the default section to
            "N/A" to be used for any kernels that cover the whole mission
            or for which the notion of coverage is not applicable. (See the
            MRO template for examples.)

            Then a set of optional sections, one for each of the mission
            phases defined in the DESCRIPTION section of ``mission.cat'',
            setting MISSION_PHASE_NAME to a particular mission phase name,
            must be set up; an abbreviated mission phase name can be used
            as tags for these sections. One of these tags should be used
            when MAKLABEL is run to make labels for kernels the coverage of
            which falls completely within that mission phase. (See the MRO
            template for examples.)

            Additional optional sections setting MISSION_PHASE_NAME to
            lists containing names for two or more adjacent mission phases
            may need to be created if some kernels have coverage that spans
            mission phase boundaries. (See MRO template for examples.)

   Usually the MAKLABEL template prepared and used to label files in the
   first release can be used without changes for all subsequent releases.
   In some cases though, for example when data from a new data producer
   need to be added to the archive or when an additional mission phase was
   added to the mission time line, the template may need to be augmented
   with additional optional sections.


Preparing Kernel List File

   After the MAKLABEL template has been prepared, the next step is to put
   together a kernel list file that, as the name suggests, lists all
   kernels that will be added to the archive in the release that is being
   prepared. The list file is the main input to the ``label_them_all.pl''
   script and, in addition to listing kernels, provides a set of MAKLABEL
   options (tags from the template) and a description for each of the files
   as well as some general information such as the data set ID, release ID,
   etc. (Note that a concatenation of all kernels lists for an archive is
   used as the primary input to the script that generates index files,
   ``xfer_index.pl'', discussed later in this document.)

   The kernel list file for a particular release must have the following
   content and structure:

      DATE = <date>
      SPACECRAFT = <s/c>
      NAIFER = <full name>
      PHONE = <phone>
      EMAIL = <e-mail>
      VOLUMEID = <volume id>
      RELEASE_ID   = <number>
      RELEASE_DATE = <YYYY-MM-DD>
      EOH
      FILE             = <name of file 1>
      MAKLABEL_OPTIONS = <MAKLABEL options for file 1>
      DESCRIPTION      = <description of file 1, on a single line!>
      FILE             = <name of file 2>
      MAKLABEL_OPTIONS = <MAKLABEL options for file 2>
      DESCRIPTION      = <description of file 2, on a single line!>
      ...
      FILE             = <name of file N>
      MAKLABEL_OPTIONS = <MAKLABEL options for file N>
      DESCRIPTION      = <description of file N, on a single line!>

   The first five keywords -- DATE, SPACECRAFT, NAIFER, PHONE, EMAIL -- and
   the ``EOH'' end-of-the-header marker are optional and are included to
   provide identification information. These keywords are not used by the
   ``label_them_all.pl'' or ``xfer_index.pl'' scripts. They are a ``carry
   over'' required by an earlier incarnation of NAIF's archive scripts.

   The VOLUMEID, RELEASE_ID, and RELEASE_DATE keywords are required and
   must be set as follows: VOLUMEID must be set to the lowercased version
   of the volume ID (for example ``mgsp_1000'' for MGS), RELEASE_ID must be
   set to the release ID number (for example ``0001'' for release 1), and
   RELEASE_DATE must be set to the date on which the data will be released
   to the public (for example ``2007-07-27'' for July 27, 2007.)

   The rest of the kernel list file must provide triplets of lines, one for
   each of the files that constitute the release, containing FILE,
   MAKLABEL_OPTIONS, and DESCRIPTION keywords. The FILE line must always be
   first, followed by the MAKLABEL_OPTIONS line followed by the DESCRIPTION
   line.

   The FILE keyword must provide the file name relative to the volumes's
   root directory (for example ``data/spk/de403.bsp'').

   The MAKLABEL_OPTIONS keyword must provide all MAKLABEL option tags
   applicable to the file named in the preceding FILE keyword. The option
   tags must be delimited by one or more spaces and will be passed ``as
   is'' to the MAKLABEL program. If no options are applicable to a file,
   MAKLABEL_OPTIONS can be set to blank but the line containing it must
   still be present in the list file, following the FILE keyword line.

   The DESCRIPTION keyword must provide a brief description of the file;
   this description will be inserted in the file label to replace the
   generic description generated by the MAKLABEL program. The value must be
   on the same line as the keyword and must not ``spill'' over onto the
   next line(s). The length of the description is not limited. DESCRIPTION
   can be set to blank but the line containing it must still be present in
   the list file, following the MAKLABEL_OPTIONS keyword line. When
   description is set to blank, "N/A" is placed in the label.

   The list file may contain blank lines as long as they are not placed
   between the lines in each of the triplets.

   Normally the kernel list files are kept in the data set root directory
   of the staging area.

   The package accompanying this document contains the
   ``examples/listfiles'' directory with numerous examples of kernel list
   files for various missions. These list files can be used as references
   or even as the starting point for preparing kernel list files for a new
   archive.


Running the Labeling Script

   Once a kernel list file has been prepared the ``label_them_all.pl''
   script can be run to generate labels for staged kernels.

   Before doing that it should be verified that each of the staged text
   kernels has an architecture/type token -- ``KPL/LSK'', ``KPL/SCLK'',
   ``KPL/PCK'', and so on -- on the first line of the file. It is required
   for the MAKLABEL and ARCHTYPE programs, as described in the programs'
   User's Guides. If the architecture/type token is missing in the file, it
   must be added using a text editor.


   If the script did not generate labels for some of the files, the
   problems that caused the error(s) need to be fixed and the script needs
   to be re-run to make these labels. Depending on how many files are
   listed in the list file it may be practical to re-generate labels for
   all kernels, including those for which the labels were generated
   successfully. To take this route, the labels that were made need to be
   deleted and the script needs to be re-run with the same list file as
   input. Sometimes re-labeling all files is not practical because for
   large files it can take quite a bit of time. In these cases a copy of
   the list can be made and edited down to include only the files for which
   the labels were not made. Then the script can be re-run with this
   reduced list to generate labels just for these files. If this was
   successful, the reduced list should be deleted to avoid using it instead
   of the original list in future steps.

   When labels for all files in the list have been generated it makes sense
   to visually inspect some (or even all) of them. In some cases doing this
   allows one to catch typos and incorrect information in the keyword
   values set via the MAKLABEL template, incorrect information in
   descriptions, and incorrect assignments of MAKLABEL option tags provided
   in the list file. One of the ways to look at the labels is simply using
   Unix ``more'' to see them, like this:

      foreach ( `grep FILE listfile | sed 's/^FILE *= *//g' )
      echo label for $FF
      more $FF:r.lbl
      end

   If any problems are found as the result of this examination, their
   causes should be fixed and just the labels affected -- or all labels if
   it is easier -- should be re-generated by re-running the script.



Step 5: Checking the Result and Finishing up
============================================

   With the labels and index files in hand the archive release is nearly
   done. The only things left to do are finishing staging new and updated
   meta-information files, performing a set of final checks on the staged
   files, adding <CR>s to all meta-information files that require them,
   copying all new data files and new and updated meta-information files to
   the final archive area, and generating the MD5 checksum table and
   accompanying label for the final archive area.

Doing Final Checks

   Once all kernel and meta-information files have been staged the final
   set of checks should be performed to verify that all required files and
   directories are present and comply with basic PDS requirements and that
   the staged kernels files have proper binary and text format. The
   ``check_everything.csh'' script provided in the package performs a
   series of such checks.

   The script must be started from the volume's root directory without any
   arguments, as follows:

      > check_everything.csh

   The script verifies that the volume has the required directory
   structure, checks for presence of all required meta-information files,
   checks each meta-information file for long lines and non-printing
   characters, checks that text kernels are in Unix format and do not
   contain non-printing characters, and checks that binary kernels have
   BIG-IEEE binary format. For each checked directory or file it prints
   confirmation and, in case of an error, diagnostic information to the
   screen.

   The script only works on volumes that have lowercase directory and file
   names.

   To check the binary file format the script uses the BFF utility program
   mentioned above.

   To check for non-printing characters the script uses a program called
   BADCHAR, the C source code for which -- ``badchar.c'' -- is provided in
   the ``scripts'' directory of the package. BADCHAR, which is a very
   simple ANSI C program without any external dependencies, can be compiled
   on any UNIX environment that has a C compiler as follows:

      > cc -o badchar badchar.c


Deploying to Final Archive Area

   After the checksum files have been generated, the new and updated
   archive-ready kernels and meta-information files should be copied from
   the staging area to the final archive area, from which the archive will
   be served to customers or delivered to the responsible PDS node. The way
   of copying the files should be the one that best fits the data
   preparer's hardware infrastructure -- ``scp'', ``rsync'', ``wget'',
   ``tar'', or simply ``cp''.

   NAIF has the staging and final archive area file systems mounted to the
   workstation on which archive preparation is done and uses ``tar'' to
   perform the copy. For example if the root directory of the staged MGS
   archive is located at

      /home/naif/staging/mgs-m-spice-6-v1.0/mgsp_1000

   and has under it the file

      files_to_copy.list

   listing the data and meta-information files that should be copied to the
   final archive directory located at

      /ftp/pub/naif/pds/data/mgs-m-spice-6-v1.0/mgsp_1000

   then this ``tar'' command can be used to perform the copy (the ``cd''
   and ``more'' commands are included to show that ``tar'' should be run
   from, and the file names in the list should be relative to, the volume's
   root directory in the staging area):

      > cd /home/naif/staging/mgs-m-spice-6-v1.0/mgsp_1000

      > more files_to_copy.list
      ./aareadme.htm
      ./aareadme.lbl
      ./aareadme.txt
      ./catalog/catinfo.txt
      ...
      ./dsindex.lbl
      ./dsindex.tab
      ...
      ./software/softinfo.txt
      ./voldesc.cat

      > tar cBf - `cat files_to_copy.list` | \
        (cd /ftp/pub/naif/pds/data/mgs-m-spice-6-v1.0/mgsp_1000; \
        tar xBf -)

   The only files that were not staged in the right place and, for this
   reason, were not copied to the right location in the final archive area
   are the PDS-D index table and its label -- ``dsindex.tab'' and
   ``dsindex.lbl''. It was suggested at the end of the ``Generating Index
   Files'' section above that these two files should be temporarily kept in
   the root directory of the volume. Doing so simplifies generating the
   ``files to copy'' and ``files to add <CRs>'' list files and the copy
   operation. As the final touch these two files must be moved to the
   directory that is one level above the volume root directory:

      > mv /ftp/pub/naif/pds/data/mgs-m-spice-6-v1.0/mgsp_1000/dsindex.*\
           /ftp/pub/naif/pds/data/mgs-m-spice-6-v1.0/

   For peace of mind, since at this point all kernels and meta-kernels are
   in the right place in the final archive area, it would make sense to
   verify all meta-kernels included in the archive using BRIEF run from the
   volume root directory in the final archive area like this:

      > brief extras/mk/*.tm

   BRIEF will display a summary for all SPK files in the archive and should
   generate no ``file could not be located'' errors.


Verifying the Final Archive using PDS Volume Validation Tools

   Although the Guide's instructions and scripts provide a lot of
   safeguards to ensure production of a fully PDS-compliant data set, many
   documents included in the archive have to be done ``by hand'' and for
   this reason are prone to errors. Because the ``check_everything.csh''
   script attempts to check only for a few selected kinds of errors that
   may result from manual editing (non-printing characters, long lines) the
   archive producer should validate the fully prepared SPICE archive using
   one of the tools provided by the PDS Engineering Node. The two tools
   currently available for this purpose are the Label Validation Tool
   (VTool) and the Online Volume Validation tool. While both tools perform
   the same basic task -- validate a PDS volume for PDS standards
   compliance -- they have very different interfaces: VTool is a command
   line application well suited for batch mode processing and customized
   report generation while the Online Volume Validation tool is a GUI
   application running in a Web browser; it is best for those who prefer
   visual interfaces.

   The VTool package can be obtained from the PDS web site:

      http://pds.jpl.nasa.gov/tools/label-validation-tool.shtml

   Once installed per instructions provided with the package, VTool can be
   run to generate the full validation report for the final archive as
   follows:

      > VTool -d <PDSDD> \
              -t <FULL_PATH_TO_DS> \
              -I <FULL_PATH_TO_DS/catalog> \
              -X <EXCLUDE_EXTENSIONS> \
              -s full
              -r <REPORTFILE> \

   where ``PDSDD'' is the location of the latest PDS data dictionary file
   (which can be obtained by following a link in the lower-left corner area
   of the ``Data Dictionary Lookup'' page on the PDS Web site),
   ``FULL_PATH_TO_DS'' is the full path to the final archive volume's root
   directory, ``FULL_PATH_TO_DS>/catalog'' is the full path to the final
   archive volume's catalog directory, ``EXCLUDE_EXTENSIONS'' is the list
   of file name extensions for files that should be excluded from
   validation, and ``REPORTFILE'' is the name of the output report file.

   The the list of extensions to be excluded from validation should include
   all SPICE kernel, meta-kernel, and orbit number file extensions,
   specifically:

      "*.bc","*.bdb","*.bep","*.bes","*.bpc","*.bsp","*.ten","*.tf",
      "*.ti","*.tls","*.tpc","*.tsc","*.nrb","*.orb","*.tm"

   Assuming that the full name of the latest PDS data dictionary file is
   ``/home/user/pds/datadictionary_1r75/pdsdd.full'', for the MGS archive
   example above the full VTool validation report could be generated as
   follows:

      > VTool \
        -d /home/user/pds/datadictionary_1r78/pdsdd.full \
        -t /ftp/pub/naif/pds/data/mro-m-spice-6-v1.0/mrosp_1000 \
        -I /ftp/pub/naif/pds/data/mro-m-spice-6-v1.0/mrosp_1000/catalog \
        -X "*.bc","*.bdb","*.bep","*.bes","*.bpc","*.bsp","*.ten","*.tf", \
           "*.ti","*.tls","*.tpc","*.tsc","*.nrb","*.orb","*.tm" \
        -s full
        -r /home/user/pds/mrosp_1000_full_vtool_report \

   The report file should be examined visually and/or ``grep''ed for errors
   and warnings, like this:

      > grep ERROR /home/user/pds/mrosp_1000_full_vtool_report
            ERROR  line 38: "CATALOG" contains the object "DATA...
            ERROR  line 38: "CATALOG" contains the object "DATA...
            ERROR  line 38: "CATALOG" contains the object "DATA...
      ...

      > grep WARNING /home/user/pds/mrosp_1000_full_vtool_report
        Severity Level                 WARNING
            WARNING  "aareadme.txt" is not a label. Could not f...
            WARNING  line 32: "NAIF" is not in the list of vali...
            WARNING  line 10: "MARS RECONNAISSANCE ORBITER SPIC...
            WARNING  The label fragment, "atalog/spice_hsk.cat"...
            WARNING  The label fragment, "atalog/person.cat", s...
      ...

   Normally VTool will generate one error ``"CATALOG" contains the object
   "DATA_SET_HOUSEKEEPING" which is neither required nor optional.'' and a
   few errors ``"CATALOG" contains the object "DATA_SET_RELEASE" which is
   neither required nor optional.'' These errors can be disregarded because
   the DATA_SET_HOUSEKEEPING and DATA_SET_RELEASE objects defined in the
   ``spice_hsk.cat'' and ``release.cat'' files and used in the PDS Central
   Node catalog were never officially folded into the PDS standards.

   There should be no other errors in the report. If any other errors are
   present they should be investigated and fixed before the archive is
   released. (The only exceptions from this requirement are any new, valid
   values for static keywords, such as MISSION_NAME, that have not yet been
   incorporated into the PDS data dictionary.)

   The report is also likely to contain many warnings. Most of these
   warnings can be disregarded because they have to do with the tool
   attempting to validate files without attached labels, finding new
   dynamic keyword values not present in the lists of suggested values, or
   detecting lines longer than 78 characters in the ``spice_hsk.cat'' file.
   Still the warnings should be examined to make sure that any problems not
   belonging to the categories above don't get overlooked.

   The Online Volume Validation tool is available at this URL:

      http://pdstools.arc.nasa.gov/pdsWeb/ManageDataSets.action

   After the tool is opened into a Java-enabled browser the final archive
   volume located on a local file system can be validated by picking the
   volume's root directory using the ``Validate Local Volume'' button. Once
   the tool has finished validation it will display its report in the same
   browser window. As with a VTool report the Online Volume Validation tool
   report must be examined for errors and warnings.

   Note that much like VTool, the Online Volume Validation tool will flag
   as errors certain things that are OK for a SPICE archive, specifically
   the absence of a detached label in the ``aareadme.txt'' file, long lines
   in the ``spice_hsk.cat'' file, presence of pointers to the
   ``DATA_SET_RELEASE'' and ``DATA_SET_HOUSEKEEPING'' objects in the
   ``voldesc.cat'' file. It will also display warnings about labeled text
   files and files in the ``extras'' directory not listed in the index, and
   new, unrecognized values for dynamic keywords. While these errors and
   warnings can be disregarded, all other errors should be investigated and
   fixed prior to releasing the data set.


Cleaning up the Staging Area

   After the archive is done it makes sense to do some cleanup in the
   staging area. The only thing that must be done there is removing <CR>s
   from all files to which they had been added. This can be done by running
   the ``remove_crs_from_files.csh'' script with the same list file that
   was used to add <CR>s:

      > remove_crs_from_files.csh files_to_add_crs.list

   It is important to remove <CR>s as soon as preparation of a data set
   release ends rather than doing it later, before the preparation of the
   next data set begins. Doing so keeps modification dates of the files
   from which <CR>s were removed on the same day when the data set release
   was finished, simplifying time based searches and listings when
   additional work is done in the staging area in the future.

   It is wise to not delete the data files and the value-added files from
   ``extras'' from the staging area. Keeping them serves as a backup copy
   and allows easier validation of the meta-kernels that will be added in
   future releases. All of the meta-information and auxiliary files should
   not be deleted, especially the individual data labels (``data/*/*.lbl'')
   and individual kernel list files, both of which will be required when
   index files for the next archive release will be generated.


Step 5: Packaging and Delivering the Archive to the NAIF Node
=============================================================

   If the project archive plan calls for delivery of the SPICE data set to
   the NAIF Node of the PDS, the data set producer can do it in two ways:

       1.   If the volume of the data to be delivered is relatively small
            (under 2 GB), either the whole data set or only the files that
            were updated or added in the last release can be packaged into
            a ``.tar'' file, which is then made available to NAIF staff.
            The tar file should contain the whole data set directory tree
            starting at the ``ds/'' level.

            For example, to make a ``.tar'' file containing the whole MGS
            data set, the following commands can be used (to first change
            to the final archive area and then to ``tar'' the whole archive
            directory tree):

              > cd /ftp/pub/naif/pds/data/
              > tar -cvf mgsp_1000.tar mgs-m-spice-6-v1.0

            To make a ``.tar'' file containing only additions and changes
            to the MGS data set from the latest release ``NNNN'' prepared
            in the last 7 days, the following commands can be used (to
            first change to the final archive area and then to ``tar'' all
            files that changed in the past 7 days under the archive
            directory tree):

              > cd /ftp/pub/naif/pds/data/
              > tar -cvf mgsp_1000_relNNNN.tar \
                `find mgs-m-spice-6-v1.0 -mtime -7 -print`

       2.   If the volume of the data to be delivered is large (greater
            than 2 GB), NAIF staff should be given access to the final
            archive area (or a copy of it), which NAIF staff will mirror
            using either ``wget'' or ``scp'' tools (depending on the kind
            of access that was provided).

   The kind of access to be given to NAIF staff is up to the data provider.
   Any of the following ways is acceptable:

       --   putting ``.tar'' file(s) or a copy of the final data set tree
            on an anonymous public FTP server or a public Web server

       --   putting ``.tar'' file(s) or a copy of the final data set tree
            on a password-protected FTP server or a Web server. In this
            case NAIF staff should be provided with an account and
            password.

       --   putting ``.tar'' file(s) or a copy of the final data set tree
            on a UNIX workstation, providing NAIF staff with an account on
            this workstation, and setting file permissions allowing read
            access to the data.
