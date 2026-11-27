"""Unit tests for the staging functions in utils/staging.py."""
import logging
import os
from pathlib import Path

import pytest

from pds.naif_pds4_bundler.utils.staging import stage_file


def messages(caplog: pytest.LogCaptureFixture) -> list[tuple[int, str]]:
    """Return the level and message of every log record."""
    return [(record.levelno, record.getMessage()) for record in caplog.records]


@pytest.fixture
def source(tmp_path: Path) -> Path:
    """A file to stage, with an old modification time."""
    path = tmp_path / "a.orb"
    path.write_text("new content")
    os.utime(path, (1_000_000_000, 1_000_000_000))
    return path


@pytest.mark.parametrize("name, staged_name", [
    pytest.param(None, "a.orb", id="source-name"),
    pytest.param("b.orb", "b.orb", id="given-name"),
])
def test_stage_file_copies(tmp_path: Path, caplog: pytest.LogCaptureFixture,
                           source: Path, name: str | None,
                           staged_name: str) -> None:
    """A file that is not staged yet is copied, keeping its content and
    modification time, under the given name or else the name of the source.
    """
    # An empty staging directory that already exists.
    destination = tmp_path / "staging"
    destination.mkdir()
    caplog.set_level(logging.INFO)

    # Stage the file.
    result = stage_file(str(source), str(destination), name)

    # The copy is reported, matches the source and is the only thing logged.
    staged = destination / staged_name
    assert result == (str(staged), True)
    assert staged.read_text() == "new content"
    assert staged.stat().st_mtime == 1_000_000_000
    assert messages(caplog) == [
        (logging.INFO, f"-- Copy {staged_name} to staging directory."),
    ]


def test_stage_file_creates_the_directory(
        tmp_path: Path, caplog: pytest.LogCaptureFixture, source: Path) -> None:
    """A missing staging directory is created, and that is logged before the
    copy, with the directory written as it was given.
    """
    # A directory that does not exist yet, with a trailing separator.
    destination = str(tmp_path / "staging") + os.sep
    caplog.set_level(logging.INFO)

    # Stage the file into it.
    result = stage_file(str(source), destination)

    # The file is in the new directory, and the log keeps the expected order.
    assert result == (destination + "a.orb", True)
    assert os.path.isfile(destination + "a.orb")
    assert messages(caplog) == [
        (logging.INFO, f"-- Generated directory: {destination}  "),
        (logging.INFO, ""),
        (logging.INFO, "-- Copy a.orb to staging directory."),
    ]


@pytest.mark.parametrize("source_name", [
    pytest.param("a.orb", id="source-present"),
    pytest.param("gone.orb", id="source-missing"),
])
def test_stage_file_already_staged(
        tmp_path: Path, caplog: pytest.LogCaptureFixture, source: Path,
        source_name: str) -> None:
    """A file that is already staged is left as it is and reported as not
    copied, with a warning, whether or not the source still exists.
    """
    # Put an older version of the file in the staging directory.
    staged = tmp_path / "staging" / "a.orb"
    staged.parent.mkdir()
    staged.write_text("old content")
    caplog.set_level(logging.INFO)

    # Stage a file under the same name.
    result = stage_file(str(tmp_path / source_name), str(staged.parent),
                        "a.orb")

    # Nothing was overwritten, and the warning follows the copy message.
    assert result == (str(staged), False)
    assert staged.read_text() == "old content"
    assert messages(caplog) == [
        (logging.INFO, "-- Copy a.orb to staging directory."),
        (logging.WARNING, "     a.orb already present in staging directory."),
    ]


@pytest.mark.parametrize("ending", [
    pytest.param("", id="without-separator"),
    pytest.param(os.sep, id="with-separator"),
])
def test_stage_file_joins_with_one_separator(
        tmp_path: Path, source: Path, ending: str) -> None:
    """The returned path has a single separator between the directory and the
    name, whether or not the directory ends with one.
    """
    # The same directory, written with or without the final separator.
    destination = str(tmp_path / "staging")

    # Stage the file and keep only the path.
    staged_path, _ = stage_file(str(source), destination + ending)

    # Compare the text of the path, since a doubled separator would still open.
    assert staged_path == destination + os.sep + "a.orb"


def test_stage_file_missing_source(
        tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Staging a source that does not exist raises the error of the copy, after
    the copy has been announced in the log.
    """
    # An existing staging directory and a source that was never written.
    source = str(tmp_path / "missing.orb")
    destination = tmp_path / "staging"
    destination.mkdir()
    caplog.set_level(logging.INFO)

    # Try to stage it.
    with pytest.raises(FileNotFoundError) as error:
        stage_file(source, str(destination))

    # The error names the source, and the announcement is the only message.
    assert error.value.filename == source
    assert messages(caplog) == [
        (logging.INFO, "-- Copy missing.orb to staging directory."),
    ]
