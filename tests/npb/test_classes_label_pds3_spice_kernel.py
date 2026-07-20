"""Unit tests for SpiceKernelPDS3Label
"""
import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pds.naif_pds4_bundler.classes.label.pds3_spice_kernel import SpiceKernelPDS3Label

# ---------------------------------------------------------------------------
# Patch target strings (adjust if the real package path differs)
# ---------------------------------------------------------------------------
MODULE      = "pds.naif_pds4_bundler.classes.label.pds3_spice_kernel"
PARENT_INIT = f"{MODULE}.PDS3Label.__init__"
WRITE_LABEL = f"{MODULE}.SpiceKernelPDS3Label.write_label"
INSERT_TEXT = f"{MODULE}.SpiceKernelPDS3Label.insert_text_label"
INSERT_BIN  = f"{MODULE}.SpiceKernelPDS3Label.insert_binary_label"
SET_IDS     = f"{MODULE}.SpiceKernelPDS3Label.set_kernel_ids"
SET_SCLK    = f"{MODULE}.SpiceKernelPDS3Label.set_sclk_times"
FORMAT_DESC = f"{MODULE}.SpiceKernelPDS3Label.format_description"


# ---------------------------------------------------------------------------
# Shared factory helpers
# ---------------------------------------------------------------------------

def _make_setup():
    """Minimal mock for the *setup* object attached to the label."""
    setup = MagicMock()
    setup.templates_directory = "/fake/templates"
    setup.spice_name = "FAKE_SC"
    setup.pds3_mission_template = {
        "MISSION_NAME": '"FAKE MISSION"',
        "SPACECRAFT_NAME": '"FAKE SPACECRAFT"',
        "maklabel_options": {
            "opt_a": {
                "DATA_SET_ID": '"FAKE-DS-1000-V1.0"',
            }
        },
    }
    return setup


def _make_product(kernel_type="SPK"):
    """Minimal mock for the *product* object."""
    product = MagicMock()
    product.name = "fake_kernel.bsp"
    product.file_format = "BINARY"
    product.start_time = "2000-001T00:00:00Z"
    product.stop_time = "2001-001T00:00:00Z"
    product.type = kernel_type
    product.record_type = "FIXED_LENGTH"
    product.record_bytes = 1024
    product.description = "A fake SPICE kernel used for unit testing purposes only."
    product.maklabel_options = ["opt_a"]
    product.path = "/fake/path/fake_kernel.bsp"
    return product


# ---------------------------------------------------------------------------
# Shared fixture – a label whose __init__ was bypassed via __new__
# ---------------------------------------------------------------------------

@pytest.fixture()
def bare_label():
    """SpiceKernelPDS3Label instance with __init__ skipped."""

    label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)
    label.setup = _make_setup()
    label.product = _make_product()
    label.name = "/fake/output/fake_kernel.lbl"
    return label


# ---------------------------------------------------------------------------
# Helper: build a fully-patched label through __init__
# ---------------------------------------------------------------------------

def _build_label(product, extra_setup=None):
    """Run __init__ with every heavy side effect patched away."""
    setup = extra_setup or _make_setup()

    label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)

    with patch(PARENT_INIT, lambda self, m, p: setattr(self, "setup", setup)), \
         patch(WRITE_LABEL, return_value=None), \
         patch(SET_IDS,     return_value=None), \
         patch(SET_SCLK,    return_value=None), \
         patch(FORMAT_DESC, return_value='"Fake description."'), \
         patch(INSERT_BIN,  return_value=None), \
         patch(INSERT_TEXT, return_value=None):
        SpiceKernelPDS3Label.__init__(label, MagicMock(), product)

    return label


# ===========================================================================
# SpiceKernelPDS3Label.__init__
# ===========================================================================

class TestSpiceKernelPDS3LabelInit:
    """Tests for SpiceKernelPDS3Label.__init__."""

    def test_template_path_set(self):
        """__init__ points self.template at the kernel label template file."""
        label = _build_label(_make_product("SPK"))
        assert "template_product_spice_kernel.lbl" in label.template

    def test_basic_attributes_set(self):
        product = _make_product("spk")
        label = _build_label(product)
        assert label.FILE_NAME == f'"{product.name}"'
        assert label.INTERCHANGE_FORMAT == product.file_format
        assert label.RECORD_BYTES == product.record_bytes
        assert "Z" not in label.START_TIME
        assert "Z" not in label.STOP_TIME
        assert label.KERNEL_TYPE_ID == "SPK"

    def test_maklabel_defaults_applied(self):
        """Template-level defaults from pds3_mission_template are set on the label."""
        label = _build_label(_make_product("SPK"))
        assert getattr(label, "MISSION_NAME") == '"FAKE MISSION"'

    def test_maklabel_options_override_defaults(self):
        """Per-option values (maklabel_options) override template defaults."""
        label = _build_label(_make_product("SPK"))
        assert getattr(label, "DATA_SET_ID") == '"FAKE-DS-1000-V1.0"'

    @pytest.mark.parametrize("target_i, target_o", [
        ('"MARS"', 'MARS'),
        ('MARS', 'MARS')
    ])
    def test_target_name_quotes_stripped(self, target_i, target_o):
        """Surrounding double-quotes are removed from TARGET_NAME."""
        product = _make_product("SPK")
        product.maklabel_options = []

        setup = _make_setup()
        setup.pds3_mission_template = {
            "TARGET_NAME": target_i,
            "maklabel_options": {},
        }

        label = _build_label(product, extra_setup=setup)
        assert label.TARGET_NAME == target_o

    @pytest.mark.parametrize("product_version_i, product_version_o", [
        ('"ACTUAL"', 'ACTUAL'),
        ('ACTUAL', 'ACTUAL')
    ])
    def test_product_version_type_quotes_stripped(self, product_version_i, product_version_o):
        """Surrounding double-quotes are removed from PRODUCT_VERSION_TYPE."""
        product = _make_product("SPK")
        product.maklabel_options = []

        setup = _make_setup()
        setup.pds3_mission_template = {
            "PRODUCT_VERSION_TYPE": product_version_i,
            "maklabel_options": {},
        }

        label = _build_label(product, extra_setup=setup)
        assert label.PRODUCT_VERSION_TYPE == product_version_o

    @pytest.mark.parametrize("platform_i, platform_o", [
        ('"ODY SPACECRAFT"', 'ODY SPACECRAFT'),
        ('ODY SPACECRAFT', 'ODY SPACECRAFT'),
        ('"N/A"', '"N/A"')  # This one is taken from the default (template).
    ])
    def test_platform_quotes_stripped(self, platform_i, platform_o):
        """Surrounding double-quotes are removed from PLATFORM_OR_MOUNTING_NAME."""
        product = _make_product("SPK")
        product.maklabel_options = []

        setup = _make_setup()
        setup.pds3_mission_template = {
            "PLATFORM_OR_MOUNTING_NAME": platform_i,
            "maklabel_options": {},
        }

        label = _build_label(product, extra_setup=setup)
        assert label.PLATFORM_OR_MOUNTING_NAME == platform_o

    def test_stream_record_type_calls_insert_text(self):
        """STREAM kernels invoke insert_text_label, not insert_binary_label."""
        product = _make_product("SPK")
        product.record_type = "STREAM"

        label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)

        with patch(PARENT_INIT, lambda s, m, p: setattr(s, "setup", _make_setup())), \
             patch(WRITE_LABEL, return_value=None), \
             patch(SET_IDS,     return_value=None), \
             patch(SET_SCLK,    return_value=None), \
             patch(FORMAT_DESC, return_value='"desc"'), \
             patch(INSERT_TEXT) as mock_text, \
             patch(INSERT_BIN)  as mock_bin:
            SpiceKernelPDS3Label.__init__(label, MagicMock(), product)

        mock_text.assert_called_once()
        mock_bin.assert_not_called()

    def test_non_stream_record_type_calls_insert_binary(self):
        """Non-STREAM kernels invoke insert_binary_label."""
        product = _make_product("SPK")
        product.record_type = "FIXED_LENGTH"

        label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)

        with patch(PARENT_INIT, lambda s, m, p: setattr(s, "setup", _make_setup())), \
             patch(WRITE_LABEL, return_value=None), \
             patch(SET_IDS,     return_value=None), \
             patch(SET_SCLK,    return_value=None), \
             patch(FORMAT_DESC, return_value='"desc"'), \
             patch(INSERT_TEXT) as mock_text, \
             patch(INSERT_BIN)  as mock_bin:
            SpiceKernelPDS3Label.__init__(label, MagicMock(), product)

        mock_bin.assert_called_once()
        mock_text.assert_not_called()


# ===========================================================================
# SpiceKernelPDS3Label.set_sclk_times
# ===========================================================================

class TestSpiceKernelPDS3LabelSetSclkTimes:
    """Tests for SpiceKernelPDS3Label.set_sclk_times."""

    def test_non_ck_returns_na(self, bare_label):
        """Non-CK kernels get 'N/A' for both SCLK fields."""
        bare_label.product.type = "SPK"
        bare_label.set_sclk_times(bare_label.product)

        assert bare_label.SPACECRAFT_CLOCK_START_COUNT == '"N/A"'
        assert bare_label.SPACECRAFT_CLOCK_STOP_COUNT  == '"N/A"'

    @pytest.mark.parametrize("system", ['UTC', 'TBD'])
    def test_ck_calls_spice_functions(self, bare_label, system):
        """CK kernels trigger bodn2c, ck_coverage, and scdecd."""
        bare_label.product.type = "CK"

        with patch(f"{MODULE}.spiceypy") as mock_spiceypy, \
             patch(f"{MODULE}.ck_coverage") as mock_coverage:
            mock_spiceypy.bodn2c.return_value = -999
            mock_coverage.return_value = (100.0, 200.0)
            mock_spiceypy.scdecd.side_effect = ["1/100.000", "1/200.000"]

            bare_label.set_sclk_times(bare_label.product, system=system)

        mock_spiceypy.bodn2c.assert_called_once_with("FAKE_SC")
        mock_coverage.assert_called_once_with(bare_label.product.path, timsys="SCLK", system=system)
        assert mock_spiceypy.scdecd.call_count == 2

        # CK SCLK tick values are wrapped in double quotes on the label.
        assert bare_label.SPACECRAFT_CLOCK_START_COUNT == '"1/100.000"'
        assert bare_label.SPACECRAFT_CLOCK_STOP_COUNT  == '"1/200.000"'

# ===========================================================================
# SpiceKernelPDS3Label.set_kernel_ids
# ===========================================================================

class TestSpiceKernelPDS3LabelSetKernelIds:
    """Tests for SpiceKernelPDS3Label.set_kernel_ids."""

    @pytest.mark.parametrize("ids, naif_inst_id", [
        ('-999', '-999'),
        ('-998,-999', '{\n'
                      '                               -998,\n'
                      '                               -999\n'
                      '                               }\n')
    ])
    def test_ck_delegates_to_product(self, bare_label, ids, naif_inst_id):
        """CK kernels source the ID from product.ck_kernel_ids()."""
        bare_label.product.type = "CK"
        bare_label.product.ck_kernel_ids.return_value = ids

        bare_label.set_kernel_ids(bare_label.product)

        bare_label.product.ck_kernel_ids.assert_called_once()
        assert bare_label.NAIF_INSTRUMENT_ID == naif_inst_id

    def test_ik_delegates_to_product(self, bare_label):
        """IK kernels source the ID from product.ik_kernel_ids()."""
        bare_label.product.type = "IK"
        bare_label.product.ik_kernel_ids.return_value = '-236600'

        bare_label.set_kernel_ids(bare_label.product)

        bare_label.product.ik_kernel_ids.assert_called_once()
        assert bare_label.NAIF_INSTRUMENT_ID == '-236600'

    def test_other_type_returns_na(self, bare_label):
        """Non-CK/IK kernels get NAIF_INSTRUMENT_ID = '"N/A"'."""
        bare_label.product.type = "SPK"

        bare_label.set_kernel_ids(bare_label.product)

        assert bare_label.NAIF_INSTRUMENT_ID == '"N/A"'

# ===========================================================================
# SpiceKernelPDS3Label.format_description
# ===========================================================================

class TestSpiceKernelPDS3LabelFormatDescription:
    """Tests for SpiceKernelPDS3Label.format_description (pure string logic)."""

    @pytest.mark.parametrize("description, expected", [
        ('', ' "\n'),   # TODO: THIS IS A BUG.
        ('A short description.',
         '"A short description. "\n'),
        # First line should be at most 46 characters (78 - 32)
        # TODO: This might be also a bug. Does it include the EOL character?
        ('A short description with 43 characters: 12.',
         '"A short description with 43 characters: 12. "\n'),
        ('A longer description that has more than 43 characters '
         'should be split in multiple lines.',
         '"A longer description that has more than 43\n'
         'characters should be split in multiple lines. "\n'),
        ('This description should be split in more than 3 lines, so that '
         'we can test that the maximum line length is not exceeded. Each '
         'line should be, at most, 78 characters long, so that the maximum '
         'line length of 80 characters is not exceeded in any case.',
         '"This description should be split in more\n'
         'than 3 lines, so that we can test that the maximum line length is not\n'
         'exceeded. Each line should be, at most, 78 characters long, so that the\n'
         'maximum line length of 80 characters is not exceeded in any case. "\n'),
        ('This description should be split: 1 2 3 4 5 6xy 7 8 9 0 1 2 3 4 5 6 7 8 9 0 '
         ' 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0'
         ' 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1',
         '"This description should be split: 1 2 3 4 5\n'
         '6xy 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2\n'
         '3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0\n'
         '1 "\n'),
        ('This description should be split: 1 2 3 4 5 6xy 7 8 9 0 1 2 3 4 5 6 7 8 9 0 '
         ' 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0'
         ' 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0.',
         '"This description should be split: 1 2 3 4 5\n'
         '6xy 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2\n'
         '3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0. "\n')
    ])
    def test_starts_with_opening_quote(self, bare_label, description, expected):
        result = bare_label.format_description(description)
        assert result == expected


# ===========================================================================
# SpiceKernelPDS3Label.insert_text_label
# ===========================================================================

LABEL_CONTENT  = "PDS_VERSION_ID = PDS3\nEND\n"
KERNEL_CONTENT = "KPL/SPK\n\\begintext\nsome content\n"


@pytest.fixture()
def text_label(bare_label):
    """bare_label pre-configured for insert_text_label tests."""
    bare_label.name = "/fake/label.lbl"
    bare_label.product.path = "/fake/fake_kernel.bsp"
    return bare_label


def _open_factory(kernel_data=KERNEL_CONTENT, label_data=LABEL_CONTENT, written=None):
    """Return an open() side effect that serves different data per path."""
    def side_effect(path, mode="r", **_kwargs):
        data = label_data if "label" in str(path) else kernel_data
        m = mock_open(read_data=data)()
        if written is not None and mode == "w":
            m.write.side_effect = lambda s: written.append(s)
        return m
    return side_effect


class TestSpiceKernelPDS3LabelInsertTextLabel:
    """Tests for SpiceKernelPDS3Label.insert_text_label."""

    def test_opens_label_for_reading(self, text_label):
        """insert_text_label opens the .lbl file at least once."""
        with patch("builtins.open", side_effect=_open_factory()) as mock_open_:
            text_label.insert_text_label()

        opened = [str(c.args[0]) for c in mock_open_.call_args_list]
        assert any("label" in p for p in opened)

    def test_opens_kernel_file(self, text_label):
        """insert_text_label opens the kernel file at least once."""
        opened_modes = []

        def tracking_open(path, mode="r", **_kwargs):
            opened_modes.append((str(path), mode))
            return mock_open(read_data=KERNEL_CONTENT)()

        with patch("builtins.open", side_effect=tracking_open):
            text_label.insert_text_label()

        kernel_opens = [p for p in opened_modes if "kernel" in p[0] or "bsp" in p[0]]
        assert len(kernel_opens) >= 1

    def test_raises_on_missing_kpl_header(self, text_label):
        """handle_npb_error is called when the kernel lacks a KPL/ first line."""
        bad_kernel = "NOT_KPL\nsome data\n"

        with patch("builtins.open", side_effect=_open_factory(kernel_data=bad_kernel)):
            with pytest.raises(RuntimeError, match='architecture spec as first line.'):
                text_label.insert_text_label()

    @pytest.mark.parametrize("kernel_data, expected, logs", [
        # Kernel does not have a label.
        ('KPL/SPK\n'
         '\\begintext\n'
         'some content\n',
         'KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         ["-- Label inserted to text kernel."]),
        # Kernel does have a label (same label).
        ('KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         'KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         ["-- Updating label in kernel.",
          "-- Label inserted to text kernel."]),
        # Kernel does have a label (another label).
        ('KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = WRONG_PDS_IDENTIFIER\n'
         'SOME_OTHER_KEY = WRONG_VALUE_TO_BE_REMOVED\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         'KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         ["-- Updating label in kernel.",
          "-- Label inserted to text kernel."]),
        # Kernel does not have an EOL character at the end of the file.
        ('KPL/SPK\n'
         '\\begintext\n'
         'some content',
         'KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         ["-- Label inserted to text kernel."]),
        # Kernel does have empty blank lines at the end of the file.
        ('KPL/SPK\n'
         '\\begintext\n'
         'some content\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n',
         'KPL/SPK\n'
         '\n'
         '\\beginlabel\n'
         'PDS_VERSION_ID = PDS3\n'
         '\\endlabel\n'
         '\\begintext\n'
         'some content\n',
         ["-- Label inserted to text kernel."]),
    ])
    def test_lines_written_to_kernel(self, text_label, caplog, kernel_data, expected, logs):
        written = []

        with patch("builtins.open", side_effect=_open_factory(kernel_data=kernel_data,
                                                              written=written)):
            with caplog.at_level(logging.INFO):
                text_label.insert_text_label()

        assert expected == "".join(written)
        assert caplog.messages == logs


# ===========================================================================
# SpiceKernelPDS3Label.insert_binary_label
# ===========================================================================

BIN_LABEL_CONTENT = "PDS_VERSION_ID = PDS3\nKERNEL_TYPE = SPK\nEND\n"


@pytest.fixture()
def binary_label(bare_label):
    """bare_label pre-configured for insert_binary_label tests."""
    bare_label.name = "/fake/label.lbl"
    return bare_label


@pytest.fixture()
def spiceypy_mock():
    """Patch spiceypy inside the module under test."""
    with patch(f"{MODULE}.spiceypy") as mock_spy:
        mock_spy.dafopw.return_value = 1
        yield mock_spy


@pytest.fixture()
def extract_comment_mock():
    """Patch extract_comment to return an empty list by default."""
    with patch(f"{MODULE}.extract_comment", return_value=[]) as mock_ec:
        yield mock_ec


class TestInsertBinaryLabel:
    """Tests for SpiceKernelPDS3Label.insert_binary_label."""

    def test_opens_label_file(self, binary_label, spiceypy_mock, extract_comment_mock):
        """insert_binary_label reads the label file in text mode."""
        with patch("builtins.open", mock_open(read_data=BIN_LABEL_CONTENT)) as m:
            binary_label.insert_binary_label()

        m.assert_called_with("/fake/label.lbl", "r", encoding="utf-8")
        spiceypy_mock.dafopw.assert_called_once_with(binary_label.product.path)

    def test_comment_deleted_before_new_one_added(self, binary_label, spiceypy_mock, extract_comment_mock):
        """dafdc (delete) is called strictly before dafac (add)."""
        call_order = []
        spiceypy_mock.dafdc.side_effect = lambda h:    call_order.append("dafdc")
        spiceypy_mock.dafac.side_effect = lambda h, c: call_order.append("dafac")
        extract_comment_mock.return_value = ["existing line"]

        with patch("builtins.open", mock_open(read_data=BIN_LABEL_CONTENT)):
            binary_label.insert_binary_label()

        assert call_order == ["dafdc", "dafac"]

    def test_dafcls_called_on_completion(self, binary_label, spiceypy_mock, extract_comment_mock):
        """The DAF file handle is always closed after the label is written."""
        spiceypy_mock.dafopw.return_value = 99

        with patch("builtins.open", mock_open(read_data=BIN_LABEL_CONTENT)):
            binary_label.insert_binary_label()

        spiceypy_mock.dafcls.assert_called_once_with(99)

    @pytest.mark.parametrize('label, comments, expected', [
        # No comments in the binary kernel.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = SPK\n'
         'END\n',
         [],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ']),
        # Some comments in the binary kernel.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = SPK\n'
         'END\n',
         ['First line of comments.',
          'Second line of comments.',],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          'First line of comments.',
          'Second line of comments.']),
        # Some comments in the binary kernel, starting with blank lines.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = SPK\n'
         'END\n',
         ['', '', '', '',
          'First line of comments.',
          'Second line of comments.', ],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          'First line of comments.',
          'Second line of comments.']),
        # Some comments in the binary kernel, with empty lines between paragraphs.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = SPK\n'
         'END\n',
         ['First line of comments.',
          '',
          'Second line of comments.', ],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          'First line of comments.',
          ' ',
          'Second line of comments.']),
        # Comment area of the binary kernel has already a label. Same label.
        # TODO: This is a bug. It should not add extra blank lines between the label and the comments.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = SPK\n'
         'END\n',
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          'First line of comments.'],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          ' ',
          ' ',
          'First line of comments.']),
        # Comment area of the binary kernel has already a label. Different label.
        # TODO: Same issue as previous test.
        ('PDS_VERSION_ID = PDS3\n'
         'KERNEL_TYPE = PCK\n'
         'END\n',
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = SPK',
          '\\endlabel',
          ' ',
          ' ',
          'First line of comments.'],
         ['\\beginlabel',
          'PDS_VERSION_ID = PDS3',
          'KERNEL_TYPE = PCK',
          '\\endlabel',
          ' ',
          ' ',
          ' ',
          ' ',
          'First line of comments.']),

    ])
    def test_written_comment(self, binary_label, spiceypy_mock, extract_comment_mock, caplog,
                             label, comments, expected):
        """The comment passed to dafac includes both \\beginlabel and \\endlabel."""
        captured = []
        spiceypy_mock.dafac.side_effect = lambda _, c: captured.extend(c)
        extract_comment_mock.side_effect = lambda _, handle: comments

        with patch("builtins.open", mock_open(read_data=label)):
            with caplog.at_level(logging.INFO):
                binary_label.insert_binary_label()

        assert expected == captured
        assert caplog.messages == ["-- Label inserted to binary kernel."]