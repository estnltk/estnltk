# -*- coding: utf-8 -*-
"""Module that defines the attribute names and constants used througout the library
and in corpora."""

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
SPELLING = 'spelling'
SUGGESTIONS = 'suggestions'


# clause segmenter related
CLAUSE_ANNOTATION = 'clause_annotation'
CLAUSE_IDX = 'clause_index'
CLAUSE_BOUNDARY = 'clause_boundary'
EMBEDDED_CLAUSE_START = 'embedded_clause_start'
EMBEDDED_CLAUSE_END = 'embedded_clause_end'

# timex related
TMX_TEMP_FUNCTION = 'temporal_function'
TMX_TID = 'tid'
TMX_ID = 'id'
TMX_TYPE = 'type'
TMX_VALUE = 'value'
TMX_MOD = 'mod'
TMX_ANCHOR_TID = 'anchor_tid'
TMX_ANCHOR_ID = 'anchor_id'
TMX_BEGINPOINT = 'begin_point'
TMX_ENDPOINT = 'end_point'
TMX_QUANT = 'quant'
TMX_FREQ = 'freq'
CREATION_DATE = 'dct'

# verb chain related
PATTERN = 'pattern'
PHRASE = 'phrase'
ROOTS = 'roots'
MORPH = 'morph'
POLARITY = 'pol'
OTHER_VERBS = 'other_verbs'
WORD_ID = 'word_id'
ANALYSIS_IDS = 'analysis_ids'
TENSE = 'tense'
MOOD = 'mood'
VOICE = 'voice'

# wordnet
WORDNET = 'wordnet'
SYNSETS = 'synsets'
SYN_ID = 'id'
SYN_POS = 'pos'
SYN_VARIANTS = 'variants'
LITERAL = 'literal'
SENSE = 'sense'
RELATIONS = 'relations'
