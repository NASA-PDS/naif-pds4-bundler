"""Functional tests for the index generator.
"""
import os
import shutil
import filecmp
import unittest
import subprocess


from unittest import TestCase
from npb.main import main


class TestIndex(TestCase):
    """
    Test family for the kernel list generation.
    The data sources are contained in the::

        data/

    directory.
    """

    def test_pds3_msl_index(self):
        """
        Basic test for MSL index generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 26.

        """

        list   = '../data/msl_release_index.kernel_list'
        command = f'perl ../../exe/xfer_index.pl {list}'
        print(f'-- Executing: {command}')

        command_process = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

        process_output, _ = command_process.communicate()
        text = process_output.decode('utf-8')

        print(text)

        if 'ERROR' in text:
            raise Exception()

        equal = filecmp.cmp('index.tab',   '../data/msl_index.tab'  )
        if not equal: raise Exception(
            'index.tab and data/msl_index.tab not equal')
        equal = filecmp.cmp('dsindex.tab', '../data/msl_dsindex.tab')
        if not equal: raise Exception(
            'dsindex.tab and data/msl_dsindex.tab not equal')
        equal = filecmp.cmp('index.lbl',   '../data/msl_index.lbl'  )
        if not equal: raise Exception(
            'index.lbl and data/msl_index.lbl not equal')
        equal = filecmp.cmp('dsindex.lbl', '../data/msl_dsindex.lbl')
        if not equal: raise Exception(
            'dsindex.lbl and data/msl_dsindex.lbl not equal')

        os.remove('index.tab')
        os.remove('index.lbl')
        os.remove('dsindex.tab')
        os.remove('dsindex.lbl')


    def test_pds4_insight_index(self):
        """
        Basic test for InSight index generation. This is a PDS3 data set.
        Implemented following the generation of the kernel list for
        release 26.

        """

        list   = '../data/insight_release_index.kernel_list'
        command = f'perl ../../exe/xfer_index.pl {list}'
        print(f'-- Executing: {command}')

        command_process = subprocess.Popen(command, shell=True,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT)

        process_output, _ = command_process.communicate()
        text = process_output.decode('utf-8')

        print(text)

        if 'ERROR' in text:
            raise Exception()

        equal = filecmp.cmp('index.tab',   '../data/insight_index.tab'  )
        if not equal: raise Exception(
            'index.tab and data/insight_index.tab not equal')
        equal = filecmp.cmp('dsindex.tab', '../data/insight_dsindex.tab')
        if not equal: raise Exception(
            'dsindex.tab and data/insight_dsindex.tab not equal')
        equal = filecmp.cmp('index.lbl',   '../data/insight_index.lbl'  )
        if not equal: raise Exception(
            'index.lbl and data/insight_index.lbl not equal')
        equal = filecmp.cmp('dsindex.lbl', '../data/insight_dsindex.lbl')
        if not equal: raise Exception(
            'dsindex.lbl and data/insight_dsindex.lbl not equal')

        os.remove('index.tab')
        os.remove('index.lbl')
        os.remove('dsindex.tab')
        os.remove('dsindex.lbl')


if __name__ == '__main__':
    unittest.main()