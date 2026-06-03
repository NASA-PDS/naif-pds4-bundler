"""Tests for KernelList class."""
import os.path
from datetime import datetime as real_datetime
import logging
from pathlib import Path
import re
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


def make_kernel_list_setup(tmp_path, **overrides) -> SimpleNamespace:
    # Create a minimal setup object to instance KernelList.
    setup = SimpleNamespace()

    setup.observer = 'MAVEN'
    setup.producer_name = 'NAIF'
    setup.pds_version = '4'
    setup.pds3_mission_template = {'DATA_SET_ID': 'MAVEN-SPICE-KERNELS-V1.0'}
    setup.volume_id = 'MAVEN_1001'
    setup.release = '3'
    setup.release_date = '2026-05-04'
    setup.templates_directory = str(tmp_path / 'templates')

    # Attribute to check a real call, instead of a mock.
    setup.kernel_list_config = {}

    for key, value in overrides.items():
        setattr(setup, key, value)

    return setup


class TestKernelListInit:

    @pytest.fixture(autouse=True)
    def patch_datetime_and_read_config(self, mocker):
        # Helper that runs automatically before each test to mock the calls to
        # datetime.datetime.now() and KernelList.read_config().

        # Mock datetime.now to set a static date to run the tests.
        mock_dt = mocker.patch('pds.naif_pds4_bundler.classes.list.datetime.datetime')
        mock_dt.now.return_value = real_datetime(2026, 5, 4, 12, 30, 0)

    @pytest.mark.parametrize(['pds_version', 'dataset_i', 'dataset_o', 'volid_i', 'volid_o'], [
        ('4', None, 'N/A', None, 'N/A'),
        ('3', '"maven-spice-kernels-v1.0"', 'MAVEN-SPICE-KERNELS-V1.0', 'maven_1001', 'maven_1001'),
        ('3', 'maven-spice-kernels-v1.0', 'MAVEN-SPICE-KERNELS-V1.0', 'maven_1001', 'maven_1001'),
        ('3', '"MAVEN-SPICE-KERNELS-V1.0"', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN_1001', 'maven_1001'),
        ('3', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN_1001', 'maven_1001')])
    def test__init__(self, mocker, tmp_path, pds_version, dataset_i,
                     dataset_o, volid_i, volid_o) -> None:
        # Mock KernelList.read_config. It only affects this test, not the whole
        # class.
        read_config_mock = mocker.patch.object(KernelList, 'read_config',
                                               autospec=True)

        # Build a setup with input values.
        setup = make_kernel_list_setup(tmp_path, pds_version=pds_version,
                                       pds3_mission_template={'DATA_SET_ID': dataset_i},
                                       volume_id=volid_i, release='3')

        kernel_list = KernelList(setup)

        # Check that the arguments are correct.
        assert kernel_list.complete_list == ''
        assert kernel_list.files == []
        assert kernel_list.kernel_list == []
        assert kernel_list.list_name == ''
        assert kernel_list.setup is setup

        assert kernel_list.CURRENTDATE == '2026-05-04'
        assert kernel_list.OBS == 'MAVEN'
        assert kernel_list.AUTHOR == 'NAIF'

        assert kernel_list.DATA_SET_ID == dataset_o
        assert kernel_list.VOLID == volid_o

        assert kernel_list.RELID == '0003'
        assert kernel_list.RELDATE == '2026-05-04'
        assert (
                kernel_list.template ==
                f'{setup.templates_directory}/template_kernel_list.txt'
        )

        read_config_mock.assert_called_once_with(kernel_list)

    def test__init__calls_real_read_config(self, mocker, tmp_path) -> None:
        # This test check that  __init__ method calls a real read_config
        # execution.

        # Simulate a kernel_list_config. This is the configuration that
        # read_config will read
        json_config = {
            r'.*\.bsp$': {'description': 'SPK kernels'},  # Take any name ending in .bsp
            r'^maven_.*\.tm$': {'description': 'Meta-kernels',  # Strings that begin with “maven_” and end with “.tm”.
                                'mklabel_options': 'META'}}

        # Literal representation expected from read_config after formatting the
        # json_config above.
        expected_json_formatted_lst = ['{',
                                       '  ".*\\\\.bsp$": {',
                                       '    "description": "SPK kernels"',
                                       '  },',
                                       '  "^maven_.*\\\\.tm$": {',
                                       '    "description": "Meta-kernels",',
                                       '    "mklabel_options": "META"',
                                       '  }',
                                       '}']

        # Build a setup object for a KernelList.
        setup = make_kernel_list_setup(tmp_path, kernel_list_config=json_config)

        # We use a spy to monitor the call, but allow the actual method to run.
        # This way, we generate a 'real' workflow using a real read_config call.
        read_config_spy = mocker.spy(KernelList, 'read_config')

        # Build a real instance of KernelList.
        kernel_list = KernelList(setup)

        read_config_spy.assert_called_once_with(kernel_list)

        # Check that read_config has saved the original configuration.
        assert kernel_list.json_config is json_config

        # Check that the list of compiled regular expressions is stored in two
        # places and that both point to the same object.
        assert kernel_list.re_config is setup.re_config

        # check that the two expected regular expressions have been compiled and
        # are in the correct order.
        assert [pattern.pattern for pattern in kernel_list.re_config] == [r'.*\.bsp$',
                                                                          r'^maven_.*\.tm$']

        # Check that the regular expressions work.
        assert kernel_list.re_config[0].match('maven_001.bsp')
        assert not kernel_list.re_config[0].match('maven_001.tsc')
        assert kernel_list.re_config[1].match('maven_release_03.tm')
        assert not kernel_list.re_config[1].match('release_03.tm')

        # Check that read_config has correctly generated the formatted
        # representation of the JSON.
        assert kernel_list.json_formatted_lst == expected_json_formatted_lst


class TestKernelListReadConfig:

    @staticmethod
    def make_kernel_list_without_init(setup) -> KernelList:
        # Build a KernelList instance without calling __init__. In this way, we
        # can create an empty instance to which we will then assign the values
        # from read_config.
        kernel_list = KernelList.__new__(KernelList)

        # The setup attribute is assigned manually.
        kernel_list.setup = setup

        return kernel_list

    @pytest.mark.parametrize('json_config, match_checks, expected_json_formatted_lst', [
        ({}, [], ['{}']),
        ({r'.*\.bsp$': {'description': 'SPK kernels'}},
         [(0, 'maven_001.bsp', True),
          (0, 'maven_001.tsc', False)],
         ['{',
          '  ".*\\\\.bsp$": {',
          '    "description": "SPK kernels"',
          '  }',
          '}']),
        ({r'.*\.bsp$': {'description': 'SPK kernels'},
          r'^maven_.*\.tm$': {'description': 'Meta-kernels', 'mklabel_options': 'META'},
          r'orbnum_[0-9]{5}\.orb$': {'description': 'Orbnum files'}},
         [(0, 'maven_001.bsp', True),
          (0, 'maven_001.bc', False),
          (1, 'maven_release_03.tm', True),
          (1, 'release_03.tm', False),
          (2, 'orbnum_00042.orb', True),
          (2, 'orbnum_42.orb', False)],
         ['{',
          '  ".*\\\\.bsp$": {',
          '    "description": "SPK kernels"',
          '  },',
          '  "^maven_.*\\\\.tm$": {',
          '    "description": "Meta-kernels",',
          '    "mklabel_options": "META"',
          '  },',
          '  "orbnum_[0-9]{5}\\\\.orb$": {',
          '    "description": "Orbnum files"',
          '  }',
          '}'])])
    def test_read_config_stores_compiled_regexes_and_formatted_json(
            self, tmp_path, json_config, match_checks, expected_json_formatted_lst) -> None:
        # Build a setup with the parametrized kernel-list configuration.
        setup = make_kernel_list_setup(tmp_path, kernel_list_config=json_config)

        kernel_list = self.make_kernel_list_without_init(setup)

        kernel_list.read_config()

        # The original JSON config is not copied or transformed.
        assert kernel_list.json_config is json_config

        # Every key in the JSON config is compiled as a regex, preserving the
        # insertion order of the configuration.
        assert len(kernel_list.re_config) == len(json_config)

        assert [pattern.pattern
                for pattern in kernel_list.re_config] == list(json_config)

        assert all(isinstance(pattern, re.Pattern)
                   for pattern in kernel_list.re_config)

        # Also exposes the same compiled regex list through setup. This is
        # important because other code consumes setup.re_config later.
        assert kernel_list.setup.re_config is kernel_list.re_config

        # The method read_config must create the pretty-printed JSON
        # representation used later when logging or displaying the kernel list
        # configuration.
        assert (kernel_list.json_formatted_lst == expected_json_formatted_lst)

        # Prove that the compiled regexes are functional.
        for pattern_index, candidate, expected_result in match_checks:
            assert (bool(kernel_list.re_config[pattern_index].match(candidate))
                    is expected_result)

    @pytest.mark.parametrize('invalid_pattern', [
        {'[': {'description': 'Invalid regex'}},
        {'(?P<kernel>': {'description': 'Invalid regex'}}])
    def test_read_config_raises_re_error_for_invalid_regex(self, tmp_path,
                                                           invalid_pattern) -> None:
        # This test highlights a bug in the code, as if read_config receives an
        # invalid regex, it triggers a re.error, causing the code to crash.

        # Build a setup object with an invalid regex.
        setup = make_kernel_list_setup(tmp_path, kernel_list_config=invalid_pattern)

        # Build KernelList without running __init__, so read_config may be
        # called with an invalid regular expression and cause an error.
        kernel_list = self.make_kernel_list_without_init(setup)

        # Invalid regex patterns must raise re.error when read_config calls
        # re.compile(pattern).
        with pytest.raises(re.error):
            kernel_list.read_config()

        # The method assigns public state only after compiling all patterns.
        # Therefore, when compilation fails, no partial state should be exposed.
        assert not hasattr(kernel_list, 're_config')
        assert not hasattr(kernel_list.setup, 're_config')
        assert not hasattr(kernel_list, 'json_config')
        assert not hasattr(kernel_list, 'json_formatted_lst')

    def test_read_config_raises_attribute_error_when_setup_has_no_config(self) -> None:
        # This test is irrelevant in the NPB environment because, due to its
        # implementation, it will always have a valid kernel_list (even if it is
        # an empty dictionary).
        # We are retaining the test so that we can carry out future checks and
        # thus strictly maintain the purpose of the unit test, for example, in
        # the event that different setups can be provided.

        # Build KernelList without running __init__. This means that
        # read_config is not called automatically
        kernel_list = KernelList.__new__(KernelList)

        # Assign an empty setup.
        kernel_list.setup = SimpleNamespace()

        # An error raises when read_config try to access to the empty setup.
        with pytest.raises(AttributeError):
            kernel_list.read_config()

        # As an error occurs, no partial state should be exposed.
        assert not hasattr(kernel_list, 're_config')
        assert not hasattr(kernel_list.setup, 're_config')
        assert not hasattr(kernel_list, 'json_config')
        assert not hasattr(kernel_list, 'json_formatted_lst')


class TestKernelListWriteList:

    @staticmethod
    def patch_write_list_file_and_validation_boundaries(
            mocker, template_content='TEMPLATE HEADER\n') -> SimpleNamespace:
        # Only patch boundaries outside write_list's own logic: template/file
        # creation and the final validation workflow required to be mocked.
        def fake_fill_template(_kernel_list, output_path, _list_dictionary) -> None:
            # Fake fill_template: create the file that write_list will append
            # to. Keep the same signature as the real function.
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write(template_content)

        fill_template_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.fill_template',
            side_effect=fake_fill_template)

        validate_mock = mocker.patch.object(KernelList, 'validate',
                                            autospec=True)

        return SimpleNamespace(fill_template=fill_template_mock,
                               validate=validate_mock)

    @staticmethod
    def make_kernel_list(tmp_path, kernel_list_config, kernels,
                         **setup_overrides) -> tuple[KernelList, SimpleNamespace, Path]:
        # Build a real KernelList with a minimal temporary setup. This keeps
        # each test focused on write_list while avoiding repeated setup code.
        working_directory = tmp_path / 'working'
        kernels_directory = tmp_path / 'kernels'

        working_directory.mkdir(exist_ok=True)
        kernels_directory.mkdir(exist_ok=True)

        setup = make_kernel_list_setup(tmp_path,
                                       mission_acronym='maven',
                                       run_type='release',
                                       working_directory=str(working_directory),
                                       kernels_directory=[str(kernels_directory)],
                                       kernel_list_config=kernel_list_config,
                                       **setup_overrides)

        kernel_list = KernelList(setup)
        kernel_list.kernel_list = kernels

        output_path = working_directory / 'maven_release_03.kernel_list'

        return kernel_list, setup, output_path

    def test_write_list_accepts_empty_kernel_list_and_only_writes_template(
            self, mocker, tmp_path) -> None:
        # Check the case when kernel_list is empty.

        # Prepare the needed mocks. The fake template is intentionally empty to
        # prove that write_list does not add anything when there are no kernels.
        mocks = self.patch_write_list_file_and_validation_boundaries(
            mocker, template_content='')

        # Build a real KernelList with an empty kernels attribute.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path,
                                                            kernel_list_config={},
                                                            kernels=[])

        kernel_list.write_list()

        # Check the exact contents of the generated file.
        #
        # The file should only contain the header written by the fake
        # fill_template.
        #
        # This proves two things:
        #   - fill_template created the file.
        #   - write_list did not add any entries because there were no kernels.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == ''

        # Check that write_list updates the list_name attribute correctly.
        assert kernel_list.list_name == 'maven_release_03.kernel_list'

        # Check that fill_template has been called only once and that the call
        # was successful.
        mocks.fill_template.assert_called_once()
        fill_template_args = mocks.fill_template.call_args.args

        # Check the arguments
        assert fill_template_args[0] is kernel_list
        assert fill_template_args[1] == str(output_path)
        assert fill_template_args[2] is kernel_list.__dict__

        # Check the validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    def test_write_list_writes_configured_fallback_and_side_effects(
            self, mocker, tmp_path) -> None:

        # Build the needed mocks (fill_template and validate).
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Define the kernel with a correct configuration.
        kernel = 'maven_orbit_v01.bsp'
        kernel_type = 'spk'

        kernel_list_config = {
            r'^maven_orbit_v01\.bsp$': {
                'description': '  MAVEN\n orbit    SPK  ',
                'patterns': {
                    'UNUSED': {'@value': 'unused',
                               '#text': 'SHOULD_NOT_APPEAR'}}}}

        # Create a real instance of KernelList with two kernels:
        #   - One with a corrct configuration.
        #   - Other: a kernel that does not appear in kernel_list_config
        #   (processed via fallback branch).
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=['orbn_00001.orb', kernel])

        kernel_list.write_list()

        # Check the file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            'FILE             = miscellaneous/orbnum/orbn_00001.orb\n'
            'MAKLABEL_OPTIONS = N/A\n'
            'DESCRIPTION      = N/A\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS =\n'
            'DESCRIPTION      = MAVEN orbit SPK\n')

        # Check the side effect; after writing the file, write_list must return:
        #   self.list_name = list_name
        assert kernel_list.list_name == 'maven_release_03.kernel_list'

        # Check teh validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    def test_write_list_uses_pds3_data_directory_when_configured(
            self, mocker, tmp_path) -> None:
        # This test verify that PDS3 output uses data/<type>/<kernel> for
        # configured kernels.

        # Configure the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Define the kernel value to test.
        kernel = 'maven_fk_v01.ti'
        kernel_type = 'ik'

        kernel_list_config = {
            r'^maven_fk_v01\.ti$': {'description': 'Instrument kernel',
                                    'mklabel_options': 'IK'}}

        # Build a real instance of KernelList for PDS3.
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel],
            pds_version='3')

        kernel_list.write_list()

        # Check the file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            f'FILE             = data/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS = IK\n'
            'DESCRIPTION      = Instrument kernel\n'
        )

        # Check the validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    @pytest.mark.parametrize('phases, expected_options', [
        (None, 'PHASE N/A'),
        ({'phase': {'@name': 'CRUISE'}}, 'PHASE CRUISE'),
        ({False: {}, 'phase': {'@name': 'IGNORED'}}, 'PHASE N/A')])
    def test_write_list_replaces_phase_option(
            self, mocker, tmp_path, phases, expected_options) -> None:
        # This test, verify all $PHASES substitutions in mklabel_options.

        # Configure the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Define the kernel value to test.
        kernel = 'maven_release_03.tm'
        kernel_type = 'mk'

        # Preapre the extra attributes for setup.
        setup_overrides = {}
        if phases is not None:
            setup_overrides['phases'] = phases

        # Define a kernel configuration.Since it has the value of
        # mklabel_options, it is included in the $PHASES substitution logic.
        kernel_list_config = {
            r'^maven_release_03\.tm$': {'description': 'Meta kernel',
                                        'mklabel_options': 'PHASE $PHASES'}}

        # Build a real KernelList.
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel],
            **setup_overrides)

        kernel_list.write_list()

        # Check the file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            f'MAKLABEL_OPTIONS = {expected_options}\n'
            'DESCRIPTION      = Meta kernel\n')

        # Check the validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    @pytest.mark.parametrize('pattern_type, kernel, mapping, expected_value, expected_mapping_line', [
        ('kernel', 'maven_v01.bsp', '', 'v01', ''),
        ('KERNEL',
         'maven_ab12.bsp',
         'mapped_$VERSION.bc',
         'AB12',
         'MAPPING          = mapped_AB12.bc\n')])
    def test_write_list_replaces_kernel_pattern_from_filename(
            self, mocker, tmp_path, pattern_type, kernel, mapping,
            expected_value, expected_mapping_line) -> None:
        # This test verify $VERSION extraction from the filename and its
        # replacement in description and optional mapping.

        # Configure the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        kernel_type = 'spk'
        escaped_kernel = re.escape(kernel)

        config_value = {
            'description': 'Version $VERSION kernel',
            'mklabel_options': 'SPK',
            'patterns': {'VERSION': {'@pattern': pattern_type,
                                     '#text': 'maven_$VERSION.bsp'}}}

        if mapping:
            config_value['mapping'] = mapping

        kernel_list_config = {fr'^{escaped_kernel}$': config_value}

        # Build a real instance of KernelList.
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel])

        kernel_list.write_list()

        # Check the file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS = SPK\n'
            f'DESCRIPTION      = Version {expected_value} kernel\n'
            f'{expected_mapping_line}')

        # Check the validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    def test_write_list_replaces_comment_pattern_from_kernel_comment(
            self, mocker, tmp_path) -> None:
        # This test, reads the kernel comment through extract_comment and use
        # the matching line as replacement in description.

        # Build the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Define the kernel to be processed.
        kernel = 'maven_kernel_v01.bc'
        kernel_type = 'ck'

        # Mock the extract_comment call.
        extract_comment_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.extract_comment',
            return_value=['unrelated comment line',
                          '  ORIGINAL_NAME = maven_old_kernel.bc  '])

        # Kernel configuration.
        kernel_list_config = {
            r'^maven_kernel_v01\.bc$': {
                'description': 'Original kernel: $ORIGINAL',
                'patterns': {'ORIGINAL': {'@file': 'comment',
                                          '#text': 'ORIGINAL_NAME'}}}}

        # Build a real KernelList instance.
        kernel_list, setup, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel])

        kernel_list.write_list()

        # Check the extract_comment call.
        extract_comment_mock.assert_called_once_with(
            f'{setup.kernels_directory[0]}/{kernel_type}/{kernel}')

        # Check file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS =\n'
            'DESCRIPTION      = Original kernel: ORIGINAL_NAME = maven_old_kernel.bc\n')

        # Check validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    @pytest.mark.parametrize('patterns_el, kernel, expected_description', [
        ({'@value': 'edr', '#text': 'EDR'},
         'maven_edr_index.bsp',
         'Level EDR'),
        ([{'@value': 'raw', '#text': 'RAW'},
          {'@value': 'rdr', '#text': 'RDR'}],
         'maven_rdr_index.bsp',
         'Level RDR')])
    def test_write_list_replaces_configured_value_pattern(
            self, mocker, tmp_path, patterns_el, kernel,
            expected_description) -> None:
        # This test, verify that $LEVEL is resolved from @value/#text
        # configuration rules.

        # Prepare the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Define the kernel to be processed.
        kernel_type = 'spk'
        escaped_kernel = re.escape(kernel)

        kernel_list_config = {fr'^{escaped_kernel}$': {'description': 'Level $LEVEL',
                                                       'patterns': {'LEVEL': patterns_el}}}

        # Build a KernelList.
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel])

        kernel_list.write_list()

        # Check file content.
        assert output_path.read_text(encoding='utf-8') == (
            'TEMPLATE HEADER\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS =\n'
            f'DESCRIPTION      = {expected_description}\n')

        # Check validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    def test_write_list_logs_mapping_separately_from_side_effects(
            self, mocker, caplog, tmp_path) -> None:
        # This test intentionally checks logging only. File content side effects
        # are asserted by the other tests.

        # Build the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        # Configure a minimum configuration to force the mapping branch.
        kernel_list_config = {r'^maven_kernel_v01\.bc$': {'description': 'CK kernel',
                                                          'mapping': 'mapped_kernel_v01.bc'}}

        # Build a real KernelList instance.
        kernel_list, _, _ = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=['maven_kernel_v01.bc'])

        # Check the logging level and logging messages.
        with caplog.at_level(logging.INFO):
            kernel_list.write_list()

        expected = [(logging.INFO, '-- Mapping maven_kernel_v01.bc with mapped_kernel_v01.bc')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert expected == results

        # Check validate call.
        mocks.validate.assert_called_once_with(kernel_list)

    @pytest.mark.parametrize('kernel_list_config, kernels, comment_lines, expected_error', [
        ({r'^maven_v01_v02\.bsp$': {
            'description': 'Version $VERSION',
            'patterns': {'VERSION': {'@pattern': 'kernel',
                                     '#text': 'maven_$VERSION_$VERSION.bsp'}}}},
         ['maven_v01_v02.bsp'],
         None,
         'Kernel pattern for maven_v01_v02.bsp not adept to write description.'),
        ({r'^maven_kernel_v01\.bc$': {
            'description': 'Original $ORIGINAL',
            'patterns': {'ORIGINAL': {'@file': 'comment',
                                      '#text': 'ORIGINAL_NAME'}}}},
         ['maven_kernel_v01.bc'],
         ['comment without the required marker'],
         'Kernel pattern not found in comment area of maven_kernel_v01.bc.'),
        ({r'^maven_level\.tab$': {
            'description': 'Level $LEVEL',
            'patterns': {'LEVEL': {'#text': 'SCI'}}}},
         ['maven_level.tab'],
         None,
         'Error generating kernel list with maven_level.tab.'),
        ({r'^maven_level\.tab$': {
            'description': 'Level $LEVEL',
            'patterns': {'LEVEL': {'@value': 'not-present-in-kernel-name',
                                   '#text': 'SCI'}}}},
         ['maven_level.tab'],
         None,
         '-- Kernel maven_level.tab description could not be updated with pattern.'),
        ({r'^maven_level\.tab$': {
            'description': 'Level $LEVEL',
            'patterns': {'LEVEL': [{'@value': 'not-present-in-kernel-name',
                                    '#text': 'SCI'}]}}},
         ['maven_level.tab'],
         None,
         '-- Kernel maven_level.tab description could not be updated with pattern.')])
    def test_write_list_reports_invalid_pattern_configurations(
            self, mocker, tmp_path, kernel_list_config, kernels, comment_lines,
            expected_error) -> None:

        # Build the needed mocks.
        mocks = self.patch_write_list_file_and_validation_boundaries(mocker)

        if comment_lines is not None:
            mocker.patch(
                'pds.naif_pds4_bundler.classes.list.extract_comment',
                return_value=comment_lines)

        # Create a real KernelList instance with an invalid configuration.
        kernel_list, _, _ = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=kernels)

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=expected_error):
            kernel_list.write_list()

        # Check the validate call.
        mocks.validate.assert_not_called()
        assert kernel_list.list_name == ''

    def test_write_list_uses_real_fill_template_to_create_output_file(
            self, mocker, tmp_path) -> None:
        # Verify write_list with real fill_template: template content is written first,
        # then the configured kernel entry is appended.

        # Mock only validate because the test scope requires write_list to
        # trigger validation, not to execute the full validation workflow.
        validate_mock = mocker.patch.object(KernelList, 'validate',
                                            autospec=True)

        # Create the real template file used by KernelList.__init__.
        templates_directory = tmp_path / 'templates'
        templates_directory.mkdir()
        template = templates_directory / 'template_kernel_list.txt'
        template.write_text('REAL TEMPLATE HEADER\n', encoding='utf-8')

        # Define a configured kernel.
        kernel = 'maven_orbit_v01.bsp'
        kernel_type = 'spk'

        kernel_list_config = {r'^maven_orbit_v01\.bsp$': {'description': 'Orbit kernel',
                                                          'mklabel_options': 'SPK'}}

        # Build a real KernelList pointing to the real template directory.
        kernel_list, _, output_path = self.make_kernel_list(
            tmp_path,
            kernel_list_config=kernel_list_config,
            kernels=[kernel],
            templates_directory=str(templates_directory))

        kernel_list.write_list()

        # Check that the real template content is preserved and write_list
        # appends the kernel-list entry after it.
        assert output_path.read_text(encoding='utf-8') == (
            'REAL TEMPLATE HEADER\n'
            f'FILE             = spice_kernels/{kernel_type}/{kernel}\n'
            'MAKLABEL_OPTIONS = SPK\n'
            'DESCRIPTION      = Orbit kernel\n')

        # Check the side effect over the object; write_list should assign
        # self.list_name = list_name
        assert kernel_list.list_name == 'maven_release_03.kernel_list'

        # Check the validate call.
        validate_mock.assert_called_once_with(kernel_list)


class TestKernelListReadList:

    @staticmethod
    def make_kernel_list(tmp_path, **setup_overrides) -> tuple[KernelList, SimpleNamespace, Path]:
        # Build a real KernelList instance with the minimum temporary setup required by
        # read_list. The helper centralizes the working-directory and expected output
        # path creation so each test can focus only on read_list behaviour.

        # Build the temporary directory that will serve as the setup.working_directory.
        working_directory = tmp_path / 'working'
        working_directory.mkdir(exist_ok=True)

        # Build a minimal setup instance.
        setup = make_kernel_list_setup(tmp_path,
                                       mission_acronym='maven',
                                       run_type='release',
                                       working_directory=str(working_directory),
                                       kernel_list_config={},
                                       **setup_overrides)

        # Build a real KernelList instance.
        kernel_list = KernelList(setup)

        # Calculate the file that we expect read_list() to use internally.
        output_path = working_directory / 'maven_release_03.kernel_list'

        return kernel_list, setup, output_path

    def test_read_list_copies_source_file_extracts_kernels_and_validates(
            self, mocker, caplog, tmp_path) -> None:
        # Verify the normal read_list workflow: copy an external kernel list
        # into the canonical working-directory path, extract only kernel names
        # from FILE entries, update public state and trigger validation once.

        # Mock the validate call, as that is not the purpose of this test.
        validate_mock = mocker.patch.object(KernelList, 'validate', autospec=True)

        # Build a real KernelList instance.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Create the path to the input file. This will be the external kernel list passed to read_list().
        source_path = tmp_path / 'input.kernel_list'

        # Define the file content.
        content = ('KERNEL LIST HEADER\n'
                   f'FILE             = {os.path.join("spice_kernels", "spk", "maven_orbit_v01.bsp")}\n'
                   'MAKLABEL_OPTIONS = SPK\n'
                   'DESCRIPTION      = Orbit kernel\n'
                   'COMMENT          = This line must be ignored by read_list.\n'
                   f'FILE             = {os.path.join("spice_kernels", "ck", "maven_attitude_v02.bc")}\n'
                   'MAKLABEL_OPTIONS = CK\n'
                   'DESCRIPTION      = Attitude kernel\n')

        # Writes the input file to disk. This means that the test uses actual
        # I/O, which makes sense here because read_list() works directly with
        # files using shutil.copy2() and open().
        source_path.write_text(content, encoding='utf-8')

        with caplog.at_level(logging.INFO):
            kernel_list.read_list(str(source_path))

        # Check the created file.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == content

        # Check the first side effect: the read_list() function should update
        # self.list_name with the name of the destination file.
        assert kernel_list.list_name == 'maven_release_03.kernel_list'

        # Check the second side effect: read_list() must populate
        # self.kernel_list with the names of the kernels found in the FILE
        # lines.
        assert kernel_list.kernel_list == ['maven_orbit_v01.bsp',
                                           'maven_attitude_v02.bc']

        # validate is mocked, so any captured log would come directly from
        # read_list. The happy path should not emit direct log records.
        assert caplog.record_tuples == []

        # Check that read_list call validate once.
        validate_mock.assert_called_once_with(kernel_list)

    def test_read_list_ignores_same_file_error_and_reads_existing_target(
            self, mocker, tmp_path) -> None:
        # Verify the SameFileError path: when the input list is already the
        # canonical working-directory file, read_list must skip the copy, read
        # the existing file, update state and trigger validation once.

        # Mock the validate call.
        validate_mock = mocker.patch.object(KernelList, 'validate', autospec=True)

        # Build a real KernelList instance.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Define the file content.
        content = ('KERNEL LIST HEADER\n'
                   f'FILE             = {os.path.join("miscellaneous/orbnum", "orbn_00001.orb")}\n'
                   'MAKLABEL_OPTIONS = N/A\n'
                   'DESCRIPTION      = N/A\n')

        # Write the file directly to the destination path that read_list() will
        # use.
        output_path.write_text(content, encoding='utf-8')

        kernel_list.read_list(str(output_path))

        # Check the file.
        assert output_path.read_text(encoding='utf-8') == content

        # Check that read_list() has read the existing file and extracted the
        # kernel name from the FILE line.
        assert kernel_list.list_name == 'maven_release_03.kernel_list'
        assert kernel_list.kernel_list == ['orbn_00001.orb']

        # Check that read_list call validate once.
        validate_mock.assert_called_once_with(kernel_list)

    @pytest.mark.parametrize('content, expected_kernels', [
        ('KERNEL LIST HEADER\n'
         'MAKLABEL_OPTIONS = N/A\n'
         'DESCRIPTION      = N/A\n',
         []),
        (f'FILE             = {os.path.join("spice_kernels", "spk", "maven_orbit_v01.bsp")}\n',
         ['maven_orbit_v01.bsp']),
        ('HEADER\n'
         f'FILE             = {os.path.join("spice_kernels", "fk", "maven_frames_v01.tf")}\n'
         'DESCRIPTION      = Frame kernel\n'
         f'FILE             = {os.path.join("spice_kernels", "sclk", "maven_clock_v02.tsc")}\n'
         'MAKLABEL_OPTIONS = SCLK\n',
         ['maven_frames_v01.tf', 'maven_clock_v02.tsc']),
        (f'FILE             = {os.path.join("spice_kernels", "spk", "maven_orbit_v01.bsp")}',
         ['maven_orbit_v01.bs'])])
    def test_read_list_builds_kernel_list_from_file_entries_only(
            self, mocker, tmp_path, content, expected_kernels) -> None:
        # TODO: The last example demonstrates the bug whereby, if there is no
        #       EOL on the FILE line, the code removes the last character from
        #       the line.

        # Verify read_list parsing rules with several inputs: ignore non-FILE
        # lines, build kernel_list only from FILE entries and preserve the
        # original order.

        # Mock the validate call.
        validate_mock = mocker.patch.object(KernelList, 'validate',
                                            autospec=True)

        # Build a real KernelList instance.
        kernel_list, _, _ = self.make_kernel_list(tmp_path)

        # Build a temporal path for the input file, and write the specified data
        # to disk.
        source_path = tmp_path / 'input.kernel_list'
        source_path.write_text(content, encoding='utf-8')

        kernel_list.read_list(str(source_path))

        assert kernel_list.kernel_list == expected_kernels

        # Check that read_list call validate once.
        validate_mock.assert_called_once_with(kernel_list)

    def test_read_list_propagates_copy_errors_without_partial_side_effects(
            self, mocker, tmp_path) -> None:
        # Verify that copy errors other than SameFileError are propagated and do
        # not leave partial state updates: no output file, no list_name, no
        # kernel_list and no validation call.

        # Build a real KernelList instance.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Define an input path that not exists.
        missing_path = tmp_path / 'missing.kernel_list'

        # Execute the method and capture the exception.
        with pytest.raises(FileNotFoundError):
            kernel_list.read_list(str(missing_path))

        # Check that the destination file has not been created.
        assert not output_path.exists()
        assert kernel_list.list_name == ''
        assert kernel_list.kernel_list == []


class TestKernelListWriteCompleteList:

    @staticmethod
    def make_kernel_list(
            tmp_path, **setup_overrides) -> tuple[KernelList, SimpleNamespace, Path]:
        # Build an isolated working directory for the files created and consumed by
        # write_complete_list
        working_directory = tmp_path / 'working'
        working_directory.mkdir(exist_ok=True)

        # Build the minimum setup required to instantiate KernelList and execute
        # write_complete_list. Any test-specific setup value can be overridden.
        setup = make_kernel_list_setup(tmp_path,
                                       mission_acronym='maven',
                                       working_directory=str(working_directory),
                                       kernel_list_config={},
                                       **setup_overrides)

        # Real KernelList instance.
        kernel_list = KernelList(setup)

        # Expected output path produced by write_complete_list.
        output_path = working_directory / 'maven_complete.kernel_list'

        return kernel_list, setup, output_path

    def test_write_complete_list_merges_release_lists_in_reverse_order_and_validates(
            self, mocker, tmp_path) -> None:
        # Check the happy path: release lists are merged in reverse order, the complete
        # list is regenerated, state is updated and validation is requested.

        # Mock validate_complete call.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Build a real KernelList with a minimal setup and the expected file
        # path.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)
        working_directory = Path(kernel_list.setup.working_directory)

        # Create tree valid release files.
        release_01 = working_directory / 'maven_release_01.kernel_list'
        release_02 = working_directory / 'maven_release_02.kernel_list'
        release_03 = working_directory / 'maven_release_03.kernel_list'

        release_01.write_text('RELEASE 01\n', encoding='utf-8')
        release_02.write_text('RELEASE 02\n', encoding='utf-8')
        release_03.write_text('RELEASE 03\n', encoding='utf-8')

        # Create unrelated files that must be ignored because they do not match the
        # exact release-list glob used by write_complete_list.
        (working_directory / 'maven_label_99.kernel_list').write_text(
            'LABEL\n', encoding='utf-8')
        (working_directory / 'other_release_04.kernel_list').write_text(
            'OTHER\n', encoding='utf-8')

        # Build an old complete_list.
        output_path.write_text('OLD COMPLETE LIST\n', encoding='utf-8')

        kernel_list.write_complete_list()

        # Check the complete list is created and contains the merged release
        # lists in reverse order.
        assert output_path.read_text(encoding='utf-8') == (
            'RELEASE 03\n'
            'RELEASE 02\n'
            'RELEASE 01\n')

        # Check that the method updates the complete_list attribute.
        assert kernel_list.complete_list == 'maven_complete.kernel_list'

        # Check that write_complete_list ultimately requests validation of the
        # complete list, but without executing the actual implementation.
        validate_complete_mock.assert_called_once_with(kernel_list)

    def test_write_complete_list_accepts_no_release_lists(
            self, mocker, tmp_path) -> None:
        # Verify the empty-input path: when no release lists are found, the method still
        # creates an empty complete list, updates state and requests validation.

        # Mock the validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Create a KernelList instance with a temporal and empty working_directory
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        with pytest.raises(ValueError):
            kernel_list.write_complete_list()

        # Check that the file exists and is empty.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == ''

        # Check that the method updates the complete_list even if it is empty.
        assert kernel_list.complete_list == ''

        # Check that check_consecutive and validate_complete called once.
        validate_complete_mock.assert_not_called()

    def test_write_complete_list_logs_added_release_lists(
            self, mocker, caplog, tmp_path) -> None:
        # Verify that write_complete_list logs every release list it adds,
        # using the same reverse order in which the files are processed.

        # Mock validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # In this case, the check_consecutive mock uses return_value=True to
        # avoid a warning.
        mocker.patch('pds.naif_pds4_bundler.classes.list.check_consecutive',
                     return_value=True)

        # Build a real KernelList with a minimal setup and the expected file
        # path.
        kernel_list, _, _ = self.make_kernel_list(tmp_path)

        # Build the files.
        working_directory = Path(kernel_list.setup.working_directory)

        release_01 = working_directory / 'maven_release_01.kernel_list'
        release_02 = working_directory / 'maven_release_02.kernel_list'

        release_01.write_text('RELEASE 01\n', encoding='utf-8')
        release_02.write_text('RELEASE 02\n', encoding='utf-8')

        # Capture the logs.
        with caplog.at_level(logging.INFO):
            kernel_list.write_complete_list()

        expected = [
            (logging.INFO, f'-- Adding {release_02}'),
            (logging.INFO, f'-- Adding {release_01}')]

        results = [(record[1], record[2]) for record in caplog.record_tuples]

        # Check the expected logs.
        assert results == expected

        # Check the validate_complete called once.
        validate_complete_mock.assert_called_once_with(kernel_list)

    def test_write_complete_list_logs_warning_when_releases_are_not_consecutive(
            self, mocker, caplog, tmp_path) -> None:
        # Verify the incomplete-release branch: non-consecutive release lists
        # are still merged, but write_complete_list logs a warning before
        # validation.

        # Mock the validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Build a real KernelList with a minimal setup and the expected file
        # path.
        kernel_list, _, _ = self.make_kernel_list(tmp_path)

        # Build the files.
        working_directory = Path(kernel_list.setup.working_directory)
        release_01 = working_directory / 'maven_release_01.kernel_list'
        release_03 = working_directory / 'maven_release_03.kernel_list'

        release_01.write_text('RELEASE 01\n', encoding='utf-8')
        release_03.write_text('RELEASE 03\n', encoding='utf-8')

        # Capture the logs
        with caplog.at_level(logging.INFO):
            kernel_list.write_complete_list()

        expected = [
            (logging.INFO, f'-- Adding {release_03}'),
            (logging.INFO, f'-- Adding {release_01}'),
            (logging.WARNING, '-- Incomplete Kernel lists available: [3, 1]')]

        results = [(record[1], record[2]) for record in caplog.record_tuples]

        # Check the logs.
        assert results == expected

        # Even if a warning has been issued, the method does not terminate. It
        # continues and requests full validation.
        validate_complete_mock.assert_called_once_with(kernel_list)

    def test_write_complete_list_propagates_invalid_release_number_without_validation(
            self, mocker, tmp_path) -> None:
        # Check that a release-list filename with a non-numeric release token
        # raises before consecutive checks, state update or complete-list
        # validation.

        # Mock the validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Build a real KernelList instance and the expected complete-list path.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Create an invalid file.
        working_directory = Path(kernel_list.setup.working_directory)
        invalid_release = working_directory / 'maven_release_bad.kernel_list'
        invalid_release.write_text('INVALID RELEASE\n', encoding='utf-8')

        # Capture the exception.
        with pytest.raises(ValueError):
            kernel_list.write_complete_list()

        # Check that the file exists and it is empty.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == ''

        # Check that the internal state is not updated.
        assert kernel_list.complete_list == ''

        # Check that validate_complete are not called.
        validate_complete_mock.assert_not_called()

    def test_write_complete_list_propagates_missing_release_file_without_validation(
            self, mocker, tmp_path) -> None:
        # Verify that a release list returned by glob but missing on disk raises
        # before consecutive checks, state update or complete-list validation.

        # Mock the validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Build a real KernelList instance and the expected complete-list path.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # The file is not created, this only builds the path.
        missing_release = (
            Path(kernel_list.setup.working_directory) /
            'maven_release_04.kernel_list')

        # Mock the glob.glob call with the before path to force the exception.
        glob_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.glob.glob',
            return_value=[str(missing_release)])

        # Capture the exception.
        with pytest.raises(FileNotFoundError):
            kernel_list.write_complete_list()

        # Check that the file exists and it is empty.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == ''

        # Check that the internal state is not updated.
        assert kernel_list.complete_list == ''

        # Check the glob call with the expected values.
        glob_mock.assert_called_once_with(
            kernel_list.setup.working_directory
            + os.sep
            + 'maven_release*.kernel_list')

        # Check that validate_complete are not called.
        validate_complete_mock.assert_not_called()

    def test_write_complete_list_propagates_validate_complete_errors_after_side_effects(
            self, mocker, tmp_path) -> None:
        # validate_complete is a boundary here, but write_complete_list must have
        # produced the complete file and updated complete_list before it raises.
        validate_complete_mock = mocker.patch.object(
            KernelList, 'validate_complete', autospec=True,
            side_effect=RuntimeError('complete validation failed'))

        # Build a real KernelList instance and the expected complete-list path.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Build a valid release list.
        release_01 = (
            Path(kernel_list.setup.working_directory) /
            'maven_release_01.kernel_list')
        release_01.write_text('RELEASE 01\n', encoding='utf-8')

        # Capture the exception.
        with pytest.raises(RuntimeError, match='complete validation failed'):
            kernel_list.write_complete_list()

        # Although the method threw an exception, the file has been created.
        assert output_path.read_text(encoding='utf-8') == 'RELEASE 01\n'
        assert kernel_list.complete_list == 'maven_complete.kernel_list'

        # The validate_complete must be called once and its exception
        # propagated.
        validate_complete_mock.assert_called_once_with(kernel_list)
