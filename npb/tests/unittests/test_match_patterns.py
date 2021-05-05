import os
import shutil
import unittest

from unittest import TestCase

from npb.utils.files import match_patterns

class TestMatchPatterns(TestCase):

    def test_match_patterns_basic(self):

        #
        # Basic test of XML parsing.
        #
        name_w_pattern = 'insight_$YEAR_v$VERSION.tm'
        name           = 'insight_2021_v02.tm'
        patterns       = [{'@lenght':'2','#text':'VERSION'},
                          {'@lenght':'4','#text':'YEAR'}]

        values = match_patterns(name, name_w_pattern, patterns)

        assert values == {'YEAR': '2021', 'VERSION': '02'}
        #
        # Testing of the initialisation of the Setup class
        #

        name_w_pattern = 'insight_$YEAR_v$VERSION.tm'
        name           = 'insight_2021_v02.tm'
        patterns       = [{'@lenght':'2','#text':'VERSION'}]

        with self.assertRaises(RuntimeError):
            values = match_patterns(name, name_w_pattern, patterns)


        name_w_pattern = 'insight_$YER_v$VERSION.tm'
        name           = 'insight_2021_v02.tm'
        patterns       = [{'@lenght':'2','#text':'VERSION'},
                          {'@lenght':'4','#text':'YEAR'}]

        with self.assertRaises(RuntimeError):
            values = match_patterns(name, name_w_pattern, patterns)


        name_w_pattern = 'insight_$YEAR_v$VERSION.tm'
        name           = 'insight_2021_v02.tm'
        patterns       = [{'@lenght':'2','#text':'VERSION'},
                          {'@lenght':'4','#text':'YAR'}]

        with self.assertRaises(RuntimeError):
            values = match_patterns(name, name_w_pattern, patterns)

        name_w_pattern = 'insight_$YEAR_v$VERSION.tm'
        name           = 'insight_2021_v02.tm'
        patterns       = [{'@lenght':'2','#text':'VERSION'},
                          {'@lenght':'10','#text':'YEAR'}]

        with self.assertRaises(RuntimeError):
            values = match_patterns(name, name_w_pattern, patterns)

        print(values)
