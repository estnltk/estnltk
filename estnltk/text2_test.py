import pytest
from text import Text as OldText

from text2 import *


def test_spans():
    text = Text('Mingi tekst')
    layer = Layer(text_object=text, name='test')
    a = Span(1, 2, layer)
    assert a.start == 1
    assert a.end == 2
    assert a.layer is layer

    with pytest.raises(AssertionError):
        Span(2, 1, layer)

    with pytest.raises(AttributeError):
        # slots should not allow assignement
        Span(1, 2, layer).test = 12

    assert Span(1, 2, layer).text == 'i'

    with pytest.raises(AttributeError):
        # Span text should not be assignable
        Span(1, 2, layer).text = 'a'


def test_span_ordering():
    text = Text('Mingi tekst')
    layer = Layer(text_object=text, name='test')
    a = Span(1, 2, layer)
    b = Span(2, 3, layer)
    c = Span(2, 3, layer)
    assert a < b
    assert not a > b
    assert a <= b
    assert not a >= b
    assert b > a
    assert not b < a
    assert b >= a
    assert c == b
    assert not a == b

    # layer2 = Layer(text_object=text, name='test2')
    # x = Span(1, 2, layer2)
    # with pytest.raises(AssertionError):
    #     x == a


def test_text():
    t = Text('test')
    assert t.text == 'test'
    with pytest.raises(AttributeError):
        t.text = 'asd'


def test_spanList():
    sl = SpanList()
    layer = Layer(text_object=Text('a'), name='test')
    span = Span(0, 1, layer)
    sl.add(span)

    assert len(sl) == 1
    assert list(sl)[0] is span

    with pytest.raises(TypeError):
        sl['asd']

    # insertion keeps items in sorted order
    sl = SpanList()
    a, b, c, d = [Span(i, i + 1, layer) for i in range(4)]
    sl.add(b)
    sl.add(c)
    sl.add(a)
    sl.add(d)
    assert sl[0] == a
    assert sl[1] == b
    assert sl[2] == c
    assert sl[3] == d


    sl.freeze()
    with pytest.raises(AssertionError):
        sl.add(a)


def test_layer():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(name='test', text_object=t)
    t.add_layer(l)

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='text', text_object=t))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='test', text_object=t))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name=' ', text_object=t))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='3', text_object=t))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='assert', text_object=t))

    with pytest.raises(AssertionError):
        t.add_layer(Layer(name='is', text_object=t))

    assert t.layers['test'] is l
    assert t.test is l

    with pytest.raises(AttributeError):
        t.notexisting

    assert t.text == text

    layer = t.test  # type: Layer
    layer.add_span(
        Span(start=0, end=2, layer=layer)
    )
    assert t.test.text == [text[:2]]

    t.test.add_span(
        Span(start=2, end=4)
    )

    t.test.freeze()
    with pytest.raises(AssertionError):
        t.test.add_span(
            Span(start=2, end=4, layer=layer)
        )


def test_layer_from_spans():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    t.add_layer(
        Layer.from_span_tuples(name='test',
                               spans=[(1, 2), (0, 3), (0, 2)])
    )

    assert t.test.spans[0].start == 0 and t.test.spans[0].end == 2
    assert len(t.test) == 3
    assert all([isinstance(i, Span) for i in t.test])


def test_unbound_layer():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)

    l = Layer(name='test')
    assert l.frozen == False
    assert l.bound == False

    l.add_span(Span(1, 2))

    with pytest.raises(AttributeError):
        for i in l:
            (i.text)

    l.bind(t)
    for i in l:
        (i.text)

    assert all([i.bound for i in l.spans])


def test_annotated_layer():
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(text_object=t, name='test', attributes=['test', 'asd'])
    t.add_layer(l)
    l.add_span(Span(1, 5))

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
    l = Layer(text_object=t, name='test', attributes=['test', 'asd'])
    t.add_layer(l)
    l.add_span(Span(1, 5))
    l.add_span(Span(2, 6))

    for i in l:
        i.asd = 123
        break

    assert (count_by(l, ['text', 'asd'])) == {('ösel', 123): 1, ('sel ', None): 1}


def test_from_dict():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer.from_span_dict('words', [{'end': 3, 'lemma': 'kui', 'start': 0},
                                           {'end': 8, 'lemma': 'mitu', 'start': 4},
                                           {'end': 13, 'lemma': 'kuu', 'start': 9},
                                           {'end': 16, 'lemma': 'olema', 'start': 14},
                                           {'end': 23, 'lemma': 'aasta', 'start': 17},
                                           {'end': 24, 'lemma': '?', 'start': 23}],
                                  attributes=['lemma']
                                  )
    t.add_layer(words)

    for span, lemma in zip(t.words, ['kui', 'mitu', 'kuu', 'olema', 'aasta', '?']):
        assert span.lemma == lemma


def test_dependant_span():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer.from_span_dict('words', [{'end': 3, 'lemma': 'kui', 'start': 0},
                                           {'end': 8, 'lemma': 'mitu', 'start': 4},
                                           {'end': 13, 'lemma': 'kuu', 'start': 9},
                                           {'end': 16, 'lemma': 'olema', 'start': 14},
                                           {'end': 23, 'lemma': 'aasta', 'start': 17},
                                           {'end': 24, 'lemma': '?', 'start': 23}],
                                  attributes=['lemma']
                                  )
    t.add_layer(words)

    dep = DependantLayer(name='reverse_lemmas', text_object=t,
                   frozen=False,
                   parent=t.words,
                   attributes=['revlemma']
                   )
    t.add_layer(dep)

    for word in t.words:
        word.mark('reverse_lemmas').revlemma = word.lemma[::-1]

    for i in t.reverse_lemmas:
        assert (i.revlemma == i.lemma[::-1])

    for i in t.words:
        assert (i.mark('reverse_lemmas').revlemma == i.lemma[::-1])

def test_delete_layer():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer.from_span_dict('words', [{'end': 3, 'lemma': 'kui', 'start': 0},
                                           {'end': 8, 'lemma': 'mitu', 'start': 4},
                                           {'end': 13, 'lemma': 'kuu', 'start': 9},
                                           {'end': 16, 'lemma': 'olema', 'start': 14},
                                           {'end': 23, 'lemma': 'aasta', 'start': 17},
                                           {'end': 24, 'lemma': '?', 'start': 23}],
                                  attributes=['lemma']
                                  )
    t.add_layer(words)

    assert len(t.layers) == 1
    del t.words
    assert len(t.layers) == 0



def test_enveloping_layer():
    t = Text('Kui mitu kuud on aastas?')
    words = Layer.from_span_dict('words', [{'end': 3, 'lemma': 'kui', 'start': 0},
                                           {'end': 8, 'lemma': 'mitu', 'start': 4},
                                           {'end': 13, 'lemma': 'kuu', 'start': 9},
                                           {'end': 16, 'lemma': 'olema', 'start': 14},
                                           {'end': 23, 'lemma': 'aasta', 'start': 17},
                                           {'end': 24, 'lemma': '?', 'start': 23}],
                                  attributes=['lemma']
                                  )
    t.add_layer(words)
    wordpairs = EnvelopingLayer(name='wordpairs', envelops=words)


    wordpairs.add_spans(t.words.spans[0:2])
    wordpairs.add_spans(t.words.spans[2:4])
    wordpairs.add_spans(t.words.spans[4:6])

    assert (wordpairs.text == [['Kui', 'mitu'], ['kuud', 'on'], ['aastas', '?']])

    wordpairs.add_spans(t.words.spans[1:3])
    wordpairs.add_spans(t.words.spans[3:5])
    assert (wordpairs.text == [['Kui', 'mitu'], ['mitu', 'kuud'], ['kuud', 'on'], ['on', 'aastas'], ['aastas', '?']])

    t.add_layer(wordpairs)

    for wordpair in t.wordpairs:
        for word in wordpair.words:
            assert (word)



    for wordpair in t.wordpairs:
        (wordpair.lemma) #this should not give a keyerror

    with pytest.raises(KeyError):
        for wordpair in t.wordpairs:
            (wordpair.nonsense)  # this SHOULD give a keyerror

    assert (words.lemma == ['kui', 'mitu', 'kuu', 'olema', 'aasta', '?'])
    assert (t.wordpairs.lemma == [['kui', 'mitu'], ['mitu', 'kuu'], ['kuu', 'olema'], ['olema', 'aasta'], ['aasta', '?']])

    with pytest.raises(AttributeError):
        (wordpairs.test)

def test_oldtext_to_new():

    text = 'Tuleb üks neiuke, järelikult tuleb ühelt poolt! Kui tuleks kaks neiukest, siis tuleksid kahelt poolt! Aga seekord tuleb üks, tuleb ühelt poolt!'
    new = words_sentences(text)
    old = OldText(text)


    for sentence, old_sentence in zip(new.sentences, old.split_by_sentences()):
        assert (sentence.text == [word['text'] for word in old_sentence.words])

    assert (new.sentences.text == [['Tuleb', 'üks', 'neiuke', ',', 'järelikult', 'tuleb', 'ühelt', 'poolt', '!'],
                                   ['Kui', 'tuleks', 'kaks', 'neiukest', ',', 'siis', 'tuleksid', 'kahelt', 'poolt', '!'],
                                   ['Aga', 'seekord', 'tuleb', 'üks', ',', 'tuleb', 'ühelt', 'poolt', '!']])
    assert (new.text == text)


def test_various():
    text = words_sentences('Minu nimi on Joosep, mis sinu nimi on? Miks me seda arutame?')

    upper = DependantLayer(parent=text.words,
                           name='uppercase',
                           attributes=['upper'])
    text.add_layer(upper)

    for word in text.words:
        #     print(word.text)
        word.mark('uppercase').upper = word.text.upper()

    with pytest.raises(AttributeError):
        for word in text.words:
            word.nonsense

    for word in text.uppercase:
        assert word.text.upper() == word.upper

    for word in text.words:
        assert (word.upper == word.text.upper())

        with pytest.raises(AttributeError):
            #but we can't assign this way.
            word.upper = 123

        #we have to get explicit access
        word.mark('uppercase').upper = 'asd'

    assert text.uppercase.text == text.words.text
    assert text.uppercase.upper == ['asd' for _ in text.words]

    #TODO:FIX! (This gives KeyError, expected result - list of strings)
    # for sentence in text.sentences:
    #     print(sentence.upper)
