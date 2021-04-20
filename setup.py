#!/usr/bin/python
"""

   @author: Marc Costa Sitja (JPL)

"""

from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

#
# Get the long description from the README file
#
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

def get_version():

    with open('version', 'r') as f:
        for line in f:
            version = line

    return version

setup(
        name='naif-pds4-bundle',

        version=get_version(),

        description='PDS4 Bundle and PDS3 data set SPICE kernels archive generation',
        url="https://mcosta@repos.cosmos.esa.int/socci/scm/spice/arcgen.git",

        author='Marc Costa Sitja (JPL)',
        author_email='Marc.Costa.Sitja@jpl.nasa.gov',

        # Classifiers
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Intended Audience :: SPICE kernels producers',
            'Topic :: Geometry Pipeline :: Planetary Science :: Geometry Computations',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
        ],

        #
        # Keywords
        #
        keywords=['nasa', 'jpl', 'pds', 'naif', 'spice', 'planetary', 'geometry'],

        #
        # Packages
        #
        packages=find_packages(),

        #
        # Include additional files into the package
        #
        include_package_data=True,

        #
        # Dependent packages (distributions)
        #
        python_requires='>=3',

        #
        # Scripts
        #
        entry_points={
            'console_scripts': ['naif-pds4-bundle=npb.main:main']}

      )