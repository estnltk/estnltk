from typing import Any, Dict, Iterable, List, Tuple, Optional

from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    ChainMatch,
    PathPattern,
)
from estnltk.taggers.system.rule_taggers.deprel_components.serializer import (
    append_unique,
    serialize_constraints,
)


def collect_role_span_names(
    patterns: Iterable[PathPattern], output_span_names: Optional[Tuple[str, ...]] = None
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """
    Collect the unique role names from all patterns to determine the span names for the output layer.
    If user provided output_span_names and there are duplicates, raise an error.

    Args:
        patterns (Iterable[PathPattern]): The patterns to collect role names from.
        output_span_names (Optional[Tuple[str, ...]]): User-provided span names for the output layer. If None, all role names from patterns are used.

    Returns:
        Tuple[Tuple[str, ...], Tuple[str, ...]]: A tuple containing the collected role span names and user-defined span names.
    """
    span_names: List[str] = []
    user_defined_span_names: List[str] = []
    seen: set[str] = set()
    for pattern in patterns:
        for node_constraint in pattern.node_steps:
            append_unique(span_names, seen, node_constraint.role)
    # Check for duplicates with user-provided output_span_names
    if output_span_names:
        for span_name in span_names:
            if span_name in output_span_names:
                raise ValueError(
                    f"Duplicate span name {span_name!r} found in pattern roles and user-provided output_span_names."
                )
        # No duplicates, so we can add all user-provided span names to the list of span names to be included in the output layer.
        for span_name in output_span_names:
            append_unique(span_names, seen, span_name)
            user_defined_span_names.append(span_name)

    return tuple(span_names), tuple(user_defined_span_names)


def collect_output_attribute_names(
    patterns: Iterable[PathPattern],
    include_pattern_constraints: bool = False,
    output_attributes: Optional[Tuple[str, ...]] = None,
) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """
    Collect the attribute names for the output layer, starting with default attributes and then adding any pattern constraint fields if include_pattern_constraints is True.
    If user provided output_attributes and there are duplicates, raise an error.

    Args:
        patterns (Iterable[PathPattern]): The patterns to collect attribute names from.
        include_pattern_constraints (bool): Whether to include pattern constraint fields as attributes.
        output_attributes (Optional[Tuple[str, ...]]): User-provided attribute names for the output layer. If None, all default and pattern constraint fields are used.

    Returns:
        Tuple[Tuple[str, ...], Tuple[str, ...]]: A tuple containing the collected attribute names and user-defined attribute names.
    """
    attribute_names: List[str] = ["pattern_name", "matched_text"]
    user_defined_attributes: List[str] = []
    seen: set[str] = set(attribute_names)

    if include_pattern_constraints:
        # Add pattern constraint fields with role-based prefixes to ensure uniqueness and clarity in the output attributes
        for pattern in patterns:
            for node_constraint in pattern.node_steps:
                prefix = f"{node_constraint.role}_"
                # Add node constraint fields with role-based prefix to ensure uniqueness and clarity in the output attributes
                if node_constraint.attribute_conditions:
                    for attr_name in node_constraint.attribute_conditions:
                        append_unique(attribute_names, seen, f"{prefix}{attr_name}")
                if node_constraint.nested_attribute_conditions:
                    for attr_name in node_constraint.nested_attribute_conditions:
                        append_unique(attribute_names, seen, f"{prefix}{attr_name}")
                if node_constraint.extra_predicates:
                    append_unique(attribute_names, seen, f"{prefix}extra_predicates")

    # Check for duplicates with user-provided output_attributes
    if output_attributes:
        for attr_name in attribute_names:
            if attr_name in output_attributes:
                raise ValueError(
                    f"Duplicate attribute name {attr_name!r} found in pattern constraints and user-provided output_attributes."
                )
        # No duplicates, so we can add all user-provided attribute names to the list of attributes to be included in the output layer.
        for attr_name in output_attributes:
            append_unique(attribute_names, seen, attr_name)
            user_defined_attributes.append(attr_name)

    return tuple(attribute_names), tuple(user_defined_attributes)


def build_match_annotation_payload(
    match: ChainMatch,
    patterns_by_name: Dict[str, PathPattern],
    span_names: Tuple[str, ...],
    user_defined_span_names: Tuple[str, ...] | None = None,
    user_defined_attributes: Tuple[str, ...] | None = None,
    include_pattern_constraints: bool = False,
) -> Dict[str, Any]:
    """
    Build the annotation payload for a given match, including role spans and optionally flattened pattern constraint fields.
    If the match's pattern name is not found in `patterns_by_name`, raise a KeyError. If a node for a role is missing `start`/`end` offsets, raise a `ValueError`.

    Args:
        match (ChainMatch): The match to build the payload for.
        patterns_by_name (Dict[str, PathPattern]): A mapping of pattern names to their definitions, used to look up constraint fields if include_pattern_constraints is True.
        span_names (Tuple[str, ...]): The role names to include as spans in the payload.
        include_pattern_constraints (bool): Whether to include flattened pattern constraint fields in the payload.

    Returns:
        Dict[str, Any]: The annotation payload for the match.
    """
    pattern = patterns_by_name.get(match.pattern_name)
    if pattern is None:
        raise KeyError(f"Unknown pattern name: {match.pattern_name!r}")

    payload: Dict[str, Any] = {role: None for role in span_names}
    payload["pattern_name"] = match.pattern_name
    payload["matched_text"] = getattr(match, "matched_text", None)

    # Add spans for each role based on the matched nodes
    for role in span_names:
        node = match.role_to_node.get(role)
        if node is None:
            continue
        node_constraint = pattern.get_node_constraint(role)
        start = getattr(node, "start", None)
        end = getattr(node, "end", None)
        if start is None or end is None:
            raise ValueError(
                f"Cannot add relation span for role {role!r}: node is missing start/end offsets."
            )
        payload[role] = (int(start), int(end))

    # Initialize user-defined span and attribute fields to None
    if user_defined_span_names:
        for span_name in user_defined_span_names:
            payload[span_name] = None
    if user_defined_attributes:
        for attr_name in user_defined_attributes:
            payload[attr_name] = None

    # Optionally add flattened pattern constraint fields with role-based prefixes to the payload
    if include_pattern_constraints:
        for node_constraint in pattern.node_steps:
            payload.update(serialize_constraints(node_constraint))

    return payload
