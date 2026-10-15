"""PDS4 version-specific collection inventory product."""

from .product_inventory import InventoryProduct
from .product_pds4 import PDS4Product


class InventoryPDS4Product(InventoryProduct, PDS4Product):
    """Collection inventory product of a PDS4 bundle (a CSV file).

    For now this only fixes the class the pipeline builds for PDS4. The
    PDS4-specific code still lives in :class:`InventoryProduct` and moves
    here next.
    """
