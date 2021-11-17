#
#   Builds an UserDictTagger from user-specified lexicon 
#   of surface word forms and their corresponding normalized 
#   word forms
# 
import warnings
import re

from typing import MutableMapping

from estnltk import Text
from estnltk import Annotation, Span, Layer

from estnltk.taggers.standard.morph_analysis.morf import VabamorfAnalyzer
from estnltk.taggers.standard.morph_analysis.morf_common import _is_empty_annotation
from estnltk.taggers.standard.morph_analysis.morf_common import NORMALIZED_TEXT
from estnltk.taggers.standard.morph_analysis.userdict_tagger import UserDictTagger

def make_userdict( lexicon, 
                   output_layer: str = 'morph_analysis',
                   ignore_case:        bool = False, 
                   overwrite_existing: bool = True, 
                   warn_on_unknown: bool = True,
                   vm_analyzer: VabamorfAnalyzer=None ):
    '''
    Given a lexicon mapping from surface word forms to normalized word 
    forms, creates morphological analyses for each normalized word form, 
    and stores in a new UserDictTagger. Returns UserDictTagger.
    The UserDictTagger can then be used to rewrite analyses of surface 
    forms with analyses of normalized word forms.
    
    :param lexicon: dictionary that contains mappings from surface word 
        forms to normalized word forms. This dictionary will be used as 
        a basis on creating entries for the UserDictTagger;
   
    :param output_layer: name of UserDictTagger's output_layer. Defaults
        to 'morph_analysis';
    
    :param ignore_case: boolean specifying the value for ignore_case 
        parameter of created UserDictTagger. Default: False;

    :param overwrite_existing: boolean specifying the value for 
        overwrite_existing parameter of created UserDictTagger. 
        Default: True;

    :param warn_on_unknown: boolean specifying whether the user should be 
        warned if no entries are generated for a word because all its 
        normalized forms are unknown to the vm_analyzer. Default: True;
    
    :param vm_analyzer: an instance VabamorfAnalyzer which will be used
        to create morphological analyses for normalized words. If not 
        specified, then VabamorfAnalyzer with default settings will be
        used.
    
    :return: an instance of UserDictTagger
    :rtype: UserDictTagger
    '''
    # Set VabamorfAnalyzer
    if vm_analyzer:
        if not isinstance(vm_analyzer, VabamorfAnalyzer):
            raise TypeError('(!) vm_analyzer should be VabamorfAnalyzer')
    else:
        # Use VabamorfAnalyzer with default settings
        vm_analyzer = VabamorfAnalyzer()
    # Generate lexicon entries
    words_dict = {}
    if isinstance(lexicon, dict):
        to_be_analysed = []
        _WORD_SEPARATOR = '...'
        _pattern_whitespace = re.compile(r'\s')
        # Take out all "normalized word forms" that will be analysed
        valid_keys = 0
        for key in sorted( lexicon.keys() ):
            if key == _WORD_SEPARATOR:
                warnings.warn('(!) {!r} is a separator string and will not be added to the user dictionary.'.format(_WORD_SEPARATOR))
                continue
            value = lexicon.get(key)
            if isinstance(value, str):
                if _pattern_whitespace.search( value.strip() ):
                    raise ValueError('(!) Lexicon entries should not change tokenization. '+\
                                     'Unexpected value {!r} for the key {!r} in input lexicon.'.format(value, key))
                to_be_analysed.append( value.strip() )
            elif isinstance(value, list):
                for val_str in value:
                    assert isinstance(val_str, str), \
                      '(!) Unexpected value {!r} for the key {!r} in input lexicon.'.format(value, key)
                    if _pattern_whitespace.search( val_str.strip() ):
                        raise ValueError('(!) Lexicon entries should not change tokenization. '+\
                                         'Unexpected value {!r} for the key {!r} in input lexicon.'.format(value, key))
                    to_be_analysed.append( val_str.strip() )
            else:
                raise ValueError('(!) Unexpected value {!r} for the key {!r} in input lexicon.'.format(value, key))
            to_be_analysed.append( _WORD_SEPARATOR )
            valid_keys += 1
        # Provide Vabamorf's analysis
        analysable_text = Text( ' '.join(to_be_analysed) )
        analysable_text.tag_layer('sentences')
        vm_analyzer.tag(analysable_text)
        # Collect analyses and construct userdict entries
        word_id = 0
        words_with_empty_annotations = 0
        for word_str in sorted( lexicon.keys() ):
            if word_str == _WORD_SEPARATOR:
                continue
            # Collect analyses / annotations
            corresponding_annotations = []
            new_normalized_forms = []
            while word_id < len( analysable_text[ vm_analyzer.output_layer ] ):
                morph_word = analysable_text[ vm_analyzer.output_layer ][word_id]
                if morph_word.text != _WORD_SEPARATOR:
                    cur_annotations = []
                    for annotation in morph_word.annotations:
                        if _is_empty_annotation( annotation ):
                            # discard an empty annotation
                            continue
                        else:
                            cur_annotations.append( annotation )
                    if len( cur_annotations ) == 0:
                        words_with_empty_annotations += 1
                    corresponding_annotations.append( cur_annotations )
                    new_normalized_forms.append( morph_word.text )
                word_id += 1
                if morph_word.text == _WORD_SEPARATOR:
                    break
            assert len(corresponding_annotations) > 0
            # Construct userdict entries
            entries = []
            for aid, word_annotations in enumerate( corresponding_annotations ):
                for annotation in word_annotations:
                    entry = { NORMALIZED_TEXT : new_normalized_forms[aid] }
                    for key in ['root', 'ending', 'clitic', 'form', 'partofspeech']:
                        entry[key] = annotation[key]
                    entries.append( entry )
            if entries:
                words_dict[word_str] = entries
            else:
                # Skip word with no entries
                if warn_on_unknown:
                    warnings.warn('(!) No entry created for {!r}: words in {!r} were unknown to morphological analyser.'.format(word_str, new_normalized_forms))
                pass
        valid_keys -= words_with_empty_annotations
        assert valid_keys == len( words_dict.keys() )
    # Create new UserDictTagger
    userdict_tagger = UserDictTagger(words_dict=words_dict,
                                     output_layer=output_layer,
                                     ignore_case=ignore_case,
                                     overwrite_existing=overwrite_existing)
    return userdict_tagger

