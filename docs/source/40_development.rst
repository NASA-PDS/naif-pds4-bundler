*************************
Running Development Tools
*************************


Virtual Environments
====================
A Virtual Environment is a tool to keep the dependencies required by different
projects in separate places, by creating virtual Python environments for them.

Python uses the standard library ``venv`` to create isolated Python
environments. ``venv`` creates a folder which contains all the necessary
executables to the packages that a Python project would need.

In order to use it, create virtual environment for the NDT project::

   $ mkdir ~/virtenvs
   $ cd ~/virtenvs
   $ python3.5 -m venv ndt_3.5

This command will not include the packages that are installed globally, with
the exception of ``pip``, and ``setuptools``, the tools required to further
install, within the virtual environment, all packages required by NDT,
both for execution and development.  This can be useful for keeping the
package list clean.

To start using the virtual environment, it needs to be activated::

   $ source ~/virtenvs/ndt_3.5/bin/activate

The name of the virtual environment should now appear on the left of the
prompt: ``(ndt_3.5) Your-Computer:Directory UserName$``.  From now on any
package that you install using pip will be placed in the ndt_3.5 folder,
isolated from the global Python installation.

Before being able to install the packages required for development, testing
and execution of NDT, the following packages must be available to Python
within the virtual environment::

   $ pip list
   Package    Version
   ---------- -------
   pip        20.0.2
   setuptools 45.1.0

(*) These were the latest version on February 08, 2020.

If ``setuptools`` is not present or it is updated, please run the following
command (if it is up-to-date, the command will have no effect)::

   $ pip install -U setuptools

In order to install all the packages required for the development, testing
and execution of the NDT, run the following commands::

   $ cd /local/user/ndt
   $ pip install -r requirements.txt

If you want to go back to the 'empty' environment, you could also uninstall
all the packages listed in the requirements.txt file by running::

   $ pip uninstall -y -r requirements.txt

If no additional packages have been manually installed, the virtual
environment should now only contain the initial packages, i.e. ``pip`` and
``setuptools``.


Checking for Python code errors: PyLint
=======================================
PyLint is a tool that checks for errors in Python code, tries to enforce a
coding standard and looks for code smells.  It can also look for certain type
errors, it can recommend suggestions about how particular blocks can be
refactored and can offer you details about the code’s complexity.  The default
coding style used by PyLint is close to PEP-008:

   https://www.python.org/dev/peps/pep-0008/

PyLint will display a number of messages as it analyzes the code and it can
also be used for displaying some statistics about the number of warnings and
errors found in different files.  The messages are classified under various
categories such as errors and warnings. For further details, refer to the
official documentation:

   https://pylint.readthedocs.io/en/latest/intro.html

Follow these steps in order to run PyLint::

 # Install the PyLint tool. This step may be skipped if already installed.
 pip install pylint
 # Navigate to the source code's root directory
 cd /local/user/ndt
 # Run the PyLint tool on all the files contained in the ndt directory
 pylint -f parseable .


Running Unit-Tests: coverage
============================
Follow these steps in order to run the unit tests.  Using ``coverage`` will
ensure that also code coverage analysis is preformed::

 # Install the coverage tool. This step may be skipped if already installed.
 pip install coverage
 # Navigate to the source code's root directory
 cd /local/user/ndt
 # Run the unittests
 coverage run -m unittest discover -b -v -s .
 # Run the coverage report (reports how much of the code is called)
 coverage report -m


Running Unit-Tests: nose
========================
Follow these steps in order to run the unit tests. Using ``nosetests`` will
ensure that both the code coverage and branch analysis is performed:

1. Create a **.noserc** file in your home directory, with the following
   contents::

    [nosetests]
    cover-erase=1
    with-coverage=1
    cover-html=1
    cover-branches=1

2. Install the nosetest tool.  This step may be skipped if already installed::

   $ pip install nose

3. Navigate to the code's unittests directory and run the unit tests::

   $ cd /local/user/ndt/ndt/tests/unittests
   $ nosetests --cover-package=ndt

4. Open the results on your web browser::

   $ open cover/index.html


Documentation Generator: Sphinx
===============================
Sphinx is a tool that makes it easy to create documentation for software
projects in a range of languages, among them Python.  It supports several
output formats: HTML, LaTeX (and PDF), ePub, Texinfo, man pages,
plain text, ...  For further details, please refer to the official
Sphinx documentation:

   http://www.sphinx-doc.org/

Follow these steps in order to generate the NAIF Development Toolkit
documentation::

 # Install the Sphinx tool. This step may be skipped if already installed.
 pip install sphinx_rtd_theme
 # Navigate to the documuentation directory.
 cd /local/ndt/docs
 # Initiate the documentation build command.
 make html
 # Open the web site in your default browser
 _build/html/index.html

A latex and a PDF generators also exist::

 make latex
 make latexpdf

A useful reference for writing Python documentation is,

    https://docs.python.org/devguide/documenting.html

It outlines the syntax used for formatting text, as well
as good documentation practices.
