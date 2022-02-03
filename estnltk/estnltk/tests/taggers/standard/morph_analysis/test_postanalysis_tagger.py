from estnltk import Text, Annotation
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import PostMorphAnalysisTagger
from estnltk.taggers.standard.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.standard.text_segmentation.whitespace_tokens_tagger import WhiteSpaceTokensTagger

from estnltk_core.tests import create_amb_attribute_list
from estnltk_core.converters import layer_to_records

# ----------------------------------
#   Helper functions
# ----------------------------------

def _sort_morph_analysis_records( morph_analysis_records:list ):
    '''Sorts sublists (lists of analyses of a single word) of 
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order. '''
    for wrid, word_records_list in enumerate( morph_analysis_records ):
        sorted_records = sorted( word_records_list, key = lambda x : \
            str(x['root'])+str(x['ending'])+str(x['clitic'])+\
            str(x['partofspeech'])+str(x['form']) )
        morph_analysis_records[wrid] = sorted_records

# ----------------------------------

def test_postanalysis_fix_names_with_initials():
    # Tests that names with initials (such as "T. S. Eliot") will have their:
    #    * partofspeech fixed to H;
    #    * root tokens normalized:
    #       1. contain underscores between initials/names;
    #       2. names do no start with no lowercase letters;
    # Initialize tagger
    morf_tagger = VabamorfTagger(postanalysis_tagger=PostMorphAnalysisTagger(fix_names_with_initials=True))
    # Case 1
    text=Text('Romaan kinnitab üht T. S. Eliot´i ennustust.')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [
        [{'normalized_text': 'Romaan', 'clitic': '', 'lemma': 'romaan', 'ending': '0', 'partofspeech': 'S', 'form': 'sg n', 'root_tokens': ['romaan',], 'end': 6, 'root': 'romaan', 'start': 0}], \
        [{'normalized_text': 'kinnitab', 'clitic': '', 'lemma': 'kinnitama', 'ending': 'b', 'partofspeech': 'V', 'form': 'b', 'root_tokens': ['kinnita',], 'end': 15, 'root': 'kinnita', 'start': 7}], \
        [{'normalized_text': 'üht', 'clitic': '', 'lemma': 'üks', 'ending': '0', 'partofspeech': 'N', 'form': 'sg p', 'root_tokens': ['üks',], 'end': 19, 'root': 'üks', 'start': 16}, \
         {'normalized_text': 'üht', 'clitic': '', 'lemma': 'üks', 'ending': '0', 'partofspeech': 'P', 'form': 'sg p', 'root_tokens': ['üks',], 'end': 19, 'root': 'üks', 'start': 16}], \
        [{'normalized_text': 'T. S. Eliot´i', 'root': 'T. _S. _Eliot', 'start': 20, 'form': 'sg g', 'root_tokens': ['T. ', 'S. ', 'Eliot'], 'clitic': '', 'partofspeech': 'H', 'lemma': 'T. S. Eliot', 'ending': '0', 'end': 33}],\
        [{'normalized_text': 'ennustust', 'clitic': '', 'lemma': 'ennustus', 'ending': 't', 'partofspeech': 'S', 'form': 'sg p', 'root_tokens': ['ennustus',], 'end': 43, 'root': 'ennustus', 'start': 34}], \
        [{'normalized_text': '.', 'clitic': '', 'lemma': '.', 'ending': '', 'partofspeech': 'Z', 'form': '', 'root_tokens': ['.',], 'end': 44, 'root': '.', 'start': 43}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2
    text=Text("Läände jõudis tualettpaber tänu Joseph C. Gayetty'le.")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Läände', 'lemma': 'lääs', 'root': 'lääs', 'ending': 'de', 'root_tokens': ['lääs',], 'start': 0, 'end': 6, 'clitic': '', 'partofspeech': 'S', 'form': 'adt'}], \
        [{'normalized_text': 'jõudis', 'lemma': 'jõudma', 'root': 'jõud', 'ending': 'is', 'root_tokens': ['jõud',], 'start': 7, 'end': 13, 'clitic': '', 'partofspeech': 'V', 'form': 's'}], \
        [{'normalized_text': 'tualettpaber', 'lemma': 'tualettpaber', 'root': 'tualett_paber', 'ending': '0', 'root_tokens': ['tualett', 'paber'], 'start': 14, 'end': 26, 'clitic': '', 'partofspeech': 'S', 'form': 'sg n'}], \
        [{'normalized_text': 'tänu', 'lemma': 'tänu', 'root': 'tänu', 'ending': '0', 'root_tokens': ['tänu',], 'start': 27, 'end': 31, 'clitic': '', 'partofspeech': 'K', 'form': ''}], \
        [{'normalized_text': 'Joseph', 'lemma': 'Joseph', 'root': 'Joseph', 'ending': '0', 'root_tokens': ['Joseph',], 'start': 32, 'end': 38, 'clitic': '', 'partofspeech': 'H', 'form': 'sg n'}], \
        [{'normalized_text': "C. Gayetty'le", 'clitic': '', 'partofspeech': 'H', 'lemma': 'C. Gayetty', 'end': 52, 'ending': 'le', 'root_tokens': ['C. ', 'Gayetty'], 'root': 'C. _Gayetty', 'start': 39, 'form': 'sg all'}], \
        [{'normalized_text': '.', 'lemma': '.', 'root': '.', 'ending': '', 'root_tokens': ['.',], 'start': 52, 'end': 53, 'clitic': '', 'partofspeech': 'Z', 'form': ''}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 3
    text=Text("Arhitektid E. Lüüs, E. Eharand ja T. Soans")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Arhitektid', 'start': 0, 'ending': 'd', 'root_tokens': ['arhitekt',], 'form': 'pl n', 'end': 10, 'lemma': 'arhitekt', 'root': 'arhitekt', 'clitic': '', 'partofspeech': 'S'}], \
        [{'normalized_text': 'E. Lüüs', 'root_tokens': ['E. ', 'Lüüs'], 'root': 'E. _Lüüs', 'clitic': '', 'partofspeech': 'H', 'lemma': 'E. Lüüs', 'start': 11, 'end': 18, 'form': 'sg n', 'ending': '0'}], \
        [{'normalized_text': ',', 'root_tokens': [',',], 'root': ',', 'clitic': '', 'partofspeech': 'Z', 'lemma': ',', 'start': 18, 'end': 19, 'form': '', 'ending': ''}], \
        [{'normalized_text': 'E. Eharand', 'root_tokens': ['E. ', 'Eha', 'rand'], 'root': 'E. _Eha_rand', 'clitic': '', 'partofspeech': 'H', 'lemma': 'E. Eharand', 'start': 20, 'end': 30, 'form': 'sg n', 'ending': '0'}], \
        [{'normalized_text': 'ja', 'root_tokens': ['ja',], 'root': 'ja', 'clitic': '', 'partofspeech': 'J', 'lemma': 'ja', 'start': 31, 'end': 33, 'form': '', 'ending': '0'}], \
        [{'normalized_text': 'T. Soans', 'root_tokens': ['T. ', 'Soans'], 'root': 'T. _Soans', 'clitic': '', 'partofspeech': 'H', 'lemma': 'T. Soans', 'start': 34, 'end': 42, 'form': '?', 'ending': '0'}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 4
    # Negative case: do not fix partofspeech on verbs (yet)
    text=Text("Ansambli nimeks oli Swing B. Esinemas käisime tantsuõhtutel")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    expected_result = create_amb_attribute_list([[['ansambel', 'S']], [['nimi', 'S']], [['olema', 'V']], 
                                                 [['Swing', 'H']], [['B. esinema', 'V']], [['käima', 'V']], 
                                                 [['tantsuõhtu', 'S']]], ('lemma', 'partofspeech')) 
    # TODO: 'B. esinema' is actually a wrong compound token, 
    #        needs to be fixed in the future
    result = text.morph_analysis['lemma', 'partofspeech']
    assert expected_result == result


def test_postanalysis_fix_emoticons():
    # Tests that emoticons have postag 'Z':
    # Initialize tagger
    morf_tagger = VabamorfTagger(postanalysis_tagger=PostMorphAnalysisTagger(fix_emoticons=True))
    # Case 1
    text=Text('Äge pull :D irw :-P')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Äge', 'form': 'sg n', 'clitic': '', 'lemma': 'äge', 'start': 0, 'end': 3, 'ending': '0', 'root': 'äge', 'partofspeech': 'A', 'root_tokens': ['äge',]}], \
        [{'normalized_text': 'pull', 'form': 'sg n', 'clitic': '', 'lemma': 'pull', 'start': 4, 'end': 8, 'ending': '0', 'root': 'pull', 'partofspeech': 'S', 'root_tokens': ['pull',]}], \
        [{'normalized_text': ':D', 'form': '?', 'clitic': '', 'lemma': 'D', 'start': 9, 'end': 11, 'ending': '0', 'root': 'D', 'partofspeech': 'Z', 'root_tokens': ['D',]}], \
        [{'normalized_text': 'irw', 'form': 'sg n', 'clitic': '', 'lemma': 'irw', 'start': 12, 'end': 15, 'ending': '0', 'root': 'irw', 'partofspeech': 'S', 'root_tokens': ['irw',]}], \
        [{'normalized_text': ':-P', 'form': '?', 'clitic': '', 'lemma': 'P', 'start': 16, 'end': 19, 'ending': '0', 'root': 'P', 'partofspeech': 'Z', 'root_tokens': ['P',]}]]
    # TODO: roots of emoticons also need to be fixed, but this 
    #       has a prerequisite that methods creating lemmas &
    #       root_tokens work in-line with the fixes
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict, results_dict


def test_postanalysis_fix_www_addresses():
    # Tests that www addresses have postag 'H':
    # Initialize tagger
    morf_tagger = VabamorfTagger(postanalysis_tagger=PostMorphAnalysisTagger(fix_www_addresses=True))
    # Case 1
    text=Text('Lugeja saatis Maaleht.ee-le http://www.tartupostimees.ee foto.')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Lugeja', 'clitic': '', 'lemma': 'lugeja', 'start': 0, 'end': 6, 'partofspeech': 'S', 'form': 'sg g', 'root_tokens': ['lugeja',], 'root': 'lugeja', 'ending': '0'}], \
        [{'normalized_text': 'saatis', 'clitic': '', 'lemma': 'saatma', 'start': 7, 'end': 13, 'partofspeech': 'V', 'form': 's', 'root_tokens': ['saat',], 'root': 'saat', 'ending': 'is'}], \
        [{'normalized_text': 'Maaleht.ee-le', 'clitic': '', 'lemma': 'Maaleht.ee', 'start': 14, 'end': 27, 'partofspeech': 'H', 'form': 'sg all', 'root_tokens': ['Maaleht.ee',], 'root': 'Maaleht.ee', 'ending': 'le'}], \
        [{'normalized_text': 'http://www.tartupostimees.ee', 'clitic': '', 'lemma': 'http://www.tartupostimees.ee', 'start': 28, 'end': 56, 'partofspeech': 'H', 'form': '?', 'root_tokens': ['http://www.tartupostimees.ee',], 'root': 'http://www.tartupostimees.ee', 'ending': '0'}], \
        [{'normalized_text': 'foto', 'clitic': '', 'lemma': 'foto', 'start': 57, 'end': 61, 'partofspeech': 'S', 'form': 'sg n', 'root_tokens': ['foto',], 'root': 'foto', 'ending': '0'}], \
        [{'normalized_text': '.', 'clitic': '', 'lemma': '.', 'start': 61, 'end': 62, 'partofspeech': 'Z', 'form': '', 'root_tokens': ['.',], 'root': '.', 'ending': ''}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_email_addresses():
    # Tests that emails have postag 'H':
    # Initialize tagger
    morf_tagger = VabamorfTagger(postanalysis_tagger=PostMorphAnalysisTagger(fix_email_addresses=True))
    # Case 1
    text=Text('Kontakt: big@boss.com; http://www.big.boss.com')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Kontakt', 'partofspeech': 'S', 'form': 'sg n', 'ending': '0', 'lemma': 'kontakt', 'root_tokens': ['kontakt',], 'start': 0, 'clitic': '', 'end': 7, 'root': 'kontakt'}], \
        [{'normalized_text': ':', 'partofspeech': 'Z', 'form': '', 'ending': '', 'lemma': ':', 'root_tokens': [':',], 'start': 7, 'clitic': '', 'end': 8, 'root': ':'}], \
        [{'normalized_text': 'big@boss.com', 'partofspeech': 'H', 'form': '?', 'ending': '0', 'lemma': 'big@boss.com', 'root_tokens': ['big@boss.com',], 'start': 9, 'clitic': '', 'end': 21, 'root': 'big@boss.com'}], \
        [{'normalized_text': ';', 'partofspeech': 'Z', 'form': '', 'ending': '', 'lemma': ';', 'root_tokens': [';',], 'start': 21, 'clitic': '', 'end': 22, 'root': ';'}], \
        [{'normalized_text': 'http://www.big.boss.com', 'partofspeech': 'H', 'form': '?', 'ending': '0', 'lemma': 'http://www.big.boss.com', 'root_tokens': ['http://www.big.boss.com',], 'start': 23, 'clitic': '', 'end': 46, 'root': 'http://www.big.boss.com'}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_abbreviations():
    # Tests that abbreviations have postag 'Y':
    # Initialize tagger
    morf_tagger = VabamorfTagger(postanalysis_tagger=PostMorphAnalysisTagger(fix_abbreviations=True))
    # Case 1
    text=Text('( 9. jaan. 1939. a. või dets. - toim. )')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': '(', 'partofspeech': 'Z', 'root': '(', 'root_tokens': ['(',], 'ending': '', 'clitic': '', 'lemma': '(', 'form': '', 'end': 1, 'start': 0}], \
        [{'normalized_text': '9.', 'partofspeech': 'O', 'root': '9.', 'root_tokens': ['9.',], 'ending': '0', 'clitic': '', 'lemma': '9.', 'form': '?', 'end': 4, 'start': 2}], \
        [{'normalized_text': 'jaan.', 'partofspeech': 'Y', 'root': 'jaan', 'root_tokens': ['jaan',], 'ending': '0', 'clitic': '', 'lemma': 'jaan', 'form': '?', 'end': 10, 'start': 5}], \
        [{'normalized_text': '1939.', 'partofspeech': 'O', 'root': '1939.', 'root_tokens': ['1939.',], 'ending': '0', 'clitic': '', 'lemma': '1939.', 'form': '?', 'end': 16, 'start': 11}], \
        [{'normalized_text': 'a.', 'partofspeech': 'Y', 'root': 'a', 'root_tokens': ['a',], 'ending': '0', 'clitic': '', 'lemma': 'a', 'form': '?', 'end': 19, 'start': 17}], \
        [{'normalized_text': 'või', 'partofspeech': 'J', 'root': 'või', 'root_tokens': ['või',], 'ending': '0', 'clitic': '', 'lemma': 'või', 'form': '', 'end': 23, 'start': 20}], \
        [{'normalized_text': 'dets', 'partofspeech': 'Y', 'root': 'dets', 'root_tokens': ['dets',], 'ending': '0', 'clitic': '', 'lemma': 'dets', 'form': '?', 'end': 28, 'start': 24}], \
        [{'normalized_text': '.', 'partofspeech': 'Z', 'root': '.', 'root_tokens': ['.',], 'ending': '', 'clitic': '', 'lemma': '.', 'form': '', 'end': 29, 'start': 28}], \
        [{'normalized_text': '-', 'partofspeech': 'Z', 'root': '-', 'root_tokens': ['-',], 'ending': '', 'clitic': '', 'lemma': '-', 'form': '', 'end': 31, 'start': 30}], \
        [{'normalized_text': 'toim.', 'partofspeech': 'Y', 'root': 'toim', 'root_tokens': ['toim',], 'ending': '0', 'clitic': '', 'lemma': 'toim', 'form': 'sg n', 'end': 37, 'start': 32}], \
        [{'normalized_text': ')', 'partofspeech': 'Z', 'root': ')', 'root_tokens': [')'], 'ending': '', 'clitic': '', 'lemma': ')', 'form': '', 'end': 39, 'start': 38}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_number_postags():
    # Tests that numerics and percentages will have postag 'N':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_number_postags=True) )
    # Case 1 : percentages
    text=Text('kahanenud 4,7% -lt 1,8% -ni')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'kahanenud', 'ending': '0', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ['kahanenud',], 'start': 0, 'partofspeech': 'A', 'form': '', 'clitic': '', 'end': 9}, \
         {'normalized_text': 'kahanenud', 'ending': '0', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ['kahanenud',], 'start': 0, 'partofspeech': 'A', 'form': 'sg n', 'clitic': '', 'end': 9}, \
         {'normalized_text': 'kahanenud', 'ending': 'd', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ['kahanenud',], 'start': 0, 'partofspeech': 'A', 'form': 'pl n', 'clitic': '', 'end': 9}, \
         {'normalized_text': 'kahanenud', 'ending': 'nud', 'lemma': 'kahanema', 'root': 'kahane', 'root_tokens': ['kahane',], 'start': 0, 'partofspeech': 'V', 'form': 'nud', 'clitic': '', 'end': 9}], \
        [{'normalized_text': '4,7%-lt', 'ending': 'lt', 'lemma': '4,7%', 'root': '4,7%', 'root_tokens': ['4,7%',], 'start': 10, 'partofspeech': 'N', 'form': 'sg abl', 'clitic': '', 'end': 18}], \
        [{'normalized_text': '1,8%-ni', 'ending': 'ni', 'lemma': '1,8%', 'root': '1,8%', 'root_tokens': ['1,8%',], 'start': 19, 'partofspeech': 'N', 'form': 'sg ter', 'clitic': '', 'end': 27}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2 : numerics
    text=Text('10-te km kaupa liiva umbes 0-iga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [
        [{'normalized_text': '10-te', 'partofspeech': 'N', 'start': 0, 'lemma': '10', 'root_tokens': ['10',], 'ending': 'te', 'root': '10', 'end': 5, 'clitic': '', 'form': 'pl g'}],  \
        [{'normalized_text': 'km', 'partofspeech': 'Y', 'start': 6, 'lemma': 'km', 'root_tokens': ['km',], 'ending': '0', 'root': 'km', 'end': 8, 'clitic': '', 'form': '?'}], \
        [{'normalized_text': 'kaupa', 'partofspeech': 'K', 'start': 9, 'lemma': 'kaupa', 'root_tokens': ['kaupa',], 'ending': '0', 'root': 'kaupa', 'end': 14, 'clitic': '', 'form': ''}], \
        [{'normalized_text': 'liiva', 'partofspeech': 'S', 'start': 15, 'lemma': 'liiv', 'root_tokens': ['liiv',], 'ending': '0', 'root': 'liiv', 'end': 20, 'clitic': '', 'form': 'sg p'}], \
        [{'normalized_text': 'umbes', 'partofspeech': 'D', 'start': 21, 'lemma': 'umbes', 'root_tokens': ['umbes',], 'ending': '0', 'root': 'umbes', 'end': 26, 'clitic': '', 'form': ''}], \
        [{'normalized_text': '0-iga', 'partofspeech': 'N', 'start': 27, 'lemma': '0', 'root_tokens': ['0',], 'ending': 'ga', 'root': '0', 'end': 32, 'clitic': '', 'form': 'sg kom'}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    # TODO: this is test case currently broken: the disambiguator picks wrong analysis for the first word
    #assert expected_records == results_dict

    # Case 3 : numerics
    text=Text('Sai 112-e helistatud, kuna 1-ed ja 2-ed on ju nii lähestikku')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [
        [{'normalized_text': 'Sai', 'partofspeech': 'V', 'form': 's', 'lemma': 'saama', 'root_tokens': ['saa',], 'clitic': '', 'root': 'saa', 'end': 3, 'start': 0, 'ending': 'i'}],
        # Following is problematic: 
        #   the correct form should be 'sg p', but then again, the 
        #   surface form '112-e' is also misleading, can be easily 
        #   interpreted as 'sg g'
        [{'normalized_text': '112-e', 'partofspeech': 'N', 'form': 'sg g', 'lemma': '112', 'root_tokens': ['112',], 'clitic': '', 'root': '112', 'end': 9, 'start': 4, 'ending': '0'}],
        [{'normalized_text': 'helistatud', 'partofspeech': 'A', 'form': '', 'lemma': 'helistatud', 'root_tokens': ['helistatud',], 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': '0'},
         {'normalized_text': 'helistatud', 'partofspeech': 'A', 'form': 'sg n', 'lemma': 'helistatud', 'root_tokens': ['helistatud',], 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': '0'},
         {'normalized_text': 'helistatud', 'partofspeech': 'A', 'form': 'pl n', 'lemma': 'helistatud', 'root_tokens': ['helistatud',], 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': 'd'},
         {'normalized_text': 'helistatud', 'partofspeech': 'V', 'form': 'tud', 'lemma': 'helistama', 'root_tokens': ['helista',], 'clitic': '', 'root': 'helista', 'end': 20, 'start': 10, 'ending': 'tud'}],
        [{'normalized_text': ',', 'partofspeech': 'Z', 'form': '', 'lemma': ',', 'root_tokens': [',',], 'clitic': '', 'root': ',', 'end': 21, 'start': 20, 'ending': ''}],
        [{'normalized_text': 'kuna', 'partofspeech': 'J', 'ending': '0', 'root_tokens': ['kuna',], 'end': 26, 'lemma': 'kuna', 'start': 22, 'root': 'kuna', 'form': '', 'clitic': ''}],
        [{'normalized_text': '1-ed', 'partofspeech': 'N', 'ending': 'd', 'root_tokens': ['1',], 'end': 31, 'lemma': '1', 'start': 27, 'root': '1', 'form': 'pl n', 'clitic': ''}],
        [{'normalized_text': 'ja', 'partofspeech': 'J', 'ending': '0', 'root_tokens': ['ja',], 'end': 34, 'lemma': 'ja', 'start': 32, 'root': 'ja', 'form': '', 'clitic': ''}],
        [{'normalized_text': '2-ed', 'partofspeech': 'N', 'ending': 'd', 'root_tokens': ['2',], 'end': 39, 'lemma': '2', 'start': 35, 'root': '2', 'form': 'pl n', 'clitic': ''}],
        [{'normalized_text': 'on', 'partofspeech': 'V', 'ending': '0', 'root_tokens': ['ole',], 'end': 42, 'lemma': 'olema', 'start': 40, 'root': 'ole', 'form': 'b', 'clitic': ''},
         {'normalized_text': 'on','partofspeech': 'V', 'ending': '0', 'root_tokens': ['ole',], 'end': 42, 'lemma': 'olema', 'start': 40, 'root': 'ole', 'form': 'vad', 'clitic': ''}],
        [{'normalized_text': 'ju','partofspeech': 'D', 'ending': '0', 'root_tokens': ['ju',], 'end': 45, 'lemma': 'ju', 'start': 43, 'root': 'ju', 'form': '', 'clitic': ''}],
        [{'normalized_text': 'nii','partofspeech': 'D', 'ending': '0', 'root_tokens': ['nii',], 'end': 49, 'lemma': 'nii', 'start': 46, 'root': 'nii', 'form': '', 'clitic': ''}],
        [{'normalized_text': 'lähestikku','partofspeech': 'D', 'ending': '0', 'root_tokens': ['lähestikku',], 'end': 60, 'lemma': 'lähestikku', 'start': 50, 'root': 'lähestikku', 'form': '', 'clitic': ''}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results

    assert expected_records == results_dict

# ----------------------------------

def test_applying_postanalysis_twice():
    postanalysis_tagger = PostMorphAnalysisTagger()
    morf_tagger = VabamorfTagger(disambiguate=False, postanalysis_tagger=None)
    text=Text('Raamatu toim. J. K. Köstrimäe')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    # retag post analysis first time
    postanalysis_tagger.retag(text)
    # retag post analysis second time
    postanalysis_tagger.retag(text)
    # check results:
    expected_result = create_amb_attribute_list([[['Raamat', '0', 'H', 'sg g'], ['raamat', '0', 'S', 'sg g']], 
                                                 [['toim', '0', 'Y', 'sg n']], 
                                                 [['J. _K. _Köstri_mägi', '0', 'H', 'sg g']]], 
                                                 ('root','ending','partofspeech','form') )
    assert expected_result == text.morph_analysis['root','ending','partofspeech','form']

# ----------------------------------

def test_postanalysis_preserves_extra_attributes():
    # Tests that extra attributes added to the 'morph_analysis'
    # layer will be preserved through the PostMorphAnalysis
    text=Text('Pulli tahad vähemalt 10e eest? Siis helista big@boss.com')
    text.tag_layer(['words','sentences'])
    analyzer = VabamorfAnalyzer(extra_attributes=['analysis_id', 'sentence_id'])
    analyzer.tag(text)
    # Sort morph analysis annotations
    # ( so the order will be independent of the ordering used by 
    #   VabamorfAnalyzer & VabamorfDisambiguator )
    for morph_word in text['morph_analysis']:
        annotations = morph_word.annotations
        sorted_annotations = sorted( annotations, key = lambda x : \
               str(x['root'])+str(x['ending'])+str(x['clitic'])+\
               str(x['partofspeech'])+str(x['form']) )
        morph_word.clear_annotations()
        for annotation in sorted_annotations:
            morph_word.add_annotation( Annotation(morph_word, **annotation) )
    # Add extra attributes
    for sp_id, span in enumerate(text.morph_analysis):
        for a_id, annotation in enumerate( span.annotations ):
            setattr(annotation, 'analysis_id', str(sp_id)+'_'+str(a_id))
    for sent_id, sentence in enumerate(text.sentences):
        for sp_id, span in enumerate(text.morph_analysis):
            if sentence.start <= span.start and \
               span.end <= sentence.end:
                for a_id, annotation in enumerate( span.annotations ):
                    setattr(annotation, 'sentence_id', str(sent_id))
    postanalysis_tagger = PostMorphAnalysisTagger()
    # make post analysis corrections
    postanalysis_tagger.retag(text)
    #print(text.morph_analysis['root','partofspeech','analysis_id','sentence_id',])
    # Check that extra attributes are preserved
    expected_result = create_amb_attribute_list([[['Pull', 'H', '0_0', '0'], ['Pull', 'H', '0_1', '0'], \
                                                 ['Pull', 'H', '0_2', '0'], ['Pulli', 'H', '0_3', '0'], \
                                                 ['Pulli', 'H', '0_4', '0'], ['pull', 'A', '0_5', '0'], \
                                                 ['pull', 'A', '0_6', '0'], ['pull', 'A', '0_7', '0'], \
                                                 ['pull', 'S', '0_8', '0'], ['pull', 'S', '0_9', '0'], \
                                                 ['pull', 'S', '0_10', '0'], ['pulli', 'V', '0_11', '0']], \
                                                 [['taht', 'V', '1_0', '0']], [['vähemalt', 'D', '2_0', '0'], \
                                                 ['vähem', 'C', '2_1', '0']], [['10', 'N', '3_0', '0']], \
                                                 [['eest', 'D', '4_0', '0'], ['eest', 'K', '4_1', '0'], \
                                                 ['esi', 'S', '4_2', '0']], [['?', 'Z', '5_0', '0']], \
                                                 [['siis', 'D', '6_0', '1'], ['siis', 'J', '6_1', '1']], \
                                                 [['helista', 'V', '7_0', '1']], [['big@boss.com', 'H', '8_0', '1']]],
                                                 ('root','partofspeech','analysis_id','sentence_id') )
    assert expected_result == text.morph_analysis['root','partofspeech','analysis_id','sentence_id']

# ----------------------------------


def test_postanalysis_fix_number_analyses_using_rules():
    # Tests fix_number_analyses_using_rules 
    # (this was previously VabamorfCorrectionRewriter's functionality)
    # Initialize taggers
    postanalysis_tagger = \
        PostMorphAnalysisTagger(fix_number_analyses_using_rules = True, 
                                fix_number_analyses_by_replacing = True)
    morf_tagger = \
        VabamorfTagger(postanalysis_tagger=postanalysis_tagger)
    # Case 1
    text=Text('Tiit müüs 10e krooniga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [ \
        [{'normalized_text': 'Tiit', 'start': 0, 'lemma': 'Tiit', 'ending': '0', 'form': 'sg n', 'root': 'Tiit', 'partofspeech': 'H', 'clitic': '', 'root_tokens': ['Tiit',], 'end': 4}], \
        [{'normalized_text': 'müüs', 'start': 5, 'lemma': 'müüma', 'ending': 's', 'form': 's', 'root': 'müü', 'partofspeech': 'V', 'clitic': '', 'root_tokens': ['müü',], 'end': 9}], \
        [{'normalized_text': '10e', 'start': 10, 'lemma': '10', 'ending': '0', 'form': 'sg g', 'root': '10', 'partofspeech': 'N', 'clitic': '', 'root_tokens': ['10',], 'end': 13}], \
        [{'normalized_text': 'krooniga', 'start': 14, 'lemma': 'kroon', 'ending': 'ga', 'form': 'sg kom', 'root': 'kroon', 'partofspeech': 'S', 'clitic': '', 'root_tokens': ['kroon',], 'end': 22}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2
    text=Text('Tiit ei maksnud 6t krooni, vaid ostis 3ga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    expected_records = [
        [{'normalized_text': 'Tiit', 'clitic': '', 'root': 'Tiit', 'lemma': 'Tiit', 'end': 4, 'form': 'sg n', 'partofspeech': 'H', 'start': 0, 'ending': '0', 'root_tokens': ['Tiit',]}],
        [{'normalized_text': 'ei', 'clitic': '', 'root': 'ei', 'lemma': 'ei', 'end': 7, 'form': 'neg', 'partofspeech': 'V', 'start': 5, 'ending': '0', 'root_tokens': ['ei',]}],
        [{'normalized_text': 'maksnud', 'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': '', 'partofspeech': 'A', 'start': 8, 'ending': '0', 'root_tokens': ['maksnud',]},
         {'normalized_text': 'maksnud', 'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': 'sg n', 'partofspeech': 'A', 'start': 8, 'ending': '0', 'root_tokens': ['maksnud',]},
         {'normalized_text': 'maksnud', 'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': 'pl n', 'partofspeech': 'A', 'start': 8, 'ending': 'd', 'root_tokens': ['maksnud',]},
         {'normalized_text': 'maksnud', 'clitic': '', 'root': 'maks', 'lemma': 'maksma', 'end': 15, 'form': 'nud', 'partofspeech': 'V', 'start': 8, 'ending': 'nud', 'root_tokens': ['maks',]}],
        [{'normalized_text': '6t', 'clitic': '', 'root': '6', 'lemma': '6', 'end': 18, 'form': 'sg p', 'partofspeech': 'N', 'start': 16, 'ending': 't', 'root_tokens': ['6',]}],
        [{'normalized_text': 'krooni', 'clitic': '', 'root': 'kroon', 'lemma': 'kroon', 'end': 25, 'form': 'sg p', 'partofspeech': 'S', 'start': 19, 'ending': '0', 'root_tokens': ['kroon',]}],
        [{'normalized_text': ',', 'clitic': '', 'root': ',', 'lemma': ',', 'end': 26, 'form': '', 'partofspeech': 'Z', 'start': 25, 'ending': '', 'root_tokens': [',',]}],
        [{'normalized_text': 'vaid', 'clitic': '', 'root': 'vaid', 'lemma': 'vaid', 'end': 31, 'form': '', 'partofspeech': 'J', 'start': 27, 'ending': '0', 'root_tokens': ['vaid',]}],
        [{'normalized_text': 'ostis', 'clitic': '', 'root': 'ost', 'lemma': 'ostma', 'end': 37, 'form': 's', 'partofspeech': 'V', 'start': 32, 'ending': 'is', 'root_tokens': ['ost',]}],
        [{'normalized_text': '3ga', 'clitic': '', 'root': '3', 'lemma': '3', 'end': 41, 'form': 'sg kom', 'partofspeech': 'N', 'start': 38, 'ending': 'ga', 'root_tokens': ['3',]}]]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict



def test_postanalysis_fix_number_analyses_using_rules_postcorrections():
    # Tests some post-corrections to fix_number_analyses_using_rules 
    # Initialize taggers
    postanalysis_tagger = \
        PostMorphAnalysisTagger(fix_number_analyses_using_rules = True, 
                                fix_number_analyses_by_replacing = True)
    morf_tagger = \
        VabamorfTagger(postanalysis_tagger=postanalysis_tagger)
    tokenizer = WhiteSpaceTokensTagger()
    # Case 1: hyphens after and before numbers should be preserved in lemma
    text=Text('4- ja 6-silindriline, -10 kraadi')
    tokenizer.tag(text)
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print( layer_to_records(text['morph_analysis']) )
    #from pprint import pprint
    #pprint( layer_to_records(text['morph_analysis']) )
    expected_records = [ \
       [{'normalized_text': '4-', 'form': '?', 'root': '4-', 'root_tokens': ['4', ''], 'start': 0, 'lemma': '4-', 'clitic': '', 'ending': '0', 'end': 2, 'partofspeech': 'N'}], \
       [{'normalized_text': 'ja', 'form': '', 'root': 'ja', 'root_tokens': ['ja',], 'start': 3, 'lemma': 'ja', 'clitic': '', 'ending': '0', 'end': 5, 'partofspeech': 'J'}], \
       [{'normalized_text': '6-silindriline,', 'form': 'sg n', 'root': '6_silindriline', 'root_tokens': ['6', 'silindriline'], 'start': 6, 'lemma': '6silindriline', 'clitic': '', 'ending': '0', 'end': 21, 'partofspeech': 'A'}], \
       [{'normalized_text': '-10', 'form': '?', 'root': '-10', 'root_tokens': ['', '10'], 'start': 22, 'lemma': '-10', 'clitic': '', 'ending': '0', 'end': 25, 'partofspeech': 'N'}], \
       [{'normalized_text': 'kraadi', 'form': 'sg p', 'root': 'kraad', 'root_tokens': ['kraad',], 'start': 26, 'lemma': 'kraad', 'clitic': '', 'ending': '0', 'end': 32, 'partofspeech': 'S'}]
    ]
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict



def test_postanalysis_fix_pronouns_WIP():
    # Tests remove_broken_pronoun_analyses
    # (this was previously VabamorfCorrectionRewriter's functionality)
    # Basically: removes pronoun analyses from words in which the normalized word 
    #   form cannot be analysed as a pronoun;
    # TODO: currently, the side effect is that if the wrongly annotated word does 
    #       not have any other analyses (other than pronoun ones), it will have an 
    #       empty list of analyses, and as a result, the text cannot be disambiguated 
    #       automatically anymore ...
    #       Future work: removals should go hand-in-hand with adding new fixed analyses
    # Initialize taggers
    postanalysis_tagger = \
        PostMorphAnalysisTagger(fix_number_analyses_using_rules = True, 
                                fix_number_analyses_by_replacing = True, 
                                remove_broken_pronoun_analyses = True )
    morf_tagger = \
        VabamorfTagger(postanalysis_tagger=postanalysis_tagger, disambiguate=False)
    # Case 1
    text=Text(' 11-endal , 22-selt , 7-meid , 80selt . ')
    #
    #   For more analysis examples, see:
    #   https://github.com/estnltk/koondkorpus-experiments/blob/master/results/pronoun_tagger/detected_pronouns_01.csv
    #
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(layer_to_records(text['morph_analysis']))
    #from pprint import pprint
    #pprint(layer_to_records(text['morph_analysis']))
    expected_records = [ \
         [{'normalized_text': '11-endal', 'end': 9, 'root': None, 'start': 1, 'form': None, '_ignore': False, 'root_tokens': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'ending': None}], 
         [{'normalized_text': ',', 'end': 11, 'root': ',', 'start': 10, 'form': '', '_ignore': False, 'root_tokens': [',',], 'partofspeech': 'Z', 'clitic': '', 'lemma': ',', 'ending': ''}], 
         [{'normalized_text': '22-selt', 'end': 19, 'root': None, 'start': 12, 'form': None, '_ignore': False, 'root_tokens': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'ending': None}], 
         [{'normalized_text': ',', 'end': 21, 'root': ',', 'start': 20, 'form': '', '_ignore': False, 'root_tokens': [',',], 'partofspeech': 'Z', 'clitic': '', 'lemma': ',', 'ending': ''}], 
         [{'normalized_text': '7-meid', 'end': 28, 'root': None, 'start': 22, 'form': None, '_ignore': False, 'root_tokens': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'ending': None}], 
         [{'normalized_text': ',', 'end': 30, 'root': ',', 'start': 29, 'form': '', '_ignore': False, 'root_tokens': [',',], 'partofspeech': 'Z', 'clitic': '', 'lemma': ',', 'ending': ''}], 
         [{'normalized_text': '80selt', 'end': 37, 'root': None, 'start': 31, 'form': None, '_ignore': False, 'root_tokens': None, 'partofspeech': None, 'clitic': None, 'lemma': None, 'ending': None}], 
         [{'normalized_text': '.', 'end': 39, 'root': '.', 'start': 38, 'form': '', '_ignore': False, 'root_tokens': ['.',], 'partofspeech': 'Z', 'clitic': '', 'lemma': '.', 'ending': ''}] 
    ]
    results_dict = layer_to_records(text['morph_analysis'])
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict