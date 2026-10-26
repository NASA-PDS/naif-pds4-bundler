"""Implementation of the NPBError exception class."""


class NPBError(RuntimeError):
    """Unrecoverable error during NPB execution."""


class NPBInternalError(RuntimeError):
    """Unrecoverable error caused by a bug internal to NPB itself.

    Unlike NPBError, which signals a user-fixable problem (bad input,
    misconfiguration), NPBInternalError signals a condition that should
    never occur if NPB is implemented correctly. It is deliberately NOT a
    subclass of NPBError, so `except NPBError` blocks in the pipeline do
    not swallow it into the graceful, user-facing error-handling path.
    """

    def __init__(self, message: str) -> None:
        super().__init__(f"NPB bug: {message}")
