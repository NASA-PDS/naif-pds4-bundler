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

    def get_mission_reference_type(self):
        """Get the mission reference type.

        :return: Mission_Reference_Type value for PDS4 label; the default
                 for any PDS4 label that does not override this.
        :rtype: str
        """
        return "data_to_investigation"

    def get_target_reference_type(self):
        """Get the target reference type.

        :return: Target_Reference_Type value for PDS4 label; the default
                 for any PDS4 label that does not override this.
        :rtype: str
        """
        return "data_to_target"

    def get_missions(self) -> str:
        """Get the label mission from the context products.

        :return: List of missions to be included in the label
        """
        miss = self.missions

        if not isinstance(miss, list):
            miss = [miss]

        mis_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab
        for mis in miss:
            if mis:
                mis_name = mis
                mission_lid, mission_type = None, None
                for product in context_products:
                    if product["name"][0] == mis_name and (
                        product["type"][0] == "Mission"
                        or product["type"][0] == "Other Investigation"
                    ):
                        mission_lid = product["lidvid"].split("::")[0]
                        mission_type = product["type"][0]

                if not mission_lid:
                    handle_npb_error(
                        f"LID has not been obtained for mission {mis}.",
                        setup=self.setup,
                    )

                mis_list_for_label += (
                    f"{' ' * 2 * tab}<Investigation_Area>{eol}"
                    + f"{' ' * 3 * tab}<name>{mis_name}</name>{eol}"
                    + f"{' ' * 3 * tab}<type>{mission_type}</type>{eol}"
                    + f"{' ' * 3 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 4 * tab}<lid_reference>{mission_lid}"
                    f"</lid_reference>{eol}" + f"{' ' * 4 * tab}<reference_type>"
                    f"{self.get_mission_reference_type()}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2 * tab}</Investigation_Area>{eol}"
                )
        if not mis_list_for_label:
            handle_npb_error(
                f"{self.product.name} missions not defined.", setup=self.setup
            )
        mis_list_for_label = mis_list_for_label.rstrip() + eol

        return mis_list_for_label

    def get_observers(self) -> str:
        """Get the label observers from the context products.

        :return: List of Observers to be included in the label
        """
        obs = self.observers
        if not isinstance(obs, list):
            obs = [obs]

        obs_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        for ob in obs:
            if ob:
                ob_lid, ob_type = None, None
                ob_name = ob.split(",")[0]
                for product in context_products:
                    if product["name"][0] == ob_name and (
                        product["type"][0] == "Spacecraft"
                        or product["type"][0] == "Rover"
                        or product["type"][0] == "Lander"
                        or product["type"][0] == "Host"
                    ):
                        ob_lid = product["lidvid"].split("::")[0]
                        ob_type = product["type"][0]

                if not ob_lid:
                    handle_npb_error(
                        f"LID has not been obtained for observer {ob}.",
                        setup=self.setup,
                    )

                obs_list_for_label += (
                    f"{' ' * 3 * tab}<Observing_System_Component>{eol}"
                    + f"{' ' * (3+1) * tab}<name>{ob_name}</name>{eol}"
                    + f"{' ' * (3+1) * tab}<type>{ob_type}</type>{eol}"
                    + f"{' ' * (3+1) * tab}<Internal_Reference>{eol}"
                    + f"{' ' * (3 + 2) * tab}<lid_reference>{ob_lid}"
                    f"</lid_reference>{eol}"
                    + f"{' ' * (3 + 2) * tab}<reference_type>is_instrument_host"
                    f"</reference_type>{eol}"
                    + f"{' ' * (3+1) * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 3 * tab}</Observing_System_Component>{eol}"
                )

        if not obs_list_for_label:
            handle_npb_error(
                f"{self.product.name} observers not defined.", setup=self.setup
            )
        obs_list_for_label = obs_list_for_label.rstrip() + eol

        return obs_list_for_label

    def get_targets(self) -> str:
        """Get the label targets from the context products.

        :return: List of Targets to be included in the label
        """
        tars = self.targets
        if not isinstance(tars, list):
            tars = [tars]

        tar_list_for_label = ""

        try:
            context_products = self.product.collection.bundle.context_products
        except BaseException:
            context_products = self.product.bundle.context_products

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        for tar in tars:
            if tar:
                target_name = tar
                target_lid, target_type = None, None
                for product in context_products:
                    if product["name"][0].upper() == target_name.upper():
                        target_lid = product["lidvid"].split("::")[0]
                        target_type = product["type"][0].capitalize()

                tar_list_for_label += (
                    f"{' ' * 2 * tab}<Target_Identification>{eol}"
                    + f"{' ' * 3 * tab}<name>{target_name}</name>{eol}"
                    + f"{' ' * 3 * tab}<type>{target_type}</type>{eol}"
                    + f"{' ' * 3 * tab}<Internal_Reference>{eol}"
                    + f"{' ' * 4 * tab}<lid_reference>{target_lid}"
                    f"</lid_reference>{eol}" + f"{' ' * 4 * tab}<reference_type>"
                    f"{self.get_target_reference_type()}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2 * tab}</Target_Identification>{eol}"
                )

        if not tar_list_for_label:
            handle_npb_error(f"{self.product.name} targets not defined.", setup=self.setup)
        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label
