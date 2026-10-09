"""Tests for the RunState class."""
import logging
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.run_state import RunState


def make_setup(tmp_path) -> SimpleNamespace:
    """Return the configuration values the writers use to name their file.

    :param tmp_path: Directory used as the working directory.
    """
    return SimpleNamespace(working_directory=str(tmp_path),
                           mission_acronym='maven', run_type='release',
                           release='3')


class TestRunStateInit:

    def test_starts_at_step_one_with_empty_records(self) -> None:
        """A new RunState starts at step 1 with no files and no checksums."""

        # Build a RunState without giving it any value.
        run_state = RunState()

        # The defaults are the beginning of a pipeline run.
        assert run_state.step == 1
        assert run_state.file_list == []
        assert run_state.checksum_registry == []

    def test_instances_do_not_share_their_lists(self) -> None:
        """Adding records to one RunState leaves any other one untouched."""

        # Build two independent RunState objects.
        first = RunState()
        second = RunState()

        # Fill only the first one.
        first.add_file('readme.txt')
        first.add_checksum('readme.txt', 'dca7381138766f7f36e7468d75b725c0')

        # The second one still has empty lists, so they are not shared.
        assert second.file_list == []
        assert second.checksum_registry == []


class TestRunStateAdd:

    @pytest.mark.parametrize('initial, entry, expected', [
        ([], 'bundle_maven_spice_v001.xml', ['bundle_maven_spice_v001.xml']),
        (['bundle_maven_spice_v001.xml'], 'document/spiceds_v001.html',
         ['bundle_maven_spice_v001.xml', 'document/spiceds_v001.html']),
    ])
    def test_add_file_appends_entry_unchanged(
            self, tmp_path, initial, entry, expected) -> None:
        """add_file appends the received entry as is, after the existing ones,
        and does not create any file."""

        # Start from a RunState that may already hold some files.
        run_state = RunState(file_list=list(initial))

        # Add one more file.
        run_state.add_file(entry)

        # The entry is the last element and the disk has not been touched.
        assert run_state.file_list == expected
        assert list(tmp_path.iterdir()) == []

    @pytest.mark.parametrize('initial, path, checksum, expected', [
        ([], 'readme.txt', 'dca7381138766f7f36e7468d75b725c0',
         ['readme.txt dca7381138766f7f36e7468d75b725c0']),
        (['readme.txt dca7381138766f7f36e7468d75b725c0'],
         'document/spiceds_v001.html', '78a6f8dbfa6c52d0d927bacb09ba6098',
         ['readme.txt dca7381138766f7f36e7468d75b725c0',
          'document/spiceds_v001.html 78a6f8dbfa6c52d0d927bacb09ba6098']),
    ])
    def test_add_checksum_appends_path_and_checksum(
            self, tmp_path, initial, path, checksum, expected) -> None:
        """add_checksum appends a '<path> <checksum>' record after the
        existing ones and does not create any file."""

        # Start from a RunState that may already hold some records.
        run_state = RunState(checksum_registry=list(initial))

        # Add one more record.
        run_state.add_checksum(path, checksum)

        # The record is the last element and the disk has not been touched.
        assert run_state.checksum_registry == expected
        assert list(tmp_path.iterdir()) == []


class TestRunStateWriters:

    @pytest.mark.parametrize('writer, attribute, suffix', [
        ('write_file_list', 'file_list', 'file_list'),
        ('write_checksum_registry', 'checksum_registry', 'checksum'),
    ])
    def test_writes_one_entry_per_line_in_order(
            self, tmp_path, writer, attribute, suffix) -> None:
        """Each writer creates '<acronym>_<run type>_<release>.<suffix>' in
        the working directory, with one entry per line in insertion order."""

        # Fill the list that the writer under test is going to dump.
        run_state = RunState(**{attribute: ['first', 'second', 'third']})

        # Call the writer by name, so both writers share this test.
        getattr(run_state, writer)(make_setup(tmp_path))

        # Only the expected file exists, with the entries in their order and
        # the release zero-padded to two digits ('3' becomes '03').
        expected_path = tmp_path / f'maven_release_03.{suffix}'
        assert list(tmp_path.iterdir()) == [expected_path]
        assert expected_path.read_text(encoding='utf-8') == (
            'first\nsecond\nthird\n')

    @pytest.mark.parametrize('writer, attribute, message', [
        ('write_file_list', 'file_list',
         '-- Run File List file written in working area.'),
        ('write_checksum_registry', 'checksum_registry',
         '-- Run Checksum Registry file written in working area.'),
    ])
    def test_logs_a_message_when_the_file_is_written(
            self, tmp_path, caplog, writer, attribute, message) -> None:
        """Each writer logs a single info message once its file is written."""

        # Fill the list that the writer under test is going to dump.
        run_state = RunState(**{attribute: ['first']})

        # Write the file while capturing the log at info level.
        with caplog.at_level(logging.INFO):
            getattr(run_state, writer)(make_setup(tmp_path))

        # The only record is the confirmation of the writer.
        assert caplog.messages == [message]

    @pytest.mark.parametrize('writer', [
        'write_file_list', 'write_checksum_registry',
    ])
    def test_writes_and_logs_nothing_when_empty(self, tmp_path,
                                                caplog, writer) -> None:
        """With nothing added, a writer creates no file and logs no message."""

        # A RunState that has not received any file nor checksum.
        run_state = RunState()

        # Call the writer while capturing the log at info level.
        with caplog.at_level(logging.INFO):
            getattr(run_state, writer)(make_setup(tmp_path))

        # No file was created and nothing was logged.
        assert list(tmp_path.iterdir()) == []
        assert caplog.messages == []
