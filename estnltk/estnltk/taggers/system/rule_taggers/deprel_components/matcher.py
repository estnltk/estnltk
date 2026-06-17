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
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import PathPattern
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    ChainMatch,
    MatchCollector,
)
from estnltk.taggers.system.rule_taggers.deprel_components.config import (
    DEFAULT_MAX_MATCHES_PER_SENTENCE,
    DEFAULT_DEDUP_MODE_MATCHER,
    VALID_DEDUP_MODES,
)


@dataclass(slots=True)
class DepChainMatcher:
    """
    Match dependency path patterns against one sentence-level syntax graph.

    This class performs the core graph-search phase of the pipeline:
    1. choose anchor-node candidates,
    2. expand the pattern step-by-step along dependency edges,
    3. materialise successful paths as `ChainMatch` objects,
    4. deduplicate/limit matches via `MatchCollector`.

    ## Attributes:
    - **patterns** (`Tuple[PathPattern, ...]`): A tuple of PathPattern objects that define the patterns to match against the syntax graph.
    - **dedup_mode** (`str`): The deduplication mode to use when collecting matches. Allowed values are "none" (no deduplication), "exact" (deduplicate based on exact match of `ChainMatch`), and "role_based" (deduplicate based on the combination of pattern name, sentence index, and role-to-token ID mapping).
    - **max_matches_per_sentence** (`int`): The maximum number of matches to collect for each sentence. Once this limit is reached, no new matches will be added for that sentence.
    - **allow_role_node_overlap** (`bool`): Whether to allow matches where the same node in the syntax graph is assigned to multiple roles in the pattern. If False, matches where a single node would be assigned to more than one role will be rejected. This can help prevent semantically confusing matches but may also exclude valid cases where a node legitimately fulfills multiple roles.
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
        """
        Match all configured patterns against one sentence graph.

        Args:
            graph_index (SyntaxGraphIndex): Sentence-level dependency graph.
            sentence_index (int): Zero-based sentence index in the source text.
            sentence_span (Optional[Tuple[int, int]], optional): Sentence
                character span override. If None, uses graph metadata when
                available.
        Returns:
            List[ChainMatch]: Accepted matches in insertion order.
        """
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
        Match one path pattern against one sentence graph.

        Args:
            pattern (PathPattern): Pattern to match.
            graph_index (SyntaxGraphIndex): Sentence-level dependency graph.
            sentence_index (int): Zero-based sentence index in the source text.
            sentence_span (Optional[Tuple[int, int]], optional): Sentence
                character span override.

        Returns:
            List[ChainMatch]: All successful matches for this pattern.
        """
        anchor_index = self._get_anchor_index(pattern)
        anchor_constraint = pattern.node_steps[anchor_index]

        resolved_sentence_span = self._resolve_sentence_span(
            graph_index=graph_index,
            sentence_span=sentence_span,
        )

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
                        sentence_span=resolved_sentence_span,
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
        if len(assigned_nodes_by_index) == len(pattern.node_steps):
            yield (dict(assigned_nodes_by_index), dict(assigned_edge_by_index))
            return

        options = self._get_frontier_options(
            pattern=pattern,
            assigned_nodes_by_index=assigned_nodes_by_index,
        )
        if not options:
            return

        # Picking the smallest index first keeps search deterministic.
        options.sort(key=lambda item: item[0])
        target_index, known_index, edge_index = options[0]

        node_constraint = pattern.node_steps[target_index]
        known_node = assigned_nodes_by_index[known_index]

        if target_index == known_index + 1:
            candidate_pairs = self._enumerate_from_node(
                graph_index=graph_index,
                source_node=known_node,
                edge_constraint=pattern.edge_steps[edge_index],
            )
        else:
            candidate_pairs = self._enumerate_sources_to_target(
                graph_index=graph_index,
                target_node=known_node,
                edge_constraint=pattern.edge_steps[edge_index],
            )

        used_token_ids = {
            self._get_node_id(node) for node in assigned_nodes_by_index.values()
        }

        for candidate_node, edge_context in candidate_pairs:
            if not node_constraint.matches(candidate_node):
                continue

            # Enforce one token per role unless overlap is explicitly allowed.
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

    def _get_frontier_options(
        self: Self,
        pattern: PathPattern,
        assigned_nodes_by_index: Dict[int, Span],
    ) -> List[Tuple[int, int, int]]:
        """
        Find one-step expansion options around currently assigned indices.

        Returns tuples in the form `(target_index, known_index, edge_index)`.
        """
        options: List[Tuple[int, int, int]] = []
        last_node_index = len(pattern.node_steps) - 1

        for known_index in assigned_nodes_by_index:
            right_index = known_index + 1
            if (
                right_index <= last_node_index
                and right_index not in assigned_nodes_by_index
            ):
                options.append((right_index, known_index, known_index))

            left_index = known_index - 1
            if left_index >= 0 and left_index not in assigned_nodes_by_index:
                options.append((left_index, known_index, left_index))

        return options

    def _enumerate_from_node(
        self: Self,
        graph_index: SyntaxGraphIndex,
        source_node: Span,
        edge_constraint: EdgeConstraint,
    ) -> List[Tuple[Span, EdgeContext]]:
        """
        Enumerate candidate target nodes reachable from `source_node`.

        Each candidate is returned together with the concrete `EdgeContext` that
        satisfied `edge_constraint`.

        Args:
            graph_index (SyntaxGraphIndex): Sentence-level dependency graph.
            source_node (Span): Node from which to enumerate.
            edge_constraint (EdgeConstraint): Constraint the edge must satisfy.
        """
        candidates: List[Tuple[Span, EdgeContext]] = []
        min_hops, max_hops = self._resolve_hop_bounds(
            graph_index=graph_index,
            min_hops=edge_constraint.min_hops,
            max_hops=edge_constraint.max_hops,
        )

        for direction in self._directions_to_try(edge_constraint.direction):
            for hops in range(min_hops, max_hops + 1):
                for node in self._nodes_at_exact_hops(
                    graph_index=graph_index,
                    start_node=source_node,
                    direction=direction,
                    hops=hops,
                ):
                    edge_context = self._build_edge_context(
                        direction=direction,
                        hops=hops,
                    )
                    if edge_constraint.matches(edge_context):
                        candidates.append((node, edge_context))
        return candidates

    def _enumerate_sources_to_target(
        self: Self,
        graph_index: SyntaxGraphIndex,
        target_node: Span,
        edge_constraint: EdgeConstraint,
    ) -> List[Tuple[Span, EdgeContext]]:
        """
        Enumerate candidate source nodes that can reach `target_node`.

        This is used when filling pattern steps to the left of the anchor index.
        Instead of iterating over every node in the graph (O(n²)), we reverse
        the edge direction and look up the target's neighbours directly.

        For single-hop edges (the common case) this is O(children + 1).
        For multi-hop edges we find candidate sources via reverse traversal,
        then verify each with a single forward call to `_enumerate_from_node`.

        Args:
            graph_index (SyntaxGraphIndex): Sentence-level dependency graph.
            target_node (Span): The target node to reach.
            edge_constraint (EdgeConstraint): Constraint the edge must satisfy.
        """
        candidates: List[Tuple[Span, EdgeContext]] = []
        min_hops, max_hops = self._resolve_hop_bounds(
            graph_index=graph_index,
            min_hops=edge_constraint.min_hops,
            max_hops=edge_constraint.max_hops,
        )
        for direction in self._directions_to_try(edge_constraint.direction):
            for hops in range(min_hops, max_hops + 1):
                # ── Fast path: single-hop direct lookups ──────────────
                if hops == 1 and direction == DirectionMode.UP:
                    # source --UP(1)--> target  ⇒  source is a child of target
                    for source_node in graph_index.get_children(
                        self._get_node_id(target_node)
                    ):
                        edge_context = self._build_edge_context(
                            direction=DirectionMode.UP,
                            hops=1,
                        )
                        if edge_constraint.matches(edge_context):
                            candidates.append((source_node, edge_context))
                    continue

                if hops == 1 and direction == DirectionMode.DOWN:
                    # source --DOWN(1)--> target  ⇒  source is the parent of target
                    source_node = graph_index.get_parent(self._get_node_id(target_node))
                    if source_node is not None:
                        edge_context = self._build_edge_context(
                            direction=DirectionMode.DOWN,
                            hops=1,
                        )
                        if edge_constraint.matches(edge_context):
                            candidates.append((source_node, edge_context))
                    continue

                # ── General path: multi-hop reverse traversal ─────────
                # Find candidate sources by walking the *reverse* direction
                # from the target, then verify each with a forward traversal
                # to obtain the correct edge context (deprel of last hop).
                if direction == DirectionMode.UP:
                    reverse_direction = DirectionMode.DOWN
                else:
                    reverse_direction = DirectionMode.UP

                source_pairs = self._nodes_at_exact_hops(
                    graph_index=graph_index,
                    start_node=target_node,
                    direction=reverse_direction,
                    hops=hops,
                )
                for source_node in source_pairs:
                    # In a tree, the backward path guarantees the forward path.
                    edge_context = self._build_edge_context(
                        direction=direction,
                        hops=hops,
                    )
                    if edge_constraint.matches(edge_context):
                        candidates.append((source_node, edge_context))

        return candidates

    def _nodes_at_exact_hops(
        self: Self,
        graph_index: SyntaxGraphIndex,
        start_node: Span,
        direction: DirectionMode,
        hops: int,
    ) -> List[Span]:
        """
        Return all nodes reachable from `start_node` at exactly `hops`.

        Returns:
            List[Span]: List of reachable nodes.
            `(reachable_node)`.
        """
        if hops == 0:
            return [start_node]

        if direction == DirectionMode.UP:
            current_node = start_node
            for _ in range(hops):
                parent_node = graph_index.get_parent(self._get_node_id(current_node))
                if parent_node is None:
                    return []
                current_node = parent_node
            return [current_node]

        if direction == DirectionMode.DOWN:
            results: List[Span] = []

            def _dfs_down(
                node: Span,
                remaining_hops: int,
            ) -> None:
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

        raise ValueError(f"Unsupported direction: {direction}")

    def _resolve_hop_bounds(
        self: Self,
        graph_index: SyntaxGraphIndex,
        min_hops: Optional[int],
        max_hops: Optional[int],
    ) -> Tuple[int, int]:
        """
        Resolve hop bounds into concrete finite integers for traversal.

        If max bound is unbounded, it is capped by sentence token count.
        """
        lower = 0 if min_hops is None else min_hops
        sentence_size = max(0, len(graph_index.token_order))
        upper = sentence_size if max_hops is None else max_hops

        if lower > upper:
            return (1, 0)
        return (lower, upper)

    def _directions_to_try(
        self: Self, direction: DirectionMode
    ) -> Tuple[DirectionMode, ...]:
        """
        Expand one configured direction into concrete search directions.
        """
        if direction == DirectionMode.BOTH:
            return (DirectionMode.UP, DirectionMode.DOWN)
        return (direction,)

    def _build_edge_context(
        self: Self,
        direction: DirectionMode,
        hops: int,
    ) -> EdgeContext:
        """
        Create an `EdgeContext` instance for edge constraint checks.
        """
        edge_context = EdgeContext(
            direction=direction,
            hops=hops,
        )
        return edge_context

    def _get_node_id(self: Self, node: Span) -> int:
        """
        Read a node ID from estnltk span-like annotations as an integer.
        """
        return int(getattr(node, "id"))

    def _build_chain_match(
        self: Self,
        pattern: PathPattern,
        sentence_index: int,
        sentence_span: Tuple[int, int],
        assigned_nodes_by_index: Dict[int, Span],
        assigned_edge_by_index: Dict[int, EdgeContext],
    ) -> ChainMatch:
        """
        Convert a completed assignment into one `ChainMatch` object.
        """
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
            if not edge_constraint.matches(edge_context):
                raise ValueError(
                    "Internal matcher error: assigned edge context no longer satisfies edge constraint."
                )
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
        """
        Find the index of the anchor role in `pattern.node_steps`.
        """
        for node_index, node_constraint in enumerate(pattern.node_steps):
            if node_constraint.role == pattern.anchor_role:
                return node_index
        raise ValueError(
            f"anchor_role '{pattern.anchor_role}' not found in pattern node_steps."
        )

    def _resolve_sentence_span(
        self: Self,
        graph_index: SyntaxGraphIndex,
        sentence_span: Optional[Tuple[int, int]],
    ) -> Tuple[int, int]:
        """
        Resolve sentence span from method input or graph metadata.
        """
        if sentence_span is not None:
            return sentence_span
        if graph_index.sentence_span is not None:
            return graph_index.sentence_span
        return (0, 0)

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.patterns, tuple) or not all(
            isinstance(pattern, PathPattern) for pattern in self.patterns
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
