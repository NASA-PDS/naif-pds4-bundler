"""Functional tests for the List generator.
"""
import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main


class TestPlan(TestCase):
    """
    Test family for the plan generation.
    The data sources are contained in the::

        data/

    directory.

    """

    def test_pds4_insight_plan(self):
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

        """

        config = '../config/insight.xml'
        plan   = ''
        faucet = 'list'


        #
        # Test preparation
        #
        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        os.mkdir('kernels/fk')
        os.mkdir('kernels/sclk')
        os.mkdir('kernels/ck')
        os.mkdir('kernels/lsk')

        shutil.copy2('../data/kernels/fk/insight_v05.tf', 'kernels/fk')
        shutil.copy2('../data/kernels/lsk/naif0012.tls', 'kernels/lsk')
        shutil.copy2('../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc','kernels/ck')
        shutil.copy2('../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc','kernels/ck')

        shutil.copy2('../data/insight_release_empty.kernel_list', 'working/insight_release_07.kernel_list')

        main(config, plan, faucet, silent=True)

        new_file = ''
        with open('working/insight_release_08.plan', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('../data/insight_release_test.plan', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()