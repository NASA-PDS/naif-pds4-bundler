import logging
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from _pytest.logging import LogCaptureHandler

from pds.naif_pds4_bundler.classes.log import Log
from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs


class DummySetup():
    def __init__(self, tmp_path, args):
        self.args = args
        self.version = "1.2.3"
        self.mission_name = "Test Mission"
        self.mission_acronym = "TM"
        self.run_type = "archive"
        self.working_directory = str(tmp_path)
        self.template_files = []
        self.step = 3
        self.pds_version = "4"
        self.release = "1"

        self.write_file_list = MagicMock()
        self.write_checksum_registry = MagicMock()
        self.write_validate_config = MagicMock()


@pytest.fixture
def args():
    return PipelineArgs(
        config="config.xml",
        debug=False,
        silent=False,
        verbose=False,
        log=False,
        faucet="bundle",
    )


@pytest.fixture
def cleanup_root_logger():
    """
    Keep tests isolated since Log configures the root logger.
    """
    root = logging.getLogger()
    old_handlers = root.handlers[:]
    old_level = root.level

    for handler in root.handlers[:]:
        root.removeHandler(handler)
        try:
            handler.close()
        except OSError:
            pass

    yield

    # Clean up any handlers added during the test (except capture handlers)
    for handler in root.handlers[:]:
        if not isinstance(handler, LogCaptureHandler):
            root.removeHandler(handler)
            try:
                handler.close()
            except OSError:
                pass

    # Restore original non-pytest handlers
    for handler in old_handlers:
        if handler not in root.handlers:
            root.addHandler(handler)
    root.setLevel(old_level)


def test_init_without_log_file(tmp_path, args, cleanup_root_logger):
    setup = DummySetup(tmp_path, args)

    log = Log(setup, args)

    assert log.setup is setup
    assert log.args is args
    assert log.log_file == ""

    root = logging.getLogger()
    assert root.level == logging.INFO

    file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
    stream_handlers = [
        h for h in root.handlers
        if isinstance(h, logging.StreamHandler)
           and not isinstance(h, logging.FileHandler)
           and not isinstance(h, LogCaptureHandler)
    ]

    assert file_handlers == []
    assert len(stream_handlers) == 1


def test_init_with_log_file_creates_file_handler(tmp_path, cleanup_root_logger):
    args = PipelineArgs(config="config.xml", log=True, faucet="bundle")

    setup = DummySetup(tmp_path, args)

    log = Log(setup, args)

    expected = Path(tmp_path) / "TM_archive_temp.log"
    assert log.log_file == str(expected)

    root = logging.getLogger()
    file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]

    assert len(file_handlers) == 1
    assert Path(file_handlers[0].baseFilename) == expected


def test_init_with_log_file_removes_existing_temp_log(tmp_path, cleanup_root_logger):
    args = PipelineArgs(config="config.xml", log=True, faucet="bundle")

    existing = tmp_path / "TM_archive_temp.log"
    existing.write_text("old content")

    setup = DummySetup(tmp_path, args)

    log = Log(setup, args)

    assert log.log_file == str(existing)
    assert existing.exists()


def test_start_logs_banner_and_runtime_info(tmp_path, args, cleanup_root_logger, monkeypatch, caplog):
    setup = DummySetup(tmp_path, args)
    log = Log(setup, args)

    monkeypatch.setattr("socket.gethostname", lambda: "test-host")
    monkeypatch.setattr("platform.platform", lambda: "TestOS-1.0")
    monkeypatch.setattr("platform.python_version", lambda: "3.11.0")
    monkeypatch.setattr("platform.python_build", lambda: ("main", "build-xyz"))

    with caplog.at_level(logging.INFO):
        log.start()

    text = caplog.text
    assert "naif-pds4-bundler-1.2.3 for Test Mission" in text
    assert "-- Executed on test-host at " in text
    assert "-- Platform: TestOS-1.0" in text
    assert "-- Python version: 3.11.0 (Build: build-xyz)" in text
    assert "-- The following arguments have been provided:" in text
    assert "faucet:" in text
    assert "bundle" in text


def test_start_logs_labeling_mode_message(tmp_path, cleanup_root_logger, caplog):
    args = PipelineArgs(config="config.xml", faucet="labels")
    setup = DummySetup(tmp_path, args)
    log = Log(setup, args)

    with caplog.at_level(logging.INFO):
        log.start()

    assert "Running in labeling mode. Only label products are generated." in caplog.text


@pytest.mark.parametrize("release, expected_path", [
    ("9", "TM_archive_09.log"),
    ("12", "TM_archive_12.log")
])
def test__rename_log_file_with_release_number(
        tmp_path, cleanup_root_logger, monkeypatch, release, expected_path
):
    """Verifies that the temp log is renamed using a zero-padded release version."""
    args = PipelineArgs(config="config.xml", log=True, faucet="bundle")

    setup = DummySetup(tmp_path, args)
    setup.release = release

    # Mock shutil.move to prevent actual file system movement during the test
    mock_move = MagicMock()
    monkeypatch.setattr(shutil, "move", mock_move)

    log = Log(setup, args)
    # Manually set the temp log path as if __init__ just created it
    temp_path = str(tmp_path / "TM_archive_temp.log")
    log.log_file = temp_path

    # Execute
    log._rename_log_file()

    # Verify
    expected_path = str(tmp_path / expected_path )
    mock_move.assert_called_once_with(temp_path, expected_path)


def test__rename_log_file_skips_if_no_file(tmp_path, args, cleanup_root_logger, monkeypatch):
    """Verifies that shutil.move is not called if log_file is empty."""
    setup = DummySetup(tmp_path, args)

    mock_move = MagicMock()
    monkeypatch.setattr(shutil, "move", mock_move)

    log = Log(setup, args)
    log.log_file = ""  # Ensure it's empty

    log._rename_log_file()

    mock_move.assert_not_called()
