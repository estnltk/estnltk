import bisect
from collections.abc import Sequence
from typing import Union, Any, Hashable, List

from estnltk_core import BaseSpan, Span


class SpanList(Sequence):
    """
    SpanList is a container of Spans sorted by start indexes.
    
    Note: all spans in SpanList must have the same (base
    span) level, but SpanList itself does not validate that span
    levels match. It is the responsibility of a programmer 
    to assure that the spanlist is populated with equal-level 
    spans (for more about span levels, see the docstring of
    BaseSpan from estnltk_core).
    
    # TODO replace with SortedDict ??
    """

    def __init__(self, span_level=None):
        # Dict[BaseSpan, Span]
        self._base_span_to_span = {}
        # Optinal[int]
        self._span_level = span_level
        # List[Span]
        self.spans = []

    def add_span(self, span):
        assert span.base_span not in self._base_span_to_span
        bisect.insort(self.spans, span)
        self._base_span_to_span[span.base_span] = span
        if self._span_level is None:
            # Level of the first span is the level 
            # of this spanlist. Once the level is 
            # set, it should not be changed
            self._span_level = span.base_span.level

    def get(self, span: BaseSpan):
        return self._base_span_to_span.get(span)

    def remove_span(self, span):
        del self._base_span_to_span[span.base_span]
        self.spans.remove(span)

    @property
    def text(self):
        return [span.text for span in self.spans]

    @property
    def span_level(self):
        return self._span_level

    def __len__(self) -> int:
        return len(self.spans)

    def __contains__(self, item: Any) -> bool:
        if isinstance(item, Hashable) and item in self._base_span_to_span:
            return True
        if isinstance(item, Span):
            span = self._base_span_to_span.get(item.base_span)
            return span is item

    def index(self, x, *args) -> int:
        return self.spans.index(x, *args)

    def __setitem__(self, key: int, value: Span):
        self.spans[key] = value
        self._base_span_to_span[value.base_span] = value

    def __getitem__(self, idx) -> Union[Span, List[Span]]:
        return self.spans[idx]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SpanList) and self.spans == other.spans

    def __str__(self):
        return 'SL[{spans}]'.format(spans=',\n'.join(str(i) for i in self.spans))

    def __repr__(self):
        return str(self)
