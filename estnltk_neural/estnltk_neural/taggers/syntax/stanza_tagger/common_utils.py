#
#  Common utility functions used by both StanzaSyntaxTagger and StanzaSyntaxEnsembleTagger
#

from typing import MutableMapping, List, Tuple

import os
from collections import OrderedDict
from random import Random

def prepare_input_doc(layers: MutableMapping[str, 'Layer'], sentences:str, morph_analysis:str, 
                      only_tokenization:bool=False, remove_fields: List[str]=None, 
                      replace_fields: Tuple[List[str], str]=None, random_picker:Random=None):
    '''
    Prepares input document for StanzaSyntax(Ensemble)Tagger. 
    Based on given sentences and morph_analysis layers, constructs a list of 
    sentences, where each sentence consists of list of word dictionaries, each 
    of which defines conllu fields {'id', 'lemma', 'upostag', 'xpostag', 
    'feats', 'misc', 'deps'} for a word.
    
    If remove_fields is defined, replaces all values of given conllu fields 
    with '_'.
    If replace_fields is defined (Tuple[list, str]), the replaces values of 
    all listed conllu fields (replace_fields[0]) with given string 
    (replace_fields[1]). 
    
    (By default) Returns list of lists of dicts, which can be used as a basis 
    for creation of stanza.models.common.doc.Document.
    
    If only_tokenization==True, then collects only sentence/word tokenization 
    and discards words' morphological features (conllu dictionaries). In that 
    case, returns list of lists of strings, which can be used as an input for 
    stanza.Pipeline.
    '''
    if random_picker is None and not only_tokenization:
        random_picker = Random()
    assert isinstance(layers, dict)
    assert sentences in layers.keys(), '(!) Missing {!r} layer'.format(sentences)
    assert only_tokenization or \
        morph_analysis in layers.keys(), '(!) Missing {!r} layer'.format(morph_analysis)
    data = []
    global_word_id = 0
    for sentence in layers[sentences]:
        sentence_analyses = []
        if only_tokenization:
            # Collect only sentence tokenization
            sentence_analyses = sentence.text
        else:
            # Collect sentence tokenization & morph features
            for wid, word_base_span in enumerate(sentence.base_span):
                # Get morph analysis of the word
                morph_word = layers[morph_analysis][global_word_id]
                assert word_base_span == morph_word.base_span
                # Pick an annotation randomly
                annotation = random_picker.choice(morph_word.annotations)
                # Construct feats
                feats = ''
                if annotation['form']:
                    feats = annotation['form']
                if not feats:
                    feats = '_'
                else:
                    # Make and join keyed features
                    feats = '|'.join([a + '=' + a for a in feats.strip().split(' ') if a])
                # Construct conllu fields for the word
                word_conllu = {
                    'id': wid+1,
                    'text': morph_word.text,
                    'lemma': annotation['lemma'],
                    'upos': annotation['partofspeech'],
                    'xpos': annotation['partofspeech'],
                    'feats': feats,
                    'misc': '_',
                    'deps': '_',
                }
                # Replace or remove specific fields (optional)
                if remove_fields is not None:
                    for field in remove_fields:
                        word_conllu[field] = '_'
                if replace_fields is not None:
                    for field in replace_fields[0]:
                        word_conllu[field] = replace_fields[1]
                sentence_analyses.append( word_conllu )
                global_word_id += 1
        data.append(sentence_analyses)
    return data


def feats_to_ordereddict(feats_str: str) -> OrderedDict:
    """
    Converts feats string to OrderedDict (as in MaltParserTagger and UDPipeTagger).
    This function is used for post-processing stanza parser's output.
    """
    feats = OrderedDict()
    if feats_str == '_':
        return feats
    feature_pairs = feats_str.split('|')
    for feature_pair in feature_pairs:
        key, value = feature_pair.split('=')
        feats[key] = value
    return feats
