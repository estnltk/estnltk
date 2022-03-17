from estnltk import Layer
from estnltk import Text

from estnltk.taggers.system.rule_taggers import StaticExtractionRule
from estnltk.taggers.system.rule_taggers import DynamicExtractionRule


def test_static_extraction_rules():
    # Standard rule
    rule = StaticExtractionRule('no', {'value': False, 'language': 'English'})
    assert(rule.pattern == 'no')
    assert(not rule.attributes['value'])
    assert(rule.attributes['language'] == 'English')

    # Rule with abnormal attributes
    rule = StaticExtractionRule('jah', {'pattern': True, 'attributes': 'Estonian'})
    assert(rule.pattern == 'jah')
    assert(rule.attributes['pattern'])
    assert(rule.attributes['attributes'] == 'Estonian')

def test_dynamic_extraction_rules():
    # Standard rule
    rule = DynamicExtractionRule('word', lambda x:
    {
        'entire_text': x.text_object.text,
        'extracted_text': x.text,
        'left_context': x.text_object.text[0:x.start],
        'right_context': x.text_object.text[x.end:],
        'layer_name': x.layer.name
    })
    assert(rule.pattern == 'word')
    text = Text('left-word-right')
    layer = Layer('test', text_object=text)
    layer.add_annotation((5, 9))
    attributes = rule.decorator(layer[0])
    assert attributes['entire_text'] == 'left-word-right'
    assert attributes['extracted_text'] == 'word'
    assert attributes['left_context'] == 'left-'
    assert attributes['right_context'] == '-right'

    # Conditional extraction rule
    rule = DynamicExtractionRule('word', lambda x: {'extracted_text': x.text} if x.start == 0 else None)
    text = Text('left-word-right')
    layer = Layer('test', text_object=text)
    layer.add_annotation((5, 9))
    result = rule.decorator(layer[0])
    assert result is None
    text = Text('word-right')
    layer = Layer('test', text_object=text)
    layer.add_annotation((0, 4))
    result = rule.decorator(layer[0])
    assert result is not None
    assert result['extracted_text'] == 'word'

