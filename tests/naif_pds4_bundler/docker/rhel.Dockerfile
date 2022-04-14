ARG username
ARG password

FROM registry.access.redhat.com/rhel7/rhel

ENV USERN ${username}
ENV PASSW ${password}

RUN subscription-manager register --username ${USERN} --password ${PASSW} --auto-attach
RUN yum -y update
RUN yum install -y gcc
RUN yum install -y libgfortran
RUN yum install -y git

#
# Python 3.6 (pip3 install is enough)
#
RUN yum install openssl -y
RUN yum install openssl-devel -y
RUN yum install wget -y
RUN yum install zlib-devel -y
RUN yum install make -y
RUN yum install bzip2-devel -y
RUN yum install libffi-devel -y
RUN wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz
RUN tar xzf Python-3.9.6.tgz
WORKDIR Python-3.9.6
RUN ls
RUN ./configure
RUN make
RUN make install
WORKDIR /
RUN ls

RUN python3.9 -m pip install beautifulsoup4
RUN python3.9 -m pip install nose
RUN python3.9 -m pip install pytest
RUN python3.9 -m pip install xmlschema
RUN python3.9 -m pip install numpy
RUN python3.9 -m pip install soupsieve
RUN python3.9 -m pip install elementpath
RUN python3.9 -m pip install coverage
RUN python3.9 -m pip install spiceypy

COPY naif-pds4-bundler root/naif-pds4-bundler/

WORKDIR /root

#
# Install NPB
#
RUN ls
WORKDIR /root/naif-pds4-bundler
RUN python3.9 -m pip install -e .

#
# Run NPB regression tests
#
WORKDIR /root/naif-pds4-bundler/tests/naif_pds4_bundler
RUN python3.9 -m unittest

#
# Back to the root
#
WORKDIR /root
