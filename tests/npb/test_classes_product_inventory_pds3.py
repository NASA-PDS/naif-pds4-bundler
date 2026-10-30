"""Unit tests for InventoryPDS3Product class."""
import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.classes.product.product import Product
from pds.naif_pds4_bundler.classes.product.product_inventory_pds3 import InventoryPDS3Product
from pds.naif_pds4_bundler.classes.product.product_metakernel import MetaKernelProduct


class MetaKernelSubclass(MetaKernelProduct):
    """Stand-in for a version-specific meta-kernel class."""


# ---------------------------------------------------------------------------
# Patch targets (relative to where InventoryPDS3Product imports things)
# ---------------------------------------------------------------------------
MODULE = "pds.naif_pds4_bundler.classes.product.product_inventory_pds3"


# ---------------------------------------------------------------------------
# InventoryPDS3Product.__init__
# ---------------------------------------------------------------------------

class TestInventoryPDS3ProductInit:
    """Tests for __init__."""

    def test_pds3_attribute_settings(
            self, inventory_helpers, fake_product_init):
        """For PDS3, path points to index.tab and name is 'index.tab'."""
        setup = inventory_helpers.make_setup(pds_version="3")
        collection = inventory_helpers.make_collection()

        with patch.object(InventoryPDS3Product, "write_product"), \
             patch.object(Product, "__init__", autospec=True,
                          side_effect=fake_product_init), \
             patch.object(Product, "derive_file_attributes"):
            obj = InventoryPDS3Product(setup, collection)

        assert obj.name == "index.tab"
        assert obj.path == "staging/index/index.tab"
        assert obj.new_product is True

    def test_pds3_write_product_called_once(
            self, inventory_helpers, fake_product_init):
        """write_product() is called exactly once during __init__.

        dsindex generation is no longer part of __init__ -- see
        TestInventoryPDS3ProductGenerateDsindexFiles below.
        """
        setup = inventory_helpers.make_setup(pds_version="3")
        collection = inventory_helpers.make_collection()

        with patch.object(InventoryPDS3Product, "write_product") as mock_write_product, \
             patch.object(Product, "__init__", autospec=True,
                          side_effect=fake_product_init), \
             patch.object(Product, "derive_file_attributes"):
            InventoryPDS3Product(setup, collection)

        mock_write_product.assert_called_once()


# ---------------------------------------------------------------------------
# InventoryPDS3Product.generate_dsindex_files
# ---------------------------------------------------------------------------

class TestInventoryPDS3ProductGenerateDsindexFiles:
    """Tests for generate_dsindex_files().

    PDS3 only. Called by the pipeline after the PDS3 label has been built
    and written to disk -- see the method's own docstring for why.
    """

    @staticmethod
    def _make_obj(inventory_helpers):
        obj = InventoryPDS3Product.__new__(InventoryPDS3Product)
        obj.setup = inventory_helpers.make_setup(pds_version="3")
        obj.path = "staging/index/index.tab"
        return obj

    def test_copies_index_and_label_to_dsindex(self, inventory_helpers):
        """The index file and its label are copied to dsindex.tab and
        dsindex.lbl, and the copied label is pointed at DSINDEX.TAB.
        """
        obj = self._make_obj(inventory_helpers)

        with patch(f"{MODULE}.shutil.copy2") as mock_copy, \
             patch(f"{MODULE}.replace_string_in_file") as mock_replace:
            obj.generate_dsindex_files()

        assert mock_copy.call_count == 2
        mock_copy.assert_any_call(obj.path, "staging/../dsindex.tab")
        mock_copy.assert_any_call("staging/index/index.lbl", "staging/../dsindex.lbl")

        mock_replace.assert_called_once_with(
            "staging/../dsindex.lbl", '"INDEX.TAB"', '"DSINDEX.TAB"', obj.setup
        )


# ---------------------------------------------------------------------------
# InventoryPDS3Product.write_product
# ---------------------------------------------------------------------------

class TestInventoryPDS3ProductWriteProduct:
    """Tests for write_product()."""

    @staticmethod
    def _make_kernel():
        k = MagicMock()
        k.start_time = "2020-001T00:00:00Z"
        k.stop_time = "2021-001T00:00:00Z"
        k.path = "/data/ck/insight_ck.bc"
        k.creation_time = "2020-001T00:00:00"
        k.type = "ck"
        k.name = "insight_ck.bc"
        return k

    def _make_obj(self, inventory_helpers, increment=False, products=None):
        obj = InventoryPDS3Product.__new__(InventoryPDS3Product)
        # The index content is what these tests check, not the logging,
        # validation and diff step that write_product() ends with.
        obj._finish_product = MagicMock()
        obj.setup = inventory_helpers.make_setup(
            pds_version="3", increment=increment)
        obj.path = "staging/index/index.tab"

        collection = inventory_helpers.make_collection()
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
    def test_writes_new_index_rows(self, eol, expected, inventory_helpers):
        """Kernel entries are written as rows in the index file."""
        obj = self._make_obj(inventory_helpers)
        obj.setup.eol_pds3 = eol

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")):
            obj.write_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == expected

    def test_sets_rows_and_column_attributes(self, inventory_helpers):
        """rows, column_bytes, column_start_bytes, row_bytes, file_types are set."""
        obj = self._make_obj(inventory_helpers)

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_product()

        assert obj.rows == 1
        assert obj.column_bytes == [17, 17, 22, 22, 17, 4, 10, 2, 13, 12]
        assert obj.column_start_bytes == [1, 19, 38, 63, 87, 106, 112, 124, 129, 145]
        assert obj.row_bytes == 159
        assert obj.file_types == ['bc']

    @pytest.mark.parametrize("meta_class", [
        pytest.param(MetaKernelProduct, id="base_class"),
        pytest.param(MetaKernelSubclass, id="subclass"),
    ])
    def test_skips_metakernel_products(self, meta_class, inventory_helpers):
        """Meta-kernels, including subclasses of MetaKernelProduct, are
        excluded from the index.
        """
        obj = self._make_obj(inventory_helpers)
        # Skip __init__: the product is only ever checked by its type
        meta = meta_class.__new__(meta_class)
        obj.collection.product = [meta]

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")):
            with pytest.raises(NPBError, match='The index file is incomplete since no binary '
                                                'kernel is present in the archive.'):
                # No rows written; NPBError raised for empty index
                obj.write_product()

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
    def test_increment_merges_existing_index(
            self, rows, existing_index, inventory_helpers):
        """When increment=True, rows from the existing index are included."""
        obj = self._make_obj(inventory_helpers, increment=True)
        m_existing = mock_open(read_data=existing_index)
        m_new = mock_open()

        def open_side_effect(_, mode="r", **__):
            if mode == "r":
                return m_existing.return_value
            return m_new.return_value

        with patch("builtins.open", side_effect=open_side_effect), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")):
            obj.write_product()

        assert obj.rows == rows

    def test_file_types_deduplicated(self, inventory_helpers):
        """file_types contains unique values only."""
        k1 = self._make_kernel()
        k2 = self._make_kernel()
        obj = self._make_obj(inventory_helpers, products=[k1, k2])

        m = mock_open()
        with patch("builtins.open", m), \
             patch(f"{MODULE}.add_carriage_return", side_effect=lambda l, eol: l), \
             patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")):
            obj.write_product()

        assert len(obj.file_types) == 1

    def test_write_product_finishes_the_product(self, inventory_helpers):
        """After writing the index file, the inventory is logged, validated
        and, if requested, compared.
        """
        # An inventory with one kernel to write
        obj = self._make_obj(inventory_helpers)

        # Write it without touching the disk, keeping hold of the mock that
        # stands in for the shared logging/validation step
        with patch("builtins.open", mock_open()), \
                patch(f"{MODULE}.type_to_extension", return_value=("CK", ".bc")), \
                patch.object(obj, "_finish_product") as mock_finish:
            obj.write_product()

        # The write ends by handing over to that step
        mock_finish.assert_called_once()


# ---------------------------------------------------------------------------
# InventoryPDS3Product.validate
# ---------------------------------------------------------------------------

class TestInventoryPDS3ProductValidate:
    """Tests for validate()."""

    def test_validate_logs_name(self, caplog):
        """validate() logs the inventory name."""
        obj = InventoryPDS3Product.__new__(InventoryPDS3Product)
        obj.name = "index.tab"

        with caplog.at_level(logging.INFO):
            obj.validate()

        expected = [
            (logging.INFO, '-- Validating index.tab...')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
