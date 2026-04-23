"""Unit tests for the pds.naif_pds4_bundler.classes.setup module"""
import logging
from pathlib import Path, PurePosixPath
from unittest.mock import mock_open

import pytest
from pds.naif_pds4_bundler.classes.setup import Setup


def make_setup(tmp_path, file_list: list[str], mission_acronym: str = "maven",
               run_type: str = "release", release: str = "3") -> Setup:
    # Create a minimal instance of Setup without calling Setup.__init__.
    setup = object.__new__(Setup)
    setup.file_list = file_list
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = mission_acronym
    setup.run_type = run_type
    setup.release = release

    return setup


class TestSetupWriteFileList:
    def test_creates_expected_file_with_expected_content(self, tmp_path) -> None:
        # Test how the method behaves when the 'file_list' file exists.
        #   - Creates the correct file.
        #   - In the correct path.
        #   - With the correct content.

        setup = make_setup(
            tmp_path,
            file_list=["bundle_maven_spice_v001.xml", "collection_spice_kernels.csv"])

        setup.write_file_list()

        # Check that the file has been created in the correct location.
        expected_path = tmp_path / "maven_release_03.file_list"

        # Check that only on file is created.
        assert list(tmp_path.iterdir()) == [expected_path]

        # Check that the contents of the file are correct.
        assert expected_path.read_text(encoding="utf-8") == (
            "bundle_maven_spice_v001.xml\n"
            "collection_spice_kernels.csv\n"
        )

    def test_creates_no_file_when_file_list_is_empty(self, tmp_path) -> None:
        # Test how the method behaves when the 'file_list' file not exists.
        #    - No file is created.

        setup = make_setup(tmp_path, file_list=[])

        setup.write_file_list()

        assert list(tmp_path.iterdir()) == []

    def test_logs_success_message_when_file_is_written(self, tmp_path,
                                                       monkeypatch, caplog) -> None:
        # When the 'file_list' exist, check the logging message is correct.

        setup = make_setup(tmp_path, file_list=["bundle_maven_spice_v001.xml"])
        monkeypatch.setattr("builtins.open", mock_open())

        # Reset the list of log records.
        caplog.clear()

        # Capture INFO-level log messages.
        with caplog.at_level(logging.INFO):
            setup.write_file_list()

        # Check the log message.
        assert caplog.messages == ["-- Run File List file written in working area."]

    def test_does_not_log_success_message_when_file_list_is_empty(self, tmp_path,
                                                                  monkeypatch, caplog) -> None:
        # When the 'file_list' does not exist, check that no log messages are recorded.

        setup = make_setup(tmp_path, file_list=[])
        monkeypatch.setattr("builtins.open", mock_open())

        # Reset the list of log records.
        caplog.clear()

        # Capture INFO-level log messages.
        with caplog.at_level(logging.INFO):
            setup.write_file_list()

        # Check that the register is empty.
        assert "-- Run File List file written in working area." not in caplog.messages

    @pytest.mark.parametrize(("file_entry", "expected_line"), [
        pytest.param("bundle_psyche_spice_v001.xml", "bundle_psyche_spice_v001.xml\n",
                     id="entry-without-path"),
        pytest.param(PurePosixPath("spice_kernels", "ck",
                                   "psyche_ep_rec_250630_250706.bc").as_posix(),
                     "spice_kernels/ck/psyche_ep_rec_250630_250706.bc\n",
                     id="entry-with-posix-path")])
    # TODO: If the data type within the file list is changed to path, the file
    #       contents must be POSIX-compliant
    def test_writes_file_list_entries_in_posix_format(self, tmp_path,
                                                      file_entry: str, expected_line: str) -> None:
        # Verify the .file_list format expected by the issue comment:
        #   - one entry without path
        #   - one entry with Unix/POSIX path separators
        # and keep the trailing newline at EOF.

        setup = make_setup(tmp_path, file_list=[file_entry])

        setup.write_file_list()

        # Check the content.
        expected_path = tmp_path / "maven_release_03.file_list"
        assert expected_path.read_text(encoding="utf-8") == expected_line

        # Check the path is POSIX.
        assert "\\" not in expected_path.read_text(encoding="utf-8")
