# Red Hat Universal Base Image 9 — no subscription required
FROM registry.access.redhat.com/ubi9/ubi:latest

#
# Install supporting libraries and Python in a single layer.
# UBI repos provide Python 3.11 directly, so no need to compile from source.
#
RUN dnf -y update &&       \
    dnf install -y         \
        gcc                \
        libgfortran        \
        git                \
        openssl            \
        openssl-devel      \
        wget               \
        zlib-devel         \
        make               \
        bzip2-devel        \
        libffi-devel       \
        python3.11         \
        python3.11-pip &&  \
    dnf clean all

#
# Create a non-root user and switch to that user.
#
RUN useradd -ms /bin/bash npbuser

USER npbuser
WORKDIR /home/npbuser

#
# Clone NPB
#
RUN git clone https://github.com/NASA-PDS/naif-pds4-bundler.git

#
# Install Python dependencies, NPB, and run NPB regression tests
#
WORKDIR /home/npbuser/naif-pds4-bundler
RUN python3.11 -m pip install --upgrade pip &&                            \
    python3.11 -m pip install --ignore-installed "setuptools==80.10.2" && \
    python3.11 -m pip install -e ".[dev]"                              && \
    python3.11 -m unittest discover tests/naif_pds4_bundler
