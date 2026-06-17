# DepChildMatcher class testing
import pytest
from typing import Any, cast

from estnltk import Text
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.child_matcher import (
    DepChildMatcher,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import PathPattern
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
)


@pytest.fixture(scope="module")
def sample_graph():
    sample_text = "Ta andis lendurist abikaasale oma raamatu."
    text_obj = Text(sample_text)
    text_obj.tag_layer("morph_extended")
    try:
        from estnltk_neural.taggers import StanzaSyntaxTagger

        stanza = StanzaSyntaxTagger(
            input_type="morph_analysis", input_morph_layer="morph_analysis"
        )
        stanza.tag(text_obj)
    except Exception:
        pytest.skip("StanzaSyntaxTagger not available; skipping child matcher tests")

    sentence = text_obj.sentences[0]
    graph_index = SyntaxGraphIndex(
        sentence.stanza_syntax,
        sentence_id=0,
        sentence_span=(sentence.start, sentence.end),
    )
    return graph_index


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


def test_match_direct_child_basic(sample_graph):
    base_pattern = build_child_pattern("base_p")
    matcher = DepChildMatcher(patterns=(base_pattern,))
    matches = matcher.match_pattern_in_sentence(
        pattern=base_pattern, graph_index=sample_graph, sentence_index=0
    )
    # Check: at least one match is found
    assert len(matches) >= 1
    first = matches[0]
    # Check: the first match contains both 'parent' and 'child' roles
    assert "parent" in first.role_to_token_id and "child" in first.role_to_token_id


def test_match_sentence_aggregates(sample_graph):
    p1 = build_child_pattern("p1")
    p2 = build_child_pattern("p2")
    matcher = DepChildMatcher(patterns=(p1, p2), dedup_mode="none")
    results = matcher.match_sentence(graph_index=sample_graph, sentence_index=0)
    # Check: aggregated sentence matches are returned as a list
    assert isinstance(results, list)


def test_dedup_modes(sample_graph):
    p = build_child_pattern("p")
    m_none = DepChildMatcher(patterns=(p, p), dedup_mode="none")
    none_matches = m_none.match_sentence(graph_index=sample_graph, sentence_index=0)

    m_role = DepChildMatcher(patterns=(p, p), dedup_mode="role_based")
    role_matches = m_role.match_sentence(graph_index=sample_graph, sentence_index=0)
    # Check: role-based deduplication produces no more matches than no deduplication
    assert len(role_matches) <= len(none_matches)


def test_allow_role_node_overlap(sample_graph):
    # pattern allowing zero hops so same node can fill both roles
    same_node_pattern = PathPattern(
        name="self_ref",
        node_steps=(
            NodeConstraint(
                role="a",
                attribute_conditions={
                    "upostag": ValueCondition(ConditionMode.WILDCARD)
                },
            ),
            NodeConstraint(
                role="b",
                attribute_conditions={
                    "upostag": ValueCondition(ConditionMode.WILDCARD),
                    "deprel": ValueCondition(ConditionMode.WILDCARD),
                },
            ),
        ),
        edge_steps=(
            EdgeConstraint(
                direction=DirectionMode.DOWN,
                min_hops=1,
                max_hops=1,
            ),
        ),
        anchor_role="a",
        emit_roles=("a", "b"),
    )

    m_no = DepChildMatcher(patterns=(same_node_pattern,), allow_role_node_overlap=False)
    no_matches = m_no.match_sentence(graph_index=sample_graph, sentence_index=0)

    m_yes = DepChildMatcher(patterns=(same_node_pattern,), allow_role_node_overlap=True)
    yes_matches = m_yes.match_sentence(graph_index=sample_graph, sentence_index=0)

    # Check: allowing role/node overlap yields at least as many matches
    assert len(yes_matches) >= len(no_matches)


def test_constructor_validation():
    p = build_child_pattern("p")
    # Check: constructor validates argument types and values
    with pytest.raises(TypeError):
        DepChildMatcher(patterns=cast(Any, [p]))
    with pytest.raises(ValueError):
        DepChildMatcher(patterns=(p,), dedup_mode="invalid")
    with pytest.raises(ValueError):
        DepChildMatcher(patterns=(p,), max_matches_per_sentence=0)
    with pytest.raises(TypeError):
        DepChildMatcher(patterns=(p,), allow_role_node_overlap=cast(Any, "no"))
