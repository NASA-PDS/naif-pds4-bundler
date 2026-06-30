"""Tests for KernelList class."""
import os.path
import sys
from datetime import datetime as real_datetime
import logging
from pathlib import Path
import re
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList

# ---------------------------------------------------------------------------
# Constants shared by TestKernelListCheckProducts
# ---------------------------------------------------------------------------

# Message logged and raised as RuntimeError when any product has errors.
_CHECK_FATAL_MESSAGE = 'Products listed above require work.'

# Message logged at INFO and printed to stdout when all checks pass.
_CHECK_SUCCESS_MESSAGE = '-- All products checks have succeeded.'


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

    @pytest.mark.parametrize('kernel', [
        'maven_001.bsp',           # SPK kernel
        'maven_orbnum_00001.orb',  # OrbNum file
        'maven_release_03.tm',     # Meta-kernel
        'name with spaces.bc',     # Unusual but valid filename
        'subdir/maven_001.bsp'])   # Path-like string (forward slash)
    def test_add_appends_single_kernel(self, kernel) -> None:
        # Build a KernelList instance without calling __init__ to isolate 'add'
        # from setup/datetime/read_config dependencies; 'add' only depends on
        # self.files.
        kernel_list = KernelList.__new__(KernelList)
        kernel_list.files = []

        kernel_list.add(kernel)

        assert kernel_list.files == [kernel]

    def test_add_preserves_insertion_order_and_allows_duplicates(self) -> None:
        # 'add' must append, not insert or deduplicate: successive calls keep
        # insertion order and the same name added twice appears. This
        # documents that deduplication is NOT adds responsibility.
        kernel_list = KernelList.__new__(KernelList)
        kernel_list.files = []

        kernels = ['maven_001.bsp', 'maven_002.bsp', 'maven_001.bsp']
        for kernel in kernels:
            kernel_list.add(kernel)

        assert kernel_list.files == kernels

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
         ['maven_orbit_v01.bsp'])])
    def test_read_list_builds_kernel_list_from_file_entries_only(
            self, mocker, tmp_path, content, expected_kernels) -> None:
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


class TestKernelListValidate:

    @staticmethod
    def expected_logs(setup, output_path, *, prefix=(), presence=None,
                      final=None, pds3=(), suffix=None):
        """Assemble the expected validate() log sequence from reusable blocks.

        The PDS4 happy flow is: [prefix] + presence + final + [pds3] + duplicates.
        Only the differing pieces are passed by each test.

        - prefix:   extra records before the presence block (e.g. badchar errors).
        - presence: the OPS-presence verdict lines (default: 'All kernels present.').
        - final:    the final-area verdict lines (default: 'No kernels present...').
        - pds3:     optional PDS3 option/template block, inserted before duplicates.
        - suffix:   records appended after the duplicates block (e.g. diff lines).
        """
        if presence is None:
            presence = [(logging.INFO, '     All kernels present.')]
        if final is None:
            final = [(logging.INFO, '     No kernels present in final area.')]
        if suffix is None:
            suffix = []

        return [*prefix,
                (logging.INFO, '-- Checking that kernels are present in: '),
                (logging.INFO, f'   {setup.kernels_directory[0]}'),
                *presence,
                (logging.INFO, ''),
                (logging.INFO, f'-- Checking that kernels are present in {setup.bundle_directory}: '),
                *final,
                (logging.INFO, ''),
                *pds3,
                (logging.INFO, '-- Checking for duplicates in complete kernel list:'),
                (logging.INFO, f'     Adding {output_path} in check.'),
                (logging.INFO, '     List contains no duplicates.'),
                (logging.INFO, ''),
                *suffix]

    @staticmethod
    def make_kernel_list(mocker, tmp_path, list_content, kernels,
                         present_kernels=(), badchar_errors=None,
                         duplicates=False,
                         **setup_overrides) -> tuple[KernelList, SimpleNamespace, Path]:
        # Create a real KernelList configured to run validate().

        # Build the actual paths to the 'working', 'kernels' and 'bundle' files.
        working_directory = tmp_path / 'working'
        kernels_directory = tmp_path / 'kernels'
        bundle_directory = tmp_path / 'bundle'
        working_directory.mkdir(exist_ok=True)
        kernels_directory.mkdir(exist_ok=True)
        bundle_directory.mkdir(exist_ok=True)

        setup_overrides.setdefault('diff', False)
        setup_overrides.setdefault('increment', False)

        # Create a setup with the attributes required to execute the validate
        # method.
        setup = make_kernel_list_setup(tmp_path,
                                       mission_acronym='maven',
                                       mission_name='MAVEN',
                                       run_type='release',
                                       working_directory=str(working_directory),
                                       kernels_directory=[str(kernels_directory)],
                                       bundle_directory=str(bundle_directory),
                                       **setup_overrides)

        # Build the kernels.
        for name in present_kernels:
            (kernels_directory / name).write_text('x', encoding='utf-8')

        # Mock the dependencies.
        mocker.patch('pds.naif_pds4_bundler.classes.list.check_badchar',
                     return_value=(badchar_errors or []))
        mocker.patch('pds.naif_pds4_bundler.classes.list.check_list_duplicates',
                     return_value=duplicates)
        mocker.patch('pds.naif_pds4_bundler.classes.list.extension_to_type',
                     return_value='spk')

        # Create a real KernelList.
        kernel_list = KernelList(setup)
        kernel_list.kernel_list = kernels
        kernel_list.list_name = 'maven_release_03.kernel_list'

        # Create the path that will open the validate method.
        output_path = working_directory / 'maven_release_03.kernel_list'
        output_path.write_text(list_content, encoding='utf-8')

        return kernel_list, setup, output_path

    @staticmethod
    def block(file_value, options, description) -> str:

        return (f"FILE             = {file_value}\n"
                f"MAKLABEL_OPTIONS = {options}\n"
                f"DESCRIPTION      = {description}\n")

    def test_validate_happy_path_passes_all_pds4_checks(
            self, mocker, caplog, tmp_path) -> None:
        # Check the clean PDS4 case in one run: a coherent kernel present in the
        # OPS area, absent from the final area, counts matching, no duplicates
        # and no diff. This walks every success branch at once.

        # Build the KernelList.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path,
            self.block('spice_kernels/spk/maven_orbit_v01.bsp', 'SPK', 'Orbit'),
            kernels=['maven_orbit_v01.bsp'],
            present_kernels=('maven_orbit_v01.bsp',))

        # Capture the logs and check the logging messages and logging level.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(setup, output_path)

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_logs_each_badchar_error(
            self, mocker, caplog, tmp_path) -> None:
        # Check that when check_badchar reports problems, validate() logs every
        # one of them as an error.

        # Build a KernelList with badchar_errors messages.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, self.block('spice_kernels/spk/k.bsp', 'SPK', 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',),
            badchar_errors=['check_badchar: msg 1', 'check_badchar: msg 2'])

        # Capture the logs and check the logging messages and logging level.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(
            setup, output_path,prefix=[(logging.ERROR, '   check_badchar: msg 1'),
                                       (logging.ERROR, '   check_badchar: msg 2')])

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        # Even if check_badchar reports errors, it does not stop the execution.
        assert results == expected

    def test_validate_ignores_file_line_without_value(
            self, mocker, tmp_path) -> None:
        # Check that even if the FILE line contains nothing after the following
        # equal sign, a file is created anyway.

        # Mock the handle_npb_error call.
        handle_npb_error_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.handle_npb_error')

        # Build a KernelList with a FILE line that contains nothing after equal
        # sign.
        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, 'FILE             = \n', kernels=[])

        kernel_list.validate()

        # Check that handle_npb_error is not called.
        handle_npb_error_mock.assert_not_called()

    def test_validate_skips_none_option_token(self, mocker, caplog,
                                              tmp_path) -> None:
        # Check that an option literally spelled "None" is filtered out. PDS3 is
        # used because it is the only mode that prints the collected options,
        # which is how the filtering becomes observable.

        # Build a KernelList with PDS3 and a 'None' option.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, self.block('data/spk/k.bsp', 'None', 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',), pds_version='3',
            pds3_mission_template={'DATA_SET_ID': 'X', 'maklabel_options': {}})

        # Capture the logs and check the logging messages and logging level.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(
            setup, output_path,
            pds3=[(logging.INFO, '-- Display all the MAKLABEL_OPTIONS:'),
                  (logging.INFO, ''),
                  (logging.INFO, '-- Check that all template tags used in the list are present in template:'),
                  (logging.INFO, '')])

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    @pytest.mark.parametrize('content', [
        ('FILE             = spice_kernels/spk/k.bsp\n'
         'DESCRIPTION      = only a description\n'),
        ('FILE             = spice_kernels/spk/k.bsp\n'
         'MAKLABEL_OPTIONS = SPK\n'
         'DESCRIPTION      = FILE naming kernel\n')])
    def test_validate_raises_on_entry_count_mismatch(self, mocker, tmp_path,
                                                     content) -> None:
        # Check that diverging FILE/OPTIONS/DESCRIPTION counts abort validation.
        # FILE and DESCRIPTION are present but the OPTIONS line is missing, so
        # the three counts diverge and the coherence check raises.

        # TODO: BUG, the second parametrized case is balanced (1 FILE, 1 OPTIONS,
        #       1 DESCRIPTION) and SHOULD pass, but its description contains the
        #       word 'FILE'. validate() counts lines by substring instead of
        #       prefix, so that description is miscounted as a FILE entry, the
        #       counts diverge and validation wrongly raises.

        # Build a KernelList.
        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, kernels=['k.bsp'])

        # Check that an Exception is raised.
        with pytest.raises(Exception, match='List does not have the same number of entries'):
            kernel_list.validate()

    @pytest.mark.parametrize('kernels, duplicates, expected_message', [
        ([], False, '   unplanned.bsp not in list.'),
        (['unplanned.bsp'], True, 'List contains duplicates.')])
    def test_validate_reports_error_condition(self, mocker, tmp_path, kernels,
                                              duplicates, expected_message) -> None:
        # Check the two independent error conditions that share the same
        # assertion shape: a kernel listed but absent from the plan, and a
        # duplicate detected in the list.

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path,
            self.block('spice_kernels/spk/unplanned.bsp', 'SPK', 'd'),
            kernels=kernels, present_kernels=('unplanned.bsp',),
            duplicates=duplicates)

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match=expected_message):
            kernel_list.validate()

    @pytest.mark.parametrize('kernel, log_lines', [
        ('maven_v01.tm',
         [(logging.INFO, '     maven_v01.tm not present as expected.'),
          (logging.INFO, '     All kernels present.')]),
        ('absent.bsp',
         [(logging.WARNING, '     absent.bsp not present. Kernel might be mapped.')])])
    def test_validate_absent_kernel_logging(
            self, mocker, caplog, tmp_path, kernel, log_lines) -> None:
        # Check how a kernel missing from the OPS area is handled. A meta-kernel
        # (.tm) is excused with an INFO and the "all present" verdict stands,
        # because meta-kernels are generated later. Any other missing kernel is
        # a WARNING and clears that verdict.

        # The kernel is deliberately NOT placed on disk, so the walk is empty.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path,
            self.block(f'spice_kernels/spk/{kernel}', 'N/A', 'd'),
            kernels=[kernel])

        # Capture the logs and check the messages.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(setup, output_path, presence=log_lines)

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_present_flag_not_reset_between_kernels(
            self, mocker, caplog, tmp_path) -> None:
        # TODO: BUG, 'present' flag is initialised once OUTSIDE the 'for ker'
        #       loop and never reset per kernel. As soon as one kernel is found,
        #       every later kernel is treated as present too, so a missing
        #       kernel listed AFTER a present one produces no warning and does
        #       not clear all_present. The output then depends on kernel ORDER.

        # Build the list using two concatenated blocks. The order is
        # deliberate: present.bsp first, then absent.bsp. It is this order
        # that triggers the bug.
        content = (self.block('spice_kernels/spk/present.bsp', 'SPK', 'd')
                   + self.block('spice_kernels/spk/absent.bsp', 'SPK', 'd'))

        # Create a KernelList using the content prepared earlier. Only
        # present.bsp (present_kernels) is loaded. However, absent.bsp does not
        # exist on the disk, so the call to os.walk cannot find it.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, content,
            kernels=['present.bsp', 'absent.bsp'],
            present_kernels=('present.bsp',))

        # Capture the logs.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        # The kernel absent.bsp is missing and no warning is emitted and 'all
        # kernel present' is logged.
        expected = self.expected_logs(setup, output_path)

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_warns_kernel_in_final_area(
            self, mocker, caplog, tmp_path) -> None:
        # Check that a kernel already present in the bundle area is flagged with
        # a warning.

        # Build the KernelList
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, self.block('spice_kernels/spk/k.bsp', 'SPK', 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',))

        # Build the exact path that is checked and the entire hierarchy. In this
        # way, the check will return TRUE.
        final_dir = (Path(setup.bundle_directory) / 'maven_spice'
                     / 'spice_kernels' / 'spk')
        final_dir.mkdir(parents=True)
        (final_dir / 'k.bsp').write_text('x', encoding='utf-8')

        # Capture the logs.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(
            setup, output_path,
            final=[(logging.WARNING, '     k.bsp present.')])

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    @pytest.mark.parametrize('option, template_options, log_lines', [
        ('SPK', {'SPK': {}}, [(logging.INFO, '     SPK is present.'),
                              (logging.INFO, ''),]),
        ('N/A', {}, [(logging.INFO, '')])])
    def test_validate_pds3_option_template_check_accepts_valid_option(
            self, mocker, caplog, tmp_path, option, template_options,
            log_lines) -> None:
        # Check that, if PDS3 contains an option in the template (or the N/A
        # placeholder), it passes the template check without generating any errors.

        # Build a KernelList with a PDS3.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, self.block('data/spk/k.bsp', option, 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',), pds_version='3',
            pds3_mission_template={'DATA_SET_ID': 'X',
                                   'maklabel_options': template_options})

        # Capture the logs and check the log messages.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(
            setup, output_path,
            pds3=[(logging.INFO, '-- Display all the MAKLABEL_OPTIONS:'),
                  (logging.INFO, f'     {option}'),
                  (logging.INFO, ''),
                  (logging.INFO, '-- Check that all template tags used in the list are present in template:'),
                  *log_lines])

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_pds3_option_template_check_rejects_unknown_option(
            self, mocker, tmp_path) -> None:
        # Check that PDS3 has an option absent from the template (and not "N/A").

        # Build a KernelList with an option that is not in the template.
        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, self.block('data/spk/k.bsp', 'CK', 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',), pds_version='3',
            pds3_mission_template={'DATA_SET_ID': 'X',
                                   'maklabel_options': {'SPK': {}}})

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match='CK not in configuration.'):
            kernel_list.validate()

    def test_validate_aborts_when_complete_kernel_list_contains_duplicates(
            self, mocker, tmp_path) -> None:
        # Verify the second duplicate check aborts validation when duplicates
        # are detected across the complete release-list.

        # Create a block with a kernel.
        content = self.block('spice_kernels/spk/current.bsp', 'SPK',
                             'description')

        # Build a KernelList.
        kernel_list, setup, _ = self.make_kernel_list(
            mocker, tmp_path, content,
            kernels=['current.bsp'],
            present_kernels=('current.bsp',))

        # The helper mocks check_list_duplicates to False; restore the real logic
        # so the cross-release (second) check detects the duplicate for real. The
        # current list has no internal duplicate (first check passes); the merged
        # release lists do (second check aborts).
        mocker.patch('pds.naif_pds4_bundler.classes.list.check_list_duplicates',
                     side_effect=lambda lst: len(lst) != len(set(lst)))

        # Add a second release list repeating the kernel -> cross-release duplicate.
        (Path(setup.working_directory) / 'maven_release_02.kernel_list'
         ).write_text(
            self.block('spice_kernels/spk/current.bsp', 'SPK', 'description'),
            encoding='utf-8')

        # This behaviour will be handled by handle_npb_error, which will raise a
        # RuntimeError. Also, checks the returned message.
        with pytest.raises(RuntimeError, match='List contains duplicates.'):
            kernel_list.validate()

    def test_validate_diff_compares_with_previous_list(self, mocker,
                                                       tmp_path) -> None:
        # Check that with diff and increment enabled and a previous release list
        # available, compare_files is invoked with the diff argument last.

        compare_files_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.compare_files')

        content = self.block('spice_kernels/spk/k.bsp', 'SPK', 'd')

        # Build a KernelList with the flags diff and increment enabled.
        kernel_list, setup, _ = self.make_kernel_list(
            mocker, tmp_path, content, kernels=['k.bsp'],
            present_kernels=('k.bsp',), diff='diff-arg', increment=True)

        # Create a second list of releases to carry out the comparison.
        (Path(setup.working_directory) / 'maven_release_02.kernel_list').write_text(
            self.block('spice_kernels/spk/old.bsp', 'SPK', 'd'),
            encoding='utf-8')

        kernel_list.validate()

        # Check that the compare_files function has been called.
        compare_files_mock.assert_called_once()
        assert compare_files_mock.call_args.args[-1] == 'diff-arg'

    def test_validate_diff_previous_list_unavailable(self, mocker, caplog,
                                                     tmp_path) -> None:
        # Check the missing-previous path: with diff and increment enabled but
        # only one release list present, kernel_lists[-2] raises IndexError,
        # which the except clause turns into an error log instead of crashing.

        # TODO: BUG; in the diff branch fromfile = kernel_lists[-1] runs BEFORE
        #       the try, so if the glob returns nothing kernel_lists[-1] raises
        #       an uncaught IndexError.

        # Build a KernleList.
        kernel_list, setup, output_path = self.make_kernel_list(
            mocker, tmp_path, self.block('spice_kernels/spk/k.bsp', 'SPK', 'd'),
            kernels=['k.bsp'], present_kernels=('k.bsp',),
            diff='diff-arg', increment=True)

        # Capture the logs and check the log messages and log level.
        with caplog.at_level(logging.INFO):
            kernel_list.validate()

        expected = self.expected_logs(
            setup, output_path,
            suffix=[(logging.INFO, '-- Comparing current list with previous list:'),
                    (logging.INFO, ''),
                    (logging.ERROR, '-- Previous list not available.')])

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected


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
            self, mocker, caplog, tmp_path) -> None:
        # Verify the empty-input path: when no release lists are found, the method still
        # creates an empty complete list, updates state and requests validation.

        # TODO: BUG; write_complete_list should handle the case with no release
        #      lists before checking if release numbers are consecutive.

        # Mock the validate_complete and check_consecutive calls.
        validate_complete_mock = mocker.patch.object(KernelList, 'validate_complete',
                                                     autospec=True)

        # Create a KernelList instance with a temporal and empty working_directory
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                kernel_list.write_complete_list()

        # Check that the file exists and is empty.
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == ''

        # The method must still publish the generated complete-list filename.
        assert kernel_list.complete_list == ''

        # Check that check_consecutive and validate_complete called once.
        validate_complete_mock.assert_not_called()

        # No release files are added and no warning is emitted.
        assert caplog.record_tuples == []

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

    @pytest.mark.skip(
        reason='To be updated after tests for validate_complete are available.')
    def test_write_complete_list_propagates_validate_complete_errors_after_side_effects(
            self, mocker, tmp_path) -> None:
        # validate_complete is a boundary here, but write_complete_list must have
        # produced the complete file and updated complete_list before it raises.
        validate_complete_mock = mocker.patch.object(
            KernelList, 'validate_complete', autospec=True,
            side_effect=Exception('complete validation failed'))

        # Build a real KernelList instance and the expected complete-list path.
        kernel_list, _, output_path = self.make_kernel_list(tmp_path)

        # Build a valid release list.
        release_01 = (
                Path(kernel_list.setup.working_directory) /
                'maven_release_01.kernel_list')
        release_01.write_text('RELEASE 01\n', encoding='utf-8')

        # Capture the exception.
        with pytest.raises(Exception, match='complete validation failed'):
            kernel_list.write_complete_list()

        # Although the method threw an exception, the file has been created.
        assert output_path.read_text(encoding='utf-8') == 'RELEASE 01\n'
        assert kernel_list.complete_list == 'maven_complete.kernel_list'

        # The validate_complete must be called once and its exception
        # propagated.
        validate_complete_mock.assert_called_once_with(kernel_list)


class TestKernelListValidateComplete:
    """Tests for KernelList.validate_complete.

    validate_complete parses the *complete* kernel list (the merge of every
    release list) and performs three checks:

      1. FILE / MAKLABEL_OPTIONS / DESCRIPTION entry counts must match.
      2. The collected kernels must contain no duplicates.
      3. For PDS3 only: every MAKLABEL_OPTION used must appear in the mission
         template file as ``--<option>``.

    The method is heavily side effect driven (it logs almost everything and only
    raises through ``handle_npb_error`` / a bare ``Exception``), so the tests
    below isolate the *logging* from the *control-flow* boundaries exactly as the
    sibling ``TestKernelListValidate`` class does.
    """

    @staticmethod
    def block(file_value: str, options: str, description: str) -> str:
        # Reuse the same three-line entry shape produced by write_list, so the
        # fixtures read like a real complete kernel list. Kept identical to
        # TestKernelListValidate.block to avoid diverging test vocabularies.
        return (f"FILE             = {file_value}\n"
                f"MAKLABEL_OPTIONS = {options}\n"
                f"DESCRIPTION      = {description}\n")

    @staticmethod
    def make_kernel_list(mocker, tmp_path, complete_content,
                         duplicates=False, template_content=None,
                         **setup_overrides) -> tuple[KernelList, SimpleNamespace, Path]:
        # Build a real KernelList wired up to run validate_complete.
        #
        # validate_complete only reads:
        #   * setup.working_directory + os.sep + self.complete_list  (the list)
        #   * setup.pds_version                                      (PDS3 branch)
        #   * setup.mission_name                                     (error log)
        #   * setup.root_dir / setup.mission_acronym                 (PDS3 template)
        #   * self.json_formatted_lst                                (error log)
        #
        # Everything else is a boundary and is mocked.

        # Real directories so the open() calls hit a genuine filesystem. Using
        # os.sep-free pathlib joins keeps this valid on Windows too.
        working_directory = tmp_path / 'working'
        config_directory = tmp_path / 'config'
        working_directory.mkdir(exist_ok=True)
        config_directory.mkdir(exist_ok=True)

        # check_list_duplicates is the only collaborator inside the method (other
        # than handle_npb_error, mocked per-test). Default: no duplicates.
        mocker.patch('pds.naif_pds4_bundler.classes.list.check_list_duplicates',
                     return_value=duplicates)

        # Build a minimal setup. root_dir points at tmp_path so the PDS3 template
        # is resolved under tmp_path/config/<acronym>_mission_template.pds, which
        # is the layout validate_complete expects.
        setup = make_kernel_list_setup(tmp_path,
                                       mission_acronym='maven',
                                       mission_name='MAVEN',
                                       working_directory=str(working_directory),
                                       root_dir=str(tmp_path),
                                       **setup_overrides)

        kernel_list = KernelList(setup)

        # complete_list is the filename validate_complete opens inside
        # working_directory.
        kernel_list.complete_list = 'maven_complete.kernel_list'
        complete_path = working_directory / kernel_list.complete_list
        complete_path.write_text(complete_content, encoding='utf-8')

        # The mission template is only opened on the PDS3 path. Create it on
        # demand so PDS4 tests do not need it on disk.
        if template_content is not None:
            (config_directory / 'maven_mission_template.pds').write_text(
                template_content, encoding='utf-8')

        return kernel_list, setup, complete_path

    # ------------------------------------------------------------------
    # Happy paths: counts coherent, no duplicates.
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('complete_content, num_entries', [
        (None, 1), (None, 2)])
    def test_validate_complete_pds4_happy_path_logs_pass_and_no_duplicates(
            self, mocker, caplog, tmp_path, complete_content, num_entries) -> None:
        # PDS4 success flow: coherent FILE/OPTIONS/DESCRIPTION counts and no
        # duplicates. The PDS3-only option/template blocks must be skipped, so
        # the log ends right after the duplicates section.

        # Build N coherent entries with distinct filenames (so no duplicates).
        content = ''.join(
            self.block(f'spice_kernels/spk/maven_{i:02d}.bsp', 'SPK', 'Orbit')
            for i in range(num_entries))

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content)

        # Capture the logs and check the exact message/level sequence.
        with caplog.at_level(logging.INFO):
            kernel_list.validate_complete()

        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.INFO, f'     PASS with total of {num_entries} entries.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking for duplicates in kernel list:'),
            (logging.INFO, '     List contains no duplicates.'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_ignores_file_and_description_lines_without_value(
            self, mocker, caplog, tmp_path) -> None:
        # Lines whose value after '=' is empty must not be counted. A FILE line
        # and a DESCRIPTION line with no value are present but, because both are
        # skipped, the three counters stay at zero and remain coherent.

        # OPTIONS has no emptiness guard in the code (it is counted regardless),
        # so we must NOT include an OPTIONS line here or the counts would
        # diverge. This isolates the empty-value guards on FILE and DESCRIPTION.
        content = ('FILE             = \n'
                   'DESCRIPTION      = \n')

        kernel_list, _, _ = self.make_kernel_list(mocker, tmp_path, content)

        with caplog.at_level(logging.INFO):
            kernel_list.validate_complete()

        # Zero coherent entries -> still a PASS with 0 entries, no duplicates.
        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.INFO, '     PASS with total of 0 entries.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking for duplicates in kernel list:'),
            (logging.INFO, '     List contains no duplicates.'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_extracts_kernel_basename_from_path(
            self, mocker, tmp_path) -> None:
        # The kernel basename fed into the duplicate check is taken as the text
        # after the last '/'. Verify the exact list passed to
        # check_list_duplicates rather than only its boolean result, because the
        # basename extraction is its own logical branch.

        content = (self.block('spice_kernels/spk/a.bsp', 'SPK', 'd')
                   + self.block('spice_kernels/ck/b.bc', 'CK', 'd'))

        kernel_list, _, _ = self.make_kernel_list(mocker, tmp_path, content)

        # The helper already patches check_list_duplicates; re-patch it AFTER the
        # helper so this mock is the active one (last patch wins) and capture the
        # reference to assert the exact argument it receives.
        duplicates_mock = mocker.patch(
            'pds.naif_pds4_bundler.classes.list.check_list_duplicates',
            return_value=False)

        kernel_list.validate_complete()

        # The basename (text after the last '/') are what gets deduplicated.
        duplicates_mock.assert_called_once_with(['a.bsp', 'b.bc'])

    # ------------------------------------------------------------------
    # Entry-count mismatch: raises a bare Exception and logs the diagnostics.
    # ------------------------------------------------------------------

    @pytest.mark.parametrize('content', [
        ('FILE             = spice_kernels/spk/k.bsp\n'
         'DESCRIPTION      = only a description\n'),
        ('FILE             = spice_kernels/spk/k.bsp\n'
         'MAKLABEL_OPTIONS = SPK\n')])
    def test_validate_complete_raises_on_entry_count_mismatch(
            self, mocker, tmp_path, content) -> None:
        # Diverging FILE/OPTIONS/DESCRIPTION counts must abort validation with a
        # bare Exception (NOT handle_npb_error). This is the only failure path in
        # validate_complete that raises directly.

        kernel_list, _, _ = self.make_kernel_list(mocker, tmp_path, content)

        with pytest.raises(Exception,
                           match='List does not have the same number of entries'):
            kernel_list.validate_complete()

    def test_validate_complete_logs_entry_count_diagnostics_before_raising(
            self, mocker, caplog, tmp_path) -> None:
        # When the counts diverge, the method must emit the full diagnostic
        # block (the three counters, the mission-name hint and the formatted JSON
        # config) and only then raise. Side-effects and the raise are asserted
        # together because the logging happens strictly before the exception.

        content = ('FILE             = spice_kernels/spk/k.bsp\n'
                   'DESCRIPTION      = d\n')

        kernel_list, setup, _ = self.make_kernel_list(mocker, tmp_path, content)

        # Pin a known formatted JSON config so the trailing INFO lines are
        # deterministic. This attribute is normally produced by read_config.
        kernel_list.json_formatted_lst = ['{', '  "k": "v"', '}']

        with caplog.at_level(logging.INFO):
            with pytest.raises(Exception,
                               match='List does not have the same number of entries'):
                kernel_list.validate_complete()

        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.ERROR, 'List does not have the same number of entries for:'),
            (logging.ERROR, '   FILE             (1)'),
            (logging.ERROR, '   MAKLABEL_OPTIONS (0)'),
            (logging.ERROR, '   DESCRIPTION      (1)'),
            (logging.ERROR, ''),
            (logging.ERROR,
             f'-- Display {setup.mission_name} kernel list configuration file to'
             ' double-check.'),
            (logging.INFO, '{'),
            (logging.INFO, '  "k": "v"'),
            (logging.INFO, '}'),
            (logging.ERROR, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_miscounts_description_containing_file_word(
            self, mocker, tmp_path) -> None:
        # TODO: BUG; validate_complete counts entry types with substring 'in'
        #       tests instead of prefix checks (mirrors the known validate()
        #       bug). A balanced 1 FILE / 1 OPTIONS / 1 DESCRIPTION list whose
        #       DESCRIPTION text contains the word 'FILE' is miscounted as 2
        #       FILE entries, so the coherent list wrongly fails the count check.
        content = ('FILE             = spice_kernels/spk/k.bsp\n'
                   'MAKLABEL_OPTIONS = SPK\n'
                   'DESCRIPTION      = FILE naming kernel\n')

        kernel_list, _, _ = self.make_kernel_list(mocker, tmp_path, content)

        # Documents the buggy behaviour: this *should* pass but currently raises.
        with pytest.raises(Exception,
                           match='List does not have the same number of entries'):
            kernel_list.validate_complete()

    # ------------------------------------------------------------------
    # Duplicate detection: routed through handle_npb_error.
    # ------------------------------------------------------------------

    def test_validate_complete_reports_duplicates_via_handle_npb_error(
            self, mocker, tmp_path) -> None:
        # When check_list_duplicates returns True, validate_complete calls
        # handle_npb_error("List contains duplicates."), which always raises
        # RuntimeError. The real function is used — exactly as
        # TestKernelListValidate.test_validate_reports_error_condition does —
        # because spiceypy.kclear() is safe to call with no kernels loaded.

        content = self.block('spice_kernels/spk/dup.bsp', 'SPK', 'd')

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, duplicates=True)

        with pytest.raises(RuntimeError, match='List contains duplicates.'):
            kernel_list.validate_complete()

    # ------------------------------------------------------------------
    # PDS3 branch: option display + template presence check.
    # ------------------------------------------------------------------

    def test_validate_complete_pds3_displays_sorted_unique_options(
            self, mocker, caplog, tmp_path) -> None:
        # On PDS3 the method deduplicates and sorts every MAKLABEL_OPTION token
        # and logs them, then checks each against the mission template. Use
        # duplicated, unsorted, multi-token option lines to exercise the
        # dedup + sort + multi-token split at once.

        # TODO: BUG; the mission-template path is built with a hardcoded
        #       forward slash (root_dir + '/config/...') instead of os.sep /
        #       os.path.join, inconsistent with the os.sep usage elsewhere in
        #       the method. It still works on Windows (which accepts '/'), but
        #       it should be normalised.

        content = (
                self.block('spice_kernels/spk/a.bsp', 'SPK LSK', 'd')
                + self.block('spice_kernels/ck/b.bc', 'CK SPK', 'd'))

        # Template must contain every distinct option as --<option> to avoid the
        # handle_npb_error escalation; this isolates the display/order logic.
        template = '--SPK\n--LSK\n--CK\n'

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, pds_version='3',
            template_content=template)

        with caplog.at_level(logging.INFO):
            kernel_list.validate_complete()

        # Tokens collected: SPK, LSK, CK, SPK -> unique+sorted = CK, LSK, SPK.
        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.INFO, '     PASS with total of 2 entries.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking for duplicates in kernel list:'),
            (logging.INFO, '     List contains no duplicates.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Display all the MAKLABEL_OPTIONS:'),
            (logging.INFO, '     CK'),
            (logging.INFO, '     LSK'),
            (logging.INFO, '     SPK'),
            (logging.INFO, ''),
            (logging.INFO, '-- Check that all template tags used in the '
                           'list are present in template:'),
            (logging.INFO, '     CK is present.'),
            (logging.INFO, '     LSK is present.'),
            (logging.INFO, '     SPK is present.'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_pds3_rejects_option_absent_from_template(
            self, mocker, tmp_path) -> None:
        # On PDS3, an option missing from the mission template must escalate via
        # handle_npb_error with the "<option> not in template." message.

        content = self.block('spice_kernels/ck/b.bc', 'CK', 'd')

        # Template lacks --CK, so the presence check fails.
        template = '--SPK\n--LSK\n'

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, pds_version='3',
            template_content=template)

        with pytest.raises(RuntimeError, match='CK not in template.'):
            kernel_list.validate_complete()

    def test_validate_complete_pds3_collects_literal_none_option(
            self, mocker, caplog, tmp_path) -> None:
        # Unlike validate(), validate_complete does NOT filter a literal 'None'
        # option token: it is displayed and checked against the template like any
        # other. This documents the behavioural divergence between the two
        # methods and covers the multistep path with a single option.

        content = self.block('spice_kernels/spk/a.bsp', 'None', 'd')

        # Template must contain --None for the presence check to pass, otherwise
        # the run would escalate. This proves 'None' is treated as a real token.
        template = '--None\n'

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, pds_version='3',
            template_content=template)

        with caplog.at_level(logging.INFO):
            kernel_list.validate_complete()

        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.INFO, '     PASS with total of 1 entries.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking for duplicates in kernel list:'),
            (logging.INFO, '     List contains no duplicates.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Display all the MAKLABEL_OPTIONS:'),
            (logging.INFO, '     None'),
            (logging.INFO, ''),
            (logging.INFO, '-- Check that all template tags used in the '
                           'list are present in template:'),
            (logging.INFO, '     None is present.'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_pds3_empty_options_skips_template_loop(
            self, mocker, caplog, tmp_path) -> None:
        # PDS3 path where no option tokens were collected: an OPTIONS line with
        # no value contributes to the OPTIONS count but yields no tokens, so the
        # display and template-presence loops both run zero iterations. The
        # template file is still opened (its readlines() result is simply
        # unused), so it must exist.

        # 1 FILE / 1 OPTIONS / 1 DESCRIPTION keeps the counts coherent while the
        # OPTIONS value is empty -> opt_in_list stays empty.
        content = ('FILE             = spice_kernels/spk/k.bsp\n'
                   'MAKLABEL_OPTIONS = \n'
                   'DESCRIPTION      = d\n')

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, pds_version='3',
            template_content='--SPK\n')

        with caplog.at_level(logging.INFO):
            kernel_list.validate_complete()

        expected = [
            (logging.INFO, '-- Checking list number of entries coherence:'),
            (logging.INFO, '     PASS with total of 1 entries.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Checking for duplicates in kernel list:'),
            (logging.INFO, '     List contains no duplicates.'),
            (logging.INFO, ''),
            (logging.INFO, '-- Display all the MAKLABEL_OPTIONS:'),
            (logging.INFO, ''),
            (logging.INFO, '-- Check that all template tags used in the '
                           'list are present in template:'),
            (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_validate_complete_pds3_raises_when_template_file_missing(
            self, mocker, tmp_path) -> None:
        # On PDS3 with at least one option, the mission template file is opened
        # for reading. If it does not exist, open() raises FileNotFoundError and
        # the method propagates it (there is no guard). template_content is left
        # as None so the file is never created.

        content = self.block('spice_kernels/spk/a.bsp', 'SPK', 'd')

        kernel_list, _, _ = self.make_kernel_list(
            mocker, tmp_path, content, pds_version='3')

        with pytest.raises(FileNotFoundError):
            kernel_list.validate_complete()

    # ------------------------------------------------------------------
    # I/O boundary: the complete list itself must exist.
    # ------------------------------------------------------------------

    def test_validate_complete_raises_when_complete_list_missing(
            self, mocker, tmp_path) -> None:
        # The very first action is opening the complete list. If complete_list
        # points at a non-existent file, open() raises FileNotFoundError before
        # any check runs.
        kernel_list, _, complete_path = self.make_kernel_list(
            mocker, tmp_path, 'placeholder\n')

        # Remove the file created by the helper to force the missing-file path.
        complete_path.unlink()

        with pytest.raises(FileNotFoundError):
            kernel_list.validate_complete()


class TestKernelListCheckProducts:
    """Tests for the ``check_products`` method.
    """

    @pytest.fixture()
    def _text_kernel(self, tmp_path) -> tuple:
        # Create maven_test.tsc on disk and return a silent KernelList
        # already pointing at it. Tests that need mocks call patch_checks
        # independently; this fixture only removes the repeated file-creation
        # and instance-construction boilerplate.
        expected_path = self.write_kernel(tmp_path, 'maven_test.tsc')
        kernel_list = self.make_kernel_list(tmp_path,
                                            kernels=['maven_test.tsc'],
                                            silent=True, verbose=False)
        return kernel_list, expected_path

    # ------------------------------------------------------------------ #
    # Static helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def make_kernel_list(tmp_path, kernels, pds_version='4', eol='\r\n',
                         silent=True, verbose=False) -> KernelList:
        # Build a real KernelList without running the heavy __init__.
        # check_products only consumes kernel_list and a handful of
        # setup attributes, so a SimpleNamespace setup is enough.
        #
        # template_files, write_file_list and write_checksum_registry are
        # required by the real handle_npb_error when setup is not None.
        kernels_directory = tmp_path / 'kernels'
        orbnum_directory = tmp_path / 'orbnum'
        kernels_directory.mkdir(exist_ok=True)
        orbnum_directory.mkdir(exist_ok=True)

        setup = SimpleNamespace(
            kernels_directory=[str(kernels_directory)],
            orbnum_directory=str(orbnum_directory),
            pds_version=pds_version,
            eol=eol,
            args=SimpleNamespace(silent=silent, verbose=verbose),
            template_files=[],
            write_file_list=lambda: None,
            write_checksum_registry=lambda: None)

        kernel_list = KernelList.__new__(KernelList)
        kernel_list.kernel_list = kernels
        kernel_list.setup = setup

        return kernel_list

    @staticmethod
    def write_kernel(tmp_path, name, subdir='kernels') -> str:
        # Create a real product file so the os.walk discovery finds it.
        # Returns the absolute path that check_products is expected to
        # resolve as origin_path.
        target = tmp_path / subdir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('CONTENT\n', encoding='utf-8')
        return str(target)

    @staticmethod
    def patch_checks(mocker, **return_values) -> SimpleNamespace:
        # Resolve the module where check_products looks up its globals.
        # KernelList.__module__ names that module and sys.modules holds
        # the already-imported object, so no second import statement is needed.
        list_module = sys.modules[KernelList.__module__]

        # Patch every 'check_*' boundary on the list module.
        defaults = {
            'check_eol': None,
            'check_badchar': [],
            'check_line_length': [],
            'check_kernel_integrity': None,
            'check_binary_endianness': None,
            'check_permissions': [],
        }
        defaults.update(return_values)

        mocks = SimpleNamespace()
        for name, value in defaults.items():
            setattr(mocks, name,
                    mocker.patch.object(list_module, name, return_value=value))

        # 'product_mapping' is only reached on the fallback path; by default
        # it returns a sentinel that never matches a real filename.
        mocks.product_mapping = mocker.patch.object(
            list_module, 'product_mapping', return_value='__no_match__')

        # Prevent SPICE pool operations in every test.
        mocks.kclear = mocker.patch('spiceypy.kclear')

        return mocks

    # ------------------------------------------------------------------ #
    # Path discovery
    # ------------------------------------------------------------------ #
    @pytest.mark.parametrize('product', [
        'm01_rec.orb', 'm01_rec.nrb', 'M01_REC.ORB', 'M01_REC.NRB'])
    def test_check_products_orbnum_uses_orbnum_directory(
            self, mocker, tmp_path, product) -> None:
        # ORBNUM products (.orb/.nrb, case-insensitive) are resolved against
        # the configured orbnum_directory instead of being searched in the
        # kernel directories. The path is built unconditionally, even if the
        # file does not physically exist, so no file is created here.
        mocks = self.patch_checks(mocker)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        kernel_list.check_products()

        expected_path = kernel_list.setup.orbnum_directory + os.sep + product

        # check_eol is the first boundary to receive the path, proving the
        # ORBNUM branch resolved the product.
        mocks.check_eol.assert_called_once_with(expected_path, mocker.ANY)
        mocks.check_permissions.assert_called_with(expected_path)

        # ORBNUM files skip the kernel-architecture and endianness checks.
        mocks.check_kernel_integrity.assert_not_called()
        mocks.check_binary_endianness.assert_not_called()

    def test_check_products_resolves_kernel_by_exact_name(
            self, mocker, tmp_path) -> None:
        # A regular kernel is located by walking each kernel directory and
        # matching the filename exactly. The mapping fallback must not be
        # reached, and the discovered path must reach every file check.
        mocks = self.patch_checks(mocker)
        product = 'maven_test.tsc'
        expected_path = self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        kernel_list.check_products()

        mocks.product_mapping.assert_not_called()
        mocks.check_eol.assert_called_once_with(expected_path, '\n')
        mocks.check_kernel_integrity.assert_called_once_with(expected_path)

    def test_check_products_resolves_kernel_via_mapping_fallback(
            self, mocker, tmp_path) -> None:
        # When no file matches the product name directly, discovery falls back
        # to product_mapping and matches the mapped name instead. The file
        # on disk is named after the mapped value, not the product, forcing the
        # exact-match list comprehension to come back empty.
        mapped_name = 'maven_mapped.bc'
        expected_path = self.write_kernel(tmp_path, mapped_name)
        product = 'maven_logical.bc'

        mocks = self.patch_checks(mocker)
        mocks.product_mapping.return_value = mapped_name

        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])
        kernel_list.check_products()

        mocks.product_mapping.assert_called_once_with(
            product, kernel_list.setup, cleanup=False)
        # '.bc' is binary: skips text checks, runs architecture + endianness.
        mocks.check_eol.assert_not_called()
        mocks.check_kernel_integrity.assert_called_once_with(expected_path)
        mocks.check_binary_endianness.assert_called_once_with(
            expected_path, endianness='little')

    def test_check_products_missing_non_mk_records_error_and_skips_checks(
            self, mocker, caplog, tmp_path) -> None:
        # A non meta-kernel product that cannot be found anywhere records a
        # fatal error, skips all file checks for that product via continue,
        # and raises RuntimeError through the real handle_npb_error.
        mocks = self.patch_checks(mocker)
        product = 'maven_absent.tsc'
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError, match=_CHECK_FATAL_MESSAGE):
                kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.ERROR, '     Product not present in any kernel directory(ies)'),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- {_CHECK_FATAL_MESSAGE}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        # No file check ran: the product was skipped via continue.
        mocks.check_permissions.assert_not_called()
        mocks.check_kernel_integrity.assert_not_called()
        # 'handle_npb_error' called kclear before raising.
        mocks.kclear.assert_called_once()

    def test_check_products_missing_meta_kernel_records_warning_only(
            self, mocker, caplog, tmp_path) -> None:
        # A missing meta-kernel (.tm) is benign: it will be generated later in
        # the run, so it only raises a warning, skips file checks and does not
        # raise RuntimeError.
        mocks = self.patch_checks(mocker)
        product = 'maven_release.tm'
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()  # must not raise

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.WARNING, '     Meta-kernel will be generated during this run.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        mocks.check_permissions.assert_not_called()
        mocks.kclear.assert_not_called()

    def test_check_products_present_in_multiple_directories_warns(
            self, mocker, caplog, tmp_path) -> None:
        # When the same kernel name exists in more than one configured kernel
        # directory the method warns, lists every location, proceeds with the
        # first directory and does not raise.
        product = 'maven_dup.tsc'

        # 'make_kernel_list' creates the 'kernels' directory; the second
        # directory is created separately. Build the instance first so both
        # directories exist before the duplicate files are written.
        mocks = self.patch_checks(mocker)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        first_dir = tmp_path / 'kernels'
        second_dir = tmp_path / 'kernels2'
        second_dir.mkdir(exist_ok=True)
        first_path = first_dir / product
        second_path = second_dir / product
        first_path.write_text('A\n', encoding='utf-8')
        second_path.write_text('B\n', encoding='utf-8')
        kernel_list.setup.kernels_directory = [str(first_dir), str(second_dir)]

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.WARNING, '     Product present in multiple directories:'),
            (logging.WARNING, f'       {first_path}'),
            (logging.WARNING, f'       {second_path}'),
            (logging.WARNING, '     The product in the first directory will be used.')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected
        # The first directory wins: every file check uses the first path.
        mocks.check_kernel_integrity.assert_called_once_with(str(first_path))
        mocks.kclear.assert_not_called()

    # ------------------------------------------------------------------ #
    # EOL selection and text checks
    # ------------------------------------------------------------------ #
    @pytest.mark.parametrize('pds_version', ['3', '4'])
    def test_check_products_text_kernel_always_uses_lf_eol(
            self, mocker, tmp_path, pds_version) -> None:
        # Text kernels always receive LF regardless of the configured EOL and
        # regardless of the PDS version. 'setup.eol' is set to CRLF to prove
        # the override rather than echoing the input.
        mocks = self.patch_checks(mocker)
        product = 'maven_test.tsc'
        expected_path = self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product],
                                            pds_version=pds_version, eol='\r\n')

        kernel_list.check_products()

        mocks.check_eol.assert_called_once_with(expected_path, '\n')

    @pytest.mark.parametrize('pds_version, expected_eol', [
        ('3', '\n'), ('4', '\r\n')])
    def test_check_products_orbnum_eol_follows_pds_version(
            self, mocker, tmp_path, pds_version, expected_eol) -> None:
        # ORBNUM files use LF under PDS3 and the configured EOL under PDS4.
        # 'setup.eol' is set to CRLF so the PDS3 case proves the override.
        mocks = self.patch_checks(mocker)
        product = 'm01_rec.orb'
        expected_path = str(tmp_path / 'orbnum' / product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product],
                                            pds_version=pds_version, eol='\r\n')

        kernel_list.check_products()

        mocks.check_eol.assert_called_once_with(expected_path, expected_eol)

    def test_check_products_orbnum_eol_error_is_warning(
            self, mocker, caplog, tmp_path) -> None:
        # A bad EOL on an ORBNUM file is recorded as a warning, so no
        # RuntimeError is raised.
        mocks = self.patch_checks(mocker, check_eol='Wrong EOL')
        product = 'm01_rec.orb'
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.WARNING, '     Wrong EOL')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        mocks.kclear.assert_not_called()

    def test_check_products_badchar_and_line_length_warn(
            self, mocker, caplog, _text_kernel) -> None:
        # Bad characters and over-long lines are warnings; neither raises
        # RuntimeError. Both checks receive the kernel path, and line length
        # applies because it is a text kernel.
        kernel_list, expected_path = _text_kernel
        mocks = self.patch_checks(mocker,
                                  check_badchar=['bad char on line 1'],
                                  check_line_length=['line 2 too long'])

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        mocks.check_badchar.assert_called_once_with(expected_path)
        mocks.check_line_length.assert_called_once_with(expected_path)

        expected = [
            (logging.WARNING, '-- maven_test.tsc'),
            (logging.WARNING, '     bad char on line 1'),
            (logging.WARNING, '     line 2 too long')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        mocks.kclear.assert_not_called()

    def test_check_products_orbnum_skips_line_length(
            self, mocker, tmp_path) -> None:
        # ORBNUM files are checked for bad characters but not for line length.
        mocks = self.patch_checks(mocker)
        product = 'm01_rec.orb'
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        kernel_list.check_products()

        mocks.check_badchar.assert_called_once()
        mocks.check_line_length.assert_not_called()

    # ------------------------------------------------------------------ #
    # Architecture, endianness and permissions
    # ------------------------------------------------------------------ #
    def test_check_products_binary_kernel_runs_endianness_not_text_checks(
            self, mocker, tmp_path) -> None:
        # A binary kernel (extension starting with 'b', e.g. '.bsp') skips
        # the text checks entirely, but still runs architecture and endianness.
        mocks = self.patch_checks(mocker)
        product = 'maven_orbit.bsp'
        expected_path = self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        kernel_list.check_products()

        mocks.check_eol.assert_not_called()
        mocks.check_badchar.assert_not_called()
        mocks.check_line_length.assert_not_called()
        mocks.check_kernel_integrity.assert_called_once_with(expected_path)
        mocks.check_binary_endianness.assert_called_once_with(
            expected_path, endianness='little')

    @pytest.mark.parametrize('product, failing_check, error_text, log_line', [
        ('maven_test.tsc', 'check_eol', 'Wrong EOL', '     Wrong EOL'),
        ('maven_test.tsc', 'check_kernel_integrity', 'Bad architecture',
         '     Bad architecture'),
        ('maven_orbit.bsp', 'check_binary_endianness', 'Wrong endianness',
         '     Wrong endianness')])
    def test_check_products_error_findings_are_fatal(
            self, mocker, caplog, tmp_path, product, failing_check,
            error_text, log_line) -> None:
        # Any check that returns an error string for a regular kernel must be
        # logged at ERROR level and cause RuntimeError via handle_npb_error.
        # The three error-producing checks are parametrized to prove they share
        # the same fatal path without duplicating the test body.
        mocks = self.patch_checks(mocker, **{failing_check: error_text})
        self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product])

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError, match=_CHECK_FATAL_MESSAGE):
                kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.ERROR, f'{log_line}'),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- {_CHECK_FATAL_MESSAGE}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        mocks.kclear.assert_called_once()

    def test_check_products_calls_permissions_twice(
            self, mocker, caplog, _text_kernel) -> None:
        # TODO: BUG; 'check_products' calls 'check_permissions' twice on
        #       the same path.
        kernel_list, expected_path = _text_kernel
        mocks = self.patch_checks(mocker, check_permissions=['not readable'])

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        expected = [
            (logging.WARNING, '-- maven_test.tsc'),
            (logging.WARNING, '     not readable')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

        assert mocks.check_permissions.call_count == 2
        assert mocks.check_permissions.call_args_list == [
            mocker.call(expected_path), mocker.call(expected_path)]

        mocks.kclear.assert_not_called()

    # ------------------------------------------------------------------ #
    # Reporting: logging
    # ------------------------------------------------------------------ #
    def test_check_products_logs_header_then_warnings_then_errors_in_order(
            self, mocker, caplog, _text_kernel) -> None:
        # Verify the logging side of reporting end to end for a single product:
        # header at WARNING, then each warning at WARNING, then each error at
        # ERROR, then the empty ERROR line from handle_npb_error, and finally
        # handle_npb_error's own fatal line at ERROR.
        kernel_list, _ = _text_kernel
        self.patch_checks(mocker, check_eol='Wrong EOL',
                          check_badchar=['bad char'])

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError):
                kernel_list.check_products()

        expected = [
            (logging.WARNING, '-- maven_test.tsc'),
            (logging.WARNING, '     bad char'),
            (logging.ERROR, '     Wrong EOL'),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- {_CHECK_FATAL_MESSAGE}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_check_products_logs_success_when_clean(
            self, mocker, caplog, _text_kernel) -> None:
        # A clean product produces neither warnings nor errors, so the success
        # branch logs the message at INFO followed by an empty INFO line, and
        # no per-product header is emitted.
        kernel_list, _ = _text_kernel
        self.patch_checks(mocker)

        with caplog.at_level(logging.INFO):
            kernel_list.check_products()

        expected = [(logging.INFO, _CHECK_SUCCESS_MESSAGE),
                    (logging.INFO, '')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_check_products_multiple_products_report_independently(
            self, mocker, caplog, tmp_path) -> None:
        # With several products, the per-product accumulation must stay
        # isolated: a clean kernel emits nothing, a warning-only kernel emits
        # a header plus its warning, and an error kernel raises RuntimeError.
        # This guards against state leaking between products in the loop.
        clean = 'maven_clean.tsc'
        warned = 'maven_warned.tsc'
        failed = 'maven_failed.tsc'
        for name in (clean, warned, failed):
            self.write_kernel(tmp_path, name)

        warned_path = str(tmp_path / 'kernels' / warned)
        failed_path = str(tmp_path / 'kernels' / failed)

        mocks = self.patch_checks(mocker)
        # 'side_effect' discriminates by path so state cannot bleed between
        # products: only the warned path gets a badchar result, only the failed
        # path gets an EOL error.
        mocks.check_badchar.side_effect = (
            lambda path: ['bad char'] if path == warned_path else [])
        mocks.check_eol.side_effect = (
            lambda path, eol: 'Wrong EOL' if path == failed_path else None)

        kernel_list = self.make_kernel_list(
            tmp_path, kernels=[clean, warned, failed])

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError, match=_CHECK_FATAL_MESSAGE):
                kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {warned}'),
            (logging.WARNING, '     bad char'),
            (logging.WARNING, f'-- {failed}'),
            (logging.ERROR, '     Wrong EOL'),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- {_CHECK_FATAL_MESSAGE}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    # ------------------------------------------------------------------ #
    # Reporting: standard output
    # ------------------------------------------------------------------ #
    def test_check_products_stdout_prints_warnings_when_interactive(
            self, mocker, capsys, tmp_path) -> None:
        # When neither 'silent' nor 'verbose' is set, the standard-output
        # block is produced. A warning-only product is used so no RuntimeError
        # is raised.
        self.patch_checks(mocker, check_badchar=['bad char'])
        product = 'maven_test.tsc'
        self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product],
                                            silent=False, verbose=False)

        kernel_list.check_products()

        captured = capsys.readouterr().out
        assert f'   * {product}' in captured
        assert '     bad char' in captured

    @pytest.mark.parametrize('silent, verbose', [
        (True, False), (False, True)])
    def test_check_products_stdout_suppressed_when_not_interactive(
            self, mocker, capsys, tmp_path, silent, verbose) -> None:
        # When either 'silent' or 'verbose' is set, nothing is printed to
        # standard output. A warning-only product is used so no RuntimeError
        # is raised. Absence is asserted on the concrete lines to avoid
        # accidental matches on the product name.
        self.patch_checks(mocker, check_badchar=['bad char'])
        product = 'maven_test.tsc'
        self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product],
                                            silent=silent, verbose=verbose)

        kernel_list.check_products()

        captured = capsys.readouterr().out
        assert f'   * {product}' not in captured
        assert '     bad char' not in captured

    def test_check_products_stdout_reports_errors_and_failure_line(
            self, mocker, caplog, tmp_path) -> None:
        # On an interactive run with errors, the method prints the product,
        # its error lines and the "require work" line, then raises RuntimeError.
        self.patch_checks(mocker, check_kernel_integrity='Bad arch')
        product = 'maven_test.tsc'
        self.write_kernel(tmp_path, product)
        kernel_list = self.make_kernel_list(tmp_path, kernels=[product],
                                            silent=False, verbose=False)
        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError, match=_CHECK_FATAL_MESSAGE):
                kernel_list.check_products()

        expected = [
            (logging.WARNING, f'-- {product}'),
            (logging.ERROR, '     Bad arch'),
            (logging.ERROR, ''),
            (logging.ERROR, f'-- {_CHECK_FATAL_MESSAGE}')]

        results = [(r[1], r[2]) for r in caplog.record_tuples]

        assert results == expected

    def test_check_products_success_stdout_printed_when_interactive(
            self, mocker, capsys, _text_kernel) -> None:
        # On an interactive (non-silent, non-verbose) run the success message
        # is printed to standard output.
        kernel_list, _ = _text_kernel
        kernel_list.setup.args.silent = False
        self.patch_checks(mocker)

        kernel_list.check_products()

        assert capsys.readouterr().out == _CHECK_SUCCESS_MESSAGE + '\n'

    def test_check_products_success_stdout_suppressed_when_silent(
            self, mocker, capsys, _text_kernel) -> None:
        # In silent mode the success message is only logged; stdout is empty.
        kernel_list, _ = _text_kernel
        # The fixture already builds the instance with silent=True.
        self.patch_checks(mocker)

        kernel_list.check_products()

        assert capsys.readouterr().out == ''
