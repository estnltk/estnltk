# DepChainMatcher class testing
import pytest
from importlib.util import find_spec

from estnltk import Text, get_resource_paths
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.matcher import (
    DepChainMatcher,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import PathPattern
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
)


def check_if_estnltk_neural_is_available():
    return find_spec("estnltk_neural") is not None


# Try to get the resources path for stanzasyntaxtagger. If missing, tests will be skipped.
STANZA_SYNTAX_MODELS_PATH = get_resource_paths(
    "stanzasyntaxtagger", only_latest=True, download_missing=False
)


@pytest.fixture(scope="module")
def sample_graph():
    if not check_if_estnltk_neural_is_available():
        pytest.skip(
            "estnltk_neural is not installed. You'll need estnltk_neural for running this test."
        )
    if STANZA_SYNTAX_MODELS_PATH is None:
        pytest.skip(
            "StanzaSyntaxTagger's model is required by this test. Use estnltk.download('stanzasyntaxtagger') to fetch the missing resource."
        )

    sample_text = "Ta andis lendurist abikaasale oma raamatu."
    text_obj = Text(sample_text)
    text_obj.tag_layer("morph_extended")

    from estnltk_neural.taggers import StanzaSyntaxTagger

    stanza = StanzaSyntaxTagger(
        input_type="morph_analysis", input_morph_layer="morph_analysis"
    )
    stanza.tag(text_obj)

    sentence = text_obj.sentences[0]
    graph_index = SyntaxGraphIndex(
        sentence.stanza_syntax,
        sentence_id=0,
        sentence_span=(sentence.start, sentence.end),
    )
    return graph_index


def build_simple_pattern(name: str) -> PathPattern:
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
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=1,
    )
    return PathPattern(
        name=name,
        node_steps=(parent_node, child_node),
        edge_steps=(edge_constraint,),
        anchor_role="child",
        emit_roles=("parent", "child"),
    )


def test_match_pattern_in_sentence_basic(sample_graph):
    base_pattern = build_simple_pattern("base_p")
    matcher = DepChainMatcher(patterns=(base_pattern,))
    matches = matcher.match_pattern_in_sentence(
        pattern=base_pattern, graph_index=sample_graph, sentence_index=0
    )
    # Check: at least one match found and roles present in first match
    assert len(matches) >= 1
    first = matches[0]
    assert "parent" in first.role_to_token_id and "child" in first.role_to_token_id


def test_sentence_span_override(sample_graph):
    base_pattern = build_simple_pattern("base_p")
    matcher = DepChainMatcher(patterns=(base_pattern,))
    overridden = matcher.match_pattern_in_sentence(
        pattern=base_pattern,
        graph_index=sample_graph,
        sentence_index=0,
        sentence_span=(999, 1001),
    )
    # Check: override of sentence_span is preserved in returned matches
    assert len(overridden) >= 1
    assert overridden[0].sentence_span == (999, 1001)


def test_match_sentence_aggregates(sample_graph):
    p1 = build_simple_pattern("p1")
    p2 = build_simple_pattern("p2")
    matcher = DepChainMatcher(patterns=(p1, p2), dedup_mode="none")
    results = matcher.match_sentence(graph_index=sample_graph, sentence_index=0)
    # Check: match_sentence aggregates results from multiple patterns
    assert len(results) >= 1


def test_dedup_modes(sample_graph):
    p = build_simple_pattern("p")
    m_none = DepChainMatcher(patterns=(p, p), dedup_mode="none")
    none_matches = m_none.match_sentence(graph_index=sample_graph, sentence_index=0)

    m_role = DepChainMatcher(patterns=(p, p), dedup_mode="role_based")
    role_matches = m_role.match_sentence(graph_index=sample_graph, sentence_index=0)
    # Check: role-based dedup reduces or equals the number of matches
    assert len(role_matches) <= len(none_matches)


def test_allow_role_node_overlap(sample_graph):
    same_node_pattern = PathPattern(
        name="self_ref",
        node_steps=(
            NodeConstraint(
                role="a",
                attribute_conditions={
                    "upostag": ValueCondition(ConditionMode.WILDCARD),
                    "deprel": ValueCondition(ConditionMode.WILDCARD),
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
                direction=DirectionMode.UP,
                min_hops=1,
                max_hops=1,
            ),
        ),
        anchor_role="a",
        emit_roles=("a", "b"),
    )

    m_no = DepChainMatcher(patterns=(same_node_pattern,), allow_role_node_overlap=False)
    no_matches = m_no.match_sentence(graph_index=sample_graph, sentence_index=0)

    m_yes = DepChainMatcher(patterns=(same_node_pattern,), allow_role_node_overlap=True)
    yes_matches = m_yes.match_sentence(graph_index=sample_graph, sentence_index=0)

    # Check: allowing role/node overlap yields at least as many matches
    assert len(yes_matches) >= len(no_matches)


def test_constructor_validation():
    p = build_simple_pattern("p")
    # Check: constructor parameter validation
    with pytest.raises(TypeError):
        DepChainMatcher(patterns=[p])
    with pytest.raises(ValueError):
        DepChainMatcher(patterns=(p,), dedup_mode="invalid")
    with pytest.raises(ValueError):
        DepChainMatcher(patterns=(p,), max_matches_per_sentence=0)
    with pytest.raises(TypeError):
        DepChainMatcher(patterns=(p,), allow_role_node_overlap="no")
