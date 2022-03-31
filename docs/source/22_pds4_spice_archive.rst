PDS4 SPICE Kernel Archive Description
=====================================


Product Types
-------------

SPICE bundles will include products only of these types:

   * Product_Bundle
   * Product_Collection
   * Product_SPICE_Kernel (under the ``spice_kernels`` directory)
   * Product_Document     (under the ``document`` directory)
   * Product_Ancillary    (under the ``miscellaneous`` directory)


Directory Structure, File naming, Product Types, and LIDs/LIDVIDs
-----------------------------------------------------------------

Directory Structure
^^^^^^^^^^^^^^^^^^^

The Bundle root directory contains a Readme file and a Bundle label along with
the Bundle Collections.

The Readme file provides a summary of the content of the archive whereas Bundle
labels, provide a handful summary of different aspects of the archive, including
the archive release, that is equivalent to the Bundle label version.

A SPICE kernel archive bundle consists of three collections: the
*spice_kernels* collection, the *miscellaneous* collection, and the
*document* collection.

Note that every collection will have a number of Inventory File CVS
(Comma Separated Value) files and Collection XML labels.


SPICE Kernels Collection
^^^^^^^^^^^^^^^^^^^^^^^^

The ``spice_kernels`` collection follows a particular directory structure and
its products a particular file naming convention. The collection is composed
of a series of directories that contain SPICE kernels of each kernel type. Each
SPICE kernel product has its PDS4 label. These labels have the same file name
of the labeled SPICE kernel except for the extension, which will be ``.xml``.


Document Collection
^^^^^^^^^^^^^^^^^^^

The ``document`` collection contains all the versions of the SPICE Data Archive
description file (SPICEDS). These files are described in the section
:ref:`32_step_2_npb_setup:SPICE Data Set Catalog File`.


Miscellaneous Collection
^^^^^^^^^^^^^^^^^^^^^^^^

The ``miscellaneous`` collection contains checksum products under the
``checksum`` directory. These checksum files provide a table of MD5 sums for
all the files in the archive as of a particular archive version, including
checksums for all previous checksum files and their labels but excluding the
checksum for the checksum file itself and its label.

There should be a checksum product for each release of the archive. As for
any other archive product, the checksum product will have a label. These labels
have the same file name except for the extension, which will be ``.xml``.

In addition, the miscellaneous collection might contain orbit number files
(ORBNUM) under an ``orbnum`` directory with their corresponding ``.xml`` labels.
Any ORBNUM files go here because they are not SPICE kernels.

Other types of files are currently not envisaged for the miscellaneous
collection.


LIDs, VIDs, LIDVIDs, and File naming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Critical elements of PDS4 archives are the products' Logical Identifiers
(LID) and the products' Version Identifiers (VID).

A LID is a unique logical identifier that is assigned to each product,
collection, and bundle. The nicety is that the LID is not bound to the data
location and therefore is able to reference data uniquely. VIDs provides the
capability to version the data identified by a LID; LIDVID combines the LID and
the VID to provide a unique reference to a specific version of the data.

For SPICE kernel archives LIDs and LIDVIDs are closely related to the file name
and its location within the ``spice_kernels`` collection: for SPICE kernel
products, except for meta-kernels, the fourth element of the LID will be a
combination of the kernel type sub-directory and the kernel name itself.

SPICE kernel archives take advantage of LIDs and LIDVIDs in a particular way
given the nature of the SPICE kernels; in general the kernel file name contains
a version number that identifies the kernel as a unique file; this version is
considered part of the file name and not a version number per se. Hence, in an
archive it is common to find products with a file name LIDVID pair such as:

.. list-table:: SPICE kernel name - LIDVID examples
   :widths: 25 75
   :header-rows: 1

   * - File name
     - LIDVID
   * - em16_tgo_v01.tf
     - urn:esa:psa:em16_spice:spice_kernels:fk_em16_tgo_v01.tf::1.0
   * - em16_tgo_v02.tf
     - urn:esa:psa:em16_spice:spice_kernels:fk_em16_tgo_v02.tf::1.0


We will talk more about this in the following section. For now lets take a
look at the general directory tree of a SPICE kernel archive. In the following
diagram you will be able to see the directory structure along with an
indication on how files are named, their product type, and their LIDVID::

      <sc>_spice (bundle root directory)
       |
       |-- bundle_<sc>_spice_v001.xml                  --> Product_Bundle
       |                                                   urn:nasa:pds:<sc>.spice::1.0
       |
       |-- bundle_<sc>_spice_v002.xml                  --> Product_Bundle
       |                                                   urn:nasa:pds:<sc>.spice::2.0
       | . . .
       |
       |-- bundle_<sc>_spice_v???.xml                  --> Product_Bundle
       |                                                   urn:nasa:pds:<sc>.spice::???.0
       |-- readme.txt
       |
       |-- document
       | |
       | |-- collection_document_v001.xml              --> Product_Collection
       | |-- collection_document_inventory_v001.tab        urn:nasa:pds:<sc>.spice:document::1.0
       | |
       | |-- collection_document_v002.xml              --> Product_Collection
       | |-- collection_document_inventory_v002.tab        urn:nasa:pds:<sc>.spice:document::2.0
       | |
       | | . . .
       | |
       | |-- collection_document_v???.xml              --> Product_Collection
       | |-- collection_document_inventory_v???.tab        urn:nasa:pds:<sc>.spice:document::???.0
       | |
       | |-- spiceds_v001.html
       | |-- spiceds_v001.xml                          --> Product_Document
       | |                                                 urn:nasa:pds:<sc>.spice:document:spiceds::1.0
       | |-- spiceds_v002.html
       | |-- spiceds_v002.xml                          --> Product_Document
       | |                                                 urn:nasa:pds:<sc>.spice:document:spiceds::2.0
       | | . . .
       | |
       | |-- spiceds_v???.html
       | +-- spiceds_v???.xml                          --> Product_Document
       |                                                   urn:nasa:pds:<sc>.spice:document:spiceds::???.0
       |
       |-- miscellaneous
       | |
       | |-- collection_miscellaneous_v001.xml         --> Product_Collection
       | |-- collection_miscellaneous_inventory_v001.tab   urn:nasa:pds:<sc>.spice:miscellaneous::1.0
       | |
       | |-- collection_miscellaneous_v002.xml         --> Product_Collection
       | |-- collection_miscellaneous_inventory_v002.tab   urn:nasa:pds:<sc>.spice:miscellaneous::2.0
       | |
       | | . . .
       | |
       | |-- collection_miscellaneous_v???.xml         --> Product_Collection
       | |-- collection_miscellaneous_inventory_v???.tab   urn:nasa:pds:<sc>.spice:miscellaneous::???.0
       | |
       | |
       | |-- checksum
       | | |
       | | |-- checksum_v001.tab
       | | |-- checksum_v001.xml                       --> Product_Ancillary (described as Checksum_Manifest)
       | | |                                               urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::1.0
       | | |-- checksum_v002.tab
       | | |-- checksum_v002.xml                       --> Product_Ancillary (described as Checksum_Manifest)
       | | |                                               urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::2.0
       | | | . . .
       | | |
       | | |-- checksum_v???.tab
       | | +-- checksum_v???.xml                       --> Product_Ancillary (described as Checksum_Manifest)
       | |                                                 urn:nasa:pds:<sc>.spice:miscellaneous:checksum_checksum::???.0
       | +-- orbnum (as needed)
       |   |
       |   |-- *.orb,*.nrb
       |   +-- *.xml                                   --> Product_Ancillary (described as Table_Character)
       |
       +-- spice_kernels
         |
         | - collection_spice_kernels_v001.xml         --> Product_Collection
         | - collection_spice_kernels_inventory_v001.tab   urn:nasa:pds:<sc>.spice:spice_kernels::1.0
         |
         | - collection_spice_kernels_v002.xml         --> Product_Collection
         | - collection_spice_kernels_inventory_v002.tab   urn:nasa:pds:<sc>.spice:spice_kernels::2.0
         |
         | . . .
         |
         | - collection_spice_kernels_v???.xml         --> Product_Collection
         | - collection_spice_kernels_inventory_v???.tab   urn:nasa:pds:<sc>.spice:spice_kernels::???.0
         |
         |-- ck
         | |
         | |- *.bc
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ck_<filename.ext>::1.0
         |-- dbk (as needed)
         | |
         | |- *.bdb
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:dbk_<filename.ext>::1.0
         |-- dsk (as needed)
         | |
         | |- *.bds
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:dsk_<filename.ext>::1.0
         |-- ek (as needed)
         | |
         | |- *.bes,*.bep,*.ten,*.tep
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ek_<filename.ext>::1.0
         |-- fk
         | |
         | |- *.tf
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:fk_<filename.ext>::1.0
         |-- ik
         | |
         | |- *.ti
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:ik_<filename.ext>::1.0
         |-- lsk
         | |
         | |- *.tls
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:lsk_<filename.ext>::1.0
         |-- mk
         | |
         | |- <sc><_type>_v01.tm
         | |- <sc><_type>_v01.xml                      --> Product_SPICE_Kernel
         | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::1.0
         | |- <sc><_type>_v02.tm
         | |- <sc><_type>_v02.xml                      --> Product_SPICE_Kernel
         | |                                               urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::2.0
         | | . . .
         | |
         | |- <sc><_type>_v??.tm
         | +- <sc><_type>_v??.xml                      --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:mk_<sc>_YYYY::??.0
         |-- pck
         | |
         | |- *.tpc,*.bpc
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:pck_<filename.ext>::1.0
         |-- sclk
         | |
         | |- *.tsc
         | +- *.xml                                    --> Product_SPICE_Kernel
         |                                                 urn:nasa:pds:<sc>.spice:spice_kernels:sclk_<filename.ext>::1.0
         +-- spk
           |
           |- *.bsp
           +- *.xml                                    --> Product_SPICE_Kernel
                                                           urn:nasa:pds:<sc>.spice:spice_kernels:spk_<filename.ext>::1.0

Where:

   *  ``<sc>`` is the short s/c name or acronym (e.g. maven, ladee, etc.)

   *  ``??`` and ``???`` are two or three digit version numbers

   *  Several types of meta-kernel can be included specifying their type
      in the ``<_type>`` field. E.g. yearly meta-kernels will have a year
      in their type (``maven_2020_v01.tm``) as opposed to meta-kernels for the
      whole mission, that will not have a type field (``insight_v01.tm``.)

   *  Any kernel type subdirectories not applicable for the mission in
      question may be omitted.

   *  Additional products of file types that are allowed for
      Product_Ancillary may be provided in subdirectories under
      ``miscellaneous``. To be acceptable for archiving, these products
      should contain types of ancillary information similar to those
      provided in the ``extras`` directory of the PDS3 SPICE data sets.
      Please contact NAIF if you wish to add any of these.

   *  Additional products of file types that are allowed for
      Product_Document may be provided in subdirectories under
      ``document``. Please contact NAIF if you wish to add any of these.

The following sections will provide more information to fully understand the
tree diagram.


LID/LIDVID Construction Rules
-----------------------------

As specified in the previous section, LIDVIDs are constructed in a particular
way for SPICE kernel archives that might differ from what is indicated in the
PDS4 Standard documentation.

For all products, the initial part of the LIDs will be::

   urn:<agency>:<authority>:<sc>.spice:

where

   * ``<agency>`` is the mission's space agency (e.g. nasa, esa, etc.)
   * ``<authority>`` is the agency's archiving authority (e.g. pds, psa, etc.)
   * ``<sc>`` is the short s/c name or acronym (e.g. maven, em16, etc.) Note that
     some ESA PSA SPICE kernel bundles have ``<sc>_spice`` instead of
     ``<sc>.spice``. NAIF recommends to use ``<sc>.spice``

for example::

   urn:nasa:pds:maven.spice:
   urn:jaxa:darts:hayabusa2.spice:
   urn:esa:psa:em16_spice:

The rest of the LIDVID can be constructed in four different ways depending
on the product:

  * path and full file name in LID
  * path and file name without version in LID
  * subdirectory name only in LID
  * no file name in LID


Path and full file name in LID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

LIDs will include the directory path and the full file name with extension
and VIDs will always be set to 1. This applies to the following products:

    * SPICE kernels under ``spice_kernels`` **except** Meta-kernels
      ``<sc><_type>_v??.tm``

    * orbit number files under ``miscellaneous``

    * documents under ``document`` **except** ``spiceds_v???.html``

The rationale behind is that the versioning of SPICE kernels and orbnum files
is not linked to archive releases (usually is related to mission operations)
and therefore the file version might not be sequential given that it is not
necessary to release intermediate files that have been generated in between
archive releases::

      miscellaneous/orbnum/maven_orb1.orb   urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb1.orb::1.0
      miscellaneous/orbnum/maven_orb2.orb   urn:nasa:pds:maven.spice:miscellaneous:orbnum_maven_orb2.orb::1.0

      spice_kernels/fk/bc_mpo_v02.tf        urn:esa:psa:bc_spice:spice_kernels:fk_bc_mpo_v02.tf::1.0
      spice_kernels/fk/bc_mpo_v15.tf        urn:esa:psa:bc_spice:spice_kernels:fk_bc_mpo_v15.tf::1.0

      spice_kernels/spk/de430.bsp           urn:nasa:pds:maven.spice:spice_kernels:spk_de430.bsp::1.0
      spice_kernels/spk/de431.bsp           urn:nasa:pds:maven.spice:spice_kernels:spk_de431.bsp::1.0


Path and file name without version in LID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

LIDs will include the directory path and the file name up to the version part
and VIDs will always be set to the version part from the file name. This applies
to the following products.

    * Meta-kernels (``<sc><_type>_v??.tm``)

    * checksum tables (``checksum_v???.tab``)

    * SPICE archive description documents (``spiceds_v???.html``)

This particular set of files are specific to the archive and therefore they
are guaranteed to be sequential::

      spice_kernels/mk/maven_v01.tm              urn:nasa:pds:maven.spice:spice_kernels:mk_maven::1.0
      spice_kernels/mk/maven_v02.tm              urn:nasa:pds:maven.spice:spice_kernels:mk_maven::2.0

      spice_kernels/mk/maven_2014_v01.tm         urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2014::1.0
      spice_kernels/mk/maven_2014_v02.tm         urn:nasa:pds:maven.spice:spice_kernels:mk_maven_2014::2.0

      miscellaneous/checksum/checksum_v001.tab   urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::1.0
      miscellaneous/checksum/checksum_v002.tab   urn:nasa:pds:maven.spice:miscellaneous:checksum_checksum::2.0

      document/spiceds_v001.html                 urn:nasa:pds:maven.spice:document:spiceds::1.0
      document/spiceds_v002.html                 urn:nasa:pds:maven.spice:document:spiceds::2.0


Subdirectory name only in LID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

LIDs will include only the subdirectory name and VIDs will always be set to
the version part from the file name. This applies to the following products:

    *  SPICE document collection products

    *  SPICE miscellaneous collection products

    *  SPICE kernels collection products

In general these products are the label and the inventory files::

      document/collection_document_v001.xml             urn:nasa:pds:maven.spice:document::1.0
      document/collection_document_v002.xml             urn:nasa:pds:maven.spice:document::2.0

      miscellaneous/collection_miscellaneous_v001.xml   urn:nasa:pds:maven.spice:miscellaneous::1.0
      miscellaneous/collection_miscellaneous_v002.xml   urn:nasa:pds:maven.spice:miscellaneous::2.0

      spice_kernels/collection_spice_kernels_v001.xml   urn:nasa:pds:maven.spice:spice_kernels::1.0
      spice_kernels/collection_spice_kernels_v002.xml   urn:nasa:pds:maven.spice:spice_kernels::2.0


No file name in LID
^^^^^^^^^^^^^^^^^^^

LIDs will include only the initial part of the LID and VIDs will always be set
to the version part from the file name. This applies to the following products:

    * all SPICE bundle products

which is reduced to the bundle label::

      bundle_maven_spice_v001.xml   urn:nasa:pds:maven.spice::1.0
      bundle_maven_spice_v002.xml   urn:nasa:pds:maven.spice::2.0


Bundle Products Construction Rules
----------------------------------

Readme files cannot be overwritten (as for any other file in the archive)
or versioned. This means that when the Readme file is generated for the first
release of the archive, it will remain unchanged; make sure not to make
mistakes when writing that file and write it as generically as possible.
For example, do not specify the archive producer name, instead provide the
the archive producer organization name (usually the archiving authority.)

This is the reason why you will probably not see any reference to the
Miscellaneous collection in most readme files of NAIF archives: the
Miscellaneous collection was added after the several releases of the archive.


Product Reference and Collection Inventory Construction Rules
-------------------------------------------------------------

This set of rules applies to all the archive products:

    * all products' ``Context_Area`` includes only Mission (``*_to_investigation``),
      Spacecraft(s) (``is_instrument_host``), and Target(s) (``*_to_target``) LID
      references. These LIDs should be obtained from your archiving authority
      (the PDS coordinating node for NASA missions, PSA for ESA missions,
      DARTS for JAXA missions, etc.) or from the PDS Engineering Node.

    * All products' ``Reference_List`` includes the latest primary SPICE
      archive description document LID reference (``*_to_document``) (**except**
      the SPICE archive description documents (``spiceds_v???.html``)
      which can't reference themselves.)

    * Each Meta-kernel's Reference_List also includes LIDVID references for
      all kernels (``data_to_associate``) listed in the MK.

    * Each collection inventory lists LIDVIDs of **all** non-collection
      products provided under collection's directory at the time when the
      collection product was created. In a particular collection
      inventory, *P* is used only for newly added products (that don't
      appear in any of the collections with earlier versions) and *S* is
      used for products that have already been registered in a collection
      with an earlier version.

    * Each Bundle label includes Bundle_Member_Entry's only for the
      latest SPICE kernel collection LIDVID
      (``bundle_has_spice_kernel_collection``), the latest document collection
      LIDVID (``bundle_has_document_collection``) and the latest miscellaneous
      collection LIDVID (``bundle_has_miscellaneous_collection``). These
      collections have Primary statuses if they have not been registered
      in any earlier bundle versions. Otherwise they have Secondary
      statuses.


Product Coverage Assignment Rules
---------------------------------

Determination of the coverage for the different products that needs to be
recorded in the ``Contex_Area/Time Coordinates`` element of the product labels
is not straightforward; to comply with the NAIF standard, the following rules
must be followed:

    *  ``start_date_time`` and ``stop_date_time`` appear in
       ``Context_Area/Time_Coordinates`` only in bundle, SPICE kernel collection,
       Miscellaneous collection, SPICE kernel labels, checksum, and orbit
       number file labels

    *  for kernels for which time boundaries can be determined from the
       data (SPKs, CKs, binary PCKs, and DSKs) ``start_date_time`` and
       ``stop_date_time`` are set to those boundaries

    *  for kernels for which time boundaries cannot be determined from the
       data (LSKs, SCLKs, text PCKs, FKs and IKs) ``start_date_time`` and
       ``stop_date_time`` are set to the default mission time range (from
       launch to an arbitrary date many decades into the future, e.g.
       ``2050-01-01``)

    *  for whole mission meta-kernels ``start_date_time`` and ``stop_date_time``
       are set to the coverage provided by spacecraft SPK, CKs, or to other
       dates at the discretion of the archive producer. These other dates might
       be required for missions whose SPks and CKs do not explicitly cover the
       dates required by the archive, e.g.: a lander mission with a fixed
       position provided by an SPK with extended coverage

    *  for yearly mission meta-kernels ``start_date_time`` and ``stop_date_time``
       are set to the coverage from Jan 1 00:00 of the year to either the
       end of coverage provided by spacecraft SPK or CKs, or the end of the
       year (whichever is earlier)

    *  for a SPICE collection the coverage is set to the boundaries of the
       combined coverage of the latest MKs that are part of this collection

    *  for a Miscellaneous collection the coverage is set to the boundaries of
       the combined coverage of the latest checksum and the coverage provided by
       the orbit number file that are part of this collection

    *  for a SPICE bundle the coverage is set to the boundaries of the
       coverage of the SPICE collection that is its member.


Bundle Creation Date Time
-------------------------

The creation time of the current version of the bundle is provided in the
bundle label under the ``File_Area_Text`` area. Although this should
correspond to the creation date of the readme file, its ``creation_date_time``
element is used because is the only way to embed the creation date within
the bundle label.

There is no need to mention this in the errata section of the
SPICE archive description document.


Miscellaneous Collection Rules
------------------------------

The generation of a new checksum product is bound to the addition of a
SPICE kernel product in the SPICE Kernels collection or to the addition of an
orbit number file product in the Miscellaneous collection. If none of these
products are added, the checksum file will not be generated.

It is highly convenient for the versions of the bundle, SPICE kernel, and
Miscellaneous collections labels to be aligned. Therefore it is not recommended
to produce an archive release that does not include an incremented SPICE kernel
collection (that automatically triggers the Miscellaneous collection increment),
or that only includes a Miscellaneous collection increment (for example to
only add an orbit number file product or a correction in any other product that
is not a SPICE kernel.)


Checksum files
--------------

It is highly recommended, not to say a policy, that archived files are ever
altered in any way. This was not possible in PDS3 but it is in PDS4. Thanks to
this, Checksum files provide the ability to revert to an earlier version
of the archive -- just take all the files listed in particular checksum plus
the checksum itself and its label.


Bundles with multiple observers and/or targets
----------------------------------------------

Multiple spacecrafts and mutliple targets. NPB incorporates the possibility to
have mutliple spacecrafts and targets in a Bundle. This is provided via
configuration. If so, the default spacecraft will be the primary spacecraft
which is specified in the configuration file. Otherwise it needs to be
specified in the Kernel List section of the configuration file. The non-kernels
bundle products will include all the targets and all the spacecrafts in the
labels.


PDS Information Model
---------------------

According to the PDS4 Concepts Document, the PDS Information model is

    A representation of concepts, relationships, constraints, rules, and
    operations to specify data semantics for a chosen domain of discourse.
    Specifically, the PDS Information Model (IM) is the representation that
    specifies PDS4.

The PDS IM is constantly evolving and new builds are released approximately
every six months.

For SPICE kernel archives the IM constrains the way in which labels are
designed. Note that the constant evolution of the IM is in conflict with NAIF's
approach to archives: archived files should never be changed.

NAIF recommends to archive producers to choose an IM and to stick with it
(as much as possible) throughout all the archive releases. At this point NAIF
uses IM 1.5.0.0 for all the NAIF PDS4 Bundles. IM 1.5.0.0 does not
support the usage of Line-Feed line endings (LF) for products, nor does it
support the inclusion of Digital Object Identifiers (DOIs) in the bundle label.
DOIs where included in IM 1.11.0.0, --the ExoMars2016 PDS4 Bundle uses IM 1.11.0.0
to be able to incorporate DOIs-- and LF for products was incorporated in IM
1.16.0.0. LF are only relevant to Checksum and ORBNUM products, given that they
are Table Character products, and LF is only required if the archive you are
generating or incrementing needs to include ORBNUM files also included in PDS3
archives or in other holdings where these objects had LF.

Because of these reasons NAIF recommends to use IM 1.16.0.0 for new archives.


Digital Objects Identifiers
---------------------------

A Digital Object Identifier (DOI) is a unique alphanumeric string assigned by a
registration agency (the International DOI Foundation) to identify content and
provide a persistent link to its location on the internet. DOIs can be used for
example to cite the SPICE kernel archive in published articles.

DOIs are not mandatory for SPICE kernel archives, but are desirable. A SPICE
kernel archive should only have one DOI associated with the bundle and if
applicable recorded in the bundle label under the ``Identification_Area`` as
follows::

    <Citation_Information>
      <author_list>$AUTHOR_LIST</author_list>
      <publication_year>$PRODUCT_CREATION_YEAR</publication_year>
      <doi>$DOI</doi>
      <keyword>Observation Geometry</keyword>
      <description>This bundle contains $MISSION_NAME SPICE kernels and related documentation.</description>
    </Citation_Information>

where uppercase keywords preceded by a ``$`` are archive specific values.


Product set, label, LIDVID and inventory examples for MAVEN releases 1 and 2
----------------------------------------------------------------------------

Below is an example of files, product types, and LIDVIDs for the MAVEN 1st and
2nd releases. Inventory contents are shown with ``P`` and ``S`` attributes. ``+``
as the first character on the line indicates files added in that release:

Release 1 includes:

    * 1 document: ``spiceds_v001.html``
    * 2 misc products: ``maven_orb1.orb``, ``checksum_v001.tab``
    * 3 kernels: ``naif0011.tls``, ``maven_2015_v01.tm``, ``maven_orb1.bsp``

::

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

Release 2 adds:

    * 1 document: ``spiceds_v002.html``
    * 2 misc products: ``maven_orb2.orb``, ``checksum_v002.tab``
    * 2 kernels: ``maven_2015_v02.tm``, ``maven_orb2.bsp``

::

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


A note on SPICE Kernels dissemination
=====================================

SPICE kernel archives might not be the only archives that include
SPICE kernels. Any other archive is free to include SPICE kernels.
As much as this is normal practice it can also be very dangerous. If you,
as the archive producer for a mission, have a say on the SPICE kernels included
in other archives of the mission, make sure of the following:

    * check if the kernels have been peer-reviewed, are valid, useful,
      and well documented;

    * if it makes sense to **also** or to **only** include the SPICE kernel
      product in the SPICE kernel archive;

    * if these kernels need to be present in the meta-kernel or even if they
      need a specific meta-kernel in the SPICE kernel archive.


SPICE Kernel archive divergences rationale
==========================================

The fact that the PDS artifacts in the SPICE Kernel archives are not 100%
aligned with PDS best practices or recommendations does **not** make
the kernels less usable because these products, such as labels, are not needed
to understand or use the kernels (unlike labels for PDS images, tables or other
science data product types.) It is the internal comments in the kernels and
other meta-information provided in the SPICE Archive Description Document
(SPICEDS) that one needs to understand to use kernels in the proper way.
