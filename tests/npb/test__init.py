import sys
import importlib


def test_pds_namespace_import():
    importlib.import_module('pds')
    importlib.import_module('pds.naif_pds4_bundler')

    assert 'pds' in sys.modules
    assert 'pds.naif_pds4_bundler' in sys.modules