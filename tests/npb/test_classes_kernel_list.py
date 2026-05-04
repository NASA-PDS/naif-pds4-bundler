"""Tests for KernelList class."""
from datetime import datetime as real_datetime
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from pds.naif_pds4_bundler.classes.list import KernelList


def make_kernel_list_setup(tmp_path, pds_version='4',
                           data_set_id='MAVEN-SPICE-KERNELS-V1.0',
                           release='3') -> SimpleNamespace:
    # Create a minimal setup object to instance KernelList.
    setup = SimpleNamespace()

    setup.observer = 'MAVEN'
    setup.producer_name = 'NAIF'
    setup.pds_version = pds_version
    setup.pds3_mission_template = {'DATA_SET_ID': data_set_id}
    setup.volume_id = 'MAVEN_1001'
    setup.release = release
    setup.release_date = '2026-05-04'
    setup.templates_directory = str(tmp_path / 'templates')

    return setup


class TestKernelListInit:

    @pytest.fixture(autouse=True)
    def patch_datetime_and_read_config(self):
        # Helper that runs automatically before each test to mock the calls to
        # datetime.datetime.now() and KernelList.read_config().

        # Mock datetime.now to set a static date to run the tests.
        with patch('pds.naif_pds4_bundler.classes.list.datetime.datetime') as datetime_mock:

            datetime_mock.now.return_value = real_datetime(2026, 5, 4, 12, 30, 0)

            # Mock the read.config call.
            with patch.object(KernelList, 'read_config', autospec=True) as read_config_mock:
                self.read_config_mock = read_config_mock

                yield

    def test_initializes_common_attributes_and_pds4_defaults(self,
                                                             tmp_path) -> None:

        # Build a setup for PDS4.
        setup = make_kernel_list_setup(tmp_path, pds_version='4', release='3')

        kernel_list = KernelList(setup)

        # Check that the PDS4 setup arguments are correct.
        assert kernel_list.complete_list == ''
        assert kernel_list.files == []
        assert kernel_list.kernel_list == []
        assert kernel_list.list_name == ''
        assert kernel_list.setup is setup

        assert kernel_list.CURRENTDATE == '2026-05-04'
        assert kernel_list.OBS == 'MAVEN'
        assert kernel_list.AUTHOR == 'NAIF'

        assert kernel_list.DATA_SET_ID == 'N/A'
        assert kernel_list.VOLID == 'N/A'

        assert kernel_list.RELID == '0003'
        assert kernel_list.RELDATE == '2026-05-04'
        assert (
            kernel_list.template ==
            f'{setup.templates_directory}/template_kernel_list.txt'
        )

        self.read_config_mock.assert_called_once_with(kernel_list)

    def test_initializes_pds3_data_set_id_from_quoted_template(self,
                                                               tmp_path) -> None:
        # Build a setup for PDS3 with a quoted dataset.
        setup = make_kernel_list_setup(tmp_path, pds_version='3',
                                       data_set_id='"maven-spice-kernels-v1.0"')

        kernel_list = KernelList(setup)

        # Check that the text within the quotation marks is extracted from the
        # data_set_id and converted to uppercase.
        assert kernel_list.DATA_SET_ID == 'MAVEN-SPICE-KERNELS-V1.0'

        # Check that VOLID has the same value as volume_id, but in lower case.
        assert kernel_list.VOLID == 'maven_1001'

        self.read_config_mock.assert_called_once_with(kernel_list)

    def test_initializes_pds3_data_set_id_from_unquoted_template(self,
                                                                 tmp_path) -> None:
        # Build a setup for PDS3 with an unquoted dataset.
        setup = make_kernel_list_setup(tmp_path, pds_version='3',
                                       data_set_id='maven-spice-kernels-v1.0')

        kernel_list = KernelList(setup)

        # Check that the entire dataset is used and converts it to uppercase.
        assert kernel_list.DATA_SET_ID == 'MAVEN-SPICE-KERNELS-V1.0'

        # Check that VOLID has the same value as volume_id, but in lower case.
        assert kernel_list.VOLID == 'maven_1001'

        self.read_config_mock.assert_called_once_with(kernel_list)
