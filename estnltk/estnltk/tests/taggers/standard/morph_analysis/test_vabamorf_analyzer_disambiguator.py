import pytest

from estnltk import Text
from estnltk import Annotation
from estnltk.taggers.standard.morph_analysis.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.standard.morph_analysis.morf import IGNORE_ATTR
from estnltk.converters import dict_to_layer
from estnltk.converters import layer_to_records

from estnltk_core.tests import create_amb_attribute_list

# ----------------------------------
#   Helper functions
# ----------------------------------


def _ignore_morph_analyses_overlapping_with_compound_tokens(
                                            text: Text,
                                            ignore_compound_tokens: list):
    """Finds all morph_analyses overlapping with compound tokens which
       types are listed in ignore_compound_tokens, and marks these as to
       be ignored during the morphological disambiguation. Returns a 
       dict containing locations (start, end) of spans that were ignored.

    """
    assert 'morph_analysis' in text.layers, \
        '(!) Text needs to be morphologically analysed!'
    mark_ignore = {}
    for span in text.morph_analysis:
        pos_key = (span.start, span.end)
        for ctid, comp_token in enumerate( text['compound_tokens'] ):
            ct_type_matches = \
                [ct_type in comp_token.type for ct_type in ignore_compound_tokens]
            if span.start==comp_token.start and \
               span.end==comp_token.end and \
               any(ct_type_matches):
                # Record location and content of morph analysis 
                # matching the compound token
                mark_ignore[pos_key] = span
        for annotation in span.annotations:
            if pos_key in mark_ignore:
                setattr(annotation, IGNORE_ATTR, True)
            else:
                setattr(annotation, IGNORE_ATTR, False)
    return mark_ignore


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
#   Initializations
# ----------------------------------

# Initialize analyser(s) & disambiguator
analyzer1     = VabamorfAnalyzer(extra_attributes=[IGNORE_ATTR])
analyzer2     = VabamorfAnalyzer()
disambiguator = VabamorfDisambiguator()

# ----------------------------------
#   Test 
#      morphological analyser
# ----------------------------------

def test_morph_analyzer_1():
    text=Text('Mitmenda koha sai kohale jõudnud mees ?')
    text.tag_layer(['words','sentences'])
    analyzer2.tag(text)
    expected_records = [
        [{'normalized_text': 'Mitmenda', 'partofspeech': 'P', 'start': 0, 'ending': '0', 'form': 'sg g', 'root': 'mitmes', 'end': 8, 'clitic': '', 'root_tokens': ['mitmes',], 'lemma': 'mitmes'}],
        [{'normalized_text': 'koha', 'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg g', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ['koha',], 'lemma': 'koha'},
         {'normalized_text': 'koha', 'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg n', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ['koha',], 'lemma': 'koha'},
         {'normalized_text': 'koha', 'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg p', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ['koha',], 'lemma': 'koha'},
         {'normalized_text': 'koha', 'partofspeech': 'V', 'start': 9, 'ending': '0', 'form': 'o', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ['koha',], 'lemma': 'kohama'},
         {'normalized_text': 'koha', 'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg g', 'root': 'koht', 'end': 13, 'clitic': '', 'root_tokens': ['koht',], 'lemma': 'koht'}],
        [{'normalized_text': 'sai', 'partofspeech': 'S', 'start': 14, 'ending': '0', 'form': 'sg n', 'root': 'sai', 'end': 17, 'clitic': '', 'root_tokens': ['sai',], 'lemma': 'sai'},
         {'normalized_text': 'sai', 'partofspeech': 'V', 'start': 14, 'ending': 'i', 'form': 's', 'root': 'saa', 'end': 17, 'clitic': '', 'root_tokens': ['saa',], 'lemma': 'saama'}],
        [{'normalized_text': 'kohale', 'partofspeech': 'D', 'start': 18, 'ending': '0', 'form': '', 'root': 'kohale', 'end': 24, 'clitic': '', 'root_tokens': ['kohale',], 'lemma': 'kohale'},
         {'normalized_text': 'kohale', 'partofspeech': 'K', 'start': 18, 'ending': '0', 'form': '', 'root': 'kohale', 'end': 24, 'clitic': '', 'root_tokens': ['kohale',], 'lemma': 'kohale'},
         {'normalized_text': 'kohale', 'partofspeech': 'S', 'start': 18, 'ending': 'le', 'form': 'sg all', 'root': 'koha', 'end': 24, 'clitic': '', 'root_tokens': ['koha',], 'lemma': 'koha'},
         {'normalized_text': 'kohale', 'partofspeech': 'S', 'start': 18, 'ending': 'le', 'form': 'sg all', 'root': 'koht', 'end': 24, 'clitic': '', 'root_tokens': ['koht',], 'lemma': 'koht'}],
        [{'normalized_text': 'jõudnud', 'partofspeech': 'A', 'start': 25, 'ending': '0', 'form': '', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ['jõudnud',], 'lemma': 'jõudnud'},
         {'normalized_text': 'jõudnud', 'partofspeech': 'A', 'start': 25, 'ending': '0', 'form': 'sg n', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ['jõudnud',], 'lemma': 'jõudnud'},
         {'normalized_text': 'jõudnud', 'partofspeech': 'S', 'start': 25, 'ending': 'd', 'form': 'pl n', 'root': 'jõud=nu', 'end': 32, 'clitic': '', 'root_tokens': ['jõudnu',], 'lemma': 'jõudnu'},
         {'normalized_text': 'jõudnud', 'partofspeech': 'A', 'start': 25, 'ending': 'd', 'form': 'pl n', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ['jõudnud',], 'lemma': 'jõudnud'},
         {'normalized_text': 'jõudnud', 'partofspeech': 'V', 'start': 25, 'ending': 'nud', 'form': 'nud', 'root': 'jõud', 'end': 32, 'clitic': '', 'root_tokens': ['jõud',], 'lemma': 'jõudma'}],
        [{'normalized_text': 'mees', 'partofspeech': 'S', 'start': 33, 'ending': '0', 'form': 'sg n', 'root': 'mees', 'end': 37, 'clitic': '', 'root_tokens': ['mees',], 'lemma': 'mees'},
         {'normalized_text': 'mees', 'partofspeech': 'S', 'start': 33, 'ending': 's', 'form': 'sg in', 'root': 'mesi', 'end': 37, 'clitic': '', 'root_tokens': ['mesi',], 'lemma': 'mesi'}],
        [{'normalized_text': '?', 'partofspeech': 'Z', 'start': 38, 'ending': '', 'form': '', 'root': '?', 'end': 39, 'clitic': '', 'root_tokens': ['?',], 'lemma': '?'}]]
    #print(layer_to_records(text['morph_analysis']))
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


# ----------------------------------
#   Test 
#      morphological analyser
#      with guessing switched off
# ----------------------------------

def test_morph_analyzer_without_guessing():
    # Tests that positions of unknown words will be filled with [None]
    analyzer2x = VabamorfAnalyzer(guess=False, propername=False)
    text=Text('Mulll on yks rõlgelt hea netikeelelause')
    text.tag_layer(['words','sentences'])
    analyzer2x.tag(text)
    
    # Check for unknown word placeholders
    assert ['Mulll', 'on', 'yks', 'rõlgelt', 'hea', 'netikeelelause'] == text.words.text
    assert create_amb_attribute_list([[None],
                                      ['ole', 'ole'], [None], ['rõlge', 'rõlge=lt'],
                                      ['hea', 'hea', 'hea', 'hea'],
                                      ['neti_keele_lause', 'neti_keele_lause']], 'root') == text.root

    # Test that zip can be used to discover unknown words
    unknown_words = []
    for word, partofspeech in zip(text.words.text, text.partofspeech):
        if partofspeech[0] is None:
            unknown_words.append(word)
    assert ['Mulll', 'yks'] == unknown_words



# ----------------------------------
#   Test 
#      morphological analyser
#      can analyse words with 
#      multiple normalized forms
# ----------------------------------

def test_morph_analyzer_with_multiple_normalized_forms():
    # Tests that morphological analyser can analyse words with multiple normalized forms
    analyzer2a = VabamorfAnalyzer()
    # Case 1: analyse with guessing
    text = Text('''isaand kui juuuubbeee ...''')
    text.tag_layer(['words', 'sentences'])
    # Add multiple normalized forms
    for word in text.words:
        if word.text == 'isaand':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['isand', 'issand']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='isand') )
                word.add_annotation( Annotation(word, normalized_form='issand') )
        if word.text == 'juuuubbeee':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['jube']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='jube') )
    # Tag morph analyses
    analyzer2a.tag(text)
    expected_records = \
         [ [{'normalized_text': 'isand', 'lemma': 'isand', 'end': 6, 'form': 'sg n', 'root_tokens': ['isand'], 'root': 'isand', 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'start': 0}, 
            {'normalized_text': 'issand', 'lemma': 'issand', 'end': 6, 'form': '', 'root_tokens': ['issand'], 'root': 'issand', 'ending': '0', 'clitic': '', 'partofspeech': 'I', 'start': 0}, 
            {'normalized_text': 'issand', 'lemma': 'issand', 'end': 6, 'form': 'sg n', 'root_tokens': ['issand'], 'root': 'issand', 'ending': '0', 'clitic': '', 'partofspeech': 'S', 'start': 0}], 
           [{'normalized_text': 'kui', 'lemma': 'kui', 'end': 10, 'form': '', 'root_tokens': ['kui'], 'root': 'kui', 'ending': '0', 'clitic': '', 'partofspeech': 'D', 'start': 7}, 
            {'normalized_text': 'kui', 'lemma': 'kui', 'end': 10, 'form': '', 'root_tokens': ['kui'], 'root': 'kui', 'ending': '0', 'clitic': '', 'partofspeech': 'J', 'start': 7}], 
           [{'normalized_text': 'jube', 'lemma': 'jube', 'end': 21, 'form': 'sg n', 'root_tokens': ['jube'], 'root': 'jube', 'ending': '0', 'clitic': '', 'partofspeech': 'A', 'start': 11}, 
            {'normalized_text': 'jube', 'lemma': 'jube', 'end': 21, 'form': '', 'root_tokens': ['jube'], 'root': 'jube', 'ending': '0', 'clitic': '', 'partofspeech': 'D', 'start': 11}], 
           [{'normalized_text': '...', 'lemma': '...', 'end': 25, 'form': '', 'root_tokens': ['...'], 'root': '...', 'ending': '', 'clitic': '', 'partofspeech': 'Z', 'start': 22}]
         ]
    #print(layer_to_records(text['morph_analysis']))
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2: analyse without guessing
    analyzer2b = VabamorfAnalyzer(guess=False, propername=False)
    text = Text('''päris hää !''')
    text.tag_layer(['words', 'sentences'])
    # Add multiple normalized forms (and one of them will remain an unknown word)
    for word in text.words:
        if word.text == 'hää':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['hea', 'hää', 'head']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='hea') )
                word.add_annotation( Annotation(word, normalized_form='hää') )
                word.add_annotation( Annotation(word, normalized_form='head') )
    analyzer2b.tag(text)
    expected_records = \
        [
          [{'normalized_text': 'päris', 'clitic': '', 'partofspeech': 'A', 'lemma': 'päris', 'root_tokens': ['päris'], 'ending': '0', 'end': 5, 'form': '', 'root': 'päris', 'start': 0}, 
           {'normalized_text': 'päris', 'clitic': '', 'partofspeech': 'D', 'lemma': 'päris', 'root_tokens': ['päris'], 'ending': '0', 'end': 5, 'form': '', 'root': 'päris', 'start': 0}, 
           {'normalized_text': 'päris', 'clitic': '', 'partofspeech': 'V', 'lemma': 'pärima', 'root_tokens': ['päri'], 'ending': 's', 'end': 5, 'form': 's', 'root': 'päri', 'start': 0}], 
          [{'normalized_text': 'hea', 'clitic': '', 'partofspeech': 'A', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': '0', 'end': 9, 'form': 'sg g', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'hea', 'clitic': '', 'partofspeech': 'A', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': '0', 'end': 9, 'form': 'sg n', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'hea', 'clitic': '', 'partofspeech': 'S', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': '0', 'end': 9, 'form': 'sg g', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'hea', 'clitic': '', 'partofspeech': 'S', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': '0', 'end': 9, 'form': 'sg n', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'head', 'clitic': '', 'partofspeech': 'A', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': 'd', 'end': 9, 'form': 'pl n', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'head', 'clitic': '', 'partofspeech': 'A', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': 'd', 'end': 9, 'form': 'sg p', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'head', 'clitic': '', 'partofspeech': 'S', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': 'd', 'end': 9, 'form': 'pl n', 'root': 'hea', 'start': 6}, 
           {'normalized_text': 'head', 'clitic': '', 'partofspeech': 'S', 'lemma': 'hea', 'root_tokens': ['hea'], 'ending': 'd', 'end': 9, 'form': 'sg p', 'root': 'hea', 'start': 6}], 
          [{'normalized_text':  None, 'root_tokens': None, 'clitic': None, 'lemma': None, 'root': None, 'ending': None, 'end': 11, 'partofspeech': None, 'form': None, 'start': 10}] ]
    #print(layer_to_records(text['morph_analysis']))
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict



# ----------------------------------
#   Test 
#      morphological disambiguator
# ----------------------------------

def test_morph_disambiguator_1():
    text=Text('Mitmenda koha sai kohale jõudnud mees ?')
    text.tag_layer(['words','sentences'])
    analyzer2.tag(text)
    disambiguator.retag(text)
    expected_records = [ \
        [{'normalized_text': 'Mitmenda', 'ending': '0', 'root': 'mitmes', 'root_tokens': ['mitmes',], 'start': 0, 'end': 8, 'clitic': '', 'partofspeech': 'P', 'lemma': 'mitmes', 'form': 'sg g'}], \
        [{'normalized_text': 'koha', 'ending': '0', 'root': 'koha', 'root_tokens': ['koha',], 'start': 9, 'end': 13, 'clitic': '', 'partofspeech': 'S', 'lemma': 'koha', 'form': 'sg g'}, \
         {'normalized_text': 'koha', 'ending': '0', 'root': 'koht', 'root_tokens': ['koht',], 'start': 9, 'end': 13, 'clitic': '', 'partofspeech': 'S', 'lemma': 'koht', 'form': 'sg g'}], \
        [{'normalized_text': 'sai', 'ending': 'i', 'root': 'saa', 'root_tokens': ['saa',], 'start': 14, 'end': 17, 'clitic': '', 'partofspeech': 'V', 'lemma': 'saama', 'form': 's'}], \
        [{'normalized_text': 'kohale', 'ending': '0', 'root': 'kohale', 'root_tokens': ['kohale',], 'start': 18, 'end': 24, 'clitic': '', 'partofspeech': 'D', 'lemma': 'kohale', 'form': ''}], \
        [{'normalized_text': 'jõudnud', 'ending': 'nud', 'root': 'jõud', 'root_tokens': ['jõud',], 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'V', 'lemma': 'jõudma', 'form': 'nud'}, \
         {'normalized_text': 'jõudnud', 'ending': '0', 'root': 'jõud=nud', 'root_tokens': ['jõudnud',], 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': ''}, \
         {'normalized_text': 'jõudnud', 'ending': '0', 'root': 'jõud=nud', 'root_tokens': ['jõudnud',], 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': 'sg n'}, \
         {'normalized_text': 'jõudnud', 'ending': 'd', 'root': 'jõud=nud', 'root_tokens': ['jõudnud',], 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': 'pl n'}], \
        [{'normalized_text': 'mees', 'ending': '0', 'root': 'mees', 'root_tokens': ['mees',], 'start': 33, 'end': 37, 'clitic': '', 'partofspeech': 'S', 'lemma': 'mees', 'form': 'sg n'}], \
        [{'normalized_text': '?', 'ending': '', 'root': '?', 'root_tokens': ['?',], 'start': 38, 'end': 39, 'clitic': '', 'partofspeech': 'Z', 'lemma': '?', 'form': ''}]]
    #print(layer_to_records(text['morph_analysis']))
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

# ----------------------------------
#   Test
#     that  disambiguator  throws 
#     an exception iff some words 
#     do not have analyses 
# ----------------------------------

def test_morph_disambiguation_exception_on_unknown_words():
    analyzer2x = VabamorfAnalyzer(guess=False, propername=False)
    text=Text('Mulll on yks rõlgelt hea netikeelelause')
    text.tag_layer(['words','sentences'])
    analyzer2x.tag(text)
    
    # Check for unknown word placeholders
    assert ['Mulll', 'on', 'yks', 'rõlgelt', 'hea', 'netikeelelause'] == text.words.text
    assert create_amb_attribute_list([[None],
                                      ['ole', 'ole'], [None], ['rõlge', 'rõlge=lt'],
                                      ['hea', 'hea', 'hea', 'hea'],
                                      ['neti_keele_lause', 'neti_keele_lause']], 'root') == text.root

    with pytest.raises(Exception) as e1:
        # Disambiguate text
        disambiguator.retag(text)
    #print(e1)
    # >>> (!) Unable to perform morphological disambiguation because words at positions [(0, 5), (9, 12), (13, 20)] have no morphological analyses.


# ----------------------------------
#   Test
#     that disambiguation preserves
#     extra attributes
# ----------------------------------


def test_morph_disambiguation_preserves_extra_attributes():
    text=Text('Mees kees üle. Naeris naeris.')
    text.tag_layer(['words','sentences'])
    analyzer = VabamorfAnalyzer(extra_attributes=['analysis_id', 'sentence_id'])
    analyzer.tag(text)
    # Add extra attributes
    for sp_id, spanlist in enumerate(text.morph_analysis):
        sorted_annotations = sorted( spanlist.annotations, key = lambda x : \
               str(x['root'])+str(x['ending'])+str(x['clitic'])+\
               str(x['partofspeech'])+str(x['form']) )
        for s_id, annotation in enumerate(sorted_annotations):
            setattr(annotation, 'analysis_id', str(sp_id)+'_'+str(s_id))
    for sent_id, sentence in enumerate(text.sentences):
        for sp_id, spanlist in enumerate(text.morph_analysis):
            if sentence.start <= spanlist.start and \
               spanlist.end <= sentence.end:
                sorted_annotations = sorted( spanlist.annotations, key = lambda x : \
                       str(x['root'])+str(x['ending'])+str(x['clitic'])+\
                       str(x['partofspeech'])+str(x['form']) )
                for s_id, annotation in enumerate( sorted_annotations ):
                    setattr(annotation, 'sentence_id', str(sent_id))
    # Disambiguate text
    disambiguator.retag(text)
    #print(layer_to_records(text['morph_analysis']))
    # Check that extra attributes are preserved
    expected_records = [
        [{'normalized_text': 'Mees', 'analysis_id': '0_3', 'clitic': '', 'root': 'mees', 'ending': '0', 'partofspeech': 'S', 'sentence_id': '0', 'start': 0, 'root_tokens': ['mees',], 'end': 4, 'form': 'sg n', 'lemma': 'mees'}],
        [{'normalized_text': 'kees', 'analysis_id': '1_1', 'clitic': '', 'root': 'kee', 'ending': 's', 'partofspeech': 'V', 'sentence_id': '0', 'start': 5, 'root_tokens': ['kee',], 'end': 9, 'form': 's', 'lemma': 'keema'}],
        [{'normalized_text': 'üle', 'analysis_id': '2_0', 'clitic': '', 'root': 'üle', 'ending': '0', 'partofspeech': 'D', 'sentence_id': '0', 'start': 10, 'root_tokens': ['üle',], 'end': 13, 'form': '', 'lemma': 'üle'}],
        [{'normalized_text': '.', 'analysis_id': '3_0', 'clitic': '', 'root': '.', 'ending': '', 'partofspeech': 'Z', 'sentence_id': '0', 'start': 13, 'root_tokens': ['.',], 'end': 14, 'form': '', 'lemma': '.'}],
        [{'normalized_text': 'Naeris', 'analysis_id': '4_4', 'clitic': '', 'root': 'naeris', 'ending': '0', 'partofspeech': 'S', 'sentence_id': '1', 'start': 15, 'root_tokens': ['naeris',], 'end': 21, 'form': 'sg n', 'lemma': 'naeris'}],
        [{'normalized_text': 'naeris', 'analysis_id': '5_1', 'clitic': '', 'root': 'naer', 'ending': 'is', 'partofspeech': 'V', 'sentence_id': '1', 'start': 22, 'root_tokens': ['naer',], 'end': 28, 'form': 's', 'lemma': 'naerma'}],
        [{'normalized_text': '.', 'analysis_id': '6_0', 'clitic': '', 'root': '.', 'ending': '', 'partofspeech': 'Z', 'sentence_id': '1', 'start': 28, 'root_tokens': ['.',], 'end': 29, 'form': '', 'lemma': '.'}] ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text['morph_analysis'] )
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


# ----------------------------------
#   Test 
#      disambiguation runs OK if 
#      multiple normalized forms 
#      are provided
# ----------------------------------

def test_morph_disambiguation_if_analysis_has_normalized_text_attribute():
    # Tests that morphological disambiguator works if morphological_analysis 
    # layer has 'normalized_text' attribute
    analyzer2a = VabamorfAnalyzer()
    # Case 1
    text = Text('''Mjees ppeeti knni.''')
    text.tag_layer(['words', 'sentences'])
    # Add multiple normalized forms for words
    for word in text.words:
        if word.text == 'Mjees':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['Mees', 'mees']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='Mees') )
                word.add_annotation( Annotation(word, normalized_form='mees') )
        if word.text == 'ppeeti':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['peeti']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='peeti') )
        if word.text == 'knni':
            if text.words.ambiguous == False:
                word.annotations[0].normalized_form = ['kinni']
            else:
                word.clear_annotations()
                word.add_annotation( Annotation(word, normalized_form='kinni') )
    analyzer2a.tag( text )
    disambiguator.retag( text )
    #from estnltk.converters import layer_to_dict
    #from pprint import pprint
    #pprint(layer_to_dict( text['morph_analysis'] ))
    expected_layer = \
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
                    'base_span': (0, 5)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'ti',
                                     'form': 'ti',
                                     'lemma': 'pidama',
                                     'normalized_text': 'peeti',
                                     'partofspeech': 'V',
                                     'root': 'pida',
                                     'root_tokens': ['pida']}],
                    'base_span': (6, 12)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'kinni',
                                     'normalized_text': 'kinni',
                                     'partofspeech': 'D',
                                     'root': 'kinni',
                                     'root_tokens': ['kinni']}],
                    'base_span': (13, 17)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (17, 18)}]}
    assert dict_to_layer( expected_layer ) == text['morph_analysis']



# ----------------------------------
#   Test 
#      disambiguation_with_ignore
# ----------------------------------

def test_morph_disambiguation_with_ignore():
    # Tests that morphological disambiguator can be set to ignore some words
    # Case 1 : test ignoring random words ( do not try this at home! )
    text = Text('Mitmenda koha sai kohale jõudnud mees ?')
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    mark_ignore = {(14,17): [],  # sai
                   (33,37): [],  # mees
                   }
    for amb_span in text.morph_analysis:
        pos_key = (amb_span.start, amb_span.end)
        if pos_key in mark_ignore:
            # Record the previous spanlist
            # (so that we can compare after disambiguation)
            mark_ignore[pos_key] = amb_span
        for span in amb_span.annotations:
            if pos_key in mark_ignore:
                setattr(span, IGNORE_ATTR, True)
            else:
                setattr(span, IGNORE_ATTR, False)
    disambiguator.retag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert IGNORE_ATTR not in text.morph_analysis.attributes
    # Check that marked spans remain the same in the new layer
    for amb_span in text.morph_analysis:
        pos_key = (amb_span.start, amb_span.end)
        if pos_key in mark_ignore:
            assert len(mark_ignore[pos_key].annotations) == len(amb_span.annotations)


def test_morph_disambiguation_with_ignore_all():
    # Test: if all words in the sentence are ignored,
    #       disambiguator won't raise any error
    text=Text('Mees peeti kinni') 
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    #print(layer_to_records(text['morph_analysis']))
    # Ignore all spans/words
    for spanlist in text.morph_analysis:
        for annotation in spanlist.annotations:
            setattr(annotation, IGNORE_ATTR, True)
    disambiguator.retag(text)
    #print(layer_to_records(text['morph_analysis']))
    # Assert that attribute IGNORE_ATTR has been removed 
    assert IGNORE_ATTR not in text.morph_analysis.attributes



def test_morph_disambiguation_with_ignore_emoticons():
    # Case 2 : test ignoring emoticons
    text = Text('Mõte on hea :-) Tuleme siis kolmeks :)')
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)
    # ignore emoticons
    mark_ignore = \
      _ignore_morph_analyses_overlapping_with_compound_tokens(text, ['emoticon'])
    disambiguator.retag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert IGNORE_ATTR not in text.morph_analysis.attributes
    # Check that marked spans remain the same in the new layer
    for amb_span in text.morph_analysis:
        pos_key = (amb_span.start, amb_span.end)
        if pos_key in mark_ignore:
            assert len(mark_ignore[pos_key].annotations) == len(amb_span.annotations)


def test_morph_disambiguation_with_ignore_xml_tags():
    # Case 1 : test ignoring xml tags inserted into text
    text=Text('Mees <b>peeti</b> kinni, aga ta <br> naeris <br> vaid!') 
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    # ignore xml_tags
    mark_ignore = \
      _ignore_morph_analyses_overlapping_with_compound_tokens(text, ['xml_tag'])
    #print(layer_to_records(text['morph_analysis']))
    disambiguator.retag(text)
    #print(layer_to_records(text['morph_analysis']))
    # Assert that attribute IGNORE_ATTR has been removed
    assert IGNORE_ATTR not in text.morph_analysis.attributes
    for span in text.morph_analysis:
        # assert that all words have been disambiguated
        assert len(span.annotations) == 1
        assert IGNORE_ATTR not in span.annotations[0]



# ----------------------------------------------------------------
#   Test 
#      morphological analyser and disambiguator will output 
#      ambiguous word's analyses in specific order
# ----------------------------------------------------------------

def test_ordering_of_ambiguous_morph_analyses():
    # Test the default ordering of ambiguous morph analyses
    text_str = '''
    Need olid ühed levinuimad rattad omal ajastul.
    Ma kusjuures ei olegi varem sinna kordagi sattunud.
    Hästi jutustatud ja korraliku ideega.
    Kuna peamine põhjus vähendada suitsugaaside kardinaid osatähtsus on vähenenud läbipääsu toru kogunenud tahm seintel.
    '''
    text=Text(text_str)
    text.tag_layer(['words','sentences'])
    analyzer2.tag(text)
    disambiguator.retag( text )
    # Collect ambiguous analyses
    ambiguous_analyses = []
    for morph_word in text.morph_analysis:
        annotations = morph_word.annotations
        #ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
        if len( annotations ) > 1:
            ambiguous_analyses.append( [morph_word.text]+[(a['root'], a['partofspeech'], a['form'] ) for a in annotations] )
    # ==============
    #print()
    #for a in ambiguous_analyses:
    #    print(a)
    # ==============
    #  ordering when VabamorfAnalyzer & VabamorfDisambiguator do not sort ambiguous analyses
    # ==============
    ordering_a = [ \
       ['ühed', ('üks', 'N', 'pl n'), ('üks', 'P', 'pl n')],
       ['sattunud', ('sattu', 'V', 'nud'), ('sattu=nud', 'A', ''), ('sattu=nud', 'A', 'sg n'), ('sattu=nud', 'A', 'pl n')],
       ['jutustatud', ('jutusta', 'V', 'tud'), ('jutusta=tud', 'A', ''), ('jutusta=tud', 'A', 'sg n'), ('jutusta=tud', 'A', 'pl n')],
       ['on', ('ole', 'V', 'b'), ('ole', 'V', 'vad')],
       ['vähenenud', ('vähene', 'V', 'nud'), ('vähene=nud', 'A', ''), ('vähene=nud', 'A', 'sg n'), ('vähene=nud', 'A', 'pl n')],
       ['kogunenud', ('kogune', 'V', 'nud'), ('kogune=nud', 'A', ''), ('kogune=nud', 'A', 'sg n'), ('kogune=nud', 'A', 'pl n')]
    ]
    # ==============
    #  validate the current ordering
    # ==============
    assert ordering_a == ambiguous_analyses


