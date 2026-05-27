#!/bin/bash
#
# This script assumes a Docker installation and builds a Docker image to run
# NPB tests using the Red Hat Universal Base Image (UBI 9).
#
# UBI is freely available and does not require a Red Hat subscription or
# credentials to pull or use.
#
TAG_NAME='naif-pds4-bundler:latest'

sudo  docker build -t $TAG_NAME -f rhel.Dockerfile .

#
# You can access the image terminal with:
#
#    $ docker run -it naif-pds4-bundler:latest
#