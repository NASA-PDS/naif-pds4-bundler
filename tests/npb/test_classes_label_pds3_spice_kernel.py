"""Unit tests for SpiceKernelPDS3Label
"""
import logging
from unittest.mock import MagicMock, patch

import pytest
from spiceypy.utils.exceptions import SpiceyPyError

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.classes.label.pds3_spice_kernel import SpiceKernelPDS3Label

# ---------------------------------------------------------------------------
# Patch target strings (adjust if the real package path differs)
# ---------------------------------------------------------------------------
MODULE      = "pds.naif_pds4_bundler.classes.label.pds3_spice_kernel"
PARENT_INIT = f"{MODULE}.PDS3Label.__init__"
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
    label._label_fields = {}
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

    with patch(PARENT_INIT, lambda self, p: (
            setattr(self, "setup", setup),
            setattr(self, "_label_fields", {}))), \
         patch(SET_IDS,     return_value=None), \
         patch(SET_SCLK,    return_value=None), \
         patch(FORMAT_DESC, return_value='"Fake description."'):
        SpiceKernelPDS3Label.__init__(label, product)

    return label


# ===========================================================================
# SpiceKernelPDS3Label.__init__
# ===========================================================================

class TestSpiceKernelPDS3LabelInit:
    """Tests for SpiceKernelPDS3Label.__init__."""

    def test_trailing_blank_log_attribute_is_false(self):
        """Guards against a silent regression if this class is renamed
        without carrying the attribute over."""
        assert SpiceKernelPDS3Label._trailing_blank_log is False

    def test_context_from_product_attribute_is_false(self):
        """Pins _context_from_product to PDSLabel's inherited default: this
        class does not override it, so it must stay False."""
        assert SpiceKernelPDS3Label._context_from_product is False

    def test_template_path_set(self):
        """__init__ points self._template at the kernel label template file."""
        label = _build_label(_make_product("SPK"))
        assert "template_product_spice_kernel.lbl" in label._template

    def test_basic_attributes_set(self):
        product = _make_product("spk")
        label = _build_label(product)
        assert label._label_fields["FILE_NAME"] == f'"{product.name}"'
        assert label._label_fields["INTERCHANGE_FORMAT"] == product.file_format
        assert label._label_fields["RECORD_BYTES"] == product.record_bytes
        assert "Z" not in label._label_fields["START_TIME"]
        assert "Z" not in label._label_fields["STOP_TIME"]
        assert label._label_fields["KERNEL_TYPE_ID"] == "SPK"

    def test_maklabel_defaults_applied(self):
        """Template-level defaults from pds3_mission_template are set on the label."""
        label = _build_label(_make_product("SPK"))
        assert label._label_fields["MISSION_NAME"] == '"FAKE MISSION"'

    def test_maklabel_options_override_defaults(self):
        """Per-option values (maklabel_options) override template defaults."""
        label = _build_label(_make_product("SPK"))
        assert label._label_fields["DATA_SET_ID"] == '"FAKE-DS-1000-V1.0"'

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
        assert label._label_fields["TARGET_NAME"] == target_o

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
        assert label._label_fields["PRODUCT_VERSION_TYPE"] == product_version_o

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
        assert label._label_fields["PLATFORM_OR_MOUNTING_NAME"] == platform_o

    @pytest.mark.parametrize("field", [
        "TARGET_NAME",
        "PRODUCT_VERSION_TYPE",
        "PLATFORM_OR_MOUNTING_NAME",
    ])
    def test_quote_stripping_skips_absent_field(self, field):
        """A field missing from the label is left absent (no KeyError)."""
        label = _build_label(_make_product("SPK"))

        assert field not in label._label_fields

    def test_init_does_not_write_label(self):
        """Writing and inserting the label is the pipeline's job now."""
        label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)

        with patch(PARENT_INIT, lambda s, p: (
                setattr(s, "setup", _make_setup()),
                setattr(s, "_label_fields", {}))), \
             patch(SET_IDS,     return_value=None), \
             patch(SET_SCLK,    return_value=None), \
             patch(FORMAT_DESC, return_value='"desc"'), \
             patch.object(SpiceKernelPDS3Label, "write_label") as mock_write:
            SpiceKernelPDS3Label.__init__(label, _make_product("SPK"))

        mock_write.assert_not_called()


# ===========================================================================
# SpiceKernelPDS3Label.write_label -- _trailing_blank_log effect
# ===========================================================================
# These tests call write_label() directly to isolate the one blank-line call
# that _trailing_blank_log gates.

class TestSpiceKernelPDS3LabelWriteLabel:
    """Proves _trailing_blank_log=False actually suppresses write_label()'s
    trailing blank log line for the real SpiceKernelPDS3Label class."""

    @pytest.fixture
    def label(self, tmp_path):
        """Real SpiceKernelPDS3Label instance, __init__ bypassed, ready for
        a direct write_label() call."""
        templates_dir = tmp_path / "templates"
        staging_dir = tmp_path / "staging"
        templates_dir.mkdir()
        staging_dir.mkdir()

        # A minimal real template so write_label() has an actual file to
        # read and substitute into -- only $FILE_NAME needs to resolve.
        template_path = templates_dir / "template_product_spice_kernel.lbl"
        template_path.write_text("Line with $FILE_NAME\n", encoding="utf-8")

        setup = MagicMock()
        setup.eol_pds3 = "\r\n"

        # MagicMock attrs are truthy by default -- must be False or
        # self.compare() runs.
        setup.diff = False

        # Must be True or write_label()'s print(...) branch also runs.
        setup.args.silent = True
        setup.args.verbose = False
        setup.staging_directory = str(staging_dir)
        setup.add_file = MagicMock()

        product = MagicMock()
        product.path = str(staging_dir / "kernel.bsp")
        product.extension = "bsp"

        # __init__ is bypassed: the label fields are set by hand.
        label = SpiceKernelPDS3Label.__new__(SpiceKernelPDS3Label)
        label._label_fields = {"FILE_NAME": "kernel.bsp"}
        label.setup = setup
        label.product = product
        label.name = str(staging_dir / "kernel.lbl")
        label._template = str(template_path)

        return label

    def test_write_label_suppresses_trailing_blank_log(self, label, caplog):
        """write_label() must not log a trailing blank line for this class,
        since SpiceKernelPDS3Label overrides _trailing_blank_log to False."""
        with caplog.at_level(logging.INFO):
            label.write_label()

        # The gated call is logging.info(""); caplog records it as "".
        assert caplog.messages.count("") == 0


# ===========================================================================
# SpiceKernelPDS3Label.set_sclk_times
# ===========================================================================

class TestSpiceKernelPDS3LabelSetSclkTimes:
    """Tests for SpiceKernelPDS3Label.set_sclk_times."""

    def test_non_ck_returns_na(self, bare_label):
        """Non-CK kernels get 'N/A' for both SCLK fields."""
        bare_label.product.type = "SPK"
        bare_label.set_sclk_times(bare_label.product)

        assert bare_label._label_fields["SPACECRAFT_CLOCK_START_COUNT"] == '"N/A"'
        assert bare_label._label_fields["SPACECRAFT_CLOCK_STOP_COUNT"]  == '"N/A"'

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
        assert bare_label._label_fields["SPACECRAFT_CLOCK_START_COUNT"] == '"1/100.000"'
        assert bare_label._label_fields["SPACECRAFT_CLOCK_STOP_COUNT"]  == '"1/200.000"'

    def test_ck_spiceypy_failure_raises_npberror(self, bare_label):
        """A SpiceyPyError from bodn2c is raised as NPBError."""
        # set_sclk_times only calls bodn2c, ck_coverage, and scdecd for CK
        # kernels; other types return "N/A" without touching SPICE at all.
        bare_label.product.type = "CK"

        with patch(f"{MODULE}.spiceypy") as mock_spiceypy:
            # bodn2c is the first SPICE call set_sclk_times makes for a CK
            # kernel, so failing it is enough to exercise the error path.
            mock_spiceypy.bodn2c.side_effect = SpiceyPyError('spiceypy error')

            with pytest.raises(NPBError):
                bare_label.set_sclk_times(bare_label.product)

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
        assert bare_label._label_fields["NAIF_INSTRUMENT_ID"] == naif_inst_id

    def test_ik_delegates_to_product(self, bare_label):
        """IK kernels source the ID from product.ik_kernel_ids()."""
        bare_label.product.type = "IK"
        bare_label.product.ik_kernel_ids.return_value = '-236600'

        bare_label.set_kernel_ids(bare_label.product)

        bare_label.product.ik_kernel_ids.assert_called_once()
        assert bare_label._label_fields["NAIF_INSTRUMENT_ID"] == '-236600'

    def test_other_type_returns_na(self, bare_label):
        """Non-CK/IK kernels get NAIF_INSTRUMENT_ID = '"N/A"'."""
        bare_label.product.type = "SPK"

        bare_label.set_kernel_ids(bare_label.product)

        assert bare_label._label_fields["NAIF_INSTRUMENT_ID"] == '"N/A"'

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
