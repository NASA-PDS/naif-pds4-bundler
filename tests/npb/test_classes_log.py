import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from _pytest.logging import LogCaptureHandler

from pds.naif_pds4_bundler.classes.log import Log


class DummySetup:
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
    return SimpleNamespace(
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


def test_init_with_log_file_creates_file_handler(tmp_path, args, cleanup_root_logger):
    args.log = True
    setup = DummySetup(tmp_path, args)

    log = Log(setup, args)

    expected = Path(tmp_path) / "TM_archive_temp.log"
    assert log.log_file == str(expected)

    root = logging.getLogger()
    file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]

    assert len(file_handlers) == 1
    assert Path(file_handlers[0].baseFilename) == expected


def test_init_with_log_file_removes_existing_temp_log(tmp_path, args, cleanup_root_logger):
    args.log = True
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


def test_start_logs_labeling_mode_message(tmp_path, args, cleanup_root_logger, caplog):
    args.faucet = "labels"
    setup = DummySetup(tmp_path, args)
    log = Log(setup, args)

    with caplog.at_level(logging.INFO):
        log.start()

    assert "Running in labeling mode. Only label products are generated." in caplog.text


def test_stop_removes_templates_and_writes_outputs(
    tmp_path, args, cleanup_root_logger, monkeypatch, caplog
):
    setup = DummySetup(tmp_path, args)

    template1 = tmp_path / "template1.xml"
    template2 = tmp_path / "template2.xml"
    template1.write_text("a")
    template2.write_text("b")
    setup.template_files = [str(template1), str(template2)]

    kclear = MagicMock()
    monkeypatch.setattr("spiceypy.kclear", kclear)

    log = Log(setup, args)

    with caplog.at_level(logging.INFO):
        log.stop()

    assert not template1.exists()
    assert not template2.exists()
    setup.write_file_list.assert_called_once()
    setup.write_checksum_registry.assert_called_once()
    setup.write_validate_config.assert_called_once()
    kclear.assert_called_once()
    assert setup.step == 4
    assert "Step 3 - Generate run by-product files" in caplog.text
    assert "Execution finished at " in caplog.text
    assert "End of log." in caplog.text


def test_stop_skips_validate_config_for_clear_runs(
    tmp_path, args, cleanup_root_logger, monkeypatch
):
    args.faucet = "clear"
    setup = DummySetup(tmp_path, args)
    monkeypatch.setattr("spiceypy.kclear", MagicMock())

    log = Log(setup, args)
    log.stop()

    setup.write_file_list.assert_called_once()
    setup.write_checksum_registry.assert_called_once()
    setup.write_validate_config.assert_not_called()


def test_stop_skips_validate_config_for_non_pds4(
    tmp_path, args, cleanup_root_logger, monkeypatch
):
    setup = DummySetup(tmp_path, args)
    setup.pds_version = "3"
    monkeypatch.setattr("spiceypy.kclear", MagicMock())

    log = Log(setup, args)
    log.stop()

    setup.write_file_list.assert_called_once()
    setup.write_checksum_registry.assert_called_once()
    setup.write_validate_config.assert_not_called()


def test_stop_renames_log_file_with_release_number(
    tmp_path, args, cleanup_root_logger, monkeypatch
):
    args.log = True
    setup = DummySetup(tmp_path, args)
    setup.release = "7"

    kclear = MagicMock()
    monkeypatch.setattr("spiceypy.kclear", kclear)

    moved = {}

    def fake_move(src, dst):
        moved["src"] = src
        moved["dst"] = dst

    monkeypatch.setattr("shutil.move", fake_move)

    log = Log(setup, args)
    log.stop()

    assert moved["src"].endswith("TM_archive_temp.log")
    assert moved["dst"].endswith("TM_archive_07.log")
    kclear.assert_called_once()
