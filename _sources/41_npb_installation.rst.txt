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
   * SetupTools (version 50.3.0 or higher)
   * xmlschema
   * nose
   * coverage
   * xmlschema
   * requests

Please note that the dependency that might cause issues is SpiceyPy. SpiceyPy
will check if you have the SPICE Toolkit in C: CSPICE, installed. If you don't
it will automatically install it for you.

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
from the `NPB GitHub repository <https://github.com/NASA-PDS/naif-pds4-bundler>`_.
Then run::

   python setup.py install

in the ``naif-pds4-bundler`` top level directory. To uninstall run::

   pip uninstall naif-pds4-bundler


Known Installation Issues
^^^^^^^^^^^^^^^^^^^^^^^^^

Certain versions of Python might report an installation error triggered by
the installation of the NumPy package that is required by SpiceyPy. The error
should point to a missing or invalid Cython package. In order to fix this error
please update Python SetupTools and Cython packages by running the following
commands::

   python -m pip install -U setuptools
   python -m pip install cython

Then you can run the installation as usual::

   python setup.py install


Development and Contribution
----------------------------

For information on how to contribute to NASA-PDS codebases please take a
look at our
`Contributing guidelines <https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md>`_.


Installation
^^^^^^^^^^^^

You can install NPB in editable mode and with extra developer dependencies into
your virtual environment of choice by running::

    pip install --editable '.[dev]'

in the ``naif-pds4-bundler`` top level directory. You can configure
the ``pre-commit`` hooks::

   pre-commit install && pre-commit install -t pre-push


Packaging
^^^^^^^^^

To isolate and be able to reproduce the environment for this package,
you should use a
`Python Virtual Environment <https://docs.python.org/3/tutorial/venv.html>`_.
To do so, run::

    python -m venv venv

Then exclusively use ``venv/bin/python``, ``venv/bin/pip``, etc.
Alternatively  use ``venv/bin/activate``.

If you have ``tox`` installed and would like it to create your environment and
install dependencies for you run::

    tox --devenv <name you'd like for env> -e dev

Dependencies for development are specified as the ``dev`` ``extras_require``
in ``setup.cfg``; they are installed into the virtual environment as follows::

    pip install --editable '.[dev]'

All the source code is in ``naif_pds4_bundler`` under ``src``.


Running Tests
^^^^^^^^^^^^^

Run tests under the ``tests/naif_pds4_bundler`` directory with::

    python -m unittest discover -s tests/naif_pds4_bundler

NPB tests use data available in the package and involves file and directory
creation and destruction. Depending on your environment the package might be
in a location where your user can have permission issues. To solve this issue
NPB uses a temporary directory for the tests. In order to do this, NPB searches
a standard list of directories to find one which the calling user can create
files in. The list is:

   #. The directory named by the ``TMPDIR`` environment variable.

   #. The directory named by the ``TEMP`` environment variable.

   #. The directory named by the ``TMP`` environment variable.

   #. The directories ``/tmp``, ``/var/tmp``, and ``/usr/tmp``, in that order.

   #. As a last resort, the current working directory.

If need be, create of modify one of the environment variables described above
to ensure your user has the appropriate permissions.

You can also run the tests using a DOCKER container. Assuming that you have
DOCKER installed, you can use the DOCKER file from
``naif-pds4-bundler/tests/naif_pds4_bundler/docker/dockerfile``

Further indications on how to use DOCKER are available in the provided Shell
script ``naif-pds4-bundler/tests/naif_pds4_bundler/docker/build_docker.sh``.

The implemented tests are documented in section :ref:`tests:tests package`


Documentation
^^^^^^^^^^^^^

NPB uses `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to build its
documentation. You can build the NPB docs with::

    python setup.py build_sphinx

You can access the build files in the following directory relative to the
project root::

    build/sphix/html

or with::

    make html

under ``docs/naif_pds4_bundler``. You can access the build files in the following directory relative to the
project root::

    docs/_build
