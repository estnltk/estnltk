import os

PACKAGE_PATH = os.path.dirname(__file__)

# Path to Java resources used by EstNLTK
JAVARES_PATH = os.path.join(PACKAGE_PATH, 'java', 'res')

# default NER model path
DEFAULT_PY2_NER_MODEL_DIR = os.path.join(PACKAGE_PATH, 'taggers', 'estner', 'models', 'py2_default')
DEFAULT_PY3_NER_MODEL_DIR = os.path.join(PACKAGE_PATH, 'taggers', 'estner', 'models', 'py3_default')


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


# ==============================================================================
#   Methods for converting between Unicode <=> Binary
#   Ported from EstNLTK 1.4.1.1 ( with slight modifications ):
#      https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/core.py
# ==============================================================================

def as_unicode(s, encoding='utf-8'):
    """Force conversion of given string to unicode type.
       If the string is already in unicode, then no conversion is done and 
       the same string is returned.
       
       Parameters
       ----------
       s: str or bytes
           The string to convert to unicode.
       encoding: str
           The encoding of the input string (default: utf-8)

       Raises
       ------
       ValueError
           In case an input of invalid type was passed to the function.
       Returns
       -------
           s converted to ``str``
    """
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(str, bytes))


def as_binary(s, encoding='utf-8'):
    """Force conversion of given string to binary type.
       If the string is already in binary, then no conversion is done and 
       the same string is returned and ``encoding`` argument is ignored.
       
       Parameters
       ----------
       s: str or bytes
           The string to convert to binary.
       encoding: str
           The encoding of the resulting binary string (default: utf-8)
       Raises
       ------
       ValueError
           In case an input of invalid type was passed to the function.
       Returns
       -------
           s converted to ``bytes`` 
    """
    if isinstance(s, str):
        return s.encode(encoding)
    elif isinstance(s, bytes):
        # make sure the binary is in required encoding
        return s.decode(encoding).encode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(str, bytes))
