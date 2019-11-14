import pytest

from copy import copy, deepcopy
from types import MethodType

from estnltk import Text
from estnltk import Layer
from estnltk import ElementaryBaseSpan

from estnltk.tests import inspect_class_members
from estnltk.tests import new_text


def test_object_teardown():
    # One cannot delete text object when layers are referenced!
    # This is a sad truth caused by reference counting memory model
    text = Text('Surematu Kašei')
    layer = Layer(name='empty_layer')
    text.add_layer(layer)
    del text
    assert layer.text_object.text == 'Surematu Kašei'


# noinspection PyArgumentList,SpellCheckingInspection
def test_copy_constructors():
    text = Text("Kihtideta teksti kopeerimine")

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers.keys() == text.layers.keys()

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers.keys() == text.layers.keys()

    # Check that deepcopy indeed uses the memo list
    # noinspection PyArgumentList
    d_copy = deepcopy(text, memo={id(text): text})
    assert d_copy is text
    d_copy = deepcopy(text, memo={id(s_copy): s_copy})
    assert d_copy is not text

    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text.nonempty_layer.add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text.nonempty_layer.add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.meta is text.meta
    assert s_copy.text is text.text
    assert s_copy.layers.keys() == text.layers.keys()
    for layer in s_copy.layers:
        assert s_copy[layer] is not text[layer]
        assert s_copy[layer] == text[layer]

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers.keys() == text.layers.keys()
    for layer in d_copy.layers:
        assert d_copy[layer] is not text[layer]
        assert d_copy[layer] == text[layer]

    text = Text("Rekursiivse metaga teksti kopeerimine")
    text.meta = {'text': text}

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers.keys() == text.layers.keys()

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta.keys() == text.meta.keys()
    assert d_copy.meta['text'] is d_copy
    assert d_copy.layers.keys() == text.layers.keys()

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

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers == text.layers

    d_copy = deepcopy(text)
    assert d_copy is not text
    assert d_copy.text == text.text
    assert d_copy.meta is not text.meta
    assert d_copy.meta == text.meta
    assert d_copy.layers.keys() == text.layers.keys()
    for layer in d_copy.layers:
        assert d_copy[layer] is not text[layer]
    assert d_copy.empty_layer == text.empty_layer
    assert len(d_copy.nonempty_layer) == 1
    # assert text.nonempty_layer[0]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text.nonempty_layer[0].layer is d_copy.nonempty_layer, "Fails as layers deep copy is incorrect"
    # assert text.nonempty_layer[0].espan is d_copy.nonempty_layer[0], "Fails as layers deep copy is incorrect"
    # assert text['text'][0]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text['text'][0].layer is d_copy['text'], "Fails as layers deep copy is incorrect"
    # assert text['text'][0].espan is d_copy['text'][0], "Fails as layers deep copy is incorrect"
    # assert text['text'][1]['text'] is d_copy, "Fails as layers deep copy is incorrect"
    # assert text['text'][1].layer is text.nonempty_layer, "Fails as layers deep copy is incorrect"
    # assert text['text'][0].espan is d_copy.nonempty_layer[0], "Fails as layers deep copy is incorrect"


# noinspection PyPropertyAccess,PyPropertyAccess
def test_attribute_assignment():
    # Attribute text is assignable under certain conditions
    with pytest.raises(AttributeError, match='raw text has already been set'):
        # noinspection PyPropertyAccess
        Text("Initsialiseeritud objekt").text = "Uus väärtus"
    with pytest.raises(TypeError, match='expecting a string as rvalue'):
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
    text.add_layer(Layer(name='innocent_bystander', attributes=['meta', '_text', '__dict__', '_shadowed_layers']))
    assert type(text.meta) == dict, "Attribute resolver cannot shadow slots"
    assert type(text._text) == str, "Attribute resolver cannot shadow slots"
    assert type(text.__dict__) == dict, "Attribute resolver cannot shadow slots"
    assert type(text._shadowed_layers) == dict, "Attribute resolver cannot shadow slots"


def test_normal_layer_access():
    text = Text('''Lennart Meri "Hõbevalge" on jõudnud rahvusvahelise lugejaskonnani.''')

    # Accessing non-existent layer
    with pytest.raises(AttributeError):
        _ = text.missing_layer
    with pytest.raises(KeyError):
        _ = text['missing_layer']

    # Accessing empty layer
    layer = Layer(name='empty_layer', attributes=['attr1'])
    text.add_layer(layer)

    assert text.empty_layer is layer
    assert text['empty_layer'] is layer
    assert text.empty_layer is text['empty_layer']

    with pytest.raises(IndexError):
        _ = text.empty_layer[0]
    with pytest.raises(IndexError):
        _ = text['empty_layer'][0]

    # Accessing non-empty layer
    layer = Layer(name='nonempty_layer', attributes=['attr_0', 'attr_1'])
    layer.add_annotation(ElementaryBaseSpan(0, 4), attr_0='L0-0', attr_1='100')
    text.add_layer(layer)

    assert text.nonempty_layer is layer
    assert text['nonempty_layer'] is layer

    assert text.nonempty_layer[0].attr_0 == 'L0-0'
    assert text['nonempty_layer'][0].attr_0 == 'L0-0'
    assert text.nonempty_layer[0] is text['nonempty_layer'][0]


def test_access_of_shadowed_layers():
    # List of all attributes that can be potentially shadowed
    properties = ['attributes', 'layers', 'text']
    private_methods = {method for method in dir(object) if callable(getattr(object, method, None))}
    public_methods = ['add_layer', 'analyse', 'delete_layer', 'diff', 'list_layers', 'set_text', 'tag_layer']
    protected_methods = ['_repr_html_']
    public_variables = ['attribute_mapping_for_elementary_layers', 'attribute_mapping_for_enveloping_layers', 'methods']
    slots = ['_text', '__dict__', 'meta', '_shadowed_layers']
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
    assert text.attributes == {}
    assert text.layers == {}
    assert text.attribute_mapping_for_elementary_layers == Text.attribute_mapping_for_elementary_layers
    assert text.attribute_mapping_for_enveloping_layers == Text.attribute_mapping_for_enveloping_layers
    assert text.methods == set(public_methods) | set(properties) | set(protected_methods) | private_methods

    # Shadowed layers are not present in a text without layers
    for layer_name in shadowed_layers:
        with pytest.raises(KeyError):
            _ = text[layer_name]

    # Shadowed layers can be created. No exceptions
    for layer_name in shadowed_layers:
        _ = Layer(name=layer_name, attributes=['attr'])

    # Shadowed layers are accessible
    other = Text('See on teine ilma kihtideta test tekst.')
    for layer_name in shadowed_layers:

        # Test access for empty layers
        layer = Layer(name=layer_name, attributes=['attr'])
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
    with pytest.raises(AssertionError, match="this Text object already has a layer with name 'empty_layer'"):
        text.add_layer(layer)

    # Safety against double linking
    text1 = Text('test1')
    layer = Layer(name='empty_layer', attributes=['attr'])
    text1.add_layer(layer)

    text2 = Text('test2')
    with pytest.raises(AssertionError,
                       match="can't add layer 'empty_layer', this layer is already bound to another Text object"):
        text2.add_layer(layer)

    # Other alternatives for layer assignment fail with reasonable error messages
    layer = Layer(name='empty_layer', attributes=['attr'])
    error_message = 'layers cannot be assigned directly, use add_layer\\(\\.\\.\\.\\) function instead'

    text = Text('test')
    with pytest.raises(TypeError, match=error_message):
        text['empty_layer'] = layer

    text = Text('test')
    with pytest.raises(AttributeError, match=error_message):
        text.empty_layer = layer


def test_delete_layer():
    text = Text('Minu nimi on Uku.')
    assert text.layers == {}

    layer_names = ['words', 'sentences', 'morph_analysis']

    text.tag_layer(layer_names)
    assert set(layer_names) <= set(text.layers)
    assert set(layer_names) <= set(text.__dict__)

    # Test del text.layer_name
    # Deleting a root layer should also delete all its dependants
    text.delete_layer('tokens')

    assert 'tokens' not in text.__dict__
    assert 'compound_tokens' not in text.__dict__

    text.delete_layer('words')

    assert 'words' not in text.__dict__
    assert 'sentences' not in text.__dict__
    assert 'morph_analysis' not in text.__dict__

    assert text.layers == {}

    # Test that deleted layers are indeed missing
    with pytest.raises(AttributeError):
        _ = text.words

    with pytest.raises(AttributeError):
        _ = text.sentences

    with pytest.raises(AttributeError):
        _ = text.morph_analysis

    # Test del text['layer_name']
    # Deleting a root layer should also delete all its dependants
    text.tag_layer(layer_names)

    text.delete_layer('tokens')

    assert 'tokens' not in text.__dict__
    assert 'compound_tokens' not in text.__dict__

    text.delete_layer('words')

    assert 'words' not in text.__dict__
    assert 'sentences' not in text.__dict__
    assert 'morph_analysis' not in text.__dict__

    assert text.layers == {}

    # Test that deleted layers are indeed missing
    with pytest.raises(AttributeError):
        _ = text.words

    with pytest.raises(AttributeError):
        _ = text.sentences

    with pytest.raises(AttributeError):
        _ = text.morph_analysis


def test_equal():
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
