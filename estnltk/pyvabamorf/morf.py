# -*- coding: utf-8 -*-
'''
Morphoanalysis functionality of pyvabamorf package.

Attributes
----------

PACKAGE_PATH: str
    The path where the pyvabamorf package is located.
DICT_PATH: str
    The path of the default vabamorf dictionary embedded with pyvabamorf.
phonetic_markers: str
    List of characters that make up phonetic markup.
compound_markers: str
    List of characters that make up compound markup.
phonetic_regex: regex
    Regular expression matching any phonetic marker.
compound_regex: regex
    Regular expression matching any compound marker.
'''
from __future__ import unicode_literals, print_function

import estnltk.pyvabamorf.vabamorf as vm
import os
import six
import re
import operator
from functools import reduce

# path listings
PACKAGE_PATH = os.path.dirname(__file__)
DICT_PATH = os.path.join(PACKAGE_PATH, 'dct')

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
    return re.compile('|'.join([re.escape(c) for c in markers]), flags=re.M)

phonetic_regex = regex_from_markers(phonetic_markers)
compound_regex = regex_from_markers(compound_markers)

def convert(word):
    '''This method converts given `word` to appropriate encoding and type to be given to
       SWIG wrapper.'''
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
    '''This method converts back the output from wrapper.
       Result should be `unicode` for Python2 and `str` for Python3'''
    if six.PY2:
        return word.decode('utf-8')
    else:
        return word

def trim_phonetics(root):
    '''Function that trims phonetic markup from the root.
    
    Parameters
    ----------
    root: str
        The string to remove the phonetic markup.
        
    Returns
    -------
    str
        The string with phonetic markup removed.
    '''
    global phonetic_markers
    global phonetic_regex
    if root in phonetic_markers:
        return root
    else:
        return phonetic_regex.sub('', root)

def trim_compounds(root):
    '''Function that trims compound markup from the root.
    
    Parameters
    ----------
    root: str
        The string to remove the compound markup.
        
    Returns
    -------
    str
        The string with compound markup removed.
    '''
    global compound_markers
    global compound_regex
    
    if root in compound_markers:
        return root
    else:
        return compound_regex.sub('', root)

def get_root(root, phonetic, compound):
    '''Get the root form without markers.
    
    Parameters
    ----------
    root: str
        The word root form.
    phonetic: boolean
        If True, add phonetic information to the root forms.
    compound: boolean
        if True, add compound word markers to root forms.
    '''
    global compound_regex
    if not phonetic:
        root = trim_phonetics(root)
    if not compound:
        root = trim_compounds(root)
    return root

def get_group_tokens(root):
    '''Function to extract tokens in hyphenated groups (saunameheks-tallimeheks).
    
    Parameters
    ----------
    root: str
        The root form.
        
    Returns
    -------
    list of (list of str)
        List of grouped root tokens.
    '''
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

def analysis_as_dict(an, trim_phonetic=True, trim_compound=True):
    '''Convert an analysis instance to a dictionary.
    Also adds "ma" ending to verbs.
    
    Parameters
    ----------
    an: vabamorf.WordAnalysis
        Analysis result as returned by vabamorf library.
    trim_phonetic: boolean
        If True, then removes phonetic annotations from root form. (default: True)
    trim_compound: boolean
        If True, then removes compund word annotations from root form. (default: True)
    
    Returns
    -------
    dict
        Morfoanalysis results.
    '''
    root = deconvert(an.root)
    
    # extract tokens and construct lemma
    grouptoks = get_group_tokens(root)
    toks = reduce(operator.add, grouptoks)
    lemma = get_lemma(grouptoks, an.partofspeech)
        
    return {'root': get_root(root, trim_phonetic, trim_compound),
            'root_tokens': toks,
            'ending': deconvert(an.ending),
            'clitic': deconvert(an.clitic),
            'partofspeech': deconvert(an.partofspeech),
            'form': deconvert(an.form),
            'lemma': lemma}

def get_args(**kwargs):
    '''Parse arguments from keyword parameters.
    
    Raises
    ------
    Exception
        In case an illegal argument is passed.
    
    Returns
    -------
    (boolean, boolean, boolean)
        Use heuristics, clean phonetics, clean compound.
    '''
    guess = True
    phonetic = False
    compound = True
    for key, value in kwargs.items():
        if key == 'guess':
            guess = bool(value)
        elif key == 'phonetic':
            phonetic = bool(value)
        elif key == 'compound':
            compound = bool(value)
        else:
            raise Exception('Unkown argument: {0}'.format(key))
    return (guess, phonetic, compound)
            
                
class PyVabamorf(object):
    '''Class for performing main tasks of morphological analysis.
    
    Attributes
    ----------
    pid: int
        Current process id.
    morf: PyVabamorf
        instance of the PyVabamorf class.
    '''

    def __init__(self, lexPath=DICT_PATH):
        '''Initialize PyVabamorf class.
        
        NB! Do not use this class directly. Instead use
        PyVabamorf.instance() to obtain access to one.
        '''
        self._analyzer = vm.Analyzer(convert(lexPath))
        self._synthesizer = vm.Synthesizer(convert(lexPath))

    @staticmethod
    def instance():
        '''Return an PyVabamorf instance.
        
        It returns the previously initialized instance or creates a new
        one if nothing exists. Also creates new instance in case the
        process has been forked.
        '''
        if not hasattr(PyVabamorf, 'pid') or PyVabamorf.pid != os.getpid():
            PyVabamorf.pid = os.getpid()
            PyVabamorf.morf = PyVabamorf()
        return PyVabamorf.morf

    def analyze(self, words, **kwargs):
        '''Perform morphological analysis on input.
        
        Parameters
        ----------
        words: list of str or str
            Either a list of pretokenized words or a string. In case of a string, it will be splitted using
            default behaviour of string.split() function.
        guess: boolean, optional
            If True, then use guessing, when analyzing unknown words (default: True)
        phonetic: boolean, optional
            If True, add phonetic information to the root forms (default: False).
        compound: boolean, optional
            if True, add compound word markers to root forms (default: True)

        Returns
        -------
        list of (list of dict)
            List of analysis for each word in input. One word usually contains more than one analysis as the
            analyser does not perform disambiguation. 
        '''
        guess, phonetic, compound = get_args(**kwargs)
        
        # if input is a string, then tokenize it with whitespace
        if isinstance(words, six.string_types):
            words = words.split()
        
        # convert words to native string
        words = [convert(w) for w in words]
        
        # perform morphological analysis
        morfresult = self._analyzer.analyze(vm.StringVector(words), guess)
        result = []
        for word, analysis in morfresult:
            analysis = [analysis_as_dict(an, phonetic, compound) for an in analysis]
            result.append({'text': deconvert(word),
                           'analysis': analysis})
        return result
        
    def synthesize(self, lemma, partofspeech='', form='', hint='', guess=True, phonetic=True):
        '''Given lemma, pos tag and a form, synthesize the word.

        Parameters
        ----------
        lemma: str
            The lemma of the word to be synthesized.
        partofspeech: str, optional
            The POS tag of the word to be synthesized.
        form: str, optional
            The form of the word to be synthesized.
        hint: str, optional
            The hint used by vabamorf to synthesize the word.
        guess: bool, optional
            If True, use guessing for unknown words (default: True)
        phonetic: bool, optional
            If True, add phonetic markers to synthesized words (default: False).

        Returns
        -------
        list of str
            The list of synthesized words.
        '''
        words = self._synthesizer.synthesize(convert(lemma),
                                             convert(partofspeech),
                                             convert(form),
                                             convert(hint),
                                             guess,
                                             phonetic)
        return [deconvert(word) for word in words]


def analyze(words, **kwargs):
    '''Perform morphological analysis on input.
    
    Parameters
    ----------
    words: list of str or str
        Either a list of pretokenized words or a string. In case of a string, it will be splitted using
        default behaviour of string.split() function.
    guess: boolean, optional
        If True, then use guessing, when analyzing unknown words (default: True)
    phonetic: boolean, optional
        If True, add phonetic information to the root forms (default: False).
    compound: boolean, optional
        if True, add compound word markers to root forms (default: True)

    Returns
    -------
    list of (list of dict)
        List of analysis for each word in input. One word usually contains more than one analysis as the
        analyser does not perform disambiguation. 
    '''
    return PyVabamorf.instance().analyze(words, **kwargs)


def synthesize(lemma, **kwargs):
    '''Given lemma, pos tag and a form, synthesize the word.

    Parameters
    ----------
    lemma: str
        The lemma of the word to be synthesized.
    partofspeech: str, optional
        The POS tag of the word to be synthesized.
    form: str, optional
        The form of the word to be synthesized.
    hint: str, optional
        The hint used by vabamorf to synthesize the word.
    guess: bool, optional
        If True, use guessing for unknown words (default: True)
    phonetic: bool, optional
        If True, add phonetic markers to synthesized words (default: False).

    Returns
    -------
    list of str
        The list of synthesized words.
    '''
    return PyVabamorf.instance().synthesize(lemma, **kwargs)
