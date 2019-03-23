#
#  Provides common functions, variables and constants for modules 
#  using Vabamorf-based morphological processing.
# 

import operator
from functools import reduce

from typing import MutableMapping, Any

from estnltk.text import Span

from estnltk.vabamorf.morf import get_group_tokens
from estnltk.vabamorf.morf import get_lemma
from estnltk.vabamorf.morf import get_root

# Default parameters to be passed to Vabamorf
# Note: these defaults are from  estnltk.vabamorf.morf
DEFAULT_PARAM_DISAMBIGUATE = True
DEFAULT_PARAM_GUESS        = True
DEFAULT_PARAM_PROPERNAME   = True
DEFAULT_PARAM_PHONETIC     = False
DEFAULT_PARAM_COMPOUND     = True

# Morphological analysis attributes used by Vabamorf
VABAMORF_ATTRIBUTES = ('root', 'ending', 'clitic', 'form', 'partofspeech')

# Morphological analysis attributes used by ESTNLTK
ESTNLTK_MORPH_ATTRIBUTES = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')

# Name of the ignore attribute. During the morphological 
# disambiguation, all spans of "morph_analysis" that have 
# ignore attribute set to True will be skipped;
IGNORE_ATTR = '_ignore'

# =================================
#    Helper functions
# =================================

def _get_word_text( word:Span ):
    '''Returns a word string corresponding to the given (word) Span. 
       If the normalized word form is available, returns the normalized 
       form instead of the surface form. 
        
       Parameters
       ----------
       word: Span
          word which text (or normalized text) needs to be acquired;
            
       Returns
       -------
       str
          normalized text of the word, or word.text
    '''
    if hasattr(word, 'normalized_form') and word.normalized_form != None:
        # return the normalized version of the word
        return word.normalized_form
    else:
        return word.text


def _create_empty_morph_record( word = None, layer_attributes = None ):
    ''' Creates an empty 'morph_analysis' record that will 
        have all of its attribute values set to None.
        If word is provided, then 'start' and 'end' attributes
        of the record will be copied from the word.
        
        Returns the record.
    '''
    current_attributes = \
        layer_attributes if layer_attributes else ESTNLTK_MORPH_ATTRIBUTES
    record = {}
    if word is not None:
        record['start'] = word.start
        record['end']   = word.end
    for attr in current_attributes:
        record[attr] = None
    return record


def _create_empty_morph_span( word, layer_attributes = None ):
    ''' Creates an empty 'morph_analysis' span that will 
        have word as its parent span. 
        All attribute values of the span will be set 
        to None.
        
        Returns the Span.
    '''
    current_attributes = \
        layer_attributes if layer_attributes else ESTNLTK_MORPH_ATTRIBUTES
    span = Span(parent=word)
    for attr in current_attributes:
        setattr(span, attr, None)
    return span


def _is_empty_span( span:Span ):
    '''Checks if the given span (from the layer 'morph_analysis')
       is empty, that is: all of its morph attributes are set to 
       None. 
       This means that the word was unknown to morphological 
       analyser. 
    '''
    all_none = [getattr(span, attr) is None for attr in ESTNLTK_MORPH_ATTRIBUTES]
    return all(all_none)

# ========================================================
#   Convert Span to records, but ignore some attributes   
# ========================================================

def _span_to_records_excl( span: Span, exclude_attribs ) -> MutableMapping[str, Any]:
    '''Converts given Span to a dictionary of attributes and 
       values (records), but excludes attributes from the 
       list exclude_attribs.
       Use this method iff Span.to_record() cannot be used 
       because "legal attributes" of the layer have already 
       been changed.'''
    return {**{k: getattr(span, k) for k in list(span.legal_attribute_names) if k not in exclude_attribs },
            **{'start': span.start, 'end': span.end } }


# ========================================================
#    Utils for converting Vabamorf dict <-> EstNLTK Span
# ========================================================

def _convert_morph_analysis_span_to_vm_dict(span: Span):
    """ Converts a SpanList from the layer 'morph_analysis'
        into a dictionary object that has the structure
        required by the Vabamorf:
        { 'text' : ..., 
          'analysis' : [
             { 'root': ..., 
               'partofspeech' : ..., 
               'clitic': ... ,
               'ending': ... ,
               'form': ... ,
             },
             ...
          ]
        }
        Returns the dictionary.
    """
    attrib_dicts = {}
    # Get lists corresponding to attributes
    for attr in ESTNLTK_MORPH_ATTRIBUTES:
        attrib_dicts[attr] = getattr(span, attr)
    # Rewrite attributes in Vabamorf's analysis format
    # Collect analysis dicts
    nr_of_analyses = len(attrib_dicts['lemma'])
    word_dict = {'text': span.text,
                 'analysis': []}
    for i in range(nr_of_analyses):
        analysis = {}
        for attr in attrib_dicts.keys():
            attr_value = attrib_dicts[attr][i]
            if attr == 'root_tokens':
                attr_value = list(attr_value)
            analysis[attr] = attr_value
        word_dict['analysis'].append(analysis)
    return word_dict


def _convert_vm_dict_to_morph_analysis_spans( vm_dict, word, \
                                              layer_attributes = None, \
                                              sort_analyses = True ):
    ''' Converts morphological analyses from the Vabamorf's 
        dictionary format to the EstNLTK's Span format, and 
        attaches the newly created span as a child of the 
        word.
        
        If sort_analyses=True, then analyses will be sorted 
        by root,ending,clitic,postag,form;
        
        Note: if word has no morphological analyses (e.g. it 
        is an unknown word), then returns an empty list.
        
        Returns a list of EstNLTK's Spans.
    '''
    spans = []
    current_attributes = \
        layer_attributes if layer_attributes else ESTNLTK_MORPH_ATTRIBUTES
    word_analyses = vm_dict['analysis']
    if sort_analyses:
        # Sort analyses ( to assure a fixed order, e.g. for testing purpose )
        word_analyses = sorted( vm_dict['analysis'], key = \
            lambda x: x['root']+x['ending']+x['clitic']+x['partofspeech']+x['form'], 
            reverse=False )
    for analysis in word_analyses:
        span = Span(parent=word)
        for attr in current_attributes:
            if attr in analysis:
                # We have a Vabamorf's attribute
                if attr == 'root_tokens':
                    # make it hashable for Span.__hash__
                    setattr(span, attr, tuple(analysis[attr]))
                else:
                    setattr(span, attr, analysis[attr])
            else:
                # We have an extra attribute -- initialize with None
                setattr(span, attr, None)
        spans.append(span)
    return spans


def _postprocess_root( root:str, partofspeech:str, \
                       trim_phonetic:bool=DEFAULT_PARAM_PHONETIC, \
                       trim_compound:bool=DEFAULT_PARAM_COMPOUND ):
    ''' Converts root string from Vabamorf's format to EstNLTK's format:
         1) trims phonetic and compound info from the root (if required);
         2) generates list of root tokens;
         3) generates root lemma;
        Basically performs all the processing steps that are performed in
        the postprocess_analysis() method:
          https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/vabamorf/morf.py#L311
          
        Returns tuple: (root, root_tokens, lemma).
    '''
    # extract tokens, construct lemma and 
    # reconstruct root
    grouptoks   = get_group_tokens(root)
    root_tokens = reduce(operator.add, grouptoks)
    lemma = get_lemma(grouptoks, partofspeech)
    root  = get_root(root, trim_phonetic, trim_compound)
    return root, root_tokens, lemma


# Pos tags used by Vabamorf
VABAMORF_POSTAGS = \
    ['A', 'C', 'D', 'G', 'H', 'I', 'J', 'K', 'N', 'O', 'P', 'S', 'U', 'V', 'X', 'Y', 'Z']

# Noun form categories used by Vabamorf
VABAMORF_NOUN_FORMS = \
    ['ab', 'abl', 'ad', 'adt', 'all', 'el', 'es', 'g', 'ill', 'in', 'kom', 'n', 'p', 'pl', 'sg', 'ter', 'tr']

# Verb form categories used by Vabamorf
VABAMORF_VERB_FORMS = \
    ['b', 'd', 'da', 'des', 'ge', 'gem', 'gu', 'ks', 'ksid', 'ksime', 'ksin', 'ksite', 'ma', 'maks', 'mas', \
     'mast', 'mata', 'me', 'n', 'neg', 'neg ge', 'neg gem', 'neg gu', 'neg ks', 'neg me', 'neg nud', 'neg nuks', \
     'neg o', 'neg vat', 'neg tud', 'nud', 'nuks', 'nuksid', 'nuksime', 'nuksin', 'nuksite', 'nuvat', 'o', \
     's', 'sid', 'sime', 'sin', 'site', 'ta', 'tagu', 'taks', 'takse', 'tama', 'tav', 'tavat', 'te', 'ti', \
     'tud', 'tuks', 'tuvat', 'v', 'vad', 'vat' ]
