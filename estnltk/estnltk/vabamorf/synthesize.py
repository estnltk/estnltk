from estnltk.vabamorf.morf import Vabamorf


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
