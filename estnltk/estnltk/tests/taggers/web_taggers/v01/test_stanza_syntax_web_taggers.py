import pytest

from estnltk import Text
from estnltk.converters import layer_to_dict
from estnltk.web_taggers import StanzaSyntaxWebTagger
from estnltk.web_taggers import StanzaSyntaxEnsembleWebTagger

# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_stanza_syntax_web_tagger(httpserver):
    response_layer_dict = {'ambiguous': False,
                 'attributes': ('id',
                                'lemma',
                                'upostag',
                                'xpostag',
                                'feats',
                                'head',
                                'deprel',
                                'deps',
                                'misc'),
                 'secondary_attributes': (),
                 'enveloping': None,
                 'meta': {},
                 'name': 'stanza_syntax',
                 'parent': 'morph_extended',
                 'serialisation_module': None,
                 'spans': [{'annotations': [{'deprel': 'nsubj:cop',
                                             'deps': '_',
                                             'feats': {'nom': 'nom', 'sg': 'sg'},
                                             'head': 3,
                                             'id': 1,
                                             'lemma': 'see',
                                             'misc': '_',
                                             'upostag': 'P',
                                             'xpostag': 'P'}],
                            'base_span': (0, 3)},
                           {'annotations': [{'deprel': 'cop',
                                             'deps': '_',
                                             'feats': {'af': 'af',
                                                       'indic': 'indic',
                                                       'main': 'main',
                                                       'pres': 'pres',
                                                       'ps': 'ps',
                                                       'ps3': 'ps3',
                                                       'sg': 'sg'},
                                             'head': 3,
                                             'id': 2,
                                             'lemma': 'olema',
                                             'misc': '_',
                                             'upostag': 'V',
                                             'xpostag': 'V'}],
                            'base_span': (4, 6)},
                           {'annotations': [{'deprel': 'root',
                                             'deps': '_',
                                             'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                             'head': 0,
                                             'id': 3,
                                             'lemma': 'lause',
                                             'misc': '_',
                                             'upostag': 'S',
                                             'xpostag': 'S'}],
                            'base_span': (7, 12)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': '_',
                                             'feats': {},
                                             'head': 3,
                                             'id': 4,
                                             'lemma': '.',
                                             'misc': '_',
                                             'upostag': 'Z',
                                             'xpostag': 'Z'}],
                            'base_span': (12, 13)}]}
    httpserver.expect_request('/estnltk/tagger/stanza_syntax').respond_with_json(response_layer_dict)

    text = Text('See on lause.')
    text.tag_layer('morph_extended')

    tagger = StanzaSyntaxWebTagger(url=httpserver.url_for('/estnltk/tagger/stanza_syntax'))
    tagger.tag(text)
    assert layer_to_dict(text.stanza_syntax) == response_layer_dict


def test_stanza_syntax_ensemble_web_tagger(httpserver):
    response_layer_dict = {'ambiguous': False,
                         'attributes': ('id',
                                        'lemma',
                                        'upostag',
                                        'xpostag',
                                        'feats',
                                        'head',
                                        'deprel',
                                        'deps',
                                        'misc'),
                         'secondary_attributes': (),
                         'enveloping': None,
                         'meta': {},
                         'name': 'stanza_ensemble_syntax',
                         'parent': 'morph_extended',
                         'serialisation_module': None,
                         'spans': [{'annotations': [{'deprel': 'nsubj:cop',
                                                     'deps': '_',
                                                     'feats': {'nom': 'nom', 'sg': 'sg'},
                                                     'head': 4,
                                                     'id': 1,
                                                     'lemma': 'see',
                                                     'misc': '_',
                                                     'upostag': 'P',
                                                     'xpostag': 'P'}],
                                    'base_span': (0, 3)},
                                   {'annotations': [{'deprel': 'cop',
                                                     'deps': '_',
                                                     'feats': {'af': 'af',
                                                               'indic': 'indic',
                                                               'main': 'main',
                                                               'pl': 'pl',
                                                               'pres': 'pres',
                                                               'ps': 'ps',
                                                               'ps3': 'ps3'},
                                                     'head': 4,
                                                     'id': 2,
                                                     'lemma': 'olema',
                                                     'misc': '_',
                                                     'upostag': 'V',
                                                     'xpostag': 'V'}],
                                    'base_span': (4, 6)},
                                   {'annotations': [{'deprel': 'amod',
                                                     'deps': '_',
                                                     'feats': {'nom': 'nom',
                                                               'ord': 'ord',
                                                               'roman': 'roman',
                                                               'sg': 'sg'},
                                                     'head': 4,
                                                     'id': 3,
                                                     'lemma': 'teine',
                                                     'misc': '_',
                                                     'upostag': 'N',
                                                     'xpostag': 'N'}],
                                    'base_span': (7, 12)},
                                   {'annotations': [{'deprel': 'root',
                                                     'deps': '_',
                                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                                     'head': 0,
                                                     'id': 4,
                                                     'lemma': 'lause',
                                                     'misc': '_',
                                                     'upostag': 'S',
                                                     'xpostag': 'S'}],
                                    'base_span': (13, 18)},
                                   {'annotations': [{'deprel': 'punct',
                                                     'deps': '_',
                                                     'feats': {},
                                                     'head': 4,
                                                     'id': 5,
                                                     'lemma': '.',
                                                     'misc': '_',
                                                     'upostag': 'Z',
                                                     'xpostag': 'Z'}],
                                    'base_span': (18, 19)}]}
    httpserver.expect_request('/estnltk/tagger/stanza_syntax_ensemble').respond_with_json(response_layer_dict)

    text = Text('See on teine lause.')
    text.tag_layer('morph_extended')

    tagger = StanzaSyntaxEnsembleWebTagger(url=httpserver.url_for('/estnltk/tagger/stanza_syntax_ensemble'))
    tagger.tag(text)
    assert layer_to_dict(text.stanza_ensemble_syntax) == response_layer_dict


