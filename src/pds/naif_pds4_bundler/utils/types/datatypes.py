"""Dataclasses defining different complex data types used within the NPB
package.
"""
from dataclasses import dataclass
from typing import Optional


# TODO: - Convert "config", "plan", "kerlist", "clear" to a PathLike
#       - Rename "kernlist" to "kernels"
#       - Implement logic present at the beginning of the current pipeline
#         module for checking arguments and setting the optional values
#         when these depend on other arguments.
#       - Remove "" from the list of supported values for "diff" and "faucet"
@dataclass(frozen=True)
class PipelineArgs:
    """Immutable argument container for an NPB pipeline run.

    All fields are set at construction time and cannot be modified
    afterward. :meth:`__post_init__` validates and normalizes the
    values of :attr:`faucet` and :attr:`diff`, enforces consistency
    between related flags, and raises :exc:`ValueError` for any
    out-of-range value.

    :param config:   Path to the NPB XML configuration file.
    :param plan:     Path to the release ``.plan`` file. Optional.
    :param kerlist:  Path to an explicit kernel list file. Optional.
    :param faucet:   Pipeline stop-point. One of ``"clear"``, ``"plan"``,
                     ``"list"``, ``"checks"``, ``"staging"``, ``"bundle"``,
                     ``"labels"``, or ``None`` / ``""`` to run to completion.
                     Defaults to ``""``.
    :param log:      Write a log file when ``True``. Defaults to ``False``.
    :param silent:   Suppress all console output when ``True``.
                     Automatically set to ``False`` when :attr:`verbose` is
                     ``True``. Defaults to ``False``.
    :param verbose:  Enable verbose console output when ``True``.
                     Defaults to ``False``.
    :param debug:    Enable debug-level logging when ``True``.
                     Defaults to ``True`` for library usage.
    :param diff:     Diff comparison scope. One of ``"all"``, ``"log"``,
                     ``"files"``, or ``None`` / ``""`` to skip diffing. Setting
                     ``"log"`` or ``"all"`` implicitly enables :attr:`log`.
                     Defaults to ``None``.
    :param clear:    Path to a directory to clear before the run. When set
                     and :attr:`faucet` is empty, :attr:`faucet` is
                     automatically set to ``"clear"``. Optional.
    :param checksum: Recompute checksums when ``True``. Defaults to
                     ``False``.
    """
    # Core Logic Flags
    config: str
    plan: Optional[str] = None
    kerlist: Optional[str] = None
    faucet: Optional[str] = ""

    # Logging & Output
    log: bool = False
    silent: bool = False
    verbose: bool = False
    debug: bool = True  # Default for Library usage

    # Operations
    diff: Optional[str] = None
    clear: Optional[str] = None
    checksum: bool = False

    def __post_init__(self) -> None:
        """Perform checks and derived assignments after field initialization.
        """
        # Note: This dataclass must be immutable once initialized and this
        #       method is executed after the default initialization, therefore
        #       we cannot use
        #          self.attribute = value
        #       Instead we will use the magic method
        #          object.__setattr__(self, name, value)
        #       whenever we need to update attributes, preventing the dataclass
        #       from raising a FrozenInstanceError exception.

        # Force the values of the attributes "faucet" and "diff" to be
        # lowercase and make sure that they are within the list of allowed
        # values.
        if isinstance(self.faucet, str):
            object.__setattr__(self,'faucet', self.faucet.lower())
        if self.faucet not in ["clear", "plan", "list", "checks", "staging",
                               "bundle", "labels", None, ""]:
            raise ValueError("`faucet` attribute has incorrect value.")

        if isinstance(self.diff, str):
            object.__setattr__(self,'diff', self.diff.lower())
        if self.diff not in ["all", "log", "files", None, ""]:
            raise ValueError("`diff` attribute has incorrect value.")

        # Set silent to False if verbose is set to True.
        if self.verbose:
            object.__setattr__(self,"silent", False)

        # Force logging (attribute "log" set to true) if Diff files are
        # provided with the log (attribute "diff" set to "log" or "all").
        if self.diff in ["log", "all"]:
            object.__setattr__(self,"log", True)

        # Set attribute "faucet" to "clear" if it is originally None and
        # attribute "clear` is True.
        if self.clear and not self.faucet:
            object.__setattr__(self,"faucet", "clear")
