from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Iterable,
    Self,
    Any,
)
from dataclasses import dataclass

from estnltk import Layer

from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import PathPattern
from estnltk.taggers.system.rule_taggers.deprel_components.matcher import (
    DepChainMatcher,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    MatchCollector,
    ChainMatch,
)
from estnltk.taggers.system.rule_taggers.deprel_components.serializer import (
    ChainMatchSerializer,
)
from estnltk.taggers.system.rule_taggers.deprel_components.config import (
    DEFAULT_MAX_MATCHES_PER_SENTENCE,
    DEFAULT_MAX_TOTAL_MATCHES,
    DEFAULT_DEDUP_MODE_SENTENCE,
    DEFAULT_DEDUP_MODE_GLOBAL,
    VALID_DEDUP_MODES,
)


@dataclass(slots=True)
class DepTaggerOrchestrator:
    """
    End-to-end orchestrator for dependency-chain tagging on sentence layers.

    The class owns the high-level pipeline:
    1. build sentence-level `SyntaxGraphIndex` objects,
    2. run `DepChainMatcher` on each sentence,
    3. optionally deduplicate across all sentence matches,
    4. transform matches into relational output rows with `ChainMatchSerializer`.

    ## Attributes:
    - **patterns** (`Tuple[PathPattern, ...]`): A tuple of PathPattern objects that define the patterns to match against the syntax graphs.
    - **matcher** (`Optional[DepChainMatcher]`): Optional pre-configured matcher instance. If None, a default matcher will be constructed from `patterns` and related configuration.
    - **serializer** (`Optional[ChainMatchSerializer]`): Optional pre-configured serializer instance. If None, a default serializer with standard settings will be constructed.
    - **sentence_match_dedup_mode** (`str`): Deduplication mode to apply within each sentence's matches. Allowed values are "none", "exact", and "role_based". This controls how matches that are similar within the same sentence are filtered before being returned.
    - **max_matches_per_sentence** (`int`): Maximum number of matches to accept for each individual sentence. This can help prevent combinatorial explosion in very complex sentences.
    - **allow_role_node_overlap** (`bool`): Whether to allow matches where the same node in the syntax graph is assigned to multiple roles in the pattern. This setting is passed down to the matcher and can help control match quality.
    - **global_dedup_mode** (`str`): Deduplication mode to apply across all matches from all sentences. Allowed values are "none", "exact", and "role_based". This controls how matches that are similar across different sentences are filtered before being returned by `tag_sentence_layers`.
    - **max_total_matches** (`int`): Maximum total number of matches to return across all sentences. This can help prevent memory issues when processing large documents with many matches.
    """

    patterns: Tuple[PathPattern, ...]
    matcher: Optional[Any] = None
    serializer: Optional[ChainMatchSerializer] = None
    sentence_match_dedup_mode: str = DEFAULT_DEDUP_MODE_SENTENCE
    max_matches_per_sentence: int = DEFAULT_MAX_MATCHES_PER_SENTENCE
    allow_role_node_overlap: bool = False
    global_dedup_mode: str = DEFAULT_DEDUP_MODE_GLOBAL
    max_total_matches: int = DEFAULT_MAX_TOTAL_MATCHES

    def __post_init__(self: Self) -> None:
        """
        Validate configuration and construct default components when needed.
        """
        self._validate_or_raise()

        if self.matcher is None:
            self.matcher = DepChainMatcher(
                patterns=self.patterns,
                dedup_mode=self.sentence_match_dedup_mode,
                max_matches_per_sentence=self.max_matches_per_sentence,
                allow_role_node_overlap=self.allow_role_node_overlap,
            )

        if self.serializer is None:
            self.serializer = ChainMatchSerializer()

    def tag_sentence_layers(
        self: Self,
        sentence_syntax_layers: Iterable[Layer],
        sentence_spans: Optional[Iterable[Tuple[int, int]]] = None,
    ) -> List[ChainMatch]:
        """
        Run dependency-chain matching over sentence-level syntax layers.

        Args:
            sentence_syntax_layers (Iterable[Layer]): Iterable of
                per-sentence syntax layers (e.g., split `stanza_syntax`).
            sentence_spans (Optional[Iterable[Tuple[int, int]]], optional):
                Optional sentence character spans aligned with input order.

        Returns:
            List[ChainMatch]: Accepted matches after optional global dedup.
        """
        layers = list(sentence_syntax_layers)
        spans = list(sentence_spans) if sentence_spans is not None else None

        if spans is not None and len(spans) != len(layers):
            raise ValueError(
                "sentence_spans length must match sentence_syntax_layers length."
            )

        global_collector = MatchCollector(
            dedup_mode=self.global_dedup_mode,
            max_matches=self.max_total_matches,
        )
        matcher = self._get_matcher()

        for sentence_index, sentence_layer in enumerate(layers):
            sentence_span = spans[sentence_index] if spans is not None else None

            # Build a sentence-local graph index and match patterns in isolation.
            graph_index = SyntaxGraphIndex(
                stanza_syntax_layer=sentence_layer,
                sentence_id=sentence_index,
                sentence_span=sentence_span,
            )

            sentence_matches = matcher.match_sentence(
                graph_index=graph_index,
                sentence_index=sentence_index,
                sentence_span=sentence_span,
            )

            global_collector.extend(sentence_matches)
            if global_collector.count() >= self.max_total_matches:
                break

        return global_collector.all()

    def tag_sentence_layer(
        self: Self,
        sentence_syntax_layer: Layer,
        sentence_index: int = 0,
        sentence_span: Optional[Tuple[int, int]] = None,
    ) -> List[ChainMatch]:
        """
        Convenience wrapper for matching one sentence syntax layer.

        Args:
            sentence_syntax_layer (Layer): One sentence syntax layer.
            sentence_index (int, optional): Sentence index to stamp into
                results. Defaults to 0.
            sentence_span (Optional[Tuple[int, int]], optional): Optional
                sentence span override.

        Returns:
            List[ChainMatch]: Matches found in the given sentence.
        """
        graph_index = SyntaxGraphIndex(
            stanza_syntax_layer=sentence_syntax_layer,
            sentence_id=sentence_index,
            sentence_span=sentence_span,
        )
        matcher = self._get_matcher()
        return matcher.match_sentence(
            graph_index=graph_index,
            sentence_index=sentence_index,
            sentence_span=sentence_span,
        )

    def serialize_matches(
        self: Self, matches: Iterable[ChainMatch]
    ) -> List[Dict[str, Any]]:
        """
        Serialize existing matches into relational output rows.

        Args:
            matches (Iterable[ChainMatch]): Match objects to serialize.

        Returns:
            List[Dict[str, Any]]: Serialized rows ready for output layers/files.
        """
        serializer = self._get_serializer()
        return serializer.serialize_matches(matches)

    def tag_and_serialize_sentence_layers(
        self: Self,
        sentence_syntax_layers: Iterable[Layer],
        sentence_spans: Optional[Iterable[Tuple[int, int]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run full pipeline and return serialized relational rows.

        Args:
            sentence_syntax_layers (Iterable[Layer]): Iterable of
                per-sentence syntax layers.
            sentence_spans (Optional[Iterable[Tuple[int, int]]], optional):
                Optional aligned sentence spans.

        Returns:
            List[Dict[str, Any]]: Serialized output rows.
        """
        matches = self.tag_sentence_layers(
            sentence_syntax_layers=sentence_syntax_layers,
            sentence_spans=sentence_spans,
        )
        serializer = self._get_serializer()
        return serializer.serialize_matches(matches)

    def _get_matcher(self: Self) -> Any:
        """
        Return configured matcher as non-optional instance.
        """
        if self.matcher is None:
            raise RuntimeError("matcher is not initialised.")
        return self.matcher

    def _get_serializer(self: Self) -> ChainMatchSerializer:
        """
        Return configured serializer as non-optional instance.
        """
        if self.serializer is None:
            raise RuntimeError("serializer is not initialised.")
        return self.serializer

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.patterns, tuple) or not all(
            isinstance(pattern, PathPattern) for pattern in self.patterns
        ):
            raise TypeError("patterns must be a tuple of PathPattern objects.")

        if self.matcher is not None:
            if not hasattr(self.matcher, "match_sentence"):
                raise TypeError(
                    "matcher must provide a match_sentence method or be None."
                )
            if not hasattr(self.matcher, "patterns"):
                raise TypeError("matcher must expose patterns or be None.")

        if self.serializer is not None and not isinstance(
            self.serializer, ChainMatchSerializer
        ):
            raise TypeError("serializer must be a ChainMatchSerializer or None.")

        if self.sentence_match_dedup_mode not in VALID_DEDUP_MODES:
            raise ValueError(
                f"sentence_match_dedup_mode must be one of {VALID_DEDUP_MODES}."
            )
        if self.global_dedup_mode not in VALID_DEDUP_MODES:
            raise ValueError(f"global_dedup_mode must be one of {VALID_DEDUP_MODES}.")

        if (
            not isinstance(self.max_matches_per_sentence, int)
            or self.max_matches_per_sentence <= 0
        ):
            raise ValueError("max_matches_per_sentence must be a positive integer.")

        if not isinstance(self.max_total_matches, int) or self.max_total_matches <= 0:
            raise ValueError("max_total_matches must be a positive integer.")

        if not isinstance(self.allow_role_node_overlap, bool):
            raise TypeError("allow_role_node_overlap must be a boolean value.")

        if self.matcher is not None and self.matcher.patterns != self.patterns:
            raise ValueError(
                "matcher.patterns must be the same as the orchestrator patterns."
            )
