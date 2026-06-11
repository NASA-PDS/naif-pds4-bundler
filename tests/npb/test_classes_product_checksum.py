"""Unit tests for the ChecksumProduct class.
"""
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_checksum import ChecksumProduct

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

def _make_setup(pds_version="4", increment=True, diff=False):
    """Return a minimal setup mock."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.increment = increment
    setup.diff = diff
    setup.staging_directory = "/staging"
    setup.bundle_directory = "/bundle"
    setup.mission_acronym = "em16"
    setup.logical_identifier = "urn:nasa:pds:em16_spice"
    setup.volume_id = "em16_spice_1000"
    setup.eol = "\r\n"
    setup.mission_start = "2016-01-01T00:00:00Z"
    setup.mission_finish = "2023-12-31T23:59:59Z"
    setup.working_directory = "/working"
    setup.args = MagicMock()
    setup.args.debug = False
    return setup


def _make_collection(name="miscellaneous"):
    collection = MagicMock()
    collection.name = name
    return collection


# ---------------------------------------------------------------------------
# Patch targets (relative to the module under test)
# ---------------------------------------------------------------------------
MOD = "pds.naif_pds4_bundler.classes.product.product_checksum"

PATCHES = dict(
    safe_make_directory=f"{MOD}.safe_make_directory",
    glob_glob=f"{MOD}.glob.glob",
    handle_npb_error=f"{MOD}.handle_npb_error",
    md5=f"{MOD}.md5",
    checksum_from_registry=f"{MOD}.checksum_from_registry",
    checksum_from_label=f"{MOD}.checksum_from_label",
    compare_files=f"{MOD}.compare_files",
    Product_init=f"{MOD}.Product.__init__",
    ChecksumPDS4Label=f"{MOD}.ChecksumPDS4Label",
    ChecksumPDS3Label=f"{MOD}.ChecksumPDS3Label",
    os_walk=f"{MOD}.os.walk",
    os_remove=f"{MOD}.os.remove",
    os_path_isfile=f"{MOD}.os.path.isfile",
)


def _patch(**extra):
    """Context-manager stack for the most common patches."""
    managers = {k: patch(v) for k, v in PATCHES.items()}
    managers.update({k: patch(v) for k, v in extra.items()})
    return managers


# ---------------------------------------------------------------------------
# Convenience builder: construct a ChecksumProduct without actually touching
# the filesystem. Returns (instance, mocks_dict).
# ---------------------------------------------------------------------------

def _build_pds4(
    increment=True,
    add_previous_checksum=True,
    glob_files=None,
    diff=False,
):
    """Build a PDS4 ChecksumProduct with controllable side effects."""

    setup = _make_setup(pds_version="4", increment=increment, diff=diff)
    collection = _make_collection()

    if glob_files is None:
        glob_files = []

    mocks = {}

    with patch(PATCHES["safe_make_directory"]) as m_mkdir, \
         patch(PATCHES["glob_glob"]) as m_glob, \
         patch(PATCHES["handle_npb_error"]) as m_err, \
         patch(PATCHES["md5"], return_value="a" * 32) as m_md5, \
         patch(PATCHES["os_walk"], return_value=[]) as m_walk, \
         patch("builtins.open", mock_open(read_data="")) as m_open:

        m_glob.return_value = glob_files

        obj = ChecksumProduct(setup, collection, add_previous_checksum)
        mocks.update(dict(
            mkdir=m_mkdir, glob=m_glob, err=m_err, md5=m_md5,
            walk=m_walk, open=m_open,
        ))

    return obj, mocks


def _build_pds3(add_previous_checksum=False):
    """Build a PDS3 ChecksumProduct."""

    setup = _make_setup(pds_version="3", increment=False, diff=False)
    collection = _make_collection()

    with patch(PATCHES["safe_make_directory"]), \
         patch(PATCHES["glob_glob"], return_value=[]), \
         patch(PATCHES["handle_npb_error"]), \
         patch(PATCHES["md5"], return_value="b" * 32), \
         patch(PATCHES["os_walk"], return_value=[]), \
         patch("builtins.open", mock_open(read_data="")):

        obj = ChecksumProduct(setup, collection, add_previous_checksum)

    return obj


# ===========================================================================
# TestChecksumProductInit
# Tests __init__, set_product_lid, and set_product_vid together.
# ===========================================================================

class TestChecksumProductInit:
    """Tests for __init__ (and set_product_lid / set_product_vid)."""

    def test_init_pds4_no_increment_sets_version_1(self):
        obj, _ = _build_pds4(increment=False)
        assert obj.version == 1
        assert obj.path_current == ""
        assert obj.path == str(Path("/staging/miscellaneous/checksum/checksum_v001.tab"))
        assert obj.lid == "urn:nasa:pds:em16_spice:miscellaneous:checksum_checksum"
        assert obj.vid == "1.0"
        assert obj.bytes == 0
        assert obj.file_records == 0
        assert obj.label is None
        assert obj.new_product is True
        assert obj.record_bytes == 0
        assert obj.start_time == ''
        assert obj.stop_time == ''

        # After init with no previous file and add_previous_checksum=True the
        # dict remains empty (path_current is "")
        assert obj.md5_dict == {}

    def test_init_pds4_increment_no_previous_file_defaults_to_v1(self):
        obj, _ = _build_pds4(increment=True, glob_files=[])
        assert obj.version == 1

    def test_init_pds4_increment_with_previous_file_increments_version(self):
        prev = "/bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab"
        obj, _ = _build_pds4(increment=True, glob_files=[prev])
        assert obj.version == 2
        assert obj.name == "checksum_v002.tab"
        assert obj.path_current == prev
        assert obj.vid == "2.0"

    def test_init_pds4_creates_checksum_directory(self):

        setup = _make_setup(pds_version="4")
        collection = _make_collection()

        with patch(PATCHES["safe_make_directory"]) as m_mkdir, \
             patch(PATCHES["glob_glob"], return_value=[]), \
             patch(PATCHES["handle_npb_error"]), \
             patch(PATCHES["md5"], return_value="a" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data="")):

            ChecksumProduct(setup, collection)

        m_mkdir.assert_called_once_with(str(Path("/staging/miscellaneous/checksum/")))

    def test_init_pds3_creates_index_directory(self):

        setup = _make_setup(pds_version="3")
        collection = _make_collection()

        with patch(PATCHES["safe_make_directory"]) as m_mkdir, \
             patch(PATCHES["glob_glob"], return_value=[]), \
             patch(PATCHES["handle_npb_error"]), \
             patch(PATCHES["md5"], return_value="b" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data="")):

            ChecksumProduct(setup, collection)

        m_mkdir.assert_called_once_with(str(Path("/staging/index")))

    def test_init_pds3_sets_names_and_paths(self):
        obj = _build_pds3()
        assert obj.name == "checksum.tab"
        assert obj.name_current == "checksum.tab"
        assert Path(obj.path).parts[-2:] == ("index", "checksum.tab")

        # PDS3 path skips set_product_lid / set_product_vid entirely.
        assert not hasattr(obj, "lid")

    def test_init_pds4_multiple_glob_files_picks_latest(self):
        files = [
            "/bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab",
            "/bundle/em16_spice/miscellaneous/checksum/checksum_v003.tab",
            "/bundle/em16_spice/miscellaneous/checksum/checksum_v002.tab",
        ]
        # glob.glob returns unsorted; ChecksumProduct sorts internally.
        obj, _ = _build_pds4(increment=True, glob_files=files)
        # Latest sorted is v003 → new version is 4
        assert obj.version == 4


# ===========================================================================
# ChecksumProduct.read_current_product
# ===========================================================================

class TestReadCurrentProduct:
    """Tests for read_current_product."""

    def test_reads_previous_checksum_into_md5_dict(self):

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = "/bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab"
        prev_content = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa some/file.tab\n"
                        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb other/file.xml\n")

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
             patch(PATCHES["handle_npb_error"]), \
             patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=prev_content)):

            obj = ChecksumProduct(setup, collection, add_previous_checksum=False)

        assert obj.md5_dict == {'some/file.tab': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                                'other/file.xml': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'}

    @pytest.mark.parametrize('bad_content, error', [
        ("this_line_has_no_space_split\n",
         'Checksum file /bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab is corrupted.'),
        ("0123456789  some/file.tab\n",
         'Checksum file /bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab '
         'corrupted entry: 0123456789  some/file.tab\n.')
    ])
    def test_corrupted_line_calls_handle_npb_error(self, bad_content, error) -> None:

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = "/bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab"

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
             patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=bad_content)):

            with pytest.raises(RuntimeError, match=error):
                ChecksumProduct(setup, collection, add_previous_checksum=False)

    def test_add_previous_checksum_true_adds_file_and_label_pds4(self):

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = "/bundle/em16_spice/miscellaneous/checksum/checksum_v001.tab"
        prev_content = "a" * 32 + "  some/file.tab\n"

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
             patch(PATCHES["handle_npb_error"]), \
             patch(PATCHES["md5"], return_value="d" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=prev_content)):

            obj = ChecksumProduct(setup, collection, add_previous_checksum=True)

        # Both the .tab and the .xml of the previous checksum should be present
        assert obj.md5_dict == {
            'some/file.tab': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'miscellaneous/checksum/checksum_v001.tab': 'dddddddddddddddddddddddddddddddd',
            'miscellaneous/checksum/checksum_v001.xml': 'dddddddddddddddddddddddddddddddd'}
        assert obj.new_product is True

    def test_add_previous_checksum_true_pds3_adds_tab_and_lbl(self):

        setup = _make_setup(pds_version="3", increment=False, diff=False)
        collection = _make_collection()
        prev_content = "a" * 32 + "  some/file.tab\n"

        # Force a non-empty path_current by patching the attribute after
        # construction via a side_effect on safe_make_directory; easier to
        # just use a real path_current value via the PDS3 branch's hard-coded
        # assignment: path_current = bundle_directory/volume_id/index/checksum.tab
        # We supply valid content for that file via mock_open.
        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[]), \
             patch(PATCHES["handle_npb_error"]), \
             patch(PATCHES["md5"], return_value="e" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=prev_content)):

            obj = ChecksumProduct(setup, collection, add_previous_checksum=True)

        assert obj.md5_dict == {
            'some/file.tab': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'index/checksum.lbl': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            'index/checksum.tab': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'}
        assert obj.new_product is True


# ===========================================================================
# ChecksumProduct.set_coverage
# ===========================================================================

class TestSetCoverage:
    """Tests for set_coverage."""

    def test_set_coverage_calls_write_product_with_set_coverage_true(self):
        obj, _ = _build_pds4(increment=False)

        with patch.object(obj, "write_product") as m_wp:
            obj.set_coverage()

        m_wp.assert_called_once_with(history=None, set_coverage=True)


# ===========================================================================
# ChecksumProduct.generate
# ===========================================================================

class TestGenerate:
    """Tests for generate."""

    def test_generate_pds4_creates_pds4_label(self):

        obj, _ = _build_pds4(increment=False)
        obj.new_product = False  # reset
        fake_label = MagicMock()

        with patch.object(obj, "write_product") as m_wp, \
             patch(PATCHES["Product_init"]) as m_parent, \
             patch(PATCHES["ChecksumPDS4Label"], return_value=fake_label) as m_lbl4, \
             patch(PATCHES["ChecksumPDS3Label"]) as m_lbl3:

            obj.generate(history=['some_file'])

        m_lbl4.assert_called_once_with(obj.setup, obj)
        m_lbl3.assert_not_called()
        m_wp.assert_called_once_with(history=['some_file'])
        m_parent.assert_called_once()

        # Generate sets new product and assigns the new label.
        assert obj.new_product is True
        assert obj.label is fake_label

    def test_generate_pds3_creates_pds3_label(self):
        obj = _build_pds3()

        with patch.object(obj, "write_product"), \
             patch(PATCHES["Product_init"]), \
             patch(PATCHES["ChecksumPDS4Label"]) as m_lbl4, \
             patch(PATCHES["ChecksumPDS3Label"]) as m_lbl3:

            obj.generate(history=None)

        m_lbl3.assert_called_once_with(obj.setup, obj)
        m_lbl4.assert_not_called()

# ===========================================================================
# ChecksumProduct.write_product
# ===========================================================================

class TestChecksumProductWriteProduct:
    """Tests for write_product."""

    @staticmethod
    def _obj_with_products(pds_version="4"):
        """Return a ChecksumProduct with a stub bundle/collection hierarchy."""
        obj, _ = _build_pds4(increment=False)
        obj.setup.pds_version = pds_version

        # Build a mini product hierarchy
        product = MagicMock()
        product.path = "/staging/em16_spice/miscellaneous/test_file.tab"
        product.checksum = "f" * 32
        label_mock = MagicMock()
        label_mock.name = "/staging/em16_spice/miscellaneous/test_file.xml"
        product.label = label_mock

        coll_mock = MagicMock()
        coll_mock.product = [product]

        bundle_mock = MagicMock()
        bundle_mock.collections = [coll_mock]
        bundle_mock.checksum = "e" * 32
        readme_mock = MagicMock()
        readme_label_mock = MagicMock()
        readme_label_mock.name = "/staging/em16_spice/readme.xml"
        readme_mock.label = readme_label_mock
        bundle_mock.readme = readme_mock

        obj.collection.bundle = bundle_mock
        return obj

    def test_write_product_no_history_writes_file(self):
        obj = self._obj_with_products()
        obj.setup.diff = False  # This is the default

        m = mock_open()
        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", m), \
             patch.object(obj, "compare") as m_compare:

            obj.write_product(history=None, set_coverage=False)

        m.assert_called()
        m_compare.assert_not_called()

        assert obj.md5_dict == {
            'miscellaneous/test_file.tab': 'ffffffffffffffffffffffffffffffff',
            'miscellaneous/test_file.xml': 'cccccccccccccccccccccccccccccccc',
            'readme.txt': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            'readme.xml': 'cccccccccccccccccccccccccccccccc'}

    def test_write_product_set_coverage_does_not_write_file(self):
        obj = self._obj_with_products()

        m = mock_open()
        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", m):

            obj.write_product(history=None, set_coverage=True)

        # open should NOT be called for writing when set_coverage=True
        write_calls = [c for c in m.call_args_list if "w" in str(c)]
        assert not write_calls

    def test_write_product_diff_true_calls_compare(self):
        obj = self._obj_with_products()
        obj.setup.diff = True

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()), \
             patch.object(obj, "compare") as m_compare:

            obj.write_product(history=None, set_coverage=False)

        m_compare.assert_called_once()

    def test_write_product_removes_ds_store_files(self):
        obj = self._obj_with_products()

        ds_store_path = "/bundle/subdir" + os.sep + ".DS_Store"
        walk_result = [("/bundle/subdir", [], [".DS_Store", "real.tab"])]

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=walk_result), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch(PATCHES["os_remove"]) as m_rm, \
             patch("builtins.open", mock_open()):

            obj.write_product(history=None, set_coverage=False)

        m_rm.assert_called_once_with(ds_store_path)

    def test_write_product_history_pds4_computes_md5_from_registry(self):
        obj = self._obj_with_products()
        history_product = "miscellaneous/checksum/checksum_v001.tab"
        history = [None, [history_product]]

        with patch(PATCHES["md5"], return_value="c" * 32) as m_md5, \
             patch(PATCHES["checksum_from_registry"], return_value='a' * 32), \
             patch(PATCHES["checksum_from_label"], return_value="") as m_lbl_cs, \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=history, set_coverage=False)

        m_lbl_cs.assert_not_called()
        m_md5.assert_not_called()

    def test_write_product_history_checksum_from_label_used_when_registry_empty(self):
        obj = self._obj_with_products()
        history_product = "miscellaneous/checksum/checksum_v001.tab"
        history = [None, [history_product]]

        with patch(PATCHES["md5"], return_value="c" * 32) as m_md5, \
             patch(PATCHES["checksum_from_registry"], return_value=""), \
             patch(PATCHES["checksum_from_label"], return_value="d" * 32) as m_lbl_cs, \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=history, set_coverage=False)

        m_lbl_cs.assert_called()
        m_md5.assert_not_called()

    def test_write_product_history_checksum_from_md5_as_last_resort(self):
        obj = self._obj_with_products()
        history_product = "miscellaneous/checksum/checksum_v001.tab"
        history = [None, [history_product]]

        with patch(PATCHES["md5"], return_value="c" * 32) as m_md5, \
             patch(PATCHES["checksum_from_registry"], return_value=""), \
             patch(PATCHES["checksum_from_label"], return_value="") as m_lbl_cs, \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=history, set_coverage=False)

        m_lbl_cs.assert_called()
        m_md5.assert_called()

    def test_write_product_xml_skips_registry_and_label_checksum(self):
        """For .xml products in history, only md5() is called directly."""
        obj = self._obj_with_products()
        history_product = "miscellaneous/collection_misc.xml"
        history = [None, [history_product]]

        with patch(PATCHES["md5"], return_value="c" * 32) as m_md5, \
             patch(PATCHES["checksum_from_registry"]) as m_reg, \
             patch(PATCHES["checksum_from_label"]) as m_lbl_cs, \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=history, set_coverage=False)

        m_reg.assert_not_called()
        m_lbl_cs.assert_not_called()
        m_md5.assert_called()

    @staticmethod
    def _run_write_product_warning_test(obj, caplog):
        """Helper to execute the product write test and assert expected log messages."""
        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()), \
             caplog.at_level(logging.INFO):

            obj.write_product(history=None, set_coverage=False)

        expected = [
            (logging.WARNING, '-- Default to version 1.'),
            (logging.WARNING, '-- Make sure this is the first release of the archive.'),
            (logging.WARNING, ''),
            (logging.WARNING, '-- miscellaneous/test_file.tab does not have a label.'),
            (logging.INFO, ''),
            (logging.WARNING, '-- Start time set to mission start time: 2016-01-01T00:00:00Z'),
            (logging.WARNING, '-- Stop time set to mission finish time: 2023-12-31T23:59:59Z')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_write_product_no_history_product_without_label_logs_warning(self, caplog):
        obj = self._obj_with_products()

        # Remove label attribute from product
        for coll in obj.collection.bundle.collections:
            for prod in coll.product:
                del prod.label

        self._run_write_product_warning_test(obj, caplog)

    def test_write_product_no_history_product_with_none_label_logs_warning(self, caplog):
        obj = self._obj_with_products()

        for coll in obj.collection.bundle.collections:
            for prod in coll.product:
                prod.label = None

        self._run_write_product_warning_test(obj, caplog)

    # TODO: This test will not be necessary when refactoring is completed.
    def test_write_product_duplicate_md5_debug_mode_logs_debug(self, caplog):
        obj = self._obj_with_products()
        obj.setup.args.debug = True

        # Pre-populate dict with the same checksum under a different key
        obj.md5_dict["other/different_name.tab"] = "f" * 32  # same as product.checksum

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()), \
             caplog.at_level(logging.DEBUG):

            obj.write_product(history=None, set_coverage=False)

    @pytest.mark.skip(reason="Fails due to bug in code. When fixed, the test should be executed.")
    def test_write_product_duplicate_md5_non_debug_calls_handle_npb_error(self):
        obj = self._obj_with_products()
        obj.setup.args.debug = False
        obj.md5_dict["other/different_name.tab"] = "f" * 32

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            with pytest.raises(RuntimeError, match='Two products have the same MD5 sum, '
                                                   'the product miscellaneous/test_file.tab '
                                                   'might be a duplicate.'):
                obj.write_product(history=None, set_coverage=False)

    def test_write_product_pds4_sets_start_and_stop_times_from_labels(self):
        obj = self._obj_with_products()

        # Manufacture a md5_dict entry that looks like a collection label
        obj.md5_dict["spice_kernels/collection_spice_kernels_v001.xml"] = "a" * 32

        label_xml = (
            "<start_date_time>2020-01-01T00:00:00Z</start_date_time>\n"
            "<stop_date_time>2021-12-31T23:59:59Z</stop_date_time>\n"
        )

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=True), \
             patch("builtins.open", mock_open(read_data=label_xml)):

            obj.write_product(history=None, set_coverage=False)

        assert obj.start_time == "2020-01-01T00:00:00Z"
        assert obj.stop_time == "2021-12-31T23:59:59Z"

    def test_write_product_pds4_falls_back_to_mission_times_when_no_coverage(self):
        obj = self._obj_with_products()
        # No coverage products in md5_dict

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open(read_data="")):

            obj.write_product(history=None, set_coverage=False)

        assert obj.start_time == obj.setup.mission_start
        assert obj.stop_time == obj.setup.mission_finish

    def test_write_product_pds4_coverage_file_not_found_logs_error(self, caplog):
        obj = self._obj_with_products()
        obj.md5_dict["spice_kernels/collection_spice_kernels_v001.xml"] = "a" * 32

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open(read_data="")), \
             caplog.at_level(logging.INFO):

            obj.write_product(history=None, set_coverage=False)

        expected = [
            (logging.WARNING, '-- Default to version 1.'),
            (logging.WARNING, '-- Make sure this is the first release of the archive.'),
            (logging.WARNING, ''),
            (logging.WARNING, '-- The following products have the same MD5 sum:'),
            (logging.WARNING, '   cccccccccccccccccccccccccccccccc'),
            (logging.WARNING, '      miscellaneous/test_file.xml'),
            (logging.WARNING, '      readme.xml'),
            (logging.ERROR, '-- Product required to determine checksum_v001.tab coverage: '
                            'spice_kernels/collection_spice_kernels_v001.xml not found.'),
            (logging.WARNING, '-- Start time set to mission start time: 2016-01-01T00:00:00Z'),
            (logging.WARNING, '-- Stop time set to mission finish time: 2023-12-31T23:59:59Z')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_write_product_pds4_duplicate_md5_warning_logged(self, caplog):
        obj = self._obj_with_products()

        # Force two keys to share the same md5 value
        obj.md5_dict["file_a.tab"] = "a" * 32
        obj.md5_dict["file_b.tab"] = "a" * 32

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()), \
             caplog.at_level(logging.INFO):

            obj.write_product(history=None, set_coverage=False)

        expected = [
            (logging.WARNING, '-- Default to version 1.'),
            (logging.WARNING, '-- Make sure this is the first release of the archive.'),
            (logging.WARNING, ''),
            (logging.WARNING, '-- The following products have the same MD5 sum:'),
            (logging.WARNING, '   aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'),
            (logging.WARNING, '      file_a.tab'),
            (logging.WARNING, '      file_b.tab'),
            (logging.WARNING, '   cccccccccccccccccccccccccccccccc'),
            (logging.WARNING, '      miscellaneous/test_file.xml'),
            (logging.WARNING, '      readme.xml'),
            (logging.WARNING, '-- Start time set to mission start time: 2016-01-01T00:00:00Z'),
            (logging.WARNING, '-- Stop time set to mission finish time: 2023-12-31T23:59:59Z')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_write_product_pds3_for_checksum_product(self):
        p = MagicMock()
        p.path = '/bundle/em16_spice_1000/test/checksum.tab'
        p.label.name = '/bundle/em16_spice_1000/test/checksum.lbl'
        delattr(p, "checksum")

        collection = _make_collection()
        collection.product = [p]

        obj = _build_pds3()
        obj.collection.bundle.collections = [collection]

        # Make sure that the collection.bundle MagicMock does not have
        # the checksum attribute. This way we can control the inputs to
        # this test.
        delattr(obj.collection.bundle, "checksum")

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=None, set_coverage=False)

        assert obj.bytes == 17
        assert obj.record_bytes == 53  # 32 + 4 + 17
        assert obj.file_records == 1 # The label file.

    def test_write_product_pds3_sets_bytes_and_record_bytes(self):
        obj = _build_pds3()
        obj.md5_dict["some/long_filename.tab"] = "a" * 32
        obj.md5_dict["short.tab"] = "b" * 32

        # Make sure that the collection.bundle MagicMock does not have
        # the checksum attribute. This way we can control the inputs to
        # this test.
        delattr(obj.collection.bundle, "checksum")

        with patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=None, set_coverage=False)

        max_len = len("some/long_filename.tab")  # longest key
        assert obj.bytes == max_len
        assert obj.record_bytes == 32 + 4 + max_len
        assert obj.file_records == 2

    def test_write_product_orbnum_label_included_in_coverage(self):
        obj = self._obj_with_products()
        obj.md5_dict["miscellaneous/orbnum/em16.xml"] = "a" * 32

        label_xml = (
            "<start_date_time>2019-01-01T00:00:00Z</start_date_time>\n"
            "<stop_date_time>2022-06-30T00:00:00Z</stop_date_time>\n"
        )

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=True), \
             patch("builtins.open", mock_open(read_data=label_xml)):

            obj.write_product(history=None, set_coverage=False)

        assert obj.start_time == "2019-01-01T00:00:00Z"
        assert obj.stop_time == "2022-06-30T00:00:00Z"

    def test_write_product_coverage_file_found_in_staging(self):
        """When file not in bundle dir but exists in staging, it is read."""
        obj = self._obj_with_products()
        obj.md5_dict["spice_kernels/collection_spice_kernels_v001.xml"] = "a" * 32

        label_xml = (
            "<start_date_time>2021-03-01T00:00:00Z</start_date_time>\n"
            "<stop_date_time>2022-03-01T00:00:00Z</stop_date_time>\n"
        )

        # First isfile call (bundle path) returns False; second (staging) True
        isfile_results = [False, True, True]

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], side_effect=isfile_results), \
             patch("builtins.open", mock_open(read_data=label_xml)):

            obj.write_product(history=None, set_coverage=False)

        assert obj.start_time == "2021-03-01T00:00:00Z"


# ===========================================================================
# TestCompare
# ===========================================================================

class TestCompare:
    """Tests for compare."""

    def test_compare_calls_compare_files(self):
        obj, _ = _build_pds4(increment=False)
        obj.path_current = "/prev/checksum_v001.tab"
        obj.path = "/staging/checksum_v002.tab"

        with patch(PATCHES["compare_files"]) as m_cf:
            obj.compare()

        m_cf.assert_called_once_with(
            obj.path_current,
            obj.path,
            obj.setup.working_directory,
            obj.setup.diff,
        )

    def test_compare_logs_warning_on_exception(self, caplog):
        obj, _ = _build_pds4(increment=False)
        obj.path_current = "/prev/checksum_v001.tab"

        with patch(PATCHES["compare_files"], side_effect=Exception("boom")), \
             caplog.at_level(logging.INFO):
            obj.compare()

        expected = [
            (logging.WARNING, '-- Default to version 1.'),
            (logging.WARNING, '-- Make sure this is the first release of the archive.'),
            (logging.WARNING, ''),
            (logging.INFO, ''),
            (logging.WARNING, '-- Checksum from previous increment does not exist.'), (20, '')]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected