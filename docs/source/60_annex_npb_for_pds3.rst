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
that are not documented in section :ref:`source/42_npb_configuration_file:The Configuration File`.

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
:ref:`source/43_using_npb:Using NPB`, for more information.


Known differences from archives generated with NAIF's PDS3 archiving approach
=============================================================================

When generating a PDS3 data set increment with NPB compared to following the
*NAIF's PDS3 archiving approach* -which implies using the NAIF utility
``MAKLABEL`` and several Perl scripts such as ``label_them_all.pl``,
``xfer_index.pl``, and ``mkpdssum.pl``-. The following differences
