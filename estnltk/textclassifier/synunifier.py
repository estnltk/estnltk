# -*- coding: utf-8 -*-
'''Module containing functionality for problem-specific synonym unification.'''

from __future__ import unicode_literals, print_function

from copy import deepcopy
import codecs

class SynUnifier(object):
    '''Class for storing technical synonyms.'''
    
    def __init__(self, mapped_values={}):
        '''Initialize a SynUnifier instance.
        
        Parameters
        ----------
        
        mapped_values: dict
            A surjective mapping from alternative synonyms to main synonyms.
            Each value in `mapped_values.values()` must also satisfy `mapped_values[value] == value`.
        
        Raises
        ------
        
        ValueError
            If at least one value in `mapped_values.values()` does not satisfy `mapped_values[value] == value`.
        '''
        self._map = {}
        for key, value in mapped_values.items():
            self._map_word(key.lower(), value.lower())
        self._check_target_values()
    
    def add_synset(self, synset):
        '''Add a synset to the object.
        
        Parameters
        ----------
        
        synset: iterable of str strings
            The collection of techinical synonyms. The first element will be used as the target value
            that other synonymous values are mapped to.
        
        Raises
        ------
        
        ValueError
            If the given collection of synsets does not contain at least two unique elements.
        
        '''
        words = [word.lower() for word in synset]
        if len(set(words)) < 2:
            err = 'Synsets {0} must have at least 2 case-insensitive unique elements.'.format(repr(synset))
            raise ValueError(err)
        main_word = words[0]
        for other_word in words:
            self._map_word(other_word, main_word)
    
    def unify(self, word):
        '''Unify the given word.
        
        Parameters
        ----------
        
        word: str
            The word to be translated.
            
        Returns
        -------
        str
            The target synonym of the given word, if it exists. Otherwise returns the same word.
        '''
        
        word = word.lower()
        if word in self._map:
            return self._map[word]
        return word

    def export(self):
        '''Export the instance to a JSON-serializable dictionary.
        
        Returns
        -------
        dict
            The dictionary contains str key and value mappings from alternative word representations to
            its main representation.
        '''
        return deepcopy(self._map)
    
    def _check_target_values(self):
        values = self._map.values()
        for value in values:
            if value not in self._map or self._map[value] != value:
                err = 'No mapping from {0} to {0}, which is implicitly required.'.format(repr(value))
                raise ValueError(err)
                
    def _map_word(self, other_word, main_word):
        if len(other_word) == 0 or len(main_word) == 0:
            raise ValueError('zero-length string')
        if other_word in self._map and self._map[other_word] != main_word:
            err = 'Word {0} already mapped to {1} when trying to map it to {2}.'.format(repr(main_word),
                                                                                        repr(self._map[main_word]),
                                                                                        repr(other_word))
            raise ValueError(err)
        self._map[other_word] = main_word


class SynFileReader(object):
    '''Class to read technical synonym files.'''
    
    def __init__(self, fnm):
        '''Initialize SynFileReader.
        
        Parameters
        ----------
        fnm: str
            Filename of the file to be read from disk.
        '''
        self._fnm = fnm
    
    def read(self):
        unifier = SynUnifier()
        with codecs.open(self._fnm, 'rb', 'utf-8') as f:
            line = f.readline()
            while line != '':
                line = line.strip()
                if len(line) == 0:
                    line = f.readline()
                    continue
                unifier.add_synset(line.split())
                line = f.readline()
        return unifier
