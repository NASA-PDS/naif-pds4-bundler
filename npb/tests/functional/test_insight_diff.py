"""
This test is used to compare labels with the test labels.
"""
import coverage
import os
import glob
import shutil
import unittest

from unittest import TestCase
from npb.main import main

class TestConsole(TestCase):
    def test_insight_diff(self):

        config = 'data/insight_release_08.json'
        plan   = 'data/insight_release_08.plan'

        #
        # Debugging does not work while using coverage.
        # See: https://github.com/microsoft/vscode-python/issues/693
        #
        #cov = coverage.Coverage()
        #cov.start()

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)

        os.mkdir('working')
        for file in glob.glob('data/insight_release_[0-9][0-9].kernel_list'):
            shutil.copy2(file,
                        'working')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')
        os.mkdir('insight')

        main(config, plan, silent=False, log=True)

        shutil.rmtree('insight', ignore_errors=True)
        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('staging', ignore_errors=True)
        #cov.stop()
        #cov.save()
        #
        #cov.html_report()


if __name__ == '__main__':
    unittest.main()