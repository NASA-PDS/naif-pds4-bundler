"""Functional tests for the List generator.
"""
import os

from unittest import TestCase
from npb.main import main


class TestKernelList(TestCase):
    """
    Test family for the kernel list generation.
    The data sources are contained in the::

        data/

    directory.

    """

    def test_pds3_list(self):
        """
        Basic test for MSL kernel list generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 26.

        """

        config = 'data/msl_release_26.json'
        plan   = 'data/msl_release_26.plan'


        main(config,plan)

        new_file = ''
        with open('msl_release_26.kernel_list', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/msl_release_26.kernel_list', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        os.remove('msl_release_26.kernel_list')


    def test_pds4_list(self):
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

        """

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'


        main(config,plan)

        new_file = ''
        with open('insight_release_08.kernel_list', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/insight_release_08.kernel_list', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        os.remove('insight_release_08.kernel_list')

