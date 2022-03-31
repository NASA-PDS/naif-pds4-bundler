NAIF's Approach to SPICE Kernel Archive Preparation
===================================================

NAIF's approach to creating SPICE archives can be summarized by this
statement:

    All SPICE data for a given mission are archived as UNIX
    text and binary files(1) in a single, accumulating archive
    on a single virtual volume(2) having the same
    directory structure(3), the same set of meta information
    files(4), data file labels with the same structure(5), and
    archive documents with the same structure(6) as all SPICE archives
    produced by NAIF(7).

Each of the points identified in this statement using a number in
parentheses is briefly explained below:

    1. *All SPICE data are archived as UNIX text and binary kernels,
       meaning that all text kernels have lines terminated by* ``<LF>`` *(line feed)
       only and all binary kernels are in* ``BIG-IEEE`` *(big-endian) binary
       format.*

       Following this requirement ensures consistency across all SPICE
       archives and usability of the data for both future users and
       the archive distribution and manipulation tools at the NAIF
       Node of the PDS. If conversion of text kernels with
       lines terminated by ``<CR><LF>`` (carriage return and line feed)
       and binary kernels in ``LTL-IEEE`` (little-endian) format to the
       required format is needed, NAIF provides a utility program called ``BINGO``,
       available on the "Utilities"s page on the NAIF web site.

    2. *All SPICE data for a given mission get archived in a single
       accumulating archive bundle on a single virtual volume.*

       There is no need to break SPICE data for a given mission into
       multiple bundles based on the mission phases (as was done by
       NEAR), kernel types (as was done in other PDS3 data sets produced
       by other nodes), data producers, different observers (spacecrafts)
       in a mission or in any other way. Doing so
       leads to duplication of data, extra effort in preparing
       multiple marginally different copies of meta-information files,
       and, most importantly, complicates the lives of future users
       who, in most cases, prefer to get all SPICE data for a mission
       from one place.

       The Bundle name for this single archive is usually set to
       ``<sc>_spice`` where ``<sc>`` is the spacecraft acronym. For example
       for MAVEN, ``maven_spice``, for ExoMars 2016, ``em16_spice``, and
       so on.

       All SPICE bundles -- even those for the missions that have
       ended -- are accumulating, which means that if/when additional
       SPICE data become available, these data are added to the same
       archive. For on-going missions the data that is being added is
       usually covering the next period of time; for past missions the
       data that is being added usually provides a better trajectory
       solution, a better attitude estimate, an instrument parameters
       update, or fixes liens. New additions are called releases or
       increments. SPICE bundles do not have a specific file to record
       releases, nevertheless the version of the bundle label is equivalent
       to the bundle release. Checksum files in the Miscellaneous collection
       are also a good resource to understand the files included in each
       release.

       Once in the archive, no files are removed from it or replaced with
       different versions with the same name. Instead, new files superseding
       already archived files are added to the archive. For kernels, they are
       given distinct names and the fact that they supersede previously archived
       kernels is reflected in the meta-information files
       (SPICEDS and meta-kernel files).

    3. *All SPICE archives have the following PDS-compliant directory
       structure*::

          <sc>_spice           bundle root directory
           |
           |-- document        contains the SPICE archive description file
           |
           |-- miscellaneous   contains the miscellaneous collection subdirectories
           | |
           | |-- checksum      contains checksum files
           | +-- orbnum*       contains orbit number files
           |
           +-- spice_kernels   contains kernel type subdirectories
             |
             |-- ck            contains binary Camera-Matrix kernels (CKs)
             |-- dbk*          contains binary database kernels (DKBs)
             |-- dsk*          contains binary digital shape kernels (DSKs)
             |-- ek*           contains text event kernels (EKs)
             |-- fk            contains text frame kernels (FKs)
             |-- ik            contains text instrument kernels (IKs)
             |-- lsk           contains text leapseconds kernels (IKs)
             |-- mk            contains meta-kernels (MKs)
             |-- pck           contains text and/or binary planetary constant kernels (PCKs)
             |-- sclk          contains text spacecraft clock kernels (SCLKs)
             +-- spk           contains binary spacecraft kernels (SPKs)

       where the ``<sc>`` part is formed as described above (for
       example, for MAVEN it is ``maven_spice``). Elements with ``*`` are
       present if needed.

       The ``miscellaneous`` directory may contain additional subdirectories
       to store additional value-added, non-kernel files such as
       ORBNUM files.

       The ``document`` directory may (but does not have to) contain
       additional subdirectories for additional documents or document
       sets.


    4. *All SPICE data have the following meta-information files, most
       of which are required by PDS standards*::

          bundle_<sc>_spice_v???.xml                                  PDS4 bundle label
          readme.txt                                                  readme in text format
          document/collection_document_v???.xml                       document collection labels
          document/collection_document_inventory_v???.tab             document inventory tables
          document/spiceds_v???.html                                  SPICE archive description document
          document/spiceds_v???.xml                                   SPICE archive description label
          miscellaneous/collection_miscellaneous_v???.xml             miscellaneous collection labels
          miscellaneous/collection_miscellaneous_inventory_v???.tab   miscellaneous inventory tables
          miscellaneous/*/*.xml                                       XML labels, 1 per checksum and ORBNUM
          spice_kernels/collection_spice_kernels_v???.xml             SPICE kernels collection labels
          spice_kernels/collection_spice_kernels_inventory_v???.tab   SOUCE kernels inventory tables
          spice_kernels/*/*.xml                                       XML labels, 1 per kernel

       where the ``<sc>`` part is formed as described above (for example, for
       MAVEN it is ``maven_spice``). Elements with ``???`` have one file
       per archive release with ``???`` replaced with the document version
       number.

    5. *All SPICE kernels included in all SPICE archives are labeled
       with PDS4 XML labels*.

       Templates for different PDS Information Model versions of SPICE kernel
       labels (and other labels) are provided with the NAIF PDS4 Bundler.

    6. *All SPICE archives include a SPICE Description document (SPICEDS) that
       provides all the required information to describe in detail the SPICE
       archive*.

       Examples of different SPICEDS that can be used as references are
       provided with the NAIF PDS4 Bundler.

    7. While experts on PDS standards can (and did during
       peer-reviews) find a number of things about SPICE archives
       that need improvement or even correcting, NAIF continues to
       carry on with the archiving approach that it established and
       polished over 20+ years of creating PDS3 SPICE data sets and over
       5+ years of creating PDS4 SPICE archive bundles. Applying
       this approach without major deviations results in archives
       that truly look and feel the same from mission to mission. This
       helps both the users of the data who can count on finding
       archives with the same structure, and the NAIF node staff who
       in most cases are the people providing expert advice about
       SPICE kernel archives.

For the reasons noted above, please carefully follow the
instructions provided in this chapter and use the NAIF PDS4 Bundler
software package.
