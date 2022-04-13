"""Unit Test Family."""
import os
import shutil
import tempfile
import unittest
from unittest import TestCase

import spiceypy
import unittests.test_bundle_history as bundle_history
import unittests.test_checksums as checksums
import unittests.test_clear as clear
import unittests.test_endianness as endianness
import unittests.test_extract_comment as extract_comment
import unittests.test_files as files
import unittests.test_im_format as im_format
import unittests.test_kernel_integrity as kernel_integrity
import unittests.test_kernel_list as kernel_list
import unittests.test_match_patterns as match_patterns
import unittests.test_mk_config as mk_config
import unittests.test_orbnum as orbnum
import unittests.test_plan as plan
import unittests.test_readme as readme
import unittests.test_time as time


class TestUnitTests(TestCase):
    """Unit Test Family Class."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        cls.test_dir = os.path.dirname(__file__)
        cls.silent = True
        cls.faucet = "list"
        cls.verbose = False
        cls.log = True
        cls.tmp_dir = tempfile.TemporaryDirectory(dir="/Users/mcosta")

        shutil.copytree(os.sep.join(cls.test_dir.split(os.sep)),
                        cls.tmp_dir.name + '/naif_pds4_bundler')
        shutil.copytree(os.sep.join(cls.test_dir.split(os.sep)[:-2]) +
                        "/src/pds/naif_pds4_bundler/templates/1.5.0.0",
                        cls.tmp_dir.name + '/naif_pds4_bundler/templates/1.5.0.0')
        os.chdir(cls.tmp_dir.name + "/naif_pds4_bundler/unittests/")

    @classmethod
    def tearDownClass(cls):
        """Destructor.

        Method that will be executed once for this test case class.
        It will execute after all tests methods.

        Clears up the functional test directory.
        """
        spiceypy.kclear()
        cls.tmp_dir.cleanup()

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        dirs = ["working", "staging", "kernels", "ladee", "insight",
                "msl-m-spice-6-v1.0", "bundle", "insight", "maven",
                "mars2020", "orex", "vco", "hyb2"]
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
        dirs = next(os.walk('.'))[1]
        for dir in dirs:
            try:
                shutil.rmtree(dir, ignore_errors=True)
            except BaseException:
                pass

    #
    # Bundle history tests.
    #
    def test_insight_history(self):
        bundle_history.test_insight_history(self)

    #
    # Checksum tests.
    #
    def test_checksum_from_record(self):
        checksums.test_checksum_from_record(self)

    def test_checksum_from_labels(self):
        checksums.test_checksum_from_labels(self)

    #
    # Clear previous execution tests.
    #
    def test_insight_basic(self):
        clear.test_insight_basic(self)

    def test_insight_error(self):
        clear.test_insight_error(self)

    def test_clear_label_mode(self):
        clear.test_clear_label_mode(self)

    #
    # Extract comment tests.
    #
    def test_ck(self):
        extract_comment.test_ck(self)

    #
    # File utilities tests.
    #
    def test_mk_to_list(self):
       files.test_mk_to_list(self)

    #
    # Information Model tests.
    #
    def test_im_format(self):
        im_format.test_im_format(self)

    def test_im_xml_incoherent(self):
        im_format.test_im_xml_incoherent(self)

    def test_im_schema_incoherent(self):
        im_format.test_im_schema_incoherent(self)

    def test_im_version_ascii(self):
        im_format.test_im_version_ascii(self)

    def test_im_version_ascii_incorrect(self):
        im_format.test_im_version_ascii_incorrect(self)

    def test_im_templates_16(self):
        im_format.test_im_templates_16(self)

    def test_im_templates_14(self):
        im_format.test_im_templates_14(self)

    def test_im_templates_11(self):
        im_format.test_im_templates_11(self)

    def test_im_templates(self):
        im_format.test_im_templates(self)

    #
    # Binary kernel endianness tests.
    #
    def test_pds4_big_endianness(self):
        endianness.test_pds4_big_endianness(self)

    def test_pds4_big_endianness_config(self):
        endianness.test_pds4_big_endianness_config(self)

    def test_pds4_ltl_endianness(self):
        endianness.test_pds4_ltl_endianness(self)

    def test_pds4_ltl_endianness_config(self):
        endianness.test_pds4_ltl_endianness_config(self)

    def test_pds3_ltl_endianness(self):
        endianness.test_pds3_ltl_endianness(self)

    def test_pds3_ltl_endianness_config(self):
        endianness.test_pds3_ltl_endianness_config(self)

    def test_pds3_big_endianness(self):
        endianness.test_pds3_big_endianness(self)

    #
    # Kernel integrity tests.
    #
    def test_text_kernel_integrity(self):
        kernel_integrity.test_text_kernel_integrity(self)

    def test_binary_kernel_integrity(self):
        kernel_integrity.test_binary_kernel_integrity(self)

    #
    # Kernel list tests.
    #
    def test_pds3_msl_list(self):
        kernel_list.test_pds3_msl_list(self)

    def test_pds3_m01_list(self):
        kernel_list.test_pds3_m01_list(self)

    def test_pds3_mro_list(self):
        kernel_list.test_pds3_mro_list(self)

    def test_pds4_insight_list(self):
        kernel_list.test_pds4_insight_list(self)

    def test_pds4_maven_list(self):
        kernel_list.test_pds4_maven_list(self)

    def test_pds4_mars2020_list(self):
        kernel_list.test_pds4_mars2020_list(self)

    def test_pds4_orex_list(self):
        kernel_list.test_pds4_orex_list(self)

    def test_pds3_juno_list(self):
        kernel_list.test_pds3_juno_list(self)

    def test_pds4_vco_list(self):
        kernel_list.test_pds4_vco_list(self)

    def test_pds4_hyb2_list(self):
        kernel_list.test_pds4_hyb2_list(self)

    def test_xml_reader(self):
        kernel_list.test_xml_reader(self)

    #
    # Match patterns tests.
    #
    def test_match_patterns_basic(self):
        match_patterns.test_match_patterns_basic(self)

    #
    # Meta-kernel configuration tests.
    #
    def test_insight_mk_error_extra_pattern(self):
        mk_config.test_insight_mk_error_extra_pattern(self)

    def test_insight_mk_error_wrong_name(self):
        mk_config.test_insight_mk_error_wrong_name(self)

    def test_insight_mk_double_keyword_in_pattern(self):
        mk_config.test_insight_mk_double_keyword_in_pattern(self)

    def test_insight_mk_double_keyword_in_pattern_no_gen(self):
        mk_config.test_insight_mk_double_keyword_in_pattern_no_gen(self)

    #
    # ORBNUM label generation tests.
    #
    def test_pds4_orbnum_coverage_user_spk(self):
        orbnum.test_pds4_orbnum_coverage_user_spk(self)

    def test_pds4_orbnum_coverage_increment_spk(self):
        orbnum.test_pds4_orbnum_coverage_increment_spk(self)

    def test_pds4_orbnum_coverage_archived_spk(self):
        orbnum.test_pds4_orbnum_coverage_archived_spk(self)

    def test_pds4_orbnum_coverage_lookup_table(self):
        orbnum.test_pds4_orbnum_coverage_lookup_table(self)

    def test_pds4_orbnum_coverage_lookup_table_multiple(self):
        orbnum.test_pds4_orbnum_coverage_lookup_table_multiple(self)

    def test_pds4_orbnum_coverage_estimate(self):
        orbnum.test_pds4_orbnum_coverage_estimate(self)

    def test_pds4_orbnum_with_former_version(self):
        orbnum.test_pds4_orbnum_with_former_version(self)

    def test_pds4_orbnum_with_former(self):
        orbnum.test_pds4_orbnum_with_former(self)

    def test_pds4_orbnum_blank_records(self):
        orbnum.test_pds4_orbnum_blank_records(self)

    def test_pds4_orbnum_blank_records_no_former(self):
        orbnum.test_pds4_orbnum_blank_records_no_former(self)

    def test_pds4_orbnum_blank_records_no_version(self):
        orbnum.test_pds4_orbnum_blank_records_no_version(self)

    def test_pds3_orbnum_files(self):
        orbnum.test_pds3_orbnum_files(self)

    def test_pds4_orbnum_eol_line_feed(self):
        orbnum.test_pds4_orbnum_eol_line_feed(self)

    def test_pds4_orbnum_generated_list(self):
        orbnum.test_pds4_orbnum_generated_list(self)

    def test_pds4_orbnum_multiple_files(self):
        orbnum.test_pds4_orbnum_multiple_files(self)

    def test_pds4_orbnum_multiple_files_incorrect_spk(self):
        orbnum.test_pds4_orbnum_multiple_files_incorrect_spk(self)

    def test_pds4_orbnum_multiple_files_in_spk_dir(self):
        orbnum.test_pds4_orbnum_multiple_files_in_spk_dir(self)

    def test_pds4_orbnum_new_im(self):
        orbnum.test_pds4_orbnum_new_im(self)

    #
    # Plan generation test.
    #
    def test_pds4_insight_plan(self):
        plan.test_pds4_insight_plan(self)

    def test_pds4_mars2020_no_plan(self):
        plan.test_pds4_mars2020_no_plan(self)

    #
    # Readme generation.
    #
    def test_im_format(self):
        readme.test_im_format(self)

    def test_im_xml_incoherent(self):
        readme.test_im_xml_incoherent(self)

    def test_im_schema_incoherent(self):
        readme.test_im_schema_incoherent(self)

    def test_im_version_ascii(self):
        readme.test_im_version_ascii(self)

    def test_im_version_ascii_incorrect(self):
        readme.test_im_version_ascii_incorrect(self)

    #
    # Time utilities tests.
    #
    def test_dsk_coverage(self):
        time.test_dsk_coverage(self)

    def test_spk_coverage(self):
        time.test_spk_coverage(self)


if __name__ == "__main__":
    unittest.main()
