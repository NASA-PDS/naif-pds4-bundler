"""Unit tests for the pds.naif_pds4_bundler.classes.setup module"""
import logging
from unittest.mock import mock_open, Mock

import pytest

import requests
from pds.naif_pds4_bundler.classes.setup import Setup


def make_setup(tmp_path, mission_acronym: str = "maven",
               run_type: str = "release", release: str = "3") -> Setup:
    # Create a minimal instance of Setup without calling Setup.__init__.
    setup = object.__new__(Setup)
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = mission_acronym
    setup.run_type = run_type
    setup.release = release

    return setup


class TestSetupWriteFileList:
    @staticmethod
    def make_minimal_setup(tmp_path, file_list) -> Setup:
        setup = make_setup(tmp_path)

        setup.file_list = file_list

        return setup

    @pytest.mark.parametrize('file_list, expected_contents', [
        (['bundle_maven_spice_v001.xml',
          'collection_spice_kernels.csv'],
         'bundle_maven_spice_v001.xml\n'
         'collection_spice_kernels.csv\n'),
        (['miscellaneous/collection_miscellaneous_inventory_v001.csv',
          'miscellaneous/collection_miscellaneous_v001.xml',
          'readme.txt'],
         'miscellaneous/collection_miscellaneous_inventory_v001.csv\n'
         'miscellaneous/collection_miscellaneous_v001.xml\n'
         'readme.txt\n')])
    # TODO: Update the file_list inputs to be PathLike when code gets updated.
    def test_creates_expected_file_with_expected_content(self, tmp_path,
                                                         file_list, expected_contents) -> None:
        # Test how the method behaves when the 'file_list' file exists.
        #   - Creates the correct file.
        #   - In the correct path.
        #   - With the correct content.

        setup = self.make_minimal_setup(tmp_path, file_list=file_list)

        setup.write_file_list()

        # Check that the file has been created in the correct location.
        expected_path = tmp_path / "maven_release_03.file_list"

        # Check that only on file is created.
        assert list(tmp_path.iterdir()) == [expected_path]

        # Check that the contents of the file are correct.
        assert expected_path.read_text(encoding="utf-8") == expected_contents

    def test_creates_no_file_when_file_list_is_empty(self, tmp_path) -> None:
        # Test how the method behaves when the 'file_list' file not exists.
        #    - No file is created.

        setup = self.make_minimal_setup(tmp_path, file_list=[])

        setup.write_file_list()

        assert list(tmp_path.iterdir()) == []

    def test_logs_success_message_when_file_is_written(self, tmp_path,
                                                       monkeypatch, caplog) -> None:
        # When the 'file_list' exist, check the logging message is correct.

        setup = self.make_minimal_setup(tmp_path, file_list=["bundle_maven_spice_v001.xml"])
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

        setup = self.make_minimal_setup(tmp_path, file_list=[])
        monkeypatch.setattr("builtins.open", mock_open())

        # Reset the list of log records.
        caplog.clear()

        # Capture INFO-level log messages.
        with caplog.at_level(logging.INFO):
            setup.write_file_list()

        # Check that the register is empty.
        assert "-- Run File List file written in working area." not in caplog.messages


class TestSetupWriteValidateConfig:

    @staticmethod
    def make_validate_setup(tmp_path) -> Setup:

        setup = make_setup(tmp_path)

        setup.working_directory = str(tmp_path)
        setup.bundle_directory = '/bundle'
        setup.xml_model = 'https://example.com/PDS4_PDS_1B00.sch'
        setup.schema_location = ('https://pds.nasa.gov/pds4/pds/v1 '
                                 'https://example.com/PDS4_PDS_1B00.xsd')

        return setup

    def test_creates_expected_files_with_expected_content(self, tmp_path,
                                                          monkeypatch) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # Mock the responses to requests.get()
        schematron_response = Mock(content=b"schematron content")
        schema_response = Mock(content=b"schema content")

        # Replaces calls to requests.get().
        monkeypatch.setattr(
            'pds.naif_pds4_bundler.classes.setup.requests.get',
            Mock(side_effect=[schematron_response, schema_response]),
        )

        setup.write_validate_config()

        expected_schematron = tmp_path / 'PDS4_PDS_1B00.sch'
        expected_schema = tmp_path / 'PDS4_PDS_1B00.xsd'
        expected_config = tmp_path / 'maven_release_03.validate_config'

        # Check that the destination contains exactly the files created by the
        # function.
        assert sorted(path.name for path in tmp_path.iterdir()) == [
            'PDS4_PDS_1B00.sch',
            'PDS4_PDS_1B00.xsd',
            'maven_release_03.validate_config',
        ]

        # Check the contents of the files.
        assert expected_schematron.read_bytes() == b'schematron content'
        assert expected_schema.read_bytes() == b'schema content'
        assert expected_config.read_text(encoding='utf-8') == (
            '# Run the PDS validate tool where the NPB working directory resides:\n'
            '# $ validate -t /bundle/maven_spice '
            f'-c {tmp_path}/maven_release_03.validate_config '
            f'-r {tmp_path}/maven_release_03.validate_report\n'
            '#\n'
            f'validate.schema = {tmp_path}/PDS4_PDS_1B00.xsd\n'
            f'validate.schematron = {tmp_path}/PDS4_PDS_1B00.sch\n'
            'validate.verbose = 1\n'
            'validate.rule = pds4.bundle\n'
            'validate.strictFieldChecks = true\n'
        )

    def test_creates_no_files_when_schematron_request_fails(self, tmp_path, monkeypatch) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # Replace the first call to requests and provoke to rise a base exception.
        monkeypatch.setattr(
            "pds.naif_pds4_bundler.classes.setup.requests.get",
            Mock(side_effect=requests.exceptions.RequestException("network error")),
        )

        setup.write_validate_config()

        # Check that the destination does not contain any files.
        assert list(tmp_path.iterdir()) == []

    def test_creates_only_schematron_file_when_schema_request_fails(self, tmp_path, monkeypatch) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # First requests call, is a correct call.
        schematron_response = Mock(content=b"schematron content")

        # Replace the two calls to requests.
        # The first one runs successfully, whilst the second one throws a base exception.
        monkeypatch.setattr(
            "pds.naif_pds4_bundler.classes.setup.requests.get",
            Mock(side_effect=[
                schematron_response,
                requests.exceptions.RequestException("network error"),
            ]),
        )

        setup.write_validate_config()

        expected_schematron = tmp_path / "PDS4_PDS_1B00.sch"
        expected_schema = tmp_path / "PDS4_PDS_1B00.xsd"
        expected_config = tmp_path / "maven_release_03.validate_config"

        # Check the first request creates the file with the correct content.
        assert expected_schematron.exists()
        assert expected_schematron.read_bytes() == b"schematron content"

        # Check that only creates the file from the first requests call.
        # Here exists a side effect: If the method fails after the first call to
        # requests, the file created by that call is retained and no further
        # files are created.
        assert not expected_schema.exists()
        assert not expected_config.exists()
        assert sorted(path.name for path in tmp_path.iterdir()) == ["PDS4_PDS_1B00.sch"]

    def test_logs_success_messages_when_validate_config_is_written(self, tmp_path,
                                                                   monkeypatch, caplog) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # Mock the responses to requests.get()
        monkeypatch.setattr(
            "pds.naif_pds4_bundler.classes.setup.requests.get",
            Mock(side_effect=[Mock(content=b"schematron"), Mock(content=b"schema")]),
        )

        # Mock the open files process.
        monkeypatch.setattr("builtins.open", mock_open())

        with caplog.at_level(logging.INFO):
            setup.write_validate_config()

        assert caplog.messages == [
            "-- PDS Validate Tool configuration file written in working area:",
            f"   {tmp_path / 'maven_release_03.validate_config'}",
        ]

    def test_logs_warning_when_schematron_is_not_reachable(self, tmp_path,
                                                           monkeypatch, caplog) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # Replace the first call to requests and provoke to rise a base exception.
        monkeypatch.setattr(
            "pds.naif_pds4_bundler.classes.setup.requests.get",
            Mock(side_effect=requests.exceptions.RequestException("network error")),
        )

        with caplog.at_level(logging.WARNING):
            setup.write_validate_config()

        assert caplog.messages == [
            "-- PDS Validate Tool configuration file not written.",
            "   PDS Schematron not reachable: PDS4_PDS_1B00.sch",
        ]

    def test_logs_warning_when_schema_location_is_not_reachable(self, tmp_path,
                                                                monkeypatch, caplog) -> None:
        # Create the minimal object with the necessary attributes.
        setup = self.make_validate_setup(tmp_path)

        # Replace the two calls to requests.
        # The first one runs successfully, whilst the second one throws a base exception.
        monkeypatch.setattr(
            "pds.naif_pds4_bundler.classes.setup.requests.get",
            Mock(side_effect=[
                Mock(content=b"schematron"),
                requests.exceptions.RequestException("network error"),
            ]),
        )

        with caplog.at_level(logging.WARNING):
            setup.write_validate_config()

        assert caplog.messages == [
            "-- PDS Validate Tool configuration file not written.",
            "   PDS Schema location not reachable: https://example.com/PDS4_PDS_1B00.xsd",
        ]
