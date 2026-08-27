"""Test family for the pds.naif_pds4_bundler.__main__ module
"""
import runpy
import sys

import pytest

from pds.naif_pds4_bundler.__main__ import main
from pds.naif_pds4_bundler.classes.exceptions import NPBError


def test_main_success(mocker):
    """Test main returns 0 when the pipeline runs successfully."""
    # Mock cli_npb.parse_arguments to return dummy args
    mock_args = object()
    mock_parse = mocker.patch(
        'pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
        return_value=mock_args)

    # Mock npb.run_pipeline to do nothing
    mock_run = mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline')

    result = main()

    assert result == 0
    mock_parse.assert_called_once_with()
    mock_run.assert_called_once_with(mock_args)
    assert mock_run.call_args.args[0] is mock_args


def test_main_cli_error(mocker):
    """Test main returns 2 when argument parsing fails."""
    # Force cli_npb.parse_arguments to raise an Exception. Note that
    # parse_arguments is based on argparse (if an issue is found, it produces
    # SystemExit with a return code 2).
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 side_effect=SystemExit(2))

    result = main()

    assert result == 2


def test_main_unexpected_error(mocker, capsys):
    """Test main returns 3 and prints the crash message when not silent."""
    # A Mock with .silent set is required (not a bare object()): the except
    # Exception branch in main() now reads args.silent to decide whether
    # to print.
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=mocker.Mock(silent=False))

    # Force npb.run_pipeline to raise a generic Exception
    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=Exception("Unexpected Crash"))

    result = main()

    assert result == 3
    assert "Unexpected Crash" in capsys.readouterr().err


def test_main_unexpected_error_silent(mocker, capsys):
    """Test main returns 3 and prints nothing to stderr when silent."""
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=mocker.Mock(silent=True))

    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=Exception("Unexpected Crash"))

    result = main()

    assert result == 3
    # -s/--silent must still suppress the console print; logging.error still
    # fires internally, but that's not observable via stderr here.
    assert capsys.readouterr().err == ""


def test_main_npb_error(mocker):
    """Test main returns 1 when run_pipeline raises a known NPBError."""
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=mocker.Mock(silent=False))

    # NPBError is a RuntimeError/Exception subclass, so this also confirms
    # the except NPBError branch is checked before the generic except Exception
    # branch (return 1, not 3).
    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=NPBError("Known configuration issue"))

    result = main()

    assert result == 1


def test_main_cli_value_error(mocker, capsys):
    """Test main returns 3 when parse_arguments raises before args is bound.

    This covers PipelineArgs.__post_init__ raising ValueError for invalid CLI
    arguments: the failure happens inside the expression that assigns `args`,
    so `args` is never bound. The except Exception branch must not crash with
    UnboundLocalError/AttributeError when it checks args.silent.
    """
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 side_effect=ValueError("Invalid CLI argument"))

    result = main()

    assert result == 3

    # args stays None (getattr default), so the message must still print.
    assert "Invalid CLI argument" in capsys.readouterr().err


def test_main_entry_point():
    """Test that the main entry point returns a system exit code."""
    # Remove the main module from the system modules.
    sys.modules.pop("pds.naif_pds4_bundler.__main__", None)

    with pytest.raises(SystemExit) as exec_info:
        runpy.run_module('pds.naif_pds4_bundler.__main__', run_name='__main__')

    # When we run NPB without any arguments in the command line, we should be
    # getting the standard error from argparse, with an error code 2.
    assert exec_info.value.code == 2
