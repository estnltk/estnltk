#
#  Tests for VabamorfMorphHomonymsRetagger -- correction of Estonian form
#  homonymy on a Vabamorf morph_analysis layer.
#
#  The retagger picks among Vabamorf's own candidate analyses rather than
#  writing the expert's prediction, so most of the logic can be tested by
#  handing _correct_layer an explicit candidate map. Those tests need no model
#  and no network.
#
import pytest

from estnltk import Text, Layer
from estnltk.downloader import get_resource_paths
from estnltk.vabamorf.morf import Vabamorf
from estnltk_neural.common import is_package_available

import estnltk_neural.taggers.neural_morph.bert_based.morph_homonyms_retagger as mhr_module
from estnltk_neural.taggers.neural_morph.bert_based.vabamorf_morph_homonyms_retagger import (
    FLAG_AGREED,
    FLAG_CORRECTED,
    FLAG_DISAGREED,
    FLAG_NONE,
    VabamorfMorphHomonymsRetagger,
)


# 'komisjoni' is form homonymous: genitive ('sg g'), partitive ('sg p') or the
# short illative / additive ('adt').
HOMONYM_SENTENCE = "Esitasin komisjoni aruande."

EXPERT_ATTRIBUTES = ["bert_tokens", "form", "partofspeech", "probability"]

# Resolve the homonymy expert model without downloading it: the end-to-end test
# is skipped when it is not available.
BERTMORPH_EXPERT_PATH = get_resource_paths(
    "bert_morph_expert", only_latest=True, download_missing=False
)


class _StubBertMorphTagger:
    """Stands in for BertMorphTagger so the retagger needs no model."""

    def __init__(self, **kwargs):
        self.input_layers = [
            kwargs.get("sentences_layer", "sentences"),
            kwargs.get("words_layer", "words"),
        ]


def _retagger_with_stub(monkeypatch, **kwargs):
    monkeypatch.setattr(mhr_module, "BertMorphTagger", _StubBertMorphTagger)
    return VabamorfMorphHomonymsRetagger(
        model_location="stub",  # skips the resource lookup
        homonym_words={"komisjoni"},  # skips reading the lexicon file
        **kwargs,
    )


def _expert_layer(text, word_text, form, partofspeech):
    """Build a one-word expert prediction layer."""
    layer = Layer(
        name="expert",
        attributes=EXPERT_ATTRIBUTES,
        text_object=text,
        parent="words",
        ambiguous=True,
    )
    for word in text.words:
        if word.text == word_text:
            layer.add_annotation(
                (word.start, word.end),
                bert_tokens=["▁" + word.text],
                form=form,
                partofspeech=partofspeech,
                probability=0.97,
            )
    return layer


def _tagged_text(sentence=HOMONYM_SENTENCE):
    """A text with a real, disambiguated Vabamorf morph_analysis layer."""
    return Text(sentence).tag_layer(["morph_analysis"])


def _annotations_of(layer, word_text):
    for span in layer:
        if span.text == word_text:
            return [(a["form"], a["partofspeech"]) for a in span.annotations]
    return None


def _flag_of(layer, word_text, flag_attribute="homonym_correction"):
    for span in layer:
        if span.text == word_text:
            return {a[flag_attribute] for a in span.annotations}
    return None


def _span_key(layer, word_text):
    for span in layer:
        if span.text == word_text:
            return (span.start, span.end)
    raise AssertionError(f"word {word_text!r} not in layer")


# ===========================================================================
#   Correction logic -- no model, explicit candidate map
# ===========================================================================


def test_expert_agreement_keeps_matching_analysis(monkeypatch):
    # If the expert confirms an analysis the word already has, only the matching
    # analyses are kept and the word is flagged 'agreed'.
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch)
    existing = _annotations_of(layer, "komisjoni")
    form, pos = existing[0]

    expert = _expert_layer(text, "komisjoni", form, pos)
    retagger._correct_layer(layer, {(s.start, s.end): s for s in expert}, {})

    assert _annotations_of(layer, "komisjoni") == [(form, pos)]
    assert _flag_of(layer, "komisjoni") == {FLAG_AGREED}
    meta = layer.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["inspected_words"] == 1
    assert meta["agreed_words"] == 1
    assert meta["corrected_words"] == 0
    assert meta["disagreed_words"] == 0


def test_correction_applied_from_vabamorf_candidates(monkeypatch):
    # If the expert disagrees but Vabamorf does offer the predicted form, the
    # matching candidate replaces the existing analysis -- and it is a complete
    # Vabamorf analysis, lemma/root/ending included.
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch)
    key = _span_key(layer, "komisjoni")

    expert = _expert_layer(text, "komisjoni", "adt", "S")
    candidates = {
        key: [
            {
                "normalized_text": "komisjoni",
                "lemma": "komisjon",
                "root": "komisjon",
                "root_tokens": ["komisjon"],
                "ending": "0",
                "clitic": "",
                "form": "adt",
                "partofspeech": "S",
            }
        ]
    }
    retagger._correct_layer(layer, {(s.start, s.end): s for s in expert}, candidates)

    assert _annotations_of(layer, "komisjoni") == [("adt", "S")]
    assert _flag_of(layer, "komisjoni") == {FLAG_CORRECTED}
    # The replacement carries real Vabamorf attributes, not a bare form/POS pair
    for span in layer:
        if span.text == "komisjoni":
            assert span.annotations[0]["lemma"] == "komisjon"
            assert span.annotations[0]["ending"] == "0"
    meta = layer.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["corrected_words"] == 1
    assert meta["agreed_words"] == 0


def test_expert_disagrees_but_vabamorf_has_no_such_form(monkeypatch):
    # The expert wants a form Vabamorf does not offer, so there is nothing valid
    # to switch to and the word must be left exactly as it was -- but flagged
    # 'disagreed' rather than 'agreed', because the expert did not agree: it
    # wanted a change the analyser could not express. These are the words worth
    # inspecting in a corpus.
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch)
    before = _annotations_of(layer, "komisjoni")
    key = _span_key(layer, "komisjoni")

    expert = _expert_layer(text, "komisjoni", "pl abl", "S")
    candidates = {key: [{"form": "sg g", "partofspeech": "S"}]}
    retagger._correct_layer(layer, {(s.start, s.end): s for s in expert}, candidates)

    # Annotations are untouched ...
    assert _annotations_of(layer, "komisjoni") == before
    # ... and the case is distinguishable from real agreement
    assert _flag_of(layer, "komisjoni") == {FLAG_DISAGREED}
    meta = layer.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["disagreed_words"] == 1
    assert meta["corrected_words"] == 0
    assert meta["agreed_words"] == 0


def test_non_homonyms_are_flagged_none_and_untouched(monkeypatch):
    # Words outside the lexicon must keep their analyses and be flagged 'none'.
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch)
    before = _annotations_of(layer, "aruande")

    expert = _expert_layer(text, "komisjoni", "adt", "S")
    retagger._correct_layer(layer, {(s.start, s.end): s for s in expert}, {})

    assert _annotations_of(layer, "aruande") == before
    assert _flag_of(layer, "aruande") == {FLAG_NONE}
    assert _flag_of(layer, "Esitasin") == {FLAG_NONE}


def test_flag_attribute_is_added_to_layer(monkeypatch):
    text = _tagged_text()
    layer = text.morph_analysis
    assert "homonym_correction" not in layer.attributes
    retagger = _retagger_with_stub(monkeypatch)
    retagger._correct_layer(layer, {}, {})
    assert "homonym_correction" in layer.attributes


def test_custom_flag_attribute_name(monkeypatch):
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch, flag_attribute="hom_flag")
    retagger._correct_layer(layer, {}, {})
    assert "hom_flag" in layer.attributes
    assert _flag_of(layer, "aruande", "hom_flag") == {FLAG_NONE}


# ===========================================================================
#   Dual mode: make_layer vs change_layer
# ===========================================================================


def test_make_layer_leaves_source_untouched(monkeypatch):
    # _make_layer must produce a corrected copy without modifying the input.
    text = _tagged_text()
    source = text.morph_analysis
    before = _annotations_of(source, "komisjoni")
    retagger = _retagger_with_stub(monkeypatch)

    new_layer = retagger._copy_morph_layer(source)
    assert _annotations_of(new_layer, "komisjoni") == before
    assert new_layer is not source

    # Correcting the copy leaves the original alone
    key = _span_key(new_layer, "komisjoni")
    expert = _expert_layer(text, "komisjoni", "adt", "S")
    candidates = {key: [{"form": "adt", "partofspeech": "S"}]}
    retagger._correct_layer(
        new_layer, {(s.start, s.end): s for s in expert}, candidates
    )

    assert _annotations_of(new_layer, "komisjoni") == [("adt", "S")]
    assert _annotations_of(source, "komisjoni") == before
    assert "homonym_correction" not in source.attributes


def test_copy_preserves_layer_structure(monkeypatch):
    text = _tagged_text()
    source = text.morph_analysis
    retagger = _retagger_with_stub(monkeypatch)
    copied = retagger._copy_morph_layer(source)

    assert copied.attributes == source.attributes
    assert copied.parent == source.parent
    assert copied.ambiguous == source.ambiguous
    assert len(copied) == len(source)


# ===========================================================================
#   Candidate regeneration -- needs Vabamorf only, which ships with estnltk
# ===========================================================================


def test_candidate_map_contains_all_homonym_readings(monkeypatch):
    # Regeneration must expose every reading Vabamorf considers possible,
    # including the ones disambiguation would have discarded.
    text = _tagged_text()
    retagger = _retagger_with_stub(monkeypatch)
    candidates = retagger._build_candidate_map(
        text, {"words": text.words, "sentences": text.sentences}, {}
    )
    key = _span_key(text.morph_analysis, "komisjoni")
    forms = {(c["form"], c["partofspeech"]) for c in candidates[key]}

    assert ("sg g", "S") in forms
    assert ("adt", "S") in forms
    # The disambiguated layer keeps only one of them; the candidate map keeps all
    assert len(forms) > len(set(_annotations_of(text.morph_analysis, "komisjoni")))


def test_slang_lexicon_instance_differs_from_standard(monkeypatch):
    # slang_lex must actually select Vabamorf's extended '_nosp' lexicon:
    # a silently-standard instance would make every later test pass for the
    # wrong reason.
    standard = VabamorfMorphHomonymsRetagger._make_vm_instance(slang_lex=False)
    slang = VabamorfMorphHomonymsRetagger._make_vm_instance(slang_lex=True)
    assert isinstance(slang, Vabamorf)

    def readings(instance, word):
        result = instance.analyze([word], disambiguate=False, guess=True)
        return {(a["form"], a["partofspeech"]) for a in result[0]["analysis"]}

    # 'mersu' is a spoken-language form: the two lexicons disagree about it
    assert readings(standard, "mersu") != readings(slang, "mersu")


def test_vm_instance_conflicts_with_slang_lex(monkeypatch):
    monkeypatch.setattr(mhr_module, "BertMorphTagger", _StubBertMorphTagger)
    with pytest.raises(ValueError, match="slang_lex"):
        VabamorfMorphHomonymsRetagger(
            model_location="stub",
            homonym_words={"komisjoni"},
            slang_lex=True,
            vm_instance=Vabamorf.instance(),
        )


# ===========================================================================
#   Dual mode end to end, with the expert stubbed out
# ===========================================================================


def _retagger_with_canned_expert(monkeypatch, form, partofspeech):
    """A retagger whose expert always predicts the given label for 'komisjoni'.

    The expert lookup is replaced on the class, not the instance: estnltk's
    Tagger forbids setting attributes on an initialised tagger.
    """

    def fake_predictions(self, text, layers, status):
        expert = _expert_layer(text, "komisjoni", form, partofspeech)
        return {(s.start, s.end): s for s in expert}

    monkeypatch.setattr(
        VabamorfMorphHomonymsRetagger, "_build_predicted_span_map", fake_predictions
    )
    return _retagger_with_stub(monkeypatch)


def test_change_layer_corrects_in_place(monkeypatch):
    # change_layer must modify the caller's layer object itself.
    text = _tagged_text()
    layer = text.morph_analysis
    retagger = _retagger_with_canned_expert(monkeypatch, "adt", "S")
    layers = {
        "words": text.words,
        "sentences": text.sentences,
        "morph_analysis": layer,
    }

    retagger._change_layer(text, layers, {})

    assert layers["morph_analysis"] is layer
    assert _annotations_of(layer, "komisjoni") == [("adt", "S")]
    assert _flag_of(layer, "komisjoni") == {FLAG_CORRECTED}
    # The correction came from Vabamorf, so it is a full analysis
    for span in layer:
        if span.text == "komisjoni":
            assert span.annotations[0]["lemma"] == "komisjon"


def test_make_layer_returns_new_layer_and_keeps_source(monkeypatch):
    # make_layer must return a corrected copy and leave the input layer alone.
    text = _tagged_text()
    source = text.morph_analysis
    before = _annotations_of(source, "komisjoni")
    retagger = _retagger_with_canned_expert(monkeypatch, "adt", "S")
    layers = {
        "words": text.words,
        "sentences": text.sentences,
        "morph_analysis": source,
    }

    new_layer = retagger._make_layer(text, layers, {})

    assert new_layer is not source
    assert new_layer.name == "morph_analysis"
    assert _annotations_of(new_layer, "komisjoni") == [("adt", "S")]
    assert _flag_of(new_layer, "komisjoni") == {FLAG_CORRECTED}
    # The source keeps its original analyses and gains no flag attribute
    assert _annotations_of(source, "komisjoni") == before
    assert "homonym_correction" not in source.attributes


def test_change_layer_agreement_path(monkeypatch):
    # When the expert confirms the existing analysis, nothing changes but the flag.
    text = _tagged_text()
    layer = text.morph_analysis
    form, pos = _annotations_of(layer, "komisjoni")[0]
    retagger = _retagger_with_canned_expert(monkeypatch, form, pos)
    layers = {
        "words": text.words,
        "sentences": text.sentences,
        "morph_analysis": layer,
    }

    retagger._change_layer(text, layers, {})

    assert _annotations_of(layer, "komisjoni") == [(form, pos)]
    assert _flag_of(layer, "komisjoni") == {FLAG_AGREED}
    meta = layer.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["agreed_words"] == 1
    assert meta["corrected_words"] == 0


# ===========================================================================
#   Public API -- the entry points callers actually use
# ===========================================================================


def test_public_retag_corrects_layer_in_place(monkeypatch):
    # retag() goes through estnltk's own machinery, including the output
    # consistency check that _change_layer alone does not exercise.
    text = _tagged_text()
    retagger = _retagger_with_canned_expert(monkeypatch, "adt", "S")

    retagger.retag(text)

    assert _annotations_of(text.morph_analysis, "komisjoni") == [("adt", "S")]
    assert _flag_of(text.morph_analysis, "komisjoni") == {FLAG_CORRECTED}


def test_public_make_layer_returns_corrected_copy(monkeypatch):
    # make_layer() validates the returned layer against output_attributes, so
    # this fails if the declared attributes do not match what is produced.
    text = _tagged_text()
    before = _annotations_of(text.morph_analysis, "komisjoni")
    retagger = _retagger_with_canned_expert(monkeypatch, "adt", "S")

    new_layer = retagger.make_layer(
        text,
        {
            "words": text.words,
            "sentences": text.sentences,
            "morph_analysis": text.morph_analysis,
        },
        {},
    )

    assert _annotations_of(new_layer, "komisjoni") == [("adt", "S")]
    assert _flag_of(new_layer, "komisjoni") == {FLAG_CORRECTED}
    # The source layer is left exactly as it was
    assert _annotations_of(text.morph_analysis, "komisjoni") == before


def test_output_attributes_describe_the_produced_layer(monkeypatch):
    # Guards the make_layer path: output_attributes must cover the Vabamorf
    # attributes as well as the flag, not the flag alone.
    retagger = _retagger_with_stub(monkeypatch)
    assert "homonym_correction" in retagger.output_attributes
    for attr in ("lemma", "root", "ending", "form", "partofspeech"):
        assert attr in retagger.output_attributes


def test_analyzer_is_wired_to_the_slang_lexicon(monkeypatch):
    # It is not enough that _make_vm_instance can build a slang instance: the
    # instance actually handed to VabamorfAnalyzer must be that one. A silent
    # fallback to Vabamorf.instance() would leave every other test passing.
    retagger = _retagger_with_stub(monkeypatch)

    def readings(instance, word):
        result = instance.analyze([word], disambiguate=False, guess=True)
        return {(a["form"], a["partofspeech"]) for a in result[0]["analysis"]}

    wired = readings(retagger._vabamorf_analyzer._vm_instance, "mersu")
    standard = readings(Vabamorf.instance(), "mersu")
    assert wired != standard


def test_correct_layer_requires_a_candidate_map(monkeypatch):
    # The candidate map is not optional: an empty one would silently route every
    # disagreement to the unresolved branch and correct nothing.
    text = _tagged_text()
    retagger = _retagger_with_stub(monkeypatch)
    with pytest.raises(TypeError):
        retagger._correct_layer(text.morph_analysis, {})


# ===========================================================================
#   End to end with the real expert model -- skipped if it is not downloaded
# ===========================================================================


@pytest.mark.skipif(
    not is_package_available("transformers"),
    reason="package tranformers is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_EXPERT_PATH is None,
    reason="VabamorfMorphHomonymsRetagger's expert model location not known. "
    "Use estnltk.download('bert_morph_expert') to get the missing resources.",
)
def test_end_to_end_corrects_komisjoni():
    # 'Kaebus esitati komisjoni.' -- the complaint was submitted *to* the
    # committee, so 'komisjoni' is the short illative ('adt'). Vabamorf's own
    # disambiguation picks the genitive ('sg g'); the expert should correct it,
    # and the correction must come from Vabamorf's candidates, complete with
    # lemma and ending.
    text = Text("Kaebus esitati komisjoni.").tag_layer(["morph_analysis"])
    assert _annotations_of(text.morph_analysis, "komisjoni") == [("sg g", "S")]

    VabamorfMorphHomonymsRetagger().retag(text)

    assert _annotations_of(text.morph_analysis, "komisjoni") == [("adt", "S")]
    assert _flag_of(text.morph_analysis, "komisjoni") == {FLAG_CORRECTED}
    assert _flag_of(text.morph_analysis, "Kaebus") == {FLAG_NONE}

    for span in text.morph_analysis:
        if span.text == "komisjoni":
            assert span.annotations[0]["lemma"] == "komisjon"
            assert span.annotations[0]["root"] == "komisjon"

    meta = text.morph_analysis.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["inspected_words"] == 1
    assert meta["corrected_words"] == 1
    assert meta["disagreed_words"] == 0


def test_public_retag_flags_disagreement(monkeypatch):
    # The 'disagreed' path through the public entry point: the expert predicts a
    # form Vabamorf never offers for this word, so the annotation must survive
    # untouched and be flagged as a disagreement rather than an agreement.
    text = _tagged_text()
    before = _annotations_of(text.morph_analysis, "komisjoni")
    retagger = _retagger_with_canned_expert(monkeypatch, "pl abl", "S")

    retagger.retag(text)

    assert _annotations_of(text.morph_analysis, "komisjoni") == before
    assert _flag_of(text.morph_analysis, "komisjoni") == {FLAG_DISAGREED}
    meta = text.morph_analysis.meta["vabamorf_morph_homonyms_retagger"]
    assert meta["disagreed_words"] == 1
    assert meta["agreed_words"] == 0
    assert meta["corrected_words"] == 0
