"""Time Functions to support NPB Classes."""
import calendar
import datetime

import spiceypy


def current_time(format="infomod2"):
    """Returns the current date and time in ``%Y-%m-%dT%H:%M:%S`` format.

    :param format: Time format from configuration.
    :type format: string
    :return: Current date and time
    :rtype: str
    """
    time = str(datetime.datetime.now())
    time = time.replace(" ", "T")

    if format == "maklabel":
        time = time.split(".")[0]
    elif format == "infomod2":
        time = time[:-3] + "Z"

    return time


def current_date(date=""):
    """Returns the current date in ``%Y-%m-%d`` format.

    :param date: If present, forces a current date otherwise is obtained from
                 the system
    :type date: str
    :return: Current date
    :rtype: str
    """
    if date:
        time = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    else:
        time = datetime.datetime.now()

    date = datetime.datetime.strftime(time, "%m %-d, %Y")
    date = calendar.month_name[int(date[0:2])] + date[2:]

    return date


def creation_time(format="infomod2"):
    """Returns the creation date and time.

    The date is either in ``maklabel`` or ``infomod2``
    ``%Y-%m-%dT%H:%M:%S.%f`` format.

    :param format: Time format
    :type format: str
    :return: Current time
    :rtype: str
    """
    t = datetime.datetime.now()
    dt, micro = datetime.datetime.strftime(t, "%Y-%m-%dT%H:%M:%S.%f").split(".")
    creation_time = "%s.%03d" % (dt, int(micro) / 1000) + "Z"

    if format == "maklabel":
        creation_time = creation_time[:-5]

    return creation_time


def spk_coverage(path, main_name="", date_format="infomod2", system="UTC"):
    """Returns the coverage of a SPK file.

    The function assumes that the appropriate kernels have already been loaded.

    :param path: File path
    :type path: str
    :param main_name: Mission observer name.
    :type main_name: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model 2.0 that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the ``MAKLABEL`` style that
                        rounds to the second.
    :type date_format: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :return: start and finish coverage
    :rtype: list of str
    """
    ids = spiceypy.spkobj(path)

    maxiv = 1000
    winsiz = 2 * maxiv

    coverage = spiceypy.support_types.SPICEDOUBLE_CELL(winsiz)

    start_points_list = list()
    end_points_list = list()

    #
    # If one of the IDs of the kernel is the ID that corresponds to the SPICE
    # acronym of the mission name.
    #
    if main_name:
        #
        # Determine the "Main" ID of the mission, using the
        # spice_name parameter of the bundle_parameters section of the
        # configuration.
        #
        main_id = spiceypy.bodn2c(main_name)

        for id in ids:
            if id == main_id:
                ids = [main_id]
                break

    for id in ids:

        spiceypy.scard, 0, coverage
        spiceypy.spkcov(spk=path, idcode=id, cover=coverage)

        num_inter = spiceypy.wncard(coverage)

        for i in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, i)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])

    start_time = min(start_points_list)
    stop_time = max(end_points_list)

    return et_to_date(start_time, stop_time, date_format=date_format, system=system)


def ck_coverage(path, timsys="TDB", date_format="infomod2", system="UTC"):
    """Returns the coverage of a CK file.

    The function assumes that the appropriate kernels have already been loaded.

    :param path: File path
    :type path: str
    :param timsys: Determines whether if the time system is SCLK or not
    :type timsys: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model 2.0 that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the ``MAKLABEL`` style that
                        rounds to the millisecond.
    :type date_format: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :param system: If the time system is not SCLK, then it can be UTC or TDB
    :type system: str
    :return: start and finish coverage
    :rtype: list of str
    """
    start_points_list = list()
    end_points_list = list()

    maxiv = 10000
    winsiz = 2 * maxiv
    maxobj = 10000

    ids = spiceypy.support_types.SPICEINT_CELL(maxobj)
    ids = spiceypy.ckobj(ck=path, out_cell=ids)

    for id in ids:
        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(winsiz)
        spiceypy.scard, 0, coverage
        coverage = spiceypy.ckcov(
            ck=path,
            idcode=id,
            needav=False,
            level="SEGMENT",
            tol=0.0,
            timsys=timsys,
            cover=coverage,
        )

        num_inter = spiceypy.wncard(coverage)

        for j in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, j)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])

    start_time = min(start_points_list)
    stop_time = max(end_points_list)

    if timsys == "SCLK":
        return (start_time, stop_time)
    else:
        return et_to_date(
            start_time,
            stop_time,
            date_format=date_format,
            kernel_type="ck",
            system=system,
        )


def pck_coverage(path, date_format="infomod2", system="UTC"):
    """Returns the coverage of a PCK file.

    The function assumes that the appropriate kernels have already been loaded.

    :param path: File path
    :type path: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model 2.0 that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second.
    :type date_format: str
    :param system: Determine the output ime system: UTC or TDB
    :type system: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :return: start and finish coverage
    :rtype: list of str
    """
    maxiv = 1000
    winsiz = 2 * maxiv
    maxobj = 1000

    ids = spiceypy.support_types.SPICEINT_CELL(maxobj)

    spiceypy.pckfrm(path, ids)

    coverage = spiceypy.support_types.SPICEDOUBLE_CELL(winsiz)

    start_points_list = list()
    end_points_list = list()

    for id in ids:

        spiceypy.scard, 0, coverage
        spiceypy.pckcov(pck=path, idcode=id, cover=coverage)

        num_inter = spiceypy.wncard(coverage)

        for i in range(0, num_inter):
            endpoints = spiceypy.wnfetd(coverage, i)

            start_points_list.append(endpoints[0])
            end_points_list.append(endpoints[1])

    start_time = min(start_points_list)
    stop_time = max(end_points_list)

    return et_to_date(start_time, stop_time, date_format=date_format, system=system)


def dsk_coverage(path, date_format="infomod2", system="UTC"):
    """Returns the coverage of a DSK file.

    The function assumes that the appropriate kernels (LSK) have already been
    loaded.

    This function is based on the DSKLBL ( Generate an MGSO or PDS DSK
    label file ) subroutine that belongs to the MAKLABEL NAIF utility.

    :param path: File path
    :type path: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model 2.0 that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second
    :type date_format: str
    :param system: Determine the output ime system: UTC or TDB
    :type system: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :return: start and finish coverage
    :rtype: list of str
    """
    found = True
    beget = []
    endet = []

    #
    # Open the DSK file.
    #
    handle = spiceypy.dasopr(path)

    #
    # Search the first segment in the file, obtain the segment's DLA
    # descriptor
    #
    nxtdsc = spiceypy.dlabfs(handle)
    dladsc = nxtdsc

    #
    #  Loop through segments to get the earliest starting epoch and the
    #  latest ending epoch.
    #
    while found:
        dskdsc = spiceypy.dskgd(handle, dladsc)

        beget.append(dskdsc.start)
        endet.append(dskdsc.stop)

        currnt = dladsc
        try:
            (dladsc, found) = spiceypy.dlafns(handle, currnt)
        except BaseException:
            #
            # Close the DSK file
            #
            spiceypy.dascls(handle)

            break

    start_time = min(beget)
    stop_time = max(endet)

    return et_to_date(start_time, stop_time, date_format=date_format, system=system)


def et_to_date(beget, endet, date_format="infomod2", kernel_type="Text", system="UTC"):
    """Convert ET (ephemeris time) to a Date Time string.

    :param beget: Start ephemeris time (ET)
    :type beget: float
    :param endet: End ephemeris time (ET)
    :type endet: float
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model 2.0 that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second
    :type date_format: str
    :param kernel_type: Indicates whether if it is a text or binary kernel
    :type kernel_type: str
    :param system: Determine the output ime system: UTC or TDB
    :type system: str
    :return: Start and Stop dates
    :rtype: list of str
    """
    time_length = 62

    if date_format == "infomod2":
        inwards_seconds = 0.001
        time_format = f"YYYY-MM-DDTHR:MN:SC.###::{system}::RND"
    elif date_format == "maklabel":
        inwards_seconds = 0.0
        if kernel_type.upper() == "CK":
            time_format = f"YYYY-MM-DDTHR:MN:SC.###::{system}::RND"
        else:
            time_format = f"YYYY-MM-DDTHR:MN:SC::{system}::RND"
    else:
        raise ValueError("date_format argument is incorrect.")

    start_time_cal = spiceypy.timout(beget, time_format, time_length) + "Z"
    stop_time_cal = spiceypy.timout(endet, time_format, time_length) + "Z"

    #
    # Inward seconds are only taken into account if the milliseconds are not
    # 000.
    #
    if (date_format == "infomod2") and ("000Z" not in start_time_cal.split(".")[-1]):
        start_time_cal = (
            spiceypy.timout(beget + inwards_seconds, time_format, time_length) + "Z"
        )
    if (date_format == "infomod2") and ("000Z" not in stop_time_cal.split(".")[-1]):
        stop_time_cal = (
            spiceypy.timout(endet - inwards_seconds, time_format, time_length) + "Z"
        )

    return [start_time_cal, stop_time_cal]


def pds3_label_gen_date(file):
    """Returns the creation date of a given PDS3 label.

    :param path: File path
    :type path: str
    :return: Creation date
    :rtype: str
    """
    generation_date = "N/A"

    with open(file, "r") as f:

        for line in f:
            if "PRODUCT_CREATION_TIME" in line:
                generation_date = line.split("=")[1].strip()

    return generation_date


def get_years(start_time, stop_time):
    """Get years contained in a time period.

    Returns the list of years contained in between the provided
    start time and the stop time.

    :param start_time: Start time to determine list of years
    :type start_time: str
    :param stop_time: Stop time to determine list of years
    :type stop_time: str
    :return: Creation date
    :rtype: list of str
    """
    years = []

    start_year = start_time.split("-")[0]
    finish_year = stop_time.split("-")[0]

    year = int(start_year)
    while year <= int(finish_year):
        years.append(str(year))
        year += 1

    return years
