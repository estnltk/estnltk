import pytest
from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import NeuralMorphDisambWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_neural_morph_disamb_web_tagger_as_tagger(httpserver):
    # Run NeuralMorphDisambWebTagger as a tagger
    response_layer_dict = {
        'name': 'neural_morph_disamb',
        'attributes': ('morphtag', 'pos', 'form'),
        'secondary_attributes': (),
        'parent': 'words',
        'enveloping': None,
        'ambiguous': False,
        'serialisation_module': None,
        'meta': {},
        'spans': [
            {'base_span': (0, 3), 'annotations': [{'morphtag': 'POS=P|NUMBER=sg|CASE=nom', 'pos': 'P', 'form': 'sg n'}]},
            {'base_span': (4, 6), 'annotations': [{'morphtag': 'POS=V|VERB_TYPE=main|MOOD=indic|TENSE=pres|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af', 'pos': 'V', 'form': 'b'}]},
            {'base_span': (7, 12), 'annotations': [{'morphtag': 'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=nom', 'pos': 'S', 'form': 'sg n'}]},
            {'base_span': (12, 13), 'annotations': [{'morphtag': 'POS=Z|PUNCT_TYPE=Fst', 'pos': 'Z', 'form': ''}]}
        ]
    }
    path = '/estnltk/tagger/neural_morph_disamb'
    httpserver.expect_request(path).respond_with_json(response_layer_dict)

    text = Text('See on lause.')
    text.tag_layer('morph_analysis')

    tagger = NeuralMorphDisambWebTagger(url=httpserver.url_for(path), output_layer='neural_morph_disamb')

    tagger.tag(text)
    assert layer_to_dict(text.neural_morph_disamb) == response_layer_dict


def test_neural_morph_disamb_web_tagger_as_retagger(httpserver):
    # Run NeuralMorphDisambWebTagger as a retagger
    response_layer_dict = {'ambiguous': False,
         'attributes': ('morphtag', 'pos', 'form'),
         'enveloping': None,
         'meta': {},
         'name': 'neural_morph_disamb',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'form': 'sg abl',
                                     'morphtag': 'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=abl',
                                     'pos': 'S'}],
                    'base_span': (0, 7)},
                   {'annotations': [{'form': '',
                                     'morphtag': 'POS=A|DEGREE=pos',
                                     'pos': 'A'}],
                    'base_span': (8, 14)},
                   {'annotations': [{'form': 'sg n',
                                     'morphtag': 'POS=S|NOUN_TYPE=com|NUMBER=sg|CASE=nom',
                                     'pos': 'S'}],
                    'base_span': (15, 24)},
                   {'annotations': [{'form': 'b',
                                     'morphtag': 'POS=V|VERB_TYPE=aux|MOOD=indic|TENSE=pres|PERSON=ps3|NUMBER=sg|VERB_PS=ps|VERB_POLARITY=af',
                                     'pos': 'V'}],
                    'base_span': (25, 27)},
                   {'annotations': [{'form': 'nud',
                                     'morphtag': 'POS=V|VERB_TYPE=main|VERB_FORM=partic|TENSE=past|VERB_PS=ps',
                                     'pos': 'V'}],
                    'base_span': (28, 34)},
                   {'annotations': [{'form': '',
                                     'morphtag': 'POS=Z|PUNCT_TYPE=Fst',
                                     'pos': 'Z'}], 
                    'base_span': (34, 35)}]}
    path = '/estnltk/tagger/neural_morph_disamb'
    httpserver.expect_request(path).respond_with_json(response_layer_dict)

    text = Text('Kiirelt võetud pangalaen on läinud.')
    text.tag_layer('morph_analysis')

    tagger = NeuralMorphDisambWebTagger(url=httpserver.url_for(path), output_layer='morph_analysis')
    tagger.retag(text)

    expected_morph_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': 'lt',
                                     'form': 'sg abl',
                                     'lemma': 'kiir',
                                     'normalized_text': 'Kiirelt',
                                     'partofspeech': 'S',
                                     'root': 'kiir',
                                     'root_tokens': ['kiir']}],
                    'base_span': (0, 7)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'võetud',
                                     'normalized_text': 'võetud',
                                     'partofspeech': 'A',
                                     'root': 'võetud',
                                     'root_tokens': ['võetud']}],
                    'base_span': (8, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'pangalaen',
                                     'normalized_text': 'pangalaen',
                                     'partofspeech': 'S',
                                     'root': 'panga_laen',
                                     'root_tokens': ['panga', 'laen']}],
                    'base_span': (15, 24)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (25, 27)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'nud',
                                     'form': 'nud',
                                     'lemma': 'minema',
                                     'normalized_text': 'läinud',
                                     'partofspeech': 'V',
                                     'root': 'mine',
                                     'root_tokens': ['mine']}],
                    'base_span': (28, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (34, 35)}]}

    assert layer_to_dict(text['morph_analysis']) == expected_morph_layer_dict

