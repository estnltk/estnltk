import pytest

import itertools
from estnltk_core import Layer
from estnltk_core.common import load_text_class

from estnltk_core.converters import dict_to_layer
from estnltk_core.converters import records_to_layer

from estnltk_core.tests import create_amb_attribute_list

def test_new_span_hierarchy():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Ilm on ilus. Päike paistab.')

    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    text.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
                                                'annotations': [{}]},
                                               {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    text.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
                                      'attributes': (),
                                      'parent': None,
                                      'enveloping': 'sentences',
                                      'ambiguous': False,
                                      'serialisation_module': None,
                                      'meta': {},
                                      'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
                                                               ((13, 18), (19, 26), (26, 27))),
                                                 'annotations': [{}]}]})
    text.add_layer(paragraphs_layer)

    l = Layer(
            name='layer1',
            parent='words',
            attributes=['test1'],
            text_object=text
    )
    text.add_layer(l)

    for i in text['words']:
        l.add_annotation(i, test1='1234')

    l = Layer(
            name='layer2',
            parent='layer1',
            attributes=['test2'],
            text_object=text
    )
    text.add_layer(l)

    for i in text['layer1']:
        l.add_annotation(i, test2='12345')

    assert text['layer2'][0].parent.layer.name == 'layer1'




def test_layer_1():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # TODO: Merge this with test_add_layer function
    string = 'Öösel on kõik kassid hallid.'

    text = Text(string)
    layer = Layer(name='test')
    text.add_layer(layer)

    # 'text' can be a layer name
    text.add_layer(Layer(name='text'))

    # test that duplicate layers cannot be added
    with pytest.raises(AssertionError):
        text.add_layer(Layer(name='test'))

    # test that layer name is not whitespace only
    with pytest.raises(AssertionError):
        text.add_layer(Layer(name=' '))

    assert text['test'] is layer

    # TODO: This should be covered by other tests
    with pytest.raises(AttributeError):
        text.notexisting

    # TODO: This should be covered by other tests
    assert text.text == string

    # TODO: This is a part of layer testing
    layer = text['test']  # type: Layer
    layer.add_annotation((0, 2))
    assert text['test'].text == [string[:2]]

    text['test'].add_annotation((2, 4))


def test_annotated_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = 'Öösel on kõik kassid hallid.'
    t = Text(text)
    l = Layer(name='test', attributes=['test', 'asd'])
    t.add_layer(l)
    l.add_annotation((1, 5))

    for i in t['test']:
        i.test = 'mock'

    with pytest.raises(AttributeError):
        for i in t['test']:
            i.test2 = 'mock'


def test_count_by():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
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




def test_dependant_span():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(name='words',
                  attributes=['lemma'])
    words = records_to_layer( words, [{'end': 3, 'lemma': 'kui', 'start': 0},
                                      {'end': 8, 'lemma': 'mitu', 'start': 4},
                                      {'end': 13, 'lemma': 'kuu', 'start': 9},
                                      {'end': 16, 'lemma': 'olema', 'start': 14},
                                      {'end': 23, 'lemma': 'aasta', 'start': 17},
                                      {'end': 24, 'lemma': '?', 'start': 23}] )
    t.add_layer(words)

    dep = Layer(name='reverse_lemmas',
                parent='words',
                attributes=['revlemma']
                )
    t.add_layer(dep)

    for word in t['words']:
        dep.add_annotation(word, revlemma=word.lemma[::-1])

    for i in t['reverse_lemmas']:
        assert (i.revlemma == i.words.lemma[::-1])

    # TODO: how should this work?
    # for i in t.words:
    #     assert (i.mark('reverse_lemmas').revlemma == i.lemma[::-1])


def test_enveloping_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Kui mitu kuud on aastas?')
    words = Layer(
            name='words',
            attributes=['lemma'])
    words = records_to_layer( words, [{'end': 3, 'lemma': 'kui', 'start': 0},
                                      {'end': 8, 'lemma': 'mitu', 'start': 4},
                                      {'end': 13, 'lemma': 'kuu', 'start': 9},
                                      {'end': 16, 'lemma': 'olema', 'start': 14},
                                      {'end': 23, 'lemma': 'aasta', 'start': 17},
                                      {'end': 24, 'lemma': '?', 'start': 23}] )
    t.add_layer(words)
    wordpairs = Layer(name='wordpairs', enveloping='words')
    t.add_layer(wordpairs)

    wordpairs.add_annotation(t['words'][0:2])
    wordpairs.add_annotation(t['words'][2:4])
    wordpairs.add_annotation(t['words'][4:6])

    #print(t['wordpairs'].text)
    assert (wordpairs.text == ['Kui', 'mitu', 'kuud', 'on', 'aastas', '?'])

    wordpairs.add_annotation(t['words'][1:3])
    wordpairs.add_annotation(t['words'][3:5])
    #print(t['wordpairs'].text)
    assert (wordpairs.text == ['Kui', 'mitu', 'mitu', 'kuud', 'kuud', 'on', 'on', 'aastas', 'aastas', '?'])

    for wordpair in t['wordpairs']:
        for word in wordpair.words:
            assert (word)

    for wordpair in t['wordpairs']:
        wordpair.words.lemma  # this should not give a keyerror

    # I have changed my mind about what this should raise so much, I'm leaving it free at the moment
    with pytest.raises(Exception):
        for wordpair in t['wordpairs']:
            wordpair.nonsense  # this SHOULD give a --keyerror--

    assert (t['words'].lemma == create_amb_attribute_list(['kui', 'mitu', 'kuu', 'olema', 'aasta', '?'], 'lemma'))

    assert ([list(wordpair.words.lemma) for wordpair in t['wordpairs']] ==
            [['kui', 'mitu'], ['mitu', 'kuu'], ['kuu', 'olema'], ['olema', 'aasta'], ['aasta', '?']])

    #print(t['wordpairs'].text)
    with pytest.raises(Exception):
        (wordpairs.test)


def test_various():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Ilm on ilus. Päike paistab.')

    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    text.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
                                                'annotations': [{}]},
                                               {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    text.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
                                      'attributes': (),
                                      'parent': None,
                                      'enveloping': 'sentences',
                                      'ambiguous': False,
                                      'serialisation_module': None,
                                      'meta': {},
                                      'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
                                                               ((13, 18), (19, 26), (26, 27))),
                                                 'annotations': [{}]}]})
    text.add_layer(paragraphs_layer)

    upper = Layer(parent='words',
                  name='uppercase',
                  attributes=['upper'])
    text.add_layer(upper)

    for word in text['words']:
        upper.add_annotation(word, upper=word.text.upper())

    with pytest.raises(AttributeError):
        for word in text['words']:
            word.nonsense

    for word in text['uppercase']:
        assert word.text.upper() == word.upper

    for word in text['words']:
        assert (word.uppercase.upper == word.text.upper())

        # we have to get explicit access
        # TODO: double marking
        # word.mark('uppercase').upper = 'asd'




def test_ambiguous_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    t = Text('Ilm on ilus. Päike paistab.')

    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    t.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
                                                'annotations': [{}]},
                                               {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    t.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
                                      'attributes': (),
                                      'parent': None,
                                      'enveloping': 'sentences',
                                      'ambiguous': False,
                                      'serialisation_module': None,
                                      'meta': {},
                                      'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
                                                               ((13, 18), (19, 26), (26, 27))),
                                                 'annotations': [{}]}]})
    t.add_layer(paragraphs_layer)

    dep = Layer(name='test',
                parent='words',
                ambiguous=True,
                attributes=['asd']
                )
    t.add_layer(dep)

    dep.add_annotation(t['words'][0], asd='asd')

    dep.add_annotation(t['words'][1], asd='asd')
    dep.add_annotation(t['words'][0], asd='123')

    # TODO: assert something



def test_delete_annotation_in_ambiguous_span():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('''Ilm on ilus. Päike paistab.''')

    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 3), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (4, 6), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (7, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 26), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (26, 27), 'annotations': [{'normalized_form': None}]}]})
    text.add_layer(words_layer)
    sentences_layer = dict_to_layer({'name': 'sentences',
                                     'attributes': (),
                                     'parent': None,
                                     'enveloping': 'words',
                                     'ambiguous': False,
                                     'serialisation_module': None,
                                     'meta': {},
                                     'spans': [{'base_span': ((0, 3), (4, 6), (7, 11), (11, 12)),
                                                'annotations': [{}]},
                                               {'base_span': ((13, 18), (19, 26), (26, 27)), 'annotations': [{}]}]})
    text.add_layer(sentences_layer)
    paragraphs_layer = dict_to_layer({'name': 'paragraphs',
                                      'attributes': (),
                                      'parent': None,
                                      'enveloping': 'sentences',
                                      'ambiguous': False,
                                      'serialisation_module': None,
                                      'meta': {},
                                      'spans': [{'base_span': (((0, 3), (4, 6), (7, 11), (11, 12)),
                                                               ((13, 18), (19, 26), (26, 27))),
                                                 'annotations': [{}]}]})
    text.add_layer(paragraphs_layer)

    l = Layer(name='test',
              parent='words',
              ambiguous=True,
              attributes=['test1'])

    text.add_layer(l)

    c = 0
    for word in text['words']:
        l.add_annotation(word, test1=c)
        c += 1

    for word in text['words']:
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



def test_attribute_values_selection():
    # Test systematically different kinds of attribute value selections
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Prepare data
    text = Text('Tere! Mis värk on?')
    words_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': ('normalized_form',),
         'enveloping': None,
         'meta': {},
         'name': 'words',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'normalized_form': None}], 'base_span': (0, 4)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (4, 5)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (6, 9)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (10, 14)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (15, 17)},
                   {'annotations': [{'normalized_form': None}], 'base_span': (17, 18)}]} )
    text.add_layer( words_layer )
    sentences_layer = dict_to_layer( \
        {'ambiguous': False,
         'attributes': (),
         'enveloping': 'words',
         'meta': {},
         'name': 'sentences',
         'parent': None,
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{}], 'base_span': ((0, 4), (4, 5))},
                   {'annotations': [{}],
                    'base_span': ((6, 9), (10, 14), (15, 17), (17, 18))}]} )
    text.add_layer( sentences_layer )
    morph_analysis_layer = dict_to_layer( \
        {'ambiguous': True,
         'attributes': ('normalized_text',
                        'lemma',
                        'root',
                        'root_tokens',
                        'ending',
                        'clitic',
                        'form',
                        'partofspeech'),
         'enveloping': None,
         'meta': {},
         'name': 'morph_analysis',
         'parent': 'words',
         'secondary_attributes': (),
         'serialisation_module': None,
         'spans': [{'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': '',
                                     'lemma': 'tere',
                                     'normalized_text': 'Tere',
                                     'partofspeech': 'I',
                                     'root': 'tere',
                                     'root_tokens': ['tere']}],
                    'base_span': (0, 4)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '!',
                                     'normalized_text': '!',
                                     'partofspeech': 'Z',
                                     'root': '!',
                                     'root_tokens': ['!']}],
                    'base_span': (4, 5)},
                   {'annotations': [{'clitic': '',
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
                    'base_span': (6, 9)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'sg n',
                                     'lemma': 'värk',
                                     'normalized_text': 'värk',
                                     'partofspeech': 'S',
                                     'root': 'värk',
                                     'root_tokens': ['värk']}],
                    'base_span': (10, 14)},
                   {'annotations': [{'clitic': '',
                                     'ending': '0',
                                     'form': 'b',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']},
                                    {'clitic': '',
                                     'ending': '0',
                                     'form': 'vad',
                                     'lemma': 'olema',
                                     'normalized_text': 'on',
                                     'partofspeech': 'V',
                                     'root': 'ole',
                                     'root_tokens': ['ole']}],
                    'base_span': (15, 17)},
                   {'annotations': [{'clitic': '',
                                     'ending': '',
                                     'form': '',
                                     'lemma': '?',
                                     'normalized_text': '?',
                                     'partofspeech': 'Z',
                                     'root': '?',
                                     'root_tokens': ['?']}],
                    'base_span': (17, 18)}]} )
    text.add_layer( morph_analysis_layer )
    
    # AttributeList
    # =============
    
    # select 1 attribute from a single span, which has ambiguous annotations
    assert text['morph_analysis'][2]['lemma'] == create_amb_attribute_list( ['mis', 'mis'], ('lemma',) )
    assert text['morph_analysis'][2]['form'] == create_amb_attribute_list( ['sg n', 'pl n'], ('form',) )
    
    # select 1 attribute from multiple spans of an unambiguous layer
    # (note: 'words' is not unambiguous in standard estnltk)
    selection = text['words']['text']
    assert selection.attribute_names == ('text',)
    # use str, because create_amb_attribute_list cannot mock 'text' attr:
    assert str(selection) == "['Tere', '!', 'Mis', 'värk', 'on', '?']"
    assert text['words']['normalized_form'] == \
        create_amb_attribute_list( [None, None, None, None, None, None], ('normalized_form',) )
    
    # AmbiguousAttributeList
    # ======================
    
    # select 1 attribute from multiple spans of an ambiguous layer
    assert text['morph_analysis']['partofspeech'] == \
        create_amb_attribute_list( [['I'], ['Z'], ['P', 'P'], ['S'], ['V', 'V'], ['Z']], ('partofspeech',) )

    # AttributeTupleList
    # ==================
    
    # select multiple attributes from a single span, which has ambiguous annotations
    assert text['morph_analysis'][2]['lemma', 'form'] == \
        create_amb_attribute_list( [['mis', 'sg n'], ['mis', 'pl n']], ('lemma', 'form') )
    
    # select multiple attributes from multiple spans of an unambiguous layer
    # (note: 'words' is not unambiguous in standard estnltk)
    selection = text['words']['text', 'normalized_form']
    assert selection.attribute_names == ('text', 'normalized_form')
    # use str, because create_amb_attribute_list cannot mock 'text' attr:
    assert str(selection) == \
        "[['Tere', None], ['!', None], ['Mis', None], ['värk', None], ['on', None], ['?', None]]"

    # select 1 index attribute from multiple spans of an unambiguous layer
    selection = text['words'].attribute_values([], index_attributes=['start'])
    assert selection.attribute_names == ('start',)
    assert str(selection) == "[[0], [4], [6], [10], [15], [17]]"
    # TODO: in principle, it could be AttributeList, but previous versions of estnltk also
    # returned AttributeTupleList on this occasion. should we correct this behavior?

    # select 1 index attribute from a level 1 enveloping layer
    selection = text['sentences'].attribute_values([], index_attributes=['start'])
    assert selection.attribute_names == ('start',)
    assert str(selection) == "[[0], [6]]"

    # select multiple index attributes from an unambiguous layer
    selection = text['words'].attribute_values([], index_attributes=['start', 'end', 'text'])
    assert selection.attribute_names == ('start', 'end', 'text')
    assert str(selection) == \
        "[[0, 4, 'Tere'], [4, 5, '!'], [6, 9, 'Mis'], [10, 14, 'värk'], [15, 17, 'on'], [17, 18, '?']]"
    
    # select multiple index attributes from an unambiguous layer via layer[attributes]
    selection = text['words'][['start', 'end', 'text']]
    assert selection.attribute_names == ('start', 'end', 'text')
    assert str(selection) == \
        "[[0, 4, 'Tere'], [4, 5, '!'], [6, 9, 'Mis'], [10, 14, 'värk'], [15, 17, 'on'], [17, 18, '?']]"
        
    # select multiple index attributes from a level 1 enveloping layer
    selection = text['sentences'].attribute_values([], index_attributes=['start', 'end', 'text'])
    assert selection.attribute_names == ('start', 'end', 'text')
    assert str(selection) == "[[0, 5, ['Tere', '!']], [6, 18, ['Mis', 'värk', 'on', '?']]]"
    
    # AmbiguousAttributeTupleList
    # ===========================
    
    # select multiple attributes from multiple spans of an ambiguous layer
    assert text['morph_analysis']['lemma', 'form'] == \
        create_amb_attribute_list( [[['tere', '']], [['!', '']], [['mis', 'sg n'], ['mis', 'pl n']], [['värk', 'sg n']], 
                                    [['olema', 'b'], ['olema', 'vad']], [['?', '']]], ('lemma', 'form') )

    # select 1 index attribute from multiple spans of an ambiguous layer
    selection = text['morph_analysis'].attribute_values([], index_attributes=['start'])
    assert selection.attribute_names == ('start',)
    assert str(selection) == "[[[0]], [[4]], [[6], [6]], [[10]], [[15], [15]], [[17]]]"
    # TODO: index attributes mimic the layer ambiguity, although there is no ambiguity in index 
    # attributes themselves. should we correct this behavior?
    
    # select multiple index attributes from an ambiguous layer
    selection = text['morph_analysis'].attribute_values([], index_attributes=['start', 'end', 'text'])
    assert selection.attribute_names == ('start', 'end', 'text')
    assert str(selection) == \
        "[[[0, 4, 'Tere']], [[4, 5, '!']], [[6, 9, 'Mis'], [6, 9, 'Mis']], [[10, 14, 'värk']], "+\
        "[[15, 17, 'on'], [15, 17, 'on']], [[17, 18, '?']]]"


