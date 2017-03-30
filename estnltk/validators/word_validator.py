from estnltk.rewriting.premorph.morph_analyzed_token import MorphAnalyzedToken

def is_word(token):
    return MorphAnalyzedToken(token).is_word

def is_pronoun(token):
    return MorphAnalyzedToken(token).is_pronoun

def is_conjunction(token):
    return MorphAnalyzedToken(token).is_conjunction
