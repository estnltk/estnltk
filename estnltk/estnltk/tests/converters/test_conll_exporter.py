import pytest
from collections import OrderedDict
from importlib.util import find_spec

from estnltk import Text
from estnltk.common import abs_path

from estnltk.converters import dict_to_text
from estnltk.converters import dict_to_layer

def check_if_conllu_is_available():
    # Check if conllu is available
    return find_spec("conllu") is not None


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



@pytest.mark.skipif(not check_if_conllu_is_available(),
                    reason="package conllu is required for this test")
def test_enc_layer_to_conll():
    # Test converting ENC morphosyntactic layer to CONLL format
    from estnltk.converters.conll.conll_exporter import enc_layer_to_conll
    text_obj = Text('"Kakssada kolmkümmend üks! Lõpetan! " Kalmer lülitas signalisatsiooni välja ja väntas ruloo üles.')
    enc_syntax_layer_dict = \
        {'ambiguous': False,
         'attributes': ('id',
                        'lemma',
                        'root_tokens',
                        'clitic',
                        'xpostag',
                        'feats',
                        'extended_feats',
                        'head',
                        'deprel',
                        'parent_span',
                        'children'),
         'enveloping': None,
         'meta': {},
         'name': 'stanza_syntax_v173',
         'parent': None,
         'secondary_attributes': ('parent_span', 'children'),
         'serialisation_module': 'syntax_v0',
         'spans': [{'annotations': [{'clitic': '',
                                     'deprel': 'punct',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 4,
                                     'id': 1,
                                     'lemma': '"',
                                     'root_tokens': ['"'],
                                     'xpostag': 'Z'}],
                    'base_span': (0, 1)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'compound',
                                     'extended_feats': 'card sg nom l',
                                     'feats': 'sg n',
                                     'head': 3,
                                     'id': 2,
                                     'lemma': 'kakssada',
                                     'root_tokens': ['kaks', 'sada'],
                                     'xpostag': 'N'}],
                    'base_span': (1, 9)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'compound',
                                     'extended_feats': 'card sg nom l',
                                     'feats': 'sg n',
                                     'head': 4,
                                     'id': 3,
                                     'lemma': 'kolmkümmend',
                                     'root_tokens': ['kolm', 'kümmend'],
                                     'xpostag': 'N'}],
                    'base_span': (10, 21)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'root',
                                     'extended_feats': 'sg nom',
                                     'feats': 'sg n',
                                     'head': 0,
                                     'id': 4,
                                     'lemma': 'üks',
                                     'root_tokens': ['üks'],
                                     'xpostag': 'P'}],
                    'base_span': (22, 25)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'punct',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 4,
                                     'id': 5,
                                     'lemma': '!',
                                     'root_tokens': ['!'],
                                     'xpostag': 'Z'}],
                    'base_span': (25, 26)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'root',
                                     'extended_feats': 'mod indic pres ps1 sg ps af',
                                     'feats': 'n',
                                     'head': 0,
                                     'id': 1,
                                     'lemma': 'lõpetama',
                                     'root_tokens': ['lõpeta'],
                                     'xpostag': 'V'}],
                    'base_span': (27, 34)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'punct',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 1,
                                     'id': 2,
                                     'lemma': '!',
                                     'root_tokens': ['!'],
                                     'xpostag': 'Z'}],
                    'base_span': (34, 35)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'punct',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 3,
                                     'id': 1,
                                     'lemma': '"',
                                     'root_tokens': ['"'],
                                     'xpostag': 'Z'}],
                    'base_span': (36, 37)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'nsubj',
                                     'extended_feats': 'prop sg nom',
                                     'feats': 'sg n',
                                     'head': 3,
                                     'id': 2,
                                     'lemma': 'Kalmer',
                                     'root_tokens': ['Kalmer'],
                                     'xpostag': 'H'}],
                    'base_span': (38, 44)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'root',
                                     'extended_feats': 'mod indic impf ps3 sg ps af',
                                     'feats': 's',
                                     'head': 0,
                                     'id': 3,
                                     'lemma': 'lülitama',
                                     'root_tokens': ['lülita'],
                                     'xpostag': 'V'}],
                    'base_span': (45, 52)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'obj',
                                     'extended_feats': 'com sg part',
                                     'feats': 'sg p',
                                     'head': 3,
                                     'id': 4,
                                     'lemma': 'signalisatsioon',
                                     'root_tokens': ['signalisatsioon'],
                                     'xpostag': 'S'}],
                    'base_span': (53, 69)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'compound:prt',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 3,
                                     'id': 5,
                                     'lemma': 'välja',
                                     'root_tokens': ['välja'],
                                     'xpostag': 'D'}],
                    'base_span': (70, 75)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'cc',
                                     'extended_feats': 'sub crd',
                                     'feats': '',
                                     'head': 7,
                                     'id': 6,
                                     'lemma': 'ja',
                                     'root_tokens': ['ja'],
                                     'xpostag': 'J'}],
                    'base_span': (76, 78)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'conj',
                                     'extended_feats': 'mod indic impf ps3 sg ps af',
                                     'feats': 's',
                                     'head': 3,
                                     'id': 7,
                                     'lemma': 'väntama',
                                     'root_tokens': ['vänta'],
                                     'xpostag': 'V'}],
                    'base_span': (79, 85)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'obj',
                                     'extended_feats': 'com sg gen',
                                     'feats': 'sg g',
                                     'head': 7,
                                     'id': 8,
                                     'lemma': 'ruloo',
                                     'root_tokens': ['ruloo'],
                                     'xpostag': 'S'}],
                    'base_span': (86, 91)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'compound:prt',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 7,
                                     'id': 9,
                                     'lemma': 'üles',
                                     'root_tokens': ['üles'],
                                     'xpostag': 'D'}],
                    'base_span': (92, 96)},
                   {'annotations': [{'clitic': '',
                                     'deprel': 'punct',
                                     'extended_feats': '',
                                     'feats': '',
                                     'head': 3,
                                     'id': 10,
                                     'lemma': '.',
                                     'root_tokens': ['.'],
                                     'xpostag': 'Z'}],
                    'base_span': (96, 97)}]}
    text_obj.add_layer( dict_to_layer(enc_syntax_layer_dict) )
    assert enc_syntax_layer_dict['name'] in text_obj.layers


    conll_str_1 = enc_layer_to_conll( text_obj, enc_syntax_layer_dict['name'], \
                                      extended_feats=True, separate_feats=False )
    #print( '{!r}'.format(conll_str_1) )

    expected_conll_str_1 = '''1	"	"	Z	Z		4	punct		
2	Kakssada	kakssada	N	N	card sg nom l	3	compound		
3	kolmkümmend	kolmkümmend	N	N	card sg nom l	4	compound		
4	üks	üks	P	P	sg nom	0	root		
5	!	!	Z	Z		4	punct		

1	Lõpetan	lõpetama	V	V	mod indic pres ps1 sg ps af	0	root		
2	!	!	Z	Z		1	punct		

1	"	"	Z	Z		3	punct		
2	Kalmer	Kalmer	H	H	prop sg nom	3	nsubj		
3	lülitas	lülitama	V	V	mod indic impf ps3 sg ps af	0	root		
4	signalisatsiooni	signalisatsioon	S	S	com sg part	3	obj		
5	välja	välja	D	D		3	compound:prt		
6	ja	ja	J	J	sub crd	7	cc		
7	väntas	väntama	V	V	mod indic impf ps3 sg ps af	3	conj		
8	ruloo	ruloo	S	S	com sg gen	7	obj		
9	üles	üles	D	D		7	compound:prt		
10	.	.	Z	Z		3	punct		
'''
    assert conll_str_1 == expected_conll_str_1


    conll_str_2 = enc_layer_to_conll( text_obj, enc_syntax_layer_dict['name'], \
                                      extended_feats=True, separate_feats=True )
    #print( '{!r}'.format(conll_str_2) )

    expected_conll_str_2 = '''1	"	"	Z	Z		4	punct		
2	Kakssada	kakssada	N	N	card|sg|nom|l	3	compound		
3	kolmkümmend	kolmkümmend	N	N	card|sg|nom|l	4	compound		
4	üks	üks	P	P	sg|nom	0	root		
5	!	!	Z	Z		4	punct		

1	Lõpetan	lõpetama	V	V	mod|indic|pres|ps1|sg|ps|af	0	root		
2	!	!	Z	Z		1	punct		

1	"	"	Z	Z		3	punct		
2	Kalmer	Kalmer	H	H	prop|sg|nom	3	nsubj		
3	lülitas	lülitama	V	V	mod|indic|impf|ps3|sg|ps|af	0	root		
4	signalisatsiooni	signalisatsioon	S	S	com|sg|part	3	obj		
5	välja	välja	D	D		3	compound:prt		
6	ja	ja	J	J	sub|crd	7	cc		
7	väntas	väntama	V	V	mod|indic|impf|ps3|sg|ps|af	3	conj		
8	ruloo	ruloo	S	S	com|sg|gen	7	obj		
9	üles	üles	D	D		7	compound:prt		
10	.	.	Z	Z		3	punct		
'''
    assert conll_str_2 == expected_conll_str_2

