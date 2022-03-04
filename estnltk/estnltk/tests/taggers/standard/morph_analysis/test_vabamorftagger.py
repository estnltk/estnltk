from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import CompoundTokenTagger
from estnltk.taggers import WordTagger
from estnltk.taggers import SentenceTokenizer
from estnltk.default_resolver import make_resolver
from estnltk_core.converters import layer_to_dict

from estnltk_core.tests import create_amb_attribute_list


def test_default_morph_analysis():
    # Case 1
    text = Text("Aga kõik juhtus iseenesest.")
    text.tag_layer('morph_analysis')
    # Check results
    assert 'morph_analysis' in text.layers
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'aga',
                                     'normalized_text': 'Aga',
                                     'partofspeech': 'J',
                                     'root': 'aga',
                                     'root_tokens': ['aga']}],
                    'base_span': (0, 3)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'pl n',
                                     'lemma': 'kõik',
                                     'normalized_text': 'kõik',
                                     'partofspeech': 'P',
                                     'root': 'kõik',
                                     'root_tokens': ['kõik']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'kõik',
                                     'normalized_text': 'kõik',
                                     'partofspeech': 'P',
                                     'root': 'kõik',
                                     'root_tokens': ['kõik']}],
                    'base_span': (4, 8)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 's',
                                     'lemma': 'juhtuma',
                                     'normalized_text': 'juhtus',
                                     'partofspeech': 'V',
                                     'root': 'juhtu',
                                     'root_tokens': ['juhtu']}],
                    'base_span': (9, 15)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'iseenesest',
                                     'normalized_text': 'iseenesest',
                                     'partofspeech': 'D',
                                     'root': 'ise_enesest',
                                     'root_tokens': ['ise', 'enesest']}],
                    'base_span': (16, 26)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (26, 27)}]}
    
    # Case 2 (contains ambiguities that should be resolved)
    text = Text("Kärbes hulbib mees ja naeris puhub sädelevaid mulle.")
    text.tag_layer('morph_analysis')
    # Check results
    # Note that this example sentence is a little out of the ordinary and 
    # hence the bad performance of disambiguator. The more 'normal' your 
    # text is, the better the results.
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'kärbes',
                                     'normalized_text': 'Kärbes',
                                     'partofspeech': 'S',
                                     'root': 'kärbes',
                                     'root_tokens': ['kärbes']}],
                    'base_span': (0, 6)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'b',
                                     'form': 'b',
                                     'lemma': 'hulpima',
                                     'normalized_text': 'hulbib',
                                     'partofspeech': 'V',
                                     'root': 'hulpi',
                                     'root_tokens': ['hulpi']}],
                    'base_span': (7, 13)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mees',
                                     'normalized_text': 'mees',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']}],
                    'base_span': (14, 18)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ja',
                                     'normalized_text': 'ja',
                                     'partofspeech': 'J',
                                     'root': 'ja',
                                     'root_tokens': ['ja']}],
                    'base_span': (19, 21)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'is',
                                     'form': 's',
                                     'lemma': 'naerma',
                                     'normalized_text': 'naeris',
                                     'partofspeech': 'V',
                                     'root': 'naer',
                                     'root_tokens': ['naer']}],
                    'base_span': (22, 28)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'b',
                                     'form': 'b',
                                     'lemma': 'puhuma',
                                     'normalized_text': 'puhub',
                                     'partofspeech': 'V',
                                     'root': 'puhu',
                                     'root_tokens': ['puhu']}],
                    'base_span': (29, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'id',
                                     'form': 'pl p',
                                     'lemma': 'sädelev',
                                     'normalized_text': 'sädelevaid',
                                     'partofspeech': 'A',
                                     'root': 'sädelev',
                                     'root_tokens': ['sädelev']}],
                    'base_span': (35, 45)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'lle',
                                     'form': 'sg all',
                                     'lemma': 'mina',
                                     'normalized_text': 'mulle',
                                     'partofspeech': 'P',
                                     'root': 'mina',
                                     'root_tokens': ['mina']}],
                    'base_span': (46, 51)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (51, 52)}]}

    # Case 3
    text = Text('<ANONYM id="14" type="per" morph="_H_ sg n"/>').tag_layer( 'morph_analysis' )
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
    # Check results ( morph should be ambiguous )
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech',
                        '_ignore'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'Kärbe',
                                     'normalized_text': 'Kärbes',
                                     'partofspeech': 'H',
                                     'root': 'Kärbe',
                                     'root_tokens': ['Kärbe']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'Kärbes',
                                     'normalized_text': 'Kärbes',
                                     'partofspeech': 'H',
                                     'root': 'Kärbes',
                                     'root_tokens': ['Kärbes']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'kärbes',
                                     'normalized_text': 'Kärbes',
                                     'partofspeech': 'S',
                                     'root': 'kärbes',
                                     'root_tokens': ['kärbes']}],
                    'base_span': (0, 6)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'b',
                                     'form': 'b',
                                     'lemma': 'hulpima',
                                     'normalized_text': 'hulbib',
                                     'partofspeech': 'V',
                                     'root': 'hulpi',
                                     'root_tokens': ['hulpi']}],
                    'base_span': (7, 13)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mees',
                                     'normalized_text': 'mees',
                                     'partofspeech': 'S',
                                     'root': 'mees',
                                     'root_tokens': ['mees']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'mesi',
                                     'normalized_text': 'mees',
                                     'partofspeech': 'S',
                                     'root': 'mesi',
                                     'root_tokens': ['mesi']}],
                    'base_span': (14, 18)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ja',
                                     'normalized_text': 'ja',
                                     'partofspeech': 'J',
                                     'root': 'ja',
                                     'root_tokens': ['ja']}],
                    'base_span': (19, 21)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'is',
                                     'form': 's',
                                     'lemma': 'naerma',
                                     'normalized_text': 'naeris',
                                     'partofspeech': 'V',
                                     'root': 'naer',
                                     'root_tokens': ['naer']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'naeris',
                                     'normalized_text': 'naeris',
                                     'partofspeech': 'S',
                                     'root': 'naeris',
                                     'root_tokens': ['naeris']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'naeris',
                                     'normalized_text': 'naeris',
                                     'partofspeech': 'S',
                                     'root': 'naeris',
                                     'root_tokens': ['naeris']}],
                    'base_span': (22, 28)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'b',
                                     'form': 'b',
                                     'lemma': 'puhuma',
                                     'normalized_text': 'puhub',
                                     'partofspeech': 'V',
                                     'root': 'puhu',
                                     'root_tokens': ['puhu']}],
                    'base_span': (29, 34)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'id',
                                     'form': 'pl p',
                                     'lemma': 'sädelev',
                                     'normalized_text': 'sädelevaid',
                                     'partofspeech': 'A',
                                     'root': 'sädelev',
                                     'root_tokens': ['sädelev']}],
                    'base_span': (35, 45)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'e',
                                     'form': 'pl p',
                                     'lemma': 'mull',
                                     'normalized_text': 'mulle',
                                     'partofspeech': 'S',
                                     'root': 'mull',
                                     'root_tokens': ['mull']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': 'lle',
                                     'form': 'sg all',
                                     'lemma': 'mina',
                                     'normalized_text': 'mulle',
                                     'partofspeech': 'P',
                                     'root': 'mina',
                                     'root_tokens': ['mina']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mulle',
                                     'normalized_text': 'mulle',
                                     'partofspeech': 'S',
                                     'root': 'mulle',
                                     'root_tokens': ['mulle']}],
                    'base_span': (46, 51)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (51, 52)}]}


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
    text.tag_layer('morph_analysis', resolver=resolver)
    # Check results
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 'sg in',
                                     'lemma': 'Ida-Euroopa',
                                     'normalized_text': 'Ida-Euroopas',
                                     'partofspeech': 'H',
                                     'root': 'Ida-Euroopa',
                                     'root_tokens': ['Ida', 'Euroopa']}],
                    'base_span': (0, 12)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'i',
                                     'form': 's',
                                     'lemma': 'saama',
                                     'normalized_text': 'sai',
                                     'partofspeech': 'V',
                                     'root': 'saa',
                                     'root_tokens': ['saa']}],
                    'base_span': (13, 16)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'valmis',
                                     'normalized_text': 'valmis',
                                     'partofspeech': 'A',
                                     'root': 'valmis',
                                     'root_tokens': ['valmis']}],
                    'base_span': (17, 23)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'parlament',
                                     'normalized_text': 'Parlament',
                                     'partofspeech': 'S',
                                     'root': 'parlament',
                                     'root_tokens': ['parlament']}],
                    'base_span': (24, 33)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': ',',
                                     'normalized_text': ',',
                                     'partofspeech': 'Z',
                                     'root': ',',
                                     'root_tokens': [',']}],
                    'base_span': (33, 34)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'suur',
                                     'normalized_text': 'suure',
                                     'partofspeech': 'A',
                                     'root': 'suur',
                                     'root_tokens': ['suur']}],
                    'base_span': (35, 40)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'ga',
                                     'form': 'sg kom',
                                     'lemma': 'algustäht',
                                     'normalized_text': 'algustähega',
                                     'partofspeech': 'S',
                                     'root': 'algus_täht',
                                     'root_tokens': ['algus', 'täht']}],
                    'base_span': (41, 52)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '.',
                                     'normalized_text': '.',
                                     'partofspeech': 'Z',
                                     'root': '.',
                                     'root_tokens': ['.']}],
                    'base_span': (52, 53)}]}


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
    # Check results: unknown words appear as annotations filled with None 
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech',
                        '_ignore'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'sina',
                                     'normalized_text': 'Sa',
                                     'partofspeech': 'P',
                                     'root': 'sina',
                                     'root_tokens': ['sina']}],
                    'base_span': (0, 2)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'aeg',
                                     'normalized_text': 'ajad',
                                     'partofspeech': 'S',
                                     'root': 'aeg',
                                     'root_tokens': ['aeg']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': 'd',
                                     'form': 'd',
                                     'lemma': 'ajama',
                                     'normalized_text': 'ajad',
                                     'partofspeech': 'V',
                                     'root': 'aja',
                                     'root_tokens': ['aja']}],
                    'base_span': (3, 7)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (8, 13)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'e',
                                     'form': 'pl p',
                                     'lemma': 'inimmest',
                                     'normalized_text': 'inimmeste',
                                     'partofspeech': 'S',
                                     'root': 'inim_mest',
                                     'root_tokens': ['inim', 'mest']}],
                    'base_span': (14, 23)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'vad',
                                     'form': 'vad',
                                     'lemma': 'erinema',
                                     'normalized_text': 'erinevad',
                                     'partofspeech': 'V',
                                     'root': 'erine',
                                     'root_tokens': ['erine']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'erinev',
                                     'normalized_text': 'erinevad',
                                     'partofspeech': 'A',
                                     'root': 'erinev',
                                     'root_tokens': ['erinev']}],
                    'base_span': (24, 32)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'd',
                                     'form': 'pl n',
                                     'lemma': 'käsitlusviis',
                                     'normalized_text': 'käsitlusviisid',
                                     'partofspeech': 'S',
                                     'root': 'käsitlus_viis',
                                     'root_tokens': ['käsitlus', 'viis']}],
                    'base_span': (33, 47)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'ja',
                                     'normalized_text': 'ja',
                                     'partofspeech': 'J',
                                     'root': 'ja',
                                     'root_tokens': ['ja']}],
                    'base_span': (48, 50)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (51, 66)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (67, 74)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'vahekord',
                                     'normalized_text': 'vahekorra',
                                     'partofspeech': 'S',
                                     'root': 'vahe_kord',
                                     'root_tokens': ['vahe', 'kord']}],
                    'base_span': (75, 84)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (84, 85)}]}
    
    # Case 2
    # Create text and tag all
    text = Text("Tüdrukud läksid poodelungile.").tag_layer()  
    # Remove old morph layer
    text.pop_layer('morph_analysis')
    # Create a new layer without guessing
    text.tag_layer(resolver=resolver)['morph_analysis']
    assert create_amb_attribute_list([['tüdruk'], ['mine'], [None], [None]], 'root') == text.root
    assert create_amb_attribute_list([['tüdruk'], ['minema'], [None], [None]], 'lemma') == text.lemma
    assert create_amb_attribute_list([['S'], ['V'], [None], [None]], 'partofspeech') == text.partofspeech
    
    # Case 3
    # Use VabamorfTagger
    morph_analyser = VabamorfTagger(disambiguate=False, guess=False, propername=False)
    text = Text("Ma tahax minna järve ääde")
    text.tag_layer(['words', 'sentences'])
    morph_analyser.tag(text)
    # Check results
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech',
                        '_ignore'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mina',
                                     'normalized_text': 'Ma',
                                     'partofspeech': 'P',
                                     'root': 'mina',
                                     'root_tokens': ['mina']}],
                    'base_span': (0, 2)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (3, 8)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': 'a',
                                     'form': 'da',
                                     'lemma': 'minema',
                                     'normalized_text': 'minna',
                                     'partofspeech': 'V',
                                     'root': 'mine',
                                     'root_tokens': ['mine']}],
                    'base_span': (9, 14)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'adt',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']},
                                    {'_ignore': False,
                                     'clitic': '',
                                     'ending': '0',
                                     'form': 'sg p',
                                     'lemma': 'järv',
                                     'normalized_text': 'järve',
                                     'partofspeech': 'S',
                                     'root': 'järv',
                                     'root_tokens': ['järv']}],
                    'base_span': (15, 20)},
                   {'annotations': [{'_ignore': False,
                                     'clitic': None,
                                     'ending': None,
                                     'form': None,
                                     'lemma': None,
                                     'normalized_text': None,
                                     'partofspeech': None,
                                     'root': None,
                                     'root_tokens': None}],
                    'base_span': (21, 25)}]}


def test_default_morph_analysis_on_compound_tokens():
    # Case 1
    text = Text("Mis lil-li müüs Tiit Mac'ile 10'e krooniga?")
    text.tag_layer('morph_analysis')
    #from pprint import pprint
    #pprint( layer_to_dict( text['morph_analysis'] ) )
    # Check results
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'name': 'morph_analysis',
         'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'parent': 'words',
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'mis',
                                     'normalized_text': 'Mis',
                                     'partofspeech': 'P',
                                     'root': 'mis',
                                     'root_tokens': ['mis']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'pl n',
                                     'lemma': 'mis',
                                     'normalized_text': 'Mis',
                                     'partofspeech': 'P',
                                     'root': 'mis',
                                     'root_tokens': ['mis']}],
                    'base_span': (0, 3)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'i',
                                     'form': 'pl p',
                                     'lemma': 'lill',
                                     'normalized_text': 'lilli',
                                     'partofspeech': 'S',
                                     'root': 'lill',
                                     'root_tokens': ['lill']}],
                    'base_span': (4, 10)},
                   {'annotations': [{'clitic': '',
                                     'ending': 's',
                                     'form': 's',
                                     'lemma': 'müüma',
                                     'normalized_text': 'müüs',
                                     'partofspeech': 'V',
                                     'root': 'müü',
                                     'root_tokens': ['müü']}],
                    'base_span': (11, 15)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'Tiit',
                                     'normalized_text': 'Tiit',
                                     'partofspeech': 'H',
                                     'root': 'Tiit',
                                     'root_tokens': ['Tiit']}],
                    'base_span': (16, 20)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'le',
                                     'form': 'sg all',
                                     'lemma': 'Mac',
                                     'normalized_text': "Mac'ile",
                                     'partofspeech': 'H',
                                     'root': 'Mac',
                                     'root_tokens': ['Mac']}],
                    'base_span': (21, 28)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg g',
                                     'lemma': '10',
                                     'normalized_text': "10'e",
                                     'partofspeech': 'S',
                                     'root': '10',
                                     'root_tokens': ['10']}],
                    'base_span': (29, 33)},
                   {'annotations': [{'clitic': '',
                                     'ending': 'ga',
                                     'form': 'sg kom',
                                     'lemma': 'kroon',
                                     'normalized_text': 'krooniga',
                                     'partofspeech': 'S',
                                     'root': 'kroon',
                                     'root_tokens': ['kroon']}],
                    'base_span': (34, 42)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '?',
                                     'normalized_text': '?',
                                     'partofspeech': 'Z',
                                     'root': '?',
                                     'root_tokens': ['?']}],
                    'base_span': (42, 43)}]}


def test_default_morph_analysis_on_empty_input():
    text = Text("")
    text.tag_layer('morph_analysis')
    # Check results
    assert len(text['morph_analysis']) == 0
    assert layer_to_dict( text['morph_analysis'] ) == \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'secondary_attributes': (),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'serialisation_module': None,
         'spans': []}


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


