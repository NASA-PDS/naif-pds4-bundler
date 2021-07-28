#! /bin/csh -f
# NPB - Environment setup script for NAIF
# MCS/NAIF, Jul 8 2021
#
# This script provides guidelines to setup a Python Virtual Environment
# for NPB. 
#
# It is assumed that there is a preexisting virtenvs directory
#

cd $HOME/virtenvs

python3 -m venv npb_3.9

cd npb_3.9

git clone https://github-fn.jpl.nasa.gov/NAIF/naif-pds4-bundle.git

source bin/activate

# or source bin/activate.csh

pip3 install -U setuptools

cd naif-pds4-bundle

pip3 install -r requirements.txt

pip3 install sphinx_rtd_theme

pip3 install -e .

#
# Run the tests
#
cd npb

coverage run -m nose --cover-package=.
#
# Now NPB can be used with:
#  
#  $naif-pds4-bundle
#


