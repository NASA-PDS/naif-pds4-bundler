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
        shutil.rmtree('kernels', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        os.mkdir('working')
        os.mkdir('staging')
        os.mkdir('maven')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<file></file>' in line:
                        n.write('            <file>working/maven_2015_v09.tm</file>\n')
                        n.write('            <file>working/maven_2020_v10.tm</file>\n')
                    else:
                        n.write(line)

        with open('working/maven_2015_v09.tm', 'w') as p:
            p.write('test')
        with open('working/maven_2020_v10.tm', 'w') as p:
            p.write('test')

        with open('working/maven.plan', 'w') as p:
            p.write('mvn_sclkscet_00088.tsc')

        main(updated_config, plan, faucet, verbose=True, log=True, diff='all')

        shutil.rmtree('maven', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)


if __name__ == '__main__':

    unittest.main()