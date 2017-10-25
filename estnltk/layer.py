import bisect
from typing import Tuple, Union, List
import pandas



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
                 name: str = None,
                 attributes: Union[Tuple, List] = tuple(),
                 parent: str = None,
                 enveloping: str = None,
                 ambiguous: bool = False
                 ) -> None:
        assert not ((parent is not None) and (enveloping is not None)), 'Cant be derived AND enveloping'

        assert name is not None, 'Layer must have a name'

        # name of the layer
        self.name = name

        # list of legal attribute names for the layer
        self.attributes = attributes

        # the name of the parent layer.
        self.parent = parent

        # has this layer been added to a text object
        self._bound = False

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
        self.spans = SpanList(layer=self, ambiguous=ambiguous)

        # boolean for if this is an ambiguous layer
        # if True, add_span will behave differently and add a SpanList instead.
        self.ambiguous = ambiguous  # type: bool

        # placeholder. is set when `_add_layer` is called on text object
        self.text_object = None  # type:Text

    def from_records(self, records, rewriting=False) -> 'Layer':
        if self.parent is not None and not self._bound:
            self._is_lazy = True

        if self.ambiguous:
            if rewriting:
                self.spans = SpanList(ambiguous=True, layer=self)
                tmpspans = []
                for record_line in records:
                    if record_line is not None:
                        spns = SpanList(layer=self, ambiguous=False)
                        spns.spans = [Span(**{**record, **{'layer': self}}, legal_attributes=self.attributes)
                                      for record in record_line]
                        tmpspans.append(spns)
                        self.spans.classes[(spns.spans[0].start, spns.spans[0].end)] = spns
                self.spans.spans = tmpspans
            else:
                for record_line in records:
                    self._add_spans([Span(**record, legal_attributes=self.attributes) for record in record_line])
        else:
            if rewriting:
                spns = SpanList(layer=self, ambiguous=False)
                spns.spans = [Span(**{**record, **{'layer': self}}, legal_attributes=self.attributes) for record in
                              records if record is not None]

                self.spans = spns
            else:
                for record in records:
                    self.add_span(Span(
                        **record,
                        legal_attributes=self.attributes
                    ))
        return self

    def to_records(self, with_text=False):
        records = []

        for item in self.spans:
            records.append(item.to_record(with_text))

        return records

    def add_span(self, span: 'Span') -> 'Span':
        return self.spans.add_span(span)

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

    def _add_spans_to_enveloping(self, spans):
        spanlist = SpanList(
            layer=self
        )
        spanlist.spans = spans
        bisect.insort(self.spans.spans, spanlist)
        return spanlist

    def _add_spans(self, spans: List['Span']) -> List['Span']:
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

    def __getattr__(self, item):
        if item in {'_ipython_canary_method_should_not_exist_', '__getstate__'}:
            raise AttributeError
        if item in self.__getattribute__('__dict__').keys():
            return self.__getattribute__('__dict__')[item]
        elif item in self.__getattribute__('attributes'):
            return self.spans.__getattr__(item)
        else:
            return self.__getattribute__('_resolve')(item)

    def __getitem__(self, idx):
        res = self.spans.__getitem__(idx)
        return res

    def __str__(self):
        return 'Layer(name={self.name}, spans={self.spans})'.format(self=self)

    def metadata(self):
        """
        Return DataFrame with layer metadata.
        """
        rec = [{'layer name': self.name,
                'attributes': ', '.join(self.attributes),
                'parent': str(self.parent),
                'enveloping': str(self.enveloping),
                'ambiguous': str(self.ambiguous),
                'span count': str(len(self.spans.spans))}]
        return pandas.DataFrame.from_records(rec,
                                             columns=['layer name', 'attributes',
                                                      'parent', 'enveloping',
                                                      'ambiguous', 'span count'])

    def to_html(self, header='Layer', start_end=False):
        res = []
        base_layer = self
        if self._base:
            base_layer = self.text_object[self._base]
        if base_layer.enveloping:
            if self.ambiguous:
                # TODO: _repr_html_ for enveloping ambiguous layers
                return repr(self)
            else:
                for span in base_layer.spans:
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
        table2 = df.to_html(index=False, escape=False)
        if header:
            return '\n'.join(('<h4>' + header + '</h4>', table1, table2))
        return '\n'.join((table1, table2))

    def _repr_html_(self):
        return self.to_html()

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
        if self.spans != other.spans:
            return "{self.name} layer spans differ".format(self=self, other=other)
        return None

    def __eq__(self, other):
        return not self.diff(other)


from .spans import Span, SpanList
