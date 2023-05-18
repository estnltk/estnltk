import pytest

from estnltk import Text, Layer
from estnltk.converters import layer_to_dict
from estnltk.web_taggers.v01.batch_processing_web_tagger import BatchProcessingWebTagger

# =========================================================
# =========================================================
#  BatchProcessingWebTagger: guided by layer size limit
# =========================================================
# =========================================================

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
        self.batch_layer    = self.input_layers[0]
        self.batch_max_size = 3
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
        self.batch_layer    = self.input_layers[0]
        self.batch_max_size = 6
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


# =========================================================
# =========================================================
#  BatchProcessingWebTagger: guided by text size limit
# =========================================================
# =========================================================

class MyBatchProcessingWebTaggerLimitedByTextSize(BatchProcessingWebTagger):
    """Tags test_webtagger_syntax layer using EstNLTK web service."""

    def __init__(self, url, output_layer='test_webtagger_words'):
        self.url = url
        self.output_layer = output_layer
        self.output_attributes = ('id',)
        self.input_layers = []
        self.batch_max_size = 16
        self.batch_layer    = None
        self.batch_enveloping_layer = None


def test_batch_processing_web_tagger_limited_by_text_size(httpserver):
    # A) Test positive case: batch processing limited by text size only
    text = Text('  Esimene lause. Keskmine lause.  Viimane lause!')
    text.tag_layer('words')

    layer_batches = [ \
        {'ambiguous': True,
         'attributes': ('id',),
         'enveloping': None,
         'meta': {},
         'name': 'test_webtagger_words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'id': 0}], 'base_span': (2, 9)},
                   {'annotations': [{'id': 1}], 'base_span': (10, 15)},
                   {'annotations': [{'id': 2}], 'base_span': (15, 16)}]},

        {'ambiguous': True,
         'attributes': ('id',),
         'enveloping': None,
         'meta': {},
         'name': 'test_webtagger_words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'id': 3}], 'base_span': (0, 8)},
                   {'annotations': [{'id': 4}], 'base_span': (9, 14)},
                   {'annotations': [{'id': 5}], 'base_span': (14, 15)}]},

        {'ambiguous': True,
         'attributes': ('id',),
         'enveloping': None,
         'meta': {},
         'name': 'test_webtagger_words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'id': 6}], 'base_span': (0, 7)},
                   {'annotations': [{'id': 7}], 'base_span': (8, 13)},
                   {'annotations': [{'id': 8}], 'base_span': (13, 14)}]}
    ]

    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched_3').respond_with_json( layer_batches[0] )
    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched_3').respond_with_json( layer_batches[1] )
    httpserver.expect_ordered_request('/estnltk/tagger/test_syntax_batched_3').respond_with_json( layer_batches[2] )
    
    # Apply tagger
    tagger = MyBatchProcessingWebTaggerLimitedByTextSize( \
               url=httpserver.url_for('/estnltk/tagger/test_syntax_batched_3') )
    tagger.tag(text)
    
    # Check the result
    assert len(text['words']) == len(text[tagger.output_layer])
    for word_span, webtagger_word_span in zip(text['words'], text[tagger.output_layer]):
        assert word_span.base_span == webtagger_word_span.base_span
    expected_output_layer_dict = \
        {'ambiguous': True,
         'attributes': ('id',),
         'enveloping': None,
         'meta': {},
         'name': 'test_webtagger_words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'id': 0}], 'base_span': (2, 9)},
                   {'annotations': [{'id': 1}], 'base_span': (10, 15)},
                   {'annotations': [{'id': 2}], 'base_span': (15, 16)},
                   {'annotations': [{'id': 3}], 'base_span': (17, 25)},
                   {'annotations': [{'id': 4}], 'base_span': (26, 31)},
                   {'annotations': [{'id': 5}], 'base_span': (31, 32)},
                   {'annotations': [{'id': 6}], 'base_span': (34, 41)},
                   {'annotations': [{'id': 7}], 'base_span': (42, 47)},
                   {'annotations': [{'id': 8}], 'base_span': (47, 48)}]}
    #from pprint import pprint
    #pprint(layer_to_dict(text[tagger.output_layer]))
    assert expected_output_layer_dict == layer_to_dict(text[tagger.output_layer])

    # B) Test error case: batch processing limited by text size 
    #    cannot be done by tagger with input_layers

    class MyBatchProcessingWebTaggerLimitedByTextSizeErrorous(BatchProcessingWebTagger):
        """Tags test_webtagger_syntax layer using EstNLTK web service."""

        def __init__(self, url, output_layer='test_webtagger_words_2'):
            self.url = url
            self.output_layer = output_layer
            self.output_attributes = ('id',)
            self.input_layers = ['words', 'sentences']
            self.batch_max_size = 16
            self.batch_layer    = None
            self.batch_enveloping_layer = None
    
    # Apply tagger
    tagger2 = MyBatchProcessingWebTaggerLimitedByTextSizeErrorous( \
               url=httpserver.url_for('/estnltk/tagger/test_syntax_batched_3') )
    with pytest.raises(Exception):
        tagger2.tag(text)
    
    