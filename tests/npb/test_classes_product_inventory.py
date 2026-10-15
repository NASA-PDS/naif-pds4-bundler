"""Unit tests for InventoryProduct class."""
import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_inventory import InventoryProduct
from pds.naif_pds4_bundler.classes.product.product_inventory_pds3 import InventoryPDS3Product
from pds.naif_pds4_bundler.classes.product.product_inventory_pds4 import InventoryPDS4Product
from pds.naif_pds4_bundler.classes.product.product_metakernel import MetaKernelProduct
from pds.naif_pds4_bundler.classes.product.product_pds3 import PDS3Product
from pds.naif_pds4_bundler.classes.product.product_pds4 import PDS4Product
from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.classes.run_state import RunState


class MetaKernelSubclass(MetaKernelProduct):
    """Stand-in for a version-specific meta-kernel class."""


# ---------------------------------------------------------------------------
# Patch targets (relative to where InventoryProduct imports things)
# ---------------------------------------------------------------------------
MODULE = "pds.naif_pds4_bundler.classes.product.product_inventory"


# ---------------------------------------------------------------------------
# InventoryProduct.__init__ (pds_version 3)
# ---------------------------------------------------------------------------

class TestInventoryProductInitPDS3:
    """Tests for __init__ with pds_version == '3'."""

    def test_pds2_attribute_settings(self, inventory_helpers):
        """For PDS3, path points to index.tab and name is 'index.tab'."""
        setup = inventory_helpers.make_setup(pds_version="3")
        collection = inventory_helpers.make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product"), \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            obj = InventoryProduct(setup, RunState(), collection)

        assert obj.name == "index.tab"
        assert obj.path == "staging/index/index.tab"
        assert obj.new_product is True

    def test_pds3_write_product_called_once(self, inventory_helpers):
        """write_product() is called exactly once during __init__.

        dsindex generation is no longer part of __init__ -- see
        TestInventoryProductGenerateDsindexFiles below.
        """
        setup = inventory_helpers.make_setup(pds_version="3")
        collection = inventory_helpers.make_collection()

        with patch(f"{MODULE}.InventoryProduct.write_product") as mock_write_product, \
             patch(f"{MODULE}.Product.__init__", return_value=None):
            InventoryProduct(setup, RunState(), collection)

        mock_write_product.assert_called_once()


# ---------------------------------------------------------------------------
# InventoryProduct.generate_dsindex_files
# ---------------------------------------------------------------------------

class TestInventoryProductGenerateDsindexFiles:
    """Tests for generate_dsindex_files().

    PDS3 only. Called by the pipeline after the PDS3 label has been built
    and written to disk -- see the method's own docstring for why.
    """

    @staticmethod
    def _make_obj(inventory_helpers):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = inventory_helpers.make_setup(pds_version="3")
        obj.path = "staging/index/index.tab"
        return obj

    def test_copies_index_and_label_to_dsindex(self, inventory_helpers):
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
# InventoryProduct.write_product
# ---------------------------------------------------------------------------

class TestInventoryProductWriteProduct:
    """Tests for write_product()."""

    @staticmethod
    def _make_obj(inventory_helpers, pds_version="3"):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = inventory_helpers.make_setup(
            pds_version=pds_version, diff=True)
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        obj.name = "collection_spice_kernels_inventory_v001.csv"
        return obj

    def test_write_product_pds3_calls_correct_methods(self, inventory_helpers):
        """write_product() calls write_pds3_index_product and validate_pds3."""
        obj = self._make_obj(inventory_helpers, "3")

        with patch.object(obj, "write_pds3_index_product") as mock_write, \
             patch.object(obj, "validate_pds3") as mock_validate, \
             patch.object(obj, "compare") as mock_compare:
            obj.write_product()

        mock_write.assert_called_once()
        mock_validate.assert_called_once()
        mock_compare.assert_called_once()


# ---------------------------------------------------------------------------
# InventoryProduct._finish_product
# ---------------------------------------------------------------------------

class TestInventoryProductFinishProduct:
    """Tests for _finish_product()."""

    @staticmethod
    def _make_obj(inventory_helpers):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = inventory_helpers.make_setup(diff=True)
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        obj.name = "collection_spice_kernels_inventory_v001.csv"
        return obj

    @pytest.mark.parametrize("diff, compares", [
        pytest.param(True, 1, id="diff"),
        pytest.param(False, 0, id="no_diff"),
    ])
    def test_compares_only_when_diff_requested(
            self, caplog, inventory_helpers, diff, compares):
        """The new file is logged and validated, and compared with the
        previous one only when setup.args.diff is set.
        """
        # Inventory whose setup asks for a diff, or not
        obj = self._make_obj(inventory_helpers)
        obj.setup.args.diff = diff

        # Run the shared step with validation and comparison replaced by mocks
        with patch.object(obj, "validate") as mock_validate, \
             patch.object(obj, "compare") as mock_compare, \
             caplog.at_level(logging.INFO):
            obj._finish_product()

        # Validation always runs; the comparison depends on the diff flag
        mock_validate.assert_called_once()
        assert mock_compare.call_count == compares
        assert caplog.messages == ['-- Generated collection_spice_kernels_inventory_v001.csv']

    @pytest.mark.parametrize("silent, verbose, prints", [
        pytest.param(False, False, 1, id="default"),
        pytest.param(True, False, 0, id="silent"),
        pytest.param(False, True, 0, id="verbose"),
    ])
    def test_created_message_only_when_not_silent_or_verbose(
            self, inventory_helpers, silent, verbose, prints):
        """The 'Created' message is printed only when neither silent nor
        verbose is set.
        """
        # Inventory with the silent/verbose flags of the case and no diff
        obj = self._make_obj(inventory_helpers)
        obj.setup.args.diff = False
        obj.setup.args.silent = silent
        obj.setup.args.verbose = verbose

        # Run the shared step, counting what gets printed
        with patch.object(obj, "validate"), \
             patch("builtins.print") as mock_print:
            obj._finish_product()

        # One 'Created' line when printing is allowed, none otherwise
        assert mock_print.call_count == prints


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
        return k

    def _make_obj(self, inventory_helpers, increment=False, products=None):
        obj = InventoryProduct.__new__(InventoryProduct)
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
            obj.write_pds3_index_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == expected

    def test_sets_rows_and_column_attributes(self, inventory_helpers):
        """rows, column_bytes, column_start_bytes, row_bytes, file_types are set."""
        obj = self._make_obj(inventory_helpers)

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_pds3_index_product()

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
            obj.write_pds3_index_product()

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
            obj.write_pds3_index_product()

        assert len(obj.file_types) == 1


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
    def _make_obj(inventory_helpers, path_current=""):
        obj = InventoryProduct.__new__(InventoryProduct)
        obj.setup = inventory_helpers.make_setup(diff=True)
        obj.name = "insight_spice/collection_spice_kernels_inventory_v002.csv"
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v002.csv"
        obj.path_current = path_current
        collection = inventory_helpers.make_collection()
        obj.collection = collection
        return obj

    def test_compare_with_path_current_calls_compare_files(
            self, inventory_helpers):
        """compare_files is called with fromfile=path_current when it exists."""
        obj = self._make_obj(inventory_helpers, path_current="/prev/v001.csv")

        with patch(f"{MODULE}.compare_files") as mock_cf:
            obj.compare()

        mock_cf.assert_called_once_with(
            "/prev/v001.csv",
            obj.path,
            obj.setup.working_directory,
            obj.setup.args.diff,
        )

    def test_compare_without_path_current_uses_sample(self, inventory_helpers):
        """When path_current is empty, the latest InSight sample file is used."""
        obj = self._make_obj(inventory_helpers, path_current="")

        sample_files = [
            "/root/data/insight_spice/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        ]
        with patch(f"{MODULE}.glob.glob", return_value=sample_files), \
             patch(f"{MODULE}.compare_files") as mock_cf:
            obj.compare()

        mock_cf.assert_called_once()
        args = mock_cf.call_args[0]
        assert args[0] == sample_files[-1]

    def test_compare_without_path_current_logs_warning(
            self, caplog, inventory_helpers):
        """A warning is logged when falling back to the InSight sample."""
        obj = self._make_obj(inventory_helpers, path_current="")

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


# ---------------------------------------------------------------------------
# Inventory subclasses
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("subclass, version_base", [
    pytest.param(InventoryPDS3Product, PDS3Product, id="pds3"),
    pytest.param(InventoryPDS4Product, PDS4Product, id="pds4"),
])
def test_inventory_subclass_hierarchy(subclass, version_base):
    """Each version-specific inventory is an InventoryProduct and also a
    product of its own PDS version.
    """
    # Both links are needed: isinstance() checks in the inventory code rely on
    # the first, and _archive_root_dir comes from the version base
    assert issubclass(subclass, InventoryProduct)
    assert issubclass(subclass, version_base)
