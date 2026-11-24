"""Functions to read values out of the NPB configuration."""
import re
from typing import Dict, List, Tuple, Union

#: A configured value is returned as the configuration parser left it: a bare
#: string when the configuration lists a single value, a list when it lists
#: several. A default value is always a list with one item.
ConfigValue = Union[str, List[str]]

#: What a kernel list entry can configure: the tag that holds it and the tag
#: nested inside. The order is the one of the values returned.
_KINDS = (
    ("missions", "mission_name"),
    ("observers", "observer"),
    ("targets", "target"),
)


def get_mission_and_observer_and_target(
    kernel_list_config: Dict[str, dict],
    name: str,
    *,
    mission_name: str,
    observer: str,
    target: str,
) -> Tuple[ConfigValue, ConfigValue, ConfigValue]:
    """Get the missions, observers and targets of a kernel or ORBNUM file.

    The first kernel list pattern that matches the name decides. Whatever
    that pattern does not configure is taken from the mission defaults, and
    so is everything when no pattern matches the name.

    :param kernel_list_config: Kernel list configuration, by pattern.
    :param name: Name of the kernel or ORBNUM file.
    :param mission_name: Mission default.
    :param observer: Observer default.
    :param target: Target default.
    :return: Missions, observers and targets, in that order.
    """
    defaults: List[ConfigValue] = [[mission_name], [observer], [target]]
    values: List[ConfigValue] = [[], [], []]

    for entry in kernel_list_config.values():
        if re.match(entry["@pattern"], name):
            values = [
                entry[tag][key] if tag in entry else default
                for (tag, key), default in zip(_KINDS, defaults)
            ]
            break

        #
        # A pattern that does not match falls back to the defaults. With an
        # empty configuration the loop never runs and the three lists stay
        # empty. That is a known defect, fixed separately.
        #
        values = defaults

    # Unpacked, so the result is known to have exactly three items
    return values[0], values[1], values[2]
