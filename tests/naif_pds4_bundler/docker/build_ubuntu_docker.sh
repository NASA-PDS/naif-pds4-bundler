#!/bin/bash

#
# This script assumes a Docker installation and is aimed to provide support
# to build and run a Docker image to run NPB tests in an Ubuntu Linux box.
#
TAG_NAME='naif-pds4-bundler:latest'
sudo docker build -t $TAG_NAME -f ubuntu.Dockerfile .

#
# You can access the image terminal with:
#
#    $ docker run -it naif-pds4-bundler:latest
#
