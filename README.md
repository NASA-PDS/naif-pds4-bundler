# NAIF PDS4 Bundler

The NAIF PDS4 Bundler (NPB) is a a pipeline that generates a SPICE archive in
the shape of a PDS4 Bundle.

The pipeline is constructed by the orchestration of a family of classes that
can also be used independently.

Please visit our website at: https://nasa-pds.github.io/naif-pds4-bundler

It has useful information for developers and end-users.


## Prerequisites

   * Python 3.8 (or higher)
   * A NAIF supported C compiler [(see link)](https://naif.jpl.nasa.gov/naif/toolkit_C.html)

Your computer must be based on a 64-bit Unix operating system: a Linux or a Mac.

### Dependencies

The following Python packages will be installed:

   * SpiceyPy (version 4.0.2 or higher)
   * beautifulsoup4 (version 4.9.3 or higher)
   * NumPy (version 1.19.4 or higher)
   * SetupTools (version 50.3.0 or higher)
   * xmlschema

Please note that the dependency that might cause issues is SpiceyPy. SpiceyPy
will check if you have the SPICE Toolkit in C: CSPICE, installed, if you don't
it will automatically install it for you (that is why only a NAIF compatible
C compiler is required.)

## User Documentation

Please visit the documentation at: https://nasa-pds.github.io/naif-pds4-bundle/


## User Quickstart

Install with:

     

To execute just to show the help message, run:

    naif-pds4-bundler -h


## Code of Conduct

All users and developers of the NASA-PDS software are expected to abide by our [Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md). Please read this to ensure you understand the expectations of our community.


## Contributing

For information on how to contribute to NASA-PDS codebases please take a look at our [Contributing guidelines](https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md).


## Installation

Install in editable mode and with extra developer dependencies into your virtual environment of choice:

    pip install --editable '.[dev]'

Configure the `pre-commit` hooks:

    pre-commit install && pre-commit install -t pre-push


### Packaging

To isolate and be able to re-produce the environment for this package, you should use a [Python Virtual Environment](https://docs.python.org/3/tutorial/venv.html). To do so, run:

    python -m venv venv

Then exclusively use `venv/bin/python`, `venv/bin/pip`, etc. (It is no longer recommended to use `venv/bin/activate`.)

If you have `tox` installed and would like it to create your environment and install dependencies for you run:

    tox --devenv <name you'd like for env> -e dev

Dependencies for development are specified as the `dev` `extras_require` in `setup.cfg`; they are installed into the virtual environment as follows:

    pip install --editable '.[dev]'

All the source code is in `naif_pds4_bundler` under `src`.


### Tests

Run tests with:

    python -m unittest

under ``tests/naif_pds4_bundler``, or:

    coverage run -m nose --cover-package=.


### Documentation

NPB uses [Sphinx](https://www.sphinx-doc.org/en/master/) to build its
documentation. You can build the NPB docs with:

    python setup.py build_sphinx

You can access the build files in the following directory relative to the project root:

    build/sphinx/html/
