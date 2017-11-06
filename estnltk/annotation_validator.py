#
#   Functions for validating annotations / checking for potential errors
#   Note that these validations are heuristic: there is no guarantee that 
#   all cases found during the validation are actually problematic
#

import re

from estnltk import Text

_parentheses_content = re.compile('(\([^()]+?\))')

_abbrev_pattern      = re.compile('\s([a-zöäüõšž\-.]+\.[a-zöäüõšž\-]+|[a-zöäüõšž\-]+[.])$')
_abbrev_caps_pattern = re.compile('\s([A-ZÖÄÜÕŠŽ\-.]+\.[A-ZÖÄÜÕŠŽ\-]+|[A-ZÖÄÜÕŠŽ\-]+[.])$')
_unlikely_sent_start = re.compile('^([a-zöäüõšž\-,;]).*')

def find_sentence_breaks_inside_parentheses_generator( text: 'Text' ):
    ''' Analyses given Text object, and detects sequences of sentences 
        in which the first sentence contains '(', and the last sentence 
        contains ')', thus, it is possible that a single sentence 
        containing parentheses has been broken mistakenly into several 
        sentences. 
        
        As a result, yields a dict containing start/end position of the 
        parentheses in text (under keys 'start' and 'end'), and a list 
        of SpanList-s corresponding potentially broken sentences (under
        key 'sentences');
    '''
    # Check the layer requirements
    requirements = ['compound_tokens', 'words', 'sentences']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Collect emoticons (as we do not want to mix up parentheses 
    # with emoticons)
    emoticons = []
    comp_tokens_spans = text['compound_tokens'].spans
    for ctid, comptoken in enumerate( comp_tokens_spans ):
        comp_text = text.text[comptoken.start:comptoken.end]
        if 'emoticon' in comptoken.type:
            emoticons.append( comptoken )
    # Check all consecutive pairs of parentheses
    for matchobj in _parentheses_content.finditer(text.text):
        start = matchobj.span(1)[0]
        end   = matchobj.span(1)[1]
        # Check if does not end with an emoticon
        ends_with_emoticon = False
        for emoticon in emoticons:
            if emoticon.start < end and end <= emoticon.end:
                ends_with_emoticon = True
        if ends_with_emoticon:
            # Skip emoticons
            continue
        # Collect sentences that are covered by parentheses
        results = { 'sentences':[], 'start':start, 'end':end }
        for sid, sentence in enumerate( text['sentences'].spans ):
            if sentence.start <= start and start < sentence.end and \
               sentence.end < end:
                # Start
                results['sentences'].append( sentence )
            elif start < sentence.start and sentence.end <= end:
                # Midpoint
                results['sentences'].append( sentence )
            elif sentence.start <= end and end <= sentence.end:
                # End
                results['sentences'].append( sentence )
            if sentence.start > end:
                # No need to look further
                break
        if len(results['sentences']) > 1:
            yield results


def find_sentence_breaking_abbreviations_generator( text: 'Text' ):
    ''' Analyses given Text object, and detects pairs of sentences 
        in which the first sentence ends with a potential abbreviation,
        and the second sentence has a prefix which is unlikely a 
        sentence start. Thus, it is possible that the pair represents
        a single sentence mistakenly split into two sentences.
        
        As a result, yields a dict containing start/end position of the 
        potential abbreviation in text (under keys 'start' and 'end'), 
        and a list of SpanList-s containing potentially broken sentences 
        (under key 'sentences');
    '''
    # Check the layer requirements
    requirements = ['words', 'sentences']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Iterate over consecutive sentences and detect mistakenly split sentences
    for sid, sentence in enumerate( text['sentences'].spans ):
        sent_text = sentence.enclosing_text
        if sid + 1 < len(text['sentences'].spans):
            next_sent = text['sentences'].spans[sid + 1]
            next_sent_text = next_sent.enclosing_text
            if _unlikely_sent_start.search( next_sent_text ):
                target_span = (-1, -1)
                target_str  = None
                # Check for small-letters abbreviation
                m1 = _abbrev_pattern.search(sent_text)
                if m1:
                    target_span = m1.span(1)
                    target_str = m1.group(1)
                # Check for capital-letters abbreviation
                m2 = _abbrev_caps_pattern.search(sent_text)
                if m2:
                    target_span = m2.span(1)
                    target_str = m2.group(1)
                if target_span != (-1, -1) and target_str:
                    results = { 'sentences':[], \
                                'start': sentence.start+target_span[0], \
                                'end':   sentence.start+target_span[1] }
                    results['sentences'].append( sentence )
                    results['sentences'].append( next_sent )
                    yield results


