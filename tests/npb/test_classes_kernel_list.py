"""Tests for KernelList class."""
import re
from datetime import datetime as real_datetime
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
