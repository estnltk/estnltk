from estnltk_core import Layer

from estnltk_core.converters import layer_to_dict
from estnltk_core.converters import dict_to_layer

from estnltk_core.layer_operations import split_by_sentences, extract_sections
from estnltk_core.layer_operations import split_by

from estnltk_core.common import load_text_class

def test_extract_sections():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # recursive values k and m
    k = []
    k.append(k)

    m = []
    m.append(m)

    text = Text('Üks kaks kolm.')
    layer = Layer('test_1', attributes=['attr_1'], text_object=text)
    text.add_layer(layer)
    layer.add_annotation((0, 3), attr_1=k)
    layer.add_annotation((4, 8), attr_1=m)

    texts = extract_sections(text, sections=[(0, 4), (4, 14)])

    assert 'Üks ' == texts[0].text
    assert 'kaks kolm.' == texts[1].text

    assert ['Üks'] == texts[0]['test_1'].text
    assert ['kaks'] == texts[1]['test_1'].text

    assert k is texts[0]['test_1'][0].attr_1
    assert m is texts[1]['test_1'][0].attr_1


def test_split_by_sentences():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Set up
    # Create example text
    t = '''Esimene lause.
    
    Teine lõik. Kolmas lause.'''
    text = Text(t)
    # Populate text with layers
    tokens_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'tokens',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}], 'base_span': (0, 7)},
                   {'annotations': [{}], 'base_span': (8, 13)},
                   {'annotations': [{}], 'base_span': (13, 14)},
                   {'annotations': [{}], 'base_span': (24, 29)},
                   {'annotations': [{}], 'base_span': (30, 34)},
                   {'annotations': [{}], 'base_span': (34, 35)},
                   {'annotations': [{}], 'base_span': (36, 42)},
                   {'annotations': [{}], 'base_span': (43, 48)},
                   {'annotations': [{}], 'base_span': (48, 49)}]} )
    text.add_layer( tokens_layer )
    compound_tokens_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': ('type', 'normalized'),
         'enveloping': 'tokens',
         'meta': {},
         'name': 'compound_tokens',
         'parent': None,
         'serialisation_module': None,
         'spans': []} )
    text.add_layer( compound_tokens_layer )
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 7)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (8, 13)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (13, 14)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (24, 29)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (30, 34)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (34, 35)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (36, 42)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (43, 48)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (48, 49)}]} )
    text.add_layer( words_layer )
    sentences_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'words',
         'meta': {},
         'name': 'sentences',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}], 'base_span': ((0, 7), (8, 13), (13, 14))},
                   {'annotations': [{}], 'base_span': ((24, 29), (30, 34), (34, 35))},
                   {'annotations': [{}], 'base_span': ((36, 42), (43, 48), (48, 49))}]} )
    text.add_layer( sentences_layer )
    paragraphs_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'sentences',
         'meta': {},
         'name': 'paragraphs',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}],
                    'base_span': (((0, 7), (8, 13), (13, 14)),
                                  ((24, 29), (30, 34), (34, 35)),
                                  ((36, 42), (43, 48), (48, 49)))}]} )
    text.add_layer( paragraphs_layer )
    morph_analysis_layer = dict_to_layer( \
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
                                     'lemma': 'esimene',
                                     'normalized_text': 'Esimene',
                                     'partofspeech': 'O',
                                     'root': 'esimene',
                                     'root_tokens': ['esimene']}],
                    'base_span': (0, 7)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'lause',
                                     'normalized_text': 'lause',
                                     'partofspeech': 'S',
                                     'root': 'lause',
                                     'root_tokens': ['lause']}],
                    'base_span': (8, 13)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (13, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'teine',
                                     'normalized_text': 'Teine',
                                     'partofspeech': 'P',
                                     'root': 'teine',
                                     'root_tokens': ['teine']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'teine',
                                     'normalized_text': 'Teine',
                                     'partofspeech': 'O',
                                     'root': 'teine',
                                     'root_tokens': ['teine']}],
                    'base_span': (24, 29)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'lõik',
                                     'normalized_text': 'lõik',
                                     'partofspeech': 'S',
                                     'root': 'lõik',
                                     'root_tokens': ['lõik']}],
                    'base_span': (30, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (34, 35)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'kolmas',
                                     'normalized_text': 'Kolmas',
                                     'partofspeech': 'O',
                                     'root': 'kolmas',
                                     'root_tokens': ['kolmas']}],
                    'base_span': (36, 42)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'lause',
                                     'normalized_text': 'lause',
                                     'partofspeech': 'S',
                                     'root': 'lause',
                                     'root_tokens': ['lause']}],
                    'base_span': (43, 48)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (48, 49)}]} )
    text.add_layer( morph_analysis_layer )
    morph_extended_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech',
                        'punctuation_type',
                        'pronoun_type',
                        'letter_case',
                        'fin',
                        'verb_extension_suffix',
                        'subcat'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_extended',
         'parent': 'morph_analysis',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom roman',
                                     'lemma': 'esimene',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Esimene',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'esimene',
                                     'root_tokens': ['esimene'],
                                     'subcat': None,
                                     'verb_extension_suffix': []},
                                    {'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom l',
                                     'lemma': 'esimene',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Esimene',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'esimene',
                                     'root_tokens': ['esimene'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (0, 7)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'com sg nom',
                                     'lemma': 'lause',
                                     'letter_case': None,
                                     'normalized_text': 'lause',
                                     'partofspeech': 'S',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'lause',
                                     'root_tokens': ['lause'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (8, 13)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'fin': None,
                                     'form': '',
                                     'lemma': '.',
                                     'letter_case': None,
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'pronoun_type': None,
                                     'punctuation_type': 'Fst',
                                     'root': '.',
                                     'root_tokens': ['.'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (13, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'sg nom',
                                     'lemma': 'teine',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Teine',
                                     'partofspeech': 'P',
                                     'pronoun_type': ['dem'],
                                     'punctuation_type': None,
                                     'root': 'teine',
                                     'root_tokens': ['teine'],
                                     'subcat': None,
                                     'verb_extension_suffix': []},
                                    {'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom roman',
                                     'lemma': 'teine',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Teine',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'teine',
                                     'root_tokens': ['teine'],
                                     'subcat': None,
                                     'verb_extension_suffix': []},
                                    {'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom l',
                                     'lemma': 'teine',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Teine',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'teine',
                                     'root_tokens': ['teine'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (24, 29)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'com sg nom',
                                     'lemma': 'lõik',
                                     'letter_case': None,
                                     'normalized_text': 'lõik',
                                     'partofspeech': 'S',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'lõik',
                                     'root_tokens': ['lõik'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (30, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'fin': None,
                                     'form': '',
                                     'lemma': '.',
                                     'letter_case': None,
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'pronoun_type': None,
                                     'punctuation_type': 'Fst',
                                     'root': '.',
                                     'root_tokens': ['.'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (34, 35)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom roman',
                                     'lemma': 'kolmas',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Kolmas',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'kolmas',
                                     'root_tokens': ['kolmas'],
                                     'subcat': None,
                                     'verb_extension_suffix': []},
                                    {'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'ord sg nom l',
                                     'lemma': 'kolmas',
                                     'letter_case': 'cap',
                                     'normalized_text': 'Kolmas',
                                     'partofspeech': 'N',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'kolmas',
                                     'root_tokens': ['kolmas'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (36, 42)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'fin': None,
                                     'form': 'com sg nom',
                                     'lemma': 'lause',
                                     'letter_case': None,
                                     'normalized_text': 'lause',
                                     'partofspeech': 'S',
                                     'pronoun_type': None,
                                     'punctuation_type': None,
                                     'root': 'lause',
                                     'root_tokens': ['lause'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (43, 48)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'fin': None,
                                     'form': '',
                                     'lemma': '.',
                                     'letter_case': None,
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'pronoun_type': None,
                                     'punctuation_type': 'Fst',
                                     'root': '.',
                                     'root_tokens': ['.'],
                                     'subcat': None,
                                     'verb_extension_suffix': []}],
                    'base_span': (48, 49)}]} )
    text.add_layer( morph_extended_layer )

    # Test splitting functionality
    texts = split_by_sentences(text=text,
                               layers_to_keep=list(text.layers),
                               trim_overlapping=True
                               )

    text_1 = texts[1]
    assert ['Teine', 'lõik', '.'] == text_1['tokens'].text
    assert [] == text_1['compound_tokens'].text
    assert ['Teine', 'lõik', '.'] == text_1['words'].text
    assert ['Teine', 'lõik', '.'] == text_1['sentences'].text
    assert ['Teine', 'lõik', '.'] == text_1['paragraphs'].text
    assert ['Teine', 'lõik', '.'] == text_1['morph_analysis'].text
    assert ['Teine', 'lõik', '.'] == text_1['morph_extended'].text


def test_split_by_clauses__fix_empty_spans_error():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Tests that split_by_clauses trim_overlapping=True 
    #       does not rise "ValueError: spans is empty"
    # Set up
    # Create example text and populate it with layers
    text = Text('Mees, keda kohtasime, oli tuttav.')
    words_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (6, 10)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (11, 20)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (20, 21)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (22, 25)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (26, 32)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (32, 33)}]} )
    text.add_layer( words_layer )
    sentences_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'words',
         'meta': {},
         'name': 'sentences',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{}],
                    'base_span': ((0, 4),
                                  (4, 5),
                                  (6, 10),
                                  (11, 20),
                                  (20, 21),
                                  (22, 25),
                                  (26, 32),
                                  (32, 33))}]} )
    text.add_layer( sentences_layer )
    morph_analysis_layer = dict_to_layer( \
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
                                     'lemma': 'mees',
                                     'normalized_text': 'Mees',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']}],
                    'base_span': (0, 4)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (4, 5)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'da',
                                     'form': 'pl p',
                                     'lemma': 'kes',
                                     'normalized_text': 'keda',
                                     'partofspeech': 'P',
                                     'root': 'kes',
                                     'root_tokens': ['kes']},
                                    {'clitic': '',
                                     'ending': 'da',
                                     'form': 'sg p',
                                     'lemma': 'kes',
                                     'normalized_text': 'keda',
                                     'partofspeech': 'P',
                                     'root': 'kes',
                                     'root_tokens': ['kes']}],
                    'base_span': (6, 10)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'sime',
                                     'form': 'sime',
                                     'lemma': 'kohtama',
                                     'normalized_text': 'kohtasime',
                                     'partofspeech': 'V',
                                     'root': 'kohta',
                                     'root_tokens': ['kohta']}],
                    'base_span': (11, 20)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (20, 21)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'i',
                                     'form': 's',
                                     'lemma': 'olema',
                                     'normalized_text': 'oli',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (22, 25)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'tuttav',
                                     'normalized_text': 'tuttav',
                                     'partofspeech': 'A',
                                     'root': 'tuttav',
                                     'root_tokens': ['tuttav']}],
                    'base_span': (26, 32)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (32, 33)}]} )
    text.add_layer( morph_analysis_layer )
    clauses_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': ('clause_type',),
         'enveloping': 'words',
         'meta': {},
         'name': 'clauses',
         'parent': None,
         'serialisation_module': None,
         'spans': [{'annotations': [{'clause_type': 'regular'}],
                    'base_span': ((0, 4), (22, 25), (26, 32), (32, 33))},
                   {'annotations': [{'clause_type': 'embedded'}],
                    'base_span': ((4, 5), (6, 10), (11, 20), (20, 21))}]} )
    text.add_layer( clauses_layer )
    # Test that split_by_clauses trim_overlapping=True 
    #       does not rise "ValueError: spans is empty"
    clause_texts = split_by(text, 'clauses',
                                  layers_to_keep=list(text.layers),
                                  trim_overlapping=True)
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0]['words'].text == ['Mees', 'oli', 'tuttav', '.']
    assert clause_texts[1]['words'].text == [',', 'keda', 'kohtasime', ',']


def test_extract_sections_on_non_ambiguous_layer_with_parent():
    # Test that extract_sections also works on non-ambiguous layer that has a parent
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()

    text = Text('Üks kaks kolm.')
    # make parent layer
    layer = Layer('test_1', attributes=['attr_1'], ambiguous=True, 
                            text_object=text)
    text.add_layer(layer)
    layer.add_annotation((0, 3),  attr_1=1)
    layer.add_annotation((4, 8),  attr_1=2)
    layer.add_annotation((4, 8),  attr_1=2.1)
    layer.add_annotation((4, 8),  attr_1=2.2)
    layer.add_annotation((9, 13), attr_1=3)
    assert layer.ambiguous
    # make child layer
    child_layer = Layer('test_2', attributes=['attr_2'], ambiguous=False, 
                                  parent=layer.name, text_object=text)
    text.add_layer(child_layer)
    child_layer.add_annotation(layer[0].base_span,  attr_2=11)
    child_layer.add_annotation(layer[1].base_span,  attr_2=22)
    child_layer.add_annotation(layer[2].base_span,  attr_2=33)
    assert not child_layer.ambiguous
    # extract_sections
    texts = extract_sections(text, sections=[(0, 4), (4, 14)])
    # Validate extracted content
    assert len(texts) == 2
    for text_obj in texts:
        assert 'test_1' in text_obj.layers
        assert 'test_2' in text_obj.layers
    assert layer_to_dict( texts[0]['test_2'] ) == \
        {'ambiguous': False,
         'attributes': ('attr_2',),
         'enveloping': None,
         'meta': {},
         'name': 'test_2',
         'parent': 'test_1',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'attr_2': 11}], 'base_span': (0, 3)}]}
    assert layer_to_dict( texts[1]['test_2'] ) == \
        {'ambiguous': False,
         'attributes': ('attr_2',),
         'enveloping': None,
         'meta': {},
         'name': 'test_2',
         'parent': 'test_1',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'attr_2': 22}], 'base_span': (0, 4)},
                   {'annotations': [{'attr_2': 33}], 'base_span': (5, 9)}]}
