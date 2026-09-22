"""Time Functions to support NPB Classes."""
import calendar
import datetime
import logging

import spiceypy



def current_date(date=""):
    """Returns the current date in ``%Y-%m-%d`` format.

    :param date: If present, forces a current date otherwise is obtained from
                 the system
    :type date: str
    :return: Current date
    :rtype: str
    """
    if date:
        t = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
    else:
        t = datetime.datetime.now()

    month = calendar.month_name[t.month]
    return f"{month} {t.day}, {t.year}"


def creation_time(time_format="infomod2"):
    """Returns the creation date and time.

    The date is either in ``maklabel`` or ``infomod2``
    ``%Y-%m-%dT%H:%M:%S.%f`` format.

    :param time_format: Time format
    :type time_format: str
    :return: Current time
    :rtype: str
    """
    t = datetime.datetime.now()
    dt, micro = datetime.datetime.strftime(t, "%Y-%m-%dT%H:%M:%S.%f").split(".")
    creation_time = f'{dt}.{int(micro) // 1000:03d}Z'

    if time_format == "maklabel":
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
                        provided by the PDS4 Information Model that
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

    start_points_list = []
    end_points_list = []

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

        for i in ids:
            if i == main_id:
                ids = [main_id]
                break

    for i in ids:

        # Initialize the coverage SPICE window, setting its cardinality to zero.
        spiceypy.scard(incard=0, cell=coverage)
        spiceypy.spkcov(spk=path, idcode=i, cover=coverage)

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
                        provided by the PDS4 Information Model that
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
    start_points_list = []
    end_points_list = []

    maxiv = 10000
    winsiz = 2 * maxiv
    maxobj = 10000

    ids = spiceypy.support_types.SPICEINT_CELL(maxobj)
    ids = spiceypy.ckobj(ck=path, out_cell=ids)

    for i in ids:
        coverage = spiceypy.support_types.SPICEDOUBLE_CELL(winsiz)

        # Initialize the coverage SPICE window, setting its cardinality to zero.
        spiceypy.scard(incard=0, cell=coverage)

        coverage = spiceypy.ckcov(
            ck=path,
            idcode=i,
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
        return start_time, stop_time

    return et_to_date(start_time, stop_time, date_format=date_format,
                      kernel_type="ck", system=system)


def pck_coverage(path, date_format="infomod2", system="UTC"):
    """Returns the coverage of a PCK file.

    The function assumes that the appropriate kernels have already been loaded.

    :param path: File path
    :type path: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second.
    :type date_format: str
    :param system: Determine the output time system: UTC or TDB
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

    start_points_list = []
    end_points_list = []

    for i in ids:

        # Initialize the coverage SPICE window, setting its cardinality to zero.
        spiceypy.scard(incard=0, cell=coverage)
        spiceypy.pckcov(pck=path, idcode=i, cover=coverage)

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
                        provided by the PDS4 Information Model that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second
    :type date_format: str
    :param system: Determine the output time system: UTC or TDB
    :type system: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :return: start and finish coverage
    :rtype: list of str
    """
    beget = []
    endet = []

    # Open the DSK file.
    handle = spiceypy.dasopr(path)

    try:
        # Search the first segment in the file, obtain the segment's DLA
        # descriptor.
        dladsc = spiceypy.dlabfs(handle)

        #  Loop through segments to get the earliest starting epoch and the
        #  latest ending epoch.
        while True:
            dskdsc = spiceypy.dskgd(handle, dladsc)

            beget.append(dskdsc.start)
            endet.append(dskdsc.stop)

            try:
                (dladsc, _) = spiceypy.dlafns(handle, dladsc)

            # SpiceyPy's dlafns raises a NotFoundError, if it cannot find a
            # segment following a specified segment in a DLA file. That
            # means that we are at the end of the file.
            except spiceypy.exceptions.NotFoundError:
                break
    finally:
        # Close the DSK file
        spiceypy.dascls(handle)

    start_time = min(beget)
    stop_time = max(endet)

    return et_to_date(start_time, stop_time, date_format=date_format, system=system)


def _find_ek_time_columns(table_name):
    """Find time columns in an EK table by directly querying common patterns.

    This approach bypasses spiceypy.ekssum() column name truncation issues
    (e.g., BEGIN_TIME reported as EGIN_TIME in some EK files) by directly
    attempting queries with known time column patterns.

    :param table_name: Name of the EK table to query
    :type table_name: str
    :return: Tuple of (start_column, stop_column) if found, None if no time columns found
    :rtype: tuple or None
    """
    # Priority order: most common patterns first
    time_patterns = [
        # Single time column (use for both start/stop)
        ('ET', 'ET', True),
        ('TIME', 'TIME', True),
        ('EPOCH', 'EPOCH', True),
        ('EVT_TIME', 'EVT_TIME', True),
        ('EVENT_TIME', 'EVENT_TIME', True),

        # Start/Stop pairs (most common first)
        ('BEGIN_TIME', 'END_TIME', False),
        ('START_TIME', 'STOP_TIME', False),
        ('START_TIME', 'END_TIME', False),
        ('BEGIN_ET', 'END_ET', False),
        ('START_ET', 'STOP_ET', False),
        ('START_UTC', 'STOP_UTC', False),
        ('BEGIN_UTC', 'END_UTC', False),
    ]

    for start_col, stop_col, is_single in time_patterns:
        try:
            # Build query
            if is_single:
                query = f"SELECT {start_col} FROM {table_name}"
            else:
                query = f"SELECT {start_col}, {stop_col} FROM {table_name}"

            # Try the query
            nmrows, error, _ = spiceypy.ekfind(query, 256)

            if not error and nmrows > 0:
                # Success! These columns exist and have data
                logging.debug(f"    Found time columns via query: {start_col}, {stop_col}")
                return (start_col, stop_col)

        except spiceypy.exceptions.SpiceyError:
            continue  # Try next pattern

    return None  # No time columns found


def ek_coverage(path, date_format="infomod2", system="UTC"):
    """Returns the coverage of an EK file following MAKLABEL's approach.

    MAKLABEL extracts EK coverage by:
    1. Loading the EK with FURNSH to make it queryable
    2. Examining segment metadata to identify time columns
    3. Querying all rows and manually finding MIN/MAX
    4. Converting time values to ET if needed

    NOTE - Text event kernels (.ten) do not have queryable coverage and
           return empty strings.

    The function assumes that the appropriate kernels (LSK) have already been
    loaded.

    :param path: File path
    :type path: str
    :param date_format: Date format, the default is the one
                        provided by the PDS4 Information Model that
                        rounds the milliseconds and then implements an
                        inward addition for the coverage start time and
                        inward subtraction for the coverage stop time.
                        The other option is the MAKLABEL style that
                        rounds to the second
    :type date_format: str
    :param system: Determine the output time system: UTC or TDB
    :type system: str
    :raise: if the date_format parameter argument is not ``infomod2`` or
            ``maklabel``
    :return: start and finish coverage, or empty strings if no time data found
    :rtype: list of str
    """
    extension = path.split(".")[-1].strip().lower()

    # Log entry for debugging
    logging.debug(f"Extracting EK coverage from: {path}")

    # Text event kernels (.ten) don't have queryable coverage
    if extension == "ten":
        logging.debug("  Text event kernel (.ten) - returning empty coverage")
        return ["", ""]

    # Load the EK to make it queryable
    try:
        spiceypy.furnsh(path)
    except spiceypy.exceptions.SpiceyError as e:
        logging.warning(f"  Failed to load EK file {path}: {e}")
        return ["", ""]

    try:
        # Open for segment examination
        handle = spiceypy.dasopr(path)

        try:
            nseg = spiceypy.eknseg(handle)
            logging.debug(f"  Found {nseg} segment(s)")

            if nseg == 0:
                logging.debug("  No segments found - returning empty coverage")
                return ["", ""]

            beget = []
            endet = []
            segments_with_time = 0
            processed_tables = set()  # Track which tables we've already queried

            for segno in range(nseg):
                try:
                    # Get segment summary: returns SpiceEKSegSum named tuple
                    segsum = spiceypy.ekssum(handle, segno)

                    if segsum.nrows == 0:
                        # No rows in this segment
                        logging.debug(f"  Segment {segno}: {segsum.tabnam} - skipping (0 rows)")
                        continue

                    table_name = segsum.tabnam

                    # Skip if we've already processed this table
                    # (SPICE EK queries return ALL rows from a table across all segments)
                    if table_name in processed_tables:
                        logging.debug(f"  Segment {segno}: {table_name} - skipping (already processed)")
                        continue

                    processed_tables.add(table_name)

                    # Try query-first approach to find time columns
                    # This bypasses spiceypy.ekssum() column name truncation issues
                    time_cols = _find_ek_time_columns(table_name)

                    if time_cols:
                        # Found time columns via direct query
                        start_col, stop_col = time_cols
                    else:
                        # Fallback: inspect cnames from ekssum (may have truncated names)
                        logging.debug(f"  Segment {segno}: {table_name} - trying cnames fallback")
                        cnames = segsum.cnames if segsum.cnames else []

                        # Filter out empty column names (BES files can have empty strings for unused slots)
                        cnames = [name for name in cnames if name]

                        if not cnames:
                            logging.debug(f"  Segment {segno}: {table_name} - skipping (no columns)")
                            continue

                        # Look for time columns - prioritize ET columns
                        start_col = None
                        stop_col = None

                        # First pass: look for ET or single TIME column
                        for idx, col_name in enumerate(cnames):
                            col_upper = col_name.upper()
                            if col_upper in ['ET', 'TIME', 'EPOCH', 'EVT_TIME', 'EVENT_TIME']:
                                start_col = col_name
                                stop_col = col_name
                                break

                        # Second pass: look for START/STOP pairs (including truncated patterns)
                        if not start_col:
                            # Include truncated patterns like 'EGIN_TIME' for 'BEGIN_TIME'
                            start_candidates = ['START_TIME', 'START_ET', 'START',
                                              'BEGIN_TIME', 'EGIN_TIME',  # truncated BEGIN_TIME
                                              'START_UTC', 'BEGIN_ET']
                            stop_candidates = ['STOP_TIME', 'STOP_ET', 'STOP',
                                             'END_TIME', 'STOP_UTC', 'END_ET']

                            for start_name in start_candidates:
                                for idx, col_name in enumerate(cnames):
                                    if col_name.upper() == start_name:
                                        start_col = col_name
                                        break
                                if start_col:
                                    break

                            for stop_name in stop_candidates:
                                for idx, col_name in enumerate(cnames):
                                    if col_name.upper() == stop_name:
                                        stop_col = col_name
                                        break
                                if stop_col:
                                    break

                        # If we have at least a start column, proceed
                        if not start_col:
                            logging.debug(f"  Segment {segno}: {table_name} - skipping (no time columns)")
                            continue

                        # Use the same column for both if only one found
                        if not stop_col:
                            stop_col = start_col

                    # Query all rows (no MIN/MAX - workaround for limited EK query support)
                    try:
                        query = f"SELECT {start_col}"
                        if stop_col != start_col:
                            query += f", {stop_col}"
                        query += f" FROM {table_name}"

                        logging.debug(f"  Segment {segno}: {table_name} - querying {segsum.nrows} rows")

                        nmrows, error, _ = spiceypy.ekfind(query, 256)

                        if error or nmrows == 0:
                            # Query failed or no results
                            logging.debug(f"  Segment {segno}: Query failed or returned 0 rows")
                            continue

                        # Fetch values from all rows to find min/max
                        # Process ALL rows (no artificial limit) to ensure we get true min/max
                        segment_times = []

                        for row in range(nmrows):
                            try:
                                # Fetch start time value
                                start_et = _ek_fetch_row_value(0, row, 0)

                                # Fetch stop time value (same column if single time column)
                                if stop_col != start_col:
                                    stop_et = _ek_fetch_row_value(1, row, 0)
                                else:
                                    stop_et = start_et

                                if start_et is not None:
                                    segment_times.append(start_et)
                                if stop_et is not None and stop_et != start_et:
                                    segment_times.append(stop_et)

                            except (spiceypy.exceptions.SpiceyError, ValueError, IndexError) as e:
                                # Failed to fetch this row, continue
                                logging.debug(f"  Segment {segno}: Row {row} fetch failed: {type(e).__name__}")
                                continue

                        if segment_times:
                            beget.append(min(segment_times))
                            endet.append(max(segment_times))
                            segments_with_time += 1
                            logging.debug(f"  Segment {segno}: {table_name} - found {len(segment_times)} time values")

                    except spiceypy.exceptions.SpiceyError as e:
                        # Query failed, skip this segment
                        logging.debug(f"  Segment {segno}: Query failed: {e}")
                        continue

                except spiceypy.exceptions.SpiceyError as e:
                    # Segment processing failed, skip it
                    logging.debug(f"  Segment {segno}: Processing failed: {e}")
                    continue

            if not beget or not endet:
                # No time-tagged segments found
                logging.info(f"  No time data found in {nseg} segment(s)")
                return ["", ""]

            start_time = min(beget)
            stop_time = max(endet)

            logging.debug(f"  Extracted coverage from {segments_with_time} segment(s)")

        finally:
            # Close the EK file
            spiceypy.dascls(handle)

    finally:
        # Unload the EK
        spiceypy.unload(path)

    result = et_to_date(start_time, stop_time, date_format=date_format, system=system)
    logging.debug(f"  Coverage: {result[0]} to {result[1]}")
    return result


def _ek_fetch_row_value(selidx, row, element):
    """Helper to fetch EK value from query result and convert to ET.

    Tries multiple fetch methods to handle different column types:
    - ekgd for double precision (ET values)
    - ekgi for integer values
    - ekgc for character/time strings (converts to ET)

    :param selidx: Index of parent column in SELECT clause
    :type selidx: int
    :param row: Row to fetch from
    :type row: int
    :param element: Index of element within column entry
    :type element: int
    :return: Time value in ET, or None if fetch failed
    :rtype: float or None
    """
    # Try double precision first (most common for ET)
    try:
        result = spiceypy.ekgd(selidx, row, element)
        if len(result) >= 2:
            value, is_null = result[0], result[-1]
            if not is_null:
                return float(value)
    except spiceypy.exceptions.SpiceyError:
        pass  # Not a double column, try next type

    # Try integer (some EKs use integer SCLK values)
    try:
        result = spiceypy.ekgi(selidx, row, element)
        if len(result) >= 2:
            value, is_null = result[0], result[-1]
            if not is_null:
                # Assume integer is already in ET or SCLK
                # For now, treat as ET - proper SCLK conversion would need spacecraft ID
                return float(value)
    except spiceypy.exceptions.SpiceyError:
        pass  # Not an integer column, try next type

    # Try character/time string
    try:
        result = spiceypy.ekgc(selidx, row, element, 256)

        # Handle both (str, bool) and (int, str, bool) return formats
        if len(result) == 2:
            value_str, is_null = result
        elif len(result) >= 3:
            value_str, is_null = result[1], result[2]
        else:
            return None

        if not is_null and value_str:
            # Try to convert as UTC string to ET
            try:
                return spiceypy.str2et(value_str.strip())
            except spiceypy.exceptions.SpiceyError:
                # Not a valid time string - might be non-time character data
                pass

    except spiceypy.exceptions.SpiceyError:
        pass  # Not a character column

    # All fetch methods failed
    return None



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
    :param system: Determine the output time system: UTC or TDB
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




def parse_date(date_str: str) -> datetime.datetime:
    """Parses a date string into a datetime object.

    The supported formats for the input date string are:
       - %Y-%b-%d-%H:%M:%S
       - %Y-%m-%dT%H:%M:%S

    :param date_str: Stop time to determine list of years

    :raises ValueError: If the input string does not conform to any of the
                        supported formats.

    :returns: date corresponding to the input str
    """
    formats = ["%Y-%b-%d-%H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError("The input string does not conform to any of the supported formats.")
