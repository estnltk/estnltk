#
#   Functions for validating annotations / checking for potential errors 
#  in text segmentation. Note that these validations are heuristic: there 
#  is no guarantee that all cases found during the validation are actually 
#  problematic.
#

import re

from estnltk import Text

_parentheses_content = re.compile(r'(\([^()]+?\))')

_abbrev_pattern      = re.compile(r'\s([a-zöäüõšž\-.]+\.[a-zöäüõšž\-]+|[a-zöäüõšž\-]+[.])$')
_abbrev_caps_pattern = re.compile(r'\s([A-ZÖÄÜÕŠŽ\-.]+\.[A-ZÖÄÜÕŠŽ\-]+|[A-ZÖÄÜÕŠŽ\-]+[.])$')
_unlikely_sent_start = re.compile(r'^([a-zöäüõšž\-,;]).*')
_hyphenation_end     = re.compile(r'(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|'+
                                  r'\u2010|\u2011|\u2012|\u2013|\u2014|\u2015)$')


_camel_case_pattern  = re.compile(r'([a-zöäüõšž][A-ZÖÄÜÕŠŽ])')

_three_lc_words = r'[a-zöäüõšž\-]+\s+[a-zöäüõšž\-]+\s+[a-zöäüõšž\-]+'
_three_lc_words_compiled = re.compile(_three_lc_words)

_double_quotes_patterns = [ # ""
                            re.compile(r'("[^"]+?")'), \
                            # «» 
                            re.compile(r'(\u00AB[^\u00AB\u00BB]+?\u00BB)'), \
                            # “”
                            re.compile(r'([“\u201C][^“”\u201C\u201D]+?[”\u201D])'), \
                          ]


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



def find_sentence_breaks_inside_double_quotes_generator( text: 'Text',\
                        apply_three_lc_words_filter:bool=False,\
                        apply_character_length_filter:bool=True,\
                        min_sentence_char_length:int=5, ):
    ''' Analyses given Text object, and detects sequences of sentences 
        in which the first sentence contains starting double quotes, and 
        the last sentence contains ending double quotes, thus, it is 
        possible that a single sentence containing quotes has been broken 
        mistakenly into several sentences. 
        Note: it is rather common that a quotation actually contains more
        than one sentence, thus, this heuristic is only effective if 
        additional checks/filters are applied on the results for confirming
        that some of the sentences might have been split mistakenly.

        As a result, yields a dict containing start/end position of the 
        quotation in text (under keys 'start' and 'end'), and a list 
        of SpanList-s corresponding sentences covered by the quotation 
        (under key 'sentences');
        
        If apply_three_lc_words_filter==True (default: False), then the 
        results are filtered: only if the one of the sentences overlapping 
        with the quotation contains less than three consecutive lowercased 
        words, the context is yielded (as a context containing potentially 
        broken sentences); In such case, spans of sentences that are 
        suspiciously short are stored under the key 'short_sentences' of
        the yielded dictionary;
        
        If apply_character_length_filter==True (default setting), then the 
        results are filtered: only if the one of the sentences is shorter 
        than min_sentence_char_length (default: 5), the context is yielded 
        (as a context containing potentially broken sentences); In such case, 
        spans of sentences that are suspiciously short are stored under the
        key 'short_sentences' of the yielded dictionary;
        
        In case of regular double quotes ("), sentences overlapping with 
        the quotation are yielded only when there is an even number of 
        double quotes in the text;
    '''
    # Check the layer requirements
    requirements = ['words', 'sentences']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Check all possible pairs of quotations
    for quotes_pattern in _double_quotes_patterns:
        if '"' in quotes_pattern.pattern:
            # if we have the pattern of regular double quotes, we should 
            # apply it only when the double quotes are balanced in the 
            # input text
            quotes_balanced = (text.text).count('"') % 2 == 0
            if not quotes_balanced:
                continue 
        # Check overlaps between quotations and sentence boundaries
        for matchobj in quotes_pattern.finditer(text.text):
            start = matchobj.span(1)[0]
            end   = matchobj.span(1)[1]
            quoted_text = matchobj.group(1)
            # Collect sentences that are covered by quotations
            results = { 'sentences':[], 'start':start, 'end':end }
            # Also remember sentences that are suspiciously short
            too_short_sentences = []
            for sid, sentence in enumerate( text['sentences'].spans ):
                sentence_overlaps_with_quotation = False
                if sentence.start <= start and start < sentence.end and \
                   sentence.end < end:
                    # Start
                    results['sentences'].append( sentence )
                    sentence_overlaps_with_quotation = True
                elif start < sentence.start and sentence.end <= end:
                    # Midpoint
                    results['sentences'].append( sentence )
                    sentence_overlaps_with_quotation = True
                elif sentence.start <= end and end <= sentence.end:
                    # End
                    results['sentences'].append( sentence )
                    sentence_overlaps_with_quotation = True
                if sentence_overlaps_with_quotation:
                    sent_text = sentence.enclosing_text
                    if apply_three_lc_words_filter:
                        if not _three_lc_words_compiled.search(sent_text):
                            # The sentence contains less than three lowercase 
                            # words, it is more likely that there is something 
                            # wrong with it ...
                            too_short_sentences.append(sentence)
                    if apply_character_length_filter:
                        if len(sent_text) < min_sentence_char_length:
                            # if the sentence is smaller than min character length,
                            # consider it as a sentence potentially problematic
                            too_short_sentences.append(sentence)
                if sentence.start > end:
                    # No need to look further
                    break
            if apply_three_lc_words_filter or \
               apply_character_length_filter:
                if not too_short_sentences:
                    # If we did not find any of the sentences being suspiciously
                    # short, then skip this quotation
                    continue
                else:
                    results['short_sentences'] = too_short_sentences
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



def find_sentence_breaking_hyphenations_generator( text: 'Text' ):
    ''' Analyses given Text object, and detects pairs of sentences 
        in which the first sentence ends with a hyphenation, and the 
        second sentence has a prefix  which  is  unlikely  a sentence 
        start. Thus, it is possible that the pair represents a single 
        sentence mistakenly split into two sentences (in the place
        of a word hyphenation).
        
        As a result, yields a dict under which the  key  'sentences' 
        contains a list of SpanList-s potentially broken sentences;
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
                # Check for hyphenation ending the first sentence
                m1 = _hyphenation_end.search(sent_text)
                if m1:
                    target_span = m1.span(1)
                    target_str = m1.group(1)
                if target_span != (-1, -1) and target_str:
                    results = { 'sentences':[] }
                    results['sentences'].append( sentence )
                    results['sentences'].append( next_sent )
                    yield results



def find_short_sentences_generator( text: 'Text', min_words:int=2 ):
    ''' Analyses given Text object, and  yields  sentences  which  are 
        "suspiciously short", that is,  contain  less  than   min_words  
        words. It is possible that short sentences are parts of a longer
        sentence that has been mistakenly split.
        
        As a result, yields a dict containing start/end position of the 
        short sentence (under keys 'start' and 'end'), and a list of SpanList-s 
        containing potentially broken sentences (under key 'sentences').
        Potentially broken sentences here include the previous sentence, the 
        short sentence, and the next sentence.
    '''
    # Check the layer requirements
    requirements = ['words', 'sentences']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Iterate over consecutive sentences and detect mistakenly split sentences
    words_spans    = text['words'].spans
    sentence_spans = text['sentences'].spans
    for sid, sentence in enumerate( sentence_spans ):
        # Find words of the current sentence
        words = [] 
        for wid, word in enumerate( words_spans ):
            if sentence.start <= word.start and word.end <= sentence.end:
                words.append(word)
            if sentence.end < word.start:
                # Look no further
                break
        if len(words) < min_words:
            # The sentence is "suspiciously short"
            results = { 'sentences':[], \
                        'start': sentence.start, \
                        'end':   sentence.end }
            # add previous sentence
            prev_sent = None
            if sid-1 > -1:
                prev_sent = sentence_spans[sid-1]
            if prev_sent:
                results['sentences'].append( prev_sent )
            # add this sentence
            results['sentences'].append( sentence )
            # add next sentence
            next_sent = None
            if sid+1 < len(sentence_spans):
                next_sent = sentence_spans[sid+1]
            if next_sent:
                results['sentences'].append( next_sent )
            yield results



def find_sentences_containing_paragraphs_generator( text: 'Text',
        max_paragraph_endings:int = 3 ):
    ''' Analyses given Text object, and  yields  sentences which contain
        more than max_paragraph_endings paragraph markers ('\n\n'). 
        It is possible that such sentences consist of (many) smaller 
        sentences mistakenly joined together.
        
        As a result, yields a dict containing start/end position of the 
        detected sentence (under keys 'start' and 'end').
    '''
    # Check the layer requirements
    requirements = ['words', 'sentences']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Iterate over sentences and detect mistakenly joined ones
    words_spans    = text['words'].spans
    sentence_spans = text['sentences'].spans
    for sid, sentence in enumerate( sentence_spans ):
        content = sentence.enclosing_text
        if content.count('\n\n') > max_paragraph_endings:
            # The sentence is "suspiciously long"
            # (contains a paragraph change)
            results = { 'start': sentence.start, \
                        'end':   sentence.end }
            yield results



def find_camel_case_word_pairs_generator( text: 'Text', \
                                get_global_text_position:bool=False ):
    ''' Analyses given Text object, and  yields  camel case words (such 
        as "EessõnaEsimese"), along with the subwords they consist of 
        (e.g. "EessõnaEsimese" --> ["Eessõna","Esimese"]). Note that a 
        camel case string may point to a typographical error (missing 
        whitespace between words), but it may also be legal word, such 
        as in names "iPhone", "eBay". The current method does not attempt 
        to distinguish between the latter two cases.
        
        If a single word contains more than  two  subwords  (such  as 
        "WorldWideWeb"), then this method  yields  all  its  subwords. 
        For instance, subwords of "WorldWideWeb"  are  ["World", "Wide", 
        "Web"].
        
        The method yields a dict containing information ("word_start", 
        "word_end", "word_text") about a camel case word, and a list
        of its subwords (under the key 'subwords').
        Each subword is also a dict, describing word's position ("start"/
        "end") and string ("text");
        
        If get_global_text_position==True, then subword positions ("start"/
        "end") are given as absolute positions inside the text. Otherwise
        (the default setting), subword positions are given as relative 
        positions inside the word (so, you can get the absolute subword start
        position by adding 'word_start' + 'start');
    '''
    # Check the layer requirements
    requirements = ['words']
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Iterate over words and yield strings forming a camel case word
    words_spans = text['words'].spans
    for wid, word in enumerate( words_spans ):
        content  = word.text
        # Detect subwords
        subwords = []
        for match in _camel_case_pattern.finditer(content):
            cc_breakpoint   = match.span(1)
            prev_word_end   = cc_breakpoint[0]
            next_word_start = cc_breakpoint[1]-1
            # a) Collect string corresponding to the previous word
            i = prev_word_end
            while i > -1:
                c = content[i]
                if i == 0 or c.isupper():
                    break
                i -= 1
            prev_word_start = i
            # b) Collect string corresponding to the next word
            i = next_word_start
            while i < len(content):
                c = content[i]
                if i == len(content)-1:
                    break
                if i > next_word_start and c.isupper():
                    i -= 1
                    break
                i += 1
            next_word_end = i
            # c) Re-construct subwords 
            base_pos = 0 if not get_global_text_position else word.start
            subword1 = {'start': base_pos+prev_word_start ,\
                        'end':   base_pos+prev_word_end+1,   \
                        'text':  \
                        content[prev_word_start:prev_word_end+1]
                       }
            subword2 = {'start': base_pos+next_word_start ,\
                        'end':   base_pos+next_word_end+1,   \
                        'text':  \
                        content[next_word_start:next_word_end+1]
                       }
            # d) Append subwords
            # Check the last word: if it matches subword1,
            # then we only need to add subword2
            if subwords and \
               subwords[-1]['start']==subword1['start'] and \
               subwords[-1]['end']==subword1['end']:
                # Add only the last word (a continuation)
                subwords.append(subword2)
            else:
                subwords.append(subword1)
                subwords.append(subword2)
        # If any subwords were found, yield these as subwords 
        # associated with the current camel case word
        if subwords:
            # d) Create and yield results dict 
            results = { 'word_start': word.start, \
                        'word_end':   word.end, \
                        'word_text':  word.text, \
                        'subwords':   subwords }
            yield results



def find_newlines_inside_tokens_generator( text: 'Text', focus_layer='words' ):
    '''Analyses given Text object, and yields tokens (from the focus_layer) 
       that contain (at least one) newline character within them, that is, 
       tokens that can potentially conflict with newlines used for marking 
       sentence and paragraph boundaries.
        
       The parameter focus_layer specifies which token layer should be analysed
       (should be one of the following: ['words', 'tokens', 'compound_tokens']).
        
       As a result, yields a dict containing start/end position of the conflicting
       token (under keys 'start' and 'end'), its id inside layer ('tokeni_id'),
       and its textual content ('token_text').
    '''
    # Check the requirements
    assert focus_layer and \
           focus_layer in ['words', 'tokens', 'compound_tokens'], \
           "(!) The focus_layer should be either 'words','tokens',or 'compound_tokens'"
    requirements = [focus_layer]
    for requirement in requirements:
        assert requirement in text.layers, \
               '(!) The input text is missing the layer "'+requirement+'"!'
    # Iterate over tokens and find tokens that contain newlines
    token_spans = text[focus_layer].spans
    for tid, token in enumerate( token_spans ):
        content = token.text
        if '\n' in content:
            results = { 'tokeni_id':   tid, \
                        'token_text':  content, \
                        'start':       token.start, \
                        'end':         token.end }
            yield results

