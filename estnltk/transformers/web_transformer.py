import requests

from estnltk.converters import text_to_json, json_to_text

CONNECTION_ERROR_MESSAGE = 'Webservice unreachable'
STATUS_OK = 'OK'


class WebTransformerChecker(type):
    def __call__(cls, *args, **kwargs):
        transformer = type.__call__(cls, *args, **kwargs)

        if transformer.__doc__ is None:
            raise ValueError('{!r} class must have a docstring'.format(cls.__name__))

        return transformer


class WebTransformer(metaclass=WebTransformerChecker):
    """Tags layers using webservice and returns a new Text object."""

    __slots__ = ['url', 'layer_names']

    def __init__(self, url: str = 'http://127.0.0.1:5000', layer_names=('morph_analysis', 'sentences')):
        self.url = url.rstrip('/')
        self.layer_names = (layer_names,) if isinstance(layer_names, str) else layer_names

    def __call__(self, text, ):
        text_json = text_to_json(text)
        try:
            resp = requests.post('{}/tag_layer/{}'.format(self.url, ','.join(self.layer_names)), json=text_json)
        except requests.ConnectionError as e:
            return str(e)
        if resp.status_code == 200:
            return json_to_text(resp.text)

    @property
    def about(self) -> str:
        try:
            return requests.get(self.url+'/about').text
        except requests.ConnectionError:
            return CONNECTION_ERROR_MESSAGE

    @property
    def status(self) -> str:
        try:
            return requests.get(self.url+'/status').text
        except requests.ConnectionError:
            return CONNECTION_ERROR_MESSAGE

    @property
    def is_alive(self) -> bool:
        return self.status == STATUS_OK

    def _repr_html_(self):
        import pandas
        assert self.__class__.__doc__ is not None, 'No docstring.'

        description = self.__class__.__doc__.strip().split('\n')[0]
        html_tokens = ['<h4>{}</h4>'.format(self.__class__.__name__), description]

        data = {'key': ['url', 'status', 'about'], 'value': [self.url, self.status, self.about]}
        status_table = pandas.DataFrame(data, columns=['key', 'value'])
        status_table = status_table.to_html(header=False, index=False)

        html_tokens.append(status_table)
        return '\n'.join(html_tokens)
