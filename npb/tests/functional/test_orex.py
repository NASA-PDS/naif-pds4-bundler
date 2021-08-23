import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestOSIRISREx(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'orex']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            
        cls.verbose = False    
        cls.silent = True
        cls.log = True

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'orex']
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree('../data/kernels', 'kernels')
        #shutil.copytree('../data/maven', 'maven')

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'orex']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)


    def test_orex_mks(self):
        '''
        Test case to debug:
        INFO    : Step 6 - Generation of meta-kernel(s)
        INFO    : -------------------------------------
        INFO    :
        INFO    : -- Copy meta-kernel: bundle/spice_kernels/mk/orx_2016_v09.tm
        ERROR   : -- Missmatch of values in meta-kernel pattern.
        WARNING : -- orx_2016_v09.tm No vid explicit in kernel name: set to 1.0
        '''
        config = '../config/orex.xml'
        plan = 'working/orex.plan'
        faucet = 'staging'

        main(config, faucet=faucet, silent=self.silent,
             verbose=self.verbose, log=self.log)

if __name__ == '__main__':

    unittest.main()