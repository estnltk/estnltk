from estnltk import Text
from estnltk.taggers.morf import VabamorfTagger
from estnltk.taggers.postanalysis_tagger import PostMorphAnalysisTagger

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
            x['root']+x['ending']+x['clitic']+x['partofspeech']+x['form'] )
        morph_analysis_records[wrid] = sorted_records


def test_postanalysis_fix_names_with_initials():
    # Tests that names with initials (such as "T. S. Eliot") will have their:
    #    * partofspeech fixed to H;
    #    * root tokens normalized (contain underscores in proper places, and no lowercase name starts);
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_names_with_initials=True) )
    # Case 1
    text=Text('Romaan kinnitab üht T. S. Eliot´i ennustust.')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'clitic': '', 'lemma': 'romaan', 'ending': '0', 'partofspeech': 'S', 'form': 'sg n', 'root_tokens': ('romaan',), 'end': 6, 'root': 'romaan', 'start': 0}], \
        [{'clitic': '', 'lemma': 'kinnitama', 'ending': 'b', 'partofspeech': 'V', 'form': 'b', 'root_tokens': ('kinnita',), 'end': 15, 'root': 'kinnita', 'start': 7}], \
        [{'clitic': '', 'lemma': 'üks', 'ending': '0', 'partofspeech': 'N', 'form': 'sg p', 'root_tokens': ('üks',), 'end': 19, 'root': 'üks', 'start': 16}, \
         {'clitic': '', 'lemma': 'üks', 'ending': '0', 'partofspeech': 'P', 'form': 'sg p', 'root_tokens': ('üks',), 'end': 19, 'root': 'üks', 'start': 16}], \
        [{'root': 'T. _S. _Eliot', 'start': 20, 'form': 'sg g', 'root_tokens': ('T. ', 'S. ', 'Eliot'), 'clitic': '', 'partofspeech': 'H', 'lemma': 'T. S. Eliot', 'ending': '0', 'end': 33}],\
        [{'clitic': '', 'lemma': 'ennustus', 'ending': 't', 'partofspeech': 'S', 'form': 'sg p', 'root_tokens': ('ennustus',), 'end': 43, 'root': 'ennustus', 'start': 34}], \
        [{'clitic': '', 'lemma': '.', 'ending': '', 'partofspeech': 'Z', 'form': '', 'root_tokens': ('.',), 'end': 44, 'root': '.', 'start': 43}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2
    text=Text("Läände jõudis tualettpaber tänu Joseph C. Gayetty'le.")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'lemma': 'lääs', 'root': 'lääs', 'ending': 'de', 'root_tokens': ('lääs',), 'start': 0, 'end': 6, 'clitic': '', 'partofspeech': 'S', 'form': 'adt'}], \
        [{'lemma': 'jõudma', 'root': 'jõud', 'ending': 'is', 'root_tokens': ('jõud',), 'start': 7, 'end': 13, 'clitic': '', 'partofspeech': 'V', 'form': 's'}], \
        [{'lemma': 'tualettpaber', 'root': 'tualett_paber', 'ending': '0', 'root_tokens': ('tualett', 'paber'), 'start': 14, 'end': 26, 'clitic': '', 'partofspeech': 'S', 'form': 'sg n'}], \
        [{'lemma': 'tänu', 'root': 'tänu', 'ending': '0', 'root_tokens': ('tänu',), 'start': 27, 'end': 31, 'clitic': '', 'partofspeech': 'K', 'form': ''}], \
        [{'lemma': 'Joseph', 'root': 'Joseph', 'ending': '0', 'root_tokens': ('Joseph',), 'start': 32, 'end': 38, 'clitic': '', 'partofspeech': 'H', 'form': 'sg n'}], \
        [{'clitic': '', 'partofspeech': 'H', 'lemma': 'C. Gayetty', 'end': 52, 'ending': 'le', 'root_tokens': ('C. ', 'Gayetty'), 'root': 'C. _Gayetty', 'start': 39, 'form': 'sg all'}], \
        [{'lemma': '.', 'root': '.', 'ending': '', 'root_tokens': ('.',), 'start': 52, 'end': 53, 'clitic': '', 'partofspeech': 'Z', 'form': ''}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 3
    text=Text("Arhitektid E. Lüüs, E. Eharand ja T. Soans")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'start': 0, 'ending': 'd', 'root_tokens': ('arhitekt',), 'form': 'pl n', 'end': 10, 'lemma': 'arhitekt', 'root': 'arhitekt', 'clitic': '', 'partofspeech': 'S'}], \
        [{'root_tokens': ('E. ', 'Lüüs'), 'root': 'E. _Lüüs', 'clitic': '', 'partofspeech': 'H', 'lemma': 'E. Lüüs', 'start': 11, 'end': 18, 'form': 'sg n', 'ending': '0'}], \
        [{'root_tokens': (',',), 'root': ',', 'clitic': '', 'partofspeech': 'Z', 'lemma': ',', 'start': 18, 'end': 19, 'form': '', 'ending': ''}], \
        [{'root_tokens': ('E. ', 'Eha', 'rand'), 'root': 'E. _Eha_rand', 'clitic': '', 'partofspeech': 'H', 'lemma': 'E. Eharand', 'start': 20, 'end': 30, 'form': 'sg n', 'ending': '0'}], \
        [{'root_tokens': ('ja',), 'root': 'ja', 'clitic': '', 'partofspeech': 'J', 'lemma': 'ja', 'start': 31, 'end': 33, 'form': '', 'ending': '0'}], \
        [{'root_tokens': ('T. ', 'Soans'), 'root': 'T. _Soans', 'clitic': '', 'partofspeech': 'H', 'lemma': 'T. Soans', 'start': 34, 'end': 42, 'form': '?', 'ending': '0'}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
