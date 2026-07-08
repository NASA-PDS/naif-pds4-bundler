"""Tests for NPBError exception class."""
import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError


def test_npberror_is_runtime_error():
    assert issubclass(NPBError, RuntimeError)


def test_npberror_message():
    exc = NPBError("something went wrong")
    assert str(exc) == "something went wrong"


def test_npberror_can_be_raised_and_caught():
    with pytest.raises(NPBError, match="something went wrong"):
        raise NPBError("something went wrong")
