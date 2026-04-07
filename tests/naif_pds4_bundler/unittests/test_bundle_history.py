"""Unit tests for the Bundle history generation."""
from unittest.mock import MagicMock

from pds.naif_pds4_bundler.classes.bundle import Bundle


def test_insight_history(self):
    """Test the generation of the bundle history."""
    setup = MagicMock(bundle_directory="../data/insight",
                      mission_acronym="insight",
                      xml_model="https://pds.nasa.gov/pds4/pds/v1/test")
    bundle = MagicMock(vid="8.0",
                       name="bundle_insight_spice_v008.xml",
                       setup=setup,
                       collections = None)
    Bundle._get_history(bundle, bundle)
