import pkgutil
import pytest
from collections import OrderedDict

from estnltk.common import abs_path

from estnltk.converters import dict_to_text

def check_if_conllu_is_available():
    # Check if conllu is available
    return pkgutil.find_loader("conllu") is not None


@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_layer_to_conll():
    # Test converting suitable layer to CONLL
    from estnltk.converters.conll.conll_exporter import layer_to_conll
    text_obj_dict = \
        {'layers': [{'ambiguous': True,
                     'attributes': ('normalized_form',),
                     'enveloping': None,
                     'meta': {},
                     'name': 'words',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'normalized_form': None}],
                                'base_span': (0, 6)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (7, 12)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (13, 17)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (18, 25)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (25, 26)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (27, 31)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (32, 37)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (38, 43)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (44, 51)},
                               {'annotations': [{'normalized_form': None}],
                                'base_span': (51, 52)}]},
                    {'ambiguous': False,
                     'attributes': (),
                     'enveloping': 'words',
                     'meta': {},
                     'name': 'sentences',
                     'parent': None,
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{}],
                                'base_span': ((0, 6),
                                              (7, 12),
                                              (13, 17),
                                              (18, 25),
                                              (25, 26))},
                               {'annotations': [{}],
                                'base_span': ((27, 31),
                                              (32, 37),
                                              (38, 43),
                                              (44, 51),
                                              (51, 52))}]},
                    {'ambiguous': True,
                     'attributes': ('id',
                                    'lemma',
                                    'upostag',
                                    'xpostag',
                                    'feats',
                                    'head',
                                    'deprel',
                                    'deps',
                                    'misc'),
                     'enveloping': None,
                     'meta': {},
                     'name': 'ud_morph_analysis',
                     'parent': 'words',
                     'secondary_attributes': (),
                     'serialisation_module': None,
                     'spans': [{'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Number',
                                                                        'Sing'),
                                                                       ('Case',
                                                                        'Nom')]),
                                                 'head': None,
                                                 'id': 1,
                                                 'lemma': 'rändur',
                                                 'misc': None,
                                                 'upostag': 'NOUN',
                                                 'xpostag': 'S'}],
                                'base_span': (0, 6)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Voice', 'Act'),
                                                                       ('Tense',
                                                                        'Pres'),
                                                                       ('Mood', 'Cnd'),
                                                                       ('VerbForm',
                                                                        'Fin')]),
                                                 'head': None,
                                                 'id': 2,
                                                 'lemma': 'pidama',
                                                 'misc': None,
                                                 'upostag': 'VERB',
                                                 'xpostag': 'V'},
                                                {'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Voice', 'Act'),
                                                                       ('Tense',
                                                                        'Pres'),
                                                                       ('Mood', 'Cnd'),
                                                                       ('VerbForm',
                                                                        'Fin')]),
                                                 'head': None,
                                                 'id': 2,
                                                 'lemma': 'pidama',
                                                 'misc': None,
                                                 'upostag': 'AUX',
                                                 'xpostag': 'V'}],
                                'base_span': (7, 12)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict(),
                                                 'head': None,
                                                 'id': 3,
                                                 'lemma': 'kohe',
                                                 'misc': None,
                                                 'upostag': 'ADV',
                                                 'xpostag': 'D'}],
                                'base_span': (13, 17)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Voice', 'Act'),
                                                                       ('VerbForm',
                                                                        'Sup'),
                                                                       ('Case',
                                                                        'Ill')]),
                                                 'head': None,
                                                 'id': 4,
                                                 'lemma': 'saabuma',
                                                 'misc': None,
                                                 'upostag': 'VERB',
                                                 'xpostag': 'V'}],
                                'base_span': (18, 25)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict(),
                                                 'head': None,
                                                 'id': 5,
                                                 'lemma': '.',
                                                 'misc': None,
                                                 'upostag': 'PUNCT',
                                                 'xpostag': 'Z'}],
                                'base_span': (25, 26)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict(),
                                                 'head': None,
                                                 'id': 1,
                                                 'lemma': 'siis',
                                                 'misc': None,
                                                 'upostag': 'ADV',
                                                 'xpostag': 'D'}],
                                'base_span': (27, 31)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Voice', 'Act'),
                                                                       ('Tense',
                                                                        'Pres'),
                                                                       ('Mood', 'Ind'),
                                                                       ('VerbForm',
                                                                        'Fin'),
                                                                       ('Number',
                                                                        'Plur'),
                                                                       ('Person',
                                                                        '1')]),
                                                 'head': None,
                                                 'id': 2,
                                                 'lemma': 'saama',
                                                 'misc': None,
                                                 'upostag': 'VERB',
                                                 'xpostag': 'V'},
                                                {'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Voice', 'Act'),
                                                                       ('Tense',
                                                                        'Pres'),
                                                                       ('Mood', 'Ind'),
                                                                       ('VerbForm',
                                                                        'Fin'),
                                                                       ('Number',
                                                                        'Plur'),
                                                                       ('Person',
                                                                        '1')]),
                                                 'head': None,
                                                 'id': 2,
                                                 'lemma': 'saama',
                                                 'misc': None,
                                                 'upostag': 'AUX',
                                                 'xpostag': 'V'}],
                                'base_span': (32, 37)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Number',
                                                                        'Sing'),
                                                                       ('Case',
                                                                        'Ine')]),
                                                 'head': None,
                                                 'id': 3,
                                                 'lemma': 'asi',
                                                 'misc': None,
                                                 'upostag': 'NOUN',
                                                 'xpostag': 'S'}],
                                'base_span': (38, 43)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict([('Number',
                                                                        'Sing'),
                                                                       ('Case',
                                                                        'Par')]),
                                                 'head': None,
                                                 'id': 4,
                                                 'lemma': 'selgus',
                                                 'misc': None,
                                                 'upostag': 'NOUN',
                                                 'xpostag': 'S'}],
                                'base_span': (44, 51)},
                               {'annotations': [{'deprel': None,
                                                 'deps': None,
                                                 'feats': OrderedDict(),
                                                 'head': None,
                                                 'id': 5,
                                                 'lemma': '.',
                                                 'misc': None,
                                                 'upostag': 'PUNCT',
                                                 'xpostag': 'Z'}],
                                'base_span': (51, 52)}]}],
         'meta': {},
         'text': 'Rändur peaks kohe saabuma. Siis saame asjas selgust.'}
    text = dict_to_text( text_obj_dict )
    
    # Case 0: layer without CONLL attributes cannot be converted
    with pytest.raises(ValueError):
        conll_str = layer_to_conll( text, 'words' )
    
    # Case 1: convert with ambiguities
    conll_str_1 = layer_to_conll( text, 'ud_morph_analysis', preserve_ambiguity=True )
    expected_conll_str = '''1	Rändur	rändur	NOUN	S	Number=Sing|Case=Nom	_	_	_	_
2	peaks	pidama	VERB	V	Voice=Act|Tense=Pres|Mood=Cnd|VerbForm=Fin	_	_	_	_
2	peaks	pidama	AUX	V	Voice=Act|Tense=Pres|Mood=Cnd|VerbForm=Fin	_	_	_	_
3	kohe	kohe	ADV	D	_	_	_	_	_
4	saabuma	saabuma	VERB	V	Voice=Act|VerbForm=Sup|Case=Ill	_	_	_	_
5	.	.	PUNCT	Z	_	_	_	_	_

1	Siis	siis	ADV	D	_	_	_	_	_
2	saame	saama	VERB	V	Voice=Act|Tense=Pres|Mood=Ind|VerbForm=Fin|Number=Plur|Person=1	_	_	_	_
2	saame	saama	AUX	V	Voice=Act|Tense=Pres|Mood=Ind|VerbForm=Fin|Number=Plur|Person=1	_	_	_	_
3	asjas	asi	NOUN	S	Number=Sing|Case=Ine	_	_	_	_
4	selgust	selgus	NOUN	S	Number=Sing|Case=Par	_	_	_	_
5	.	.	PUNCT	Z	_	_	_	_	_

'''
    assert conll_str_1 == expected_conll_str
    
    # Case 2: convert without ambiguities
    conll_str_2 = layer_to_conll( text, 'ud_morph_analysis', preserve_ambiguity=False )
    expected_conll_str = '''1	Rändur	rändur	NOUN	S	Number=Sing|Case=Nom	_	_	_	_
2	peaks	pidama	VERB	V	Voice=Act|Tense=Pres|Mood=Cnd|VerbForm=Fin	_	_	_	_
3	kohe	kohe	ADV	D	_	_	_	_	_
4	saabuma	saabuma	VERB	V	Voice=Act|VerbForm=Sup|Case=Ill	_	_	_	_
5	.	.	PUNCT	Z	_	_	_	_	_

1	Siis	siis	ADV	D	_	_	_	_	_
2	saame	saama	VERB	V	Voice=Act|Tense=Pres|Mood=Ind|VerbForm=Fin|Number=Plur|Person=1	_	_	_	_
3	asjas	asi	NOUN	S	Number=Sing|Case=Ine	_	_	_	_
4	selgust	selgus	NOUN	S	Number=Sing|Case=Par	_	_	_	_
5	.	.	PUNCT	Z	_	_	_	_	_

'''
    assert conll_str_2 == expected_conll_str



@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_sentence_to_conll():
    from estnltk.converters.conll.conll_importer import conll_to_text
    from estnltk.converters.conll.conll_exporter import sentence_to_conll
    
    file = abs_path('tests/converters/test_conll.conll')

    text = conll_to_text(file, 'conll')

    expected = """1	See	see	P	P	dem|sg|nom	2	@SUBJ	_	_
2	oli	ole	V	V	indic|impf|ps3|sg	0	ROOT	_	_
3	rohkem	rohkem	D	D	_	2	@OBJ	_	_
4	kui	kui	J	Jc	_	5	@J	_	_
5	10	10	N	N	card|sg|nom	3	@ADVL	_	_
6	protsenti	protsent	S	S	sg|part	5	@<Q	_	_
7	kogu	kogu	A	A	_	10	@AN>	_	_
8	Hansapanka	Hansa_pank	S	H	sg|adit	9	@ADVL	_	_
9	paigutatud	paiguta=tud	A	A	partic	10	@AN>	_	_
10	rahast	raha	S	S	sg|el	5	@ADVL	_	_
11	.	.	Z	Z	Fst	10	@Punc	_	_

"""
    assert sentence_to_conll(sentence_span=text.sentences[1], conll_layer=text.conll) == expected
