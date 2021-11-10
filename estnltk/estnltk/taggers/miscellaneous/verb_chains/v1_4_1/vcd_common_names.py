#  Common attribute names used by the verb chain detector
#  Ported from the version 1.4.1:
#     https://github.com/estnltk/estnltk/blob/a8f5520b1c4d26fd58223ffc3f0a565778b3d99f/estnltk/names.py

# commonly required attributes
START = 'start'
END = 'end'
TEXT = 'text'

# document-level attributes
WORDS = 'words'
SENTENCES = 'sentences'
PARAGRAPHS = 'paragraphs'

# sentence level attributes
CLAUSES = 'clauses'

# word attributes
ANALYSIS = 'analysis'
LEMMA = 'lemma'
POSTAG = 'partofspeech'
ROOT = 'root'
ROOT_TOKENS = 'root_tokens'
CLITIC = 'clitic'
ENDING = 'ending'
FORM = 'form'

# clause segmenter related
CLAUSE_IDX = 'clause_index'

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
