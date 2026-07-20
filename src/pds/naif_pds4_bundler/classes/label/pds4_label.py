"""PDS4 version-specific base class for PDS labels."""

from .label import PDSLabel
from ...pipeline.runtime import handle_npb_error


class PDS4Label(PDSLabel):
    """Version-specific base class for PDS4 labels.

    Adds the PDS4-only fields that used to be gated behind
    ``if setup.pds_version == "4":`` checks in ``PDSLabel``.
    """

    def __init__(self, setup, product) -> None:
        """Constructor."""
        super().__init__(setup, product)

        try:
            context_products = product.collection.bundle.context_products
            if not context_products:
                raise Exception("No context products from bundle in collection")
        except BaseException:
            context_products = product.bundle.context_products

        self.XML_MODEL = setup.xml_model
        self.SCHEMA_LOCATION = setup.schema_location
        self.INFORMATION_MODEL_VERSION = setup.information_model

        #
        # Needs to be built for several Missions.
        #
        if hasattr(setup, "secondary_missions"):
            if len(setup.secondary_missions) == 1:
                missions_text = (
                    f"{setup.mission_name} and {setup.secondary_missions[0]}"
                )
            else:
                missions_text = f"{setup.mission_name}, "
                for i, sm_name in enumerate(setup.secondary_missions):
                    if i == len(setup.secondary_missions) - 1:
                        missions_text += f"and {sm_name}"
                    else:
                        missions_text += f"{sm_name}, "

            self.PDS4_MISSION_NAME = f"{missions_text}"
        else:
            self.PDS4_MISSION_NAME = f"{setup.mission_name}"

        #
        # Needs to be built for several observers.
        #
        if hasattr(setup, "secondary_observers"):
            if len(setup.secondary_observers) == 1:
                observers_text = (
                    f"{setup.observer} and {setup.secondary_observers[0]}"
                )
            else:
                observers_text = f"{setup.observer}, "
                for i, so_name in enumerate(setup.secondary_observers):
                    if i == len(setup.secondary_observers) - 1:
                        observers_text += f"and {so_name}"
                    else:
                        observers_text += f"{so_name}, "

            self.PDS4_OBSERVER_NAME = f"{observers_text} spacecraft and their"
        else:
            self.PDS4_OBSERVER_NAME = f"{setup.observer} spacecraft and its"

        self.END_OF_LINE_PDS4 = "Carriage-Return Line-Feed"
        if setup.end_of_line == "CRLF":
            self.END_OF_LINE = "Carriage-Return Line-Feed"
        elif setup.end_of_line == "LF":
            self.END_OF_LINE = "Line-Feed"
        else:
            handle_npb_error(
                "End of Line provided via configuration is not CRLF nor LF.",
                setup=self.setup,
            )

        self.BUNDLE_DESCRIPTION_LID = f"{setup.logical_identifier}:document:spiceds"

        self.MISSIONS = self.get_missions()
        self.OBSERVERS = self.get_observers()
        self.TARGETS = self.get_targets()

    @property
    def _label_extension(self) -> str:
        """File extension used for PDS4 labels."""
        return ".xml"

    @property
    def _eol(self) -> str:
        """End-of-line convention used for PDS4 labels."""
        return self.setup.eol_pds4
