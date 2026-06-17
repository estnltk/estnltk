# DepChildTagger class testing
from typing import Any, cast
from types import SimpleNamespace

import pytest

from estnltk import Text
from estnltk.taggers.system.rule_taggers.deprel_components.child_matcher import (
    DepChildMatcher,
)
from estnltk.taggers.system.rule_taggers.taggers.dep_child_tagger import DepChildTagger
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import PathPattern
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
)


def dummy_decorator(text, base_span, annotation):
    if annotation["pattern_name"] == "drop_me":
        return None
    annotation["decorated"] = True
    annotation["base_roles"] = tuple(sorted(base_span))
    annotation["text_length"] = len(text.text)
    annotation["updated"] = True
    return annotation


def build_child_pattern(name: str) -> PathPattern:
    parent_node = NodeConstraint(
        role="parent",
        attribute_conditions={"upostag": ValueCondition(ConditionMode.WILDCARD)},
    )
    child_node = NodeConstraint(
        role="child",
        attribute_conditions={
            "upostag": ValueCondition(ConditionMode.WILDCARD),
            "deprel": ValueCondition(ConditionMode.WILDCARD),
        },
    )
    edge_constraint = EdgeConstraint(
        direction=DirectionMode.DOWN,
        min_hops=1,
        max_hops=1,
    )
    return PathPattern(
        name=name,
        node_steps=(parent_node, child_node),
        edge_steps=(edge_constraint,),
        anchor_role="parent",
        emit_roles=("parent", "child"),
    )


def test_constructor_wires_child_matcher():
    pattern = build_child_pattern("base_p")
    tagger = DepChildTagger(patterns=(pattern,))

    # Check: DepChildTagger builds and wires an internal DepChildMatcher
    assert tagger._depchild_tagger is not None
    # Check: the internal wrapper exposes a matcher instance
    assert tagger._depchild_tagger.matcher is not None
    # Check: the matcher is an instance of DepChildMatcher
    assert isinstance(tagger._depchild_tagger.matcher, DepChildMatcher)


def test_constructor_validation():
    pattern = build_child_pattern("base_p")

    # Check: constructor enforces tuple type for patterns
    with pytest.raises(TypeError):
        DepChildTagger(patterns=cast(Any, [pattern]))

    # Check: duplicate patterns are rejected
    with pytest.raises(ValueError):
        DepChildTagger(patterns=(pattern, pattern))


def test_constructor_accepts_custom_input_layer_names():
    pattern = build_child_pattern("base_p")

    tagger = DepChildTagger(
        patterns=(pattern,),
        syntax_layer="v172_stanza_syntax",
        sentences_layer="sentences",
    )

    assert tagger.syntax_layer == "v172_stanza_syntax"
    assert tagger.sentences_layer == "sentences"
    assert tagger.input_layers == ("v172_stanza_syntax", "sentences")


def test_annotation_decorator_can_filter_and_update_payload():
    text = Text("Ta andis raamatu.")

    def decorator(text_obj, base_span, annotation):
        if annotation["pattern_name"] == "drop_me":
            return None
        annotation["decorated"] = True
        annotation["base_roles"] = tuple(sorted(base_span))
        annotation["text_length"] = len(text_obj.text)
        return annotation

    annotation_decorator = dummy_decorator

    kept = annotation_decorator(
        text=text,
        base_span={"parent": object(), "child": object()},
        annotation={"pattern_name": "keep_me"},
    )
    assert kept is not None
    assert kept["decorated"] is True
    assert kept["base_roles"] == ("child", "parent")
    assert kept["text_length"] == len(text.text)

    dropped = annotation_decorator(
        text=text,
        base_span={"parent": object()},
        annotation={"pattern_name": "drop_me"},
    )
    assert dropped is None


def test_add_match_to_layer_uses_annotation_decorator():
    pattern = build_child_pattern("base_p")

    class DummyNode:
        def __init__(self, start, end, text):
            self.start = start
            self.end = end
            self.text = text

    class DummyLayer:
        def __init__(self, text_object):
            self.text_object = text_object
            self.rows = []

        def add_annotation(self, payload):
            self.rows.append(payload)

    tagger = DepChildTagger(
        patterns=(pattern,),
        annotation_decorator=dummy_decorator,
    )

    layer = DummyLayer(text_object=Text("Ta andis raamatu."))
    keep_match = SimpleNamespace(
        pattern_name="base_p",
        role_to_node={
            "parent": DummyNode(0, 2, "Ta"),
            "child": DummyNode(3, 8, "andis"),
        },
    )
    tagger._add_match_to_layer(layer, keep_match)

    assert len(layer.rows) == 1
    assert layer.rows[0]["updated"] is True

    drop_match = SimpleNamespace(
        pattern_name="drop_me",
        role_to_node={
            "parent": DummyNode(0, 2, "Ta"),
            "child": DummyNode(3, 8, "andis"),
        },
    )
    tagger._pattern_by_name["drop_me"] = pattern
    tagger._add_match_to_layer(layer, drop_match)

    assert len(layer.rows) == 1
