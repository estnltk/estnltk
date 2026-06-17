import re
from collections.abc import Mapping
from typing import (
    Dict,
    Optional,
    Tuple,
    Self,
    Any,
    Callable,
)
from dataclasses import dataclass

from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
    NodePredicate,
    EdgeContext,
)

from estnltk.taggers.system.rule_taggers.deprel_components.config import (
    DEFAULT_MISSING_MARKERS,
    SELECTIVITY_WEIGHT_EXACT,
    SELECTIVITY_WEIGHT_NEGATION,
    SELECTIVITY_WEIGHT_MEMBERSHIP,
    SELECTIVITY_WEIGHT_REGEX,
    SELECTIVITY_WEIGHT_EXTRA_PREDICATE,
    RESERVED_NODE_ATTRIBUTE_NAMES,
)


def _is_text_scalar(value: Any) -> bool:
    """Return True when value should be treated as a scalar text-like leaf."""
    return isinstance(value, (str, bytes)) or not isinstance(
        value, (Mapping, list, tuple, set, frozenset)
    )


def _iter_feature_children(value: Any) -> Tuple[Any, ...]:
    """Return child values that should be traversed when recursing nested features."""
    if isinstance(value, Mapping):
        return tuple(value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(value)
    return tuple()


def _normalize_recursive(value: Any, normalizer: Optional[Callable[[Any], Any]]) -> Any:
    """Recursively normalise scalar leaves while preserving container shape."""
    if normalizer is None:
        return value
    if isinstance(value, Mapping):
        return {
            key: _normalize_recursive(child, normalizer) for key, child in value.items()
        }
    if isinstance(value, list):
        return [_normalize_recursive(child, normalizer) for child in value]
    if isinstance(value, tuple):
        return tuple(_normalize_recursive(child, normalizer) for child in value)
    if isinstance(value, set):
        return {_normalize_recursive(child, normalizer) for child in value}
    if isinstance(value, frozenset):
        return frozenset(_normalize_recursive(child, normalizer) for child in value)
    return normalizer(value)


def _feature_exact_match(
    actual_value: Any,
    expected_value: Any,
    allow_extra_keys: bool,
    allow_missing: bool = False,
) -> bool:
    """Recursively compare nested feature structures with exact semantics."""
    if isinstance(expected_value, Mapping):
        if not isinstance(actual_value, Mapping):
            return False
        for key, expected_child in expected_value.items():
            if key not in actual_value:
                if allow_missing:
                    continue
                return False
            if not _feature_exact_match(
                actual_value[key], expected_child, allow_extra_keys, allow_missing
            ):
                return False
        if not allow_extra_keys:
            actual_keys = set(actual_value.keys())
            expected_keys = set(expected_value.keys())
            if actual_keys != expected_keys:
                return False
        return True

    if isinstance(expected_value, tuple):
        if not isinstance(actual_value, tuple) or len(actual_value) != len(
            expected_value
        ):
            return False
        return all(
            _feature_exact_match(
                child_actual, child_expected, allow_extra_keys, allow_missing
            )
            for child_actual, child_expected in zip(actual_value, expected_value)
        )

    if isinstance(expected_value, list):
        if not isinstance(actual_value, list) or len(actual_value) != len(
            expected_value
        ):
            return False
        return all(
            _feature_exact_match(
                child_actual, child_expected, allow_extra_keys, allow_missing
            )
            for child_actual, child_expected in zip(actual_value, expected_value)
        )

    if isinstance(expected_value, (set, frozenset)):
        if not isinstance(actual_value, (set, frozenset)):
            return False
        actual_items = list(actual_value)
        expected_items = list(expected_value)
        if len(actual_items) != len(expected_items):
            return False

        used = [False] * len(actual_items)

        def _backtrack(index: int) -> bool:
            if index == len(expected_items):
                return True
            expected_child = expected_items[index]
            for actual_index, actual_child in enumerate(actual_items):
                if used[actual_index]:
                    continue
                if _feature_exact_match(
                    actual_child, expected_child, allow_extra_keys, allow_missing
                ):
                    used[actual_index] = True
                    if _backtrack(index + 1):
                        return True
                    used[actual_index] = False
            return False

        return _backtrack(0)

    return actual_value == expected_value


def _feature_recursive_match(
    actual_value: Any,
    expected_value: Any,
    allow_extra_keys: bool,
) -> bool:
    """Search recursively for a sub-structure matching the expected value."""
    if _feature_exact_match(actual_value, expected_value, allow_extra_keys):
        return True
    for child_value in _iter_feature_children(actual_value):
        if _feature_recursive_match(child_value, expected_value, allow_extra_keys):
            return True
    return False


def _feature_any_match(
    actual_value: Any,
    candidate_patterns: Any,
    allow_extra_keys: bool,
) -> bool:
    """Check whether any candidate pattern matches the actual structure."""
    if candidate_patterns is None:
        return False
    if isinstance(candidate_patterns, Mapping):
        items = [dict([(key, value)]) for key, value in candidate_patterns.items()]
    elif isinstance(candidate_patterns, (list, tuple, set, frozenset)):
        items = list(candidate_patterns)
    else:
        items = [candidate_patterns]

    for candidate in items:
        if _feature_recursive_match(actual_value, candidate, allow_extra_keys):
            return True
    return False


@dataclass(frozen=True, slots=True)
class ValueCondition:
    """
    Match one scalar value using exact, negation, wildcard, membership, not-membership, or regex logic.

    ## Attributes:
    - **mode** (`ConditionMode`): The matching mode to use (EXACT, NEGATION, WILDCARD, MEMBERSHIP, NOT_MEMBERSHIP, or REGEX).
    - **value** (`Any`, optional): The value to match against. Required for EXACT, NEGATION, MEMBERSHIP, NOT_MEMBERSHIP, and REGEX modes. Must be None for WILDCARD mode. Defaults to None.
    - **allow_missing** (`bool`, optional): Whether to allow missing values (e.g., None, empty string, or other specified missing markers) as a match. Defaults to False.
    - **normalizer** (`Optional[Callable[[Any], Any]]`, optional): An optional function to normalize both the expected value and the actual value before comparison. This can be used to implement case-insensitive matching, for example. When using REGEX mode, the normalizer is applied to the text form of the actual value and to the regex pattern text if the pattern was provided as a string. Defaults to None (no normalization).
    - **missing_markers** (`Tuple[Any, ...]`, optional): A tuple of values that should be treated as missing when `allow_missing` is True. Defaults to (None, "", "_").

    ## Mode semantics:
    - **EXACT**: The actual attribute value must be exactly equal to ``value``.
    - **NEGATION**: The actual attribute value must not be equal to ``value``.
    - **WILDCARD**: Any attribute value matches (``value`` must be None).
    - **MEMBERSHIP**: The actual (scalar) attribute value must be in the iterable ``value``.
      The *condition* holds a collection; the *attribute* is scalar.
    - **NOT_MEMBERSHIP**: The actual (scalar) attribute value must not be in the iterable ``value``.
    - **REGEX**: The text representation of the actual value must match the provided
            regular-expression pattern.

    ## Methods:
    - :func:`~ValueCondition.matches`: Checks whether a given actual value satisfies this condition.
    - :func:`~ValueCondition.describe`: Returns a human-readable explanation of the condition.
    """

    mode: ConditionMode
    value: Any = None
    allow_missing: bool = False
    normalizer: Optional[Callable[[Any], Any]] = None
    missing_markers: Tuple[Any, ...] = DEFAULT_MISSING_MARKERS

    def __post_init__(self: Self) -> None:
        """
        Validate config and pre-normalise expected value once.
        """
        self._validate_or_raise()

        if (
            self.normalizer is not None
            and self.value is not None
            and self.mode
            not in (
                ConditionMode.WILDCARD,
                ConditionMode.MEMBERSHIP,
                ConditionMode.NOT_MEMBERSHIP,
            )
        ):
            # dataclass is frozen, so we use object.__setattr__
            object.__setattr__(self, "value", self.normalizer(self.value))

    def matches(self: Self, actual_value: Any) -> bool:
        """
        Check whether `actual_value` satisfies this condition.

        Args:
            actual_value (Any): The value to check against this condition.

        Returns:
            bool: True if the actual value satisfies the condition, False otherwise.
        """
        if self.mode is ConditionMode.WILDCARD:
            return True

        if self._is_missing(actual_value):
            return bool(self.allow_missing)

        if self.mode is ConditionMode.REGEX:
            return self._matches_regex(actual_value)

        if self.normalizer is not None:
            actual_value = self.normalizer(actual_value)

        if self.mode is ConditionMode.EXACT:
            return actual_value == self.value
        if self.mode is ConditionMode.NEGATION:
            return actual_value != self.value
        if self.mode is ConditionMode.MEMBERSHIP:
            return actual_value in self.value
        if self.mode is ConditionMode.NOT_MEMBERSHIP:
            return actual_value not in self.value

        # Defensive fallback; should be unreachable due to validation.
        raise ValueError(f"Unsupported mode: {self.mode}")

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of the condition.
        """
        if self.mode is ConditionMode.EXACT:
            return f"Value must be exactly {self.value!r}"
        if self.mode is ConditionMode.NEGATION:
            return f"Value must not be {self.value!r}"
        if self.mode is ConditionMode.WILDCARD:
            return "Value can be any value"
        if self.mode is ConditionMode.MEMBERSHIP:
            return f"Value must be in {self.value!r}"
        if self.mode is ConditionMode.NOT_MEMBERSHIP:
            return f"Value must not be in {self.value!r}"
        if self.mode is ConditionMode.REGEX:
            return f"Value must match regex {self.value!r}"
        raise ValueError(f"Unsupported mode: {self.mode}")

    def _matches_regex(self: Self, actual_value: Any) -> bool:
        """
        Check whether the text representation of the actual value matches the
        configured regular-expression pattern.

        Args:
            actual_value (Any): The collection-valued attribute value to search.

        Returns:
            bool: True if any element/key matches the condition value, False otherwise.
        """
        pattern = self.value
        if hasattr(pattern, "search"):
            regex = pattern
            pattern_text = None
        else:
            pattern_text = str(pattern)
            if self.normalizer is not None:
                pattern_text = self.normalizer(pattern_text)
            regex = re.compile(pattern_text)

        text_value = str(actual_value)
        if self.normalizer is not None:
            text_value = self.normalizer(text_value)

        return bool(regex.search(text_value))

    def _is_missing(self: Self, value: Any) -> bool:
        """
        Return True when value should be treated as missing.

        Args:
            value (Any): The value to check for missingness.
        Returns:
            bool: True if the value should be treated as missing, False otherwise.
        """
        return value in self.missing_markers

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments and raise explicit errors.
        """
        if not isinstance(self.mode, ConditionMode):
            raise TypeError(
                "mode must be ConditionMode (EXACT, NEGATION, WILDCARD, MEMBERSHIP, NOT_MEMBERSHIP, or REGEX)."
            )

        if self.mode in (
            ConditionMode.EXACT,
            ConditionMode.NEGATION,
            ConditionMode.REGEX,
        ):
            if self.value is None:
                raise ValueError(
                    "value is required for EXACT, NEGATION, and REGEX modes."
                )

        if self.mode is ConditionMode.WILDCARD and self.value is not None:
            raise ValueError("value must be None when mode is WILDCARD.")

        if self.mode in (ConditionMode.MEMBERSHIP, ConditionMode.NOT_MEMBERSHIP):
            if self.value is None:
                raise ValueError(
                    "value is required for MEMBERSHIP / NOT_MEMBERSHIP mode."
                )
            # Check if value is iterable (but not string)
            if isinstance(self.value, str):
                raise TypeError(
                    "value for MEMBERSHIP / NOT_MEMBERSHIP mode must be an iterable (list, tuple, set) but not a string."
                )
            try:
                iter(self.value)
            except TypeError:
                raise TypeError(
                    f"value for MEMBERSHIP / NOT_MEMBERSHIP mode must be iterable, got {type(self.value).__name__}."
                )

        if self.normalizer is not None and not callable(self.normalizer):
            raise TypeError("normalizer must be callable or None.")


@dataclass(frozen=True, slots=True)
class NestedValueCondition:
    """
    Match a nested feature structure using exact, negation, membership, or wildcard logic.

    The actual value can be a dict, list, tuple, set, frozenset, string, or any
    nested combination of those containers. Scalar leaves are compared with the
    configured normalizer, if one is provided.

    ## Attributes:
    - **mode** (`ConditionMode`): The matching mode to use (EXACT, NEGATION, MEMBERSHIP, or WILDCARD).
    - **required** (`Any`): The required feature structure or pattern.
    - **forbidden** (`Any`): The forbidden feature structure or pattern.
    - **allow_extra_keys** (`bool`, optional): Whether to allow extra keys in the actual features that are not specified in either `required` or `forbidden`. When `mode` is EXACT and `allow_extra_keys` is False, no keys outside union of `required` and `forbidden` are allowed. When `mode` is NEGATION, `allow_extra_keys` has no effect since we only check the specified keys.
    Defaults to True.
    - **allow_missing** (`bool`, optional): Whether to allow missing keys (i.e., keys that are specified in `required` but not present in the actual features) as a match.
    Defaults to False.
    - **normalizer** (`Optional[Callable[[Any], Any]]`, optional): An optional function to normalize both the expected values and the actual values before comparison. This can be used to implement case-insensitive matching, for example.
    Defaults to None (no normalization).
    ## Methods:
    - :func:`~NestedValueCondition.matches`: Checks whether a given actual features dictionary satisfies this condition.
    - :func:`~NestedValueCondition.describe`: Returns a human-readable explanation of the condition.
    """

    mode: ConditionMode
    required: Any = None
    forbidden: Any = None
    allow_extra_keys: Optional[bool] = True
    allow_missing: Optional[bool] = False
    normalizer: Optional[Callable[[Any], Any]] = None
    missing_markers: Tuple[Any, ...] = DEFAULT_MISSING_MARKERS

    def __post_init__(self: Self) -> None:
        """
        Validate config and pre-normalise expected values once.
        """

        self._validate_or_raise()

        if self.normalizer is not None:
            if self.required is not None:
                # dataclass is frozen, so we use object.__setattr__
                object.__setattr__(
                    self,
                    "required",
                    _normalize_recursive(self.required, self.normalizer),
                )
            if self.forbidden is not None:
                # dataclass is frozen, so we use object.__setattr__
                object.__setattr__(
                    self,
                    "forbidden",
                    _normalize_recursive(self.forbidden, self.normalizer),
                )

    def matches(self: Self, actual_value: Any) -> bool:
        """
        Check whether `actual_value` satisfies this condition.

        Args:
            actual_value (Dict[str, Any] | None): The value to check against this condition.

        Returns:
            bool: True if the actual value satisfies the condition, False otherwise.
        """
        if self.mode is ConditionMode.WILDCARD:
            return True

        if self._is_missing(actual_value):
            return bool(self.allow_missing)

        actual_value = _normalize_recursive(actual_value, self.normalizer)

        if self.mode is ConditionMode.EXACT:
            if self.required is not None:
                if isinstance(actual_value, Mapping) and isinstance(
                    self.required, Mapping
                ):
                    required_keys = set(self.required.keys())
                    forbidden_keys = (
                        set(self.forbidden.keys())
                        if isinstance(self.forbidden, Mapping)
                        else set()
                    )

                    if not bool(self.allow_extra_keys):
                        allowed_keys = required_keys | forbidden_keys
                        if not set(actual_value.keys()).issubset(allowed_keys):
                            return False

                    for key, expected_child in self.required.items():
                        if key not in actual_value:
                            if self.allow_missing:
                                continue
                            return False
                        if not _feature_exact_match(
                            actual_value[key],
                            expected_child,
                            bool(self.allow_extra_keys),
                            bool(self.allow_missing),
                        ):
                            return False
                elif not _feature_exact_match(
                    actual_value,
                    self.required,
                    bool(self.allow_extra_keys),
                    bool(self.allow_missing),
                ):
                    return False
            if self.forbidden is not None and _feature_any_match(
                actual_value, self.forbidden, True
            ):
                return False
            return True

        if self.mode is ConditionMode.NEGATION:
            if self.required is not None and _feature_exact_match(
                actual_value, self.required, bool(self.allow_extra_keys)
            ):
                return False
            if self.forbidden is not None and _feature_any_match(
                actual_value, self.forbidden, True
            ):
                return False
            return True

        if self.mode is ConditionMode.MEMBERSHIP:
            if self.required is not None and not _feature_any_match(
                actual_value, self.required, True
            ):
                return False
            if self.forbidden is not None and _feature_any_match(
                actual_value, self.forbidden, True
            ):
                return False
            return True

        raise ValueError(f"Unsupported mode: {self.mode}")

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of the condition.
        """
        if self.mode is ConditionMode.EXACT:
            return f"Features must match {self.required!r} and avoid {self.forbidden!r}"
        if self.mode is ConditionMode.NEGATION:
            return f"Features must not match {self.required!r}; and must not include {self.forbidden!r}"
        if self.mode is ConditionMode.MEMBERSHIP:
            parts = []
            if self.required is not None:
                parts.append(f"at least one of {self.required!r} must be present")
            if self.forbidden is not None:
                parts.append(f"none of {self.forbidden!r} may be present")
            return (
                "Features: " + "; and ".join(parts)
                if parts
                else "Features: membership with no constraints"
            )
        if self.mode is ConditionMode.WILDCARD:
            return "Features can be any value"
        raise ValueError(f"Unsupported mode: {self.mode}")

    def _is_missing(self: Self, value: Any) -> bool:
        """Treat missing markers and empty containers as missing feature structures."""
        if any(value == marker for marker in self.missing_markers):
            return True
        if isinstance(value, Mapping):
            return len(value) == 0
        if isinstance(value, (list, tuple, set, frozenset)):
            return len(value) == 0
        return False

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.mode, ConditionMode):
            raise TypeError("mode must be ConditionMode.")

        if self.normalizer is not None and not callable(self.normalizer):
            raise TypeError("normalizer must be callable or None.")

        if not isinstance(self.missing_markers, tuple):
            raise TypeError("missing_markers must be a tuple.")

        if self.mode is ConditionMode.WILDCARD:
            if self.required is not None or self.forbidden is not None:
                raise ValueError("required/forbidden must be None for WILDCARD mode.")
            return

        if self.mode in (
            ConditionMode.EXACT,
            ConditionMode.NEGATION,
            ConditionMode.MEMBERSHIP,
        ):
            if self.required is None and self.forbidden is None:
                raise ValueError(
                    "Provide required and/or forbidden for EXACT/NEGATION/MEMBERSHIP."
                )

        if self.mode is ConditionMode.REGEX:
            raise ValueError(
                "REGEX mode is a scalar ValueCondition mode and is not supported by NestedValueCondition."
            )

        if self.allow_extra_keys is not None and not isinstance(
            self.allow_extra_keys, bool
        ):
            raise TypeError("allow_extra_keys must be a boolean value or None.")

        if self.allow_missing is not None and not isinstance(self.allow_missing, bool):
            raise TypeError("allow_missing must be a boolean value or None.")


@dataclass(frozen=True, slots=True)
class NodeConstraint:
    """
    Constraint for a single node in the dependency graph, used for matching nodes during feature extraction.

    All scalar attribute conditions are specified via ``attribute_conditions``: a dictionary
    that maps attribute names to ``ValueCondition`` objects. At match time each key is used
    as a ``getattr()`` lookup on the node annotation span, and the retrieved value is tested
    against the corresponding condition. This makes the constraint extensible to any attribute
    on the annotation layer without requiring new dataclass fields.

    ## Attributes:
    - **role** (`str`): The role of the node in the dependency chain (e.g., "self", "parent", "child", "sibling", etc.).
    - **attribute_conditions** (`Optional[Dict[str, ValueCondition]]`): An optional dictionary mapping attribute names to `ValueCondition` objects. These are intended only for scalar attributes (e.g. `upostag`, `lemma`, `deprel`). Each key is an attribute name that will be looked up on the node annotation via ``getattr(node_annotation, key, None)``, and the retrieved value is matched against the corresponding condition.
    - **nested_attribute_conditions** (`Optional[Dict[str, NestedValueCondition]]`): An optional dictionary mapping attribute names that hold nested/dict-like values (e.g. `feats`) to `NestedValueCondition` objects. Use this to express constraints over nested attribute structures. Do not use `attribute_conditions` for dict-valued attributes.
    - **extra_predicates** (`Optional[Tuple[NodePredicate, ...]]`): An optional tuple of additional callables that take the node annotation as input and return a boolean indicating whether the node satisfies some custom condition. These can be used for more complex checks that are not easily expressed with the other conditions.

    ## Methods:
    - :func:`~NodeConstraint.matches`: Checks whether a given node annotation satisfies all the specified conditions in this constraint.
    - :func:`~NodeConstraint.score_selectivity`: Calculates a heuristic selectivity score for this constraint, which can be used to prioritize more selective constraints during matching.
    - :func:`~NodeConstraint.describe`: Returns a human-readable explanation of this node constraint, including the role and the specified conditions.
    """

    role: str
    attribute_conditions: Optional[Dict[str, ValueCondition]] = None
    # Nested-structure attribute conditions (e.g. `feats`) mapped by attribute name.
    nested_attribute_conditions: Optional[Dict[str, NestedValueCondition]] = None
    extra_predicates: Optional[Tuple[NodePredicate, ...]] = None

    def __post_init__(self: Self) -> None:
        """
        Validate config and pre-normalise expected values once.
        """
        # Enforce strict typing for nested_attribute_conditions early so
        # callers receive immediate, predictable TypeErrors when they pass
        # incorrect values (tests expect this behavior).
        if self.nested_attribute_conditions is not None:
            if not isinstance(self.nested_attribute_conditions, dict):
                raise TypeError(
                    "nested_attribute_conditions must be a dict mapping attribute names to NestedValueCondition instances"
                )
            for key, cond in self.nested_attribute_conditions.items():
                if not isinstance(cond, NestedValueCondition):
                    raise TypeError(
                        f"Each value in nested_attribute_conditions must be NestedValueCondition, got {type(cond).__name__} for key '{key}'"
                    )

        self._validate_or_raise()

    def matches(self: Self, node_annotation: Any) -> bool:
        """
        Check whether the given node annotation satisfies this constraint.

        Each key in ``attribute_conditions`` is resolved via
        ``getattr(node_annotation, key, None)`` and the resulting value is
        tested against the corresponding ``ValueCondition``.

        Args:
            node_annotation (estnltk.Span): The estnltk Span annotation of the node to check against this constraint.

        Returns:
            bool: True if the node annotation satisfies all specified conditions,
            otherwise False. Conditions that are None are ignored.
        """
        if self.attribute_conditions:
            for attr_name, condition in self.attribute_conditions.items():
                actual_value = getattr(node_annotation, attr_name, None)
                if not condition.matches(actual_value):
                    return False

        # Check nested-structure attribute conditions (e.g. feats)
        if self.nested_attribute_conditions:
            for attr_name, condition in self.nested_attribute_conditions.items():
                actual_value = getattr(node_annotation, attr_name, None)
                if not condition.matches(actual_value):
                    return False
        if self.extra_predicates:
            for pred in self.extra_predicates:
                if not pred(node_annotation):
                    return False
        return True

    def score_selectivity(self: Self) -> float:
        """
        Calculate a heuristic selectivity score for this constraint, which can be used to prioritize more selective constraints during matching.

        Returns:
            float: A selectivity score where higher values indicate more selective constraints. The score is calculated based on the number and restrictiveness of the specified conditions. For example, an EXACT ValueCondition is more selective than a NEGATION, and both are more selective than a WILDCARD. Similarly, having multiple conditions (e.g., UPOS, lemma, feats) increases selectivity compared to having only one or none.
        """
        score = 0.0
        # Exact > Membership ≈ Regex > Negation > Wildcard(0.0) in terms of selectivity
        if self.attribute_conditions:
            for cond in self.attribute_conditions.values():
                if cond.mode == ConditionMode.EXACT:
                    score += SELECTIVITY_WEIGHT_EXACT
                elif cond.mode == ConditionMode.MEMBERSHIP:
                    score += SELECTIVITY_WEIGHT_MEMBERSHIP
                elif cond.mode == ConditionMode.NOT_MEMBERSHIP:
                    score += SELECTIVITY_WEIGHT_MEMBERSHIP
                elif cond.mode == ConditionMode.REGEX:
                    score += SELECTIVITY_WEIGHT_REGEX
                elif cond.mode == ConditionMode.NEGATION:
                    score += SELECTIVITY_WEIGHT_NEGATION

        if self.nested_attribute_conditions:
            for cond in self.nested_attribute_conditions.values():
                if cond.mode == ConditionMode.EXACT:
                    score += SELECTIVITY_WEIGHT_EXACT
                elif cond.mode == ConditionMode.MEMBERSHIP:
                    score += SELECTIVITY_WEIGHT_MEMBERSHIP
                elif cond.mode == ConditionMode.NOT_MEMBERSHIP:
                    score += SELECTIVITY_WEIGHT_MEMBERSHIP
                elif cond.mode == ConditionMode.NEGATION:
                    score += SELECTIVITY_WEIGHT_NEGATION

        # nested_attribute_conditions already counted above when present
        if self.extra_predicates:
            score += SELECTIVITY_WEIGHT_EXTRA_PREDICATE * len(self.extra_predicates)

        return score

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of this node constraint, including the role and the specified conditions.

        Returns:
            str: A human-readable string describing this node constraint, including the role and the details of each specified condition. This can be used for debugging or for explaining why a particular node did or did not match this constraint.
        """
        parts = [f"Role: {self.role}"]
        if self.attribute_conditions:
            for attr_name, condition in self.attribute_conditions.items():
                parts.append(f"Attribute '{attr_name}': {condition.describe()}")
        if self.nested_attribute_conditions:
            for attr_name, condition in self.nested_attribute_conditions.items():
                parts.append(f"Nested '{attr_name}': {condition.describe()}")
        if self.extra_predicates:
            parts.append(
                f"Extra predicates: {len(self.extra_predicates)} predicates defined"
            )
        return "; ".join(parts)

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.role, str) or self.role.strip() == "":
            raise TypeError("role must be a non-empty string.")

        if self.attribute_conditions is not None:
            if not isinstance(self.attribute_conditions, dict):
                raise TypeError(
                    "attribute_conditions must be a Dict[str, ValueCondition|NestedValueCondition] or None."
                )
            for key, cond in self.attribute_conditions.items():
                if not isinstance(key, str) or key.strip() == "":
                    raise TypeError(
                        "Each key in attribute_conditions must be a non-empty string."
                    )
                # Accept either ValueCondition or FeatureCondition as a value.
                if not isinstance(cond, (ValueCondition, NestedValueCondition)):
                    raise TypeError(
                        f"Each value in attribute_conditions must be ValueCondition or NestedValueCondition, "
                        f"got {type(cond).__name__} for key '{key}'."
                    )
                # Disallow dict-valued expected values on ValueCondition entries to
                # avoid confusing use for dict-like attributes (e.g. `feats`).
                if (
                    isinstance(cond, ValueCondition)
                    and getattr(cond, "value", None) is not None
                    and isinstance(cond.value, dict)
                ):
                    raise ValueError(
                        f"attribute_conditions entry '{key}' has a dict-valued expected "
                        "value; use NestedValueCondition for dict-valued attributes."
                    )
            # Reject attribute names that must use a different condition type
            # or are handled by dedicated non-condition fields.
            overlapping = set(self.attribute_conditions.keys()) & set(
                RESERVED_NODE_ATTRIBUTE_NAMES.keys()
            )
            if overlapping:
                invalid_reserved = {
                    attr
                    for attr in overlapping
                    if not isinstance(
                        self.attribute_conditions.get(attr), NestedValueCondition
                    )
                }
                if invalid_reserved:
                    details = {
                        attr: RESERVED_NODE_ATTRIBUTE_NAMES[attr]
                        for attr in invalid_reserved
                    }
                    raise ValueError(
                        f"attribute_conditions keys {invalid_reserved} are reserved. "
                        f"These attributes require a different condition type or are "
                        f"handled by dedicated fields: {details}. "
                        f"Use the dedicated fields instead."
                    )

        if self.extra_predicates is not None:
            if not isinstance(self.extra_predicates, tuple):
                raise TypeError(
                    "extra_predicates must be a tuple of callables or None."
                )
            for pred in self.extra_predicates:
                if not callable(pred):
                    raise TypeError("Each item in extra_predicates must be callable.")


@dataclass(frozen=True, slots=True)
class EdgeConstraint:
    """
    A constraint for filtering edges in the syntax graph based on their properties.

    Linguistic attributes such as ``deprel`` are stored on the child/dependent node in
    UD dependency syntax, so they should be constrained via ``NodeConstraint.attribute_conditions``
    on the corresponding node step rather than on the edge.

    ## Attributes:
    - **direction** (`DirectionMode`): The direction of the edge to consider (up, down, or both).
    - **min_hops** (`Optional[int]`): The minimum number of hops (edges) to traverse in the specified direction for this constraint to apply. Defaults to 1.
    - **max_hops** (`Optional[int]`): The maximum number of hops (edges) to traverse in the specified direction for this constraint to apply. Defaults to 1.
    ## Methods:
    - :func:`~EdgeConstraint.matches`: Checks whether a given edge context satisfies this constraint.
    - :func:`~EdgeConstraint.describe`: Returns a human-readable explanation of this edge constraint, including the direction and hop range.
    """

    direction: DirectionMode
    min_hops: Optional[int] = 1
    max_hops: Optional[int] = 1

    def __post_init__(self: Self) -> None:
        """
        Validate config once.
        """
        self._validate_or_raise()

    def matches(self: Self, edge_context: EdgeContext) -> bool:
        """
        Check whether the given edge context satisfies this constraint.

        Args:
            edge_context (EdgeContext): The context of the edge to check against this constraint, including its direction and the number of hops from the source node.

        Returns:
            bool: True if the edge context satisfies this constraint, False otherwise.
        """
        # Check direction
        # If BOTH, we allow any direction, so no check needed. Otherwise, the edge's direction must match the specified direction.
        if (
            self.direction != DirectionMode.BOTH
            and edge_context.direction != self.direction
        ):
            return False
        # Check hop bounds
        if self.min_hops is not None and edge_context.hops < self.min_hops:
            return False
        if self.max_hops is not None and edge_context.hops > self.max_hops:
            return False
        return True

    def describe(self: Self) -> str:
        """
        Return a human-readable explanation of this edge constraint, including the direction and hop range.

        Returns:
            str: A human-readable string describing this edge constraint, including the direction and hop range. This can be used for debugging or for explaining why a particular edge did or did not match this constraint.
        """
        parts = [f"Direction: {self.direction.value}"]
        if self.min_hops is not None or self.max_hops is not None:
            parts.append(f"Hops: {self.min_hops or 0} to {self.max_hops or '∞'}")
        return "; ".join(parts)

    def _validate_or_raise(self: Self) -> None:
        """
        Validate constructor arguments with explicit, actionable errors.
        """
        if not isinstance(self.direction, DirectionMode):
            raise TypeError("direction must be an instance of DirectionMode.")

        if self.min_hops is not None:
            if not isinstance(self.min_hops, int) or self.min_hops <= 0:
                raise ValueError("min_hops must be a positive integer or None.")
        if self.max_hops is not None:
            if not isinstance(self.max_hops, int) or self.max_hops <= 0:
                raise ValueError("max_hops must be a positive integer or None.")

        if (
            self.min_hops is not None
            and self.max_hops is not None
            and self.min_hops > self.max_hops
        ):
            raise ValueError("min_hops cannot be greater than max_hops.")
