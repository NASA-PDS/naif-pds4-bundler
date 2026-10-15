"""PDS3 version-specific collection inventory product."""

from .product_inventory import InventoryProduct
from .product_pds3 import PDS3Product


class InventoryPDS3Product(InventoryProduct, PDS3Product):
    """Collection inventory product of a PDS3 archive (the index file).

    For now this only fixes the class the pipeline builds for PDS3. The
    PDS3-specific code still lives in :class:`InventoryProduct` and moves
    here next.
    """
