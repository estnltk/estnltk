from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import VabamorfAnalyzer

from estnltk.taggers.morph_analysis.vm_est_cat_names import VabamorfEstCategories

from estnltk.converters import dict_to_layer, layer_to_dict

# ----------------------------------

def test_converting_vm_category_names_for_estonian():
    # Test: converting Vabamorf's category names to Estonian
    #       (for educational purposes)
    # Case 1
    # Create text with default morph analysis
    text=Text('Sõbralik müüja tatsas rahulikult külmiku juurde.')
    text.tag_layer(['morph_analysis'])
    # Translate categories to Estonian
    translator = VabamorfEstCategories()
    translator.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict(text.morph_analysis_est) )
    expected_layer_dict = \
    {'ambiguous': True,
     'attributes': ('normaliseeritud_sõne',
                    'lemma',
                    'lõpp',
                    'sõnaliik',
                    'vormitunnused',
                    'kliitik'),
     'enveloping': None,
     'meta': {},
     'name': 'morph_analysis_est',
     'parent': 'morph_analysis',
     'serialisation_module': None,
     'spans': [{'annotations': [{'kliitik': '',
                                 'lemma': 'sõbralik',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'Sõbralik',
                                 'sõnaliik': 'omadussõna algvõrre',
                                 'vormitunnused': 'ainsus nimetav (nominatiiv)'}],
                'base_span': (0, 8)},
               {'annotations': [{'kliitik': '',
                                 'lemma': 'müüja',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'müüja',
                                 'sõnaliik': 'nimisõna',
                                 'vormitunnused': 'ainsus nimetav (nominatiiv)'}],
                'base_span': (9, 14)},
               {'annotations': [{'kliitik': '',
                                 'lemma': 'tatsama',
                                 'lõpp': 's',
                                 'normaliseeritud_sõne': 'tatsas',
                                 'sõnaliik': 'tegusõna',
                                 'vormitunnused': 'kindel kõneviis lihtminevik 3. '
                                                  'isik ainsus aktiiv jaatav '
                                                  'kõne'}],
                'base_span': (15, 21)},
               {'annotations': [{'kliitik': '',
                                 'lemma': 'rahulikult',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'rahulikult',
                                 'sõnaliik': 'määrsõna',
                                 'vormitunnused': ''}],
                'base_span': (22, 32)},
               {'annotations': [{'kliitik': '',
                                 'lemma': 'külmik',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'külmiku',
                                 'sõnaliik': 'nimisõna',
                                 'vormitunnused': 'ainsus omastav (genitiiv)'}],
                'base_span': (33, 40)},
               {'annotations': [{'kliitik': '',
                                 'lemma': 'juurde',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'juurde',
                                 'sõnaliik': 'kaassõna',
                                 'vormitunnused': ''}],
                'base_span': (41, 47)},
               {'annotations': [{'kliitik': '',
                                 'lemma': '.',
                                 'lõpp': '',
                                 'normaliseeritud_sõne': '.',
                                 'sõnaliik': 'lausemärk',
                                 'vormitunnused': ''}],
                'base_span': (47, 48)}]}
    assert expected_layer_dict == layer_to_dict( text.morph_analysis_est )

# ----------------------------------

def test_converting_vm_category_names_for_estonian_with_empty_annotations():
    # Test: converting Vabamorf's category names to Estonian 
    #       (annotations can include empty ones)
    # Case 1
    # Create text with morph analysis without guessing
    analyzer = VabamorfAnalyzer(guess=False,propername=False)
    text = Text("Ma tahax minna järve ääde")
    text.tag_layer(['words', 'sentences'])
    analyzer.tag(text)
    # Translate categories to Estonian
    translator = VabamorfEstCategories()
    translator.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict(text.morph_analysis_est) )
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normaliseeritud_sõne',
                        'lemma',
                        'lõpp',
                        'sõnaliik',
                        'vormitunnused',
                        'kliitik'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis_est',
         'parent': 'morph_analysis',
         'serialisation_module': None,
         'spans': [{'annotations': [{'kliitik': '',
                                     'lemma': 'mina',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'Ma',
                                     'sõnaliik': 'asesõna',
                                     'vormitunnused': 'ainsus nimetav (nominatiiv)'}],
                    'base_span': (0, 2)},
                   {'annotations': [{'kliitik': None,
                                     'lemma': None,
                                     'lõpp': None,
                                     'normaliseeritud_sõne': None,
                                     'sõnaliik': None,
                                     'vormitunnused': None}],
                    'base_span': (3, 8)},
                   {'annotations': [{'kliitik': '',
                                     'lemma': 'minema',
                                     'lõpp': 'a',
                                     'normaliseeritud_sõne': 'minna',
                                     'sõnaliik': 'tegusõna',
                                     'vormitunnused': 'infinitiiv jaatav kõne'}],
                    'base_span': (9, 14)},
                   {'annotations': [{'kliitik': '',
                                     'lemma': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormitunnused': 'lühike sisseütlev (aditiiv)'},
                                    {'kliitik': '',
                                     'lemma': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormitunnused': 'ainsus omastav (genitiiv)'},
                                    {'kliitik': '',
                                     'lemma': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormitunnused': 'ainsus osastav (partitiiv)'}],
                    'base_span': (15, 20)},
                   {'annotations': [{'kliitik': None,
                                     'lemma': None,
                                     'lõpp': None,
                                     'normaliseeritud_sõne': None,
                                     'sõnaliik': None,
                                     'vormitunnused': None}],
                    'base_span': (21, 25)}]}
    assert expected_layer_dict == layer_to_dict( text.morph_analysis_est )

