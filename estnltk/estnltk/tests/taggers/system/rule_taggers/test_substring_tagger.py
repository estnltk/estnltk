from estnltk.taggers.system.rule_taggers import Ruleset
from estnltk.taggers.system.rule_taggers import StaticExtractionRule
from estnltk.taggers.system.rule_taggers import DynamicExtractionRule
from estnltk.taggers.system.rule_taggers import SubstringTagger

from estnltk import Text, Layer

import pytest

def layer_to_dict(layer: Layer):
    return [
        {'start': span.start,
         'end': span.end,
         'text': span.text,
         **dict(span.annotations[0])
        } for span in layer
    ]

def test_matching_without_separators():
    rules = Ruleset([
        StaticExtractionRule('first'),
        StaticExtractionRule('firs'),
        StaticExtractionRule('irst'),
        StaticExtractionRule('last')
    ])

    text = Text('first second last')
    tagger = SubstringTagger(rules)
    tagger(text)

    expected_output = [
        {'start': 0, 'end': 5, 'text': 'first'},
        {'start': 13, 'end': 17, 'text': 'last'}]

    assert layer_to_dict(text.terms) == expected_output, "Maximal matches must be returned"




    rules = Ruleset([
        StaticExtractionRule('First'),
        StaticExtractionRule('firs'),
        StaticExtractionRule('irst'),
        StaticExtractionRule('LAST')
    ])

    text = Text('first second last')
    tagger = SubstringTagger(rules, ignore_case=True)
    tagger(text)

    expected_output = [
        {'start': 0, 'end': 5, 'text': 'first'},
        {'start': 13, 'end': 17, 'text': 'last'}]

    assert layer_to_dict(text.terms) == expected_output, "Maximal matches must be returned"

def test_separator_effect():
    rules = Ruleset([StaticExtractionRule('match')])

    text = Text('match|match| match| match| match |match')
    separators = '|'
    tagger = SubstringTagger(rules, token_separators=separators)
    tagger(text)

    expected_output = [
        {'start': 0, 'end': 5, 'text': 'match'},
        {'start': 6, 'end': 11, 'text': 'match'},
        {'start': 34, 'end': 39, 'text': 'match'}]
    assert layer_to_dict(text.terms) == expected_output, "Separators are not correctly handled"

    rules = Ruleset([StaticExtractionRule('match')])
    text = Text('match match, :match, match')
    separators = ' , :'
    tagger = SubstringTagger(rules, token_separators=separators)
    tagger(text)

    expected_output = [
        {'start': 0, 'end': 5, 'text': 'match'},
        {'start': 6, 'end': 11, 'text': 'match'},
        {'start': 14, 'end': 19, 'text': 'match'},
        {'start': 21, 'end': 26, 'text': 'match'}]
    assert layer_to_dict(text.terms) == expected_output, "Multiple separators do not work"

def test_annotations():
    rules = Ruleset([
        StaticExtractionRule('first', {'a': 1, 'b': 1}),
        StaticExtractionRule('second', {'b': 2, 'a': 3}),
        StaticExtractionRule('last', {'a': 3, 'b': 5})])
    text = Text('first second last')
    tagger = SubstringTagger(rules, output_attributes=['a', 'b'])
    tagger(text)

    expected_outcome = [
        {'start': 0, 'end': 5, 'text': 'first', 'a': 1, 'b': 1},
        {'start': 6, 'end': 12, 'text': 'second', 'b': 2, 'a': 3},
        {'start': 13, 'end': 17, 'text': 'last', 'a': 3, 'b': 5}]
    assert layer_to_dict(text.terms) == expected_outcome, "Annotations do not work"

def test_global_decorator():
    rules = Ruleset([
        StaticExtractionRule('first'),
        StaticExtractionRule('second'),
        StaticExtractionRule('third'),
        StaticExtractionRule('fourth'),
        StaticExtractionRule('last')
    ])

    def decorator(text, span, annotation):
        if text.text[span.start:span.end] == 'first':
            return {'value': 1}
        elif text.text[span.start:span.end] == 'second':
            return {'value': 2}
        elif text.text[span.start:span.end] == 'third':
            return {'value': 3}
        elif text.text[span.start:span.end] == 'fourth':
            return {'value': 4}

        return None

    text = Text('first, second, third and last')
    tagger = SubstringTagger(rules, output_attributes=['value'], global_decorator=decorator)
    tagger(text)

    expected_outcome = [
        {'start': 0, 'end': 5, 'text': 'first', 'value': 1},
        {'start': 7, 'end': 13, 'text': 'second', 'value': 2},
        {'start': 15, 'end': 20, 'text': 'third', 'value': 3}]
    assert layer_to_dict(text.terms) == expected_outcome, "Global decorator does not work"

    def text_analyzer(text, span,annotation):
        layer = span.layer
        value = -1
        for prev in layer:
            if prev == span:
                break
            value = max(value, prev['value'])

        return {'value': value + 1}

    rules = Ruleset([
        StaticExtractionRule('first'),
        StaticExtractionRule('second'),
        StaticExtractionRule('third'),
        StaticExtractionRule('fourth'),
        DynamicExtractionRule('last', decorator=text_analyzer)
    ])

    text = Text('first, second, third and last')
    tagger = SubstringTagger(rules, output_attributes=['value'], global_decorator=decorator)
    tagger(text)

    expected_outcome = [
        {'start': 0, 'end': 5, 'text': 'first', 'value': 1},
        {'start': 7, 'end': 13, 'text': 'second', 'value': 2},
        {'start': 15, 'end': 20, 'text': 'third', 'value': 3}]
    assert layer_to_dict(text.terms) == expected_outcome, "Dynamic decorator does not work"


def test_minimal_and_maximal_matching():
    rules = Ruleset([
        StaticExtractionRule('abcd'),
        StaticExtractionRule('abc'),
        StaticExtractionRule('bc'),
        StaticExtractionRule('bcd'),
        StaticExtractionRule('bcde'),
        StaticExtractionRule('f'),
        StaticExtractionRule('ef')
    ])

    text = Text('abcdea--efg')
    tagger = SubstringTagger(rules, output_attributes=[], conflict_resolver='KEEP_MINIMAL')
    tagger(text)

    expected_outcome = [
        {'start': 1, 'end': 3, 'text': 'bc'},
        {'start': 9, 'end': 10, 'text': 'f'}]
    assert layer_to_dict(text.terms) == expected_outcome, "Minimal matching does not work"

    rules = Ruleset([
        StaticExtractionRule('abcd'),
        StaticExtractionRule('abc'),
        StaticExtractionRule('bc'),
        StaticExtractionRule('bcd'),
        StaticExtractionRule('bcde'),
        StaticExtractionRule('f'),
        StaticExtractionRule('ef')
    ])

    text = Text('abcdea--efg')
    tagger = SubstringTagger(rules, output_attributes=[], conflict_resolver='KEEP_MAXIMAL')
    tagger(text)

    expected_outcome = [
        {'start': 0, 'end': 4, 'text': 'abcd'},
        {'start': 1, 'end': 5, 'text': 'bcde'},
        {'start': 8, 'end': 10, 'text': 'ef'}]

    assert layer_to_dict(text.terms) == expected_outcome, "Maximal matching does not work"

    rules = Ruleset([
        StaticExtractionRule('abcd'),
        StaticExtractionRule('abc'),
        StaticExtractionRule('bc'),
        StaticExtractionRule('bcd'),
        StaticExtractionRule('bcde'),
        StaticExtractionRule('f'),
        StaticExtractionRule('ef')
    ])

    text = Text('abcdea--efg')
    tagger = SubstringTagger(rules, output_attributes=[], conflict_resolver='KEEP_ALL')
    tagger(text)

    expected_outcome = [
        {'start': 0, 'end': 3, 'text': 'abc'},
        {'start': 0, 'end': 4, 'text': 'abcd'},
        {'start': 1, 'end': 3, 'text': 'bc'},
        {'start': 1, 'end': 4, 'text': 'bcd'},
        {'start': 1, 'end': 5, 'text': 'bcde'},
        {'start': 8, 'end': 10, 'text': 'ef'},
        {'start': 9, 'end': 10, 'text': 'f'}]

    assert layer_to_dict(text.terms) == expected_outcome, "All matches does not work"