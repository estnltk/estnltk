from importlib.util import find_spec
import pytest
import os

from estnltk import Text
from estnltk.downloader import get_resource_paths

from estnltk.converters import layer_to_dict 
from estnltk.converters import dict_to_layer 

def check_if_transformers_is_available():
    return find_spec("transformers") is not None

def check_if_pytorch_is_available():
    return find_spec("torch") is not None

# Try to get the resources path for BertMorphTagger's model v1. If missing, do nothing. It's up for the user to download the missing resources
BERTMORPH_V1_PATH = get_resource_paths("bert_morph_tagging", only_latest=True, download_missing=False)


def _round_up_probabilities(layer_dict):
    assert 'spans' in layer_dict.keys()
    for span_dict in layer_dict['spans']:
        for anno in span_dict['annotations']:
            anno['probability'] = round(anno['probability'], 2)
    return layer_dict

def _extract_word_partofspeech_and_form(morph_layer, add_probs=False, round_probs=False):
    results = []
    for span in morph_layer:
        for annotation in span.annotations:
            entry = {'word': span.text}
            if 'morph_label' in morph_layer.attributes:
                entry['morph_label'] = annotation['morph_label']
            if 'partofspeech' in morph_layer.attributes:
                entry['partofspeech'] = annotation['partofspeech']
            if 'form' in morph_layer.attributes:
                entry['form'] = annotation['form']
            if add_probs:
                entry['probability'] = annotation['probability']
                if round_probs:
                    entry['probability'] = round(entry['probability'], 2)
            results.append(entry)
    return results

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(BERTMORPH_V1_PATH is None,
                    reason="BertMorphTagger's model location not known. "+\
                           "Use estnltk.download('bert_morph_tagging') to get the missing resources.")
def test_bert_morph_v1_out_of_the_box():
    # Case 1: Test that BertMorphTagger works "out_of_the_box" if model v1 is available
    from estnltk_neural.taggers import BertMorphTagger
    bert_morph_tagger = BertMorphTagger()
    text = Text('A. H. Tammsaare oli eesti kirjanik, esseist, kultuurifilosoof ja tõlkija. '+\
                'Üksnes autorihüvitis oli 12 431 krooni. ').tag_layer(['words', 'sentences'])
    bert_morph_tagger.tag(text)
    output_layer = bert_morph_tagger.output_layer
    #from pprint import pprint
    #pprint( _round_up_probabilities( layer_to_dict(text[output_layer])) )
    # Validate results
    assert output_layer in text.layers
    results = _extract_word_partofspeech_and_form(text[output_layer], add_probs=False)
    assert results == \
        [{'form': 'sg n', 'partofspeech': 'H', 'word': 'A. H. Tammsaare'},
         {'form': 's', 'partofspeech': 'V', 'word': 'oli'},
         {'form': '', 'partofspeech': 'G', 'word': 'eesti'},
         {'form': 'sg n', 'partofspeech': 'S', 'word': 'kirjanik'},
         {'form': '', 'partofspeech': 'Z', 'word': ','},
         {'form': 'sg n', 'partofspeech': 'S', 'word': 'esseist'},
         {'form': '', 'partofspeech': 'Z', 'word': ','},
         {'form': 'sg n', 'partofspeech': 'S', 'word': 'kultuurifilosoof'},
         {'form': '', 'partofspeech': 'J', 'word': 'ja'},
         {'form': 'sg n', 'partofspeech': 'S', 'word': 'tõlkija'},
         {'form': '', 'partofspeech': 'Z', 'word': '.'},
         {'form': '', 'partofspeech': 'D', 'word': 'Üksnes'},
         {'form': 'sg n', 'partofspeech': 'S', 'word': 'autorihüvitis'},
         {'form': 's', 'partofspeech': 'V', 'word': 'oli'},
         {'form': '?', 'partofspeech': 'N', 'word': '12 431'},
         {'form': 'sg p', 'partofspeech': 'S', 'word': 'krooni'},
         {'form': '', 'partofspeech': 'Z', 'word': '.'}]

    # Case 2: Test BertMorphTagger with original labels, do not split morph labels
    bert_morph_tagger_2 = BertMorphTagger(output_layer='bert_morph_2', split_pos_form=False)
    bert_morph_tagger_2.tag(text)
    output_layer = bert_morph_tagger_2.output_layer
    #from pprint import pprint
    #pprint( _round_up_probabilities( layer_to_dict(text[output_layer])) )
    # Validate results
    assert output_layer in text.layers
    results = _extract_word_partofspeech_and_form(text[output_layer], add_probs=False)
    assert results == \
        [{'word': 'A. H. Tammsaare', 'morph_label': 'sg n_H'}, 
         {'word': 'oli', 'morph_label': 's_V'}, 
         {'word': 'eesti', 'morph_label': 'G'}, 
         {'word': 'kirjanik', 'morph_label': 'sg n_S'}, 
         {'word': ',',  'morph_label': 'Z'}, 
         {'word': 'esseist', 'morph_label': 'sg n_S'}, 
         {'word': ',', 'morph_label': 'Z'}, 
         {'word': 'kultuurifilosoof', 'morph_label': 'sg n_S'}, 
         {'word': 'ja', 'morph_label': 'J'}, 
         {'word': 'tõlkija', 'morph_label': 'sg n_S'}, 
         {'word': '.', 'morph_label': 'Z'}, 
         {'word': 'Üksnes', 'morph_label': 'D'}, 
         {'word': 'autorihüvitis', 'morph_label': 'sg n_S'}, 
         {'word': 'oli', 'morph_label': 's_V'}, 
         {'word': '12 431', 'morph_label': '?_N'}, 
         {'word': 'krooni', 'morph_label': 'sg p_S'}, 
         {'word': '.', 'morph_label': 'Z'}]

    # Case 3: apply same tagger on another text
    text = Text('Autojuhi lapitekk pälvis linna kodukal palju teenimatut tähelepanu. ')
    text.tag_layer(['words', 'sentences'])
    bert_morph_tagger_2.tag(text)
    # Validate results
    assert output_layer in text.layers
    results = _extract_word_partofspeech_and_form(text[output_layer], add_probs=False)
    assert results == \
        [{'word': 'Autojuhi', 'morph_label': 'sg g_S'}, 
         {'word': 'lapitekk', 'morph_label': 'sg n_S'}, 
         {'word': 'pälvis', 'morph_label': 's_V'}, 
         {'word': 'linna', 'morph_label': 'sg g_S'}, 
         {'word': 'kodukal', 'morph_label': 'sg ad_S'}, 
         {'word': 'palju', 'morph_label': 'D'}, 
         {'word': 'teenimatut', 'morph_label': 'sg p_A'}, 
         {'word': 'tähelepanu', 'morph_label': 'sg p_S'}, 
         {'word': '.', 'morph_label': 'Z'}]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(BERTMORPH_V1_PATH is None,
                    reason="BertMorphTagger's model location not known. "+\
                           "Use estnltk.download('bert_morph_tagging') to get the missing resources.")
def test_bert_morph_disambiguator_v1_out_of_the_box():
    # Case 1: Test that BertMorphTagger works "out_of_the_box" as a disambiguator if model v1 is available
    from estnltk.taggers import VabamorfAnalyzer
    from estnltk_neural.taggers import BertMorphTagger
    vm_analyser = VabamorfAnalyzer()
    bert_morph_disambiguator = BertMorphTagger(output_layer=vm_analyser.output_layer, disambiguate=True)
    # Case 1
    text = Text("Lae äpp kohe alla!")
    # Tag layers required by morph analysis
    text.tag_layer(['words', 'sentences'])
    vm_analyser.tag( text )
    amb_results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer], add_probs=False)
    #print(amb_results)
    assert amb_results == \
       [{'word': 'Lae', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'partofspeech': 'H', 'form': 'sg n'}, 
        {'word': 'Lae', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'partofspeech': 'S', 'form': 'sg g'}, 
        {'word': 'Lae', 'partofspeech': 'V', 'form': 'o'}, 
        {'word': 'Lae', 'partofspeech': 'S', 'form': 'sg g'}, 
        {'word': 'äpp', 'partofspeech': 'S', 'form': 'sg n'}, 
        {'word': 'kohe', 'partofspeech': 'A', 'form': 'sg n'}, 
        {'word': 'kohe', 'partofspeech': 'D', 'form': ''}, 
        {'word': 'alla', 'partofspeech': 'D', 'form': ''}, 
        {'word': 'alla', 'partofspeech': 'K', 'form': ''}, 
        {'word': '!', 'partofspeech': 'Z', 'form': ''}]
    # Apply disambiguation
    bert_morph_disambiguator.retag( text )
    # Validate results
    results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer], add_probs=False)
    #print(results)
    assert results == \
        [{'word': 'Lae', 'partofspeech': 'V', 'form': 'o'}, 
         {'word': 'äpp', 'partofspeech': 'S', 'form': 'sg n'}, 
         {'word': 'kohe', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'alla', 'partofspeech': 'D', 'form': ''}, 
         {'word': '!', 'partofspeech': 'Z', 'form': ''}]

