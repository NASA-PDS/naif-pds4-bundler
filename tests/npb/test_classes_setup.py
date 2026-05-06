"""Unit tests for the pds.naif_pds4_bundler.classes.setup module"""
import logging
import os
import re
from types import SimpleNamespace
from typing import Generator
from unittest.mock import mock_open, Mock

import pytest

import requests
from pds.naif_pds4_bundler.classes.setup import Setup


# This function is used to ensure that version numbers cannot be traced back to
# specific IP addresses
def im_version(*parts) -> str:
    return '.'.join(str(part) for part in parts)


def make_setup(tmp_path, mission_acronym: str = "maven",
               run_type: str = "release", release: str = "3") -> Setup:
    # Create a minimal instance of Setup without calling Setup.__init__.
    setup = object.__new__(Setup)
    setup.working_directory = str(tmp_path)
    setup.mission_acronym = mission_acronym
    setup.run_type = run_type
    setup.release = release

    return setup


class TestSetupCheckConfiguration:

    @pytest.fixture(autouse=True)
    def patch_handle_npb_error_and_restore_cwd(self, monkeypatch) -> Generator[None, None, None]:
        """The current directory is saved, as the check_configuration function
        switches between directories and eventually returns to the original
        directory. If a test fails, the working directory is restored to its
        original state."""

        original_cwd = os.getcwd()

        # Mock the handle_npb_error call.
        def raise_configuration_error(message):
            # When the code makes the call, a RuntimeError will be raised with
            # the same message
            raise RuntimeError(message)

        # Perform the handle_npb_error call mock.
        monkeypatch.setattr(
            'pds.naif_pds4_bundler.classes.setup.handle_npb_error',
            raise_configuration_error,
        )

        yield

        # After the test, restore the working directory.
        os.chdir(original_cwd)

    @staticmethod
    def make_templates_root(tmp_path, versions=(im_version(10, 11, 12, 13),),
                            bundle_template='    <Identification_Area>\n',
                            include_bundle_template=True) -> str:
        """Create a dummy template directory structure.
        By default, it creates a version 10.11.12.13, with a
        template_bundle.xml file containing an <Identification_Area> element
        indented by 4 spaces."""

        # Build the base path.
        root = tmp_path / 'root'
        templates_root = root / 'templates'

        # Creates the necessary environment using the required templates and
        # directory structure.
        for version in versions:
            version_dir = templates_root / version
            version_dir.mkdir(parents=True, exist_ok=True)

            if include_bundle_template:
                (version_dir / 'template_bundle.xml').write_text(
                    bundle_template, encoding='utf-8'
                )

            (version_dir / 'template_collection.xml').write_text(
                f'collection template for {version}\n', encoding='utf-8'
            )

        # Build the environment for PDS3.
        pds3_dir = templates_root / 'pds3'
        pds3_dir.mkdir(parents=True, exist_ok=True)
        (pds3_dir / 'pds3_template.lbl').write_text(
            'pds3 template\n', encoding='utf-8'
        )

        return f'{str(root)}{os.sep}'

    def make_check_setup(self, tmp_path, pds_version='4', relative_paths=False,
                         information_model=im_version(10, 11, 12, 13), xml_model=None,
                         schema_location=None, templates_directory=None,
                         root_dir=None, faucet='bundle', include_information_model=True,
                         coverage_kernels=None, include_coverage_kernels=True) -> Setup:
        setup = make_setup(tmp_path)

        # Define and create the temporary directories.
        work = tmp_path / 'work'
        staging = tmp_path / 'staging'
        bundle = tmp_path / 'bundle'
        kernels = tmp_path / 'kernels'

        for directory in (work, staging, bundle, kernels):
            directory.mkdir(exist_ok=True)

        # Create the maven_spice directory inside the bundle, which is the one
        # required for PDS4.
        (bundle / 'maven_spice').mkdir(exist_ok=True)

        # Create a readme.txt file to prevent the method from failing due to a
        # lack of readme configuration.
        (bundle / 'maven_spice' / 'readme.txt').write_text(
            'existing readme\n', encoding='utf-8'
        )

        # Set the setup attributes.
        setup.pds_version = pds_version
        setup.volume_id = 'MAVEN_1001'
        setup.date_format = 'maklabel'
        setup.end_of_line = 'CRLF'
        setup.kernel_endianness = 'little'
        setup.faucet = faucet

        setup.working_directory = 'work' if relative_paths else str(work)
        setup.staging_directory = 'staging' if relative_paths else str(staging)
        setup.bundle_directory = 'bundle' if relative_paths else str(bundle)
        setup.kernels_directory = ['kernels'] if relative_paths else [str(kernels)]

        if include_information_model:
            setup.information_model = information_model

        # Set a valid xml_model and schema_location if they are not provided.
        if xml_model is None:
            xml_model = 'https://example.com/PDS4_PDS_ABCD.sch'
        if schema_location is None:
            schema_location = (
                'https://pds.nasa.gov/pds4/pds/v1 '
                'https://example.com/PDS4_PDS_ABCD.xsd'
            )

        setup.xml_model = xml_model
        setup.schema_location = schema_location

        setup.templates_directory = templates_directory

        # If root_dir is not provided, mocks a template structure.
        setup.root_dir = (root_dir or self.make_templates_root(tmp_path))

        # Build a valid kernel and meta-kernel patterns.
        setup.kernel_list_config = {'fk': {}, 'spk': {}}
        setup.mk = [{
            '@name': 'maven_$version_$release.tm',
            'name': [{'pattern': [{'#text': 'version'}, {'#text': 'release'}]}]}]

        if coverage_kernels is None:
            coverage_kernels = {'pattern': 'maven_*.bc'}

        if include_coverage_kernels:
            setup.coverage_kernels = coverage_kernels

        return setup

    @pytest.mark.parametrize('coverage_kernels, include_coverage_kernels,expected_coverage_kernels', [
        ({'pattern': 'maven_*.bc'}, True, [{'pattern': 'maven_*.bc'}]),
        ([{'pattern': 'maven_*.bc'}], True, [{'pattern': 'maven_*.bc'}]),
        (None, False, None)])
    def test_applies_expected_side_effects_for_valid_pds4_configuration(
            self, tmp_path, monkeypatch, coverage_kernels, include_coverage_kernels,
            expected_coverage_kernels) -> None:

        # Change the current directory to the temporary directory so that
        # relative paths are resolved within tmp_path.
        monkeypatch.chdir(tmp_path)

        # Build the setup.
        setup = self.make_check_setup(tmp_path, relative_paths=True,
                                      coverage_kernels=coverage_kernels,
                                      include_coverage_kernels=include_coverage_kernels)

        setup.check_configuration()

        # Check that all paths have been changed from relative to absolute and
        # that the values are of the expected data types.
        assert setup.working_directory == str(tmp_path / 'work')
        assert setup.staging_directory == str(tmp_path / 'staging' / 'maven_spice')
        assert setup.bundle_directory == str(tmp_path / 'bundle')
        assert setup.kernels_directory == [str(tmp_path / 'kernels')]
        assert setup.information_model_float == pytest.approx(float('10011012013'))
        assert setup.templates_directory == str(tmp_path / 'work')
        assert sorted(setup.template_files) == sorted([
            f'{tmp_path / "work" / "template_bundle.xml"}',
            f'{tmp_path / "work" / "template_collection.xml"}'])
        assert (tmp_path / 'work' / 'template_bundle.xml').exists()
        assert (tmp_path / 'work' / 'template_collection.xml').exists()
        assert setup.xml_tab == 4

        # Check the final result for both scenarios: attribute present or
        # attribute absent.
        if include_coverage_kernels:
            assert setup.coverage_kernels == expected_coverage_kernels
        else:
            assert not hasattr(setup, 'coverage_kernels')

    def test_handles_mission_directory_in_absolute_staging_directory(
            self, tmp_path) -> None:

        # Create the configuration using absolute paths.
        setup = self.make_check_setup(tmp_path)

        mission_dir = 'maven_spice'
        staging_directory = tmp_path / 'staging' / mission_dir

        # The directory is created so that the branch can be fully evaluated.
        staging_directory.mkdir()

        setup.staging_directory = str(staging_directory)

        setup.check_configuration()

        assert setup.staging_directory == str(staging_directory)

    def test_creates_missing_staging_directory_when_faucet_uses_it(self, tmp_path,
                                                                   monkeypatch) -> None:
        # Move the test to the temporal directory.
        monkeypatch.chdir(tmp_path)

        # Build a setup with relative paths.
        setup = self.make_check_setup(tmp_path, relative_paths=True)

        # Force the staging directory not to exist.
        setup.staging_directory = 'missing_staging'

        setup.check_configuration()

        # Check that the staging base directory has been created.
        assert (tmp_path / 'missing_staging').is_dir()

    @pytest.mark.parametrize('faucet', ['plan', 'list', 'checks'])
    def test_keeps_running_when_staging_and_bundle_are_unused_by_faucet(
            self, tmp_path, monkeypatch, caplog, faucet) -> None:

        # Move the test to the temporal directory.
        monkeypatch.chdir(tmp_path)

        # Build a setup within faucet modes.
        setup = self.make_check_setup(tmp_path, relative_paths=True, faucet=faucet)

        # Force non-existent routes.
        setup.staging_directory = 'missing_staging'
        setup.bundle_directory = 'missing_bundle'

        # Added a minimal readme.
        setup.readme = {
            'input': str(tmp_path / 'missing_readme.txt'),
            'cognisant_authority': 'NAIF',
            'overview': 'Generated readme',
        }

        # Cause os.mkdir to fail and raise an OSError. The aim is to avoid using
        # BaseException.
        monkeypatch.setattr(
            'pds.naif_pds4_bundler.classes.setup.os.mkdir',
            Mock(side_effect=OSError('permission denied')),
        )

        # Capture and check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [(logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
                    (logging.WARNING, '-- Creating staging directory: missing_staging/maven_spice.'),
                    (logging.WARNING, f'-- Staging directory cannot be created but is not used with {faucet} faucet.'),
                    (logging.WARNING, f'-- Bundle directory does not exist but is not used with {faucet} faucet.'),
                    (logging.INFO, '-- Label templates will use the ones from information model 10.11.12.13.'),
                    (logging.INFO, f'-- Label templates directory: {setup.working_directory}'),
                    (logging.WARNING, 'Input readme file not present. File will be generated from configuration.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    @pytest.mark.parametrize('faucet', ['clear', 'staging', 'bundle', 'labels', None, ''])
    def test_raises_when_missing_staging_directory_cannot_be_created_for_used_faucet(
            self, tmp_path, monkeypatch, faucet) -> None:

        # Move the test to the temporal directory.
        monkeypatch.chdir(tmp_path)

        # Build a setup using the mode provided by 'faucet'.
        setup = self.make_check_setup(tmp_path, relative_paths=True, faucet=faucet)

        # Forces a non-existent staging directory.
        setup.staging_directory = 'missing_staging'

        # Simulate that the directory cannot be created in order to trigger the
        # exception.
        monkeypatch.setattr(
            'pds.naif_pds4_bundler.classes.setup.os.mkdir',
            Mock(side_effect=OSError('permission denied')),
        )

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError,
                           match='Staging directory cannot be created: '
                                 'missing_staging\\.'):
            setup.check_configuration()

    def test_raises_when_bundle_directory_is_missing_for_used_faucet(
            self, tmp_path, monkeypatch) -> None:
        # Move the test to the temporal directory.
        monkeypatch.chdir(tmp_path)

        # Build a setup with relative paths.
        setup = self.make_check_setup(tmp_path, relative_paths=True)

        # Forces a non-existent bundle directory.
        setup.bundle_directory = 'missing_bundle'

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError,
                           match='Bundle directory does not exist:'
                                 ' missing_bundle\\.'):
            setup.check_configuration()

    def test_raises_when_kernel_directory_is_missing(self, tmp_path) -> None:

        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Forces a non-existent kernel directory.
        setup.kernels_directory = [str(tmp_path / 'missing_kernels')]

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=re.escape(f'Directory does not exist: '
                                                         f'{tmp_path / "missing_kernels"}.')):
            setup.check_configuration()

    def test_logs_directory_collision_before_raising(self, tmp_path, caplog) -> None:
        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Forces that the staging directory is the same as the working directory.
        setup.staging_directory = setup.working_directory

        # Captures the logging and the RuntimeException. And also check the
        # message returned by handle_npb_error.
        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError,
                               match='Update working, staging, or bundle '
                                     'directory\\.'):
                setup.check_configuration()

        # Check the logging level and logging messages.
        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.ERROR, '--The working, staging, and bundle directories must be different:'),
            (logging.ERROR, f'  working: {setup.working_directory}'),
            (logging.ERROR, f'  staging: {setup.working_directory}'),
            (logging.ERROR, f'  bundle:  {setup.bundle_directory}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_raises_when_working_directory_is_missing(self, tmp_path) -> None:
        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Forces a non-existent working directory.
        setup.working_directory = str(tmp_path / 'missing_work')

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=re.escape(f'Directory does not exist: '
                                                         f'{tmp_path / "missing_work"}.')):
            setup.check_configuration()

    @pytest.mark.parametrize('date_format, values, expected_message', [
        ('maklabel', {'mission_start': '2020-01-01T00:00:00.000Z'},
         'mission_start parameter does not match the required format: YYYY-MM-DDThh:mm:ssZ\\.'),
        ('maklabel', {'mission_finish': '2020-01-01'},
         'mission_finish does not match the required format: YYYY-MM-DDThh:mm:ssZ\\.'),
        ('infomod2', {'increment_start': '2020-01-01T00:00:00Z'},
         'increment_start parameter does not match the required format: YYYY-MM-DDThh:mm:ss\\.sssZ\\.'),
        ('infomod2', {'increment_finish': '2020-01-01T00:00:00Z'},
         'increment_finish does not match the required format: YYYY-MM-DDThh:mm:ss\\.sssZ\\.'),
        ('maklabel', {'mission_start': '2020-01-01T00:00:00Z', 'mission_finish': '2020-01-01T00:00:00Z',
                      'increment_start': '2020-01-01T00:00:00Z', 'increment_finish': '2020-01-02T00:00:00Z'},
         None),
        ('infomod2', {'mission_start': '2020-01-01T00:00:00.000Z', 'mission_finish': '2020-01-01T00:00:00.000Z',
                      'increment_start': '2020-01-01T00:00:00.000Z', 'increment_finish': '2020-01-02T00:00:00.000Z'},
         None)])
    def test_validates_configured_times_according_to_selected_date_format(
            self, tmp_path, date_format, values, expected_message) -> None:

        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Set the format.
        setup.date_format = date_format
        setup.end_of_line = 'LF' if date_format == 'infomod2' else 'CRLF'

        for field, value in values.items():
            setattr(setup, field, value)

        # In case of invalid dates, this behaviour will be handled by
        # handle_npb_error, which will raise a RuntimeError. Also, checks the
        # returned message.
        if expected_message:
            with pytest.raises(RuntimeError, match=expected_message):
                setup.check_configuration()

        # In case of valid dates, check that the method completed successfully
        # and ran the PDS4 configuration through to the end.
        else:
            setup.check_configuration()
            assert setup.xml_tab == 4

    @pytest.mark.parametrize('increment_start, increment_finish', [
        ('', '2020-01-02T00:00:00Z'),
        ('2020-01-01T00:00:00Z', '')])
    def test_raises_when_only_one_increment_boundary_is_configured(
            self, tmp_path, increment_start, increment_finish) -> None:
        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Set the values for the increments.
        setup.increment_start = increment_start
        setup.increment_finish = increment_finish

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError,
                           match='If provided via configuration, increment_start '
                                 'and increment_finish parameters need to be '
                                 'provided together\\.'):
            setup.check_configuration()

    def test_generates_xml_model_and_schema_location_when_not_configured(
            self, tmp_path, caplog) -> None:
        # Create the templates.
        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 2, 3, 4),))

        # Build the setup without setting xml_model and schema_location.
        setup = self.make_check_setup(tmp_path, information_model=im_version(1, 2, 3, 4),
                                      xml_model='', schema_location='',
                                      root_dir=root_dir)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        # Check template files.
        assert setup.xml_model == 'https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1234.sch'
        assert setup.schema_location == ('https://pds.nasa.gov/pds4/pds/v1 '
                                         'https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1234.xsd')

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.INFO, '-- Schema XML Model (xml_model) not provided with configuration file. Set to:'),
            (logging.INFO, f'   {setup.xml_model}'),
            (logging.INFO, '-- Schema Location (schema_location) not provided with configuration file. Set to:'),
            (logging.INFO, f'   {setup.schema_location}'),
            (logging.INFO, '-- Label templates will use the ones from information model 1.2.3.4.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    @pytest.mark.parametrize('attribute, value, expected_message', [
        ('information_model', '1.2.bad',
         'PDS4 Information Model 1.2.bad format from configuration is incorrect.'),
        ('xml_model', 'https://example.com/PDS4_PDS_9999.sch',
         'PDS4 Information Model ABCD is incoherent with the XML Model '
         'version: https://example.com/PDS4_PDS_9999.sch.'),
        ('schema_location', 'https://pds.nasa.gov/pds4/pds/v1 https://example.com/PDS4_PDS_9999.xsd',
         'PDS4 Information Model ABCD is incoherent with the Schema '
         'location: https://pds.nasa.gov/pds4/pds/v1 https://example.com/PDS4_PDS_9999.xsd.')])
    def test_raises_when_information_model_configuration_is_invalid(
            self, tmp_path, attribute, value, expected_message) -> None:

        # Build a setup and set the attributes to be tested.
        setup = self.make_check_setup(tmp_path)
        setattr(setup, attribute, value)

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=expected_message):
            setup.check_configuration()

    @pytest.mark.parametrize('information_model, xml_model, schema_location, expected_template_version', [
        (im_version(1, 6, 0, 0), 'https://example.com/PDS4_PDS_1600.sch',
         'https://pds.nasa.gov/pds4/pds/v1 https://example.com/PDS4_PDS_1600.xsd',
         im_version(1, 5, 0, 0)),
        (im_version(2, 1, 0, 0), 'https://example.com/PDS4_PDS_2100.sch',
         'https://pds.nasa.gov/pds4/pds/v1 https://example.com/PDS4_PDS_2100.xsd',
         im_version(2, 0, 0, 0)),
        pytest.param(im_version(1, 0, 0, 0), 'https://example.com/PDS4_PDS_1000.sch',
                     'https://pds.nasa.gov/pds4/pds/v1 https://example.com/PDS4_PDS_1000.xsd',
                     im_version(1, 5, 0, 0),
                     marks=pytest.mark.skip(reason='Fails due to bug'))])
    def test_uses_closest_available_templates_when_exact_schema_is_unavailable(
            self, tmp_path, caplog, information_model, xml_model, schema_location,
            expected_template_version) -> None:

        # Create two versions of the available templates.
        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 5, 0, 0),
                                                                im_version(2, 0, 0, 0)))

        # The configuration requires a version that does not exist exactly.
        setup = self.make_check_setup(tmp_path, information_model=information_model,
                                      xml_model=xml_model,
                                      schema_location=schema_location,
                                      root_dir=root_dir)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.WARNING,
             f'-- Label templates will use the ones from information model {expected_template_version}.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        # Check that the expected templates have been used.
        assert sorted(setup.template_files) == sorted([
            f'{tmp_path / "work" / "template_bundle.xml"}',
            f'{tmp_path / "work" / "template_collection.xml"}'])

    def test_raises_when_custom_templates_directory_does_not_exist(
            self, tmp_path) -> None:

        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 5, 0, 0),))

        # Build a setup with a custom templates directory that does not exist.
        setup = self.make_check_setup(tmp_path, information_model=im_version(1, 5, 0, 0),
                                      xml_model='https://example.com/PDS4_PDS_1500.sch',
                                      schema_location=('https://pds.nasa.gov/pds4/pds/v1 '
                                                       'https://example.com/PDS4_PDS_1500.xsd'),
                                      templates_directory=str(tmp_path / 'missing_templates'),
                                      root_dir=root_dir)

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match='Path provided/derived for '
                                               'templates is not available\\.'):
            setup.check_configuration()

    def test_uses_custom_templates_and_fills_missing_templates_from_default(
            self, tmp_path, caplog) -> None:

        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 5, 0, 0),))

        # Create a custom templates' directory.
        custom_templates = tmp_path / 'custom_templates'
        custom_templates.mkdir()

        # Only adds one template.
        (custom_templates / 'template_bundle.xml').write_text(
            '      <Identification_Area>\n', encoding='utf-8')

        setup = self.make_check_setup(tmp_path, information_model=im_version(1, 5, 0, 0),
                                      xml_model='https://example.com/PDS4_PDS_1500.sch',
                                      schema_location=('https://pds.nasa.gov/pds4/pds/v1 '
                                                       'https://example.com/PDS4_PDS_1500.xsd'),
                                      templates_directory=str(custom_templates),
                                      root_dir=root_dir)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.WARNING, '-- Template template_collection.xml has not been provided. Using label from: '),
            (logging.WARNING, f'   {root_dir}templates/{im_version(1, 5, 0, 0)}/'),
            (logging.INFO, f'-- Label templates directory: {custom_templates}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        # Check that the custom template has been used.
        assert ((tmp_path / 'work' / 'template_bundle.xml').read_text(encoding='utf-8') ==
                '      <Identification_Area>\n')
        assert (tmp_path / 'work' / 'template_collection.xml').exists()
        assert setup.xml_tab == 6

    def test_sets_default_xml_tab_when_template_bundle_is_missing(
            self, tmp_path, caplog) -> None:

        # Create the templates without template_bundle.xml.
        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 5, 0, 0),),
                                            include_bundle_template=False)

        # Build the setup.
        setup = self.make_check_setup(tmp_path, information_model=im_version(1, 5, 0, 0),
                                      xml_model='https://example.com/PDS4_PDS_1500.sch',
                                      schema_location=('https://pds.nasa.gov/pds4/pds/v1 '
                                                       'https://example.com/PDS4_PDS_1500.xsd'),
                                      root_dir=root_dir)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.INFO, '-- Label templates will use the ones from information model 1.5.0.0.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}'),
            (logging.WARNING, '-- XML Template not found to determine XML Tab. It has been set to 2.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        assert setup.xml_tab == 2

    def test_sets_default_xml_tab_when_template_bundle_has_no_identification_area(
            self, tmp_path, caplog) -> None:
        # Crate a template_bundle.xml without expected tag.
        root_dir = self.make_templates_root(tmp_path, versions=(im_version(1, 5, 0, 0),),
                                            bundle_template='<No_Identification_Area>\n')

        # Build the setup.
        setup = self.make_check_setup(tmp_path, information_model=im_version(1, 5, 0, 0),
                                      xml_model='https://example.com/PDS4_PDS_1500.sch',
                                      schema_location=('https://pds.nasa.gov/pds4/pds/v1 '
                                                       'https://example.com/PDS4_PDS_1500.xsd'),
                                      root_dir=root_dir)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE (little endian) binary format.'),
            (logging.INFO, '-- Label templates will use the ones from information model 1.5.0.0.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}'),
            (logging.WARNING, '-- XML Template not useful to determine XML Tab. It has been set to 2.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        assert setup.xml_tab == 2

    @pytest.mark.parametrize('include_information_model',
                             [True, False])
    def test_pds3_configuration_uses_pds3_templates_and_leaves_xml_tab_zero(
            self, tmp_path, include_information_model) -> None:

        # Build a setup with PDS3.
        setup = self.make_check_setup(tmp_path, pds_version='3',
                                      include_information_model=include_information_model)
        setup.bundle_directory = str(tmp_path / 'bundle')
        setup.staging_directory = str(tmp_path / 'staging')
        setup.kernels_directory = [str(tmp_path / 'kernels')]
        setup.volume_id = 'MAVEN_1001'

        setup.check_configuration()

        # Check that the PDS3 templates have been processed as expected.
        #
        # The templates ramain in working directory.
        assert setup.templates_directory == str(tmp_path / 'work')

        # PDS3 template have been copied.
        assert sorted(os.path.basename(path) for path in setup.template_files) == ['pds3_template.lbl']

        # The file exists.
        assert (tmp_path / 'work' / 'pds3_template.lbl').exists()

        # In PDS3, the XML tab isn't calculated.
        assert setup.xml_tab == 0

    @pytest.mark.parametrize('kernel_endianness, system_byteorder, expected', [
        ('little', 'big', [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE '
                           '(little endian) binary format.'),
            (logging.WARNING, '-- NAIF strongly recommends to use BIG-IEEE (big '
                              'endian) for binary kernels in PDS3 archives '),
            (logging.WARNING, '   and enforces it if the archive is hosted by '
                              'NAIF.'),
            (logging.WARNING, '   Your system is BIG-IEEE (big endian): PDS3 '
                              'Labels cannot be attached to binary kernels.'),
            (logging.WARNING, '   If binary kernels are present this will result'
                              ' in an error.')]),
        ('big', 'little', [
            (logging.INFO, '-- Binary SPICE kernels expected to have BIG-IEEE '
                           '(big endian) binary format.'),
            (logging.WARNING, '   Your system is LTL-IEEE (little endian): PDS3 '
                              'Labels cannot be attached to binary kernels.'),
            (logging.WARNING, '   If binary kernels are present this will result '
                              'in an error.')]),
        ('little', 'little', [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE '
                           '(little endian) binary format.'),
            (logging.WARNING, '-- NAIF strongly recommends to use BIG-IEEE (big '
                              'endian) for binary kernels in PDS3 archives '),
            (logging.WARNING, '   and enforces it if the archive is hosted by '
                              'NAIF.'), ]),
        ('big', 'big', [
            (logging.INFO, '-- Binary SPICE kernels expected to have BIG-IEEE '
                           '(big endian) binary format.')])])
    def test_logs_pds3_endianness_recommendations(self, tmp_path, monkeypatch,
                                                  caplog, kernel_endianness,
                                                  system_byteorder, expected) -> None:

        # Build a setup with PDS3 and set the endianness attribute.
        setup = self.make_check_setup(tmp_path, pds_version='3')
        setup.kernel_endianness = kernel_endianness

        # Mock the system's endianness.
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.sys.byteorder',
                            system_byteorder)

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected.append((logging.INFO, f'-- Label templates directory: '
                                       f'{setup.root_dir}templates/pds3'))

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_logs_check_configuration_warnings_separately(self, tmp_path,
                                                          caplog) -> None:

        # Create an invalid template to trigger an XML tab warning.
        root_dir = self.make_templates_root(tmp_path, versions=(im_version(10, 11, 12, 13),),
                                            bundle_template='<No_Identification_Area>\n')

        setup = self.make_check_setup(tmp_path, root_dir=root_dir)

        # Force teh warnings.
        setup.date_format = 'infomod2'
        setup.end_of_line = 'CRLF'
        setup.kernel_endianness = 'big'
        setup.kernel_list_config = {'FK': {}, 'spk': {}, 'SCLK': {}}

        # Minimal readme configuration.
        setup.readme = {'input': str(tmp_path / 'missing_readme.txt'),
                        'cognisant_authority': 'NAIF',
                        'overview': 'Generated readme'}

        # Delete the existing readme file to activate its validation branch.
        os.remove(tmp_path / 'bundle' / 'maven_spice' / 'readme.txt')

        # Remove the meta-kernel configuration to force a warning.
        del setup.mk

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.WARNING, '-- NAIF recommends to use `LF\' End-of-Line while'
                              ' using the `infomod2\' parameter instead of `CRLF\'.'),
            (logging.INFO, '-- Binary SPICE kernels expected to have BIG-IEEE '
                           '(little endian) binary format.'),
            (logging.WARNING, '-- NAIF strongly recommends to use LTL-IEEE (little'
                              ' endian) for binary kernels in PDS4 archives '),
            (logging.WARNING, '   and enforces it if the archive is hosted by NAIF.'),
            (logging.INFO, '-- Label templates will use the ones from information '
                           'model 10.11.12.13.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}'),
            (logging.WARNING, '-- XML Template not useful to determine XML Tab. '
                              'It has been set to 2.'),
            (logging.WARNING, '-- There is no meta-kernel configuration to check.'),
            (logging.WARNING, 'Input readme file not present. File will be '
                              'generated from configuration.'),
            (logging.WARNING, '-- Kernel list configuration has entries with '
                              'uppercase letters:'),
            (logging.WARNING, '      FK'),
            (logging.WARNING, '      SCLK'),
            (logging.WARNING, '   Uppercase letters in kernel names are HIGHLY '
                              'discouraged. ')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_logs_maklabel_end_of_line_recommendation(self, tmp_path, caplog) -> None:

        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Maklabel, requires CRLF, so this should trigger a warning.
        setup.end_of_line = 'LF'

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.WARNING, '-- NAIF recommends to use `CRLF\' End-of-Line '
                              'while using the `maklabel\' parameter instead of `LF\'.'),
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE '
                           '(little endian) binary format.'),
            (logging.INFO, '-- Label templates will use the ones from information'
                           ' model 10.11.12.13.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_allows_single_meta_kernel_pattern_dictionary(self, tmp_path, caplog) -> None:

        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Set a mk as a dictionary.
        setup.mk = [{'@name': 'maven_$version.tm',
                     'name': [{'pattern': {'#text': 'version'}}]}]

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.check_configuration()

        expected = [
            (logging.INFO, '-- Binary SPICE kernels expected to have LTL-IEEE'
                           ' (little endian) binary format.'),
            (logging.INFO, '-- Label templates will use the ones from information'
                           ' model 10.11.12.13.'),
            (logging.INFO, f'-- Label templates directory: {setup.working_directory}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        # This is a valid configuration, so there should be no WARNING or ERROR logging messages.
        assert results == expected

    @pytest.mark.parametrize('mk, expected_message', [
        ([{'@name': 'maven_$version.tm',
           'name': [{'pattern': {'#text': 'release'}}]}],
         'The meta-kernel pattern release is not provided\\.'),
        ([{'@name': 'maven_$version_$release.tm',
           'name': [{'pattern': {'#text': 'version'}}]}],
         'The MK patterns maven_\\$version_\\$release\\.tm do not correspond '
         'to the present MKs\\.')])
    def test_raises_when_meta_kernel_patterns_are_inconsistent(self, tmp_path,
                                                               mk, expected_message) -> None:

        # Build a setup with an invalid mk configuration.
        setup = self.make_check_setup(tmp_path)
        setup.mk = mk

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=expected_message):
            setup.check_configuration()

    @pytest.mark.parametrize('readme, create_input_file, expected_message', [
        ({'input': 'missing_readme.txt'}, False,
         'Readme elements not present in configuration file\\.'),
        ({'input': 'missing_readme.txt', 'cognisant_authority': 'NAIF'}, False,
         'Readme elements not present in configuration file\\.'),
        ({'cognisant_authority': 'NAIF', 'overview': 'Generated readme'}, False,
         None),
        ({'input': 'input_readme.txt'}, True, None)])
    def test_validates_readme_configuration_when_bundle_readme_is_missing(
            self, tmp_path, readme, create_input_file, expected_message) -> None:

        # Build a setup with two incomplete readmes.
        setup = self.make_check_setup(tmp_path)

        # Remove the current readme to activate the validation.
        os.remove(tmp_path / 'bundle' / 'maven_spice' / 'readme.txt')

        if create_input_file:
            input_readme = tmp_path / readme['input']
            input_readme.write_text('input readme\n', encoding='utf-8')
            readme = {'input': str(input_readme)}

        setup.readme = readme

        # In case of readme cannot be found or generated, this behaviour will be
        # handled by handle_npb_error, which will raise a RuntimeError. Also,
        # checks the returned message.
        if expected_message:

            with pytest.raises(RuntimeError, match='Readme elements not present in '
                                                   'configuration file\\.'):
                setup.check_configuration()

        # In case of readme can be created, check that the method completed
        # successfully.
        else:
            setup.check_configuration()
            assert setup.xml_tab == 4

    def test_raises_when_readme_section_is_missing(self, tmp_path) -> None:

        # Build a setup.
        setup = self.make_check_setup(tmp_path)

        # Remove the current readme and its configuration.
        os.remove(tmp_path / 'bundle' / 'maven_spice' / 'readme.txt')

        if hasattr(setup, 'readme'):
            del setup.readme

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match='Readme elements not present in '
                                               'configuration file\\.'):
            setup.check_configuration()


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

        # Check the logging level and logging messages.
        expected = [
            (logging.INFO, '-- Checking existence of previous release.'),
            (logging.WARNING, '-- Bundle label not found. Checking previous kernel list.'),
            (logging.INFO, '-- Generating release 012'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_logs_expected_messages_when_kernel_list_is_provided_as_argument(
            self, tmp_path, monkeypatch, caplog) -> None:
        # When args.kerlist is provided, check the logging messages are
        # correct.

        setup = self.make_release_setup(tmp_path, pds_version='4',
                                        kerlist='input.kernel_list')

        # Mock the glob.glob() call to reach the second 'try' (the first search fail).
        monkeypatch.setattr('pds.naif_pds4_bundler.classes.setup.glob.glob',
                            Mock(return_value=[]))

        with caplog.at_level(logging.INFO):
            setup.set_release()

        # Check the logging level and logging messages.
        expected = [(logging.INFO, '-- Checking existence of previous release.'),
                    (logging.WARNING, '-- Bundle label not found. Checking previous kernel list.'),
                    (logging.WARNING, '-- Kernel list provided as input. Release number cannot be obtained.'),
                    (logging.WARNING, '-- This is the first release.'),
                    (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

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

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            setup.set_release()

        expected = [(logging.INFO, '-- Checking existence of previous release.'),
                    (logging.WARNING, '-- This is the first release.'),
                    (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected


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
