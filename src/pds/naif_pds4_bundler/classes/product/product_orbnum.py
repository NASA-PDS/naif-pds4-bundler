"""Implementation of the OrbNum file product class."""
import datetime
import logging
import os
import re
import shutil
from typing import List

from .product import Product
from ...pipeline.runtime import handle_npb_error
from ...utils.time import parse_date
from ...utils import add_crs_to_file
from ...utils import check_eol
from ...utils import get_latest_kernel
from ...utils import safe_make_directory
from ...utils import spk_coverage
from ...utils import utf8len
from ..label import OrbnumFilePDS4Label


class OrbnumFileProduct(Product):
    """Class that represents an OrbNum file.

    :param setup:                    NPB execution setup object
    :param name:                     OrbNum file path
    :param collection:               Miscellaneous Collection that contains the
                                     OrbNum file product
    :param spice_kernels_collection: SPICE Kernel Collection
    """

    def __init__(self, setup, name: str, collection, spice_kernels_collection) -> None:
        """Constructor."""
        self.collection = collection
        self.kernels_collection = spice_kernels_collection
        self.setup = setup
        self.name = name
        self.extension = name.split(".")[-1].strip()
        self.path = setup.orbnum_directory

        if setup.pds_version == "3":
            self.collection_path = setup.staging_directory + os.sep + "extras"
            product_path = self.collection_path + os.sep + "orbnum" + os.sep

        elif setup.pds_version == "4":
            self.collection_path = setup.staging_directory + os.sep + "miscellaneous"
            product_path = self.collection_path + os.sep + "orbnum" + os.sep

        #
        # Map the orbnum file with its configuration.
        #
        for orbnum_type in setup.orbnum:
            if re.match(orbnum_type["pattern"], name):
                self._orbnum_type = orbnum_type
                self._pattern = orbnum_type["pattern"]

        if not hasattr(self, "_orbnum_type"):
            handle_npb_error(
                "The orbnum file does not match any type "
                "described in the configuration.",
                setup=self.setup,
            )

        if self.setup.pds_version == "4":
            self.set_product_lid()
            self.set_product_vid()

        #
        # We generate the kernel directory if not present
        #
        safe_make_directory(product_path)

        #
        # We copy the file to the staging directory.
        #
        logging.info(f"-- Copy {self.name} to staging directory.")
        if not os.path.isfile(product_path + self.name):
            shutil.copy2(
                self.path + os.sep + self.name, product_path + os.sep + self.name
            )
            self.new_product = True
        else:
            logging.warning(f"     {self.name} already present in staging directory.")

            self.new_product = False

        #
        # Add CRs to the ORBNUM file. Need reveiw for PDS3.
        #
        if self.setup.pds_version == "4":
            if check_eol(product_path + os.sep + self.name, self.setup.eol):
                logging.info("-- Adding CRLF to ORBNUM file.")
                add_crs_to_file(
                    product_path + os.sep + self.name, self.setup.eol, self.setup
                )

        #
        # We update the path after having copied the kernel.
        #
        self.path = product_path + self.name

        #
        # We obtain the parameters required to fill the label.
        #
        if self.setup.pds_version == "4":
            header = self.read_header()
            self.set_event_detection_key(header)
            self.header_length = self.get_header_length()
            self.set_previous_orbnum()
            self.read_records()
            self._sample_record = self.get_sample_record()
            self.description = self.get_description()

            #
            # Table character description is only obtained if there are missing
            # records.
            #
            self.table_char_description = self.table_character_description()

            self.get_params(header)
            self.set_params(header)

            self.coverage()

            #
            # Extract the required information from the kernel list read from
            # configuration for the product.
            #
            (missions, observers, targets) = self.get_mission_and_observer_and_target()

            self.missions = missions
            self.targets = targets
            self.observers = observers

            if "mission_name" in self._orbnum_type:
                self.missions = [self._orbnum_type["mission_name"]]
            if "observer" in self._orbnum_type:
                self.observers = [self._orbnum_type["observer"]]
            if "target" in self._orbnum_type:
                self.targets = [self._orbnum_type["target"]]

        super().__init__()

        #
        # The kernel is labeled.
        #
        if self.setup.pds_version == "4":
            logging.info(f"-- Labeling {self.name}...")
            self.label = OrbnumFilePDS4Label(setup, self)

    def set_product_lid(self) -> None:
        """Set the Product LID."""
        self.lid = "{}:miscellaneous:orbnum_{}".format(
            self.setup.logical_identifier, self.name
        ).lower()

    def set_product_vid(self) -> None:
        """Set the Product VID."""
        self.vid = "1.0"

    def set_previous_orbnum(self) -> None:
        """Determine the previous version of the ORBNUM file.

        For some cases, more than one orbit number file
        may exist for a given SPK, with only one file having the same name
        as the SPK and other files having a version token appended to the
        SPK name. It is also possible that a version token is always present.
        This method finds the latest version of such an orbnum file in the
        final area.

        NPB assumes that the version pattern of the orbnum file name follows
        the REGEX pattern::

           _[vV][0-9]*[.]

        E.g.::

           (...)_v01.orb
           (...)_V9999.nrb
           (...)_v1.orb

        This method provides values to the ``_previous_orbnum`` and
        ``_orbnum_version`` protected attributes, both are strings.
        """
        path = [
            f"{self.setup.bundle_directory}/{self.setup.mission_acronym}"
            f"_spice//miscellaneous/"
        ]
        previous_orbnum = get_latest_kernel("orbnum", path, self._pattern, dates=True)

        if previous_orbnum:

            version_match = re.search(r"_v\d*\.", previous_orbnum[0], flags=re.I)
            version = re.findall(r"\d+", version_match.group(0))
            version = "".join(version)

            self._previous_version = version
            self.previous_orbnum = previous_orbnum[0]

        #
        # If a previous orbnum file is not found, it might be due to the
        # fact that the file does not have a version explicitly indicated
        # by the filename.
        #
        else:

            #
            # Try to remove the version part of the filename pattern. For
            # the time being this implementation is limited to NAIF
            # orbnum files with these characteristics.
            #
            try:
                version_pattern = r"_[vV]\[0\-9\]*[\.]"
                version_match = re.search(version_pattern, self._pattern)
                pattern = ".".join(self._pattern.split(version_match.group(0)))
            except BaseException:
                #
                # The pattern already does not have an explicit version
                # number.
                #
                pattern = self._pattern

            previous_orbnum = get_latest_kernel("orbnum", path, pattern, dates=True)
            if not previous_orbnum:
                self._previous_orbnum = ""
            else:
                self._previous_orbnum = previous_orbnum

            self._previous_version = "1"

    def read_header(self) -> None:
        """Read and process an ORBNUM file header.

        Defines the record_fixed_length attribute that provides the length of
        a record.

        :return: ORBNUM header line
        :rtype: str
        """
        header = []
        with open(self.path, "r") as o:

            if int(self._orbnum_type["header_start_line"]) > 1:
                for _i in range(int(self._orbnum_type["header_start_line"]) - 1):
                    o.readline()

            header.append(o.readline())
            header.append(o.readline())

        #
        # Perform a minimal check to determine if the orbnum file has
        # the appropriate header. Include the old ORBNUM utility header format
        # for Descending and Ascending node events (Odyssey).
        #
        if ("Event" not in header[0]) and ("Node" not in header[0]):
            handle_npb_error(
                f"The header of the orbnum file {self.name} is not as expected.",
                setup=self.setup,
            )

        if "===" not in header[1]:
            handle_npb_error(
                f"The header of the orbnum file {self.name} is not as expected.",
                setup=self.setup,
            )

        #
        # Set the fixed record length from the header.
        #
        self.record_fixed_length = len(header[1])

        return header

    def get_header_length(self) -> str:
        """Read an OrbNum file and return the length of the header in bytes.

        :return: OrbNum file header length
        """
        header_length = 0
        with open(self.path, "r", newline="") as o:
            lines = 0
            header_start = int(self._orbnum_type["header_start_line"])
            for line in o:
                lines += 1
                if lines < header_start + 2:
                    header_length += utf8len(line)
                else:
                    break

        return header_length

    def get_sample_record(self) -> str:
        """Read an OrbNum file and return one record sample.

        This sample (one data line) will be used to determine the format of
        each parameter of the OrbNum file. The sample is re-processed in such a
        way that it contains no spaces for the UTC dates.

        :return: sample record line
        """
        sample_record = ""
        with open(self.path, "r") as o:
            lines = 0
            header_start = int(self._orbnum_type["header_start_line"])
            for line in o:
                lines += 1
                if lines > header_start + 1:
                    #
                    # The original condition was: ``if line.strip():``
                    # But some orbnum files have records that only have the
                    # orbit number and nothing else. E.g.:
                    #
                    # header[0]        No.     Event UTC PERI
                    # header[1]      =====  ====================
                    # skip               2
                    # sample_record      3  1976 JUN 22 18:07:09
                    #
                    if len(line.strip()) > 5:
                        sample_record = line
                        break

        if not sample_record:
            handle_npb_error("The orbnum file has no records.", setup=self.setup)

        sample_record = self.utc_blanks_to_dashes(sample_record)

        return sample_record

    @staticmethod
    def utc_blanks_to_dashes(sample_record: str) -> str:
        """Reformat UTC strings in the OrbNum file.

        Re-process the UTC string fields of an OrbNum sample row
        to remove blank spaces.

        :param sample_record: sample row with UTC string with blank spaces
        :return: sample row with UTC string with dashes
        """
        matches = re.finditer(
            r"\d{4} [A-Z]{3} \d{2} \d{2}:\d{2}:\d{2}",
            sample_record)

        for match in matches:
            #
            # Turn the string to a list to modify it.
            #
            sample_record = sample_record.replace(
                match.group(0), match.group(0).replace(" ", "-")
            )

        return sample_record

    def read_records(self) -> str:
        """Read and interpret the records of an OrbNum file.

        Read an OrbNum file and set the number of records attribute,
        the length of the records attribute, determine which lines have blank
        records and, perform simple checks of the records.

        :return: number of records of OrbNum file
        """
        blank_records = []

        with open(self.path, "r") as o:
            previous_orbit_number = None
            records = 0
            lines = 0
            header_start = int(self._orbnum_type["header_start_line"])
            for line in o:
                lines += 1
                if lines > header_start + 1:
                    orbit_number = int(line.split()[0])
                    records_length = utf8len(line)

                    #
                    # Checks are performed from the first record.
                    #
                    if lines > header_start:
                        if previous_orbit_number and (
                            orbit_number - previous_orbit_number != 1
                        ):
                            logging.warning(
                                f"-- Orbit number "
                                f"{previous_orbit_number} record "
                                f"is followed by {orbit_number}."
                            )
                        if not line.strip():
                            handle_npb_error(
                                f"Orbnum record number {line} is blank.",
                                setup=self.setup,
                            )
                        elif (
                            line.strip() and records_length != self.record_fixed_length
                        ):
                            logging.warning(
                                f"-- Orbit number {orbit_number} "
                                f"record has an incorrect length,"
                                f" the record will be expanded "
                                f"to cover the adequate fixed "
                                f"length."
                            )

                            blank_records.append(str(orbit_number))

                    if line.strip():
                        records += 1

                    previous_orbit_number = orbit_number

        #
        # If there are blank records, we need to add blank spaces and
        # generate a new version of the orbnum file.
        #
        if blank_records:

            #
            # Generate the name for the new orbnum file. This is the only
            # place where the version of the previous orbnum file is used.
            #
            matches = re.search(r"_v\d*\.", self.name, flags=re.I)

            if not matches:

                #
                # If the name does not have an explicit version, the version
                # is set to 2.
                #
                original_name = self.name
                name = self.name.split(".")[0] + "_v2." + self.name.split(".")[-1]
                path = f"{os.sep}".join(self.path.split(os.sep)[:-1]) + os.sep + name

                logging.warning(
                    f"-- ORBNUM file name updated with explicit "
                    f"version number to: {name}"
                )

            else:
                version = re.findall(r"\d+", matches.group(0))
                version_number = "".join(version)

                new_version_number = int(version_number) + 1
                leading_zeros = len(version_number) - len(str(new_version_number))
                new_version_number = str(new_version_number).zfill(leading_zeros)

                new_version = matches.group(0).replace(
                    version_number, new_version_number
                )

                original_name = matches.string
                name = self.name.replace(matches.group(0), new_version)
                path = self.path.replace(matches.group(0), new_version)

                logging.warning(f"-- Orbnum name updated to: {name}")

            #
            # The updated name needs to be propagated to the kernel
            # list.
            #
            for index, item in enumerate(self.kernels_collection.list.kernel_list):
                if item == original_name:
                    self.kernels_collection.list.kernel_list[index] = name

            #
            # Following the name, write the new file and remove the
            # provided orbnum file.
            #
            with open(self.path, "r") as o:
                with open(path, "w") as n:
                    i = 1
                    for line in o:
                        if i > int(header_start) + 1:
                            orbit_number = int(line.split()[0])
                            if str(orbit_number) in blank_records:
                                #
                                # Careful, Python will change the EOL to
                                # Line Feed when reading the file.
                                #
                                line = line.split("\n")[0]
                                n.write(
                                    line
                                    + " " * (self.record_fixed_length - len(line) - 1)
                                    + self.setup.eol
                                )
                            else:
                                n.write(line.split("\n")[0] + self.setup.eol)
                        else:
                            n.write(line.split("\n")[0] + self.setup.eol)
                        i += 1
                os.remove(self.path)

            self.path = path
            self.name = name

        self.blank_records = blank_records
        self.records = records

        return records

    def set_event_detection_key(self, header: List[str]) -> None:
        """Obtain the OrbNum event detection key.

        The event detection key is a string identifying which geometric event
        signifies the start of an orbit. The possible events are:

           ``APO``    signals a search for apoapsis

           ``PERI``   signals a search for periapsis

           ``A-NODE`` signals a search for passage through
           the ascending node

           ``D-NODE`` signals a search for passage through
           the descending node

           ``MINLAT`` signals a search for the time of
           minimum planetocentric latitude

           ``MAXLAT`` signals a search for the time of
           maximum planetocentric latitude

           ``MINZ``   signals a search for the time of the
           minimum value of the Z (Cartesian) coordinate

           ``MAXZ``   signals a search for the time of the
           maximum value of the Z (Cartesian) coordinate

        :param header: OrbNum file header line
        """
        events = ["APO", "PERI", "A-NODE", "D-NODE", "MINLAT", "MAXLAT", "MINZ", "MAXZ"]
        for event in events:
            if header[0].count(event) >= 2:
                self._event_detection_key = event
                break

        #
        # For orbnum files generated with older versions of the ORBNUM
        # utility, the event columns have a different format. For example,
        # for Mars Odyssey (m01_ext64.nrb):
        #
        #  No.      Desc-Node UTC         Node SCLK          Asc-Node UTC  ...
        # ===== ====================  ================  ====================
        # 82266 2020 JUL 01 01:24:31  4/1278034592.076  2020 JUL 01 02:23:12
        # 82267 2020 JUL 01 03:23:06  4/1278041706.241  2020 JUL 01 04:21:46
        # 82268 2020 JUL 01 05:21:38  4/1278048819.054  2020 JUL 01 06:20:18
        #
        if not hasattr(self, "_event_detection_key"):
            if ("Desc-Node" in header[0]) or ("Asc-Node" in header[0]):
                desc_node_index = header[0].index("Desc-Node")
                asc_node_index = header[0].index("Asc-Node")
                if asc_node_index < desc_node_index:
                    self._event_detection_key = "A-NODE"
                else:
                    self._event_detection_key = "D-NODE"

        if not hasattr(self, "_event_detection_key"):
            handle_npb_error("orbnum event detection key is incorrect.", setup=self.setup)

    # TODO: Is this method really needed?
    @staticmethod
    def event_mapping(event: str) -> str:
        """Maps the event keyword to the event name/description.

        :param event: OrbNum event key
        :return:      OrbNum event description
        """
        event_dict = {
            "APO": "apocenter",
            "PERI": "pericenter",
            "A-NODE": "passage through the ascending node",
            "D-NODE": "passage through the descending node",
            "MINLAT": "minimum planetocentric latitude",
            "MAXLAT": "maximum planetocentric latitude",
            "MINZ": "minimum value of the cartesian Z coordinate",
            "MAXZ": "maximum value of the cartesian Z coordinate",
        }

        return event_dict[event]

    # TODO: Is this method really needed?
    @staticmethod
    def opposite_event_mapping(event: str) -> str:
        """Maps the event keyword to the opposite event keyword.

        :param event: OrbNum event key
        :return:      OrbNum opposite event keyword
        """
        opp_event_dict = {
            "APO": "PERI",
            "PERI": "APO",
            "A-NODE": "D-NODE",
            "D-NODE": "A-NODE",
            "MINLAT": "MAXLAT",
            "MAXLAT": "MINLAT",
            "MINZ": "MAXZ",
            "MAXZ": "MINZ",
        }

        return opp_event_dict[event]

    def get_params(self, header: List[str]) -> None:
        """Obtain the parameters present in the OrbNum file.

        Currently, there are 11 orbital parameters available:

           ``No.``          The orbit number of a descending node event.

           ``Event UTC``    The UTC time of that event.

           ``Event SCLK``    The SCLK time of the event.

           ``OP-Event UTC`` The UTC time of the opposite event.

           ``Sub Sol Lon``  Sub-solar planetodetic longitude at event
           time (DEGS).

           ``Sub Sol Lat``  Sub-solar planetodetic latitude at event
           time (DEGS).

           ``Sub SC Lon``   Sub-target planetodetic longitude (DEGS).

           ``Sub SC Lat``   Sub-target planetodetic latitude (DEGS).

           ``Alt``          Altitude of the target above the observer
           body at event time (KM).

           ``Inc``          Inclination of the vehicle orbit plane at
           event time (DEGS).

           ``Ecc``          Eccentricity of the target orbit about
           the primary body at event time (DEGS),

           ``Lon Node``     Longitude of the ascending node of the
           orbit plane at event time (DEGS).

           ``Arg Per``      Argument of periapsis of the orbit plane at
           event time (DEGS).

           ``Sol Dist``     Solar distance from target at event
           time (KM).

           ``Semi Axis``   Semi-major axis of the target's orbit at
           event time (KM).

        :param header: ORBNUM file header line
        """
        parameters = []
        params = [
            "No.",
            "Event UTC",
            "Desc-Node UTC",
            "Event SCLK",
            "Node SCLK",
            "OP-Event UTC",
            "Asc-Node UTC",
            "SolLon",
            "SolLat",
            "SC Lon",
            "SC Lat",
            "Alt",
            "Inc",
            "Ecc",
            "LonNode",
            "Arg Per",
            "Sol Dist",
            "Semi Axis",
        ]
        for param in params:
            if param in header[0]:
                parameters.append(param)

        self._params = parameters

    def set_params(self, header: List[str]) -> None:
        """Define the parameters' template dictionary.

        :param header: OrbNum file header line
        """
        # The orbit number, UTC date and angular parameters have fixed
        # lengths, which are provided in the parameters' template.
        # The length of the rest of the parameters depends on each orbnum
        # file and are obtained from the OrbNum file itself.
        #
        # For OrbNum files using IM previous to v1.7.0.0 the ``field_format``
        # values are:
        #
        #    Parameter      IM < 1.7.0.0  IM >= 1.7.0.0
        #    =============  ============  =============
        #    No.            I5            %5d
        #    Event UTC      A20           %20s
        #    Desc-Node UTC  A20           %20s
        #    Event SCLK     A?            %?s
        #    Node SCLK      A?            %?s
        #    OP-Event UTC   A20           %20s
        #    Asc-Node UTC   A20           %20s
        #    All the rest   F?.?          %?.?f
        #
        params_template = {
            "No.": {
                "location": "1",
                "type": "ASCII_Integer",
                "length": "5",
                "description": "Number that provides an incremental orbit "
                "count determined by the $EVENT event.",
            },
            "Event UTC": {
                "type": "ASCII_String",
                "location": "8",
                "length": "20",
                "description": "UTC time of the $EVENT event that "
                "signifies the start of an orbit.",
            },
            "Desc-Node UTC": {
                "type": "ASCII_String",
                "location": "8",
                "length": "20",
                "description": "UTC time of the $EVENT event that "
                "signifies the start of an orbit.",
            },
            "Event SCLK": {
                "type": "ASCII_String",
                "description": "SCLK time of the $EVENT event that "
                "signifies the start of an orbit.",
            },
            "Node SCLK": {
                "type": "ASCII_String",
                "description": "SCLK time of the $EVENT event that "
                "signifies the start of an orbit.",
            },
            "OP-Event UTC": {
                "type": "ASCII_String",
                "length": "20",
                "description": "UTC time of opposite event ($OPPEVENT).",
            },
            "Asc-Node UTC": {
                "type": "ASCII_String",
                "length": "20",
                "description": "UTC time of opposite event ($OPPEVENT).",
            },
            "SolLon": {
                "type": "ASCII_Real",
                "description": "Sub-solar planetodetic longitude at the "
                "$EVENT event time in the $FRAME.",
                "unit": "deg",
            },
            "SolLat": {
                "type": "ASCII_Real",
                "description": "Sub-solar planetodetic latitude at the "
                "$EVENT event time in the $FRAME.",
                "unit": "deg",
            },
            "SC Lon": {
                "type": "ASCII_Real",
                "description": "Sub-target planetodetic longitude at the "
                "$EVENT event time in the $FRAME.",
                "unit": "deg",
            },
            "SC Lat": {
                "type": "ASCII_Real",
                "description": "Sub-target planetodetic latitude at at the "
                "$EVENT event time in the $FRAME.",
                "unit": "deg",
            },
            "Alt": {
                "type": "ASCII_Real",
                "description": "Altitude of the target above the observer "
                "body at the $EVENT event time relative to"
                " the $TARGET ellipsoid.",
                "unit": "km",
            },
            "Inc": {
                "type": "ASCII_Real",
                "description": "Inclination of the vehicle orbit plane at "
                "event time.",
                "unit": "km",
            },
            "Ecc": {
                "type": "ASCII_Real",
                "description": "Eccentricity of the target orbit about "
                "the primary body at the $EVENT event time.",
                "unit": "deg",
            },
            "LonNode": {
                "type": "ASCII_Real",
                "description": "Longitude of the ascending node of the"
                " orbit plane at the $EVENT event time.",
                "unit": "deg",
            },
            "Arg Per": {
                "type": "ASCII_Real",
                "description": "Argument of periapsis of the orbit plane at "
                "the $EVENT event time.",
                "unit": "deg",
            },
            "Sol Dist": {
                "type": "ASCII_Real",
                "description": "Solar distance from target at the $EVENT "
                "event time.",
                "unit": "km",
            },
            "Semi Axis": {
                "type": "ASCII_Real",
                "description": "Semi-major axis of the target's orbit at"
                " the $EVENT event time.",
                "unit": "km",
            },
        }

        #
        # Define the complete list of parameters.
        #
        params = self._params

        sample_record = self._sample_record

        #
        # Iterate the parameters and generate a dictionary for each based on
        # the parameters' template dictionary.
        #
        # The parameters are first initialised. The orbnum header with two
        # re-processed records will look as follows:
        #
        # header[1]     No.     Event UTC PERI       Event SCLK PERI      ...
        # header[2]    =====  ====================  ====================  ...
        # param_record  1954  2015-OCT-01T01:33:57    2/0496935200.34677  ...
        #               1955  2015-OCT-01T06:06:54    2/0496951577.40847  ...
        #
        # The length of each parameter is based on the second header line.
        # Please note that what will be used is the maximum potential length
        # of each parameter.
        #
        number = 0
        location = 1
        length = 0
        params_dict = {}
        blankspace_iter = re.finditer(r"[ ]", header[1])

        for param in params:

            name = param
            #
            # Parameter location; offset with respect to the line start.
            # Use the length from the previous iteration and add the
            # blank spaces in between parameter columns.
            #
            # To find blank spaces we use a regular expression iterator.
            #
            if number > 0:
                blankspaces_loc = blankspace_iter.__next__().regs[0]
                blankspaces = blankspaces_loc[1] - blankspaces_loc[0] + 1
                location += int(length) + blankspaces

            p_type = params_template[param]["type"]

            if "length" in params_template[param]:
                length = params_template[param]["length"]
                param_length = False
            else:
                #
                # Obtain the parameter length as the length of the table
                # separator from the header.
                #
                length = str(len(header[1].split()[number]))
                #
                # If the parameter is a float we need to include the decimal
                # part.
                #
                if "ASCII_Real" in params_template[param]["type"]:
                    #
                    # We need to sort the number of decimals.
                    #
                    param_record = sample_record.split()[number]
                    param_length = str(len(param_record.split(".")[-1]))

                else:
                    param_length = False

            #
            # Write the format
            #
            if self.setup.information_model_float >= 1007000000.0:
                ascii_format = "%" + length
                if "ASCII_Real" in params_template[param]["type"]:
                    ascii_format += "." + param_length + "f"
                elif "ASCII_String" in params_template[param]["type"]:
                    ascii_format += "s"
                elif "ASCII_Integer" in params_template[param]["type"]:
                    ascii_format += "d"
                else:
                    handle_npb_error("Parameter type for ORBNUM file is incorrect.")
            else:
                if "ASCII_Real" in params_template[param]["type"]:
                    ascii_format = "F" + length + "." + param_length
                elif "ASCII_String" in params_template[param]["type"]:
                    ascii_format = "A" + length
                elif "ASCII_Integer" in params_template[param]["type"]:
                    ascii_format = "I" + length
                else:
                    handle_npb_error("Parameter type for ORBNUM file is incorrect.")

            #
            # Parameter number (column number)
            #
            number += 1

            #
            # Description. It can contain $EVENT, $TARGET and/or $FRAME. If
            # so is substituted by the appropriate value.
            #
            description = params_template[param]["description"]

            if "$EVENT" in description:
                event_desc = self.event_mapping(self._event_detection_key)
                description = description.replace("$EVENT", event_desc)

            if "$TARGET" in description:
                target = self.setup.target.title()
                description = description.replace("$TARGET", target)

            if "$FRAME" in description:
                frame_dict = self._orbnum_type["event_detection_frame"]
                frame = f"{frame_dict['description']} ({frame_dict['spice_name']})"
                description = description.replace("$FRAME", frame)

            if "$OPPEVENT" in description:
                #
                # For the opposite event correct the field description as
                # well.
                #
                oppevent = self.opposite_event_mapping(self._event_detection_key)
                oppevent_desc = self.event_mapping(oppevent)
                description = description.replace("$OPPEVENT", oppevent_desc)

            #
            # Add event type in names.
            #
            if (name == "Event UTC") or (name == "Event SCLK"):
                name += " " + self._event_detection_key
            if name == "OP-Event UTC":
                name += " " + oppevent

            #
            # If the parameter has a unit, get it from the template.
            #
            if "unit" in params_template[param]:
                unit = params_template[param]["unit"]
            else:
                unit = None

            #
            # build the dictionary for the parameter and add it to the
            # parameter list
            #
            params_dict[param] = {
                "name": name,
                "number": number,
                "location": location,
                "type": p_type,
                "length": length,
                "format": ascii_format,
                "description": description,
                "unit": unit,
            }

        self.params = params_dict

    def get_description(self) -> str:
        """Write the OrbNum table character description.

        Write the OrbNum product description information based on the orbit
        determination event and the PCK kernel used.

        :return: OrbNum file description for label.
        """
        event_mapping = {
            "PERI": "periapsis",
            "APO": "apoapsis",
            "A-NODE": "ascending node",
            "D-NODE": "descending node",
            "MINLAT": "minimum planetocentric latitude",
            "MAXLAT": "maximum planetocentric latitude",
            "MINZ": "minimum value of Z (cartesian) coordinate",
            "MAXZ": "maximum value of Z (cartesian) coordinate",
        }

        event = event_mapping[self._event_detection_key]

        pck_mapping = self._orbnum_type["pck"]
        report = f"{pck_mapping['description']} ({pck_mapping['kernel_name']})"

        description = (
            f"SPICE text orbit number file containing orbit "
            f"numbers and start times for orbits numbered by/"
            f"starting at {event} events, and sets of selected "
            f"geometric parameters at the orbit start times. "
            f"SPICE text PCK file constants from the {report}."
        )
        if hasattr(self, "_previous_orbnum"):
            if self._previous_orbnum:
                description += (
                    f" This file supersedes the following orbit "
                    f"number file: {self._previous_orbnum}."
                )

        description += f" Created by {self._orbnum_type['author']}."

        return description

    def table_character_description(self) -> str:
        """Write the OrbNum table character description.

        Write the OrbNum table character description information
        determination event and the PCK kernel used.
        """
        description = ""

        if self.blank_records:
            number_of_records = len(self.blank_records)
            if int(number_of_records) == 1:
                plural = ""
            else:
                plural = "s"

            description += (
                f"Since the SPK file(s) used to "
                f"generate this orbit number file did not provide "
                f"continuous coverage, the file contains "
                f"{number_of_records} record{plural} that only provide the "
                f"orbit number in the first field (No.) with all other "
                f"fields set to blank spaces."
            )

        return description

    def coverage(self) -> None:
        """Determine the coverage of the OrbNum file.

        The coverage of the OrbNum file can be determined in three different
        ways:

           *  If there is a one to one correspondence with an SPK
              file, the SPK file can be provided with the ``<kernel>``
              tag. The tag can be a path to a specific kernel that
              does not have to be part of the increment, a pattern
              of a kernel present in the increment or a pattern of
              a kernel present in the final directory of the archive.

           *  If there is a quasi one to one correspondence with an
              SPK file with a given cutoff time prior to the end
              of the SPK file, the SPK file can be provided with the
              ``<kernel>`` tag. The tag can be a path to a specific kernel
              that does not have to be part of the increment, a pattern
              of a kernel present in the increment or a pattern of
              a kernel present in the final directory of the archive.
              Currently, the only cutoff pattern available is the
              boundary of the previous day of the SPK coverage stop
              time.

           *  A user can provide a look-up table with this file, as follows::

                <lookup_table>
                   <file name="maven_orb_rec_210101_210401_v1.orb">
                      <start>2021-01-01T00:00:00.000Z</start>
                      <finish>2021-04-01T01:00:00.000Z</finish>
                   </file>
                </lookup_table>

              Note that in this particular case the first three and
              last three lines of the orbnum files would have provided::

                   Event UTC PERI
                   ====================
                   2021 JAN 01 00:14:15
                   2021 JAN 01 03:50:43
                   2021 JAN 01 07:27:09
                   (...)
                   2021 MAR 31 15:00:05
                   2021 MAR 31 18:36:29
                   2021 MAR 31 22:12:54

           *  If nothing is provided NPB will provide the coverage based on
              the event time of the first orbit and the opposite event time
              of the last orbit.
        """
        if "coverage" in self._orbnum_type:
            coverage_source = self._orbnum_type["coverage"]
        else:
            coverage_source = ""

        coverage_found = False

        if "kernel" in coverage_source:
            if coverage_source["kernel"]:
                coverage_kernel = coverage_source["kernel"]["#text"]
                #
                # Search the kernel that provides coverage, Note that
                # this kernel is either
                #
                #   -- present in the increment
                #   -- in the previous increment
                #   -- provided by the user
                #
                # The kernel can be a pattern defining multiple kernels or
                # a name. If the kernel provided contains a pattern it will be
                # useful to determine the coverage of multiple orbnum files
                # provided in the plan.
                #
                cov_patn = coverage_kernel.split(os.sep)[-1]

                #
                # Start checking the path provided in the configuration file.
                #
                cov_path = os.sep.join(coverage_kernel.split(os.sep)[:-1])

                try:
                    cov_kers = [
                        x for x in os.listdir(cov_path) if re.fullmatch(cov_patn, x)
                    ]

                except BaseException:
                    cov_kers = []

                #
                # Check if the SPK kernel is present in the increment.
                #
                if not cov_kers:
                    cov_path = f"{self.setup.staging_directory}/spice_kernels/spk"

                    try:
                        cov_kers = [
                            x for x in os.listdir(cov_path) if re.fullmatch(cov_patn, x)
                        ]
                    except BaseException:
                        cov_kers = []

                    #
                    # Check if the SPK kernel is present in the bundle
                    # directory.
                    #
                    if not cov_kers:
                        cov_path = f"{self.setup.bundle_directory}/spice_kernels/spk"
                        try:
                            cov_kers = [
                                x
                                for x in os.listdir(cov_path)
                                if re.fullmatch(cov_patn, x)
                            ]
                        except BaseException:
                            cov_kers = []

                if cov_kers:
                    coverage_found = True

                #
                # If there is only one coverage kernel this is the one that
                # will be used.
                #
                if len(cov_kers) == 1 and coverage_found:
                    coverage_kernel = cov_path + os.sep + cov_kers[0]
                    logging.info(f"-- Coverage determined by {coverage_kernel}.")
                #
                # If there are more, the only possibility is that the orbnum
                # filename and the SPK filename, both without extensions, match.
                #
                elif coverage_found:
                    for kernel in cov_kers:
                        kername = kernel.split(os.sep)[-1]
                        if kername.split(".")[0] == self.name.split(".")[0]:
                            coverage_kernel = cov_path + os.sep + kernel
                            logging.info(
                                f"-- Coverage determined by {coverage_kernel}."
                            )

                if os.path.isfile(coverage_kernel):
                    #
                    # Kernel provided by the user and directly available.
                    #
                    (start_time, stop_time) = spk_coverage(
                        coverage_kernel,
                        main_name=self.setup.spice_name,
                        date_format="maklabel",
                    )

                    #
                    # If the XML tag has a cutoff attribute, apply the cutoff.
                    #
                    if coverage_source["kernel"]["@cutoff"] == "True":
                        stop_time = datetime.datetime.strptime(
                            stop_time, "%Y-%m-%dT%H:%M:%SZ"
                        )
                        stop_time = stop_time.strftime("%Y-%m-%dT00:00:00Z")
                    elif coverage_source["kernel"]["@cutoff"] == "False":
                        pass
                    else:
                        logging.error(
                            "-- cutoff value of <kernel>"
                            "configuration item is not set to "
                            'a parseable value: "True" or "False".'
                        )
                    coverage_found = True
                else:
                    coverage_found = False
            else:
                coverage_found = False
        elif "lookup_table" in coverage_source:
            if coverage_source["lookup_table"]:
                if coverage_found:
                    logging.warning(
                        "-- Orbnum file lookup table cov. found "
                        "but cov. already provided by SPK file."
                    )

                table_files = coverage_source["lookup_table"]["file"]
                if not isinstance(table_files, list):
                    table_files = [table_files]
                for file in table_files:
                    if file["@name"] == self.name:
                        start_time = file["start"]
                        stop_time = file["finish"]
                        coverage_found = True
                        logging.info(
                            f"-- Coverage determined by "
                            f'{file["@name"]} from lookup table.'
                        )
                        break
            else:
                coverage_found = False

        if not coverage_found:
            #
            # Set the start and stop times to the first and last
            # time-tags of the orbnum file.
            #
            start_time = self._sample_record.split()[1]
            start = parse_date(start_time)
            start_time = start.strftime("%Y-%m-%dT%H:%M:%SZ")

            #
            # Read the orbnum file in binary mode in order to start
            # from the end of the file.
            #
            with open(self.path, "rb") as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
                #
                # Replace the spaces in the UTC strings for dashes in order
                # to be able to split the file with blank spaces.
                #
            last_line = self.utc_blanks_to_dashes(last_line)
            #
            # If the opposite event is outside of the coverage of the SPK file
            # with which the orbnum has been generated, there is no UTC time
            # or the opposite event, in such case we will use the UTC time
            # of the last event.
            #
            if "Unable to determine" in last_line:
                stop_time = last_line.split()[1]
            else:
                stop_time = last_line.split()[3]

            try:
                stop = parse_date(stop_time)
                stop_time = stop.strftime("%Y-%m-%dT%H:%M:%SZ")
            except BaseException:
                #
                # Exception to cope with orbnum files without all the ground
                # set of parameters.
                #
                stop_time = last_line.split()[1]
                stop = datetime.datetime.strptime(stop_time, "%Y-%b-%d-%H:%M:%S")
                stop_time = stop.strftime("%Y-%m-%dT%H:%M:%SZ")

            logging.warning("-- Coverage determined by ORBNUM file data.")

        self.start_time = start_time
        self.stop_time = stop_time
