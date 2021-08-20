*************************
PDS4 SPICE Kernel Bundles
*************************

Overview
========

   This section describes the structure and contents of a PDS SPICE
   bundle following the PDS4 standard produced by NAIF and.



Product Types
=============

   SPICE bundles will include products only of these types:

      * Product_Bundle
      * Product_Collection
      * Product_SPICE_Kernel (under "spice_kernels" directory)
      * Product_Document     (under "document" directory)
      * Product_Ancillary    (under "miscellaneous" directory)

Directory Structure, File naming, Product Types, and LIDs/LIDVIDs
==============================================================================

    <sc>_spice (bundle root directory)
    |
    | - bundle_<sc>_spice_v001.xml                  --> Product_Bundle
    |                                                   urn:nasa:pds:<sc>.spice::1.0
    |
    | - bundle_<sc>_spice_v002.xml                  --> Product_Bundle
    |                                                   urn:nasa:pds:<sc>.spice::2.0
    |
    | - bundle_<sc>_spice_v???.xml                  --> Product_Bundle
    |                                                   urn:nasa:pds:<sc>.spice::???.0
    | . . .
    |
    | - readme.txt
    |
    | - document
    | |
    | | - collection_document_v001.xml              --> Product_Collection
    | | - collection_document_inventory_v001.tab        urn:nasa:pds:<sc>.spice:document::1.0
    | |
    | | - collection_document_v002.xml              --> Product_Collection
    | | - collection_document_inventory_v002.tab        urn:nasa:pds:<sc>.spice:document::2.0
    | |
    | | - collection_document_v???.xml              --> Product_Collection
    | | - collection_document_inventory_v???.tab        urn:nasa:pds:<sc>.spice:document::???.0
    | |
    | | . . .
    | |
    | | - spiceds_v001.html
    | | - spiceds_v001.xml                          --> Product_Document
    | |                                                 urn:nasa:pds:<sc>.spice:document:spiceds::1.0
    | | - spiceds_v002.html
    | | - spiceds_v002.xml                          --> Product_Document
    | |                                                 urn:nasa:pds:<sc>.spice:document:spiceds::2.0
    | | - spiceds_v???.html
    | | - spiceds_v???.xml                          --> Product_Document
    | |                                                 urn:nasa:pds:<sc>.spice:document:spiceds::???.0
    | | . . .
    | |
    | + - (as needed) <other>
    |   |
    |   | - *.txt,*.pdf,*.html,*.gif[...]
    |   + - *.xml                                   --> Product_Document
    |                                                   urn:nasa:pds:<sc>.spice:document:<filename.ext>::1.0
    |
    | - miscellaneous
    | |
    | | - collection_miscellaneous_v001.xml         --> Product_Collection
    | | - collection_miscellaneous_inventory_v001.tab   urn:nasa:pds:<sc>.spice:miscellaneous::1.0
    | |
    | | - collection_miscellaneous_v002.xml         --> Product_Collection
    | | - collection_miscellaneous_inventory_v002.tab   urn:nasa:pds:<sc>.spice:miscellaneous::2.0
    | |
    | | - collection_miscellaneous_v???.xml         --> Product_Collection
    | | - collection_miscellaneous_inventory_v???.tab   urn:nasa:pds:<sc>.spice:miscellaneous::???.0
    | |
    | | . . .
    | |
    | | - checksum
    | | |
    | | |- checksum_v001.tab
    | | |- checksum_v001.xml                        --> Product_Ancillary (described as Checksum_Manifest)
    | | |                                               urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::1.0
    | | |- checksum_v002.tab
    | | |- checksum_v002.xml                        --> Product_Ancillary (described as Checksum_Manifest)
    | | |                                               urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::2.0
    | | | . . .
    | | |
    | | |- checksum_v???.tab
    | | +- checksum_v???.xml                        --> Product_Ancillary (described as Checksum_Manifest)
    | |                                                 urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::???.0
    | | - (as needed) orbnum
    | | |
    | | |- *.orb,*.nrb
    | | +- *.xml                                    --> Product_Ancillary (described as Table_Character)
    | |                                                 urn:nasa:pds:<sc>.spice:miscellaneous:orbnum_<filename.ext>::1.0
    | + - (as needed) <other>
    |   |
    |   |- *.txt
    |   |- *.xml                                    --> Product_Ancillary (described as Stream_Text)
    |   |                                               urn:nasa:pds:<sc>.spice:miscellaneous:<other>_<filename.ext>::1.0
    |   |
    |   |- *.tab
    |   |- *.xml                                    --> Product_Ancillary (described as Table_Character)
    |   |                                               urn:nasa:pds:<sc>.spice:miscellaneous:<other>_<filename.ext>::1.0
    |   |
    |   |- *.pdf,*.jpg,*.gif,*.png
    |   |- *.xml                                    --> Product_Ancillary (described as Encoded_Image)
    |   |                                               urn:nasa:pds:<sc>.spice:miscellaneous:<other>_<filename.ext>::1.0
    |   |
    |   |- *.zip
    |   +- *.xml                                    --> Product_Zipped
    |                                                   urn:nasa:pds:<sc>.spice:miscellaneous:<other>_<filename.ext>::1.0
    |
    +-- spice_kernels
      |
      | - collection_spice_kernels_v001.xml         --> Product_Collection
      | - collection_spice_kernels_inventory_v001.tab   urn:nasa:pds:<sc>.spice:spice_kernels::1.0
      |
      | - collection_spice_kernels_v002.xml         --> Product_Collection
      | - collection_spice_kernels_inventory_v002.tab   urn:nasa:pds:<sc>.spice:spice_kernels::2.0
      |
      | - collection_spice_kernels_v???.xml         --> Product_Collection
      | - collection_spice_kernels_inventory_v???.tab   urn:nasa:pds:<sc>.spice:spice_kernels::???.0
      |
      | . . .
      |
      | - ck
      | |
      | |- *.bc
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ck_<filename.ext>::1.0
      | - dbk
      | |
      | |- *.bdb
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:dbk_<filename.ext>::1.0
      | - dsk
      | |
      | |- *.bds
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:dsk_<filename.ext>::1.0
      | - ek
      | |
      | |- *.bes,*.bep,*.ten,*.tep
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ek_<filename.ext>::1.0
      | - fk
      | |
      | |- *.tf
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:fk_<filename.ext>::1.0
      | - ik
      | |
      | |- *.ti
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ik_<filename.ext>::1.0
      | - lsk
      | |
      | |- *.tls
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:lsk_<filename.ext>::1.0
      | - mk
      | |
      | |- <sc>_v01.tm
      | |- <sc>_v01.xml                             --> Product_SPICE_Kernel
      | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>::1.0
      | |- <sc>_v02.tm
      | |- <sc>_v02.xml                             --> Product_SPICE_Kernel
      | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>::2.0
      | |- <sc>_v??.tm
      | |- <sc>_v??.xml                             --> Product_SPICE_Kernel
      | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>::??.0
      | | . . .
      | |
      | |- <sc>_YYYY_v01.tm
      | |- <sc>_YYYY_v01.xml                         --> Product_SPICE_Kernel
      | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::1.0
      | |- <sc>_YYYY_v02.tm
      | |- <sc>_YYYY_v02.xml                         --> Product_SPICE_Kernel
      | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::2.0
      | |- <sc>_YYYY_v??.tm
      | +- <sc>_YYYY_v??.xml                         --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::??.0
      | - pck
      | |
      | |- *.tpc,*.bpc
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:pck_<filename.ext>::1.0
      | - sclk
      | |
      | |- *.tsc
      | +- *.xml                                    --> Product_SPICE_Kernel
      |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:sclk_<filename.ext>::1.0
      + - spk
        |
        |- *.bsp
        +- *.xml                                    --> Product_SPICE_Kernel
                                                        urn:nasa:pds:<sc>.spice:spice_kernels:spk_<filename.ext>::1.0

Where:

   -  <sc> is the short s/c name or acronym (e.g. maven, ladee, etc.)

   -  ?? and ??? are two or three digit version numbers

   -  Either the whole mission ("<sc>_v??.tm") or yearly
      ("<sc>_YYYY_v??.tm") may be included.

   -  Any kernel type subdirectories not applicable for the mission in
      question may be omitted.

   -  Additional products of file types that are allowed for
      Product_Ancillary may be provided in subdirectories under
      "miscellaneous". To be acceptable for archiving these products
      should contain types of ancillary information similar to those
      provided in the "extras" directory of the PDS3 SPICE data sets.

   -  Additional products of file types that are allowed for
      Product_Document may be provided in subdirectories under
      "document".


LID/LIDVID Construction Rules
==============================================================================

*  the initial part of the LIDs for NASA missions will be
   "urn:nasa:pds:<sc>.spice:" where <sc> is the short s/c name or
   acronym (e.g. maven, ladee, etc.), e.g.:

      urn:nasa:pds:maven.spice:


*  LIDs for

      -  SPICE kernels under "spice_kernels" *except* MKs <sc>_v??.tm
         and <sc>_YYYY_v??.tm

      -  ancillary products under "miscellaneous" *except* checksum
         tables checksum_v???.tab

      -  documents under "document" *except* spiceds_v???.html

   will include the directory path and the full file name with
   extension and VIDs will always be set to 1, e.g.:

      miscellaneous/orbnum/maven_orb1.orb               urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
      miscellaneous/orbnum/maven_orb2.orb               urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb2.orb::1.0

      spice_kernels/lsk/naif0010.tls                    urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0010.tls::1.0
      spice_kernels/lsk/naif0011.tls                    urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0

      spice_kernels/spk/de430.bsp                       urn:nasa:pds:maven.spice:spice_kernels:spk_de430.bsp::1.0
      spice_kernels/spk/de431.bsp                       urn:nasa:pds:maven.spice:spice_kernels:spk_de431.bsp::1.0


*  LIDs for

      -  MKs (<sc>_v??.tm and <sc>_YYYY_v??.tm)

      -  checksum tables (checksum_v???.tab)

      -  primary SPICE archive description documents
         (spiceds_v???.html)

   will include the directory path and the file name up to the version
   part and VIDs will always be set to the version part from the file
   name, for example:

      spice_kernels/mk/maven_v01.tm                     urn:nasa:pds:maven.spice:spice_kernels:mk_maven::1.0
      spice_kernels/mk/maven_v02.tm                     urn:nasa:pds:maven.spice:spice_kernels:mk_maven::2.0

      spice_kernels/mk/maven_2014_v01.tm                urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2014::1.0
      spice_kernels/mk/maven_2014_v02.tm                urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2014::2.0

      miscellaneous/checksum/checksum_v001.tab          urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
      miscellaneous/checksum/checksum_v002.tab          urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::2.0

      document/spiceds_v001.html                        urn:nasa:pds:maven.spice:document:spiceds::1.0
      document/spiceds_v002.html                        urn:nasa:pds:maven.spice:document:spiceds::2.0


+  LIDs for

      -  SPICE document collection products

      -  SPICE miscellaneous collection products

      -  SPICE kernels collection products

   will include only the subdirectory name and VIDs will always be set to
   the version part from the file name, for example:

      document/collection_document_v001.xml             urn:nasa:pds:maven.spice:document::1.0
      document/collection_document_v002.xml             urn:nasa:pds:maven.spice:document::2.0

      miscellaneous/collection_miscellaneous_v001.xml   urn:nasa:pds:maven.spice:miscellaneous::1.0
      miscellaneous/collection_miscellaneous_v002.xml   urn:nasa:pds:maven.spice:miscellaneous::2.0

      spice_kernels/collection_spice_kernels_v001.xml   urn:nasa:pds:maven.spice:spice_kernels::1.0
      spice_kernels/collection_spice_kernels_v002.xml   urn:nasa:pds:maven.spice:spice_kernels::2.0


+  LIDs for

      -  all SPICE bundle products

   will include only the initial part of the LID and VIDs will always
   be set to the version part from the file name, for example:

      bundle_maven_spice_v001.xml                        urn:nasa:pds:maven.spice::1.0
      bundle_maven_spice_v002.xml                        urn:nasa:pds:maven.spice::2.0



Product Reference and Collection Inventory Construction Rules
==============================================================================

-  all products' Context_Area includes only Mission (*_to_investigation), Spacecraft
   (is_instrument_host), and one primary Target (*_to_target) LID
   references. These LIDs should be obtained from the
   coordinating PDS node or EN.

-  all products' Reference_List includes the latest primary SPICE
   archive description document LID reference (*_to_document) (*except*
   the primary SPICE archive description documents (spiceds_v???.html)
   which can't reference themselves)

-  each MK's Reference_List also includes LIDVID references for all kernels
   (data_to_associate) listed in the MK.

-  each collection inventory lists LIDVIDs of *all* non-collection
   products provided under collection's directory at the time when
   collection product was created. In a particular collection
   inventory, P is used only for newly added products (that don't
   appear in any of the collections with earlier versions) and S is
   used for products that have already been registered in a collection
   with an earlier version.

-  each Bundle label includes Bundle_Member_Entry'es only for the
   latest SPICE kernel collection LIDVID
   (bundle_has_spice_kernel_collection), the latest document collection
   LIDVID (bundle_has_document_collection) and the latest miscellaneous
   collection LIDVID (bundle_has_miscellaneous_collection). These
   collections have Primary statuses if they have not been registered
   in any earlier bundle versions. Otherwise they have Secondary
   statuses.


start_date_time and stop_date_time Assignment Rules
==============================================================================

-  start_date_time and stop_date_time appear in Context_Area/Time_Coordinates
   only in bundle, SPICE kernel collection, and SPICE kernel labels.

-  for kernels for which time boundaries can determined from the
   data (SPK, CK, etc) start_date_time and stop_date_time set to those
   boundaries

-  for kernels for which time boundaries cannot be determined from the
   data (LSK, SCLK, PCK, etc) start_date_time and stop_date_time set to
   the default mission time range (from launch to an arbitrary date many
   decades into the future, e.g. 2050-01-01)

-  for whole mission meta-kernels start_date_time and stop_date_time
   are set to the coverage provided by spacecraft SPK or CKs, at the
   discretion of the archive producer.

-  for yearly mission meta-kernels start_date_time and stop_date_time
   are set to the coverage from Jan 1 00:00 of the year to either the
   end of coverage provided by spacecraft SPK or CKs, or the end of the
   year (whichever is earlier)

-  for a SPICE collection the coverage is set to the boundaries of the
   combined coverage of the latest MKs that are part of this collection

-  for a SPICE bundle the coverage is set to the boundaries of the
   coverage of the SPICE collection that is its member.


RANDOM:

The SPICE Kenrel Bundle start and stop times are determined by the 
times of the Spice Kernels collection (the Miscellaneous collection contains
orbnum files that might be)

Miscellaneous collections Rules
==============================================================================

   The generation of a new checksum product is bound to the addition of a 
   SPICE kernel product in the SPICE Kernels collection, or an orbnum product.
   If none of these happen, the cehcksum file will not be generated.

Product set, label, LIDVID and inventory examples for MAVEN release 1 and 2
==============================================================================

   Below is an example of files, product types and LIDVIDs for the
   MAVEN 1st and 2nd releases. Inventory contents shows with "P" and
   "S" attributes. "+" as the first character on the line indicates
   files added in that release:


   Release 1 includes:

        1 document       -- spiceds_v001.html
        2 misc products  -- maven_orb1.orb, checksum_v001.tab
        3 kernels        -- naif0011.tls, maven_2015_v01.tm, maven_orb1.bsp

   ---------------------------------------------------------  -----------------------  ------------------------------------------------------------------
   File                                                       Product Type             LIDVID
        Inventory Contents
   ---------------------------------------------------------  -----------------------  ------------------------------------------------------------------

   ./bundle_maven_spice_v001.xml                              Product_Bundle           urn:nasa:pds:maven.spice::1.0
        P,urn:nasa:pds:maven.spice:document::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels::1.0
   ./readme.txt

   ./document/collection_document_v001.xml                    Product_Collection       urn:nasa:pds:maven.spice:document::1.0
   ./document/collection_document_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:document:spiceds::1.0

   ./document/spiceds_v001.xml                                Product_Document         urn:nasa:pds:maven.spice:document:spiceds::1.0
   ./document/spiceds_v001.html

   ./miscellaneous/collection_miscellaneous_v001.xml          Product_Collection       urn:nasa:pds:maven.spice:miscellaneous::1.0
   ./miscellaneous/collection_miscellaneous_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0

   ./miscellaneous/orbnum/maven_orb1.xml                      Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
   ./miscellaneous/orbnum/maven_orb1.orb

   ./miscellaneous/checksum/checksum_v001.xml                 Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
   ./miscellaneous/checksum/checksum_v001.tab

   ./spice_kernels/collection_spice_kernels_v001.xml          Product_Collection       urn:nasa:pds:maven.spice:spice_kernels::1.0
   ./spice_kernels/collection_spice_kernels_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb1.bsp::1.0

   ./spice_kernels/lsk/naif0011.xml                           Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0
   ./spice_kernels/lsk/naif0011.tls

   ./spice_kernels/mk/maven_2015_v01.xml                      Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::1.0
   ./spice_kernels/mk/maven_2015_v01.tm

   ./spice_kernels/spk/maven_orb1.xml                         Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb1.bsp::1.0
   ./spice_kernels/spk/maven_orb1.bsp
   ---------------------------------------------------------  -----------------------  ------------------------------------------------------------------


Release 2 add:

        1 document       -- spiceds_v002.html
        2 misc products  -- maven_orb2.orb, checksum_v002.tab
        2 kernels        -- maven_2015_v02.tm, maven_orb2.bsp

   ---------------------------------------------------------  -----------------------  ------------------------------------------------------------------
   File                                                       Product Type             LIDVID
        Inventory Contents
   ---------------------------------------------------------  -----------------------  ------------------------------------------------------------------

   ./bundle_maven_spice_v001.xml                              Product_Bundle           urn:nasa:pds:maven.spice::1.0
        P,urn:nasa:pds:maven.spice:document::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels::1.0
+  ./bundle_maven_spice_v002.xml                              Product_Bundle           urn:nasa:pds:maven.spice::2.0
        P,urn:nasa:pds:maven.spice:document::2.0
        P,urn:nasa:pds:maven.spice:miscellaneous::2.0
        P,urn:nasa:pds:maven.spice:spice_kernels::2.0
   ./readme.txt

   ./document/collection_document_v001.xml                    Product_Collection       urn:nasa:pds:maven.spice:document::1.0
   ./document/collection_document_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:document:spiceds::1.0
+  ./document/collection_document_v002.xml                    Product_Collection       urn:nasa:pds:maven.spice:document::2.0
+  ./document/collection_document_inventory_v002.tab
        S,urn:nasa:pds:maven.spice:document:spiceds::1.0
        P,urn:nasa:pds:maven.spice:document:spiceds::2.0

   ./document/spiceds_v001.xml                                 Product_Document        urn:nasa:pds:maven.spice:document:spiceds::1.0
   ./document/spiceds_v001.html
+  ./document/spiceds_v002.xml                                 Product_Document        urn:nasa:pds:maven.spice:document:spiceds::2.0
+  ./document/spiceds_v002.html

   ./miscellaneous/collection_miscellaneous_v001.xml           Product_Collection      urn:nasa:pds:maven.spice:miscellaneous::1.0
   ./miscellaneous/collection_miscellaneous_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
+  ./miscellaneous/collection_miscellaneous_v002.xml           Product_Collection      urn:nasa:pds:maven.spice:miscellaneous::2.0
+  ./miscellaneous/collection_miscellaneous_inventory_v002.tab
        S,urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb2.orb::1.0
        S,urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
        P,urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::2.0

   ./miscellaneous/orbnum/maven_orb1.xml                      Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
   ./miscellaneous/orbnum/maven_orb1.orb
+  ./miscellaneous/orbnum/maven_orb2.xml                      Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb2.orb::1.0
+  ./miscellaneous/orbnum/maven_orb2.orb

   ./miscellaneous/checksum/checksum_v001.xml                 Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
   ./miscellaneous/checksum/checksum_v001.tab
+  ./miscellaneous/checksum/checksum_v002.xml                 Product_Ancillary/Table  urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::2.0
+  ./miscellaneous/checksum/checksum_v002.tab

   ./spice_kernels/collection_spice_kernels_v001.xml          Product_Collection       urn:nasa:pds:maven.spice:spice_kernels::1.0
   ./spice_kernels/collection_spice_kernels_inventory_v001.tab
        P,urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb1.bsp::1.0
+  ./spice_kernels/collection_spice_kernels_v002.xml          Product_Collection       urn:nasa:pds:maven.spice:spice_kernels::2.0
+  ./spice_kernels/collection_spice_kernels_inventory_v002.tab
        S,urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0
        S,urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::2.0
        S,urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb1.bsp::1.0
        P,urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb2.bsp::1.0

   ./spice_kernels/lsk/naif0011.xml                           Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:lsk_naif0011.tls::1.0
   ./spice_kernels/lsk/naif0011.tls

   ./spice_kernels/mk/maven_2015_v01.xml                      Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::1.0
   ./spice_kernels/mk/maven_2015_v01.tm
+  ./spice_kernels/mk/maven_2015_v02.xml                      Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2015::2.0
+  ./spice_kernels/mk/maven_2015_v02.tm

   ./spice_kernels/spk/maven_orb1.xml                         Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb1.bsp::1.0
   ./spice_kernels/spk/maven_orb1.bsp
+  ./spice_kernels/spk/maven_orb2.xml                         Product_SPICE_Kernel     urn:nasa:pds:maven.spice:spice_kernels:spk_maven_orb2.bsp::1.0
+  ./spice_kernels/spk/maven_orb2.bsp
