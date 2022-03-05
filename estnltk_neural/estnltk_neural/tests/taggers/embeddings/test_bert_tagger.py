import pkgutil
import pytest
from estnltk import Text
import os

PACKAGE_PATH = os.path.dirname(__file__)
MODEL_PATH = os.path.join(PACKAGE_PATH, '..', '..', '..', 'taggers', 'embeddings', 'bert', 'model-data')


def check_if_transformers_is_available():
    return pkgutil.find_loader("transformers") is not None


def check_if_pytorch_is_available():
    return pkgutil.find_loader("torch") is not None


def check_if_model_present():
    # Check that expected Bert model files are present
    # (this is a minimum, there can be more files)
    expected_model_files = ['bert_config.json',
        'config.json', 'pytorch_model.bin', 
        'special_tokens_map.json', 'tokenizer_config.json',
        'vocab.txt']
    model_dir_files = list( os.listdir(MODEL_PATH) )
    return all([exp_file in model_dir_files for exp_file in expected_model_files])


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="Model is not available in the models directory")
def test_bert_tagger():
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    bert_tagger = BertTagger(MODEL_PATH)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    bert_tagger.tag(text)
    assert 'bert_embeddings' in text.layers

    for embedding_span in text.bert_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072

    bert_add_tagger = BertTagger(MODEL_PATH, method='add',
                                 output_layer='bert_embeddings_add')
    bert_add_tagger.tag(text)
    assert 'bert_embeddings_add' in text.layers

    for embedding_span in text.bert_embeddings_add:
        assert len(embedding_span.bert_embedding[0]) == 768

    bert_all_tagger = BertTagger(MODEL_PATH, method='all',
                                 output_layer='bert_embeddings_all')
    bert_all_tagger.tag(text)
    assert 'bert_embeddings_all' in text.layers
    for embedding_span in text.bert_embeddings_all:
        assert len(embedding_span.bert_embedding[0][0]) == 768
        assert len(embedding_span.bert_embedding[0][1]) == 768
        assert len(embedding_span.bert_embedding[0][2]) == 768
        assert len(embedding_span.bert_embedding[0][3]) == 768
        assert len(embedding_span.bert_embedding[0]) == 4

    bert_word_tagger = BertTagger(MODEL_PATH, token_level=False,
                                  output_layer='bert_word_embeddings')
    bert_word_tagger.tag(text)

    assert 'bert_word_embeddings' in text.layers

    assert len(text.words) == len(text.bert_word_embeddings)
    for s1, s2 in zip(text.words, text.bert_word_embeddings):
        assert s1.start == s2.start
        assert s1.end == s2.end
        assert len(s2.bert_embedding[0]) == 3072

    bert_word_tagger_all = BertTagger(MODEL_PATH, token_level=False, method='all',
                                      output_layer='bert_word_embeddings_all')
    bert_word_tagger_all.tag(text)
    assert 'bert_word_embeddings_all' in text.layers

    for embedding_span in text.bert_word_embeddings_all:
        assert len(embedding_span.bert_embedding[0][0]) == 4
        for emb in embedding_span.bert_embedding[0][0]:
            assert len(emb) == 768

    bert_word_tagger_concat = BertTagger(MODEL_PATH, token_level=False, method='concatenate',
                                         output_layer='bert_word_embeddings_concat')
    bert_word_tagger_concat.tag(text)
    assert 'bert_word_embeddings_concat' in text.layers

    for embedding_span in text.bert_word_embeddings_concat:
        assert len(embedding_span.bert_embedding[0]) == 3072

    bert_word_tagger_add = BertTagger(MODEL_PATH, token_level=False, method='add',
                                      output_layer='bert_word_embeddings_add')
    bert_word_tagger_add.tag(text)
    assert 'bert_word_embeddings_add' in text.layers
    for embedding_span in text.bert_word_embeddings_add:
        assert len(embedding_span.bert_embedding[0]) == 768

    bert_diff_layer_tagger1 = BertTagger(MODEL_PATH, bert_layers=[-1],
                                         output_layer='bert_diff_layers1_embeddings')
    bert_diff_layer_tagger1.tag(text)
    assert 'bert_diff_layers1_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers1_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 768

    bert_diff_layer_tagger2 = BertTagger(MODEL_PATH, bert_layers=[-2, -1],
                                         output_layer='bert_diff_layers2_embeddings')
    bert_diff_layer_tagger2.tag(text)
    assert 'bert_diff_layers2_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers2_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 1536

    text = Text(' '.join(['Tere ']*513))
    text.tag_layer('sentences')
    bert_long_seq_tagger = BertTagger(MODEL_PATH, output_layer='bert_embeddings_long_seq')
    bert_long_seq_tagger.tag(text)
    assert 'bert_embeddings_long_seq' in text.layers

    for embedding_span in text.bert_embeddings_long_seq:
        assert len(embedding_span.bert_embedding[0]) == 3072