from .tagger import Tagger


class WebTagger(Tagger):
    __slots__ = []

    def _repr_html_(self):
        return self._repr_html('WebTagger')
