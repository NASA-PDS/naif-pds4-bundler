from unittest.mock import patch


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
@patch("traceback.format_exc", return_value="mock_traceback")
def test_handler_without_setup_attr(_mock_traceback, mock_handler):
    """Test case where args[0] does NOT have a 'setup' attribute."""

    @spice_exception_handler
    def fail_func(x: str) -> None:
        raise ValueError(x)

    fail_func("not_an_object_with_setup")

    # Check if handler was called without the setup keyword
    mock_handler.assert_called_once_with('mock_traceback')


@patch("pds.naif_pds4_bundler.utils.decorators.handle_npb_error")
@patch("traceback.format_exc", return_value="mock_traceback")
def test_handler_with_setup_attr(_mock_traceback, mock_handler):
    """Test case where args[0] DOES have a 'setup' attribute."""

    class MockObject:
        def __init__(self):
            self.setup = "mock_setup_config"

        @spice_exception_handler
        def fail_method(self, x):
            raise ValueError("Boom")

    obj = MockObject()
    obj.fail_method(obj, 123)

    # Check if handler was called WITH the setup keyword
    mock_handler.assert_called_once_with("mock_traceback", setup="mock_setup_config")


def test_successful_execution_with_return_None():
    """Ensure the decorator doesn't interfere with successful calls."""

    @spice_exception_handler
    def success_func(a, b):
        a + b

    assert success_func(1, 2) is None

def test_successful_execution_with_return_not_None():
    """Ensure the decorator doesn't interfere with successful calls."""

    @spice_exception_handler
    def success_func(a, b):
        return a + b

    assert success_func(1, 2) == 3
