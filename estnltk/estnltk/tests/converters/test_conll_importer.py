from collections import OrderedDict
import pytest
import tempfile
import os, os.path
from importlib.util import find_spec

from estnltk.common import abs_path
from estnltk.converters import text_to_dict

def check_if_conllu_is_available():
    # Check if conllu is available
    return find_spec("conllu") is not None


text_dict = {
    'text': 'Iga üheksas kroon tuli salapärastelt isikutelt . '
            'See oli rohkem kui 10 protsenti kogu Hansapanka paigutatud rahast .',
    'meta': {},
    'layers': [{'name': 'syntax',
                'attributes': ('id',
                               'lemma',
                               'upostag',
                               'xpostag',
                               'feats',
                               'head',
                               'deprel',
                               'deps',
                               'misc',
                               'parent_span',
                               'children'),
                'secondary_attributes': ('parent_span',
                                         'children'),
                'parent': None,
                'enveloping': None,
                'ambiguous': False,
                'serialisation_module': 'syntax_v0',
                'meta': {},
                'spans': [{'base_span': (0, 3),
                           'annotations': [{'id': 1,
                                            'lemma': 'iga',
                                            'upostag': 'P',
                                            'xpostag': 'P',
                                            'feats': OrderedDict([('det', ''), ('sg', ''), ('nom', '')]),
                                            'head': 2,
                                            'deprel': '@NN>',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (4, 11),
                           'annotations': [{'id': 2,
                                            'lemma': 'üheksas',
                                            'upostag': 'N',
                                            'xpostag': 'A',
                                            'feats': OrderedDict([('ord', ''), ('sg', ''), ('nom', ''), ('l', '')]),
                                            'head': 3,
                                            'deprel': '@AN>',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (12, 17),
                           'annotations': [{'id': 3,
                                            'lemma': 'kroon',
                                            'upostag': 'S',
                                            'xpostag': 'S',
                                            'feats': OrderedDict([('sg', ''), ('nom', '')]),
                                            'head': 4,
                                            'deprel': '@SUBJ',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (18, 22),
                           'annotations': [{'id': 4,
                                            'lemma': 'tule',
                                            'upostag': 'V',
                                            'xpostag': 'V',
                                            'feats': OrderedDict([('indic', ''),
                                                                  ('impf', ''),
                                                                  ('ps3', ''),
                                                                  ('sg', '')]),
                                            'head': 0,
                                            'deprel': 'ROOT',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (23, 36),
                           'annotations': [{'id': 5,
                                            'lemma': 'sala_pärane',
                                            'upostag': 'A',
                                            'xpostag': 'A',
                                            'feats': OrderedDict([('pl', ''), ('abl', '')]),
                                            'head': 6,
                                            'deprel': '@AN>',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (37, 46),
                           'annotations': [{'id': 6,
                                            'lemma': 'isik',
                                            'upostag': 'S',
                                            'xpostag': 'S',
                                            'feats': OrderedDict([('pl', ''), ('abl', '')]),
                                            'head': 4,
                                            'deprel': '@ADVL',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (47, 48),
                           'annotations': [{'id': 7,
                                            'lemma': '.',
                                            'upostag': 'Z',
                                            'xpostag': 'Z',
                                            'feats': OrderedDict([('Fst', '')]),
                                            'head': 6,
                                            'deprel': '@Punc',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (49, 52),
                           'annotations': [{'id': 1,
                                            'lemma': 'see',
                                            'upostag': 'P',
                                            'xpostag': 'P',
                                            'feats': OrderedDict([('dem', ''), ('sg', ''), ('nom', '')]),
                                            'head': 2,
                                            'deprel': '@SUBJ',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (53, 56),
                           'annotations': [{'id': 2,
                                            'lemma': 'ole',
                                            'upostag': 'V',
                                            'xpostag': 'V',
                                            'feats': OrderedDict([('indic', ''),
                                                                  ('impf', ''),
                                                                  ('ps3', ''),
                                                                  ('sg', '')]),
                                            'head': 0,
                                            'deprel': 'ROOT',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (57, 63),
                           'annotations': [{'id': 3,
                                            'lemma': 'rohkem',
                                            'upostag': 'D',
                                            'xpostag': 'D',
                                            'feats': None,
                                            'head': 2,
                                            'deprel': '@OBJ',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (64, 67),
                           'annotations': [{'id': 4,
                                            'lemma': 'kui',
                                            'upostag': 'J',
                                            'xpostag': 'Jc',
                                            'feats': None,
                                            'head': 5,
                                            'deprel': '@J',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (68, 70),
                           'annotations': [{'id': 5,
                                            'lemma': '10',
                                            'upostag': 'N',
                                            'xpostag': 'N',
                                            'feats': OrderedDict([('card', ''), ('sg', ''), ('nom', '')]),
                                            'head': 3,
                                            'deprel': '@ADVL',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (71, 80),
                           'annotations': [{'id': 6,
                                            'lemma': 'protsent',
                                            'upostag': 'S',
                                            'xpostag': 'S',
                                            'feats': OrderedDict([('sg', ''), ('part', '')]),
                                            'head': 5,
                                            'deprel': '@<Q',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (81, 85),
                           'annotations': [{'id': 7,
                                            'lemma': 'kogu',
                                            'upostag': 'A',
                                            'xpostag': 'A',
                                            'feats': None,
                                            'head': 10,
                                            'deprel': '@AN>',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (86, 96),
                           'annotations': [{'id': 8,
                                            'lemma': 'Hansa_pank',
                                            'upostag': 'S',
                                            'xpostag': 'H',
                                            'feats': OrderedDict([('sg', ''), ('adit', '')]),
                                            'head': 9,
                                            'deprel': '@ADVL',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (97, 107),
                           'annotations': [{'id': 9,
                                            'lemma': 'paiguta=tud',
                                            'upostag': 'A',
                                            'xpostag': 'A',
                                            'feats': OrderedDict([('partic', '')]),
                                            'head': 10,
                                            'deprel': '@AN>',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (108, 114),
                           'annotations': [{'id': 10,
                                            'lemma': 'raha',
                                            'upostag': 'S',
                                            'xpostag': 'S',
                                            'feats': OrderedDict([('sg', ''), ('el', '')]),
                                            'head': 5,
                                            'deprel': '@ADVL',
                                            'deps': None,
                                            'misc': None}]},
                          {'base_span': (115, 116),
                           'annotations': [{'id': 11,
                                            'lemma': '.',
                                            'upostag': 'Z',
                                            'xpostag': 'Z',
                                            'feats': OrderedDict([('Fst', '')]),
                                            'head': 10,
                                            'deprel': '@Punc',
                                            'deps': None,
                                            'misc': None}]}]},
               {'name': 'words',
                'attributes': (),
                'secondary_attributes': (),
                'parent': None,
                'enveloping': None,
                'ambiguous': True,
                'serialisation_module': None,
                'meta': {},
                'spans': [{'base_span': (0, 3), 'annotations': [{}]},
                          {'base_span': (4, 11), 'annotations': [{}]},
                          {'base_span': (12, 17), 'annotations': [{}]},
                          {'base_span': (18, 22), 'annotations': [{}]},
                          {'base_span': (23, 36), 'annotations': [{}]},
                          {'base_span': (37, 46), 'annotations': [{}]},
                          {'base_span': (47, 48), 'annotations': [{}]},
                          {'base_span': (49, 52), 'annotations': [{}]},
                          {'base_span': (53, 56), 'annotations': [{}]},
                          {'base_span': (57, 63), 'annotations': [{}]},
                          {'base_span': (64, 67), 'annotations': [{}]},
                          {'base_span': (68, 70), 'annotations': [{}]},
                          {'base_span': (71, 80), 'annotations': [{}]},
                          {'base_span': (81, 85), 'annotations': [{}]},
                          {'base_span': (86, 96), 'annotations': [{}]},
                          {'base_span': (97, 107), 'annotations': [{}]},
                          {'base_span': (108, 114), 'annotations': [{}]},
                          {'base_span': (115, 116), 'annotations': [{}]}]},
               {'name': 'sentences',
                'attributes': (),
                'secondary_attributes': (),
                'parent': None,
                'enveloping': 'words',
                'ambiguous': False,
                'serialisation_module': None,
                'meta': {},
                'spans': [{'base_span': ((0, 3),
                                         (4, 11),
                                         (12, 17),
                                         (18, 22),
                                         (23, 36),
                                         (37, 46),
                                         (47, 48)),
                           'annotations': [{}]},
                          {'base_span': ((49, 52),
                                         (53, 56),
                                         (57, 63),
                                         (64, 67),
                                         (68, 70),
                                         (71, 80),
                                         (81, 85),
                                         (86, 96),
                                         (97, 107),
                                         (108, 114),
                                         (115, 116)),
                           'annotations': [{}]}]}],
    'relation_layers': []
}

@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_conll_importers():
    from estnltk.converters.conll.conll_importer import conll_to_text
    from estnltk.converters.conll.conll_importer import add_layer_from_conll
    
    file = abs_path('tests/converters/test_conll.conll')
    text = conll_to_text(file, syntax_layer='syntax')

    assert text_to_dict(text) == text_dict

    text.pop_layer('syntax')
    assert 'syntax' not in text.layers

    add_layer_from_conll(file, text, 'syntax')

    assert text_to_dict(text) == text_dict


input_conll_syntax_with_empty_nodes_str = \
'''
# sent_id = aja_luup200009_511
# text = Sonja isa oli Shveitsi tulnud juba 12 ja vennad 20 aastat tagasi.
1	Sonja	Sonja	S	S	prop=prop|sg=sg|nom=nom	2	nmod	_	_
2	isa	isa	S	S	com=com|sg=sg|nom=nom	5	nsubj	_	_
3	oli	olema	V	V	aux=aux|indic=indic|impf=impf|ps3=ps3|sg=sg|ps=ps|af=af	5	aux	_	_
4	Shveitsi	Shveits	S	S	prop=prop|sg=sg|gen=gen	5	obl	_	_
5	tulnud	tulema	V	V	pos=pos	0	root	_	_
6	juba	juba	D	D	_	7	advmod	_	_
7	12	12	N	N	card=card|<?>=<?>|digit=digit	5	obl	_	_
8	ja	ja	J	J	sub=sub|crd=crd	9	cc	_	_
9	vennad	vend	S	S	com=com|pl=pl|nom=nom	5	conj	_	_
9.1	tulnud	tulema	V	V	aux=aux|partic=partic|past=past|ps=ps	_	_	_	_
10	20	20	N	N	card=card|<?>=<?>|digit=digit	11	nummod	_	_
11	aastat	aasta	S	S	com=com|sg=sg|part=part	9	orphan	_	_
12	tagasi	tagasi	K	K	post=post	11	case	_	_
13	.	.	Z	Z	_	5	punct	_	_

# sent_id = aja_luup200009_973
# text = Surnu pistis jooksu ja koer järele.
1	Surnu	surnu	S	S	com=com|sg=sg|nom=nom	2	nsubj	_	_
2	pistis	pistma	V	V	main=main|indic=indic|impf=impf|ps3=ps3|sg=sg|ps=ps|af=af	0	root	_	_
3	jooksu	jooks	S	S	com=com|sg=sg|adit=adit	2	obl	_	_
4	ja	ja	J	J	sub=sub|crd=crd	5	cc	_	_
5	koer	koer	S	S	com=com|sg=sg|nom=nom	2	conj	_	_
5.1	pistis	pistma	V	V	aux=aux|indic=indic|impf=impf|ps3=ps3|sg=sg|ps=ps|af=af	_	_	_	_
6	järele	järele	D	D	_	5	orphan	_	_
7	.	.	Z	Z	_	2	punct	_	_

'''

@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_conll_importer_remove_empty_nodes():
    # Tests remove_empty_nodes functionality of the importer
    from estnltk.converters.conll.conll_importer import conll_to_text
    from estnltk.converters.conll.conll_importer import conll_to_texts_list
    
    # Write example conll text into tempfile
    fp = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.conll', delete=False)
    fp.write( input_conll_syntax_with_empty_nodes_str )
    fp.close()
    
    text_with_0_nodes = None
    text_without_0_nodes = None
    texts_without_0_nodes = None
    try:
        text_with_0_nodes = conll_to_text(fp.name, remove_empty_nodes=False)
        text_without_0_nodes = conll_to_text(fp.name, remove_empty_nodes=True)
        texts_without_0_nodes = conll_to_texts_list(fp.name, remove_empty_nodes=True)
    finally:
        # clean up: remove temporary file
        os.remove(fp.name)
    assert not os.path.exists(fp.name)

    # 1) Check annotations loaded (via conll_to_text) from .conll without removing null nodes
    text = text_with_0_nodes
    # Chk that text contains null nodes
    assert text.text == 'Sonja isa oli Shveitsi tulnud juba 12 ja vennad tulnud 20 aastat tagasi . '+\
                        'Surnu pistis jooksu ja koer pistis järele .'
    # Assert layers contains null nodes
    words = [sp.text for sp in text['words']]
    syntax_words = [sp.text for sp in text['conll_syntax']]
    assert words == syntax_words
    assert syntax_words == ['Sonja', 'isa', 'oli', 'Shveitsi', 'tulnud', 'juba', '12', 'ja', 'vennad', \
                            'tulnud', '20', 'aastat', 'tagasi', '.', 'Surnu', 'pistis', 'jooksu', 'ja', \
                            'koer', 'pistis', 'järele', '.']
    # Assert that sentences are correctly loaded and contain null nodes
    sentence_texts = [sp.enclosing_text for sp in text['sentences']]
    assert sentence_texts == ['Sonja isa oli Shveitsi tulnud juba 12 ja vennad tulnud 20 aastat tagasi .', \
                              'Surnu pistis jooksu ja koer pistis järele .']

    # 2) Check annotations loaded (via conll_to_text) from .conll with removing null nodes
    text = text_without_0_nodes
    # Chk that text does not contain null nodes:
    assert text.text == 'Sonja isa oli Shveitsi tulnud juba 12 ja vennad 20 aastat tagasi . '+\
                        'Surnu pistis jooksu ja koer järele .'
    # Assert layers do not contain null nodes
    words = [sp.text for sp in text['words']]
    syntax_words = [sp.text for sp in text['conll_syntax']]
    assert words == syntax_words
    assert syntax_words == ['Sonja', 'isa', 'oli', 'Shveitsi', 'tulnud', 'juba', '12', 'ja', 'vennad', \
                            '20', 'aastat', 'tagasi', '.', 'Surnu', 'pistis', 'jooksu', 'ja', 'koer', 'järele', '.']
    # Assert that sentences are correctly loaded and do not contain null nodes
    sentence_texts = [sp.enclosing_text for sp in text['sentences']]
    assert sentence_texts == ['Sonja isa oli Shveitsi tulnud juba 12 ja vennad 20 aastat tagasi .', \
                              'Surnu pistis jooksu ja koer järele .']

    # 3) Check annotations loaded (via conll_to_texts_list) from .conll with removing null nodes
    text = texts_without_0_nodes[0]
    # Chk that text does not contain orphan null nodes:
    assert text.text == 'Sonja isa oli Shveitsi tulnud juba 12 ja vennad 20 aastat tagasi . '+\
                        'Surnu pistis jooksu ja koer järele .'
    # Assert layers do not contain orphan null nodes
    words = [sp.text for sp in text['words']]
    syntax_words = [sp.text for sp in text['conll_syntax']]
    assert words == syntax_words
    assert syntax_words == ['Sonja', 'isa', 'oli', 'Shveitsi', 'tulnud', 'juba', '12', 'ja', 'vennad', \
                            '20', 'aastat', 'tagasi', '.', 'Surnu', 'pistis', 'jooksu', 'ja', 'koer', 'järele', '.']
    # Assert that sentences are correctly loaded and do not contain null nodes
    sentence_texts = [sp.enclosing_text for sp in text['sentences']]
    assert sentence_texts == ['Sonja isa oli Shveitsi tulnud juba 12 ja vennad 20 aastat tagasi .', \
                              'Surnu pistis jooksu ja koer järele .']