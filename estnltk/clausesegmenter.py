# -*- coding: utf-8 -*-

'''
Wrapper class around Java-based clause segmenter (Osalausestaja). 
Allows to process results sentence by sentence. 

Requires javabridge, see module "javabridge_support.py" for more 
details on initializing JVM with necessary JAR files;

More on JNI notation:
** http://docs.oracle.com/javase/1.5.0/docs/guide/jni/spec/types.html
'''
from __future__ import unicode_literals, print_function

import json
import os.path
import re

from estnltk.core import JsonPaths
from estnltk.javaprocess import JavaProcess
from copy import deepcopy

CLAUSE_ANNOT = 'clauseAnnotation'
CLAUSE_IDX = 'clause'


class ClauseSegmenter(JavaProcess):
    ''' Wrapper class around Java-based clause segmenter (Osalausestaja). 
        Allows to process results sentence by sentence. 
        ''' 
    
    def __init__(self):
        JavaProcess.__init__(self, 'Osalau.jar', ['-pyvabamorf'])
    
    def __call__(self, corpus):
        for sentence in JsonPaths.words.find(corpus):
            sentence.value = self.detect_clause_boundaries(sentence.value)
        return corpus
    
    def prepare_sentence(self, sentence):
        # Remove phonetic markings from the root
        for word in sentence:
            if 'analysis' in word:
                for analysis in word['analysis']:
                    if 'root' in analysis:
                        analysis['root'] = analysis['root'].replace("~", "")
                        analysis['root'] = re.sub('[?<\]]([aioueöäõü])', '\\1', analysis['root'])
        # Add "words" key (because segmenter looks for it)
        sentence = { "words": sentence }
        # convert from json to string
        return json.dumps(sentence)
    
    def detect_clause_boundaries(self, sentence):
        ''' Detects clause boundaries from given sentence. Assumes that the input
           sentence has been analyzed with pyvabamorf. '''
        sentence_json = self.prepare_sentence(deepcopy(sentence))
        result = self._process_line(sentence_json)
        # fetch the result and take the clause annotation tag where present
        result = json.loads(result)["words"]
        result = self.index_clauses(result)
        assert len(result) == len(sentence)
        for idx in range(len(sentence)):
            sentence[idx][CLAUSE_IDX] = result[idx][CLAUSE_IDX]
        return sentence
        
    def index_clauses(self, sentence):
        '''Add clause indexes to already annotated sentence.'''
        max_index = 0
        max_depth = 1
        stack_of_indexes = [ max_index ]
        for token in sentence:
            if CLAUSE_ANNOT not in token:
                token[CLAUSE_IDX] = stack_of_indexes[-1]
            else:
                # Alustavad märgendused
                for annotation in token[CLAUSE_ANNOT]:
                    if annotation == "KIILU_ALGUS":
                        # Liigume sügavamale, alustame järgmist kiilu
                        max_index += 1
                        stack_of_indexes.append(max_index)
                        if (len(stack_of_indexes) > max_depth):
                            max_depth = len(stack_of_indexes)
                token[CLAUSE_IDX] = stack_of_indexes[-1]
                # Lõpetavad märgendused
                for annotation in token[CLAUSE_ANNOT]:
                    if annotation == "KINDEL_PIIR":
                        # Liigume edasi samal tasandil, alustame järgmist osalauset
                        max_index += 1
                        stack_of_indexes[-1] = max_index
                    elif annotation == "KIILU_LOPP":
                        # Taandume sügavusest, sulgeme ühe kiilu
                        stack_of_indexes.pop()
        return sentence
