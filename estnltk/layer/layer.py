import keyword
from typing import Union, List, Sequence
import pandas
import collections
import warnings

from estnltk import BaseSpan, ElementaryBaseSpan, EnvelopingBaseSpan
from estnltk import Span, EnvelopingSpan, Annotation, SpanList
from estnltk.layer import AmbiguousAttributeTupleList, AmbiguousAttributeList, AttributeTupleList, AttributeList


def to_base_span(x) -> BaseSpan:
    if isinstance(x, BaseSpan):
        return x
    if isinstance(x, Span):
        return x.base_span
    if isinstance(x, Annotation):
        return x.span.base_span
    if isinstance(x, (List, tuple, Layer)):
        if len(x) == 2 and isinstance(x[0], int) and isinstance(x[1], int):
            return ElementaryBaseSpan(*x)
        return EnvelopingBaseSpan(to_base_span(y) for y in x)
    raise TypeError(x)


class Layer:
    """Basic container for text annotations.

    Layer is used to give annotations to text fragments. Each annotation consists of:
        selected text fragment
        corresponding annotations
    Annotation consists of attributes which can have arbitrary names except reserved words:
        meta - meta information
        start
        end

    It is possible to add meta-information about layer as a whole by specifying layer.meta,
    which is a dictionary of type MutableMapping[str, Any]. However we strongly advise to use
    the following list of attribute types:
        str
        int
        float
        DateTime
    as database serialisation does not work for other types. See [estnltk.storage.postgres] for further documentation.

    """
    def __init__(self,
                 name: str,
                 attributes: Sequence[str] = (),
                 text_object=None,
                 parent: str = None,
                 enveloping: str = None,
                 ambiguous: bool = False,
                 default_values: dict = None
                 ) -> None:
        assert parent is None or enveloping is None, "can't be derived AND enveloping"

        self.default_values = default_values or {}
        assert isinstance(self.default_values, dict)

        # list of legal attribute names for the layer
        self.attributes = attributes

        # name of the layer
        assert name.isidentifier() and not \
            keyword.iskeyword(name), 'layer name must be a valid python identifier, {!r}'.format(name)
        assert name != 'text'
        self.name = name

        # the name of the parent layer.
        self.parent = parent

        self._base = name if enveloping or not parent else None  # This is a placeholder for the base layer.
        # _base is self.name if self.enveloping or not self.parent
        # _base is parent._base otherwise, but we can't assign the value yet,
        # because we have no access to the parent layer
        # The goal is to swap the use of the "parent" attribute to the new "_base" attribute for all
        # layer inheritance purposes. As the idea about new-style text objects has evolved, it has been decided that
        # it is more sensible to keep the tree short and pruned. I'm hoping to avoid a rewrite though.

        # the name of the layer this class envelops
        # sentences envelop words
        # paragraphs envelop sentences
        # and so on...
        self.enveloping = enveloping

        # Container for spans
        self._span_list = SpanList()

        # boolean for if this is an ambiguous layer
        # if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous  # type: bool

        # placeholder. is set when `_add_layer` is called on text object
        self.text_object = text_object  # type: Text

        self.meta = {}

    @property
    def layer(self):
        return self

    @property
    def start(self):
        return self._span_list.spans[0].start

    @property
    def end(self):
        return self._span_list.spans[-1].end

    @property
    def spans(self):
        return self._span_list.spans

    @property
    def text(self):
        result = []
        for span in self._span_list.spans:
            if isinstance(span, EnvelopingSpan):
                result.extend(span.text)
            else:
                result.append(span.text)
        return result

    @property
    def enclosing_text(self):
        return self.text_object.text[self.start:self.end]

    def from_records(self, records, rewriting=False) -> 'Layer':
        if rewriting:
            self._span_list = SpanList()

        if self.ambiguous:
            for record_line in records:
                for record in record_line:
                    attributes = {attr: record.get(attr, self.default_values[attr]) for attr in self.attributes}
                    self.add_annotation(ElementaryBaseSpan(record['start'], record['end']), **attributes)
        else:
            for record in records:
                if record is None:
                    continue
                attributes = {attr: record.get(attr, self.default_values[attr]) for attr in self.attributes}
                self.add_annotation(ElementaryBaseSpan(record['start'], end=record['end']), **attributes)
        return self

    def attribute_list(self, attributes):
        assert isinstance(attributes, (str, list, tuple)), str(type(attributes))
        if not attributes:
            raise IndexError('no attributes: ' + str(attributes))
        if self.ambiguous:
            if isinstance(attributes, (list, tuple)):
                result = AmbiguousAttributeTupleList(
                        (((getattr(a, attr) for attr in attributes) for a in sp.annotations)
                         for sp in self.spans), attributes)
            else:
                result = AmbiguousAttributeList(((getattr(a, attributes) for a in sp.annotations)
                                                 for sp in self.spans), attributes)
        else:
            if isinstance(attributes, (list, tuple)):
                result = AttributeTupleList([[getattr(sp, attr) for attr in attributes] for sp in self.spans],
                                            attributes)
            else:
                result = AttributeList([getattr(sp, attributes) for sp in self.spans], attributes)
        return result

    def copy(self):
        layer = Layer(name=self.name,
                      attributes=self.attributes,
                      text_object=self.text_object,
                      parent=self.parent,
                      enveloping=self.enveloping,
                      ambiguous=self.ambiguous,
                      default_values=self.default_values.copy())
        for span in self:
            for annotation in span.annotations:
                layer.add_annotation(span.base_span, **annotation)
        layer._base = self._base
        return layer

    def to_records(self, with_text=False):
        return self._span_list.to_records(with_text)

    def to_dict(self):
        """Returns a dict representation of this layer.

        """
        return {
            'name': self.name,
            'attributes': self.attributes,
            'parent': self.parent,
            'enveloping': self.enveloping,
            'ambiguous': self.ambiguous,
            'meta': self.meta,
            'spans': [{'base_span': span.base_span.raw(),
                       'annotations': [dict(annotation) for annotation in span.annotations]}
                      for span in self._span_list]
        }

    @classmethod
    def from_dict(cls, d: dict, text_object=None):
        """Parses dict to layer.

        """
        layer = cls(name=d['name'],
                    attributes=d['attributes'],
                    text_object=text_object,
                    parent=d['parent'],
                    enveloping=d['enveloping'],
                    ambiguous=d['ambiguous']
                    )
        layer.meta.update(d['meta'])

        for span_dict in d['spans']:
            base_span = to_base_span(span_dict['base_span'])
            for annotation in span_dict['annotations']:
                layer.add_annotation(base_span, **annotation)

        return layer

    def add_span(self, span: Span) -> Span:
        assert isinstance(span, Span), str(type(span))
        assert len(span.annotations) > 0, span
        assert self.ambiguous or len(span.annotations) == 1, span
        assert span.layer is self, span.layer

        if self.get(span) is not None:
            raise ValueError('this layer already has a span with the same base span')

        self._span_list.add_span(span)

        return span

    def remove_span(self, span):
        self._span_list.remove_span(span)

    def add_annotation(self, base_span, **attributes) -> Annotation:
        base_span = to_base_span(base_span)
        attributes = {**self.default_values, **{k: v for k, v in attributes.items() if k in self.attributes}}
        span = self.get(base_span)

        if self.enveloping is not None:
            if span is None:
                span = EnvelopingSpan(base_span=base_span, layer=self)
                annotation = span.add_annotation(Annotation(span, **attributes))
                self._span_list.add_span(span)
            else:
                annotation = span.add_annotation(Annotation(span, **attributes))

            return annotation

        if self.ambiguous:
            if span is None:
                span = Span(base_span, self)
                self._span_list.add_span(span)
            assert isinstance(span, Span), span
            return span.add_annotation(Annotation(span, **attributes))

        if span is not None:
            raise ValueError('the layer is not ambiguous and already contains this span')

        span = Span(base_span=base_span, layer=self)
        annotation = span.add_annotation(Annotation(span, **attributes))
        self._span_list.add_span(span)
        return annotation

    def check_span_consistency(self) -> None:
        """Checks for layer's span consistency

        """
        attribute_names = set(self.attributes)

        last_span = None
        for span in self:
            assert last_span is None or last_span < span
            last_span = span

            annotations = span.annotations

            assert len(annotations) > 0, 'the span {} has no annotations'.format(span)
            assert self.ambiguous or len(annotations) == 1, \
                'the layer is not ambiguous but the span {} has {} annotations'.format(span, len(annotations))

            for annotation in annotations:
                assert set(annotation) == attribute_names, \
                    'extra annotation attributes: {}, missing annotation attributes: {} in layer {!r}'.format(
                            set(annotation) - attribute_names,
                            attribute_names - set(annotation),
                            self.name)

    def count_values(self, attribute: str):
        """count attribute values, return frequency table"""
        if self.ambiguous:
            return collections.Counter(getattr(annotation, attribute)
                                       for span in self.spans for annotation in span.annotations)
        return collections.Counter(getattr(span, attribute) for span in self.spans)

    def groupby(self, by: Sequence[str], return_type: str = 'spans'):
        if isinstance(by, Sequence) and all(isinstance(b, str) for b in by):
            return layer_operations.GroupBy(layer=self, by=by, return_type=return_type)
        elif isinstance(by, Layer):
            return layer_operations.group_by(layer=self, by=by)
        raise ValueError(by)

    def rolling(self, window: int, min_periods: int = None, inside: str = None):
        return layer_operations.Rolling(self, window=window,  min_periods=min_periods, inside=inside)

    def __getattr__(self, item):
        if item in {'_ipython_canary_method_should_not_exist_', '__getstate__', '__setstate__'}:
            raise AttributeError
        if item in self.__getattribute__('attributes'):
            return self.__getitem__(item)

        return self.text_object._resolve(self.name, item, sofar=self._span_list)

    def _set_attributes(self, attributes: Sequence[str]):
        assert not isinstance(attributes, str), attributes
        attributes = tuple(attributes)
        assert all(attr.isidentifier() for attr in attributes), attributes
        assert len(attributes) == len(set(attributes)), 'repetitive attribute name: ' + str(attributes)
        super().__setattr__('attributes', attributes)

        for attr in set(self.default_values) - set(attributes):
            del self.default_values[attr]

        for attr in set(attributes) - set(self.default_values):
            self.default_values[attr] = None

    def __setattr__(self, key, value):
        if key == 'attributes':
            return self._set_attributes(value)
        if key == 'default_values':
            return super().__setattr__(key, value)
        # TODO: can 'name' be an attribute name?
        if key != 'name' and key in self.attributes:
            raise AttributeError(key)
        super().__setattr__(key, value)

    def __iter__(self):
        return iter(self._span_list.spans)

    def __setitem__(self, key: int, value: Span):
        self._span_list[key] = value

    def index(self, x, *args) -> int:
        return self._span_list.index(x, *args)

    def __getitem__(self, item) -> Union[Span, 'Layer', AmbiguousAttributeTupleList]:
        if isinstance(item, int):
            return self._span_list[item]

        if isinstance(item, BaseSpan):
            return self._span_list.get(item)

        if item == [] or item == ():
            raise IndexError('no attributes: ' + str(item))

        if isinstance(item, str) or isinstance(item, (list, tuple)) and all(isinstance(s, str) for s in item):
            return self.attribute_list(item)

        if isinstance(item, tuple) and len(item) == 2 \
           and (callable(item[0])
                or isinstance(item[0], (int, slice))
                or (isinstance(item[0], (tuple, list)) and all(isinstance(i, int) for i in item[0])))\
           and (isinstance(item[1], str)
                or isinstance(item[1], (list, tuple)) and all(isinstance(i, str) for i in item[1])):
            if isinstance(item[0], int):
                return self[item[1]][item[0]]
            return self[item[0]][item[1]]

        layer = Layer(name=self.name,
                      attributes=self.attributes,
                      text_object=self.text_object,
                      parent=self.parent,
                      enveloping=self.enveloping,
                      ambiguous=self.ambiguous,
                      default_values=self.default_values)
        layer._base = self._base

        if isinstance(item, slice):
            wrapped = self._span_list.spans.__getitem__(item)
            layer._span_list.spans = wrapped
            return layer
        if isinstance(item, (list, tuple)):
            if all(isinstance(i, bool) for i in item):
                if len(item) != len(self):
                    warnings.warn('Index boolean list not equal to length of layer: {}!={}'.format(len(item), len(self)))
                wrapped = [s for s, i in zip(self._span_list.spans, item) if i]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, int) for i in item):
                wrapped = [self._span_list.spans.__getitem__(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
            if all(isinstance(i, BaseSpan) for i in item):
                wrapped = [self._span_list.get(i) for i in item]
                layer._span_list.spans = wrapped
                return layer
        if callable(item):
            wrapped = [span for span in self._span_list.spans if item(span)]
            layer._span_list.spans = wrapped
            return layer

        raise TypeError('index not supported: ' + str(item))

    def __delitem__(self, key):
        self._span_list.remove_span(self[key])

    def get(self, item):
        if len(self._span_list) == 0:
            return
        if isinstance(item, Span):
            item = item.base_span
        if isinstance(item, BaseSpan):
            level = self._span_list[0].base_span.level
            if level == item.level:
                return self._span_list.get(item)
            item = item.reduce(level)

        if isinstance(item, (list, tuple)):
            layer = Layer(name=self.name,
                          attributes=self.attributes,
                          text_object=self.text_object,
                          parent=self.parent,
                          enveloping=self.enveloping,
                          ambiguous=self.ambiguous,
                          default_values=self.default_values)
            layer._base = self._base

            wrapped = [self._span_list.get(i) for i in item]
            assert all(s is not None for s in wrapped)
            layer._span_list.spans = wrapped
            return layer

        raise ValueError(item)

    def __len__(self):
        return len(self._span_list)

    def __str__(self):
        return 'Layer(name={self.name!r}, attributes={self.attributes}, spans={self._span_list})'.format(self=self)

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer name': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self._span_list.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    def display(self, **kwargs):
        from estnltk.visualisation import DisplaySpans
        display_spans = DisplaySpans(**kwargs)
        display_spans(self)

    def to_html(self, header='Layer', start_end=False):
        res = []
        table2 = None
        base_layer = self
        if self._base:
            base_layer = self.text_object[self._base]
        if base_layer.enveloping:
            if self.ambiguous:
                attributes = ['text', 'start', 'end'] + self.attributes
                aatl = AmbiguousAttributeTupleList((((getattr(es, name) for name in attributes) for es in eas)
                                                    for eas in self), attributes)
                table2 = aatl.to_html(index='text')
            else:
                for span in base_layer.span_list:
                    # html.escape(span[i].text) TODO?
                    t = ['<b>', self.text_object.text[span[0].start:span[0].end], '</b>']
                    for i in range(1, len(span)):
                        t.extend([self.text_object.text[span[i - 1].end: span[i].start], '<b>',
                                  self.text_object.text[span[i].start:span[i].end], '</b>'])
                    t = ''.join(t)
                    res.append({'text': t, 'start': span.start, 'end': span.end,
                                **{k: span.__getattribute__(k) for k in self.attributes}})
        else:
            if self.ambiguous:
                for record in self.to_records(True):
                    first = True
                    for rec in record:
                        if not first:
                            rec['text'] = ''
                        res.append(rec)
                        first = False
            else:
                res = self.to_records(True)
        if start_end:
            columns = ('text', 'start', 'end') + tuple(self.attributes)
        else:
            columns = ('text',) + tuple(self.attributes)
        df = pandas.DataFrame.from_records(res, columns=columns)
        pandas.set_option('display.max_colwidth', -1)
        table1 = self.metadata().to_html(index=False, escape=False)
        if table2 is None:
            table2 = df.to_html(index=False, escape=True)
        if header:
            return '\n'.join(('<h4>' + header + '</h4>', table1, table2))
        return '\n'.join((table1, table2))

    print_start_end = False

    def _repr_html_(self):
        if self.meta:
            data = {'key': sorted(self.meta), 'value': [self.meta[k] for k in sorted(self.meta)]}
            meta_table = pandas.DataFrame(data, columns=['key', 'value'])
            meta_table = meta_table.to_html(header=False, index=False)
            meta = '\n'.join(('<h4>Metadata</h4>', meta_table))
        else:
            meta = ''

        attributes = []
        if self.text_object is None:
            text_object = 'No Text object.'
        else:
            attributes.append('text')
            text_object = ''
        if self.print_start_end:
            attributes.extend(['start', 'end'])
        attributes.extend(self.attributes)
        if not attributes:
            attributes = ['start', 'end']
        table_1 = self.metadata().to_html(index=False, escape=False)
        table_2 = ''
        if attributes:
            table_2 = self.attribute_list(attributes).to_html(index='text')
        return '\n'.join(('<h4>{}</h4>'.format(self.__class__.__name__), meta, text_object, table_1, table_2))

    def __repr__(self):
        return str(self)

    def diff(self, other):
        if not isinstance(other, Layer):
            return 'Other is not a Layer.'
        if self.name != other.name:
            return "Layer names are different: {self.name}!={other.name}".format(self=self, other=other)
        if tuple(self.attributes) != tuple(other.attributes):
            return "{self.name} layer attributes differ: {self.attributes} != {other.attributes}".format(self=self,
                                                                                                         other=other)
        if self.ambiguous != other.ambiguous:
            return "{self.name} layer ambiguous differs: {self.ambiguous} != {other.ambiguous}".format(self=self,
                                                                                                       other=other)
        if self.parent != other.parent:
            return "{self.name} layer parent differs: {self.parent} != {other.parent}".format(self=self, other=other)
        if self.enveloping != other.enveloping:
            return "{self.name} layer enveloping differs: {self.enveloping}!={other.enveloping}".format(self=self,
                                                                                                        other=other)
        if self._span_list != other._span_list:
            return "{self.name} layer spans differ".format(self=self)
        return None

    def __eq__(self, other):
        return self.diff(other) is None


import estnltk.layer_operations as layer_operations
