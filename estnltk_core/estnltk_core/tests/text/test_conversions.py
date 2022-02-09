import pytest

from estnltk_core import Layer
from estnltk_core.common import load_text_class
from estnltk_core.layer.base_span import ElementaryBaseSpan
from estnltk_core.converters import dict_to_layer
from estnltk_core.converters import layer_to_records
from estnltk_core.converters import records_to_layer

from estnltk_core.tests import create_amb_attribute_list

@pytest.mark.filterwarnings("ignore:Attribute names")
def test_pickle():
    import pickle

    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()

    def save_restore(text: Text) -> Text:
        bytes = pickle.dumps(text)
        return pickle.loads(bytes)

    text = Text("Kihtideta teksti serialiseerimine")
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers

    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    for layer in result.layers:
        assert result[layer] == text[layer]

    text = Text("Ümbriskihtidega teksti kopeerimine")
    text.meta = {'a': 15, 'b': 13}
    text.add_layer(Layer('words'))
    text.add_layer(Layer('sentences', enveloping='words'))
    text.add_layer(Layer('paragraphs', enveloping='sentences'))
    text['words'].add_annotation(ElementaryBaseSpan(0, 15))
    text['words'].add_annotation(ElementaryBaseSpan(16, 22))
    text['words'].add_annotation(ElementaryBaseSpan(23, 34))
    text['sentences'].add_annotation( [(0, 15), (16, 22), (23, 34)] )
    text['paragraphs'].add_annotation( [((0, 15), (16, 22), (23, 34),)] )
    assert text['words'].span_level == 0
    assert text['sentences'].span_level == 1
    assert text['paragraphs'].span_level == 2
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    assert result['words'].span_level == 0
    assert result['sentences'].span_level == 1
    assert result['paragraphs'].span_level == 2
    for layer in result.layers:
        assert result[layer] == text[layer]

    text = Text("Rekursiivse metaga teksti kopeerimine")
    text.meta = {'text': text}
    result = save_restore(text)
    assert result.text == text.text
    assert set(result.meta.keys()) == {'text'}
    assert result.meta['text'] is result
    assert result.layers == text.layers
    for layer in result.layers:
        assert result[layer] == text[layer]

    text = Text("Rekursiivsete kihtidega teksti kopeerimine")
    text.add_layer(Layer('empty_layer', attributes=[]))
    with pytest.warns(UserWarning, match='Attribute names.+overlap with Span/Annotation property names.+'):
        text.add_layer(Layer('nonempty_layer', attributes=['text', 'layer', 'espan']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text['nonempty_layer'])
    text['nonempty_layer'][0].espan = text['nonempty_layer'][0]
    with pytest.warns(UserWarning, match='Attribute names.+overlap with Span/Annotation property names.+'):
        text.add_layer(Layer('text', attributes=['text', 'layer', 'espan']))
    text['text'].add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text['text'], espan=None)
    text['text'][0].espan = text['text'][0]
    text['text'].add_annotation(ElementaryBaseSpan(5, 8), text=text, layer=text['nonempty_layer'], espan=None)
    text['text'][1].espan = text['nonempty_layer'][0]
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    assert len(result['empty_layer']) == 0
    assert len(result['nonempty_layer']) == len(text['nonempty_layer'])
    for i in range(len(result['nonempty_layer'])):
        assert result['nonempty_layer'][i].base_span == text['nonempty_layer'][i].base_span
    assert result['nonempty_layer'][0]['text'] is result
    assert result['nonempty_layer'][0]['layer'] is result['nonempty_layer']
    assert result['nonempty_layer'][0]['espan'] is result['nonempty_layer'][0]
    assert len(result['text']) == len(text['text'])
    for i in range(len(result['text'])):
        assert result['text'][i].base_span == text['text'][i].base_span
    assert result['text'][0]['text'] is result
    assert result['text'][0]['layer'] is result['text']
    assert result['text'][0]['espan'] is result['text'][0]
    assert result['text'][1]['text'] is result
    assert result['text'][1]['layer'] is result['nonempty_layer']
    assert result['text'][1]['espan'] is result['nonempty_layer'][0]

def test_to_records():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Minu nimi on Uku.')

    words_layer = dict_to_layer({'name': 'words',
     'attributes': ('normalized_form',),
     'parent': None,
     'enveloping': None,
     'ambiguous': True,
     'serialisation_module': None,
     'meta': {},
     'spans': [{'base_span': (0, 4), 'annotations': [{'normalized_form': None}]},
      {'base_span': (5, 9), 'annotations': [{'normalized_form': None}]},
      {'base_span': (10, 12), 'annotations': [{'normalized_form': None}]},
      {'base_span': (13, 16), 'annotations': [{'normalized_form': None}]},
      {'base_span': (16, 17), 'annotations': [{'normalized_form': None}]}]})
    text.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
 'attributes': (),
 'parent': None,
 'enveloping': 'words',
 'ambiguous': False,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': ((0, 4), (5, 9), (10, 12), (13, 16), (16, 17)),
   'annotations': [{}]}]})
    text.add_layer(sentences_layer)
    tokens_layer = dict_to_layer({'name': 'tokens',
 'attributes': (),
 'parent': None,
 'enveloping': None,
 'ambiguous': False,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (0, 4), 'annotations': [{}]},
  {'base_span': (5, 9), 'annotations': [{}]},
  {'base_span': (10, 12), 'annotations': [{}]},
  {'base_span': (13, 16), 'annotations': [{}]},
  {'base_span': (16, 17), 'annotations': [{}]}]})
    text.add_layer(tokens_layer)
    morph_layer = dict_to_layer({'name': 'morph_analysis',
 'attributes': ('normalized_text',
  'lemma',
  'root',
  'root_tokens',
  'ending',
  'clitic',
  'form',
  'partofspeech'),
 'parent': 'words',
 'enveloping': None,
 'ambiguous': True,
 'serialisation_module': None,
 'meta': {},
 'spans': [{'base_span': (0, 4),
   'annotations': [{'normalized_text': 'Minu',
     'lemma': 'mina',
     'root': 'mina',
     'root_tokens': ['mina'],
     'ending': '0',
     'clitic': '',
     'form': 'sg g',
     'partofspeech': 'P'}]},
  {'base_span': (5, 9),
   'annotations': [{'normalized_text': 'nimi',
     'lemma': 'nimi',
     'root': 'nimi',
     'root_tokens': ['nimi'],
     'ending': '0',
     'clitic': '',
     'form': 'sg n',
     'partofspeech': 'S'}]},
  {'base_span': (10, 12),
   'annotations': [{'normalized_text': 'on',
     'lemma': 'olema',
     'root': 'ole',
     'root_tokens': ['ole'],
     'ending': '0',
     'clitic': '',
     'form': 'b',
     'partofspeech': 'V'},
    {'normalized_text': 'on',
     'lemma': 'olema',
     'root': 'ole',
     'root_tokens': ['ole'],
     'ending': '0',
     'clitic': '',
     'form': 'vad',
     'partofspeech': 'V'}]},
  {'base_span': (13, 16),
   'annotations': [{'normalized_text': 'Uku',
     'lemma': 'Uku',
     'root': 'Uku',
     'root_tokens': ['Uku'],
     'ending': '0',
     'clitic': '',
     'form': 'sg n',
     'partofspeech': 'H'}]},
  {'base_span': (16, 17),
   'annotations': [{'normalized_text': '.',
     'lemma': '.',
     'root': '.',
     'root_tokens': ['.'],
     'ending': '',
     'clitic': '',
     'form': '',
     'partofspeech': 'Z'}]}]})
    text.add_layer(morph_layer)
    compound_tokens_layer = dict_to_layer({'name': 'compound_tokens',
 'attributes': ('type', 'normalized'),
 'parent': None,
 'enveloping': 'tokens',
 'ambiguous': False,
 'serialisation_module': None,
 'meta': {},
 'spans': []})
    text.add_layer(compound_tokens_layer)


    # ambiguous
    assert layer_to_records( text['morph_analysis'] ) == [[{'normalized_text': 'Minu',
   'lemma': 'mina',
   'root': 'mina',
   'root_tokens': ['mina'],
   'ending': '0',
   'clitic': '',
   'form': 'sg g',
   'partofspeech': 'P',
   'start': 0,
   'end': 4}],
 [{'normalized_text': 'nimi',
   'lemma': 'nimi',
   'root': 'nimi',
   'root_tokens': ['nimi'],
   'ending': '0',
   'clitic': '',
   'form': 'sg n',
   'partofspeech': 'S',
   'start': 5,
   'end': 9}],
 [{'normalized_text': 'on',
   'lemma': 'olema',
   'root': 'ole',
   'root_tokens': ['ole'],
   'ending': '0',
   'clitic': '',
   'form': 'b',
   'partofspeech': 'V',
   'start': 10,
   'end': 12},
  {'normalized_text': 'on',
   'lemma': 'olema',
   'root': 'ole',
   'root_tokens': ['ole'],
   'ending': '0',
   'clitic': '',
   'form': 'vad',
   'partofspeech': 'V',
   'start': 10,
   'end': 12}],
 [{'normalized_text': 'Uku',
   'lemma': 'Uku',
   'root': 'Uku',
   'root_tokens': ['Uku'],
   'ending': '0',
   'clitic': '',
   'form': 'sg n',
   'partofspeech': 'H',
   'start': 13,
   'end': 16}],
 [{'normalized_text': '.',
   'lemma': '.',
   'root': '.',
   'root_tokens': ['.'],
   'ending': '',
   'clitic': '',
   'form': '',
   'partofspeech': 'Z',
   'start': 16,
   'end': 17}]]


    if not text['words'].ambiguous:
        # base
        assert layer_to_records( text['words'] ) == [{'normalized_form': None, 'start': 0, 'end': 4},
 {'normalized_form': None, 'start': 5, 'end': 9},
 {'normalized_form': None, 'start': 10, 'end': 12},
 {'normalized_form': None, 'start': 13, 'end': 16},
 {'normalized_form': None, 'start': 16, 'end': 17}]
        # enveloping (note nested lists)
        assert layer_to_records( text['sentences'] ) == [[{'normalized_form': None, 'start': 0, 'end': 4},
  {'normalized_form': None, 'start': 5, 'end': 9},
  {'normalized_form': None, 'start': 10, 'end': 12},
  {'normalized_form': None, 'start': 13, 'end': 16},
  {'normalized_form': None, 'start': 16, 'end': 17}]]
    else:
        # base
        assert layer_to_records( text['words'] ) == [[{'normalized_form': None, 'start': 0, 'end': 4}],
 [{'normalized_form': None, 'start': 5, 'end': 9}],
 [{'normalized_form': None, 'start': 10, 'end': 12}],
 [{'normalized_form': None, 'start': 13, 'end': 16}],
 [{'normalized_form': None, 'start': 16, 'end': 17}]]
        # enveloping (note double nested lists)
        assert layer_to_records( text['sentences'] ) == [[[{'normalized_form': None, 'start': 0, 'end': 4}],
  [{'normalized_form': None, 'start': 5, 'end': 9}],
  [{'normalized_form': None, 'start': 10, 'end': 12}],
  [{'normalized_form': None, 'start': 13, 'end': 16}],
  [{'normalized_form': None, 'start': 16, 'end': 17}]]]


def test_to_record():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Minu nimi on Uku.')

    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 4), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (5, 9), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (10, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 16), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (16, 17), 'annotations': [{'normalized_form': None}]}]})
    t.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 4), (5, 9), (10, 12), (13, 16), (16, 17)),
                                                'annotations': [{}]}]})
    t.add_layer(sentences_layer)
    tokens_layer = dict_to_layer({'name': 'tokens',
                                  'attributes': (),
                                  'parent': None,
                                  'enveloping': None,
                                  'ambiguous': False,
                                  'serialisation_module': None,
                                  'meta': {},
                                  'spans': [{'base_span': (0, 4), 'annotations': [{}]},
                                            {'base_span': (5, 9), 'annotations': [{}]},
                                            {'base_span': (10, 12), 'annotations': [{}]},
                                            {'base_span': (13, 16), 'annotations': [{}]},
                                            {'base_span': (16, 17), 'annotations': [{}]}]})
    t.add_layer(tokens_layer)
    morph_layer = dict_to_layer({'name': 'morph_analysis',
                                 'attributes': ('normalized_text',
                                                'lemma',
                                                'root',
                                                'root_tokens',
                                                'ending',
                                                'clitic',
                                                'form',
                                                'partofspeech'),
                                 'parent': 'words',
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 4),
                                            'annotations': [{'normalized_text': 'Minu',
                                                             'lemma': 'mina',
                                                             'root': 'mina',
                                                             'root_tokens': ['mina'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg g',
                                                             'partofspeech': 'P'}]},
                                           {'base_span': (5, 9),
                                            'annotations': [{'normalized_text': 'nimi',
                                                             'lemma': 'nimi',
                                                             'root': 'nimi',
                                                             'root_tokens': ['nimi'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'S'}]},
                                           {'base_span': (10, 12),
                                            'annotations': [{'normalized_text': 'on',
                                                             'lemma': 'olema',
                                                             'root': 'ole',
                                                             'root_tokens': ['ole'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'},
                                                            {'normalized_text': 'on',
                                                             'lemma': 'olema',
                                                             'root': 'ole',
                                                             'root_tokens': ['ole'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'vad',
                                                             'partofspeech': 'V'}]},
                                           {'base_span': (13, 16),
                                            'annotations': [{'normalized_text': 'Uku',
                                                             'lemma': 'Uku',
                                                             'root': 'Uku',
                                                             'root_tokens': ['Uku'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'H'}]},
                                           {'base_span': (16, 17),
                                            'annotations': [{'normalized_text': '.',
                                                             'lemma': '.',
                                                             'root': '.',
                                                             'root_tokens': ['.'],
                                                             'ending': '',
                                                             'clitic': '',
                                                             'form': '',
                                                             'partofspeech': 'Z'}]}]})
    t.add_layer(morph_layer)
    compound_tokens_layer = dict_to_layer({'name': 'compound_tokens',
                                           'attributes': ('type', 'normalized'),
                                           'parent': None,
                                           'enveloping': 'tokens',
                                           'ambiguous': False,
                                           'serialisation_module': None,
                                           'meta': {},
                                           'spans': []})
    t.add_layer(compound_tokens_layer)

    # siin on kaks võimalikku (ja põhjendatavat) käitumist.

    # esimene
    # assert t.words.morph_analysis.to_records() == t.words.to_records()

    # või teine
    # assert t.words.morph_analysis.to_records() == t.morph_analysis.to_records()

    # teine tundub veidi loogilisem, aga piisavalt harv vajadus ja piisavalt tülikas implementeerida, et valida esimene
    # alati saab teha lihtsalt
    assert layer_to_records( t['morph_analysis'] ) == [[{'normalized_text': 'Minu',
                                               'lemma': 'mina',
                                               'root': 'mina',
                                               'root_tokens': ['mina'],
                                               'ending': '0',
                                               'clitic': '',
                                               'form': 'sg g',
                                               'partofspeech': 'P',
                                               'start': 0,
                                               'end': 4}],
                                             [{'normalized_text': 'nimi',
                                               'lemma': 'nimi',
                                               'root': 'nimi',
                                               'root_tokens': ['nimi'],
                                               'ending': '0',
                                               'clitic': '',
                                               'form': 'sg n',
                                               'partofspeech': 'S',
                                               'start': 5,
                                               'end': 9}],
                                             [{'normalized_text': 'on',
                                               'lemma': 'olema',
                                               'root': 'ole',
                                               'root_tokens': ['ole'],
                                               'ending': '0',
                                               'clitic': '',
                                               'form': 'b',
                                               'partofspeech': 'V',
                                               'start': 10,
                                               'end': 12},
                                              {'normalized_text': 'on',
                                               'lemma': 'olema',
                                               'root': 'ole',
                                               'root_tokens': ['ole'],
                                               'ending': '0',
                                               'clitic': '',
                                               'form': 'vad',
                                               'partofspeech': 'V',
                                               'start': 10,
                                               'end': 12}],
                                             [{'normalized_text': 'Uku',
                                               'lemma': 'Uku',
                                               'root': 'Uku',
                                               'root_tokens': ['Uku'],
                                               'ending': '0',
                                               'clitic': '',
                                               'form': 'sg n',
                                               'partofspeech': 'H',
                                               'start': 13,
                                               'end': 16}],
                                             [{'normalized_text': '.',
                                               'lemma': '.',
                                               'root': '.',
                                               'root_tokens': ['.'],
                                               'ending': '',
                                               'clitic': '',
                                               'form': '',
                                               'partofspeech': 'Z',
                                               'start': 16,
                                               'end': 17}]]

def test_from_dict():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words', attributes=['lemma'])
    t.add_layer(words)
    words = records_to_layer(words, [{'end': 3, 'lemma': 'kui', 'start': 0},
                                     {'end': 8, 'lemma': 'mitu', 'start': 4},
                                     {'end': 13, 'lemma': 'kuu', 'start': 9},
                                     {'end': 16, 'lemma': 'olema', 'start': 14},
                                     {'end': 23, 'lemma': 'aasta', 'start': 17},
                                     {'end': 24, 'lemma': '?', 'start': 23}] )
    for span, lemma in zip(t['words'], ['kui', 'mitu', 'kuu', 'olema', 'aasta', '?']):
        print(span.lemma, lemma)
        assert span.lemma == lemma


def test_ambiguous_from_dict():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words', attributes=['lemma'], ambiguous=True)
    t.add_layer(words)

    words = records_to_layer(words, [ \
        [{'end': 3, 'lemma': 'kui', 'start': 0}, {'end': 3, 'lemma': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma': 'olema', 'start': 14}],
        [{'end': 23, 'lemma': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma': '?', 'start': 23}]
    ])

    assert t['words'][0].lemma == create_amb_attribute_list(['kui', 'KUU'], 'lemma')


def test_ambiguous_from_dict_unbound():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()

    words = Layer(name='words', attributes=['lemma'], ambiguous=True)

    # We create the layer
    words = records_to_layer(words, [ \
        [{'end': 3, 'lemma': 'kui', 'start': 0}, {'end': 3, 'lemma': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma': 'olema', 'start': 14}],
        [{'end': 23, 'lemma': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma': '?', 'start': 23}]
    ])

    # then we bind it to an object
    t = Text('Kui mitu kuud on aastas?')
    t.add_layer(words)

    assert t['words'][0].lemma == create_amb_attribute_list(['kui', 'KUU'], 'lemma')

    words2 = Layer(name='words2', attributes=['lemma2'], ambiguous=True, parent='words')
    # We create the layer
    words2 = records_to_layer(words2, [ \
        [{'end': 3, 'lemma2': 'kui', 'start': 0}, {'end': 3, 'lemma2': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma2': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma2': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma2': 'olema', 'start': 14}],
        [{'end': 23, 'lemma2': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma2': '?', 'start': 23}]
    ]
    )
    t.add_layer(words2)
    assert t['words2'][0].lemma2 == create_amb_attribute_list(['kui', 'KUU'], 'lemma2')

    assert t['words2'][0].parent is t['words'][0]
