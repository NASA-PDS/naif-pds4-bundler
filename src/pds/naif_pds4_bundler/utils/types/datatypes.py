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
    # Core Logic Flags
    config: str
    plan: Optional[str] = None
    kerlist: Optional[str] = None
    faucet: str = ""

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
