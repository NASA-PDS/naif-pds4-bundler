"""Decorator module that contains decorator functions."""
import traceback
from functools import wraps

from ..classes.log import error_message


def spice_exception_handler(func):
    """SPICE Exception handler.

    This function is used as a decorator to catch and display SpiceyPy errors.

    A wrapper is inserted as a workaround to unmask the docstring of the
    wrapped function. See: https://github.com/sphinx-doc/sphinx/issues/3783
    """

    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            if hasattr(args[0], "setup"):
                error_message(traceback.format_exc(), setup=args[0].setup)
            else:
                error_message(traceback.format_exc())

    return inner_function
