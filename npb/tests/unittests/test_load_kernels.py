"""Functional tests for the List generator.
"""
import os
import shutil
import unittest
from unittest import TestCase
from npb.main import main

class TestLoadKernels(TestCase):
    """
    Test family to test loading the kernels required to execute the pipeline.
    Test implemented after incorrect SCLK was loaded for MAVEN.
    """
    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'kernels', 'misc', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.faucet = 'staging'
        cls.silent = True

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'maven']
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/misc', 'misc')
        
    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'kernels', 'misc', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)


    def test_load_kernels(self):
        """
        
        """

        config = '../config/maven.xml'
        plan = 'working/maven_orbnum.plan'

        with open(plan, 'w') as p:
            p.write('maven_orb_rec_210101_210401_v1.orb')
            p.write('\nmaven_orb_rec_210101_210401_v1.nrb')
        
        shutil.copy2('kernels/sclk/MVN_SCLKSCET.00088.tsc',
                     'kernels/sclk/MVN_SCLKSCET.00100.tsc.bad')
        shutil.copy2('kernels/sclk/MVN_SCLKSCET.00088.tsc',
                     'kernels/sclk/MVN_SCLKSCET.00000.tsc')
        os.mkdir('kernels/sclk/zzarchive')
        shutil.copy2('kernels/sclk/MVN_SCLKSCET.00088.tsc',
                     'kernels/sclk/zzarchive/MVN_SCLKSCET.00000.tsc')

        main(config, plan, self.faucet, silent=self.silent, log=True)

        log_line = "setup        load_kernels            || INFO    : " \
                   "-- SCLK(s) loaded: ['/Users/mcosta/workspace/pds/" \
                   "naif-pds4-bundle/npb/tests/unittests/kernels/sclk/" \
                   "MVN_SCLKSCET.00088.tsc']\n"
        with open("working/maven_release_01.log", "r") as f:
            found = log_line in f.readlines()
        
        self.assertTrue(found) 
            
if __name__ == '__main__':
    unittest.main()