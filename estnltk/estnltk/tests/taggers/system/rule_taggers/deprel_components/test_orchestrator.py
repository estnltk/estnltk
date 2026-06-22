# DepTaggerOrchestrator class testing
import pytest
from importlib.util import find_spec

from estnltk import Text, get_resource_paths
from estnltk.taggers.system.rule_taggers.deprel_components.conditions import (
    EdgeConstraint,
    NodeConstraint,
    ValueCondition,
)
from estnltk.taggers.system.rule_taggers.deprel_components.serializer import (
    ChainMatchSerializer,
)
from estnltk.taggers.system.rule_taggers.deprel_components.matcher import (
    DepChainMatcher,
)
from estnltk.taggers.system.rule_taggers.deprel_components.orchestrator import (
    DepTaggerOrchestrator,
)
from estnltk.taggers.system.rule_taggers.deprel_components.patterns import (
    PathPattern,
    ChainMatch,
)
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
def sample_layers_and_spans():
    if not check_if_estnltk_neural_is_available():
        pytest.skip(
            "estnltk_neural is not installed. You'll need estnltk_neural for running this test."
        )
    if STANZA_SYNTAX_MODELS_PATH is None:
        pytest.skip(
            "StanzaSyntaxTagger's model is required by this test. Use estnltk.download('stanzasyntaxtagger') to fetch the missing resource."
        )

    sample_text = (
        "Ta andis lendurist abikaasale oma raamatu. See raamat on väga huvitav."
    )
    text_obj = Text(sample_text)
    text_obj.tag_layer("morph_extended")

    from estnltk_neural.taggers import StanzaSyntaxTagger

    stanza = StanzaSyntaxTagger(
        input_type="morph_analysis", input_morph_layer="morph_analysis"
    )
    stanza.tag(text_obj)

    layers = [sent.stanza_syntax for sent in text_obj.sentences]
    spans = [(sent.start, sent.end) for sent in text_obj.sentences]
    return layers, spans


def build_wildcard_pattern(name: str) -> PathPattern:
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


def test_constructor_sets_defaults():
    base_pattern = build_wildcard_pattern("base_p")
    orchestrator = DepTaggerOrchestrator(
        patterns=(base_pattern,),
        sentence_match_dedup_mode="role_based",
        max_matches_per_sentence=100,
        allow_role_node_overlap=False,
    )
    # Check: orchestrator builds a matcher and decorator with sensible defaults
    assert orchestrator.matcher is not None
    assert orchestrator.serializer is not None
    assert isinstance(orchestrator.matcher, DepChainMatcher)
    assert isinstance(orchestrator.serializer, ChainMatchSerializer)


def test_tag_sentence_layer_and_layers(sample_layers_and_spans):
    layers, spans = sample_layers_and_spans
    base_pattern = build_wildcard_pattern("base_p")
    orchestrator = DepTaggerOrchestrator(
        patterns=(base_pattern,),
        sentence_match_dedup_mode="role_based",
        max_matches_per_sentence=100,
    )

    matches = orchestrator.tag_sentence_layer(
        sentence_syntax_layer=layers[0], sentence_index=0, sentence_span=spans[0]
    )
    # Check: tag_sentence_layer returns a list of ChainMatch objects when present
    assert isinstance(matches, list)
    if matches:
        assert all(isinstance(m, ChainMatch) for m in matches)

    all_matches = orchestrator.tag_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    # Check: tag_sentence_layers returns an aggregate list
    assert isinstance(all_matches, list)


def test_decorate_and_full_pipeline(sample_layers_and_spans):
    layers, spans = sample_layers_and_spans
    base_pattern = build_wildcard_pattern("base_p")
    orchestrator = DepTaggerOrchestrator(
        patterns=(base_pattern,), sentence_match_dedup_mode="role_based"
    )

    matches = orchestrator.tag_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    # Check: decorator produces list of dicts for matched results
    if matches:
        decorated = orchestrator.serialize_matches(matches)
        assert isinstance(decorated, list)
        if decorated:
            assert isinstance(decorated[0], dict)

    decorated_all = orchestrator.tag_and_serialize_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    # Check: combined tag-and-decorate pipeline returns a list
    assert isinstance(decorated_all, list)


def test_global_dedup_and_capping(sample_layers_and_spans):
    layers, spans = sample_layers_and_spans
    base_pattern = build_wildcard_pattern("base_p")

    orch_none = DepTaggerOrchestrator(
        patterns=(base_pattern, base_pattern),
        global_dedup_mode="none",
        max_total_matches=1000000,
    )
    orch_role = DepTaggerOrchestrator(
        patterns=(base_pattern, base_pattern),
        global_dedup_mode="role_based",
        max_total_matches=1000000,
    )

    matches_none = orch_none.tag_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    matches_role = orch_role.tag_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    # Check: global role-based dedup reduces or equals match count
    assert len(matches_role) <= len(matches_none)

    orch_capped = DepTaggerOrchestrator(
        patterns=(base_pattern,), global_dedup_mode="none", max_total_matches=1
    )
    capped = orch_capped.tag_sentence_layers(
        sentence_syntax_layers=layers, sentence_spans=spans
    )
    # Check: max_total_matches caps the total number of matches
    assert len(capped) <= 1


def test_constructor_validation():
    base_pattern = build_wildcard_pattern("base_p")
    # Check: constructor enforces tuple type for patterns
    with pytest.raises(TypeError):
        DepTaggerOrchestrator(patterns=[base_pattern])
    # Check: invalid dedup modes raise ValueError
    with pytest.raises(ValueError):
        DepTaggerOrchestrator(
            patterns=(base_pattern,), sentence_match_dedup_mode="invalid"
        )
    with pytest.raises(ValueError):
        DepTaggerOrchestrator(patterns=(base_pattern,), global_dedup_mode="invalid")
    with pytest.raises(ValueError):
        DepTaggerOrchestrator(patterns=(base_pattern,), max_matches_per_sentence=0)
    with pytest.raises(ValueError):
        DepTaggerOrchestrator(patterns=(base_pattern,), max_total_matches=0)
    with pytest.raises(TypeError):
        DepTaggerOrchestrator(patterns=(base_pattern,), allow_role_node_overlap="no")


def test_span_alignment_validation(sample_layers_and_spans):
    layers, spans = sample_layers_and_spans
    base_pattern = build_wildcard_pattern("base_p")
    # Check: span alignment validation raises when lengths differ
    orch = DepTaggerOrchestrator(patterns=(base_pattern,))
    with pytest.raises(ValueError):
        orch.tag_sentence_layers(
            sentence_syntax_layers=layers, sentence_spans=[spans[0]]
        )
