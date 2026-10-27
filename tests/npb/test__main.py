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


def test_main_cli_error(mocker):
    """Test main returns 2 when argument parsing fails."""
    # Force cli_npb.parse_arguments to raise an Exception. Note that
    # parse_arguments is based on argparse (if an issue is found, it produces
    # SystemExit with a return code 2).
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 side_effect=SystemExit(2))

    result = main()

    assert result == 2


@pytest.mark.parametrize("code, expected", [
    (0, 0),
    (2, 2),
    (1, 1),
    (None, 0),
    ("message", 2),
])
def test_main_system_exit_code_propagated(mocker, code, expected):
    """Test main propagates the SystemExit code.

    argparse exits with 0 for -h/--help and 2 for usage errors. None means
    success, and a non-integer code (e.g. sys.exit("message")) is mapped to 2.
    """
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 side_effect=SystemExit(code))

    assert main() == expected


def test_main_help_returns_0(monkeypatch, capsys):
    """Test that -h prints the help and main returns 0."""
    monkeypatch.setattr(sys, "argv", ["naif-pds4-bundler", "-h"])

    assert main() == 0
    assert "usage:" in capsys.readouterr().out


def test_main_unknown_argument_returns_2(monkeypatch, capsys):
    """Test that an unknown option makes main return 2."""
    monkeypatch.setattr(sys, "argv", ["naif-pds4-bundler", "cfg.xml", "--bogus"])

    assert main() == 2
    assert "unrecognized arguments" in capsys.readouterr().err


def test_main_unexpected_error(mocker, capsys):
    """Test main returns 3 and prints the crash message to stderr only."""
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=object())

    # Force npb.run_pipeline to raise a generic Exception
    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=Exception("Unexpected Crash"))

    result = main()
    captured = capsys.readouterr()

    assert result == 3
    assert "Unexpected Crash" in captured.err
    assert captured.out == ""


def test_main_unexpected_error_prints_even_when_silent(mocker, capsys):
    """Test main prints unexpected-error messages regardless of -s/--silent.

    Unlike NPBError, an unexpected exception signals a bug in the code, not
    an issue with the input arguments or NPB data, so -s/--silent must not
    suppress it.
    """
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=mocker.Mock(silent=True))

    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=Exception("Unexpected Crash"))

    result = main()
    captured = capsys.readouterr()

    assert result == 3
    assert "Unexpected Crash" in captured.err
    assert captured.out == ""


def test_main_npb_error(mocker, capsys):
    """Test main returns 1 when run_pipeline raises a known NPBError.

    Also confirms the NPBError branch itself prints nothing: handle_npb_error
    already logs the message elsewhere via logging.error, not print, so no
    output should reach stderr from main() for this path.
    """
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=object())

    # NPBError is a RuntimeError/Exception subclass, so this also confirms
    # the except NPBError branch is checked before the generic except Exception
    # branch (return 1, not 3).
    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=NPBError("Known configuration issue"))

    result = main()

    assert result == 1
    assert capsys.readouterr().err == ""


def test_main_entry_point():
    """Test that the main entry point returns a system exit code."""
    # Remove the main module from the system modules.
    sys.modules.pop("pds.naif_pds4_bundler.__main__", None)

    with pytest.raises(SystemExit) as exec_info:
        runpy.run_module('pds.naif_pds4_bundler.__main__', run_name='__main__')

    # When we run NPB without any arguments in the command line, we should be
    # getting the standard error from argparse, with an error code 2.
    assert exec_info.value.code == 2
