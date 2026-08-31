"""Decorator module that contains decorator functions."""
from functools import wraps

from spiceypy.utils.exceptions import SpiceyPyError

from ..classes.exceptions import NPBError


def spice_exception_handler(func):
    """SPICE Exception handler.

    This function is used as a decorator to catch SpiceyPy errors and
    re-raise them as NPBError, in line with every other error path in NPB.

    A wrapper is inserted as a workaround to unmask the docstring of the
    wrapped function. See: https://github.com/sphinx-doc/sphinx/issues/3783
    """

    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except SpiceyPyError as error:
            # Re-raise as NPBError so SPICE failures are handled like any other
            # NPB error; `from error` keeps the original traceback.
            raise NPBError(str(error)) from error

    return inner_function
