from estnltk.taggers import Tagger
from estnltk.taggers import RegexTagger

from estnltk.text import Span, SpanList, Layer

import regex as re

# ===================================================================
#   Patterns for capturing text snippets that should be ignored;
#
#   Note: these patterns are based on the patterns defined in:
#      * https://github.com/kristiinavaik/ettenten-eeltootlus
#      * https://github.com/EstSyntax/preprocessing-module
#
# ===================================================================

# TODO: the following pattern needs refactoring and testing
# ( Finck , 1979 ; Kuldkepp , 1994) --> <ignore> ( Finck , 1979 ; Kuldkepp , 1994) </ignore> OTSI RELEVANTSEM
# ( vt tabel 2 )" --> <ignore> ( vt tabel 2 ) </ignore>
# <ignore> ( nr 5/ 13.1.2012 ) </ignore>
_reference_year = r'''
    \s?\d+,?\s?[a-zõüöäA-ZÕÜÖÄ%'"\]!]*  # arv (aasta)
    (/\d+)?[-']?\s                      # valikuline kaldkriipsuga aastaarv
    (                                   # valikulise grupi 2 algus
        :\s                             # koolon
        \d+                             # arvud, nt lk nr
        ([-–]\d+[\.,]+)\s               # kuni-märk ja arvud, nt lk 5-6
    )?                                  # grupi 2 lõpp
    -?\w*\s?\.?\s?                      # lõpus tühik
'''

ignore_patterns = [ 
      # TODO
      { 'comment': 'TODO',
        'example': 'TODO',
        '_priority_': 1,
        '_regex_pattern_': re.compile(\
                            r'''
                            (\(            # reference starts with '('
                               [^()]+      # can contain symbols that are not '(' or ')'
                              {end}        # a number, e.g. a year
                            \))            # reference ends with ')'
                            '''.format(end=_reference_year), re.X),
        '_group_': 1 },\

 ]

# ===================================================================

class SyntaxIgnoreTagger(Tagger):
    description = 'Tags text snippets that should be ignored during the syntactic analysis.'
    layer_name  = 'syntax_ignore'
    attributes  = ('type')
    depends_on  = ['words', 'sentences']
    configuration = None


    def __init__(self, allow_loose_match:bool = True):
        self.configuration = {'allow_loose_match': allow_loose_match,}
        # Populate vocabulary
        patterns = []
        for ignore_pat in ignore_patterns:
            patterns.append( ignore_pat )
        # Create a new tagger
        self._syntax_ignore_tagger = RegexTagger(vocabulary=patterns,
                                   attributes=[ '_priority_' ],
                                   conflict_resolving_strategy="MAX",
                                   overlapped=False,
                                   layer_name='syntax_ignore_hints',
                                   )


    def tag(self, text: 'Text', return_layer=False) -> 'Text':
        ''' Tag syntax_ignore layer. '''
        # *) Apply tagger
        conflict_status = {}
        new_layer = self._syntax_ignore_tagger.tag( \
                    text, return_layer=True, status=conflict_status )

        # *) Create an alignment between words and spans
        wid = 0
        ignored_words_spans = []
        for sp in new_layer.spans:
            # Find words that fall within the span
            words_start = -1
            words_end   = -1
            current_wid = wid
            while current_wid < len(text.words):
                word = text.words[current_wid]
                # Exact match
                if word.start == sp.start:
                    words_start = current_wid
                if word.end   == sp.end:
                    words_end = current_wid
                if words_start != -1 and words_end != -1:
                    break
                # Loose match (if allowed)
                if self.configuration['allow_loose_match']:
                    if word.start <= sp.start and sp.start <= word.end:
                        words_start = current_wid
                    if word.start <= sp.end and sp.end <= word.end:
                        words_end = current_wid
                if sp.end < word.start:
                    break
                current_wid += 1
            if words_start != -1 and words_end != -1:
                # Record ignored words
                new_spanlist = SpanList()
                new_spanlist.spans = text.words[words_start:words_end+1]
                ignored_words_spans.append( new_spanlist )
                #print('*',text.text[sp.start:sp.end], sp.start, sp.end)
                #print(text.words[words_start].start, text.words[words_end].end, new_spanlist.spans)
                # Advance in text
                wid = current_wid + 1

        # *) Finally: create a new layer and add spans to the layer
        layer = Layer(name=self.layer_name,
                      parent = 'words',
                      attributes=self.attributes,
                      ambiguous=False)
        for span in ignored_words_spans:
            layer.add_span( span )

        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text

