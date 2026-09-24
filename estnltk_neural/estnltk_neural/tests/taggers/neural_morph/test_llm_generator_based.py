#
#  Tests for the LLM generator based morphological correction components.
#
#  No test performs a real API call. The provider is replaced by a stub that
#  returns the response shape Azure OpenAI's strict JSON schema output
#  guarantees, so the generators and the retagger can be tested without
#  credentials. What remains unverified by this suite is the live provider
#  itself: that the deployment answers, that the real response parses, and how
#  the pacing and retry logic behaves against actual rate limits.
#
import json

import pytest

from estnltk import Text
from estnltk_neural.common import is_package_available

from estnltk_neural.taggers.neural_morph.llm_generator_based.llm_provider import (
    LLMBudgetExceededError,
    LLMProvider,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_filter import (
    LLMWordFilter,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_generator import (
    LLMWordReplacementGenerator,
    WordReplacementGenerator,
    mark_target_word,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.word_replacement_analyzer import (
    WordReplacementAnalyzer,
)
from estnltk_neural.taggers.neural_morph.llm_generator_based.llm_morph_corrections_retagger import (
    FLAG_AGREED,
    FLAG_CORRECTED,
    FLAG_DISAGREED,
    FLAG_NONE,
    LLMmorphCorrectionsRetagger,
)

# 'komisjoni' is form homonymous: genitive ('sg g'), partitive ('sg p') or the
# short illative / additive ('adt').
HOMONYM_SENTENCE = "Kaebus esitati komisjoni."

# Replacements that fit an illative slot. Most are long illatives ('sg ill'),
# which Vabamorf does not offer for 'komisjoni' -- the point being that 'adt'
# then wins among the forms it does offer.
ILLATIVE_CANDIDATES = [
    "ministeeriumisse", "kohtusse", "valitsusse", "nõukogusse", "parlamenti",
]
GENITIVE_CANDIDATES = ["nõukogu", "valitsuse", "parlamendi", "ministeeriumi", "kohtu"]


class _StubProvider(LLMProvider):
    """Returns a canned JSON object, recording what it was asked."""

    def __init__(self, payload, model_name="stub-model"):
        self._payload = payload
        self._model_name = model_name
        self.calls = []

    def complete_json(self, messages, schema, schema_name="response", max_tokens=512):
        self.calls.append(
            {"messages": messages, "schema": schema, "schema_name": schema_name}
        )
        return self._payload

    @property
    def model_name(self):
        return self._model_name


class _StubGenerator(WordReplacementGenerator):
    """A generator with fixed output, so the analyzer needs no provider at all."""

    def __init__(self, candidates):
        self.candidates = candidates

    def generate(self, sentence, loc):
        return [(word, None) for word in self.candidates]


# ===========================================================================
#   Prompt construction
# ===========================================================================


def test_mark_target_word_brackets_the_right_token():
    assert mark_target_word(["Ma", "näen", "maja", "."], 2) == "Ma näen <maja> ."


@pytest.mark.parametrize("loc", [-1, 4, 99])
def test_mark_target_word_rejects_out_of_range(loc):
    with pytest.raises(IndexError):
        mark_target_word(["Ma", "näen", "maja", "."], loc)


# ===========================================================================
#   Generator
# ===========================================================================


def test_generator_returns_candidates_with_no_scores():
    # A chat model gives no probabilities, so every score must be None rather
    # than an invented number.
    provider = _StubProvider({"candidates": ["üks", "kaks", "kolm"]})
    gen = LLMWordReplacementGenerator(provider=provider, n_candidates=3)

    result = gen.generate(["Ma", "näen", "maja", "."], 2)

    assert result == [("üks", None), ("kaks", None), ("kolm", None)]


def test_generator_schema_pins_the_candidate_count():
    provider = _StubProvider({"candidates": ["a"] * 10})
    gen = LLMWordReplacementGenerator(provider=provider, n_candidates=10)
    gen.generate(["Ma", "näen", "maja", "."], 2)

    schema = provider.calls[0]["schema"]
    assert schema["properties"]["candidates"]["minItems"] == 10
    assert schema["properties"]["candidates"]["maxItems"] == 10
    assert schema["additionalProperties"] is False


def test_generator_sends_the_marked_sentence_and_one_shot_example():
    provider = _StubProvider({"candidates": ["x"]})
    gen = LLMWordReplacementGenerator(provider=provider, n_candidates=1)
    gen.generate(["Kaebus", "esitati", "komisjoni", "."], 2)

    messages = provider.calls[0]["messages"]
    assert messages[0]["role"] == "system"
    # The one-shot example must be a user/assistant pair, with valid JSON in the
    # assistant turn, or it teaches the model the wrong output shape.
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    assert "candidates" in json.loads(messages[2]["content"])
    assert messages[-1]["content"] == "Sentence: Kaebus esitati <komisjoni> ."


@pytest.mark.parametrize("payload", [{}, {"candidates": "not a list"}, {"other": []}])
def test_generator_rejects_a_malformed_response(payload):
    # Strict schema output means this should not happen, so it must fail at the
    # boundary rather than surface as a puzzling morphological result later.
    gen = LLMWordReplacementGenerator(provider=_StubProvider(payload))
    with pytest.raises(ValueError, match="candidates"):
        gen.generate(["Ma", "näen", "maja", "."], 2)


# ===========================================================================
#   Filter
# ===========================================================================


def test_filter_keeps_only_offered_candidates_and_their_scores():
    # The prompt forbids inventing candidates; accepting an invented one would
    # turn a prompt violation into a wrong form distribution.
    provider = _StubProvider({"candidates": ["kohtusse", "väljamõeldis"]})
    f = LLMWordFilter(provider=provider, keep_n=5)

    result = f.filter(
        ["Kaebus", "esitati", "komisjoni", "."],
        2,
        [("kohtusse", 0.7), ("valitsusse", 0.2)],
    )

    assert result == [("kohtusse", 0.7)]


def test_filter_short_circuits_on_an_empty_candidate_list():
    provider = _StubProvider({"candidates": []})
    f = LLMWordFilter(provider=provider)
    assert f.filter(["Ma", "näen", "maja", "."], 2, []) == []
    assert provider.calls == []


# ===========================================================================
#   Analyzer -- uses real Vabamorf, which ships with estnltk
# ===========================================================================


def test_analyzer_returns_a_normalised_distribution():
    analyzer = WordReplacementAnalyzer(generator=_StubGenerator(GENITIVE_CANDIDATES))
    dist = analyzer.analyze(["Komisjoni", "liikmed", "arutasid", "eelnõu", "."], 0)

    assert dist, "expected a non-empty distribution"
    assert abs(sum(share for _, share in dist) - 1.0) < 1e-9
    # Sorted most likely first, and the genitive should lead for this context.
    assert dist == sorted(dist, key=lambda p: (-p[1], p[0]))
    assert dist[0][0] == "sg g"


def test_analyzer_returns_empty_when_nothing_is_generated():
    analyzer = WordReplacementAnalyzer(generator=_StubGenerator([]))
    assert analyzer.analyze(["Ma", "näen", "maja", "."], 2) == []


def test_analyzer_applies_the_filter_when_given_one():
    class _DropAll:
        def filter(self, sentence, loc, words):
            return []

    analyzer = WordReplacementAnalyzer(
        generator=_StubGenerator(GENITIVE_CANDIDATES), word_filter=_DropAll()
    )
    assert analyzer.analyze(["Komisjoni", "liikmed", "."], 0) == []


# ===========================================================================
#   Retagger
# ===========================================================================


def _retagger(candidates, select=None, **kwargs):
    return LLMmorphCorrectionsRetagger(
        analyzer=WordReplacementAnalyzer(generator=_StubGenerator(candidates)),
        select=select or (lambda span: span.text.lower() == "komisjoni"),
        **kwargs,
    )


def _flag_of(layer, word, attribute="llm_morph_correction"):
    for span in layer:
        if span.text == word:
            return {a[attribute] for a in span.annotations}
    return None


def _form_of(layer, word):
    for span in layer:
        if span.text == word:
            return [a["form"] for a in span.annotations]
    return None


def test_retagger_corrects_from_vabamorf_candidates():
    # Vabamorf disambiguates 'komisjoni' to 'sg g' here, which is wrong: the
    # complaint was submitted *to* the committee. The distribution puts most of
    # its weight on 'sg ill', which Vabamorf does not offer for this word, so
    # 'adt' wins among the forms it does -- the additive/illative split resolving
    # itself through the select-from-candidates constraint.
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    assert _form_of(text.morph_analysis, "komisjoni") == ["sg g"]

    _retagger(ILLATIVE_CANDIDATES).retag(text)

    assert _form_of(text.morph_analysis, "komisjoni") == ["adt"]
    assert _flag_of(text.morph_analysis, "komisjoni") == {FLAG_CORRECTED}
    meta = text.morph_analysis.meta["llm_morph_corrections_retagger"]
    assert meta["analysed_words"] == 1
    assert meta["corrected_words"] == 1


def test_correction_carries_a_full_vabamorf_annotation():
    # The prediction is a form only; the annotation written must still have the
    # lemma, root and ending a Vabamorf layer requires.
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    _retagger(ILLATIVE_CANDIDATES).retag(text)

    for span in text.morph_analysis:
        if span.text == "komisjoni":
            annotation = span.annotations[0]
            assert annotation["lemma"] == "komisjon"
            assert annotation["root"] == "komisjon"
            assert annotation["ending"] == "0"


def test_retagger_agrees_when_the_existing_form_is_most_likely():
    text = Text("Komisjoni liikmed arutasid eelnõu.").tag_layer(["morph_analysis"])
    before = _form_of(text.morph_analysis, "Komisjoni")

    _retagger(GENITIVE_CANDIDATES, select=lambda s: s.text == "Komisjoni").retag(text)

    assert _form_of(text.morph_analysis, "Komisjoni") == before
    assert _flag_of(text.morph_analysis, "Komisjoni") == {FLAG_AGREED}
    assert text.morph_analysis.meta["llm_morph_corrections_retagger"]["agreed_words"] == 1


def test_retagger_flags_disagreement_when_vabamorf_offers_no_such_form():
    # Candidates that are all plural: Vabamorf has no plural reading of
    # 'komisjoni', so nothing can be selected and the word must be left alone.
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    before = _form_of(text.morph_analysis, "komisjoni")

    _retagger(["majadelt", "kohtutelt", "valitsustelt"]).retag(text)

    assert _form_of(text.morph_analysis, "komisjoni") == before
    assert _flag_of(text.morph_analysis, "komisjoni") == {FLAG_DISAGREED}
    meta = text.morph_analysis.meta["llm_morph_corrections_retagger"]
    assert meta["disagreed_words"] == 1
    assert meta["corrected_words"] == 0
    assert meta["agreed_words"] == 0


def test_unselected_words_are_untouched_and_flagged_none():
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    before = _form_of(text.morph_analysis, "Kaebus")

    _retagger(ILLATIVE_CANDIDATES).retag(text)

    assert _form_of(text.morph_analysis, "Kaebus") == before
    assert _flag_of(text.morph_analysis, "Kaebus") == {FLAG_NONE}
    assert _flag_of(text.morph_analysis, "esitati") == {FLAG_NONE}


def test_select_predicate_controls_how_many_words_are_analysed():
    # Each selected word costs a model call, so a predicate that selects nothing
    # must cost nothing.
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    _retagger(ILLATIVE_CANDIDATES, select=lambda span: False).retag(text)

    meta = text.morph_analysis.meta["llm_morph_corrections_retagger"]
    assert meta["analysed_words"] == 0
    assert all(
        a["llm_morph_correction"] == FLAG_NONE
        for span in text.morph_analysis
        for a in span.annotations
    )


def test_flag_attribute_name_is_configurable():
    # This retagger is not specific to homonymy, so the attribute name should not
    # be baked in.
    text = Text(HOMONYM_SENTENCE).tag_layer(["morph_analysis"])
    _retagger(ILLATIVE_CANDIDATES, flag_attribute="my_flag").retag(text)

    assert "my_flag" in text.morph_analysis.attributes
    assert _flag_of(text.morph_analysis, "komisjoni", "my_flag") == {FLAG_CORRECTED}


def test_output_attributes_cover_the_produced_layer():
    r = _retagger(ILLATIVE_CANDIDATES)
    assert "llm_morph_correction" in r.output_attributes
    for attribute in ("lemma", "root", "ending", "form", "partofspeech"):
        assert attribute in r.output_attributes


def test_vm_instance_conflicts_with_slang_lex():
    from estnltk.vabamorf.morf import Vabamorf

    with pytest.raises(ValueError, match="slang_lex"):
        _retagger(ILLATIVE_CANDIDATES, slang_lex=True, vm_instance=Vabamorf.instance())


# ===========================================================================
#   Provider spend ceiling
# ===========================================================================


@pytest.mark.skipif(
    not is_package_available("openai"),
    reason="package openai is required for this test",
)
def test_budget_ceiling_raises_before_a_run_gets_expensive():
    from estnltk_neural.taggers.neural_morph.llm_generator_based.llm_provider import (
        AzureOpenAIProvider,
    )

    class _Usage:
        prompt_tokens = 1_000_000
        completion_tokens = 1_000_000

    provider = AzureOpenAIProvider.__new__(AzureOpenAIProvider)
    provider._model_name = "gpt-4o"
    provider._costs = AzureOpenAIProvider.DEFAULT_COSTS
    provider._spent_usd = 0.0
    provider._max_cost = 1.0

    class _Response:
        usage = _Usage()

    with pytest.raises(LLMBudgetExceededError):
        provider._record_cost(_Response())
