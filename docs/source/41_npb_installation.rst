NPB Installation
================

Prerequisites
-------------

In order to run the NAIF PDS4 Bundler (NPB), the following software must be
present on the users's computer:

   * Python 3.8 (or higher)
   * A NAIF supported C compiler (`See link to NAIF CSPICE page <https://naif.jpl.nasa.gov/naif/toolkit_C.html>`_)

Your computer must be based on a 64-bit Unix operating system: a Linux or OSX.

A number of Python packages are required as well:

   * SpiceyPy (version 4.0.2 or higher)
   * beautifulsoup4 (version 4.9.3 or higher)
   * NumPy (version 1.19.4 or higher)
   * SetupTools (version 50.3.0 or higher)
   * xmlschema

Please note that the dependency that might cause issues is SpiceyPy. SpiceyPy
will check if you have the SPICE Toolkit in C: CSPICE, installed. If you don't
it will automatically install it for you (that is why only a NAIF compatible
C compiler is required.)

The following section will provides instructions to install NPB.


User Quickstart
---------------

Install with::

    pip install naif-pds4-bundler

To execute just to show the help message, run::

    naif-pds4-bundler -h


Manual Installation
-------------------

If you wish to install NPB from source first download or clone the project
from the `NPB GitHub repository<https://github.com/NASA-PDS/pds-template-repo-python>`_.
Then run::

   python setup.py install

in the ``naif-pds4-bundler`` top level directory. To uninstall run::

   pip uninstall spiceypy


Development and Contribution
----------------------------

For information on how to contribute to NASA-PDS codebases please take a
look at our
`Contributing guidelines <https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md>`_.


Installation
^^^^^^^^^^^^

You can install NPB in editable mode and with extra developer dependencies into
your virtual environment of choice::

    pip install --editable '.[dev]'

Configure the ``pre-commit`` hooks::

   pre-commit install && pre-commit install -t pre-push


Packaging
^^^^^^^^^

To isolate and be able to re-produce the environment for this package,
you should use a
`Python Virtual Environment <https://docs.python.org/3/tutorial/venv.html>`_.
To do so, run::

    python -m venv venv

Then exclusively use ``venv/bin/python``, ``venv/bin/pip``, etc.
(It is no longer recommended to use ``venv/bin/activate``.)

If you have ``tox`` installed and would like it to create your environment and
install dependencies for you run::

    tox --devenv <name you'd like for env> -e dev

Dependencies for development are specified as the ``dev`` ``extras_require``
in ``setup.cfg``; they are installed into the virtual environment as follows::

    pip install --editable '.[dev]'

All the source code is in ``naif_pds4_bundler`` under ``src``.


Running Tests
^^^^^^^^^^^^^

Run tests with: ::

    python -m unittest


Documentation
^^^^^^^^^^^^^

NPB uses `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to build its
documentation. You can build the NPB docs with::

    python setup.py build_sphinx

You can access the build files in the following directory relative to the
project root::

    build/sphinx/html/