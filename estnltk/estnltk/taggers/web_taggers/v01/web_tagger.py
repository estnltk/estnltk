import requests
from typing import MutableMapping

from estnltk.taggers import Tagger
from estnltk import Text
from estnltk import Layer
from estnltk.converters import layers_to_json, dict_to_layer


class WebTaggerRequestTooLargeError(Exception):
    pass


class Status:
    CONNECTION_ERROR = 'Webservice unreachable'
    OK = 'OK'


class WebTagger(Tagger):
    __slots__ = []
    conf_param = ['url']

    def post_request(self, text: Text, layers: MutableMapping[str, Layer], parameters=None):
        data = {
            'text': text.text,
            'meta': text.meta,
            'layers': layers_to_json(layers),
            'parameters': parameters,
            'output_layer': self.output_layer
        }
        resp = requests.post(self.url, json=data)
        resp.raise_for_status()
        resp_json = resp.json()
        layer = dict_to_layer(resp_json, text)
        return layer

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        layer = self.post_request(text, layers)
        return layer

    @property
    def about(self) -> str:
        try:
            return requests.get(self.url+'/about').text
        except requests.ConnectionError:
            return Status.CONNECTION_ERROR

    @property
    def status(self) -> str:
        try:
            return requests.get(self.url+'/status').text
        except requests.ConnectionError:
            return Status.CONNECTION_ERROR

    @property
    def is_alive(self) -> bool:
        return self.status == Status.OK

    def _repr_html_(self):
        return self._repr_html('WebTagger', self.about)
