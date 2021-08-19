import os
import spiceypy
import unittest
from unittest import TestCase
from npb.utils.time import dsk_coverage
from npb.utils.time import spk_coverage

class TestTime(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")
        
        lsk_file = '../data/kernels/lsk/naif0012.tls'
        spiceypy.furnsh(lsk_file)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)
        
        spiceypy.kclear()

    def test_dsk_coverage(self):
        
        dsk_file = '../data/kernels/dsk/DEIMOS_K005_THO_V01.BDS'

        [start_time_cal, stop_time_cal] = \
            dsk_coverage(dsk_file)
        
        self.assertEqual((start_time_cal, 
                          stop_time_cal), 
                         ('1950-01-01T00:00:00.001Z', 
                          '2049-12-31T23:59:58.999Z'))

    def test_spk_coverage(self):

        spk_file = '../data/kernels/spk/m2020_surf_rover_loc_0000_0089_v1.bsp'
        spiceypy.furnsh('../data/kernels/fk/m2020_v04.tf')
        [start_time_cal, stop_time_cal] = \
            spk_coverage(spk_file, main_name='M2020')

        self.assertEqual((start_time_cal,
                          stop_time_cal),
                         ('2021-02-18T21:52:40.482Z', 
                          '2021-05-21T15:47:07.765Z'))

if __name__ == '__main__':

    unittest.main()