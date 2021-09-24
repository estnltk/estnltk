from typing import Any, Iterable

from estnltk_core.layer.span import Span, Annotation
from estnltk_core import BaseSpan, EnvelopingBaseSpan


class EnvelopingSpan(Span):
    __slots__ = ['_spans']

    def __init__(self, base_span: BaseSpan, layer):
        self._spans = None
        super().__init__(base_span, layer)

    @classmethod
    def from_spans(cls, spans: Iterable[Span], layer, records):
        span = cls(base_span=EnvelopingBaseSpan(s.base_span for s in spans), layer=layer)
        for record in records:
            span.add_annotation(Annotation(span, **record))
        return span

    @property
    def spans(self):
        if self._spans is None:
            get_from_enveloped = self._layer.text_object[self._layer.enveloping].get
            self._spans = tuple(get_from_enveloped(base) for base in self._base_span)

        return self._spans

    def to_records(self, with_text=False):
        return [i.to_records(with_text) for i in self.spans]

    @property
    def _html_text(self):
        rt = self.raw_text
        result = []
        for a, b in zip(self.spans, self.spans[1:]):
            result.extend(('<b>', rt[a.start:a.end], '</b>', rt[a.end:b.start]))
        result.extend(('<b>', rt[self.spans[-1].start:self.spans[-1].end], '</b>'))
        return ''.join(result)

    def __iter__(self):
        yield from self.spans

    def __len__(self) -> int:
        return len(self._base_span)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __setattr__(self, key, value):
        if key == '_spans':
            object.__setattr__(self, key, value)
        else:
            super().__setattr__(key, value)

    def resolve_attribute(self, item):
        if item not in self.text_object.layers:
            attribute_mapping = self.text_object.attribute_mapping_for_enveloping_layers
            return self._layer.text_object[attribute_mapping[item]].get(self.base_span)[item]

        target_layer = self.text_object[item]

        if len(target_layer) == 0:
            return

        if target_layer[0].base_span.level >= self._base_span.level:
            raise AttributeError('target layer level {} should be lower than {}'.format(
                    target_layer[0].base_span.level, self._base_span.level))

        return target_layer.get(self.base_span)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.spans[idx]

        return super().__getitem__(idx)
