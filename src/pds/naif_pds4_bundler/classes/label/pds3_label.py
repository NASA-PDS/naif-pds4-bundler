"""PDS3 version-specific base class for PDS labels."""

from .label import PDSLabel


class PDS3Label(PDSLabel):
    """Version-specific base class for PDS3 labels.

    Leaf PDS3 label classes still assign their own PDS3-specific fields
    in their own ``__init__``; this class exists so that ``write_label()``
    can ask any label for its extension and end-of-line convention without
    checking ``setup.pds_version``.
    """

    @property
    def _label_extension(self) -> str:
        """File extension used for PDS3 labels."""
        return ".lbl"

    @property
    def _eol(self) -> str:
        """End-of-line convention used for PDS3 labels."""
        return self.setup.eol_pds3
