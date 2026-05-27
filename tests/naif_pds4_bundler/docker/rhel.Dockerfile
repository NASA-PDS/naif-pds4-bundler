# Red Hat Universal Base Image 9 — no subscription required
FROM registry.access.redhat.com/ubi9/ubi

#
# Install supporting libraries and Python 3.11 in a single layer.
# UBI repos provide Python 3.11 directly, so no need to compile from source.
#
RUN dnf -y update && \
    dnf install -y \
        gcc \
        libgfortran \
        git \
        openssl \
        openssl-devel \
        wget \
        zlib-devel \
        make \
        bzip2-devel \
        libffi-devel \
        python3.11 \
        python3.11-pip && \
    dnf clean all

#
# Install Python dependencies.
#
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install --ignore-installed "setuptools==80.10.2"

WORKDIR /root
RUN git clone https://github.com/NASA-PDS/naif-pds4-bundler.git

#
# Install NPB
#
WORKDIR /root/naif-pds4-bundler
RUN python3.11 -m pip install -e ".[dev]"

#
# Run NPB regression tests
#
RUN python3.11 -m unittest discover tests/naif_pds4_bundler
