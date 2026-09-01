"""Implementation of the PDS3 version of a label for SPICE kernel files.
"""
import logging
from pathlib import Path

import spiceypy

from .pds3_label import PDS3Label
from ..exceptions import NPBError
from ...utils import (
    ck_coverage,
    extract_comment,
    format_multiple_values,
    spice_exception_handler,
    type_to_pds3_type,
)


class SpiceKernelPDS3Label(PDS3Label):
    """Class to generate a PDS3 SPICE Kernel Label.

    :param product: SPICE Kernel product to be labeled
    """

    def __init__(self, product) -> None:
        """Constructor."""
        # The parameter used to be named "mission" even though it was
        # always the setup object; renamed to match PDSLabel.__init__'s
        # single-argument signature.
        super().__init__(product)

        self._template = str(Path(self.setup.templates_directory)
                             / "template_product_spice_kernel.lbl")

        self._label_fields["FILE_NAME"] = f'"{product.name}"'
        self._label_fields["INTERCHANGE_FORMAT"] = product.file_format
        self._label_fields["START_TIME"] = product.start_time.split("Z")[0]
        self._label_fields["STOP_TIME"] = product.stop_time.split("Z")[0]
        self._label_fields["KERNEL_TYPE_ID"] = product.type.upper()
        self._label_fields["KERNEL_TYPE"] = type_to_pds3_type(product.type.upper())
        self._label_fields["RECORD_TYPE"] = product.record_type
        self._label_fields["RECORD_BYTES"] = product.record_bytes
        self._label_fields["SPICE_KERNEL_DESCRIPTION"] = self.format_description(product.description)

        self.set_kernel_ids(product)
        self.set_sclk_times(product)

        # Field names here come from the mission's YAML config, not from
        # source code, so they can't be assigned individually by name.
        #
        # Values from template defaults first.
        #
        for item in self.setup.pds3_mission_template.items():
            if item[0] != "maklabel_options":
                maklabel_key = item[0]
                maklabel_val = item[1]
                self._label_fields[maklabel_key] = maklabel_val

        #
        # Values extracted from the mission template.
        #
        for option in product.maklabel_options:
            values = self.setup.pds3_mission_template["maklabel_options"][option]

            for item in values.items():
                maklabel_key = item[0]
                maklabel_val = item[1]

                maklabel_val = format_multiple_values(maklabel_val)

                self._label_fields[maklabel_key] = maklabel_val

        #
        # Remove the quotes from the target name and product version type.
        #
        if "TARGET_NAME" in self._label_fields:
            if '"' in self._label_fields["TARGET_NAME"]:
                self._label_fields["TARGET_NAME"] = self._label_fields["TARGET_NAME"].split('"')[1]
        if "PRODUCT_VERSION_TYPE" in self._label_fields:
            if '"' in self._label_fields["PRODUCT_VERSION_TYPE"]:
                self._label_fields["PRODUCT_VERSION_TYPE"] = self._label_fields["PRODUCT_VERSION_TYPE"].split('"')[1]
        if "PLATFORM_OR_MOUNTING_NAME" in self._label_fields:
            if (
                '"' in self._label_fields["PLATFORM_OR_MOUNTING_NAME"]
                and self._label_fields["PLATFORM_OR_MOUNTING_NAME"] != '"N/A"'
            ):
                self._label_fields["PLATFORM_OR_MOUNTING_NAME"] = self._label_fields[
                    "PLATFORM_OR_MOUNTING_NAME"
                ].split('"')[1]

        self.write_label()

        if product.record_type == "STREAM":
            self.insert_text_label()
        else:
            self.insert_binary_label()

        logging.info("")

    @spice_exception_handler
    def set_sclk_times(self, product, system="UTC"):
        """Calculates the SCLK times for PDS3 labels."""
        if product.type.upper() == "CK":
            spice_id = spiceypy.bodn2c(self.setup.spice_name)

            (start_ticks, stop_ticks) = ck_coverage(
                product.path, timsys="SCLK", system=system
            )

            sclk_start = spiceypy.scdecd(spice_id, start_ticks)
            sclk_stop = spiceypy.scdecd(spice_id, stop_ticks)
        else:
            sclk_start = "N/A"
            sclk_stop = "N/A"

        self._label_fields["SPACECRAFT_CLOCK_START_COUNT"] = f'"{sclk_start}"'
        self._label_fields["SPACECRAFT_CLOCK_STOP_COUNT"] = f'"{sclk_stop}"'

    def set_kernel_ids(self, product):
        """Set the SPICE Kernel ID field of the label."""
        if product.type.upper() == "CK":
            naif_instrument_id = product.ck_kernel_ids()
        elif product.type.upper() == "IK":
            naif_instrument_id = product.ik_kernel_ids()
        else:
            naif_instrument_id = '"N/A"'

        self._label_fields["NAIF_INSTRUMENT_ID"] = format_multiple_values(naif_instrument_id)

    def format_description(self, description):
        """Format the SPICE kernel description appropriately.

        The first line goes from character 33 to 78.
        Successive lines go from character  1 to 78.
        Last line has a blank space after the full stop.

        :return: Formatted label description
        :rtype: str
        """
        description = description.split()

        desc = ""
        line_len = 32
        for word in description:
            if line_len + len(word + " ") < 77:
                if not desc:
                    desc += '"' + word
                else:
                    desc += " " + word
                line_len += len(" " + word)
            else:
                desc += "\n"
                desc += word
                line_len = len(word)

        # Close the description value with a trailing space, closing quote,
        # and newline.
        desc += ' "\n'

        return desc

    def insert_text_label(self):
        """Insert or update a label in a text kernel.

        The routine inserts the label, after the first line containing the
        kernel architecture specification and removes extra empty lines at the
        end of the kernel file.
        """
        with open(self.name, "r", encoding='utf-8') as label:
            label_lines = label.readlines()

        with open(self.product.path, "r+", encoding='utf-8') as kernel:
            kernel_lines = kernel.readlines()

        with open(self.product.path, "w", encoding='utf-8') as kernel:

            if "KPL/" in kernel_lines[0]:
                kernel.write(kernel_lines[0])
            else:
                raise NPBError(
                    f"Kernel {self.product.name} does not have "
                    f"architecture spec as first line."
                )

            kernel.write("\n\\beginlabel\n")

            for line in label_lines:
                if line.strip() != "END":
                    kernel.write(line)

            kernel.write("\\endlabel")

            write_line = True

            kernel_lines[-1] += "\n"

            #
            # If the kernel does not have a label add an empty line.
            #
            label_in_kernel = False
            for line in kernel_lines:
                if "\\beginlabel" in line:
                    label_in_kernel = True
            if not label_in_kernel:
                kernel.write("\n")

            #
            # Remove empty lines at the end of the kernel, add a new line
            # character in the last line.
            #
            while kernel_lines and not kernel_lines[-1].strip():
                kernel_lines.pop()

            #
            # Add kernel list to kernel.
            #
            for line in kernel_lines:
                if "\\beginlabel" in line:
                    write_line = False
                    logging.info("-- Updating label in kernel.")

                if write_line:
                    if line != kernel_lines[0]:
                        kernel.write(line.rstrip() + "\n")

                if "\\endlabel" in line:
                    write_line = True

        logging.info("-- Label inserted to text kernel.")

    @spice_exception_handler
    def insert_binary_label(self):
        """Insert or update a label in a binary kernel.

        The routine inserts the label in the kernel comment.
        """
        label_lines = []
        with open(self.name, "r", encoding='utf-8') as label:
            for line in label:
                if line.strip() != "END":
                    label_lines.append(line.rstrip())

        # Kept outside the try: if dafopw itself fails, there is no handle
        # yet to close.
        handle = spiceypy.dafopw(self.product.path)

        try:
            #
            # Extract comment from the kernel.
            #
            commnt = extract_comment(self.product.path, handle=handle)

            #
            # Remove the first N blank lines.
            #
            j = 0
            for line in commnt:
                if line.strip():
                    break
                j += 1
            if j > 0:
                commnt = commnt[j:]

            #
            # Add a blank character in each empty line.
            #
            for i, line in enumerate(commnt):
                if not line:
                    commnt[i] = " "

            #
            # Add or replace label to comment list.
            #
            new_commnt = ["\\beginlabel"] + label_lines + ["\\endlabel"] + 2 * [" "]

            if "\\endlabel" in commnt:
                index = commnt.index("\\endlabel")
                commnt = commnt[index + 1 :]

            new_commnt += commnt

            #
            # Delete comment from the kernel.
            #
            spiceypy.dafdc(handle)

            #
            # Insert updated comment to kernel.
            #
            spiceypy.dafac(handle, new_commnt)

        finally:
            # Runs even if extract_comment, dafdc, or dafac raises, so the
            # handle is never left open.
            spiceypy.dafcls(handle)

        logging.info("-- Label inserted to binary kernel.")
