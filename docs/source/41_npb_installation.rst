NPB Installation
================

Prerequisites
-------------

In order to run the NAIF PDS4 Bundler (NPB), the following software must be
present on the users's computer:

   * Python 3.8 (or higher)
   * A NAIF supported C compiler [(see link)](https://naif.jpl.nasa.gov/naif/toolkit_C.html)

Your computer must be based on a 64-bit Unix operating system: a Linux or a Mac.

A number of Python packages are required as well:

   * SpiceyPy (version 4.0.2 or higher)
   * beautifulsoup4 (version 4.9.3 or higher)
   * NumPy (version 1.19.4 or higher)
   * SetupTools (version 50.3.0 or higher)
   * Nose
   * Coverage
   * xmlschema

will check if you have the SPICE Toolkit in C: CSPICE, installed, if you don't
it will automatically install it for you (that is why only a NAIF compatible
C compiler is required.)

The following section will provides indications to install these packages and
NPB.


User Quickstart
---------------

Install with: ::

    pip install naif-pds4-bundler

To execute just to show the help message, run: ::

    naif-pds4-bundler -h


Installation
------------

You can install NPB in editable mode and with extra developer dependencies into
your virtual environment of choice:

    pip install --editable .


Running Tests
-------------

Run tests with: ::

    python -m unittest

under ``tests/naif_pds4_bundler``, or ::

    coverage run -m nose --cover-package=.
