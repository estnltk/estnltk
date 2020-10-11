import requests


class Status:
    CONNECTION_ERROR = 'Webservice unreachable'
    OK = 'OK'


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
        import pandas
        assert self.__class__.__doc__ is not None, 'No docstring.'

        html_tokens = ['<h4>{}</h4>'.format(self.__class__.__name__), self.about]

        data = {'key': ['url', 'status'], 'value': [self.url, self.status]}
        status_table = pandas.DataFrame(data, columns=['key', 'value'])
        status_table = status_table.to_html(header=False, index=False)

        html_tokens.append(status_table)
        return '\n'.join(html_tokens)
