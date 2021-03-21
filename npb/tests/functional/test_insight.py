"""Functional tests for the List generator.
"""

from unittest import TestCase
from npb.main import main

class TestConsole(TestCase):
    def test_basic(self):

        config = 'data/insight.json'
        plan   = 'data/insight_release_26.plan'

        main(config,plan,silent=True)


