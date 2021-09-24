import pytest

from estnltk_core import Layer
from estnltk_core import Text
from estnltk_core.layer import AttributeList
from estnltk_core.layer.base_span import ElementaryBaseSpan


@pytest.mark.xfail(reason="TODO needs fixing")
def test_pickle():
    import pickle

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
    text.nonempty_layer.add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text.nonempty_layer.add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    for layer in result.layers:
        assert result[layer] == text[layer]

    text = Text('Tavaline analüüsitud teksti serialiseerimine.').analyse('all')
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
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
    text.add_layer(Layer('nonempty_layer', attributes=['text', 'layer', 'espan']))
    text.nonempty_layer.add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text.nonempty_layer)
    text.nonempty_layer[0].espan = text.nonempty_layer[0]
    text.add_layer(Layer('text', attributes=['text', 'layer', 'espan']))
    text['text'].add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text['text'], espan=None)
    text['text'][0].espan = text['text'][0]
    text['text'].add_annotation(ElementaryBaseSpan(5, 8), text=text, layer=text.nonempty_layer, espan=None)
    text['text'][1].espan = text.nonempty_layer[0]
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    assert len(result.empty_layer) == 0
    assert len(result.nonempty_layer) == len(text.nonempty_layer)
    for i in range(len(result.nonempty_layer)):
        assert result.nonempty_layer[i].base_span == text.nonempty_layer[i].base_span
    assert result.nonempty_layer[0]['text'] is result
    assert result.nonempty_layer[0]['layer'] is result.nonempty_layer
    assert result.nonempty_layer[0]['espan'] is result.nonempty_layer[0]
    assert len(result['text']) == len(text['text'])
    for i in range(len(result['text'])):
        assert result['text'][i].base_span == text['text'][i].base_span
    assert result['text'][0]['text'] is result
    assert result['text'][0]['layer'] is result['text']
    assert result['text'][0]['espan'] is result['text'][0]
    assert result['text'][1]['text'] is result
    assert result['text'][1]['layer'] is result['nonempty_layer']
    assert result['text'][1]['espan'] is result['nonempty_layer'][0]


@pytest.mark.xfail(reason="TODO needs fixing")
def test_to_records():
    text = Text('Olnud aeg.').tag_layer()

    # ambiguous
    assert (text['morph_analysis'].to_records()) == [
        [{'normalized_text': 'Olnud', 'root': 'ole', 'lemma': 'olema', 'form': 'nud', 'ending': 'nud', 'root_tokens': ['ole'], 'partofspeech': 'V',
          'start': 0, 'end': 5, 'clitic': ''}, 
         {'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': '', 'ending': '0', 'root_tokens': ['olnud'], 'partofspeech': 'A',
          'start': 0, 'end': 5, 'clitic': ''},
         {'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': 'sg n', 'ending': '0', 'root_tokens': ['olnud'],
          'partofspeech': 'A', 'start': 0, 'end': 5, 'clitic': ''},
         {'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': 'pl n', 'ending': 'd', 'root_tokens': ['olnud'],
          'partofspeech': 'A', 'start': 0, 'end': 5, 'clitic': ''}],
        [{'normalized_text': 'aeg', 'root': 'aeg', 'lemma': 'aeg', 'form': 'sg n', 'ending': '0', 'root_tokens': ['aeg'], 'partofspeech': 'S',
          'start': 6, 'end': 9, 'clitic': ''}],
        [{'normalized_text': '.', 'root': '.', 'lemma': '.', 'form': '', 'ending': '', 'root_tokens': ['.'], 'partofspeech': 'Z', 'start': 9,
          'end': 10, 'clitic': ''}]]


    if not text['words'].ambiguous:
        # base
        assert (text['words'].to_records() == [{'start': 0, 'end': 5, 'normalized_form': None},
                                               {'start': 6, 'end': 9, 'normalized_form': None},
                                               {'start': 9, 'end': 10, 'normalized_form': None}])
        # enveloping (note nested lists)
        assert (text['sentences'].to_records() == [
            [{'end': 5, 'start': 0, 'normalized_form': None}, {'end': 9, 'start': 6, 'normalized_form': None},
             {'end': 10, 'start': 9, 'normalized_form': None}]])
    else:
        # base
        assert (text['words'].to_records() == [[{'start': 0, 'end': 5, 'normalized_form': None}],
                                               [{'start': 6, 'end': 9, 'normalized_form': None}],
                                               [{'start': 9, 'end': 10, 'normalized_form': None}]])
        # enveloping (note double nested lists)
        assert (text['sentences'].to_records() == [
            [[{'end': 5, 'start': 0, 'normalized_form': None}], [{'end': 9, 'start': 6, 'normalized_form': None}],
             [{'end': 10, 'start': 9, 'normalized_form': None}]]])


@pytest.mark.xfail(reason="TODO needs fixing")
def test_to_record():
    t = Text('Minu nimi on Uku.').tag_layer()

    # siin on kaks võimalikku (ja põhjendatavat) käitumist.

    # esimene
    # assert t.words.morph_analysis.to_records() == t.words.to_records()

    # või teine
    # assert t.words.morph_analysis.to_records() == t.morph_analysis.to_records()

    # teine tundub veidi loogilisem, aga piisavalt harv vajadus ja piisavalt tülikas implementeerida, et valida esimene
    # alati saab teha lihtsalt
    assert t.morph_analysis.to_records() == [[{'normalized_text': 'Minu',
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
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words', attributes=['lemma'])
    t.add_layer(words)
    words.from_records([{'end': 3, 'lemma': 'kui', 'start': 0},
                        {'end': 8, 'lemma': 'mitu', 'start': 4},
                        {'end': 13, 'lemma': 'kuu', 'start': 9},
                        {'end': 16, 'lemma': 'olema', 'start': 14},
                        {'end': 23, 'lemma': 'aasta', 'start': 17},
                        {'end': 24, 'lemma': '?', 'start': 23}]
                       )

    for span, lemma in zip(t.words, ['kui', 'mitu', 'kuu', 'olema', 'aasta', '?']):
        print(span.lemma, lemma)
        assert span.lemma == lemma


def test_ambiguous_from_dict():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words', attributes=['lemma'], ambiguous=True)
    t.add_layer(words)

    words.from_records([
        [{'end': 3, 'lemma': 'kui', 'start': 0}, {'end': 3, 'lemma': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma': 'olema', 'start': 14}],
        [{'end': 23, 'lemma': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma': '?', 'start': 23}]
    ]
    )

    assert t.words[0].lemma == AttributeList(['kui', 'KUU'], 'lemma')


def test_ambiguous_from_dict_unbound():
    words = Layer(name='words', attributes=['lemma'], ambiguous=True)

    # We create the layer
    words.from_records([
        [{'end': 3, 'lemma': 'kui', 'start': 0}, {'end': 3, 'lemma': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma': 'olema', 'start': 14}],
        [{'end': 23, 'lemma': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma': '?', 'start': 23}]
    ]
    )

    # then we bind it to an object
    t = Text('Kui mitu kuud on aastas?')
    t.add_layer(words)

    assert t.words[0].lemma == AttributeList(['kui', 'KUU'], 'lemma')

    words2 = Layer(name='words2', attributes=['lemma2'], ambiguous=True, parent='words')
    # We create the layer
    words2.from_records([
        [{'end': 3, 'lemma2': 'kui', 'start': 0}, {'end': 3, 'lemma2': 'KUU', 'start': 0}],
        [{'end': 8, 'lemma2': 'mitu', 'start': 4}],
        [{'end': 13, 'lemma2': 'kuu', 'start': 9}],
        [{'end': 16, 'lemma2': 'olema', 'start': 14}],
        [{'end': 23, 'lemma2': 'aasta', 'start': 17}],
        [{'end': 24, 'lemma2': '?', 'start': 23}]
    ]
    )
    t.add_layer(words2)
    assert t.words2[0].lemma2 == AttributeList(['kui', 'KUU'], 'lemma2')

    assert t.words2[0].parent is t.words[0]
