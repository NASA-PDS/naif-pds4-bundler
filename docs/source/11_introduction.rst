Applicability
=============

This document is written for anyone who will be preparing a new or
augmented SPICE data archive for submission to the NAIF Node of the PDS.
However, following the standards and procedures provided in this document
is highly encouraged for any entity involved in archiving SPICE ancillary
data at some other archive facility.


Motivation
==========

NAIF's approach to creating SPICE kernel archives can be summarized by this
statement:

**All SPICE data for a given mission are archived as UNIX text files and
little-endian binary files in a single, accumulating PDS4 archive bundle
for that mission, having the same directory structure, the same set of meta
information files, data file labels with the same structure, and archive
documents with the same structure as all PDS4 SPICE archive bundles
produced by NAIF.**

Each time that an accumulating archive is released we either refer this to
a release of the archive or to an archive increment. In this document you
will find both terms used interchangeably.

This document should be seen as something more than a user's software guide
since it describes the whole process to prepare SPICE archives and it also
describes the NAIF approach to using PDS4 standards in great detail (These
are the standards adopted by the consortium of agencies comprising the
International Planetary Data Alliance.) Some of the standards may seem rather
"picky" or unnecessary, and indeed there are a few items included that are not
currently used/useful. But adhering to all of these details is critical to the
current and future use of archived SPICE data, especially to achieve
interoperability across national archives, and, to facilitate use of archived
SPICE data in data search, retrieval and processing tools that are, or will be,
part of archive systems.

It is imperative that archive preparers carefully check and re-check all
components of an archive -- whether it is a new one or an augmentation
to an existing one -- before it is submitted for ingestion. NAIF
through the NAIF PDS4 Bundler package and this document, provides
guidance, recommendations, and tools to generate and to validate
the archives. These can help a great deal, but there is much that only the
archive preparer can do.


How to Read This Document?
==========================

We are glad that you got this far, but you’ve got a ways to go.
You might not have to look into each section of this document.
If you already know about SPICE you can skip the rest of this chapter. If
you are very familiar with PDS SPICE kernel archives you can skip the
:ref:`20_spice_kernel_archive_description:SPICE Kernel Archive Description`
chapter and jump directly to
:ref:`30_spice_kernel_archive_preparation_guide:SPICE Kernel Archive Preparation Guide`.

Also if you are only interested in the NAIF PDS4 Bundler software package
itself you can jump to :ref:`40_naif_pds4_bundler_user_guide:NAIF PDS4 Bundler User Guide`. The installation
instructions are available at :ref:`41_npb_installation:NPB Installation`.

Needless to say, the chapter
:ref:`50_api_docs:API Reference`
dedicated to the description of functions and
modules is aimed at potential contributors to the further development of this
NPB software package, if you are not planning to do so, don't bother to take a
look at that chapter.
