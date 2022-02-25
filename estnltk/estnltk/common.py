#    
#    This module contains constants, paths and functions commonly used in the EstNLTK library.
#
import os

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