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


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(ESTROBERTA_PATH is None,
                    reason="RobertaTagger's model location not known. "+\
                           "Set environment variable ESTROBERTA_PATH to model's local directory.")
def test_roberta_tagger_tokens_and_word_span_misaligment_bugfix():
    # 1) Test RobertaTagger for handling misalignment of word spans and embedding tokens
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎☏??? Tema seepeale: ╳🔥!🔥!')

    # token level
    roberta_tagger_1 = RobertaTagger(bert_location=ESTROBERTA_PATH, token_level=True)
    text.tag_layer('sentences')
    roberta_tagger_1.tag(text)
    assert 'roberta_embeddings' in text.layers
    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 

    # word level
    roberta_tagger_2 = RobertaTagger(output_layer='roberta_word_embeddings',
                                     bert_location=ESTROBERTA_PATH, token_level=False)
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text
    
    # 2) Test RobertaTagger for handling … and ... replacements
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎…??? ...! Tema seepeale: ╳🔥!🔥!')
    text.tag_layer('sentences')
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text
    
    # 3) Test RobertaTagger for handling tokens where starting ▁ is separated from
    #    the first token of the word, such as in 'iaido' -> ['▁', 'ia', 'ido']
    text = Text('Sobudo on täielik võitluskunstide süsteem , mis koosneb erinevatest aladest sh : '+\
                'jodo , aikido , iaido ja jukempo . Tema seepeale: ╳🔥!🔥!')
    text.tag_layer('sentences')
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding[0]) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text