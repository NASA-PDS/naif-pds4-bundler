from unittest.mock import patch

import pytest
import spiceypy.utils.exceptions as spice_exc

from pds.naif_pds4_bundler.utils.decorators import spice_exception_handler


def test_preserves_metadata():
    """Verify @wraps is working to keep docstrings and names."""

    @spice_exception_handler
    def my_test_func():
        """Original docstring."""
        pass

    assert my_test_func.__name__ == "my_test_func"
    assert my_test_func.__doc__ == "Original docstring."


@patch("pds.naif_pds4_bundler.utils.decorators.handle_npb_error")
def test_handler_without_setup_attr(mock_handler):
    """Test case where args[0] does NOT have a 'setup' attribute."""
    # Simulate a specific SpiceyPy 'File Not Found' exception."""

    @spice_exception_handler
    def mock_furnish(_):
        # Manually raise a specific SpiceyPy exception
        raise spice_exc.SpiceNOSUCHFILE("The file could not be located.")

    mock_furnish("missing_kernel.tm")

    # Verify handle_npb_error was triggered by the SpiceyPy error
    assert mock_handler.called_once()

    # The first argument to the handler is the formatted traceback string
    traceback_arg = mock_handler.call_args[0][0]
    assert "SpiceNOSUCHFILE" in traceback_arg


@patch("pds.naif_pds4_bundler.utils.decorators.handle_npb_error")
def test_handler_with_setup_attr(mock_handler):
    """Test case where args[0] DOES have a 'setup' attribute."""

    class MockObject:
        def __init__(self):
            self.setup = "mock_setup_config"

        @spice_exception_handler
        def mock_furnish(self, _):
            # Manually raise a specific SpiceyPy exception
            raise spice_exc.SpiceNOSUCHFILE("The file could not be located.")

    obj = MockObject()
    obj.mock_furnish("missing_kernel.tm")

    # Verify handle_npb_error was triggered by the SpiceyPy error
    assert mock_handler.called_once()

    # The first argument to the handler is the formatted traceback string
    traceback_arg = mock_handler.call_args[0][0]
    assert "SpiceNOSUCHFILE" in traceback_arg


def test_successful_execution_with_return_none():
    """Ensure the decorator doesn't interfere with successful calls."""

    @spice_exception_handler
    def success_func(a, b):
        print(a + b)

    assert success_func(1, 2) is None

def test_successful_execution_with_return_not_none():
    """Ensure the decorator doesn't interfere with successful calls."""

    @spice_exception_handler
    def success_func(a, b):
        return a + b

    assert success_func(1, 2) == 3

def test_function_raises_a_non_spiceypy_error_exception():
    """Ensure the decorator doesn't interfere with non-SpiceyPyError."""

    @spice_exception_handler
    def raise_value_error():
        raise ValueError("Invalid value")

    with pytest.raises(ValueError):
        raise_value_error()
