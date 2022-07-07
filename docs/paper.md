---
title: 'NAIF PDS4 Bundler: A Python package to generate SPICE PDS4 archives'
tags:
  - Python
  - planetary science
  - data archive
  - SPICE
  - geometry
  - navigation
authors:
  - name: Marc Costa Sitja
    orcid: 0000-0003-0055-2959
    affiliation: "1"
affiliations:
 - name: Jet Propulsion Laboratory, California Institute of Technology, USA
   index: 1
date: 25 March 2022
bibliography: paper.bib

---

# Summary

``naif-pds4-bundler`` (NPB) is a Python package that enables SPICE kernels
archive producers to become familiar with, design, and generate Planetary Data
System (PDS) [@Prockter2021Planetary] SPICE archives from end-to-end using the
applicable PDS4 standards [@pds4standard].

A SPICE archive includes the complete set of SPICE data files (kernel files) for
a given mission, which can be accessed using SPICE software. The SPICE data
contain geometric and other ancillary information needed to recover the full
value of science instrument data. In particular, SPICE kernels provide spacecraft
and planetary ephemerides, spacecraft and instrument orientation, instrument
mounting alignments, data specifying target body size, shape and orientation,
and data needed for relevant time conversions. Data in SPICE kernel files must
be accessed using the software called the SPICE Toolkit produced and distributed
by the Navigation and Ancillary Information Facility (NAIF) Node of the
Planetary Data System [@ACTON199665; @ACTON20189].

NPB is an open source software project led by the NAIF group at the Jet Propulsion
Laboratory (JPL) with the support of the PDS Engineering Node (PDS-EN).
NPB makes use of the SPICE Toolkit through the open source Python wrapper
SpiceyPy [@Annex2020]. NPB is hosted at the [NASA PDS GitHub repository](https://github.com/NASA-PDS/naif-pds4-bundler) and
is easy to install since it is hosted in the Python Package Index
and includes a number of ready-to-go examples that facilitate the task to set
it up.

NPB also includes [documentation](https://nasa-pds.github.io/naif-pds4-bundler/)
that describes the process to prepare SPICE archives and describes the NAIF
approach to using PDS4 standards in great detail. Adhering to this approach is
critical to the current and future use of archived SPICE data, especially to
achieve interoperability across national archives, and, to facilitate use of
archived SPICE data in data search, retrieval and processing tools that are, or
will be, part of archive systems.

The planetary data community and SPICE archive producers are encouraged to
contribute to the project following the [NASA PDS Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md).
The expected forum for discussions related to NPB is the [OpenPlanetary community](http://openplanetary.co/).


# Statement of need

SPICE is widely used in the planetary data community and is the recommended
ancillary data standard by the [International Planetary Data Alliance](https://planetarydata.org/)
(IPDA). Most planetary science space missions that use SPICE data
normally intend to generate a PDS4 SPICE kernels archive; NPB
is aimed to make things easier for those generating such archives.

NPB is used in the day-to-day archiving activities of NAIF and is used to
generate all the PDS4 archives: Mars 2020 [@mars2020.spice], MAVEN [@maven.spice],
InSight [@insight.spice], OSIRIS-REx [@orex.spice], and LADEE [@ladee.spice].

Both the European Space Agency (ESA) SPICE Service (ESS) and the Japanese Space
Exploration Agency (JAXA) Data Archives and Transmission System (DARTS) have
started using it for their PDS4 SPICE Archives: ExoMars2016 [@em16.spice],
BepiColombo [@bc.spice], Venus Climate Orbiter Akatsuki, and Hayabusa2.

In the future, in addition to supporting NASA’s, ESA’s and JAXA’s SPICE PDS4
archives, NPB could also help the rising community of science small satellites
and commercial science payloads that could greatly benefit from such a package
to reduce the effort spent on generating SPICE PDS4 archives.


# State of the field

Understanding and generating the PDS4 artifacts required by PDS4 archives is a
challenging endeavor. Because of this, PDS is making an effort to generate and
gather [training material](https://pds.nasa.gov/datastandards/training/) and to
provide a number of tools to assist archive producers. NPB is part of this effort
and benefits from NAIF's terse usage of the PDS4 standards and enables
archive producers to generate a PDS4 SPICE archive from end-to-end with minimal effort.

Different nodes of the PDS offer a number of tools adequate for the data archived
in their holdings. PDS-EN provides the [Metadata Injector for PDS Labels](https://nasa-pds.github.io/mi-label/) [@milabel],
a command-line interface for generating PDS4 Labels using a user provided PDS4 XML
template and input (source) data products. The PDS Geosciences Node provides [MakeLabels](https://pds-geosciences.wustl.edu/tools/makelabels.html),
a program that generates PDS4 labels using a label template and one or two Excel
spreadsheets. The PDS Small Bodies Node (SBN) also provides a [suite of tools](https://pds-smallbodies.astro.umd.edu/tools/tools_file-label.shtml)
to assist in label generation. In addition, SBN provides an end-to-end web-based
tool to generate PDS4 archives, but it only supports Images (FITS and 2-D arrays)
and tables.


# Acknowledgements

The author would like to thank the NAIF group at JPL, especially Boris
Semenov, the PDS-EN at JPL, and the colleagues of the ESA SPICE Service and the
Planetary Science Archive at the European Space and Astronomy Center.
This project was carried out at the Jet Propulsion Laboratory, California
Institute of Technology, under a contract with the National Aeronautics and
Space Administration (80NM0018D0004).

# References
