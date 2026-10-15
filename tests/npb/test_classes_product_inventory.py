"""Unit tests for the InventoryProduct base class."""
import logging
from unittest.mock import patch

import pytest

from pds.naif_pds4_bundler.classes.product.product_inventory import InventoryProduct
from pds.naif_pds4_bundler.classes.product.product_inventory_pds3 import InventoryPDS3Product
from pds.naif_pds4_bundler.classes.product.product_inventory_pds4 import InventoryPDS4Product
from pds.naif_pds4_bundler.classes.product.product_pds3 import PDS3Product
from pds.naif_pds4_bundler.classes.product.product_pds4 import PDS4Product


# ---------------------------------------------------------------------------
# Patch targets (relative to where InventoryProduct imports things)
# ---------------------------------------------------------------------------
MODULE = "pds.naif_pds4_bundler.classes.product.product_inventory"


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


# ---------------------------------------------------------------------------
# Version-specific hooks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("hook", [
    pytest.param("_set_location", id="set_location"),
    pytest.param("write_product", id="write_product"),
    pytest.param("validate", id="validate"),
])
def test_version_specific_hooks_are_left_to_subclasses(hook):
    """The base class does not implement the version-specific steps, so
    calling any of them on it is an error.
    """
    # An inventory object built without __init__, which would call the hooks
    obj = InventoryProduct.__new__(InventoryProduct)

    # Each hook is up to the version-specific subclass to provide
    with pytest.raises(NotImplementedError):
        getattr(obj, hook)()
