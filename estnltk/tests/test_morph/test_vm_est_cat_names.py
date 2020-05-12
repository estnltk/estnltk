from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import VabamorfAnalyzer

from estnltk.taggers.morph_analysis.vm_est_cat_names import VabamorfEstCatNames

from estnltk.converters import dict_to_layer, layer_to_dict

# ----------------------------------

def test_converting_vm_category_names_to_estonian():
    # Test: converting Vabamorf's category names to Estonian
    #       (for educational purposes)
    # Case 1
    # Create text with default morph analysis
    text=Text('Sõbralik müüja tatsas rahulikult külmiku juurde.')
    text.tag_layer(['morph_analysis'])
    # Translate categories to Estonian
    translator = VabamorfEstCatNames()
    translator.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict(text.morph_analysis_est) )
    expected_layer_dict = \
    {'ambiguous': True,
     'attributes': ('normaliseeritud_sõne',
                    'algvorm',
                    'lõpp',
                    'sõnaliik',
                    'vormi_nimetus',
                    'kliitik'),
     'enveloping': None,
     'meta': {},
     'name': 'morph_analysis_est',
     'parent': 'morph_analysis',
     'serialisation_module': None,
     'spans': [{'annotations': [{'kliitik': '',
                                 'algvorm': 'sõbralik',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'Sõbralik',
                                 'sõnaliik': 'omadussõna algvõrre',
                                 'vormi_nimetus': 'ainsus nimetav (nominatiiv)'}],
                'base_span': (0, 8)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': 'müüja',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'müüja',
                                 'sõnaliik': 'nimisõna',
                                 'vormi_nimetus': 'ainsus nimetav (nominatiiv)'}],
                'base_span': (9, 14)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': 'tatsama',
                                 'lõpp': 's',
                                 'normaliseeritud_sõne': 'tatsas',
                                 'sõnaliik': 'tegusõna',
                                 'vormi_nimetus': 'kindel kõneviis lihtminevik 3. '
                                                  'isik ainsus aktiiv jaatav '
                                                  'kõne'}],
                'base_span': (15, 21)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': 'rahulikult',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'rahulikult',
                                 'sõnaliik': 'määrsõna',
                                 'vormi_nimetus': ''}],
                'base_span': (22, 32)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': 'külmik',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'külmiku',
                                 'sõnaliik': 'nimisõna',
                                 'vormi_nimetus': 'ainsus omastav (genitiiv)'}],
                'base_span': (33, 40)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': 'juurde',
                                 'lõpp': '0',
                                 'normaliseeritud_sõne': 'juurde',
                                 'sõnaliik': 'kaassõna',
                                 'vormi_nimetus': ''}],
                'base_span': (41, 47)},
               {'annotations': [{'kliitik': '',
                                 'algvorm': '.',
                                 'lõpp': '',
                                 'normaliseeritud_sõne': '.',
                                 'sõnaliik': 'lausemärk',
                                 'vormi_nimetus': ''}],
                'base_span': (47, 48)}]}
    assert expected_layer_dict == layer_to_dict( text.morph_analysis_est )

# ----------------------------------

def test_converting_vm_category_names_to_estonian_with_empty_annotations():
    # Test: converting Vabamorf's category names to Estonian 
    #       (annotations can include empty ones)
    # Case 1
    # Create text with morph analysis without guessing
    analyzer = VabamorfAnalyzer(guess=False,propername=False)
    text = Text("Ma tahax minna järve ääde")
    text.tag_layer(['words', 'sentences'])
    analyzer.tag(text)
    # Translate categories to Estonian
    translator = VabamorfEstCatNames()
    translator.tag(text)
    #from pprint import pprint
    #pprint( layer_to_dict(text.morph_analysis_est) )
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normaliseeritud_sõne',
                        'algvorm',
                        'lõpp',
                        'sõnaliik',
                        'vormi_nimetus',
                        'kliitik'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis_est',
         'parent': 'morph_analysis',
         'serialisation_module': None,
         'spans': [{'annotations': [{'kliitik': '',
                                     'algvorm': 'mina',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'Ma',
                                     'sõnaliik': 'asesõna',
                                     'vormi_nimetus': 'ainsus nimetav (nominatiiv)'}],
                    'base_span': (0, 2)},
                   {'annotations': [{'kliitik': None,
                                     'algvorm': None,
                                     'lõpp': None,
                                     'normaliseeritud_sõne': None,
                                     'sõnaliik': None,
                                     'vormi_nimetus': None}],
                    'base_span': (3, 8)},
                   {'annotations': [{'kliitik': '',
                                     'algvorm': 'minema',
                                     'lõpp': 'a',
                                     'normaliseeritud_sõne': 'minna',
                                     'sõnaliik': 'tegusõna',
                                     'vormi_nimetus': 'infinitiiv jaatav kõne'}],
                    'base_span': (9, 14)},
                   {'annotations': [{'kliitik': '',
                                     'algvorm': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormi_nimetus': 'lühike sisseütlev (aditiiv)'},
                                    {'kliitik': '',
                                     'algvorm': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormi_nimetus': 'ainsus omastav (genitiiv)'},
                                    {'kliitik': '',
                                     'algvorm': 'järv',
                                     'lõpp': '0',
                                     'normaliseeritud_sõne': 'järve',
                                     'sõnaliik': 'nimisõna',
                                     'vormi_nimetus': 'ainsus osastav (partitiiv)'}],
                    'base_span': (15, 20)},
                   {'annotations': [{'kliitik': None,
                                     'algvorm': None,
                                     'lõpp': None,
                                     'normaliseeritud_sõne': None,
                                     'sõnaliik': None,
                                     'vormi_nimetus': None}],
                    'base_span': (21, 25)}]}
    assert expected_layer_dict == layer_to_dict( text.morph_analysis_est )

