from typing import Union

from estnltk_core.layer.base_layer import BaseLayer
from estnltk_core.layer.enveloping_span import EnvelopingSpan


class Rolling:
    """Yields span lists from a window rolling over a layer."""

    def __init__(self, layer: Union[BaseLayer, 'Layer'], window: int, min_periods: int = None, inside: str = None):
        """Initiates Rolling object yielding span sequences from a window rolling over the layer.

           Parameters
           -----------
           layer
              layer over which the rolling window will be created;
           window
              length of the window (in spans);
           min_periods
              the minimal length of the window for borderline cases; allows to shrink the window
              to meet this minimal length. If not specified, then `min_periods == window`, which
              means that the shrinking is not allowed, and contexts smaller than the `window`
              will be discarded. Note: condition `0 < min_periods <= window` must hold;
           inside
              (name of) an enveloping layer to be used for constraining the rolling window.
              The rolling window is applied on each span of the enveloping layer separately, 
              thus ensuring that the window does not exceed boundaries of enveloping spans. 
              For instance, if you create a rolling window over 'words', you can specify
              inside='sentences', ensuring that the generated word N-grams do not exceed 
              sentence boundaries;
        """
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
