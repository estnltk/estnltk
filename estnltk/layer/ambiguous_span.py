from typing import Union, Any
import collections
import pandas as pd
from IPython.core.display import display_html

from estnltk import Span
from estnltk import Annotation
from estnltk.layer import AttributeList


class AmbiguousSpan(collections.Sequence):
    def __init__(self, layer: 'Layer', span: Span) -> None:

        assert not isinstance(span, Annotation), span
        self._span = span

        self.layer = layer

        self.parent = span.parent  # type:Union[Span, None]

        # placeholder for dependant layer
        self._base = None  # type:Union[Span, None]

        self._annotations = []

    @property
    def annotations(self):
        return self._annotations

    @annotations.setter
    def annotations(self, value):
        self._annotations = value

    def to_records(self, with_text=False):
        return [i.to_record(with_text) for i in self._annotations]

    def add_span(self, span: Span) -> Span:
        assert hash(span) == hash(self._span)
        assert not isinstance(span, Annotation)
        annotation = Annotation(self)
        for attr in span.legal_attribute_names:
            setattr(annotation, attr, getattr(span, attr))
        if not isinstance(span, Span):
            # EnvelopingSpan
            annotation.spans = span.spans
        if annotation not in self._annotations:
            self._annotations.append(annotation)
            return span

    def add_annotation(self, **attributes) -> Annotation:
        annotation = Annotation(self)
        for attr in self.layer.attributes:
            setattr(annotation, attr, attributes[attr])
        if annotation not in self._annotations:
            self._annotations.append(annotation)
            return annotation

    def __delitem__(self, key):
        del self._annotations[key]
        if not self._annotations:
            self.layer.remove_span(self)

    @property
    def span(self):
        return self._span

    @property
    def start(self):
        return self._span.start

    @property
    def end(self):
        return self._span.end

    @property
    def base_spans(self):
        return self._span.base_spans

    @property
    def text(self):
        return self._span.text

    @property
    def text_object(self):
        if self.layer is not None:
            return self.layer.text_object

    def __len__(self) -> int:
        return len(self.annotations)

    def __getattr__(self, item):
        if item in {'__getstate__', '__setstate__'}:
            raise AttributeError
        layer = self.__getattribute__('layer')  # type: Layer
        if item in layer.attributes:
            if layer.ambiguous:
                return AttributeList((getattr(span, item) for span in self._annotations), item)
            return getattr(self._annotations[0], item)
        if item == getattr(self.layer, 'parent', None):
            return self.parent
        if item in self.__dict__:
            return self.__dict__[item]

        return self.__getattribute__(item)

    def __getitem__(self, idx: int) -> Union[Annotation, AttributeList]:
        if isinstance(idx, int):
            return self._annotations[idx]

        if isinstance(idx, str):
            return getattr(self, idx)

        raise KeyError(idx)

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AmbiguousSpan) \
               and hash(self.span) == hash(other.span) \
               and len(self._annotations) == len(other._annotations) \
               and all(s in other._annotations for s in self._annotations)

    def __contains__(self, item: Any):
        return item in self._annotations

    def __hash__(self):
        return hash(self.span)

    def __str__(self):
        if self.text_object is not None:
            return 'AS(start={self.start}, end={self.end}, text:{self.text!r})'.format(self=self)
        return 'AS[{spans}]'.format(spans=', '.join(str(i) for i in self.annotations))

    def __repr__(self):
        return str(self)

    def _to_html(self, margin=0) -> str:
        pd.set_option("display.max_colwidth", -1)

        records = [{attr: getattr(annotation, attr) for attr in self.layer.attributes}
                   for annotation in self.annotations]
        first = True
        for rec in records:
            rec['start'] = self.span.start
            rec['end'] = self.span.end
            if first:
                rec['text'] = self.span.html_text(margin)
                first = False
            else:
                rec['text'] = ''
        df = pd.DataFrame.from_records(records, columns=('text', 'start', 'end')+self.layer.attributes)
        return '<b>{}</b>\n{}'.format(self.__class__.__name__, df.to_html(escape=False, justify='left', index=False))

    def display(self, margin: int=0):
        display_html(self._to_html(margin), raw=True)

    def _repr_html_(self):
        return self._to_html()
