from typing import Any
from typing import Dict
from typing import Union
from typing import Callable
from dataclasses import dataclass

from estnltk_core import Span
from estnltk import Text


@dataclass(frozen=True)
class DynamicExtractionRule:
    """
    Class for describing extraction rules fixed by the pattern and a decorator function:
    * pattern specifies a text segment;
    * decorator function adds attribute values to the extracted text segment.

    The exact form of valid patterns is determined by the tagger which interprets rules:
    * SubstringTagger accepts ordinary strings as patterns

    Taggers are expected to use the decorator function to add attribute values to the extracted segments.
    These segments are specified through the Span class. By default we assume that the tagger attaches the span to
    the layer and to the text objects. As a result the decorator function can access characters surrounding the span.

    It is possible to use decorators as validators. The user is free to specify the corresponding signalling protocol.
    In the most obvious protocol, the decorator outputs None to indicate that the span should not be added to the layer.
    The latter is a safe default, as this would most probably reveal when the tagger is incompatible.

    """

    pattern: str
    decorator:  Callable[[Text, Span], Union[Dict[str, Any], None]]
    group: int = 0
    priority: int = 0
