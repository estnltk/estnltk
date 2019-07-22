from typing import Sequence


class BaseSpan:
    __slots__ = ['_raw', '_hash', 'start', 'end', 'level']

    def __init__(self, raw, level: int, start: int, end: int):
        self._raw = raw
        self._hash = hash(raw)
        self.level = level
        self.start = start
        self.end = end

    def flatten(self):
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

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return '{}{}'.format(self.__class__.__name__, (self.start, self.end))


class EnvelopingBaseSpan(BaseSpan):
    __slots__ = ['_spans']

    def __init__(self, spans: Sequence[BaseSpan]):
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

        self._spans = spans
        super().__init__(raw=raw, level=base_level+1, start=spans[0].start, end=spans[-1].end)

    def flatten(self):
        return tuple(sp for span in self._spans for sp in span.flatten())

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
