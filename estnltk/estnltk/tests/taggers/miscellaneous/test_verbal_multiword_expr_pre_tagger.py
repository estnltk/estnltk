import json

import pytest

from estnltk import Layer, Text
from estnltk.downloader import get_resource_paths
from estnltk.taggers import VerbalMultiWordExprPreTagger
from estnltk.vabamorf.morf import Vabamorf, generate_verb_phrases


DEFAULT_LEXICON = get_resource_paths('verbal_multiword_expr_lexicon',
                                     only_latest=True, download_missing=False)
pytestmark = pytest.mark.skipif(
    DEFAULT_LEXICON is None,
    reason="Missing lexicon. Use estnltk.download('verbal_multiword_expr_lexicon').",
)


def make_text(sentence, syntax_rows):
    # Use a fixed analysis so the tests do not need a parser or model.
    text = Text(sentence).tag_layer(['sentences'])
    clauses = Layer('clauses', enveloping='words', text_object=text)
    clauses.add_annotation([word.base_span for word in text.words])
    text.add_layer(clauses)

    syntax = Layer('stanza_syntax', parent='words', text_object=text,
                   attributes=('id', 'lemma', 'upostag', 'feats', 'head', 'deprel'))
    for i, (word, row) in enumerate(zip(text.words, syntax_rows), 1):
        lemma, pos, feats, head, deprel = row
        syntax.add_annotation(word.base_span, id=i, lemma=lemma, upostag=pos,
                              feats=feats, head=head, deprel=deprel)
    text.add_layer(syntax)
    return text


def test_verbal_multiword_expr_pre_tagger_smoke():
    text = make_text('Ta õiendas arveid.', [
        ('tema', 'PRON', {}, 2, 'nsubj'),
        ('õiendama', 'VERB', {'VerbForm': 'Fin'}, 0, 'root'),
        ('arve', 'NOUN', {}, 2, 'obj'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    VerbalMultiWordExprPreTagger().tag(text)

    layer = text.pre_verbal_multiword_expressions
    assert len(layer) == 1
    relation = layer[0]
    assert relation['verb'].text == 'õiendas'
    assert relation['comp_1'].text == 'arveid'
    assert relation.annotations[0]['expression'] == 'arveid õiendama'


def test_include_nonfinite():
    text = make_text('Ta tahtis arveid õiendada.', [
        ('tema', 'PRON', {}, 2, 'nsubj'),
        ('tahtma', 'VERB', {'VerbForm': 'Fin'}, 0, 'root'),
        ('arve', 'NOUN', {}, 4, 'obj'),
        ('õiendama', 'VERB', {'VerbForm': 'Inf'}, 2, 'xcomp'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    default_layer = VerbalMultiWordExprPreTagger().make_layer(text)
    assert len(default_layer) == 0

    layer = VerbalMultiWordExprPreTagger(include_nonfinite=True).make_layer(text)
    assert len(layer) == 1
    assert layer[0]['verb'].text == 'õiendada'
    assert layer[0].annotations[0]['expression'] == 'arveid õiendama'


def test_include_compound_verbs():
    text = make_text('Ta läks ära.', [
        ('tema', 'PRON', {}, 2, 'nsubj'),
        ('minema', 'VERB', {'VerbForm': 'Fin'}, 0, 'root'),
        ('ära', 'ADV', {}, 2, 'compound:prt'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    assert len(VerbalMultiWordExprPreTagger().make_layer(text)) == 0

    layer = VerbalMultiWordExprPreTagger(include_compound_verbs=True).make_layer(text)
    assert len(layer) == 1
    assert layer[0]['verb'].text == 'läks'
    assert layer[0]['comp_1'].text == 'ära'
    assert layer[0].annotations[0]['is_compound_verb'] is True


def test_include_verbal_idioms():
    text = make_text('Ta pani selle kirja.', [
        ('tema', 'PRON', {}, 2, 'nsubj'),
        ('panema', 'VERB', {'VerbForm': 'Fin'}, 0, 'root'),
        ('see', 'PRON', {}, 2, 'obj'),
        ('kiri', 'NOUN', {}, 2, 'compound:idiom'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    assert len(VerbalMultiWordExprPreTagger().make_layer(text)) == 0

    layer = VerbalMultiWordExprPreTagger(include_verbal_idioms=True).make_layer(text)
    assert len(layer) == 1
    assert layer[0]['verb'].text == 'pani'
    assert layer[0]['comp_1'].text == 'kirja'
    assert layer[0].annotations[0]['is_verbal_idiom'] is True


def test_include_copula_heads():
    text = make_text('Ta on abiks.', [
        ('tema', 'PRON', {}, 3, 'nsubj:cop'),
        ('olema', 'AUX', {'VerbForm': 'Fin'}, 3, 'cop'),
        ('abi', 'NOUN', {}, 0, 'root'),
        ('.', 'PUNCT', {}, 3, 'punct'),
    ])
    assert len(VerbalMultiWordExprPreTagger(include_copula_heads=False).make_layer(text)) == 0

    layer = VerbalMultiWordExprPreTagger().make_layer(text)
    assert len(layer) == 1
    assert layer[0]['verb'].text == 'on'
    assert layer[0]['comp_1'].text == 'abiks'
    assert layer[0].annotations[0]['expression'] == 'abiks olema'


def test_custom_lexicon_and_max_components(tmp_path):
    path = tmp_path / 'lexicon.json'
    path.write_text(json.dumps([{
        'expression': 'luubi alla võtma',
        'is_inflected': False,
        'components': [
            {'form': 'luubi', 'lemmas': ['luup'], 'match_by_lemma': False, 'is_anchor': False},
            {'form': 'alla', 'lemmas': ['alla'], 'match_by_lemma': False, 'is_anchor': False},
            {'form': 'võtma', 'lemmas': ['võtma'], 'match_by_lemma': True, 'is_anchor': True},
        ],
    }]), encoding='utf-8')
    with pytest.raises(ValueError, match='exceeds max_components=1'):
        VerbalMultiWordExprPreTagger(lexicon_path=path, max_components=1)

    text = make_text('Ta võttis luubi alla.', [
        ('tema', 'PRON', {}, 2, 'nsubj'),
        ('võtma', 'VERB', {'VerbForm': 'Fin'}, 0, 'root'),
        ('luup', 'NOUN', {}, 2, 'obl'),
        ('alla', 'ADP', {}, 3, 'case'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    layer = VerbalMultiWordExprPreTagger(lexicon_path=path, max_components=2).make_layer(text)
    assert layer.span_names == ('verb', 'comp_1', 'comp_2')
    assert len(layer) == 1
    assert layer[0]['comp_2'].text == 'alla'


def make_verb_phrase_text(phrase):
    # Keep dependencies fixed while using real Vabamorf analyses of generated forms.
    words = phrase.split() + ['arveid', '.']
    anchor_id = len(words) - 2
    relations = ['aux'] * (anchor_id - 1) + ['root', 'obj', 'punct']
    analyses = Vabamorf.instance().analyze(words, disambiguate=False)
    syntax_rows = []
    for word_id, word in enumerate(analyses, 1):
        analysis = next((a for a in word['analysis'] if a['partofspeech'] == 'V'),
                        word['analysis'][0])
        features = {form: form for form in analysis['form'].split()}
        head = 0 if word_id == anchor_id else anchor_id
        deprel = relations[word_id - 1]
        syntax_rows.append((analysis['lemma'], analysis['partofspeech'], features, head, deprel))
    return make_text(f'{phrase} arveid.', syntax_rows)


def test_generated_verb_phrases():
    phrases = generate_verb_phrases('õiendama', output_type='verb_phrase')
    assert phrases
    tagger = VerbalMultiWordExprPreTagger(include_nonfinite=True)
    for phrase in sorted(set(phrases)):
        text = make_verb_phrase_text(phrase)
        layer = tagger.make_layer(text)
        assert len(layer) == 1, text.text
        assert layer[0]['verb'].text == phrase.split()[-1]
        assert layer[0]['comp_1'].text == 'arveid'
        assert layer[0].annotations[0]['expression'] == 'arveid õiendama'


def test_negative_verb_form():
    tagger = VerbalMultiWordExprPreTagger()
    text = make_text('Poldud abiks.', [
        ('olema', 'AUX', {'neg': 'neg', 'tud': 'tud'}, 2, 'cop'),
        ('abi', 'NOUN', {}, 0, 'root'),
        ('.', 'PUNCT', {}, 2, 'punct'),
    ])
    layer = tagger.make_layer(text)
    assert len(layer) == 1
    assert layer[0]['verb'].text == 'Poldud'
    assert layer[0].annotations[0]['expression'] == 'abiks olema'

    text = make_text('Abiks oldud.', [
        ('abi', 'NOUN', {}, 0, 'root'),
        ('olema', 'AUX', {'tud': 'tud'}, 1, 'cop'),
        ('.', 'PUNCT', {}, 1, 'punct'),
    ])
    assert len(tagger.make_layer(text)) == 0
    assert len(VerbalMultiWordExprPreTagger(include_nonfinite=True).make_layer(text)) == 1
