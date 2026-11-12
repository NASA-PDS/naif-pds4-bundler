"""PDS4 version-specific base class for PDS labels."""

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from .label import PDSLabel
from ..exceptions import NPBError


# Name of each supported line ending as it appears in the label.
_END_OF_LINE_NAMES = {
    "CRLF": "Carriage-Return Line-Feed",
    "LF": "Line-Feed",
}


def _join_names(primary: str, secondary: List[str]) -> str:
    """Join the primary name and the secondary ones as 'A, B, and C'.

    :param primary: Name that goes first
    :param secondary: Names that follow it
    :return: ``primary`` alone, 'A and B' for one secondary name, or the
        comma-separated list with 'and' before the last name
    """
    names = [primary] + list(secondary)

    if len(names) <= 2:
        return " and ".join(names)

    # Oxford comma: the last name is introduced by ', and'.
    return ", ".join(names[:-1]) + ", and " + names[-1]


@dataclass(frozen=True)
class _ContextKind:
    """What sets missions, observers and targets apart when rendering."""

    # Used in the "LID has not been obtained for ..." error.
    singular: str
    # Used in the "... not defined." error.
    plural: str
    # XML element that wraps each entry.
    tag: str
    indent: int
    valid_types: Optional[Tuple[str, ...]] = None
    case_insensitive: bool = False
    capitalize_type: bool = False
    name_before_comma: bool = False


_MISSION = _ContextKind(
    "mission", "missions", "Investigation_Area", 2,
    valid_types=("Mission", "Other Investigation"),
)
_OBSERVER = _ContextKind(
    "observer", "observers", "Observing_System_Component", 3,
    valid_types=("Spacecraft", "Rover", "Lander", "Host"),
    name_before_comma=True,
)
# No type filter: unlike missions/observers, which are restricted to a fixed
# vocabulary of context-product types, a target can be anybody type (planet,
# satellite, ring, ...), so any type is accepted.
_TARGET = _ContextKind(
    "target", "targets", "Target_Identification", 2,
    case_insensitive=True,
    capitalize_type=True,
)


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

    def __init__(self, product) -> None:
        """Constructor."""

        # PDSLabel.__init__ sets self.setup from product.setup, so from here
        # on we read setup off self, not off a separate parameter.
        super().__init__(product)

        # Context products normally hang off the product's collection; a few
        # product types (e.g. the bundle readme) attach the bundle directly
        # instead, so fall back to that when there is no collection.
        try:
            self._context_products = product.collection.bundle.context_products

        # Products with no real collection (e.g. the bundle readme) have a
        # placeholder .collection with no .bundle attribute to chain off;
        # a broken .collection/.bundle chain can also raise TypeError.
        except (AttributeError, TypeError):
            self._context_products = product.bundle.context_products

        # Fixed PDS4 header fields that come straight from setup.
        self._label_fields["XML_MODEL"] = self.setup.xml_model
        self._label_fields["SCHEMA_LOCATION"] = self.setup.schema_location
        self._label_fields["INFORMATION_MODEL_VERSION"] = self.setup.information_model

        # The names are rendered as a single value, or as an "and"-joined
        # list when secondary missions and observers are configured.
        secondary_missions = getattr(self.setup, "secondary_missions", [])
        self._label_fields["PDS4_MISSION_NAME"] = _join_names(
            self.setup.mission_name, secondary_missions
        )

        secondary_observers = getattr(self.setup, "secondary_observers", [])
        observers_text = _join_names(self.setup.observer, secondary_observers)
        pronoun = "their" if secondary_observers else "its"
        self._label_fields["PDS4_OBSERVER_NAME"] = (
            f"{observers_text} spacecraft and {pronoun}"
        )

        # PDS4 labels always render CRLF in the model name, regardless of which
        # line ending the file itself actually uses.
        self._label_fields["END_OF_LINE_PDS4"] = _END_OF_LINE_NAMES["CRLF"]

        # Setup only lets 'CRLF' or 'LF' through, so the lookup cannot miss.
        self._label_fields["END_OF_LINE"] = _END_OF_LINE_NAMES[
            self.setup.end_of_line
        ]

        # Every bundle description links to the spiceds document -- it's the
        # one document guaranteed to exist for any mission, regardless of
        # which product this label actually belongs to.
        self._label_fields["BUNDLE_DESCRIPTION_LID"] = f"{self.setup.logical_identifier}:document:spiceds"

        # Each is a block of rendered XML (not a plain name or list) built
        # from the context products matching self.missions/observers/targets.
        self._label_fields["MISSIONS"] = self.get_missions()
        self._label_fields["OBSERVERS"] = self.get_observers()
        self._label_fields["TARGETS"] = self.get_targets()

    @property
    def _eol(self) -> str:
        """End-of-line convention used for PDS4 labels."""
        return self.setup.eol_pds4

    def _match_context_entry(
        self,
        name: str,
        valid_types: Optional[Tuple[str, ...]] = None,
        case_insensitive: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """Find the lid/type of the context product matching ``name``.

        If several entries in ``self._context_products`` match, the last
        one encountered wins.

        :param name: Name to match against each entry's ``name``
        :param valid_types: Tuple of acceptable ``type`` values, or
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
        product_type: str,
        lid: str,
        reference_type: str,
    ) -> str:
        """Render one Investigation_Area/Observing_System_Component/
        Target_Identification XML block.

        :param tag: Wrapping element name
        :param indent: Base indent level, in units of ``self.setup.xml_tab``
        :param name: Value of the ``name`` element
        :param product_type: Value of the ``type`` element
        :param lid: Value of the ``lid_reference`` element
        :param reference_type: Value of the ``reference_type`` element
        :return: The rendered XML block
        """
        eol = self._eol
        tab = self.setup.xml_tab
        return (
            f"{' ' * indent * tab}<{tag}>{eol}"
            f"{' ' * (indent + 1) * tab}<name>{name}</name>{eol}"
            f"{' ' * (indent + 1) * tab}<type>{product_type}</type>{eol}"
            f"{' ' * (indent + 1) * tab}<Internal_Reference>{eol}"
            f"{' ' * (indent + 2) * tab}<lid_reference>{lid}</lid_reference>{eol}"
            f"{' ' * (indent + 2) * tab}<reference_type>{reference_type}</reference_type>{eol}"
            f"{' ' * (indent + 1) * tab}</Internal_Reference>{eol}"
            f"{' ' * indent * tab}</{tag}>{eol}"
        )

    def _render_context_kind(
        self, kind: _ContextKind, entries: Any, reference_type: str
    ) -> str:
        """Render every entry of one kind (missions, observers or targets).

        :param kind: Differences for the kind being rendered
        :param entries: One entry or a list of entries from the label
        :param reference_type: Value of the ``reference_type`` element
        :return: The XML blocks, ending in exactly one end of line
        :raises NPBError: If an entry has no matching context product, or
            if nothing was rendered
        """
        if not isinstance(entries, list):
            entries = [entries]

        blocks = ""

        for entry in entries:
            if not entry:
                continue

            # Observers may carry extra text after a comma; only the first
            # part is the name, but the error below quotes the whole entry.
            name = entry.split(",")[0] if kind.name_before_comma else entry
            lid, type_ = self._match_context_entry(
                name, kind.valid_types, kind.case_insensitive
            )

            # Handle the case where no LID was found: without this check,
            # the label would be built with "None" as the value, instead of
            # stopping with a clear error.
            if not lid:
                raise NPBError(
                    f"LID has not been obtained for {kind.singular} {entry}."
                )

            # If we got here we already have a real match, so there's always
            # a type to capitalize.
            if kind.capitalize_type:
                type_ = type_.capitalize()

            blocks += self._render_context_entry(
                kind.tag, kind.indent, name, type_, lid, reference_type
            )

        if not blocks:
            raise NPBError(f"{self.product.name} {kind.plural} not defined.")

        # Strip trailing whitespace from the last rendered entry, then
        # append exactly one EOL.
        return blocks.rstrip() + self._eol

    def get_missions(self) -> str:
        """Get the label mission from the context products.

        :return: List of missions to be included in the label
        """
        return self._render_context_kind(
            _MISSION, self.missions, self._mission_reference_type
        )

    def get_observers(self) -> str:
        """Get the label observers from the context products.

        :return: List of Observers to be included in the label
        """
        return self._render_context_kind(
            _OBSERVER, self.observers, "is_instrument_host"
        )

    def get_targets(self) -> str:
        """Get the label targets from the context products.

        :return: List of Targets to be included in the label
        """
        return self._render_context_kind(
            _TARGET, self.targets, self._target_reference_type
        )
