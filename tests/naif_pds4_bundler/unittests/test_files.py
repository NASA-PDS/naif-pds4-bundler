"""Unit tests for the files utilities."""
import unittest

import spiceypy
from pds.naif_pds4_bundler.utils import check_line_length
from pds.naif_pds4_bundler.utils import mk_to_list


def test_mk_to_list(self):
    """Test MK to Python list function."""
    mk = "../data/kernels/mk/vco_v01.tm"

    ker_mk_list = mk_to_list(mk, False)
    self.assertTrue(ker_mk_list)

    mk = "../data/kernels/mk/msl_v29.tm"

    ker_mk_list = mk_to_list(mk, False)
    self.assertTrue(ker_mk_list)


def test_check_line_length(self):
    """Test line length check."""

    mk = "../data/kernels/mk/bc_v001.tm"
    expected = [
        "Line 97 is longer than 80 characters",
        "Line 100 is longer than 80 characters",
        "Line 103 is longer than 80 characters",
        "Line 104 is longer than 80 characters",
        "Line 105 is longer than 80 characters",
        "Line 106 is longer than 80 characters",
        "Line 107 is longer than 80 characters",
        "Line 108 is longer than 80 characters",
        "Line 109 is longer than 80 characters",
        "Line 110 is longer than 80 characters",
        "Line 111 is longer than 80 characters",
        "Line 112 is longer than 80 characters",
        "Line 113 is longer than 80 characters",
        "Line 114 is longer than 80 characters",
        "Line 115 is longer than 80 characters",
        "Line 116 is longer than 80 characters",
        "Line 117 is longer than 80 characters",
        "Line 118 is longer than 80 characters",
        "Line 121 is longer than 80 characters",
        "Line 123 is longer than 80 characters",
        "Line 124 is longer than 80 characters",
        "Line 125 is longer than 80 characters",
        "Line 126 is longer than 80 characters",
        "Line 127 is longer than 80 characters",
    ]
    errors = check_line_length(mk)
    self.assertEqual(errors, expected)
