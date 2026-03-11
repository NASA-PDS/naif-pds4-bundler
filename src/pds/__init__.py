"""PDS Namespace."""

from importlib.resources import files
__version__ = VERSION = (
    files(__package__)
    .joinpath("VERSION.txt")
    .read_text(encoding="utf-8")
    .strip()
)
