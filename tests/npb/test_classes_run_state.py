"""Tests for the RunState class."""
import logging
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.run_state import RunState


def make_setup(tmp_path, mission_acronym: str = 'maven',
               run_type: str = 'release', release: str = '3') -> SimpleNamespace:
    """Return the configuration values the writers use to name their file.

    :param tmp_path: Directory used as the working directory.
    :param mission_acronym: Mission acronym, first part of the file name.
    :param run_type: Run type, second part of the file name.
    :param release: Release number, last part of the file name.
    """
    return SimpleNamespace(working_directory=str(tmp_path),
                           mission_acronym=mission_acronym, run_type=run_type,
                           release=release)


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
        ([], 'spice_kernels/fk/maven_v11.tf', ['spice_kernels/fk/maven_v11.tf']),
        ([], '/usr1/pds4/staging/maven/maven_spice/readme.txt',
         ['/usr1/pds4/staging/maven/maven_spice/readme.txt']),
        (['bundle_maven_spice_v001.xml'], 'document/spiceds_v001.html',
         ['bundle_maven_spice_v001.xml', 'document/spiceds_v001.html']),
    ])
    def test_add_file_appends_entry_unchanged(
            self, tmp_path, caplog, initial, entry, expected) -> None:
        """add_file appends the received entry as is, after the existing ones,
        and neither creates any file nor logs anything."""

        # Start from a RunState that may already hold some files.
        run_state = RunState(file_list=list(initial))

        # Add one more file while capturing the log at info level.
        with caplog.at_level(logging.INFO):
            run_state.add_file(entry)

        # The entry is the last element, the disk has not been touched and
        # nothing was logged.
        assert run_state.file_list == expected
        assert list(tmp_path.iterdir()) == []
        assert caplog.messages == []

    @pytest.mark.parametrize('initial, path, expected', [
        ([], 'bundle_maven_spice_v001.xml', ['bundle_maven_spice_v001.xml']),
        ([], 'spice_kernels/fk/maven_v11.xml',
         ['spice_kernels/fk/maven_v11.xml']),
        (['bundle_maven_spice_v001.xml'], 'document/spiceds_v001.xml',
         ['bundle_maven_spice_v001.xml', 'document/spiceds_v001.xml']),
        # Registering the same label twice lists it twice, nothing is skipped.
        (['readme.xml'], 'readme.xml', ['readme.xml', 'readme.xml']),
    ])
    def test_register_label_file_appends_path_unchanged(
            self, tmp_path, caplog, initial, path, expected) -> None:
        """register_label_file appends the received path as is, after the
        existing ones, and neither creates any file nor logs anything."""

        # Start from a RunState that may already hold some files.
        run_state = RunState(file_list=list(initial))

        # Register one more label while capturing the log at info level.
        with caplog.at_level(logging.INFO):
            run_state.register_label_file(path)

        # The path is the last element, the disk has not been touched and
        # nothing was logged.
        assert run_state.file_list == expected
        assert list(tmp_path.iterdir()) == []
        assert caplog.messages == []

    @pytest.mark.parametrize('initial, path, checksum, expected', [
        ([], 'readme.txt', 'dca7381138766f7f36e7468d75b725c0',
         ['readme.txt dca7381138766f7f36e7468d75b725c0']),
        (['readme.txt dca7381138766f7f36e7468d75b725c0'],
         'document/spiceds_v001.html', '78a6f8dbfa6c52d0d927bacb09ba6098',
         ['readme.txt dca7381138766f7f36e7468d75b725c0',
          'document/spiceds_v001.html 78a6f8dbfa6c52d0d927bacb09ba6098']),
    ])
    def test_add_checksum_appends_path_and_checksum(
            self, tmp_path, caplog, initial, path, checksum, expected) -> None:
        """add_checksum appends a '<path> <checksum>' record after the
        existing ones and neither creates any file nor logs anything."""

        # Start from a RunState that may already hold some records.
        run_state = RunState(checksum_registry=list(initial))

        # Add one more record while capturing the log at info level.
        with caplog.at_level(logging.INFO):
            run_state.add_checksum(path, checksum)

        # The record is the last element, the disk has not been touched and
        # nothing was logged.
        assert run_state.checksum_registry == expected
        assert list(tmp_path.iterdir()) == []
        assert caplog.messages == []


class TestRunStateRegisterProduct:

    @pytest.mark.parametrize(
        'is_registrable, expected_files, expected_checksums', [
            (True,
             [os.path.join('spice_kernels', 'ck', 'x.bc')],
             ['/stage/maven_spice/spice_kernels/ck/x.bc '
              'fadf8e23f21b18710f8cb1d3be8eeebd']),
            (False, [], []),
        ])
    def test_register_product_records_only_registrable_products(
            self, is_registrable, expected_files, expected_checksums) -> None:
        """A registrable product adds its archive path to the File List and
        its full path with the checksum to the Checksum Registry; any other
        adds nothing."""

        # A product that already knows its archive path and checksum.
        product = SimpleNamespace(
            is_registrable=is_registrable,
            archive_path=Path('spice_kernels', 'ck', 'x.bc'),
            registered_path='/stage/maven_spice/spice_kernels/ck/x.bc',
            checksum='fadf8e23f21b18710f8cb1d3be8eeebd')
        run_state = RunState()

        # Register it once.
        run_state.register_product(product)

        # Each record shows up exactly once, or not at all.
        assert run_state.file_list == expected_files
        assert run_state.checksum_registry == expected_checksums


class TestRunStateWriters:

    @pytest.mark.parametrize('mission_acronym, run_type, release, stem', [
        ('maven', 'release', '3', 'maven_release_03'),
        ('psyche', 'labels', '12', 'psyche_labels_12'),
    ])
    @pytest.mark.parametrize('writer, attribute, suffix', [
        ('write_file_list', 'file_list', 'file_list'),
        ('write_checksum_registry', 'checksum_registry', 'checksum'),
    ])
    def test_writes_one_entry_per_line_in_order(
            self, tmp_path, writer, attribute, suffix,
            mission_acronym, run_type, release, stem) -> None:
        """Each writer creates '<acronym>_<run type>_<release>.<suffix>' in
        the working directory, with one entry per line in insertion order."""

        # Fill the list that the writer under test is going to dump.
        run_state = RunState(**{attribute: ['first', 'second', 'third']})
        setup = make_setup(tmp_path, mission_acronym, run_type, release)

        # Call the writer by name, so both writers share this test.
        getattr(run_state, writer)(setup)

        # Only the expected file exists, with the entries in their order and
        # the release zero-padded to two digits ('3' becomes '03').
        expected_path = tmp_path / f'{stem}.{suffix}'
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

    @pytest.mark.parametrize('adder, calls, writer, suffix, expected', [
        ('add_file',
         [('bundle_psyche_spice_v012.xml',),
          ('collection_spice_kernels_inventory_v012.csv',),
          ('spice_kernels/mk/psyche_2025_v01.tm',)],
         'write_file_list', 'file_list',
         'bundle_psyche_spice_v012.xml\n'
         'collection_spice_kernels_inventory_v012.csv\n'
         'spice_kernels/mk/psyche_2025_v01.tm\n'),
        ('add_checksum',
         [('/usr1/pds4/staging/psyche/psyche_spice/spice_kernels/ck/'
           'psyche_ep_rec_250616_250622.bc', 'fadf8e23f21b18710f8cb1d3be8eeebd'),
          ('/usr1/pds4/staging/psyche/psyche_spice/spice_kernels/ck/'
           'psyche_ep_rec_250623_250629.bc', '55b74c3bdc78bb8c956f0464f3c628c6'),
          ('/usr1/pds4/staging/psyche/psyche_spice/document/spiceds_v001.html',
           '78a6f8dbfa6c52d0d927bacb09ba6098')],
         'write_checksum_registry', 'checksum',
         '/usr1/pds4/staging/psyche/psyche_spice/spice_kernels/ck/'
         'psyche_ep_rec_250616_250622.bc fadf8e23f21b18710f8cb1d3be8eeebd\n'
         '/usr1/pds4/staging/psyche/psyche_spice/spice_kernels/ck/'
         'psyche_ep_rec_250623_250629.bc 55b74c3bdc78bb8c956f0464f3c628c6\n'
         '/usr1/pds4/staging/psyche/psyche_spice/document/spiceds_v001.html '
         '78a6f8dbfa6c52d0d927bacb09ba6098\n'),
    ])
    def test_added_records_are_written_in_order(
            self, tmp_path, adder, calls, writer, suffix, expected) -> None:
        """Whatever was added is written unchanged, one record per line and
        in the order it was added."""

        # Start from an empty RunState and add every record through the real
        # method, so the written format is the one the add method builds.
        run_state = RunState()
        for arguments in calls:
            getattr(run_state, adder)(*arguments)

        # Write the matching file.
        getattr(run_state, writer)(make_setup(tmp_path))

        # The file holds exactly the added records.
        expected_path = tmp_path / f'maven_release_03.{suffix}'
        assert list(tmp_path.iterdir()) == [expected_path]
        assert expected_path.read_text(encoding='utf-8') == expected
