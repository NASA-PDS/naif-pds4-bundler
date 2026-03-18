"""Implementation of the PDS4 version of a label for Orbit Number (OrbNum)
files.
"""
from .label import PDSLabel


class OrbnumFilePDS4Label(PDSLabel):
    """PDS Label child class to generate a PDS4 Orbit Number File Label.

    :param setup: NPB execution Setup object
    :type setup: object
    :param product: ORBNUM product to label
    :type product: object
    """

    def __init__(self, setup: object, product: object) -> object:
        """Constructor."""
        PDSLabel.__init__(self, setup, product)

        self.template = f"{setup.templates_directory}/template_product_orbnum_table.xml"

        #
        # Fields from orbnum object.
        #
        self.FILE_NAME = product.name
        self.PRODUCT_LID = self.product.lid
        self.PRODUCT_VID = self.product.vid
        self.FILE_FORMAT = "Character"
        self.START_TIME = product.start_time
        self.STOP_TIME = product.stop_time
        self.DESCRIPTION = product.description
        self.HEADER_LENGTH = str(product.header_length)
        self.TABLE_CHARACTER_DESCRIPTION = product.table_char_description

        #
        # The orbnum table data starts one byte after the header section.
        #
        self.TABLE_OFFSET = str(product.header_length)
        self.TABLE_RECORDS = str(product.records)

        #
        # The ORBNUM utility produces an information ground set regardless
        # of the parameters listed in ORBIT_PARAMS. This set consists of 4
        # parameters.
        #
        self.NUMBER_OF_FIELDS = str(len(product.params.keys()))
        if self.END_OF_LINE == "Carriage-Return Line-Feed":
            eol_length = 1
        else:
            eol_length = 0
        self.FIELDS_LENGTH = str(product.record_fixed_length + eol_length)
        self.FIELDS = self.get_table_character_fields()

        if self.TABLE_CHARACTER_DESCRIPTION:
            self.TABLE_CHARACTER_DESCRIPTION = self.get_table_character_description()

        self.name = product.name.split(".")[0] + ".xml"

        self.write_label()

    def get_table_character_fields(self):
        """Get the Table Character fields.

        :return: Table Character fields
        :rytpe: str
        """
        fields = ""
        for param in self.product.params.values():
            field = self.field_template(
                param["name"],
                param["number"],
                param["location"],
                param["type"],
                param["length"],
                param["format"],
                param["description"],
                param["unit"],
                self.product.blank_records,
            )
            fields += field

        return fields

    def get_table_character_description(self):
        """Get The description of the Table Character.

        :return: Table Character description
        :rytpe: str
        """
        description = (
            f"{self.setup.eol_pds4}{' ' * 6 * self.setup.xml_tab}<description>"
            f"{self.product.table_char_description}"
            f"</description>{self.setup.eol_pds4}"
        )

        return description

    def field_template(
        self, name, number, location, type, length, format, description, unit, blanks
    ):
        """For a label provide all the parameters required for an ORBNUM field character.

        :param name: Name field
        :type name: str
        :param number: Number field
        :type number: str
        :param location: Location field
        :type location: str
        :param type: Type field
        :type type: str
        :param length: Length field
        :type length: str
        :param format: Format field
        :type format: str
        :param description: Description field
        :type description: str
        :param unit: Unit field
        :type unit: str
        :param blanks: Blank space missing constant indication
        :type blanks: str
        :return: Field Character for ORBNUM PDS4 label
        :rtype: str
        """
        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        field = (
            f'{" " * (4 * tab)}<Field_Character>{eol}'
            f'{" " * (4 * tab + 1 * tab)}<name>{name}</name>{eol}'
            f'{" " * (4 * tab + 1 * tab)}<field_number>{number}</field_number>{eol}'
            f'{" " * (4 * tab + 1 * tab)}<field_location unit="byte">{location}'
            f"</field_location>{eol}"
            f'{" " * (4 * tab + 1 * tab)}<data_type>{type}</data_type>{eol}'
            f'{" " * (4 * tab + 1 * tab)}<field_length unit="byte">{length}'
            f"</field_length>{eol}"
            f'{" " * (4 * tab + 1 * tab)}<field_format>{format}</field_format>{eol}'
        )
        if unit:
            field += f'{" " * (4 * tab + 1 * tab)}<unit>{unit}</unit>{eol}'
        field += (
            f'{" " * (4 * tab + 1 * tab)}<description>{description}</description>{eol}'
        )
        if blanks and name != "No.":
            field += (
                f'{" " * (4 * tab + 1 * tab)}<Special_Constants>{eol}'
                f'{" " * (4 * tab + 2 * tab)}<missing_constant>blank space'
                f"</missing_constant>{eol}"
                f'{" " * (4 * tab + 1 * tab)}</Special_Constants>{eol}'
            )
        field += f'{" " * (4 * tab)}</Field_Character>{eol}'

        return field
