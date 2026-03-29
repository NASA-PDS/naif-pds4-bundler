from unittest.mock import MagicMock

import pytest

import spiceypy

from pds.naif_pds4_bundler.pipeline.runtime import handle_npb_error


def test_handle_error_raises_runtime_error(caplog):
    """Verifies that the function always raises RuntimeError with the message."""
    message = "Test failure message"

    with pytest.raises(RuntimeError, match=message):
        handle_npb_error(message)

    assert f"-- {message}" in caplog.text


def test_handle_error_calls_setup_methods(tmp_path, monkeypatch):
    """Verifies artifact generation and template cleanup when setup is provided."""
    # Setup mocks
    mock_setup = MagicMock()
    mock_setup.write_file_list = MagicMock()
    mock_setup.write_checksum_registry = MagicMock()

    # Create a dummy template file to test removal
    temp_file = tmp_path / "template.xml"
    temp_file.write_text("<xml/>")
    mock_setup.template_files = [str(temp_file)]

    # Mock SPICE and os.remove
    monkeypatch.setattr(spiceypy, "kclear", MagicMock())

    with pytest.raises(RuntimeError):
        handle_npb_error("Error", setup=mock_setup)

    # Verify side effects
    mock_setup.write_file_list.assert_called_once()
    mock_setup.write_checksum_registry.assert_called_once()
    assert not temp_file.exists()
    spiceypy.kclear.assert_called_once()


def test_handle_error_spice_cleanup_without_setup(monkeypatch):
    """Verifies that SPICE is cleared even if no setup object is provided."""
    mock_kclear = MagicMock()
    monkeypatch.setattr(spiceypy, "kclear", mock_kclear)

    with pytest.raises(RuntimeError):
        handle_npb_error("Quick Error", setup=None)

    mock_kclear.assert_called_once()


def test_handle_error_handles_missing_templates(monkeypatch):
    """Verifies it doesn't crash if a template file in the list is already gone."""
    mock_setup = MagicMock()
    mock_setup.template_files = ["/non/existent/path.xml"]

    monkeypatch.setattr(spiceypy, "kclear", MagicMock())

    # This should not raise FileNotFoundError because of the os.path.exists check
    with pytest.raises(RuntimeError):
        handle_npb_error("Error with missing template", setup=mock_setup)
