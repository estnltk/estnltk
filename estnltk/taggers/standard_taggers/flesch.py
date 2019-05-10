# -*- coding: utf-8 -*-
"""
Module containing functions for calculating the Flesch reading-ease score for Estonian texts.
"""

# TODO import names või miskit kust saab kätte muutuja WORDS
def fres_score(total_sentences, total_words, total_syllables):
    """Computes the Flesch reading-ease score from the input values."""
    
    score = 206.835 - 1.015 * (total_words / total_sentences) \
            - 84.6 * (total_syllables / total_words)
    
    return score

def fres_no_compound(estnltk_text):
    """Computes the Flesch reading-ease score for the input text by considering compound words as single words."""
    from estnltk import syllabify_word
    
    # tokenize words only if words layer does not exist
    if not estnltk_text.is_tagged('words'): # TODO is_tagged(WORDS)
        #estnltk_text.tag_analysis()
        estnltk_text.tokenize_words()
    
    total_words = len(estnltk_text['words'])
    total_sentences = len(estnltk_text['sentences'])
    
    # simplistic syllable count
    total_syllables = sum(len(syllabify_word(word['text']))
                          for word in estnltk_text['words'])
    
    fres = 206.835 - 1.015 * (total_words / total_sentences) \
           - 84.6 * (total_syllables / total_words)
    
    return fres

def fres_compound(estnltk_text):
    """Computes the Flesch reading-ease score for the input text by considering compound words as separate words."""
    from estnltk import syllabify_word
    
    # tokenize words only if words layer does not exist
    if not estnltk_text.is_tagged('words'): # TODO is_tagged(WORDS)
        estnltk_text.tag_analysis()
        #estnltk_text.tokenize_words()
    
    # count the total root parts (each compounded root counts as a separate word)
    # note that only the first analysis is considered
    total_words = sum(len(word['analysis'][0]['root_tokens'])
                      for word in estnltk_text['words'])
    total_sentences = len(estnltk_text['sentences'])
    
    # the syllable count stays the same
    total_syllables = sum(len(syllabify_word(word['text']))
                          for word in estnltk_text['words'])
    
    score = fres_score(total_sentences, total_words, total_syllables)
    
    return score


def fres(estnltk_text, compounds=True):
    """Computes the Flesch reading-ease score for the input text.
    Compound words are treated as separate words if compounds is not set to False."""
    if compounds:
        fres_compound(estnltk_text)
    else:
        fres_no_compound(estnltk_text)

def fres_per_sentence(estnltk_text):
    """Returns a generator with the FRES scores per sentence in the input text."""
    return (fres(sentence) for sentence in estnltk_text.split_by('sentences'))

def fres_per_sentence_mean(estnltk_text):
    """Returns the mean of the FRES scores computed per sentence in the input text.."""
    total = 0
    n = 0
    for score in fres_per_sentence(estnltk_text):
        total += score
        n += 1
        
    return total / n

def school_level(score):
    """Returns a tuple with the American school level and a descriptive note for the input score.
    Baseed on https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch_reading_ease"""
    # Based on the table found on https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    # Score     School level    Notes
    # 100.00-90.00      5th grade       Very easy to read. Easily understood by an average 11-year-old student.
    # 90.0–80.0         6th grade       Easy to read. Conversational English for consumers.
    # 80.0–70.0         7th grade       Fairly easy to read.
    # 70.0–60.0         8th & 9th grade         Plain English. Easily understood by 13- to 15-year-old students.
    # 60.0–50.0         10th to 12th grade      Fairly difficult to read.
    # 50.0–30.0         College         Difficult to read.
    # 30.0–0.0  College graduate        Very difficult to read. Best understood by university graduates.

    levels = [
        ("6th grade", "Easy to read. Conversational English for consumers."),
        ("7th grade", "Fairly easy to read."),
        ("8th & 9th grade", "Plain English. Easily understood by 13- to 15-year-old students."),
        ("10th to 12th grade", "Fairly difficult to read."),
        ("College", "Difficult to read."),
        ("College graduate", "Very difficult to read. Best understood by university graduates.")]
    
    if 100 >= score and score >= 90:
        return levels[0]
    elif 90 >= score and score >= 80:
        return levels[1]
    elif 80 >= score and score >= 70:
        return levels[2]
    elif 70 >= score and score >= 60:
        return levels[3]
    elif 60 >= score and score >= 50:
        return levels[4]
    elif 50 >= score and score >= 30:
        return levels[5]
    elif 30 >= score and score >= 0:
        return levels[6]
