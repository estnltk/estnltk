import bisect
from collections.abc import Sequence
from typing import Union, Any, Hashable, List

from estnltk_core import BaseSpan, Span


class SpanList(Sequence):
    """
    # TODO replace with SortedDict
    """

    def __init__(self):
        self._base_span_to_span = {}
        self.spans = []

    def add_span(self, span):
        assert span.base_span not in self._base_span_to_span
        bisect.insort(self.spans, span)
        self._base_span_to_span[span.base_span] = span

    def get(self, span: BaseSpan):
        return self._base_span_to_span.get(span)

    def remove_span(self, span):
        del self._base_span_to_span[span.base_span]
        self.spans.remove(span)

    @property
    def text(self):
        return [span.text for span in self.spans]

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
