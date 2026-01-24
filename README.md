# 🪐 NAIF PDS4 Bundler

[![JOSS DOI](https://joss.theoj.org/papers/10.21105/joss.04327/status.svg)](https://doi.org/10.21105/joss.04327)
[![Testing NPB](https://github.com/NASA-PDS/naif-pds4-bundler/workflows/Testing%20NPB%20%F0%9F%AA%90/badge.svg "Latest testing log")](https://github.com/NASA-PDS/naif-pds4-bundler/actions?query=workflow%3A%22Testing+NPB+%F0%9F%AA%90%22)
[![Unstable Build](https://github.com/NASA-PDS/naif-pds4-bundler/workflows/%F0%9F%A4%AA%20Unstable%20integration%20&%20delivery/badge.svg "Latest unstable integration log")](https://github.com/NASA-PDS/naif-pds4-bundler/actions?query=workflow%3A%22%F0%9F%A4%AA+Unstable+integration+%26+delivery%22)
[![Stable Build](https://github.com/NASA-PDS/naif-pds4-bundler/workflows/%F0%9F%98%8C%20Stable%20integration%20&%20delivery/badge.svg "Latest stable integration log")](https://github.com/NASA-PDS/naif-pds4-bundler/actions?query=workflow%3A%22%F0%9F%98%8C+Stable+integration+%26+delivery%2)

Software package by [NASA's Navigation and Ancillary Information Facility](https://naif.jpl.nasa.gov/naif/)
that enables SPICE kernels archive producers to get familiar with,
design, and generate [Planetary Data System](https://pds.nasa.gov/) SPICE
archives from end-to-end using the applicable PDS4 standards.

## 🛠️️ Prerequisites

   * A computer based on a 64-bit Unix operating system: Linux or Mac
   * If using a Windows machine, NPB can be installed using 'Windows Subsystem for Linux' (WSL).
   * Python 3.8 (or higher)
   * A NAIF supported C compiler [(see link)](https://naif.jpl.nasa.gov/naif/toolkit_C.html)

## ⎆ Installation

Install with:

    pip install naif-pds4-bundler

To execute just to show the help message, run:

    naif-pds4-bundler --help

See the online documentation for [Installation](https://nasa-pds.github.io/naif-pds4-bundler/41_npb_installation.html) instructions.

👉 _Note:_ The above commands demonstrate typical usage with a command-line prompt, such as that provided by the popular `bash` shell; your own prompt may appear differently and may vary depending on operating system, shell choice, and so forth.

## 📄 Documentation

Installation and Usage information can be found in the documentation online
at https://nasa-pds.github.io/naif-pds4-bundler/ or the latest version is
maintained under the `docs` directory.

The documentation describes the process to prepare SPICE archives and describes the NAIF
approach to using PDS4 standards in great detail.

## 👏 Contribute

All users and developers of the NASA-PDS software are expected to abide by our [Code of Conduct](https://github.com/NASA-PDS/.github/blob/main/CODE_OF_CONDUCT.md). Please read this to ensure you understand the expectations of our community. For information on how to contribute to NASA-PDS codebases please take a look at our [Contributing guidelines](https://github.com/NASA-PDS/.github/blob/main/CONTRIBUTING.md).

- Issue Tracker: https://github.com/NASA-PDS/naif-pds4-bundler/issues
- Source Code: https://github.com/NASA-PDS/naif-pds4-bundler

## 💁‍♀️ Support

If you are having issues file a bug report in GitHub: https://github.com/NASA-PDS/naif-pds4-bundler/issues

Or you can reach us at https://pds.nasa.gov/?feedback=true

## 💳 License

The project is licensed under the Apache License, version 2. See the `LICENSE.txt` file for details.
