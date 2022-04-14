# Information extracted from
# https://docs.gitlab.com/omnibus/development/s390x.html
#
# docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
# docker run --rm -it s390x/ubuntu bash
#

FROM s390x/ubuntu

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install software-properties-common
RUN apt install python3.8
RUN apt install python3-pip
RUN apt install python3.8-venv

RUN apt install git
WORKDIR /root
RUN git clone https://github.com/NASA-PDS/naif-pds4-bundler.git
WORKDIR /root/naif-pds4-bundler
RUN python3.8 -m venv venv
RUN ./venv/bin/python3.8 -m pip install -e .
RUN ./venv/bin/python3.8 -m unittest discover -s tests/naif_pds4_bundler
