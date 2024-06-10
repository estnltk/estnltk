import os, os.path
import unittest
from importlib.util import find_spec

from estnltk import Text
from estnltk_core import Span
from estnltk.converters import dict_to_text, text_to_dict
from estnltk.converters import layer_to_dict, dict_to_layer
from estnltk.downloader import get_resource_paths

from estnltk.taggers.standard.syntax.phrase_extraction.phrase_extractor import PhraseExtractor

# Try to get the resources path for stanzasyntaxtagger. If missing, do nothing. It's up for the user to download the missing resources
STANZA_SYNTAX_MODELS_PATH = get_resource_paths("stanzasyntaxtagger", only_latest=True, download_missing=False)

def check_if_estnltk_neural_is_available():
    return find_spec("estnltk_neural") is not None

# Example inputs
example_sentence_1_dict = \
    {'layers': [{'ambiguous': False,
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
                 'name': 'conll_syntax',
                 'parent': None,
                 'secondary_attributes': ('parent_span', 'children'),
                 'serialisation_module': 'syntax_v0',
                 'spans': [{'annotations': [{'deprel': 'root',
                                             'deps': [('root', 0)],
                                             'feats': {'Case': 'Tra',
                                                       'Number': 'Sing',
                                                       'PronType': 'Dem'},
                                             'head': 0,
                                             'id': 1,
                                             'lemma': 'see',
                                             'misc': {'SpaceAfter': 'No'},
                                             'upostag': 'PRON',
                                             'xpostag': 'P'}],
                            'base_span': (0, 7)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': [('punct', 6)],
                                             'feats': None,
                                             'head': 6,
                                             'id': 2,
                                             'lemma': ',',
                                             'misc': None,
                                             'upostag': 'PUNCT',
                                             'xpostag': 'Z'}],
                            'base_span': (8, 9)},
                           {'annotations': [{'deprel': 'mark',
                                             'deps': [('mark', 6)],
                                             'feats': None,
                                             'head': 6,
                                             'id': 3,
                                             'lemma': 'et',
                                             'misc': None,
                                             'upostag': 'SCONJ',
                                             'xpostag': 'J'}],
                            'base_span': (10, 12)},
                           {'annotations': [{'deprel': 'obl',
                                             'deps': [('obl', 6)],
                                             'feats': {'Case': 'Ade',
                                                       'Number': 'Plur'},
                                             'head': 6,
                                             'id': 4,
                                             'lemma': 'uurija',
                                             'misc': None,
                                             'upostag': 'NOUN',
                                             'xpostag': 'S'}],
                            'base_span': (13, 22)},
                           {'annotations': [{'deprel': 'cop',
                                             'deps': [('cop', 6)],
                                             'feats': {'Mood': 'Cnd',
                                                       'Tense': 'Pres',
                                                       'VerbForm': 'Fin',
                                                       'Voice': 'Act'},
                                             'head': 6,
                                             'id': 5,
                                             'lemma': 'olema',
                                             'misc': None,
                                             'upostag': 'AUX',
                                             'xpostag': 'V'}],
                            'base_span': (23, 28)},
                           {'annotations': [{'deprel': 'acl',
                                             'deps': [('acl', 1)],
                                             'feats': {'Case': 'Nom',
                                                       'Degree': 'Cmp',
                                                       'Number': 'Sing'},
                                             'head': 1,
                                             'id': 6,
                                             'lemma': 'lihtsam',
                                             'misc': None,
                                             'upostag': 'ADJ',
                                             'xpostag': 'A'}],
                            'base_span': (29, 36)},
                           {'annotations': [{'deprel': 'obl',
                                             'deps': [('obl', 9)],
                                             'feats': {'Case': 'Gen',
                                                       'Number': 'Sing'},
                                             'head': 9,
                                             'id': 7,
                                             'lemma': 'raha_pesu',
                                             'misc': None,
                                             'upostag': 'NOUN',
                                             'xpostag': 'S'}],
                            'base_span': (37, 45)},
                           {'annotations': [{'deprel': 'case',
                                             'deps': [('case', 7)],
                                             'feats': {'AdpType': 'Post'},
                                             'head': 7,
                                             'id': 8,
                                             'lemma': 'vastu',
                                             'misc': None,
                                             'upostag': 'ADP',
                                             'xpostag': 'K'}],
                            'base_span': (46, 51)},
                           {'annotations': [{'deprel': 'csubj:cop',
                                             'deps': [('csubj', 6)],
                                             'feats': {'VerbForm': 'Inf'},
                                             'head': 6,
                                             'id': 9,
                                             'lemma': 'võitlema',
                                             'misc': {'SpaceAfter': 'No'},
                                             'upostag': 'VERB',
                                             'xpostag': 'V'}],
                            'base_span': (52, 60)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': [('punct', 1)],
                                             'feats': None,
                                             'head': 1,
                                             'id': 10,
                                             'lemma': '.',
                                             'misc': None,
                                             'upostag': 'PUNCT',
                                             'xpostag': 'Z'}],
                            'base_span': (61, 62)}]},
                {'ambiguous': True,
                 'attributes': (),
                 'enveloping': None,
                 'meta': {},
                 'name': 'words',
                 'parent': None,
                 'secondary_attributes': (),
                 'serialisation_module': None,
                 'spans': [{'annotations': [{}], 'base_span': (0, 7)},
                           {'annotations': [{}], 'base_span': (8, 9)},
                           {'annotations': [{}], 'base_span': (10, 12)},
                           {'annotations': [{}], 'base_span': (13, 22)},
                           {'annotations': [{}], 'base_span': (23, 28)},
                           {'annotations': [{}], 'base_span': (29, 36)},
                           {'annotations': [{}], 'base_span': (37, 45)},
                           {'annotations': [{}], 'base_span': (46, 51)},
                           {'annotations': [{}], 'base_span': (52, 60)},
                           {'annotations': [{}], 'base_span': (61, 62)}]},
                {'ambiguous': False,
                 'attributes': (),
                 'enveloping': 'words',
                 'meta': {},
                 'name': 'sentences',
                 'parent': None,
                 'secondary_attributes': (),
                 'serialisation_module': None,
                 'spans': [{'annotations': [{}],
                            'base_span': ((0, 7),
                                          (8, 9),
                                          (10, 12),
                                          (13, 22),
                                          (23, 28),
                                          (29, 36),
                                          (37, 45),
                                          (46, 51),
                                          (52, 60),
                                          (61, 62))}]}],
     'meta': {},
     'relation_layers': [],
     'text': 'Selleks , et uurijatel oleks lihtsam rahapesu vastu võidelda .'}


example_sentence_2_dict = \
        {'layers': [{'ambiguous': False,
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
                 'name': 'conll_syntax',
                 'parent': None,
                 'secondary_attributes': ('parent_span', 'children'),
                 'serialisation_module': 'syntax_v0',
                 'spans': [{'annotations': [{'deprel': 'amod',
                                             'deps': [('amod', 2)],
                                             'feats': {'Case': 'Nom',
                                                       'NumForm': 'Word',
                                                       'NumType': 'Ord',
                                                       'Number': 'Sing'},
                                             'head': 2,
                                             'id': 1,
                                             'lemma': 'esimene',
                                             'misc': None,
                                             'upostag': 'ADJ',
                                             'xpostag': 'N'}],
                            'base_span': (0, 7)},
                           {'annotations': [{'deprel': 'nsubj',
                                             'deps': [('nsubj', 3)],
                                             'feats': {'Case': 'Nom',
                                                       'Number': 'Sing'},
                                             'head': 3,
                                             'id': 2,
                                             'lemma': 'võistlus',
                                             'misc': None,
                                             'upostag': 'NOUN',
                                             'xpostag': 'S'}],
                            'base_span': (8, 16)},
                           {'annotations': [{'deprel': 'root',
                                             'deps': [('root', 0)],
                                             'feats': {'Mood': 'Ind',
                                                       'Number': 'Sing',
                                                       'Person': '3',
                                                       'Tense': 'Pres',
                                                       'VerbForm': 'Fin',
                                                       'Voice': 'Act'},
                                             'head': 0,
                                             'id': 3,
                                             'lemma': 'toimuma',
                                             'misc': None,
                                             'upostag': 'VERB',
                                             'xpostag': 'V'}],
                            'base_span': (17, 23)},
                           {'annotations': [{'deprel': 'amod',
                                             'deps': [('amod', 5)],
                                             'feats': {'Case': 'Ade',
                                                       'NumForm': 'Digit',
                                                       'NumType': 'Ord',
                                                       'Number': 'Sing'},
                                             'head': 5,
                                             'id': 4,
                                             'lemma': '29.',
                                             'misc': None,
                                             'upostag': 'ADJ',
                                             'xpostag': 'N'}],
                            'base_span': (24, 27)},
                           {'annotations': [{'deprel': 'obl',
                                             'deps': [('obl', 3)],
                                             'feats': {'Case': 'Ade',
                                                       'Number': 'Sing'},
                                             'head': 3,
                                             'id': 5,
                                             'lemma': 'mai',
                                             'misc': None,
                                             'upostag': 'NOUN',
                                             'xpostag': 'S'}],
                            'base_span': (28, 32)},
                           {'annotations': [{'deprel': 'obl',
                                             'deps': [('obl', 3)],
                                             'feats': {'Case': 'Ine',
                                                       'Number': 'Sing'},
                                             'head': 3,
                                             'id': 6,
                                             'lemma': 'Väike-Maarja',
                                             'misc': {'NE': 'B-Loc',
                                                      'SpaceAfter': 'No'},
                                             'upostag': 'PROPN',
                                             'xpostag': 'S'}],
                            'base_span': (33, 46)},
                           {'annotations': [{'deprel': 'punct',
                                             'deps': [('punct', 3)],
                                             'feats': None,
                                             'head': 3,
                                             'id': 7,
                                             'lemma': '.',
                                             'misc': None,
                                             'upostag': 'PUNCT',
                                             'xpostag': 'Z'}],
                            'base_span': (47, 48)}]},
                {'ambiguous': True,
                 'attributes': (),
                 'enveloping': None,
                 'meta': {},
                 'name': 'words',
                 'parent': None,
                 'secondary_attributes': (),
                 'serialisation_module': None,
                 'spans': [{'annotations': [{}], 'base_span': (0, 7)},
                           {'annotations': [{}], 'base_span': (8, 16)},
                           {'annotations': [{}], 'base_span': (17, 23)},
                           {'annotations': [{}], 'base_span': (24, 27)},
                           {'annotations': [{}], 'base_span': (28, 32)},
                           {'annotations': [{}], 'base_span': (33, 46)},
                           {'annotations': [{}], 'base_span': (47, 48)}]},
                {'ambiguous': False,
                 'attributes': (),
                 'enveloping': 'words',
                 'meta': {},
                 'name': 'sentences',
                 'parent': None,
                 'secondary_attributes': (),
                 'serialisation_module': None,
                 'spans': [{'annotations': [{}],
                            'base_span': ((0, 7),
                                          (8, 16),
                                          (17, 23),
                                          (24, 27),
                                          (28, 32),
                                          (33, 46),
                                          (47, 48))}]}],
     'meta': {},
     'relation_layers': [],
     'text': 'Esimene võistlus toimub 29. mail Väike-Maarjas .'}

def test_syntax_phrase_extractor_smoke():
    # Smoke test that PhraseExtractor works on (manually corrected) conllu syntax
    # Based on: 
    #   https://github.com/estnltk/estnltk/blob/93a9435c353c6b0c39fdf2596ca9b9f48bcf8205/estnltk/estnltk/taggers/standard/syntax/phrase_extraction/tests/phrase_extractor_jupyter_tests.ipynb
    phrase_tagger1 = PhraseExtractor(deprel="obl", 
                                     syntax_layer="conll_syntax", 
                                     sentences_layer='sentences',
                                     output_layer="obl_phrases")
    # Case 1
    # 'text': 'Selleks , et uurijatel oleks lihtsam rahapesu vastu võidelda .'
    sentence1 = dict_to_text( example_sentence_1_dict )
    phrase_tagger1.tag( sentence1 )
    assert phrase_tagger1.output_layer in sentence1.layers
    assert len(sentence1.obl_phrases) == 2, len(sentence1.obl_phrases)
    assert list(sentence1.obl_phrases[0].text) == ['uurijatel'], list(sentence1.obl_phrases[0].text)
    assert len(sentence1.obl_phrases[1]) == 2, len(sentence1.obl_phrases[1])
    assert list(sentence1.obl_phrases[1].text) == ['rahapesu', 'vastu'], list(sentence1.obl_phrases[1].text)
    
    # Case 2
    # 'text': 'Esimene võistlus toimub 29. mail Väike-Maarjas .'
    sentence2 = dict_to_text( example_sentence_2_dict )
    phrase_tagger1.tag( sentence2 )
    assert phrase_tagger1.output_layer in sentence2.layers
    assert len(sentence2.obl_phrases) == 2, len(sentence2.obl_phrases)
    assert list(sentence2.obl_phrases[0].text) == ['29.', 'mail'], list(sentence2.obl_phrases[0].text)
    assert len(sentence2.obl_phrases[1]) == 1, len(sentence2.obl_phrases[1])
    assert list(sentence2.obl_phrases[1].text) == ['Väike-Maarjas'], list(sentence2.obl_phrases[1].text)


def test_syntax_phrase_extractor_layer_serialization():
    # Test layer <-> dict serialization of PhraseExtractor's output_layer
    phrase_tagger = PhraseExtractor(deprel="obl", 
                                    syntax_layer="conll_syntax", 
                                    sentences_layer='sentences',
                                    output_layer="obl_phrases")
    # Case 1
    # 'text': 'Selleks , et uurijatel oleks lihtsam rahapesu vastu võidelda .'
    sentence1 = dict_to_text( example_sentence_1_dict )
    phrase_tagger.tag( sentence1 )
    # layer -> dict
    assert layer_to_dict( sentence1[phrase_tagger.output_layer] ) == \
        {'ambiguous': False,
         'attributes': ('root_id', 'root'),
         'enveloping': 'conll_syntax',
         'meta': {},
         'name': 'obl_phrases',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': 'syntax_phrases_v0',
         'spans': [{'annotations': [{'root_id': 4}], 'base_span': ((13, 22),)},
                   {'annotations': [{'root_id': 7}],
                    'base_span': ((37, 45), (46, 51))}]}
    # dict -> layer
    new_layer = dict_to_layer(layer_to_dict(sentence1[phrase_tagger.output_layer]), 
                              text_object=sentence1)
    assert len(new_layer) == 2
    for new_span in new_layer:
        assert isinstance(new_span['root'], Span)
        assert new_span['root'].annotations[0]['id'] == new_span['root_id']
        assert new_span['root'].legal_attribute_names == sentence1["conll_syntax"].attributes

    # Case 2
    # 'text': 'Esimene võistlus toimub 29. mail Väike-Maarjas .'
    sentence2 = dict_to_text( example_sentence_2_dict )
    phrase_tagger.tag( sentence2 )
    assert layer_to_dict( sentence2[phrase_tagger.output_layer] ) == \
        {'ambiguous': False,
         'attributes': ('root_id', 'root'),
         'enveloping': 'conll_syntax',
         'meta': {},
         'name': 'obl_phrases',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': 'syntax_phrases_v0',
         'spans': [{'annotations': [{'root_id': 5}], 'base_span': ((24, 27), (28, 32))},
                   {'annotations': [{'root_id': 6}], 'base_span': ((33, 46),)}]}

    # dict -> layer
    new_layer = dict_to_layer(layer_to_dict(sentence2[phrase_tagger.output_layer]), 
                              text_object=sentence2)
    assert len(new_layer) == 2
    for new_span in new_layer:
        assert isinstance(new_span['root'], Span)
        assert new_span['root'].annotations[0]['id'] == new_span['root_id']
        assert new_span['root'].legal_attribute_names == sentence2["conll_syntax"].attributes


@unittest.skipIf(not check_if_estnltk_neural_is_available(),
                 reason="estnltk_neural is not installed. You'll need estnltk_neural for running this test.")
@unittest.skipIf(STANZA_SYNTAX_MODELS_PATH is None,
                 reason="StanzaSyntaxTagger's model is required by this test. Use estnltk.download('stanzasyntaxtagger') to fetch the missing resource.")
def test_syntax_phrase_extractor_on_stanza_syntax():
    # Test that PhraseExtractor works on the output of StanzaSyntaxTagger (requires estnltk_neural)
    # Based on: 
    #   https://github.com/estnltk/estnltk/blob/93a9435c353c6b0c39fdf2596ca9b9f48bcf8205/estnltk/estnltk/taggers/standard/syntax/phrase_extraction/tests/phrase_extractor_jupyter_tests.ipynb
    from estnltk_core.layer_operations import split_by_sentences
    from estnltk_neural.taggers import StanzaSyntaxTagger
    stanza_tagger = StanzaSyntaxTagger(input_type="morph_extended", input_morph_layer="morph_extended", add_parent_and_children=True)
    phrase_tagger2 = PhraseExtractor(deprel="obl", syntax_layer="stanza_syntax", output_layer="obl_phrases")
    three_sentences = Text('Kolme aastaga on Eminem alias Marshall Mathers III ( 30 ) kindlalt meie teadvusesse sööbinud . '+\
                           'Aga ma sain sellest nõiaringist välja . '+\
                           'Oleksin võinud vangi sattuda .')
    three_sentences.tag_layer('sentences')
    assert len( three_sentences['sentences'] ) == 3
    three_sentences.tag_layer('morph_extended')
    stanza_tagger.tag( three_sentences )
    phrase_tagger2.tag( three_sentences )
    split_sentences = split_by_sentences(text=three_sentences,
                                         layers_to_keep=list(three_sentences.layers),
                                         trim_overlapping=True)
    assert len(split_sentences) == 3
    # Validate sentence Text objects
    txt1 = split_sentences[0]
    assert len(txt1.obl_phrases) == 2, len(txt1.obl_phrases)
    assert list(txt1.obl_phrases[0].text) == ['Kolme', 'aastaga'], list(txt1.obl_phrases[0].text)
    assert len(txt1.obl_phrases[0]) == 2, len(txt1.obl_phrases[0])
    assert len(txt1.obl_phrases[1]) == 2, len(txt1.obl_phrases[1])
    assert list(txt1.obl_phrases[1].text) == ['meie', 'teadvusesse'], list(txt1.obl_phrases[1].text)
    txt2 = split_sentences[1]
    # Note: restult depends on stanza's version/implementation
    assert len(txt2.obl_phrases) in [1, 2], len(txt2.obl_phrases)
    if len(txt2.obl_phrases) == 2:
        # Result with stanza version < 1.8.2,  model version stanza_syntax_2023-01-21
        assert list(txt2.obl_phrases[0].text) == ['sellest'], list(txt2.obl_phrases[0].text)
        assert len(txt2.obl_phrases[0]) == 1, len(txt2.obl_phrases[0])
        assert len(txt2.obl_phrases[1]) == 1, len(txt2.obl_phrases[1])
        assert list(txt2.obl_phrases[1].text) == ['nõiaringist'], list(txt2.obl_phrases[1].text)
    elif len(txt2.obl_phrases) == 1:
        # Result with stanza version 1.8.2,  model version stanza_syntax_2023-01-21
        assert list(txt2.obl_phrases[0].text) == ['nõiaringist'], list(txt2.obl_phrases[0].text)
        assert len(txt2.obl_phrases[0]) == 1, len(txt2.obl_phrases[0])
    txt3 = split_sentences[2]
    assert len(txt3.obl_phrases) == 1, len(txt3.obl_phrases)
    assert list(txt3.obl_phrases[0].text) == ['vangi'], list(txt3.obl_phrases[0].text)
    assert len(txt3.obl_phrases[0]) == 1, len(txt3.obl_phrases[0])

