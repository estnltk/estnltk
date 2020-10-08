import requests

from estnltk.converters import text_to_json, json_to_text


class WebTransformerChecker(type):
    def __call__(cls, *args, **kwargs):
        transformer = type.__call__(cls, *args, **kwargs)

        if transformer.__doc__ is None:
            raise ValueError('{!r} class must have a docstring'.format(cls.__name__))

        return transformer


class WebTransformer(metaclass=WebTransformerChecker):
    """Tags layers using webservice and returns a new Text object."""

    __slots__ = ['url']

    def __init__(self, url: str = 'http://127.0.0.1:5000/tag_layer/morph_analysis,words',
                 layer_names=('morph_analysis', 'sentences')):
        separator = '' if url.endswith('/') else '/'

        if isinstance(layer_names, str):
            layer_names = layer_names,

        self.url = '{}{}{}'.format(url, separator, ','.join(layer_names))

    def __call__(self, text, ):
        text_json = text_to_json(text)
        resp = requests.post(self.url, json=text_json)
        return json_to_text(resp.text)
