"""Label classes for NPB archive label generation.

Each class represents a distinct archive label type and is responsible for
generating the XML (PDS4) or PDS3 label file that accompanies its corresponding
archive product.

Available labels:

- :class:`~.pds4_bundle.BundlePDS4Label`            -- PDS4 bundle label
- :class:`~.pds3_checksum.ChecksumPDS3Label`        -- PDS3 checksum label
- :class:`~.pds4_checksum.ChecksumPDS4Label`        -- PDS4 checksum label
- :class:`~.pds4_document.DocumentPDS4Label`        -- PDS4 document label
- :class:`~.pds3_inventory.InventoryPDS3Label`      -- PDS3 index label
- :class:`~.pds4_inventory.InventoryPDS4Label`      -- PDS4 collection inventory label
- :class:`~.pds4_metakernel.MetaKernelPDS4Label`    -- PDS4 SPICE meta-kernel label
- :class:`~.pds4_orbnum_file.OrbnumFilePDS4Label`   -- PDS4 orbit number file label
- :class:`~.pds3_spice_kernel.SpiceKernelPDS3Label` -- PDS3 SPICE kernel label
- :class:`~.pds4_spice_kernel.SpiceKernelPDS4Label` -- PDS4 SPICE kernel label
"""

from .pds4_bundle import BundlePDS4Label
from .pds3_checksum import ChecksumPDS3Label
from .pds4_checksum import ChecksumPDS4Label
from .pds4_document import DocumentPDS4Label
from .pds3_inventory import InventoryPDS3Label
from .pds4_inventory import InventoryPDS4Label
from .pds4_metakernel import MetaKernelPDS4Label
from .pds4_orbnum_file import OrbnumFilePDS4Label
from .pds3_spice_kernel import SpiceKernelPDS3Label
from .pds4_spice_kernel import SpiceKernelPDS4Label
