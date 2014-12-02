# -*- coding: utf-8 -*-
'''Module that defines the attribute names used through the library
and in corpora.'''

from __future__ import unicode_literals, print_function

# commonly required attributes
START = 'start'
END = 'end'
REL_START = 'rel_start'
REL_END = 'rel_end'
TEXT = 'text'

# document-level attributes
WORDS = 'words'
SENTENCES = 'sentences'
PARAGRAPHS = 'paragraphs'
DOCUMENTS = 'documents'
FILE = 'file' # the file path of the source corpus
NAMED_ENTITIES = 'named_entities'

# word attributes
ANALYSIS = 'analysis'
LEMMA = 'lemma'
POSTAG = 'partofspeech'
ROOT = 'root'
ROOT_TOKENS = 'root_tokens'
CLITIC = 'clitic'
LABEL = 'label' # named entity
ENDING = 'ending'
FORM = 'form'

# named entity attributes
WORD_START = 'word_start'
WORD_END = 'word_end'
