"""Collection classes for NPB archive collection generation.

Each class represents a distinct archive collection type and is responsible for
grouping and managing the products that belong to its corresponding collection.

Available collections:

- :class:`~.collection_docs.DocumentCollection`           -- document collection
- :class:`~.collection_misc.MiscellaneousCollection`      -- miscellaneous collection
- :class:`~.collection_kernels.SpiceKernelsCollection`    -- SPICE kernels collection
"""

from .collection_docs import DocumentCollection
from .collection_misc import MiscellaneousCollection
from .collection_kernels import SpiceKernelsCollection
