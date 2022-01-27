import pytest
from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import VabamorfWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_vabamorph_web_tagger(httpserver):
    layer_dict = {
        'name': 'morph_analysis',
        'attributes': ('normalized_text', 'lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech'),
        'secondary_attributes': (),
        'parent': 'words',
        'enveloping': None,
        'ambiguous': True,
        'serialisation_module': None,
        'meta': {},
        'spans': [
            {'base_span': (0, 3), 'annotations': [{'normalized_text': 'See', 'lemma': 'see', 'root': 'see', 'root_tokens': ['see'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'P'}]},
            {'base_span': (4, 6), 'annotations': [{'normalized_text': 'on', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'], 'ending': '0', 'clitic': '', 'form': 'b', 'partofspeech': 'V'}, {'normalized_text': 'on', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'], 'ending': '0', 'clitic': '', 'form': 'vad', 'partofspeech': 'V'}]},
            {'base_span': (7, 12), 'annotations': [{'normalized_text': 'lause', 'lemma': 'lause', 'root': 'lause', 'root_tokens': ['lause'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'S'}]},
            {'base_span': (12, 13), 'annotations': [{'normalized_text': '!', 'lemma': '!', 'root': '!', 'root_tokens': ['!'], 'ending': '', 'clitic': '', 'form': '', 'partofspeech': 'Z'}]}
        ]
    }
    httpserver.expect_request('/1.6.7beta/tag/morph_analysis').respond_with_json(layer_dict)

    text = Text('See on lause.')
    text.tag_layer('sentences')

    tagger = VabamorfWebTagger(url=httpserver.url_for('/1.6.7beta/tag/morph_analysis'))

    tagger.tag(text)
    assert layer_to_dict(text.morph_analysis) == layer_dict
