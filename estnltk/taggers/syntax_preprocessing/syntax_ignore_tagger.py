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

lc_letter      = 'a-zöäüõžš'
uc_letter      = 'A-ZÖÄÜÕŽŠ'
titlecase_word = '['+uc_letter+']['+lc_letter+']+'

ignore_patterns = [ 

      # Partly based on PATT_BRACS from https://github.com/EstSyntax/preprocessing-module
      { 'comment': 'Captures sequences of 1-3 symbols in parenthesis;',
        'example': 'Tal on kaks tütart - Beatrice ( 9 ) ja Eugenie ( 8 ).',
        'type'   : 'parenthesis_1to3',
        '_priority_': (0, 0, 0, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s                                                        # starts with '('
              (                                                          #
                (['''+uc_letter+lc_letter+'''0-9,-<>\[\]\/]{1,3}|\+)     # 1-3 symbols or +
              )                                                          #
              (                                                          #
                 \s(['''+uc_letter+lc_letter+'''0-9,-<>\[\]\/]{1,3}|\+)  # 1-3 symbols or +
              )*                                                         #
            \s\))                                                        # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      # Note: in the previous pattern, a space must be after '(' and before ')' in order to 
      #        block extraction of:
      #           ... sellest tulenevalt raamatukogu[(de)] võimalikkus ...
      #           ... Romaanilikkust [(re)]presenteerib Itaalia ...

      # Partly based on PATT_55 from https://github.com/EstSyntax/preprocessing-module
      { 'comment': 'Captures 1-2 titlecase words inside parenthesis;',
        'example': '( Jaapan , Subaru )',
        'type'   : 'parenthesis_title_words',
        '_priority_': (0, 0, 0, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (['''+uc_letter+lc_letter+'''0-9]+\s)                        # preceding word
            (\(\s*                                                       # starts with '('
                ('''+titlecase_word+''')                                 # titlecase word 
                (-'''+titlecase_word+''')?                               # hyphen + titlecase word 
                \s?                                                      # space
                (,'''+titlecase_word+'''\s)?                             # comma + titlecase word 
            \s*\))                                                       # ends with ')'
            ''', re.X),
        '_group_': 2 },\

      # Partly based on PATT_62 from https://github.com/EstSyntax/preprocessing-module
      { 'comment': 'Captures 1-2 titlecase words inside parenthesis;',
        'example': '( 3. koht ) või ( WTA 210. )',
        'type'   : 'parenthesis_ordinal_numbers',
        '_priority_': (0, 0, 0, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (['''+uc_letter+lc_letter+'''0-9]+\s)      # preceding word
            (\(\s*                                     # starts with '('
                (\d+\s?\.                              # ordinal number 
                  (\s['''+lc_letter+''']+)?|           #   followed by lc word, or 
                 '''+uc_letter+'''+                    # uc word
                  \s\d+\s?\.)                          #   followed by ordinal number 
            \s*\))                                     # ends with ')'
            ''', re.X),
        '_group_': 2 },\

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
                                   attributes=[ '_priority_', 'type' ],
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
                new_spanlist.type = sp.type
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

