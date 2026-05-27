# Pinned to a specific version for reproducibility and security
FROM ubuntu:22.04

#
# Disable prompt during package installation
#
ENV DEBIAN_FRONTEND=noninteractive

#
# Install Python and dependencies in a single layer to minimise image size.
# Clean up apt cache afterwards to keep the image lean.
#
RUN apt-get update && apt-get install -y \
        git                              \
        python3                          \
        python3-pip &&                   \
    apt-get clean &&                     \
    rm -rf /var/lib/apt/lists/*

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
RUN python3 -m pip install --upgrade pip &&                            \
    python3 -m pip install --ignore-installed "setuptools==80.10.2" && \
    python3 -m pip install -e ".[dev]"                              && \
    python3 -m unittest discover tests/naif_pds4_bundler

