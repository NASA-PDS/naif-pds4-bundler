"""Functional tests for the List generator.
"""
import os
import shutil

from unittest import TestCase
from npb.main import main

class TestConsole(TestCase):
    def test_msl_list(self):

        config = 'data/msl.json'
        plan   = 'data/msl_release_26.plan'
        faucet = 'list'

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('final', ignore_errors=True)

        os.mkdir('working')
        os.mkdir('final')

        main(config, plan, faucet)

        shutil.rmtree('working', ignore_errors=True)
        shutil.rmtree('final', ignore_errors=True)

