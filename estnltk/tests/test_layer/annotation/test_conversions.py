from estnltk import Text
from estnltk import Layer
from estnltk import Span
from estnltk import Annotation
from estnltk import ElementaryBaseSpan


def test_pickle():
    import pickle

    def save_restore(input_annotation: Annotation) -> Annotation:
        binary_repr = pickle.dumps(input_annotation)
        return pickle.loads(binary_repr)

    # Non-recursive annotations without the span
    annotation = Annotation(span=None)
    result = save_restore(annotation)
    assert result.span is None
    assert result.mapping == dict()

    annotation = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    result = save_restore(annotation)
    assert result.span is None
    assert result.mapping == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'})

    annotation = Annotation(span=None, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __getstate__='its gonna fail without arrangements')
    result = save_restore(annotation)
    assert result.span is None
    assert result.mapping == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                                  end=['a', 'b'], __getstate__='its gonna fail without arrangements')

    # Span in a layer must have all attributes required by the layer but pickling does not care!
    layer = Layer('test_layer', attributes=['attr_1', 'attr_2', 'attr_3'], text_object=Text('Tere!'))
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span)
    result = save_restore(annotation)
    assert result.span == annotation.span
    assert result.mapping == dict()
    # The order of attributes is determined by the order of attributes in the layer but pickling does not care!
    layer = Layer('test_layer', attributes=['number', 'string', 'dict'], text_object=Text('Tere!'))
    span = Span(base_span=ElementaryBaseSpan(0, 4), layer=layer)
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    result = save_restore(annotation)
    assert result.span == annotation.span
    assert result.mapping == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'})
    # There are no restrictions what attribute names are for the layer
    layer = Layer('test_layer', attributes=['number', 'string', 'dict', 'end', '__setstate__'], text_object=Text('Jah'))
    span = Span(base_span=ElementaryBaseSpan(0, 3), layer=layer)
    annotation = Annotation(span=span, number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                            end=['a', 'b'], __setstate__='its gonna fail without arrangements')
    result = save_restore(annotation)
    assert result.span == annotation.span
    assert result.mapping == dict(number=42, string='twelve', dict={'a': 15, 'b': 'one'},
                                  end=['a', 'b'], __setstate__='its gonna fail without arrangements')

    # Simple test that pickling is recursion safe
    annotation = Annotation(span=None)
    annotation.update(dict(number=42, string='twelve', dict={'a': 15, 'b': annotation}, rec=annotation))
    result = save_restore(annotation)
    assert result.span == annotation.span
    assert set(result.mapping.keys()) == {'number', 'string', 'dict', 'rec'}
    assert result['number'] == 42
    assert result['string'] == 'twelve'
    assert set(result['dict'].keys()) == {'a', 'b'}
    assert result['dict']['a'] == 15
    assert result['dict']['b'] is result
    assert result['rec'] is result
