"""Shared fixtures for the integration tests.

The fixtures build a real ``Setup`` and a real ``KernelList`` on top of a
sandbox directory under ``tmp_path``, so tests can run NPB code against real
files without mocking anything.
"""
import re
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

import pytest

from pds.naif_pds4_bundler import __version__
from pds.naif_pds4_bundler.classes.list import KernelList
from pds.naif_pds4_bundler.classes.setup import Setup
from pds.naif_pds4_bundler.utils.types.datatypes import PipelineArgs

TESTS_DATA = Path(__file__).parents[2] / "naif_pds4_bundler"

# Real SPICE kernels shipped with the tests.
KERNELS = TESTS_DATA / "data" / "kernels"

# Configuration the real Setup is built from. Only its directories are
# rewritten; its kernel list patterns are used as they are.
BASE_CONFIG = TESTS_DATA / "config" / "maven.xml"

TEMPLATES = (Path(__file__).parents[3] / "src" / "pds" / "naif_pds4_bundler"
             / "templates" / "1.5.0.0")

# Directories created in the sandbox, named after the configuration tag that
# points to each of them.
SANDBOX_DIRECTORIES = {
    "working_directory": "working",
    "kernels_directory": "kernels",
    "staging_directory": "staging",
    "bundle_directory": "bundle",
    "orbnum_directory": "orbnum",
}


@pytest.fixture
def sandbox(tmp_path: Path) -> SimpleNamespace:
    """Create the directories a real Setup expects, empty, under tmp_path.

    :param tmp_path: pytest temporary directory
    :return: container with the sandbox ``root`` and one attribute per
        directory (``working``, ``kernels``, ``staging``, ``bundle`` and
        ``orbnum``)
    """
    directories = {}
    for name in SANDBOX_DIRECTORIES.values():
        directories[name] = tmp_path / name
        directories[name].mkdir()

    return SimpleNamespace(root=tmp_path, **directories)


@pytest.fixture
def install_kernel(sandbox: SimpleNamespace) -> Callable[..., Path]:
    """Provide a function that copies a real kernel into the sandbox.

    The copy lets a test corrupt a kernel without touching the repository
    data.

    :param sandbox: sandbox directories
    :return: function taking the kernel path relative to the tests' kernels
        directory (such as ``ck/insight_ida_enc_200829_201220_v1.bc``) and an
        optional new file name; it returns the path of the copy
    """

    def _install_kernel(kernel: str, name: str | None = None) -> Path:
        source = KERNELS / kernel
        target = sandbox.kernels / (name or source.name)
        shutil.copy(source, target)
        return target

    return _install_kernel


@pytest.fixture
def real_setup(sandbox: SimpleNamespace,
               monkeypatch: pytest.MonkeyPatch) -> Setup:
    """Build a real Setup the way the pipeline does, rooted in the sandbox.

    :param sandbox: sandbox directories
    :param monkeypatch: pytest monkeypatch, used to restore the working
        directory that ``check_configuration`` changes
    :return: Setup with its configuration checked and its release set
    """
    # Setup.check_configuration changes the process working directory and
    # does not restore it; monkeypatch puts it back when the test ends.
    monkeypatch.chdir(sandbox.root)

    config = BASE_CONFIG.read_text(encoding="utf-8")
    replacements = {tag: str(getattr(sandbox, name))
                    for tag, name in SANDBOX_DIRECTORIES.items()}
    replacements["templates_directory"] = str(TEMPLATES)
    for tag, path in replacements.items():
        config, count = re.subn(rf"<{tag}>[^<]*</{tag}>",
                                f"<{tag}>{path}</{tag}>", config)
        assert count == 1, f"{tag} not found in {BASE_CONFIG}"

    config_path = sandbox.root / "config.xml"
    config_path.write_text(config, encoding="utf-8")

    args = PipelineArgs(config=str(config_path), silent=True, verbose=False,
                        log=False)

    setup = Setup(args, __version__)
    setup.check_configuration()
    setup.set_release()

    return setup


@pytest.fixture
def kernel_list(real_setup: Setup) -> KernelList:
    """Build a real KernelList from the real Setup.

    :param real_setup: Setup rooted in the sandbox
    :return: empty KernelList
    """
    return KernelList(real_setup)
