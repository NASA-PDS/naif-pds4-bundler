"""Tests for KernelList class."""
from datetime import datetime as real_datetime
from types import SimpleNamespace

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


def make_kernel_list_setup(tmp_path, pds_version='4',
                           data_set_id='MAVEN-SPICE-KERNELS-V1.0',
                           volid='MAVEN_1001', release='3') -> SimpleNamespace:
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

    return setup


class TestKernelListInit:

    @pytest.fixture(autouse=True)
    def patch_datetime_and_read_config(self, mocker):
        # Helper that runs automatically before each test to mock the calls to
        # datetime.datetime.now() and KernelList.read_config().

        # Mock datetime.now to set a static date to run the tests.
        mock_dt = mocker.patch('pds.naif_pds4_bundler.classes.list.datetime.datetime')
        mock_dt.now.return_value = real_datetime(2026, 5, 4, 12, 30, 0)

        # Mock KernelList.read_config
        self.read_config_mock = mocker.patch.object(KernelList, 'read_config', autospec=True)

    @pytest.mark.parametrize(['pds_version', 'dataset_i', 'dataset_o', 'volid_i', 'volid_o'], [
        ('4', 'MAVEN-SPICE-KERNELS-V1.0', 'N/A', 'N/A', 'N/A'),
        ('3', '"maven-spice-kernels-v1.0"', 'MAVEN-SPICE-KERNELS-V1.0', 'maven_1001', 'maven_1001'),
        ('3', 'maven-spice-kernels-v1.0', 'MAVEN-SPICE-KERNELS-V1.0', 'maven_1001', 'maven_1001'),
        ('3', '"MAVEN-SPICE-KERNELS-V1.0"', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN_1001', 'maven_1001'),
        ('3', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN-SPICE-KERNELS-V1.0', 'MAVEN_1001', 'maven_1001')])
    def test__init__(self, tmp_path, pds_version, dataset_i,
                     dataset_o, volid_i, volid_o) -> None:

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

        self.read_config_mock.assert_called_once_with(kernel_list)
