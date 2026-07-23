"""PDS4 version-specific base class for PDS labels."""

from typing import Iterable, Optional, Tuple

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
            self._context_products = product.collection.bundle.context_products
        except BaseException:
            self._context_products = product.bundle.context_products

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

    def _match_context_entry(
        self,
        name: str,
        valid_types: Optional[Iterable[str]] = None,
        case_insensitive: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Find the lid/type of the context product matching ``name``.

        If several entries in ``self._context_products`` match, the last
        one encountered wins (matches the pre-existing behaviour of
        get_missions/get_observers/get_targets, which never ``break`` out
        of their matching loop).

        :param name: Name to match against each entry's ``name``
        :param valid_types: Iterable of acceptable ``type`` values, or
            ``None`` to accept any type
        :param case_insensitive: If ``True``, match ``name`` case-insensitively
        :return: ``(lid, type)`` tuple, or ``(None, None)`` if no entry matches
        """
        lid, type_ = None, None

        for context_product in self._context_products:
            cp_name = context_product["name"][0]
            name_matches = (
                cp_name.upper() == name.upper() if case_insensitive else cp_name == name
            )
            type_matches = valid_types is None or context_product["type"][0] in valid_types

            if name_matches and type_matches:
                lid = context_product["lidvid"].split("::")[0]
                type_ = context_product["type"][0]

        return lid, type_

    def _render_context_entry(
        self,
        tag: str,
        indent: int,
        name: str,
        type_: Optional[str],
        lid: Optional[str],
        reference_type: str,
    ) -> str:
        """Render one Investigation_Area/Observing_System_Component/
        Target_Identification XML block.

        The three callers share this exact inner structure and differ only
        in the wrapping ``tag`` and the base ``indent`` level (2 for
        Investigation_Area/Target_Identification, 3 for
        Observing_System_Component); inner elements sit at ``indent + 1``
        and ``lid_reference``/``reference_type`` at ``indent + 2``.

        :param tag: Wrapping element name
        :param indent: Base indent level, in units of ``self.setup.xml_tab``
        :param name: Value of the ``name`` element
        :param type_: Value of the ``type`` element
        :param lid: Value of the ``lid_reference`` element
        :param reference_type: Value of the ``reference_type`` element
        :return: The rendered XML block
        """
        eol = self.setup.eol_pds4
        tab = self.setup.xml_tab
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

        eol = self.setup.eol_pds4
        for mis in miss:
            if mis:
                mission_lid, mission_type = self._match_context_entry(
                    mis, valid_types=("Mission", "Other Investigation")
                )

                if not mission_lid:
                    handle_npb_error(
                        f"LID has not been obtained for mission {mis}.",
                        setup=self.setup,
                    )

                mis_list_for_label += self._render_context_entry(
                    "Investigation_Area", 2,
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

        eol = self.setup.eol_pds4

        for ob in obs:
            if ob:
                ob_name = ob.split(",")[0]
                ob_lid, ob_type = self._match_context_entry(
                    ob_name,
                    valid_types=("Spacecraft", "Rover", "Lander", "Host"),
                )

                if not ob_lid:
                    handle_npb_error(
                        f"LID has not been obtained for observer {ob}.",
                        setup=self.setup,
                    )

                obs_list_for_label += self._render_context_entry(
                    "Observing_System_Component", 3,
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

        eol = self.setup.eol_pds4

        for tar in tars:
            if tar:
                target_name = tar
                # No type filter: unlike missions/observers, which are
                # restricted to a fixed vocabulary of context-product types,
                # a target can be any body type (planet, satellite, ring,
                # ...), so any type is accepted.
                target_lid, target_type = self._match_context_entry(
                    target_name, case_insensitive=True
                )
                # TODO: BUG, unlike get_missions/get_observers above, no
                #       handle_npb_error is raised here when target_lid is
                #       None (no context product matched). lid/type instead
                #       fall through as the literal string "None" into the
                #       rendered label. Pre-existing behaviour, preserved by
                #       this refactor and pinned by
                #       test_no_match_renders_none_without_raising.
                if target_type is not None:
                    target_type = target_type.capitalize()

                tar_list_for_label += self._render_context_entry(
                    "Target_Identification", 2,
                    target_name, target_type, target_lid, self._target_reference_type,
                )

        if not tar_list_for_label:
            handle_npb_error(f"{self.product.name} targets not defined.", setup=self.setup)
        tar_list_for_label = tar_list_for_label.rstrip() + eol

        return tar_list_for_label
