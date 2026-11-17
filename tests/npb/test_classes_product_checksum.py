"""Unit tests for the ChecksumProduct class.
"""
import logging
import os
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_checksum import ChecksumProduct
from pds.naif_pds4_bundler.classes.exceptions import NPBError

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

def _make_setup(pds_version="4", increment=True, diff=False):
    """Return a minimal setup mock."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.increment = increment
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
    setup.args.diff = diff
    return setup


def _make_collection(name="miscellaneous"):
    collection = MagicMock()
    collection.name = name
    return collection


# The expected "previous checksum file" candidate. Built by joining path
# segments (never embedding "/" inside a string literal) so it's correct on both
# POSIX and Windows. Kept as a Path -- comparisons against obj.path_current
# (also a Path) use Path.__eq__, which compares parsed path parts rather than
# separator-sensitive strings. str(PREV_CHECKSUM_PATH) is used only where an
# actual string is required: standing in for a Path.glob() match (a plain str
# works too, since find_latest_versioned_file wraps every match in Path()), or
# building a regex.
PREV_CHECKSUM_PATH = Path("bundle", "em16_spice", "miscellaneous",
                          "checksum", "checksum_v001.tab")

# NPBError embeds str(self.path_current) (a Path) in its message, so this is
# escaped once here for reuse in pytest.raises(match=...) regexes below --
# on Windows str(PREV_CHECKSUM_PATH) contains backslashes, which would
# otherwise be read as regex escape sequences instead of literal separators.
PREV_CHECKSUM_PATH_ESCAPED = re.escape(str(PREV_CHECKSUM_PATH))

# ---------------------------------------------------------------------------
# Patch targets (relative to the module under test)
# ---------------------------------------------------------------------------
MOD = "pds.naif_pds4_bundler.classes.product.product_checksum"

PATCHES = dict(
    safe_make_directory=f"{MOD}.safe_make_directory",
    # find_latest_versioned_file globs candidates itself via Path.glob, so
    # that's what's patched here instead of anything in this module.
    glob_glob="pathlib.Path.glob",
    md5=f"{MOD}.md5",
    checksum_from_registry=f"{MOD}.checksum_from_registry",
    checksum_from_label=f"{MOD}.checksum_from_label",
    compare_files=f"{MOD}.compare_files",
    Product_common=f"{MOD}.Product._set_common_attributes",
    Product_derive=f"{MOD}.Product.derive_file_attributes",
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
         patch(PATCHES["md5"], return_value="a" * 32) as m_md5, \
         patch(PATCHES["os_walk"], return_value=[]) as m_walk, \
         patch("builtins.open", mock_open(read_data="")) as m_open:

        # find_latest_versioned_file globs two patterns (bundle + staging
        # dir) and pools the results, so this mock is hit twice per call;
        # returning the same glob_files both times is harmless here since
        # duplicates don't change which entry sorts last.
        m_glob.return_value = glob_files

        obj = ChecksumProduct(setup, collection, add_previous_checksum)
        mocks.update(dict(
            mkdir=m_mkdir, glob=m_glob, md5=m_md5,
            walk=m_walk, open=m_open,
        ))

    return obj, mocks


def _build_pds3(add_previous_checksum=False):
    """Build a PDS3 ChecksumProduct."""

    setup = _make_setup(pds_version="3", increment=False, diff=False)
    collection = _make_collection()

    with patch(PATCHES["safe_make_directory"]), \
         patch(PATCHES["glob_glob"], return_value=[]), \
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
        prev = str(PREV_CHECKSUM_PATH)
        obj, _ = _build_pds4(increment=True, glob_files=[prev])
        assert obj.version == 2
        assert obj.name == "checksum_v002.tab"

        # path_current is a Path when a previous file was found. Compare as
        # Path == Path (parsed parts), not string equality, so this doesn't
        # depend on separator style.
        assert obj.path_current == PREV_CHECKSUM_PATH
        assert obj.vid == "2.0"

    def test_init_pds4_creates_checksum_directory(self):

        setup = _make_setup(pds_version="4")
        collection = _make_collection()

        with patch(PATCHES["safe_make_directory"]) as m_mkdir, \
             patch(PATCHES["glob_glob"], return_value=[]), \
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
        # "checksum_v9.tab" sorts *after* "checksum_v10.tab" and
        # "checksum_v2.tab" lexically (since "9" > "1" and "9" > "2" at
        # that character position), even though 9 is numerically the
        # smallest. This pins find_latest_versioned_file's numeric (not
        # lexical) comparison, per commit 9275b96.
        files = [
            str(PREV_CHECKSUM_PATH.parent / "checksum_v2.tab"),
            str(PREV_CHECKSUM_PATH.parent / "checksum_v10.tab"),
            str(PREV_CHECKSUM_PATH.parent / "checksum_v9.tab"),
        ]

        # Path.glob returns unsorted; find_latest_versioned_file picks by
        # numeric version, not list order or lexical string order.
        obj, _ = _build_pds4(increment=True, glob_files=files)
        assert obj.version == 11
        assert obj.name == "checksum_v011.tab"
        assert obj.path_current == PREV_CHECKSUM_PATH.parent / "checksum_v10.tab"


# ===========================================================================
# ChecksumProduct.read_current_product
# ===========================================================================

class TestReadCurrentProduct:
    """Tests for read_current_product."""

    def test_reads_previous_checksum_into_md5_dict(self):

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = str(PREV_CHECKSUM_PATH)
        prev_content = ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa some/file.tab\n"
                        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb other/file.xml\n")

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
             patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=prev_content)):

            obj = ChecksumProduct(setup, collection, add_previous_checksum=False)

        assert obj.md5_dict == {'some/file.tab': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                                'other/file.xml': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'}

    @pytest.mark.parametrize('bad_content, error', [
        ("this_line_has_no_space_split\n",
         f'Checksum file {PREV_CHECKSUM_PATH_ESCAPED} is corrupted.'),
        ("0123456789  some/file.tab\n",
         f'Checksum file {PREV_CHECKSUM_PATH_ESCAPED} '
         'corrupted entry: 0123456789  some/file.tab\n.')
    ])
    def test_corrupted_line_raises_npberror(self, bad_content, error) -> None:

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = str(PREV_CHECKSUM_PATH)

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
             patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch("builtins.open", mock_open(read_data=bad_content)):

            with pytest.raises(NPBError, match=error):
                ChecksumProduct(setup, collection, add_previous_checksum=False)

    def test_add_previous_checksum_true_adds_file_and_label_pds4(self):

        setup = _make_setup(pds_version="4", increment=True)
        collection = _make_collection()
        prev = str(PREV_CHECKSUM_PATH)
        prev_content = "a" * 32 + "  some/file.tab\n"

        with patch(PATCHES["safe_make_directory"]), \
             patch(PATCHES["glob_glob"], return_value=[prev]), \
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

    def test_generate_writes_product_and_fills_file_attributes(self):
        # generate() used to also pick a label class and set self.label; that
        # moved to npb.py, so this test checks what's left: writing the file
        # and filling in the attributes of the base class.
        obj, _ = _build_pds4(increment=False)
        obj.new_product = False  # reset, so we can check generate() flips it back to True
        obj.label = None  # pre-set, so the assertion below proves generate() left it alone

        with patch.object(obj, "write_product") as m_wp, \
             patch(PATCHES["Product_common"]) as m_common, \
             patch(PATCHES["Product_derive"]) as m_derive:

            obj.generate(history=['some_file'])

        m_wp.assert_called_once_with(history=['some_file'])
        m_common.assert_called_once()
        m_derive.assert_called_once()

        assert obj.new_product is True

        # The regression guard for this whole refactor: if labeling ever creeps
        # back into generate(), this is the assertion that catches it.
        assert obj.label is None

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
        obj.setup.args.diff = False  # This is the default

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
        obj.setup.args.diff = True

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

    @pytest.mark.parametrize(
        "pds_version, archive_dir, set_coverage",
        [
            pytest.param("4", "em16_spice", True, id="pds4-coverage-pass"),
            pytest.param("4", "em16_spice", False, id="pds4-writing-pass"),
            pytest.param("3", "em16_spice_1000", True,
                         id="pds3-coverage-pass"),
            pytest.param("3", "em16_spice_1000", False,
                         id="pds3-writing-pass"),
        ])
    def test_write_product_own_file_without_label_logs_no_warning(
            self, caplog, pds_version, archive_dir, set_coverage):
        """Check the checksum does not warn about its own missing label.

        The checksum being generated is already in the collection when
        ``write_product()`` walks the products, and its label is only written
        later. Its file must not log 'does not have a label', in either PDS
        version and in both the coverage pass and the writing pass, and it
        must not be an entry in its own table, which has to be the same as
        without it in the collection.
        """
        own_path = (f"/staging/{archive_dir}/miscellaneous/"
                    "checksum/checksum_v001.tab")
        own_name = "miscellaneous/checksum/checksum_v001.tab"

        # Two identical bundles; the second one also holds the checksum
        # itself as a product, with no label yet, like the pipeline does.
        baseline = self._obj_with_products(pds_version)
        obj = self._obj_with_products(pds_version)
        obj.path = own_path
        obj.collection.bundle.collections[0].product.append(obj)

        # Write both checksums, keeping the log of the whole run.
        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()), \
             caplog.at_level(logging.INFO):

            baseline.write_product(history=None, set_coverage=set_coverage)
            obj.write_product(history=None, set_coverage=set_coverage)

        # No missing-label warning names the checksum's own file, and having
        # it in the collection left the table untouched.
        warnings = [r.getMessage() for r in caplog.records
                    if "does not have a label" in r.getMessage()]
        assert not any(own_name in message for message in warnings)
        assert own_name not in obj.md5_dict
        assert obj.md5_dict == baseline.md5_dict

    def test_write_product_skips_own_file_even_with_checksum_and_label(self):
        """Check the checksum is never an entry in its own table.

        Even if the checksum being generated carried a checksum and a label,
        like the other products do, it must not list itself or its label.
        """
        own_name = "miscellaneous/checksum/checksum_v001.tab"
        own_label_name = "miscellaneous/checksum/checksum_v001.xml"

        obj = self._obj_with_products("4")
        obj.path = f"/staging/em16_spice/{own_name}"
        obj.checksum = "d" * 32
        obj.label = MagicMock()
        obj.label.name = f"/staging/em16_spice/{own_label_name}"
        obj.collection.bundle.collections[0].product.append(obj)

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            obj.write_product(history=None, set_coverage=False)

        assert own_name not in obj.md5_dict
        assert own_label_name not in obj.md5_dict

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
    def test_write_product_duplicate_md5_non_debug_raises_npberror(self):
        obj = self._obj_with_products()
        obj.setup.args.debug = False
        obj.md5_dict["other/different_name.tab"] = "f" * 32

        with patch(PATCHES["md5"], return_value="c" * 32), \
             patch(PATCHES["os_walk"], return_value=[]), \
             patch(PATCHES["os_path_isfile"], return_value=False), \
             patch("builtins.open", mock_open()):

            with pytest.raises(NPBError, match='Two products have the same MD5 sum, '
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
            obj.setup.args.diff,
        )

    # Both errors must hit the same fallback: a missing previous file
    # (FileNotFoundError, an OSError subclass - compare_files() opens it with
    # open()) and a previous file that exists but isn't valid UTF-8
    # (UnicodeDecodeError - compare_files() opens with encoding='utf-8').
    # Only the side_effect differs, so one parametrized test covers both.
    @pytest.mark.parametrize("side_effect", [
        pytest.param(FileNotFoundError("boom"), id="missing-file"),
        pytest.param(
            UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
            id="non-utf8-file"),
    ])
    def test_compare_logs_warning_on_previous_file_error(self, caplog, side_effect):
        """compare() falls back to the same warning for either error - proving
        except (OSError, UnicodeDecodeError) catches both real conditions."""
        obj, _ = _build_pds4(increment=False)
        obj.path_current = "/prev/checksum_v001.tab"

        with patch(PATCHES["compare_files"], side_effect=side_effect), \
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

    def test_compare_propagates_unexpected_exception(self, caplog):
        """A bug inside compare_files() that isn't a missing-file case (here a
        generic Exception, standing in for e.g. a TypeError from a real defect)
        must propagate, not be misreported as "previous checksum does not
        exist" - proving except OSError no longer masks it."""
        obj, _ = _build_pds4(increment=False)
        obj.path_current = "/prev/checksum_v001.tab"

        with patch(PATCHES["compare_files"], side_effect=Exception("boom")), \
             caplog.at_level(logging.INFO):
            with pytest.raises(Exception, match="boom"):
                obj.compare()

# ===========================================================================
# TestChecksumProductComputeChecksum
# ChecksumProduct overrides Product._compute_checksum() so the checksum is
# always recomputed with md5(), never reused from the registry or the label.
# ===========================================================================

def _make_bare_checksum_product(path, checksum_arg):
    """Build a ChecksumProduct without running __init__ (no filesystem)."""
    product = ChecksumProduct.__new__(ChecksumProduct)
    product.path = str(path)
    product.new_product = False
    product.setup = MagicMock()
    product.setup.args.checksum = checksum_arg
    return product


class TestChecksumProductComputeChecksum:

    def test_compute_checksum_ignores_registry_and_label(self, tmp_path):
        """Even with checksum reuse on, only md5() is consulted."""
        product = _make_bare_checksum_product(tmp_path / "x.checksum", True)

        with patch(PATCHES["md5"], return_value="fresh-md5") as m_md5, \
             patch(PATCHES["checksum_from_registry"]) as m_reg, \
             patch(PATCHES["checksum_from_label"]) as m_lbl:

            checksum = product._compute_checksum()

        assert checksum == "fresh-md5"
        m_reg.assert_not_called()
        m_lbl.assert_not_called()
        m_md5.assert_called_once_with(product.path)

    def test_derive_file_attributes_dispatches_to_override(self, tmp_path):
        """derive_file_attributes() stores the md5 checksum and skips the registry."""
        path = tmp_path / "maven_spice" / "release.checksum"
        path.parent.mkdir(parents=True)
        path.write_text("checksum-registry", encoding="utf-8")
        product = _make_bare_checksum_product(path, True)

        with patch(PATCHES["md5"], return_value="fresh-md5"), \
             patch("pds.naif_pds4_bundler.classes.product.product."
                   "checksum_from_registry") as m_reg:

            product.derive_file_attributes()

        assert product.checksum == "fresh-md5"
        m_reg.assert_not_called()


# ===========================================================================
# Golden output of the checksum table
# ===========================================================================

def written_as(text: str) -> bytes:
    """Return the bytes that the checksum writer leaves on disk for ``text``.

    The table is written in text mode, so on Windows every line feed becomes
    a carriage return and a line feed, and a CRLF line ending ends up as
    CR CR LF.
    """
    return text.replace("\n", os.linesep).encode()


# The entries are given out of order on purpose. Their names also check the
# plain ASCII sort: 'B' goes before 'a', and '.' goes before '_'.
PDS4_ENTRIES = {
    "spice_kernels/ck/b.bc": "b" * 32,
    "readme.txt": "e" * 32,
    "spice_kernels/ck/a_b.bc": "d" * 32,
    "spice_kernels/ck/B.bc": "a" * 32,
    "spice_kernels/ck/a.bc": "c" * 32,
}

# MD5 of the bundle label that the test writes ('bundle label' plus a line
# break). It comes from md5sum, not from the code under test.
BUNDLE_LABEL_MD5 = "4716ac8418e52ca2304202c1af6c13b5"

PDS4_TABLE_LINES = [
    f"{'e' * 32}  readme.txt",
    f"{BUNDLE_LABEL_MD5}  readme.xml",
    f"{'a' * 32}  spice_kernels/ck/B.bc",
    f"{'c' * 32}  spice_kernels/ck/a.bc",
    f"{'d' * 32}  spice_kernels/ck/a_b.bc",
    f"{'b' * 32}  spice_kernels/ck/b.bc",
]


@pytest.mark.parametrize("eol", ["\n", "\r\n"])
def test_pds4_table_bytes(tmp_path: Path, eol: str) -> None:
    """Check the bytes of a PDS4 checksum table built from fixed entries.

    The file lists the entries and the bundle label sorted by name, with two
    spaces between the MD5 and the name, and every line ends with the EOL of
    the setup (LF or CRLF).
    """
    # Write a real bundle label and the miscellaneous folder, which has to
    # exist before the product is created because its checksum folder is made
    # with a non-recursive mkdir.
    staging = tmp_path / "staging"
    bundle_label = staging / "em16_spice" / "readme.xml"
    bundle_label.parent.mkdir(parents=True)
    bundle_label.write_bytes(b"bundle label\n")
    (staging / "miscellaneous").mkdir()

    # Build a bundle with no products and no readme checksum, so the table
    # only holds the entries added below plus the bundle label.
    setup = _make_setup(pds_version="4", increment=False)
    setup.staging_directory = str(staging)
    setup.bundle_directory = str(tmp_path / "bundle")
    setup.eol = eol
    collection = _make_collection()
    # The checksum cuts the names at '/em16_spice/', so they are given with
    # forward slashes, whatever the platform.
    readme_label = SimpleNamespace(name=bundle_label.as_posix())
    collection.bundle = SimpleNamespace(
        collections=[],
        readme=SimpleNamespace(label=readme_label))
    checksum = ChecksumProduct(setup, collection)
    checksum.md5_dict.update(PDS4_ENTRIES)

    # Write the table to disk.
    checksum.write_product()

    # Compare the file with the expected bytes, line ending included.
    expected = written_as("".join(line + eol for line in PDS4_TABLE_LINES))
    assert Path(checksum.path).read_bytes() == expected


# Names that differ only by '_' and '.', plus mixed case and digits. A plain
# sort would order them a.b, a1, aB, a_b, a_b_c, ab.
PDS3_ENTRIES = {
    "ab.tab": "4" * 32,
    "a_b_c.tab": "6" * 32,
    "a.b.tab": "5" * 32,
    "aB.tab": "3" * 32,
    "a_b.tab": "2" * 32,
    "a1.tab": "1" * 32,
}

# The order of the original mkpdssum.pl script, with trailing spaces so every
# name takes as many characters as the longest one (9).
PDS3_TABLE_LINES = [
    f"{'1' * 32}  a1.tab   ",
    f"{'3' * 32}  aB.tab   ",
    f"{'4' * 32}  ab.tab   ",
    f"{'5' * 32}  a.b.tab  ",
    f"{'2' * 32}  a_b.tab  ",
    f"{'6' * 32}  a_b_c.tab",
]


@pytest.mark.parametrize("eol", ["\n", "\r\n"])
def test_pds3_table_bytes_and_counts(tmp_path: Path, eol: str) -> None:
    """Check the bytes and the size attributes of a PDS3 checksum table.

    The entries are sorted like mkpdssum.pl does, not like Python does, and
    each name is padded with spaces to the longest one. The product reports
    the longest name length as 'bytes', the length of a record, and the
    number of records.
    """
    # Create the PDS3 setup and an empty previous checksum file, because the
    # product always opens it, even when it has nothing to add.
    staging = tmp_path / "staging"
    staging.mkdir()
    setup = _make_setup(pds_version="3", increment=False)
    setup.staging_directory = str(staging)
    setup.bundle_directory = str(tmp_path / "bundle")
    setup.eol = eol
    previous = tmp_path / "bundle" / setup.volume_id / "index" / "checksum.tab"
    previous.parent.mkdir(parents=True)
    previous.write_bytes(b"")

    # Build a bundle with no products, so the table only holds the entries
    # added below.
    collection = _make_collection()
    collection.bundle = SimpleNamespace(collections=[])
    checksum = ChecksumProduct(
        setup, collection, add_previous_checksum=False)
    checksum.md5_dict.update(PDS3_ENTRIES)

    # Write the table to disk.
    checksum.write_product()

    # Compare the file with the expected bytes, then check the size
    # attributes: 9 is the longest name and 45 is 32 + 4 + 9.
    expected = written_as("".join(line + eol for line in PDS3_TABLE_LINES))
    assert Path(checksum.path).read_bytes() == expected
    assert checksum.bytes == 9
    assert checksum.record_bytes == 45
    assert checksum.file_records == 6


# ===========================================================================
# Loading the previous checksum file from disk
# ===========================================================================

# Entries of the previous checksum file. The PDS3 files pad the names with
# trailing spaces, so the second line carries some on purpose.
PREVIOUS_LINES = [
    f"{'a' * 32}  spice_kernels/ck/a.bc",
    f"{'b' * 32}  spice_kernels/ck/b.bc   ",
]

PREVIOUS_ENTRIES = {
    "spice_kernels/ck/a.bc": "a" * 32,
    "spice_kernels/ck/b.bc": "b" * 32,
}


@pytest.mark.parametrize("eol", ["\n", "\r\n"])
@pytest.mark.parametrize("pds_version, previous_path", [
    pytest.param("4", "em16_spice/miscellaneous/checksum/checksum_v001.tab",
                 id="pds4"),
    pytest.param("3", "em16_spice_1000/index/checksum.tab", id="pds3"),
])
def test_previous_checksum_file_is_loaded(
        tmp_path: Path, pds_version: str, previous_path: str,
        eol: str) -> None:
    """Check that the entries of a previous checksum file are loaded.

    Each line holds an MD5 and a file name separated by spaces. The line
    ending (LF or CRLF) and the padding after the name do not end up in the
    name, in PDS4 and in PDS3.
    """
    # Write a previous checksum file where the product looks for it.
    previous = tmp_path / "bundle" / previous_path
    previous.parent.mkdir(parents=True)
    previous.write_bytes("".join(line + eol for line in PREVIOUS_LINES)
                         .encode())
    staging = tmp_path / "staging"
    staging.mkdir()
    setup = _make_setup(pds_version=pds_version, increment=True)
    setup.staging_directory = str(staging)
    setup.bundle_directory = str(tmp_path / "bundle")

    # Create the product, which reads the file.
    checksum = ChecksumProduct(
        setup, _make_collection(), add_previous_checksum=False)

    # Only the two entries of the file are loaded.
    assert checksum.md5_dict == PREVIOUS_ENTRIES


CORRUPTED_LINE = "Checksum file {path} is corrupted."
CORRUPTED_ENTRY = "Checksum file {path} corrupted entry: {line}."


@pytest.mark.parametrize("line, message", [
    pytest.param("some/file.tab\n", CORRUPTED_LINE, id="one-field"),
    pytest.param(f"{'a' * 32}  some/file.tab extra\n", CORRUPTED_LINE,
                 id="three-fields"),
    pytest.param("\n", CORRUPTED_LINE, id="blank-line"),
    pytest.param(f"{'a' * 31}  some/file.tab\n", CORRUPTED_ENTRY,
                 id="md5-too-short"),
    pytest.param(f"{'a' * 33}  some/file.tab\n", CORRUPTED_ENTRY,
                 id="md5-too-long"),
])
def test_corrupted_previous_checksum_file_raises(
        tmp_path: Path, line: str, message: str) -> None:
    """Check that a corrupted previous checksum file stops the run.

    A line that does not have exactly two fields, blank lines included,
    raises an NPBError saying the file is corrupted. A line whose MD5 does
    not have 32 characters raises an NPBError that also quotes the line.
    """
    # Write a previous checksum file that starts with a valid entry and
    # then has the corrupted line.
    previous = (tmp_path / "bundle" / "em16_spice" / "miscellaneous"
                / "checksum" / "checksum_v001.tab")
    previous.parent.mkdir(parents=True)
    previous.write_text(f"{'a' * 32}  some/other.tab\n" + line)
    setup = _make_setup(pds_version="4", increment=True)
    setup.staging_directory = str(tmp_path / "staging")
    setup.bundle_directory = str(tmp_path / "bundle")

    # Create the product, which reads the file.
    with pytest.raises(NPBError) as error:
        ChecksumProduct(setup, _make_collection(), add_previous_checksum=False)

    # The message names the file and, for a bad MD5, quotes the line.
    assert str(error.value) == message.format(path=previous, line=line)


# ===========================================================================
# Duplicate MD5 sums
# ===========================================================================

SHARED_MD5 = "f" * 32

# MD5 of the product label that the test writes ('product label' plus a
# line break). It comes from md5sum, not from the code under test.
PRODUCT_LABEL_MD5 = "e9dd7768c0a27c878861ef20a6856acd"

DUPLICATE_MD5_TABLE_LINES = [
    f"{SHARED_MD5}  other/different_name.tab",
    f"{BUNDLE_LABEL_MD5}  readme.xml",
    f"{SHARED_MD5}  spice_kernels/ck/a.bc",
    f"{PRODUCT_LABEL_MD5}  spice_kernels/ck/a.xml",
]

DUPLICATE_MD5_WARNINGS = [
    '-- Default to version 1.',
    '-- Make sure this is the first release of the archive.',
    '',
    '-- The following products have the same MD5 sum:',
    f'   {SHARED_MD5}',
    '      other/different_name.tab',
    '      spice_kernels/ck/a.bc',
    '-- Start time set to mission start time: 2016-01-01T00:00:00Z',
    '-- Stop time set to mission finish time: 2023-12-31T23:59:59Z',
]


@pytest.mark.parametrize("debug", [False, True])
def test_duplicate_md5_is_warned_and_does_not_raise(
        tmp_path: Path, caplog: pytest.LogCaptureFixture,
        debug: bool) -> None:
    """Check what happens when two files have the same MD5 sum.

    The table is written with both files, and the warnings list the MD5 with
    the names that share it. The check that looks for duplicates while the
    products are added does not raise, whether the run is in debug mode or
    not.
    """
    # Write the real labels, and a product whose MD5 is the same as the one
    # of a file that is already in the table under another name.
    staging = tmp_path / "staging"
    bundle_label = staging / "em16_spice" / "readme.xml"
    product_label = staging / "em16_spice" / "spice_kernels" / "ck" / "a.xml"
    product_label.parent.mkdir(parents=True)
    bundle_label.write_bytes(b"bundle label\n")
    product_label.write_bytes(b"product label\n")
    (staging / "miscellaneous").mkdir()
    # The checksum cuts the names at '/em16_spice/', so they are given with
    # forward slashes, whatever the platform.
    product = SimpleNamespace(
        path=product_label.with_suffix(".bc").as_posix(),
        checksum=SHARED_MD5,
        label=SimpleNamespace(name=product_label.as_posix()))
    readme_label = SimpleNamespace(name=bundle_label.as_posix())
    setup = _make_setup(pds_version="4", increment=False)
    setup.staging_directory = str(staging)
    setup.bundle_directory = str(tmp_path / "bundle")
    setup.args.debug = debug
    collection = _make_collection()
    collection.bundle = SimpleNamespace(
        collections=[SimpleNamespace(product=[product])],
        readme=SimpleNamespace(label=readme_label))

    # Create the product, add the file that shares the MD5, and write the
    # table.
    with caplog.at_level(logging.WARNING):
        checksum = ChecksumProduct(setup, collection)
        checksum.md5_dict["other/different_name.tab"] = SHARED_MD5
        checksum.write_product()

    # Both files are in the table and the warnings name them.
    table = "".join(line + setup.eol for line in DUPLICATE_MD5_TABLE_LINES)
    assert Path(checksum.path).read_bytes() == written_as(table)
    assert [r.getMessage() for r in caplog.records] == DUPLICATE_MD5_WARNINGS
