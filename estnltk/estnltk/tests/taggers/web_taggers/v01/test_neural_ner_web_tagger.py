import pytest

from estnltk import Text
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.web_taggers import NerWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def _ner_spans_as_tuples(ner_layer, nertag_attr='nertag'):
    results = []
    for ne_span in ner_layer:
        ner_tag = ne_span.annotations[0][nertag_attr]
        results.append( \
            (ne_span.start, ne_span.end, ne_span.enclosing_text, ner_tag) )
    return results


def test_neural_ner_web_tagger_smoke(httpserver):
    # Test on an unfunny example, use the default tokenization of NER WS
    text = Text("Mari käib Tartu Ülikoolis. See on Eesti vanim ülikool.")

    # Mock NER response
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
              {"word":"ülikool", "ner":"O"},
              {"word":".", "ner":"O"}
            ]
          ]
        }
    httpserver.expect_request('/estnltk/tagger/neural_estbertner_v1').respond_with_json(response_layer_dict)
    # Tag named entities (without custom words layer)
    tagger = NerWebTagger(url=httpserver.url_for('/estnltk/tagger/neural_estbertner_v1'), 
                          output_layer='webner', 
                          custom_words_layer=None)
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
                   {'annotations': [{}], 'base_span': (46, 53)},
                   {'annotations': [{}], 'base_span': (53, 54)}]}
    assert layer_to_dict( text[output_tokens_layer] ) == expected_ner_tokens_layer_dict



def test_neural_ner_web_tagger_with_custom_words_layers(httpserver):
    # Test NER WS with custom words layer. 
    # Test cases where custom words tokenization diverges from the NER WS tokenization. 
    text_str = \
        "Klaipeda Neptunase alistanud TÜ/Rock. USA president George W. Bush paistis silma ka Austraalias, "+\
        "kirjutas O. Angelus. Ei teadnud, et S. oli abielus ja et tal on ligi kahekümnene poeg. Lõik "+\
        "pärineb J. Cocteau' või B. Shaw' teosest."
    text = Text( text_str )
    
    # Add custom words layer
    words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 8)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (9, 18)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (19, 28)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (29, 31)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (31, 32)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (32, 36)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (36, 37)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (38, 41)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (42, 51)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (52, 58)},
                   {'annotations': [{'normalized_form': 'W. Bush'}],
                    'base_span': (59, 66)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (67, 74)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (75, 80)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (81, 83)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (84, 95)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (95, 96)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (97, 105)},
                   {'annotations': [{'normalized_form': 'O. Angelus'}],
                    'base_span': (106, 116)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (116, 117)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (118, 120)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (121, 128)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (128, 129)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (130, 132)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (133, 134)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (134, 135)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (136, 139)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (140, 147)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (148, 150)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (151, 153)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (154, 157)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (158, 160)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (161, 165)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (166, 177)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (178, 182)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (182, 183)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (184, 188)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (189, 196)},
                   {'annotations': [{'normalized_form': 'J. Cocteau'}],
                    'base_span': (197, 207)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (207, 208)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (209, 212)},
                   {'annotations': [{'normalized_form': 'B. Shaw'}],
                    'base_span': (213, 220)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (220, 221)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (222, 229)},
                   {'annotations': [{'normalized_form': None}],
                    'base_span': (229, 230)}]}
    text.add_layer( dict_to_layer(words_layer_dict) )

    # Mock NER response
    response_layer_dict = \
        {'result': [[{'ner': 'B-LOC', 'word': 'Klaipeda'},
                     {'ner': 'B-ORG', 'word': 'Neptunase'},
                     {'ner': 'O', 'word': 'alistanud'},
                     {'ner': 'B-ORG', 'word': 'TÜ/Rock'},
                     {'ner': 'O', 'word': '.'}],
                    [{'ner': 'B-LOC', 'word': 'USA'},
                     {'ner': 'O', 'word': 'president'},
                     {'ner': 'B-PER', 'word': 'George'},
                     {'ner': 'I-PER', 'word': 'W.'},
                     {'ner': 'I-PER', 'word': 'Bush'},
                     {'ner': 'O', 'word': 'paistis'},
                     {'ner': 'O', 'word': 'silma'},
                     {'ner': 'O', 'word': 'ka'},
                     {'ner': 'B-LOC', 'word': 'Austraalias'},
                     {'ner': 'O', 'word': ','},
                     {'ner': 'O', 'word': 'kirjutas'},
                     {'ner': 'B-ORG', 'word': 'O.'},
                     {'ner': 'I-ORG', 'word': 'Angelus'},
                     {'ner': 'O', 'word': '.'}],
                    [{'ner': 'O', 'word': 'Ei'},
                     {'ner': 'O', 'word': 'teadnud'},
                     {'ner': 'O', 'word': ','},
                     {'ner': 'O', 'word': 'et'},
                     {'ner': 'B-PER', 'word': 'S.'},
                     {'ner': 'O', 'word': 'oli'},
                     {'ner': 'O', 'word': 'abielus'},
                     {'ner': 'O', 'word': 'ja'},
                     {'ner': 'O', 'word': 'et'},
                     {'ner': 'O', 'word': 'tal'},
                     {'ner': 'O', 'word': 'on'},
                     {'ner': 'O', 'word': 'ligi'},
                     {'ner': 'O', 'word': 'kahekümnene'},
                     {'ner': 'O', 'word': 'poeg'},
                     {'ner': 'O', 'word': '.'}],
                    [{'ner': 'O', 'word': 'Lõik'},
                     {'ner': 'O', 'word': 'pärineb'},
                     {'ner': 'B-PER', 'word': 'J.'},
                     {'ner': 'I-PER', 'word': "Cocteau'"},
                     {'ner': 'O', 'word': 'või'},
                     {'ner': 'B-PER', 'word': 'B.'},
                     {'ner': 'O', 'word': "Shaw'"},
                     {'ner': 'O', 'word': 'teosest'},
                     {'ner': 'O', 'word': '.'}]]}
    httpserver.expect_request('/estnltk/tagger/neural_estbertner_v1').respond_with_json(response_layer_dict)
    
    # Tag named entities (with custom words layer)
    tagger = NerWebTagger(url=httpserver.url_for('/estnltk/tagger/neural_estbertner_v1'), 
                          output_layer='webner', 
                          custom_words_layer='words')
    tagger.tag(text)
    
    output_ner_layer = tagger.output_layers[0]
    assert output_ner_layer in text.layers
    #print(_ner_spans_as_tuples( text[output_ner_layer] ))

    expected_ner_spans = \
        [(0, 8, 'Klaipeda', 'LOC'), 
         (9, 18, 'Neptunase', 'ORG'), 
         (29, 36, 'TÜ/Rock', 'ORG'), 
         (38, 41, 'USA', 'LOC'), 
         (52, 66, 'George W. Bush', 'PER'), 
         (84, 95, 'Austraalias', 'LOC'), 
         (106, 116, 'O. Angelus', 'ORG'), 
         (133, 135, 'S.', 'PER'), 
         (197, 208, "J. Cocteau'", 'PER'), 
         (213, 221, "B. Shaw'", 'PER')]
    assert _ner_spans_as_tuples( text[output_ner_layer] ) == expected_ner_spans
