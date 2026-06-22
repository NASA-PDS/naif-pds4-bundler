"""Unit tests for InventoryProduct class."""
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_pds3doc import PDS3DocumentProduct

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

# Get the directory where the data is located.
DATA = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "msl" / "mslsp_1000"
DATA_2 = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "msl"

@pytest.fixture
def mock_setup():
    setup = MagicMock()
    setup.diff = True
    setup.bundle_directory = str(DATA_2)
    setup.working_directory = "/working"
    setup.volume_id = "mslsp_1000"
    return setup

@pytest.fixture
def mock_product():
    product = MagicMock(spec=PDS3DocumentProduct)
    product.path = DATA / "catalog" / "release.cat"
    product.name = "release.cat"

    product.setup = MagicMock()
    product.setup.release = "025"
    product.setup.release_date = "2020-12-04"
    return product

# ---------------------------------------------------------------------------
# Patch targets (relative to where InventoryProduct imports things)
# ---------------------------------------------------------------------------

MODULE = "pds.naif_pds4_bundler.classes.product.product_pds3doc"

# ---------------------------------------------------------------------------
# PDSDocumentProduct.__init__ (pds_version 3)
# ---------------------------------------------------------------------------

class TestPDS3DocumentProductInit:
    """Tests for __init__ with pds_version == '3'."""

   #__init__
    def test_init_handles_path_formatting(self, mock_setup):
        """Test that path.split handles deep paths correctly for the file name."""

        full_path = str(DATA/"errata.txt")
        product = PDS3DocumentProduct(setup=mock_setup, path=full_path)

        assert product.name == "errata.txt"


    #_validate
    def test_validate_cat_success(self, mock_product, caplog):
        """Test validation for a catalog file when the required string is found."""

        mock_product.name = "kitty.cat"

        with caplog.at_level(logging.INFO):
            PDS3DocumentProduct._validate(mock_product)

        assert "Is present in: kitty.cat" in caplog.text
        assert "WARNING" not in caplog.text

    def test_validate_cat_success_2(self, mock_product, caplog):
        """Test validation for release.cat when the required string is found."""

        with caplog.at_level(logging.INFO):
            PDS3DocumentProduct._validate(mock_product)

        assert f"Is present in: {mock_product.name}" in caplog.text
        assert "WARNING" not in caplog.text

    def test_validate_release_fail(self, mocker, caplog):
        """Test validation for a catalog file when the required string is not found."""

        inputs = \
        (""""OBJECT                          = DATA_SET_RELEASE"
            "DATA_SET_ID                     = "MSL-M-SPICE-6-V1.0""
            "RELEASE_DATE                    = 2026-04-19"
            "RELEASE_MEDIUM                  = "ONLINE DISK STORAGE""
            "PRODUCT_TYPE                    = "SPICE_KERNELS""
            "ARCHIVE_STATUS                  = "LOCALLY ARCHIVED""
            "DISTRIBUTION_TYPE               = "MSL-SPICE""
            "DATA_PROVIDER_NAME              = "JPL-NAIF""
            "DESCRIPTION                     = "Mock Description""
            "END_OBJECT                      = DATA_SET_RELEASE""""")


        mock_file = mocker.mock_open(read_data=inputs)
        mocker.patch("builtins.open", mock_file)

        mock_file.name = "release.cat"
        mock_file.path = "release.cat"
        mock_file.setup = MagicMock()
        mock_file.setup.release = "0333"
        mock_file.setup.release_date = "2026-04-19"

        with caplog.at_level(logging.WARNING):
            PDS3DocumentProduct._validate(mock_file)

        assert f"Is not present in: {mock_file.name}" in caplog.text
