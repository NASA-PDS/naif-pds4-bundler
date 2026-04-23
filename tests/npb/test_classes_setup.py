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

    @pytest.mark.parametrize(('path_to_file_list', 'content'), [
        pytest.param('bundle_psyche_spice_v001.xml', ['bundle_psyche_spice_v001.xml'],
                     id='entry-without-path'),
        pytest.param('spice_kernels/ck/psyche_ep_rec_250630_250706.bc',
                     ['spice_kernels/ck/psyche_ep_rec_250630_250706.bc',
                      'spice_kernels/ck/psyche_ep_rec_250630_250706.xml',
                      'spice_kernels/mk/psyche_2025_v01.xml',
                      'spice_kernels/collection_spice_kernels_inventory_v001.csv',
                      'spice_kernels/collection_spice_kernels_v001.xml',
                      'document/spiceds_v001.html',
                      'document/spiceds_v001.xml',
                      'document/collection_document_inventory_v001.csv',
                      'document/collection_document_v001.xml',
                      'miscellaneous/collection_miscellaneous_inventory_v001.csv',
                      'miscellaneous/collection_miscellaneous_v001.xml',
                      'readme.txt',
                      'bundle_psyche_spice_v001.xml',
                      'miscellaneous/checksum/checksum_v001.tab',
                      'miscellaneous/checksum/checksum_v001.xml'],
                     id="entry-with-posix-path")])
    # TODO: If the data type within the file list is changed to path, the file
    #       contents must be POSIX-compliant
    def test_writes_file_list_entries_in_posix_format(self, tmp_path,
                                                      path_to_file_list: str, content: list) -> None:

        # Verify the format of the .file_list file is as expected:
        #   - one entry without path
        #   - one entry with Unix/POSIX path separators
        # and keep the trailing newline at EOF.

        setup = make_setup(tmp_path, file_list=content)

        setup.write_file_list()

        # Check that the file has been created in the correct location.
        expected_path = tmp_path / 'maven_release_03.file_list'

        # Check that the contents of the file are correct.
        assert expected_path.read_text(encoding='utf-8') == '\n'.join(content) + '\n'

        # Check that the expected path to file list entry exists in the content.
        assert path_to_file_list in content
