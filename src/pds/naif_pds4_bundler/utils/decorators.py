"""Decorator module that contains decorator functions."""
import traceback
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
            # NPB error. The message is the formatted Python traceback (not
            # str(error)), so the NPB call site (file/line) that triggered the
            # SPICE failure stays visible in the log, as it did before this
            # decorator raised NPBError directly; `from error` additionally
            # keeps the original exception chained.
            raise NPBError(traceback.format_exc()) from error

    return inner_function
