"""Tests for the NPBError and NPBInternalError exception classes.

NPBError signals a problem the user can plausibly fix (bad input or
configuration). NPBInternalError signals a defect in NPB itself and is
deliberately NOT a subclass of NPBError, so pipeline-level `except
NPBError` blocks never catch it and mistakenly route a genuine bug through
the graceful, user-facing error-handling path.
"""
import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError, NPBInternalError


# ---------------------------------------------------------------------------
# NPBError
# ---------------------------------------------------------------------------

class TestNPBError:
    """Unit tests for NPBError: a plain RuntimeError with no message
    transformation.
    """

    def test_is_runtime_error(self) -> None:
        """NPBError subclasses RuntimeError, consistent with NPB's
        exception hierarchy.
        """
        assert issubclass(NPBError, RuntimeError)

    def test_message_unchanged(self) -> None:
        """NPBError passes its message through unchanged: no prefix or
        other transformation is applied.
        """
        assert str(NPBError("something went wrong")) == "something went wrong"

    def test_can_be_raised_and_caught(self) -> None:
        """NPBError can be raised and caught with normal exception
        semantics, with the message intact for pytest.raises to match on.
        """
        with pytest.raises(NPBError, match="something went wrong"):
            raise NPBError("something went wrong")


# ---------------------------------------------------------------------------
# NPBInternalError
# ---------------------------------------------------------------------------

class TestNPBInternalError:
    """Unit tests for NPBInternalError: NPBError's sibling for internal
    invariant violations, which auto-prefixes its message with "NPB bug: ".
    """

    def test_is_runtime_error(self) -> None:
        """NPBInternalError also subclasses RuntimeError, so code that only
        expects a standard exception (e.g. __main__'s catch-all) still handles
        it correctly.
        """
        assert issubclass(NPBInternalError, RuntimeError)

    def test_is_not_npberror_subclass(self) -> None:
        """NPBInternalError must NOT be an NPBError subclass: this is what keeps
        it out of the pipeline's `except NPBError` blocks, so a real NPB bug
        can't be silently absorbed into the same handling as an ordinary
        user/config mistake.
        """
        assert not issubclass(NPBInternalError, NPBError)

    def test_prefixes_message(self) -> None:
        """NPBInternalError automatically prepends "NPB bug: " to whatever
        message is passed in, so the convention is enforced by the type itself
        rather than relying on each call site to type it.
        """
        exc = NPBInternalError("something impossible happened")
        assert str(exc) == "NPB bug: something impossible happened"

    def test_can_be_raised_and_caught(self) -> None:
        """NPBInternalError can be raised and caught with normal exception
        semantics; the prefix applied in __init__ is what pytest.raises matches
        against here, not the raw message passed by the caller.
        """
        with pytest.raises(NPBInternalError,
                           match="NPB bug: something impossible happened"):
            raise NPBInternalError("something impossible happened")
