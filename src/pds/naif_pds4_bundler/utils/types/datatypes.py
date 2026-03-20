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
#       - Change "frozen" to True
@dataclass(frozen=False)
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
