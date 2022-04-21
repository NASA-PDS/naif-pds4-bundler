"""Unit tests for NPB SPICE kernel slicer."""
import os
import shutil
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.utils.zz_slicer import slice_kernels


class ZzTestSlicer(TestCase):
    """Unit Test Family Class for NPB SPICE kernel slicer.

    Slicer is an auxiliary function used to "slice" kernel data sets
    in order to make them adept to be included as data for NPB tests by
    reducing its size. This utility is not mentioned in the NPB documentation
    other than the function header itself.

    Since these tests require the NAIF Utility ``CKSLICER`` the tests are not
    included as part of the NPB test suite.
    """

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        shutil.move("kernels_sliced", ignore_errors=True)

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        shutil.rmtree("kernels_sliced", ignore_errors=True)

    def test_slicer_insight_release_08_cks(self):
        """Test InSight CK slicing."""
        kernels_dir = "../data/kernels"
        out_kernels_dir = "kernels_sliced"
        lsk_file = "../data/kernels/lsk/naif0012.tls"
        sclk_file = "../data/kernels/sclk/NSY_SCLKSCET.00019.tsc"
        start_time = "2020 NOV 07 02:00:00.000"
        stop_time = "2020 NOV 07 03:00:00.000"

        slice_kernels(
            kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time
        )

    def test_slicer_ladee(self):
        """Test LADEE kernel data set slicing."""
        kernels_dir = "../data/ladee/ladee_spice/spice_kernels"
        out_kernels_dir = "kernels_sliced"
        lsk_file = "../data/kernels/lsk/naif0012.tls"
        sclk_file = (
            "../data/ladee/ladee_spice/spice_kernels/sclk/"
            "ladee_clkcor_13250_14108_v01.tsc"
        )
        start_time = "2014 APR 04 00:00:00.000"
        stop_time = "2014 APR 04 12:00:00.000"

        slice_kernels(
            kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time
        )

    def test_slicer_kplo(self):
        """Test KPLO kernel data set slicing."""
        kernels_dir = "../data/kplo/kplo_spice/spice_kernels"
        out_kernels_dir = "kernels_sliced"
        lsk_file = "../data/kernels/lsk/naif0012.tls"
        sclk_file = (
            "../data/kplo/kplo_spice/spice_kernels/sclk/kplo_200926_000100.tsc"
        )
        start_time = "2023 JAN 18 00:00:00.000"
        stop_time = "2023 JAN 18 12:00:00.000"

        slice_kernels(
            kernels_dir, out_kernels_dir, lsk_file, sclk_file, start_time, stop_time
        )

if __name__ == "__main__":
    unittest.main()
