"""Functional tests for the List generator.
"""
import coverage

from unittest import TestCase
from npb.main import main

class TestConsole(TestCase):
    def test_basic(self):

        config = 'data/msl.json'
        plan   = 'data/msl_release_26.plan'

        cov = coverage.Coverage()
        cov.start()

        main(config,plan)

        cov.stop()
        cov.save()

        cov.html_report()

