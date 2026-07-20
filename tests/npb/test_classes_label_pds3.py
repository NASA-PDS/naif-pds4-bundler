"""
Tests for PDS3Label class.

PDS3Label currently adds no __init__ logic of its own — PDS3-specific
field assignment still lives in each PDS3 leaf class. Its only real
behavior is the _label_extension/_eol pair consumed by PDSLabel.write_label,
and by construction it must not pick up any PDS4-only attribute.
"""

from unittest.mock import MagicMock

from pds.naif_pds4_bundler.classes.label.pds3_label import PDS3Label


def _make_setup_pds3(**kwargs):
    setup = MagicMock()
    setup.pds_version = "3"
    setup.root_dir = "/root"
    setup.mission_acronym = "test"
    setup.eol_pds3 = "\r\n"
    del setup.creation_date_time

    for k, v in kwargs.items():
        setattr(setup, k, v)
    return setup


def _make_product():
    product = MagicMock()
    product.creation_time = "2024-01-01T00:00:00"
    product.creation_date = "2024-01-01"
    product.size = 1024
    product.checksum = "abc123"
    product.missions = ["TestMission"]
    product.observers = ["TestObserver"]
    product.targets = ["TestTarget"]
    return product


class TestPDS3LabelInit:
    """Covers PDS3Label.__init__ – inherited, version-agnostic behavior."""

    def test_construction_succeeds(self):
        setup = _make_setup_pds3()
        product = _make_product()
        label = PDS3Label(setup, product)
        assert label.setup is setup
        assert label.product is product

    def test_no_pds4_attrs_present(self):
        """PDS3Label must never pick up PDS4-only attributes."""
        setup = _make_setup_pds3()
        product = _make_product()
        label = PDS3Label(setup, product)
        assert not hasattr(label, "XML_MODEL")
        assert not hasattr(label, "SCHEMA_LOCATION")
        assert not hasattr(label, "PDS4_MISSION_NAME")
        assert not hasattr(label, "MISSIONS")


class TestPDS3LabelExtensionAndEol:
    """Covers the _label_extension/_eol properties consumed by write_label."""

    def test_label_extension_is_lbl(self):
        setup = _make_setup_pds3()
        product = _make_product()
        label = PDS3Label(setup, product)
        assert label._label_extension == ".lbl"

    def test_eol_reads_setup_eol_pds3(self):
        setup = _make_setup_pds3(eol_pds3="\n")
        product = _make_product()
        label = PDS3Label(setup, product)
        assert label._eol == "\n"
