import os
import glob
import shutil
import unittest
from unittest import TestCase
from npb.main import main


class TestRegressionINSIGHT(TestCase):
    '''
    Test Family for INSIGHT archive generation. 
    '''

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.
         
        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            
        cls.silent = False
        cls.log = True

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")
        
        os.chdir(os.path.dirname(__file__))
        
        dirs = ['working', 'staging']
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/insight', 'insight')

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists('staging'):
            os.remove('staging')

    def test_insight_regression(self):
        '''
        Test complete pipeline with basic Insight data (no binary kernels,
        no SCLK).

        '''
        config = '../config/insight.xml'
        plan = '../data/insight_release_08.plan'
        faucet = 'final'

        main(config, plan, faucet, silent=self.silent, log=self.log, diff='all')
        print('test')
            
if __name__ == '__main__':
    unittest.main()
