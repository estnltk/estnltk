#    
#    This module contains constants, paths and functions commonly used in the EstNLTK library.
#
import os

from estnltk_core.layer.span import Span
from estnltk_core.layer import AttributeList

PACKAGE_PATH = os.path.dirname(__file__)

# Path to Java resources used by EstNLTK
JAVARES_PATH = os.path.join(PACKAGE_PATH, 'java', 'res')

# default NER model path
DEFAULT_PY3_NER_MODEL_DIR = os.path.join(PACKAGE_PATH, 'taggers', 'standard', 'ner', 'models', 'py3_default')


def abs_path(repo_path: str) -> str:
    """Absolute path to repo_path.
       Note: It is recommended to use abs_path instead of rel_path
       in  order  to  make  the  code successfully runnable on all
       platforms, including Windows.
       If you are using relative paths in Windows, the code may
       break for the following reasons:
       A) If a Windows system has more than one drive (e.g. "C:" and
          "D:"), and the estnltk is installed on one drive, and
          the code using estnltk is executed from the other drive,
          then the relative path from one drive to another does not
          exist, and the path creator function fails with an error;
       B) If you are trying to execute a code that uses estnltk
          in a deeply nested directory structure, and as a result,
          the relative path from the current directory to estnltk's
          repo directory becomes long and exceeds the Windows Maximum
          Path Limitation, you will get a FileNotFoundError.
          About the Windows Maximum Path Limitation:
              https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#maximum-path-length-limitation
    """
    return os.path.join(PACKAGE_PATH, repo_path)


def rel_path(repo_path: str) -> str:
    """Relative path to repo_path."""
    return os.path.relpath(os.path.join(PACKAGE_PATH, repo_path))


# ==================================================================
#    Vabamorf's parameters and attribute names                      
# ==================================================================

# Default parameters to be passed to Vabamorf
# Note: these defaults are from  estnltk.vabamorf.morf
DEFAULT_PARAM_DISAMBIGUATE = True
DEFAULT_PARAM_GUESS        = True
DEFAULT_PARAM_PROPERNAME   = True
DEFAULT_PARAM_PHONETIC     = False
DEFAULT_PARAM_COMPOUND     = True

# Morphological analysis attributes used by Vabamorf
VABAMORF_ATTRIBUTES = ('root', 'ending', 'clitic', 'form', 'partofspeech')

# Morphological analysis attributes used by ESTNLTK's Vabamorf
ESTNLTK_MORPH_ATTRIBUTES = ('lemma', 'root', 'root_tokens', 'ending', 'clitic', 'form', 'partofspeech')

# Name of the normalized text attribute. This refers to 
# the normalized word form that was used as a basis in 
# morphological analysis.
NORMALIZED_TEXT = 'normalized_text'

# Name of the ignore attribute. During the morphological 
# disambiguation, all spans of "morph_analysis" that have 
# ignore attribute set to True will be skipped;
IGNORE_ATTR = '_ignore'


# ==================================================================
#    Getting normalized forms from the 'words' layer                
# ==================================================================

def _get_word_texts(word: Span):
    '''Returns all possible normalized forms of the given Span from 
       the 'words' layer.
       If there are normalized word forms available, returns a list
       containing all normalized forms (excluding word.text).
       Otherwise, if no normalized word forms have been set, returns
       a list containing only one item: the surface form (word.text).

       Taggers that want to be aware of word normalization/spelling 
       correction should use this function to retrieve normalized word 
       forms.

       Parameters
       ----------
       word: Span
          word which normalized texts need to be acquired;

       Returns
       -------
       str
          a list of normalized forms of the word, or [ word.text ]
    '''
    if hasattr(word, 'normalized_form') and word.normalized_form != None:
        # return normalized versions of the word
        if isinstance(word.normalized_form, AttributeList):
            # words is ambiguous
            atr_list = [nf for nf in word.normalized_form if nf != None]
            return atr_list if len(atr_list) > 0 else [ word.text ]
        elif isinstance(word.normalized_form, str):
            # words is not ambiguous, and attribute has a single value
            return [ word.normalized_form ]
        elif isinstance(word.normalized_form, list):
            # words is not ambiguous, and attribute has multiple values
            return word.normalized_form
        else:
            raise TypeError('(!) Unexpected data type for word.normalized_form: {}', type(word.normalized_form) )
    else:
        # return the surface form
        return [ word.text ]


def _get_word_text(word: Span):
    '''Returns a word string corresponding to the given Span from 
       the 'words' layer.
       If there are normalized word forms available, returns the 
       first normalized form instead of the surface form.

       Parameters
       ----------
       word: Span
          word which text (or normalized text) needs to be acquired;

       Returns
       -------
       str
          first normalized text of the word, or word.text
    '''
    return _get_word_texts(word)[0]