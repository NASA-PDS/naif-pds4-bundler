********************************
SPICE Kernel Archive Description
********************************

This section describes the structure and contents of a PDS SPICE
bundle following the PDS4 standard using the NAIF approach [PDS3GUIDE]_.

There might be some concepts and/or words used in this chapter that
you might not know or understand, if so please take a look at the documents
that describe the PDS4 standards. These documents are available at the
`PDS Data Standards Document page <https://pds.nasa.gov/datastandards/documents>`_.

Don't worry, everything that is specified in this chapter is implemented by the
NAIF PDS4 Bundler: the idea of this chapter is to provide you background and the
rationale of how and why SPICE kernel archives are implemented this way.

.. toctree::
   :maxdepth: 3

   21_naif_approach
   22_pds4_spice_archive


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
science data product types). It is the internal comments in the kernels and
other meta-information provided in the SPICE Archive Description Document
(SPICEDS) that one needs to understand to use kernels in the proper way.
