from estnltk_core import Layer, ElementaryBaseSpan

from estnltk_core.tests import new_text

from estnltk_core.converters import dict_to_layer

from estnltk_core.layer_operations import diff_layer
from estnltk_core.layer_operations import create_ngram_fingerprint_index

from estnltk_core.common import load_text_class


def test_layer_groupby_attributes():
    text   = new_text( 5 )
    groups = text['layer_1'].groupby(['attr_1'], return_type='spans')
    assert groups.count == {('SADA',): 3, \
                            ('KAKS',): 2,
                            ('KAKSKÜMMEND',): 1,
                            ('KÜMME',): 6,
                            ('KOLM',): 1,
                            ('NELI',): 1,
                            ('TUHAT',): 1,
                            ('VIIS',): 2,
                            ('VIISSADA',): 1,
                            ('KUUS',): 2,
                            ('KUUSKÜMMEND',): 1,
                            ('SEITSE',): 1,
                            ('KOMA',): 1,
                            ('KAHEKSA',): 1,
                            ('ÜHEKSA',): 2,
                            ('ÜHEKSAKÜMMEND',): 1}
    assert groups.groups[ ('KAHEKSA',) ] == [ text['layer_1'][15] ]
    assert groups.groups[ ('KAKS',) ] == [ text['layer_1'][1], text['layer_1'][2] ]
    assert groups.groups[ ('KAKSKÜMMEND',) ] == [ text['layer_1'][2] ]


def test_layer_groupby_text():
    # Case 1
    text   = new_text( 5 )
    groups = text['layer_1'].groupby(['text'], return_type='spans')
    assert groups.count == { ('Sada',): 1,
                             ('kaheksa',): 1,
                             ('kaks',): 1,
                             ('kakskümmend',): 1,
                             ('kolm',): 1,
                             ('Neli',): 1,
                             ('koma',): 1,
                             ('kuus',): 1,
                             ('kuuskümmend',): 1,
                             ('kümme',): 3,
                             ('sada',): 1,
                             ('seitse',): 1,
                             ('tuhat',): 1,
                             ('viis',): 1,
                             ('viissada',): 1,
                             ('Üheksa',): 1,
                             ('Üheksakümmend',): 1 }
    assert groups.groups[ ('neli',) ] == []
    assert groups.groups[ ('viis',) ] == [ text['layer_1'][7] ]
    assert groups.groups[ ('sada',) ] == [ text['layer_1'][9] ]
    assert groups.groups[ ('kümme',) ] == [ text['layer_1'][3], text['layer_1'][12], text['layer_1'][18] ]

    # Case 2:
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text_1 = Text('Üks kaks kolm neli kaks.')
    layer_1 = Layer('test', attributes=['label'], text_object=text_1, ambiguous=True)
    layer_1.add_annotation( ElementaryBaseSpan(0, 3), label=1 )
    layer_1.add_annotation( ElementaryBaseSpan(4, 8), label=2 )
    layer_1.add_annotation( ElementaryBaseSpan(9, 13), label=3 )
    layer_1.add_annotation( ElementaryBaseSpan(14, 18), label=4 )
    layer_1.add_annotation( ElementaryBaseSpan(19, 23), label=2 )
    text_1.add_layer( layer_1 )
    
    text_2 = Text('Neli kolm kaks üks kaks.')
    layer_2 = Layer('test', attributes=['label'], text_object=text_2, ambiguous=False)
    layer_2.add_annotation( ElementaryBaseSpan(0, 4), label=4 )
    layer_2.add_annotation( ElementaryBaseSpan(5, 9), label=3 )
    layer_2.add_annotation( ElementaryBaseSpan(10, 14), label=2 )
    layer_2.add_annotation( ElementaryBaseSpan(15, 18), label=1 )
    layer_2.add_annotation( ElementaryBaseSpan(19, 23), label=2 )
    text_2.add_layer( layer_2 )

    counter1 = text_1['test'].groupby( ['text', 'label'], return_type='annotations' )
    expected = {('Üks', 1): 1, ('kaks', 2): 2, ('kolm', 3): 1, ('neli', 4): 1}
    assert counter1.count == expected
    counter2 = text_2['test'].groupby( ['text', 'label'], return_type='annotations' )
    merged_counts = counter2.count
    for k,v in counter1.count.items():
        if k not in merged_counts.keys():
            merged_counts[k] = v
        else:
            merged_counts[k] += v
    expected = {('üks', 1): 1, ('Üks', 1): 1, ('kaks', 2): 4, ('kolm', 3): 2, ('neli', 4): 1, ('Neli', 4): 1}
    assert merged_counts == expected


def test_layer_groupby_enveloping_layer():
    # Get a grouping of spans
    text = new_text( 5 )
    assert text['layer_4'].enveloping == text['layer_0'].name
    grouped_spanlist_texts = []
    for (env_layer_id, list_of_spans) in text['layer_0'].groupby( text['layer_4'] ):
        grouped_spanlist_texts.append( [sp.text for sp in list_of_spans] )
    assert grouped_spanlist_texts == [ \
       ['Sada', 'kakskümmend', 'kolm'],
       [' Neli', 'tuhat', 'viissada', 'kuuskümmend', 'seitse'],
       ['koma'],
       ['kaheksa'],
       ['Üheksakümmend', 'tuhat']
    ]
    # Get a grouping of spans' annotations
    grouped_annotations_1 = []
    for (env_layer_id, list_of_annotations) in text['layer_0'].groupby( text['layer_4'], return_type='annotations' ):
        grouped_annotations_1.append( [] )
        for ann in list_of_annotations:
            ann_dict = {}
            for attr in text['layer_0'].attributes:
                ann_dict[attr] = ann[attr]
            grouped_annotations_1[-1].append( ann_dict )
    assert grouped_annotations_1 == [ \
       [ {'attr': 'L0-0', 'attr_0': '100'},
         {'attr': 'L0-2', 'attr_0': '20'},
         {'attr': 'L0-4', 'attr_0': '3'} ],
       [ {'attr': 'L0-5', 'attr_0': '4'},
         {'attr': 'L0-6', 'attr_0': '1000'},
         {'attr': 'L0-8', 'attr_0': '500'},
         {'attr': 'L0-11', 'attr_0': '60'},
         {'attr': 'L0-13', 'attr_0': '7'} ],
       [ {'attr': 'L0-14', 'attr_0': ','} ],
       [ {'attr': 'L0-15', 'attr_0': '8'} ],
       [ {'attr': 'L0-17', 'attr_0': '90'},
         {'attr': 'L0-19', 'attr_0': '1000'} ]
    ]


def test_diff_layer():
    layer_1 = Layer('layer_1')
    layer_2 = Layer('layer_2')
    result = list(diff_layer(layer_1, layer_2))
    expected = []
    assert result == expected

    layer_1 = Layer('layer_1')
    layer_1.add_annotation(ElementaryBaseSpan(0, 3))
    layer_2 = Layer('layer_2')
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], None)]
    assert result == expected

    layer_1 = Layer('layer_1')
    layer_1.add_annotation((0, 3))
    layer_1.add_annotation((6, 9))
    layer_1.add_annotation((12, 15))
    layer_1.add_annotation((18, 21))
    layer_2 = Layer('layer_2')
    layer_2.add_annotation((1, 3))
    layer_2.add_annotation((6, 9))
    layer_2.add_annotation((12, 15))
    layer_2.add_annotation((18, 20))
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], None),
                (None, layer_2[0]),
                (None, layer_2[3]),
                (layer_1[3], None)]
    assert result == expected

    layer_1 = Layer('layer_1', attributes=['label'])
    layer_1.add_annotation((0, 3), label=1)
    layer_2 = Layer('layer_2', attributes=['label'])
    layer_2.add_annotation((0, 3), label=2)
    result = list(diff_layer(layer_1, layer_2))
    expected = [(layer_1[0], layer_2[0])]
    assert result == expected

    def fun(x, y):
        return True

    layer_1 = Layer('layer_1', attributes=['label'])
    layer_1.add_annotation((0, 3), label=1)
    layer_1.add_annotation((5, 7), label=1)
    layer_2 = Layer('layer_2', attributes=['label'])
    layer_2.add_annotation((0, 3), label=2)
    layer_2.add_annotation((6, 7), label=1)
    result = list(diff_layer(layer_1, layer_2, fun))
    expected = [(layer_1[1], None),
                (None, layer_2[1])]
    assert result == expected


def test_create_ngram_fingerprint_index():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Create test Text for testing
    text = Text("Koomik paarutab perimeetril.")
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 6)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (7, 15)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (16, 27)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (27, 28)}]}
    )
    text.add_layer( words_layer )
    morph_layer = dict_to_layer( \
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
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'koomik',
                                     'normalized_text': 'Koomik',
                                     'partofspeech': 'S',
                                     'root': 'koomik',
                                     'root_tokens': ['koomik']}],
                    'base_span': (0, 6)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'b',
                                     'form': 'b',
                                     'lemma': 'paarutama',
                                     'normalized_text': 'paarutab',
                                     'partofspeech': 'V',
                                     'root': 'paaruta',
                                     'root_tokens': ['paaruta']}],
                    'base_span': (7, 15)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'l',
                                     'form': 'sg ad',
                                     'lemma': 'perimeeter',
                                     'normalized_text': 'perimeetril',
                                     'partofspeech': 'S',
                                     'root': 'perimeeter',
                                     'root_tokens': ['perimeeter']}],
                    'base_span': (16, 27)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (27, 28)}]}
    )
    text.add_layer( morph_layer )
    
    # 1) Test N-gram fingerprinting (no ambiguities)
    bigram_fingerprint = create_ngram_fingerprint_index(layer=text["morph_analysis"], 
                                                        attribute='lemma', n=2)
    assert set(bigram_fingerprint) == \
        {'perimeeter', '.', 'koomik', 'paarutama', \
         'koomik-paarutama', 'perimeeter-.', 'paarutama-perimeeter'}
    
    trigram_fingerprint = create_ngram_fingerprint_index(layer=text["morph_analysis"], 
                                                         attribute='lemma', n=3)
    assert set(trigram_fingerprint) == \
        {'.', 'paarutama', 'koomik', 'perimeeter', \
         'perimeeter-.', 'paarutama-perimeeter', 'koomik-paarutama', \
         'paarutama-perimeeter-.', 'koomik-paarutama-perimeeter'}

    # 2) Test N-gram fingerprinting (ambiguities)
    # Make the first word ambiguous
    text["morph_analysis"][0].add_annotation( \
        {'clitic': '',
         'ending': '0',
         'form': 'sg n',
         'lemma': 'roomik',
         'normalized_text': 'Roomik',
         'partofspeech': 'S',
         'root': 'roomik',
         'root_tokens': ['roomik']} )
    assert len(text["morph_analysis"][0].annotations) == 2
    
    bigram_fingerprint = create_ngram_fingerprint_index(layer=text["morph_analysis"], 
                                                        attribute='lemma', n=2)
    assert set(bigram_fingerprint) == \
        {'.', 'paarutama', 'perimeeter', 'roomik', 'koomik', \
         'paarutama-perimeeter', 'roomik-paarutama', 'koomik-paarutama', 'perimeeter-.'}

    trigram_fingerprint = create_ngram_fingerprint_index(layer=text["morph_analysis"], 
                                                         attribute='lemma', n=3)
    assert set(trigram_fingerprint) == \
        {'.', 'paarutama', 'perimeeter', 'roomik', 'koomik', \
         'paarutama-perimeeter', 'roomik-paarutama', 'koomik-paarutama', 'perimeeter-.', \
         'koomik-paarutama-perimeeter', 'roomik-paarutama-perimeeter', 'paarutama-perimeeter-.'}
    
    
    