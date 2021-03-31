"""Functional tests for the List generator.
"""
import coverage
import os
import shutil

from unittest import TestCase
from npb.main import main

class TestConsole(TestCase):
    def test_basic(self):

        config = 'data/insight.json'
        plan   = 'data/insight_release_26.plan'

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
        shutil.copy2('data/insight_release_07.kernel_list',
                     'working/insight_release_07.kernel_list')
        os.mkdir('staging')
        os.mkdir('staging/insight')
        os.mkdir('staging/insight/insight_spice')

        shutil.copytree('data/insight', 'insight')
        with open('data/insight.list', 'r') as i:
            for line in i:
                with open(f'insight/insight_spice/{line[0:-1]}', 'w') as fp:
                    pass

        main(config,plan, silent=False, log=True)

        #cov.stop()
        #cov.save()
        #
        #cov.html_report()


