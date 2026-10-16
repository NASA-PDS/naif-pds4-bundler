"""Product classes for NPB archive file generation.

Each class represents a distinct archive product type and inherits from
:class:`~.product.Product`, which provides common file attributes (size,
checksum, creation time) and the :meth:`~.product.Product.register` method
that subclasses must call once the product file exists on disk.

Available products:

- :class:`~.product_checksum.ChecksumProduct`     -- checksum table file
- :class:`~.product_inventory_pds3.InventoryPDS3Product` -- PDS3 collection inventory (index file)
- :class:`~.product_inventory_pds4.InventoryPDS4Product` -- PDS4 collection inventory (CSV file)
- :class:`~.product_metakernel.MetaKernelProduct` -- SPICE meta-kernel
- :class:`~.product_orbnum.OrbnumFileProduct`     -- orbit number file
- :class:`~.product_pds3doc.PDS3DocumentProduct`  -- PDS3 document product
- :class:`~.product_readme.ReadmeProduct`         -- bundle readme file
- :class:`~.product_spiceds.SpicedsProduct`       -- SPICE dataset description document
- :class:`~.product_kernel.SpiceKernelProduct`    -- SPICE kernel file
"""

from .product_checksum import ChecksumProduct
from .product_inventory_pds3 import InventoryPDS3Product
from .product_inventory_pds4 import InventoryPDS4Product
from .product_metakernel import MetaKernelProduct
from .product_orbnum import OrbnumFileProduct
from .product_pds3doc import PDS3DocumentProduct
from .product_readme import ReadmeProduct
from .product_spiceds import SpicedsProduct
from .product_kernel import SpiceKernelProduct
