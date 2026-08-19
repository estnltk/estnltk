from importlib.util import find_spec
import pytest
import os

from packaging.version import Version as pkg_Version
from packaging.version import parse as parse_version

from estnltk import Text
from estnltk.downloader import get_resource_paths

# Try to get the resources path for BertTagger. If missing, do nothing. It's up for the user to download the missing resources
MODEL_PATH = get_resource_paths("berttagger", only_latest=True, download_missing=False)


def check_if_transformers_is_available():
    return find_spec("transformers") is not None


def check_if_pytorch_is_available():
    return find_spec("torch") is not None


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
                    reason="BertTagger's resources have not been downloaded. "+\
                           "Use estnltk.download('berttagger') to get the missing resources.")
def test_bert_tagger_out_of_the_box():
    # Test that BertTagger works "out_of_the_box" if resources have been downloaded
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    bert_tagger = BertTagger()
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    bert_tagger.tag(text)
    assert 'bert_embeddings' in text.layers
    assert not text.bert_embeddings.ambiguous
    for embedding_span in text.bert_embeddings:
        assert len(embedding_span.bert_embedding) == 3072


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="BertTagger's resources have not been downloaded. "+\
                           "Use estnltk.download('berttagger') to get the missing resources.")
def test_bert_tagger():
    # Test that BertTagger's different configurations
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    bert_tagger = BertTagger(bert_location=MODEL_PATH)
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    bert_tagger.tag(text)
    assert 'bert_embeddings' in text.layers
    assert not text.bert_embeddings.ambiguous

    for embedding_span in text.bert_embeddings:
        assert len(embedding_span.bert_embedding) == 3072

    bert_add_tagger = BertTagger(bert_location=MODEL_PATH, method='add',
                                 output_layer='bert_embeddings_add')
    bert_add_tagger.tag(text)
    assert 'bert_embeddings_add' in text.layers

    for embedding_span in text.bert_embeddings_add:
        assert len(embedding_span.bert_embedding) == 768

    bert_all_tagger = BertTagger(bert_location=MODEL_PATH, method='all',
                                 output_layer='bert_embeddings_all')
    bert_all_tagger.tag(text)
    assert 'bert_embeddings_all' in text.layers
    for embedding_span in text.bert_embeddings_all:
        assert len(embedding_span.bert_embedding) == 4
        assert len(embedding_span.bert_embedding[0]) == 768
        assert len(embedding_span.bert_embedding[1]) == 768
        assert len(embedding_span.bert_embedding[2]) == 768
        assert len(embedding_span.bert_embedding[3]) == 768

    bert_word_tagger = BertTagger(bert_location=MODEL_PATH, token_level=False,
                                  output_layer='bert_word_embeddings')
    bert_word_tagger.tag(text)

    assert 'bert_word_embeddings' in text.layers
    assert not text.bert_word_embeddings.ambiguous

    assert len(text.words) == len(text.bert_word_embeddings)
    for s1, s2 in zip(text.words, text.bert_word_embeddings):
        assert s1.start == s2.start
        assert s1.end == s2.end
        assert len(s2.bert_embedding) == 3072

    bert_word_tagger_concat = BertTagger(bert_location=MODEL_PATH, token_level=False, method='concatenate',
                                         output_layer='bert_word_embeddings_concat')
    bert_word_tagger_concat.tag(text)
    assert 'bert_word_embeddings_concat' in text.layers
    assert not text.bert_word_embeddings_concat.ambiguous

    for embedding_span in text.bert_word_embeddings_concat:
        assert len(embedding_span.bert_embedding) == 3072

    bert_word_tagger_add = BertTagger(bert_location=MODEL_PATH, token_level=False, method='add',
                                      output_layer='bert_word_embeddings_add')
    bert_word_tagger_add.tag(text)
    assert 'bert_word_embeddings_add' in text.layers
    assert not text.bert_word_embeddings_add.ambiguous
    for embedding_span in text.bert_word_embeddings_add:
        assert len(embedding_span.bert_embedding) == 768

    bert_diff_layer_tagger1 = BertTagger(bert_location=MODEL_PATH, bert_layers=[-1],
                                         output_layer='bert_diff_layers1_embeddings')
    bert_diff_layer_tagger1.tag(text)
    assert 'bert_diff_layers1_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers1_embeddings:
        assert len(embedding_span.bert_embedding) == 768

    bert_diff_layer_tagger2 = BertTagger(bert_location=MODEL_PATH, bert_layers=[-2, -1],
                                         output_layer='bert_diff_layers2_embeddings')
    bert_diff_layer_tagger2.tag(text)
    assert 'bert_diff_layers2_embeddings' in text.layers

    for embedding_span in text.bert_diff_layers2_embeddings:
        assert len(embedding_span.bert_embedding) == 1536

    text = Text(' '.join(['Tere ']*513))
    text.tag_layer('sentences')
    bert_long_seq_tagger = BertTagger(bert_location=MODEL_PATH, output_layer='bert_embeddings_long_seq')
    bert_long_seq_tagger.tag(text)
    assert 'bert_embeddings_long_seq' in text.layers

    for embedding_span in text.bert_embeddings_long_seq:
        assert len(embedding_span.bert_embedding) == 3072


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="BertTagger's resources have not been downloaded. "+\
                           "Use estnltk.download('berttagger') to get the missing resources.")
def test_bert_tagger_word_embeddings_all():
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    text = Text(
        'Ilus suur karvane kass nurrus punasel diivanil. Ta on ise tee esimesel poolel. Valge jänes jooksis metsa!')
    text.tag_layer('sentences')
    bert_word_tagger_all = BertTagger(bert_location=MODEL_PATH, token_level=False, method='all',
                                      output_layer='bert_word_embeddings_all')
    bert_word_tagger_all.tag(text)
    assert 'bert_word_embeddings_all' in text.layers
    assert text.bert_word_embeddings_all.ambiguous

    for embedding_span in text.bert_word_embeddings_all:
        tokens = embedding_span.token
        bert_embeddings = embedding_span.bert_embedding
        # At the first level, there should be a list containing an embeddings for each bert token
        assert len(bert_embeddings) == len(tokens)
        for emb in bert_embeddings:
            # At the second level, each token has 4 embedding vectors (all from the last 4 layers)
            assert len(emb) == 4
            # At the third level, each embedding vector should have length 768
            for e in emb:
                assert len(e) == 768

# Fetches pairs (word, bert_tokens) from BertTagger's output
def _get_bert_tokens(text_obj, bert_layer='bert_word_embeddings'):
    results = []
    for bert_span in text_obj[bert_layer]:
        results.append( (bert_span.text, list(bert_span.token)))
    return results

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="BertTagger's resources have not been downloaded. "+\
                           "Use estnltk.download('berttagger') to get the missing resources.")
def test_bert_tagger_tokens_and_word_span_misaligment_bugfix():
    # 1) Test BertTagger for handling misalignment of word spans and embedding tokens
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎☏??? Tema seepeale: ╳🔥!🔥!')

    # token level
    bert_tagger_1 = BertTagger(bert_location=MODEL_PATH, token_level=True)
    text.tag_layer('sentences')
    bert_tagger_1.tag(text)
    assert 'bert_embeddings' in text.layers
    for embedding_span in text.bert_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 

    # word level
    bert_tagger_2 = BertTagger(output_layer='bert_word_embeddings',
                                  bert_location=MODEL_PATH, token_level=False)
    bert_tagger_2.tag(text)
    assert 'bert_word_embeddings' in text.layers
    for embedding_span in text.bert_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.bert_word_embeddings.text == text.words.text
    
    # 2) Test BertTagger for handling … and ...
    text = Text('Ta säutsus: 😃💁?💁!💁💁? Mina vastu: ☎…??? ...! Tema seepeale: ╳🔥!🔥!')
    text.tag_layer('sentences')
    bert_tagger_2.tag(text)
    assert 'bert_word_embeddings' in text.layers
    for embedding_span in text.bert_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.bert_word_embeddings.text == text.words.text

    # 3) Test BertTagger for handling tokenized words with diacritics and lowercase
    text = Text('Hiljuti saime taas lugeda-kuulda , kuidas põhiseaduse muutmine tähtsustavat '+\
                'eesti keelt . “ “ Joone ” tegijad on olnud tublid ja pühendunud .')
    text.tag_layer('sentences')
    bert_tagger_2.tag(text)
    assert 'bert_word_embeddings' in text.layers
    for embedding_span in text.bert_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.bert_word_embeddings.text == text.words.text

    # 4) Test BertTagger for handling '\xad' and multiword tokens
    text = Text('Millenniumiprobleem : tõestada , et iga kompaktse lihtsa rühma G korral Yangi­Millsi '+\
                'kalibratsioonivälja kvantteooria muutkonnal R 4 eksisteerib ja tema massispektris on '+\
                'pilu > 0. Teda nimetatakse ka kalibratsiooniteisenduste rühmaks ja elektromagnetvälja '+\
                'nimetatakse U ( 1 ) ­kalibratsiooniväljaks . Paarkümmend aastat hiljem leiti , et '+\
                'Yangi­Millsi välja A μ ( x ) saab interpreteerida kui peakihtkonna P ( M , G ) seostuse '+\
                '1­vormi komponente lokaalsel lõikel . Källeni­Lehmanni teoreem väidab , et on olemas '+\
                'positiivne mõõt  ( m )  ...')
    text.tag_layer('sentences')
    bert_tagger_2.tag(text)
    assert 'bert_word_embeddings' in text.layers
    for embedding_span in text.bert_word_embeddings:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    assert text.bert_word_embeddings.text == text.words.text
    # 5) Check how partial overlaps between bert tokens and words are handled.
    #    Current logic: if a bert token can be associated with multiple words, 
    #    then associate it with all words;
    from transformers import __version__ as transformers_version
    partial_overlap1 = Text('Yangi­Millsi kalibratsioonivälja kvantteooria.').tag_layer('sentences')
    bert_tagger_2.tag(partial_overlap1)
    words_and_bert_tokens = _get_bert_tokens(partial_overlap1, bert_layer=bert_tagger_2.output_layer)
    if parse_version(transformers_version) < pkg_Version('5.0.0'):
        # transformers 4.x
        assert words_and_bert_tokens == \
            [('Yangi', ['y', '##angi']), 
             ('\xad', ['##mil']), 
             ('Millsi', ['##mil', '##ls', '##i']), 
             ('kalibratsioonivälja', ['kalib', '##ratsiooni', '##val', '##ja']), 
             ('kvantteooria', ['kvant', '##teooria']), 
             ('.', ['.'])]
    else:
        # transformers 5.x
        assert words_and_bert_tokens == \
            [('Yangi', ['Ya', '##ngi']), 
             ('\xad', ['##M']), 
             ('Millsi', ['##M', '##ill','##si']), 
             ('kalibratsioonivälja', ['kalib', '##ratsiooni', '##välja']), 
             ('kvantteooria', ['kvant', '##teooria']), 
             ('.', ['.'])]
    partial_overlap2 = Text('Ning Källeni­Lehmanni teoreem').tag_layer('sentences')
    bert_tagger_2.tag(partial_overlap2)
    words_and_bert_tokens = _get_bert_tokens(partial_overlap2, bert_layer=bert_tagger_2.output_layer)
    if parse_version(transformers_version) < pkg_Version('5.0.0'):
        # transformers 4.x
        assert words_and_bert_tokens == \
            [('Ning', ['ning']), 
             ('Källeni', ['kalle', '##nile']), 
             ('\xad', ['##nile']), 
             ('Lehmanni', ['##nile', '##hma', '##nni']), 
             ('teoreem', ['teoree', '##m'])]
    else:
        # transformers 5.x
        assert words_and_bert_tokens == \
            [('Ning', ['Nin', '##g']), 
             ('Källeni', ['Kä', '##lle', '##ni']), 
             ('\xad', ['##L']), 
             ('Lehmanni', ['##L', '##eh', '##manni']), 
             ('teoreem', ['teoree', '##m'])]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(not check_if_model_present(),
                    reason="BertTagger's resources have not been downloaded. "+\
                           "Use estnltk.download('berttagger') to get the missing resources.")
def test_bert_tagger_cyrillic_chars_problem_bugfix():
    # Test BertNerTagger on texts that contain substrings with cyrillic symbols 'е' and 'и'. 
    # Previous versions of the tagger crashed on these substrings with an error:
    #
    # ...\Lib\site-packages\torch\nn\modules\sparse.py:190: in forward
    #>       return torch.embedding(weight, input, padding_idx, scale_grad_by_freq, sparse)
    #E       IndexError: ('index out of range in self', "in the 'BertTagger'")
    #
    from estnltk_neural.taggers.embeddings.bert.bert_tagger import BertTagger
    from estnltk_neural.taggers.embeddings.bert.bert_patches import estbert_normalizer
    from transformers import __version__ as transformers_version
    text = Text('Jah, kuni ta 15 4е jala pikuseks saab. Kas kood oli 1и või Cи ?')
    text.tag_layer('sentences')
    # word level
    bert_tagger_2 = BertTagger(output_layer='bert_word_embeddings',
                               bert_location=MODEL_PATH, token_level=False)
    assert bert_tagger_2.input_normalizer == estbert_normalizer
    bert_tagger_2.tag(text)
    assert 'bert_word_embeddings' in text.layers
    for embedding_span in text['bert_word_embeddings']:
        assert len(embedding_span.bert_embedding) == 3072  # 768 * 4 
    words_and_bert_tokens = _get_bert_tokens(text, bert_layer=bert_tagger_2.output_layer)
    if parse_version(transformers_version) < pkg_Version('5.0.0'):
        # transformers 4.x
        assert words_and_bert_tokens == \
            [('Jah', ['jah']), (',', [',']), ('kuni', ['kuni']), ('ta', ['ta']), ('15', ['15']), 
             ('4е', ['4', '##e']), ('jala', ['jala']), ('pikuseks', ['piku', '##seks']), ('saab', ['saab']), 
             ('.', ['.']), 
             ('Kas', ['kas']), ('kood', ['kood']), ('oli', ['oli']), ('1и', ['1', '##i']), ('või', ['voi']), 
             ('Cи', ['c', '##i']), ('?', ['?'])]
    else:
        # transformers 5.x
        assert words_and_bert_tokens == \
            [('Jah', ['Ja', '##h']), (',', [',']), ('kuni', ['kuni']), ('ta', ['ta']), ('15', ['15']), 
             ('4е', ['4', '##e']), ('jala', ['jala']), ('pikuseks', ['piku', '##seks']), ('saab', ['saab']), 
             ('.', ['.']), 
             ('Kas', ['Kas']), ('kood', ['kood']), ('oli', ['oli']), ('1и', ['1', '##i']), ('või', ['või']), 
             ('Cи', ['Ci']), ('?', ['?'])]
