"""Unit tests for pattern matching."""
from pds.naif_pds4_bundler.utils import match_patterns


def test_match_patterns_basic(self):
    """Test match_patterns utils function."""
    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    values = match_patterns(name, name_w_pattern, patterns)

    assert values == {"YEAR": "2021", "VERSION": "02"}

    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [{"@length": "2", "#text": "VERSION"}]

    with self.assertRaises(RuntimeError):
        () = match_patterns(name, name_w_pattern, patterns)

    name_w_pattern = "insight_$YER_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YEAR"},
    ]

    with self.assertRaises(RuntimeError):
        () = match_patterns(name, name_w_pattern, patterns)

    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "4", "#text": "YAR"},
    ]

    with self.assertRaises(RuntimeError):
        () = match_patterns(name, name_w_pattern, patterns)

    name_w_pattern = "insight_$YEAR_v$VERSION.tm"
    name = "insight_2021_v02.tm"
    patterns = [
        {"@length": "2", "#text": "VERSION"},
        {"@length": "10", "#text": "YEAR"},
    ]

    with self.assertRaises(RuntimeError):
        () = match_patterns(name, name_w_pattern, patterns)
