import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestPDS3(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'final', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'final', 'kernels']
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'final', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def test_pds3_m01(self):
        """
        Basic test for M01 kernel list generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 75.
        """
        config = '../config/m01.xml'
        plan   = '../data/m01_release_75.plan'
        faucet = 'staging'

        shutil.copy2('../data/m01_release_74.kernel_list', 'working')

        main(config, plan, faucet, silent=True, diff='log')


if __name__ == '__main__':
    unittest.main()