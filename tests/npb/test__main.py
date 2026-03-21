"""Test family for the pds.naif_pds4_bundler.__main__ module
"""
import runpy
import sys

import pytest

from pds.naif_pds4_bundler.__main__ import main


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


def test_main_unexpected_error(mocker):
    """Test main returns 2 when an unexpected Exception occurs in the pipeline."""
    mocker.patch('pds.naif_pds4_bundler.__main__.cli_npb.parse_arguments',
                 return_value=object())

    # Force npb.run_pipeline to raise a generic Exception
    mocker.patch('pds.naif_pds4_bundler.__main__.npb.run_pipeline',
                 side_effect=Exception("Unexpected Crash"))

    result = main()

    assert result == 3


def test_main_entry_point():
    """Test that the main entry point returns a system exit code."""
    # Remove the main module from the system modules.
    sys.modules.pop("pds.naif_pds4_bundler.__main__", None)

    with pytest.raises(SystemExit) as exec_info:
        runpy.run_module('pds.naif_pds4_bundler.__main__', run_name='__main__')

    # When we run NPB without any arguments in the command line, we should be
    # getting the standard error from argparse, with an error code 2.
    assert exec_info.value.code == 2