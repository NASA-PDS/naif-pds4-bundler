"""Unit tests for the Bundle history generation."""
from pds.naif_pds4_bundler.classes.bundle import Bundle
from pds.naif_pds4_bundler.classes.object import Object


def test_insight_history(self):
    """Test the generation of the bundle history."""
    test_setup = Object()
    test_setup.bundle_directory = "../data/insight"
    test_setup.mission_acronym = "insight"
    test_setup.xml_model = "http://pds.nasa.gov/pds4/pds/v1/test"

    test_bundle = Object()
    test_bundle.vid = "8.0"
    test_bundle.name = "bundle_insight_spice_v008.xml"
    test_bundle.setup = test_setup
    test_bundle.collections = None

    Bundle.get_history(test_bundle, test_bundle, debug=True)
