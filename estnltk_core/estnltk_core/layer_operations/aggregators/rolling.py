from typing import Union

from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer.enveloping_span import EnvelopingSpan


class Rolling:
    """Yields span lists from a window rolling over a layer."""

    def __init__(self, layer: Union[BaseLayer, 'Layer'], window: int, min_periods: int = None, inside: str = None):
        self.layer = layer

        if not(isinstance(window, int)):
            raise TypeError('window must be int')
        elif not (window > 0):
            raise ValueError('window > 0 must hold')
        self.window = window

        if min_periods is None:
            min_periods = window
        elif not isinstance(min_periods, int):
            raise TypeError('min_periods must be int or None')
        elif not(0 < min_periods <= window):
            raise ValueError('0 < min_periods <= window must hold')
        self.min_periods = min_periods

        self.inside = inside

    def __iter__(self):
        window = self.window
        min_periods = self.min_periods

        if self.inside is None:
            len_s = len(self.layer)

            if min_periods <= len_s:
                for start in range(min_periods-window, len_s-min_periods+1):
                    end = min(start + window, len_s)
                    start = max(0, start)

                    yield self.layer[start:end]
        else:
            if self.inside in self.layer.text_object.layers:
                enveloping_layer = self.layer.text_object[self.inside]
                for span in enveloping_layer:
                    spans = getattr(span, self.layer.name)
                    len_s = len(spans)
                    if min_periods <= len_s:
                        for start in range(min_periods-window, len_s-min_periods+1):
                            end = min(start + window, len_s)
                            start = max(0, start)

                            yield self.layer[span.base_span[start:end]]
            else:
                raise ValueError(self.inside)

    # TODO: make it work
    def spans(self, decorator: callable):
        for s in self:
            span = EnvelopingSpan(s)
            span.add_annotation(**decorator(s))
            yield span

    def __repr__(self):
        return ('{self.__class__.__name__}(layer=<{self.layer.name}>, window={self.window}, '
                'min_periods={self.min_periods}, inside={self.inside!r})').format(self=self)
