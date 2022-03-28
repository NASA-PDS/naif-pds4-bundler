***********************************
Functions and Modules Documentation
***********************************

Running tests with DOCKER

The DOCKER file is available from:

     naif-pds4-bundler/tests/naif_pds4_bundler/docker

     TAG_NAME='naif-pds4-bundler:latest'
     sudo docker build . -t $TAG_NAME

This already runs the tests. The tests can be run
manually with:

     docker run -it naif-pds4-bundler:latest



.. The API documentation is automatically generated with:
.. sphinx-apidoc -f -o source ../src/pds
.. sphinx-apidoc -f -o source ../tests

.. toctree::
   :maxdepth: 7

   pds.rst
   tests.rst
