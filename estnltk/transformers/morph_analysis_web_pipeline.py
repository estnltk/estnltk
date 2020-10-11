import requests

from estnltk.converters import json_to_text, layers_to_json
from .web_transformer import WebTransformer


class MorphAnalysisWebPipeline(WebTransformer):
    """Tags layers using webservice and returns a new Text object."""

    __slots__ = ['url', 'layer_names']

    def __init__(self, url: str, layer_names=('morph_analysis', 'sentences')):
        self.layer_names = (layer_names,) if isinstance(layer_names, str) else layer_names
        super().__init__(url)

    def __call__(self, text):
        data = {
            'text': text.text,
            'meta': text.meta,
            'layers': layers_to_json(text.__dict__),
            'parameters': {'layer_names': self.layer_names},
        }
        try:
            resp = requests.post(self.url, json=data)
        except requests.ConnectionError as e:
            return str(e)
        if resp.status_code == 200:
            return json_to_text(resp.text)
