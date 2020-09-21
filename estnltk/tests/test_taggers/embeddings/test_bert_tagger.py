import pkgutil
import pytest
from estnltk import Text
import os

PACKAGE_PATH = os.path.dirname(__file__)
MODEL_PATH = os.path.join(PACKAGE_PATH, '..','..', '..','taggers', 'embeddings', 'bert','model-data')


def check_if_transformers_is_available():
    return pkgutil.find_loader("transformers") is not None


def check_if_pytorch_is_available():
    return pkgutil.find_loader("torch") is not None


def check_if_model_present():

    return len(os.listdir(MODEL_PATH)) != 0

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="Model is not available in the models directory")
def test_bert_tagger():
    from estnltk.taggers.embeddings.bert.bert_tagger import BertTagger
    bert_tagger = BertTagger(MODEL_PATH)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.analyse('segmentation')
    bert_tagger.tag(text)
    assert 'bert_embeddings' in text.layers

    for embedding_span in text.bert_embeddings:
        assert embedding_span.bert_embedding[0].shape == (3072,)

    bert_add_tagger = BertTagger(MODEL_PATH, method='add',
                                 output_layer='bert_embeddings_add')
    bert_add_tagger.tag(text)
    assert 'bert_embeddings_add' in text.layers

    for embedding_span in text.bert_embeddings_add:
        assert embedding_span.bert_embedding[0].shape == (768,)

    bert_all_tagger = BertTagger(MODEL_PATH, method='all',
                                 output_layer='bert_embeddings_all')
    bert_all_tagger.tag(text)
    assert 'bert_embeddings_all' in text.layers
    for embedding_span in text.bert_embeddings_all:
        assert embedding_span.bert_embedding[0][0].size == 768
        assert embedding_span.bert_embedding[0][1].size == 768
        assert embedding_span.bert_embedding[0][2].size == 768
        assert embedding_span.bert_embedding[0][3].size == 768
        assert len(embedding_span.bert_embedding[0]) == 4

    bert_word_tagger = BertTagger(MODEL_PATH, token_level=False,
                                  output_layer='bert_word_embeddings')
    bert_word_tagger.tag(text)

    assert 'bert_word_embeddings' in text.layers

    assert len(text.words) == len(text.bert_word_embeddings)
    for s1, s2 in zip(text.words, text.bert_word_embeddings):
        assert s1.start == s2.start
        assert s1.end == s2.end
        assert s2.bert_embedding[0].size == 3072

    bert_diff_layer_tagger1 = BertTagger(MODEL_PATH, bert_layers=[-1],
                                         output_layer='bert_diff_layers1_embeddings')
    bert_diff_layer_tagger1.tag(text)
    assert 'bert_diff_layers1_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers1_embeddings:
        assert embedding_span.bert_embedding[0].shape == (768,)

    bert_diff_layer_tagger2 = BertTagger(MODEL_PATH, bert_layers=[-2, -1],
                                         output_layer='bert_diff_layers2_embeddings')
    bert_diff_layer_tagger2.tag(text)
    assert 'bert_diff_layers2_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers2_embeddings:
        assert embedding_span.bert_embedding[0].shape == (1536,)


