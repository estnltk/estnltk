import pytest

from estnltk import Text
from estnltk.taggers import CompoundWordTagger

from estnltk.converters import layer_to_dict, dict_to_layer


def test_compound_word_tagger_smoke():
    # A smoke test on a simple input 
    # Initialize compound word annotator
    cw_tagger = CompoundWordTagger()
    
    text = Text('Kaubahoovi edelanurgas, rehepeksumasina tagaluugi kõrval. Seal on kosmoselaev. VÄLK-JA-PAUK!')
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    
    expected_layer_dict = \
        {'ambiguous': True,
         'attributes': ('normalized_text', 'subwords'),
         'enveloping': None,
         'meta': {},
         'name': 'compound_words',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_text': 'Kaubahoovi',
                                     'subwords': ['Kauba', 'hoovi']}],
                    'base_span': (0, 10)},
                   {'annotations': [{'normalized_text': 'edelanurgas',
                                     'subwords': ['edela', 'nurgas']}],
                    'base_span': (11, 22)},
                   {'annotations': [{'normalized_text': ',', 'subwords': [',']}],
                    'base_span': (22, 23)},
                   {'annotations': [{'normalized_text': 'rehepeksumasina',
                                     'subwords': ['rehe', 'peksu', 'masina']}],
                    'base_span': (24, 39)},
                   {'annotations': [{'normalized_text': 'tagaluugi',
                                     'subwords': ['taga', 'luugi']}],
                    'base_span': (40, 49)},
                   {'annotations': [{'normalized_text': 'kõrval',
                                     'subwords': ['kõrval']}],
                    'base_span': (50, 56)},
                   {'annotations': [{'normalized_text': '.', 'subwords': ['.']}],
                    'base_span': (56, 57)},
                   {'annotations': [{'normalized_text': 'Seal', 'subwords': ['Seal']}],
                    'base_span': (58, 62)},
                   {'annotations': [{'normalized_text': 'on', 'subwords': ['on']}],
                    'base_span': (63, 65)},
                   {'annotations': [{'normalized_text': 'kosmoselaev',
                                     'subwords': ['kosmose', 'laev']}],
                    'base_span': (66, 77)},
                   {'annotations': [{'normalized_text': '.', 'subwords': ['.']}],
                    'base_span': (77, 78)},
                   {'annotations': [{'normalized_text': 'VÄLK-JA-PAUK',
                                     'subwords': ['VÄLK', 'JA', 'PAUK']}],
                    'base_span': (79, 91)},
                   {'annotations': [{'normalized_text': '!', 'subwords': ['!']}],
                    'base_span': (91, 92)}]}
    #from pprint import pprint
    #pprint( layer_to_dict( text[cw_tagger.output_layer] ) )
    assert layer_to_dict( text[cw_tagger.output_layer] ) == expected_layer_dict


def _whitespace_words_tokenization(text):
    # Performs whitespace tokenization on input
    from estnltk.taggers import WhiteSpaceTokensTagger
    from estnltk.taggers import PretokenizedTextCompoundTokensTagger
    # Initialize tools for white space tokenization
    tokens_tagger = WhiteSpaceTokensTagger()
    compound_tokens_tagger = PretokenizedTextCompoundTokensTagger()
    # Perform word tokenization
    tokens_tagger.tag(text)
    compound_tokens_tagger.tag(text)
    text.tag_layer('words') # join tokens and compound_tokens layers
    return text


def test_compound_word_tagger_error_cases():
    # Test on some cases that were erroneous/problematic at the first run
    # Initialize compound word annotator
    cw_tagger = CompoundWordTagger()

    # Case 1:  
    #  Problem: Vabamorf tags "Online'ile" --> 'Online’' + 'le' 
    #           ( infix 'i' is missing from the ending )
    text = Text('Päevaleht Online\'ile')
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    annotations = \
        [ (a['normalized_text'], a['subwords']) for w in text[cw_tagger.output_layer] for a in w.annotations ]
    #from pprint import pprint
    #pprint(annotations)
    expected_annotations = \
        [('Päevaleht', ['Päeva', 'leht']),
         ('Päevaleht', ['Päevaleht']),
         ("Online'ile", ["Online'ile"])]
    assert annotations == expected_annotations

    # Case 2:  
    #  Problem: Vabamorf tags 'ekspress.ee.' --> 'ekspress.ee' 
    #           ( '.' is missing from the ending )
    text = Text('Jah , kirjutab ekspress.ee.')
    text = _whitespace_words_tokenization(text)
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    annotations = \
        [ (a['normalized_text'], a['subwords']) for w in text[cw_tagger.output_layer] for a in w.annotations ]
    #from pprint import pprint
    #pprint(annotations)
    expected_annotations = \
        [('Jah', ['Jah']),
         (',', [',']),
         ('kirjutab', ['kirjutab']),
         ('ekspress.ee.', ['ekspress.ee.'])]
    assert annotations == expected_annotations

    # Cases 3:  
    #  Problem: Vabamorf tags 'õlikatastrooof' --> 'õli_katastroof',
    #                         'noorloooma' --> 'noor_looma',
    #                         'Clermont-Ferrand\'is' -> 'Clermont_Ferrand'+'s'
    text = Text('Kohutav õlikatastrooof morjendas noorloooma Clermont-Ferrand\'is.')
    text = _whitespace_words_tokenization(text)
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    annotations = \
        [ (a['normalized_text'], a['subwords']) for w in text[cw_tagger.output_layer] for a in w.annotations ]
    #from pprint import pprint
    #pprint(annotations)
    expected_annotations = \
        [('Kohutav', ['Kohutav']),
         ('õlikatastrooof', ['õli', 'katastrooof']),
         ('morjendas', ['morjendas']),
         ('noorloooma', ['noor', 'loooma']),
         ("Clermont-Ferrand'is.", ['Clermont', "Ferrand'is."])]
    assert annotations == expected_annotations

    # Case 4:  triple-hyphen is normalized to ['', '', '', ''] by Vabamorf
    text = Text('kuid matemaatika mõttes väga lai --- puudutab lineaaralgebrat , rühmateooriat , diferentsiaalgeomeetriat')
    text = _whitespace_words_tokenization(text)
    text.tag_layer( cw_tagger.input_layers )
    cw_tagger.tag( text )
    annotations = \
        [ (a['normalized_text'], a['subwords']) for w in text[cw_tagger.output_layer] for a in w.annotations ]
    #from pprint import pprint
    #pprint(annotations)
    expected_annotations = \
        [('kuid', ['kuid']),
         ('matemaatika', ['matemaatika']),
         ('mõttes', ['mõttes']),
         ('väga', ['väga']),
         ('lai', ['lai']),
         ('---', ['---']),
         ('puudutab', ['puudutab']),
         ('lineaaralgebrat', ['lineaar', 'algebrat']),
         (',', [',']),
         ('rühmateooriat', ['rühma', 'teooriat']),
         (',', [',']),
         ('diferentsiaalgeomeetriat', ['diferentsiaal', 'geomeetriat'])]
    assert annotations == expected_annotations