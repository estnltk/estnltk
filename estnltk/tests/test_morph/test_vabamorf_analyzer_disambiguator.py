from estnltk import Text
from estnltk.taggers.morf import VabamorfAnalyzer, VabamorfDisambiguator
from estnltk.taggers.morf import IGNORE_ATTR

# ----------------------------------
#   Helper functions
# ----------------------------------

def _ignore_morph_analyses_overlapping_with_compound_tokens( \
                                            text:Text, \
                                            ignore_compound_tokens:list ):
    '''Finds all morph_analyses overlapping with compound tokens which 
       types are listed in ignore_compound_tokens, and marks these as to
       be ignored during the morphological disambiguation. Returns a 
       dict containing locations (start, end) of spans that were ignored.
    '''
    assert 'morph_analysis' in text.layers, \
        '(!) Text needs to be morphologically analysed!'
    mark_ignore = {}
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        for ctid, comp_token in enumerate( text['compound_tokens'] ):
            ct_type_matches = \
                [ct_type in comp_token.type for ct_type in ignore_compound_tokens]
            if spanlist.start==comp_token.start and \
               spanlist.end==comp_token.end and \
               any(ct_type_matches):
                # Record location and content of morph analysis 
                # matching the compound token
                mark_ignore[pos_key] = spanlist
        for span in spanlist:
            if pos_key in mark_ignore:
                setattr(span, IGNORE_ATTR, True)
            else:
                setattr(span, IGNORE_ATTR, False)
    return mark_ignore


def _sort_morph_analysis_records( morph_analysis_records:list ):
    '''Sorts sublists (lists of analyses of a single word) of 
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order. '''
    for wrid, word_records_list in enumerate( morph_analysis_records ):
        sorted_records = sorted( word_records_list, key = lambda x : \
            x['root']+x['ending']+x['clitic']+x['partofspeech']+x['form'] )
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
    expected_records = [ \
        [{'partofspeech': 'P', 'start': 0, 'ending': '0', 'form': 'sg g', 'root': 'mitmes', 'end': 8, 'clitic': '', 'root_tokens': ('mitmes',), 'lemma': 'mitmes'}], \
        [{'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg g', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ('koha',), 'lemma': 'koha'}, \
         {'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg n', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ('koha',), 'lemma': 'koha'}, \
         {'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg p', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ('koha',), 'lemma': 'koha'}, \
         {'partofspeech': 'V', 'start': 9, 'ending': '0', 'form': 'o', 'root': 'koha', 'end': 13, 'clitic': '', 'root_tokens': ('koha',), 'lemma': 'kohama'}, \
         {'partofspeech': 'S', 'start': 9, 'ending': '0', 'form': 'sg g', 'root': 'koht', 'end': 13, 'clitic': '', 'root_tokens': ('koht',), 'lemma': 'koht'}], \
        [{'partofspeech': 'S', 'start': 14, 'ending': '0', 'form': 'sg n', 'root': 'sai', 'end': 17, 'clitic': '', 'root_tokens': ('sai',), 'lemma': 'sai'}, \
         {'partofspeech': 'V', 'start': 14, 'ending': 'i', 'form': 's', 'root': 'saa', 'end': 17, 'clitic': '', 'root_tokens': ('saa',), 'lemma': 'saama'}], \
        [{'partofspeech': 'D', 'start': 18, 'ending': '0', 'form': '', 'root': 'kohale', 'end': 24, 'clitic': '', 'root_tokens': ('kohale',), 'lemma': 'kohale'}, \
         {'partofspeech': 'K', 'start': 18, 'ending': '0', 'form': '', 'root': 'kohale', 'end': 24, 'clitic': '', 'root_tokens': ('kohale',), 'lemma': 'kohale'}, \
         {'partofspeech': 'S', 'start': 18, 'ending': 'le', 'form': 'sg all', 'root': 'koha', 'end': 24, 'clitic': '', 'root_tokens': ('koha',), 'lemma': 'koha'}, \
         {'partofspeech': 'S', 'start': 18, 'ending': 'le', 'form': 'sg all', 'root': 'koht', 'end': 24, 'clitic': '', 'root_tokens': ('koht',), 'lemma': 'koht'}], \
        [{'partofspeech': 'A', 'start': 25, 'ending': '0', 'form': '', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ('jõudnud',), 'lemma': 'jõudnud'}, \
         {'partofspeech': 'A', 'start': 25, 'ending': '0', 'form': 'sg n', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ('jõudnud',), 'lemma': 'jõudnud'}, \
         {'partofspeech': 'S', 'start': 25, 'ending': 'd', 'form': 'pl n', 'root': 'jõud=nu', 'end': 32, 'clitic': '', 'root_tokens': ('jõudnu',), 'lemma': 'jõudnu'}, \
         {'partofspeech': 'A', 'start': 25, 'ending': 'd', 'form': 'pl n', 'root': 'jõud=nud', 'end': 32, 'clitic': '', 'root_tokens': ('jõudnud',), 'lemma': 'jõudnud'}, \
         {'partofspeech': 'V', 'start': 25, 'ending': 'nud', 'form': 'nud', 'root': 'jõud', 'end': 32, 'clitic': '', 'root_tokens': ('jõud',), 'lemma': 'jõudma'}], \
        [{'partofspeech': 'S', 'start': 33, 'ending': '0', 'form': 'sg n', 'root': 'mees', 'end': 37, 'clitic': '', 'root_tokens': ('mees',), 'lemma': 'mees'}, \
         {'partofspeech': 'S', 'start': 33, 'ending': 's', 'form': 'sg in', 'root': 'mesi', 'end': 37, 'clitic': '', 'root_tokens': ('mesi',), 'lemma': 'mesi'}], \
        [{'partofspeech': 'Z', 'start': 38, 'ending': '', 'form': '', 'root': '?', 'end': 39, 'clitic': '', 'root_tokens': ('?',), 'lemma': '?'}]]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
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
    disambiguator.tag(text)
    expected_records = [ \
        [{'ending': '0', 'root': 'mitmes', 'root_tokens': ('mitmes',), 'start': 0, 'end': 8, 'clitic': '', 'partofspeech': 'P', 'lemma': 'mitmes', 'form': 'sg g'}], \
        [{'ending': '0', 'root': 'koha', 'root_tokens': ('koha',), 'start': 9, 'end': 13, 'clitic': '', 'partofspeech': 'S', 'lemma': 'koha', 'form': 'sg g'}, \
         {'ending': '0', 'root': 'koht', 'root_tokens': ('koht',), 'start': 9, 'end': 13, 'clitic': '', 'partofspeech': 'S', 'lemma': 'koht', 'form': 'sg g'}], \
        [{'ending': 'i', 'root': 'saa', 'root_tokens': ('saa',), 'start': 14, 'end': 17, 'clitic': '', 'partofspeech': 'V', 'lemma': 'saama', 'form': 's'}], \
        [{'ending': '0', 'root': 'kohale', 'root_tokens': ('kohale',), 'start': 18, 'end': 24, 'clitic': '', 'partofspeech': 'D', 'lemma': 'kohale', 'form': ''}], \
        [{'ending': 'nud', 'root': 'jõud', 'root_tokens': ('jõud',), 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'V', 'lemma': 'jõudma', 'form': 'nud'}, \
         {'ending': '0', 'root': 'jõud=nud', 'root_tokens': ('jõudnud',), 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': ''}, \
         {'ending': '0', 'root': 'jõud=nud', 'root_tokens': ('jõudnud',), 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': 'sg n'}, \
         {'ending': 'd', 'root': 'jõud=nud', 'root_tokens': ('jõudnud',), 'start': 25, 'end': 32, 'clitic': '', 'partofspeech': 'A', 'lemma': 'jõudnud', 'form': 'pl n'}], \
        [{'ending': '0', 'root': 'mees', 'root_tokens': ('mees',), 'start': 33, 'end': 37, 'clitic': '', 'partofspeech': 'S', 'lemma': 'mees', 'form': 'sg n'}], \
        [{'ending': '', 'root': '?', 'root_tokens': ('?',), 'start': 38, 'end': 39, 'clitic': '', 'partofspeech': 'Z', 'lemma': '?', 'form': ''}]]
    #print(text['morph_analysis'].to_records())
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


# ----------------------------------
#   Test 
#      disambiguation_with_ignore
# ----------------------------------

def test_morph_disambiguation_with_ignore():
    # Tests that morphological disambiguator can be set to ignore some words
    # Case 1 : test ignoring random words ( do not try this at home! )
    text=Text('Mitmenda koha sai kohale jõudnud mees ?')
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    mark_ignore = { (14,17) : [],  # sai
                    (33,37) : [],  # mees
                  }
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            # Record the pervious spanlist
            mark_ignore[pos_key] = spanlist
        for span in spanlist:
            if pos_key in mark_ignore:
                setattr(span, IGNORE_ATTR, True)
            else:
                setattr(span, IGNORE_ATTR, False)
    disambiguator.tag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    # Check that marked spans remain the same in the new layer
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            assert mark_ignore[pos_key] == spanlist


def test_morph_disambiguation_with_ignore_all():
    # Test: if all words in the sentence are ignored,
    #       disambiguator won't raise any error
    text=Text('Mees peeti kinni') 
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    #print(text['morph_analysis'].to_records())
    # Ignore all spans/words
    for spanlist in text.morph_analysis.spans:
        for span in spanlist:
            setattr(span, IGNORE_ATTR, True)
    disambiguator.tag(text)
    #print(text['morph_analysis'].to_records())
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)


def test_morph_disambiguation_with_ignore_emoticons():
    # Case 2 : test ignoring emoticons
    text=Text('Mõte on hea :-) Tuleme siis kolmeks :)')
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)
    # ignore emoticons
    mark_ignore = \
      _ignore_morph_analyses_overlapping_with_compound_tokens(text, ['emoticon'])
    disambiguator.tag(text)
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    # Check that marked spans remain the same in the new layer
    for spanlist in text.morph_analysis.spans:
        pos_key = (spanlist.start, spanlist.end)
        if pos_key in mark_ignore:
            assert mark_ignore[pos_key] == spanlist


def test_morph_disambiguation_with_ignore_xml_tags():
    # Case 1 : test ignoring xml tags inserted into text
    text=Text('Mees <b>peeti</b> kinni, aga ta <br> naeris <br> vaid!') 
    text.tag_layer(['words','sentences'])
    analyzer1.tag(text)  # analyze and add empty IGNORE_ATTR-s
    # ignore xml_tags
    mark_ignore = \
      _ignore_morph_analyses_overlapping_with_compound_tokens(text, ['xml_tag'])
    #print(text['morph_analysis'].to_records())
    disambiguator.tag(text)
    #print(text['morph_analysis'].to_records())
    # Assert that attribute IGNORE_ATTR has been removed 
    assert not hasattr(text.morph_analysis, IGNORE_ATTR)
    for spanlist in text.morph_analysis.spans:
        # assert that all words have been disambiguated
        assert len(spanlist) == 1



