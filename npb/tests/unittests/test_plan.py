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

        config = 'data/insight_release_08.json'
        plan   = ''
        faucet = 'list'

        shutil.rmtree('working', ignore_errors=True)
        os.mkdir('working')
        shutil.copy2('data/insight_release_07.kernel_list', 'working')

        main(config, plan, faucet, silent=True)

        new_file = ''
        with open('working/insight_release_08.plan', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/insight_release_test.plan', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        shutil.rmtree('working', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()