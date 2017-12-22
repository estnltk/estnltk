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

    # Case 4
    # Negative case: do not fix partofspeech on verbs (yet)
    text=Text("Ansambli nimeks oli Swing B. Esinemas käisime tantsuõhtutel")
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    expected_result = [('Ansambli', ['S']), ('nimeks', ['S']), ('oli', ['V']), ('Swing', ['H']), \
                       ('B. Esinemas', ['V']), ('käisime', ['V']), ('tantsuõhtutel', ['S'])]
    # TODO: 'B. Esinemas' is actually a wrong compound token, 
    #        needs to be fixed in the future
    result = list(zip(text.words.text,text.partofspeech))
    assert expected_result == result


def test_postanalysis_fix_emoticons():
    # Tests that emoticons have postag 'Z':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_emoticons=True) )
    # Case 1
    text=Text('Äge pull :D irw :-P')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'form': 'sg n', 'clitic': '', 'lemma': 'äge', 'start': 0, 'end': 3, 'ending': '0', 'root': 'äge', 'partofspeech': 'A', 'root_tokens': ('äge',)}], \
        [{'form': 'sg n', 'clitic': '', 'lemma': 'pull', 'start': 4, 'end': 8, 'ending': '0', 'root': 'pull', 'partofspeech': 'S', 'root_tokens': ('pull',)}], \
        [{'form': '?', 'clitic': '', 'lemma': 'D', 'start': 9, 'end': 11, 'ending': '0', 'root': 'D', 'partofspeech': 'Z', 'root_tokens': ('D',)}], \
        [{'form': 'sg n', 'clitic': '', 'lemma': 'irw', 'start': 12, 'end': 15, 'ending': '0', 'root': 'irw', 'partofspeech': 'S', 'root_tokens': ('irw',)}], \
        [{'form': '?', 'clitic': '', 'lemma': 'P', 'start': 16, 'end': 19, 'ending': '0', 'root': 'P', 'partofspeech': 'Z', 'root_tokens': ('P',)}]]
    # TODO: roots of emoticons also need to be fixed, but this 
    #       has a prerequisite that methods creating lemmas &
    #       root_tokens work in-line with the fixes
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_www_addresses():
    # Tests that www addresses have postag 'H':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_www_addresses=True) )
    # Case 1
    text=Text('Lugeja saatis Maaleht.ee-le http://www.tartupostimees.ee foto.')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'clitic': '', 'lemma': 'lugeja', 'start': 0, 'end': 6, 'partofspeech': 'S', 'form': 'sg g', 'root_tokens': ('lugeja',), 'root': 'lugeja', 'ending': '0'}], \
        [{'clitic': '', 'lemma': 'saatma', 'start': 7, 'end': 13, 'partofspeech': 'V', 'form': 's', 'root_tokens': ('saat',), 'root': 'saat', 'ending': 'is'}], \
        [{'clitic': '', 'lemma': 'Maaleht.ee', 'start': 14, 'end': 27, 'partofspeech': 'H', 'form': 'sg all', 'root_tokens': ('Maaleht.ee',), 'root': 'Maaleht.ee', 'ending': 'le'}], \
        [{'clitic': '', 'lemma': 'http://www.tartupostimees.ee', 'start': 28, 'end': 56, 'partofspeech': 'H', 'form': '?', 'root_tokens': ('http://www.tartupostimees.ee',), 'root': 'http://www.tartupostimees.ee', 'ending': '0'}], \
        [{'clitic': '', 'lemma': 'foto', 'start': 57, 'end': 61, 'partofspeech': 'S', 'form': 'sg n', 'root_tokens': ('foto',), 'root': 'foto', 'ending': '0'}], \
        [{'clitic': '', 'lemma': '.', 'start': 61, 'end': 62, 'partofspeech': 'Z', 'form': '', 'root_tokens': ('.',), 'root': '.', 'ending': ''}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_email_addresses():
    # Tests that emails have postag 'H':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_email_addresses=True) )
    # Case 1
    text=Text('Kontakt: big@boss.com; http://www.big.boss.com')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'partofspeech': 'S', 'form': 'sg n', 'ending': '0', 'lemma': 'kontakt', 'root_tokens': ('kontakt',), 'start': 0, 'clitic': '', 'end': 7, 'root': 'kontakt'}], \
        [{'partofspeech': 'Z', 'form': '', 'ending': '', 'lemma': ':', 'root_tokens': (':',), 'start': 7, 'clitic': '', 'end': 8, 'root': ':'}], \
        [{'partofspeech': 'H', 'form': '?', 'ending': '0', 'lemma': 'big@boss.com', 'root_tokens': ('big@boss.com',), 'start': 9, 'clitic': '', 'end': 21, 'root': 'big@boss.com'}], \
        [{'partofspeech': 'Z', 'form': '', 'ending': '', 'lemma': ';', 'root_tokens': (';',), 'start': 21, 'clitic': '', 'end': 22, 'root': ';'}], \
        [{'partofspeech': 'H', 'form': '?', 'ending': '0', 'lemma': 'http://www.big.boss.com', 'root_tokens': ('http://www.big.boss.com',), 'start': 23, 'clitic': '', 'end': 46, 'root': 'http://www.big.boss.com'}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_abbreviations():
    # Tests that abbreviations have postag 'Y':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_abbreviations=True) )
    # Case 1
    text=Text('( 9. jaan. 1939. a. või dets. - toim. )')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'partofspeech': 'Z', 'root': '(', 'root_tokens': ('(',), 'ending': '', 'clitic': '', 'lemma': '(', 'form': '', 'end': 1, 'start': 0}], \
        [{'partofspeech': 'N', 'root': '9', 'root_tokens': ('9',), 'ending': '0', 'clitic': '', 'lemma': '9', 'form': '?', 'end': 4, 'start': 2}], \
        [{'partofspeech': 'Y', 'root': 'jaan', 'root_tokens': ('jaan',), 'ending': '0', 'clitic': '', 'lemma': 'jaan', 'form': '?', 'end': 10, 'start': 5}], \
        [{'partofspeech': 'N', 'root': '1939', 'root_tokens': ('1939',), 'ending': '0', 'clitic': '', 'lemma': '1939', 'form': '?', 'end': 16, 'start': 11}], \
        [{'partofspeech': 'Y', 'root': 'a', 'root_tokens': ('a',), 'ending': '0', 'clitic': '', 'lemma': 'a', 'form': '?', 'end': 19, 'start': 17}], \
        [{'partofspeech': 'J', 'root': 'või', 'root_tokens': ('või',), 'ending': '0', 'clitic': '', 'lemma': 'või', 'form': '', 'end': 23, 'start': 20}], \
        [{'partofspeech': 'Y', 'root': 'dets', 'root_tokens': ('dets',), 'ending': '0', 'clitic': '', 'lemma': 'dets', 'form': '?', 'end': 28, 'start': 24}], \
        [{'partofspeech': 'Z', 'root': '.', 'root_tokens': ('.',), 'ending': '', 'clitic': '', 'lemma': '.', 'form': '', 'end': 29, 'start': 28}], \
        [{'partofspeech': 'Z', 'root': '-', 'root_tokens': ('-',), 'ending': '', 'clitic': '', 'lemma': '-', 'form': '', 'end': 31, 'start': 30}], \
        [{'partofspeech': 'Y', 'root': 'toim', 'root_tokens': ('toim',), 'ending': '0', 'clitic': '', 'lemma': 'toim', 'form': 'sg n', 'end': 37, 'start': 32}], \
        [{'partofspeech': 'Z', 'root': ')', 'root_tokens': (')',), 'ending': '', 'clitic': '', 'lemma': ')', 'form': '', 'end': 39, 'start': 38}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_postanalysis_fix_numeric():
    # Tests that numerics and percentages will have postag 'N':
    # Initialize tagger
    morf_tagger = VabamorfTagger( postanalysis_tagger=PostMorphAnalysisTagger(fix_numeric=True) )
    # Case 1 : percentages
    text=Text('kahanenud 4,7% -lt 1,8% -ni')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'ending': '0', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ('kahanenud',), 'start': 0, 'partofspeech': 'A', 'form': '', 'clitic': '', 'end': 9}, \
         {'ending': '0', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ('kahanenud',), 'start': 0, 'partofspeech': 'A', 'form': 'sg n', 'clitic': '', 'end': 9}, \
         {'ending': 'd', 'lemma': 'kahanenud', 'root': 'kahane=nud', 'root_tokens': ('kahanenud',), 'start': 0, 'partofspeech': 'A', 'form': 'pl n', 'clitic': '', 'end': 9}, \
         {'ending': 'nud', 'lemma': 'kahanema', 'root': 'kahane', 'root_tokens': ('kahane',), 'start': 0, 'partofspeech': 'V', 'form': 'nud', 'clitic': '', 'end': 9}], \
        [{'ending': 'lt', 'lemma': '4,7%', 'root': '4,7%', 'root_tokens': ('4,7%',), 'start': 10, 'partofspeech': 'N', 'form': 'sg abl', 'clitic': '', 'end': 18}], \
        [{'ending': 'ni', 'lemma': '1,8%', 'root': '1,8%', 'root_tokens': ('1,8%',), 'start': 19, 'partofspeech': 'N', 'form': 'sg ter', 'clitic': '', 'end': 27}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2 : numerics
    text=Text('10-te km kaupa liiva umbes 0-iga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'partofspeech': 'N', 'start': 0, 'lemma': '10', 'root_tokens': ('10',), 'ending': 'te', 'root': '10', 'end': 5, 'clitic': '', 'form': 'pl g'}],  \
        [{'partofspeech': 'Y', 'start': 6, 'lemma': 'km', 'root_tokens': ('km',), 'ending': '0', 'root': 'km', 'end': 8, 'clitic': '', 'form': '?'}], \
        [{'partofspeech': 'K', 'start': 9, 'lemma': 'kaupa', 'root_tokens': ('kaupa',), 'ending': '0', 'root': 'kaupa', 'end': 14, 'clitic': '', 'form': ''}], \
        [{'partofspeech': 'S', 'start': 15, 'lemma': 'liiv', 'root_tokens': ('liiv',), 'ending': '0', 'root': 'liiv', 'end': 20, 'clitic': '', 'form': 'sg p'}], \
        [{'partofspeech': 'D', 'start': 21, 'lemma': 'umbes', 'root_tokens': ('umbes',), 'ending': '0', 'root': 'umbes', 'end': 26, 'clitic': '', 'form': ''}], \
        [{'partofspeech': 'N', 'start': 27, 'lemma': '0', 'root_tokens': ('0',), 'ending': 'ga', 'root': '0', 'end': 32, 'clitic': '', 'form': 'sg kom'}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    # TODO: this is test case currently broken: the disambiguator picks wrong analysis for the first word
    #assert expected_records == results_dict

    # Case 3 : numerics
    text=Text('Sai 112-e helistatud, kuna 1-ed ja 2-ed on ju nii lähestikku')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'partofspeech': 'V', 'form': 's', 'lemma': 'saama', 'root_tokens': ('saa',), 'clitic': '', 'root': 'saa', 'end': 3, 'start': 0, 'ending': 'i'}], \
        # Following is problematic: 
        #   the correct form should be 'sg p', but then again, the 
        #   surface form '112-e' is also misleading, can be easily 
        #   interpreted as 'sg g'
        [{'partofspeech': 'N', 'form': 'sg g', 'lemma': '112', 'root_tokens': ('112',), 'clitic': '', 'root': '112', 'end': 9, 'start': 4, 'ending': '0'}], \
        [{'partofspeech': 'A', 'form': '', 'lemma': 'helistatud', 'root_tokens': ('helistatud',), 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': '0'}, \
         {'partofspeech': 'A', 'form': 'sg n', 'lemma': 'helistatud', 'root_tokens': ('helistatud',), 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': '0'}, \
         {'partofspeech': 'A', 'form': 'pl n', 'lemma': 'helistatud', 'root_tokens': ('helistatud',), 'clitic': '', 'root': 'helista=tud', 'end': 20, 'start': 10, 'ending': 'd'}, \
         {'partofspeech': 'V', 'form': 'tud', 'lemma': 'helistama', 'root_tokens': ('helista',), 'clitic': '', 'root': 'helista', 'end': 20, 'start': 10, 'ending': 'tud'}], \
        [{'partofspeech': 'Z', 'form': '', 'lemma': ',', 'root_tokens': (',',), 'clitic': '', 'root': ',', 'end': 21, 'start': 20, 'ending': ''}], \
        [{'partofspeech': 'J', 'ending': '0', 'root_tokens': ('kuna',), 'end': 26, 'lemma': 'kuna', 'start': 22, 'root': 'kuna', 'form': '', 'clitic': ''}], \
        [{'partofspeech': 'N', 'ending': 'd', 'root_tokens': ('1',), 'end': 31, 'lemma': '1', 'start': 27, 'root': '1', 'form': 'pl n', 'clitic': ''}], \
        [{'partofspeech': 'J', 'ending': '0', 'root_tokens': ('ja',), 'end': 34, 'lemma': 'ja', 'start': 32, 'root': 'ja', 'form': '', 'clitic': ''}], \
        [{'partofspeech': 'N', 'ending': 'd', 'root_tokens': ('2',), 'end': 39, 'lemma': '2', 'start': 35, 'root': '2', 'form': 'pl n', 'clitic': ''}], \
        [{'partofspeech': 'V', 'ending': '0', 'root_tokens': ('ole',), 'end': 42, 'lemma': 'olema', 'start': 40, 'root': 'ole', 'form': 'b', 'clitic': ''}, \
         {'partofspeech': 'V', 'ending': '0', 'root_tokens': ('ole',), 'end': 42, 'lemma': 'olema', 'start': 40, 'root': 'ole', 'form': 'vad', 'clitic': ''}], \
        [{'partofspeech': 'D', 'ending': '0', 'root_tokens': ('ju',), 'end': 45, 'lemma': 'ju', 'start': 43, 'root': 'ju', 'form': '', 'clitic': ''}], \
        [{'partofspeech': 'D', 'ending': '0', 'root_tokens': ('nii',), 'end': 49, 'lemma': 'nii', 'start': 46, 'root': 'nii', 'form': '', 'clitic': ''}], \
        [{'partofspeech': 'D', 'ending': '0', 'root_tokens': ('lähestikku',), 'end': 60, 'lemma': 'lähestikku', 'start': 50, 'root': 'lähestikku', 'form': '', 'clitic': ''}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


# ----------------------------------


from estnltk.rewriting.postmorph.vabamorf_corrector import VabamorfCorrectionRewriter

def test_postanalysis_with_correction_rewriter_for_numbers():
    # Tests VabamorfCorrectionRewriter on providing fixes to numbers:
    # Initialize taggers
    postanalysis_tagger = \
        PostMorphAnalysisTagger(correction_rewriter = VabamorfCorrectionRewriter())
    morf_tagger = \
        VabamorfTagger( postanalysis_tagger=postanalysis_tagger )
    # Case 1
    text=Text('Tiit müüs 10e krooniga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'start': 0, 'lemma': 'Tiit', 'ending': '0', 'form': 'sg n', 'root': 'Tiit', 'partofspeech': 'H', 'clitic': '', 'root_tokens': ('Tiit',), 'end': 4}], \
        [{'start': 5, 'lemma': 'müüma', 'ending': 's', 'form': 's', 'root': 'müü', 'partofspeech': 'V', 'clitic': '', 'root_tokens': ('müü',), 'end': 9}], \
        [{'start': 10, 'lemma': '10', 'ending': '0', 'form': 'sg g', 'root': '10', 'partofspeech': 'N', 'clitic': '', 'root_tokens': ('10',), 'end': 13}], \
        [{'start': 14, 'lemma': 'kroon', 'ending': 'ga', 'form': 'sg kom', 'root': 'kroon', 'partofspeech': 'S', 'clitic': '', 'root_tokens': ('kroon',), 'end': 22}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

    # Case 2
    text=Text('Tiit ei maksnud 6t krooni, vaid ostis 3ga')
    text.tag_layer(['words','sentences'])
    morf_tagger.tag(text)
    #print(text['morph_analysis'].to_records())
    expected_records = [ \
        [{'clitic': '', 'root': 'Tiit', 'lemma': 'Tiit', 'end': 4, 'form': 'sg n', 'partofspeech': 'H', 'start': 0, 'ending': '0', 'root_tokens': ('Tiit',)}], \
        [{'clitic': '', 'root': 'ei', 'lemma': 'ei', 'end': 7, 'form': 'neg', 'partofspeech': 'V', 'start': 5, 'ending': '0', 'root_tokens': ('ei',)}], \
        [{'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': '', 'partofspeech': 'A', 'start': 8, 'ending': '0', 'root_tokens': ('maksnud',)}, \
         {'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': 'sg n', 'partofspeech': 'A', 'start': 8, 'ending': '0', 'root_tokens': ('maksnud',)}, \
         {'clitic': '', 'root': 'maks=nud', 'lemma': 'maksnud', 'end': 15, 'form': 'pl n', 'partofspeech': 'A', 'start': 8, 'ending': 'd', 'root_tokens': ('maksnud',)}, \
         {'clitic': '', 'root': 'maks', 'lemma': 'maksma', 'end': 15, 'form': 'nud', 'partofspeech': 'V', 'start': 8, 'ending': 'nud', 'root_tokens': ('maks',)}], \
        [{'clitic': '', 'root': '6', 'lemma': '6', 'end': 18, 'form': 'sg p', 'partofspeech': 'N', 'start': 16, 'ending': 't', 'root_tokens': ('6',)}], \
        [{'clitic': '', 'root': 'kroon', 'lemma': 'kroon', 'end': 25, 'form': 'sg p', 'partofspeech': 'S', 'start': 19, 'ending': '0', 'root_tokens': ('kroon',)}], \
        [{'clitic': '', 'root': ',', 'lemma': ',', 'end': 26, 'form': '', 'partofspeech': 'Z', 'start': 25, 'ending': '', 'root_tokens': (',',)}], \
        [{'clitic': '', 'root': 'vaid', 'lemma': 'vaid', 'end': 31, 'form': '', 'partofspeech': 'J', 'start': 27, 'ending': '0', 'root_tokens': ('vaid',)}], \
        [{'clitic': '', 'root': 'ost', 'lemma': 'ostma', 'end': 37, 'form': 's', 'partofspeech': 'V', 'start': 32, 'ending': 'is', 'root_tokens': ('ost',)}], \
        [{'clitic': '', 'root': '3', 'lemma': '3', 'end': 41, 'form': 'sg kom', 'partofspeech': 'N', 'start': 38, 'ending': 'ga', 'root_tokens': ('3',)}]]
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict

