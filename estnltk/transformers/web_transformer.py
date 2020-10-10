import requests


CONNECTION_ERROR_MESSAGE = 'Webservice unreachable'
STATUS_OK = 'OK'


class WebTransformerChecker(type):
    def __call__(cls, *args, **kwargs):
        transformer = type.__call__(cls, *args, **kwargs)

        if transformer.__doc__ is None:
            raise ValueError('{!r} class must have a docstring'.format(cls.__name__))

        return transformer


class WebTransformer(metaclass=WebTransformerChecker):

    __slots__ = ['url']

    def __init__(self, url: str):
        self.url = url.rstrip('/')

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
