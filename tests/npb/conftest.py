from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

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
    spiceypy.unload(lsk_file)  # Cleanup after the test finishes


# ---------------------------------------------------------------------------
# Shared PDS4 context products
# ---------------------------------------------------------------------------

# The PDS4 context products are consumed by the inherited PDSLabel logic
# (get_missions / get_observers / get_targets). They are identical across
# every PDS4 label test, so they are defined once here.
CONTEXT_PRODUCTS = [
    {'name': ['MAVEN'],
     'type': ['Mission'],
     'lidvid': 'urn:nasa:pds:context:investigation:mission.maven::1.0'},
    {'name': ['MAVEN'],
     'type': ['Spacecraft'],
     'lidvid': 'urn:nasa:pds:context:instrument_host:spacecraft.maven::1.0'},
    {'name': ['Mars'],
     'type': ['Planet'],
     'lidvid': 'urn:nasa:pds:context:target:planet.mars::1.0'}]


# ---------------------------------------------------------------------------
# Generic Setup + base Product factories
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_helpers(tmp_path: Path) -> SimpleNamespace:
    """Provide the generic PDS4 mock factories shared by every label test.

    Returns a container exposing two callables:

    * ``make_setup(end_of_line='LF', eol_pds4='\\n')`` builds a fully
      configured PDS4 Setup mock rooted at the test ``tmp_path``.

    * ``make_product(path, name, lid=..., vid=..., collection_name=...)``
      builds a base PDS4 product mock with only the attributes common to
      every PDS4 product. Each test module specializes it with the fields
      specific to its label.

    :param tmp_path: pytest temporary directory for project folders
    :return: container with ``make_setup`` and ``make_product`` factories
    """

    def _make_setup(end_of_line: str = 'LF',
                    eol_pds4: str = '\n') -> MagicMock:
        setup = MagicMock()

        # Basic execution context expected by the label hierarchy.
        setup.pds_version = '4'
        setup.volume_id = 'maven_0001'
        setup.mission_acronym = 'maven'
        setup.mission_name = 'MAVEN'
        setup.observer = 'MAVEN'
        setup.target = 'Mars'

        # Secondary context values are empty because these tests only need the
        # primary mission, observer and target metadata.
        setup.secondary_missions = []
        setup.secondary_observers = []
        setup.secondary_targets = []

        # Temporary project directories used by the label writer.
        setup.root_dir = str(tmp_path)
        setup.templates_directory = str(tmp_path / 'templates')
        setup.staging_directory = str(tmp_path / 'staging')
        setup.working_directory = str(tmp_path / 'work')
        setup.bundle_directory = str(tmp_path / 'bundle')

        # Disable unrelated diff/compare behaviour during label generation.
        setup.diff = False

        # PDS4 XML metadata that may be consumed by PDSLabel or rendering.
        setup.xml_model = 'https://pds.nasa.gov/pds4/pds/v1/PDS4_PDS_1F00.sch'
        setup.schema_location = (
            'https://pds.nasa.gov/pds4/pds/v1 PDS4_PDS_1F00.xsd')

        # Joined to ensure version numbers are not confused with IP addresses.
        setup.information_model = '.'.join(['1', '16', '0', '0'])
        setup.information_model_float = 1016000000.0
        setup.logical_identifier = 'urn:nasa:pds:maven_spice'

        # End-of-line configuration used when writing PDS4 XML labels.
        setup.end_of_line = end_of_line
        setup.eol_pds4 = eol_pds4

        # XML indentation configuration expected by the inherited writer.
        setup.xml_tab = 1

        # Simulate CLI flags used by the writer without invoking the parser.
        setup.args = MagicMock()
        setup.args.silent = True
        setup.args.verbose = False

        # Mock side effect so tests can assert the generated label was
        # registered.
        setup.add_file = MagicMock()

        return setup

    def _make_product(path: str, name: str,
                      lid: str = 'urn:nasa:pds:maven_spice:product',
                      vid: str = '1.0',
                      collection_name: str = 'miscellaneous') -> MagicMock:
        # Return a fresh copy of the context products so a test cannot mutate
        # the module-level list and leak that change into another test.
        context_products = [dict(product) for product in CONTEXT_PRODUCTS]

        product = MagicMock()

        # Physical product metadata used directly by the labels and by the
        # inherited writer to derive the XML label path.
        product.name = name
        product.extension = name.rsplit('.', 1)[-1] if '.' in name else ''
        product.path = path

        # PDS4 product identifiers copied by the concrete labels.
        product.lid = lid
        product.vid = vid

        # Temporal coverage copied by several labels.
        product.start_time = '2024-01-01T00:00:00'
        product.stop_time = '2024-01-31T23:59:59'

        # Creation metadata consumed by the inherited PDSLabel writer.
        product.creation_time = '2024-02-01T12:00:00'
        product.creation_date = '2024-02-01'

        # File metadata commonly substituted in PDS4 templates.
        product.size = '2048'
        product.checksum = 'd41d8cd98f00b204e9800998ecf8427e'

        # Collection/bundle context expected by the inherited PDS4 logic.
        product.collection.name = collection_name
        product.collection.bundle.context_products = context_products
        product.bundle.context_products = context_products

        return product

    return SimpleNamespace(make_setup=_make_setup, make_product=_make_product)
