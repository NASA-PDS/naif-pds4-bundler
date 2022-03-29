"""Unit tests for the files utilities."""
import unittest

import spiceypy
from pds.naif_pds4_bundler.utils import mk_to_list


def test_mk_to_list(self):
    """Test MK to Python list function."""
    mk = "../data/kernels/mk/vco_v01.tm"

    ker_mk_list = mk_to_list(mk, False)
    self.assertTrue(ker_mk_list)

    mk = "../data/kernels/mk/msl_v29.tm"

    ker_mk_list = mk_to_list(mk, False)
    self.assertTrue(ker_mk_list)
