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

        config = 'data/msl_list.json'
        plan   = 'data/msl_release_26.plan'

        main(config,plan)

        os.remove('msl_release_26.kernel_list')



