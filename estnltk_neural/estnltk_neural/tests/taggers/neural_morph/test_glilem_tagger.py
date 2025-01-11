from importlib.util import find_spec
import pytest
import os

from estnltk import Text
from estnltk.downloader import get_resource_paths

from estnltk.converters import layer_to_dict 
from estnltk.converters import dict_to_layer 

from estnltk_neural.taggers import GliLemTagger

def check_if_transformers_is_available():
    return find_spec("transformers") is not None

def check_if_gliner_is_available():
    return find_spec("gliner") is not None

# Try to get the resources path for GliLemTagger's model. If missing, do nothing. It's up for the user to download the missing resources
GLILEM_MODEL_PATH = get_resource_paths("glilem_vabamorf_disambiguator", only_latest=True, download_missing=False)

def _round_up_probabilities(layer_dict):
    assert 'spans' in layer_dict.keys()
    for span_dict in layer_dict['spans']:
        for anno in span_dict['annotations']:
            if anno['score'] is not None:
                anno['score'] = round(anno['score'], 2)
    return layer_dict

def _extract_glilem_annotations(glilem_layer, add_probs=False, round_probs=False):
    results = []
    layer_attributes = glilem_layer.attributes
    for span in glilem_layer:
        for annotation in span.annotations:
            entry = {'word': span.text}
            for attribute in layer_attributes:
                if attribute == 'score':
                    continue
                entry[attribute] = annotation[attribute]
            if add_probs:
                entry['score'] = annotation['score']
                if round_probs and entry['score'] is not None:
                    entry['score'] = round(entry['score'], 2)
            results.append(entry)
    return results

def _extract_word_partofspeech_and_form(morph_layer):
    results = []
    for span in morph_layer:
        for annotation in span.annotations:
            entry = {'word': span.text}
            if 'lemma' in morph_layer.attributes:
                entry['lemma'] = annotation['lemma']
            if 'partofspeech' in morph_layer.attributes:
                entry['partofspeech'] = annotation['partofspeech']
            if 'form' in morph_layer.attributes:
                entry['form'] = annotation['form']
            results.append(entry)
    return results


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_gliner_is_available(),
                    reason="package gliner is required for this test")
@pytest.mark.skipif(GLILEM_MODEL_PATH is None,
                    reason="GliLemTagger's model location not known. "+\
                           "Use estnltk.download('glilem') to get the missing resources.")
def test_glilem_tagger_out_of_the_box():
    # Case 1: Test that GliLemTagger works "out_of_the_box" if the model is available
    glilem = GliLemTagger(missing_lemmas_strategy='vabamorf_lemmas')
    text = Text('Puuotsast kukkunud õun igatses tagasi. '+\
                'Kolletunud naeris saagis rediseid. ').tag_layer( glilem.input_layers )
    glilem.tag(text)
    output_layer = glilem.output_layer
    #from pprint import pprint
    #pprint( _round_up_probabilities( layer_to_dict(text[output_layer])) )
    # Validate results
    assert output_layer in text.layers
    assert _extract_glilem_annotations(text[output_layer]) == \
        [{'word': 'Puuotsast', 'lemma': 'puuots', 'label': '↓0;d¦---', 'vabamorf_overwritten': True, 'is_input_token': True}, 
         {'word': 'kukkunud', 'lemma': 'kukkuma', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'kukkunud', 'lemma': 'kukkunu', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'kukkunud', 'lemma': 'kukkunud', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'õun', 'lemma': 'õun', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'igatses', 'lemma': 'igatsema', 'label': '↓0;d¦-+m+a', 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'tagasi', 'lemma': 'tagasi', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': '.', 'lemma': '.', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': 'Kolletunud', 'lemma': 'kolletunud', 'label': '↓0;d¦', 'vabamorf_overwritten': True, 'is_input_token': True}, 
         {'word': 'naeris', 'lemma': 'naeri', 'label': '↓0;d¦-', 'vabamorf_overwritten': True, 'is_input_token': True}, 
         {'word': 'saagis', 'lemma': 'saak', 'label': '↓0;d¦---+k', 'vabamorf_overwritten': True, 'is_input_token': True}, 
         {'word': 'rediseid', 'lemma': 'redis', 'label': '↓0;d¦---', 'vabamorf_overwritten': False, 'is_input_token': True}, 
         {'word': '.', 'lemma': '.', 'label': None, 'vabamorf_overwritten': False, 'is_input_token': True}]


@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_gliner_is_available(),
                    reason="package gliner is required for this test")
@pytest.mark.skipif(GLILEM_MODEL_PATH is None,
                    reason="GliLemTagger's model location not known. "+\
                           "Use estnltk.download('glilem') to get the missing resources.")
def test_glilem_tagger_as_disambiguator():
    # Case: Test that GliLemTagger can be used as a disamiguator of morph_analysis layer
    from estnltk.taggers import VabamorfAnalyzer
    vm_analyser = VabamorfAnalyzer()
    glilem = GliLemTagger(output_layer='morph_analysis', disambiguate=True, missing_lemmas_strategy='discard')
    # Case 1
    text = Text("Lae äpp kohe alla!")
    # Tag layers required by morph analysis
    text.tag_layer(['words', 'sentences'])
    vm_analyser.tag( text )
    amb_results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer])
    #print(amb_results)
    assert amb_results == \
       [{'word': 'Lae', 'lemma': 'Laad', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'lemma': 'Lae', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'lemma': 'Lae', 'partofspeech': 'H', 'form': 'sg n'}, 
        {'word': 'Lae', 'lemma': 'Lagi', 'partofspeech': 'H', 'form': 'sg g'}, 
        {'word': 'Lae', 'lemma': 'laad', 'partofspeech': 'S', 'form': 'sg g'}, 
        {'word': 'Lae', 'lemma': 'laadima', 'partofspeech': 'V', 'form': 'o'}, 
        {'word': 'Lae', 'lemma': 'lagi', 'partofspeech': 'S', 'form': 'sg g'}, 
        {'word': 'äpp', 'lemma': 'äpp', 'partofspeech': 'S', 'form': 'sg n'}, 
        {'word': 'kohe', 'lemma': 'kohe', 'partofspeech': 'A', 'form': 'sg n'}, 
        {'word': 'kohe', 'lemma': 'kohe', 'partofspeech': 'D', 'form': ''}, 
        {'word': 'alla', 'lemma': 'alla', 'partofspeech': 'D', 'form': ''}, 
        {'word': 'alla', 'lemma': 'alla', 'partofspeech': 'K', 'form': ''}, 
        {'word': '!', 'lemma': '!', 'partofspeech': 'Z', 'form': ''}]
    # Apply disambiguation
    glilem.retag(text)
    # Validate results
    results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer])
    #print(results)
    assert results == \
        [{'word': 'Lae', 'lemma': 'laadima', 'partofspeech': 'V', 'form': 'o'}, 
         {'word': 'äpp', 'lemma': 'äpp', 'partofspeech': 'S', 'form': 'sg n'}, 
         {'word': 'kohe', 'lemma': 'kohe', 'partofspeech': 'A', 'form': 'sg n'}, 
         {'word': 'kohe', 'lemma': 'kohe', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'alla', 'lemma': 'alla', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'alla', 'lemma': 'alla', 'partofspeech': 'K', 'form': ''}, 
         {'word': '!', 'lemma': '!', 'partofspeech': 'Z', 'form': ''}]

    # Case 2
    text = Text("Meie teod räägivad nüüd enda eest.")
    # Tag layers required by morph analysis
    text.tag_layer(['words', 'sentences'])
    vm_analyser.tag( text )
    amb_results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer])
    #print(amb_results)
    assert amb_results == \
        [{'word': 'Meie', 'lemma': 'mina', 'partofspeech': 'P', 'form': 'pl g'}, 
         {'word': 'Meie', 'lemma': 'mina', 'partofspeech': 'P', 'form': 'pl n'}, 
         {'word': 'teod', 'lemma': 'tegu', 'partofspeech': 'S', 'form': 'pl n'}, 
         {'word': 'teod', 'lemma': 'tigu', 'partofspeech': 'S', 'form': 'pl n'}, 
         {'word': 'räägivad', 'lemma': 'rääkima', 'partofspeech': 'V', 'form': 'vad'}, 
         {'word': 'nüüd', 'lemma': 'nüüd', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'enda', 'lemma': 'ise', 'partofspeech': 'P', 'form': 'sg g'}, 
         {'word': 'eest', 'lemma': 'eest', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'eest', 'lemma': 'eest', 'partofspeech': 'K', 'form': ''}, 
         {'word': 'eest', 'lemma': 'esi', 'partofspeech': 'S', 'form': 'sg el'}, 
         {'word': '.', 'lemma': '.', 'partofspeech': 'Z', 'form': ''}]
    # Apply disambiguation
    glilem.retag(text)
    # Validate results
    results = _extract_word_partofspeech_and_form(text[vm_analyser.output_layer])
    #print(results)
    assert results == \
        [{'word': 'Meie', 'lemma': 'mina', 'partofspeech': 'P', 'form': 'pl g'}, 
         {'word': 'Meie', 'lemma': 'mina', 'partofspeech': 'P', 'form': 'pl n'}, 
         {'word': 'teod', 'lemma': 'tegu', 'partofspeech': 'S', 'form': 'pl n'}, 
         {'word': 'räägivad', 'lemma': 'rääkima', 'partofspeech': 'V', 'form': 'vad'}, 
         {'word': 'nüüd', 'lemma': 'nüüd', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'enda', 'lemma': 'ise', 'partofspeech': 'P', 'form': 'sg g'}, 
         {'word': 'eest', 'lemma': 'eest', 'partofspeech': 'D', 'form': ''}, 
         {'word': 'eest', 'lemma': 'eest', 'partofspeech': 'K', 'form': ''}, 
         {'word': 'eest', 'lemma': 'esi', 'partofspeech': 'S', 'form': 'sg el'}, 
         {'word': '.', 'lemma': '.', 'partofspeech': 'Z', 'form': ''}]

