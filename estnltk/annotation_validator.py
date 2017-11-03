#
#   Functions for validating annotations / checking for potential errors
#   Note that these validations are heuristic: there is no guarantee that 
#   all cases found during the validation are problematic
#

import re

from estnltk import Text

_parentheses_content = re.compile('(\([^()]+?\))')

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
               'The input text is missing the layer "'+requirement+'"!'
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
       