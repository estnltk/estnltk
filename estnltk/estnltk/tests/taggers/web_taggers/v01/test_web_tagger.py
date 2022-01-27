import pytest
import json
from estnltk import Text, Layer
from estnltk.converters import layer_to_dict
from estnltk.web_taggers.v01.web_tagger import WebTagger


class MyTestWebTagger(WebTagger):
    """Tags my_test layer using EstNLTK web service."""

    conf_param = ['url', 'param_1', 'param_2']

    def __init__(self, url, param_1, param_2, output_layer='my_test'):
        self.input_layers = ('layer_1', 'layer_2')
        self.output_layer = output_layer
        self.output_attributes = ('attr_1', 'attr_2')
        self.url = url
        self.param_1 = param_1
        self.param_2 = param_2


# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_web_tagger(httpserver):
    layer_dict = {
        'name': 'my_test',
        'attributes': ('attr_1', 'attr_2'),
        'secondary_attributes': (),
        'parent': None,
        'enveloping': None,
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {'meta_1': 'meta 1', 'meta_2': 'meta 2'},
        'spans': [
            {'base_span': (0, 3), 'annotations': [{'attr_1': '1', 'attr_2': '2'}, {'attr_1': '3', 'attr_2': '4'}]},
            {'base_span': (4, 6), 'annotations': [{'attr_1': '5', 'attr_2': '6'}]},
        ]
    }

    def match_data(request):
        global request_data
        request_data = request.data
        return True

    request_handler = httpserver.expect_request('/1.6.7beta/tag/my_test')
    request_handler.matcher.match_data = match_data
    request_handler.respond_with_json(layer_dict)

    text = Text('See on lause.')
    text.add_layer(Layer('layer_1'))
    text.add_layer(Layer('layer_2'))
    text.meta['text_meta'] = 'text meta'

    tagger = MyTestWebTagger(url=httpserver.url_for('/1.6.7beta/tag/my_test'),
                             param_1='parameter 1', param_2='param 2')

    tagger.tag(text)
    assert layer_to_dict(text.my_test) == layer_dict

    data = json.loads(request_data)
    data['layers'] = json.loads(data['layers'])
    assert data == {
        'text': 'See on lause.',
        'meta': {'text_meta': 'text meta'},
        'layers': {'layer_1': {'name': 'layer_1',
                               'attributes': [],
                               'secondary_attributes': [],
                               'parent': None,
                               'enveloping': None,
                               'ambiguous': False,
                               'serialisation_module': None,
                               'meta': {},
                               'spans': []},
                   'layer_2': {'name': 'layer_2',
                               'attributes': [],
                               'secondary_attributes': [],
                               'parent': None,
                               'enveloping': None,
                               'ambiguous': False,
                               'serialisation_module': None,
                               'meta': {},
                               'spans': []}},
        'parameters': None,
        'output_layer': 'my_test'
    }
