import pkgutil
import pytest
from estnltk import Text
import os


def check_if_transformers_is_available():
    return pkgutil.find_loader("transformers") is not None

def check_if_pytorch_is_available():
    return pkgutil.find_loader("torch") is not None

ESTROBERTA_PATH = os.environ.get('ESTROBERTA_PATH', None)


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTROBERTA_PATH is None,
                    reason="RobertaTagger's model location not known. "+\
                           "Set environment variable ESTROBERTA_PATH to model's local directory.")
def test_roberta_tagger_out_of_the_box():
    # Test that RobertaTagger works "out_of_the_box" if model is available
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    roberta_tagger = RobertaTagger(bert_location=ESTROBERTA_PATH)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    roberta_tagger.tag(text)
    assert 'roberta_embeddings' in text.layers

    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 

    assert len(text.words) < len(text.roberta_embeddings)


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTROBERTA_PATH is None,
                    reason="RobertaTagger's model location not known. "+\
                           "Set environment variable ESTROBERTA_PATH to model's local directory.")
def test_roberta_tagger_word_level_smoke():
    # Test that RobertaTagger works on word level
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    roberta_tagger = RobertaTagger(bert_location=ESTROBERTA_PATH, token_level=False)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa, ütles KabernaakelHiks.')
    text.tag_layer('sentences')
    roberta_tagger.tag(text)
    assert 'roberta_embeddings' in text.layers

    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 

    assert text.roberta_embeddings.text == text.words.text
