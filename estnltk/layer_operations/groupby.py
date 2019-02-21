from typing import Sequence
from collections import defaultdict
from estnltk.layer.layer import Layer


class GroupBy:
    def __init__(self, layer: Layer, by: Sequence[str], return_type: str):
        self.layer = layer
        self.by = by
        self.return_type = return_type

        groups = defaultdict(list)

        if return_type == 'annotations':
            for span in layer.spans:
                for annotation in span.annotations:
                    key = tuple(getattr(annotation, k) for k in by)
                    groups[key].append(annotation)

        elif return_type == 'spans':
            for span in layer.spans:
                keys = {tuple(getattr(annotation, a) for a in by) for annotation in span.annotations}
                for k in keys:
                    groups[k].append(span)
        else:
            raise ValueError("return_type must be 'spans' or 'annotations', got {!r}".format(return_type))

        self._groups = groups

    @property
    def groups(self):
        return self._groups

    @property
    def count(self):
        return {k: len(v) for k, v in self._groups.items()}

    def aggregate(self, func: callable, combiner: callable = None):
        if combiner is None:
            def combiner(spans):
                return spans

        return combiner({key: func(value) for key, value in self._groups.items()})

    def __iter__(self):
        yield from ((key, self._groups[key]) for key in sorted(self._groups))

    def __repr__(self):
        return '{self.__class__.__name__}(layer=<{self.layer.name}>, by={self.by}, return_type={self.return_type!r})'.format(self=self)
