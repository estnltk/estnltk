#
#  Tests for MorphHomonymsRetagger -- Bert-based correction of Estonian form
#  homonymy (e.g. 'komisjoni' as genitive 'sg g' vs short illative 'adt').
#
#  The tests are grouped by what they need:
#   * tests that replace the Bert expert with a stub and therefore need no model.
#     These cover the homonym lexicon gate, the annotation correction logic and
#     the single pass over the source layer;
#   * tests of the post_disambiguator wiring, which need the baseline model (they
#     create a Bert layer) but use a stub retagger, so that they do not depend on
#     what the expert model predicts;
#   * end-to-end tests with both real models, asserting exact labels. These are
#     skipped if the models are not downloaded.
#
from importlib.util import find_spec
import pytest

from estnltk import Text, Layer, Retagger
from estnltk.downloader import get_resource_paths

from estnltk.converters import layer_to_records

from estnltk_neural.taggers.neural_morph.bert_based.morph_homonyms_retagger import (
    DEFAULT_HOMONYM_LIST_PATH,
    _load_homonym_words,
)
import estnltk_neural.taggers.neural_morph.bert_based.morph_homonyms_retagger as mhr_module


def check_if_transformers_is_available():
    return find_spec("transformers") is not None


def check_if_pytorch_is_available():
    return find_spec("torch") is not None


# Try to get the resources paths for the baseline and the homonymy expert models.
# If missing, do nothing.
BERTMORPH_V2_PATH = get_resource_paths(
    "bert_morph_v2", only_latest=True, download_missing=False
)
BERTMORPH_EXPERT_PATH = get_resource_paths(
    "bert_morph_expert", only_latest=True, download_missing=False
)

MORPH_ATTRIBUTES = ["bert_tokens", "form", "partofspeech", "probability"]

# A homonymous word form from the packaged lexicon: 'komisjoni' can be either
# genitive ('sg g') or the short form illative / additive ('adt').
HOMONYM_SENTENCE = "Esitasin komisjoni aruande."


# ===========================================================================
#   Tests that do not require any model
# ===========================================================================


def test_homonym_lexicon_is_packaged():
    # Tests DEFAULT_HOMONYM_LIST_PATH and _load_homonym_words: the homonymous
    # word forms lexicon must ship inside the package and be locatable via
    # neural_abs_path, regardless of where the package was installed
    assert DEFAULT_HOMONYM_LIST_PATH.exists(), (
        f"Homonymous word forms lexicon not found at {DEFAULT_HOMONYM_LIST_PATH!s}"
    )
    words = _load_homonym_words(DEFAULT_HOMONYM_LIST_PATH, ignore_case=True)
    # Sanity checks on the loaded lexicon (currently 1296 lowercased entries)
    assert len(words) >= 1000
    assert "komisjoni" in words
    # With ignore_case=True all entries must be lowercased
    assert all(word == word.lower() for word in words)
    # Case-sensitive loading keeps the original spellings, so it yields more entries
    words_cased = _load_homonym_words(DEFAULT_HOMONYM_LIST_PATH, ignore_case=False)
    assert len(words_cased) >= len(words)


class _StubBertMorphTagger:
    """Stands in for BertMorphTagger so the retagger's logic can be tested
    without downloading any model."""

    def __init__(self, **kwargs):
        self.input_layers = [
            kwargs.get("sentences_layer", "sentences"),
            kwargs.get("words_layer", "words"),
        ]


def _make_layer(text, name, per_word):
    """Build an ambiguous word-based layer; per_word maps word text -> list of dicts."""
    layer = Layer(
        name=name,
        attributes=MORPH_ATTRIBUTES,
        text_object=text,
        parent="words",
        ambiguous=True,
    )
    for word in text.words:
        for annotation in per_word(word.text):
            layer.add_annotation((word.start, word.end), **annotation)
    return layer


def _annotations_of(layer, word_text):
    for span in layer:
        if span.text == word_text:
            return [(a["form"], a["partofspeech"]) for a in span.annotations]
    return None


def _retagger_with_stub(monkeypatch, **kwargs):
    monkeypatch.setattr(mhr_module, "BertMorphTagger", _StubBertMorphTagger)
    return mhr_module.MorphHomonymsRetagger(
        model_location="stub",  # skips the resource lookup
        homonym_words={"komisjoni"},  # skips reading the lexicon file
        **kwargs,
    )


def test_expert_correction_replaces_disagreeing_annotation(monkeypatch):
    # Tests MorphHomonymsRetagger._correct_layer and _build_expert_annotation
    # (the override branch): if the expert disagrees with every existing analysis
    # of a homonymous word, the expert's own prediction replaces them
    text = Text(HOMONYM_SENTENCE).tag_layer(["words", "sentences"])
    source = _make_layer(
        text,
        "bert_morph_tagging",
        lambda w: [
            {
                "bert_tokens": ["▁" + w],
                "form": "sg g",
                "partofspeech": "S",
                "probability": 0.5,
            }
        ],
    )
    expert = _make_layer(
        text,
        "expert",
        lambda w: (
            [
                {
                    "bert_tokens": ["▁" + w],
                    "form": "adt",
                    "partofspeech": "S",
                    "probability": 0.97,
                }
            ]
            if w == "komisjoni"
            else []
        ),
    )

    retagger = _retagger_with_stub(monkeypatch)
    retagger._correct_layer(source, {(s.start, s.end): s for s in expert})

    # The homonymous word takes the expert's label ...
    assert _annotations_of(source, "komisjoni") == [("adt", "S")]
    # ... and the other words are left alone
    assert _annotations_of(source, "Esitasin") == [("sg g", "S")]
    assert _annotations_of(source, "aruande") == [("sg g", "S")]
    meta = source.meta["morph_homonyms_retagger"]
    assert meta["inspected_words"] == 1
    assert meta["agreed_words"] == 0
    assert meta["corrected_words"] == 1


def test_expert_agreement_keeps_matching_annotation(monkeypatch):
    # Tests MorphHomonymsRetagger._correct_layer (the disambiguation branch): if
    # the expert confirms one of the existing analyses, only the matching ones are
    # kept, and this counts as an agreement rather than a correction
    text = Text(HOMONYM_SENTENCE).tag_layer(["words", "sentences"])
    source = _make_layer(
        text,
        "bert_morph_tagging",
        lambda w: (
            [
                {"bert_tokens": ["x"], "form": f, "partofspeech": "S", "probability": p}
                for f, p in (("sg g", 0.5), ("adt", 0.3))
            ]
            if w == "komisjoni"
            else [
                {
                    "bert_tokens": ["▁" + w],
                    "form": "sg n",
                    "partofspeech": "S",
                    "probability": 0.9,
                }
            ]
        ),
    )
    expert = _make_layer(
        text,
        "expert",
        lambda w: (
            [
                {
                    "bert_tokens": ["x"],
                    "form": "adt",
                    "partofspeech": "S",
                    "probability": 0.88,
                }
            ]
            if w == "komisjoni"
            else []
        ),
    )

    retagger = _retagger_with_stub(monkeypatch)
    retagger._correct_layer(source, {(s.start, s.end): s for s in expert})

    assert _annotations_of(source, "komisjoni") == [("adt", "S")]
    meta = source.meta["morph_homonyms_retagger"]
    assert meta["agreed_words"] == 1
    assert meta["corrected_words"] == 0


def test_words_outside_lexicon_are_never_inspected(monkeypatch):
    # Tests the homonym lexicon gate (_is_homonym_word, as used by _correct_layer):
    # predictions exist for every word, but only lexicon members may be changed
    text = Text(HOMONYM_SENTENCE).tag_layer(["words", "sentences"])
    source = _make_layer(
        text,
        "bert_morph_tagging",
        lambda w: [
            {
                "bert_tokens": ["▁" + w],
                "form": "sg g",
                "partofspeech": "S",
                "probability": 0.5,
            }
        ],
    )
    expert = _make_layer(
        text,
        "expert",
        lambda w: [
            {
                "bert_tokens": ["▁" + w],
                "form": "adt",
                "partofspeech": "S",
                "probability": 0.97,
            }
        ],
    )

    retagger = _retagger_with_stub(monkeypatch)
    retagger._correct_layer(source, {(s.start, s.end): s for s in expert})

    assert _annotations_of(source, "Esitasin") == [("sg g", "S")]
    assert _annotations_of(source, "aruande") == [("sg g", "S")]
    assert source.meta["morph_homonyms_retagger"]["inspected_words"] == 1


def test_vabamorf_style_layer_cannot_be_overridden(monkeypatch):
    # Tests _build_expert_annotation's attribute guard: Vabamorf annotations carry
    # lemma/root/ending, which cannot be derived from a (form, partofspeech)
    # prediction, so overriding must raise instead of blanking those attributes
    text = Text(HOMONYM_SENTENCE).tag_layer(["words", "sentences"])
    source = Layer(
        name="morph_analysis",
        attributes=["lemma", "root", "ending", "form", "partofspeech"],
        text_object=text,
        parent="words",
        ambiguous=True,
    )
    for word in text.words:
        source.add_annotation(
            (word.start, word.end),
            lemma=word.text,
            root=word.text,
            ending="0",
            form="sg g",
            partofspeech="S",
        )
    expert = _make_layer(
        text,
        "expert",
        lambda w: (
            [
                {
                    "bert_tokens": ["x"],
                    "form": "adt",
                    "partofspeech": "S",
                    "probability": 0.9,
                }
            ]
            if w == "komisjoni"
            else []
        ),
    )

    retagger = _retagger_with_stub(monkeypatch, output_layer="morph_analysis")
    with pytest.raises(ValueError, match="lemma"):
        retagger._correct_layer(source, {(s.start, s.end): s for s in expert})


# Five sentences; 'komisjoni' appears in the 1st, 3rd and 5th.
MULTI_SENTENCE_TEXT = (
    "Komisjoni aruanne tuli. Ma tulin koju. Kass magab komisjoni toolil. "
    "Vaatasin filmi. Lugesin komisjoni raportit."
)


class _RecordingBertMorphTagger(_StubBertMorphTagger):
    """Stub that records which sentences it was asked to tag, and predicts a
    label for every word of the (extracted) sentence it receives."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seen_sentences = []

    def make_layer(self, text, layers, status=None):
        self.seen_sentences.append(text.text)
        layer = Layer(
            name="expert_predictions",
            attributes=MORPH_ATTRIBUTES,
            text_object=text,
            parent="words",
            ambiguous=True,
        )
        for word in text.words:
            layer.add_annotation(
                (word.start, word.end),
                bert_tokens=["▁" + word.text],
                form="adt",
                partofspeech="S",
                probability=0.9,
            )
        return layer


def _build_span_map(monkeypatch, homonyms, skip_words=()):
    """Run _build_predicted_span_map over MULTI_SENTENCE_TEXT.

    Words listed in skip_words get no span in the source layer, which models a
    sparse layer (not every word is necessarily covered).
    Returns (retagger, text, span_map).
    """
    monkeypatch.setattr(mhr_module, "BertMorphTagger", _RecordingBertMorphTagger)
    retagger = mhr_module.MorphHomonymsRetagger(
        model_location="stub", homonym_words=homonyms, output_layer="bert_morph_tagging"
    )
    text = Text(MULTI_SENTENCE_TEXT).tag_layer(["words", "sentences"])
    skip = {w.lower() for w in skip_words}
    source = Layer(
        name="bert_morph_tagging",
        attributes=MORPH_ATTRIBUTES,
        text_object=text,
        parent="words",
        ambiguous=True,
    )
    for word in text.words:
        if word.text.lower() in skip:
            continue
        source.add_annotation(
            (word.start, word.end),
            bert_tokens=["▁" + word.text],
            form="sg g",
            partofspeech="S",
            probability=0.5,
        )
    span_map = retagger._build_predicted_span_map(
        text,
        {
            "sentences": text.sentences,
            "words": text.words,
            "bert_morph_tagging": source,
        },
        {},
    )
    return retagger, text, span_map


def test_only_sentences_with_homonyms_are_sent_to_the_expert(monkeypatch):
    # Tests _build_predicted_span_map: the expert is run only for sentences that
    # contain a lexicon word, and the source layer is walked with a single
    # running index instead of being rescanned for every sentence
    retagger, _text, _span_map = _build_span_map(monkeypatch, {"komisjoni"})
    assert retagger._bert_morph_tagger.seen_sentences == [
        "Komisjoni aruanne tuli.",
        "Kass magab komisjoni toolil.",
        "Lugesin komisjoni raportit.",
    ]


def test_predicted_span_map_uses_original_text_offsets(monkeypatch):
    # Tests _build_predicted_span_map: sentences are cut out with extract_section,
    # which rebases offsets to 0, so the span map must be keyed by offsets in the
    # ORIGINAL text again
    _retagger, text, span_map = _build_span_map(monkeypatch, {"komisjoni"})

    expected = set()
    for sentence in text.sentences:
        words = [
            w for w in text.words if w.start >= sentence.start and w.end <= sentence.end
        ]
        if any(w.text.lower() == "komisjoni" for w in words):
            expected |= {(w.start, w.end) for w in words}
    assert set(span_map) == expected
    # The keys must address the very words they were produced for
    for (start, end), span in span_map.items():
        assert text.text[start:end] == span.text


@pytest.mark.parametrize(
    "homonyms,skip_words,expected_sentences",
    [
        # homonym in the first sentence only
        ({"aruanne"}, (), ["Komisjoni aruanne tuli."]),
        # homonym in the last sentence only
        ({"raportit"}, (), ["Lugesin komisjoni raportit."]),
        # homonym in a middle sentence only
        ({"filmi"}, (), ["Vaatasin filmi."]),
        # no homonyms at all
        ({"puudub"}, (), []),
        # sparse source layer: words before/after the homonym have no span
        (
            {"komisjoni"},
            ("ma", "kass"),
            [
                "Komisjoni aruanne tuli.",
                "Kass magab komisjoni toolil.",
                "Lugesin komisjoni raportit.",
            ],
        ),
        # sparse source layer: the homonym itself has no span, so it is not found
        ({"komisjoni"}, ("komisjoni",), []),
    ],
)
def test_running_index_finds_homonyms_in_any_position(
    monkeypatch, homonyms, skip_words, expected_sentences
):
    # Tests _build_predicted_span_map's running index: advancing it must never
    # skip past a later sentence's words, wherever the homonyms happen to sit,
    # and it must cope with a source layer that does not cover every word
    retagger, _text, _span_map = _build_span_map(monkeypatch, homonyms, skip_words)
    assert retagger._bert_morph_tagger.seen_sentences == expected_sentences


# ===========================================================================
#   Tests that require both the baseline and the expert model
# ===========================================================================


def _tag_and_retag(sentence):
    """Apply BertMorphTagger, then MorphHomonymsRetagger, and return
    (baseline labels, final labels, bert_tokens, retagging metadata)."""
    from estnltk_neural.taggers import BertMorphTagger
    from estnltk_neural.taggers import MorphHomonymsRetagger

    text = Text(sentence).tag_layer(["words", "sentences"])
    BertMorphTagger(model_location=BERTMORPH_V2_PATH).tag(text)
    layer = text["bert_morph_tagging"]
    baseline = [
        (sp.text, sp.annotations[0]["form"], sp.annotations[0]["partofspeech"])
        for sp in layer
    ]

    MorphHomonymsRetagger(model_location=BERTMORPH_EXPERT_PATH).retag(text)
    layer = text["bert_morph_tagging"]
    final = [
        (sp.text, sp.annotations[0]["form"], sp.annotations[0]["partofspeech"])
        for sp in layer
    ]
    tokens = [(sp.text, list(sp.annotations[0]["bert_tokens"])) for sp in layer]
    return baseline, final, tokens, layer.meta["morph_homonyms_retagger"]


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None or BERTMORPH_EXPERT_PATH is None,
    reason="BertMorphTagger's and/or the expert model's location not known. "
    + "Use estnltk.download('bert_morph_v2') and "
    + "estnltk.download('bert_morph_expert') to get the missing resources.",
)
def test_expert_model_uses_sentencepiece_tokenization():
    # Guards against a broken tokenizer_config.json in the published models.
    # These models carry a SentencePiece vocabulary whose subwords are marked
    # with '▁'. If tokenizer_config.json names a tokenizer class that makes
    # transformers fall back to byte-level BPE (which happens with
    # 'RobertaTokenizer' on transformers >= 5), the model silently receives
    # token ids it never saw during training and its output becomes completely wrong.
    from transformers import AutoTokenizer

    for name, location in (
        ("expert", BERTMORPH_EXPERT_PATH),
        ("baseline", BERTMORPH_V2_PATH),
    ):
        tokenizer = AutoTokenizer.from_pretrained(location)
        tokens = tokenizer.tokenize("Kutsuti komisjoni kokku.")
        assert tokens == ["▁Kuts", "uti", "▁komisjoni", "▁kokku", "."], (
            f"{name} model is not tokenizing with SentencePiece; got {tokens!r}. "
            "Check 'tokenizer_class' in the model's tokenizer_config.json."
        )


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    not check_if_pytorch_is_available(),
    reason="package pytorch is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None,
    reason="BertMorphTagger's model location not known. "
    + "Use estnltk.download('bert_morph_v2') to get the missing resources.",
)
@pytest.mark.skipif(
    BERTMORPH_EXPERT_PATH is None,
    reason="MorphHomonymsRetagger's expert model location not known. "
    + "Use estnltk.download('bert_morph_expert') to get the missing resources.",
)
def test_morph_homonyms_retagger_out_of_the_box():
    # Tests MorphHomonymsRetagger end-to-end (retag) with the real expert model:
    # BertMorphTagger creates the 'bert_morph_tagging' layer, then the retagger
    # re-evaluates only the homonymous words in it. Here the expert DISAGREES
    # with the baseline, so its correction must be applied.
    baseline, final, tokens, meta = _tag_and_retag("Kutsuti komisjoni kokku.")

    assert baseline == [
        ("Kutsuti", "ti", "V"),
        ("komisjoni", "sg p", "S"),
        ("kokku", "", "D"),
        (".", "", "Z"),
    ]
    # 'komisjoni' is corrected sg p -> sg g; every other word is left alone
    assert final == [
        ("Kutsuti", "ti", "V"),
        ("komisjoni", "sg g", "S"),
        ("kokku", "", "D"),
        (".", "", "Z"),
    ]
    # Subtokens must be SentencePiece pieces (see the tokenization test above)
    assert tokens == [
        ("Kutsuti", ["▁Kuts", "uti"]),
        ("komisjoni", ["▁komisjoni"]),
        ("kokku", ["▁kokku"]),
        (".", ["."]),
    ]
    assert meta["inspected_words"] == 1
    assert meta["agreed_words"] == 0
    assert meta["corrected_words"] == 1
    assert meta["output_layer"] == "bert_morph_tagging"
    assert meta["homonym_list_size"] >= 1000


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    not check_if_pytorch_is_available(),
    reason="package pytorch is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None,
    reason="BertMorphTagger's model location not known. "
    + "Use estnltk.download('bert_morph_v2') to get the missing resources.",
)
@pytest.mark.skipif(
    BERTMORPH_EXPERT_PATH is None,
    reason="MorphHomonymsRetagger's expert model location not known. "
    + "Use estnltk.download('bert_morph_expert') to get the missing resources.",
)
def test_morph_homonyms_retagger_keeps_baseline_when_expert_agrees():
    # Same pipeline, but a context where the expert confirms the baseline:
    # nothing may change and the word counts as an agreement.
    baseline, final, _tokens, meta = _tag_and_retag("Esitasin komisjoni aruande.")

    assert baseline == [
        ("Esitasin", "sin", "V"),
        ("komisjoni", "sg g", "S"),
        ("aruande", "sg g", "S"),
        (".", "", "Z"),
    ]
    assert final == baseline
    assert meta["inspected_words"] == 1
    assert meta["agreed_words"] == 1
    assert meta["corrected_words"] == 0


# ===========================================================================
#   MorphHomonymsRetagger used as a post_disambiguator inside other taggers
# ===========================================================================

POST_DISAMB_SENTENCE = "Kutsuti komisjoni kokku."

# 'komisjoni' is a homonymous form for which Vabamorf offers 'adt', 'sg g' and
# 'sg p'. The wiring tests below force 'adt' with a stub retagger instead of
# relying on the real expert model: that way the assertions do not depend on the
# models predicting any particular label, and they cannot pass vacuously if a
# future model happens to agree with the baseline.
FORCED_FORM = "adt"


class _ForcingRetagger(Retagger):
    """Minimal Retagger that rewrites one word's form to a fixed value.

    Used to verify that `post_disambiguator` is invoked, on the expected layer
    and at the expected point, without depending on the expert model. It records
    the name of every layer it was handed, so a test can prove it really ran
    rather than inferring it from a label that a model might produce anyway.
    """

    conf_param = ("target_word", "forced_form", "seen_layers",
                  "sentences_layer", "words_layer")

    def __init__(self, target_word, forced_form=FORCED_FORM,
                 output_layer="bert_morph_tagging",
                 sentences_layer="sentences", words_layer="words"):
        self.target_word = target_word
        self.forced_form = forced_form
        self.output_layer = output_layer
        self.output_attributes = MORPH_ATTRIBUTES
        self.sentences_layer = sentences_layer
        self.words_layer = words_layer
        self.input_layers = [sentences_layer, words_layer, output_layer]
        self.seen_layers = []

    def _change_layer(self, text, layers, status=None):
        layer = layers[self.output_layer]
        self.seen_layers.append(layer.name)
        for span in layer:
            if span.text != self.target_word:
                continue
            annotations = [dict(a) for a in span.annotations]
            span.clear_annotations()
            for annotation in annotations:
                annotation["form"] = self.forced_form
                span.add_annotation(annotation)


def _forms_of(layer, word):
    for span in layer:
        if span.text == word:
            return sorted({(a["partofspeech"], a["form"]) for a in span.annotations})
    return None


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    not check_if_pytorch_is_available(),
    reason="package pytorch is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None,
    reason="BertMorphTagger's model location not known. "
    + "Use estnltk.download('bert_morph_v2') to get the missing resources.",
)
def test_post_disambiguator_is_applied_in_tagger_mode():
    # Tests BertMorphTagger's post_disambiguator in tagger mode: the retagger must
    # be handed the layer Bert has just created. A stub retagger is used so that
    # the assertion does not depend on what the expert model happens to predict.
    from estnltk_neural.taggers import BertMorphTagger

    stub = _ForcingRetagger("komisjoni")
    text = Text(POST_DISAMB_SENTENCE).tag_layer(["words", "sentences"])
    BertMorphTagger(model_location=BERTMORPH_V2_PATH, post_disambiguator=stub).tag(text)

    # The retagger really ran, and it was handed Bert's own layer
    assert stub.seen_layers == ["bert_morph_tagging"]
    # ... and its effect is visible on the target word only
    assert _forms_of(text["bert_morph_tagging"], "komisjoni") == [("S", FORCED_FORM)]
    assert _forms_of(text["bert_morph_tagging"], "Kutsuti") == [("V", "ti")]


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    not check_if_pytorch_is_available(),
    reason="package pytorch is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None,
    reason="BertMorphTagger's model location not known. "
    + "Use estnltk.download('bert_morph_v2') to get the missing resources.",
)
def test_post_disambiguator_is_applied_in_disambiguator_mode():
    # Tests that post_disambiguator also applies when BertMorphTagger is used as a
    # disambiguator (disambiguate=True, applied via retag) on a Vabamorf layer.
    # The retagger is applied to Bert's own layer, and the refined prediction is
    # what then disambiguates the Vabamorf analyses -- so forcing 'adt' must leave
    # 'adt' in morph_analysis, which Vabamorf does offer for this word.
    from estnltk.taggers import VabamorfAnalyzer
    from estnltk_neural.taggers import BertMorphTagger

    stub = _ForcingRetagger("komisjoni")
    text = Text(POST_DISAMB_SENTENCE).tag_layer(
        ["words", "sentences", "compound_tokens"]
    )
    VabamorfAnalyzer().tag(text)
    BertMorphTagger(
        model_location=BERTMORPH_V2_PATH,
        output_layer="morph_analysis",
        disambiguate=True,
        post_disambiguator=stub,
    ).retag(text)

    # The retagger was handed Bert's layer (named after this tagger's output_layer)
    assert stub.seen_layers == ["morph_analysis"]
    assert _forms_of(text["morph_analysis"], "komisjoni") == [("S", FORCED_FORM)]


@pytest.mark.skipif(
    not check_if_transformers_is_available(),
    reason="package transformers is required for this test",
)
@pytest.mark.skipif(
    not check_if_pytorch_is_available(),
    reason="package pytorch is required for this test",
)
@pytest.mark.skipif(
    BERTMORPH_V2_PATH is None,
    reason="BertMorphTagger's model location not known. "
    + "Use estnltk.download('bert_morph_v2') to get the missing resources.",
)
def test_post_disambiguator_is_passed_on_by_vabamorf_with_bert_tagger():
    # Tests VabamorfWithBertTagger's post_disambiguator: it must reach the
    # BertMorphTagger created inside, and its effect must survive into the final
    # morph_analysis layer. Note that the stub keeps its own default output_layer
    # name ('bert_morph_tagging') here -- it is handed the layer under the name it
    # expects, so it does not have to be reconfigured to match.
    from estnltk_neural.taggers import VabamorfWithBertTagger

    stub = _ForcingRetagger("komisjoni")
    tagger = VabamorfWithBertTagger(post_disambiguator=stub)
    # The parameter is forwarded to the internal BertMorphTagger
    assert tagger.bert_disamb.post_disambiguator is stub

    text = Text(POST_DISAMB_SENTENCE).tag_layer(
        ["words", "sentences", "compound_tokens"]
    )
    tagger.tag(text)
    assert stub.seen_layers == ["morph_analysis"]
    assert _forms_of(text["morph_analysis"], "komisjoni") == [("S", FORCED_FORM)]


def test_invalid_post_disambiguator_is_rejected():
    # Tests BertMorphTagger's validation of post_disambiguator. The validation runs
    # before the model is loaded, so no model is needed here -- a misconfigured
    # post_disambiguator should not cost a model download first.
    from estnltk_neural.taggers import BertMorphTagger

    # Not a Retagger
    with pytest.raises(TypeError, match="Retagger"):
        BertMorphTagger(model_location="no_such_model", post_disambiguator="nope")

    # A post disambiguator works on the word level, so token_level is not allowed
    with pytest.raises(Exception, match="token_level"):
        BertMorphTagger(
            model_location="no_such_model",
            token_level=True,
            post_disambiguator=_ForcingRetagger("komisjoni"),
        )

    # Input layers the tagger cannot provide
    with pytest.raises(Exception, match="input layer"):
        BertMorphTagger(
            model_location="no_such_model",
            post_disambiguator=_ForcingRetagger(
                "komisjoni", sentences_layer="my_sentences"
            ),
        )
