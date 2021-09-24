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
