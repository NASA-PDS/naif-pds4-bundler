"""NAIF PDS4 Bundle Namespace."""
try:
    from importlib.resources import files
except ImportError:  # Python 3.8
    from importlib_resources import files

__version__ = VERSION = (
    files(__package__)
    .joinpath("VERSION.txt")
    .read_text(encoding="utf-8")
    .strip()
)
