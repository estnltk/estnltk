from estnltk.vabamorf.morf import Vabamorf


def analyze(words, **kwargs):
    """Perform morphological analysis and disambiguation of given text.

    Parameters
    ----------
    words: list of str or str
        Either a list of pretokenized words or a string. In case of a string, it will be splitted using
        default behaviour of string.split() function.
    disambiguate: boolean (default: True)
        Disambiguate the output and remove incosistent analysis.
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


def spellcheck(words, suggestions=True):
    """Spellcheck given sentence.

    Note that spellchecker does not respect pre-tokenized words and concatenates
    token sequences such as "New York".

    Parameters
    ----------
    words: list of str or str
        Either a list of pretokenized words or a string. In case of a string, it will be splitted using
        default behaviour of string.split() function.
    suggestions: boolean (default: True)
        Add spell suggestions to result.

    Returns
    -------
    list of dict
        Each dictionary contains following values:
            'word': the original word
            'spelling': True, if the word was spelled correctly
            'suggestions': list of suggested strings in case of incorrect spelling
    """
    return Vabamorf.instance().spellcheck(words, suggestions)


def fix_spelling(words, join=True, joinstring=' '):
    """Simple function for quickly correcting misspelled words.

    Parameters
    ----------
    words: list of str or str
        Either a list of pretokenized words or a string. In case of a string, it will be splitted using
        default behaviour of string.split() function.
    join: boolean (default: True)
        Should we join the list of words into a single string.
    joinstring: str (default: ' ')
        The string that will be used to join together the fixed words.

    Returns
    -------
    str
        In case join is True
    list of str
        In case join is False.
    """
    return Vabamorf.instance().fix_spelling(words, join, joinstring)


def synthesize(lemma, form, partofspeech='', hint='', guess=True, phonetic=False):
    """Synthesize a single word based on given morphological attributes.

    Note that spellchecker does not respect pre-tokenized words and concatenates
    token sequences such as "New York".

    Parameters
    ----------
    lemma: str
        The lemma of the word(s) to be synthesized.
    form: str
        The form of the word(s) to be synthesized.
    partofspeech: str
        Part-of-speech.
    hint: str
        Hint.
    guess: boolean (default: True)
        Use heuristics when synthesizing unknown words.
    phonetic: boolean (default: False)
        Add phonetic markup to synthesized words.

    Returns
    -------
    list
        List of synthesized words.
    """
    return Vabamorf.instance().synthesize(lemma, form, partofspeech, hint, guess, phonetic)
