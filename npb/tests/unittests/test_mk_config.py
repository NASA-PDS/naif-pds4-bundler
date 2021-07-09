"""Functional tests for the List generator.
"""
import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main


class TestMetaKernelConfiguration(TestCase):
    """
    Test Family for meta-kernel configuration.
    """

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'insight', 'kernels', 'orx']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True
        cls.faucet = 'list'

    def setUp(self):
        '''
        This method will be executed before each test function.
        '''
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ['working', 'staging', 'orx','insight']
        for directory in dirs:
            os.mkdir(directory)

        shutil.copytree('../data/kernels/', 'kernels')

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'insight', 'kernels', 'orx']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
        
    def test_insight_mk_error_extra_pattern(self):
        """
        Test for meta-kernel configuration loading error cases.

        """
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        '
                                '<mk name="insight_$YEAR_v$VERSION.tm">\n')
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, self.faucet, silent=self.silent)

    def test_insight_mk_error_wrong_name(self):

        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        <mk name="insight.tm">\n')
                    else:
                        n.write(line)
                        
        with self.assertRaises(RuntimeError):
            main(updated_config, plan, self.faucet, silent=self.silent)

    def test_insight_mk_double_pattern(self):

        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan = '../data/insight_release_08.plan'

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        '
                                '<mk name="insight_$YEAR_v$VERSION.tm">\n')
                    elif '<pattern length="2">VERSION</pattern>' in line:
                        n.write('                '
                                '<pattern length="2">VERSION</pattern>\n')
                        n.write('                '
                                '<pattern length="4">YEAR</pattern>\n')
                    else:
                        n.write(line)

        main(updated_config, plan, self.faucet, silent=self.silent)

    def test_orx_mk_multiple_mks(self):
        """
        Test for meta-kernel configuration with multiple meta-kernels
        to generate.

        """
        config = '../config/orx.xml'
        plan   = '../data/orx_release_10.plan'

        main(config, plan, self.faucet, silent=self.silent)
        

if __name__ == '__main__':
    unittest.main()