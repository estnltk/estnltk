from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.resolve_layer_dag import make_resolver

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

def test_default_morph_analysis():
    # Case 1
    text = Text("Aga kõik juhtus iseenesest.")
    text.analyse('morphology')
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'root': 'aga', 'ending': '0', 'start': 0, 'form': '', 'lemma': 'aga', 'root_tokens': ('aga',), 'partofspeech': 'J', 'clitic': '', 'end': 3}], \
        [{'root': 'kõik', 'ending': '0', 'start': 4, 'form': 'pl n', 'lemma': 'kõik', 'root_tokens': ('kõik',), 'partofspeech': 'P', 'clitic': '', 'end': 8}, \
         {'root': 'kõik', 'ending': '0', 'start': 4, 'form': 'sg n', 'lemma': 'kõik', 'root_tokens': ('kõik',), 'partofspeech': 'P', 'clitic': '', 'end': 8}], \
        [{'root': 'juhtu', 'ending': 's', 'start': 9, 'form': 's', 'lemma': 'juhtuma', 'root_tokens': ('juhtu',), 'partofspeech': 'V', 'clitic': '', 'end': 15}], \
        [{'root': 'ise_enesest', 'ending': '0', 'start': 16, 'form': '', 'lemma': 'iseenesest', 'root_tokens': ('ise', 'enesest'), 'partofspeech': 'D', 'clitic': '', 'end': 26}], \
        [{'root': '.', 'ending': '', 'start': 26, 'form': '', 'lemma': '.', 'root_tokens': ('.',), 'partofspeech': 'Z', 'clitic': '', 'end': 27}] ]
    # Check results
    assert expected_records == text['morph_analysis'].to_records()
    assert [['J'], ['P', 'P'], ['V'], ['D'], ['Z']] == text.partofspeech
    
    # Case 2 (contains ambiguities that should be resolved)
    text = Text("Kärbes hulbib mees ja naeris puhub sädelevaid mulle.")
    text.analyse('morphology')
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'partofspeech': 'S', 'root': 'kärbes', 'start': 0, 'clitic': '', 'end': 6, 'root_tokens': ('kärbes',), 'lemma': 'kärbes', 'ending': '0', 'form': 'sg n'}], \
        [{'partofspeech': 'V', 'root': 'hulpi', 'start': 7, 'clitic': '', 'end': 13, 'root_tokens': ('hulpi',), 'lemma': 'hulpima', 'ending': 'b', 'form': 'b'}], \
        [{'partofspeech': 'S', 'root': 'mees', 'start': 14, 'clitic': '', 'end': 18, 'root_tokens': ('mees',), 'lemma': 'mees', 'ending': '0', 'form': 'sg n'}], \
        [{'partofspeech': 'J', 'root': 'ja', 'start': 19, 'clitic': '', 'end': 21, 'root_tokens': ('ja',), 'lemma': 'ja', 'ending': '0', 'form': ''}], \
        [{'partofspeech': 'V', 'root': 'naer', 'start': 22, 'clitic': '', 'end': 28, 'root_tokens': ('naer',), 'lemma': 'naerma', 'ending': 'is', 'form': 's'}], \
        [{'partofspeech': 'V', 'root': 'puhu', 'start': 29, 'clitic': '', 'end': 34, 'root_tokens': ('puhu',), 'lemma': 'puhuma', 'ending': 'b', 'form': 'b'}], \
        [{'partofspeech': 'A', 'root': 'sädelev', 'start': 35, 'clitic': '', 'end': 45, 'root_tokens': ('sädelev',), 'lemma': 'sädelev', 'ending': 'id', 'form': 'pl p'}], \
        [{'partofspeech': 'P', 'root': 'mina', 'start': 46, 'clitic': '', 'end': 51, 'root_tokens': ('mina',), 'lemma': 'mina', 'ending': 'lle', 'form': 'sg all'}], \
        [{'partofspeech': 'Z', 'root': '.', 'start': 51, 'clitic': '', 'end': 52, 'root_tokens': ('.',), 'lemma': '.', 'ending': '', 'form': ''}]]
    # Note that this example sentence is a little out of the ordinary and 
    # hence the bad performance of disambiguator. The more 'normal' your 
    # text is, the better the results.
    # Check results
    assert expected_records == text['morph_analysis'].to_records()


def test_default_morph_analysis_without_disambiguation():
    # Case 1
    resolver = make_resolver(
                   disambiguate=False,
                   guess=True,
                   propername=True,
                   phonetic=False,
                   compound=True)
    # Create text and tag all
    text = Text("Kärbes hulbib mees ja naeris puhub sädelevaid mulle.").tag_layer()
    # Remove old morph layer
    delattr(text, 'morph_analysis')
    # Create a new layer without disambiguation
    text.tag_layer(resolver=resolver)['morph_analysis']
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'root_tokens': ('Kärbes',), 'lemma': 'Kärbes', 'root': 'Kärbes', 'clitic': '', 'ending': '0', 'end': 6, 'start': 0, 'form': 'sg n', 'partofspeech': 'H', '_ignore': False},\
        {'root_tokens': ('Kärbe',), 'lemma': 'Kärbe', 'root': 'Kärbe', 'clitic': '', 'ending': 's', 'end': 6, 'start': 0, 'form': 'sg in', 'partofspeech': 'H', '_ignore': False},\
        {'root_tokens': ('kärbes',), 'lemma': 'kärbes', 'root': 'kärbes', 'clitic': '', 'ending': '0', 'end': 6, 'start': 0, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False}], \
        [{'root_tokens': ('hulpi',), 'lemma': 'hulpima', 'root': 'hulpi', 'clitic': '', 'ending': 'b', 'end': 13, 'start': 7, 'form': 'b', 'partofspeech': 'V', '_ignore': False}], \
        [{'root_tokens': ('mesi',), 'lemma': 'mesi', 'root': 'mesi', 'clitic': '', 'ending': 's', 'end': 18, 'start': 14, 'form': 'sg in', 'partofspeech': 'S', '_ignore': False}, \
        {'root_tokens': ('mees',), 'lemma': 'mees', 'root': 'mees', 'clitic': '', 'ending': '0', 'end': 18, 'start': 14, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False}], \
        [{'root_tokens': ('ja',), 'lemma': 'ja', 'root': 'ja', 'clitic': '', 'ending': '0', 'end': 21, 'start': 19, 'form': '', 'partofspeech': 'J', '_ignore': False}], \
        [{'root_tokens': ('naeris',), 'lemma': 'naeris', 'root': 'naeris', 'clitic': '', 'ending': '0', 'end': 28, 'start': 22, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False},\
         {'root_tokens': ('naer',), 'lemma': 'naerma', 'root': 'naer', 'clitic': '', 'ending': 'is', 'end': 28, 'start': 22, 'form': 's', 'partofspeech': 'V', '_ignore': False},\
         {'root_tokens': ('naeris',), 'lemma': 'naeris', 'root': 'naeris', 'clitic': '', 'ending': 's', 'end': 28, 'start': 22, 'form': 'sg in', 'partofspeech': 'S', '_ignore': False}], \
        [{'root_tokens': ('puhu',), 'lemma': 'puhuma', 'root': 'puhu', 'clitic': '', 'ending': 'b', 'end': 34, 'start': 29, 'form': 'b', 'partofspeech': 'V', '_ignore': False}], \
        [{'root_tokens': ('sädelev',), 'lemma': 'sädelev', 'root': 'sädelev', 'clitic': '', 'ending': 'id', 'end': 45, 'start': 35, 'form': 'pl p', 'partofspeech': 'A', '_ignore': False}], \
        [{'root_tokens': ('mina',), 'lemma': 'mina', 'root': 'mina', 'clitic': '', 'ending': 'lle', 'end': 51, 'start': 46, 'form': 'sg all', 'partofspeech': 'P', '_ignore': False}, \
         {'root_tokens': ('mulle',), 'lemma': 'mulle', 'root': 'mulle', 'clitic': '', 'ending': '0', 'end': 51, 'start': 46, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False},\
         {'root_tokens': ('mull',), 'lemma': 'mull', 'root': 'mull', 'clitic': '', 'ending': 'e', 'end': 51, 'start': 46, 'form': 'pl p', 'partofspeech': 'S', '_ignore': False}], \
        [{'root_tokens': ('.',), 'lemma': '.', 'root': '.', 'clitic': '', 'ending': '', 'end': 52, 'start': 51, 'form': '', 'partofspeech': 'Z', '_ignore': False}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results ( morph should be ambiguous )
    assert len(expected_records) == len(results_dict)
    assert expected_records == results_dict


def test_default_morph_analysis_without_propername():
    # Case 1
    resolver = make_resolver(
                   disambiguate=True,
                   guess=True,
                   propername=False,
                   phonetic=False,
                   compound=True)
    # Create text and tag all
    text = Text("Ida-Euroopas sai valmis Parlament, suure algustähega.")
    # Analyse 'morphology' without without propername guessing
    text.analyse('morphology', resolver=resolver)
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'partofspeech': 'H', 'ending': 's', 'root_tokens': ('Ida', 'Euroopa'), 'end': 12, 'clitic': '', 'start': 0, 'lemma': 'Ida-Euroopa', 'form': 'sg in', 'root': 'Ida-Euroopa'}], \
        [{'partofspeech': 'V', 'ending': 'i', 'root_tokens': ('saa',), 'end': 16, 'clitic': '', 'start': 13, 'lemma': 'saama', 'form': 's', 'root': 'saa'}], \
        [{'partofspeech': 'A', 'ending': '0', 'root_tokens': ('valmis',), 'end': 23, 'clitic': '', 'start': 17, 'lemma': 'valmis', 'form': '', 'root': 'valmis'}], \
        [{'partofspeech': 'S', 'ending': '0', 'root_tokens': ('parlament',), 'end': 33, 'clitic': '', 'start': 24, 'lemma': 'parlament', 'form': 'sg n', 'root': 'parlament'}], \
        [{'partofspeech': 'Z', 'ending': '', 'root_tokens': (',',), 'end': 34, 'clitic': '', 'start': 33, 'lemma': ',', 'form': '', 'root': ','}], \
        [{'partofspeech': 'A', 'ending': '0', 'root_tokens': ('suur',), 'end': 40, 'clitic': '', 'start': 35, 'lemma': 'suur', 'form': 'sg g', 'root': 'suur'}], \
        [{'partofspeech': 'S', 'ending': 'ga', 'root_tokens': ('algus', 'täht'), 'end': 52, 'clitic': '', 'start': 41, 'lemma': 'algustäht', 'form': 'sg kom', 'root': 'algus_täht'}], \
        [{'partofspeech': 'Z', 'ending': '', 'root_tokens': ('.',), 'end': 53, 'clitic': '', 'start': 52, 'lemma': '.', 'form': '', 'root': '.'}]]
    # Check results
    assert expected_records == text['morph_analysis'].to_records()


def test_default_morph_analysis_without_guessing():
    # Case 1
    resolver = make_resolver(
                   disambiguate=False,
                   guess       =False,
                   propername  =False,
                   # Note: when switching off guess, we must also switch off propername and disambiguate,
                   # as disambiguation does not work on partially analysed texts 
                   phonetic=False,
                   compound=True)
    # Create text and tag all
    text = Text("Sa ajad sássi inimmeste erinevad käsitlusviisid ja lóodusnähhtuste kinndla vahekorra.").tag_layer()
    # Remove old morph layer
    delattr(text, 'morph_analysis')
    # Create a new layer without guessing
    text.tag_layer(resolver=resolver)['morph_analysis']
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'lemma': 'sina', 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'P', 'end': 2, 'root_tokens': ('sina',), 'root': 'sina', 'start': 0, '_ignore': False}], \
        [{'lemma': 'aeg', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'S', 'end': 7, 'root_tokens': ('aeg',), 'root': 'aeg', 'start': 3, '_ignore': False}, \
         {'lemma': 'ajama', 'ending': 'd', 'clitic': '', 'form': 'd', 'partofspeech': 'V', 'end': 7, 'root_tokens': ('aja',), 'root': 'aja', 'start': 3, '_ignore': False}], \
        [{'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 13, 'lemma': None, 'start': 8, 'root_tokens': None, 'ending': None}],\
        [{'lemma': 'inimmest', 'ending': 'e', 'clitic': '', 'form': 'pl p', 'partofspeech': 'S', 'end': 23, 'root_tokens': ('inim', 'mest'), 'root': 'inim_mest', 'start': 14, '_ignore': False}], \
        [{'lemma': 'erinema', 'ending': 'vad', 'clitic': '', 'form': 'vad', 'partofspeech': 'V', 'end': 32, 'root_tokens': ('erine',), 'root': 'erine', 'start': 24, '_ignore': False}, \
         {'lemma': 'erinev', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'A', 'end': 32, 'root_tokens': ('erinev',), 'root': 'erinev', 'start': 24, '_ignore': False}], \
        [{'lemma': 'käsitlusviis', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'S', 'end': 47, 'root_tokens': ('käsitlus', 'viis'), 'root': 'käsitlus_viis', 'start': 33, '_ignore': False}], \
        [{'lemma': 'ja', 'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'J', 'end': 50, 'root_tokens': ('ja',), 'root': 'ja', 'start': 48, '_ignore': False}], \
        [{'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 66, 'lemma': None, 'start': 51, 'root_tokens': None, 'ending': None}],\
        [{'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 74, 'lemma': None, 'start': 67, 'root_tokens': None, 'ending': None}],\
        [{'lemma': 'vahekord', 'ending': '0', 'clitic': '', 'form': 'sg g', 'partofspeech': 'S', 'end': 84, 'root_tokens': ('vahe', 'kord'), 'root': 'vahe_kord', 'start': 75, '_ignore': False}],\
        [{'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 85, 'lemma': None, 'start': 84, 'root_tokens': None, 'ending': None}] ]
    # Note: currently words without analyses will not show up when calling to_records()
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict
    
    # Case 2
    # Create text and tag all
    text = Text("Tüdrukud läksid poodelungile.").tag_layer()  
    # Remove old morph layer
    delattr(text, 'morph_analysis')
    # Create a new layer without guessing
    text.tag_layer(resolver=resolver)['morph_analysis']
    assert [['tüdruk'], ['mine'], [None], [None]]   == text.root
    assert [['tüdruk'], ['minema'], [None], [None]] == text.lemma
    assert [['S'], ['V'], [None], [None]]           == text.partofspeech
    
    # Case 3
    # Use VabamorfTagger
    morph_analyser = VabamorfTagger( disambiguate=False, guess=False, propername=False )
    text = Text("Ma tahax minna järve ääde")
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'partofspeech': 'P', 'lemma': 'mina', 'form': 'sg n', 'root_tokens': ('mina',), 'ending': '0', 'end': 2, 'clitic': '', 'start': 0, 'root': 'mina', '_ignore': False}], \
        [{'ending': None, 'start': 3, 'lemma': None, 'form': None, 'root_tokens': None, '_ignore': False, 'root': None, 'clitic': None, 'end': 8, 'partofspeech': None}], \
        [{'partofspeech': 'V', 'lemma': 'minema', 'form': 'da', 'root_tokens': ('mine',), 'ending': 'a', 'end': 14, 'clitic': '', 'start': 9, 'root': 'mine', '_ignore': False}], \
        [{'partofspeech': 'S', 'lemma': 'järv', 'form': 'adt', 'root_tokens': ('järv',), 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}, \
         {'partofspeech': 'S', 'lemma': 'järv', 'form': 'sg g', 'root_tokens': ('järv',), 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}, \
         {'partofspeech': 'S', 'lemma': 'järv', 'form': 'sg p', 'root_tokens': ('järv',), 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}],\
        [{'ending': None, 'start': 21, 'lemma': None, 'form': None, 'root_tokens': None, '_ignore': False, 'root': None, 'clitic': None, 'end': 25, 'partofspeech': None}], \
    ]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_default_morph_analysis_on_compound_tokens():
    # Case 1
    text = Text("Mis lil-li müüs Tiit Mac'ile 10'e krooniga?")
    text.analyse('morphology')
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'end': 3, 'partofspeech': 'P', 'start': 0, 'root_tokens': ('mis',), 'lemma': 'mis', 'ending': '0', 'root': 'mis', 'form': 'pl n', 'clitic': ''}, \
         {'end': 3, 'partofspeech': 'P', 'start': 0, 'root_tokens': ('mis',), 'lemma': 'mis', 'ending': '0', 'root': 'mis', 'form': 'sg n', 'clitic': ''}], \
        [{'end': 10, 'partofspeech': 'S', 'start': 4, 'root_tokens': ('lill',), 'lemma': 'lill', 'ending': 'i', 'root': 'lill', 'form': 'pl p', 'clitic': ''}], \
        [{'end': 15, 'partofspeech': 'V', 'start': 11, 'root_tokens': ('müü',), 'lemma': 'müüma', 'ending': 's', 'root': 'müü', 'form': 's', 'clitic': ''}], \
        [{'end': 20, 'partofspeech': 'H', 'start': 16, 'root_tokens': ('Tiit',), 'lemma': 'Tiit', 'ending': '0', 'root': 'Tiit', 'form': 'sg n', 'clitic': ''}], \
        [{'end': 28, 'partofspeech': 'H', 'start': 21, 'root_tokens': ('Mac',), 'lemma': 'Mac', 'ending': 'le', 'root': 'Mac', 'form': 'sg all', 'clitic': ''}], \
        [{'end': 33, 'partofspeech': 'S', 'start': 29, 'root_tokens': ('10',), 'lemma': '10', 'ending': '0', 'root': '10', 'form': 'sg g', 'clitic': ''}], \
        [{'end': 42, 'partofspeech': 'S', 'start': 34, 'root_tokens': ('kroon',), 'lemma': 'kroon', 'ending': 'ga', 'root': 'kroon', 'form': 'sg kom', 'clitic': ''}], \
        [{'end': 43, 'partofspeech': 'Z', 'start': 42, 'root_tokens': ('?',), 'lemma': '?', 'ending': '', 'root': '?', 'form': '', 'clitic': ''}]]
    # Sort analyses (so that the order within a word is always the same)
    results_dict = text['morph_analysis'].to_records()
    _sort_morph_analysis_records( results_dict )
    _sort_morph_analysis_records( expected_records )
    # Check results
    assert expected_records == results_dict


def test_default_morph_analysis_on_empty_input():
    text = Text("")
    text.analyse('morphology')
    # Check results
    assert [] == text['morph_analysis'].to_records()

