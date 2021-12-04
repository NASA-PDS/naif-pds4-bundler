"""Decorator module that contains decorator functions."""
import traceback

from ..classes.log import error_message


def spice_exception_handler(func):
    """SPICE Exception handler.

    This function is used as a decorator to propagate SpiceyPy errors.
    """

    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            if hasattr(args[0], 'setup'):
                error_message(traceback.format_exc(), setup=args[0].setup)
            else:
                error_message(traceback.format_exc())
    return inner_function
