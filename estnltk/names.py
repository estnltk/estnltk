# -*- coding: utf-8 -*-
'''Module that defines the attribute names and constants used througout the library
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

# sentence level attributes
NAMED_ENTITIES = 'named_entities'
CLAUSES = 'clauses'
TIMEXES = 'timexes'
VERB_CHAINS = 'verb_chains'

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

# named entity related
WORD_START = 'word_start'
WORD_END = 'word_end'

# clause segmenter related
CLAUSE_ANNOTATION = 'clause_annotation'
CLAUSE_IDX = 'clause_index'
CLAUSE_BOUNDARY = 'clause_boundary'
EMBEDDED_CLAUSE_START = 'embedded_clause_start'
EMBEDDED_CLAUSE_END = 'embedded_clause_end'

# timex related
TMX_TEMP_FUNCTION = 'temporal_function'
TMX_ID = 'tid'
TMX_TYPE = 'type'
TMX_VALUE = 'value'
TMX_MOD = 'mod'
TMX_ANCHOR = 'anchor_time_id'
TMX_BEGINPOINT = 'begin_point'
TMX_ENDPOINT = 'end_point'
TMX_QUANT = 'quant'
TMX_FREQ = 'freq"'

# verb chain related
PATTERN = 'pattern'
PHRASE = 'phrase'
ROOTS = 'roots'
MORPH = 'morph'
POLARITY = 'pol'
OTHER_VERBS = 'otherVerbs'
WORD_ID = 'wordID'
ANALYSIS_IDS = 'analysisIDs'
