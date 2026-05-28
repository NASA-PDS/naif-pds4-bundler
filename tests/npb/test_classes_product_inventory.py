"""Unit tests for InventoryProduct class."""
import logging
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_inventory import InventoryProduct

# ---------------------------------------------------------------------------
# Helpers / shared fixtures
# ---------------------------------------------------------------------------

def make_setup(pds_version="4", increment=True, diff=True):
    """Return a minimal mock setup object."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.increment = increment
    setup.diff = diff
    setup.staging_directory = "staging"
    setup.bundle_directory = "/bundle"
    setup.mission_acronym = "insight"
    setup.logical_identifier = "urn:nasa:pds:insight_spice"
    setup.eol_pds4 = "\n"
    setup.eol_pds3 = "\r\n"
    setup.working_directory = "/work"
    setup.volume_id = "INSIGHT_0001"
    setup.root_dir = "/root/"
    setup.args.silent = False
    setup.args.verbose = False
    return setup


def make_collection(name="spice_kernels"):
    """Return a minimal mock collection."""
    collection = MagicMock()
    collection.name = name
    return collection


def make_product(lid="urn:nasa:pds:insight_spice:spice_kernels::1.0", vid="1.0",
                 new_product=True, is_inventory=False):
    """Return a mock product."""
    product = MagicMock()
    product.lid = lid
    product.vid = vid
    product.new_product = new_product
    product.__class__.__name__ = "InventoryProduct" if is_inventory else "KernelProduct"
    return product


# ---------------------------------------------------------------------------
# Patch targets (relative to where InventoryProduct imports things)
# ---------------------------------------------------------------------------
MODULE = "pds.naif_pds4_bundler.classes.product.product_inventory"


# ---------------------------------------------------------------------------
# InventoryProduct.__init__ (pds_version 4)
# ---------------------------------------------------------------------------

class TestInventoryProductInitPDS4:
    """Tests for __init__ with pds_version == '4'."""

    @pytest.mark.parametrize("increment, previous_version, current, "
                             "path_current, name, path, vid",[
        (True,
         ["/bundle/insight_spice/spice_kernels/collection_spice_kernels_inventory_v001.csv"],
         2,
         "/bundle/insight_spice/spice_kernels/collection_spice_kernels_inventory_v001.csv",
         "collection_spice_kernels_inventory_v002.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v002.csv")),
         "2.0"),
        (True,
         [],
         1,
         "",
         "collection_spice_kernels_inventory_v001.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v001.csv")),
         "1.0"),
        (False,
         [],
         1,
         "",
         "collection_spice_kernels_inventory_v001.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v001.csv")),
         "1.0"),
    ])
    @patch(f"{MODULE}.glob.glob")
    def test_pds4_attribute_settings(self, mock_glob, increment, previous_version,
                                           current, path_current, name, path, vid):
        mock_glob.return_value = previous_version
        setup = make_setup(pds_version="4", increment=increment)
        collection = make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product"), \
             patch(f"{MODULE}.InventoryPDS4Label"), \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            obj = InventoryProduct(setup, collection)

        assert obj.version == current
        assert obj.path_current == path_current
        assert obj.name == name
        assert obj.path == path
        assert obj.lid == "urn:nasa:pds:insight_spice:document:spiceds"
        assert obj.vid == vid
        assert obj.new_product is True

    @pytest.mark.parametrize("increment, glob_call_count", [
        (True, 2),
        (False, 0)
    ])
    @patch(f"{MODULE}.glob.glob")
    def test_pds4_init_logic_testing(self, mock_glob, increment, glob_call_count):
        """new_product is always True after __init__."""
        mock_glob.return_value = []
        setup = make_setup(pds_version="4", increment=increment)
        collection = make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product") as mock_write_product, \
             patch(f"{MODULE}.InventoryPDS4Label") as mock_label_cls, \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            InventoryProduct(setup, collection)

        mock_write_product.assert_called_once()
        mock_label_cls.assert_called_once()

        assert mock_glob.call_count == glob_call_count

# ---------------------------------------------------------------------------
# InventoryProduct.__init__ (pds_version 3)
# ---------------------------------------------------------------------------

class TestInventoryProductInitPDS3:
    """Tests for __init__ with pds_version == '3'."""

    def test_pds2_attribute_settings(self):
        """For PDS3, path points to index.tab and name is 'index.tab'."""
        setup = make_setup(pds_version="3")
        collection = make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product"), \
             patch(f"{MODULE}.InventoryPDS3Label"), \
             patch(f"{MODULE}.shutil.copy2"), \
             patch(f"{MODULE}.replace_string_in_file"), \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            obj = InventoryProduct(setup, collection)

        assert obj.name == "index.tab"
        assert obj.path == "staging/index/index.tab"
        assert obj.new_product is True

    def test_pds4_init_logic_testing(self):
        """InventoryPDS3Label is instantiated for pds_version == '3'."""
        setup = make_setup(pds_version="3")
        collection = make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product") as mock_write_product, \
             patch(f"{MODULE}.InventoryPDS3Label") as mock_label_cls, \
             patch(f"{MODULE}.shutil.copy2") as mock_copy, \
             patch(f"{MODULE}.replace_string_in_file") as mock_replace, \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            InventoryProduct(setup, collection)

        mock_write_product.assert_called_once()
        mock_label_cls.assert_called_once()

        assert mock_copy.call_count == 2

        mock_replace.assert_called_once_with('staging/../dsindex.lbl',
                                             '"INDEX.TAB"',
                                             '"DSINDEX.TAB"',
                                             setup)

# ---------------------------------------------------------------------------
# InventoryProduct.write_product
# ---------------------------------------------------------------------------

class TestInventoryProductWriteProduct:
    """Tests for write_product()."""

    @staticmethod
    def _make_obj(pds_version="4"):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = make_setup(pds_version=pds_version, diff=True)
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        obj.name = "collection_spice_kernels_inventory_v001.csv"
        return obj

    def test_write_product_pds4_calls_correct_methods(self):
        """write_product() calls write_pds4_collection_product and validate_pds4."""
        obj = self._make_obj("4")

        with patch.object(obj, "write_pds4_collection_product") as mock_write, \
             patch.object(obj, "validate_pds4") as mock_validate, \
             patch.object(obj, "compare") as mock_compare:
            obj.write_product()

        mock_write.assert_called_once()
        mock_validate.assert_called_once()
        mock_compare.assert_called_once()

    def test_write_product_pds3_calls_correct_methods(self):
        """write_product() calls write_pds3_index_product and validate_pds3."""
        obj = self._make_obj("3")

        with patch.object(obj, "write_pds3_index_product") as mock_write, \
             patch.object(obj, "validate_pds3") as mock_validate, \
             patch.object(obj, "compare") as mock_compare:
            obj.write_product()

        mock_write.assert_called_once()
        mock_validate.assert_called_once()
        mock_compare.assert_called_once()

    def test_write_product_no_diff_skips_compare(self, caplog):
        """When setup.diff is False, compare() is not called."""
        obj = self._make_obj("4")
        obj.setup.diff = False

        with patch.object(obj, "write_pds4_collection_product"), \
             patch.object(obj, "validate_pds4"), \
             patch.object(obj, "compare") as mock_compare, \
             caplog.at_level(logging.INFO):
            obj.write_product()

        mock_compare.assert_not_called()
        assert caplog.messages == ['-- Generated collection_spice_kernels_inventory_v001.csv']

    def test_write_product_prints_when_not_silent_or_verbose(self, capsys):
        """Output is printed when silent=False and verbose=False."""
        obj = self._make_obj("4")
        obj.setup.diff = False
        obj.setup.args.silent = False
        obj.setup.args.verbose = False

        with patch.object(obj, "write_pds4_collection_product"), \
             patch.object(obj, "validate_pds4"), \
             patch("builtins.print") as mock_print:
            obj.write_product()

        mock_print.assert_called_once()

    def test_write_product_silent_suppresses_print(self):
        """No print when silent=True."""
        obj = self._make_obj("4")
        obj.setup.diff = False
        obj.setup.args.silent = True
        obj.setup.args.verbose = False

        with patch.object(obj, "write_pds4_collection_product"), \
             patch.object(obj, "validate_pds4"), \
             patch("builtins.print") as mock_print:
            obj.write_product()

        mock_print.assert_not_called()

    def test_write_product_verbose_suppresses_print(self):
        """No print when verbose=True."""
        obj = self._make_obj("4")
        obj.setup.diff = False
        obj.setup.args.silent = False
        obj.setup.args.verbose = True

        with patch.object(obj, "write_pds4_collection_product"), \
             patch.object(obj, "validate_pds4"), \
             patch("builtins.print") as mock_print:
            obj.write_product()

        mock_print.assert_not_called()


# ---------------------------------------------------------------------------
# InventoryProduct.write_pds4_collection_product
# ---------------------------------------------------------------------------

class TestInventoryProductWritePds4CollectionProduct:
    """Tests for write_pds4_collection_product()."""

    @staticmethod
    def _make_obj(path_current="", products=None):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = make_setup(pds_version="4")
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v002.csv"
        obj.path_current = path_current

        if products is None:
            products = []
        collection = make_collection()
        collection.product = products
        obj.collection = collection
        return obj

    def test_writes_new_products_as_primary(self):
        """New products are written as 'P,lid::vid'."""
        product = make_product(lid="urn:nasa:pds:test::1.0", vid="1.0", new_product=True)
        obj = self._make_obj(products=[product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_pds4_collection_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == 'P,urn:nasa:pds:test::1.0::1.0\n'

    def test_skips_inventory_products(self):
        """InventoryProduct instances in collection.product are skipped."""
        inventory_product = InventoryProduct.__new__(InventoryProduct)
        obj = self._make_obj(products=[inventory_product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_pds4_collection_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == ''

    def test_skips_non_new_products(self):
        """Products with new_product=False are not written."""
        product = make_product(new_product=False)
        obj = self._make_obj(products=[product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_pds4_collection_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == ''

    def test_previous_primary_items_become_secondary(self):
        """Lines from path_current with "P,urn" are replaced with "S,urn".
        """
        obj = self._make_obj(path_current="/prev/collection_v001.csv")

        prev_content = ("P,urn:nasa:pds:insight_spice:spice_kernels:ck_v2.bc::1.0\n"
                        "S,urn:nasa:pds:insight_spice:spice_kernels:ck_v1.bc::1.0\n")
        m_out = mock_open()
        m_in = mock_open(read_data=prev_content)

        def open_side_effect(_, mode="r", **__):
            if mode == "w+":
                return m_out.return_value
            return m_in.return_value

        with patch("builtins.open", side_effect=open_side_effect):
            obj.write_pds4_collection_product()

        written = "".join(c.args[0] for c in m_out.return_value.write.call_args_list)
        expected = ('S,urn:nasa:pds:insight_spice:spice_kernels:ck_v2.bc::1.0\n'
                    'S,urn:nasa:pds:insight_spice:spice_kernels:ck_v1.bc::1.0\n')
        assert written == expected

    def test_no_path_current_skips_previous_file(self):
        """When path_current is empty, only the output file is opened."""
        obj = self._make_obj(path_current="", products=[])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_pds4_collection_product()

        # Only one file open (write mode)
        assert m.call_count == 1


# ---------------------------------------------------------------------------
# InventoryProduct.write_pds3_index_product
# ---------------------------------------------------------------------------

class TestInventoryProductWritePds3IndexProduct:
    """Tests for write_pds3_index_product()."""

    @staticmethod
    def _make_kernel():
        k = MagicMock()
        k.start_time = "2020-001T00:00:00Z"
        k.stop_time = "2021-001T00:00:00Z"
        k.path = "/data/ck/insight_ck.bc"
        k.creation_time = "2020-001T00:00:00"
        k.type = "ck"
        k.name = "insight_ck.bc"
        k.__class__.__name__ = "KernelProduct"
        return k

    def _make_obj(self, increment=False, products=None):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = make_setup(pds_version="3", increment=increment)
        obj.path = "staging/index/index.tab"

        collection = make_collection()
        collection.list.DATA_SET_ID = "INSIGHT-M-SPICE-6-V1.0"
        collection.list.RELID = "0001"
        collection.list.RELDATE = "2020-01-01"
        collection.list.VOLID = "INSIGHT_0001"
        if products is not None:
            collection.product = products
        else:
            collection.product = [self._make_kernel()]
        obj.collection = collection
        return obj

    @pytest.mark.parametrize("eol, expected", [
        ('\n', # TODO: Is \n a valid EOL for this? Check with NAIF.
         '2020-001T00:00:00,2021-001T00:00:00,"data/ck/insight_ck.lbl","INSIGHT-M-SPICE-6-V1.0",'
         '2020-001T00:00:00,"0001",2020-01-01,"CK","insight_ck.bc","insight_0001"\n'),
        ('\r\n',
         '2020-001T00:00:00,2021-001T00:00:00,"data/ck/insight_ck.lbl","INSIGHT-M-SPICE-6-V1.0",'
         '2020-001T00:00:00,"0001",2020-01-01,"CK","insight_ck.bc","insight_0001"\r\n')
    ])
    def test_writes_new_index_rows(self, eol, expected):
        """Kernel entries are written as rows in the index file."""
        obj = self._make_obj()
        obj.setup.eol_pds3 = eol

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")), \
             patch(f"{MODULE}.handle_npb_error"):
            obj.write_pds3_index_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == expected

    def test_sets_rows_and_column_attributes(self):
        """rows, column_bytes, column_start_bytes, row_bytes, file_types are set."""
        obj = self._make_obj()

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.handle_npb_error"):
            obj.write_pds3_index_product()

        assert obj.rows == 1
        assert obj.column_bytes == [17, 17, 22, 22, 17, 4, 10, 2, 13, 12]
        assert obj.column_start_bytes == [1, 19, 38, 63, 87, 106, 112, 124, 129, 145]
        assert obj.row_bytes == 159
        assert obj.file_types == ['bc']

    def test_skips_metakernel_products(self):
        """MetaKernelProduct instances are excluded from the index."""
        obj = self._make_obj()
        meta = MagicMock()
        meta.__class__.__name__ = "MetaKernelProduct"
        obj.collection.product = [meta]

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol, s: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")):
            with pytest.raises(RuntimeError, match='The index file is incomplete since no binary '
                                                   'kernel is present in the archive.'):
                # No rows written; handle_npb_error triggered for empty index
                obj.write_pds3_index_product()

    @pytest.mark.parametrize('rows, existing_index', [
        # Windows version.
        (2, '2019-001T00:00:00,"2020-001T00:00:00","data/ck/prev.lbl",'
            '"INSIGHT-M-SPICE-6-V1.0","2019-001","0001","2019-01-01","CK",'
            '"prev.bc","insight_0001"\r\n'),
        # Unix version.
        (2, '2019-001T00:00:00,"2020-001T00:00:00","data/ck/prev.lbl",'
            '"INSIGHT-M-SPICE-6-V1.0","2019-001","0001","2019-01-01","CK",'
            '"prev.bc","insight_0001"\n'),
        # Multiple lines.
        (3, '2020-08-29T21:22:33.166,2020-12-20T01:09:37.544,'
            '"spice_kernels/ck/insight_ida_enc_200829_201220_v1.lbl",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"CK  ",'
            '"insight_ida_enc_200829_201220_v1.bc","NSYTSP_1000"\n'
            '2018-05-05T11:05:00    ,2050-01-01T00:00:00    ,'
            '"spice_kernels/sclk/nsy_sclkscet_00019.lbl            ",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"SCLK",'
            '"nsy_sclkscet_00019.tsc             ","NSYTSP_1000"\n'),
        # Multiple lines. No extra blanks within quoted strings. TODO: Review with NAIF.
        (3, '2020-08-29T21:22:33.166,2020-12-20T01:09:37.544,'
            '"spice_kernels/ck/insight_ida_enc_200829_201220_v1.lbl",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"CK  ",'
            '"insight_ida_enc_200829_201220_v1.bc","NSYTSP_1000"\n'
            '2018-05-05T11:05:00,2050-01-01T00:00:00    ,'
            '"spice_kernels/sclk/nsy_sclkscet_00019.lbl            ",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"SCLK",'
            '"nsy_sclkscet_00019.tsc","NSYTSP_1000"\n'),
        # Multiple lines. Blank lines. TODO: Review with NAIF.
        (3, '2020-08-29T21:22:33.166,2020-12-20T01:09:37.544,'
            '"spice_kernels/ck/insight_ida_enc_200829_201220_v1.lbl",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"CK  ",'
            '"insight_ida_enc_200829_201220_v1.bc","NSYTSP_1000"\n'
            '2018-05-05T11:05:00,2050-01-01T00:00:00    ,'
            '"spice_kernels/sclk/nsy_sclkscet_00019.lbl            ",'
            '"NSYT-M-SPICE-6-V1.0",2021-03-11T21:43:36,"0008",2020-03-16,"SCLK",'
            '"nsy_sclkscet_00019.tsc","NSYTSP_1000"\n'
            '\n'),
        (2, '"N/A"                  ,"N/A"                  ,'
            '"data/ek/10A.lbl                                ",'
            '"CO-S/J/E/V-SPICE-6-V1.0",2005-06-24T07:11:10,"0001",2005-07-01,"EK  ",'
            '"10A.bdb                               ","cosp_1000"\r\n')
    ])
    def test_increment_merges_existing_index(self, rows, existing_index):
        """When increment=True, rows from the existing index are included."""
        obj = self._make_obj(increment=True)
        m_existing = mock_open(read_data=existing_index)
        m_new = mock_open()

        def open_side_effect(_, mode="r", **__):
            if mode == "r":
                return m_existing.return_value
            return m_new.return_value

        with patch("builtins.open", side_effect=open_side_effect), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol, s: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")), \
             patch(f"{MODULE}.handle_npb_error"):
            obj.write_pds3_index_product()

        assert obj.rows == rows

    def test_file_types_deduplicated(self):
        """file_types contains unique values only."""
        k1 = self._make_kernel()
        k2 = self._make_kernel()
        obj = self._make_obj(products=[k1, k2])

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol, s: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")), \
             patch(f"{MODULE}.handle_npb_error"):
            obj.write_pds3_index_product()

        assert len(obj.file_types) == 1


# ---------------------------------------------------------------------------
# InventoryProduct.validate_pds4
# ---------------------------------------------------------------------------

class TestInventoryProductValidatePds4:
    """Tests for validate_pds4()."""

    @staticmethod
    def _make_obj(products=None):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = make_setup()
        obj.name = "collection_spice_kernels_inventory_v001.csv"
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        collection = make_collection()
        collection.product = products or []
        obj.collection = collection
        return obj

    def test_all_products_found_no_error_logged(self, caplog):
        """No error is logged when all products are present in the inventory file."""
        product = make_product(lid="urn:nasa:pds:test::1.0")
        obj = self._make_obj(products=[product])

        csv_content = "P,urn:nasa:pds:test::1.0::1.0\r\n"
        with patch("builtins.open", mock_open(read_data=csv_content)), \
             caplog.at_level(logging.INFO):
            obj.validate_pds4()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_missing_product_logs_error(self, caplog):
        """An error is logged when a product is absent from the inventory file."""
        product = make_product(lid="urn:nasa:pds:missing::1.0")
        obj = self._make_obj(products=[product])

        csv_content = "P,urn:nasa:pds:other::1.0::1.0\r\n"
        with patch("builtins.open", mock_open(read_data=csv_content)), \
             caplog.at_level(logging.INFO):
            obj.validate_pds4()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.ERROR, '      Product urn:nasa:pds:missing::1.0 not found. Consider increment re-generation.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_inventory_products_skipped(self, caplog):
        """InventoryProduct instances in the collection are not validated."""
        inv = InventoryProduct.__new__(InventoryProduct)
        obj = self._make_obj(products=[inv])

        with patch("builtins.open", mock_open(read_data="")), \
             caplog.at_level(logging.INFO):
            obj.validate_pds4()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected


# ---------------------------------------------------------------------------
# InventoryProduct.validate_pds3
# ---------------------------------------------------------------------------

class TestInventoryProductValidatePds3:
    """Tests for validate_pds3()."""

    def test_validate_pds3_logs_name(self, caplog):
        """validate_pds3 logs the inventory name."""
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.name = "index.tab"

        with caplog.at_level(logging.INFO):
            obj.validate_pds3()

        expected = [
            (logging.INFO, '-- Validating index.tab...')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected


# ---------------------------------------------------------------------------
# InventoryProduct.compare
# ---------------------------------------------------------------------------

class TestInventoryProductCompare:
    """Tests for compare()."""

    @staticmethod
    def _make_obj(path_current=""):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = make_setup(diff=True)
        obj.name = "insight_spice/collection_spice_kernels_inventory_v002.csv"
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v002.csv"
        obj.path_current = path_current
        collection = make_collection()
        obj.collection = collection
        return obj

    def test_compare_with_path_current_calls_compare_files(self):
        """compare_files is called with fromfile=path_current when it exists."""
        obj = self._make_obj(path_current="/prev/v001.csv")

        with patch(f"{MODULE}.compare_files") as mock_cf:
            obj.compare()

        mock_cf.assert_called_once_with(
            "/prev/v001.csv",
            obj.path,
            obj.setup.working_directory,
            obj.setup.diff,
        )

    def test_compare_without_path_current_uses_sample(self):
        """When path_current is empty, the latest InSight sample file is used."""
        obj = self._make_obj(path_current="")

        sample_files = [
            "/root/data/insight_spice/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        ]
        with patch(f"{MODULE}.glob.glob", return_value=sample_files), \
             patch(f"{MODULE}.compare_files") as mock_cf:
            obj.compare()

        mock_cf.assert_called_once()
        args = mock_cf.call_args[0]
        assert args[0] == sample_files[-1]

    def test_compare_without_path_current_logs_warning(self, caplog):
        """A warning is logged when falling back to the InSight sample."""
        obj = self._make_obj(path_current="")

        sample_files = [
            "/root/data/insight_spice/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        ]
        with patch(f"{MODULE}.glob.glob", return_value=sample_files), \
             patch(f"{MODULE}.compare_files"), \
             caplog.at_level(logging.INFO):
            obj.compare()

        expected = [
            (logging.INFO, '-- Comparing collection_spice_kernels_inventory_v002.csv...'),
            (logging.WARNING, '-- Comparing with InSight test inventory product.'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
