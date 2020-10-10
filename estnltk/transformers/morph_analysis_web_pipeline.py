import requests

from estnltk.converters import text_to_json, json_to_text
from .web_transformer import WebTransformer


class MorphAnalysisWebPipeline(WebTransformer):
    """Tags layers using webservice and returns a new Text object."""

    __slots__ = ['url', 'layer_names']

    def __init__(self, url: str, layer_names=('morph_analysis', 'sentences')):
        self.layer_names = (layer_names,) if isinstance(layer_names, str) else layer_names
        super().__init__(url)

    def __call__(self, text):
        text_json = text_to_json(text)
        try:
            resp = requests.post('{}/tag_layer/{}'.format(self.url, ','.join(self.layer_names)), json=text_json)
        except requests.ConnectionError as e:
            return str(e)
        if resp.status_code == 200:
            return json_to_text(resp.text)
