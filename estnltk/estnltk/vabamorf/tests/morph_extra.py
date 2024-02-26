from estnltk.vabamorf.morf import Vabamorf


def analyze(words, **kwargs):
    """Perform morphological analysis and disambiguation of given text.

    Parameters
    ----------
    words: list of str or str
        Either a list of pre-tokenized words or a string. In case of a string, it will be split using
        default behaviour of string.split() function.
    disambiguate: boolean (default: True)
        Disambiguate the output and remove inconsistent analysis.
    guess: boolean (default: True)
        Use guessing in case of unknown words
    propername: boolean (default: True)
        Perform additional analysis of proper names.
    compound: boolean (default: True)
        Add compound word markers to root forms.
    phonetic: boolean (default: False)
        Add phonetic information to root forms.

    Returns
    -------
    list of (list of dict)
        List of analysis for each word in input.
    """
    return Vabamorf.instance().analyze(words, **kwargs)


def disambiguate(words, **kwargs):
    """Disambiguate previously analyzed words.

    Parameters
    ----------
    words: list of dict
        A sentence of words.
    compound: boolean (default: True)
        Preserve compound word markers in root forms.
        Note: this has effect only if analysis has
        also preserved compound word markers.
    phonetic: boolean (default: False)
        Preserve phonetic information in root forms.
        Note: this has effect only if analysis has
        also preserved phonetic markers.

    Returns
    -------
    list of dict
        Sentence of disambiguated words.
    """
    return Vabamorf.instance().disambiguate(words, **kwargs)

