"""Implementation of the PDS3 version of a label for SPICE kernel files.
"""
from pathlib import Path

import spiceypy

from .pds3_label import PDS3Label
from ...utils import (
    ck_coverage,
    format_multiple_values,
    spice_exception_handler,
    type_to_pds3_type,
)


class SpiceKernelPDS3Label(PDS3Label):
    """Class to generate a PDS3 SPICE Kernel Label.

    :param product: SPICE Kernel product to be labeled
    """

    # write_label() does not emit a trailing blank log line for this class.
    _trailing_blank_log = False

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
        if ("TARGET_NAME" in self._label_fields
                and  '"' in self._label_fields["TARGET_NAME"]):
            self._label_fields["TARGET_NAME"] = self._label_fields["TARGET_NAME"].split('"')[1]

        if ("PRODUCT_VERSION_TYPE" in self._label_fields
                and '"' in self._label_fields["PRODUCT_VERSION_TYPE"]):
            self._label_fields["PRODUCT_VERSION_TYPE"] = self._label_fields["PRODUCT_VERSION_TYPE"].split('"')[1]

        if ("PLATFORM_OR_MOUNTING_NAME" in self._label_fields
            and '"' in self._label_fields["PLATFORM_OR_MOUNTING_NAME"]
                and self._label_fields["PLATFORM_OR_MOUNTING_NAME"] != '"N/A"'):
            self._label_fields["PLATFORM_OR_MOUNTING_NAME"] = self._label_fields[
                "PLATFORM_OR_MOUNTING_NAME"].split('"')[1]

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
