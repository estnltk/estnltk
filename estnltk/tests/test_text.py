import pytest

import itertools
from estnltk import Layer
from estnltk import Text
from estnltk import Annotation
from estnltk.layer import AmbiguousAttributeList, AttributeTupleList
from estnltk.layer import AttributeList
from estnltk.tests import new_text


def test_general():
    t = Text('Minu nimi on Uku. Mis Sinu nimi on? Miks me seda arutame?').tag_layer()

    assert isinstance(t.sentences, Layer)
    assert isinstance(t.words, Layer)

    assert len(t.sentences) == 3
    assert len(t.words) == 15
    with pytest.raises(AttributeError):
        t.sentences.words

    assert {'tokens', 'compound_tokens', 'sentences', 'words', 'morph_analysis'} <= set(t.__dict__)

    with pytest.raises(AttributeError):
        t.words.sentences

    assert len(t.words) == len(t.words.text)
    # assert len(t.sentences) == len(t.sentences.text)
    # assert len(t.sentences.words.text) == len(t.sentences.text)
    assert t.morph_analysis.lemma == AmbiguousAttributeList([['mina'], ['nimi'], ['olema', 'olema'], ['Uku'],
                                                             ['.'], ['mis', 'mis'], ['sina'], ['nimi'],
                                                             ['olema', 'olema'], ['?'], ['miks'], ['mina'],
                                                             ['see'], ['arutama'], ['?']],
                                                            'lemma')

    assert len(t.morph_analysis.lemma) == len(t.words)
    assert len(t.morph_analysis) == len(t.words)

    # assert t.words.morph_analysis.lemma == t.words.lemma
    # assert len(t.sentences[1:].words) == len(t.sentences[1:].text)

    # assert len(t.sentences[1:].morph_analysis) == len(t.sentences[1:].text)

    # assert len(t.sentences[:].morph_analysis) == len(t.sentences[:].text)
    # assert t.sentences[:] == t.sentences.span_list
    # assert t.words[:] == t.words.span_list
    # assert (t.words[:].lemma) == (t.words.lemma)
    # assert (t.words[:].text) == (t.words.text)


def test_equivalences():
    t = Text('Minu nimi on Uku, mis sinu nimi on? Miks see üldse oluline on?')

    with pytest.raises(AttributeError):
        t.morph_analysis

    t.tag_layer()
    t.morph_analysis.lemma  # nüüd töötab

    # Text object has attribute access if attributes are unique
    assert t.lemma == t.words.lemma

    assert list(t.sentences.lemma) == [sentence.lemma for sentence in t.sentences]

    assert t.words.text == t.sentences.text

    assert t.morph_analysis.text == t.words.text


def test_equal():
    t_1 = Text('Tekst algab. Tekst lõpeb.')
    t_2 = Text('Tekst algab.')
    assert t_1 != t_2
    t_2 = Text('Tekst algab. Tekst lõpeb.')
    assert t_1 == t_2
    t_1.meta['year'] = 2017
    assert t_1 != t_2
    t_2.meta['year'] = 2017
    assert t_1 == t_2
    t_1.tag_layer(['morph_extended', 'paragraphs'])
    assert t_1 != t_2
    t_2.tag_layer(['morph_extended', 'paragraphs'])
    assert t_1 == t_2
    t_1['morph_analysis'][0].annotations[0].form = 'x'
    assert t_1 != t_2

    t_1 = new_text(5)
    t_2 = new_text(5)
    assert t_1 == t_2
    t_1.layer_5[1].annotations[1].attr_5 = 'bla'
    assert t_1 != t_2


def test_pickle():
    # Text object can be pickled
    import pickle
    t_1 = Text('Tekst algab. Tekst lõpeb.').tag_layer()
    b = pickle.dumps(t_1)
    t_2 = pickle.loads(b)
    assert t_1 == t_2


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


def test_paragraph_tokenizer():
    t = Text('''Minu nimi on Uku. Miks?

Mis sinu nimi on?
    ''').tag_layer(['paragraphs', 'morph_analysis'])

    # Should not raise NotImplementedError
    t.paragraphs
    assert t.paragraphs.text == ['Minu', 'nimi', 'on', 'Uku', '.', 'Miks', '?', 'Mis', 'sinu', 'nimi', 'on', '?']


def test_delete_layer():
    t = Text('Minu nimi on Uku.')
    assert t.layers == {}

    layer_names = 'words sentences morph_analysis'.split()
    t.tag_layer(layer_names)
    assert set(layer_names) <= set(t.layers)
    assert set(layer_names) <= set(t.__dict__)

    # Should not raise NotImplementedError
    # deleting a root lalyer should also delete all its dependants
    del t.tokens

    assert 'tokens' not in t.__dict__
    assert 'compound_tokens' not in t.__dict__

    del t.words

    assert 'words' not in t.__dict__
    assert 'sentences' not in t.__dict__
    assert 'morph_analysis' not in t.__dict__

    assert t.layers == {}

    with pytest.raises(AttributeError):
        t.words

    with pytest.raises(AttributeError):
        t.sentences

    with pytest.raises(AttributeError):
        t.morph_analysis


def test_new_span_hierarchy():
    text = Text('''
    Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.
    Seni vaid soome keelde tõlgitud teos ilmus äsja ka itaalia keeles
    ning seda esitleti Rooma reisikirjanduse festivalil.
    Tuntud reisikrijanduse festival valis tänavu peakülaliseks Eesti,
    Ultima Thule ning Iidse-Põhjala ja Vahemere endisaegsed kultuurikontaktid j
    ust seetõttu, et eelmisel nädalal avaldas kirjastus Gangemi "Hõbevalge"
    itaalia keeles, vahendas "Aktuaalne kaamera".''').tag_layer()
    l = Layer(
            name='layer1',
            parent='words',
            attributes=['test1'],
            text_object=text
    )
    text.add_layer(l)

    for i in text.words:
        l.add_annotation(i, test1='1234')

    l = Layer(
            name='layer2',
            parent='layer1',
            attributes=['test2'],
            text_object=text
    )
    text.add_layer(l)

    for i in text.layer1:
        l.add_annotation(i, test2='12345')

    assert text.layer2[0].parent.layer.name == 'layer1'


def test_text():
    t = Text('test')
    assert t.text == 'test'
    with pytest.raises(AttributeError):
        t.text = 'asd'


def test_layer_1():
    text = Text('')

    layer = Layer(name='test', text_object=text)
    layer.add_annotation((0, 1))

    assert len(layer) == 1
    assert layer[0].start == 0
    assert layer[0].end == 1

    # insertion keeps spans in sorted order
    layer = Layer(name='test')
    layer.add_annotation((1, 2))
    layer.add_annotation((0, 1))
    layer.add_annotation((3, 4))
    layer.add_annotation((2, 3))
    assert layer[0].start == 0
    assert layer[1].start == 1
    assert layer[2].start == 2
    assert layer[3].start == 3


def test_layer():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(name='test')
    t.add_layer(l)

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='text'))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='test'))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name=' '))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='3'))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='assert'))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='is'))

    assert t.layers['test'] is l

    with pytest.raises(AttributeError):
        t.notexisting

    assert t.text == text

    layer = t.test  # type: Layer
    layer.add_annotation((0, 2))
    assert t.test.text == [text[:2]]

    t.test.add_annotation((2, 4))


def test_annotated_layer():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(name='test', attributes=['test', 'asd'])
    t.add_layer(l)
    l.add_annotation((1, 5))

    for i in t.test:
        i.test = 'mock'

    with pytest.raises(AttributeError):
        for i in t.test:
            i.test2 = 'mock'


def test_count_by():
    def count_by(layer, attributes, counter=None):
        from collections import Counter
        if counter is None:
            counter = Counter()

        for span in layer:
            key = []
            for a in attributes:
                if a == 'text':
                    key.append(span.text)
                else:
                    key.append(getattr(span, a))
            key = tuple(key)
            counter[key] += 1

        return counter

    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(name='test', attributes=['test', 'asd'])
    t.add_layer(l)
    l.add_annotation((1, 5))
    l.add_annotation((2, 6))

    for i in l:
        i.asd = 123
        break

    assert (count_by(l, ['text', 'asd'])) == {('ösel', 123): 1, ('sel ', None): 1}


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


def test_dependant_span():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words',
                  attributes=['lemma']
                  ).from_records([{'end': 3, 'lemma': 'kui', 'start': 0},
                                  {'end': 8, 'lemma': 'mitu', 'start': 4},
                                  {'end': 13, 'lemma': 'kuu', 'start': 9},
                                  {'end': 16, 'lemma': 'olema', 'start': 14},
                                  {'end': 23, 'lemma': 'aasta', 'start': 17},
                                  {'end': 24, 'lemma': '?', 'start': 23}],
                                 )
    t.add_layer(words)

    dep = Layer(name='reverse_lemmas',
                parent='words',
                attributes=['revlemma']
                )
    t.add_layer(dep)

    for word in t.words:
        dep.add_annotation(word, revlemma=word.lemma[::-1])

    for i in t.reverse_lemmas:
        assert (i.revlemma == i.words.lemma[::-1])

    # TODO: how should this work?
    # for i in t.words:
    #     assert (i.mark('reverse_lemmas').revlemma == i.lemma[::-1])


def test_enveloping_layer():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(
            name='words',
            attributes=['lemma']

    ).from_records([{'end': 3, 'lemma': 'kui', 'start': 0},
                    {'end': 8, 'lemma': 'mitu', 'start': 4},
                    {'end': 13, 'lemma': 'kuu', 'start': 9},
                    {'end': 16, 'lemma': 'olema', 'start': 14},
                    {'end': 23, 'lemma': 'aasta', 'start': 17},
                    {'end': 24, 'lemma': '?', 'start': 23}],
                   )
    t.add_layer(words)
    wordpairs = Layer(name='wordpairs', enveloping='words')
    t.add_layer(wordpairs)

    wordpairs.add_annotation(t.words[0:2])
    wordpairs.add_annotation(t.words[2:4])
    wordpairs.add_annotation(t.words[4:6])

    print(t.wordpairs.text)
    assert (wordpairs.text == ['Kui', 'mitu', 'kuud', 'on', 'aastas', '?'])

    wordpairs.add_annotation(t.words[1:3])
    wordpairs.add_annotation(t.words[3:5])
    print(t.wordpairs.text)
    assert (wordpairs.text == ['Kui', 'mitu', 'mitu', 'kuud', 'kuud', 'on', 'on', 'aastas', 'aastas', '?'])

    for wordpair in t.wordpairs:
        for word in wordpair.words:
            assert (word)

    for wordpair in t.wordpairs:
        wordpair.words.lemma  # this should not give a keyerror

    # I have changed my mind about what this should raise so much, I'm leaving it free at the moment
    with pytest.raises(Exception):
        for wordpair in t.wordpairs:
            wordpair.nonsense  # this SHOULD give a --keyerror--

    assert (t.words.lemma == AttributeList(['kui', 'mitu', 'kuu', 'olema', 'aasta', '?'], 'lemma'))

    assert ([list(wordpair.words.lemma) for wordpair in t.wordpairs] ==
            [['kui', 'mitu'], ['mitu', 'kuu'], ['kuu', 'olema'], ['olema', 'aasta'], ['aasta', '?']])

    print(t.wordpairs.text)
    with pytest.raises(Exception):
        (wordpairs.test)


def test_various():
    text = Text('Minu nimi on Joosep, mis sinu nimi on? Miks me seda arutame?').tag_layer()

    upper = Layer(parent='words',
                  name='uppercase',
                  attributes=['upper'])
    text.add_layer(upper)

    for word in text.words:
        upper.add_annotation(word, upper=word.text.upper())

    with pytest.raises(AttributeError):
        for word in text.words:
            word.nonsense

    for word in text.uppercase:
        assert word.text.upper() == word.upper

    for word in text.words:
        assert (word.uppercase.upper == word.text.upper())

        # we have to get explicit access
        # TODO: double marking
        # word.mark('uppercase').upper = 'asd'


def test_words_sentences():
    t = Text('Minu nimi on Uku, mis sinu nimi on? Miks me seda arutame?').tag_layer()

    assert t.sentences.text == ['Minu', 'nimi', 'on', 'Uku', ',', 'mis', 'sinu', 'nimi', 'on', '?', 'Miks', 'me',
                                'seda', 'arutame', '?']
    assert t.words.text == ['Minu', 'nimi', 'on', 'Uku', ',', 'mis', 'sinu', 'nimi', 'on', '?', 'Miks', 'me', 'seda',
                            'arutame', '?']
    assert t.text == 'Minu nimi on Uku, mis sinu nimi on? Miks me seda arutame?'

    # assert [sentence.text for sentence in t.sentences] == t.sentences.text

    with pytest.raises(AttributeError):
        t.nonsense

    with pytest.raises(Exception):
        t.sentences.nonsense

    with pytest.raises(Exception):
        t.nonsense.nonsense

    with pytest.raises(Exception):
        t.words.nonsense

    dep = Layer(name='uppercase',
                parent='words',
                attributes=['upper']
                )
    t.add_layer(dep)
    for word in t.words:
        dep.add_annotation(word, upper=word.text.upper())

    assert t.uppercase.upper == AttributeList(
            ['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?'],
            'upper')
    # assert t.sentences.uppercase.upper == [['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', ],[ 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?']]
    # assert t.words.uppercase.upper == ['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?']


def test_ambiguous_layer():
    t = Text('Minu nimi on Uku, mis sinu nimi on? Miks me seda arutame?').tag_layer()

    dep = Layer(name='test',
                parent='words',
                ambiguous=True,
                attributes=['asd']
                )
    t.add_layer(dep)

    dep.add_annotation(t.words[0], asd='asd')

    dep.add_annotation(t.words[1], asd='asd')
    dep.add_annotation(t.words[0], asd='123')

    # TODO: assert something


def test_morph():
    text = Text('Minu nimi on Uku, mis sinu nimi on? Miks me seda arutame?').tag_layer()
    for i in text.words:
        i.morph_analysis

    text.words.lemma
    text.morph_analysis.lemma

    # assert text.sentences.lemma != text.words.lemma
    # text.sentences[:1].lemma
    # text.sentences[:1].words

    # assert len(text.sentences[:1].words.lemma) > 0


def test_change_lemma():
    text = Text('Olnud aeg.').tag_layer()
    setattr(text.morph_analysis[0].annotations[0], 'lemma', 'blabla')
    assert text.morph_analysis[0].annotations[0].lemma == 'blabla'

    setattr(text.morph_analysis[0].annotations[1], 'lemma', 'blabla2')
    assert text.morph_analysis[0].annotations[1].lemma == 'blabla2'


def test_to_records():
    text = Text('Olnud aeg.').tag_layer()

    # ambiguous
    assert (text['morph_analysis'].to_records()) == [
        [{'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': '', 'ending': '0', 'root_tokens': ['olnud'], 'partofspeech': 'A',
          'start': 0, 'end': 5, 'clitic': ''},
         {'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': 'sg n', 'ending': '0', 'root_tokens': ['olnud'],
          'partofspeech': 'A', 'start': 0, 'end': 5, 'clitic': ''},
         {'normalized_text': 'Olnud', 'root': 'ol=nud', 'lemma': 'olnud', 'form': 'pl n', 'ending': 'd', 'root_tokens': ['olnud'],
          'partofspeech': 'A', 'start': 0, 'end': 5, 'clitic': ''},
         {'normalized_text': 'Olnud', 'root': 'ole', 'lemma': 'olema', 'form': 'nud', 'ending': 'nud', 'root_tokens': ['ole'], 'partofspeech': 'V',
          'start': 0, 'end': 5, 'clitic': ''}],
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



def test_morph2():
    sort_analyses = True
    text = Text('''
    Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.
    Seni vaid soome keelde tõlgitud teos ilmus äsja ka itaalia keeles
    ning seda esitleti Rooma reisikirjanduse festivalil.
    Tuntud reisikrijanduse festival valis tänavu peakülaliseks Eesti,
    Ultima Thule ning Iidse-Põhjala ja Vahemere endisaegsed kultuurikontaktid j
    ust seetõttu, et eelmisel nädalal avaldas kirjastus Gangemi "Hõbevalge"
    itaalia keeles, vahendas "Aktuaalne kaamera".''').tag_layer()

    if sort_analyses:
        # Sort morph analysis annotations
        # ( so the order will be independent of the ordering used by 
        #   VabamorfAnalyzer & VabamorfDisambiguator )
        for morph_word in text['morph_analysis']:
            annotations = morph_word.annotations
            if len(annotations) > 1:
                sorted_annotations = sorted( annotations, key = lambda x : \
                       str(x['root'])+str(x['ending'])+str(x['clitic'])+\
                       str(x['partofspeech'])+str(x['form']) )
                morph_word.clear_annotations()
                for annotation in sorted_annotations:
                    morph_word.add_annotation( Annotation(morph_word, **annotation) )
    
    assert len(text.morph_analysis[5].annotations) == 2
    print(text.morph_analysis[5])
    print(text.morph_analysis[5].lemma)
    assert len(text.morph_analysis[5].lemma) == 2
    assert text.morph_analysis[5].lemma == AttributeList(['olema', 'olema'], 'lemma')
    assert text.morph_analysis.lemma == AmbiguousAttributeList(
            [['Lennart'], ['Meri'], ['"'], ['hõbevalge'], ['"'], ['olema', 'olema'],
             ['jõudnud', 'jõudnud', 'jõudnud', 'jõudma'], ['rahvusvaheline'], ['lugejaskond'], ['.'], ['seni'],
             ['vaid'],
             ['soome'], ['keel'], ['tõlgitud', 'tõlgitud', 'tõlgitud', 'tõlkima'], ['teos'], ['ilmuma'], ['äsja'],
             ['ka'],
             ['itaalia'], ['keel'], ['ning'], ['see'], ['esitlema'], ['Rooma'], ['reisikirjandus'], ['festival'], ['.'],
             ['tundma', 'tuntud', 'tuntud', 'tuntud'], ['reisikrijandus'], ['festival'], ['valima'], ['tänavu'],
             ['peakülaline'], ['Eesti'], [','], ['Ultima'], ['Thule'], ['ning'], ['Iidse-Põhjala'], ['ja'],
             ['Vahemeri'],
             ['endisaegne'], ['kultuurikontakt'], ['j'], ['uks'], ['seetõttu'], [','], ['et'], ['eelmine'], ['nädal'],
             ['avaldama'], ['kirjastus'], ['Gangemi'], ['"'], ['hõbevalge'], ['"'], ['itaalia'], ['keel'], [','],
             ['vahendama'], ['"'], ['aktuaalne'], ['kaamera'], ['"'], ['.']
             ],
            'lemma')


def test_text_setitem():
    text = Text('''Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.''').tag_layer()
    l = Layer(name='test', attributes=['test1'])
    text.add_layer(l)

    assert text['test'] is l

    # getting something that is not in the dict
    with pytest.raises(KeyError):
        text['nothing']


def test_delete_annotation_in_ambiguous_span():
    text = Text('''Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.''').tag_layer()
    l = Layer(name='test',
              parent='words',
              ambiguous=True,
              attributes=['test1'])

    text.add_layer(l)

    c = 0
    for word in text.words:
        l.add_annotation(word, test1=c)
        c += 1

    for word in text.words:
        l.add_annotation(word, test1=c)
        c += 1

    assert len(text['test'][0].annotations) == 2

    (text['test'][0].annotations
        .remove(
            text['test'][0].annotations[0]  # this is the annotation we want to remove
    )
    )
    assert len(text['test'][0].annotations) == 1

    # removing the second
    assert len(text['test'][1].annotations) == 2

    (text['test'][1].annotations
        .remove(
            text['test'][1].annotations[0]  # this is the annotation we want to remove
    )
    )
    assert len(text['test'][1].annotations) == 1


def test_span_morph_access():
    text = Text('Oleme jõudnud kohale. Kus me oleme?').tag_layer()
    assert text.sentences[0].words[0].morph_analysis.lemma == AttributeList(['olema'], 'lemma')


def test_lemma_access_from_text_object():
    """See on oluline, sest Dage tungivalt soovib säärast varianti."""
    text = Text('Oleme jõudnud kohale. Kus me oleme?').tag_layer()
    assert (text.lemma) == text.words.lemma


def test_sentences_morph_analysis_lemma():
    text = Text('Oleme jõudnud kohale. Kus me oleme?')

    text.tag_layer()
    with pytest.raises(AttributeError):
        text.sentences.morph_analysis


def test_phrase_layer():
    class UppercasePhraseTagger:
        # demo tagger, mis markeerib ära lause piirides järjestikused jooksud suurtähtedega sõnu

        def tag(self, text: Text) -> Text:

            uppercases = []
            prevstart = 0
            for sentence in text.sentences:
                for idx, word in enumerate(sentence.words):
                    if word.text.upper() == word.text and word.text.lower() != word.text:
                        uppercases.append((idx + prevstart, word))
                prevstart += len(sentence)

            from operator import itemgetter
            from itertools import groupby
            rs = []
            for k, g in groupby(enumerate(uppercases), lambda i: i[0] - i[1][0]):
                r = map(itemgetter(1), g)
                rs.append(list(r))

            spans = [[j for _, j in i] for i in rs if len(i) > 1]
            l = Layer(enveloping='words', name='uppercasephrase', attributes=['phrasetext', 'tag'])

            for idx, s in enumerate(spans):
                l.add_annotation(s, phrasetext=' '.join([i.text for i in s]).lower(), tag=idx)

            text.add_layer(l)

            return text

    w = UppercasePhraseTagger()
    t = w.tag(Text('Minu KARU ON PUNANE. MIS värvi SINU KARU on? Kuidas PALUN?').tag_layer(['words', 'sentences']))
    t.tag_layer(['morph_analysis'])
    assert t.uppercasephrase['phrasetext', 'text'] == AttributeTupleList([['karu on punane', ['KARU', 'ON', 'PUNANE']],
                                                                          ['sinu karu', ['SINU', 'KARU']]],
                                                                         ('phrasetext', 'text'))

    assert (t.phrasetext) == AttributeList(['karu on punane', 'sinu karu'], 'phrasetext')

    assert t.uppercasephrase.lemma == \
           AttributeList([AmbiguousAttributeList([['karu'], ['olema', 'olema'], ['punane']], ('lemma')),
                          AmbiguousAttributeList([['sina'], ['karu']], ('lemma'))],
                         'lemma')

    assert ([i.text for i in t.words if i not in list(itertools.chain(*t.uppercasephrase))]) == ['Minu', '.', 'MIS',
                                                                                                 'värvi', 'on', '?',
                                                                                                 'Kuidas', 'PALUN', '?']

    assert ([i.text for i in t.words if i not in list(itertools.chain(*t.uppercasephrase))]) == ['Minu', '.', 'MIS',
                                                                                                 'värvi', 'on', '?',
                                                                                                 'Kuidas', 'PALUN', '?']

    mapping = {i: j for j in t.uppercasephrase for i in j.base_span}
    assert [mapping[i.base_span].tag if i.base_span in mapping else i.text for i in t.words] == \
           ['Minu', 0, 0, 0, '.', 'MIS', 'värvi', 1, 1, 'on', '?', 'Kuidas', 'PALUN', '?']
