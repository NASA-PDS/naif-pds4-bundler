"""Tests for the PDS3Product class."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.product.product_pds3 import PDS3Product


class TestPDS3ProductArchiveRootDir:

    @pytest.mark.parametrize('volume_id', ['MAVEN_1001', 'VOL_2002'])
    def test_archive_root_dir_is_the_setup_volume_id(self, volume_id) -> None:
        """The archive root directory of a PDS3 product is the volume id."""
        # Skip __init__ so the constructor does not need a real file.
        product = PDS3Product.__new__(PDS3Product)
        product.setup = SimpleNamespace(volume_id=volume_id)

        # The volume id comes straight from the setup, whatever its value.
        assert product._archive_root_dir == volume_id

    @pytest.mark.parametrize('volume_id', ['MAVEN_1001', 'VOL_2002'])
    def test_archive_path_is_relative_to_volume_id(
            self, tmp_path, volume_id) -> None:
        """archive_path uses the volume id as the archive directory."""
        # A path inside a directory named after the volume id, with a
        # pds_version that would send Product's own fallback to PDS4.
        setup = SimpleNamespace(volume_id=volume_id, pds_version='4',
                                mission_acronym='maven')

        # Skip __init__; only _registered_path and setup matter here.
        product = PDS3Product.__new__(PDS3Product)
        product._registered_path = str(
            tmp_path / 'bundle' / volume_id / 'data' / 'k.bsp')
        product.setup = setup

        # The path starts below the volume directory. With the PDS4 fallback
        # the lookup of 'maven_spice' would have failed instead.
        assert product.archive_path == Path('data', 'k.bsp')
