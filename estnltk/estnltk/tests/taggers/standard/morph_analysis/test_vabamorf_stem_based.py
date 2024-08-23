from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers.standard.morph_analysis.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.standard.morph_analysis.morf import IGNORE_ATTR
from estnltk_core.converters import layer_to_dict

from estnltk_core.tests import create_amb_attribute_list


def test_stembased_morph_analysis_smoke_test():
    # Smoke test stem-based morphological analysis
    vm_stembased = \
        VabamorfTagger(output_layer='morph_analysis_stembased', stem=True)
    
    text = Text("Ta jõi hundijalavett. Ja läks omastega rappa.")
    text.tag_layer(['compound_tokens', 'sentences'])
    vm_stembased.tag( text )
    
    # Check results
    assert 'morph_analysis_stembased' in text.layers
    assert text['morph_analysis_stembased'].attributes == \
            ('normalized_text', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')
    # Check the whole layer
    #from pprint import pprint
    #pprint( layer_to_dict( text['morph_analysis_stembased'] ) )
    assert layer_to_dict( text['morph_analysis_stembased'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis_stembased',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'normalized_text': 'Ta',
                                     'partofspeech': 'P',
                                     'root': 'ta',
                                     'root_tokens': ['ta']}],
                    'base_span': (0, 2)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'i',
                                     'form': 's',
                                     'normalized_text': 'jõi',
                                     'partofspeech': 'V',
                                     'root': 'jõ',
                                     'root_tokens': ['jõ']}],
                    'base_span': (3, 6)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'tt',
                                     'form': 'sg p',
                                     'normalized_text': 'hundijalavett',
                                     'partofspeech': 'S',
                                     'root': 'hundi_jala_ve',
                                     'root_tokens': ['hundi', 'jala', 've']}],
                    'base_span': (7, 20)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (20, 21)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'normalized_text': 'Ja',
                                     'partofspeech': 'J',
                                     'root': 'ja',
                                     'root_tokens': ['ja']}],
                    'base_span': (22, 24)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 's',
                                     'normalized_text': 'läks',
                                     'partofspeech': 'V',
                                     'root': 'läk',
                                     'root_tokens': ['läk']}],
                    'base_span': (25, 29)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'tega',
                                     'form': 'pl kom',
                                     'normalized_text': 'omastega',
                                     'partofspeech': 'S',
                                     'root': 'omas',
                                     'root_tokens': ['omas']}],
                    'base_span': (30, 38)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'adt',
                                     'normalized_text': 'rappa',
                                     'partofspeech': 'S',
                                     'root': 'rappa',
                                     'root_tokens': ['rappa']}],
                    'base_span': (39, 44)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (44, 45)}]}


def test_stembased_morph_analysis_different_settings():
    # Smoke test stem-based morphological analysis with different settings
    text = Text("Ta jõi hundijalavett. Ja läks omastega rappa. Talle tundus kõik õige.")
    text.tag_layer(['compound_tokens', 'sentences'])

    # Case 1: no disambiguation
    vm_stembased_1 = \
        VabamorfTagger(output_layer='morph_analysis_sb_no_dismb', 
                       disambiguate=False, stem=True)
    vm_stembased_1.tag( text )
    # Check results
    assert 'morph_analysis_sb_no_dismb' in text.layers
    assert len(text['morph_analysis_sb_no_dismb']) == 14
    
    # Case 2: no disambiguation, (propername) guessing
    vm_stembased_2 = \
        VabamorfTagger(output_layer='morph_analysis_sb_no_dismb_2', 
                       disambiguate=False, propername=False, 
                       guess=False, stem=True)
    vm_stembased_2.tag( text )
    # Check results
    assert 'morph_analysis_sb_no_dismb_2' in text.layers
    assert len(text['morph_analysis_sb_no_dismb_2']) == 14
    
    # Case 3: preserve phonetic markers
    vm_stembased_3 = \
        VabamorfTagger(output_layer='morph_analysis_sb_phonetic', 
                       phonetic=True, stem=True)
    vm_stembased_3.tag( text )
    # Check results
    assert 'morph_analysis_sb_phonetic' in text.layers
    assert len(text['morph_analysis_sb_phonetic']) == 14
    
    # Case 4: with slang_lex
    text = Text("Lonks hundijalavett. Ja pandikunni kodukas kahanes kiirelt.")
    text.tag_layer(['compound_tokens', 'sentences'])
    vm_stembased_4 = \
        VabamorfTagger(output_layer='morph_analysis_sb_slang', 
                       slang_lex=True, stem=True)
    vm_stembased_4.tag( text )
    # Check results
    assert 'morph_analysis_sb_slang' in text.layers
    assert len(text['morph_analysis_sb_slang']) == 9


def test_stembased_morph_analysis_postanalysis_tagging():
    # Smoke (some) post-analysis fixes on stem-based morphological analysis
    vm_stembased = \
        VabamorfTagger(output_layer='morph_analysis_stembased', stem=True)

    text = Text("Tiit ei maksnud 6t krooni, vaid ostis 3ga. "+\
                "T. S. Eliot´i ennustus Maaleht.ee-le: võta http://www.tartupostimees.ee üle... irw :-P")
    text.tag_layer(['compound_tokens', 'sentences'])
    vm_stembased.tag( text )
    # Check results
    assert 'morph_analysis_stembased' in text.layers
    assert len(text['morph_analysis_stembased']) == 20
    #from pprint import pprint
    #pprint( layer_to_dict( text['morph_analysis_stembased'] ) )