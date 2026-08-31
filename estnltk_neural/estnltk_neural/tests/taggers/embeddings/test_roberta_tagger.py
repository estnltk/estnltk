from importlib.util import find_spec
import pytest
import os

from estnltk import Text
from estnltk_neural.common import check_if_hf_repo_is_available


def check_if_transformers_is_available():
    return find_spec("transformers") is not None

def check_if_pytorch_is_available():
    return find_spec("torch") is not None


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_hf_repo_is_available('EMBEDDIA/est-roberta'),
                    reason="RobertaTagger's model (EMBEDDIA/est-roberta) is not available. "+\
                           "Please download the model via huggingface_hub.snapshot_download('EMBEDDIA/est-roberta').")
def test_roberta_tagger_out_of_the_box():
    # Test that RobertaTagger works "out_of_the_box" if model is available
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    roberta_tagger = RobertaTagger()
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    roberta_tagger.tag(text)
    assert 'roberta_embeddings' in text.layers
    assert not text.roberta_embeddings.ambiguous

    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 

    assert len(text.words) < len(text.roberta_embeddings)


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_hf_repo_is_available('EMBEDDIA/est-roberta'),
                    reason="RobertaTagger's model (EMBEDDIA/est-roberta) is not available. "+\
                           "Please download the model via huggingface_hub.snapshot_download('EMBEDDIA/est-roberta').")
def test_roberta_tagger_word_level_smoke():
    # Test that RobertaTagger works on word level
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    roberta_tagger = RobertaTagger(token_level=False)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa, ütles KabernaakelHiks.')
    text.tag_layer('sentences')
    roberta_tagger.tag(text)
    assert 'roberta_embeddings' in text.layers
    assert not text.roberta_embeddings.ambiguous

    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 

    assert text.roberta_embeddings.text == text.words.text

# Fetches pairs (word, bert_tokens) from RobertaTagger's output
def _get_bert_tokens(text_obj, bert_layer='roberta_word_embeddings'):
    results = []
    for bert_span in text_obj[bert_layer]:
        results.append( (bert_span.text, list(bert_span.token)))
    return results

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_hf_repo_is_available('EMBEDDIA/est-roberta'),
                    reason="RobertaTagger's model (EMBEDDIA/est-roberta) is not available. "+\
                           "Please download the model via huggingface_hub.snapshot_download('EMBEDDIA/est-roberta').")
def test_roberta_tagger_tokens_and_word_span_misaligment_bugfix():
    # 1) Test RobertaTagger for handling misalignment of word spans and embedding tokens
    from estnltk_neural.taggers.embeddings.bert.roberta_tagger import RobertaTagger
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎☏??? Tema seepeale: ╳🔥!🔥!')

    # token level
    roberta_tagger_1 = RobertaTagger(token_level=True)
    text.tag_layer('sentences')
    roberta_tagger_1.tag(text)
    assert 'roberta_embeddings' in text.layers
    for embedding_span in text.roberta_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 

    # word level
    roberta_tagger_2 = RobertaTagger(output_layer='roberta_word_embeddings',
                                     token_level=False)
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text
    
    # 2) Test RobertaTagger for handling … and ... replacements
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎…??? ...! Tema seepeale: ╳🔥!🔥!')
    text.tag_layer('sentences')
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text
    
    # 3) Test RobertaTagger for handling tokens where starting ▁ is separated from
    #    the first token of the word, such as in 'iaido' -> ['▁', 'ia', 'ido']
    text = Text('Sobudo on täielik võitluskunstide süsteem , mis koosneb erinevatest aladest sh : '+\
                'jodo , aikido , iaido ja jukempo . Tema seepeale: ╳🔥!🔥!')
    text.tag_layer('sentences')
    roberta_tagger_2.tag(text)
    assert 'roberta_word_embeddings' in text.layers
    for embedding_span in text.roberta_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.roberta_word_embeddings.text == text.words.text

    # 4) Test handling inputs that have '\xad' and/or '…' symbol.
    partial_overlap1 = Text('Yangi­Millsi kalibratsioonivälja kvantteooria …?').tag_layer('sentences')
    roberta_tagger_2.tag(partial_overlap1)
    words_and_bert_tokens = _get_bert_tokens(partial_overlap1, bert_layer=roberta_tagger_2.output_layer)
    assert words_and_bert_tokens == \
        [('Yangi', ['▁Y', 'angi']), 
         ('\xad', ['\xad']), 
         ('Millsi', ['M', 'ill', 'si']), 
         ('kalibratsioonivälja', ['▁kal', 'ib', 'ratsiooni', 'välja']), 
         ('kvantteooria', ['▁kvant', 'teooria']), 
         ('…?', ['▁...', '?'])]
    partial_overlap2 = Text('Ning Källeni­Lehmanni teoreem').tag_layer('sentences')
    roberta_tagger_2.tag(partial_overlap2)
    words_and_bert_tokens = _get_bert_tokens(partial_overlap2, bert_layer=roberta_tagger_2.output_layer)
    assert words_and_bert_tokens == \
        [('Ning', ['▁Ning']), 
         ('Källeni', ['▁Kä', 'lle', 'ni']), 
         ('\xad', ['\xad']), 
         ('Lehmanni', ['Le', 'hma', 'nni']), 
         ('teoreem', ['▁te', 'or', 'eem'])]

