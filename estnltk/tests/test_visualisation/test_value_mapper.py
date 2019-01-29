from estnltk.tests.helpers.text_objects import new_text
from estnltk.visualisation.mappers.value_mapper import value_mapper_discrete
from estnltk.visualisation.mappers.value_mapper import value_mapper_ambigious
from estnltk.visualisation.core.prettyprinter import decompose_to_elementary_spans

def test_empty_mapper():
    segment = decompose_to_elementary_spans(new_text(5).layer_1, new_text(5).text)[0]
    result = empty_mapper(segment)
    expected = "default"
    assert result == expected

def test_conflicting_mapper():
    segment = decompose_to_elementary_spans(new_text(5).layer_1, new_text(5).text)[2]
    result = conflicting_mapper(segment)
    expected = "conflict_value"
    assert result == expected


def test_usual_mapper():
    segment = decompose_to_elementary_spans(new_text(5).layer_1, new_text(5).text)[0]
    result = my_best_color_mapper(segment)
    expected = "red"
    assert result == expected


def empty_mapper(segment):
    return value_mapper_discrete(segment, "start", {}, "default", "")

def conflicting_mapper(segment):
    return value_mapper_discrete(segment,"start",{},"default_value","conflict_value")

def my_best_color_mapper(segment):
    return value_mapper_ambigious(segment, "attr_1", {'SADA':"red"}, "blue", "green")