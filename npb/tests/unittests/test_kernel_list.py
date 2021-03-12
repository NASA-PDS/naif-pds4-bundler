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

    def test_basic(self):
        """
        Basic test for MSL kernel list generation. Implemented following
        the generation of the MSK kernel list for release 26.

        """

        config = 'data/msl_list.json'
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



