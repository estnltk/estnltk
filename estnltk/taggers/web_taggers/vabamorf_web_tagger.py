import requests
from typing import MutableMapping

from estnltk.text import Text
from estnltk.layer.layer import Layer
from estnltk.taggers import Tagger
from estnltk.converters import text_to_json, layers_to_json, dict_to_layer


class VabamorfWebTagger(Tagger):
    """Tags morphological analysis using EstNLTK web service."""

    conf_param = ['url']

    def __init__(self, url, output_layer='morph_analysis'):
        self.input_layers = ('words', 'sentences', 'compound_tokens')
        self.output_layer = output_layer
        self.output_attributes = ('normalized_text', 'lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form',
                                  'partofspeech')
        self.url = url

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
