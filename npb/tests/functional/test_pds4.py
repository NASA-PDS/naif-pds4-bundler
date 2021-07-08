import os
import shutil
import unittest
from unittest import TestCase
from npb.main import main

class TestPDS4(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'kplo', 
                'ladee']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'final', 'misc', 'kplo', 'ladee']
        for dir in dirs:
            os.mkdir(dir)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)
        
        return
        
        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'kplo',
                'ladee']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

            pass

    def test_ladee(self):
        '''
        Test to generate the LADEE archive.
        '''
        config = '../config/ladee.xml'

        shutil.copytree(
            '/Users/mcosta/workspace/pds/npb_workspace/ops/LADEE/kernels',
            'kernels')

        main(config, silent=False, verbose=False, log=True, diff='files')

    def test_kplo(self):
        '''
        Test to generate the KPLO archive (non-PDS archive).
        '''
        config = '../config/kplo.xml'

        shutil.copytree(
            '/Users/mcosta/workspace/pds/npb_workspace/kplo_area/kernels',
            'kernels')

        main(config, silent=False, verbose=False, log=True, diff='files')


if __name__ == '__main__':
    unittest.main()