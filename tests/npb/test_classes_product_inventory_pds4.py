"""Unit tests for InventoryPDS4Product class."""
import logging
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.product.product import Product
from pds.naif_pds4_bundler.classes.product.product_inventory import InventoryProduct
from pds.naif_pds4_bundler.classes.product.product_inventory_pds4 import InventoryPDS4Product


def fake_product_init(self, setup) -> None:
    """Stand in for Product.__init__, which only has to store the setup."""
    self.setup = setup


class InventorySubclass(InventoryProduct):
    """Stand-in for a version-specific inventory class."""


# ---------------------------------------------------------------------------
# InventoryPDS4Product.__init__
# ---------------------------------------------------------------------------

# The expected "previous inventory file" candidate. Built by joining path
# segments (never embedding "/" inside a string literal) so it's correct on both
# POSIX and Windows. Kept as a Path -- the parametrized comparison below is
# obj.path_current == path_current, and obj.path_current is itself a Path when a
# previous file was found, so Path.__eq__ (parsed path parts) applies instead of
# a separator-sensitive string comparison.
PREV_INVENTORY_PATH = Path("bundle", "insight_spice", "spice_kernels",
                           "collection_spice_kernels_inventory_v001.csv")


class TestInventoryPDS4ProductInit:
    """Tests for __init__."""

    @pytest.mark.parametrize("increment, previous_version, current, path_current, name, path, vid", [
        (True, [str(PREV_INVENTORY_PATH)], 2, PREV_INVENTORY_PATH, "collection_spice_kernels_inventory_v002.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v002.csv")), "2.0"),
        (True, [], 1, "", "collection_spice_kernels_inventory_v001.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v001.csv")), "1.0"),
        (False, [], 1, "", "collection_spice_kernels_inventory_v001.csv",
         str(Path("staging/spice_kernels/collection_spice_kernels_inventory_v001.csv")), "1.0"),
    ])
    @patch("pathlib.Path.glob")
    def test_pds4_attribute_settings(self, mock_glob, increment, previous_version,
                                     current, path_current, name, path, vid,
                                     inventory_helpers):
        """The version, path, name, LID and VID are set up, taking the version
        after the previous inventory file when there is one.
        """
        mock_glob.return_value = previous_version
        setup = inventory_helpers.make_setup(
            pds_version="4", increment=increment)
        collection = inventory_helpers.make_collection()

        with patch.object(InventoryPDS4Product, "write_product"), \
                patch.object(Product, "__init__", autospec=True,
                             side_effect=fake_product_init), \
                patch.object(Product, "derive_file_attributes"):
            obj = InventoryPDS4Product(setup, collection)

        assert obj.version == current

        # path_current is a Path when a previous file was found, and the plain
        # sentinel string "" otherwise. path_current (parametrized) is the
        # matching type in each case, so this compares Path == Path (parsed path
        # parts, not separator-sensitive strings) or "" == "".
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
    @patch("pathlib.Path.glob")
    def test_pds4_init_logic_testing(
            self, mock_glob, increment, glob_call_count, inventory_helpers):
        """The inventory file is written once, and the previous inventories
        are only searched for when the release is an increment.
        """
        mock_glob.return_value = []
        setup = inventory_helpers.make_setup(
            pds_version="4", increment=increment)
        collection = inventory_helpers.make_collection()

        with patch.object(InventoryPDS4Product, "write_product") as mock_write_product, \
                patch.object(Product, "__init__", autospec=True,
                             side_effect=fake_product_init), \
                patch.object(Product, "derive_file_attributes"):
            InventoryPDS4Product(setup, collection)

        mock_write_product.assert_called_once()

        assert mock_glob.call_count == glob_call_count


# ---------------------------------------------------------------------------
# InventoryPDS4Product.write_product
# ---------------------------------------------------------------------------

class TestInventoryPDS4ProductWriteProduct:
    """Tests for write_product()."""

    @staticmethod
    def _make_obj(inventory_helpers, path_current="", products=None):
        obj = InventoryPDS4Product.__new__(InventoryPDS4Product)
        # The file content is what these tests check, not the logging,
        # validation and diff step that write_product() ends with.
        obj._finish_product = MagicMock()
        obj.setup = inventory_helpers.make_setup(pds_version="4")
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v002.csv"
        obj.path_current = path_current

        if products is None:
            products = []
        collection = inventory_helpers.make_collection()
        collection.product = products
        obj.collection = collection
        return obj

    def test_writes_new_products_as_primary(self, inventory_helpers):
        """New products are written as 'P,lid::vid'."""
        product = inventory_helpers.make_product(
            lid="urn:nasa:pds:test::1.0", vid="1.0", new_product=True)
        obj = self._make_obj(inventory_helpers, products=[product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == 'P,urn:nasa:pds:test::1.0::1.0\n'

    def test_skips_inventory_products(self, inventory_helpers):
        """InventoryProduct instances in collection.product are skipped."""
        inventory_product = InventoryPDS4Product.__new__(InventoryPDS4Product)
        obj = self._make_obj(inventory_helpers, products=[inventory_product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == ''

    def test_skips_non_new_products(self, inventory_helpers):
        """Products with new_product=False are not written."""
        product = inventory_helpers.make_product(new_product=False)
        obj = self._make_obj(inventory_helpers, products=[product])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_product()

        handle = m()
        written = "".join(c.args[0] for c in handle.write.call_args_list)
        assert written == ''

    def test_previous_primary_items_become_secondary(self, inventory_helpers):
        """Lines from path_current with "P,urn" are replaced with "S,urn".
        """
        obj = self._make_obj(
            inventory_helpers, path_current="/prev/collection_v001.csv")

        prev_content = ("P,urn:nasa:pds:insight_spice:spice_kernels:ck_v2.bc::1.0\n"
                        "S,urn:nasa:pds:insight_spice:spice_kernels:ck_v1.bc::1.0\n")
        m_out = mock_open()
        m_in = mock_open(read_data=prev_content)

        def open_side_effect(_, mode="r", **__):
            if mode == "w+":
                return m_out.return_value
            return m_in.return_value

        with patch("builtins.open", side_effect=open_side_effect):
            obj.write_product()

        written = "".join(c.args[0] for c in m_out.return_value.write.call_args_list)
        expected = ('S,urn:nasa:pds:insight_spice:spice_kernels:ck_v2.bc::1.0\n'
                    'S,urn:nasa:pds:insight_spice:spice_kernels:ck_v1.bc::1.0\n')
        assert written == expected

    def test_no_path_current_skips_previous_file(self, inventory_helpers):
        """When path_current is empty, only the output file is opened."""
        obj = self._make_obj(inventory_helpers, path_current="", products=[])

        m = mock_open()
        with patch("builtins.open", m):
            obj.write_product()

        # Only one file open (write mode)
        assert m.call_count == 1

    def test_write_product_finishes_the_product(self, inventory_helpers):
        """After writing the file, the inventory is logged, validated and,
        if requested, compared.
        """
        # An inventory with nothing to write
        obj = self._make_obj(inventory_helpers)

        # Write it without touching the disk, keeping hold of the mock that
        # stands in for the shared logging/validation step
        with patch("builtins.open", mock_open()), \
                patch.object(obj, "_finish_product") as mock_finish:
            obj.write_product()

        # The write ends by handing over to that step
        mock_finish.assert_called_once()


# ---------------------------------------------------------------------------
# InventoryPDS4Product.validate
# ---------------------------------------------------------------------------

class TestInventoryPDS4ProductValidate:
    """Tests for validate()."""

    @staticmethod
    def _make_obj(inventory_helpers, products=None):
        obj = InventoryPDS4Product.__new__(InventoryPDS4Product)
        obj.setup = inventory_helpers.make_setup()
        obj.name = "collection_spice_kernels_inventory_v001.csv"
        obj.path = "staging/spice_kernels/collection_spice_kernels_inventory_v001.csv"
        collection = inventory_helpers.make_collection()
        collection.product = products or []
        obj.collection = collection
        return obj

    def test_all_products_found_no_error_logged(self, caplog, inventory_helpers):
        """No error is logged when all products are present in the inventory file."""
        product = inventory_helpers.make_product(lid="urn:nasa:pds:test::1.0")
        obj = self._make_obj(inventory_helpers, products=[product])

        csv_content = "P,urn:nasa:pds:test::1.0::1.0\r\n"
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                caplog.at_level(logging.INFO):
            obj.validate()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    def test_missing_product_logs_error(self, caplog, inventory_helpers):
        """An error is logged when a product is absent from the inventory file."""
        product = inventory_helpers.make_product(lid="urn:nasa:pds:missing::1.0")
        obj = self._make_obj(inventory_helpers, products=[product])

        csv_content = "P,urn:nasa:pds:other::1.0::1.0\r\n"
        with patch("builtins.open", mock_open(read_data=csv_content)), \
                caplog.at_level(logging.INFO):
            obj.validate()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.ERROR, '      Product urn:nasa:pds:missing::1.0 not found. Consider increment re-generation.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected

    @pytest.mark.parametrize("inventory_class", [
        pytest.param(InventoryProduct, id="base_class"),
        pytest.param(InventorySubclass, id="subclass"),
    ])
    def test_inventory_products_skipped(
            self, caplog, inventory_class, inventory_helpers):
        """Inventories, including subclasses of InventoryProduct, in the
        collection are not validated.
        """
        # Skip __init__: the product is only ever checked by its type, and
        # reading its 'lid' would fail if it were not skipped
        inv = inventory_class.__new__(inventory_class)
        obj = self._make_obj(inventory_helpers, products=[inv])

        with patch("builtins.open", mock_open(read_data="")), \
                caplog.at_level(logging.INFO):
            obj.validate()

        expected = [
            (logging.INFO, '-- Validating collection_spice_kernels_inventory_v001.csv...'),
            (logging.INFO, '      Check that all the products are in the collection.'),
            (logging.INFO, '      OK'),
            (logging.INFO, '')
        ]

        messages = [(r[1], r[2]) for r in caplog.record_tuples]
        assert messages == expected
