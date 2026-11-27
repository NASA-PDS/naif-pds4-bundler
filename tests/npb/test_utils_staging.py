"""Unit tests for the staging functions in utils/staging.py."""
import logging
import os
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import pytest

from pds.naif_pds4_bundler.classes.exceptions import NPBError
from pds.naif_pds4_bundler.utils.staging import stage_file, stage_kernel


def messages(caplog: pytest.LogCaptureFixture) -> list[tuple[int, str]]:
    """Return the level and message of every log record."""
    return [(record.levelno, record.getMessage()) for record in caplog.records]


def make_kernels(root: Path, files: list[str]) -> list[str]:
    """Create two kernel directories holding the given files, each one with its
    own relative path as content, and return the directories.
    """
    directories = [root / "first", root / "second"]
    for directory in directories:
        directory.mkdir()

    for file in files:
        path = root / file
        path.parent.mkdir(exist_ok=True)
        path.write_text(file)

    return [str(directory) for directory in directories]


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


@pytest.mark.parametrize("files, expected", [
    pytest.param(["first/a.bsp"], "first/a.bsp", id="first-directory"),
    pytest.param(["first/spk/a.bsp"], "first/spk/a.bsp", id="subdirectory"),
    pytest.param(["second/a.bsp"], "second/a.bsp", id="second-directory"),
    pytest.param(["second/a.bsp", "first/a.bsp"], "first/a.bsp",
                 id="first-directory-wins"),
    pytest.param(["first/m.bsp", "second/a.bsp"], "second/a.bsp",
                 id="name-before-mapping"),
])
def test_stage_kernel_by_name(
        tmp_path: Path, caplog: pytest.LogCaptureFixture, files: list[str],
        expected: str) -> None:
    """A kernel found by its name is copied from the first directory that has
    it, and its mapping is never looked up.
    """
    # Two kernel directories, a staging directory and a lookup to watch.
    directories = make_kernels(tmp_path, files)
    destination = tmp_path / "staging"
    destination.mkdir()
    lookup = Mock(return_value="m.bsp")
    caplog.set_level(logging.INFO)

    # Stage the kernel.
    result = stage_kernel("a.bsp", directories, str(destination), lookup)

    # The content tells which of the files was copied.
    staged = destination / "a.bsp"
    assert result == (str(staged), True)
    assert staged.read_text() == expected
    lookup.assert_not_called()
    assert messages(caplog) == [
        (logging.INFO, "-- Copy a.bsp to staging directory."),
    ]


@pytest.mark.parametrize("files, expected", [
    pytest.param(["first/m.bsp"], "first/m.bsp", id="first-directory"),
    pytest.param(["first/x.bsp", "first/y.bsp", "second/spk/m.bsp"],
                 "second/spk/m.bsp", id="after-other-files"),
    pytest.param(["second/m.bsp", "first/m.bsp"], "first/m.bsp",
                 id="first-directory-wins"),
])
def test_stage_kernel_by_mapping(
        tmp_path: Path, caplog: pytest.LogCaptureFixture, files: list[str],
        expected: str) -> None:
    """A kernel found only through its mapping is staged under the kernel name.
    The lookup runs once, and the mapping is logged after the copy message.
    """
    # No file is called 'a.bsp', and the staging directory does not exist.
    directories = make_kernels(tmp_path, files)
    destination = str(tmp_path / "staging")
    lookup = Mock(return_value="m.bsp")
    caplog.set_level(logging.INFO)

    # Stage the kernel.
    result = stage_kernel("a.bsp", directories, destination, lookup)

    # The mapped file was copied, and the whole log keeps its order.
    staged = Path(destination, "a.bsp")
    assert result == (str(staged), True)
    assert staged.read_text() == expected
    lookup.assert_called_once_with("a.bsp")
    assert messages(caplog) == [
        (logging.INFO, f"-- Generated directory: {destination}  "),
        (logging.INFO, ""),
        (logging.INFO, "-- Copy a.bsp to staging directory."),
        (logging.INFO, "-- Mapping m.bsp with a.bsp"),
    ]


@pytest.mark.parametrize("files", [
    pytest.param(["first/a.bsp"], id="source-present"),
    pytest.param([], id="source-missing"),
])
def test_stage_kernel_already_staged(
        tmp_path: Path, caplog: pytest.LogCaptureFixture,
        files: list[str]) -> None:
    """A kernel that is already staged is neither searched for nor looked up,
    so it does not matter whether its source still exists.
    """
    # An older version of the kernel is in the staging directory.
    directories = make_kernels(tmp_path, files)
    staged = tmp_path / "staging" / "a.bsp"
    staged.parent.mkdir()
    staged.write_text("old content")
    lookup = Mock(return_value="m.bsp")
    caplog.set_level(logging.INFO)

    # Stage the kernel.
    result = stage_kernel("a.bsp", directories, str(staged.parent), lookup)

    # The staged file is untouched and only the warning is added.
    assert result == (str(staged), False)
    assert staged.read_text() == "old content"
    lookup.assert_not_called()
    assert messages(caplog) == [
        (logging.INFO, "-- Copy a.bsp to staging directory."),
        (logging.WARNING, "     a.bsp already present in staging directory."),
    ]


@pytest.mark.parametrize("error", [
    pytest.param(NPBError("a.bsp does not have mapping."), id="no-mapping"),
    pytest.param(FileNotFoundError("kernel list"), id="no-kernel-list"),
])
def test_stage_kernel_lookup_error(
        tmp_path: Path, caplog: pytest.LogCaptureFixture,
        error: Exception) -> None:
    """An error raised by the mapping lookup reaches the caller unchanged, and
    nothing is staged.
    """
    # A file that is not the kernel, so that the lookup is needed.
    directories = make_kernels(tmp_path, ["first/x.bsp"])
    destination = tmp_path / "staging"
    destination.mkdir()
    caplog.set_level(logging.INFO)

    # Try to stage the kernel with a failing lookup.
    with pytest.raises(type(error)) as raised:
        stage_kernel("a.bsp", directories, str(destination),
                     Mock(side_effect=error))

    # It is the very same error object.
    assert raised.value is error
    assert list(destination.iterdir()) == []
    assert messages(caplog) == [
        (logging.INFO, "-- Copy a.bsp to staging directory."),
    ]


@pytest.mark.parametrize("lookup", [
    pytest.param(None, id="without-lookup"),
    pytest.param(lambda name: "m.bsp", id="mapping-not-found"),
])
def test_stage_kernel_not_found(
        tmp_path: Path, caplog: pytest.LogCaptureFixture,
        lookup: Callable[[str], str] | None) -> None:
    """A kernel found neither by name nor by mapping raises an error naming the
    last directory searched.
    """
    # Neither the kernel nor its mapping is in the directories.
    directories = make_kernels(tmp_path, ["first/x.bsp"])
    destination = tmp_path / "staging"
    destination.mkdir()
    caplog.set_level(logging.INFO)

    # Try to stage the kernel.
    with pytest.raises(NPBError) as raised:
        stage_kernel("a.bsp", directories, str(destination), lookup)

    # The message is compared in full.
    assert str(raised.value) == f"a.bsp not present in {directories[-1]}."
    assert list(destination.iterdir()) == []
    assert messages(caplog) == [
        (logging.INFO, "-- Copy a.bsp to staging directory."),
    ]


def test_stage_kernel_without_files(tmp_path: Path) -> None:
    """With no files to compare, the lookup is not run, so the error is that
    the kernel is not present, even if the lookup would fail.
    """
    # Empty kernel directories and a lookup that would raise its own error.
    directories = make_kernels(tmp_path, [])
    destination = tmp_path / "staging"
    destination.mkdir()
    lookup = Mock(side_effect=NPBError("a.bsp does not have mapping."))

    # Try to stage the kernel.
    with pytest.raises(NPBError) as raised:
        stage_kernel("a.bsp", directories, str(destination), lookup)

    # The lookup was never needed.
    assert str(raised.value) == f"a.bsp not present in {directories[-1]}."
    lookup.assert_not_called()
