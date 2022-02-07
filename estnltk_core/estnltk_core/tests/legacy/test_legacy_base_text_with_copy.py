#
#  Legacy tests for BaseText that supports shallow copy
#  Note that shallow copying deprecated and no longer supported
#
import pytest

from copy import copy

from estnltk_core.legacy.base_text_with_copy import BaseTextWithCopy
from estnltk_core import Layer
from estnltk_core import ElementaryBaseSpan
from estnltk_core import EnvelopingBaseSpan, EnvelopingSpan

from estnltk_core.converters import layer_to_dict, dict_to_layer

@pytest.mark.filterwarnings("ignore:Attribute names")
def test_shallow_copy_constructor():
    Text = BaseTextWithCopy
    
    text = Text("Kihtideta teksti kopeerimine")
    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers == text.layers

    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.meta is text.meta
    assert s_copy.text is text.text
    assert s_copy.layers == text.layers
    for layer in s_copy.layers:
        assert s_copy[layer] is not text[layer]
        assert s_copy[layer] == text[layer]
        # Check for text_object value equality
        assert s_copy[layer].text_object == s_copy
        for span in s_copy[layer]:
            assert span.text_object == s_copy

    # check copying text w enveloping layer
    text.add_layer(Layer('enveloping_layer', attributes=['c'], enveloping='nonempty_layer'))
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [s.base_span for s in text['nonempty_layer']] ), \
                               layer=text['enveloping_layer'] )
    text['enveloping_layer'].add_annotation( env_span, c=9 )

    s_copy = copy(text)
    layer = 'enveloping_layer'
    assert s_copy[layer] is not text[layer]
    assert s_copy[layer] == text[layer]
    assert s_copy[layer].text_object == s_copy
    assert s_copy[layer].enveloping == 'nonempty_layer'
    for env_span in s_copy[layer]:
        assert env_span.text_object == s_copy
        assert list(env_span.spans) == s_copy['nonempty_layer'].spans

    text = Text("Rekursiivse metaga teksti kopeerimine")
    text.meta = {'text': text}

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers == text.layers

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

    s_copy = copy(text)
    assert s_copy is not text
    assert s_copy.text is text.text
    assert s_copy.meta is text.meta
    assert s_copy.layers == text.layers


def test_shallow_copy_reference_equality():
    Text = BaseTextWithCopy

    # 1) check copying text w simple layers
    text = Text("Lihtsate kihtidega teksti kopeerimine")
    text.meta = {'a': 55, 'b': 53}
    text.add_layer(Layer('empty_layer', attributes=[]))
    text.add_layer(Layer('nonempty_layer', attributes=['a', 'b']))
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(0, 4), a=1, b=2)
    text['nonempty_layer'].add_annotation(ElementaryBaseSpan(5, 8), a=3, b=4)
    
    s_copy = copy(text)
    assert s_copy is not text
    for layer in s_copy.layers:
        # Check for text_object reference equality 
        assert s_copy[layer].text_object is s_copy
        assert s_copy[layer].text_object is not text
        for span in s_copy[layer]:
            # Spans still point to the original text obj
            assert span.text_object is text
            assert span.text_object is not s_copy

    # 2) check copying text w enveloping layer
    text.add_layer(Layer('enveloping_layer', attributes=['c'], enveloping='nonempty_layer'))
    env_span = EnvelopingSpan( EnvelopingBaseSpan( [s.base_span for s in text['nonempty_layer']] ), \
                               layer=text['enveloping_layer'] )
    text['enveloping_layer'].add_annotation( env_span, c=9 )
    
    s_copy = copy(text)
    assert s_copy['enveloping_layer'].text_object is s_copy
    assert s_copy['enveloping_layer'].enveloping == 'nonempty_layer'
    for env_span in s_copy['enveloping_layer']:
        # Spans still point to the original text obj
        assert env_span.text_object is text
        assert env_span.text_object is not s_copy
        for sid, span in enumerate(env_span.spans):
            assert span is text['nonempty_layer'][sid]

    # 3) check copying text w parent layers
    text.add_layer(Layer('child_layer_1', attributes=['d'], parent='nonempty_layer'))
    text.add_layer(Layer('child_layer_2', attributes=['e'], parent='child_layer_1'))
    text['child_layer_1'].add_annotation( text['nonempty_layer'][0].base_span, d=10 )
    text['child_layer_1'].add_annotation( text['nonempty_layer'][1].base_span, d=12 )
    text['child_layer_2'].add_annotation( text['child_layer_1'][0].base_span, e=20 )
    text['child_layer_2'].add_annotation( text['child_layer_1'][1].base_span, e=22 )
    
    s_copy = copy(text)
    assert s_copy['child_layer_1'].text_object is s_copy
    assert s_copy['child_layer_2'].text_object is s_copy
    # Check that spans still point to the original text obj
    for sid, child_span in enumerate( s_copy['child_layer_1'] ):
        assert child_span.text_object is text
        assert child_span.text_object is not s_copy
        assert child_span is text['child_layer_1'][sid]
        assert child_span.parent is text['nonempty_layer'][sid]
    for sid, child_span in enumerate( s_copy['child_layer_2'] ):
        assert child_span.text_object is text
        assert child_span.text_object is not s_copy
        assert child_span is text['child_layer_2'][sid]
        assert child_span.parent is text['child_layer_1'][sid]

