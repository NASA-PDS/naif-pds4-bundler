"""PDS4 version-specific base class for products."""

from .product import Product


class PDS4Product(Product):
    """Version-specific base class for PDS4 products.

    Leaf PDS4 product classes still do their own ``__init__``; this class
    exists so that ``register()`` can ask any product for its archive root
    directory without checking ``setup.pds_version``.
    """

    @property
    def _archive_root_dir(self) -> str:
        """Bundle directory, the top-level directory of a PDS4 archive."""
        return f"{self.setup.mission_acronym}_spice"
