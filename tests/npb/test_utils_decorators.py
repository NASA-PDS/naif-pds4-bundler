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

    # Match on the error message text; the full NPBError message is the
    # formatted Python traceback (see the test below), which still contains
    # this text as part of the underlying SpiceyPyError's own message.
    with pytest.raises(NPBError, match="could not be located") as exc_info:
        mock_furnish("missing_kernel.tm")

    # The original SpiceyPyError should still be reachable as the cause.
    assert isinstance(exc_info.value.__cause__, spice_exc.SpiceNOSUCHFILE)


def test_npberror_message_is_the_formatted_traceback():
    """Regression test for the exact message content raised as NPBError.

    Pins the current behavior (NPBError(traceback.format_exc())): the
    message must be the full Python traceback of the caught SpiceyPyError,
    not just str(error), so the NPB call site (file/line) that triggered
    the SPICE failure stays visible in the log. See PR #365 review.
    """

    @spice_exception_handler
    def mock_furnish(_):
        raise spice_exc.SpiceNOSUCHFILE("The file could not be located.")

    with pytest.raises(NPBError) as exc_info:
        mock_furnish("missing_kernel.tm")

    message = str(exc_info.value)
    assert message.startswith("Traceback (most recent call last):")
    assert "SpiceNOSUCHFILE" in message
    assert "The file could not be located." in message


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
