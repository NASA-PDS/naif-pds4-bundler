"""PDS3 version-specific base class for products."""

from .product import Product


class PDS3Product(Product):
    """Version-specific base class for PDS3 products.

    Leaf PDS3 product classes still do their own ``__init__``; this class
    exists so that ``register()`` can ask any product for its archive root
    directory without checking ``setup.pds_version``.
    """

    @property
    def _archive_root_dir(self) -> str:
        """Volume identifier, the top-level directory of a PDS3 archive."""
        return self.setup.volume_id
