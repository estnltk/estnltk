import pytest
from importlib.util import find_spec

from estnltk import Text, get_resource_paths
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    NodeConstraint,
    ValueCondition,
    EdgeConstraint,
)
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    ChainMatch,
    MatchCollector,
    PathPattern,
)
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
    EdgeContext,
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

    stanza_syntax_tagger = StanzaSyntaxTagger(
        input_type="morph_analysis", input_morph_layer="morph_analysis"
    )
    stanza_syntax_tagger.tag(text_obj)

    sentence = text_obj.sentences[0]
    graph = SyntaxGraphIndex(
        sentence.stanza_syntax,
        sentence_id=0,
        sentence_span=(sentence.start, sentence.end),
    )
    return graph


@pytest.fixture
def nodes(sample_graph):
    return {
        3: sample_graph.get_node(3),
        4: sample_graph.get_node(4),
        5: sample_graph.get_node(5),
        6: sample_graph.get_node(6),
    }


def make_edge_context(direction: DirectionMode, hops: int) -> EdgeContext:
    return EdgeContext(
        direction=direction,
        hops=hops,
    )


@pytest.fixture
def simple_pattern():
    src = NodeConstraint(
        role="source",
        attribute_conditions={"upostag": ValueCondition(ConditionMode.EXACT, "NOUN")},
    )
    tgt = NodeConstraint(
        role="target",
        attribute_conditions={
            "upostag": ValueCondition(ConditionMode.EXACT, "ADJ"),
            "deprel": ValueCondition(ConditionMode.EXACT, "amod"),
        },
    )
    e = EdgeConstraint(
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=1,
    )
    return PathPattern(
        name="noun_to_adj",
        node_steps=(src, tgt),
        edge_steps=(e,),
        anchor_role="source",
        emit_roles=("source", "target"),
    )


def test_pathpattern_basic_api(simple_pattern):
    pattern = simple_pattern
    # Check: basic PathPattern API (name, node/edge accessors, describe)
    assert pattern.name == "noun_to_adj"
    assert pattern.get_node_constraint("source") is not None
    assert pattern.get_node_constraint("missing") is None
    assert pattern.get_edge_constraint("source", "target") is not None
    desc = pattern.describe()
    assert "Pattern name: noun_to_adj" in desc


def test_pathpattern_default_emit_roles():
    src = NodeConstraint(role="source")
    tgt = NodeConstraint(role="target")
    e = EdgeConstraint(direction=DirectionMode.UP)

    pattern = PathPattern(
        name="default_emit_roles",
        node_steps=(src, tgt),
        edge_steps=(e,),
        anchor_role="source",
    )

    # Check: default emit_roles fallback when not provided
    assert pattern.emit_roles == ("source", "target")


def test_pathpattern_validation_errors():
    src = NodeConstraint(role="source")
    tgt = NodeConstraint(role="target")
    e = EdgeConstraint(direction=DirectionMode.UP)
    # Check: invalid path/edge lengths and duplicate roles raise
    with pytest.raises(ValueError):
        PathPattern(
            name="bad_length",
            node_steps=(src, tgt),
            edge_steps=(),
            anchor_role="source",
            emit_roles=("source",),
        )
    duplicate = NodeConstraint(role="source")
    with pytest.raises(ValueError):
        PathPattern(
            name="duplicate_roles",
            node_steps=(duplicate, duplicate),
            edge_steps=(e,),
            anchor_role="source",
            emit_roles=("source",),
        )


def test_chainmatch_and_to_output(nodes):
    node_3 = nodes[3]
    node_4 = nodes[4]
    edge_ctx = make_edge_context(DirectionMode.UP, 1)

    match = ChainMatch(
        pattern_name="p",
        sentence_index=0,
        sentence_span=(0, 10),
        role_to_token_id={"source": 3, "target": 4},
        role_to_node={"source": node_3, "target": node_4},
        traversed_edges=(("source", "target", edge_ctx),),
        matched_text=f"{node_3.text} {node_4.text}",
        metadata={"c": 1},
    )

    # Check: ChainMatch accessors, roles and output row generation
    assert match.get_node("source").text == node_3.text
    assert match.get_token_id("target") == 4
    assert match.get_roles() == {"source", "target"}
    row = match.to_output_row()
    assert row["pattern_name"] == "p"
    assert row["role_to_token_id"]["source"] == 3


def make_chain_match_for_collector(
    pattern_name: str,
    sentence_span: tuple[int, int],
    source_id: int,
    target_id: int,
    source_node,
    target_node,
    text: str,
    metadata: dict | None = None,
) -> ChainMatch:
    edge_ctx = make_edge_context(DirectionMode.UP, 1)
    return ChainMatch(
        pattern_name=pattern_name,
        sentence_index=0,
        sentence_span=sentence_span,
        role_to_token_id={"source": source_id, "target": target_id},
        role_to_node={"source": source_node, "target": target_node},
        traversed_edges=(("source", "target", edge_ctx),),
        matched_text=text,
        metadata={} if metadata is None else metadata,
    )


def test_matchcollector_behaviour(nodes, sample_graph):
    node_3 = nodes[3]
    node_4 = nodes[4]
    node_5 = nodes[5]
    node_6 = nodes[6]
    span = sample_graph.sentence_span

    m1 = make_chain_match_for_collector(
        "p1", span, 3, 4, node_3, node_4, f"{node_3.text} {node_4.text}", {"m": 1}
    )
    m1_var = make_chain_match_for_collector(
        "p1", span, 3, 4, node_3, node_4, "other", {"m": 2}
    )
    m2 = make_chain_match_for_collector(
        "p2", span, 5, 6, node_5, node_6, f"{node_5.text} {node_6.text}"
    )

    # Check: 'none' dedup allows identical matches and counts accurately
    c_none = MatchCollector(dedup_mode="none", max_matches=10)
    assert c_none.add(m1)
    assert c_none.add(m1)
    assert c_none.count() == 2

    # Check: 'exact' dedup rejects identical matches
    c_exact = MatchCollector(dedup_mode="exact", max_matches=10)
    assert c_exact.add(m1)
    assert not c_exact.add(m1)
    assert c_exact.count() == 1

    # Check: 'role_based' dedup treats same role mapping as duplicate
    c_role = MatchCollector(dedup_mode="role_based", max_matches=10)
    assert c_role.add(m1)
    assert not c_role.add(m1_var)
    assert c_role.add(m2)
    assert c_role.count() == 2

    # Check: extend returns number of actually added matches respecting dedup
    c_ext = MatchCollector(dedup_mode="role_based", max_matches=10)
    added = c_ext.extend([m1, m1_var, m2])
    assert added == 2

    # Check: max_matches enforces capacity cap
    c_cap = MatchCollector(dedup_mode="none", max_matches=1)
    assert c_cap.add(m1)
    assert not c_cap.add(m2)

    # Check: summary reports totals and per-pattern counts
    summary = c_role.summary()
    assert summary["total"] == 2
    assert summary["pattern::p1"] == 1
    assert summary["pattern::p2"] == 1

    # Check: to_output_rows converts stored matches to list-of-rows
    rows = c_role.to_output_rows()
    assert len(rows) == 2

    # Check: clear empties the collector
    c_role.clear()
    assert c_role.count() == 0

    # Check: invalid constructor args raise appropriate exceptions
    with pytest.raises(ValueError):
        MatchCollector(dedup_mode="invalid")
    with pytest.raises(ValueError):
        MatchCollector(dedup_mode="none", max_matches=0)
    with pytest.raises(TypeError):
        MatchCollector(matches="not-a-list")  # type: ignore[arg-type]
