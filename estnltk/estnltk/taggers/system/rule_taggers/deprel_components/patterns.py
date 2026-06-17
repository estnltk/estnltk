from typing import (
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Iterable,
    Self,
    Any,
)
from dataclasses import dataclass, field
from estnltk import Span

from estnltk.taggers.system.rule_taggers.deprel_components.types import EdgeContext
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    NodeConstraint,
    EdgeConstraint,
)
from estnltk.taggers.system.rule_taggers.deprel_components.config import (
    DEFAULT_MAX_MATCHES_PER_COLLECTOR,
    DEFAULT_DEDUP_MODE_COLLECTOR,
    VALID_DEDUP_MODES,
)


@dataclass(frozen=True, slots=True)
class PathPattern:
    """
    Represents a pattern for matching paths in the dependency tree.

    ## Attributes:
    - **name** (`str`): A unique name for this path pattern, used for identification and debugging purposes.
    - **node_steps** (`Tuple[NodeConstraint, ...]`): A tuple of NodeConstraint objects that specify the constraints for each node along the path. The first NodeConstraint corresponds to the starting node (e.g., the "self" node), and subsequent NodeConstraints correspond to nodes reached by traversing edges according to the specified EdgeConstraints.
    - **edge_steps** (`Tuple[EdgeConstraint, ...]`): A tuple of EdgeConstraint objects that specify the constraints for the edges to traverse between the nodes specified in `node_steps`. The length of `edge_steps` should be one less than the length of `node_steps`, as each edge connects two nodes.
    - **anchor_role** (`str`): The role of the anchor node in this path pattern, which serves as the reference point for the path. This is typically the role of the first NodeConstraint in `node_steps`, but it can be specified separately for clarity.
    - **emit_roles** (`Optional[Tuple[str, ...]]`): Roles corresponding to the nodes in `node_steps` that should be included in the emitted features when this pattern matches. If omitted, all roles defined in `node_steps` are emitted by default.

    ## Methods:
    - :func:`~PathPattern.get_node_constraint`: Retrieves the NodeConstraint associated with a given role in this path pattern.
    - :func:`~PathPattern.get_edge_constraint`: Retrieves the EdgeConstraint associated with the edge connecting two specified roles in this path pattern.
    - :func:`~PathPattern.describe`: Returns a human-readable explanation of this path pattern, including the name, node constraints, edge constraints, anchor role, and emit roles.
    """

    name: str
    node_steps: Tuple[NodeConstraint, ...]
    edge_steps: Tuple[EdgeConstraint, ...]
    anchor_role: Optional[str] = None
    emit_roles: Optional[Tuple[str, ...]] = None

    def __post_init__(self: Self) -> None:
        """
        Validate config once.
        """
        # If anchor_role was not provided, default to the first node step's role.
        if self.anchor_role is None:
            if not self.node_steps:
                raise ValueError("Cannot infer anchor_role: node_steps is empty")
            object.__setattr__(self, "anchor_role", self.node_steps[0].role)

        # If emit_roles is omitted, emit every role in node_steps by default.
        if self.emit_roles is None:
            object.__setattr__(
                self,
                "emit_roles",
                tuple(node_constraint.role for node_constraint in self.node_steps),
            )

        self._validate_or_raise()

    def get_node_constraint(self: Self, role: str) -> Optional[NodeConstraint]:
        """
        Retrieve the NodeConstraint associated with a given role in this path pattern.

        Args:
            role (str): The role of the node constraint to retrieve (e.g., "self", "parent", "child", etc.).

        Returns:
            Optional[NodeConstraint]: The NodeConstraint object associated with the specified role, or None if no such role exists in this pattern. This allows for easy access to the constraints for specific roles when processing matched paths.
        """
        for nc in self.node_steps:
            if nc.role == role:
                return nc
        return None

    def get_edge_constraint(
        self: Self, from_role: str, to_role: str
    ) -> Optional[EdgeConstraint]:
        """
        Retrieve the EdgeConstraint associated with the edge connecting two specified roles in this path pattern.

        Args:
            from_role (str): The role of the starting node of the edge (e.g., "self", "parent", "child", etc.).
            to_role (str): The role of the ending node of the edge (e.g., "self", "parent", "child", etc.).

        Returns:
            Optional[EdgeConstraint]: The EdgeConstraint object associated with the edge connecting the specified roles, or None if no such edge exists in this pattern. This allows for easy access to the constraints for specific edges when processing matched paths.
        """
        for i in range(len(self.edge_steps)):
            if (
                self.node_steps[i].role == from_role
                and self.node_steps[i + 1].role == to_role
            ):
                return self.edge_steps[i]
        return None

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of this path pattern, including the name, node constraints, edge constraints, anchor role, and emit roles.

        Returns:
            str: A human-readable string describing this path pattern, including the name, node constraints, edge constraints, anchor role, and emit roles. This can be used for debugging or for explaining what this pattern is designed to match.
        """
        parts = [f"Pattern name: {self.name}"]
        for i in range(len(self.node_steps)):
            parts.append(f"Node step {i}: {self.node_steps[i].describe()}")
            if i < len(self.edge_steps):
                parts.append(f"Edge step {i}: {self.edge_steps[i].describe()}")
        parts.append(f"Anchor role: {self.anchor_role}")
        parts.append(
            f"Emit roles: {', '.join(self.emit_roles) if self.emit_roles else 'None'}"
        )
        return "\n".join(parts)

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.name, str) or self.name.strip() == "":
            raise TypeError("name must be a non-empty string.")

        if not isinstance(self.node_steps, tuple) or not all(
            isinstance(nc, NodeConstraint) for nc in self.node_steps
        ):
            raise TypeError("node_steps must be a tuple of NodeConstraint objects.")

        if not isinstance(self.edge_steps, tuple) or not all(
            isinstance(ec, EdgeConstraint) for ec in self.edge_steps
        ):
            raise TypeError("edge_steps must be a tuple of EdgeConstraint objects.")

        if len(self.edge_steps) != len(self.node_steps) - 1:
            raise ValueError(
                "Length of edge_steps must be one less than length of node_steps."
            )

        if not isinstance(self.anchor_role, str) or self.anchor_role.strip() == "":
            raise TypeError("anchor_role must be a non-empty string.")

        roles = [nc.role for nc in self.node_steps]
        valid_roles = {nc.role for nc in self.node_steps}
        if self.anchor_role not in valid_roles:
            raise ValueError(
                f"anchor_role '{self.anchor_role}' must match one of the roles defined in node_steps: {valid_roles}"
            )

        if len(valid_roles) != len(roles):
            raise ValueError("Roles defined in node_steps must be unique.")

        if (
            self.emit_roles is None
            or not isinstance(self.emit_roles, tuple)
            or not all(
                isinstance(role, str) and role.strip() != "" for role in self.emit_roles
            )
        ):
            raise TypeError("emit_roles must be a tuple of non-empty strings or None.")

        emit_roles_list = list(self.emit_roles)
        emit_roles_set = set(self.emit_roles)
        if not emit_roles_set.issubset(valid_roles):
            raise ValueError(
                f"All emit_roles must match roles defined in node_steps. Valid roles: {valid_roles}, emit_roles: {emit_roles_set}"
            )

        if len(emit_roles_list) != len(emit_roles_set):
            raise ValueError("emit_roles must not contain duplicate roles.")


@dataclass(frozen=True, slots=True)
class ChainMatch:
    """
    Represents a successful match of a PathPattern against a specific instance in the data, including the matched nodes, traversed edges, and any extracted features.
    ## Attributes:
    - **pattern_name** (`str`): The name of the PathPattern that was matched.
    - **sentence_index** (`int`): The index of the sentence in which the match was found.
    - **sentence_span** (`Tuple[int, int]`): The character span (start, end) of the entire sentence in the original text.
    - **role_to_token_id** (`Dict[str, int]`): A dictionary mapping each role defined in the PathPattern to the token ID of the node that was matched for that role in this instance.
    - **role_to_node** (`Dict[str, Span]`): A dictionary mapping each role defined in the PathPattern to the actual estnltk Span annotation of the node that was matched for that role in this instance. This allows for access to all the properties of the matched nodes, not just their token IDs.
    - **traversed_edges** (`Tuple[Tuple[str, str, EdgeContext], ...]`): A tuple of tuples representing the edges that were traversed to match this pattern. Each inner tuple contains the from_role, to_role, and the EdgeContext of the traversed edge. This provides a detailed record of how the pattern was matched in terms of the dependency graph traversal.
    - **matched_text** (`str`): The text of the entire matched path, which can be useful for debugging, analysis, or as part of the emitted features.
    - **metadata** (`Dict[str, Any]`): An optional dictionary for storing any additional metadata about this match that may be useful for downstream processing, debugging, or analysis. This can include things like confidence scores, timestamps, or any other relevant information that does not fit into the other fields.
    """

    pattern_name: str
    sentence_index: int
    sentence_span: Tuple[int, int]
    role_to_token_id: Dict[str, int]
    role_to_node: Dict[str, Span]
    traversed_edges: Tuple[
        Tuple[str, str, EdgeContext], ...
    ]  # (from_role, to_role, edge_context) for each traversed edge
    matched_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self: Self) -> None:
        """
        Validate config once.
        """
        self._validate_or_raise()

    def get_node(self: Self, role: str) -> Span:
        """
        Get the estnltk Span annotation of the node matched for the given role.

        Args:
            role (str): The role of the node to retrieve (e.g., "self", "parent", "child", etc.).

        Returns:
            Span: The estnltk Span annotation of the node matched for the given role. This allows for easy access to the properties of the matched nodes when processing the results of pattern matching.
        """
        if role not in self.role_to_node:
            raise ValueError(f"Role '{role}' not found in this match.")
        return self.role_to_node[role]

    def get_token_id(self: Self, role: str) -> int:
        """
        Get the token ID of the node matched for the given role.

        Args:
            role (str): The role of the node to retrieve (e.g., "self", "parent", "child", etc.).

        Returns:
            int: The token ID of the node matched for the given role. This allows for easy access to the token IDs of the matched nodes when processing the results of pattern matching.
        """
        if role not in self.role_to_token_id:
            raise ValueError(f"Role '{role}' not found in this match.")
        return self.role_to_token_id[role]

    def get_roles(self: Self) -> Set[str]:
        """
        Get the set of roles that were matched in this ChainMatch.

        Returns:
            Set[str]: A set of roles that were matched in this ChainMatch. This can be useful for quickly checking which roles are present in the match without having to look at the individual node annotations.
        """
        return set(self.role_to_node.keys())

    def build_matched_text(self: Self, ordered_roles: Tuple[str, ...]) -> str:
        """
        Build the matched text for this ChainMatch based on the specified order of roles. This concatenates the text of the nodes corresponding to the given roles in the specified order.

        Args:
            ordered_roles (Tuple[str, ...]): A tuple specifying the order of roles to concatenate for building the matched text. The roles should correspond to those defined in the PathPattern and present in this ChainMatch.

        Returns:
            str: The concatenated text of the nodes corresponding to the specified roles in the given order. This can be used for generating a human-readable representation of the matched path or for use in emitted features.
        """
        parts: List[str] = []
        for role in ordered_roles:
            node = self.get_node(role)
            parts.append(
                getattr(node, "text", "")
            )  # Use empty string if 'text' attribute is missing
        return " ".join(parts).strip()

    def to_output_row(self: Self) -> Dict[str, Any]:
        """
        Convert this ChainMatch to a dictionary format suitable for output (e.g., for saving to JSON or CSV).

        Returns:
            Dict[str, Any]: A dictionary representation of this ChainMatch, including all relevant information such as pattern name, sentence index, sentence span, role-to-token ID mapping, role-to-node mapping (with node properties), traversed edges, matched text, and metadata. This can be used for exporting the results of pattern matching in a structured format.
        """
        return {
            "pattern_name": self.pattern_name,
            "sentence_index": self.sentence_index,
            "sentence_span": self.sentence_span,
            "role_to_token_id": self.role_to_token_id,
            "role_to_node": {
                role: {
                    "start": getattr(node, "start", None),
                    "end": getattr(node, "end", None),
                    "upostag": getattr(node, "upostag", None),
                    "xpostag": getattr(node, "xpostag", None),
                    "lemma": getattr(node, "lemma", None),
                    "feats": getattr(node, "feats", None),
                }
                for role, node in self.role_to_node.items()
            },
            "traversed_edges": [
                {
                    "from_role": from_role,
                    "to_role": to_role,
                    "edge_context": {
                        "direction": edge_context.direction.value,
                        "hops": edge_context.hops,
                    },
                }
                for from_role, to_role, edge_context in self.traversed_edges
            ],
            "matched_text": self.matched_text,
            "metadata": self.metadata,
        }

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of this ChainMatch, including the pattern name, sentence index, sentence span, matched roles and their corresponding token IDs and node properties, traversed edges, matched text, and any metadata.

        Returns:
            str: A human-readable string describing this ChainMatch in detail. This can be used for debugging or for explaining what this match represents in terms of the pattern that was matched and the specific instance in the data.
        """
        parts = [f"Pattern name: {self.pattern_name}"]
        parts.append(f"Sentence index: {self.sentence_index}")
        parts.append(f"Sentence span: {self.sentence_span}")
        parts.append("Matched roles:")
        for role in self.get_roles():
            token_id = self.get_token_id(role)
            node = self.get_node(role)
            parts.append(
                f"  Role: {role}, Token ID: {token_id}, Node properties: {{start: {node.start}, end: {node.end}, upostag: {node.upostag}, xpostag: {node.xpostag}, lemma: {node.lemma}, feats: {node.feats}}}"
            )
        parts.append("Traversed edges:")
        for from_role, to_role, edge_context in self.traversed_edges:
            parts.append(
                f"  From role: {from_role} to role: {to_role}, Edge context: {{direction: {edge_context.direction.value}, hops: {edge_context.hops}}}"
            )
        parts.append(f"Matched text: '{self.matched_text}'")
        if self.metadata:
            parts.append(f"Metadata: {self.metadata}")
        return "\n".join(parts)

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.pattern_name, str) or self.pattern_name.strip() == "":
            raise TypeError("pattern_name must be a non-empty string.")

        if not isinstance(self.sentence_index, int) or self.sentence_index < 0:
            raise ValueError("sentence_index must be a non-negative integer.")

        if (
            not isinstance(self.sentence_span, tuple)
            or len(self.sentence_span) != 2
            or not all(isinstance(i, int) and i >= 0 for i in self.sentence_span)
            or self.sentence_span[0] > self.sentence_span[1]
        ):
            raise ValueError(
                "sentence_span must be a tuple of two non-negative integers (start, end) with start <= end."
            )

        if not isinstance(self.role_to_token_id, dict) or not all(
            isinstance(k, str) and k.strip() != "" and isinstance(v, int) and v >= 0
            for k, v in self.role_to_token_id.items()
        ):
            raise TypeError(
                "role_to_token_id must be a dictionary mapping non-empty strings to non-negative integers."
            )

        if not isinstance(self.role_to_node, dict) or not all(
            isinstance(k, str) and k.strip() != "" and isinstance(v, Span)
            for k, v in self.role_to_node.items()
        ):
            raise TypeError(
                "role_to_node must be a dictionary mapping non-empty strings to Span objects."
            )

        if not isinstance(self.traversed_edges, tuple) or not all(
            isinstance(edge_info, tuple)
            and len(edge_info) == 3
            and isinstance(edge_info[0], str)
            and edge_info[0].strip() != ""
            and isinstance(edge_info[1], str)
            and edge_info[1].strip() != ""
            and isinstance(edge_info[2], EdgeContext)
            for edge_info in self.traversed_edges
        ):
            raise TypeError(
                "traversed_edges must be a tuple of tuples (from_role, to_role, edge_context) where from_role and to_role are non-empty strings and edge_context is an EdgeContext object."
            )

        if not isinstance(self.matched_text, str):
            raise TypeError("matched_text must be a string.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        token_roles = set(self.role_to_token_id.keys())
        node_roles = set(self.role_to_node.keys())
        if token_roles != node_roles:
            raise ValueError(
                f"Roles in role_to_token_id and role_to_node must match. token_roles: {token_roles}, node_roles: {node_roles}"
            )


@dataclass(slots=True)
class MatchCollector:
    """
    Collect and manage `ChainMatch` objects with optional deduplication.

    ## Attributes:
    - **matches** (`List[ChainMatch]`): A list to store the collected matches in insertion order.
    - **dedup_mode** (`str`): The deduplication mode to use when adding matches. Allowed values are "none" (no deduplication), "exact" (deduplicate based on exact match of `ChainMatch`), and "role_based" (deduplicate based on the combination of pattern name, sentence index, and role-to-token ID mapping).
    - **max_matches** (`int`): The maximum number of matches to store. Once this limit is reached, no new matches will be added.
    """

    matches: List[ChainMatch] = field(default_factory=list)
    dedup_mode: str = DEFAULT_DEDUP_MODE_COLLECTOR
    max_matches: int = DEFAULT_MAX_MATCHES_PER_COLLECTOR
    # Internal O(1) dedup indexes (kept out of repr/init)
    _exact_keys: Set[Tuple[Any, ...]] = field(
        default_factory=set, init=False, repr=False
    )
    _role_keys: Set[Tuple[Any, ...]] = field(
        default_factory=set, init=False, repr=False
    )

    def __post_init__(self: Self) -> None:
        """
        Validate collector configuration after initialisation.
        """
        self._validate_or_raise()

    def make_dedup_key(self: Self, match: ChainMatch) -> Tuple[Any, ...]:
        """
        Build a stable deduplication key for role-based deduplication.

        Args:
            match (ChainMatch): The match for which to build a key.

        Returns:
            Tuple[Any, ...]: A deterministic key representing the semantic identity
            of the match under role-based deduplication.
        """
        role_items = tuple(sorted(match.role_to_token_id.items()))
        return (match.pattern_name, match.sentence_index, role_items)

    def _make_exact_key(self: Self, match: ChainMatch) -> Tuple[Any, ...]:
        """Stable exact-match key for O(1) exact deduplication."""
        role_items = tuple(sorted(match.role_to_token_id.items()))
        return (
            match.pattern_name,
            match.sentence_index,
            role_items,
            match.matched_text,
        )

    def is_duplicate(self: Self, match: ChainMatch) -> bool:
        """
        Check whether `match` is already present according to current strategy.

        Args:
            match (ChainMatch): Candidate match to test.

        Returns:
            bool: True if duplicate, False otherwise.
        """
        if self.dedup_mode == "none":
            return False

        if self.dedup_mode == "exact":
            return self._make_exact_key(match) in self._exact_keys

        if self.dedup_mode == "role_based":
            return self.make_dedup_key(match) in self._role_keys

        # Defensive fallback; should be unreachable due to validation.
        raise ValueError(f"Unsupported dedup_mode: {self.dedup_mode}")

    def add(self: Self, match: ChainMatch) -> bool:
        """
        Add a match if capacity allows and deduplication does not reject it.

        Args:
            match (ChainMatch): Match candidate to add.

        Returns:
            bool: True if added, False if rejected.
        """
        if len(self.matches) >= self.max_matches:
            return False

        if self.is_duplicate(match):
            return False

        self.matches.append(match)
        # Update internal indexes for fast dedup checks
        try:
            self._exact_keys.add(self._make_exact_key(match))
        except Exception:
            pass
        try:
            self._role_keys.add(self.make_dedup_key(match))
        except Exception:
            pass
        return True

    def extend(self: Self, new_matches: Iterable[ChainMatch]) -> int:
        """
        Add multiple matches in sequence.

        Args:
            new_matches (Iterable[ChainMatch]): Iterable of match candidates.

        Returns:
            int: Number of matches successfully added.
        """
        added_count = 0
        for match in new_matches:
            if self.add(match):
                added_count += 1
        return added_count

    def count(self: Self) -> int:
        """
        Return the number of stored matches.

        Returns:
            int: Number of accepted matches currently stored.
        """
        return len(self.matches)

    def clear(self: Self) -> None:
        """
        Remove all collected matches.
        """
        self.matches.clear()
        self._exact_keys.clear()
        self._role_keys.clear()

    def all(self: Self) -> List[ChainMatch]:
        """
        Return all stored matches in insertion order.

        Returns:
            List[ChainMatch]: Shallow copy of stored matches.
        """
        return list(self.matches)

    def summary(self: Self) -> Dict[str, int]:
        """
        Build a compact summary of collected matches.

        Returns:
            Dict[str, int]: Summary map containing total count and per-pattern counts.
        """
        summary_data: Dict[str, int] = {"total": len(self.matches)}
        for match in self.matches:
            key = f"pattern::{match.pattern_name}"
            summary_data[key] = summary_data.get(key, 0) + 1
        return summary_data

    def to_output_rows(self: Self) -> List[Dict[str, Any]]:
        """
        Convert all matches to output dictionaries.

        Returns:
            List[Dict[str, Any]]: Output rows suitable for saving/reporting.
        """
        return [match.to_output_row() for match in self.matches]

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if self.dedup_mode not in VALID_DEDUP_MODES:
            raise ValueError(f"dedup_mode must be one of {VALID_DEDUP_MODES}.")

        if not isinstance(self.max_matches, int) or self.max_matches <= 0:
            raise ValueError("max_matches must be a positive integer.")

        if not isinstance(self.matches, list) or not all(
            isinstance(match, ChainMatch) for match in self.matches
        ):
            raise TypeError("matches must be a list of ChainMatch objects.")
