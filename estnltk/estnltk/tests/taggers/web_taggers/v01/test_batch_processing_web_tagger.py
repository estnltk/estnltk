import pytest

from estnltk import Text, Layer
from estnltk.converters import layer_to_dict
from estnltk.web_taggers.v01.batch_processing_web_tagger import BatchProcessingWebTagger

# =========================================================
#  Test batch processing guided by an enveloping layer     
# =========================================================

class MyBatchProcessingWebTaggerWithEnvelopingLayer(BatchProcessingWebTagger):
    """Tags test_webtagger_syntax layer using EstNLTK web service."""

    def __init__(self, url, output_layer='test_webtagger_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['words', 'sentences']
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 3
        self.batch_enveloping_layer = self.input_layers[1]


# Fix for DeprecationWarning: httpserver_listen_address fixture will be converted to session scope in version 1.0.0
@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 8000)


def test_batch_processing_web_tagger_with_enveloping_layer(httpserver):
    # Test text
    text = Text('  Esimene lause. Keskmine lause.  Viimane lause!')
    text.tag_layer('sentences')
    # First batch
    first_result_layer_dict = \
        {'ambiguous': False,
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
         'name': 'test_webtagger_syntax',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom',
                                               'ord': 'ord',
                                               'roman': 'roman',
                                               'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'esimene',
                                     'misc': '_',
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (2, 9)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (10, 15)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (15, 16)}]}
    # Second batch
    second_result_layer_dict = \
            {'ambiguous': False,
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
             'name': 'test_webtagger_syntax',
             'parent': 'words',
             'serialisation_module': None,
             'spans': [{'annotations': [{'deprel': 'amod',
                                         'deps': '_',
                                         'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                         'head': 2,
                                         'id': 1,
                                         'lemma': 'keskmine',
                                         'misc': '_',
                                         'upostag': 'A',
                                         'xpostag': 'A'}],
                        'base_span': (0, 8)},
                       {'annotations': [{'deprel': 'root',
                                         'deps': '_',
                                         'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                         'head': 0,
                                         'id': 2,
                                         'lemma': 'lause',
                                         'misc': '_',
                                         'upostag': 'S',
                                         'xpostag': 'S'}],
                        'base_span': (9, 14)},
                       {'annotations': [{'deprel': 'punct',
                                         'deps': '_',
                                         'feats': {},
                                         'head': 2,
                                         'id': 3,
                                         'lemma': '.',
                                         'misc': '_',
                                         'upostag': 'Z',
                                         'xpostag': 'Z'}],
                        'base_span': (14, 15)}]}
    # Third batch
    third_result_layer_dict = \
            {'ambiguous': False,
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
             'name': 'test_webtagger_syntax',
             'parent': 'words',
             'serialisation_module': None,
             'spans': [{'annotations': [{'deprel': 'amod',
                                         'deps': '_',
                                         'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                         'head': 2,
                                         'id': 1,
                                         'lemma': 'viimane',
                                         'misc': '_',
                                         'upostag': 'A',
                                         'xpostag': 'A'}],
                        'base_span': (0, 7)},
                       {'annotations': [{'deprel': 'root',
                                         'deps': '_',
                                         'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                         'head': 0,
                                         'id': 2,
                                         'lemma': 'lause',
                                         'misc': '_',
                                         'upostag': 'S',
                                         'xpostag': 'S'}],
                        'base_span': (8, 13)},
                       {'annotations': [{'deprel': 'punct',
                                         'deps': '_',
                                         'feats': {},
                                         'head': 2,
                                         'id': 3,
                                         'lemma': '!',
                                         'misc': '_',
                                         'upostag': 'Z',
                                         'xpostag': 'Z'}],
                        'base_span': (13, 14)}]}

    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched').respond_with_json( first_result_layer_dict )
    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched').respond_with_json( second_result_layer_dict )
    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched').respond_with_json( third_result_layer_dict )

    tagger = MyBatchProcessingWebTaggerWithEnvelopingLayer( url=httpserver.url_for('/estnltk/tagger/test_syntax_batched') )
    tagger.tag(text)
    
    # Check the final result
    final_result_layer_dict = \
        {'ambiguous': False,
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
         'name': 'test_webtagger_syntax',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom',
                                               'ord': 'ord',
                                               'roman': 'roman',
                                               'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'esimene',
                                     'misc': '_',
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (2, 9)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (10, 15)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (15, 16)},
                   {'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'keskmine',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (17, 25)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (26, 31)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (31, 32)},
                   {'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'viimane',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (34, 41)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (42, 47)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '!',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (47, 48)}]}
    
    assert layer_to_dict( text['test_webtagger_syntax'] ) == final_result_layer_dict


# =========================================================
#  Test batch processing without enveloping layer          
# =========================================================

class MyBatchProcessingWebTagger(BatchProcessingWebTagger):
    """Tags test_webtagger_syntax layer using EstNLTK web service."""

    def __init__(self, url, output_layer='test_webtagger_syntax'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc')
        self.input_layers = ['words', 'sentences']
        self.batch_layer            = self.input_layers[0]
        self.batch_layer_max_size   = 6
        self.batch_enveloping_layer = None


def test_batch_processing_web_tagger_without_enveloping_layer(httpserver):
    # Test text
    text = Text('  Esimene lause. Keskmine lause.  Viimane lause!')
    text.tag_layer('sentences')
    # First batch
    first_batch_layer_dict = \
        {'ambiguous': False,
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
         'name': 'test_webtagger_syntax',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom',
                                               'ord': 'ord',
                                               'roman': 'roman',
                                               'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'esimene',
                                     'misc': '_',
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (2, 9)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (10, 15)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (15, 16)},
                   {'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'keskmine',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (17, 25)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (26, 31)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (31, 32)}]}
    # Second batch
    second_batch_layer_dict = \
        {'ambiguous': False,
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
         'name': 'test_webtagger_syntax',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'viimane',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (0, 7)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (8, 13)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '!',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (13, 14)}]}

    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched_2').respond_with_json( first_batch_layer_dict  )
    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched_2').respond_with_json( second_batch_layer_dict  )

    tagger = MyBatchProcessingWebTagger( url=httpserver.url_for('/estnltk/tagger/test_syntax_batched_2') )
    tagger.tag(text)
    
    # Check the final result
    final_result_layer_dict = \
        {'ambiguous': False,
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
         'name': 'test_webtagger_syntax',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom',
                                               'ord': 'ord',
                                               'roman': 'roman',
                                               'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'esimene',
                                     'misc': '_',
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (2, 9)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (10, 15)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (15, 16)},
                   {'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'keskmine',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (17, 25)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (26, 31)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '.',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (31, 32)},
                   {'annotations': [{'deprel': 'amod',
                                     'deps': '_',
                                     'feats': {'nom': 'nom', 'pos': 'pos', 'sg': 'sg'},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'viimane',
                                     'misc': '_',
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (34, 41)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': '_',
                                     'feats': {'com': 'com', 'nom': 'nom', 'sg': 'sg'},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'lause',
                                     'misc': '_',
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (42, 47)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': '_',
                                     'feats': {},
                                     'head': 2,
                                     'id': 3,
                                     'lemma': '!',
                                     'misc': '_',
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (47, 48)}]}
    
    assert layer_to_dict( text['test_webtagger_syntax'] ) == final_result_layer_dict
