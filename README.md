# 🪐 NAIF PDS4 Bundler

Software package by [NASA's Navigation and Ancillary Information Facility] (https://naif.jpl.nasa.gov/naif/) that enables SPICE kernels archive producers to get familiar with,
design, and generate [Planetary Data System](https://pds.nasa.gov/) SPICE
archives from end-to-end using the applicable PDS4 standards.

## 🛠️️ Prerequisites

   * A computer based on 64-bit Unix operating system: a Linux or a Mac.
   * Python 3.8 (or higher)
   * A NAIF supported C compiler [(see link)](https://naif.jpl.nasa.gov/naif/toolkit_C.html)

## ⎆ Installation

Install with:

    pip install naif-pds4-bundler

To execute just to show the help message, run:

    naif-pds4-bundler --help

Run tests under `tests/naif_pds4_bundler`` with:

    python -m unittest

See the online documentation for [Installation](https://nasa-pds.github.io/naif-pds4-bundler/source/41_npb_installation.html) instructions.

👉 _Note:_ The above commands demonstrate typical usage with a command-line prompt, such as that provided by the popular `bash` shell; your own prompt may appear differently and may vary depending on operating system, shell choice, and so forth.

## 📄 Documentation

Installation and Usage information can be found in the documentation online
at https://nasa-pds.github.io/naif-pds4-bundler/ or the latest version is
maintained under the `docs` directory.

The documentation describes the process to prepare SPICE archives and describes the NAIF
approach to using PDS4 standards in great detail.

### 🐈 To build the Sphinx HTML documentation:

```console
$ python3 -m venv venv
$ venv/bin/python setup.py develop
$ venv/bin/python setup.py build_sphinx
running build_sphinx
…
The HTML pages are in build/sphinx/html.
```

## 👏 Contribute

All users and developers of the NASA-PDS software are expected to abide by our [Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md). Please read this to ensure you understand the expectations of our community. For information on how to contribute to NASA-PDS codebases please take a look at our [Contributing guidelines](https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md).

- Issue Tracker: https://github.com/NASA-PDS/naif-pds4-bundler/issues
- Source Code: https://github.com/NASA-PDS/naif-pds4-bundler

## 💁‍♀️ Support

If you are having issues file a bug report in Github: https://github.com/NASA-PDS/naif-pds4-bundler/issues

Or you can reach us at https://pds.nasa.gov/?feedback=true

## 💳 License

The project is licensed under the Apache License, version 2. See the `LICENSE.txt` file for details.
