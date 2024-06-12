Reporting Bugs
==============

In order to report a bug either in this document or the NAIF PDS4 Bundler
software package you can open a issue in the ``naif-pds4-bundler`` `GitHub
repository Issues section <https://github.com/NASA-PDS/naif-pds4-bundler/issues>`_.

Click on the "New issue" button and follow the instructions provided in the
issue template.


Contact Information
===================

If you have any questions on any aspect of the generation
of a SPICE kernel archive please contact Boris Semenov (Boris.V.Semenov@jpl.nasa.gov)

at the

     **PDS Navigation and Ancillary Information Facility (NAIF)**,
     MAIL STOP 301-121,
     Jet Propulsion Laboratory,
     California Institute of Technology,
     4800 Oak Grove Drive,
     Pasadena, CA, 91109-8099

     WWW Site: https://naif.jpl.nasa.gov


References
==========

.. [PDS4STD] Planetary Data System Standards Reference, Version 1.22.0
             March 31, 2024, Jet Propulsion Laboratory, California Institute of
             Technology Pasadena, California

.. [PDS3GUIDE] PDS Navigation and Ancillary Information Facility (NAIF)
             `SPICE Archive Preparation Guide <https://naif.jpl.nasa.gov/pub/naif/pds/doc/archiving_guide/spice_archiving_guide.txt>`_

.. [KERNELS] PDS Navigation and Ancillary Information Facility (NAIF)
             `Introduction to Kernels Tutorial <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/Tutorials/pdf/individual_docs/12_intro_to_kernels.pdf>`_

.. [MAKLABEL] PDS Navigation and Ancillary Information Facility (NAIF)
             `MAKLABEL Users's Guide <https://naif.jpl.nasa.gov/pub/naif/utilities/MacIntel_OSX_64bit/maklabel.ug>`_

.. [SPICEYPY] Annex et al., (2020). SpiceyPy: a Pythonic Wrapper for the SPICE
              Toolkit. Journal of Open Source Software, 5(46), 2050,
              https://doi.org/10.21105/joss.02050


Utility Programs
----------------

The executables and User's Guides for the following utility programs::

   ARCHTYPE  BINGO     BRIEF     CKBRIEF   CKSLICER  CKSMRG
   COMMNT    DAFCAT    MAKLABEL  ORBNUM    SPACIT    SPKDIFF
   SPY       BFF       FRMDIFF   OPTIKS

mentioned in this document are available from the "Utilities" page on
the NAIF web site, `NAIF Utilities <https://naif.jpl.nasa.gov/naif/utilities.html>`_.

Note that for some environments (e.g. Linux, Mac/OSX) these utilities
can not be statically linked and require certain shared object libraries
in order to run. Usually these libraries can be installed on your
computer by installing the compiler used to compile the executables
(e.g. gfortran/gcc).


Tutorials
---------

A collection of tutorials covering most aspects of using SPICE kernel
files and allied Toolkit software is available from the "Tutorials"
page on the NAIF web site, `NAIF Tutorials <https://naif.jpl.nasa.gov/naif/tutorials.html>`_.


SPICE Kernel Archives
---------------------

SPICE archives are available on the NAIF server either directly,
from the `FTP-like HTTP page <https://naif.jpl.nasa.gov/pub/naif/pds/pds4/>`_,
or from the `NAIF Data page <https://naif.jpl.nasa.gov/naif/data_archived.html>`_.

They may be useful as examples for new archive producers.


PDS Standards
-------------

The PDS standards Documents are available on the PDS documents web site,
`PDS4 web site Data Standards <https://pds.nasa.gov/datastandards/documents/>`_
of these the following might be most useful:

   * Concepts Document
   * Data Provider's Handbook
   * Standard's Reference
   * Context Products


PDS Validate Tool
-----------------

The PDS Validate tool is available at the
`validate tool website <https://nasa-pds.github.io/validate/>`_.
