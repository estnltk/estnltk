import abc
import bisect
import collections
import keyword  # type: ignore
from typing import Tuple, List, Dict, Any, Sequence


class Text:
    def __init__(self, text: str) -> None:
        self._text = text
        self._layers = {}  # type: dict

    @property
    def text(self) -> str:
        return self._text

    @property
    def layers(self) -> Dict[str, 'Layer']:
        return self._layers

    def add_layer(self, layer: 'Layer') -> None:
        name = layer.name

        # Making sure we have an unused name for the layer
        assert (name not in self.layers.keys()  # name not already used for a layer in this object
                and name not in self.__dict__.keys()  # name not in use for the Text instance
                and name not in self.__class__.__dict__.keys())  # name not in use for the Text class
        layer.bind(self)
        self._layers[name] = layer

    def __getattr__(self, item):  # type: ignore
        try:
            return collections.ChainMap(
                self.__class__.__dict__,
                self.__dict__,
                self.layers
            )[item]
        except KeyError as e:
            # AttributeError is more appropriate here.
            raise AttributeError(*e.args)

    def __delattr__(self, item):
        assert item in self.layers.keys()
        del self.layers[item]

    def __str__(self):
        return 'Text(text="{text}", \n\tlayers=[{layers}]\n)'.format(
            text=self.text,
            layers='\n'.join(str(i) for i in self.layers.values())
        )


class AbstractLayer(Sequence, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def text(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def bound(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def bind(self, text_object: Text) -> None:
        pass

    @property
    @abc.abstractmethod
    def text_object(self):
        pass

    @property
    @abc.abstractmethod
    def frozen(self) -> bool:
        pass

    @abc.abstractmethod
    def freeze(self) -> None:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def text(self) -> List[str]:
        pass

    @abc.abstractmethod
    def add_span(self, span: 'Span') -> None:
        pass


class AbstractSpan(metaclass=abc.ABCMeta):
    __slots__ = []

    @property
    @abc.abstractmethod
    def start(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def end(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def bound(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def text(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def layer(self):
        pass

    @abc.abstractmethod
    def bind(self, layer: 'AbstactLayer') -> None:
        pass

    @abc.abstractmethod
    def __lt__(self, other: Any) -> bool:
        pass

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass

    @abc.abstractmethod
    def __le__(self, other: Any) -> bool:
        pass


class BaseSpan(AbstractSpan):
    __slots__ = ['_layer', '_bound']

    @property
    def layer(self) -> 'BaseLayer':
        return self._layer

    @property
    def bound(self) -> bool:
        return self._bound

    def bind(self, layer: 'Layer') -> None:
        self._bound = True
        self._layer = layer

    # ORDERING

    def __validate_ordering(self, other: 'Span') -> None:
        assert isinstance(other, BaseSpan)

    def __lt__(self, other: Any) -> bool:
        self.__validate_ordering(other)
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        self.__validate_ordering(other)
        return (self.start, self.end) == (other.start, other.end)

    def __le__(self, other: Any) -> bool:
        self.__validate_ordering(other)
        return self < other or self == other


class DependantSpan(BaseSpan):
    __slots__ = ['_parent']

    def __init__(self, parent: AbstractSpan):
        self._bound = False
        self._parent = parent

    @property
    def end(self):
        return self.parent.end

    @property
    def start(self):
        return self.parent.start

    @property
    def text(self):
        return self.parent.text

    @property
    def parent(self):
        return self._parent

    def __getattr__(self, item):
        try:
            return getattr(self.parent, item)
        except AttributeError:
            raise


class Span(BaseSpan):
    __slots__ = ['_start', '_end', '_layer', '_bound']

    def __init__(self, start: int, end: int, layer: 'Layer' = None) -> None:
        assert start < end
        self._start = start
        self._end = end

        if layer is None:
            # If a layer has not been explicitly given, we consider the Span unbound until it has been added to a layer.
            self._bound = False
        else:
            self._bound = True
        self._layer = layer

    @property
    def start(self) -> int:
        return self._start

    @property
    def end(self) -> int:
        return self._end

    @property
    def text(self) -> str:
        return self.layer.text_object.text[self.start:self.end]

    def __getattr__(self, item):
        if item == 'text':
            if not self.bound:
                raise AttributeError('No text for unbound Spans')
            else:
                raise AttributeError('We are bound but have no text? The layer we are bound to must be unbound.')
        if item in self.__slots__:
            return None
        else:
            #we haven't found the attribute. Do we have dependants that have it?
            for layer in self.layer.text_object.layers.values():
                if isinstance(layer, DependantLayer) and layer.parent == self.layer and item in layer.attributes:
                    #check if the layer has a span that corresponds to this span
                    for span in layer.spans:
                        if span.parent == self:
                            return getattr(span, item)
            raise AttributeError

    def __str__(self):
        return 'Span({text}, {rest})'.format(
            text=self.text,
            rest=', '.join('{key}={value}'.format(
                key=k,
                value=getattr(self, k, None)
            ) for k in self.__slots__ if not k.startswith('_'))
        )

    def __repr__(self):
        return str(self)

    # TODO: think up a better name.
    def mark(self, name: str):
        assert self.bound and self.layer.bound, 'Span must be bound to a bound layer to have dependants'

        layer = self.layer.text_object.layers[name]
        assert layer.parent is self.layer, 'We must be accessing a layer that is dependant on this one'

        # TODO: Speedup. Remove iteration.
        for span in layer.spans:
            if span.parent is self:
                return span

        depspan = DependantSpan(parent=self)
        return layer.add_span(depspan)


class SpanList(collections.Sequence):
    def __init__(self, frozen: bool = False) -> None:
        self.spans = []  # type: list[AbstractSpan]
        self._frozen = frozen
        self._bound = False

    def bind(self, parent: 'Layer') -> None:
        self._parent = parent
        self._bound = True

    @property
    def parent(self):
        return self._parent

    @property
    def bound(self):
        return self._bound

    @property
    def start(self):
        return self.spans[0].start

    def end(self):
        return self.spans[-1].end

    @property
    def text(self):
        return [span.text for span in self.spans]

    def defer(self, item):
        return [span.mark(item) for span in self.spans]


    def __getattr__(self, item: str) -> List[Any]:
        self.spans  # type: List[DependantSpan]

        text = self.spans[0].layer.text_object
        try:
            layer = text.layers[item]
        except KeyError:
            # we are trying to access 'item' that is not a layer.
            # I'd guess that it is an attribute of the main span then
            if item in self.spans[0].parent.layer.attributes:
                return [getattr(span.parent, item) for span in self.spans]
            else:
                #we guessed wrong. Is it an attribute of a dependant layer?
                for layer in self.spans[0].layer.text_object.layers.values():
                    print(self.spans[0].layer.name)
                    if isinstance(layer, DependantLayer) and layer.parent == self.spans[0].layer and item in layer.attributes:
                        # check if the layer has a span that corresponds to this span
                        #TODO: speedup
                        return [getattr(span, item) for span in self.spans if span in [i.parent for i in layer.spans]]
                raise KeyError



        try:
            return [span for span in layer.spans if span in self.spans]
        except AttributeError:
            raise

    @property
    def frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> None:
        self._frozen = True

    def add(self, span: Span) -> None:
        if self.frozen:
            raise AssertionError('Can not add to frozen SpanList')
        bisect.insort(self.spans, span)

    def __iter__(self):
        yield from self.spans

    def __len__(self) -> int:
        return len(self.spans)

    def __contains__(self, item: Any) -> bool:
        return item in self.spans

    def __getitem__(self, idx: int) -> Span:
        return self.spans[idx]

    def __lt__(self, other: Any) -> bool:
        return (self.start, self.end) < (other.start, other.end)

    def __eq__(self, other: Any) -> bool:
        return (self.start, self.end) == (other.start, other.end)

    def __le__(self, other: Any) -> bool:
        return self < other or self == other

    def __str__(self):
        return 'SpanList({spans})'.format(spans=','.join(str(i) for i in self.spans))


class BaseLayer(AbstractLayer):
    @property
    def attributes(self):
        return self._attributes

    def __len__(self):
        return len(self.spans)

    def __iter__(self):
        yield from self.spans

    @property
    def bound(self) -> bool:
        return self._bound

    @property
    def text_object(self) -> Text:
        return self._text_object

    @property
    def spans(self) -> SpanList:
        return self._spans

    @property
    def name(self) -> str:
        return self._name

    @property
    def frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> None:
        if not self.frozen:
            self.spans.freeze()
            self._frozen = True

    @property
    def text(self) -> List[str]:
        return [span.text for span in self.spans]

    def bind(self, text_object: Text) -> None:
        self._bound = True
        self._text_object = text_object

    def __getitem__(self, item):
        return self.spans[item]

    def __getattr__(self, item):
        if item in self.attributes:
            return [getattr(span, item) for span in self.spans]
        else:
            try:

                if item in getattr(self.parent, '_attributes'):
                    return [getattr(span, item) for span in self.spans]
            except Exception as e:
                # print(e)
                raise AttributeError('{item} not in layer {layer}'.format(item=item, layer=self.name))

        raise AttributeError


class Layer(BaseLayer):
    def __init__(self, *, text_object: Text = None,
                 name: str,
                 frozen: bool = False,
                 spans=None,
                 attributes: List[str] = None
                 ) -> None:
        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'
        self._name = name

        if attributes is not None:
            for attribute in attributes:
                assert attribute.isidentifier() and not keyword.iskeyword(
                    attribute), 'Layer name must be a valid python identifier'
                assert attribute not in Span.__slots__
                assert attribute not in Span.__class__.__dict__.keys()

            self.Span = type('Span', (Span,), {'__slots__': attributes})
            self._attributes = attributes
        else:
            self._attributes = tuple()

        if text_object is None:
            self._bound = False
        else:
            assert isinstance(text_object, Text)
            self._bound = True
            self._text_object = text_object

        self._spans = SpanList()
        if spans:
            for span in spans:
                self._spans.add(span)
        self._frozen = frozen
        if frozen:
            self._spans.freeze()

    @classmethod
    def from_span_tuples(cls, name: str, spans: List[Tuple[int, int]], attributes=None) -> 'Layer':
        layer = Layer(name=name, attributes=attributes)
        _spans = [Span(start, end) for start, end in spans]
        for span in _spans:
            layer.add_span(span)
        return layer

    @classmethod
    def from_span_dict(cls, name: str, spans: Dict, attributes=None) -> 'Layer':
        layer = Layer(name=name, attributes=attributes)
        for span in spans:
            new = layer.add_span(Span(span['start'], span['end']))
            for k, v in span.items():
                if k in attributes:
                    setattr(new, k, v)
        return layer

    def add_span(self, span: Span) -> Span:
        if hasattr(self, 'Span'):
            span = self.Span(span.start, span.end)
        span.bind(self)
        self.spans.add(span)
        return span

    def __str__(self):
        return 'Layer(name={name}, spans=[{spans}])'.format(
            name=self.name,
            spans=', '.join(str(i) for i in self.spans)
        )


class DependantLayer(BaseLayer):
    def __init__(self, *, text_object: Text = None,
                 name: str,
                 frozen: bool = False,
                 spans=None,
                 attributes: List[str] = None,
                 parent: AbstractLayer
                 ) -> None:

        # Let's not allow chains of dependancies for now
        assert not isinstance(parent, DependantLayer)
        assert isinstance(parent, Layer)

        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'
        self._name = name

        if attributes is not None:
            for attribute in attributes:
                assert attribute.isidentifier() and not keyword.iskeyword(
                    attribute), 'Layer name must be a valid python identifier'
                assert attribute not in Span.__slots__
                assert attribute not in Span.__class__.__dict__.keys()

            self.Span = type('Span', (DependantSpan,), {'__slots__': attributes})
            self._attributes = attributes
        else:
            self._attributes = tuple()

        if text_object is None:
            self._bound = False
        else:
            assert isinstance(text_object, Text)
            self._bound = True
            self._text_object = text_object

        self._spans = SpanList()
        if spans:
            for span in spans:
                self._spans.add(span)
        self._frozen = frozen
        if frozen:
            self._spans.freeze()
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def add_span(self, span: DependantSpan) -> None:
        if hasattr(self, 'Span'):
            span = self.Span(span.parent)
        span.bind(self)
        self.spans.add(span)
        return span


class EnvelopingLayer(BaseLayer):
    def __init__(self, *,
                 text_object: Text = None,
                 name: str,
                 envelops: Layer,
                 attributes: List[str] = None
                 ) -> None:
        assert name.isidentifier() and not keyword.iskeyword(name), 'Layer name must be a valid python identifier'
        self._name = name

        self._envelops = envelops

        if attributes is not None:
            for attribute in attributes:
                assert attribute.isidentifier() and not keyword.iskeyword(
                    attribute), 'Layer name must be a valid python identifier'
                assert attribute not in Span.__slots__
                assert attribute not in Span.__class__.__dict__.keys()

            self.Span = type('Span', (DependantSpan,), {'__slots__': attributes})
            self._attributes = attributes
        else:
            self.Span = type('Span', (DependantSpan,), {'__slots__': []})
            self._attributes = tuple()

        if text_object is None:
            self._bound = False
        else:
            assert isinstance(text_object, Text)
            self._bound = True
            self._text_object = text_object

        self._spans = SpanList()

    @property
    def parent(self):
        return self._envelops

    def add_spans(self, spans):
        if hasattr(self, 'Span'):
            wrapper = self.Span
        else:
            wrapper = lambda x: x

        sl = SpanList()
        sl.bind(parent=self)

        for span in spans:
            sp = wrapper(span)
            sp.bind(self)
            sl.add(
                sp
            )
        sl.freeze()
        self.spans.add(
            sl
        )

    def add_span(self, spans):
        raise NotImplementedError('add_span not implemented EnvelopingLayer')



def words_sentences(text):
    from estnltk import Text as OldText
    old = OldText(text)
    old.sentences
    old.words
    old.paragraphs
    # print(dict(old))
    new = Text(text)
    words = Layer.from_span_tuples(spans=old.spans('words'), name='words')
    new.add_layer(words)
    old_sentences = old.split_by('sentences')
    sentences = EnvelopingLayer(envelops=words, name='sentences')
    i = 0
    new_sentences = []
    for sentence in old_sentences:
        sent = []
        for word in sentence.words:
            sent.append(words[i])
            i += 1
        new_sentences.append(sent)
    for sentence in new_sentences:
        sentences.add_spans(sentence)
    new.add_layer(sentences)
    return new
