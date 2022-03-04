'''
This file contains tests for the functionality in standard estnltk: tag_layer and analyse.
For tests that test the core estnltk text functionality, see the same file in estnltk_core
'''

import pytest

import itertools
from estnltk_core import Layer
from estnltk import Text
from estnltk_core.layer import AttributeList, AmbiguousAttributeList
from estnltk_core import Annotation
from estnltk_core.tests import create_amb_attribute_list


def test_general():
    t = Text('Minu nimi on Uku. Mis Sinu nimi on? Miks me seda arutame?').tag_layer()

    assert isinstance(t.sentences, Layer)
    assert isinstance(t.words, Layer)

    assert len(t.sentences) == 3
    assert len(t.words) == 15
    with pytest.raises(AttributeError):
        t.sentences.words

    assert {'tokens', 'compound_tokens', 'sentences', 'words', 'morph_analysis'} <= set(t.layers)

    with pytest.raises(AttributeError):
        t.words.sentences

    assert len(t.words) == len(t.words.text)
    # assert len(t.sentences) == len(t.sentences.text)
    # assert len(t.sentences.words.text) == len(t.sentences.text)
    assert t.morph_analysis.lemma == create_amb_attribute_list([['mina'], ['nimi'], ['olema', 'olema'], ['Uku'],
                                                                ['.'], ['mis', 'mis'], ['sina'], ['nimi'],
                                                                ['olema', 'olema'], ['?'], ['miks'], ['mina'],
                                                                ['see'], ['arutama'], ['?']],
                                                                'lemma')

    assert len(t.morph_analysis.lemma) == len(t.words)
    assert len(t.morph_analysis) == len(t.words)



def test_paragraph_tokenizer():
    t = Text('''Minu nimi on Uku. Miks?

Mis sinu nimi on?
    ''').tag_layer(['paragraphs', 'morph_analysis'])

    # Should not raise NotImplementedError
    t.paragraphs
    assert t.paragraphs.text == ['Minu', 'nimi', 'on', 'Uku', '.', 'Miks', '?', 'Mis', 'sinu', 'nimi', 'on', '?']


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

    assert t.uppercase.upper == create_amb_attribute_list(
            ['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?'],
            'upper')

def test_serialization():

    import pickle

    def save_restore(text: Text) -> Text:
        bytes = pickle.dumps(text)
        return pickle.loads(bytes)

    text = Text('Tavaline analüüsitud teksti serialiseerimine.').tag_layer(['paragraphs','morph_extended'])
    result = save_restore(text)
    assert result.text == text.text
    assert result.meta == text.meta
    assert result.layers == text.layers
    for layer in result.layers:
        assert result[layer] == text[layer]


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

    assert t.uppercase.upper == create_amb_attribute_list(
            ['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?'],
            'upper')
    # assert t.sentences.uppercase.upper == [['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', ],[ 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?']]
    # assert t.words.uppercase.upper == ['MINU', 'NIMI', 'ON', 'UKU', ',', 'MIS', 'SINU', 'NIMI', 'ON', '?', 'MIKS', 'ME', 'SEDA', 'ARUTAME', '?']


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
                sorted_annotations = sorted(annotations, key=lambda x: \
                    str(x['root']) + str(x['ending']) + str(x['clitic']) + \
                    str(x['partofspeech']) + str(x['form']))
                morph_word.clear_annotations()
                for annotation in sorted_annotations:
                    morph_word.add_annotation(Annotation(morph_word, **annotation))

    assert len(text.morph_analysis[5].annotations) == 2
    #print(text.morph_analysis[5])
    #print(text.morph_analysis[5].lemma)
    assert len(text.morph_analysis[5].lemma) == 2
    assert text.morph_analysis[5].lemma == create_amb_attribute_list(['olema', 'olema'], 'lemma')
    assert text.morph_analysis.lemma == create_amb_attribute_list(
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


def test_sentences_morph_analysis_lemma():
    text = Text('Oleme jõudnud kohale. Kus me oleme?')

    text.tag_layer()
    with pytest.raises(AttributeError):
        text.sentences.morph_analysis


def test_span_morph_access():
    text = Text('Oleme jõudnud kohale. Kus me oleme?').tag_layer()
    assert text.sentences[0].words[0].morph_analysis.lemma == create_amb_attribute_list(['olema'], 'lemma')


def test_lemma_access_from_text_object():
    """See on oluline, sest Dage tungivalt soovib säärast varianti."""
    text = Text('Oleme jõudnud kohale. Kus me oleme?').tag_layer()
    assert (text.lemma) == text.words.lemma


def test_tag_layer_with_string_input():
    #
    # Test that tag_layer also accepts string as an input
    #
    t = Text( 'Tere, maailm!' )
    t.tag_layer('words')
    assert t.layers == {'compound_tokens', 'tokens', 'words'}
    t.tag_layer('sentences')
    t.tag_layer('paragraphs')
    assert t.layers == {'compound_tokens', 'tokens', 'words', 'sentences', 'paragraphs'}


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
    assert (t.phrasetext) == create_amb_attribute_list(['karu on punane', 'sinu karu'], 'phrasetext')
    assert (t.uppercasephrase['phrasetext']) == create_amb_attribute_list(['karu on punane', 'sinu karu'], 'phrasetext')
    # TODO: it's not a nice way to check, but currently there is not other way, as we cannot mock 'text' attribute
    assert str(t.uppercasephrase['phrasetext', 'text']) == "[['karu on punane', ['KARU', 'ON', 'PUNANE']], "+\
                                                           "['sinu karu', ['SINU', 'KARU']]]"

    assert isinstance(t.uppercasephrase.lemma, AttributeList)
    assert str(t.uppercasephrase.lemma) == \
           "[AmbiguousAttributeList([['karu'], ['olema', 'olema'], ['punane']], ('lemma',)), "+\
            "AmbiguousAttributeList([['sina'], ['karu']], ('lemma',))]"
    #
    # More specifically,  t.uppercasephrase.lemma  returns:
    #
    #  AttributeList([AmbiguousAttributeList([['karu'], ['olema', 'olema'], ['punane']], ('lemma')),
    #                 AmbiguousAttributeList([['sina'], ['karu']], ('lemma'))], 
    #                'lemma')
    #
    #  (but we can't mock that structure)
    #

    assert ([i.text for i in t.words if i not in list(itertools.chain(*t.uppercasephrase))]) == ['Minu', '.', 'MIS',
                                                                                                 'värvi', 'on', '?',
                                                                                                 'Kuidas', 'PALUN', '?']

    assert ([i.text for i in t.words if i not in list(itertools.chain(*t.uppercasephrase))]) == ['Minu', '.', 'MIS',
                                                                                                 'värvi', 'on', '?',
                                                                                                 'Kuidas', 'PALUN', '?']

    mapping = {i: j for j in t.uppercasephrase for i in j.base_span}
    assert [mapping[i.base_span].tag if i.base_span in mapping else i.text for i in t.words] == \
           ['Minu', 0, 0, 0, '.', 'MIS', 'värvi', 1, 1, 'on', '?', 'Kuidas', 'PALUN', '?']
