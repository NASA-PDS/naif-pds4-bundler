"""
This test is used to compare labels with the test labels.
"""
import os
import glob
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestLadee(TestCase):

    def test_ladee(self):
        '''
        Testcase for when the readme file is not present.
        '''
        config = '../config/ladee.xml'

        shutil.rmtree('ladee', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels_ladee', ignore_errors=True)

        shutil.copytree(
            '/Users/mcosta/workspace/pds/npb_workspace/ops/LADEE/kernels',
            'kernels')
        os.mkdir('working')
        os.mkdir('staging')
        os.mkdir('ladee')

        main(config, silent=False, verbose=True, log=True, diff='files')

#        shutil.rmtree('insight', ignore_errors=True)
#        shutil.rmtree('working', ignore_errors=True)
#        shutil.rmtree('staging', ignore_errors=True)
#        shutil.rmtree('kernels', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()