from typing import Iterable


class BaseSpan:
    '''
    BaseSpan is class that defines meta information about a Span and is used when creating a Span.
    A BaseSpan can be given a level, start and end of a Span which then make sure that the Span is
    in the right position in a Layer.

    Level of a BaseSpan determines its positional structure: whether it is a raw text position 
    or is enveloping around sequences of smaller level text positions.
    
    *) ElementaryBaseSpan has level = 0, and it corresponds to a raw text position: 
         (start, end);
    
    *) EnvelopingBaseSpan at level = 1 corresponds to a sequence of ElementaryBaseSpan-s:
         [(start_1, end_1), ..., (start_N, end_N)]

    *) EnvelopingBaseSpan at level = 2 corresponds to a sequence of level 1 EnvelopingBaseSpans:
         [((start_11, end_11), ... ), ... ((start_N1, end_N1), ...)]

    And so forth.

    Note #1: In case of layers in parent-child relation, a child span has the same level as 
    the parent span. So, if the parent layer is made of level 0 spans (ElementaryBaseSpan-s), 
    then the child layer also has level 0 spans.
    
    Note #2: BaseSpans are immutable: once initialized, they cannot be changed anymore.
    '''
    __slots__ = ['_raw', '_hash', 'start', 'end', 'level']

    def __init__(self, raw, level: int, start: int, end: int):
        super().__setattr__('_raw',  raw)
        super().__setattr__('_hash', hash(raw))
        super().__setattr__('level', level)
        super().__setattr__('start', start)
        super().__setattr__('end',   end)

    def __getstate__(self):
        return dict( _raw=self._raw, level=self.level, 
                     start=self.start, end=self.end )

    def __setstate__(self, state):
        super().__setattr__('_raw',  state['_raw'])
        super().__setattr__('_hash', hash(state['_raw']))
        super().__setattr__('level', state['level'])
        super().__setattr__('start', state['start'])
        super().__setattr__('end',   state['end'])

    def __setattr__(self, *ignored):
        raise AttributeError('Basespans are immutable')

    def __delattr__(self, *ignored):
        raise AttributeError('Basespans are immutable')

    def flatten(self):
        """Returns this basespan flattened to a tuple of raw text positions.
           For ElementaryBaseSpan, returns ((start, end),). 
           For EnvelopingBaseSpan at any level, returns 
           ((start1, end1), ..., (startN, endN)).
        """
        raise NotImplementedError

    def reduce(self, level):
        """Returns this basespan reduced down to a tuple of basespans on a given level.

           A higher level basespan is a tree of lower-level basespans. 
           This function returns all basespans in the requested level.
           Parameter `level` must be smaller than or equal to the 
           level of this basespan.
        """
        raise NotImplementedError
        
    def raw(self):
        return self._raw

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, self.__class__):
            return self.raw() == other.raw()
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return (self.start, self.end, self.raw()) < (other.start, other.end, other.raw())
        raise TypeError('unorderable types: {}<={}'.format(type(self), type(other)))

    def __le__(self, other):
        return self == other or self < other


class ElementaryBaseSpan(BaseSpan):
    '''An ElementaryBaseSpan is a BaseSpan which has level 0. 
       It corresponds to a raw text position: (start, end). 
    ''' 
    __slots__ = []

    def __init__(self, start: int, end: int):
        if not isinstance(start, int):
            raise TypeError('expected int, got', type(start))
        if not isinstance(end, int):
            raise TypeError('expected int, got', type(end))
        if not 0 <= start <= end:
            raise ValueError('0 <= {} <= {} not satisfied'.format(start, end))

        raw = (start, end)

        super().__init__(raw=raw, level=0, start=start, end=end)

    def flatten(self):
        return (self.start, self.end),

    def reduce(self, level):
        if level == 0:
            return self
        raise ValueError(level)

    def __len__(self):
        return self.end - self.start

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return '{}{}'.format(self.__class__.__name__, (self.start, self.end))


class EnvelopingBaseSpan(BaseSpan):
    '''An EnvelopingBaseSpan is a BaseSpan that is made up of other BaseSpans.
       Its level determines the depth of its nested structure:

       *) EnvelopingBaseSpan at level = 1 corresponds to a sequence of ElementaryBaseSpan-s:
            [(start_1, end_1), ..., (start_N, end_N)]

       *) EnvelopingBaseSpan at level = 2 corresponds to a sequence of level 1 EnvelopingBaseSpans:
            [((start_11, end_11), ... ), ... ((start_N1, end_N1), ...)]

        And so on.
    ''' 
    __slots__ = ['_spans']

    def __init__(self, spans: Iterable[BaseSpan]):
        spans = tuple(spans)

        if len(spans) == 0:
            raise ValueError('spans is empty')
        if not all(isinstance(span, BaseSpan) for span in spans):
            raise TypeError('spans must be of type BaseSpan')
        for i in range(len(spans) - 1):
            if spans[i].end > spans[i + 1].start:
                raise ValueError('enveloped components must be sorted and must not overlap: {}, {}'.format(
                        spans[i], spans[i+1]))

        base_level = spans[0].level
        if any(span.level != base_level for span in spans):
            raise ValueError('enveloped components must have the same levels: {}'.format(
                    [span.level for span in spans]))

        raw = tuple(span.raw() for span in spans)

        object.__setattr__(self, '_spans', spans)
        super().__init__(raw=raw, level=base_level+1, start=spans[0].start, end=spans[-1].end)

    def __getstate__(self):
        state = super().__getstate__()
        state['_spans'] = self._spans
        return state

    def __setstate__(self, state):
        object.__setattr__(self, '_spans', state['_spans'])
        super().__setstate__(state)

    def flatten(self):
        return tuple(sp for span in self._spans for sp in span.flatten())

    def reduce(self, level):
        if self.level == level:
            return self
        if self.level == level + 1:
            return self._spans
        if self.level > level:
            return tuple(sp for span in self._spans for sp in span.reduce(level))
        raise ValueError(level)

    def __len__(self):
        return len(self._spans)

    def __getitem__(self, item):
        return self._spans[item]

    def __iter__(self):
        return iter(self._spans)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self._spans)
