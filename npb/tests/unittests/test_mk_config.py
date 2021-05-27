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

    def test_pds4_insight_mk(self):
        """
        Test for meta-kernel configuration loading error cases.

        """
        config = '../config/insight.xml'
        updated_config = 'working/insight.xml'
        plan   = '../data/insight_release_08.plan'
        faucet = 'list'

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')
        os.mkdir('working')

        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        '
                                '<mk name="insight_$YEAR_v$VERSION.tm">\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=True)


        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        <mk name="insight.tm">\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=True)


        with open(config, 'r') as c:
            with open(updated_config, 'w') as n:
                for line in c:
                    if '<mk name="insight_v$VERSION.tm">' in line:
                        n.write('        '
                                '<mk name="insight_$YEAR_v$VERSION.tm">\n')
                    elif '<pattern lenght="2">VERSION</pattern>' in line:
                        n.write('                '
                                '<pattern lenght="2">VERSION</pattern>\n')
                        n.write('                '
                                '<pattern lenght="4">YEAR</pattern>\n')
                    else:
                        n.write(line)

        #
        # Test preparation
        #
        dirs = ['staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(updated_config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'insight', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)


    def test_pds4_orex_mk(self):
        """
        Test for meta-kernel configuration with multiple meta-kernels
        to generate.

        """
        config = '../config/orx.xml'
        plan   = '../data/orx_release_10.plan'
        faucet = 'list'

        shutil.rmtree('orx', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        shutil.rmtree('kernels', ignore_errors=True)

        shutil.copytree('../data/kernels', 'kernels')

        #
        # Test preparation
        #
        dirs = ['staging', 'orx', 'kernels', 'working']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)
            os.mkdir(dir)

        main(config, plan, faucet, silent=True)

        #
        # Cleanup test facility
        #
        dirs = ['working', 'staging', 'orx', 'kernels']
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()