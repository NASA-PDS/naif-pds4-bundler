import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestMAVEN(TestCase):

    @classmethod
    def setUpClass(cls):
        '''
        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        '''
        print(f"NPB - Functional Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'maven']
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

        dirs = ['working', 'staging']
        for dir in dirs:
            os.mkdir(dir)

        shutil.copytree('../data/kernels', 'kernels')
        shutil.copytree('../data/maven', 'maven')

    def tearDown(self):
        '''
        This method will be executed after each test function.
        '''
        unittest.TestCase.tearDown(self)

        dirs = ['working', 'staging', 'final', 'kernels', 'misc', 'maven']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        try:
            os.remove('maven_orbnum.plan')
        except:
            pass

    def test_maven_mks_input(self):
        '''
        In this case, the previous kernel list is present.    
        '''
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        shutil.copy2('../data/maven_release_24.kernel_list', 'working/')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file></file>' in line:
                        n.write('            '
                                '<file>working/maven_2015_v09.tm</file>\n')
                        n.write('            '
                                '<file>working/maven_2020_v06.tm</file>\n')
                    else:
                        n.write(line)

        with open('working/maven_2015_v09.tm', 'w') as p:
            p.write('test')
        with open('working/maven_2020_v06.tm', 'w') as p:
            p.write('test')

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc')

        main(updated_config, plan=plan, faucet=faucet, silent=self.silent,
             verbose=self.verbose, log=self.log, diff='all')

    def test_maven_mks_list(self):
        '''
        '''
        config = '../config/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc\n')
            p.write('maven_2015_v09.tm\n')
            p.write('maven_2020_v06.tm')

        main(config, plan=plan, faucet=faucet, silent=self.silent,
             verbose=self.verbose, log=self.log, diff='all')

    def test_maven_first_release(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc')

        main(config, plan=plan, faucet=faucet, silent=self.silent,
             verbose=self.verbose, log=self.log, diff='all')

    def test_maven_generate_mk(self):
        '''
        Testcase used to fix bug with the year information in the text of
        the meta-kernel.
        '''
        config = '../config/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc')
            p.write('maven_2021_v01.tm')

        main(config, plan=plan, faucet=faucet, silent=self.silent,
             verbose=self.verbose, log=self.log, diff='all')


if __name__ == '__main__':

    unittest.main()