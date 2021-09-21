import os
import shutil
import unittest
from unittest import TestCase
from naif_pds4_bundle.__main__ import main  
    

class TestDART(TestCase):
    '''
    Test Family for DART archive generation. 
    '''

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.
         
        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ['working', 'staging', 'dart', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            
        cls.silent = True
        cls.log = True

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")
        
        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'dart', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists('staging'):
            os.remove('staging')

    def test_dart_multiple_obs_tar(self):
        '''
        Test complete pipeline with basic Insight data to test the generation
        of labels with multiple observers and targets.

        '''
        config = '../config/dart.xml'

        os.makedirs('working', mode=0o777, exist_ok=True)
        os.makedirs('staging', mode=0o777, exist_ok=True)
        os.makedirs('dart', mode=0o777, exist_ok=True)
        shutil.rmtree('kernels', ignore_errors=True)
        shutil.copytree('../data/kernels', 'kernels')
        

        main(config, plan=False, faucet='final', silent=self.silent, log=self.log)
        
            
if __name__ == '__main__':
    unittest.main()
