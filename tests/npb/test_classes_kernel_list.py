"""Tests for KernelList class."""
import json
from datetime import datetime as real_datetime
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


def make_kernel_list_setup(tmp_path, pds_version='4',
                           data_set_id='MAVEN-SPICE-KERNELS-V1.0',
                           volid='MAVEN_1001', release='3',
                           kernel_list_config=None) -> SimpleNamespace:
    # Create a minimal setup object to instance KernelList.
    setup = SimpleNamespace()

    setup.observer = 'MAVEN'
    setup.producer_name = 'NAIF'
    setup.pds_version = pds_version
    setup.pds3_mission_template = {'DATA_SET_ID': data_set_id}
    setup.volume_id = volid
    setup.release = release
    setup.release_date = '2026-05-04'
    setup.templates_directory = str(tmp_path / 'templates')

    # Attribute to check a real call, instead of a mock.
    setup.kernel_list_config = {} if kernel_list_config is None else kernel_list_config

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
        read_config_mock = mocker.patch.object(
            KernelList, 'read_config', autospec=True
        )

        # Build a setup with input values.
        setup = make_kernel_list_setup(tmp_path, pds_version=pds_version,
                                       data_set_id=dataset_i, volid=volid_i,
                                       release='3')

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

        # Build a setup object for a KernelList.
        setup = make_kernel_list_setup(tmp_path, pds_version='4',
                                       kernel_list_config=json_config)

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
        assert (kernel_list.json_formatted_lst ==
                json.dumps(json_config, indent=2).split('\n'))
