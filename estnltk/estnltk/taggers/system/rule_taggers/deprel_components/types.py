from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    TypeAlias,
)
from enum import Enum

NodePredicate: TypeAlias = Callable[[Any], bool]


class ConditionMode(str, Enum):
    """
    Supported matching modes for value conditions.

    ## Modes:
    - **EXACT**: Match when the actual value is exactly equal to the expected value.
    - **NEGATION**: Match when the actual value is not equal to the expected value.
    - **WILDCARD**: Match any value (expected value is ignored, must be None).
    - **MEMBERSHIP**: Match when the actual (scalar) value is in the expected iterable
      of condition values.  The *condition* holds a collection; the *attribute* is scalar.
    - **NOT_MEMBERSHIP**: Match when the actual (scalar) value is not in the expected
      iterable of condition values.  This is the logical inverse of MEMBERSHIP.
    - **REGEX**: Match when the actual value, converted to text, satisfies the given
      regular-expression pattern. This is intended for flexible substring and pattern
      matching on scalar attributes.
    """

    EXACT = "exact"  # Match when actual value is exactly equal to expected value
    NEGATION = "negation"  # Match when actual value is not equal to expected value
    WILDCARD = "wildcard"  # Match any value (expected value is ignored, must be None)
    MEMBERSHIP = "membership"  # Match when actual value is in the expected iterable (list, tuple, set, etc.)
    NOT_MEMBERSHIP = "not_membership"  # Match when actual value is not in the expected iterable (list, tuple, set, etc.)
    REGEX = (
        "regex"  # Match when the actual value (as text) satisfies a regular expression
    )


class DirectionMode(str, Enum):
    """
    Supported edge direction modes for iterating edges in the syntax graph.
    """

    UP = "up"  # Move from id to head (up the tree)
    DOWN = "down"  # Move from head to id (down the tree)
    BOTH = "both"  # Include both up and down edges (default)


@dataclass(frozen=True, slots=True)
class EdgeContext:
    """
    Context for an edge in the dependency graph, used for matching edges during feature extraction.
    """

    direction: DirectionMode
    hops: int = 1
