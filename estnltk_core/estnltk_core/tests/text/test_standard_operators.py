import pytest

from copy import copy, deepcopy
from types import MethodType

from estnltk_core.common import load_text_class
from estnltk_core import Layer
from estnltk_core import ElementaryBaseSpan
from estnltk_core import EnvelopingBaseSpan, EnvelopingSpan

from estnltk_core.tests import inspect_class_members
from estnltk_core.tests import new_text

from estnltk_core.converters import layer_to_dict, dict_to_layer


def test_object_teardown():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # One cannot delete text object when layers are referenced!
    # This is a sad truth caused by reference counting memory model
    text = Text('Surematu Kašei')
    layer = Layer(name='empty_layer')
    text.add_layer(layer)
    del text
    assert layer.text_object.text == 'Surematu Kašei'


def test_shallow_copy():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text("Kihtideta teksti kopeerimine")
    error_msg = 'Shallow copying of {} object is not allowed. Use deepcopy instead.'.format(text.__class__.__name__)
    with pytest.raises(Exception, match=error_msg):
        s_copy = copy(text)


@pytest.mark.filterwarnings("ignore:Attribute names")
def test_deepcopy_constructor():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text("Kihtideta teksti kopeerimine")

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers == text.layers

    # Check that deepcopy indeed uses the memo list
    # noinspection PyArgumentList
    d_copy = deepcopy(text, memo={id(text): text})
    assert d_copy is text
    s_copy = Text("Kihtideta teksti kopeerimine")
    d_copy = deepcopy(text, memo={id(s_copy): s_copy})
    assert d_copy is not text

    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers == text.layers
    for layer in d_copy.layers:
        assert d_copy[layer] is not text[layer]
        assert d_copy[layer] == text[layer]
        # Check for text_object value equality
        assert d_copy[layer].text_object == d_copy
        for span in d_copy[layer]:
            assert span.text_object == d_copy

    # check copying text w enveloping layer
    text.add_layer(Layer('enveloping_layer', attributes=['c'], enveloping='nonempty_layer'))
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [s.base_span for s in text['nonempty_layer']] ), \
                               layer=text['enveloping_layer'] )
    text['enveloping_layer'].add_annotation( env_span, c=9 )

    d_copy = deepcopy(text)
    layer = 'enveloping_layer'
    assert d_copy[layer] is not text[layer]
    assert d_copy[layer] == text[layer]
    assert d_copy[layer].text_object == d_copy
    assert d_copy[layer].enveloping == 'nonempty_layer'
    for env_span in d_copy[layer]:
        assert env_span.text_object == d_copy
        assert list(env_span.spans) == d_copy['nonempty_layer'].spans

    text = Text("Rekursiivse metaga teksti kopeerimine")
    text.meta = {'text': text}

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta.keys() == text.meta.keys()
    assert d_copy.meta['text'] is d_copy
    assert d_copy.layers == text.layers
    
    text = Text("Rekursiivsete kihtidega teksti kopeerimine")
    text.add_layer(Layer('empty_layer', attributes=[]))
    with pytest.warns(UserWarning, match='Attribute names.+overlap with Span/Annotation property names.+'):
        text.add_layer(Layer('nonempty_layer', attributes=['text', 'layer', 'espan']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text['nonempty_layer'])
    text['nonempty_layer'][0].espan = text['nonempty_layer'][0]
    text.add_layer(Layer('text', attributes=['text', 'layer', 'espan']))
    text['text'].add_annotation(ElementaryBaseSpan(0, 4), text=text, layer=text['text'], espan=None)
    text['text'][0].espan = text['text'][0]
    text['text'].add_annotation(ElementaryBaseSpan(5, 8), text=text, layer=text['nonempty_layer'], espan=None)
    text['text'][1].espan = text['nonempty_layer'][0]

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers == text.layers
    for layer in d_copy.layers:
        assert d_copy[layer] is not text[layer]
    assert d_copy['empty_layer'] == text['empty_layer']
    assert len(d_copy['nonempty_layer']) == 1
    # assert text.nonempty_layer[0]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text.nonempty_layer[0].layer is d_copy.nonempty_layer, "Fails as layers deep copy is incorrect"
    # assert text.nonempty_layer[0].espan is d_copy.nonempty_layer[0], "Fails as layers deep copy is incorrect"
    # assert text['text'][0]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text['text'][0].layer is d_copy['text'], "Fails as layers deep copy is incorrect"
    # assert text['text'][0].espan is d_copy['text'][0], "Fails as layers deep copy is incorrect"
    # assert text['text'][1]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text['text'][1].layer is text.nonempty_layer, "Fails as layers deep copy is incorrect"
    # assert text['text'][0].espan is d_copy.nonempty_layer[0], "Fails as layers deep copy is incorrect"


def test_deepcopy_reference_equality():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()

    # 1) check copying text w simple layers
    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)

    d_copy = deepcopy(text)
    assert d_copy is not text
    for layer in d_copy.layers:
        # Check for text_object reference equality 
        assert d_copy[layer].text_object is d_copy
        assert d_copy[layer].text_object is not text
        for span in d_copy[layer]:
            # Spans point to the new text obj
            assert span.text_object is d_copy
            assert span.text_object is not text

    # 2) check copying text w enveloping layer
    text.add_layer(Layer('enveloping_layer', attributes=['c'], enveloping='nonempty_layer'))
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [s.base_span for s in text['nonempty_layer']] ), \
                               layer=text['enveloping_layer'] )
    text['enveloping_layer'].add_annotation( env_span, c=9 )
    
    d_copy = deepcopy(text)
    assert d_copy['enveloping_layer'].text_object is d_copy
    assert d_copy['enveloping_layer'].enveloping == 'nonempty_layer'
    for env_span in d_copy['enveloping_layer']:
        # Spans point to the new text obj
        assert env_span.text_object is not text
        assert env_span.text_object is d_copy
        for sid, span in enumerate(env_span.spans):
            assert span is d_copy['nonempty_layer'][sid]

    # 3) check copying text w parent layers
    text.add_layer(Layer('child_layer_1', attributes=['d'], parent='nonempty_layer'))
    text.add_layer(Layer('child_layer_2', attributes=['e'], parent='child_layer_1'))
    text['child_layer_1'].add_annotation( text['nonempty_layer'][0].base_span, d=10 )
    text['child_layer_1'].add_annotation( text['nonempty_layer'][1].base_span, d=12 )
    text['child_layer_2'].add_annotation( text['child_layer_1'][0].base_span, e=20 )
    text['child_layer_2'].add_annotation( text['child_layer_1'][1].base_span, e=22 )

    d_copy = deepcopy(text)
    assert d_copy['child_layer_1'].text_object is d_copy
    assert d_copy['child_layer_2'].text_object is d_copy
    # Check that spans point to the new text obj
    for sid, child_span in enumerate( d_copy['child_layer_1'] ):
        assert child_span.text_object is not text
        assert child_span.text_object is d_copy
        assert child_span is d_copy['child_layer_1'][sid]
        assert child_span.parent is d_copy['nonempty_layer'][sid]
    for sid, child_span in enumerate( d_copy['child_layer_2'] ):
        assert child_span.text_object is not text
        assert child_span.text_object is d_copy
        assert child_span is d_copy['child_layer_2'][sid]
        assert child_span.parent is d_copy['child_layer_1'][sid]


def test_attribute_assignment():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # Attribute text is assignable under certain conditions
    with pytest.raises(AttributeError, match='raw text has already been set'):
        # noinspection PyPropertyAccess
        Text("Initsialiseeritud objekt").text = "Uus väärtus"
    with pytest.raises(TypeError, match='expecting a string as value'):
        Text().text = 5
    text = Text()
    assert text.text is None
    text.text = 'Uus väärtus'
    assert text.text == 'Uus väärtus'

    # Attribute meta is assignable with a right dictionary
    with pytest.raises(ValueError, match='meta must be of type dict'):
        Text().meta = 5
    with pytest.raises(ValueError, match='meta must be of type dict with keys of type str'):
        Text().meta = {1: 'a', '2': 0}
    text = Text()
    assert text.meta == {}
    text.meta = {'a': 'a', 'b': 1}
    assert text.meta == {'a': 'a', 'b': 1}
    text.meta = {}
    assert text.meta == {}

    # No other attribute is assignable
    text = Text()
    error_pattern = 'layers cannot be assigned directly, use add_layer\\(\\.\\.\\.\\) function instead'
    for attribute in set(dir(text)) - {'text', 'meta'}:
        with pytest.raises(AttributeError, match=error_pattern):
            setattr(text, attribute, '42')
    text.add_layer(Layer('existing_layer', attributes=[]))
    with pytest.raises(AttributeError, match=error_pattern):
        text.existing_layer = '42'
    with pytest.raises(AttributeError, match=error_pattern):
        text.missing_layer = '42'


def test_item_assignment():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # No item is assignable
    text = Text()
    error_pattern = 'layers cannot be assigned directly, use add_layer\\(\\.\\.\\.\\) function instead'
    for attribute in set(dir(text)) - {'text', 'meta'}:
        with pytest.raises(TypeError, match=error_pattern):
            text[attribute] = '42'
    text.add_layer(Layer('existing_layer', attributes=[]))
    with pytest.raises(TypeError, match=error_pattern):
        text['existing_layer'] = '42'
    with pytest.raises(TypeError, match=error_pattern):
        text['missing_layer'] = '42'


def test_abnormal_attribute_access():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # Test for shadowing errors
    text = Text('Äkksurm varjuteatris')
    text.add_layer(Layer(name='add_layer'))
    assert type(text.add_layer) == MethodType, "Layers cannot shadow methods"
    text.add_layer(Layer(name='new_layer'))

    # Test that attribute resolving does not introduce shadowing errors for methods
    text = Text('Šaakali päev')
    text.add_layer(Layer(name='innocent_bystander', attributes=['add_layer']))
    assert type(text.add_layer) == MethodType, "Attribute resolver cannot shadow methods"
    text.add_layer(Layer(name='new_layer'))

    # Test that attribute resolving does not introduce shadowing errors for slots
    text = Text('Poola zloti devalveerimine')
    text.add_layer(Layer(name='innocent_bystander', attributes=['meta', '_text', '_layers']))
    assert type(text.meta) == dict, "Attribute resolver cannot shadow slots"
    assert type(text.text) == str, "Attribute resolver cannot shadow slots"
    assert type(text._layers) == dict, "Attribute resolver cannot shadow slots"

    if Text().__class__.__name__ == 'BaseText':
        text = Text('Suflee kahele')
        text.add_layer(Layer(name='new_layer'))
        # BaseText supports accessing layers via brackets
        _ = text['new_layer']
        # BaseText does not support accessing layers as attributes
        with pytest.raises(AttributeError):
            _ = text.new_layer


def test_normal_layer_access():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('''Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.''')

    # Accessing non-existent layer
    with pytest.raises(AttributeError):
        _ = text.missing_layer
    with pytest.raises(KeyError):
        _ = text['missing_layer']

    # Accessing empty layer
    layer = Layer(name='empty_layer', attributes=['attr1'])
    text.add_layer(layer)

    assert text['empty_layer'] is layer
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]
    
    if Text().__class__.__name__ == 'Text':
        # .attr access will only be available in estnltk-standard
        assert text.empty_layer is layer
        assert text.empty_layer is text['empty_layer']

        with pytest.raises(IndexError):
            _ = text.empty_layer[0]

    # Accessing non-empty layer
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)

    assert text['nonempty_layer'] is layer
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    
    if Text().__class__.__name__ == 'Text':
        # .attr access will only be available in estnltk-standard
        assert text.nonempty_layer is layer
        assert text.nonempty_layer[0].attr_0 == 'L0-0'
        assert text.nonempty_layer[0] is text['nonempty_layer'][0]


def test_access_of_shadowed_layers():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # List of all attributes that can be potentially shadowed
    if Text().__class__.__name__ == 'BaseText':
        properties = ['layers']
    else:
        properties = ['layer_attributes', 'layers']
    private_methods = {method for method in dir(object) if callable(getattr(object, method, None))}
    public_methods = ['add_layer', 'analyse', 'diff', 'pop_layer', 'sorted_layers', 'tag_layer', 'topological_sort']
    protected_methods = ['_repr_html_']
    if Text().__class__.__name__ == 'BaseText':
        public_variables = []
    else:
        public_variables = [ 'attribute_mapping_for_elementary_layers', \
                             'attribute_mapping_for_enveloping_layers', \
                             'layer_resolver', \
                             'methods',
                             'presorted_layers' ]
    slots = ['text', 'meta', '_layers']
    shadowed_layers = properties + public_methods + protected_methods + public_variables + slots

    # Check that lists are correct
    members = inspect_class_members(Text())
    assert properties == members['properties']
    assert public_variables == members['public_variables']
    assert public_methods == members['public_methods']
    assert slots == Text.__slots__

    # Check that all attributes are present
    text = Text('See on kihtideta tekst')
    assert text.text == 'See on kihtideta tekst'
    assert text.meta == {}
    assert text.layers == set()
    if Text().__class__.__name__ == 'Text':
        assert text.layer_attributes == {}
        assert text.methods == set(public_methods) | set(properties) | set(protected_methods) | private_methods

    # Shadowed layers are not present in a text without layers
    for layer_name in shadowed_layers:
        with pytest.raises(KeyError):
            _ = text[layer_name]

    # Shadowed layers can be created. No exceptions
    for layer_name in shadowed_layers:
        _ = Layer(name=layer_name, attributes=['attr'])

    # Test accessibility of a shadowed layer -- only brackets access allowed
    other = Text('See on teine ilma kihtideta test tekst.')
    for layer_name in shadowed_layers:
        # Test access for empty layers
        layer = Layer(name=layer_name, attributes=['attr'])
        # successfully add shadowed layer
        text.add_layer(layer)
        assert text[layer_name] is layer
        with pytest.raises(IndexError):
            _ = text[layer_name][0]

        # # Test access for non-empty layers
        layer = Layer(name=layer_name, attributes=['attr_0', 'attr_1'])
        layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
        other.add_layer(layer)

        assert other[layer_name] is layer
        assert other[layer_name][0].attr_0 == 'L0-0'
        assert other[layer_name][0] == layer[0]



def test_attribute_resolver():
    # Unique layer attributes are resolved
    pass
    # attribute layer mapping is used for resolving


def test_add_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    # The only way to add a layer
    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text.add_layer(layer)
    assert text['empty_layer'] is layer
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    text = Text('test')
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)
    assert text['nonempty_layer'] is layer
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0] == layer[0]

    # Safety against recursive references in layers
    text = Text('Rekursioon, rekursioon. Sind vaid loon')
    layer = Layer(name='recursive_layer', attributes=['recursive_ref_1', 'recursive_ref_2', 'recursive_ref_3'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), recursive_ref_1=text, recursive_ref_2=layer, recursive_ref_3=None)
    annotation = layer[0].annotations[0]
    layer[0].recursive_ref_3 = annotation
    text.add_layer(layer)
    assert text['recursive_layer'] is layer
    assert text['recursive_layer'][0].annotations[0].recursive_ref_1 is text
    assert text['recursive_layer'][0].annotations[0].recursive_ref_2 is layer
    assert text['recursive_layer'][0].annotations[0].recursive_ref_3 is annotation

    # Safety against double invocation
    text = Text('test')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text.add_layer(layer)
    with pytest.raises(AssertionError, match="this (Text|BaseText) object already has a layer with name 'empty_layer'"):
        text.add_layer(layer)

    # Safety against double linking
    text1 = Text('test1')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text1.add_layer(layer)

    text2 = Text('test2')
    with pytest.raises(AssertionError,
                       match="can't add layer 'empty_layer', this layer is already bound to another (Text|BaseText) object"):
        text2.add_layer(layer)

    # Other alternatives for layer assignment fail with reasonable error messages
    layer = Layer(name='empty_layer', attributes=['attr'])
    error_message = 'layers cannot be assigned directly, use add_layer\\(\\.\\.\\.\\) function instead'

    text = Text('test')
    with pytest.raises(TypeError, match=error_message):
        text['empty_layer'] = layer

    if Text().__class__.__name__ == 'Text':
        # .attr access will only be available in estnltk-standard
        text = Text('test')
        with pytest.raises(AttributeError, match=error_message):
            text.empty_layer = layer


def test_pop_layer():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Minu nimi on Uku.')
    assert text.layers == set()

    layer_names = ['words', 'sentences', 'morph_analysis']

    # text.tag_layer(layer_names)
    # simulated by the code below

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
    compound_tokens_layer = dict_to_layer({'name': 'compound_tokens',
                                           'attributes': ('type', 'normalized'),
                                           'parent': None,
                                           'enveloping': 'tokens',
                                           'ambiguous': False,
                                           'serialisation_module': None,
                                           'meta': {},
                                           'spans': []})
    text.add_layer(compound_tokens_layer)
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

    assert set(layer_names) <= set(text.layers)

    # Test del text.layer_name
    # Deleting a root layer should also delete all its dependants
    text.pop_layer('tokens')

    assert 'tokens' not in text.layers
    assert 'compound_tokens' not in text.layers

    text.pop_layer('words')

    assert 'words' not in text.layers
    assert 'sentences' not in text.layers
    assert 'morph_analysis' not in text.layers

    assert text.layers == set()

    # Test that deleted layers are indeed missing
    with pytest.raises(KeyError):
        _ = text['words']

    with pytest.raises(KeyError):
        _ = text['sentences']

    with pytest.raises(KeyError):
        _ = text['morph_analysis']

    # Test del text['layer_name']
    # Deleting a root layer should also delete all its dependants
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
    compound_tokens_layer = dict_to_layer({'name': 'compound_tokens',
                                           'attributes': ('type', 'normalized'),
                                           'parent': None,
                                           'enveloping': 'tokens',
                                           'ambiguous': False,
                                           'serialisation_module': None,
                                           'meta': {},
                                           'spans': []})
    text.add_layer(compound_tokens_layer)
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

    text.pop_layer('tokens')

    assert 'tokens' not in text.layers
    assert 'compound_tokens' not in text.layers

    text.pop_layer('words')

    assert 'words' not in text.layers
    assert 'sentences' not in text.layers
    assert 'morph_analysis' not in text.layers

    assert text.layers == set()

    # Test that deleted layers are indeed missing
    with pytest.raises(KeyError):
        _ = text['words']

    with pytest.raises(KeyError):
        _ = text['sentences']

    with pytest.raises(KeyError):
        _ = text['morph_analysis']

    # Test more obscure configurations


def test_equal():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # TODO: Make comparison secure against recursion!

    t_1 = Text('Tekst algab. Tekst lõpeb.')
    t_2 = Text('Tekst algab.')
    assert t_1 != t_2
    t_2 = Text('Tekst algab. Tekst lõpeb.')
    assert t_1 == t_2

    t_1.meta['year'] = 2017
    assert t_1 != t_2
    t_2.meta['year'] = 2017
    assert t_1 == t_2

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
                                 'spans': [{'base_span': (0, 5),
                                            'annotations': [{'normalized_text': 'Tekst',
                                                             'lemma': 'tekst',
                                                             'root': 'tekst',
                                                             'root_tokens': ['tekst'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'S'}]},
                                           {'base_span': (6, 11),
                                            'annotations': [{'normalized_text': 'algab',
                                                             'lemma': 'algama',
                                                             'root': 'alga',
                                                             'root_tokens': ['alga'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'}]},
                                           {'base_span': (11, 12),
                                            'annotations': [{'normalized_text': '.',
                                                             'lemma': '.',
                                                             'root': '.',
                                                             'root_tokens': ['.'],
                                                             'ending': '',
                                                             'clitic': '',
                                                             'form': '',
                                                             'partofspeech': 'Z'}]},
                                           {'base_span': (13, 18),
                                            'annotations': [{'normalized_text': 'Tekst',
                                                             'lemma': 'tekst',
                                                             'root': 'tekst',
                                                             'root_tokens': ['tekst'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'S'}]},
                                           {'base_span': (19, 24),
                                            'annotations': [{'normalized_text': 'lõpeb',
                                                             'lemma': 'lõppema',
                                                             'root': 'lõppe',
                                                             'root_tokens': ['lõppe'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'},
                                                            {'normalized_text': 'lõpeb',
                                                             'lemma': 'lõpma',
                                                             'root': 'lõp',
                                                             'root_tokens': ['lõp'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'}]},
                                           {'base_span': (24, 25),
                                            'annotations': [{'normalized_text': '.',
                                                             'lemma': '.',
                                                             'root': '.',
                                                             'root_tokens': ['.'],
                                                             'ending': '',
                                                             'clitic': '',
                                                             'form': '',
                                                             'partofspeech': 'Z'}]}]})
    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 5), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (6, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 24), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (24, 25), 'annotations': [{'normalized_form': None}]}]})

    t_1.add_layer(words_layer)
    t_1.add_layer(morph_layer)
    assert t_1 != t_2
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
                                 'spans': [{'base_span': (0, 5),
                                            'annotations': [{'normalized_text': 'Tekst',
                                                             'lemma': 'tekst',
                                                             'root': 'tekst',
                                                             'root_tokens': ['tekst'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'S'}]},
                                           {'base_span': (6, 11),
                                            'annotations': [{'normalized_text': 'algab',
                                                             'lemma': 'algama',
                                                             'root': 'alga',
                                                             'root_tokens': ['alga'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'}]},
                                           {'base_span': (11, 12),
                                            'annotations': [{'normalized_text': '.',
                                                             'lemma': '.',
                                                             'root': '.',
                                                             'root_tokens': ['.'],
                                                             'ending': '',
                                                             'clitic': '',
                                                             'form': '',
                                                             'partofspeech': 'Z'}]},
                                           {'base_span': (13, 18),
                                            'annotations': [{'normalized_text': 'Tekst',
                                                             'lemma': 'tekst',
                                                             'root': 'tekst',
                                                             'root_tokens': ['tekst'],
                                                             'ending': '0',
                                                             'clitic': '',
                                                             'form': 'sg n',
                                                             'partofspeech': 'S'}]},
                                           {'base_span': (19, 24),
                                            'annotations': [{'normalized_text': 'lõpeb',
                                                             'lemma': 'lõppema',
                                                             'root': 'lõppe',
                                                             'root_tokens': ['lõppe'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'},
                                                            {'normalized_text': 'lõpeb',
                                                             'lemma': 'lõpma',
                                                             'root': 'lõp',
                                                             'root_tokens': ['lõp'],
                                                             'ending': 'b',
                                                             'clitic': '',
                                                             'form': 'b',
                                                             'partofspeech': 'V'}]},
                                           {'base_span': (24, 25),
                                            'annotations': [{'normalized_text': '.',
                                                             'lemma': '.',
                                                             'root': '.',
                                                             'root_tokens': ['.'],
                                                             'ending': '',
                                                             'clitic': '',
                                                             'form': '',
                                                             'partofspeech': 'Z'}]}]})
    words_layer = dict_to_layer({'name': 'words',
                                 'attributes': ('normalized_form',),
                                 'parent': None,
                                 'enveloping': None,
                                 'ambiguous': True,
                                 'serialisation_module': None,
                                 'meta': {},
                                 'spans': [{'base_span': (0, 5), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (6, 11), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (11, 12), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (13, 18), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (19, 24), 'annotations': [{'normalized_form': None}]},
                                           {'base_span': (24, 25), 'annotations': [{'normalized_form': None}]}]})
    t_2.add_layer(words_layer)
    t_2.add_layer(morph_layer)
    assert t_1 == t_2
    t_1['morph_analysis'][0].annotations[0].form = 'x'
    assert t_1 != t_2

    t_1 = new_text(5)
    t_2 = new_text(5)
    assert t_1 == t_2
    t_1['layer_5'][1].annotations[1].attr_5 = 'bla'
    assert t_1 != t_2



def test_text_diff():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # case 1: simple texts with layers and metadata
    text1 = Text('Tshempionite eine kahele')
    text1.meta['author'] = 'K. Vonnegut'
    text1.add_layer( Layer('notes', attributes=('remark',) ) )
    text1['notes'].add_annotation( (0, 17), remark='this is title' )
    # check identity
    assert text1.diff( text1 ) == None
    # check uncomparable type
    assert text1.diff('some string') == 'Not a {} object.'.format( Text().__class__.__name__ )
    # check different raw text
    assert text1.diff( Text('Tshempionite hommikusöök') ) == 'The raw text is different.'
    # check different layer names
    text2 = Text('Tshempionite eine kahele')
    text2.meta['author'] = 'K. Vonnegut'
    text2.add_layer( Layer('remarks', attributes=('note',) ) )
    assert text1.diff( text2 ) == 'Different layer names: {} != {}'.format(set(text1.layers), set(text2.layers))
    # check different metadata
    text3 = Text('Tshempionite eine kahele')
    text3.meta['author'] = 'K. Vonnegut'
    text3.meta['publishing_date'] = 1973
    text3.add_layer( Layer('notes', attributes=('remark',) ) )
    text3['notes'].add_annotation( (0, 17), remark='this is title' )
    assert text1.diff( text3 ) == 'Different metadata.'
    # check difference inside a layer
    del text3.meta['publishing_date']
    text3['notes'].add_annotation( (0, 12), remark="title's first word" )
    assert text1.diff( text3 ) == '{} layer spans differ'.format('notes')
    text4 = Text('Tshempionite eine kahele')
    text4.meta['author'] = 'K. Vonnegut'
    text4.add_layer( Layer('notes', attributes=('remark',) ) )
    text4['notes'].add_annotation( (0, 17), remark='this may be a title' )
    assert text1.diff( text4 ) == '{} layer spans differ'.format('notes')
    
    # case 2: simple texts with shadowed layers
    text1 = Text('Tshempionite eine kahele')
    text1.add_layer( Layer('words') )
    text1.add_layer( Layer('diff') )
    text1.add_layer( Layer('tag_layer') )
    text2 = Text('Tshempionite eine kahele')
    text2.add_layer( Layer('words') )
    text2.add_layer( Layer('sorted_layers') )
    text2.add_layer( Layer('layers') )
    assert text1.diff(text2) == 'Different layer names: {} != {}'.format(set(text1.layers), set(text2.layers))


@pytest.mark.skip(reason='currently throws a RecursionError, needs fixing')
def test_text_diff_recursion_problems():
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    # case 1: texts with recursive metadata
    text1 = Text('Tshempionite eine kahele')
    text1.meta['text'] = text1
    text2 = Text('Tshempionite eine kahele')
    text2.meta['text'] = text2
    # throws RecursionError: maximum recursion depth exceeded
    assert text1.diff( text2 ) == 'Different metadata.'

    # case 2: texts with recursive annotation data
    text1 = Text('Tshempionite eine kolmele')
    text1.add_layer(Layer('rec_layer', attributes=['text', 'layer']))
    text1['rec_layer'].add_annotation(ElementaryBaseSpan(0, 12), text=text1, layer=text1['rec_layer'])
    text2 = Text('Tshempionite eine kolmele')    
    text2.add_layer(Layer('rec_layer', attributes=['text', 'layer']))
    text2['rec_layer'].add_annotation(ElementaryBaseSpan(0, 12), text=text2, layer=text2['rec_layer'])
    # throws RecursionError: maximum recursion depth exceeded while calling a Python object
    assert text1.diff( text2 ) == '{} layer annotations differ'.format('rec_layer')


def test_text_repr_and_str( capsys ):
    # Load Text or BaseText class (depending on the available packages)
    Text = load_text_class()
    
    text = Text('Suflee kolmele')
    if Text().__class__.__name__ == 'BaseText':
        assert str(text)  == "BaseText(text={!r})".format( text.text )
        assert repr(text) == "BaseText(text={!r})".format( text.text )
        print( text )
        captured = capsys.readouterr()
        assert captured.out == "BaseText(text={!r})\n".format( text.text )
    else:
        assert str(text)  == "Text(text={!r})".format( text.text )
        assert repr(text) == "Text(text={!r})".format( text.text )
        print( text )
        captured = capsys.readouterr()
        assert captured.out == "Text(text={!r})\n".format( text.text )
    
    
