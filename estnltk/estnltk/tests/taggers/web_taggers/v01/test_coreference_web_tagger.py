import pytest

from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import CoreferenceV1WebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_coreference_web_tagger_smoke(httpserver):
    # Create test text
    text = Text('Piilupart Donald, kes kunagi ei anna järele, läks uuele ringile. '+\
                'Ta kärkis ja paukus, kuni muusika vaikis ja pasadoobel seiskus. '+\
                'Mis sa tühja lällad, küsis rahvas.')
    text.tag_layer('morph_analysis')
    # Mock response (use an old serialisation_module)
    response_layer_dict = \
        {'ambiguous': False,
         'attributes': (),
         'meta': {},
         'name': 'coreference_v1',
         'relations': [{'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (65, 67)}},
                       {'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (133, 135)}}],
         'secondary_attributes': (),
         'serialisation_module': 'relations_v0',
         'span_names': ('pronoun', 'mention')}
    httpserver.expect_request('/estnltk/tagger/coreference_v1').respond_with_json(response_layer_dict)
    # Tag coref
    tagger = CoreferenceV1WebTagger(url=httpserver.url_for('/estnltk/tagger/coreference_v1'))
    tagger.tag(text)
    # Check results
    assert tagger.output_layer in text.relation_layers
    assert tagger.output_layer not in text.layers
    assert text[tagger.output_layer][0]['mention'].text == 'Donald'
    assert text[tagger.output_layer][1]['mention'].text == 'Donald'
    assert text[tagger.output_layer][2]['mention'].text == 'Donald'
    assert text[tagger.output_layer][0]['pronoun'].text == 'kes'
    assert text[tagger.output_layer][1]['pronoun'].text == 'Ta'
    assert text[tagger.output_layer][2]['pronoun'].text == 'sa'
    # Check full layer (serialisation_module gets updated to 'relations_v1')
    expected_response_layer_dict = \
        {'ambiguous': False,
         'attributes': (),
         'meta': {},
         'name': 'coreference_v1',
         'relations': [{'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (18, 21)}},
                       {'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (65, 67)}},
                       {'annotations': [{}],
                        'named_spans': {'mention': (10, 16), 'pronoun': (133, 135)}}],
         'secondary_attributes': (),
         'display_order': ('pronoun', 'mention'), 
         'serialisation_module': 'relations_v1',
         'span_names': ('pronoun', 'mention')}
    assert layer_to_dict( text[tagger.output_layer] ) == expected_response_layer_dict