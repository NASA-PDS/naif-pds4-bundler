"""Unit tests for InventoryProduct class."""
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product import PDS3DocumentProduct

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

# Get the directory where the data is located.
DATA = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "msl" / "mslsp_1000"

@pytest.fixture
def mock_setup():
    """Minimal mock setup object with attributes needed to avoid crashes."""
    setup = MagicMock()
    setup.diff = "diff"
    setup.bundle_directory = "/mock/bundle"
    setup.working_directory = "/mock/work"
    setup.volume_id = "FakeVOL_419"
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
PRODUCT_INIT_PATH = "pds.naif_pds4_bundler.classes.product.product.Product.__init__"
VALIDATE_PATH = "pds.naif_pds4_bundler.classes.product.product_pds3doc.PDS3DocumentProduct._validate"
COMPARE_FILES_PATH = "pds.naif_pds4_bundler.classes.product.product_pds3doc.compare_files"

# ---------------------------------------------------------------------------
# PDSDocumentProduct.__init__ (pds_version 3)
# ---------------------------------------------------------------------------

class TestPDS3DocumentProductInit:
    """Tests for __init__ and _validate with pds_version == '3'."""

   #__init__
    def test_new_product_when_files_differ(self, monkeypatch, mock_setup):
        """Test that when compare_files returns True, product is marked as new."""

        monkeypatch.setattr(PRODUCT_INIT_PATH, lambda self: None)
        monkeypatch.setattr(VALIDATE_PATH, lambda self: None)

        # Force compare_files to return True (files differ)
        monkeypatch.setattr(COMPARE_FILES_PATH, lambda *args: True)

        product = PDS3DocumentProduct(mock_setup, "/path/FakeVOL_419/doc.txt")

        assert product.name == "doc.txt"
        assert product.new_product is True

    def test_not_new_product_when_files_match(self, monkeypatch, mock_setup):
        """Test that when compare_files returns False, product is marked as not new."""

        monkeypatch.setattr(PRODUCT_INIT_PATH, lambda self: None)
        monkeypatch.setattr(VALIDATE_PATH, lambda self: None)

        # Force compare_files to return False (files are the same)
        monkeypatch.setattr(COMPARE_FILES_PATH, lambda *args: False)

        product = PDS3DocumentProduct(mock_setup, "/path/FakeVOL_419/doc.txt")

        assert product.name == "doc.txt"
        assert product.new_product is False

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
