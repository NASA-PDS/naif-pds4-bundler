"""NAIF PDS4 Bundle Classes Namespace.

The NPB Classes implement the main functionalities of the pipeline.
"""
from importlib.resources import files
__version__ = VERSION = (
    files(__package__)
    .joinpath("VERSION.txt")
    .read_text(encoding="utf-8")
    .strip()
)
