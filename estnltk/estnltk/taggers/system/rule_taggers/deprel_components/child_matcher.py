from typing import (
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Self,
)
from dataclasses import dataclass
from estnltk import Span

from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    DirectionMode,
    EdgeContext,
)
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    PathPattern,
    ChainMatch,
    MatchCollector,
)
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
)
from estnltk.taggers.system.rule_taggers.deprel_components.config import (
    DEFAULT_MAX_MATCHES_PER_SENTENCE,
    DEFAULT_DEDUP_MODE_MATCHER,
    VALID_DEDUP_MODES,
)


@dataclass(slots=True)
class DepChildMatcher:
    """
    Lightweight matcher specialised for child/descendant-only patterns.

    This scaffold intentionally supports a restricted subset of patterns:
    - the `anchor_role` must correspond to the first node in `node_steps`
      (anchor at index 0), and
    - all other nodes must be reachable by traversing children from the
      anchor (downwards).  The class emits the same `ChainMatch` objects
    as `DepChainMatcher` so the rest of the pipeline (decorator,
    orchestrator) can be reused unchanged.
    """

    patterns: Tuple[PathPattern, ...]
    dedup_mode: str = DEFAULT_DEDUP_MODE_MATCHER
    max_matches_per_sentence: int = DEFAULT_MAX_MATCHES_PER_SENTENCE
    allow_role_node_overlap: bool = False

    def __post_init__(self: Self) -> None:
        """
        Validate matcher configuration after initialisation.
        """
        self._validate_or_raise()

    def match_sentence(
        self: Self,
        graph_index: SyntaxGraphIndex,
        sentence_index: int,
        sentence_span: Optional[Tuple[int, int]] = None,
    ) -> List[ChainMatch]:
        collector = MatchCollector(
            dedup_mode=self.dedup_mode,
            max_matches=self.max_matches_per_sentence,
        )

        for pattern in self.patterns:
            pattern_matches = self.match_pattern_in_sentence(
                pattern=pattern,
                graph_index=graph_index,
                sentence_index=sentence_index,
                sentence_span=sentence_span,
            )
            collector.extend(pattern_matches)

        return collector.all()

    def match_pattern_in_sentence(
        self: Self,
        pattern: PathPattern,
        graph_index: SyntaxGraphIndex,
        sentence_index: int,
        sentence_span: Optional[Tuple[int, int]] = None,
    ) -> List[ChainMatch]:
        """
        Match one path pattern against the sentence graph, but only via
        downward traversals from the anchor node.  Currently requires the
        anchor to be at index 0 in `pattern.node_steps`.
        """
        anchor_index = self._get_anchor_index(pattern)
        if anchor_index != 0:
            raise ValueError(
                "DepChildMatcher currently requires the anchor role to be the first node (index 0)."
            )

        anchor_constraint = pattern.node_steps[anchor_index]

        matches: List[ChainMatch] = []
        for anchor_node in graph_index.iter_nodes():
            if not anchor_constraint.matches(anchor_node):
                continue

            initial_nodes: Dict[int, Span] = {anchor_index: anchor_node}
            initial_edges: Dict[int, EdgeContext] = {}

            for assigned_nodes, assigned_edges in self._expand_assignments(
                pattern=pattern,
                graph_index=graph_index,
                assigned_nodes_by_index=initial_nodes,
                assigned_edge_by_index=initial_edges,
            ):
                matches.append(
                    self._build_chain_match(
                        pattern=pattern,
                        sentence_index=sentence_index,
                        sentence_span=sentence_span
                        or graph_index.sentence_span
                        or (0, 0),
                        assigned_nodes_by_index=assigned_nodes,
                        assigned_edge_by_index=assigned_edges,
                    )
                )
                # Stop early if we've reached the maximum matches per sentence.
                if len(matches) >= self.max_matches_per_sentence:
                    return matches

        return matches

    def _expand_assignments(
        self: Self,
        pattern: PathPattern,
        graph_index: SyntaxGraphIndex,
        assigned_nodes_by_index: Dict[int, Span],
        assigned_edge_by_index: Dict[int, EdgeContext],
    ) -> Iterator[Tuple[Dict[int, Span], Dict[int, EdgeContext]]]:
        """
        Recursively expand a partial assignment until all pattern steps are set.

        Args:
            pattern (PathPattern): Pattern being matched.
            graph_index (SyntaxGraphIndex): Sentence-level dependency graph.
            assigned_nodes_by_index (Dict[int, Span]): Current partial
                node assignment keyed by `node_steps` index.
            assigned_edge_by_index (Dict[int, EdgeContext]): Current partial
                edge assignment keyed by `edge_steps` index.
        Yields:
            Tuple[Dict[int, Span], Dict[int, EdgeContext]]: A complete
                assignment of nodes and edges that satisfies the pattern.
        """
        # Completion condition
        if len(assigned_nodes_by_index) == len(pattern.node_steps):
            yield (dict(assigned_nodes_by_index), dict(assigned_edge_by_index))
            return

        # Only expand to the right (higher index) because this matcher is
        # anchored at index 0 and only considers descendants.
        options = []
        for known_index in assigned_nodes_by_index:
            target_index = known_index + 1
            if (
                target_index < len(pattern.node_steps)
                and target_index not in assigned_nodes_by_index
            ):
                options.append((target_index, known_index, known_index))

        if not options:
            return

        # deterministic: pick smallest target index first
        options.sort(key=lambda item: item[0])
        target_index, known_index, edge_index = options[0]

        node_constraint = pattern.node_steps[target_index]
        known_node = assigned_nodes_by_index[known_index]

        candidate_pairs = self._enumerate_from_node(
            graph_index=graph_index,
            source_node=known_node,
            edge_constraint=pattern.edge_steps[edge_index],
        )

        used_token_ids = {
            self._get_node_id(node) for node in assigned_nodes_by_index.values()
        }

        for candidate_node, edge_context in candidate_pairs:
            if not node_constraint.matches(candidate_node):
                continue

            if (
                not self.allow_role_node_overlap
                and self._get_node_id(candidate_node) in used_token_ids
            ):
                continue

            next_nodes = dict(assigned_nodes_by_index)
            next_nodes[target_index] = candidate_node

            next_edges = dict(assigned_edge_by_index)
            next_edges[edge_index] = edge_context

            yield from self._expand_assignments(
                pattern=pattern,
                graph_index=graph_index,
                assigned_nodes_by_index=next_nodes,
                assigned_edge_by_index=next_edges,
            )

    def _enumerate_from_node(
        self: Self,
        graph_index: SyntaxGraphIndex,
        source_node: Span,
        edge_constraint: EdgeConstraint,
    ) -> List[Tuple[Span, EdgeContext]]:
        candidates: List[Tuple[Span, EdgeContext]] = []
        min_hops, max_hops = self._resolve_hop_bounds(
            graph_index=graph_index,
            min_hops=edge_constraint.min_hops,
            max_hops=edge_constraint.max_hops,
        )

        # If the edge_constraint allows BOTH, try DOWN.
        for direction in (DirectionMode.DOWN,):
            for hops in range(min_hops, max_hops + 1):
                for node in self._nodes_at_exact_hops(
                    graph_index=graph_index,
                    start_node=source_node,
                    direction=direction,
                    hops=hops,
                ):
                    edge_context = EdgeContext(
                        direction=DirectionMode.DOWN,
                        hops=hops,
                    )
                    if edge_constraint.matches(edge_context):
                        candidates.append((node, edge_context))

        return candidates

    def _nodes_at_exact_hops(
        self: Self,
        graph_index: SyntaxGraphIndex,
        start_node: Span,
        direction: DirectionMode,
        hops: int,
    ) -> List[Span]:
        if hops == 0:
            return [start_node]

        if direction == DirectionMode.DOWN:
            results: List[Span] = []

            def _dfs_down(
                node: Span,
                remaining_hops: int,
            ):
                if remaining_hops == 0:
                    results.append(node)
                    return
                for child_node in graph_index.get_children(self._get_node_id(node)):
                    _dfs_down(
                        node=child_node,
                        remaining_hops=remaining_hops - 1,
                    )

            _dfs_down(start_node, hops)
            return results

        # UP and BOTH are not supported in this simplified matcher
        raise ValueError(
            "DepChildMatcher only supports DOWN traversals in this scaffold."
        )

    def _resolve_hop_bounds(
        self: Self,
        graph_index: SyntaxGraphIndex,
        min_hops: Optional[int],
        max_hops: Optional[int],
    ) -> Tuple[int, int]:
        lower = 0 if min_hops is None else min_hops
        sentence_size = max(0, len(graph_index.token_order))
        upper = sentence_size if max_hops is None else max_hops

        if lower > upper:
            return (1, 0)
        return (lower, upper)

    def _get_node_id(self: Self, node: Span) -> int:
        return int(getattr(node, "id"))

    def _build_chain_match(
        self: Self,
        pattern: PathPattern,
        sentence_index: int,
        sentence_span: Tuple[int, int],
        assigned_nodes_by_index: Dict[int, Span],
        assigned_edge_by_index: Dict[int, EdgeContext],
    ) -> ChainMatch:
        role_to_node: Dict[str, Span] = {}
        role_to_token_id: Dict[str, int] = {}

        for node_index, node_constraint in enumerate(pattern.node_steps):
            node = assigned_nodes_by_index[node_index]
            role_to_node[node_constraint.role] = node
            role_to_token_id[node_constraint.role] = self._get_node_id(node)

        traversed_edges: List[Tuple[str, str, EdgeContext]] = []
        for edge_index, edge_constraint in enumerate(pattern.edge_steps):
            from_role = pattern.node_steps[edge_index].role
            to_role = pattern.node_steps[edge_index + 1].role
            edge_context = assigned_edge_by_index[edge_index]
            traversed_edges.append((from_role, to_role, edge_context))

        emit_roles = pattern.emit_roles or ()
        matched_text = " ".join(
            getattr(role_to_node[role], "text", "") for role in emit_roles
        ).strip()

        return ChainMatch(
            pattern_name=pattern.name,
            sentence_index=sentence_index,
            sentence_span=sentence_span,
            role_to_token_id=role_to_token_id,
            role_to_node=role_to_node,
            traversed_edges=tuple(traversed_edges),
            matched_text=matched_text,
        )

    def _get_anchor_index(self: Self, pattern: PathPattern) -> int:
        for node_index, node_constraint in enumerate(pattern.node_steps):
            if node_constraint.role == pattern.anchor_role:
                return node_index
        raise ValueError(
            f"anchor_role '{pattern.anchor_role}' not found in pattern node_steps."
        )

    def _validate_or_raise(self: Self) -> None:
        if not isinstance(self.patterns, tuple) or not all(
            isinstance(p, PathPattern) for p in self.patterns
        ):
            raise TypeError("patterns must be a tuple of PathPattern objects.")

        if self.dedup_mode not in VALID_DEDUP_MODES:
            raise ValueError(f"dedup_mode must be one of {VALID_DEDUP_MODES}.")

        if (
            not isinstance(self.max_matches_per_sentence, int)
            or self.max_matches_per_sentence <= 0
        ):
            raise ValueError("max_matches_per_sentence must be a positive integer.")

        if not isinstance(self.allow_role_node_overlap, bool):
            raise TypeError("allow_role_node_overlap must be a boolean value.")
