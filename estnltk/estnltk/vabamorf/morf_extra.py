from estnltk.vabamorf.morf import Vabamorf






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
