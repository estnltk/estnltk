import pytest
from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import BertEmbeddingsWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_vabamorph_web_tagger(httpserver):
    layer_dict = {
        'name': 'bert_embeddings',
        'attributes': ('token', 'bert_embedding'),
        'secondary_attributes': (),
        'parent': None,
        'enveloping': None,
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {},
        'spans': [{'base_span': (0, 3), 'annotations': [{'token': 'see', 'bert_embedding': [0.31815552711486816, 0.6534809470176697]}]},
                  {'base_span': (4, 6), 'annotations': [{'token': 'on', 'bert_embedding': [0.6255878210067749, 0.5773592591285706]}]},
                  {'base_span': (7, 10), 'annotations': [{'token': 'lau', 'bert_embedding': [-0.27353978157043457, 0.1765025109052658]}]},
                  {'base_span': (10, 12), 'annotations': [{'token': '##se', 'bert_embedding': [-0.230107843875885, 0.3230907618999481]}]},
                  {'base_span': (12, 13), 'annotations': [{'token': '!', 'bert_embedding': [0.21018444001674652, 0.3435976803302765]}]}]}
    path = '/1.6.7beta/tag/bert_embeddings'
    httpserver.expect_request(path).respond_with_json(layer_dict)

    text = Text('See on lause.')
    text.tag_layer('sentences')

    tagger = BertEmbeddingsWebTagger(url=httpserver.url_for(path))

    tagger.tag(text)
    assert layer_to_dict(text.bert_embeddings) == layer_dict
