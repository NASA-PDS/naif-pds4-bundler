"""Tests for the ChecksumPDS3Label class.

Two test classes are provided:

* TestChecksumPDS3LabelUnit  – pure unit tests that mock every external
  dependency (filesystem, PDSLabel.write_label, sibling modules).

* TestChecksumPDS3LabelIntegration – integration tests that exercise
  ChecksumPDS3Label together with the real PDSLabel.write_label() logic
  and the real template file, writing an actual label to a temp directory
  and asserting on its contents.
"""
from pathlib import Path
import textwrap
from unittest.mock import MagicMock, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds3_checksum import ChecksumPDS3Label

# ---------------------------------------------------------------------------
# Helpers – factories for the two collaborator mocks (setup & product)
# ---------------------------------------------------------------------------

def _make_setup(tmp_path: Path, *, pds_version: str = "3") -> MagicMock:
    """Return a fully-configured mock Setup object for PDS3 usage."""
    setup = MagicMock()
    setup.pds_version = pds_version
    setup.volume_id = "vg_0001"
    setup.mission_acronym = "vgr"
    setup.mission_name = "Voyager"
    setup.observer = "Voyager 1"
    setup.target = "Jupiter"
    setup.root_dir = str(tmp_path)
    setup.templates_directory = str(tmp_path / "templates")
    setup.staging_directory = str(tmp_path / "staging")
    setup.working_directory = str(tmp_path / "work")
    setup.diff = False
    setup.eol_pds3 = "\r\n"
    # args namespace expected by write_label
    setup.args.silent = True
    setup.args.verbose = False
    # add_file must be callable without side-effects
    setup.add_file = MagicMock()
    return setup


def _make_product(staging_dir: Path) -> MagicMock:
    """Return a mock Checksum product object."""
    product = MagicMock()
    product.creation_time = "2024-01-15T12:00:00"
    product.creation_date = "2024-01-15"
    product.record_bytes = 80
    product.file_records = 42
    product.bytes = 46          # path column width in template
    product.size = 3360
    product.checksum = "d41d8cd98f00b204e9800998ecf8427e"
    product.name = "checksum.tab"
    product.extension = "tab"
    # path used by write_label to derive the label filename
    product.path = str(staging_dir / "checksum.tab")
    return product


# ===========================================================================
# Class 1 – Unit tests (all external I/O is mocked)
# ===========================================================================

class TestChecksumPDS3Label:
    """Unit tests for ChecksumPDS3Label.

    Every collaborator (filesystem, write_label, PDSLabel.__init__) is
    mocked so that tests remain fast, isolated, and deterministic.
    """

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    @pytest.fixture()
    def label(self, tmp_path):
        """Return a ChecksumPDS3Label with write_label mocked out."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)

        # Patch write_label so the constructor does not touch the filesystem.
        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True):
            instance = ChecksumPDS3Label(setup, product)

        return instance

    # ------------------------------------------------------------------
    # Regular Tests
    # ------------------------------------------------------------------
    def test_attribute_assignments(self, label):
        assert label.VOLUME_ID == "VG_0001"
        assert label.PRODUCT_CREATION_TIME == "2024-01-15T12:00:00"
        assert label.RECORD_BYTES == "80"
        assert label.FILE_RECORDS == "42"
        assert label.BYTES == "46"
        assert label.name == "checksum.lbl"

    def test_template_path_uses_setup_directory(self, tmp_path, label):
        """Template path must be constructed from setup.templates_directory."""
        expected = str(
            Path(tmp_path / "templates")
            / "template_product_checksum_table.lbl"
        )
        assert label.template == expected

    def test_setup_and_product_reference_stored(self, tmp_path):
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)

        # Patch write_label so the constructor does not touch the filesystem.
        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True):
            label = ChecksumPDS3Label(setup, product)
        assert label.setup == setup
        assert label.product == product

    def test_write_label_called_once_during_init(self, tmp_path):
        """Constructor must call write_label exactly once."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)

        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True) as mock_write:
            ChecksumPDS3Label(setup, product)

        mock_write.assert_called_once()

    def test_is_instance_of_pds_label(self, label):
        """ChecksumPDS3Label must be a subclass of PDSLabel."""
        from pds.naif_pds4_bundler.classes.label.label import PDSLabel
        assert isinstance(label, PDSLabel)

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_volume_id_already_uppercase_unchanged(self, tmp_path):
        """If volume_id is already uppercase, VOLUME_ID must still match."""
        setup = _make_setup(tmp_path)
        setup.volume_id = "VG_0001"
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)

        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True):
            instance = ChecksumPDS3Label(setup, product)

        assert instance.VOLUME_ID == "VG_0001"

    def test_zero_file_records(self, tmp_path):
        """RECORD_BYTES must tolerate a product with zero file records."""
        setup = _make_setup(tmp_path)
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)
        product.file_records = 0

        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True):
            instance = ChecksumPDS3Label(setup, product)

        assert instance.FILE_RECORDS == "0"

    def test_creation_time_override_from_setup(self, tmp_path):
        """When setup.creation_date_time exists, PRODUCT_CREATION_TIME must
        reflect it (behavior inherited from PDSLabel.__init__)."""
        setup = _make_setup(tmp_path)
        setup.creation_date_time = "2099-12-31T23:59:59"
        staging = tmp_path / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        product = _make_product(staging)

        with patch("pds.naif_pds4_bundler.classes.label.label.PDSLabel.write_label",
                   autospec=True):
            instance = ChecksumPDS3Label(setup, product)

        # PDSLabel.__init__ sets PRODUCT_CREATION_TIME from setup when the
        # attribute exists; ChecksumPDS3Label then *overwrites* it with the
        # product value. Assert the child-class assignment wins.
        assert instance.PRODUCT_CREATION_TIME == product.creation_time


# ===========================================================================
# Class 2 – Integration tests (real PDSLabel + real template)
# ===========================================================================

TEMPLATE_CONTENT = textwrap.dedent("""\
    PDS_VERSION_ID        = PDS3

    RECORD_TYPE           = "FIXED_LENGTH"
    FILE_RECORDS          = $FILE_RECORDS
    RECORD_BYTES          = $RECORD_BYTES

    ^TABLE                = "checksum.tab"

    VOLUME_ID             = "$VOLUME_ID"
    PRODUCT_NAME          = "MD5 CHECKSUM TABLE FOR VOLUME $VOLUME_ID"
    PRODUCT_CREATION_TIME = $PRODUCT_CREATION_TIME
    START_TIME            = "N/A"
    STOP_TIME             = "N/A"

    OBJECT     = TABLE
      INTERCHANGE_FORMAT = "ASCII"
      ROWS               = $FILE_RECORDS
      ROW_BYTES          = $RECORD_BYTES
      COLUMNS            = 2

      OBJECT     = COLUMN
        COLUMN_NUMBER = 1
        NAME          = "MD5_CHECKSUM"
        START_BYTE    = 1
        BYTES         = 32
        DATA_TYPE     = "CHARACTER"
        FORMAT        = "A32"
        DESCRIPTION   = "MD5 checksum presented as a 32-character string of
          hexadecimal digits (0-9,a-f)"
      END_OBJECT = COLUMN

      OBJECT     = COLUMN
        COLUMN_NUMBER = 2
        NAME          = "FILE_SPECIFICATION_NAME"
        START_BYTE    = 35
        BYTES         = $BYTES
        DATA_TYPE     = "CHARACTER"
        FORMAT        = "A$BYTES"
        DESCRIPTION   = "File name and path from the volume root"
      END_OBJECT = COLUMN

    END_OBJECT = TABLE

    END
""")


class TestChecksumPDS3LabelIntegration:
    """Integration tests for ChecksumPDS3Label + PDSLabel + template.

    These tests instantiate the real class (without patching write_label)
    and assert on the content of the label file written to a temp directory.

    External I/O that is *unrelated* to label writing (logging, add_file,
    compare) is still mocked to keep the tests self-contained.
    """

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    @pytest.fixture()
    def env(self, tmp_path):
        """Set up a realistic directory tree and write the template."""
        templates_dir = tmp_path / "templates"
        staging_dir = tmp_path / "staging"
        templates_dir.mkdir()
        staging_dir.mkdir()

        # Write the template the class will read.
        template_path = templates_dir / "template_product_checksum_table.lbl"
        template_path.write_text(TEMPLATE_CONTENT, encoding="utf-8")

        setup = _make_setup(tmp_path)
        # Make staging_directory point at our staging dir so write_label
        # can call Path(label_name).relative_to(setup.staging_directory).
        setup.staging_directory = str(staging_dir)
        setup.eol_pds3 = "\r\n"   # use LF for easier cross-platform assertions

        product = _make_product(staging_dir)

        return {
            "tmp_path": tmp_path,
            "templates_dir": templates_dir,
            "staging_dir": staging_dir,
            "setup": setup,
            "product": product,
            "label_path": staging_dir / "checksum.lbl",
        }

    # ------------------------------------------------------------------
    # 1. File creation
    # ------------------------------------------------------------------

    def test_label_file_is_created(self, env):
        setup = env["setup"]
        product = env["product"]

        ChecksumPDS3Label(setup, product)

        assert env["label_path"].exists()

        with open(env["label_path"], "rt", encoding="utf-8", newline='') as f:
            written_label = f.read()

        expected_label = (
            'PDS_VERSION_ID        = PDS3                                                  \r\n'
            '                                                                              \r\n'
            'RECORD_TYPE           = "FIXED_LENGTH"                                        \r\n'
            'FILE_RECORDS          = 42                                                    \r\n'
            'RECORD_BYTES          = 80                                                    \r\n'
            '                                                                              \r\n'
            '^TABLE                = "checksum.tab"                                        \r\n'
            '                                                                              \r\n'
            'VOLUME_ID             = "VG_0001"                                             \r\n'
            'PRODUCT_NAME          = "MD5 CHECKSUM TABLE FOR VOLUME VG_0001"               \r\n'
            'PRODUCT_CREATION_TIME = 2024-01-15T12:00:00                                   \r\n'
            'START_TIME            = "N/A"                                                 \r\n'
            'STOP_TIME             = "N/A"                                                 \r\n'
            '                                                                              \r\n'
            'OBJECT     = TABLE                                                            \r\n'
            '  INTERCHANGE_FORMAT = "ASCII"                                                \r\n'
            '  ROWS               = 42                                                     \r\n'
            '  ROW_BYTES          = 80                                                     \r\n'
            '  COLUMNS            = 2                                                      \r\n'
            '                                                                              \r\n'
            '  OBJECT     = COLUMN                                                         \r\n'
            '    COLUMN_NUMBER = 1                                                         \r\n'
            '    NAME          = "MD5_CHECKSUM"                                            \r\n'
            '    START_BYTE    = 1                                                         \r\n'
            '    BYTES         = 32                                                        \r\n'
            '    DATA_TYPE     = "CHARACTER"                                               \r\n'
            '    FORMAT        = "A32"                                                     \r\n'
            '    DESCRIPTION   = "MD5 checksum presented as a 32-character string of       \r\n'
            '      hexadecimal digits (0-9,a-f)"                                           \r\n'
            '  END_OBJECT = COLUMN                                                         \r\n'
            '                                                                              \r\n'
            '  OBJECT     = COLUMN                                                         \r\n'
            '    COLUMN_NUMBER = 2                                                         \r\n'
            '    NAME          = "FILE_SPECIFICATION_NAME"                                 \r\n'
            '    START_BYTE    = 35                                                        \r\n'
            '    BYTES         = 46                                                        \r\n'
            '    DATA_TYPE     = "CHARACTER"                                               \r\n'
            '    FORMAT        = "A46"                                                     \r\n'
            '    DESCRIPTION   = "File name and path from the volume root"                 \r\n'
            '  END_OBJECT = COLUMN                                                         \r\n'
            '                                                                              \r\n'
            'END_OBJECT = TABLE                                                            \r\n'
            '                                                                              \r\n'
            'END                                                                           \r\n')

        assert written_label == expected_label

    # ------------------------------------------------------------------
    # 7. setup.add_file is called with the relative label path
    # ------------------------------------------------------------------

    def test_add_file_called_with_label_path(self, env):
        """setup.add_file() must be invoked with the relative label path."""
        setup = env["setup"]
        product = env["product"]

        ChecksumPDS3Label(setup, product)

        setup.add_file.assert_called_once_with("checksum.lbl")