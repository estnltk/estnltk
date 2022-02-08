from typing import Any, Iterable

from estnltk_core.layer.span import Span, Annotation
from estnltk_core import BaseSpan, EnvelopingBaseSpan


class EnvelopingSpan(Span):
    '''
    EnvelopingSpan is a Span which envelops around lower level spans. 
    It is used to convey text annotations that build upon other, lower 
    level annotations. For instance, a sentence is an EnvelopingSpan 
    built from word spans, and a paragraph is an EnvelopingSpan built 
    from sentence spans. 
    '''
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
        """Resolves and returns values of foreign attribute `item`, 
           or resolves and returns a foreign span from layer `item`.
           
           More specifically:
           1) If `item` is a name of a foreign attribute which 
              is listed in the mapping from attribute names to 
              foreign layer names 
              (`attribute_mapping_for_enveloping_layers`),
              attempts to find foreign span with the same base 
              span as this span from the foreign layer & returns 
              value(s) of the attribute `item` from that foreign 
              span. 
              (raises KeyError if base span is missing in the 
               foreign layer);
              Note: this is only available when this span belongs to 
              estnltk's `Text` object. The step will be skipped if 
              the span belongs to `BaseText`;

           2) If `item` is a layer attached to span's the text_object, 
              and the layer has `span_level` equal to or lower than this 
              enveloping span (meaning: spans of this layer could envelop 
              around spans of the target layer), then attempts to get & 
              return span or spans from the target layer that match the 
              base span of this span 
              (raises KeyError if base span is missing);
        """
        if self.text_object is not None:
            if hasattr(self.text_object, 'attribute_mapping_for_enveloping_layers'):
                # Attempt to get the foreign attribute of 
                # the same base span of a different attached 
                # layer, based on the mapping of attributes-layers
                # (only available if we have estnltk.text.Text object)
                attribute_mapping = self.text_object.attribute_mapping_for_enveloping_layers
                if item in attribute_mapping:
                    return self._layer.text_object[attribute_mapping[item]].get(self.base_span)[item]
            if item in self.text_object.layers:
                # Attempt to get spans with same base 
                # span(s) from a different attached 
                # layer that has appropriate span_level
                target_layer = self.text_object[item]

                if len(target_layer) == 0:
                    return
                
                if target_layer.span_level >= self._base_span.level:
                    raise AttributeError('target layer span_level {} should be lower than {}'.format(
                            target_layer.span_level, self._base_span.level))
                
                return target_layer.get(self.base_span)
        else:
            raise AttributeError(("Unable to resolve foreign attribute {!r}: "+\
                                  "the layer is not attached to Text object.").format(item) )
        raise AttributeError("Unable to resolve foreign attribute {!r}.".format(item))


    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.spans[idx]

        return super().__getitem__(idx)
