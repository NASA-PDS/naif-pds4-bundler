*******************************
Appendix: NPB for PDS3 Archives
*******************************

NPB is capable to generate PDS3 SPICE kernels data sets increments. This
capability is not intended for people external to NAIF and is only adept
for PDS3 data sets archived by or for NAIF.

For PDS3 archives, NPB follows the PDS3 standard and uses NAIF's PDS3 archiving
approach [PDS3GUIDE]_. The NAIF PDS3 archiving guide document is available
under: ``naif-pds4-bundler/docs/spice_archiving_guide.txt``

There might be some concepts and/or words used in this chapter that
you might not know or understand, if so please take a look at the documents
that describe the PDS3 standards. These documents are available at the
`PDS3 Data Standards page <https://pds.nasa.gov/datastandards/pds3/>`_.


Configuration File Particulars
==============================

PDS3 archives require several modifications to the NPB configuration file
that are not documented in section :ref:`42_npb_configuration_file:The Configuration File`.

Use the MSL, the MRO or the JUNO configuration file examples as references. They
are provided under: ``/Users/mcosta/pds/naif-pds4-bundler/tests/naif_pds4_bundler/config``

The most relevant change is the inclusion of the PDS3 Mission Template element.
This element incorporates the so called Mission Template Configuration File
used to generate PDS3 labels with the NAIF utility ``MAKLABEL``.

Finally, another particularity is that the meta-kernels and ORBNUM files must
have an entry in the Kernel List section. The value of the ``mklabel_options``
and ``descriptions`` elements is irrelevant, you can use ``N/A``.


Using NPB for PDS3 Archives
===========================

You can use NPB for PDS3 archives exactly in the same way that you would for a
PDS4 archive. The only differences being present in the content of NPB's
logging. Please refer to section
:ref:`43_using_npb:Using NPB`, for more information.


Binary kernels endianness in PDS3 archives
------------------------------------------

NAIF requires all their PDS3 archives to have ``BIG-IEEE`` binary kernels. The
same applies to "old" archives from other agencies (ESA, JAXA) such as
Mars Express (``mex-e_m-spice-6-v1.0``), Venus Express (``vex-e_v-spice-6-v1.0``),
Rosetta (``ros-e_m_a_c-spice-6-v1.0``), and Hayabusa (``hay-a-spice-6-v1.0``).

The only intentional exception to this rule are DSKs in the DAWN archive
(``dawn-m_a-spice-6-v1.0``) which are ``LTL-IEEE``.

For "recent", PDS3 ESA archives (``vex-e_v-spice-6-v2.0``, ``mex-e_m-spice-6-v2.0``,
and ``ro_rl-e_m_a_c-spice-6-v1.0``) and for JAXA's Venus Climate Orbiter Akatsuki
(``co-v-spice-6-v1.0``) archive endianness is set to ``LTL-IEEE``.


Known differences from archives generated with NAIF's PDS3 archiving approach
=============================================================================

When generating a PDS3 data set increment with NPB compared to following the
*NAIF's PDS3 archiving approach* -which implies using the NAIF utility
``MAKLABEL`` and several Perl scripts such as ``label_them_all.pl``,
``xfer_index.pl``, and ``mkpdssum.pl``-. The following differences are known and
are accepted by NAIF:

   * ``MAKLABEL`` introduces a whitespace in the empty lines of the comments
     with attached labels for binary kernels. This whitespace is not present
     with NPB.
   * The order of the items in the ``INDEXED_FILE_NAME`` field of the ``INDEX``
     file label is alphabetical with NPB but somewhat "random" with ``xfer_index.pl``.
