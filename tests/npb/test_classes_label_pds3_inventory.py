"""Tests for the InventoryPDS3Label class.

Two test classes are provided:

* TestInventoryPDS3LabelUnit        – pure unit tests that mock every external
  dependency (filesystem, PDSLabel.write_label, sibling modules).

* TestInventoryPDS3LabelIntegration – integration tests that exercise
  InventoryPDS3Label together with the real PDSLabel.write_label() logic and
  the real template, writing an actual label to a temp directory and asserting
  on its content.
"""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds3_inventory import InventoryPDS3Label

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# 10 columns are declared in the template.
NUM_COLUMNS = 10

# Column widths and start bytes used across all fixtures.
COLUMN_BYTES = [19, 19, 60, 40, 19, 4, 10, 3, 40, 8]
COLUMN_START_BYTES = [1, 21, 41, 102, 143, 163, 168, 179, 183, 224]

# ---------------------------------------------------------------------------
# Helpers – mock factories
# ---------------------------------------------------------------------------

def _make_setup(tmp_path: Path) -> MagicMock:
    """Return a fully-configured mock Setup object for PDS3 usage."""
    setup = MagicMock()
    setup.pds_version = "3"
    setup.volume_id = "vg_0001"
    setup.mission_acronym = "vgr"
    setup.mission_name = "Voyager"
    setup.observer = "Voyager 1"
    setup.target = "Jupiter"
    setup.root_dir = str(tmp_path)
    setup.staging_directory = str(tmp_path / "staging")
    setup.working_directory = str(tmp_path / "work")
    setup.eol_pds3 = "\r\n"
    setup.diff = False
    setup.args.silent = True
    setup.args.verbose = False

    # add_file must be callable without side effects.
    setup.add_file = MagicMock()
    return setup


def _make_collection(collection_type: str = "spice_kernels") -> MagicMock:
    """Return a mock Collection object."""
    return MagicMock(type=collection_type, name=collection_type)


def _make_product(staging_dir: Path) -> MagicMock:
    """Return a mock Inventory product with 10 columns."""
    product = MagicMock()
    product.name = "INDEX.TAB"
    product.extension = "TAB"
    product.path = str(staging_dir / "INDEX.TAB")
    product.creation_time = "2024-06-01T08:00:00"
    product.creation_date = "2024-06-01"
    product.size = 23100
    product.checksum = "abc123def456"
    product.row_bytes = 232
    product.rows = 100
    product.column_bytes = list(COLUMN_BYTES)
    product.column_start_bytes = list(COLUMN_START_BYTES)
    # Single file-type path (the simple branch)
    product.file_types = ["bc"]
    return product


# ===========================================================================
# Class 1 – Unit tests (all external I/O is mocked)
# ===========================================================================

class TestInventoryPDS3LabelUnit:
    """Unit tests for InventoryPDS3Label.

    write_label and the filesystem are mocked out so tests stay fast,
    isolated, and deterministic.
    """

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path):
        """Return an InventoryPDS3Label instance with write_label stubbed."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        collection = _make_collection()
        product = _make_product(staging)

        with patch(
            "pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label", autospec=True
        ):
            instance = InventoryPDS3Label(setup, collection, product)

        return instance

    @pytest.fixture()
    def label_multi(self, tmp_path):
        """Label instance with two file types."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        collection = _make_collection()
        product = _make_product(staging)
        product.file_types = ["tf", "bc"]          # unsorted on purpose

        with patch(
            "pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label", autospec=True
        ):
            instance = InventoryPDS3Label(setup, collection, product)

        return instance

    def test_template_keys_scalar_fields(self, label):
        """VOLUME_ID must be assigned from setup.volume_id (not uppercased)."""
        assert label.VOLUME_ID == "vg_0001"
        assert label.ROW_BYTES == "232"
        assert label.ROWS == "100"
        assert label.INDEXED_FILE_NAME == "*.bc"

    @pytest.mark.parametrize("i,expected_bytes,expected_start", [
        (idx, COLUMN_BYTES[idx], COLUMN_START_BYTES[idx])
        for idx in range(NUM_COLUMNS)
    ])
    def test_template_keys_dynamic_attributes(self, label, i, expected_bytes, expected_start):
        # BYTES_NN must be set as a string for every column (1-based).
        attr = f"BYTES_{i + 1:02d}"
        assert hasattr(label, attr), f"Missing attribute {attr}"
        assert getattr(label, attr) == str(expected_bytes)

        # START_BYTE_NN must be set as a string for every column (1-based).
        attr = f"START_BYTE_{i + 1:02d}"
        assert hasattr(label, attr), f"Missing attribute {attr}"
        assert getattr(label, attr) == str(expected_start)

    def test_no_extra_column_attributes(self, label):
        """No column attribute for index 11 or beyond must be set."""
        assert not hasattr(label, f"BYTES_{NUM_COLUMNS + 1:02d}")
        assert not hasattr(label, f"START_BYTE_{NUM_COLUMNS + 1:02d}")

    def test_indexed_file_name_multiple_types(self, label_multi):
        assert label_multi.INDEXED_FILE_NAME == ('{\r\n'
                                                 '                               "*.bc",\r\n'
                                                 '                               "*.tf"\r\n'
                                                 '                             }\n')

    def test_is_instance_of_pds_label(self, label):
        """InventoryPDS3Label must be a subclass of PDSLabel."""
        from pds.naif_pds4_bundler.classes.label.label import PDSLabel
        assert isinstance(label, PDSLabel)

    # ------------------------------------------------------------------
    # 8. write_label called once
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("collection_type, expected_path", [
        ('spice_kernels', 'templates/pds3/template_collection_spice_kernels.lbl'),
        ('miscellaneous', 'templates/pds3/template_collection_miscellaneous.lbl')
    ])
    def test_write_label_called_once_during_init(self, tmp_path, collection_type, expected_path):
        """Constructor must call write_label exactly once."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        collection = _make_collection(collection_type)
        product = _make_product(staging)

        with patch(
            "pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label", autospec=True
        ) as mock_write:
            label = InventoryPDS3Label(setup, collection, product)

        mock_write.assert_called_once()

        # Template path must embed root_dir and collection.type.
        assert label.template == f"{tmp_path}/{expected_path}"
        assert label.collection ==  collection
        assert label.collection.type == collection_type

    def test_zero_rows(self, tmp_path):
        """ROWS must tolerate zero rows without error."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)
        product.rows = 0

        with patch(
            "pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label", autospec=True
        ):
            instance = InventoryPDS3Label(setup, _make_collection(), product)

        assert instance.ROWS == "0"

    def test_single_column_only(self, tmp_path):
        """Constructor must work when the product exposes only one column."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)
        product.column_bytes = [50]
        product.column_start_bytes = [1]

        with patch(
            "pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label", autospec=True
        ):
            instance = InventoryPDS3Label(setup, _make_collection(), product)

        assert getattr(instance, 'BYTES_01') == '50'
        assert getattr(instance, 'START_BYTE_01') == '1'
        assert not hasattr(instance, 'BYTES_02')


# ===========================================================================
# Class 2 – Integration tests (real PDSLabel + real template)
# ===========================================================================

TEMPLATE_CONTENT = textwrap.dedent("""\
    PDS_VERSION_ID             = PDS3
    VOLUME_ID                  = $VOLUME_ID
    RECORD_TYPE                = FIXED_LENGTH
    RECORD_BYTES               = $ROW_BYTES
    FILE_RECORDS               = $ROWS
    ^INDEX_TABLE               = "INDEX.TAB"

    OBJECT                     = INDEX_TABLE

      INTERCHANGE_FORMAT       = ASCII
      ROW_BYTES                = $ROW_BYTES
      ROWS                     = $ROWS
      COLUMNS                  = 10
      INDEX_TYPE               = SINGLE
      INDEXED_FILE_NAME        = $INDEXED_FILE_NAME

      OBJECT                   = COLUMN
        NAME                   = START_TIME
        DATA_TYPE              = "TIME"
        START_BYTE             = $START_BYTE_01
        BYTES                  = $BYTES_01
        FORMAT                 = "A$BYTES_01"
        DESCRIPTION            = "Start time of the product."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = STOP_TIME
        DATA_TYPE              = "TIME"
        START_BYTE             = $START_BYTE_02
        BYTES                  = $BYTES_02
        FORMAT                 = "A$BYTES_02"
        DESCRIPTION            = "Stop time of the product."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = FILE_SPECIFICATION_NAME
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_03
        BYTES                  = $BYTES_03
        FORMAT                 = "A$BYTES_03"
        DESCRIPTION            = "Unix style path and label file name."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = DATA_SET_ID
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_04
        BYTES                  = $BYTES_04
        FORMAT                 = "A$BYTES_04"
        DESCRIPTION            = "Data set ID."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = PRODUCT_CREATION_TIME
        DATA_TYPE              = "TIME"
        START_BYTE             = $START_BYTE_05
        BYTES                  = $BYTES_05
        FORMAT                 = "A$BYTES_05"
        DESCRIPTION            = "Product creation time."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = RELEASE_ID
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_06
        BYTES                  = $BYTES_06
        FORMAT                 = "A$BYTES_06"
        DESCRIPTION            = "Identifier for product release."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = RELEASE_DATE
        DATA_TYPE              = "DATE"
        START_BYTE             = $START_BYTE_07
        BYTES                  = $BYTES_07
        FORMAT                 = "A$BYTES_07"
        DESCRIPTION            = "Date on which the product was released."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = KERNEL_TYPE_ID
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_08
        BYTES                  = $BYTES_08
        FORMAT                 = "A$BYTES_08"
        DESCRIPTION            = "Kernel type."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = PRODUCT_ID
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_09
        BYTES                  = $BYTES_09
        FORMAT                 = "A$BYTES_09"
        DESCRIPTION            = "Kernel file name."
      END_OBJECT               = COLUMN

      OBJECT                   = COLUMN
        NAME                   = VOLUME_ID
        DATA_TYPE              = "CHARACTER"
        START_BYTE             = $START_BYTE_10
        BYTES                  = $BYTES_10
        FORMAT                 = "A$BYTES_10"
        DESCRIPTION            = "The volume containing this data file."
      END_OBJECT               = COLUMN

    END_OBJECT                 = INDEX_TABLE
    END
""")


class TestInventoryPDS3LabelIntegration:
    """Integration tests for InventoryPDS3Label + PDSLabel + template.

    These tests instantiate the real class without patching write_label, so
    the actual label file is written to a temp directory. Only
    add_carriage_return is patched to avoid cross-platform EOL noise.
    """

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path):
        """Set up directory tree, write the template, and build mocks."""
        templates_dir = tmp_path / "templates" / "pds3"
        staging_dir = tmp_path / "staging"
        templates_dir.mkdir(parents=True)
        staging_dir.mkdir(parents=True)

        template_path = templates_dir / "template_collection_spice_kernels.lbl"
        template_path.write_text(TEMPLATE_CONTENT, encoding="utf-8")

        setup = _make_setup(tmp_path)
        setup.staging_directory = str(staging_dir)

        collection = _make_collection()
        product = _make_product(staging_dir)

        return {
            "tmp_path": tmp_path,
            "templates_dir": templates_dir,
            "staging_dir": staging_dir,
            "setup": setup,
            "collection": collection,
            "product": product,
            # write_label derives the output path by stripping the product
            # extension and appending the label extension.
            "label_path": staging_dir / "INDEX.lbl",
        }

    # ------------------------------------------------------------------
    # 1. File creation
    # ------------------------------------------------------------------

    def test_label_file_is_created(self, env):
        setup = env["setup"]
        product = env["product"]
        collection = env["collection"]

        InventoryPDS3Label(setup, collection, product)

        assert env["label_path"].exists()

        with open(env["label_path"], "rt", encoding="utf-8", newline='') as f:
            written_label = f.read()

        expected_label = ('PDS_VERSION_ID             = PDS3\r\n'
                          'VOLUME_ID                  = vg_0001\r\n'
                          'RECORD_TYPE                = FIXED_LENGTH\r\n'
                          'RECORD_BYTES               = 232\r\n'
                          'FILE_RECORDS               = 100\r\n'
                          '^INDEX_TABLE               = "INDEX.TAB"\r\n'
                          '\r\n'
                          'OBJECT                     = INDEX_TABLE\r\n'
                          '\r\n'
                          '  INTERCHANGE_FORMAT       = ASCII\r\n'
                          '  ROW_BYTES                = 232\r\n'
                          '  ROWS                     = 100\r\n'
                          '  COLUMNS                  = 10\r\n'
                          '  INDEX_TYPE               = SINGLE\r\n'
                          '  INDEXED_FILE_NAME        = *.bc\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = START_TIME\r\n'
                          '    DATA_TYPE              = "TIME"\r\n'
                          '    START_BYTE             = 1\r\n'
                          '    BYTES                  = 19\r\n'
                          '    FORMAT                 = "A19"\r\n'
                          '    DESCRIPTION            = "Start time of the product."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = STOP_TIME\r\n'
                          '    DATA_TYPE              = "TIME"\r\n'
                          '    START_BYTE             = 21\r\n'
                          '    BYTES                  = 19\r\n'
                          '    FORMAT                 = "A19"\r\n'
                          '    DESCRIPTION            = "Stop time of the product."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = FILE_SPECIFICATION_NAME\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 41\r\n'
                          '    BYTES                  = 60\r\n'
                          '    FORMAT                 = "A60"\r\n'
                          '    DESCRIPTION            = "Unix style path and label file name."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = DATA_SET_ID\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 102\r\n'
                          '    BYTES                  = 40\r\n'
                          '    FORMAT                 = "A40"\r\n'
                          '    DESCRIPTION            = "Data set ID."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = PRODUCT_CREATION_TIME\r\n'
                          '    DATA_TYPE              = "TIME"\r\n'
                          '    START_BYTE             = 143\r\n'
                          '    BYTES                  = 19\r\n'
                          '    FORMAT                 = "A19"\r\n'
                          '    DESCRIPTION            = "Product creation time."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = RELEASE_ID\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 163\r\n'
                          '    BYTES                  = 4\r\n'
                          '    FORMAT                 = "A4"\r\n'
                          '    DESCRIPTION            = "Identifier for product release."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = RELEASE_DATE\r\n'
                          '    DATA_TYPE              = "DATE"\r\n'
                          '    START_BYTE             = 168\r\n'
                          '    BYTES                  = 10\r\n'
                          '    FORMAT                 = "A10"\r\n'
                          '    DESCRIPTION            = "Date on which the product was released."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = KERNEL_TYPE_ID\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 179\r\n'
                          '    BYTES                  = 3\r\n'
                          '    FORMAT                 = "A3"\r\n'
                          '    DESCRIPTION            = "Kernel type."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = PRODUCT_ID\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 183\r\n'
                          '    BYTES                  = 40\r\n'
                          '    FORMAT                 = "A40"\r\n'
                          '    DESCRIPTION            = "Kernel file name."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          '  OBJECT                   = COLUMN\r\n'
                          '    NAME                   = VOLUME_ID\r\n'
                          '    DATA_TYPE              = "CHARACTER"\r\n'
                          '    START_BYTE             = 224\r\n'
                          '    BYTES                  = 8\r\n'
                          '    FORMAT                 = "A8"\r\n'
                          '    DESCRIPTION            = "The volume containing this data file."\r\n'
                          '  END_OBJECT               = COLUMN\r\n'
                          '\r\n'
                          'END_OBJECT                 = INDEX_TABLE\r\n'
                          'END\r\n')

        assert written_label == expected_label

    # ------------------------------------------------------------------
    # 9. setup.add_file is called with the relative label path
    # ------------------------------------------------------------------

    def test_add_file_called_with_label_path(self, env):
        """setup.add_file() must be invoked with the relative label path."""
        setup = env["setup"]
        product = env["product"]
        collection = env["collection"]

        InventoryPDS3Label(setup, collection, product)

        setup.add_file.assert_called_once_with("INDEX.lbl")