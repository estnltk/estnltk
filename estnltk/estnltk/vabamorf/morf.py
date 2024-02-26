"""
Morphoanalysis/synthesis functionality of estnltk vabamorf package.

Attributes
----------

PACKAGE_PATH: str
    The path where the vabamorf package is located.
DICT_ROOT_PATH: str
    The path to the root directory containing subdirectories for different versions of 
    Vabamorf's lexicons.
VM_LEXICONS: str
    List of Vabamorf's lexicons available in EstNLTK. Basically, the list contains 
    subdirectories of DICT_ROOT_PATH (sorted by names). Subdirectory names are ISO 
    format dates, indicating dates in which corresponding lexicons were created or 
    introduced into EstNLTK. 
    As directory names are sorted, the last name is always the latest one, and this is 
    also the lexicon used by default.
phonetic_markers: str
    List of characters that make up phonetic markup.
compound_markers: str
    List of characters that make up compound markup.
phonetic_regex: regex
    Regular expression matching any phonetic marker.
compound_regex: regex
    Regular expression matching any compound marker.
"""

from . import vabamorf as vm
import os
import re
import operator
from functools import reduce

# path listings
PACKAGE_PATH   = os.path.dirname(__file__)
DICT_ROOT_PATH = os.path.join(PACKAGE_PATH, 'dct')

# =============================================================================
#   Utils
# =============================================================================

# various markers
phonetic_markers = frozenset('~?]<')
compound_markers = frozenset('_+=')
all_markers = phonetic_markers | compound_markers

def regex_from_markers(markers):
    """Given a string of characters, construct a regex that matches them.

    Parameters
    ----------
    markers: str
        The list of string containing the markers

    Returns
    -------
    regex
        The regular expression matching the given markers.
    """
    return re.compile('|'.join([re.escape(c) for c in markers]))

phonetic_regex = \
    regex_from_markers(phonetic_markers)
phonetic_marker_repetition_regex = \
    re.compile( '^('+('|'.join([re.escape(c) for c in phonetic_markers]))+')+$' )
compound_regex = regex_from_markers(compound_markers)


def convert(word):
    """This method converts given `word` to UTF-8 encoding and `bytes` type for the
       SWIG wrapper."""
    if isinstance(word, bytes):
        return word.decode('utf-8') # bytes must be in utf8
    return word


# =============================================================================
#   Handling Vabamorf's lexicons
# =============================================================================

# All Vabamorf's lexicons available in EstNLTK
VM_LEXICONS = [item for item in sorted(os.listdir(DICT_ROOT_PATH),reverse=False) if os.path.isdir(os.path.join(DICT_ROOT_PATH,item))]

def get_vm_lexicon_files( vm_lexicon_dir, dict_path=DICT_ROOT_PATH ):
    '''Given EstNLTK's directory that contains Vabamorf\'s lexicons, 
       creates names of the lexicon files, checks for their existence 
       and returns a tuple of lexicon file paths:
          ( path to analyser's lexicon, 
            path to disambiguator's lexicon ).
       If vm_lexicon_dir is a directory name without path, and 
       dict_path is provided, then first constructs the full path 
       to Vabamorf\'s lexicon directory by joining dict_path and 
       vm_lexicon_dir;
    '''
    if not os.path.isdir(vm_lexicon_dir) and dict_path is not None:
        vm_lexicon_dir = os.path.join(dict_path, vm_lexicon_dir)
    assert os.path.isdir(vm_lexicon_dir), '(!) Unexpected Vabamorf\'s lexicon directory {!r}'.format(vm_lexicon_dir)
    et_file  = os.path.join(vm_lexicon_dir, 'et.dct')
    et3_file = os.path.join(vm_lexicon_dir, 'et3.dct')
    assert os.path.isfile(et_file), '(!) Unable to find Vabamorf analyser\'s lexicon file: {!r}'.format(et_file)
    assert os.path.isfile(et3_file), '(!) Unable to find Vabamorf disambiguator\'s lexicon file: {!r}'.format(et3_file)
    return (et_file, et3_file)


# =============================================================================
#   Vabamorf class
# =============================================================================

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

    def __init__(self, lexicon_dir=VM_LEXICONS[-1], lex_path=None, disamb_lex_path=None):
        """Initialize Vabamorf class.

        NB! Do not use this class directly. Instead, use Vabamorf.instance() to obtain access to one.
        Use this only when you want to define custom paths to lexicons / dictionaries.

        Parameters
        ----------
        lexicon_dir: str
            The path to a directory containing both morphological analyzer's and disambiguator's 
            lexicons (files 'et.dct' and 'et3.dct');
            Defaults to the last directory name in the list VM_LEXICONS.
        lex_path: str
            The path to morphological analyzer's lexicon (defaults to None).
            If you use this along with lexicon_dir, then the lexicon_dir's specification 
            will be overwritten by this specification.
        disamb_lex_path: str
            The path to morphological disambiguator's lexicon (defaults to None).
            If you use this along with lexicon_dir, then the lexicon_dir's specification 
            will be overwritten by this specification.
        """
        latest_lex_path, latest_disamb_lex_path = (None, None)
        if lexicon_dir is not None:
            # Get full paths to the latest VM lexicons
            (latest_lex_path, latest_disamb_lex_path) = get_vm_lexicon_files(lexicon_dir, dict_path=DICT_ROOT_PATH)
        lex_path = latest_lex_path if lex_path is None else lex_path
        disamb_lex_path = latest_disamb_lex_path if disamb_lex_path is None else disamb_lex_path
        # Sanity check: at the end of day, all lexicons should be specified
        assert lex_path is not None, '(!) lex_path unspecified. Please use the parameter lex_path to specify Vabamorf analyser\'s lexicon file.'
        assert disamb_lex_path is not None, '(!) disamb_lex_path unspecified. Please use the parameter disamb_lex_path to specify Vabamorf disambiguator\'s lexicon file.'
        self._morf = vm.Vabamorf(convert(lex_path), convert(disamb_lex_path))

    def analyze(self, words, **kwargs):
        """Perform morphological analysis and disambiguation of given text.

        Parameters
        ----------
        stem: boolean (default: False)  # TV-2024.02.03 ???
            asenda lemma tüvega         # TV-2024.02.03 ???        
        words: list of str or str
            Either a list of pretokenized words or a string. In case of a string, it will be split using
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
        if isinstance(words, str):
            words = words.split()

        # convert words to native strings
        words = [convert(w) for w in words]

        morfresults = self._morf.analyze(
            vm.StringVector(words),
            kwargs.get('disambiguate', True),
            kwargs.get('guess', True),
            True, # add phonetic and compound information by default
            kwargs.get('propername', True),
            kwargs.get('stem', False)) # TV-2024.02.03 ???
        preserve_phonetic = kwargs.get('phonetic', False)
        preserve_compound = kwargs.get('compound', True)

        return [postprocess_result(mr, preserve_phonetic, preserve_compound) for mr in morfresults]

    def disambiguate(self, words, **kwargs):
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
        preserve_phonetic = kwargs.get('phonetic', False)
        preserve_compound = kwargs.get('compound', True)
        
        words = vm.SentenceAnalysis([as_wordanalysis(w) for w in words])
        disambiguated = self._morf.disambiguate(words)
        return [postprocess_result(mr, preserve_phonetic, preserve_compound) for mr in disambiguated]

    def spellcheck(self, words, suggestions=True):
        """Spellcheck given sentence.

        Note that spellchecker does not respect pre-tokenized words and concatenates
        token sequences such as "New York".

        Parameters
        ----------
        words: list of str or str
            Either a list of pretokenized words or a string. In case of a string, it will be split using
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
        if isinstance(words, str):
            words = words.split()

        # convert words to native strings
        words = [convert(w) for w in words]

        spellresults = self._morf.spellcheck(words, suggestions)
        results = []
        for spellresult in spellresults:
            suggestions = list(spellresult.suggestions)
            result = {
                'text': spellresult.word,
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
            Either a list of pretokenized words or a string. In case of a string, it will be split using
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
        return list(words)


def postprocess_result(morphresult, preserve_phonetic, preserve_compound):
    """Postprocess vabamorf wrapper output."""
    word, analysis = morphresult
    return {
        'text': word,
        'analysis': [postprocess_analysis(a, preserve_phonetic, preserve_compound) for a in analysis]
    }


def postprocess_analysis(analysis, preserve_phonetic, preserve_compound):
    root = analysis.root

    # extract tokens and construct lemma
    grouptoks = get_group_tokens(root)
    toks = reduce(operator.add, grouptoks)
    lemma = get_lemma(grouptoks, analysis.partofspeech)

    return {
        'root': get_root(root, preserve_phonetic, preserve_compound),
        'root_tokens': toks,
        'ending': analysis.ending,
        'clitic': analysis.clitic,
        'partofspeech': analysis.partofspeech,
        'form': analysis.form,
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
    global phonetic_regex
    global phonetic_marker_repetition_regex
    if phonetic_marker_repetition_regex.match(root):
        # Preserve a single phonetic symbol, e.g. '?',
        #              and repeated symbols, e.g. '??????'
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


def as_analysis(analysis):
    return vm.Analysis(
        convert(analysis['root']),
        convert(analysis['ending']),
        convert(analysis['clitic']),
        convert(analysis['partofspeech']),
        convert(analysis['form'])
    )


def as_wordanalysis(word):
    analysis = vm.AnalysisVector([as_analysis(a) for a in word['analysis']])
    return vm.WordAnalysis(convert(word['text']), analysis)












