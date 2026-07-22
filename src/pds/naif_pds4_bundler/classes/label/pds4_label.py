"""PDS4 version-specific base class for PDS labels."""

from .label import PDSLabel
from ...pipeline.runtime import handle_npb_error


class PDS4Label(PDSLabel):
    """Version-specific base class for PDS4 labels.

    Adds the PDS4-only fields that used to be gated behind
    ``if setup.pds_version == "4":`` checks in ``PDSLabel``.
    """

    # File extension used for PDS4 labels.
    _label_extension = ".xml"

    # Default Mission/Target_Reference_Type for any PDS4 label that does
    # not override them.
    _mission_reference_type = "data_to_investigation"
    _target_reference_type = "data_to_target"

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
    def _eol(self) -> str:
        """End-of-line convention used for PDS4 labels."""
        return self.setup.eol_pds4

    def _resolve_context_products(self):
        """Resolve the bundle context products used to label this product.

        Falls back to ``product.bundle.context_products`` when
        ``product.collection`` is unavailable. An empty (but present) list
        is returned as-is and does not trigger the fallback; only a lookup
        failure does.

        # TODO: PDS4Label.__init__ separately resolves and discards a
        #       context_products local with slightly different fallback
        #       logic (it also falls back on an empty list). That dead code
        #       and the discrepancy are tracked as a follow-up, not fixed
        #       here.

        :return: List of context product dictionaries
        """
        try:
            return self.product.collection.bundle.context_products
        except BaseException:
            return self.product.bundle.context_products

    @staticmethod
    def _match_context_entry(context_products, name, valid_types=None, case_insensitive=False):
        """Find the lid/type of the context product matching ``name``.

        If several entries in ``context_products`` match, the last one
        encountered wins (matches the pre-existing behaviour of
        get_missions/get_observers/get_targets, which never ``break`` out
        of their matching loop).

        :param context_products: List of context product dictionaries
        :param name: Name to match against each entry's ``name``
        :param valid_types: Iterable of acceptable ``type`` values, or
            ``None`` to accept any type
        :param case_insensitive: If ``True``, match ``name`` case-insensitively
        :return: ``(lid, type)`` tuple, or ``(None, None)`` if no entry matches
        """
        lid, type_ = None, None

        for context_product in context_products:
            cp_name = context_product["name"][0]
            name_matches = (
                cp_name.upper() == name.upper() if case_insensitive else cp_name == name
            )
            type_matches = valid_types is None or context_product["type"][0] in valid_types

            if name_matches and type_matches:
                lid = context_product["lidvid"].split("::")[0]
                type_ = context_product["type"][0]

        return lid, type_

    @staticmethod
    def _render_context_entry(eol, tab, tag, indent, name, type_, lid, reference_type):
        """Render one Investigation_Area/Observing_System_Component/
        Target_Identification XML block.

        The three callers share this exact inner structure and differ only
        in the wrapping ``tag`` and the base ``indent`` level (2 for
        Investigation_Area/Target_Identification, 3 for
        Observing_System_Component); inner elements sit at ``indent + 1``
        and ``lid_reference``/``reference_type`` at ``indent + 2``.

        :param eol: End-of-line string to use
        :param tab: Number of spaces per indent level
        :param tag: Wrapping element name
        :param indent: Base indent level, in units of ``tab``
        :param name: Value of the ``name`` element
        :param type_: Value of the ``type`` element
        :param lid: Value of the ``lid_reference`` element
        :param reference_type: Value of the ``reference_type`` element
        :return: The rendered XML block
        """
        return (
            f"{' ' * indent * tab}<{tag}>{eol}"
            f"{' ' * (indent + 1) * tab}<name>{name}</name>{eol}"
            f"{' ' * (indent + 1) * tab}<type>{type_}</type>{eol}"
            f"{' ' * (indent + 1) * tab}<Internal_Reference>{eol}"
            f"{' ' * (indent + 2) * tab}<lid_reference>{lid}</lid_reference>{eol}"
            f"{' ' * (indent + 2) * tab}<reference_type>{reference_type}</reference_type>{eol}"
            f"{' ' * (indent + 1) * tab}</Internal_Reference>{eol}"
            f"{' ' * indent * tab}</{tag}>{eol}"
        )

    def get_missions(self) -> str:
        """Get the label mission from the context products.

        :return: List of missions to be included in the label
        """
        miss = self.missions

        if not isinstance(miss, list):
            miss = [miss]

        mis_list_for_label = ""

        context_products = self._resolve_context_products()

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab
        for mis in miss:
            if mis:
                mission_lid, mission_type = self._match_context_entry(
                    context_products, mis, valid_types=("Mission", "Other Investigation")
                )

                if not mission_lid:
                    handle_npb_error(
                        f"LID has not been obtained for mission {mis}.",
                        setup=self.setup,
                    )

                mis_list_for_label += self._render_context_entry(
                    eol, tab, "Investigation_Area", 2,
                    mis, mission_type, mission_lid, self._mission_reference_type,
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

        context_products = self._resolve_context_products()

        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab

        for ob in obs:
            if ob:
                ob_name = ob.split(",")[0]
                ob_lid, ob_type = self._match_context_entry(
                    context_products, ob_name,
                    valid_types=("Spacecraft", "Rover", "Lander", "Host"),
                )

                if not ob_lid:
                    handle_npb_error(
                        f"LID has not been obtained for observer {ob}.",
                        setup=self.setup,
                    )

                obs_list_for_label += self._render_context_entry(
                    eol, tab, "Observing_System_Component", 3,
                    ob_name, ob_type, ob_lid, "is_instrument_host",
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
                    f"{self._target_reference_type}"
                    f"</reference_type>{eol}"
                    + f"{' ' * 3 * tab}</Internal_Reference>{eol}"
                    + f"{' ' * 2 * tab}</Target_Identification>{eol}"
                )

        if not tar_list_for_label:
            handle_npb_error(f"{self.product.name} targets not defined.", setup=self.setup)
        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label
