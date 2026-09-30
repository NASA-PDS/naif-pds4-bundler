"""Tests for the PDS3Product class."""
import os
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from pds.naif_pds4_bundler.classes.product.product_pds3 import PDS3Product


class TestPDS3ProductArchiveRootDir:

    @pytest.mark.parametrize('volume_id', ['MAVEN_1001', 'VOL_2002'])
    def test_archive_root_dir_is_the_setup_volume_id(self, volume_id) -> None:
        """The archive root directory of a PDS3 product is the volume id."""
        # Skip __init__ so the constructor does not try to register a file that
        # does not exist.
        product = PDS3Product.__new__(PDS3Product)
        product.setup = SimpleNamespace(volume_id=volume_id)

        # The volume id comes straight from the setup, whatever its value.
        assert product._archive_root_dir == volume_id

    @pytest.mark.parametrize('volume_id', ['MAVEN_1001', 'VOL_2002'])
    def test_register_records_path_relative_to_volume_id(
            self, mocker, tmp_path, volume_id) -> None:
        """register() uses the volume id as the archive directory."""
        # Put a real file inside a directory named after the volume id, with a
        # pds_version that would send Product's own fallback to PDS4.
        path = tmp_path / 'bundle' / volume_id / 'data' / 'k.bsp'
        path.parent.mkdir(parents=True)
        path.write_text('kernel-content', encoding='utf-8')
        setup = SimpleNamespace(volume_id=volume_id, pds_version='4',
                                mission_acronym='maven',
                                add_file=Mock(), add_checksum=Mock())

        # Skip __init__ so the constructor does not register the product
        # before the test is ready.
        product = PDS3Product.__new__(PDS3Product)
        product.path = str(path)
        product.setup = setup
        product.new_product = True
        mocker.patch.object(PDS3Product, '_compute_checksum', return_value='sum')

        # Register the product.
        product.register()

        # The setup receives the path below the volume directory. With the
        # PDS4 fallback the lookup of 'maven_spice' would have failed instead.
        setup.add_file.assert_called_once_with(os.path.join('data', 'k.bsp'))
