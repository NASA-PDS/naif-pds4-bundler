"""Functions to copy provided files into the staging area."""
import logging
import os
import shutil
from typing import Callable, Optional, Tuple

from .files import safe_make_directory


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
