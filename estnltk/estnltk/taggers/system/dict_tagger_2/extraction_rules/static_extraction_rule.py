from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class StaticExtractionRule:
    """
    Class for describing simple extraction rules fixed by the pattern and list of static attributes.

    Fields
    ------
    pattern:
        Specifies a pattern to be matched (usually a string or regular expression).
    attributes:
        Specifies attribute names together with values that are associated with the pattern.
    priority:
        Specifies the priority of a rule. Default value 0.
        Smaller number represents higher priorities and higher numbers lower priorities.
    group:
        Allows to split rules into distinct groups.
        Priorities are usually considered inside a rule group.

    The exact form of valid patterns is determined by the tagger which interprets rules.
    Taggers are expected to decorate extracted spans with intended attribute values.
    Different taggers can treat missing attributes differently, e.g. use default values for missing keys.
    """

    pattern: Any
    attributes: Dict[str, Any] = field(default_factory=dict)
    group: int = 0
    priority: int = 0
