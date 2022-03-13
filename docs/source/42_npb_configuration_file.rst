The Configuration File
======================

The NAIF PDS4 Bundler needs a configuration file to be executed.
This configuration file is bundle-specific and it can also be release-specific.
It is a rather long file and setting it up for the first time for a given bundle
might take some effort.

Once the configuration file is generated for the bundle and is adapted to the
user's environment using NPB becomes an trivial task.

The following sections provide a detailed description and recommendations
to facilitate the task of writing the NPB configuration file.

If you are not familiar with the generation of PDS4 SPICE archives we recommend
you to first read the chapter
:ref:`source/20_spice_kernel_archive_description:SPICE Kernel Archive Description`
in such a way that you get familiar with some concepts that are discussed in the
following sections.


Configuration File Format
-------------------------

The NPB configuration file is an XML (eXtensible Markup Language) file.
The extension of the file should be .xml, although this is not strictly
necessary.

XML files (or documents), contain XML elements; these
elements can contain:

 * text
 * attributes
 * other elements
 * a mix of these elements.

Each XML element is defined in between angle brackets::

     <element>

elements enclose contents such as::

     <element>Some content<\element>

and elements can have attributes with a value::

     <element an_attribute="with value">Some content<\element>

The NPB Configuration File includes all the elements described above.
This document refers to configuration elements as parameters interchangeably.

NPB includes a Configuration File XML Schema
``src/naif_pds4_bundler/templates/configuration.xsd`` that is used to validate
configuration files. This validation is performed to confirm that the file is
well-formed and also "valid" according to the structure defined in the Schema.

Do not use the XML Schema as a reference to generate a configuration file, instead
use one of the configuration files included in the test area of the NPB package.
The MAVEN Configuration is the recommended reference: ``tests/naif_pds4_bundler/config/maven.xml``.
If the bundle to be generated includes secondary observers and/or targets
complement the MAVEN Configuration with the DART configuration:
``tests/naif_pds4_bundler/config/dart.xml``.

The Configuration File consists of a number of nested parameters that are
grouped in the following categories:

    1. PDS parameters
    2. Bundle parameters
    3. Mission parameters
    4. Directories
    5. Kernel list
    6. Meta-kernel
    7. Orbit number file (if ORBNUM files are present)

In order to facilitate the understanding of the Configuration File, the MAVEN
example is provided hereunder. We encourage you to first take a look
at the example and then continue to the sections that explain in detail each
parameter.::

    <?xml version='1.0' encoding='UTF-8'?>
    <naif-pds4-bundler_configuration>

        <!-- =========================== -->
        <!-- PDS parameters              -->
        <!-- =========================== -->
        <pds_parameters>
            <pds_version>4</pds_version>
            <information_model>1.5.0.0</information_model>
            <xml_model>http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.sch</xml_model>
            <schema_location>http://pds.nasa.gov/pds4/pds/v1 http://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1500.xsd
            </schema_location>
            <logical_identifier>urn:nasa:pds:maven.spice</logical_identifier>

            <!-- Optional Parameters -->
            <!-- Context Products that are not present in the registered context
                 products JSON file -->
            <context_products>
                <!-- The product name, type, and lidvid needs to be provided -->
                <product name="MAVEN">
                    <type>Spacecraft</type>
                    <lidvid>urn:nasa:pds:context:instrument_host:spacecraft.maven::1.0</lidvid>
                </product>
                <product name="Oumuamua">
                    <type>Hyperbolic Asteroid</type>
                    <lidvid>urn:nasa:pds:context:target:asteroid.oumauma::2.0</lidvid>
                </product>
            </context_products>
        </pds_parameters>

        <!-- =========================== -->
        <!-- Bundle parameters           -->
        <!-- =========================== -->
        <bundle_parameters>
            <producer_name>Marc Costa Sitja</producer_name>
            <author_list>Semenov B. V.; Costa Sitja M.</author_list>
            <institution>NAIF/JPL</institution>
            <doi>10.17189/1520434</doi>
            <!-- Location fo the SPICE archive description HTML file to be
                 included -->
            <spiceds>../data/spiceds_maven.html</spiceds>
            <spice_name>MAVEN</spice_name>
            <!-- Information to be included in the archive readme file, only used
                 if the file is not present -->
            <readme>
                <overview>
                    The MAVEN SPICE archive bundle contains observation geometry and
                    other ancillary data in the form of SPICE System kernel files for
                    the MAVEN spacecraft, its instruments, and targets.
                </overview>
                <cognisant_authority>
                    This archive bundle was produced by Boris Semenov, Planetary Data
                    System Navigation and Ancillary Information Facility Node, Jet
                    Propulsion Laboratory, Pasadena, California.
                </cognisant_authority>
            </readme>

            <!-- Optional Parameters -->
            <!-- Release date as a UTC calendar string. Use the following format:
                 YYYY-MM-DD e.g. 2021-04-09 -->
            <release_date>2021-06-25</release_date>
            <!-- Creation date and time for all the new archive products, usage
                 of this parameter is highly discouraged -->
            <creation_date_time>2021-06-25T08:00:00</creation_date_time>
            <!-- Increment start and stop times provided as a UTC calendar string.
                 Use the following format: YYYY-MM-DDThh:mm:ssZ
                 e.g. 2021-04-09T15:11:12Z -->
            <increment_start>2021-05-25T08:00:00Z</increment_start>
            <increment_finish>2021-06-25T08:00:00Z</increment_finish>
            <!-- Date format can be 'maklabel' style or 'infomod2' style. Default
                 value is 'maklabel'-->
            <date_format>maklabel</date_format>
            <!-- End of line format can either be 'CRLF' or 'LF', 'CRLF' is the
                 default value -->
            <end_of_line>CRLF</end_of_line>
        </bundle_parameters>

        <!-- =========================== -->
        <!-- Mission Parameters          -->
        <!-- =========================== -->
        <mission_parameters>
            <mission_acronym>maven</mission_acronym>
            <mission_name>MAVEN</mission_name>
            <mission_start>2013-11-18T19:20:43Z</mission_start>
            <mission_finish>2050-01-01T00:00:00Z</mission_finish>
            <observer>MAVEN</observer>
            <target>MARS</target>
            <kernels_to_load>
                <lsk>naif[0-9][0-9][0-9][0-9].tls</lsk>
                <sclk>MVN_SCLKSCET.[0-9][0-9][0-9][0-9][0-9].tsc</sclk>
                <fk>maven_v[0-9][0-9].tf</fk>
            </kernels_to_load>
        </mission_parameters>

        <!-- =========================== -->
        <!-- Directories                 -->
        <!-- =========================== -->
        <directories>
            <working_directory>working</working_directory>
            <kernels_directory>kernels</kernels_directory>
            <staging_directory>staging</staging_directory>
            <bundle_directory>maven</bundle_directory>

            <!-- Optional Parameters -->
            <orbnum_directory>misc/orbnum</orbnum_directory>
            <templates_directory>../../../src/pds/naif_pds4_bundler/templates/1.5.0.0</templates_directory>
        </directories>

        <!-- =========================== -->
        <!-- Kernel List                 -->
        <!-- =========================== -->
        <kernel_list>
            <kernel pattern="naif[0-9][0-9][0-9][0-9].tls">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE LSK file incorporating leapseconds up to $DATE, created by NAIF, JPL.</description>
                <patterns>
                    <DATE value="naif0011.tls">2015-JAN-01</DATE>
                    <DATE value="naif0012.tls">2017-JAN-01</DATE>
                </patterns>
            </kernel>
            <kernel pattern="pck[0-9][0-9][0-9][0-9][0-9].tpc">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE text PCK file containing constants from the $REPORT report, created by NAIF, JPL.
                </description>
                <patterns>
                    <REPORT value="pck00010.tpc">IAU 2009</REPORT>
                </patterns>
            </kernel>
            <kernel pattern="maven_v[0-9][0-9].tf">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE FK file defining reference frames for the MAVEN spacecraft, its structures, and science
                    instruments, created by NAIF, JPL.
                </description>
            </kernel>
            <kernel pattern="maven_ant_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions for the MAVEN communication antennae, created by NAIF,
                    JPL.
                </description>
            </kernel>
            <kernel pattern="maven_euv_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the MAVEN Extreme
                    Ultraviolet (EUV) monitor instrument, created by NAIF, JPL.
                </description>
            </kernel>
            <kernel pattern="maven_iuvs_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the MAVEN Imaging
                    Ultraviolet Spectrograph (IUVS) instrument, created by IUVS Team, CU/LASP.
                </description>
            </kernel>
            <kernel pattern="maven_ngims_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the MAVEN Neutral
                    Gas and Ion Mass Spectrometer (NGIMS) instrument, created by NGIMS Team, GSFC.
                </description>
            </kernel>
            <kernel pattern="maven_sep_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the Solar Energetic
                    Particle (SEP) instrument, created by SEP Team, UC Berkeley.
                </description>
            </kernel>
            <kernel pattern="maven_static_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the SupraThermal
                    And Thermal Ion Composition (STATIC) instrument, created by STATIC Team, UC Berkeley.
                </description>
            </kernel>
            <kernel pattern="maven_swea_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the MAVEN Solar
                    Wind Electron Analyzer (SWEA) instrument, created by SWEA Team, UC Berkeley.
                </description>
            </kernel>
            <kernel pattern="maven_swia_v[0-9][0-9].ti">
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE IK file providing FOV definitions and other instrument parameters for the MAVEN Solar
                    Wind Ion Analyzer (SWIA) instrument, created by SWIA Team, UC Berkeley.
                </description>
            </kernel>
            <kernel pattern="mvn_sclkscet_[0-9][0-9][0-9][0-9][0-9].tsc">
                <mapping>MVN_SCLKSCET.$VERSION.tsc</mapping>
                <mklabel_options>DEF_TIMES</mklabel_options>
                <description>SPICE SCLK file containing time correlation data for the main MAVEN on-board clock, created by
                    NAIF, JPL. The original name of this file was MVN_SCLKSCET.$VERSION.tsc.
                </description>
                <patterns>
                    <VERSION pattern="KERNEL">MVN_SCLKSCET.$VERSION.tsc</VERSION>
                </patterns>
            </kernel>
            <kernel pattern="de[0-9][0-9][0-9]s.bsp">
                <mklabel_options>de[0-9][0-9][0-9]s.bsp</mklabel_options>
                <description>SPICE SPK file containing JPL planetary ephemerides version $VERSION, created by NAIF, JPL.
                </description>
                <patterns>
                    <VERSION pattern="de430s.bsp">DE430</VERSION>
                </patterns>
            </kernel>
            <kernel pattern="mar[0-9][0-9][0-9]s.bsp">
                <mklabel_options></mklabel_options>
                <description>SPICE SPK file containing JPL Martian satellite ephemerides version $VERSION, created by NAIF,
                    JPL.
                </description>
                <patterns>
                    <VERSION pattern="mar097s.bsp">MAR097</VERSION>
                </patterns>
            </kernel>
            <kernel pattern="maven_struct_v[0-9][0-9].bsp">
                <mklabel_options></mklabel_options>
                <description>SPICE SPK file containing relative locations of selected MAVEN structures and science
                    instruments, created by NAIF, JPL.
                </description>
            </kernel>
            <kernel pattern="maven_cru_rec_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9].bsp">
                <mklabel_options></mklabel_options>
                <description>SPICE SPK file containing reconstructed cruise trajectory of the MAVEN spacecraft, created by
                    MAVEN NAV Team, JPL. The original name of this file was trj_c_131118-140923_rec_v1.bsp.
                </description>
            </kernel>
            <kernel pattern="maven_orb_rec_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9].bsp">
                <mklabel_options></mklabel_options>
                <description>SPICE SPK file containing reconstructed orbital trajectory of the MAVEN spacecraft, created by
                    NAIF, JPL by merging operational weekly reconstructed SPK files produced by MAVEN NAV Team, JPL.
                </description>
            </kernel>
            <kernel pattern="mvn_swea_nom_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing nominal orientation of the MAVEN SWEA instrument boom, created by
                    NAIF, JPL.
                </description>
            </kernel>
            <kernel pattern="mvn_app_rel_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing reconstructed orientation of the MAVEN Articulated Payload Platform
                    (APP), created by NAIF, JPL.
                </description>
            </kernel>
            <kernel pattern="mvn_iuvs_rem_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing reconstructed orientation of the MAVEN IUVS instrument internal
                    mirror, created by NAIF, JPL by merging data from daily IUVS CKs produced by the IUVS Team, CU/LASP.
                </description>
            </kernel>
            <kernel pattern="mvn_sc_rel_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing reconstructed orientation of the MAVEN spacecraft, created by NAIF,
                    JPL.
                </description>
            </kernel>
            <kernel pattern="mvn_sc_pred_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing predicted orientation of the MAVEN spacecraft, created by NAIF,
                    JPL. The original name of this file was $ORIGINAL.
                </description>
                <patterns>
                    <ORIGINAL value="mvn_sc_pred_210104_210120_v01.bc">mvn_sc_pred_210104_210120_vm321_322_v03.bc</ORIGINAL>
                    <ORIGINAL value="mvn_sc_pred_141205_141209_v01.bc">mvn_sc_pred_141205_141209_vm002OTM_v02.bc</ORIGINAL>
                    <ORIGINAL value="mvn_sc_pred_141223_150109_v01.bc">mvn_sc_pred_141223_150109_vm004_v02.bc</ORIGINAL>
                    <ORIGINAL value="mvn_sc_pred_150302_150315_v01.bc">mvn_sc_pred_150302_150315_vm013ar01_v01.bc</ORIGINAL>
                    <ORIGINAL value="mvn_sc_pred_150630_150707_v01.bc">mvn_sc_pred_150630_150707_vm027b_v01.bc</ORIGINAL>
                </patterns>
            </kernel>
            <kernel pattern="mvn_app_pred_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9].bc">
                <mklabel_options></mklabel_options>
                <description>SPICE CK file containing predicted orientation of the MAVEN Articulated Payload Platform
                    (APP), created by NAIF, JPL. The original name of this file was $ORIGINAL.
                </description>
                <patterns>
                    <ORIGINAL value="mvn_app_pred_210104_210120_v01.bc">mvn_app_pred_210104_210120_vm321_322_v03.bc</ORIGINAL>
                    <ORIGINAL value="mvn_app_pred_141205_141209_v01.bc">mvn_app_pred_141205_141209_vm002OTM_v02.bc</ORIGINAL>
                    <ORIGINAL value="mvn_app_pred_141223_150109_v01.bc">mvn_app_pred_141223_150109_vm004_v02.bc</ORIGINAL>
                    <ORIGINAL value="mvn_app_pred_150302_150315_v01.bc">mvn_app_pred_150302_150315_vm013ar01_v01.bc</ORIGINAL>
                    <ORIGINAL value="mvn_app_pred_150630_150707_v01.bc">mvn_app_pred_150630_150707_vm027b_v01.bc</ORIGINAL>
                </patterns>
            </kernel>
            <kernel pattern="maven_[0-9][0-9][0-9][0-9]_v[0-9][0-9].tm">
                <mklabel_options></mklabel_options>
                <description>SPICE MK file listing kernels for $YEAR, created by NAIF, JPL.</description>
                <patterns>
                    <YEAR pattern="KERNEL">maven_$YEAR_v[0-9][0-9].tm</YEAR>
                </patterns>
            </kernel>
        </kernel_list>

        <!-- =========================== -->
        <!-- Meta-kernel                 -->
        <!-- =========================== -->
        <meta-kernel>
            <!-- Each meta-kernel present in the bundle can be automatically
                 generated by NPB, providing the parameters below. -->
            <mk name="maven_$YEAR_v$VERSION.tm">
                <name>
                    <pattern length="2">VERSION</pattern>
                    <pattern length="4">YEAR</pattern>
                </name>
                <coverage_kernels>
                    <!-- These kernels determine the coverage of the increment -->
                    <pattern>maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp</pattern>
                </coverage_kernels>
                <interrupt_to_update>False</interrupt_to_update>
                <grammar>
                    <!-- LSK -->
                    <pattern>naif0012.tls</pattern>
                    <!-- PCK -->
                    <pattern>pck00010.tpc</pattern>
                    <!-- FK -->
                    <pattern>maven_v[0-9]{2}.tf</pattern>
                    <!-- IK -->
                    <pattern>maven_ant_v[0-9]{2}.ti</pattern>
                    <pattern>maven_euv_v[0-9]{2}.ti</pattern>
                    <pattern>maven_iuvs_v[0-9]{2}.ti</pattern>
                    <pattern>maven_ngims_v[0-9]{2}.ti</pattern>
                    <pattern>maven_sep_v[0-9]{2}.ti</pattern>
                    <pattern>maven_static_v[0-9]{2}.ti</pattern>
                    <pattern>maven_swea_v[0-9]{2}.ti</pattern>
                    <pattern>maven_swia_v[0-9]{2}.ti</pattern>
                    <!-- SCLK -->
                    <pattern>MVN_SCLKSCET.[0-9]{5}.tsc</pattern>
                    <pattern>mvn_sclkscet_[0-9]{5}.tsc</pattern>
                    <!-- SPK -->
                    <pattern>de430s.bsp</pattern>
                    <pattern>mar097s.bsp</pattern>
                    <pattern>maven_struct_v[0-9]{2}.bsp</pattern>
                    <pattern>date:maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp</pattern>
                    <!-- CK -->
                    <pattern>date:mvn_iuvs_rem_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                    <pattern>date:mvn_app_pred_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                    <pattern>date:mvn_app_rel_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                    <pattern>mvn_swea_nom_131118_300101_v[0-9]{2}.bc</pattern>
                    <pattern>date:mvn_sc_pred_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                    <pattern>date:mvn_sc_rel_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                    <!-- DSK -->
                </grammar>
                <metadata>
                    <description>
                        This meta-kernel lists the MAVEN SPICE kernels providing coverage
                        for $YEAR. All of the kernels listed below are archived in the PDS
                        MAVEN SPICE kernel archive. This set of files and the order in which
                        they are listed were picked to provide the best available data and
                        the most complete coverage for the specified year based on the
                        information about the kernels available at the time this meta-kernel
                        was made. For detailed information about the kernels listed below
                        refer to the internal comments included in the kernels and the
                        documentation accompanying the MAVEN SPICE kernel archive.
                    </description>
                    <!-- The keyword field is used to speficy parameters such as the
                         meta-kernel year.
                    -->
                    <keyword> </keyword>
                    <data> </data>
                </metadata>
            </mk>
        </meta-kernel>

        <!-- =========================== -->
        <!-- Orbit number file           -->
        <!-- =========================== -->
        <orbit_number_file>
            <orbnum>
                <pattern>maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].orb</pattern>
                <!-- Parameters from the orbnum generation preference file -->
                <event_detection_frame>
                    <spice_name>IAU_MARS</spice_name>
                    <description>Mars body-fixed frame</description>
                </event_detection_frame>
                <header_start_line>1</header_start_line >
                <pck>
                    <kernel_name>pck0010.tpc</kernel_name>
                    <description>IAU 2009 report</description>
                </pck>
                <coverage>
                    <kernel cutoff="True">../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp</kernel>
                </coverage>
                <author>NAIF, JPL</author>
            </orbnum>
        </orbit_number_file>
    </naif-pds4-bundler_configuration>


PDS Parameters
--------------

PDS Parameters are mission-level and bundle-level agnostic and are only related
to the PDS version, information model (IM), and available registered context
products. The table below provides a summary of the parameters:

.. list-table:: PDS Parameters
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - pds_version
     - Archive PDS version. Currently only 4 is fully
       implemented.
     - Yes
   * - information_model
     - Specifies the PDS4 information model to be used.
     - Yes
   * - xml_model
     - URL location of the XML Schematron associated with an information model.
       The ``information_model`` and ``xml_model`` parameters must refer to the
       same information model.
     - Yes
   * - schema_location
     - URL location of the XML Schema associated with an information model. The
       ``schema_location`` and ``xml_model`` parameters must refer to the same
       information model.
     - Yes
   * - logical_identifier
     - Logical identifier for the bundle.
     - Yes
   * - context_products
     - Provides the location of a file that lists required context products that are not available in
       the registered context products. More information below.
     - No


The Information Model
^^^^^^^^^^^^^^^^^^^^^

The ``information_model`` parameter will determine the PDS4 artifacts templates
that will be used for the bundle generation. NPB provides different templates
depending on the specified IM.

NAIF recommends to use IM 1.5.0.0, but if you need to include a DOI in the bundle
label you can use IM 1.14.0.0 or higher.

The choice of the IM will determine the ``xml_model`` and ``schema_location``
values. The only element value that will change is the one that specifies the IM
version.

The IM choice impacts other elements of the configuration file
and of the archive generation such as some contents of the SPICEDS file and
the templates used for the generation of PDS artifacts. These impacts are
described in the appropriate sections.


Context Products
^^^^^^^^^^^^^^^^

The ``context_products`` parameter provides the location of a JSON file that
contains additional context un-registered context products. This file is
required if the primary and/or secondary observer(s) and/or target(s) of the
bundle are not registered. The registered products are available in the
following file:
``src/naif_pds4_bundler/templates/registered_context_products.json``.
This list of registered context products is generated based on the registered
context products obtained with the PDS Validate tool with minor modifications,
and is maintained by the NAIF NPB developer.

The management of context products requires a bit of attention. Although NPB
will raise a run time error if any of the observers or targets is not
registered, we recommend that you search these items in the registered context
products. If you cannot find them, you need to provide them in the configuration
file. In order to do so, you will need to include the following elements
per product:

   * Product Name e.g.: DART, InSight Mars Lander Spacecraft
   * Product Type e.g.: Spacecraft, Planet, Asteroid, Satellite
   * Product LIDIV e.g.:
     ``urn:nasa:pds:context:instrument_host:spacecraft.dart::1.0``
     ``urn:nasa:pds:context:instrument_host:spacecraft.insight::2.0``

Here's an example for the DART mission::

        <context_products>
            <product name="DART">
                <type>Spacecraft</type>
                <lidvid>urn:nasa:pds:context:instrument_host:spacecraft.dart::1.0</lidvid>
            </product>
            <product name="LICIA">
                <type>Spacecraft</type>
                <lidvid>urn:nasa:pds:context:instrument_host:spacecraft.licia::1.0</lidvid>
            </product>
            <product name="Earth">
                <type>Planet</type>
                <lidvid>urn:nasa:pds:context:target:planet.earth::1.0</lidvid>
            </product>
            <product name="Didymos">
                <type>Asteroid</type>
                <lidvid>urn:nasa:pds:context:target:asteroid.didymos::1.0</lidvid>
            </product>
            <product name="Dimorphos">
                <type>Satellite</type>
                <lidvid>urn:nasa:pds:context:target:satellite.didymos.dimorphos::1.0</lidvid>
            </product>
        </context_products>

In addition, contact your archiving authority contact to ensure that the
context product information is correct. If your archiving authority is the PDS
you will need to consult with the leading node of the mission archive.


Bundle Parameters
-----------------

Bundle Parameters provide bundle level information required for the PDS4
artifacts and are SPICE Kernel collection-agnostic. The table below provides a
summary of the parameters:

.. list-table:: Bundle Parameters
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - producer_name
     - Name of the archive producer (or NPB operator.)
     - Yes
   * - author_list
     - Name of the SPICE kernel main author(s) and the archive producer
       (or NPB operator.)
     - Yes
   * - institution
     - Institution affiliation of the archive produced e.g., ``NAIF/JPL``,
       ``PSA/ESA``, etc.
     - Yes
   * - doi
     - Digital Object Identifier (DOI) of the bundle. More information in
       :ref:`source/22_pds4_spice_archive:Digital Objects Identifiers`.
     - No
   * - spice_name
     - Specifies the SPICE name of the main spacecraft of the archive.
     - Yes
   * - spiceds
     - Indicates the location of the SPICE Data Archive Description document
       (SPICEDS) for the release.
     - No
   * - readme
     - Provides the parameters required to generate the bundle readme file by
       using the readme file template or the path to an input readme file.
     - No
   * - release_date
     - Bundle increment release date. The date is provided with a UTC calendar
       format string with following syntax: ``YYYY-MM-DD`` e.g. ``2021-04-09``.
       If not provided the NPB execution date is used. NAIF does not recommend to
       include this parameter.
     - No
   * - creation_date_time
     - Creation date and time for all the products of the release. Usage
       of this parameter is highly discouraged. The date is provided with
       a UTC calendar format string with following syntax: ``YYYY-MM-DDThh:mm:ss``
       e.g. ``2021-06-25T08:00:00``. If not provided the NPB execution date is used.
     - No
   * - increment_start
     - Archive release start time. This time forces the  More details are provided in
       :ref:`source/22_pds4_spice_archive:Product Coverage Assignment Rules`. The
       date is provided with a UTC calendar format string with following syntax:
       ``YYYY-MM-DDThh:mm:ssZ`` e.g. ``2021-06-25T08:00:00Z``. NAIF does not
       recommend to include this parameter.
     - No
   * - increment_finish
     - Release stop time. More details are provided in
       :ref:`source/22_pds4_spice_archive:Product Coverage Assignment Rules`. The
       date is provided with a UTC calendar format string with following syntax:
       ``YYYY-MM-DDThh:mm:ssZ`` e.g. ``2021-06-25T08:00:00Z``. NAIF does not recommend
       to include this parameter.
     - No
   * - date_format
     - Product labels use different date and time formats. The values can
       be ``infomod2`` or ``maklabel``. More information is provided below.
       The default value is ``maklabel``.
     - No
   * - end_of_line
     - The end of line character for products can either be ``CRLF`` or ``LF``.
       The default is ``CRLF`` (for ``<CR><LF>``). NAIF recommends to use
       ``<CRLF>`` when using PDS IM version prior to 1.14.0.0, The choice of
       this parameter affects the content of the SPICEDS file (section
       "File Formats".) More information is provided in
       :ref:`source/32_step_2_npb_setup:SPICE Data Set Catalog File`.
     - No


SPICEDS
^^^^^^^

In addition to the NPB Configuration File -if the meta-kernel is generated
automatically - the SPICEDS file is the only bundle product that requires manual
intervention. More details on SPICEDS are provided in the section
:ref:`source/32_step_2_npb_setup:SPICE Data Set Catalog File`.


Readme File
^^^^^^^^^^^

The readme file configuration provides either the parameters required to
generate the readme file by NPB or the path to an input readme file.

If the readme file is generated by NPB, the readme file template will be used
along with the elements included in the configuration:

   * ``overview`` provides an overview of the archive and
   * ``cognisant_persons`` indicates the institution responsible for the
     archive generation.

If present these elements should have the same value for all archive releases.
More information on the readme file is provided in section
:ref:`source/22_pds4_spice_archive:Bundle Products Construction Rules`.


Increment Start and Finish Times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These configuration elements, if present, set the archive increment start and
stop times regardless of the coverage times provided by the MK(s) --if any--.

NPB will set the MK(s) start and finish times to this elements --each
individually--, and will propagate these times to the SPICE Kernels Collection
and to the Bundle labels. Note that for yearly MKs --see section
:ref:`source/31_step_1_preparing_data:Preparing Meta-kernels`--, NPB will only
update the start or finish times for the MKs that correspond either to the
start or finish year.

Note that these configuration elements should be used with care and
understanding their implications on the bundle coverage.


Date Format
^^^^^^^^^^^

There two possible strategies for date time string format across the archive:
``maklabel`` and ``infomod2``.

``infomod2`` stands for "PDS Information Model 2.0.0.0". This format sets the
format of all date time instances across the label products to::

    yyyy-mm-ddThh:mm:ss.sssZ

where

  * ``yyyy`` is the 4-digit year
  * ``mm`` is the 2-digit month
  * ``dd`` is the 2-digit day
  * ``hh`` is the 2-digit hour (24h format)
  * ``mm`` are the 2-digit minutes
  * ``ss.sss`` are the seconds and milliseconds rounded inwards to milliseconds.

For example: ``2016-01-01T00:00:00.000Z``. The main characteristic is of this
format is that is used for all labels and milliseconds are rounded inwards:
start times are rounded to the next nearest millisecond and stop times
are rounded to the previous nearest millisecond. The coverage specified for
SPICE kernels products and for those products whose coverage is determined by
them will always be within the time bounds of the SPICE kernel. For example
``2016-01-01T00:00:00.1257Z`` will be rounded to  ``2016-01-01T00:00:00.126Z``
if it is a start time, and to ``2016-01-01T00:00:00.125Z`` if it is a stop time.

The ``maklabel`` format replicates the date time formats provided by NAIF's
``MAKLABEL`` utility [MAKLABEL]_. ``MAKLABEL`` has been used for all NAIF's
PDS3 data sets and for some PDS4 archives and sets the format of all date
time instances across the label products, except for the CK kernel labels to::

    yyyy-mm-ddThh:mm:ssZ

whereas sets times for CK kernel labels to::

    yyyy-mm-ddThh:mm:ss.sssZ

the fields are the same as for the ``infomod2`` format except that for non
CK labels it rounds the decimal part of the seconds to the nearest second.
Because of this, labels with non-integer-second times are outside of the actual
file coverage.

Note that the date time strings provided via configuration (``mission_start``,
``mission_finish`` at least) that feed label tags need to be provided with the
appropriate format to NPB, if not NPB will raise a run time error.
This does not apply to the times provided in the kernel list section of the
configuration.

NAIF uses the ``maklabel`` format for PDS IM 1.5.0.0 archives for comparison
and reproducibility reasons. The idea is that NAIF will use ``infomod2`` only
after the PDS IM 2.0.0.0 is released. NAIF recommends using the
``infomod2`` format, especially for new archives.

More details on the determination of coverage for different files in the archives
are provided in section :ref:`source/22_pds4_spice_archive:Product Coverage Assignment Rules`.


Mission Parameters
------------------

Mission parameters provide mission-specific information such as: mission
name, acronym, observers, and targets. The table below provides a
summary of the parameters:

.. list-table:: Mission Parameters
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - mission_acronym
     - Specifies the mission acronym that is used to construct the directory
       structure and some of the NPB execution by-products.
     - Yes
   * - mission_name
     - Specifies the mission name that is used in several product labels. This
       name must correspond to the name provided by the registered context
       products (including the ones provided via configuration.)
     - Yes
   * - observer
     - The observer is the main spacecraft of the data and the SPICE kernels,
       this name must correspond to the name provided by the registered context
       products (including the ones provided via configuration.)
     - Yes
   * - target
     - The target is the mission's primary target (investigated natural body),
       this name must correspond to the name provided by the registered context
       products including the ones provided via configuration.)
     - Yes
   * - kernels_to_load
     - Lists the SPICE kernels that are required to run NPB. More information
       is provided below.
     - Yes
   * - mission_start
     - Mission start time; typically is the start time of the post-launch SPK.
       The date is provided with a UTC calendar format string. The syntax of
       the string is determined by the ``date_format`` used.
     - Yes
   * - mission_finish
     - Mission finish time; typically is the start time of the post-launch SPK.
       The date is provided with a UTC calendar format string. The syntax of
       the string is determined by the ``date_format`` used.
     - Yes
   * - secondary_observers
     - Provides a list of the secondary spacecrafts present in the SPICE
       kernels. Each name entry must use the observer tag. These names must
       correspond to the names provided by the registered context products
       (including the ones provided via configuration.)
     - No
   * - secondary_targets
     - Provides a list of the secondary targets present in the SPICE
       kernels. Each name entry must use the target tag. These names must
       correspond to the names provided by the registered context products
       (including the ones provided via configuration.)
     - No


On Names and Acronyms
^^^^^^^^^^^^^^^^^^^^^

Distinction in between ``mission_acronym``, ``mission_name``,
observer, and the Bundle parameter ``spice_name`` can be rather confusing. A
good example to distinguish in between the parameters is the Mars 2020 SPICE
kernel archive, for which the values are as follows:

   * ``mission_acronym``: mars2020
   * ``mission_name``: Mars 2020 Perseverance Rover Mission
   * ``observer``: Mars 2020 Perseverance Rover
   * ``spice_name``: M2020

Contrarily for other archives, such as MAVEN, is as follows:

   * ``mission_acronym``: maven
   * ``mission_name``: MAVEN
   * ``observer``: MAVEN
   * ``spice_name``: MAVEN

A note on secondary observers and targets: although secondary s/c and/or targets
might be present in the SPICE kernels, **they do not have to be present in the
Configuration File, nor in the bundle PDS4 labels**. It is perfectly
fine to use the primary s/c and target for all kernels.

This is the case for the INSIGHT SPICE kernel bundle: the secondary s/c MARCO-A
and MARCO-B use INSIGHT in their labels as observer. If this simplified approach
is followed then it must be noted in the Errata section of the SPICE archive
description document (SPICEDS) as follows::

        All MARCO-A and MARCO-B kernels included in the archive
        are labeled as being associate the INSIGHT instrument host.

This simplified approach is especially convenient for missions that have
a main prime s/c or target. For other missions such as BepiColombo where the
Mercury Planet Orbiter (MPO) and the Mercury Magnetospheric Orbiter (MMO or MIO)
have a comparable relevance, the bundle must include a secondary s/c. Here's an
example of the entries for secondary s/c and targets for DART::

        <observer>DART</observer>
        <target>Didymos</target>
        (...)
        <secondary_observers>
            <observer>LICIA</observer>
        </secondary_observers>
        <secondary_targets>
            <target>Dimorphos</target>
            <target>Earth</target>
        </secondary_targets>


Kernels To Load
^^^^^^^^^^^^^^^

The ``kernels_to_load`` mission parameter lists the SPICE kernels that are
required to run NPB. At least a LSK, a SCLK, and a FK kernel will be required;
if there are multiple observers most likely more FKs and SCLKs will be required.
PCKs might also be needed.

These kernels are used by NPB to use SPICE (via SpiceyPy [SPICEYPY]_ a wrapper
to CSPICE for Python) to perform time conversions (a LSK kernel is needed),
to obtain different bundle coverages (SPKs, CKs, FKs and SCLKs are needed),
and to support coverage determination of kernels included in the release.

Understanding which kernels need to be loaded requires some experience with
SPICE and some experience with the SPICE kernels of the mission to be archived.
If you have any questions please contact the NAIF NPB developer.

You can either specify a kernel name or a kernel name with a pattern
(recommended). More information on kernel patterns is provided in
:ref:`source/42_npb_configuration_file:Kernel patterns`.

In the Configuration File, each entry must be specified by its kernel type,
there can be multiple entries with the same kernel type. For INSIGHT for
example: ::

        <kernels_to_load>
            <lsk>naif[0-9][0-9][0-9][0-9].tls</lsk>
            <sclk>NSY_SCLKSCET.[0-9][0-9][0-9][0-9][0-9].tsc</sclk>
            <sclk>marcoa_fake_v[0-9][0-9].tsc</sclk>
            <fk>../data/kernels/fk/insight_v05.tf</fk>
            <fk>marcob_v[0-9][0-9].tf</fk>
        </kernels_to_load>

NPB will use the ``bundle_directory`` and ``kernels_directory`` directories
specified in the next section of the Configuration File "Directories" to search
for the latest version of these kernels (if provided by patterns) or to the
kernel specified (if the kernel name does not contain patterns.)


Kernel patterns
^^^^^^^^^^^^^^^

Throughout the configuration you will find multiple occurrences of kernels that
are specified with a pattern. The usage of patterns allows NPB to know that it
must scan a directory or a list of directories, for a specific version of the
kernel within the possibilities provided by the pattern, such as the latest
version of a specific kernel.

The patterns recognised by NPB are quite limited and are a subset of the ones
used for regular expressions. They are the following:

   * ``[0-9]``: any digit
   * ``[a-z]``: any lowercase letter
   * ``[A-Z]``: any uppercase letter

In addition there are two special patterns:

   * ``{n}``: is placed after another pattern and indicates "n" repetitions of
     that pattern; ``n`` spans from 1 to a *N* where *N* is a number
     limited by the SPICE file name length. E.g., ``[0-6]{4}`` are four
     consecutive digits (used to specify a year for example: 2021.)
   * ``$``: indicates that the contiguous set of uppercase letters correspond to a
     literal pattern e.g., ``$YEAR`` indicates that this will be replaced by a
     year. Use cases are provided later in the document.

Therefore the following FK kernel pattern: ``maven_v[0-9][0-9].tf``, would
be matched by any version of the MAVEN FK, for example ``maven_v09.tf``.


Directories
-----------

They specify the directories used to run NPB. The table below provides a summary
of the required and optional directories:

.. list-table:: Directories
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - working_directory
     - Specifies the directory that will be used by NPB to generate the
       execution by-products that include but are not limited to: execution log,
       kernel list, and the file list. It is a good idea to use the working
       directory to store the configuration file(s), validation reports,
       archive plans, etc. More information of this directory is provided in
       section :ref:`source/32_step_2_npb_setup:Working Directory`.
     - Yes
   * - kernels_directory
     - Specifies the directory(ies) that will be used by NPB to obtain the kernels
       to be archived from. These directories must follow the usual operational
       SPICE kernel sub-directory structure by kernel type.
     - Yes
   * - staging_directory
     - This directory will be used by NPB to store the files generated by its
       execution for the archive (the release or increment.)
     - Yes
   * - bundle_directory
     - Indicates the directory where the current version of the SPICE kernel
       bundle is present (before the execution of NPB.)
     - Yes
   * - orbnum_directory
     - Indicates the directory(ies) where the orbit number files to be archived
       are present.
     - No
   * - templates_directory
     - Indicates the directory where the user input templates are present.
     - No

More information on the setup of the NPB directories is provided in
:ref:`source/32_step_2_npb_setup:Workspace Setup`.


Kernel List
-----------

The Kernel List is an NPB execution by-product (more information on NPB
execution by-products is provided in
:ref:`source/43_using_npb:Execution by-products`) that is used for two main
purposes:

   * to generate a description for each kernel to be archived; the
     description of the kernel is present in all kernel labels
   * if necessary, to change the name of the provided kernels to the name
     required by the archive

NPB will try to match every input kernel, including meta-kernels, with an entry
of the kernel list and based on that will generate a Kernel List product.
This section of the configuration provides a list of all the kernels that
might be included in the bundle for any release. Consequently,
the Kernel List section in the configuration file is prone to grow as new
archive releases are prepared.

The Kernel List configuration section includes a kernel element for
each kernel that has a pattern attribute the value of which is a kernel name
with (or without) a pattern. For example::

    <kernel_list>
        <kernel pattern="naif[0-9][0-9][0-9][0-9].tls">

This kernel element is used to identify the leapseconds kernels present in
the kernels to be archived. An important remark of the pattern attribute value
is that it cannot contain any of the special patterns ``{n}`` or ``$``, and
therefore can only include ``[0-9]``, ``[a-z]``, and ``[A-Z]`` patterns.

The first nested element of the kernel element is ``<mklabel_options>``. This
element is a leftover of the PDS3 data sets and for all the kernels in PDS4
bundles can be omitted.

If the number of characters for a given pattern of a kernel to load is not known
in advance then multiple entries in the kernel list should be used in the
configuration file. For example, if you do not know whether you will have one of
the following files::

      msl_76_sclkscet_refit_j5.tsc
      msl_76_sclkscet_refit_k13.tsc

Then the two entries specified hereunder can be provided in the kernel list: ::

      <kernel pattern="msl_76_sclkscet_refit_[a-z][0-9].tsc">       (...)
      <kernel pattern="msl_76_sclkscet_refit_[a-z][0-9][0-9].tsc">  (...)

The second and third element patterns are optional and provide the observers and
targets required by the kernels. By default, the kernel label will set its
observer and target elements to the ``<observer>`` and ``<target>`` provided in
the Mission Parameters section of the configuration file. But what happens if
the kernel data for one of the secondary observers/targets or
for several of them? Since there is no way to fully automatize the
identification of all possible cases this is indicated in this
element of the kernel list. The following example should be self-explanatory::

            <observers>
                <observer>DART</observer>
                <observer>LICIA</observer>
            </observers>
            <targets>
                <target>Didymos</target>
                <target>Dimorphos</target>
            </targets>


Kernel Descriptions
^^^^^^^^^^^^^^^^^^^

The fourth (or second) nested element is the kernel description. This is a very
important configuration parameter and its content must describe synthetically
and precisely the SPICE kernel. The recommended structure of the description
is::

   SPICE <text/binary> <kernel type> kernel ... created by <producer>, <institution>.

where

   * ``<text/binary>`` is either text or binary
   * ``<kernel type>`` is the kernel type acronym (SPK, FK, etc.)
   * ``<producer>`` is the author or the group that generated the kernel
   * ``<institution>`` is the affiliation of the kernel producer.

For example::

       <description>SPICE LSK file incorporating leapseconds up to $DATE, created by NAIF, JPL.</description>

The description element might contain patterns based on the special expression
``$`` followed by an upper case name, ``$DATE`` in the example above. These
patterns are used to accommodate information particular to each individual
kernel of each kind. In the example above the ``$DATE`` expression is meant to
specify the year of the latest leapsecond provided by that kernel. Other
examples are: original name of the kernel (see
:ref:`source/31_step_1_preparing_data:Renaming Files`), version of the IAU
report, kernel coverage, etc. These patterns are determined by the next element:
``patterns``.

The ``patterns`` element maps the patterns present in the description element
with its value. NPB maps the patterns with one of the following methods:

   * match by value
   * match by pattern
   * match from comment

These are described in the following subsections.


Match by value
""""""""""""""

The first method to identify patterns in the kernel pattern attribute value is
by value. In order to do so, the kernel pattern attribute value is set to
``value`` and its value corresponds to the actual name of the kernel, without
patterns, in such a way that the value of the element is substituted by the
pattern in the resulting description. It is also possible to use a subset of
the kernel name but this option should be used carefully and only if the subset
identifies a unique kernel "type".

Going back to the leapseconds example, the complete entry in the kernel list
would be: ::

        <kernel pattern="naif[0-9][0-9][0-9][0-9].tls">
            <description>SPICE LSK file incorporating leapseconds up to $DATE, created by NAIF, JPL.</description>
            <patterns>
                <DATE value="naif0011.tls">2015-JAN-01</DATE>
                <DATE value="naif0012.tls">2017-JAN-01</DATE>
            </patterns>
        </kernel>

In this case, if the kernel to be archived is ``naif0012.tls`` then the
description for the label will be: ::

    SPICE LSK file incorporating leapseconds up to 2017-JAN-01, created by NAIF, JPL.

Because the ``$DATE`` pattern has been replaced by the ``DATE`` element nested from
the patterns element and the kernel name equals one of the values of the
``value`` attribute. With this configuration, archiving ``naif0010.tls`` would
have resulted into a runtime error::

    RuntimeError: -- Kernel naif0010.tls description could not be updated with pattern.

The names of the elements to map the patterns are defined by the user. Some
examples are provided hereunder:

   * ``ORIGINAL``: specify the original name of the kernel.
   * ``REPORT``: specify the IAU report for PCKs.
   * ``DATE``: specifies a date.
   * ``FILE``: specify the original name of the kernel

These names are meant to help the archive producers to understand the pattern
matching.

The limitation of this method is that each individual kernel type requires an
element entry in the configuration file.


Match by pattern
""""""""""""""""

This method uses parts of the kernel name pattern to identify patterns required
by the kernel description. Another way to describe it, using XML terminology:
this method uses the pattern attribute value of the kernel element to map one
pattern of its file name as obtained from the kernel name without patterns.

To do so, nested elements from patterns are provided. The name of the element
coincides with a pattern with the special pattern ``$`` and is indicated by an
attribute called pattern.

Take the following kernel element form the kernel list for MAVEN::

        <kernel pattern="maven_[0-9][0-9][0-9][0-9]_v[0-9][0-9].tm">
            <description>SPICE MK file listing kernels for $YEAR, created by NAIF, JPL.</description>
            <patterns>
                <YEAR pattern="KERNEL">maven_$YEAR_v[0-9][0-9].tm</YEAR>
            </patterns>
        </kernel>

In this case we need to obtain the ``$YEAR`` pattern for the description. The
value of the ``YEAR`` element indicates that NPB must extract the ``$YEAR``
value from the first pattern of the kernel pattern: ::

    maven_[0-9][0-9][0-9][0-9]_v[0-9][0-9].tm
    maven_       $YEAR        _v[0-9][0-9].tm

If the archived kernel is ``maven_2021_v01.tm`` the ``$YEAR`` value will be
``2021`` and the description will be: ::

    SPICE MK file listing kernels for 2021, created by NAIF, JPL.

The names of the elements to map the patterns are defined by the configuration
file schema. They are currently limited to:

   * ``YEAR``: used to specify a year.
   * ``START``: indicates that we are looking at the coverage start time.
   * ``FINISH``: indicates that we are looking at the coverage finish time.
   * ``COVERAGE``: specific name for OSIRIS-REx DSKs.
   * ``REFERENCE``: specific name for OSIRIS-REx DSKs.
   * ``VERSION``: indicates that SPICE kernel version.
   * ``DATE``: indicates that we are extracting a date from the name.
   * ``ORIGINAL``: indicates that we obtaining the original kernel name.

These names are meant to help the archive producers to understand the pattern
matching. Any of these names can be used regardless of the pattern. If you
need to add additional elements please contact the NAIF NPB developer.


Match from Comment
""""""""""""""""""

Sometimes the original name of the kernel that must be included in the
description is only present in the comment area of the binary kernel (SPK, CK,
DSK or binary PCK), if so the comment must be extracted from the kernel. The
kernel file name must be in a single line. NPB will extract the comment if you
indicate it to do so similar to the way the "Match by pattern" method is used.

The pattern nested element must have an attribute called ``file`` the value of
which must be ``COMMENT``. Currently the only available name for the element is
``ORIGINAL``, to indicate that you are mapping the description with the original
kernel name. Also, the value of the ``ORIGINAL`` element must be the text of the
line that precedes the original kernel name in the comment area of the kernel::

        <kernel pattern="mro_sc_psp_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]p.bc">
            <mklabel_options>NAIF HGA PREDICT ESP</mklabel_options>
            <description>MRO SPICE CK file providing predicted orientation of the MRO spacecraft bus modeled by the MRO Spacecraft Team, LMA using the AtArPS tool for a part of the Extended Science phase of the mission, created by NAIF, JPL. The original name of this file was $ORIGINAL
            </description>
            <patterns>
                <ORIGINAL file="COMMENT">The original name of this file was</ORIGINAL>
            </patterns>
        </kernel>

The value of the ``ORIGINAL`` element will be then used to extract the kernel
name from the CK comment area. If we use the NAIF utility ``COMMNT`` we can read the
comment in an example kernel ``mro_sc_psp_210628_210710p.bc``::

        $ commnt -r mro_sc_psp_210628_210710p.bc

        ********************************************************************************

        The original name of this file was CK_Pred_21180_21192_sc_20210629155609.bc.
        It was changed to mro_sc_psp_210628_210710p.bc on Thu Aug 12 17:51:24 PDT 2021.
        (...)

The line with ``The original name of this file was`` must be present and will be
used and therefore ``CK_Pred_21180_21192_sc_20210629155609.bc`` will be
extracted and the description will then be::

        MRO SPICE CK file providing predicted orientation of the MRO spacecraft
        bus modeled by the MRO Spacecraft Team, LMA using the AtArPS tool for a
        part of the Extended Science phase of the mission, created by NAIF, JPL.
        The original name of this file was CK_Pred_21180_21192_sc_20210629155609.bc.


This method has been implemented for the MRO PDS3 SPICE kernel data set
generation. NAIF does not recommend to record the original name of the kernel
in the comment area kernels.


Mapping kernels
^^^^^^^^^^^^^^^

Sometimes the name of the archived kernel is modified with respect to the
original kernel - sometimes present in the kernels operational area - this
happens for kernels that have long names, mixed case, fields that are
meaningless to users but are meaningful to operation engineers, etc. In such
cases NAIF recommends to update the archived kernel name for it to be more user
friendly.

The mapping in between the original kernel name and the archived kernel name
can be achieved in two different ways.

The first approach consists to update the name manually and to use the
updated name in the release plan. If the original name of the kernel has to be
included in the kernel description, this can be implemented with the
"Match by value" method by reflecting this on the attribute value of the given
kernel element.

The second and recommended approach is to use a special element nested in the
corresponding kernel element. This special "mapping" element is called
``mapping`` and if present, it must be the first element of the nested elements
of a kernel. If this element is present then the patterns present for the
"Match by pattern" method must also be present. The mapping element contains
the original kernel name with the patterns provided with the special pattern
``$``; those patterns are then correlated with the ones provided in the
patterns nested elements.

Say that we need to rename the OSIRIS-REx asteroid Bennu DSKs.
The original name is::

    l_00050mm_alt_ptm_5595n04217_v021.bds

and we want to rename it to::

    bennu_l_00050mm_alt_ptm_5595n04217_v021.bds

With the first approach we would simply rename it, and given that in the
description we want to include the original file name, the ``<kernel>`` entry
in the Kernel List section of the configuration file would be::

        <kernel pattern="bennu_l_[0-9][0-9][0-9][0-9][0-9]mm_alt_dtm_[0-9][0-9][0-9][0-9][a-z][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9][0-9].bds">
            <description>SPICE DSK file containing shape model data for the surface of asteroid (101955) Bennu,
                created by the ORX Altimetry Working Group (AltWG). The original name of this file was $ORIGINAL.</description>
            <patterns>
                <ORIGINAL value="bennu_l_00050mm_alt_ptm_5595n04217_v021.bds">l_00050mm_alt_ptm_5595n04217_v021.bds</ORIGINAL>
                <ORIGINAL value="bennu_l_00050mm_alt_ptm_5595n04217_v020.bds">l_00050mm_alt_ptm_5595n04217_v020.bds</ORIGINAL>
            </patterns>
        </kernel>

This approach would require a pattern entry per DSK. The second approach, albeit
more difficult to implement, would work for each DSK::


        <kernel pattern="bennu_l_[0-9][0-9][0-9][0-9][0-9]mm_alt_dtm_[0-9][0-9][0-9][0-9][a-z][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9][0-9].bds">
            <mapping>l_$RESOLUTIONmm_alt_dtm_$REFERENCE_v$VERSION.bds</mapping>
            <description>SPICE DSK file containing shape model data for the surface of asteroid (101955) Bennu,
                created by the ORX Altimetry Working Group (AltWG). The original name of this file was l_$RESOLUTIONmm_alt_dtm_$REFERENCE_v$VERSION.bds.</description>
            <patterns>
                <RESOLUTION pattern="KERNEL">l_$RESOLUTIONmm_alt_dtm_[0-9][0-9][0-9][0-9][a-z][0-9][0-9][0-9][0-9][0-9]_v[0-9][0-9][0-9].bds</RESOLUTION>
                <REFERENCE pattern="KERNEL">l_[0-9][0-9][0-9][0-9][0-9]mm_alt_dtm_$REFERENCE_v[0-9][0-9][0-9].bds</REFERENCE>
                <VERSION pattern="KERNEL">l_[0-9][0-9][0-9][0-9][0-9]mm_alt_dtm_[0-9][0-9][0-9][0-9][a-z][0-9][0-9][0-9][0-9][0-9]_v$VERSION.bds</VERSION>
            </patterns>
        </kernel>

As you can see the three patterns present in the mapping element:
``$RESOLUTION``, ``$REFERENCE``, and ``$VERSION`` are present as pattern
elements.

When no release plan is provided as an input, the mapping of kernels does not
occur and the kernels present in the kernels directories need to have their
final names as described in the first approach.

Meta-kernel
-----------

The next section of the configuration file is the one that defines the
generation of the meta-kernels (MKs). NPB is capable to either generate MKs
automatically or to assist you in their generation.

If NPB is set to generate kernels automatically, after the MK is
generated and if indicated via configuration, NPB will pause the execution and
will provide you with the option to review the MK that it has generated.
More information is provided in
:ref:`source/33_step_3_running_npb:Interactive step for Meta-kernels`.

Alternatively you can provide MKs that you have generated manually or
by any other mean to NPB via configuration as well. The elements of the MK
section of the configuration file are the following:

.. list-table:: Meta-kernels
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - mk_inputs
     - You can specify a list of MKs for the archive release by
       providing their path.
     - No
   * - mk
     - This element provides the configuration elements necessary to
       automatically generate a MK.
     - Yes

The elements present in the ``mk`` element are: ``name``, ``coverage_kernels``,
``interrupt_to_update``, ``grammar``, and ``metadata`` - that at the same time
consists of the ``description``, ``keyword`` and ``data`` elements. There can be as many mk
elements as needed. This element is described in detail below.


Automatic generation of Meta-kernels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``<mk>`` element of the configuration provides the parameters required
to automatically generate MKs. The first nested element of ``<mk>`` is the
``<name>`` element, that provides a mapping to the patterns in the name by
specifying the length of these patterns; therefore these patterns must have
a fixed length.

The element ``<name>`` is required even if the MK is provided as an input --and
therefore is not generated automatically.

For example a MAVEN MK that provides yearly coverage and can have
multiple versions would be as follows: ::

        <mk name="maven_$YEAR_v$VERSION.tm">
            <name>
                <pattern length="2">VERSION</pattern>
                <pattern length="4">YEAR</pattern>
            </name>

Please note that the patterns of the ``<mk>`` name attribute cannot be
contiguous, the following is not permitted: ``insight_$YEAR$VERSION.tm``.

The next element is ``<interrupt_to_update>``, this element determines whether if
after kernel generation and before the kernel label generation NPB must be
paused to provide the option to manually edit the generated MK. It must be set
to either ``True`` or ``False``.


Meta-kernel grammar
"""""""""""""""""""

The next element is "grammar". The kernel grammar provides an ordered list of
kernel names with patterns that will populate the MK. For example::

            <grammar>
                <!-- LSK -->
                <pattern>naif0012.tls</pattern>
                <!-- PCK -->
                <pattern>pck00010.tpc</pattern>
                <!-- FK -->
                <pattern>maven_v[0-9]{2}.tf</pattern>
                <!-- IK -->
                <pattern>maven_ant_v[0-9]{2}.ti</pattern>
                <pattern>maven_euv_v[0-9]{2}.ti</pattern>
                <pattern>maven_iuvs_v[0-9]{2}.ti</pattern>
                <pattern>maven_ngims_v[0-9]{2}.ti</pattern>
                <pattern>maven_sep_v[0-9]{2}.ti</pattern>
                <pattern>maven_static_v[0-9]{2}.ti</pattern>
                <pattern>maven_swea_v[0-9]{2}.ti</pattern>
                <pattern>maven_swia_v[0-9]{2}.ti</pattern>
                <!-- SCLK -->
                <pattern>MVN_SCLKSCET.[0-9]{5}.tsc</pattern>
                <pattern>mvn_sclkscet_[0-9]{5}.tsc</pattern>
                <!-- SPK -->
                <pattern>de430s.bsp</pattern>
                <pattern>mar097s.bsp</pattern>
                <pattern>maven_struct_v[0-9]{2}.bsp</pattern>
                <pattern>date:maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp</pattern>
                <!-- CK -->
                <pattern>date:mvn_iuvs_rem_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                <pattern>date:mvn_app_pred_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                <pattern>date:mvn_app_rel_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                <pattern>mvn_swea_nom_131118_300101_v[0-9]{2}.bc</pattern>
                <pattern>date:mvn_sc_pred_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                <pattern>date:mvn_sc_rel_[0-9]{6}_[0-9]{6}_v[0-9]{2}.bc</pattern>
                <!-- DSK -->
            </grammar>

As it can be seen in the example, there are three types of entries:

   * entries without patterns e.g., ``naif0012.tls``
   * entries with patterns e.g., ``maven_v[0-9]{2}.tf``
   * entries with patterns and preceded by ``date:`` e.g.,
     ``date:maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp``

Entries without patterns will include the kernels literally specified. Entries
with patterns will look for the last version of the kernel sorted in
alphanumerical order. Entries with patterns and with ``date:``
will include the last version in alphanumerical order for each date specified
by a set of its patterns; this allows for multiple SPK and CK kernels with the
same pattern that provide coverage for a given year of for the whole mission to
be included in the appropriate order.

For example, the SPK kernel pattern
``date:maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].bsp``, includes two patterns that
specify the coverage start and finish: ``[0-9]{6}``, by including the ``date:``
prefix in the pattern, NPB will include the following kernels::

                          '$KERNELS/spk/orx_200827_201020_201020_od294_v1.bsp'
                          '$KERNELS/spk/orx_201020_210524_210103_od297_v1.bsp'
                          '$KERNELS/spk/orx_201020_201109_201020_od294_v1.bsp'

instead of only::

                          '$KERNELS/spk/orx_201020_201109_201020_od294_v1.bsp'

NPB will combine search these kernels in the ``staging_directory``,
the ``bundle_directory``, and as a last resort kernels present in
other MKs.


Meta-kernel metadata
""""""""""""""""""""

The MK metadata are all the other elements of the MK that
are not kernels to be included in the NPB MK template, available
at ``npb/templates/template_metakernel.tm``.

The metadata includes:

   * a MK description that can have patterns;
   * a keyword element that provides the values of the description patterns;
   * a data element that provides additional data to be included in the MK.

Here's an example for INSIGHT::

            <metadata>
                <description>
                    This meta-kernel lists the INSIGHT SPICE kernels providing coverage
                    for the whole $MISSION. All of the kernels (...).
                </description>
                <keyword>
                   <MISSION>mission</MISSION>
                </keyword>
                <data>
                    SPACECRAFT_ID     = -189
                    CENTER_ID         = 499
                    LANDING_TIME      = '2018-11-26T19:44:52.444'
                    LANDING_SOL_INDEX = 0
                    BODY10_GM         = 1.3271244004193938E+11
                </data>
            </metadata>


Manual Input
^^^^^^^^^^^^

If you choose to provide a manually generated MK, you only need to provide
the location of the MK(s) using the required number of entries of the
``file`` element in ``mk_inputs``. E.g. for the LADEE archive the MK section
of the configuration file can be as simple as: ::

    <meta-kernel>
        <mk_inputs>
            <file>../data/ladee_v01.tm</file>
        </mk_inputs>
        <mk name="ladee_v$VERSION.tm">
            <name>
                <pattern length="2">VERSION</pattern>
            </name>
         </mk>
    </meta-kernel>


Coverage determination
^^^^^^^^^^^^^^^^^^^^^^

Whether if you generate the MKs automatically or provide them as inputs, NPB
needs to know how to determine their coverage. The ``<coverage_kernel>``
element is optional and indicates the kernels that will determine the coverage
of the MKs by providing a list of kernel patterns and binding each of them to a
MK pattern using an attribute for each entry.

The kernel pattern must match a kernel that is included in the MK.
What follows is a Mars 2020 configuration file extract example::

        <coverage_kernels>
            <pattern>m2020_cruise_od138_v[0-9].bsp</pattern>
            <pattern>m2020_surf_rover_loc_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]_v[0-9].bsp</pattern>
        </coverage_kernels>

With this configuration, specified in the ``<mk>`` element ``m2020_v$VERSION.tm``
if the release includes the ``m2020_v01.tm``. The MK coverage will be determined
by the kernels included in the MK defined by the pattern. For example::

   m2020_cruise_od138_v1.bsp
   m2020_surf_rover_loc_0001_0083_v1.bsp

If the ``<coverage_kernel>`` element is not specified the MK coverage will be
set to the mission start and mission stop times specified in
:ref:`source/42_npb_configration_file:Mission Parameters`.

Please note that unless specified via configuration, the combined coverage
of MKs for which kernels have been provided to determine their coverage will
be used to determine the coverage of the SPICE Kernels and Miscellaneous
Collections and the Bundle coverage. More details are provided in the section
:ref:`source/22_pds4_spice_archive:Product Coverage Assignment Rules`.


Final remarks
"""""""""""""

Regardless of the content of the Meta-Kernel section of the configuration file,
MKs must have entries in the Kernel List section in order to be considered by
NPB as an input.

Generating MKs is not a trivial task. NPB's automated MK generation is designed
to support you on the task.

There is an infinite number of combinations in which a MK can be organised.
This is a problem for already existing archives that start using NPB and the
MK style of which does not match with the one provided by NPB. For such cases
NPB can still be helpful since it can be set to pause after the MK generation
and before the MK is labeled for the operator to update the automatically
generated MK at will.

When starting a new archive, NAIF recommends that you follow the style provided by
NPB.

Orbit number file
-----------------

The last element of the Configuration File is the Orbit number (ORBNUM) file
configuration. ORBNUM files, if present, are included in the miscellaneous
collection since they are not SPICE kernels. The generation of their labels
requires some special configuration elements described in this section.

An ORBNUM file provides a table of records ordered by an increasing orbit
numbering scheme. The orbit number changes at every given orbit event
(periapsis, apoapsis, etc.) and the information contained for each
record includes a number of fields. Some of these fields are expressed in a
given reference frame that makes use of a set of kernels (generally a PCK).
More information on ORBNUM files is provided in the section
:ref:`source/31_step_1_preparing_data:A Word on Orbit Number Files`. Here's an example of the
orbit number file section of the configuration file for MAVEN::

    <orbit_number_file>
        <orbnum>
            <pattern>maven_orb_rec_[0-9]{6}_[0-9]{6}_v[0-9].orb</pattern>
            <!-- Parameters from the orbnum generation preference file -->
            <event_detection_frame>
                <spice_name>IAU_MARS</spice_name>
                <description>Mars body-fixed frame</description>
            </event_detection_frame>
            <header_start_line>1</header_start_line >
            <pck>
                <kernel_name>pck0010.tpc</kernel_name>
                <description>IAU 2009 report</description>
            </pck>
            <coverage>
                <kernel cutoff="True">../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp</kernel>
            </coverage>
            <author>NAIF, JPL</author>
        </orbnum>
    </orbit_number_file>

This section requires a ``<orbnum>`` configuration element nested from
``<orbit_number_file>`` per ORBNUM file type to be archived. Each of these
``orbnum`` elements will have a number of elements to facilitate the generation
of the ORBNUM label:

.. list-table:: orbnum (nested from orbit_number_file)
   :widths: 25 60 15
   :header-rows: 1

   * - Element
     - Description
     - Required?
   * - pattern
     - Provides the ORBNUM file name with patterns to match with the ORBNUM file
       to be archived.
     - Yes
   * - event_detection_frame
     - Provides the SPICE name (e.g., IAU_MARS) and the description (e.g.,
       "Mars body-fixed frame") for the reference frame that has been used to
       detect the orbit event.
     - Yes
   * - header_start_line
     - Specifies the line where the ORBNUM file header starts (typically 1.)
     - Yes
   * - pck
     - Provides the PCK kernel name used with the event detection frame and its
       description (e.g., ``pck0010.tpc`` and ``IAU 2009 report``.)
     - Yes
   * - coverage
     - Provides the element to determine the coverage of the ORBNUM file.
       This element is described in detail in the next subsection.
     - Yes
   * - author
     - Indicates the organisation that originally generated the ORBNUM file.
       (e.g., ``NAIF, JPL``)
     - Yes


ORBNUM Coverage determination
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The coverage of an ORBNUM file can be determined in four different ways:

   * If there is a one to one correspondence with an SPK
     file, the SPK file can be provided with the ``<kernel>``
     element. The element value can be: a path to a specific kernel that
     does not have to be part of the increment, a kernel with patterns
     present in the increment, or a kernel with patterns
     present in the final directory of the archive. E.g., ::

              <kernel>maven_orb_rec_[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9]_v[0-9].bsp</kernel>

   * If there is a quasi one-to-one correspondence with an
     SPK file with a given cutoff time prior to the end
     of the SPK file, the SPK file can be provided with the
     ``<kernel>`` element. The value can be: a path to a specific kernel
     that does not have to be part of the increment, a pattern
     of a kernel present in the increment, or a pattern of
     a kernel present in the final directory of the archive.
     Currently the only cutoff pattern available is the
     boundary of the previous day of the SPK coverage stop
     time. The cutoff time is provided as an attribute of the
     ``<kernel>`` element and must be set to True or False. E.g., ::

              <kernel cutoff="True">../data/kernels/spk/maven_orb_rec_210101_210401_v2.bsp</kernel>

   * A user can provide a look up table with this configuration file, as
     follows::

        <lookup_table>
           <file name="maven_orb_rec_210101_210401_v1.orb">
              <start>2021-01-01T00:00:00Z</start>
              <finish>2021-04-01T01:00:00Z</finish>
           </file>
        </lookup_table>

     Note that in this particular case the first three and
     last three lines of the orbnum files would have provided::

        Event UTC PERI
        ====================
        2021 JAN 01 00:14:15
        2021 JAN 01 03:50:43
        2021 JAN 01 07:27:09
        (...)
        2021 MAR 31 15:00:05
        2021 MAR 31 18:36:29
        2021 MAR 31 22:12:54

   * If nothing is provided NPB will provide the coverage based on the event
     time of the first orbit and the opposite event time of the last orbit.
     This will generate a warning because it is likely to be incorrect.


Summary
-------

After going through the detailed description of every section of the
Configuration File we hope that the MAVEN example provided at the beginning of
this chapter is better understood.

Some NPB configuration files can become quite complex especially because of the
Kernel List, MK, and ORBNUM sections. A good
example of a complex configuration file is the the OSIRIS-REx sample file:
``naif-pds4-bundler/tests/naif_pds4_bundler/config/orex.xml``.

Other configuration files can be really simple: descriptions do not require
complex pattern matching and MKs are manually generated. An example of such
configuration files is the LADEE sample file: ```naif-pds4-bundler/tests/naif_pds4_bundler/config/ladee.xml``.

Generating the configuration file should be a one time effort for which the
NAIF NPB developer can assist you. After the configuration file has been setup
for the first release, it can be used with limited changes for all subsequent
releases. Changes will probably be limited to:

   * update spiceds name and/or location
   * update directories
   * addition of Kernel List elements
   * meta-kernel updates
   * new archive producer.
