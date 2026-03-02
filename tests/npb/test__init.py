import sys
import importlib


def test_pds_namespace_import():
     importlib.import_module('pds')
     importlib.import_module('pds.naif_pds4_bundler')

     assert 'pds' in sys.modules
     assert 'pds.naif_pds4_bundler' in sys.modules


def test_version_string_loaded():
     import pds.naif_pds4_bundler

     version = pds.naif_pds4_bundler.__version__

     assert isinstance(version, str)
     assert len(version) > 0
