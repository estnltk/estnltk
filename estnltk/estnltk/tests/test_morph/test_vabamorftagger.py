from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import CompoundTokenTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.resolve_layer_dag import make_resolver
from estnltk_core.layer import AmbiguousAttributeList

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

def test_analyse_segmentation_and_morphology():
    # Analysing first for 'segmentation', and then for 'morphology'
    # should not produce any errors 
    # (no errors due to missing dependencies)
    text = Text('Tere, maailm!')
    text.analyse('segmentation')
    text.analyse('morphology')
    assert 'morph_analysis' in text.layers


def test_default_morph_analysis():
    # Case 1
    text = Text("Aga kõik juhtus iseenesest.")
    text.analyse('morphology')
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Aga', 'root': 'aga', 'ending': '0', 'start': 0, 'form': '', 'lemma': 'aga', 'root_tokens': ['aga',], 'partofspeech': 'J', 'clitic': '', 'end': 3}], \
        [{'normalized_text': 'kõik', 'root': 'kõik', 'ending': '0', 'start': 4, 'form': 'pl n', 'lemma': 'kõik', 'root_tokens': ['kõik',], 'partofspeech': 'P', 'clitic': '', 'end': 8}, \
         {'normalized_text': 'kõik', 'root': 'kõik', 'ending': '0', 'start': 4, 'form': 'sg n', 'lemma': 'kõik', 'root_tokens': ['kõik',], 'partofspeech': 'P', 'clitic': '', 'end': 8}], \
        [{'normalized_text': 'juhtus', 'root': 'juhtu', 'ending': 's', 'start': 9, 'form': 's', 'lemma': 'juhtuma', 'root_tokens': ['juhtu',], 'partofspeech': 'V', 'clitic': '', 'end': 15}], \
        [{'normalized_text': 'iseenesest', 'root': 'ise_enesest', 'ending': '0', 'start': 16, 'form': '', 'lemma': 'iseenesest', 'root_tokens': ['ise', 'enesest'], 'partofspeech': 'D', 'clitic': '', 'end': 26}], \
        [{'normalized_text': '.', 'root': '.', 'ending': '', 'start': 26, 'form': '', 'lemma': '.', 'root_tokens': ['.',], 'partofspeech': 'Z', 'clitic': '', 'end': 27}] ]
    # Check results
    assert expected_records == text['morph_analysis'].to_records()
    assert AmbiguousAttributeList([['J'], ['P', 'P'], ['V'], ['D'], ['Z']], 'partofspeech') == text.partofspeech
    
    # Case 2 (contains ambiguities that should be resolved)
    text = Text("Kärbes hulbib mees ja naeris puhub sädelevaid mulle.")
    text.analyse('morphology')
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Kärbes', 'partofspeech': 'S', 'root': 'kärbes', 'start': 0, 'clitic': '', 'end': 6, 'root_tokens': ['kärbes',], 'lemma': 'kärbes', 'ending': '0', 'form': 'sg n'}], \
        [{'normalized_text': 'hulbib', 'partofspeech': 'V', 'root': 'hulpi', 'start': 7, 'clitic': '', 'end': 13, 'root_tokens': ['hulpi',], 'lemma': 'hulpima', 'ending': 'b', 'form': 'b'}], \
        [{'normalized_text': 'mees', 'partofspeech': 'S', 'root': 'mees', 'start': 14, 'clitic': '', 'end': 18, 'root_tokens': ['mees',], 'lemma': 'mees', 'ending': '0', 'form': 'sg n'}], \
        [{'normalized_text': 'ja', 'partofspeech': 'J', 'root': 'ja', 'start': 19, 'clitic': '', 'end': 21, 'root_tokens': ['ja',], 'lemma': 'ja', 'ending': '0', 'form': ''}], \
        [{'normalized_text': 'naeris', 'partofspeech': 'V', 'root': 'naer', 'start': 22, 'clitic': '', 'end': 28, 'root_tokens': ['naer',], 'lemma': 'naerma', 'ending': 'is', 'form': 's'}], \
        [{'normalized_text': 'puhub', 'partofspeech': 'V', 'root': 'puhu', 'start': 29, 'clitic': '', 'end': 34, 'root_tokens': ['puhu',], 'lemma': 'puhuma', 'ending': 'b', 'form': 'b'}], \
        [{'normalized_text': 'sädelevaid', 'partofspeech': 'A', 'root': 'sädelev', 'start': 35, 'clitic': '', 'end': 45, 'root_tokens': ['sädelev',], 'lemma': 'sädelev', 'ending': 'id', 'form': 'pl p'}], \
        [{'normalized_text': 'mulle', 'partofspeech': 'P', 'root': 'mina', 'start': 46, 'clitic': '', 'end': 51, 'root_tokens': ['mina',], 'lemma': 'mina', 'ending': 'lle', 'form': 'sg all'}], \
        [{'normalized_text': '.', 'partofspeech': 'Z', 'root': '.', 'start': 51, 'clitic': '', 'end': 52, 'root_tokens': ['.',], 'lemma': '.', 'ending': '', 'form': ''}]]
    # Note that this example sentence is a little out of the ordinary and 
    # hence the bad performance of disambiguator. The more 'normal' your 
    # text is, the better the results.
    # Check results
    assert expected_records == text['morph_analysis'].to_records()

    text = Text('<ANONYM id="14" type="per" morph="_H_ sg n"/>').tag_layer(['morph_analysis'])
    assert text.morph_analysis[0].parent is not None


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
    text.pop_layer('morph_analysis')
    # Create a new layer without disambiguation
    text.tag_layer(resolver=resolver)['morph_analysis']
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Kärbes', 'root_tokens': ['Kärbes',], 'lemma': 'Kärbes', 'root': 'Kärbes', 'clitic': '', 'ending': '0', 'end': 6, 'start': 0, 'form': 'sg n', 'partofspeech': 'H', '_ignore': False},\
         {'normalized_text': 'Kärbes', 'root_tokens': ['Kärbe',], 'lemma': 'Kärbe', 'root': 'Kärbe', 'clitic': '', 'ending': 's', 'end': 6, 'start': 0, 'form': 'sg in', 'partofspeech': 'H', '_ignore': False},\
         {'normalized_text': 'Kärbes', 'root_tokens': ['kärbes',], 'lemma': 'kärbes', 'root': 'kärbes', 'clitic': '', 'ending': '0', 'end': 6, 'start': 0, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False}], \
        [{'normalized_text': 'hulbib', 'root_tokens': ['hulpi',], 'lemma': 'hulpima', 'root': 'hulpi', 'clitic': '', 'ending': 'b', 'end': 13, 'start': 7, 'form': 'b', 'partofspeech': 'V', '_ignore': False}], \
        [{'normalized_text': 'mees', 'root_tokens': ['mesi',], 'lemma': 'mesi', 'root': 'mesi', 'clitic': '', 'ending': 's', 'end': 18, 'start': 14, 'form': 'sg in', 'partofspeech': 'S', '_ignore': False}, \
         {'normalized_text': 'mees', 'root_tokens': ['mees',], 'lemma': 'mees', 'root': 'mees', 'clitic': '', 'ending': '0', 'end': 18, 'start': 14, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False}], \
        [{'normalized_text': 'ja', 'root_tokens': ['ja',], 'lemma': 'ja', 'root': 'ja', 'clitic': '', 'ending': '0', 'end': 21, 'start': 19, 'form': '', 'partofspeech': 'J', '_ignore': False}], \
        [{'normalized_text': 'naeris', 'root_tokens': ['naeris',], 'lemma': 'naeris', 'root': 'naeris', 'clitic': '', 'ending': '0', 'end': 28, 'start': 22, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False},\
         {'normalized_text': 'naeris', 'root_tokens': ['naer',], 'lemma': 'naerma', 'root': 'naer', 'clitic': '', 'ending': 'is', 'end': 28, 'start': 22, 'form': 's', 'partofspeech': 'V', '_ignore': False},\
         {'normalized_text': 'naeris', 'root_tokens': ['naeris',], 'lemma': 'naeris', 'root': 'naeris', 'clitic': '', 'ending': 's', 'end': 28, 'start': 22, 'form': 'sg in', 'partofspeech': 'S', '_ignore': False}], \
        [{'normalized_text': 'puhub', 'root_tokens': ['puhu',], 'lemma': 'puhuma', 'root': 'puhu', 'clitic': '', 'ending': 'b', 'end': 34, 'start': 29, 'form': 'b', 'partofspeech': 'V', '_ignore': False}], \
        [{'normalized_text': 'sädelevaid', 'root_tokens': ['sädelev',], 'lemma': 'sädelev', 'root': 'sädelev', 'clitic': '', 'ending': 'id', 'end': 45, 'start': 35, 'form': 'pl p', 'partofspeech': 'A', '_ignore': False}], \
        [{'normalized_text': 'mulle', 'root_tokens': ['mina',], 'lemma': 'mina', 'root': 'mina', 'clitic': '', 'ending': 'lle', 'end': 51, 'start': 46, 'form': 'sg all', 'partofspeech': 'P', '_ignore': False}, \
         {'normalized_text': 'mulle', 'root_tokens': ['mulle',], 'lemma': 'mulle', 'root': 'mulle', 'clitic': '', 'ending': '0', 'end': 51, 'start': 46, 'form': 'sg n', 'partofspeech': 'S', '_ignore': False},\
         {'normalized_text': 'mulle', 'root_tokens': ['mull',], 'lemma': 'mull', 'root': 'mull', 'clitic': '', 'ending': 'e', 'end': 51, 'start': 46, 'form': 'pl p', 'partofspeech': 'S', '_ignore': False}], \
        [{'normalized_text': '.', 'root_tokens': ['.',], 'lemma': '.', 'root': '.', 'clitic': '', 'ending': '', 'end': 52, 'start': 51, 'form': '', 'partofspeech': 'Z', '_ignore': False}]]
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
        [{'normalized_text': 'Ida-Euroopas', 'partofspeech': 'H', 'ending': 's', 'root_tokens': ['Ida', 'Euroopa'], 'end': 12, 'clitic': '', 'start': 0, 'lemma': 'Ida-Euroopa', 'form': 'sg in', 'root': 'Ida-Euroopa'}], \
        [{'normalized_text': 'sai', 'partofspeech': 'V', 'ending': 'i', 'root_tokens': ['saa',], 'end': 16, 'clitic': '', 'start': 13, 'lemma': 'saama', 'form': 's', 'root': 'saa'}], \
        [{'normalized_text': 'valmis', 'partofspeech': 'A', 'ending': '0', 'root_tokens': ['valmis',], 'end': 23, 'clitic': '', 'start': 17, 'lemma': 'valmis', 'form': '', 'root': 'valmis'}], \
        [{'normalized_text': 'Parlament', 'partofspeech': 'S', 'ending': '0', 'root_tokens': ['parlament',], 'end': 33, 'clitic': '', 'start': 24, 'lemma': 'parlament', 'form': 'sg n', 'root': 'parlament'}], \
        [{'normalized_text': ',', 'partofspeech': 'Z', 'ending': '', 'root_tokens': [',',], 'end': 34, 'clitic': '', 'start': 33, 'lemma': ',', 'form': '', 'root': ','}], \
        [{'normalized_text': 'suure', 'partofspeech': 'A', 'ending': '0', 'root_tokens': ['suur',], 'end': 40, 'clitic': '', 'start': 35, 'lemma': 'suur', 'form': 'sg g', 'root': 'suur'}], \
        [{'normalized_text': 'algustähega', 'partofspeech': 'S', 'ending': 'ga', 'root_tokens': ['algus', 'täht'], 'end': 52, 'clitic': '', 'start': 41, 'lemma': 'algustäht', 'form': 'sg kom', 'root': 'algus_täht'}], \
        [{'normalized_text': '.', 'partofspeech': 'Z', 'ending': '', 'root_tokens': ['.',], 'end': 53, 'clitic': '', 'start': 52, 'lemma': '.', 'form': '', 'root': '.'}]]
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
    text.pop_layer('morph_analysis')
    # Create a new layer without guessing
    text.tag_layer(resolver=resolver)['morph_analysis']
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Sa', 'lemma': 'sina', 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'P', 'end': 2, 'root_tokens': ['sina',], 'root': 'sina', 'start': 0, '_ignore': False}], \
        [{'normalized_text': 'ajad', 'lemma': 'aeg', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'S', 'end': 7, 'root_tokens': ['aeg',], 'root': 'aeg', 'start': 3, '_ignore': False}, \
         {'normalized_text': 'ajad', 'lemma': 'ajama', 'ending': 'd', 'clitic': '', 'form': 'd', 'partofspeech': 'V', 'end': 7, 'root_tokens': ['aja',], 'root': 'aja', 'start': 3, '_ignore': False}], \
        [{'normalized_text': None, 'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 13, 'lemma': None, 'start': 8, 'root_tokens': None, 'ending': None}],\
        [{'normalized_text': 'inimmeste', 'lemma': 'inimmest', 'ending': 'e', 'clitic': '', 'form': 'pl p', 'partofspeech': 'S', 'end': 23, 'root_tokens': ['inim', 'mest'], 'root': 'inim_mest', 'start': 14, '_ignore': False}], \
        [{'normalized_text': 'erinevad', 'lemma': 'erinema', 'ending': 'vad', 'clitic': '', 'form': 'vad', 'partofspeech': 'V', 'end': 32, 'root_tokens': ['erine',], 'root': 'erine', 'start': 24, '_ignore': False}, \
         {'normalized_text': 'erinevad', 'lemma': 'erinev', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'A', 'end': 32, 'root_tokens': ['erinev',], 'root': 'erinev', 'start': 24, '_ignore': False}], \
        [{'normalized_text': 'käsitlusviisid', 'lemma': 'käsitlusviis', 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'S', 'end': 47, 'root_tokens': ['käsitlus', 'viis'], 'root': 'käsitlus_viis', 'start': 33, '_ignore': False}], \
        [{'normalized_text': 'ja', 'lemma': 'ja', 'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'J', 'end': 50, 'root_tokens': ['ja',], 'root': 'ja', 'start': 48, '_ignore': False}], \
        [{'normalized_text': None, 'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 66, 'lemma': None, 'start': 51, 'root_tokens': None, 'ending': None}],\
        [{'normalized_text': None, 'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 74, 'lemma': None, 'start': 67, 'root_tokens': None, 'ending': None}],\
        [{'normalized_text': 'vahekorra', 'lemma': 'vahekord', 'ending': '0', 'clitic': '', 'form': 'sg g', 'partofspeech': 'S', 'end': 84, 'root_tokens': ['vahe', 'kord'], 'root': 'vahe_kord', 'start': 75, '_ignore': False}],\
        [{'normalized_text': None, 'clitic': None, '_ignore': False, 'form': None, 'root': None, 'partofspeech': None, 'end': 85, 'lemma': None, 'start': 84, 'root_tokens': None, 'ending': None}] ]
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
    text.pop_layer('morph_analysis')
    # Create a new layer without guessing
    text.tag_layer(resolver=resolver)['morph_analysis']
    assert AmbiguousAttributeList([['tüdruk'], ['mine'], [None], [None]], 'root') == text.root
    assert AmbiguousAttributeList([['tüdruk'], ['minema'], [None], [None]], 'lemma') == text.lemma
    assert AmbiguousAttributeList([['S'], ['V'], [None], [None]], 'partofspeech') == text.partofspeech
    
    # Case 3
    # Use VabamorfTagger
    morph_analyser = VabamorfTagger(disambiguate=False, guess=False, propername=False)
    text = Text("Ma tahax minna järve ääde")
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    #print( text['morph_analysis'].to_records() )
    expected_records = [ \
        [{'normalized_text': 'Ma', 'partofspeech': 'P', 'lemma': 'mina', 'form': 'sg n', 'root_tokens': ['mina',], 'ending': '0', 'end': 2, 'clitic': '', 'start': 0, 'root': 'mina', '_ignore': False}], \
        [{'normalized_text': None, 'ending': None, 'start': 3, 'lemma': None, 'form': None, 'root_tokens': None, '_ignore': False, 'root': None, 'clitic': None, 'end': 8, 'partofspeech': None}], \
        [{'normalized_text': 'minna', 'partofspeech': 'V', 'lemma': 'minema', 'form': 'da', 'root_tokens': ['mine',], 'ending': 'a', 'end': 14, 'clitic': '', 'start': 9, 'root': 'mine', '_ignore': False}], \
        [{'normalized_text': 'järve', 'partofspeech': 'S', 'lemma': 'järv', 'form': 'adt', 'root_tokens': ['järv',], 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}, \
         {'normalized_text': 'järve','partofspeech': 'S', 'lemma': 'järv', 'form': 'sg g', 'root_tokens': ['järv',], 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}, \
         {'normalized_text': 'järve','partofspeech': 'S', 'lemma': 'järv', 'form': 'sg p', 'root_tokens': ['järv',], 'ending': '0', 'end': 20, 'clitic': '', 'start': 15, 'root': 'järv', '_ignore': False}],\
        [{'normalized_text': None, 'ending': None, 'start': 21, 'lemma': None, 'form': None, 'root_tokens': None, '_ignore': False, 'root': None, 'clitic': None, 'end': 25, 'partofspeech': None}], \
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
        [{'normalized_text': 'Mis', 'end': 3, 'partofspeech': 'P', 'start': 0, 'root_tokens': ['mis',], 'lemma': 'mis', 'ending': '0', 'root': 'mis', 'form': 'pl n', 'clitic': ''}, \
         {'normalized_text': 'Mis', 'end': 3, 'partofspeech': 'P', 'start': 0, 'root_tokens': ['mis',], 'lemma': 'mis', 'ending': '0', 'root': 'mis', 'form': 'sg n', 'clitic': ''}], \
        [{'normalized_text': 'lilli', 'end': 10, 'partofspeech': 'S', 'start': 4, 'root_tokens': ['lill',], 'lemma': 'lill', 'ending': 'i', 'root': 'lill', 'form': 'pl p', 'clitic': ''}], \
        [{'normalized_text': 'müüs', 'end': 15, 'partofspeech': 'V', 'start': 11, 'root_tokens': ['müü',], 'lemma': 'müüma', 'ending': 's', 'root': 'müü', 'form': 's', 'clitic': ''}], \
        [{'normalized_text': 'Tiit', 'end': 20, 'partofspeech': 'H', 'start': 16, 'root_tokens': ['Tiit',], 'lemma': 'Tiit', 'ending': '0', 'root': 'Tiit', 'form': 'sg n', 'clitic': ''}], \
        [{'normalized_text': "Mac'ile", 'end': 28, 'partofspeech': 'H', 'start': 21, 'root_tokens': ['Mac',], 'lemma': 'Mac', 'ending': 'le', 'root': 'Mac', 'form': 'sg all', 'clitic': ''}], \
        [{'normalized_text': "10'e", 'end': 33, 'partofspeech': 'S', 'start': 29, 'root_tokens': ['10',], 'lemma': '10', 'ending': '0', 'root': '10', 'form': 'sg g', 'clitic': ''}], \
        [{'normalized_text': 'krooniga', 'end': 42, 'partofspeech': 'S', 'start': 34, 'root_tokens': ['kroon',], 'lemma': 'kroon', 'ending': 'ga', 'root': 'kroon', 'form': 'sg kom', 'clitic': ''}], \
        [{'normalized_text': '?', 'end': 43, 'partofspeech': 'Z', 'start': 42, 'root_tokens': ['?',], 'lemma': '?', 'ending': '', 'root': '?', 'form': '', 'clitic': ''}]]
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


def test_default_morph_analysis_with_different_output_layer_name():
    # Should be able to use a different output layer name 
    # without running into errors
    morph_analyser = VabamorfTagger(output_layer='my_morph')
    text = Text('Tere, maailm!')
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    # Check results
    assert 'my_morph' in text.layers


def test_default_morph_analysis_with_different_input_layer_names():
    # Should be able to use a different input layer names
    # without running into errors
    # 1) Initialize taggers with custom names 
    cp_tagger = CompoundTokenTagger(output_layer='my_compounds')
    word_tagger = WordTagger( input_compound_tokens_layer='my_compounds',
                              output_layer='my_words' )
    sentence_tokenizer = SentenceTokenizer( 
                              input_compound_tokens_layer='my_compounds',
                              input_words_layer='my_words',
                              output_layer='my_sentences' )
    morph_analyser = VabamorfTagger(
                              output_layer='my_morph',
                              input_words_layer='my_words',
                              input_sentences_layer='my_sentences',
                              input_compound_tokens_layer='my_compounds' )
    # 2) Analyse
    text = Text('Tere, maailm! Kuidas siis läheb?')
    text.tag_layer(['tokens'])
    cp_tagger.tag(text)
    word_tagger.tag(text)
    sentence_tokenizer.tag(text)
    morph_analyser.tag(text)
    # Check results
    for layer in ['my_compounds', 'my_words', 'my_sentences', 'my_morph']:
        assert layer in text.layers


def test_default_morph_analysis_on_detached_layers():
    # Should be able to use a different input layer names
    # and work only on detached layers 
    # 1) Initialize taggers with custom names 
    cp_tagger = CompoundTokenTagger(output_layer='my_compounds')
    word_tagger = WordTagger( input_compound_tokens_layer='my_compounds',
                              output_layer='my_words' )
    sentence_tokenizer = SentenceTokenizer( 
                              input_compound_tokens_layer='my_compounds',
                              input_words_layer='my_words',
                              output_layer='my_sentences' )
    morph_analyser = VabamorfTagger(
                              output_layer='my_morph',
                              input_words_layer='my_words',
                              input_sentences_layer='my_sentences',
                              input_compound_tokens_layer='my_compounds' )
    # 2) Make detached layers
    text = Text('Tere, maailm! Kuidas siis on?')
    text.tag_layer('tokens')
    cp_tokens_layer = cp_tagger.make_layer(text, {'tokens':text['tokens']})
    words_layer = word_tagger.make_layer(text,   {'tokens':text['tokens'],\
                                                  'my_compounds' :cp_tokens_layer})
    sentences_layer = sentence_tokenizer.make_layer(text, {'my_words' : words_layer,
                                                           'my_compounds' :cp_tokens_layer})
    morph_layer = morph_analyser.make_layer(text, {'my_words' : words_layer,\
                                                   'my_compounds' : cp_tokens_layer,\
                                                   'my_sentences' : sentences_layer})
    # Check results
    raw_analyses = []
    for span in morph_layer:
        raw_analyses.append( [(a.text, a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    #print( raw_analyses )
    expected_raw_analyses = \
        [ [('Tere', 'tere', 'I', '')], 
          [(',', ',', 'Z', '')], 
          [('maailm', 'maa_ilm', 'S', 'sg n')], 
          [('!', '!', 'Z', '')], 
          [('Kuidas', 'kuidas', 'D', '')], 
          [('siis', 'siis', 'D', '')], 
          [('on', 'ole', 'V', 'b'), ('on', 'ole', 'V', 'vad')], 
          [('?', '?', 'Z', '')] ]
    assert expected_raw_analyses == raw_analyses


def test_default_morph_analysis_with_textbased_disambiguation():
    text = Text('Ott sai teise koha ja tahab nüüd ka Kuldgloobust. Mis koht see on? '+\
                'Kas Otil jätkub tarmukust teisest kohast kõrgemale tõusta? Ott lubas pingutada. '+\
                'Võib-olla tuleks siiski teha Kuldgloobuse eesti variant.')
    text.tag_layer(['words', 'sentences'])
    #
    # 1) Add morph analysis without text-based disambiguation
    #
    morph_tagger_no_textbased_disamb = VabamorfTagger(predisambiguate=False,
                                                      postdisambiguate=False)
    morph_tagger_no_textbased_disamb.tag( text )
    no_tbd_raw_analyses = []
    for span in text['morph_analysis']:
        no_tbd_raw_analyses.append( [(a.text, a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    #
    # 2) Add morph analysis with text-based disambiguation
    #
    morph_tagger_textbased_disamb = VabamorfTagger(output_layer='morph_analysis_textbased_disamb',
                                                   predisambiguate =True,
                                                   postdisambiguate=True)
    morph_tagger_textbased_disamb.tag( text )
    tbd_raw_analyses = []
    for span in text['morph_analysis_textbased_disamb']:
        tbd_raw_analyses.append( [(a.text, a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    #
    # Get differences
    #
    textbased_corrections = []
    for no_tbd_analysis, tbd_analysis in zip(no_tbd_raw_analyses, tbd_raw_analyses):
        if no_tbd_analysis != tbd_analysis:
            textbased_corrections.append( {'old':no_tbd_analysis, 'new': tbd_analysis} )
    #print( textbased_corrections )
    #
    # Validate differences
    #
    expected_textbased_corrections = [ \
       {'old': [('Ott', 'ott', 'S', 'sg n')], 'new': [('Ott', 'Ott', 'H', 'sg n')]}, \
       {'old': [('koha', 'koht', 'S', 'sg g'), ('koha', 'koha', 'S', 'sg g')], 'new': [('koha', 'koht', 'S', 'sg g')]}, \
       {'old': [('Kuldgloobust', 'kuld_gloobus', 'S', 'sg p')], 'new': [('Kuldgloobust', 'Kuld_gloobus', 'H', 'sg p')]}, \
       {'old': [('Otil', 'ott', 'S', 'sg ad')], 'new': [('Otil', 'Ott', 'H', 'sg ad')]}, \
       {'old': [('kohast', 'koht', 'S', 'sg el'), ('kohast', 'koha', 'S', 'sg el')], 'new': [('kohast', 'koht', 'S', 'sg el')]}, \
       {'old': [('Ott', 'ott', 'S', 'sg n')], 'new': [('Ott', 'Ott', 'H', 'sg n')]}, \
       {'old': [('Kuldgloobuse', 'kuld_gloobus', 'S', 'sg g')], 'new': [('Kuldgloobuse', 'Kuld_gloobus', 'H', 'sg g')]} ]
    assert expected_textbased_corrections == textbased_corrections


def test_default_morph_with_vm_src_update_2020_04_07():
    # Test effects of the Vabamorf's source update from 2020_04_07
    # ( default lexicon )
    morph_analyser = VabamorfTagger(output_layer='my_morph')
    text = Text('Pole olnd või toimund ulatuslikku metasomatoosi vms protsessi.')
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    analyses = []
    for span in text.my_morph:
        analyses.append( [(a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    expected_analyses = \
      [ [('ole', 'V', 'neg o')], 
        [('ole', 'V', 'nud')], 
        [('või', 'J', '')], 
        [('toimunu', 'S', 'pl n')], 
        [('ulatuslik', 'A', 'sg p')], 
        [('metasomatoos', 'S', 'sg p')], 
        [('vms', 'Y', '?')], 
        [('protsess', 'S', 'sg p')], 
        [('.', 'Z', '')] ]
    assert expected_analyses == analyses



from estnltk.vabamorf.morf import VM_LEXICONS
from estnltk.vabamorf.morf import Vabamorf as VabamorfInstance

def test_no_spell_morph_with_vm_src_update_2020_04_07():
    # Test effects of the Vabamorf's source update from 2020_04_07
    # ( newly added nosp [no-spell] improvements to the lexicon )
    # 1) Test that nosp lexicon is available
    nosp_lexicons = [lex_dir for lex_dir in VM_LEXICONS if lex_dir.endswith('_nosp')]
    assert len(nosp_lexicons) > 0
    # 2.1) Test using the last nosp lexicon:
    #      Provide nosp lexicon via VabamorfInstance
    vm_instance    = VabamorfInstance( lexicon_dir=nosp_lexicons[-1] )
    morph_analyser = VabamorfTagger(output_layer='morph_nosp', vm_instance=vm_instance)
    text = Text('Bemmiga paarutanud pandikunn kadus kippelt kirbukale.')
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    analyses = []
    for span in text.morph_nosp:
        analyses.append( [(a.text, a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    expected_analyses = \
        [[('Bemmiga', 'bemm', 'S', 'sg kom')], 
         [('paarutanud', 'paaruta', 'V', 'nud'), ('paarutanud', 'paaruta=nud', 'A', ''), ('paarutanud', 'paaruta=nud', 'A', 'sg n'), ('paarutanud', 'paaruta=nud', 'A', 'pl n')], 
         [('pandikunn', 'pandi_kunn', 'S', 'sg n')], 
         [('kadus', 'kadu', 'V', 's')], 
         [('kippelt', 'kippelt', 'D', '')], 
         [('kirbukale', 'kirbukas', 'S', 'sg all')], 
         [('.', '.', 'Z', '')]]
    assert expected_analyses == analyses
    # 2.2) Test using the last nosp lexicon:
    #      Set slang_lex parameter
    morph_analyser_2 = VabamorfTagger(output_layer='morph_nosp_2', slang_lex=True)
    text = Text('Bemmiga paarutanud pandikunn kadus kippelt kirbukale.')
    text.tag_layer(['words', 'sentences'])
    morph_analyser_2.tag(text)
    analyses = []
    for span in text.morph_nosp_2:
        analyses.append( [(a.text, a['root'],a['partofspeech'],a['form']) for a in span.annotations] )
    assert expected_analyses == analyses


