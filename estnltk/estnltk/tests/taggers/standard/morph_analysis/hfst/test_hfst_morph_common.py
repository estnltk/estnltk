#
#   Tests for common utilities in HFST based morph analysis
# 

from collections import OrderedDict

from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import split_into_morphemes
from estnltk.taggers.standard.morph_analysis.hfst.hfst_morph_common import extract_morpheme_features

def test_hfst_morph_common_split_analyses_into_morphemes():
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_morphemes':['talv+N+Sg+Nom']}, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_morphemes':['miski+Pron+Sg+Ine', '+Use/NotNorm']}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_morphemes':['ütlema+V+Pers+Prt+Ind+Neg']}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_morphemes':['karu+N+Sg+Gen', 'tapma+V+Der', 'ja+N+Sg+Nom', '+Foc/gi']}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_morphemes':['üli+Pref', 'püüd+N+Der', 'lik+A+Sg+Nom']}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_morphemes':['laupäev+N+Sg+Gen', 'hommik+N+Der', 'ti+Adv']}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_morphemes':['kild+N+Dim', 'ke+Sg+Nom']}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_morphemes':['ilu+N+Sg+Gen', 'aed+N+Pl+Par', '+Use/Rare']}, \
                  {'word':'kohtumispaik',\
                   'raw_analysis':'kohtumine+N+Der/minus#paik+N+Sg+Nom' , \
                   'expected_morphemes':['kohtumine+N+Der/minus', 'paik+N+Sg+Nom']}, \
                  {'word':'lahkumisvalust',\
                   'raw_analysis':'lahkuma+V+Der/mine+N+Der/minus#valu+N+Sg+Ela' , \
                   'expected_morphemes':['lahkuma+V+Der', 'mine+N+Der/minus', 'valu+N+Sg+Ela']}, \
                  {'word':'hingamisteed',\
                   'raw_analysis':'hingamine+N+Der/minus#tee+N+Pl+Nom' , \
                   'expected_morphemes':['hingamine+N+Der/minus', 'tee+N+Pl+Nom']}, \
                  {'word':'arvamis-',\
                   'raw_analysis':'arvama+V+Der/mine+N+Der/minus' , \
                   'expected_morphemes':['arvama+V+Der', 'mine+N+Der/minus']}, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        assert morphemes == test_item['expected_morphemes']



def test_hfst_morph_common_extract_morpheme_features():
    test_data = [ {'word':'talv',\
                   'raw_analysis':'talv+N+Sg+Nom', \
                   'expected_features': OrderedDict([('morphemes', ['talv']), ('postags', ['N']), ('forms', ['Sg+Nom']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':'millegis',\
                   'raw_analysis':'miski+Pron+Sg+Ine+Use/NotNorm', \
                   'expected_features': OrderedDict([('morphemes', ['miski']), ('postags', ['Pron']), ('forms', ['Sg+Ine']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', ['Use/NotNorm'])])}, \
                  {'word':'öelnud',\
                   'raw_analysis':'ütlema+V+Pers+Prt+Ind+Neg', \
                   'expected_features': OrderedDict([('morphemes', ['ütlema']), ('postags', ['V']), ('forms', ['Pers+Prt+Ind+Neg']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])])}, \
                  {'word':'karutapjagi',\
                   'raw_analysis':'karu+N+Sg+Gen#tapma+V+Der/ja+N+Sg+Nom+Foc/gi' , \
                   'expected_features': OrderedDict([('morphemes', ['karu', 'tapma', 'ja']), ('postags', ['N', 'V', 'N']), \
                                                     ('forms', ['Sg+Gen', 'Der', 'Sg+Nom']), ('has_clitic', [False,False,True]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'ülipüüdlik',\
                   'raw_analysis':'üli+Pref#püüd+N+Der/lik+A+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['üli', 'püüd', 'lik']), ('postags', ['Pref', 'N', 'A']), \
                                                     ('forms', ['', 'Der', 'Sg+Nom']), ('has_clitic', [False,False,False]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'laupäevahommikuti',\
                   'raw_analysis':'laupäev+N+Sg+Gen#hommik+N+Der/ti+Adv' , \
                   'expected_features': OrderedDict([('morphemes', ['laupäev', 'hommik', 'ti']), ('postags', ['N', 'N', 'Adv']), \
                                                     ('forms', ['Sg+Gen', 'Der', '']), ('has_clitic', [False,False,False]), \
                                                     ('is_guessed', [False,False,False]), ('usage', ['','',''])])}, \
                  {'word':'killuke',\
                   'raw_analysis':'kild+N+Dim/ke+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['kild', 'ke']), ('postags', ['N', '']), ('forms', ['Dim', 'Sg+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'iluaedasid',\
                   'raw_analysis':'ilu+N+Sg+Gen#aed+N+Pl+Par+Use/Rare' , \
                   'expected_features': OrderedDict([('morphemes', ['ilu', 'aed']), ('postags', ['N', 'N']), ('forms', ['Sg+Gen', 'Pl+Par']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['','Use/Rare'])])}, \
                  {'word':'vannaema',\
                   'raw_analysis':'vanna+Guess#ema+N+Sg+Gen' , \
                   'expected_features': OrderedDict([('morphemes', ['vanna', 'ema']), ('postags', ['', 'N']), ('forms', ['', 'Sg+Gen']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [True,False]), ('usage', ['',''])])}, \
                  # It should also work on empty string
                  {'word':'',\
                   'raw_analysis':'' , \
                   'expected_features': OrderedDict([('morphemes', []), ('postags', []), ('forms', []), ('has_clitic', []), \
                                                     ('is_guessed', []), ('usage', [])])}, \
                  # Words containing shortenings
                  {'word':'arvamis-',\
                   'raw_analysis':'arvama+V+Der/mine+N+Der/minus' , \
                   'expected_features': OrderedDict([('morphemes', ['arvama', 'mine']), ('postags', ['V', 'N']), ('forms', ['Der', 'Der/minus']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'kohtumispaik',\
                   'raw_analysis':'kohtumine+N+Der/minus#paik+N+Sg+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['kohtumine', 'paik']), ('postags', ['N', 'N']), ('forms', ['Der/minus', 'Sg+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  {'word':'hingamisteed',\
                   'raw_analysis':'hingamine+N+Der/minus#tee+N+Pl+Nom' , \
                   'expected_features': OrderedDict([('morphemes', ['hingamine', 'tee']), ('postags', ['N', 'N']), ('forms', ['Der/minus', 'Pl+Nom']), \
                                                     ('has_clitic', [False,False]), ('is_guessed', [False,False]), ('usage', ['',''])])}, \
                  # Guessed proper nouns
                  {'word':'Sallamaa',\
                   'raw_analysis':'Sallamaa+Guess+N+Prop+Sg+Gen' , \
                   'expected_features': OrderedDict([('morphemes', ['Sallamaa']), ('postags', ['N+Prop']), ('forms', ['Sg+Gen']), \
                                                     ('has_clitic', [False]), ('is_guessed', [True]), ('usage', [''])])}, \
                  {'word':'Inglismaal',\
                   'raw_analysis':'Inglismaa+Guess+N+Prop+Sg+Ade' , \
                   'expected_features': OrderedDict([('morphemes', ['Inglismaa']), ('postags', ['N+Prop']), ('forms', ['Sg+Ade']), \
                                                     ('has_clitic', [False]), ('is_guessed', [True]), ('usage', [''])])}, \
                  # Punctuation
                  {'word':'--',\
                   'raw_analysis':'--+PUNCT' , \
                   'expected_features': OrderedDict([('morphemes', ['--']), ('postags', ['PUNCT']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':'"',\
                   'raw_analysis':'"+PUNCT' , \
                   'expected_features': OrderedDict([('morphemes', ['"']), ('postags', ['PUNCT']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  {'word':')',\
                   'raw_analysis':')+PUNCT+RIGHT' , \
                   'expected_features': OrderedDict([('morphemes', [')']), ('postags', ['PUNCT']), ('forms', ['RIGHT']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                  # Abbreviations
                  {'word':'vrd',\
                   'raw_analysis':'vrd+ABBR' , \
                   'expected_features': OrderedDict([('morphemes', ['vrd']), ('postags', ['ABBR']), ('forms', ['']), \
                                                     ('has_clitic', [False]), ('is_guessed', [False]), ('usage', [''])]) }, \
                ]
    for test_item in test_data:
        input_raw_analysis = test_item['raw_analysis']
        morphemes = split_into_morphemes( input_raw_analysis )
        morpheme_feats = extract_morpheme_features( morphemes )
        #print(morpheme_feats)
        assert morpheme_feats == test_item['expected_features']

