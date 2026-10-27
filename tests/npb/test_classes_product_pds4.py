"""Tests for the PDS4Product class."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.product.product_pds4 import PDS4Product


class TestPDS4ProductArchiveRootDir:

    @pytest.mark.parametrize('mission_acronym', ['maven', 'bepicolombo'])
    def test_archive_root_dir_is_the_mission_spice_directory(
            self, mission_acronym) -> None:
        """The archive root directory of a PDS4 product is '<mission>_spice'."""
        # Skip __init__ so the constructor does not need a real file.
        product = PDS4Product.__new__(PDS4Product)
        product.setup = SimpleNamespace(mission_acronym=mission_acronym)

        # The name is built from the mission acronym in the setup.
        assert product._archive_root_dir == f'{mission_acronym}_spice'

    @pytest.mark.parametrize('mission_acronym', ['maven', 'bepicolombo'])
    def test_archive_path_is_relative_to_mission_spice_directory(
            self, tmp_path, mission_acronym) -> None:
        """archive_path uses '<mission>_spice' as the archive directory."""
        # A path inside the mission's spice directory, with a pds_version
        # that would send Product's own fallback to PDS3.
        spice_dir = f'{mission_acronym}_spice'
        setup = SimpleNamespace(mission_acronym=mission_acronym,
                                pds_version='3', volume_id='MAVEN_1001')

        # Skip __init__; only _registered_path and setup matter here.
        product = PDS4Product.__new__(PDS4Product)
        product._registered_path = str(
            tmp_path / 'bundle' / spice_dir / 'data' / 'k.bsp')
        product.setup = setup

        # The path starts below the spice directory. With the PDS3 fallback
        # the lookup of the volume id would have failed instead.
        assert product.archive_path == Path('data', 'k.bsp')
