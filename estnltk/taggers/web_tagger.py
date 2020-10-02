import requests
from typing import MutableMapping

from .tagger import Tagger
from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.converters import layers_to_json, dict_to_layer


class WebTagger(Tagger):
    __slots__ = []
    conf_param = ['url']

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        data = {
            'text': text.text,
            'meta': text.meta,
            'layers': layers_to_json(layers),
            'output_layer': self.output_layer
        }
        resp = requests.post(self.url, json=data)
        resp_json = resp.json()
        layer = dict_to_layer(resp_json, text)
        return layer

    def _repr_html_(self):
        return self._repr_html('WebTagger')
