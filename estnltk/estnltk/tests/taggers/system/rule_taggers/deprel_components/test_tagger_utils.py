from estnltk import Text
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.taggers.dep_child_tagger import DepChildTagger
from estnltk.taggers.system.rule_taggers.taggers.dep_chain_tagger import DepChainTagger
from estnltk.taggers.system.rule_taggers.deprel_components.tagger_utils import (
    build_match_annotation_payload,
    collect_output_attribute_names,
    collect_role_span_names,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    ChainMatch,
    PathPattern,
)
from estnltk.taggers.system.rule_taggers.deprel_components.types import (
    ConditionMode,
    DirectionMode,
    EdgeContext,
)


def build_pattern() -> PathPattern:
    """Build a tiny pattern with one node condition and one edge condition."""
    anchor = NodeConstraint(
        role="anchor",
        attribute_conditions={"text": ValueCondition(ConditionMode.EXACT, "suvel")},
    )
    child = NodeConstraint(
        role="s",
        attribute_conditions={"deprel": ValueCondition(ConditionMode.EXACT, "nmod")},
    )
    edge = EdgeConstraint(
        direction=DirectionMode.UP,
        min_hops=1,
        max_hops=1,
    )
    return PathPattern(
        name="season",
        node_steps=(anchor, child),
        edge_steps=(edge,),
        anchor_role="anchor",
        emit_roles=("anchor", "s"),
    )


def test_collect_schema_fields() -> None:
    """The schema should expose role spans first and flattened metadata fields after."""
    pattern = build_pattern()
    # Check: role span names are collected in first-seen order
    assert collect_role_span_names((pattern,)) == (("anchor", "s"), ())
    # Check: opt-in constraint fields expand the schema with flattened metadata
    assert collect_output_attribute_names(
        (pattern,), include_pattern_constraints=True
    ) == (("pattern_name", "matched_text", "anchor_text", "s_deprel"), ())


def test_build_match_annotation_payload() -> None:
    """A match should become one relation row with role spans and flattened metadata."""
    pattern = build_pattern()
    text_obj = Text("1990. aasta kuumal suvel")
    text_obj.tag_layer("words")
    child = text_obj.words[1]
    anchor = text_obj.words[3]
    match = ChainMatch(
        pattern_name="season",
        sentence_index=0,
        sentence_span=(0, len(text_obj.text)),
        role_to_token_id={"anchor": 3, "s": 1},
        role_to_node={"anchor": anchor, "s": child},
        traversed_edges=(
            (
                "anchor",
                "s",
                EdgeContext(
                    direction=DirectionMode.UP,
                    hops=1,
                ),
            ),
        ),
        matched_text="suvel aasta",
        metadata={},
    )

    payload = build_match_annotation_payload(
        match=match,
        patterns_by_name={pattern.name: pattern},
        span_names=("anchor", "s"),
        include_pattern_constraints=True,
    )
    # Check: the payload contains the expected role spans and flattened metadata fields
    assert payload["anchor"] == (19, 24)
    assert payload["s"] == (6, 11)
    assert payload["pattern_name"] == "season"
    assert payload["matched_text"] == "suvel aasta"
    assert payload["anchor_text"]["value"] == "suvel"
    assert payload["s_deprel"]["value"] == "nmod"


def test_tagger_constructors_use_schema_helpers() -> None:
    """Both taggers should expose the same row-per-match output schema."""
    chain_pattern = build_pattern()
    child_pattern = PathPattern(
        name="child_season",
        node_steps=chain_pattern.node_steps,
        edge_steps=(
            EdgeConstraint(
                direction=DirectionMode.DOWN,
                min_hops=1,
                max_hops=1,
            ),
        ),
        anchor_role="anchor",
        emit_roles=("anchor", "s"),
    )

    chain_tagger = DepChainTagger(patterns=(chain_pattern,))
    child_tagger = DepChildTagger(patterns=(child_pattern,))
    # Check: both taggers use the same helpers to collect output schema fields
    assert chain_tagger.output_span_names == (("anchor", "s"))
    assert (
        chain_tagger._user_defined_span_names == ()
    )  # no user-defined spans in this test
    assert child_tagger.output_span_names == (("anchor", "s"))
    assert (
        child_tagger._user_defined_span_names == ()
    )  # no user-defined spans in this test
    assert chain_tagger.output_attributes[:2] == ("pattern_name", "matched_text")
    assert child_tagger.output_attributes[:2] == ("pattern_name", "matched_text")
