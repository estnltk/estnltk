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
      # Partly based on PATT_BRACS from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures sequences of 1-3 symbols in parenthesis;',
        'example': 'Tal on kaks tütart - Beatrice ( 9 ) ja Eugenie ( 8 ).',
        'type'   : 'parenthesis_1to3',
        '_priority_': (0, 0, 1, 1),
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
      # Note: in the previous pattern, a space is intentionally added after '(' and before ')' 
      #       in order to prevent extraction of optional word endings/prefixes, such as:
      #           ... sellest tulenevalt raamatukogu[(de)] võimalikkus ...
      #           ... Romaanilikkust [(re)]presenteerib Itaalia ...
      { 'comment': 'Captures at least 2 char sequences of 1-3 symbols in parenthesis;',
        'example': '(x 1 , x 2 , ... , K , ... , x n)',
        'type'   : 'parenthesis_1to3',
        '_priority_': (0, 0, 1, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                                          # starts with '('
              (                                                          #
                (['''+uc_letter+lc_letter+'''0-9,.-<>\[\]\/]{1,3}|\+)    # 1-3 symbols or +
              )                                                          #
              (                                                          #
                 \s(['''+uc_letter+lc_letter+'''0-9,.-<>\[\]\/]{1,3}|\+) # 1-3 symbols or +
              )+                                                         #
            \))                                                          # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures sequences of 1-4 non-letters in parenthesis;',
        'example': 'Pariisi (1919) ja Tartu (1920) rahukonverentsid',
        'type'   : 'parenthesis_1to4',
        '_priority_': (0, 0, 1, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                               # starts with '('
              (                                               #
                ([0-9,.-<>\[\]\/]{1,4}|\+)                    # 1-4 non-letters or +
              )                                               #
              (                                               #
                 \s([0-9,.-<>\[\]\/]{1,4}|\+)                 # 1-4 non-letters or +
              )*                                              #
            \))                                               # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures sequences of 1-4 non-letters in parenthesis;',
        'example': 'Pariis ( 1919 ) ja Tartu ( 1920 )',
        'type'   : 'parenthesis_1to4',
        '_priority_': (0, 0, 1, 4),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                            # starts with '('
              (                                               #
                ([0-9,.-<>\[\]\/]{4}|\+)                      # 4 non-letters or +
              )                                               #
              (                                               #
                 \s([0-9,.-<>\[\]\/]{1,4}|\+)                 # 1-4 non-letters or +
              )*                                              #
            \s*\))                                            # ends with ')'
            ''', re.X),
        '_group_': 1 },\

      # Partly based on PATT_55 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures 1-2 comma-separated titlecase words inside parenthesis;',
        'example': '( Jaapan , Subaru )',
        'type'   : 'parenthesis_title_words',
        '_priority_': (0, 0, 2, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (['''+uc_letter+lc_letter+'''0-9]+\s)                        # preceding word
            (\(\s*                                                       # starts with '('
                ('''+titlecase_word+''')                                 # titlecase word 
                (-'''+titlecase_word+''')?                               # hyphen + titlecase word (optional)
                \s?                                                      # space
                (,'''+titlecase_word+'''\s)?                             # comma + titlecase word 
            \s*\))                                                       # ends with ')'
            ''', re.X),
        '_group_': 2 },\
        
      # Partly based on PATT_72 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures 2 (space-separated) titlecase words inside parenthesis;',
        'example': '( Tallinna Wado )',
        'type'   : 'parenthesis_title_words',
        '_priority_': (0, 0, 2, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                     # starts with '('
                ('''+titlecase_word+''')               # titlecase word 
                (-'''+titlecase_word+''')?             # hyphen + titlecase word (optional)
                \s+                                    # space
                ('''+titlecase_word+''')               # titlecase word
                (-'''+titlecase_word+''')?             # hyphen + titlecase word (optional)
            \s*\))                                     # ends with ')'
            ''', re.X),
        '_group_': 1 },\

      # Partly based on PATT_62 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures ordinal number inside parenthesis, maybe accompanied by a word;',
        'example': '( 3. koht ) või ( WTA 210. )',
        'type'   : 'parenthesis_ordinal_numbers',
        '_priority_': (0, 0, 2, 3),
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

      # Partly based on PATT_45 from https://github.com/EstSyntax/preprocessing-module (tea)
      #          and on PATT_80 from https://github.com/kristiinavaik/ettenten-eeltootlus 
      { 'comment': 'Captures content inside square brackets #1 (numeric references);',
        'example': 'Nurksulgudes viited, nt [9: 5] või [9 lk 5]',
        'type'   : 'brackets_ref',
        '_priority_': (0, 0, 3, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (\[\s?                          # starts with '['
                (\d+\s[^\ \[\]]{1,2}\s\d+|  # a) numbers + space + few non-spaces + space + numbers, or
                 \d+:\s?\d+|                # b) numbers + colon + space + numbers, or
                 \d+,\d+|                   # c) numbers + comma + numbers, or
                 \d+)                       # d) only numbers
            \s?\])                          # ends with ']'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures content inside square brackets #2 (non-numeric stuff);',
        'example': 'Nt [Viide2006]',
        'type'   : 'brackets',
        '_priority_': (0, 0, 3, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\[                              # starts with '['
                (?!at\]|\s?\d)               # look-ahead: not '[at]' (inside e-mail) nor number
                [^\s\[\]]+                   # sequence of non-whitespace/non-brackets symbols 
            \])                              # ends with ']'
            ''', re.X),
        '_group_': 1 },\
        
      #{ 'comment': 'Captures TODO',
      #  'example': '',
      #  'type'   : 'parenthesis_ref',
      #  '_priority_': (0, 0, 4, 1),
      #  '_regex_pattern_': re.compile(\
      #      r'''
      #      (\(                                                        # starts with '('
      #        [^()]+                                                   # non-parenthesis
      #        (                                                        #
      #           \s*\d+\.?\s*                                          # a number (potentially year)
      #        )                                                        #
      #      \))                                                        # ends with ')'
      #      ''', re.X),
      #}
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

