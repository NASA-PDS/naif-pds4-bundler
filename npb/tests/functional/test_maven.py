"""
This test is used to check multiple meta-kernels as inputs.
"""
import os
import glob
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestMAVEN(TestCase):

    def test_maven_mks_input(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/maven.xml'
        updated_config = 'working/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        shutil.copytree('../data/maven', 'maven')
        os.mkdir('working')
        os.mkdir('staging')

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

        main(updated_config, plan, faucet, verbose=True, log=True, diff='all')

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_maven_mks_list(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('maven')
        os.mkdir('working')
        os.mkdir('staging')

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc\n')
            p.write('maven_2015_v09.tm\n')
            p.write('maven_2020_v06.tm')

        main(config, plan, faucet, verbose=True, log=True, diff='all')

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


    def test_maven_first_release(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/maven.xml'
        plan = 'working/maven.plan'
        faucet = 'staging'

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels_ladee')
        os.mkdir('maven')
        os.mkdir('working')
        os.mkdir('staging')

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc')

        main(config, plan, faucet, verbose=True, log=True, diff='all')

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)


if __name__ == '__main__':

    unittest.main()