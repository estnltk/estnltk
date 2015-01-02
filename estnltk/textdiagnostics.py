# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import string
import sys
from random import sample
from collections import defaultdict

# estonian alphabet with foreign characters
EST_ALPHA_LOWER = 'abcdefghijklmnoprsšzžtuvwõäöüxyz'
EST_ALPHA_UPPER = EST_ALPHA_LOWER.upper()
EST_ALPHA = EST_ALPHA_LOWER + EST_ALPHA_UPPER

# cyrillic alphabet
RUS_ALPHA_LOWER = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
RUS_ALPHA_UPPER = RUS_ALPHA_LOWER.upper()
RUS_ALPHA = RUS_ALPHA_LOWER + RUS_ALPHA_UPPER

DIGITS = string.digits
PUNCTUATION = string.punctuation + '–'
WHITESPACE = string.whitespace

# some common alphabets
ESTONIAN = EST_ALPHA + DIGITS + WHITESPACE + PUNCTUATION
RUSSIAN = RUS_ALPHA + DIGITS + WHITESPACE + PUNCTUATION


class TextDiagnostics(object):
    '''Class for comparing texts against a predefined alphabet'''
    
    def __init__(self, alphabet=ESTONIAN):
        self._alpha = frozenset(alphabet)
    
    def is_valid(self, text):
        return len(self.find_invalid_chars(text)) == 0

    def find_invalid_chars(self, text, context_size=20):
        '''Find invalid characters in text and store information about
        the findings.
        
        Parameters
        ----------
        context_size: int
            How many characters to return as the context.

        '''
        result = defaultdict(list)
        for idx, char in enumerate(text):
            if char not in self._alpha:
                start = max(0, idx-context_size)
                end   = min(len(text), idx+context_size)
                result[char].append(text[start:end])
        return result

    def compute_report(self, texts, context_size=10):
        '''Compute statistics of invalid characters on given texts.
        
        Parameters
        ----------
        texts: list of str
            The texts to search for invalid characters.
        context_size: int
            How many characters to return as the context.
        
        Returns
        -------
        dict of (char -> list of tuple (index, context))
            Returns a dictionary, where keys are invalid characters.
            Values are lists containign tuples with character indices
                and context strings.
        '''
        result = defaultdict(list)
        for text in texts:
            for char, examples in self.find_invalid_chars(text, context_size).items():
                result[char].extend(examples)
        return result

    def report(self, texts, n_examples=10, context_size=10, f=sys.stdout):
        '''Compute statistics of invalid characters and print them.
        
        Parameters
        ----------
        texts: list of str
            The texts to search for invalid characters.
        n_examples: int
            How many examples to display per invalid character.
        context_size: int
            How many characters to return as the context.
        f: file
            The file to print the report (default is sys.stdout)
        '''
            
        result = list(self.compute_report(texts, context_size).items())
        result.sort(key=lambda x: (len(x[1]), x[0]), reverse=True)
        s = 'Analyzed {0} texts.\n'.format(len(texts))
        if (len(texts)) == 0:
            f.write(s)
            return
        s += 'Invalid characters and their counts:\n'
        for c, examples in result:
            s += '"{0}"\t{1}\n'.format(c, len(examples))
        s += '\n'
        for c, examples in result:
            s += 'For character "{0}", found {1} occurrences.\nExamples:\n'.format(c, len(examples))
            examples = sample(examples, min(len(examples), n_examples))
            for idx, example in enumerate(examples):
                s += 'example {0}: {1}\n'.format(idx+1, example)
            s += '\n'
        f.write(s)
