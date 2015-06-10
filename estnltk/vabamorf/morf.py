# -*- coding: utf-8 -*-
"""
Morphoanalysis/synthesis functionality of estnltk vabamorf package.

Attributes
----------

PACKAGE_PATH: str
    The path where the vabamorf package is located.
DICT_PATH: str
    The path of the default vabamorf dictionary embedded with vabamorf.
DEFAULT_ET_PATH: str
    The path to the default morphoanalyzer lexicon that comes with the vabamorf library.
DEFAULT_ET3_PATH: str
    The path to the default disambiguator lexicon that comes with the vabamorf library.
phonetic_markers: str
    List of characters that make up phonetic markup.
compound_markers: str
    List of characters that make up compound markup.
phonetic_regex: regex
    Regular expression matching any phonetic marker.
compound_regex: regex
    Regular expression matching any compound marker.
"""
from __future__ import unicode_literals, print_function, absolute_import

from . import vabamorf as vm
import os
import six
import re
import operator
from functools import reduce

# path listings
PACKAGE_PATH = os.path.dirname(__file__)
DICT_PATH = os.path.join(PACKAGE_PATH, 'dct')
DEFAULT_ET_PATH = os.path.join(DICT_PATH, 'et.dct')
DEFAULT_ET3_PATH = os.path.join(DICT_PATH, 'et3.dct')

# various markers
phonetic_markers = frozenset('~?]<')
compound_markers = frozenset('_+=')
all_markers = phonetic_markers | compound_markers

def regex_from_markers(markers):
    '''Given a string of characters, construct a regex that matches them.

    Parameters
    ----------
    markers: str
        The list of string containing the markers

    Returns
    -------
    regex
        The regular expression matching the given markers.
    '''
    return re.compile('|'.join([re.escape(c) for c in markers]))

phonetic_regex = regex_from_markers(phonetic_markers)
compound_regex = regex_from_markers(compound_markers)

def convert(word):
    """This method converts given `word` to UTF-8 encoding and `bytes` type for the
       SWIG wrapper."""
    if six.PY2:
        if isinstance(word, unicode):
            return word.encode('utf-8')
        else:
            return word.decode('utf-8').encode('utf-8') # make sure it is real utf8, otherwise complain
    else: # ==> Py3
        if isinstance(word, bytes):
            return word.decode('utf-8') # bytes must be in utf8
        return word

def deconvert(word):
    """This method converts back the output from wrapper.
       Result should be `unicode` for Python2 and `str` for Python3"""
    if six.PY2:
        return word.decode('utf-8')
    else:
        return word


class Vabamorf(object):
    """Class for performing main tasks of morphological analysis.

    Attributes
    ----------
    pid: int
        Current process id.
    morf: Vabamorf
        instance of the Vabamorf class. There should be only one instance per
        process as vabamorf has a global state that might get corrputed by using
        multiple instances in a single process.
    """

    @staticmethod
    def instance():
        """Return an PyVabamorf instance.

        It returns the previously initialized instance or creates a new
        one if nothing exists. Also creates new instance in case the
        process has been forked.
        """
        if not hasattr(Vabamorf, 'pid') or Vabamorf.pid != os.getpid():
            Vabamorf.pid = os.getpid()
            Vabamorf.morf = Vabamorf()
        return Vabamorf.morf

    def __init__(self, lex_path=DEFAULT_ET_PATH, disamb_lex_path=DEFAULT_ET3_PATH):
        """Initialize Vabamorf class.

        NB! Do not use this class directly. Instead use Vabamorf.instance() to obtain access to one.
        Use this only when you want to define custom paths to dictionaries.

        Parameters
        ----------
        lex_path: str
            The path to morphoanalyzer lexicon (default path points to the default dictionary).
        ambig_lex_path: str
            The path to disambiguator lexicon (default path points to the default dictionary).

        """
        self._morf = vm.Vabamorf(convert(lex_path), convert(disamb_lex_path))

    def analyze(self, words, **kwargs):
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
        # if input is a string, then tokenize it
        if isinstance(words, six.string_types):
            words = words.split()

        # convert words to native strings
        words = [convert(w) for w in words]

        morfresults = self._morf.analyze(
            vm.StringVector(words),
            kwargs.get('disambiguate', True),
            kwargs.get('guess', True),
            True, # phonetic and compound information
            kwargs.get('propername', True))
        trim_phonetic = kwargs.get('phonetic', False)
        trim_compound = kwargs.get('compound', True)

        return [postprocess_result(mr, trim_phonetic, trim_compound) for mr in morfresults]

    def spellcheck(self, words, suggestions=True):
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
        if isinstance(words, six.string_types):
            words = words.split()

        # convert words to native strings
        words = [convert(w) for w in words]

        spellresults = self._morf.spellcheck(words, suggestions)
        results = []
        for spellresult in spellresults:
            suggestions = [deconvert(s) for s in spellresult.suggestions]
            result = {
                'text': deconvert(spellresult.word),
                'spelling': spellresult.spelling,
                'suggestions': suggestions
            }
            results.append(result)
        return results

    def fix_spelling(self, words, join=True, joinstring=' '):
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

        fixed_words = []
        for word in self.spellcheck(words, suggestions=True):
            if word['spelling']:
                fixed_words.append(word['text'])
            else:
                suggestions = word['suggestions']
                if len(suggestions) > 0:
                    fixed_words.append(suggestions[0])
                else:
                    fixed_words.append(word['text'])
        if join:
            return joinstring.join(fixed_words)
        else:
            return fixed_words


    def synthesize(self, lemma, form, partofspeech='', hint='', guess=True, phonetic=False):
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
        words = self._morf.synthesize(
            convert(lemma.strip()),
            convert(form.strip()),
            convert(partofspeech.strip()),
            convert(hint.strip()),
            guess,
            phonetic
        )
        return [deconvert(w) for w in words]


def postprocess_result(morphresult, trim_phonetic, trim_compound):
    """Postprocess vabamorf wrapper output."""
    word, analysis = morphresult
    return {
        'text': deconvert(word),
        'analysis': [postprocess_analysis(a, trim_phonetic, trim_compound) for a in analysis]
    }

def postprocess_analysis(analysis, trim_phonetic, trim_compound):
    root = deconvert(analysis.root)

    # extract tokens and construct lemma
    grouptoks = get_group_tokens(root)
    toks = reduce(operator.add, grouptoks)
    lemma = get_lemma(grouptoks, analysis.partofspeech)

    return {
        'root': get_root(root, trim_phonetic, trim_compound),
        'root_tokens': toks,
        'ending': deconvert(analysis.ending),
        'clitic': deconvert(analysis.clitic),
        'partofspeech': deconvert(analysis.partofspeech),
        'form': deconvert(analysis.form),
        'lemma': lemma
        }

def trim_phonetics(root):
    """Function that trims phonetic markup from the root.

    Parameters
    ----------
    root: str
        The string to remove the phonetic markup.

    Returns
    -------
    str
        The string with phonetic markup removed.
    """
    global phonetic_markers
    global phonetic_regex
    if root in phonetic_markers:
        return root
    else:
        return phonetic_regex.sub('', root)

def trim_compounds(root):
    """Function that trims compound markup from the root.

    Parameters
    ----------
    root: str
        The string to remove the compound markup.

    Returns
    -------
    str
        The string with compound markup removed.
    """
    if root in compound_markers:
        return root
    else:
        return compound_regex.sub('', root)

def get_root(root, phonetic, compound):
    """Get the root form without markers.

    Parameters
    ----------
    root: str
        The word root form.
    phonetic: boolean
        If True, add phonetic information to the root forms.
    compound: boolean
        if True, add compound word markers to root forms.
    """
    global compound_regex
    if not phonetic:
        root = trim_phonetics(root)
    if not compound:
        root = trim_compounds(root)
    return root

def get_group_tokens(root):
    """Function to extract tokens in hyphenated groups (saunameheks-tallimeheks).

    Parameters
    ----------
    root: str
        The root form.

    Returns
    -------
    list of (list of str)
        List of grouped root tokens.
    """
    global all_markers
    if root in all_markers or root in ['-', '_']: # special case
        return [[root]]
    groups = []
    for group in root.split('-'):
        toks = [trim_phonetics(trim_compounds(tok)) for tok in group.split('_')]
        groups.append(toks)
    return groups

def get_lemma(grouptoks, partofspeech):
    lemma = '-'.join([''.join(gr) for gr in grouptoks])
    if partofspeech == 'V' and lemma not in ['ei', 'ära']:
        lemma += 'ma'
    return lemma


######################################################
# SHORTCUT FUNCTIONS
######################################################


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

