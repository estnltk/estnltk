from importlib.util import find_spec
import pytest
import os

from estnltk import Text
from estnltk.downloader import get_resource_paths

from estnltk.converters import layer_to_records

from estnltk.converters import layer_to_dict 
from estnltk.converters import dict_to_layer 

def _sort_morph_analysis_records( morph_analysis_records:list ):
    '''Sorts sublists (lists of analyses of a single word) of 
       morph_analysis_records. Sorting is required for comparing
       morph analyses of a word without setting any constraints 
       on their specific order. '''
    for wrid, word_records_list in enumerate( morph_analysis_records ):
        sorted_records = sorted( word_records_list, key = lambda x : \
            str(x['root'])+str(x['ending'])+str(x['clitic'])+\
            str(x['partofspeech'])+str(x['form']) )
        morph_analysis_records[wrid] = sorted_records

def check_if_transformers_is_available():
    return find_spec("transformers") is not None

def check_if_pytorch_is_available():
    return find_spec("torch") is not None

# Try to get the resources path for BertMorphTagger's model v2. If missing, do nothing. It's up for the user to download the missing resources
BERTMORPH_V2_PATH = get_resource_paths("bert_morph_v2", only_latest=True, download_missing=False)

@pytest.mark.skipif(not check_if_transformers_is_available(),
                    reason="package tranformers is required for this test")
@pytest.mark.skipif(not check_if_pytorch_is_available(),
                    reason="package pytorch is required for this test")
@pytest.mark.skipif(BERTMORPH_V2_PATH is None,
                    reason="VabamorfWithBertTagger's model location not known. "+\
                           "Use estnltk.download('bert_morph_v2') to get the missing resources.")
def test_vabamorf_with_bert_morph_v2_out_of_the_box():
    # Case 1: Test that BertMorphTagger v2 works "out_of_the_box" if the model is available
    from estnltk_neural.taggers import VabamorfWithBertTagger
    vm_bert_morph_tagger_v2 = VabamorfWithBertTagger()
    text = Text('Küll nad on targad. Mis te õitsete, seltsimehed? '+\
                'kommenteeris 5. sajandil elanud munk. ').tag_layer(['compound_tokens', 'words', 'sentences'])
    vm_bert_morph_tagger_v2.tag(text)
    output_layer = vm_bert_morph_tagger_v2.output_layer
    #from pprint import pprint
    #pprint( layer_to_dict(text[vm_bert_morph_tagger_v2.output_layer]) )
    # Validate results
    assert output_layer in text.layers
    expected_records = \
        [[{'normalized_text': 'Küll', 'lemma': 'küll', 'root': 'küll', 'root_tokens': ['küll'], 'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'D', 'start': 0, 'end': 4}], 
         [{'normalized_text': 'nad', 'lemma': 'tema', 'root': 'tema', 'root_tokens': ['tema'], 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'P', 'start': 5, 'end': 8}], 
         [{'normalized_text': 'on', 'lemma': 'olema', 'root': 'ole', 'root_tokens': ['ole'], 'ending': '0', 'clitic': '', 'form': 'vad', 'partofspeech': 'V', 'start': 9, 'end': 11}], 
         [{'normalized_text': 'targad', 'lemma': 'tark', 'root': 'tark', 'root_tokens': ['tark'], 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'A', 'start': 12, 'end': 18}], 
         [{'normalized_text': '.', 'lemma': '.', 'root': '.', 'root_tokens': ['.'], 'ending': '', 'clitic': '', 'form': '', 'partofspeech': 'Z', 'start': 18, 'end': 19}], 
         [{'normalized_text': 'Mis', 'lemma': 'mis', 'root': 'mis', 'root_tokens': ['mis'], 'ending': '0', 'clitic': '', 'form': 'pl n', 'partofspeech': 'P', 'start': 20, 'end': 23}], 
         [{'normalized_text': 'te', 'lemma': 'sina', 'root': 'sina', 'root_tokens': ['sina'], 'ending': '0', 'clitic': '', 'form': 'pl n', 'partofspeech': 'P', 'start': 24, 'end': 26}], 
         [{'normalized_text': 'õitsete', 'lemma': 'õitsema', 'root': 'õitse', 'root_tokens': ['õitse'], 'ending': 'te', 'clitic': '', 'form': 'te', 'partofspeech': 'V', 'start': 27, 'end': 34}], 
         [{'normalized_text': ',', 'lemma': ',', 'root': ',', 'root_tokens': [','], 'ending': '', 'clitic': '', 'form': '', 'partofspeech': 'Z', 'start': 34, 'end': 35}], 
         [{'normalized_text': 'seltsimehed', 'lemma': 'seltsimees', 'root': 'seltsi_mees', 'root_tokens': ['seltsi', 'mees'], 'ending': 'd', 'clitic': '', 'form': 'pl n', 'partofspeech': 'S', 'start': 36, 'end': 47}], 
         [{'normalized_text': '?', 'lemma': '?', 'root': '?', 'root_tokens': ['?'], 'ending': '', 'clitic': '', 'form': '', 'partofspeech': 'Z', 'start': 47, 'end': 48}], 
         [{'normalized_text': 'kommenteeris', 'lemma': 'kommenteerima', 'root': 'kommenteeri', 'root_tokens': ['kommenteeri'], 'ending': 's', 'clitic': '', 'form': 's', 'partofspeech': 'V', 'start': 49, 'end': 61}], 
         [{'normalized_text': '5.', 'lemma': '5.', 'root': '5.', 'root_tokens': ['5.'], 'ending': '0', 'clitic': '', 'form': '?', 'partofspeech': 'O', 'start': 62, 'end': 64}], 
         [{'normalized_text': 'sajandil', 'lemma': 'sajand', 'root': 'sajand', 'root_tokens': ['sajand'], 'ending': 'l', 'clitic': '', 'form': 'sg ad', 'partofspeech': 'S', 'start': 65, 'end': 73}], 
         [{'normalized_text': 'elanud', 'lemma': 'elanud', 'root': 'ela=nud', 'root_tokens': ['elanud'], 'ending': '0', 'clitic': '', 'form': '', 'partofspeech': 'A', 'start': 74, 'end': 80}], 
         [{'normalized_text': 'munk', 'lemma': 'munk', 'root': 'munk', 'root_tokens': ['munk'], 'ending': '0', 'clitic': '', 'form': 'sg n', 'partofspeech': 'S', 'start': 81, 'end': 85}], 
         [{'normalized_text': '.', 'lemma': '.', 'root': '.', 'root_tokens': ['.'], 'ending': '', 'clitic': '', 'form': '', 'partofspeech': 'Z', 'start': 85, 'end': 86}]]
    
    # Sort analyses (so that the order within a word is always the same)
    results_dict = layer_to_records( text[output_layer] )
    _sort_morph_analysis_records( results_dict )
    #print(results_dict)
    _sort_morph_analysis_records( expected_records )
    
    # Check results
    assert expected_records == results_dict


