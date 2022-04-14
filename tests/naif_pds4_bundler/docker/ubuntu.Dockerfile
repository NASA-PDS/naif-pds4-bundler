FROM ubuntu:18.04

#
# Disable Prompt During Packages Installation.
#
ENV DEBIAN_FRONTEND=noninteractive

#
# Install Python 3.8.
#
RUN apt update
RUN apt install -y software-properties-common
RUN apt install -y python3.8
RUN apt install -y python3-pip
RUN apt install -y python3.8-venv

#
# Install Git, a virtual environment, and NPB.
#
RUN apt install -y git
WORKDIR /root
RUN git clone https://github.com/NASA-PDS/naif-pds4-bundler.git
WORKDIR /root/naif-pds4-bundler
RUN python3.8 -m venv venv
RUN ./venv/bin/python3.8 -m pip install -e .

#
# Run NPB tests.
#
RUN ./venv/bin/python3.8 -m unittest discover -s tests/naif_pds4_bundler
