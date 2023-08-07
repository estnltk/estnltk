import pytest

from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import NerWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_neural_ner_web_tagger_smoke(httpserver):
    # Test on unfunny example
    text = Text("Mari käib Tartu Ülikoolis. See on Eesti vanim ülikool.")

    # Mock response
    response_layer_dict = \
        {
          "result": [
            [
              {"word":"Mari", "ner":"B-PER"},
              {"word":"käib", "ner":"O"},
              {"word":"Tartu", "ner":"B-ORG"},
              {"word":"Ülikoolis", "ner":"I-ORG"},
              {"word":".", "ner":"O"}
            ],
            [
              {"word":"See", "ner":"O"},
              {"word":"on", "ner":"O"},
              {"word":"Eesti", "ner":"B-LOC"},
              {"word":"vanim", "ner":"O"},
              {"word":"Ülikool", "ner":"O"},
              {"word":".", "ner":"O"}
            ]
          ]
        }
    httpserver.expect_request('/estnltk/tagger/neural_estbertner_v1').respond_with_json(response_layer_dict)
    # Tag named entities
    tagger = NerWebTagger(url=httpserver.url_for('/estnltk/tagger/neural_estbertner_v1'), 
                          ner_output_layer='webner')
    tagger.tag(text)
    
    # Check results
    output_layer = tagger.output_layers[0]
    output_tokens_layer = tagger.output_layers[1]
    
    assert output_layer in text.layers
    assert output_tokens_layer in text.layers
    
    #from pprint import pprint
    #pprint( layer_to_dict( text[output_layer] ) )
    #pprint( layer_to_dict( text[output_tokens_layer] ) )
    
    expected_ner_layer_dict = \
        {'ambiguous': False,
         'attributes': ('nertag',),
         'enveloping': 'nertokens',
         'meta': {},
         'name': 'webner',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'nertag': 'PER'}], 'base_span': ((0, 4),)},
                   {'annotations': [{'nertag': 'ORG'}], 'base_span': ((10, 15), (16, 25))},
                   {'annotations': [{'nertag': 'LOC'}], 'base_span': ((34, 39),)}]}
    assert layer_to_dict( text[output_layer] ) == expected_ner_layer_dict
    
    expected_ner_tokens_layer_dict = \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'nertokens',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{}], 'base_span': (0, 4)},
                   {'annotations': [{}], 'base_span': (5, 9)},
                   {'annotations': [{}], 'base_span': (10, 15)},
                   {'annotations': [{}], 'base_span': (16, 25)},
                   {'annotations': [{}], 'base_span': (25, 26)},
                   {'annotations': [{}], 'base_span': (27, 30)},
                   {'annotations': [{}], 'base_span': (31, 33)},
                   {'annotations': [{}], 'base_span': (34, 39)},
                   {'annotations': [{}], 'base_span': (40, 45)},
                   {'annotations': [{}], 'base_span': (54, 61)},
                   {'annotations': [{}], 'base_span': (61, 62)}]}
    assert layer_to_dict( text[output_tokens_layer] ) == expected_ner_tokens_layer_dict