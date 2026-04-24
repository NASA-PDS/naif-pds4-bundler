"""Unit tests for the pds.naif_pds4_bundler.classes.setup module"""
import logging
from types import SimpleNamespace
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


class TestSetupSetRelease:
    @staticmethod
    def make_release_setup(tmp_path, clear=None, kerlist=None, pds_version="4") -> Setup:
        setup = make_setup(tmp_path)

        setup.file_list = []
        setup.bundle_directory = '/bundle'
        setup.pds_version = pds_version
        setup.args = SimpleNamespace(clear=clear, kerlist=kerlist)

        return setup

    def test_sets_expected_release_when_clear_argument_is_provided(self,
                                                                   tmp_path) -> None:
        # Check the behaviour when a previous '.file_list' is provided
        # using args.clear.
        #   - Gets the release from the file name.
        #   - Sets the previous release correctly.
        #   - Marks the execution as an increment.

        # Build a setup object with a valid args.clear.
        setup = self.make_release_setup(tmp_path,
                                        clear='maven_release_003.file_list')

        setup.set_release()

        # The method gets the release by split it from the .file_list.
        assert setup.release == '003'

        # The method calculate the 'current_release' as 'release - 1'.
        assert setup.current_release == '002'

        # Check that the increment values is set as True.
        assert setup.increment is True

    def test_sets_expected_release_from_previous_bundle_label(self, tmp_path,
                                                              monkeypatch) -> None:
        # Check the behaviour when a previous bundle label exists.
        #   - Gets the highest previous release from the bundle directory.
        #   - Increments it.
        #   - Stores the previous release correctly.

        # Build a default setup object.
        setup = self.make_release_setup(tmp_path)

        # Mock the glob.glob() call and the return values as a list with two
        # bundle labels.
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(return_value=[
                                '/bundle/maven_spice/bundle_maven_spice_v002.xml',
                                '/bundle/maven_spice/bundle_maven_spice_v010.xml']))

        setup.set_release()

        # The method retrieves the last item from the sorted list, so it sets
        # the current value to 010.
        assert setup.release == '011'
        assert setup.current_release == '010'
        assert setup.increment is True

    @pytest.mark.parametrize('bundle_matches', [
        [],
        ['/bundle/maven_spice/bundle_maven_spice_vbad.xml']])
    def test_sets_expected_release_from_previous_kernel_list_when_bundle_lookup_fails(
            self, tmp_path, monkeypatch, bundle_matches) -> None:
        # Check the behaviour when the bundle lookup fails.
        #   - Falls back to the previous kernel list.
        #   - Gets the highest previous release from the kernel list files.
        #   - Increments it.
        #
        # The realistic exceptions in the first try block are:
        #   - IndexError: no bundle labels found.
        #   - ValueError: malformed bundle label release number.

        # Build a setup object with pds4.
        setup = self.make_release_setup(tmp_path, pds_version='4')

        # Mock the glob.glob() call twice:
        #   - First, look for bundle labels (when it fails, raise an IndexError)
        #   - Second, look for kernel list (when it fails, raise a ValueError)
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(side_effect=[bundle_matches, [
                                f'{tmp_path}/maven_release_003.kernel_list',
                                f'{tmp_path}/maven_release_011.kernel_list']]))

        setup.set_release()

        # The highest kernel_list value is 011, so the new one is 012.
        assert setup.release == '012'
        assert setup.current_release == '011'
        assert setup.increment is True

    def test_sets_first_release_when_kernel_list_is_provided_as_argument(
            self, tmp_path, monkeypatch) -> None:
        # Check the behaviour when args.kerlist is provided.
        #   - Does not deduce the release from previous kernel list files.
        #   - Sets the execution as the first release.
        #   - Does not mark the execution as an increment.

        # Build a setup object with an 'existing' kernel_list.
        setup = self.make_release_setup(tmp_path, pds_version='4',
                                        kerlist='input.kernel_list')

        # Mock the  glob.glob() with an empty return value so that the first
        # 'except' statement is triggered and the second 'try' statement is
        # reached.
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(return_value=[]))

        setup.set_release()

        # As no previous usable release could be identified, this is the first
        # one.
        assert setup.release == '001'
        assert setup.current_release == ''
        assert setup.increment is False

    @pytest.mark.parametrize('kernel_list_matches', [
        [],
        ['maven_release_bad.kernel_list']])
    def test_sets_first_release_when_kernel_list_lookup_fails(
            self, tmp_path, monkeypatch, kernel_list_matches) -> None:
        # Check the behaviour when neither the bundle lookup nor them kernel
        # list lookup provide a valid previous release.
        #   - Sets the execution as the first release.
        #   - Leaves the previous release empty.
        #
        # The realistic exceptions in the second try block are:
        #   - IndexError: no kernel list files found.
        #   - ValueError: malformed kernel list release number.

        # Build a setup object with pds4.
        setup = self.make_release_setup(tmp_path, pds_version='4')

        if kernel_list_matches:
            kernel_list_matches = [f'{tmp_path}/{kernel_list_matches[0]}']

        # Mock the glob.glob() call:
        #   - First, empty bundle
        #   - Second, empty or incorrect kernel_list
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(side_effect=[[], kernel_list_matches]))

        setup.set_release()

        # As no previous usable release could be identified, this is the first
        # one.
        assert setup.release == '001'
        assert setup.current_release == ''
        assert setup.increment is False

    def test_logs_expected_messages_when_clear_argument_is_provided(
            self, tmp_path, caplog) -> None:
        # When args.clear is provided, check the logging messages are correct.

        # Build a setup object with a valid args.clear.
        setup = self.make_release_setup(tmp_path, clear='maven_release_003.file_list')

        with caplog.at_level(logging.INFO):
            setup.set_release()

        assert caplog.messages == [
            '-- Checking existence of previous release.',
            '-- Generating release 003 as obtained from file list from previous run: '
            'maven_release_003.file_list',
            '']

    def test_logs_expected_messages_when_previous_bundle_label_exists(
            self, tmp_path, monkeypatch, caplog) -> None:
        # When a previous bundle label exists, check the logging messages are
        # correct.

        # Build a default setup object.
        setup = self.make_release_setup(tmp_path)

        # Mock the glob.glob() call and the return values as a list with two
        # bundle labels.
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(return_value=[
                                '/bundle/maven_spice/bundle_maven_spice_v002.xml',
                                '/bundle/maven_spice/bundle_maven_spice_v010.xml']))

        with caplog.at_level(logging.INFO):
            setup.set_release()

        assert caplog.messages == ['-- Checking existence of previous release.',
                                   '-- Generating release 011.',
                                   '']

    @pytest.mark.parametrize('bundle_matches', [
        [],
        ['/bundle/maven_spice/bundle_maven_spice_vbad.xml']])
    def test_logs_expected_messages_when_bundle_lookup_fails_but_kernel_list_succeeds(
            self, tmp_path, monkeypatch, caplog, bundle_matches) -> None:
        # When the bundle lookup fails but the kernel list lookup succeeds,
        # check the logging messages are correct.

        setup = self.make_release_setup(tmp_path, pds_version='4')

        # Mock the glob.glob() call:
        #   - First, fail because an empty bundle
        #   - Second, valid kernel_list
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(side_effect=[bundle_matches,
                                              [f'{tmp_path}/maven_release_003.kernel_list',
                                               f'{tmp_path}/maven_release_011.kernel_list']]))

        with caplog.at_level(logging.INFO):
            setup.set_release()

        assert caplog.messages == ['-- Checking existence of previous release.',
                                   '-- Bundle label not found. Checking previous kernel list.',
                                   '-- Generating release 012',
                                   '']

    def test_logs_expected_messages_when_kernel_list_is_provided_as_argument(
            self, tmp_path, monkeypatch, caplog) -> None:
        # When args.kerlist is provided, check the logging messages are
        # correct.

        setup = self.make_release_setup(tmp_path, pds_version='4',
                                        kerlist='input.kernel_list')

        # Mock the glob.glob() call to reach the second 'try' (the first search fail).
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(return_value=[]))

        with caplog.at_level(logging.WARNING):
            setup.set_release()

        assert caplog.messages == [
            '-- Bundle label not found. Checking previous kernel list.',
            '-- Kernel list provided as input. Release number cannot be obtained.',
            '-- This is the first release.']

    @pytest.mark.parametrize('kernel_list_matches', [
        [],
        ['maven_release_bad.kernel_list']])
    def test_logs_only_first_release_warning_for_pds3_when_kernel_list_lookup_fails(
            self, tmp_path, monkeypatch, caplog, kernel_list_matches) -> None:
        # When the run is PDS3 and no valid previous release can be obtained,
        # check that only the first-release warning is logged.

        # Build a setup object with pds3.
        setup = self.make_release_setup(tmp_path, pds_version='3')

        if kernel_list_matches:
            kernel_list_matches = [f'{tmp_path}/{kernel_list_matches[0]}']

        # Mock the glob.glob() call:
        #   - First, empty bundle
        #   - Second, empty or incorrect kernel_list
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(side_effect=[[], kernel_list_matches]))

        with caplog.at_level(logging.WARNING):
            setup.set_release()

        # When the setting is set to pds3, only a warning is issued.
        assert caplog.messages == ['-- This is the first release.']


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
