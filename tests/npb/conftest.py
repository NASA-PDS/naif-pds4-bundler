from pathlib import Path

import pytest
import spiceypy

# Get the directory where the data is located.
KERNELS = Path(__file__).parent.parent / "naif_pds4_bundler" / "data" / "kernels"


@pytest.fixture
def lsk():
    """Provides the standard LSK."""
    lsk_file = str(KERNELS / "lsk" / "naif0012.tls")
    spiceypy.furnsh(lsk_file)
    yield
    spiceypy.unload(lsk_file) # Cleanup after the test finishes
