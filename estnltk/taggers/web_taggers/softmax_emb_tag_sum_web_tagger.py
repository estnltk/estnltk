import requests
from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import WebTagger
from estnltk.converters import text_to_json, layers_to_json, dict_to_layer


class SoftmaxEmbTagSumWebTagger(WebTagger):
    """Performs neural morphological tagging using EstNLTK web service.

    See also SoftmaxEmbTagSumTagger documentation.
    """

    conf_param = ['url']

    def __init__(self, url, output_layer='neural_morph_analysis'):
        self.url = url
        self.input_layers = ('morph_analysis', 'sentences', 'words')
        self.output_attributes = ('morphtag', 'pos', 'form')
        self.output_layer = output_layer

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict):
        data = {
            'text': text_to_json(text),
            'layers': layers_to_json(layers),
            'output_layer': self.output_layer
        }
        resp = requests.post(self.url, json=data)
        resp_json = resp.json()
        layer = dict_to_layer(resp_json, text)
        return layer
