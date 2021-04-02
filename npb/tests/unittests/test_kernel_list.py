"""Functional tests for the List generator.
"""
import os
import shutil
import unittest

from unittest import TestCase
from npb.main import main


class TestKernelList(TestCase):
    """
    Test family for the kernel list generation.
    The data sources are contained in the::

        data/

    directory.

    """

    def test_pds3_msl_list(self):
        """
        Basic test for MSL kernel list generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 26.

        """

        config = 'data/msl_release_26.json'
        plan   = 'data/msl_release_26.plan'

        shutil.rmtree('working', ignore_errors=True)
        os.mkdir('working')
        shutil.copy2('data/msl_release_25.kernel_list', 'working')

        main(config=config, plan=plan, silent=True)

        new_file = ''
        with open('working/msl_release_26.kernel_list', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/msl_release_26.kernel_list', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        shutil.rmtree('working', ignore_errors=True)


    def test_pds3_m01_list(self):
        """
        Basic test for M01 kernel list generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 75.

        """

        config = 'data/m01_release_75.json'
        plan   = 'data/m01_release_75.plan'

        shutil.rmtree('working', ignore_errors=True)
        os.mkdir('working')
        shutil.copy2('data/m01_release_74.kernel_list', 'working')

        main(config=config, plan=plan, silent=True)

        new_file = ''
        with open('working/m01_release_75.kernel_list', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/m01_release_75.kernel_list', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        shutil.rmtree('working', ignore_errors=True)



    def test_pds4_insight_list(self):
        """
        Basic test for InSight kernel list generation. This is a PDS4 Bundle.
        Implemented following the generation of the kernel list for release 8.

        """

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'

        shutil.rmtree('working', ignore_errors=True)
        os.mkdir('working')
        shutil.copy2('data/insight_release_07.kernel_list', 'working')

        main(config=config, plan=plan, silent=True)

        new_file = ''
        with open('working/insight_release_08.kernel_list', 'r') as f:
            for line in f:
                new_file += line

        old_file = ''
        with open('data/insight_release_08.kernel_list', 'r') as f:
            for line in f:
                old_file += line

        self.assertEqual(old_file.split('\n')[9:],new_file.split('\n')[9:])

        shutil.rmtree('working', ignore_errors=True)


if __name__ == '__main__':
    unittest.main()