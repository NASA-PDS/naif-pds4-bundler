"""Decorator module that contains decorator functions."""
import traceback
from functools import wraps

from spiceypy.utils.exceptions import SpiceyPyError

from ..pipeline.runtime import handle_npb_error


def spice_exception_handler(func):
    """SPICE Exception handler.

    This function is used as a decorator to catch and display SpiceyPy errors.

    A wrapper is inserted as a workaround to unmask the docstring of the
    wrapped function. See: https://github.com/sphinx-doc/sphinx/issues/3783
    """

    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SpiceyPyError:
            if hasattr(args[0], "setup"):
                handle_npb_error(traceback.format_exc(), setup=args[0].setup)
            else:
                handle_npb_error(traceback.format_exc())

    return inner_function
