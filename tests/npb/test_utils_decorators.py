import pytest
import spiceypy.utils.exceptions as spice_exc

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.utils.decorators import spice_exception_handler


def test_preserves_metadata():
    """Verify @wraps is working to keep docstrings and names."""

    @spice_exception_handler
    def my_test_func():
        """Original docstring."""
        pass

    assert my_test_func.__name__ == "my_test_func"
    assert my_test_func.__doc__ == "Original docstring."


def test_spiceypy_error_is_raised_as_npberror():
    """A SpiceyPyError from the wrapped function escapes as NPBError."""

    @spice_exception_handler
    def mock_furnish(_):
        # Manually raise a specific SpiceyPy exception
        raise spice_exc.SpiceNOSUCHFILE("The file could not be located.")

    # Match on the error message, since converting to NPBError keeps the
    # message text but drops the SpiceNOSUCHFILE class name.
    with pytest.raises(NPBError, match="could not be located") as exc_info:
        mock_furnish("missing_kernel.tm")

    # The original SpiceyPyError should still be reachable as the cause.
    assert isinstance(exc_info.value.__cause__, spice_exc.SpiceNOSUCHFILE)


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
