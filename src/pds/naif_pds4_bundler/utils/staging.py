"""Functions to copy provided files into the staging area."""
import functools
import logging
import os
import shutil
from typing import Callable, Optional, Sequence, Tuple

from .files import safe_make_directory
from ..classes.exceptions import NPBError


def stage_file(source: str, destination_directory: str,
               name: Optional[str] = None) -> Tuple[str, bool]:
    """Copy a file into a staging directory, unless it is already there.

    :param source: Path of the file to copy.
    :param destination_directory: Directory to copy the file into. It is
        created if missing, but its parent must exist.
    :param name: Name of the staged file. Defaults to the name of the source.
    :return: Path of the staged file, and whether it was copied.
    """
    if name is None:
        name = os.path.basename(source)

    # _stage() takes a function that returns the source. The path is already
    # known here, so the function just hands it back.
    return _stage(destination_directory, name, lambda: source)


def stage_kernel(
        name: str, directories: Sequence[str], destination_directory: str,
        mapping_lookup: Optional[Callable[[str], str]] = None
) -> Tuple[str, bool]:
    """Find a kernel and copy it into a staging directory, unless it is
    already there.

    :param name: Name of the kernel, and of the staged file.
    :param directories: Directories to search, with their subdirectories, in
        order of preference. At least one is required.
    :param destination_directory: Directory to copy the kernel into. It is
        created if missing, but its parent must exist.
    :param mapping_lookup: Receives the kernel name and returns the name of
        the file to use instead. Only used if no file has the kernel name.
    :return: Path of the staged kernel, and whether it was copied.
    :raises NPBError: if the kernel has to be copied and is not found.
    """
    return _stage(destination_directory, name,
                  lambda: _find_kernel(name, directories, mapping_lookup))


def _stage(destination_directory: str, name: str,
           find_source: Callable[[], str]) -> Tuple[str, bool]:
    """Stage a file whose source is only needed if it has to be copied.

    :param destination_directory: Directory to copy the file into.
    :param name: Name of the staged file.
    :param find_source: Returns the path of the file to copy. It is not
        called when the file is already staged.
    :return: Path of the staged file, and whether it was copied.
    """
    # The directory is passed on as received, because the log message shows
    # it exactly as written, including any trailing separator.
    safe_make_directory(destination_directory)

    logging.info('-- Copy %s to staging directory.', name)

    staged_path = os.path.join(destination_directory, name)

    if os.path.isfile(staged_path):
        logging.warning('     %s already present in staging directory.', name)
        return staged_path, False

    # Call find_source() only at this point: a file that is already staged
    # needs no source, and whatever the call logs must follow the message
    # announcing the copy.
    shutil.copy2(find_source(), staged_path)

    return staged_path, True


def _find_kernel(name: str, directories: Sequence[str],
                 mapping_lookup: Optional[Callable[[str], str]]) -> str:
    """Find the file to copy for a kernel, by its name or by its mapping.

    :param name: Name of the kernel.
    :param directories: Directories to search, in order of preference.
    :param mapping_lookup: Receives the kernel name and returns its mapping.
    :return: Path of the file found.
    :raises NPBError: if neither search finds a file.
    """
    source = _find_file(directories, lambda file: file == name)

    if source is None and mapping_lookup is not None:
        # The lookup is made when the first file is compared, so it never runs
        # if there are no files. The cache keeps it from running again.
        get_mapping = functools.cache(mapping_lookup)

        source = _find_file(directories,
                            lambda file: file == get_mapping(name))

        if source is not None:
            logging.info('-- Mapping %s with %s', get_mapping(name), name)

    if source is None:
        # Only the last directory searched is named in the message.
        raise NPBError(f"{name} not present in {directories[-1]}.")

    return source


def _find_file(directories: Sequence[str],
               is_wanted: Callable[[str], bool]) -> Optional[str]:
    """Return the first file accepted by a condition.

    :param directories: Directories to search, with their subdirectories, in
        order of preference.
    :param is_wanted: Receives a file name and says whether it is the one.
    :return: Path of the file, or None if no file is accepted.
    """
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if is_wanted(file):
                    return os.path.join(root, file)

    return None
