#
#  Provides common functions, variables and constants for modules 
#  using Vabamorf-based morphological processing.
# 
from estnltk.text import Span

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

