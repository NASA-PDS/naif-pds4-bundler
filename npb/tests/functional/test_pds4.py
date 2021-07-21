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
                'ladee', 'dart']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            
        cls.silent = True
        cls.log = False

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'final', 'misc', 'kplo', 'ladee',
                'dart']
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)
        
        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'kplo',
                'ladee', 'dart']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

            pass

    def test_ladee(self):
        '''
        Test to generate the LADEE archive.
        '''
        config = '../config/ladee.xml'

        shutil.copytree('../data/ladee/ladee_spice/spice_kernels','kernels',
                        ignore=shutil.ignore_patterns('*.xml','*.csv'))

        main(config, silent=self.silent, log=self.log)

    def test_kplo(self):
        '''
        Test to generate the KPLO archive (non-PDS archive).
        '''
        config = '../config/kplo.xml'

        shutil.copytree('../data/kplo/kplo_spice/spice_kernels','kernels',
                        ignore=shutil.ignore_patterns('*.xml','*.csv'))

        main(config, silent=self.silent, log=self.log)
        
    def test_dart(self):
        '''
        Test to generate the DART archive. This test includes multiple
        targets and spacecrafts.
        '''
        config = '../config/dart.xml'

        shutil.copytree('/Users/mcosta/workspace/dart/DART/kernels/','kernels',
                        ignore=shutil.ignore_patterns('*.xml','*.csv'))

        main(config, silent=False, verbose=True, log=True, diff='files')
        

if __name__ == '__main__':
    unittest.main()