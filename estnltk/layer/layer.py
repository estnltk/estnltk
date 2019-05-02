import keyword
from typing import Union, List, Sequence
import pandas
import collections
import warnings

from estnltk import Span, EnvelopingSpan, AmbiguousSpan, Annotation, SpanList
from estnltk.layer import AmbiguousAttributeTupleList
from estnltk.visualisation import DisplaySpans


def whitelist_record(record, source_attributes):
    # the goal is to only keep the keys explicitly listed in source_attributes

    # record might be a dict:
    if isinstance(record, dict):
        res = {}
        for k in source_attributes:
            res[k] = record.get(k, None)
        return res

    else:
        # record might be nested
        return [whitelist_record(i, source_attributes) for i in record]


class Layer:
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

        # list of legal attribute names for the layer
        assert not isinstance(attributes, str), attributes
        attributes = tuple(attributes)
        assert all(attr.isidentifier() for attr in attributes), attributes
        self.attributes = attributes
        assert len(attributes) == len(set(attributes)), 'repetitive attribute name: ' + str(attributes)

        # name of the layer
        assert name.isidentifier() and not \
               keyword.iskeyword(name), 'layer name must be a valid python identifier, {!r}'.format(name)
        assert name != 'text'
        self.name = name

        # the name of the parent layer.
        self.parent = parent

        self._is_frozen = False

        # marker for creating a lazy layer
        # used in Text._add_layer to check if additional work needs to be done
        self._is_lazy = False

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
        self.span_list = SpanList(layer=self)

        # boolean for if this is an ambiguous layer
        # if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous  # type: bool

        self.default_values = default_values or {}

        for attr in self.attributes:
            if attr not in self.default_values:
                self.default_values[attr] = None

        # placeholder. is set when `_add_layer` is called on text object
        self.text_object = text_object  # type: Text

        self.meta = {}

    @property
    def layer(self):
        return self

    @property
    def start(self):
        return self.span_list.spans[0].start

    @property
    def end(self):
        return self.span_list.spans[-1].end

    @property
    def spans(self):
        return self.span_list.spans

    @property
    def text(self):
        result = []
        for span in self.span_list.spans:
            if isinstance(span, EnvelopingSpan):
                result.extend(span.text)
            else:
                result.append(span.text)
        return result

    @property
    def enclosing_text(self):
        return self.text_object.text[self.start:self.end]

    def freeze(self):
        self._is_frozen = True

    def unfreeze(self):
        if self.text_object is None:
            self._is_frozen = False
            return
        for layer in self.text_object.layers.values():
            assert not layer.enveloping == self.name, "can't unfreeze. This layer is enveloped by " + layer.name
            assert not layer.parent == self.name, "can't unfreeze. This layer is parent of " + layer.name
        self._is_frozen = False

    @property
    def is_frozen(self):
        return self._is_frozen

    def from_records(self, records, rewriting=False) -> 'Layer':
        if self.parent is not None:
            self._is_lazy = True

        if self.ambiguous:
            if rewriting:
                self.span_list = SpanList(layer=self)
                tmpspans = []
                for record_line in records:
                    span = Span(start=record_line[0]['start'], end=record_line[0]['end'], layer=self, legal_attributes=self.attributes)
                    span.add_annotation(**record_line[0])

                    spns = AmbiguousSpan(layer=self, span=span)
                    for record in record_line:
                        spns.add_annotation(**record)
                    tmpspans.append(spns)
                self.span_list.spans = tmpspans
            else:
                for record_line in records:
                    for record in record_line:
                        self.add_annotation(Span(start=record['start'], end=record['end']), **record)
        else:
            if rewriting:
                spns = SpanList(layer=self)

                for record in records:
                    if record is None:
                        continue
                    sp = Span(start=record['start'], end=record['end'], layer=self)
                    sp.add_annotation(**record)
                    spns.add_span(sp)
                self.span_list = spns
            else:
                for record in records:
                    self.add_annotation(Span(start=record['start'], end=record['end']), **record)
        return self

    def attribute_list(self, attributes):
        return self.span_list.attribute_list(attributes)

    def get_attributes(self, items):
        return self.__getattribute__('span_list').get_attributes(items)

    def to_records(self, with_text=False):
        return self.span_list.to_records(with_text)

    def add_span(self, span: Union[Span, EnvelopingSpan]) -> Span:
        assert not self.is_frozen, "can't add spans to frozen layer"
        assert isinstance(span, (EnvelopingSpan, Span, Layer, Annotation)), str(type(span))
        if isinstance(span, Layer):
            span = EnvelopingSpan(spans=span.spans)
        for attr in self.attributes:
            try:
                if isinstance(span, EnvelopingSpan):
                    if attr not in span._attributes:
                        raise AttributeError
                else:
                    getattr(span, attr)
            except AttributeError:
                if isinstance(span, Span):
                    setattr(span[0], attr, self.default_values[attr])
                else:
                    setattr(span, attr, self.default_values[attr])

        span.add_layer(self)
        target = self.span_list.get(span)
        if self.ambiguous:
            if target is None:
                new = AmbiguousSpan(layer=self, span=span)
                new.add_span(span)
                self.span_list.add_span(new)
                new.parent = span.parent
            else:
                assert isinstance(target, AmbiguousSpan)
                target.add_span(span)
        else:
            if target is None:
                self.span_list.add_span(span)
            else:
                raise ValueError('this layer is not ambiguous and the span is already in the spanlist', span)
        return span

    def remove_span(self, span):
        self.span_list.remove_span(span)

    def add_annotation(self, base_span, **attributes):
        if self.parent is not None and self.ambiguous:
            span = self.span_list.get(base_span)
            if span is None:
                span = AmbiguousSpan(self, base_span)
                self.span_list.add_span(span)
            assert isinstance(span, AmbiguousSpan), span
            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            return span.add_annotation(**attributes_pluss_default_values)

        if self.enveloping is not None:
            span = EnvelopingSpan(spans=base_span, layer=self)

            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            annotation = span.add_annotation(**attributes_pluss_default_values)
            self.span_list.add_span(span)
            return annotation

        if self.parent is None and self.enveloping is None and self.ambiguous:
            span = self.span_list.get(base_span)
            if span is None:
                span = AmbiguousSpan(self, Span(base_span.start, base_span.end, layer=self))
                self.span_list.add_span(span)
            assert isinstance(span, AmbiguousSpan), span
            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            return span.add_annotation(**attributes_pluss_default_values)

        if self.parent is None and self.enveloping is None and not self.ambiguous:
            if self.span_list.get(base_span) is not None:
                raise ValueError('the layer is not ambiguous and already contains this span')

            attributes_pluss_default_values = self.default_values.copy()
            attributes_pluss_default_values.update(attributes)
            span = Span(base_span.start, base_span.end, layer=self)
            span.add_annotation(**attributes_pluss_default_values)
            self.span_list.add_span(span)
            return span.annotations[0]

        # TODO: implement add_annotation
        raise NotImplementedError('add_annotation not yet implemented for this type of layer')

    def check_span_consistency(self) -> None:
        # Checks for layer's span consistency
        starts_ends = set()
        for span in self.span_list.spans:
            # Check for duplicate locations
            assert (span.start, span.end) not in starts_ends, \
                   '(!) {} is a span with duplicate location!'.format(span)
            starts_ends.add( (span.start, span.end) )
            # Check for ambiguous spans
            if self.ambiguous:
                assert isinstance(span, AmbiguousSpan), \
                       '(!) {} should be AmbiguousSpan'.format(span)
            # Check that the span is connected with the layer
            if isinstance(span, (EnvelopingSpan, AmbiguousSpan)):
                assert self == span.layer, \
                       '(!) missing or wrong layer: {}'.format(span.layer)
            # Check attributes of AmbiguousSpan
            if isinstance(span, AmbiguousSpan):
                for annotation in span.annotations:
                    # Check for missing attributes in Annotations
                    for attr in self.attributes:
                        attrib_exists = True
                        try:
                            getattr(annotation, attr)
                        except AttributeError:
                            attrib_exists = False
                        assert attrib_exists, \
                               '(!) Annotation missing attribute {}'.format(attr)
                    # Check for redundant attributes in Annotations
                    for anno_attr in annotation._attributes:
                        assert anno_attr in self.attributes, \
                       '(!) Annotation has redundant attribute {}'.format(anno_attr)
            # Check attributes of EnvelopingSpan and Span
            elif isinstance(span, (EnvelopingSpan, Span)):
                # Check for existence of layer's attributes
                for attr in self.attributes:
                    assert hasattr(span, attr), \
                       '(!) missing attribute {} in {}'.format(attr, span)
                # Check for redundant attributes
                for span_attr in span.legal_attribute_names:
                    assert span_attr in self.attributes, \
                       '(!) redundant attribute {} in {}'.format(span_attr, span)

    def rewrite(self, source_attributes: List[str], target_attributes: List[str], rules, **kwargs):
        assert 'name' in kwargs.keys(), '"name" must currently be an argument to layer'
        res = [whitelist_record(record, source_attributes + ('start', 'end')) for record in
               self.to_records(with_text='text' in source_attributes)]
        rewritten = [rules.rewrite(j) for j in res]
        resulting_layer = Layer(
            **kwargs,
            attributes=target_attributes,
            parent=self.name

        ).from_records(
            rewritten, rewriting=True
        )

        return resulting_layer

    def _add_spans(self, spans: List['Span']) -> List['Span']:
        assert not self.is_frozen, "can't add spans to frozen layer"
        assert self.ambiguous or self.enveloping
        res = []
        for span in spans:
            res.append(self.add_span(span))
        return res

    def _resolve(self, target):
        if target in self.attributes:
            raise AssertionError('This path should not be taken')
        else:
            return self.text_object._resolve(self.name, target)

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
        if item in {'_ipython_canary_method_should_not_exist_', '__getstate__'}:
            raise AttributeError
        if item in self.__getattribute__('__dict__').keys():
            return self.__getattribute__('__dict__')[item]
        if item in self.__getattribute__('attributes'):
            return self.__getitem__(item)

        return self.text_object._resolve(self.name, item, sofar=self.span_list)

    def __setattr__(self, key, value):
        # TODO: can 'name' be an attribute name?
        if key != 'attributes' and key != 'name' and key in self.attributes:
            raise AttributeError(key)
        super().__setattr__(key, value)

    def __getitem__(self, item) -> Union[Span, 'Layer', AmbiguousAttributeTupleList]:
        if item == [] or item == ():
            raise IndexError('no attributes: ' + str(item))

        if isinstance(item, str) or isinstance(item, (list, tuple)) and all(isinstance(s, str) for s in item):
            return self.span_list.attribute_list(item)

        if isinstance(item, int):
            wrapped = self.span_list.spans.__getitem__(item)
            return wrapped

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
            wrapped = self.span_list.spans.__getitem__(item)
            layer.span_list.spans = wrapped
            return layer
        if isinstance(item, (list, tuple)):
            if all(isinstance(i, bool) for i in item):
                if len(item) != len(self):
                    warnings.warn('Index boolean list not equal to length of layer: {}!={}'.format(len(item), len(self)))
                wrapped = [s for s, i in zip(self.span_list.spans, item) if i]
                layer.span_list.spans = wrapped
                return layer
            if all(isinstance(i, int) for i in item):
                wrapped = [self.span_list.spans.__getitem__(i) for i in item]
                layer.span_list.spans = wrapped
                return layer
        if callable(item):
            wrapped = [span for span in self.span_list.spans if item(span)]
            layer.span_list.spans = wrapped
            return layer

        raise TypeError('index not supported: ' + str(item))

    def get(self, item):
        if isinstance(item, Span):
            return self.span_list.get(span=item)
        if isinstance(item, EnvelopingSpan):
            result = self.span_list.get(span=item)
            if result is not None:
                return result
            item = item.spans
        if isinstance(item, (list, tuple)):
            layer = Layer(name=self.name,
                          attributes=self.attributes,
                          text_object=self.text_object,
                          parent=self.parent,
                          enveloping=self.enveloping,
                          ambiguous=self.ambiguous,
                          default_values=self.default_values)
            layer._base = self._base

            wrapped = [self.span_list.get(i) for i in item]
            assert all(s is not None for s in wrapped)
            layer.span_list.spans = wrapped
            return layer

        raise ValueError(item)

    def __len__(self):
        return len(self.span_list)

    def __str__(self):
        return 'Layer(name={self.name!r}, attributes={self.attributes}, spans={self.span_list})'.format(self=self)

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer name': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self.span_list.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    def display(self):
        display_spans = DisplaySpans()
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
            table_2 = self.span_list.attribute_list(attributes).to_html(index='text')
        return '\n'.join(('<h4>{}</h4>'.format(self.__class__.__name__), text_object, table_1, table_2))

    def __repr__(self):
        return str(self)

    def diff_spans(self, other: 'Layer'):
        return sorted(set(self.span_list).symmetric_difference(other.span_list))

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
        if self._base != other._base:
            return "{self.name} layer _base differs: {self._base} != {other._base}".format(self=self, other=other)
        if self.enveloping != other.enveloping:
            return "{self.name} layer enveloping differs: {self.enveloping}!={other.enveloping}".format(self=self,
                                                                                                        other=other)
        if self.span_list != other.span_list:
            return "{self.name} layer spans differ".format(self=self, other=other)
        return None

    def __eq__(self, other):
        return self.diff(other) is None


import estnltk.layer_operations as layer_operations
