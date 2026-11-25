"""Start and stop times of the PDS4 checksum product."""
from __future__ import annotations

import logging
import os
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from ..classes.setup import Setup


def checksum_coverage(file_names: Iterable[str], setup: Setup,
                      checksum_name: str) -> tuple[str, str]:
    """Determine the start and stop times of a PDS4 checksum file.

    The times come from the labels of the spice_kernels collection and from the
    ORBNUM labels listed in the checksum. Each label is read from the bundle
    directory or, if it is not there, from the staging directory. Any other
    file name is ignored.

    Messages are logged as if the caller had written them.

    :param file_names: Names of the archive files listed in the checksum.
    :param setup: NPB execution setup object.
    :param checksum_name: Name of the checksum file, used in the error message.
    :return: The earliest start time and the latest stop time. The mission
        start or finish time is used when no label provides one.
    """
    # The root logger is called directly because, on Python 3.10, stacklevel
    # does not skip the right frame through logging.error() and the like.
    logger = logging.getLogger()

    #
    # Gather all the relevant products that define the coverage of the
    # checksum file: orbnum labels and spice_kernels collection labels.
    #
    coverage_list = [
        name for name in sorted(file_names)
        if ("spice_kernels/collection_spice_kernels_v" in name) or (
            "miscellaneous/orbnum/" in name and ".xml" in name)
    ]

    start_times = []
    stop_times = []
    for product in coverage_list:
        #
        # The files can either be in the staging or the final area.
        #
        path = (
            f"{setup.bundle_directory}/"
            f"{setup.mission_acronym}_spice/" + product
        )
        if not os.path.isfile(path):
            path = f"{setup.staging_directory}/" + product
            if not os.path.isfile(path):
                logger.error(
                    '-- Product required to determine %s coverage: '
                    '%s not found.',
                    checksum_name, product, stacklevel=2)

        if os.path.isfile(path):
            with open(path, "r", encoding='utf-8') as lbl:
                for line in lbl:
                    if "<start_date_time>" in line:
                        start_time = line.split("<start_date_time>")[-1].split(
                            "</"
                        )[0]
                        start_times.append(start_time)
                    if "<stop_date_time>" in line:
                        stop_time = line.split("<stop_date_time>")[-1].split(
                            "</"
                        )[0]
                        stop_times.append(stop_time)

    if not start_times:
        logger.warning('-- Start time set to mission start time: %s',
                       setup.mission_start, stacklevel=2)
        start_times.append(setup.mission_start)

    if not stop_times:
        logger.warning('-- Stop time set to mission finish time: %s',
                       setup.mission_finish, stacklevel=2)
        stop_times.append(setup.mission_finish)

    # The times are compared as strings.
    return min(start_times), max(stop_times)
