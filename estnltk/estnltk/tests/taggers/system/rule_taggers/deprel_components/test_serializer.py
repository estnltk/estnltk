import pytest

from estnltk import Text
from estnltk.taggers.system.rule_taggers.deprel_components.graph import SyntaxGraphIndex
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    ChainMatch,
    MatchCollector,
)
from estnltk.taggers.system.rule_taggers.deprel_components.serializer import (
    ChainMatchSerializer,
)
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    DirectionMode,
    EdgeContext,
)


@pytest.fixture
def sample_nodes():
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
        pytest.skip("StanzaSyntaxTagger not available; skipping decorator tests")

    sentence = text_obj.sentences[0]
    graph = SyntaxGraphIndex(
        sentence.stanza_syntax,
        sentence_id=0,
        sentence_span=(sentence.start, sentence.end),
    )
    return graph.get_node(3), graph.get_node(4)


def make_match(source_node, target_node, pattern_name="p") -> ChainMatch:
    edge_ctx = EdgeContext(
        direction=DirectionMode.UP,
        hops=1,
    )
    return ChainMatch(
        pattern_name=pattern_name,
        sentence_index=0,
        sentence_span=(0, 10),
        role_to_token_id={"source": source_node.id, "target": target_node.id},
        role_to_node={"source": source_node, "target": target_node},
        traversed_edges=(("source", "target", edge_ctx),),
        matched_text=f"{source_node.text} {target_node.text}",
        metadata={"k": "v"},
    )


def test_decorate_single_match_fields(sample_nodes):
    src, tgt = sample_nodes
    match = make_match(src, tgt, pattern_name="testpat")

    dec = ChainMatchSerializer()
    row = dec.serialize_match(match)

    # Check: decorated row contains expected pattern metadata and role fields
    assert row["pattern_name"] == "testpat"
    assert row["sentence_index"] == 0
    assert row["matched_text"] == "lendurist abikaasale"
    # Check: token ids and text mapping for roles
    assert row["role_to_token_id"]["source"] == 3
    assert row["role_to_text"]["target"] == "abikaasale"
    # Check: span mapping and traversed edges structure
    assert row["role_to_span"]["source"] == (9, 18)
    assert isinstance(row["traversed_edges"], list)
    assert row["metadata"]["k"] == "v"


def test_decorate_matches_and_collector(sample_nodes):
    src, tgt = sample_nodes
    m1 = make_match(src, tgt, pattern_name="p1")
    m2 = make_match(src, tgt, pattern_name="p2")

    dec = ChainMatchSerializer(output_field_prefix="x_")
    rows = dec.serialize_matches([m1, m2])
    # Check: multiple matches decorated and prefixed output field present
    assert len(rows) == 2
    assert "x_pattern_name" in rows[0]

    # Check: decorator can consume a MatchCollector and produce rows
    coll = MatchCollector(dedup_mode="none", max_matches=10)
    coll.add(m1)
    coll.add(m2)
    rows2 = dec.serialize_collector(coll)
    assert len(rows2) == 2


def test_output_text_roles_and_flags(sample_nodes):
    src, tgt = sample_nodes
    match = make_match(src, tgt, pattern_name="p")

    dec = ChainMatchSerializer(
        include_pattern_name=False,
        include_role_spans=False,
        output_text_roles=("target",),
    )
    row = dec.serialize_match(match)
    # Check: flags control which fields appear and matched_text can be limited
    assert "pattern_name" not in row
    assert "role_to_span" not in row
    assert row["matched_text"] == tgt.text
