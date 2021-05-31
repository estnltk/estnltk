from estnltk import Text, Layer

from estnltk.converters import layer_to_dict
from estnltk.converters import dict_to_layer

from estnltk.layer_operations import split_by_sentences, extract_sections
from estnltk.layer_operations import split_by


def test_extract_sections():
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

    assert ['Üks'] == texts[0].test_1.text
    assert ['kaks'] == texts[1].test_1.text

    assert k is texts[0].test_1[0].attr_1
    assert m is texts[1].test_1[0].attr_1


def test_split_by_sentences():
    t = '''Esimene lause.
    
    Teine lõik. Kolmas lause.'''

    text = Text(t)
    text.analyse('all')

    texts = split_by_sentences(text=text,
                               layers_to_keep=list(text.layers),
                               trim_overlapping=True
                               )

    text_1 = texts[1]
    assert ['Teine', 'lõik', '.'] == text_1.tokens.text
    assert [] == text_1.compound_tokens.text
    assert ['Teine', 'lõik', '.'] == text_1.words.text
    assert ['Teine', 'lõik', '.'] == text_1.sentences.text
    assert ['Teine', 'lõik', '.'] == text_1.paragraphs.text
    assert ['Teine', 'lõik', '.'] == text_1.morph_analysis.text
    assert ['Teine', 'lõik', '.'] == text_1.morph_extended.text


def test_split_by_clauses__fix_empty_spans_error():
    # Tests that split_by_clauses trim_overlapping=True 
    #       does not rise "ValueError: spans is empty"
    text = Text('Mees, keda kohtasime, oli tuttav.')
    text.tag_layer(['words', 'sentences', 'morph_analysis'])
    #from pprint import pprint
    #pprint(layer_to_dict(text['clauses']))
    clauses_layer_dict = \
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
                    'base_span': ((4, 5), (6, 10), (11, 20), (20, 21))}]}
    text.add_layer( dict_to_layer(clauses_layer_dict) )
    clause_texts = split_by(text, 'clauses',
                                  layers_to_keep=list(text.layers),
                                  trim_overlapping=True)
    assert len(clause_texts) == len(text['clauses'])
    assert clause_texts[0].words.text == ['Mees', 'oli', 'tuttav', '.']
    assert clause_texts[1].words.text == [',', 'keda', 'kohtasime', ',']



