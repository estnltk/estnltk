import pkgutil
import pytest
from estnltk import Text
import os

from estnltk.downloader import get_resource_paths

# Try to get the resources path for BertTransformer. If missing, do nothing. It's up for the user to download the missing resources
MODEL_PATH = get_resource_paths("berttransformer", only_latest=True, download_missing=False)


def check_if_transformers_is_available():
    return pkgutil.find_loader("transformers") is not None


def check_if_pytorch_is_available():
    return pkgutil.find_loader("torch") is not None


def check_if_model_present():
    # Check that expected Bert model files are present
    # (this is a minimum, there can be more files)
    expected_model_files = [ \
        'config.json', 'pytorch_model.bin', 
        'special_tokens_map.json', 'tokenizer_config.json',
        'vocab.txt']
    model_dir_files = list(os.listdir(MODEL_PATH)) if MODEL_PATH is not None else []
    return all([exp_file in model_dir_files for exp_file in expected_model_files])


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="BertTransformer's resources have not been downloaded. "+\
                           "Use estnltk.download('berttransformer') to get the missing resources.")
def test_bert_transformer_out_of_the_box():
    # Test that BertTransformer works "out_of_the_box" if resources have been downloaded
    from estnltk_neural.taggers.embeddings.bert.bert_transformer import BertTransformer
    bert_transformer = BertTransformer()
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    bert_transformer.tag(text)
    assert 'bert_word_embeddings' in text.layers
    assert 'bert_sentence_embeddings' in text.layers
    
    for embedding_span in text['bert_word_embeddings']:
        assert len(embedding_span.bert_token_embedding[0]) == 3072

    for embedding_span in text['bert_sentence_embeddings']:
        assert len(embedding_span.bert_sentence_embedding[0]) == 3072

