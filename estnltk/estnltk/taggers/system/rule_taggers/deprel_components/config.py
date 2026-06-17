"""
Centralised configuration constants for the dep_chain_tagger package.

Every default value, limit, heuristic weight, and sentinel used across the
package is defined here so that:
  * users can discover and override defaults in one place,
  * adding a new dedup mode / missing marker / output attribute requires
    editing only this file,
  * the constants can be imported into tests for deterministic assertions.

Constants are intentionally *module-level* (not class-level) so that they can
be referenced before any class is instantiated.
"""

SEED = 42
"""Default random seed for reproducibility.  Override this at the start of your script or notebook if you want a different seed."""

# ──────────────────────────────────────────────────────────────
# 1.  ValueCondition — missing-value sentinels
# ──────────────────────────────────────────────────────────────
DEFAULT_MISSING_MARKERS: tuple = (None, "", "_")
"""
Tuple of values that `ValueCondition._is_missing()` treats as absent.

Extend or replace this when working with corpora that use alternative
missing-value conventions (e.g. ``"NA"``, ``"--"``, ``"null"``).

Example::

    from dep_chain_tagger.config import DEFAULT_MISSING_MARKERS
    markers = DEFAULT_MISSING_MARKERS + ("NA", "--")
    cond = ValueCondition(mode=ConditionMode.EXACT, value="N",
                          allow_missing=True, missing_markers=markers)
"""

# ──────────────────────────────────────────────────────────────
# 2.  NodeConstraint — selectivity scoring weights
# ──────────────────────────────────────────────────────────────
SELECTIVITY_WEIGHT_EXACT: float = 1.0
"""Score added when a ValueCondition or FeatureCondition uses EXACT mode.
EXACT is the most selective mode because it pins one specific value, so it gets the highest weight.
"""

SELECTIVITY_WEIGHT_NEGATION: float = 0.5
"""Score added when a ValueCondition or FeatureCondition uses NEGATION mode.
NEGATION is less selective than EXACT because it only excludes one value, while EXACT pins one value.
"""

SELECTIVITY_WEIGHT_EXTRA_PREDICATE: float = 0.5
"""Score added per extra predicate in `NodeConstraint.extra_predicates`.
Extra predicates are user-defined functions that can check any property of the node, so they are more flexible but less selective than built-in attribute conditions.
"""

SELECTIVITY_WEIGHT_MEMBERSHIP: float = 0.75
"""Score added when a ValueCondition or FeatureCondition uses MEMBERSHIP mode.

MEMBERSHIP is more selective than NEGATION (which only excludes one value)
but less selective than EXACT (which pins one value).
"""

SELECTIVITY_WEIGHT_REGEX: float = 0.75
"""Score added when a ValueCondition uses REGEX mode.

Regex matching is flexible and can express both simple substring checks and
more precise patterns, so it is treated as moderately selective.
"""

# ──────────────────────────────────────────────────────────────
# 3.  Match capacity limits
# ──────────────────────────────────────────────────────────────
DEFAULT_MAX_MATCHES_PER_COLLECTOR: int = 100_000
"""Default `max_matches` for `MatchCollector`."""

DEFAULT_MAX_MATCHES_PER_SENTENCE: int = 100_000
"""Default `max_matches_per_sentence` for `DepChainMatcher`."""

DEFAULT_MAX_TOTAL_MATCHES: int = 1_000_000
"""Default `max_total_matches` for the orchestrator."""

# ──────────────────────────────────────────────────────────────
# 4.  Deduplication
# ──────────────────────────────────────────────────────────────
VALID_DEDUP_MODES: frozenset = frozenset({"none", "exact", "role_based"})
"""All recognised dedup_mode string values.

Every site that validates `dedup_mode` should test membership against
this set instead of repeating the literal strings.
"""

DEFAULT_DEDUP_MODE_MATCHER: str = "role_based"
"""Default `dedup_mode` for `DepChainMatcher`."""

DEFAULT_DEDUP_MODE_COLLECTOR: str = "none"
"""Default `dedup_mode` for `MatchCollector`."""

DEFAULT_DEDUP_MODE_SENTENCE: str = "role_based"
"""Default `sentence_match_dedup_mode` for the orchestrator (used by taggers)."""

DEFAULT_DEDUP_MODE_GLOBAL: str = "none"
"""Default `global_dedup_mode` for the orchestrator (used by taggers)."""

# ──────────────────────────────────────────────────────────────
# 5.  Tagger — output layer defaults  (H11)
# ──────────────────────────────────────────────────────────────
DEFAULT_OUTPUT_LAYER_NAME: str = "dep_chains"
"""Default name of the estnltk Layer produced by `DepChainTagger` or `DepChildTagger`."""

DEFAULT_OUTPUT_ATTRIBUTES: tuple = (
    "pattern_name",
    "matched_text",
    # "text",
    # "upostag",
    # "xpostag",
    # "feats",
    # "lemma",
    # "deprel",
    # "role",
    # "is_anchor",
    # "match_id",
)
"""Default attribute names on the output Layer."""

# ──────────────────────────────────────────────────────────────
# 6.  Tagger — input layer names  (H2 / H12)
# ──────────────────────────────────────────────────────────────
DEFAULT_SYNTAX_LAYER_NAME: str = "stanza_syntax"
"""Name of the input syntax layer that taggers read from (e.g. `DepChainTagger`).

Currently hard-wired to Stanza Syntax output.  Making this configurable
is the first step toward supporting other syntax providers.
"""
DEFAULT_SENTENCES_LAYER_NAME: str = "sentences"
"""Name of the input sentences layer that taggers read from.
This is used for sentence-level deduplication and cross-sentence matching.
"""

# ──────────────────────────────────────────────────────────────
# 7.  Anchor role fallback  (H3)
# ──────────────────────────────────────────────────────────────
DEFAULT_ANCHOR_ROLE: str = "self"
"""Role name used as fallback anchor when the pattern's `anchor_role`
is not present in the match.  Override this if your patterns use a
different convention for the "self" / pivot role.
"""

# ──────────────────────────────────────────────────────────────
# 8.  attribute_conditions — reserved attribute names
# ──────────────────────────────────────────────────────────────
RESERVED_NODE_ATTRIBUTE_NAMES: dict = {
    "role": "role (structural field, not a simple attribute condition)",
    "is_anchor": "is_anchor (structural field, boolean indicating if the node is the anchor)",
}
"""Attribute names that must NOT appear in ``NodeConstraint.attribute_conditions``.

These names are reserved because they require a different condition type
(``FeatureCondition`` for dict-valued attributes) or are handled by dedicated
fields with non-scalar matching logic.

When a user accidentally includes one of these keys, the validation in
``NodeConstraint._validate_or_raise()`` raises a ``ValueError`` with a
clear message pointing to the dedicated field they should use instead.

Extend this mapping when new dedicated condition fields are added to
``NodeConstraint`` that use a condition type other than ``ValueCondition``.
"""
