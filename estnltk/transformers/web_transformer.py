import requests

from estnltk.converters import text_to_json, json_to_text


class WebTransformer:
    __slots__ = ['url']

    def __init__(self, url: str = 'http://127.0.0.1:5000/tag_layer/morph_analysis,words'):
        if not url.endswith('/'):
            url += '/'
        self.url = url

    def __call__(self, text, layer_names=('morph_analysis', 'sentences')):
        if isinstance(layer_names, str):
            layer_names = layer_names,

        text_json = text_to_json(text)
        resp = requests.post(self.url + ','.join(layer_names), json=text_json)
        return json_to_text(resp.text)
