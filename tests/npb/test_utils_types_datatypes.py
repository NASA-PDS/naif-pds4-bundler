"""Test family for the pds.naif_pds4_bundler.utils.types.datatypes module.
"""
import pytest

from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs


def test_pipeline_args_initialization_defaults():
    """Test basic initialization with mandatory and optional fields."""
    args = PipelineArgs(config="base.cfg", plan="v1.plan")
    assert args.config == "base.cfg"
    assert args.plan == "v1.plan"

    # Verify defaults
    assert args.kerlist is None
    assert args.faucet == ""
    assert args.log is False
    assert args.silent is False
    assert args.verbose is False
    assert args.debug is True
    assert args.diff is None
    assert args.clear is None
    assert args.checksum is False


def test_faucet_and_diff_normalization():
    """Test that faucet and diff are converted to lowercase."""
    args = PipelineArgs(config="test", faucet="BUNDLE", diff="ALL")
    assert args.faucet == "bundle"
    assert args.diff == "all"


@pytest.mark.parametrize("faucet_val",[
    "clear", "plan", "list", "checks", "staging", "bundle", "labels", None, ""])
def test_faucet_allowed_values(faucet_val):
    """Test all faucet allowed values."""
    args = PipelineArgs(config="test", faucet=faucet_val)
    assert args.faucet == faucet_val


@pytest.mark.parametrize("diff_val", ["all", "log", "files", None, ""])
def test_diff_allowed_values(diff_val):
    """Test all diff allowed values."""
    args = PipelineArgs(config="test", diff=diff_val)
    assert args.diff == diff_val


def test_invalid_faucet_raises_error():
    """Verify ValueError is raised for unsupported faucet values."""
    with pytest.raises(ValueError, match="`faucet` attribute has incorrect value"):
        PipelineArgs(config="test", faucet="not_a_real_option")


def test_invalid_diff_raises_error():
    """Verify ValueError is raised for unsupported diff values."""
    with pytest.raises(ValueError, match="`diff` attribute has incorrect value"):
        PipelineArgs(config="test", diff="everything")


def test_verbose_forces_silent_false():
    """Test logic: if verbose is True, silent must be False."""
    args = PipelineArgs(config="test", verbose=True, silent=True)
    assert args.verbose is True
    assert args.silent is False


@pytest.mark.parametrize("diff_val", ["log", "all"])
def test_diff_forces_logging(diff_val):
    """Test logic: diff='log' or 'all' forces log=True."""
    args = PipelineArgs(config="test", diff=diff_val, log=False)
    assert args.log is True


def test_clear_sets_faucet_if_none():
    """Test logic: faucet is set to 'clear' if clear is provided and faucet is empty."""
    args = PipelineArgs(config="test", clear="some_path", faucet="")
    assert args.faucet == "clear"


def test_frozen_instance_error():
    """Verify the dataclass is actually frozen after init."""
    args = PipelineArgs(config="test")
    with pytest.raises(AttributeError):
        # Note: In some IDEs and lints, the following line will show with an
        #       error indicating that 'PipelineArgs' object attribute 'config'
        #       is read-only. In this case, the error is correct, but we want
        #       the code to be erroneous in order to test the error itself.
        args.config = "new_path"
