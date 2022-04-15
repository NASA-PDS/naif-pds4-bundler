#!/bin/bash

#
# This script assumes a Docker installation and is aimed to provide support
# to build and run a Docker image to run NPB tests in a Red Hat Rhel7 platform.
#

#
# Assumes the existence of a script that provides the username and password
# of a Red Hat account. E.g.:
#
#    $ cat ~/.secrets/passwords.csh
#    export REDHAT_USERNAME="*****"
#    export REDHAT_PASSWORD=*****"
#
source $HOME/.secrets/passwords.csh

TAG_NAME='naif-pds4-bundler:latest'

git clone https://github.com/NASA-PDS/naif-pds4-bundler.git

#
# Some Docker versions have issues passing arguments to environment variables
# if that is the case provide the username and password values directly.
#
sudo  docker build -t $TAG_NAME --build-arg username=$REDHAT_USERNAME --build-arg password=$REDHAT_PASSWORD -g rhel.Dockerfile .

#
# You can access the image terminal with:
#
#    $ docker run -it naif-pds4-bundler:latest
#
