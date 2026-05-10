"""Unit tests for the parse_arguments() function in cli_npb.py.

All tests patch sys.argv to simulate command-line invocations and verify
that the returned PipelineArgs object carries the expected values.
"""
import pytest
from unittest.mock import patch

from pds.naif_pds4_bundler.cli import cli_npb


# ===========================================================================
# Positional argument: config
# ===========================================================================

class TestConfigArgument:
    def test_single_config_file(self):
        args = parse(["mission.xml"])
        assert args.config == "mission.xml"

    def test_config_is_first_element_when_nargs_plus(self):
        # nargs="+" accepts multiple tokens, but parse_arguments() collapses
        # them to args.config[0] — only the first value should survive.
        args = parse(["mission.xml", "extra.xml"])
        assert args.config == "mission.xml"

    def test_missing_config_exits(self):
        with pytest.raises(SystemExit):
            parse([])


# ===========================================================================
# -p / --plan
# ===========================================================================

class TestPlanArgument:
    def test_plan_short_form(self):
        args = parse(["cfg.xml", "-p", "release.plan"])
        assert args.plan == "release.plan"

    def test_plan_long_form(self):
        args = parse(["cfg.xml", "--plan", "release.plan"])
        assert args.plan == "release.plan"

    def test_plan_defaults_to_none(self):
        args = parse(["cfg.xml"])
        assert args.plan is None


# ===========================================================================
# -f / --faucet
# ===========================================================================

class TestFaucetArgument:
    @pytest.mark.parametrize("value", [
        "clear", "plan", "list", "checks", "staging", "bundle", "labels"
    ])
    def test_valid_faucet_values(self, value):
        args = parse(["cfg.xml", "-f", value])
        assert args.faucet == value

    def test_faucet_long_form(self):
        args = parse(["cfg.xml", "--faucet", "bundle"])
        assert args.faucet == "bundle"

    def test_faucet_defaults_to_empty_string(self):
        args = parse(["cfg.xml"])
        assert args.faucet == ""


# ===========================================================================
# -l / --log
# ===========================================================================

class TestLogArgument:
    def test_log_flag_enabled(self):
        args = parse(["cfg.xml", "-l"])
        assert args.log is True

    def test_log_long_form(self):
        args = parse(["cfg.xml", "--log"])
        assert args.log is True

    def test_log_defaults_to_false(self):
        args = parse(["cfg.xml"])
        assert args.log is False


# ===========================================================================
# -s / --silent
# ===========================================================================

class TestSilentArgument:
    def test_silent_flag_enabled(self):
        args = parse(["cfg.xml", "-s"])
        assert args.silent is True

    def test_silent_long_form(self):
        args = parse(["cfg.xml", "--silent"])
        assert args.silent is True

    def test_silent_defaults_to_false(self):
        args = parse(["cfg.xml"])
        assert args.silent is False


# ===========================================================================
# -v / --verbose
# ===========================================================================

class TestVerboseArgument:
    def test_verbose_flag_enabled(self):
        args = parse(["cfg.xml", "-v"])
        assert args.verbose is True

    def test_verbose_long_form(self):
        args = parse(["cfg.xml", "--verbose"])
        assert args.verbose is True

    def test_verbose_defaults_to_false(self):
        args = parse(["cfg.xml"])
        assert args.verbose is False

    def test_verbose_overrides_silent(self):
        # PipelineArgs.__post_init__ forces silent=False when verbose=True.
        args = parse(["cfg.xml", "-v", "-s"])
        assert args.verbose is True
        assert args.silent is False


# ===========================================================================
# -d / --diff
# ===========================================================================

class TestDiffArgument:
    @pytest.mark.parametrize("value", ["files", "log", "all"])
    def test_valid_diff_values(self, value):
        args = parse(["cfg.xml", "-d", value])
        assert args.diff == value

    def test_diff_long_form(self):
        args = parse(["cfg.xml", "--diff", "all"])
        assert args.diff == "all"

    def test_diff_defaults_to_empty_string(self):
        args = parse(["cfg.xml"])
        assert args.diff == ""


# ===========================================================================
# -c / --clear
# ===========================================================================

class TestClearArgument:
    def test_clear_short_form(self):
        args = parse(["cfg.xml", "-c", "run.file_list"])
        assert args.clear == "run.file_list"

    def test_clear_long_form(self):
        args = parse(["cfg.xml", "--clear", "run.file_list"])
        assert args.clear == "run.file_list"

    def test_clear_defaults_to_empty_string(self):
        args = parse(["cfg.xml"])
        assert args.clear == ""

    def test_clear_without_faucet_sets_faucet_to_clear(self):
        # PipelineArgs.__post_init__: clear + empty faucet → faucet="clear".
        args = parse(["cfg.xml", "-c", "run.file_list"])
        assert args.faucet == "clear"

    def test_clear_with_explicit_faucet_preserves_faucet(self):
        args = parse(["cfg.xml", "-c", "run.file_list", "-f", "staging"])
        assert args.faucet == "staging"


# ===========================================================================
# -k / --kerlist
# ===========================================================================

class TestKerlistArgument:
    def test_kerlist_short_form(self):
        args = parse(["cfg.xml", "-k", "kernels.list"])
        assert args.kerlist == "kernels.list"

    def test_kerlist_long_form(self):
        args = parse(["cfg.xml", "--kerlist", "kernels.list"])
        assert args.kerlist == "kernels.list"

    def test_kerlist_defaults_to_none(self):
        args = parse(["cfg.xml"])
        assert args.kerlist is None


# ===========================================================================
# -m / --checksum
# ===========================================================================

class TestChecksumArgument:
    def test_checksum_short_form(self):
        args = parse(["cfg.xml", "-m"])
        assert args.checksum is True

    def test_checksum_long_form(self):
        args = parse(["cfg.xml", "--checksum"])
        assert args.checksum is True

    def test_checksum_defaults_to_false(self):
        args = parse(["cfg.xml"])
        assert args.checksum is False


# ===========================================================================
# debug is always False when invoked from CLI
# ===========================================================================

class TestDebugAlwaysFalse:
    def test_debug_is_false(self):
        args = parse(["cfg.xml"])
        assert args.debug is False

    def test_debug_false_regardless_of_other_flags(self):
        args = parse(["cfg.xml", "-v", "-l", "-m"])
        assert args.debug is False


# ===========================================================================
# Return type
# ===========================================================================

class TestReturnType:
    def test_returns_pipeline_args_instance(self):
        from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs
        args = parse(["cfg.xml"])
        assert isinstance(args, PipelineArgs)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def parse(argv: list[str]):
    """Invoke parse_arguments() with a controlled sys.argv."""
    with patch("sys.argv", ["npb"] + argv):
        return cli_npb.parse_arguments()