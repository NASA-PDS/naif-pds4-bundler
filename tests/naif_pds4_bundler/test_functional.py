"""Functional Test Family for InSight Archive Generation."""
import os
import shutil
import tempfile
import unittest
from unittest import TestCase

import functional.test_bc as bc
import functional.test_dart as dart
import functional.test_insight as insight
import functional.test_ladee as ladee
import functional.test_m2020 as m2020
import functional.test_maven as maven
import functional.test_mro as mro
from pds.naif_pds4_bundler.utils import add_crs_to_file


class TestFunctional(TestCase):
    """Functional Test Family Class."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        cls.test_dir = os.path.dirname(__file__)
        cls.silent = True
        cls.verbose = False
        cls.log = True
        cls.tmp_dir = tempfile.TemporaryDirectory()

        shutil.copytree(
            os.sep.join(cls.test_dir.split(os.sep)),
            cls.tmp_dir.name + "/naif_pds4_bundler",
        )
        shutil.copytree(
            os.sep.join(cls.test_dir.split(os.sep)[:-2])
            + "/src/pds/naif_pds4_bundler/templates/1.5.0.0",
            cls.tmp_dir.name + "/naif_pds4_bundler/templates/1.5.0.0",
        )

        tests_dir = cls.tmp_dir.name + "/naif_pds4_bundler/functional/"
        print(f"      Tests data on: {cls.tmp_dir.name}")
        os.chdir(tests_dir)

        #
        # The ORBNUM files that are supposed to have CRLF are updated here.
        # The reason is to avoid issues with Git LF to CRLF updates: The
        # repository only contains files with LF line endings.
        #
        files = [
            f"{tests_dir}../data/misc/orbnum/maven_orb_rec_210101_210401.orb",
            f"{tests_dir}../data/misc/orbnum/maven_orb_rec_210101_210401_v1.orb",
            f"{tests_dir}../data/misc/orbnum/maven_orb_rec_210101_210401_v2.orb",
            f"{tests_dir}../data/misc/orbnum/maven_orb_rec_210101_210401_v3.orb",
        ]
        for file in files:
            add_crs_to_file(file, "\r\n")

    @classmethod
    def tearDownClass(cls):
        """Destructor.

        Method that will be executed once for this test case class.
        It will execute after all tests methods.

        Clears up the functional test directory.
        """
        cls.tmp_dir.cleanup()

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "misc", "ladee", "mars2020", "dart", "orex", "bc"]
        for dir in dirs:
            try:
                os.makedirs(dir, exist_ok=True)
            except BaseException:
                pass

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)
        test_dir = self.tmp_dir.name + "/naif_pds4_bundler/functional/"
        dirs = next(os.walk(test_dir))[1]
        for dir in dirs:
            shutil.rmtree(test_dir + dir)

    #
    # InSight functional tests.
    #
    def test_insight_basic(self):
        insight.test_insight_basic(self)

    def test_insight_diff_previous_none(self):
        insight.test_insight_diff_previous_none(self)

    def test_insight_diff_previous_all(self):
        insight.test_insight_diff_previous_all(self)

    def test_insight_diff_previous_files(self):
        insight.test_insight_diff_previous_files(self)

    def test_insight_diff_previous_log(self):
        insight.test_insight_diff_previous_log(self)

    def test_insight_diff_templates(self):
        insight.test_insight_diff_templates(self)

    def test_insight_files_in_staging(self):
        insight.test_insight_files_in_staging(self)

    def test_insight_previous_spiceds(self):
        insight.test_insight_previous_spiceds(self)

    def test_insight_start_finish(self):
        insight.test_insight_start_finish(self)

    def test_insight_incorrect_times(self):
        insight.test_insight_incorrect_times(self)

    def test_insight_mk_input(self):
        insight.test_insight_mk_input(self)

    def test_insight_mks_input(self):
        insight.test_insight_mks_input(self)

    def test_insight_mks_inputs_coverage(self):
        insight.test_insight_mks_inputs_coverage(self)

    def test_insight_mks_coverage_in_final(self):
        insight.test_insight_mks_coverage_in_final(self)

    def test_insight_generate_mk(self):
        insight.test_insight_generate_mk(self)

    def test_insight_no_spiceds_in_conf(self):
        insight.test_insight_no_spiceds_in_conf(self)

    def test_insight_no_spiceds(self):
        insight.test_insight_no_spiceds(self)

    def test_insight_no_readme(self):
        insight.test_insight_no_readme(self)

    def test_insight_no_readme_in_config(self):
        insight.test_insight_no_readme_in_config(self)

    def test_insight_readme_incomplete_in_config(self):
        insight.test_insight_readme_incomplete_in_config(self)

    def test_insight_no_kernels(self):
        insight.test_insight_no_kernels(self)

    def test_insight_no_kernels_with_bundle(self):
        insight.test_insight_no_kernels_with_bundle(self)

    def test_insight_only_checksums(self):
        insight.test_insight_only_checksums(self)

    def test_insight_extra_mk_pattern(self):
        insight.test_insight_extra_mk_pattern(self)

    def test_insight_increment_with_misc(self):
        insight.test_insight_increment_with_misc(self)

    #   def test_insight_missing_bundle_directory(self):
    #       insight.test_insight_missing_bundle_directory(self)

    def test_insight_missing_staging_directory_nok(self):
        insight.test_insight_missing_staging_directory_nok(self)

    def test_insight_flat_kernel_directory(self):
        insight.test_insight_flat_kernel_directory(self)

    #    def test_insight_multiple_kernel_directory(self):
    #        insight.test_insight_multiple_kernel_directory(self)

    #
    # LADEE functional tests.
    #
    def test_ladee_update_input_mk_name(self):
        ladee.test_ladee_update_input_mk_name(self)

    def test_ladee_checksum_registry(self):
        ladee.test_ladee_checksum_registry(self)

    def test_ladee_date_format(self):
        ladee.test_ladee_date_format(self)

    def test_ladee_label_mode(self):
        ladee.test_ladee_label_mode(self)

    def test_ladee_label_mode_ker_input(self):
        ladee.test_ladee_label_mode_ker_input(self)

    def test_ladee_label_mode_plan_input(self):
        ladee.test_ladee_label_mode_plan_input(self)

    def test_ladee_label_mode_ker_bun_dir(self):
        ladee.test_ladee_label_mode_ker_bun_dir(self)

    #
    # Mars 2020 functional tests.
    #
    def test_m2020_mks_inputs_coverage(self):
        m2020.test_m2020_mks_inputs_coverage(self)

    def test_m2020_kernel_list(self):
        m2020.test_m2020_kernel_list(self)

    def test_m2020_kernel_list_dir(self):
        m2020.test_m2020_kernel_list_dir(self)

    def test_m2020_duplicated_kernel(self):
        m2020.test_m2020_duplicated_kernel(self)

    def test_m2020_spk_with_unrelated_id(self):
        m2020.test_m2020_spk_with_unrelated_id(self)

    def test_m2020_incorrect_mission_times(self):
        m2020.test_m2020_incorrect_mission_times(self)

    def test_m2020_incorrect_start_time(self):
        m2020.test_m2020_incorrect_start_time(self)

    def test_m2020_increment_start_time(self):
        m2020.test_m2020_increment_start_time(self)

    def test_m2020_increment_finish_time(self):
        m2020.test_m2020_increment_finish_time(self)

    def test_m2020_mks_incorrect_path(self):
        m2020.test_m2020_mks_incorrect_path(self)

    def test_m2020_empty_spk(self):
        m2020.test_m2020_empty_spk(self)

    def test_m2020_kernel_list_checks(self):
        m2020.test_m2020_kernel_list_checks(self)

    def test_m2020_multiple_kernel_directories(self):
        m2020.test_m2020_multiple_kernel_directories(self)

    #
    # MAVEN functional tests.
    #
    def test_maven_mks_input(self):
        maven.test_maven_mks_input(self)

    def test_maven_mks_list(self):
        maven.test_maven_mks_list(self)

    def test_maven_mks_list_in_kernels(self):
        maven.test_maven_mks_list_in_kernels(self)

    def test_maven_mks_list_config_in_kernels(self):
        maven.test_maven_mks_list_config_in_kernels(self)

    def test_maven_mks_list_config_in_kernels_and_config(self):
        maven.test_maven_mks_list_config_in_kernels_and_config(self)

    def test_maven_no_mk(self):
        maven.test_maven_no_mk(self)

    def test_maven_generate_mk(self):
        maven.test_maven_generate_mk(self)

    def test_maven_increment_times_from_yearly_mks(self):
        maven.test_maven_increment_times_from_yearly_mks(self)

    def test_maven_load_kernels(self):
        maven.test_maven_load_kernels(self)

    #
    # DART functional tests.
    #
    def test_dart_multiple_obs_tar(self):
        dart.test_dart_multiple_obs_tar(self)

    def test_dart_host_type(self):
        dart.test_dart_host_type(self)

    #
    # BepiColombo functional tests.
    #
    def test_bc_multiple_obs_tar(self):
        bc.test_bc_multiple_obs_tar(self)

    #
    # MRO functional tests.
    #
    def test_mro_basic(self):
        mro.test_mro_basic(self)


if __name__ == "__main__":
    unittest.main()
