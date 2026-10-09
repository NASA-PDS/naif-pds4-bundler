"""Tests for the PDS4Product class."""
import os
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.product.product_pds4 import PDS4Product
from pds.naif_pds4_bundler.classes.run_state import RunState


class TestPDS4ProductArchiveRootDir:

    @pytest.mark.parametrize('mission_acronym', ['maven', 'bepicolombo'])
    def test_archive_root_dir_is_the_mission_spice_directory(
            self, mission_acronym) -> None:
        """The archive root directory of a PDS4 product is '<mission>_spice'."""
        # Skip __init__ so the constructor does not try to register a file
        # that does not exist.
        product = PDS4Product.__new__(PDS4Product)
        product.setup = SimpleNamespace(mission_acronym=mission_acronym)

        # The name is built from the mission acronym in the setup.
        assert product._archive_root_dir == f'{mission_acronym}_spice'

    @pytest.mark.parametrize('mission_acronym', ['maven', 'bepicolombo'])
    def test_register_records_path_relative_to_mission_spice_directory(
            self, mocker, tmp_path, mission_acronym) -> None:
        """register() uses '<mission>_spice' as the archive directory."""
        # Put a real file inside the mission's spice directory, with a
        # pds_version that would send Product's own fallback to PDS3.
        spice_dir = f'{mission_acronym}_spice'
        path = tmp_path / 'bundle' / spice_dir / 'data' / 'k.bsp'
        path.parent.mkdir(parents=True)
        path.write_text('kernel-content', encoding='utf-8')
        setup = SimpleNamespace(mission_acronym=mission_acronym,
                                pds_version='3', volume_id='MAVEN_1001')

        # Skip __init__ so the constructor does not register the product
        # before the test is ready.
        product = PDS4Product.__new__(PDS4Product)
        product.path = str(path)
        product.setup = setup
        product.run_state = RunState()
        product.new_product = True
        mocker.patch.object(PDS4Product, '_compute_checksum', return_value='sum')

        # Register the product.
        product.register()

        # The run state receives the path below the spice directory. With the
        # PDS3 fallback the lookup of the volume id would have failed instead.
        assert product.run_state.file_list == [os.path.join('data', 'k.bsp')]
