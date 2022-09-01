""" Test removing segments of the Text object that should be ignored by the syntactic analyser;
"""

from estnltk import Text
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.taggers.standard.syntax.preprocessing.syntax_ignore_tagger import SyntaxIgnoreTagger
from estnltk.taggers.standard.syntax.preprocessing.syntax_ignore_cutter import SyntaxIgnoreCutter
from estnltk.taggers.standard.syntax.preprocessing.syntax_ignore_cutter import add_syntax_layer_from_cut_text

def test_syntax_ignore_cutter_smoke():
    # Test that SyntaxIgnoreCutter works with SyntaxIgnoreTagger "off-the-shelf"
    test_text = Text('Klubi sai kuus korda Inglismaa meistriks (1976, 1977, 1979, 1980, 1982, 1983). '+\
                     'Tallinna ( 21.-22. mai ) , Haapsalu ( 2.-3. juuli ) ja Liivimaa ( 30.-31. juuli ) '+\
                     'rallidel on vähemalt see probleem lahendatud . '+\
                     'Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt '+\
                     '(Priit Pullerits «Džiibi kaitseks», PM 30.07.2010).')
    test_text.tag_layer('sentences')
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    syntax_ignore_tagger.tag(test_text)
    assert 'syntax_ignore' in test_text.layers
    assert len(test_text['syntax_ignore']) > 0
    syntax_ignore_cutter = SyntaxIgnoreCutter(add_words_layer=True)
    cut_text = syntax_ignore_cutter.cut(test_text)
    assert cut_text.text == \
        'Klubi sai kuus korda Inglismaa meistriks . Tallinna  , Haapsalu  ja Liivimaa  rallidel '+\
        'on vähemalt see probleem lahendatud . Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt .'
    #from pprint import pprint
    #pprint(layer_to_dict(cut_text['words']))
    expected_words_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_form', 'original_start', 'original_end', 'original_index'),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None,
                                     'original_end': 5,
                                     'original_index': 0,
                                     'original_start': 0}],
                    'base_span': (0, 5)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 9,
                                     'original_index': 1,
                                     'original_start': 6}],
                    'base_span': (6, 9)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 14,
                                     'original_index': 2,
                                     'original_start': 10}],
                    'base_span': (10, 14)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 20,
                                     'original_index': 3,
                                     'original_start': 15}],
                    'base_span': (15, 20)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 30,
                                     'original_index': 4,
                                     'original_start': 21}],
                    'base_span': (21, 30)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 40,
                                     'original_index': 5,
                                     'original_start': 31}],
                    'base_span': (31, 40)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 78,
                                     'original_index': 19,
                                     'original_start': 77}],
                    'base_span': (41, 42)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 87,
                                     'original_index': 20,
                                     'original_start': 79}],
                    'base_span': (43, 51)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 105,
                                     'original_index': 27,
                                     'original_start': 104}],
                    'base_span': (53, 54)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 114,
                                     'original_index': 28,
                                     'original_start': 106}],
                    'base_span': (55, 63)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 133,
                                     'original_index': 35,
                                     'original_start': 131}],
                    'base_span': (65, 67)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 142,
                                     'original_index': 36,
                                     'original_start': 134}],
                    'base_span': (68, 76)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 169,
                                     'original_index': 43,
                                     'original_start': 161}],
                    'base_span': (78, 86)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 172,
                                     'original_index': 44,
                                     'original_start': 170}],
                    'base_span': (87, 89)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 181,
                                     'original_index': 45,
                                     'original_start': 173}],
                    'base_span': (90, 98)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 185,
                                     'original_index': 46,
                                     'original_start': 182}],
                    'base_span': (99, 102)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 194,
                                     'original_index': 47,
                                     'original_start': 186}],
                    'base_span': (103, 111)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 205,
                                     'original_index': 48,
                                     'original_start': 195}],
                    'base_span': (112, 122)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 207,
                                     'original_index': 49,
                                     'original_start': 206}],
                    'base_span': (123, 124)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 219,
                                     'original_index': 50,
                                     'original_start': 208}],
                    'base_span': (125, 136)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 227,
                                     'original_index': 51,
                                     'original_start': 220}],
                    'base_span': (137, 144)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 232,
                                     'original_index': 52,
                                     'original_start': 228}],
                    'base_span': (145, 149)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 240,
                                     'original_index': 53,
                                     'original_start': 233}],
                    'base_span': (150, 157)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 245,
                                     'original_index': 54,
                                     'original_start': 241}],
                    'base_span': (158, 162)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 256,
                                     'original_index': 55,
                                     'original_start': 246}],
                    'base_span': (163, 173)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 264,
                                     'original_index': 56,
                                     'original_start': 257}],
                    'base_span': (174, 181)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 269,
                                     'original_index': 57,
                                     'original_start': 265}],
                    'base_span': (182, 186)},
                   {'annotations': [{'normalized_form': None,
                                     'original_end': 321,
                                     'original_index': 69,
                                     'original_start': 320}],
                    'base_span': (187, 188)}]}
    assert layer_to_dict(cut_text['words']) == expected_words_layer_dict


def test_syntax_ignore_cutter_on_overlapping_ignore_spans():
    # Test that SyntaxIgnoreCutter works even if syntax_ignore layer has overlapping spans
    test_text = Text('Uurimuslikuks lähtekohaks on siin Alfseni ja Effrose fundamentaalne töö '+\
                     '( 1972 , Ann . Math . 96 ) . \n'+\
                     '( X 4\n\n 1 ) = 0 ja ( X 4\n\n2 ) = 1. Kui vorm on paarisvorm ...')
    test_text.tag_layer('sentences')
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    syntax_ignore_tagger.tag(test_text)
    syntax_ignore_cutter = SyntaxIgnoreCutter(add_words_layer=True)
    cut_text = syntax_ignore_cutter.cut(test_text)
    assert cut_text.text == \
        'Uurimuslikuks lähtekohaks on siin Alfseni ja Effrose fundamentaalne töö  \n = 0 ja  Kui vorm on paarisvorm ...'


def test_add_syntax_layer_from_cut_text_smoke():
    # Test that add_syntax_layer_from_cut_text works with 
    # SyntaxIgnoreCutter and SyntaxIgnoreTagger "off-the-shelf"
    test_text = Text('Klubi sai kuus korda Inglismaa meistriks (1976, 1977, 1979, 1980, 1982, 1983). '+\
                     'Tallinna ( 21.-22. mai ) , Haapsalu ( 2.-3. juuli ) ja Liivimaa ( 30.-31. juuli ) '+\
                     'rallidel on vähemalt see probleem lahendatud . '+\
                     'Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt '+\
                     '(Priit Pullerits «Džiibi kaitseks», PM 30.07.2010).')
    test_text.tag_layer('sentences')
    syntax_ignore_tagger = SyntaxIgnoreTagger()
    syntax_ignore_tagger.tag(test_text)
    assert 'syntax_ignore' in test_text.layers
    assert len(test_text['syntax_ignore']) > 0
    syntax_ignore_cutter = SyntaxIgnoreCutter(add_words_layer=True)
    cut_text = syntax_ignore_cutter.cut(test_text)
    assert cut_text.text == \
        'Klubi sai kuus korda Inglismaa meistriks . Tallinna  , Haapsalu  ja Liivimaa  rallidel '+\
        'on vähemalt see probleem lahendatud . Temaatikaga seondub veel teinegi äsja Postimehes ilmunud jutt .'
    # Add syntactic analysis to cut_text
    maltparser_syntax_dict = \
        {'ambiguous': False,
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
         'enveloping': None,
         'meta': {},
         'name': 'maltparser_syntax',
         'parent': None,
         'secondary_attributes': ('parent_span', 'children'),
         'serialisation_module': 'syntax_v0',
         'spans': [{'annotations': [{'deprel': 'nsubj',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'Klubi',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (0, 5)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': None,
                                     'feats': {'s': ''},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'saama',
                                     'misc': None,
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (6, 9)},
                   {'annotations': [{'deprel': 'nummod',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 4,
                                     'id': 3,
                                     'lemma': 'kuus',
                                     'misc': None,
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (10, 14)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'p': '', 'sg': ''},
                                     'head': 2,
                                     'id': 4,
                                     'lemma': 'kord',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (15, 20)},
                   {'annotations': [{'deprel': 'nmod',
                                     'deps': None,
                                     'feats': {'g': '', 'sg': ''},
                                     'head': 6,
                                     'id': 5,
                                     'lemma': 'Inglismaa',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (21, 30)},
                   {'annotations': [{'deprel': 'xcomp',
                                     'deps': None,
                                     'feats': {'sg': '', 'tr': ''},
                                     'head': 2,
                                     'id': 6,
                                     'lemma': 'meister',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (31, 40)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': None,
                                     'feats': None,
                                     'head': 2,
                                     'id': 7,
                                     'lemma': '.',
                                     'misc': None,
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (41, 42)},
                   {'annotations': [{'deprel': 'nmod',
                                     'deps': None,
                                     'feats': {'g': '', 'sg': ''},
                                     'head': 6,
                                     'id': 1,
                                     'lemma': 'Tallinn',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (43, 51)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': None,
                                     'feats': None,
                                     'head': 3,
                                     'id': 2,
                                     'lemma': ',',
                                     'misc': None,
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (53, 54)},
                   {'annotations': [{'deprel': 'conj',
                                     'deps': None,
                                     'feats': {'g': '', 'sg': ''},
                                     'head': 1,
                                     'id': 3,
                                     'lemma': 'Haapsalu',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (55, 63)},
                   {'annotations': [{'deprel': 'cc',
                                     'deps': None,
                                     'feats': None,
                                     'head': 5,
                                     'id': 4,
                                     'lemma': 'ja',
                                     'misc': None,
                                     'upostag': 'J',
                                     'xpostag': 'J'}],
                    'base_span': (65, 67)},
                   {'annotations': [{'deprel': 'conj',
                                     'deps': None,
                                     'feats': {'g': '', 'sg': ''},
                                     'head': 1,
                                     'id': 5,
                                     'lemma': 'Liivimaa',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (68, 76)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'ad': '', 'pl': ''},
                                     'head': 11,
                                     'id': 6,
                                     'lemma': 'ralli',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (78, 86)},
                   {'annotations': [{'deprel': 'aux',
                                     'deps': None,
                                     'feats': {'b': ''},
                                     'head': 11,
                                     'id': 7,
                                     'lemma': 'olema',
                                     'misc': None,
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (87, 89)},
                   {'annotations': [{'deprel': 'advmod',
                                     'deps': None,
                                     'feats': None,
                                     'head': 10,
                                     'id': 8,
                                     'lemma': 'vähemalt',
                                     'misc': None,
                                     'upostag': 'D',
                                     'xpostag': 'D'}],
                    'base_span': (90, 98)},
                   {'annotations': [{'deprel': 'det',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 10,
                                     'id': 9,
                                     'lemma': 'see',
                                     'misc': None,
                                     'upostag': 'P',
                                     'xpostag': 'P'}],
                    'base_span': (99, 102)},
                   {'annotations': [{'deprel': 'obj',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 11,
                                     'id': 10,
                                     'lemma': 'probleem',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (103, 111)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': None,
                                     'feats': {'tud': ''},
                                     'head': 0,
                                     'id': 11,
                                     'lemma': 'lahendama',
                                     'misc': None,
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (112, 122)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': None,
                                     'feats': None,
                                     'head': 11,
                                     'id': 12,
                                     'lemma': '.',
                                     'misc': None,
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (123, 124)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'kom': '', 'sg': ''},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'temaatika',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (125, 136)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': None,
                                     'feats': {'b': ''},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'seonduma',
                                     'misc': None,
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (137, 144)},
                   {'annotations': [{'deprel': 'advmod',
                                     'deps': None,
                                     'feats': None,
                                     'head': 4,
                                     'id': 3,
                                     'lemma': 'veel',
                                     'misc': None,
                                     'upostag': 'D',
                                     'xpostag': 'D'}],
                    'base_span': (145, 149)},
                   {'annotations': [{'deprel': 'nsubj',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 2,
                                     'id': 4,
                                     'lemma': 'teine',
                                     'misc': None,
                                     'upostag': 'P',
                                     'xpostag': 'P'}],
                    'base_span': (150, 157)},
                   {'annotations': [{'deprel': 'advmod',
                                     'deps': None,
                                     'feats': None,
                                     'head': 8,
                                     'id': 5,
                                     'lemma': 'äsja',
                                     'misc': None,
                                     'upostag': 'D',
                                     'xpostag': 'D'}],
                    'base_span': (158, 162)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'in': '', 'sg': ''},
                                     'head': 7,
                                     'id': 6,
                                     'lemma': 'Postimees',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (163, 173)},
                   {'annotations': [{'deprel': 'acl',
                                     'deps': None,
                                     'feats': {'nud': ''},
                                     'head': 8,
                                     'id': 7,
                                     'lemma': 'ilmunud',
                                     'misc': None,
                                     'upostag': 'A',
                                     'xpostag': 'A'}],
                    'base_span': (174, 181)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 2,
                                     'id': 8,
                                     'lemma': 'jutt',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (182, 186)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': None,
                                     'feats': None,
                                     'head': 2,
                                     'id': 9,
                                     'lemma': '.',
                                     'misc': None,
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (187, 188)}]}
    cut_text.add_layer( dict_to_layer(maltparser_syntax_dict) )
    assert 'maltparser_syntax' in cut_text.layers
    # Validate
    # Adding with empty spans
    add_syntax_layer_from_cut_text( test_text, cut_text, 'maltparser_syntax', add_empty_spans=True )
    assert 'maltparser_syntax' in test_text.layers
    assert len(test_text['maltparser_syntax']) == len(test_text['words'])
    # Adding without empty spans
    test_text.pop_layer('maltparser_syntax')
    add_syntax_layer_from_cut_text( test_text, cut_text, 'maltparser_syntax', add_empty_spans=False )
    assert 'maltparser_syntax' in test_text.layers
    assert len(test_text['maltparser_syntax']) > 0
    assert len(test_text['maltparser_syntax']) < len(test_text['words'])
    expected_syntax_layer_first_sentence_dict = \
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
         'enveloping': None,
         'meta': {},
         'name': 'maltparser_syntax',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'deprel': 'nsubj',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 2,
                                     'id': 1,
                                     'lemma': 'Klubi',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (0, 5)},
                   {'annotations': [{'deprel': 'root',
                                     'deps': None,
                                     'feats': {'s': ''},
                                     'head': 0,
                                     'id': 2,
                                     'lemma': 'saama',
                                     'misc': None,
                                     'upostag': 'V',
                                     'xpostag': 'V'}],
                    'base_span': (6, 9)},
                   {'annotations': [{'deprel': 'nummod',
                                     'deps': None,
                                     'feats': {'n': '', 'sg': ''},
                                     'head': 4,
                                     'id': 3,
                                     'lemma': 'kuus',
                                     'misc': None,
                                     'upostag': 'N',
                                     'xpostag': 'N'}],
                    'base_span': (10, 14)},
                   {'annotations': [{'deprel': 'obl',
                                     'deps': None,
                                     'feats': {'p': '', 'sg': ''},
                                     'head': 2,
                                     'id': 4,
                                     'lemma': 'kord',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (15, 20)},
                   {'annotations': [{'deprel': 'nmod',
                                     'deps': None,
                                     'feats': {'g': '', 'sg': ''},
                                     'head': 6,
                                     'id': 5,
                                     'lemma': 'Inglismaa',
                                     'misc': None,
                                     'upostag': 'H',
                                     'xpostag': 'H'}],
                    'base_span': (21, 30)},
                   {'annotations': [{'deprel': 'xcomp',
                                     'deps': None,
                                     'feats': {'sg': '', 'tr': ''},
                                     'head': 2,
                                     'id': 6,
                                     'lemma': 'meister',
                                     'misc': None,
                                     'upostag': 'S',
                                     'xpostag': 'S'}],
                    'base_span': (31, 40)},
                   {'annotations': [{'deprel': 'punct',
                                     'deps': None,
                                     'feats': None,
                                     'head': 2,
                                     'id': 7,
                                     'lemma': '.',
                                     'misc': None,
                                     'upostag': 'Z',
                                     'xpostag': 'Z'}],
                    'base_span': (77, 78)}]}
    #from pprint import pprint
    #pprint( layer_to_dict(test_text['maltparser_syntax'][0:7]) )
    assert expected_syntax_layer_first_sentence_dict == \
           layer_to_dict( test_text['maltparser_syntax'][0:7] )
