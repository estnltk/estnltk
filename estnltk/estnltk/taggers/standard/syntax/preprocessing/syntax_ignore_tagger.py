#
#  Tags text snippets that should be ignored during the syntactic analysis.
#  
from estnltk.taggers import Tagger
from estnltk.legacy.dict_taggers.regex_tagger import RegexTagger
from estnltk import Annotation, EnvelopingBaseSpan, EnvelopingSpan, Layer

import regex as re

_lc_letter      = 'a-zöäüõžš'
_uc_letter      = 'A-ZÖÄÜÕŽŠ'
_titlecase_word = '['+_uc_letter+']['+_lc_letter+']+'
_hyphen_pat     = '(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015|-)'
_start_quotes   = '"\u00AB\u02EE\u030B\u201C\u201D\u201E'
_end_quotes     = '"\u00BB\u02EE\u030B\u201C\u201D\u201E'
_three_lc_words = r'['+_lc_letter+r']+\s+['+_lc_letter+r']+\s+['+_lc_letter+r']+'
_clock_time     = r'((0|\D)[0-9]|[12][0-9]|2[0123])\s?:\s?([0-5][0-9])'
_clock_time_2   = r'(0?[0-9]|[12][0-9]|2[0123])\s?[.:]\s?([0-5][0-9])'
_comma_ucase_list_item = r',\s*['+_uc_letter+r']'


_contains_number_compiled  = re.compile(r'\d+')
_contains_letter_compiled  = re.compile('['+_uc_letter+_lc_letter+']')
_three_lc_words_compiled   = re.compile(_three_lc_words)
_colon_start_compiled      = re.compile(r'^[^: ]+(\s+[^: ]+)?(\s+[^: ]+)?\s*:')
_enum_ucase_num_compiled   = re.compile(r'^(?=\D*\d)(\d+\s*(\.\s|\s))?['+_uc_letter+']')
_enum_num_compiled         = re.compile(r'^\d+\s*\.?\s?$')
_clock_time_start_compiled = re.compile(r'^\s*'+_clock_time_2+r'\s*'+_hyphen_pat+r'+\s*'+_clock_time_2+
                                        r'(?!\s*['+_lc_letter+r'])\s*.')

# ===================================================================
#  Patterns for capturing text snippets that should be ignored;
#
#  Note: these patterns are partly based on the patterns defined in:
#      * https://github.com/kristiinavaik/ettenten-eeltootlus
#      * https://github.com/EstSyntax/preprocessing-module
#
# ===================================================================

ignore_patterns = [ 
      # Partly based on PATT_BRACS from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures sequences of 1-3 symbols in parentheses;',
        'example': 'Tal on kaks tütart - Beatrice ( 9 ) ja Eugenie ( 8 ).',
        'type'   : 'parentheses_1to3',
        '_priority_': (0, 0, 1, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s                                                          # starts with '('
              (                                                            #
                (['''+_uc_letter+_lc_letter+r'''0-9,\-<>\[\]\/]{1,3}|\+)    # 1-3 symbols or +
              )                                                            #
              (                                                            #
                 \s(['''+_uc_letter+_lc_letter+r'''0-9,\-<>\[\]\/]{1,3}|\+) # 1-3 symbols or +
              )*                                                           #
            \s\))                                                          # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      # Note: in the previous pattern, a space is intentionally added after '(' and before ')' 
      #       in order to prevent extraction of optional word endings/prefixes, such as:
      #           ... sellest tulenevalt raamatukogu[(de)] võimalikkus ...
      #           ... Romaanilikkust [(re)]presenteerib Itaalia ...
      { 'comment': 'Captures at least 2 char sequences of 1-3 symbols in parentheses;',
        'example': '(x 1 , x 2 , ... , K , ... , x n)',
        'type'   : 'parentheses_1to3',
        '_priority_': (0, 0, 1, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                                             # starts with '('
              (                                                             #
                (['''+_uc_letter+_lc_letter+r'''0-9,.\-<>\[\]\/]{1,3}|\+)    # 1-3 symbols or +
              )                                                             #
              (                                                             #
                 \s(['''+_uc_letter+_lc_letter+r'''0-9,.\-<>\[\]\/]{1,3}|\+) # 1-3 symbols or +
              )+                                                            #
            \))                                                             # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures sequences of 1-4 non-letters in parentheses;',
        'example': 'Pariisi (1919) ja Tartu (1920) rahukonverentsid',
        'type'   : 'parentheses_1to4',
        '_priority_': (0, 0, 1, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                               # starts with '('
              (                                               #
                ([0-9,.\-<>\[\]\/]{1,4}|\+)                   # 1-4 non-letters or +
              )                                               #
              (                                               #
                 \s([0-9,.\-<>\[\]\/]{1,4}|\+)                # 1-4 non-letters or +
              )*                                              #
            \))                                               # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures sequences of 1-4 non-letters in parentheses;',
        'example': 'Pariis ( 1919 ) ja Tartu ( 1920 )',
        'type'   : 'parentheses_1to4',
        '_priority_': (0, 0, 1, 4),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                            # starts with '('
              (                                               #
                ([0-9,.\-<>\[\]\/]{4}|\+)                     # 4 non-letters or +
              )                                               #
              (                                               #
                 \s([0-9,.\-<>\[\]\/]{1,4}|\+)                # 1-4 non-letters or +
              )*                                              #
            \s*\))                                            # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures birth or death years inside parentheses;',
        'example': '( s.1978 ) või ( sünd. 1978 ) või ( surnud 1978 )',
        'type'   : 'parentheses_birdeah_year',
        '_priority_': (0, 0, 1, 5),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                               # starts with '('
              (s|(sünd|sur[nm])['''+_lc_letter+r''']*)\s*\.?\s*   # birth/death
              (                                                  #
                ([0-9,.\-+]{4,5})                                # a year-number like sequence
              )                                                  #
            \s*\))                                               # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures sequences of parenthesized uppercase letters and numbers, which do not include whitespace.',
        'example': 'ksülitool (E967), sorbitool (E420), mannitool (E421), laktitool (E966) jt.',
        'type'   : 'parentheses_ucase_number_seq',
        '_priority_': (0, 0, 1, 6),
        '_regex_pattern_': re.compile(\
            r'''
            [^'''+_uc_letter+r''']                             # preceding char is not ucase letter
            (\(                                               # starts with '('
               (?=[^()]*['''+_uc_letter+r'''])                 # look ahead: ucase letter inside parentheses
               ['''+_uc_letter+r'''0-9.]+                      # sequence of ucase letters, numbers, puncts
             \))                                              #  ends with ')'
             [^'''+_uc_letter+r''']                            # following char is not ucase letter
            ''', re.X),
        '_group_': 1 },\

      # Partly based on PATT_55 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures 1-2 comma-separated titlecase words inside parentheses;',
        'example': '( Jaapan , Subaru )',
        'type'   : 'parentheses_title_words',
        '_priority_': (0, 0, 2, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (['''+_uc_letter+_lc_letter+r'''0-9]+\s)          # preceding word
            (\(\s*                                           # starts with '('
                ('''+_titlecase_word+r''')                    # titlecase word 
                (-'''+_titlecase_word+r''')?                  # hyphen + titlecase word (optional)
                \s?                                          # space
                (,'''+_titlecase_word+r'''\s)?                # comma + titlecase word 
            \s*\))                                           # ends with ')'
            ''', re.X),
        '_group_': 2 },\
        
      # Partly based on PATT_72 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures 2 (space-separated) titlecase words inside parentheses;',
        'example': '( Tallinna Wado )',
        'type'   : 'parentheses_title_words',
        '_priority_': (0, 0, 2, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                     # starts with '('
                ('''+_titlecase_word+r''')              # titlecase word 
                (-'''+_titlecase_word+r''')?            # hyphen + titlecase word (optional)
                \s+                                    # space
                ('''+_titlecase_word+r''')              # titlecase word
                (-'''+_titlecase_word+r''')?            # hyphen + titlecase word (optional)
            \s*\))                                     # ends with ')'
            ''', re.X),
        '_group_': 1 },\

      # Partly based on PATT_62 from https://github.com/EstSyntax/preprocessing-module (aja)
      { 'comment': 'Captures ordinal number inside parentheses, maybe accompanied by a word;',
        'example': '( 3. koht ) või ( WTA 210. )',
        'type'   : 'parentheses_num_word',
        '_priority_': (0, 0, 2, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (['''+_uc_letter+_lc_letter+r'''0-9]+\s)    # preceding word
            (\(\s*                                     # starts with '('
                (\d+\s?\.                              # ordinal number 
                  (\s['''+_lc_letter+r''']+)?|          #   followed by lc word, or 
                 '''+_uc_letter+r'''+                   # uc word
                  \s\d+\s?\.)                          #   followed by ordinal number 
            \s*\))                                     # ends with ')'
            ''', re.X),
        '_group_': 2 },\
      { 'comment': 'Captures parentheses containing titlecased word(s) followed by comma and number(s);',
        'example': '( New York , 1994 ) või ( PM , 25.05. ) või ( Šveits , +0.52 )',
        'type'   : 'parentheses_num_comma_word',
        '_priority_': (0, 0, 2, 4),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                  # starts with '('
                ['''+_uc_letter+r''']+               # titlecased word start
                ['''+_lc_letter+r'''\-]*             # titlecased word content
                ((\s+|\s*/\s*)                      # separator: space or slash
                   ['''+_uc_letter+r''']+            # next titlecased word start (optional)
                   ['''+_lc_letter+r'''-]*){0,2}     # next titlecased word (optional)
                (\s?,\s?)                           # separating comma content
                (?=[^()]*\d)                        # look-ahead: should contain a number
                ([0-9,.\-<>\[\]\/+])+               # non-letters / non-spaces (optional)
            \s*\))                                  # ends with ')'
            ''', re.X),
        '_group_': 1 },\

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
        
      # Partly based on PATT_12 from https://github.com/EstSyntax/preprocessing-module 
      #                          and https://github.com/kristiinavaik/ettenten-eeltootlus 
      { 'comment': 'Captures parentheses that contain a numeric range, and less than 3 surrounding words;',
        'example': '(600–800 sõna) või (u AD 450–1050) või ( 2.03.1900 -16.09.1975 )',
        'type'   : 'parentheses_num_range',
        '_priority_': (0, 0, 4, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                     # starts with '('
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                [^()]*                              # some content after range (optional)
                \d+\s*\.?\s*                        # first number
                '''+_hyphen_pat+r'''+               # hyphen, dash etc.
                \d+\s*\.?\s*                        # second number
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                [^()]*                              # some content after range (optional)
            \))                                     # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures parentheses that likely contain date/time;',
        'example': '(22.08.2010 18:11:32)',
        'type'   : 'parentheses_datetime',
        '_priority_': (0, 0, 4, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                  # starts with '('
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                (?=[^()]*[12][05-9]\d\d)            # look-ahead: require a year-like number
                (?=[^()]*'''+_clock_time+r''')      # look-ahead: require a clock-time-like number
                [^()]*                              # some content (different date formats possibly)
            \s*\))                                  # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures parentheses likely containing a reference with year number;',
        'example': '( PM 3.02.1998 ) või ( “ Kanuu ” , 1982 ) või ( Looming , 1999 , nr.6 )',
        'type'   : 'parentheses_ref_year',
        '_priority_': (0, 0, 4, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                  # starts with '('
                ['''+_uc_letter+_start_quotes+r'''] # titlecase word, or starting quotes
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                (?=[^()]*[12][05-9]\d\d)            # look-ahead: require a year-like number
                [^()]*                              # content
            \s*\))                                  # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures parentheses likely containing a reference with quotes, and a number;',
        'example': '( “ Postimees ” , 12. märts ) või ("Preester , rabi ja blondiin", 2000)',
        'type'   : 'parentheses_ref_quotes_num',
        '_priority_': (0, 0, 4, 4),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                        # starts with '('
                (?=[^()]*\s*,\s*\D{0,3}\s*\d)             # look-ahead: there should comma + number somewhere
                [^()]*                                    # some content (optional)
                ['''+_start_quotes+r''']                  # starting quotes
                [^'''+_start_quotes+_end_quotes+r'''()]+  # some content
                ['''+_end_quotes+r''']                    # ending quotes
                [^()]*                                    # some content (optional)
            \s*\))                                        # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures parentheses that likely contain references to paragraphs;',
        'example': '( §2, 4, 6, 7 ) või ( §-d 979 , 980 ) või ( § 970 , vt. §-d 683 , 670 )',
        'type'   : 'parentheses_ref_paragraph',
        '_priority_': (0, 0, 4, 5),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                  # starts with '('
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                [^()]*                              # random content
                §(-?[a-z]{1,3})?\s*\d               # look-ahead: require a year-like number
                (?![^()]*'''+_three_lc_words+r''')  # look-ahead: block if there are 3 lowercase words
                [^()]*                              # random content
            \s*\))                                  # ends with ')'
            ''', re.X),
        '_group_': 1 },\
      { 'comment': 'Captures parentheses containing numbers and punctuation (unrestricted length);',
        'example': '( 54,71 /57 , 04 ) või ( 195,0 + 225,0 )',
        'type'   : 'parentheses_num',
        '_priority_': (0, 0, 4, 6),
        '_regex_pattern_': re.compile(\
            r'''
            (\(\s*                                 # starts with '('
               (?=[^()]*\d)                        # look-ahead: should contain numbers
               [0-9;:,.\-<>\[\]\/\\+\s]+           # numbers + punctuation + spaces
            \s*\))                                 # ends with ')'
            ''', re.X),
        '_group_': 1 },\

      # Very greedy patterns
      # ( ... if parentheses contain a number and less than 3 consecutive lc words, then ignore their content ... )
      { 'comment': 'Captures content inside parentheses ending with a number (and containing less than 3 lc words)',
        'example': '(Rm 9:4 – 5), (mudelid PI70 ja PI90), (Rookopli 18), (meie puhul 165/80), (1920 x 1080)',
        'type'   : 'parentheses_num_end_uncategorized',
        '_priority_': (0, 0, 5, 1),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                           # starts with '('
              (?![^()]*'''+_three_lc_words+r''')          # look-ahead: block if there are 3 lowercase words
              [^()]+                                      # non-parenthesis
              \s*\d+\.?\s*                                # a number
            \))                                           # ends with ')'
            ''', re.X),
        '_group_': 1 
      },
      { 'comment': 'Captures content inside parentheses starting with a number (and containing less than 3 lc words)',
        'example': '(23%), (2 päeva, osavõtutasu 250 eurot), (13 ja 4 aastased), (300 000 000 m/sek), (46,8 p 60-st)',
        'type'   : 'parentheses_num_start_uncategorized',
        '_priority_': (0, 0, 5, 2),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                          # starts with '('
              \s*\d+                                     # a number 
              (?![^()]*'''+_three_lc_words+r''')         # look-ahead: block if there are 3 lowercase words
              [^()]+                                     # non-parenthesis
            \))                                          # ends with ')'
            ''', re.X),
        '_group_': 1 
      },
      { 'comment': 'Captures parentheses containing a number in the middle (and containing less than 3 lc words)',
        'example': '( Sonera osalus 42,8 protsenti ), ( ligi 100 000 krooni ), ( naised 5 km , mehed 7,5 km )',
        'type'   : 'parentheses_num_mid_uncategorized',
        '_priority_': (0, 0, 5, 3),
        '_regex_pattern_': re.compile(\
            r'''
            (\(                                          # starts with '('
              (?![^()]*'''+_three_lc_words+r''')         # look-ahead: block if there are 3 lowercase words
              [^()0-9]+                                  # non-numbers
              \s*\d+                                     # a number 
              [^()]+                                     # non-parenthesis
            \))                                          # ends with ')'
            ''', re.X),
        '_group_': 1 
      },
]


# ===================================================================
#   T h e   m a i n   c l a s s
# ===================================================================

class SyntaxIgnoreTagger( Tagger ):
    """Tags text snippets that should be ignored during the syntactic analysis."""
    output_layer      = 'syntax_ignore'
    output_attributes = ('type',)
    input_layers      = ['words', 'sentences']
    conf_param = [ # Configuration flags:
                   'allow_loose_match',
                   'ignore_parenthesized_num',
                   'ignore_parenthesized_num_greedy',
                   'ignore_parenthesized_ref',
                   'ignore_parenthesized_title_words',
                   'ignore_parenthesized_short_char_sequences',
                   'ignore_consecutive_parenthesized_sentences',
                   'ignore_consecutive_enum_ucase_num_sentences',
                   'ignore_sentences_consisting_of_numbers',
                   'ignore_sentences_starting_with_time',
                   'ignore_sentences_with_comma_separated_num_name_lists',
                   'ignore_brackets',
                   # Names of the specific input layers
                   '_input_words_layer', '_input_sentences_layer',
                   # Inner parameter(s)
                   '_syntax_ignore_hints_tagger',
                 ]

    def __init__(self, output_layer:str='syntax_ignore',
                       input_words_layer:str='words',
                       input_sentences_layer:str='sentences',
                       allow_loose_match:bool = True,
                       ignore_parenthesized_num:bool = True,
                       ignore_parenthesized_num_greedy:bool = True,
                       ignore_parenthesized_ref:bool = True,
                       ignore_parenthesized_title_words:bool = True,
                       ignore_parenthesized_short_char_sequences:bool  = True,
                       ignore_consecutive_parenthesized_sentences:bool = True,
                       ignore_consecutive_enum_ucase_num_sentences:bool = True,
                       ignore_sentences_consisting_of_numbers:bool = True,
                       ignore_sentences_starting_with_time:bool = True,
                       ignore_sentences_with_comma_separated_num_name_lists:bool = True,
                       ignore_brackets:bool = True,):
        """Initializes SyntaxIgnoreTagger.
        
        Parameters
        ----------
        output_layer: str (default: 'syntax_ignore')
            Name for the syntax_ignore layer;
        
        input_words_layer: str (default: 'words')
            Name of the input words layer;

        input_sentences_layer: str (default: 'sentences')
            Name of the input sentences layer;
        
        allow_loose_match: boolean (default: True)
            If True, then an ignore text snippet may consume words without 
            matching exactly with their boundaries (e.g. ignore snippet's start 
            does not have to match word's start). If False, then an ignore text 
            snippet must match exactly with word boundaries: it must start where 
            a word starts, and end where a word ends.

        ignore_parenthesized_num: boolean (default: True)
            Parenthesized numerics (such as dates, date ranges, number sequences) 
            will be ignored.

        ignore_parenthesized_num_greedy: boolean (default: True)
            Applies greedy parenthesized numeric content detection patterns: if 
            there is at least one number inside parentheses, but there cannot be 
            found at least 3 consecutive lowercase words, then the whole content 
            inside parentheses will be marked as to be ignored.

        ignore_parenthesized_ref: boolean (default: True)
            Parenthesized content which looks like a reference (e.g. contains 
            titlecased words, and date information) will be ignored.

        ignore_parenthesized_title_words: boolean (default: True)
            Parenthesized 1-2 titlecase words (which may be comma-separated) will 
            be ignored.

        ignore_parenthesized_short_char_sequences: boolean (default: True)
            Parenthesized short sequences of tokens (up to 4 tokens), each of 
            which also has as short length (up to 4 characters), will be ignored.

        ignore_brackets: boolean (default: True)            
            Content inside square brackets will be ignored.
            
        ignore_consecutive_parenthesized_sentences: boolean (default: True)
            If consecutive sentences all contain parenthesized content that is 
            already ignored, and all of these sentences contain less than 3 
            consecutive lowercase words, then these sentences will also be 
            ignored.
        
        ignore_consecutive_enum_ucase_num_sentences: boolean (default: True)
            Ignores sentences that match the following conditions: 
            1) start with an uppercase letter, or an ordinal number followed 
               by an uppercase letter, or an ordinal number; 
            2) contain at least one number; 
            3) do not contain 3 consecutive lowercase words; 
            4) are a part of at least 4 consecutive sentences that have the 
               same properties (1, 2 and 3).
        
        ignore_sentences_consisting_of_numbers: boolean (default: True)
            Ignores sentences that only contain number or numbers, no letters, 
            and do not end with '!' nor '?'.
        
        ignore_sentences_starting_with_time: boolean (default: True)
            Sentences starting with a date range (e.g. a time schedule of a 
            seminar or a TV program) will be ignored.

        ignore_sentences_with_comma_separated_num_name_lists: boolean (default: True)
            Sentences containing comma separated list of titlecase words / 
            numbers ( like sport results, player/country listings, game scores 
            etc.) will be ignored.
        """
        # Set input/output layer names
        self.output_layer           = output_layer
        self.output_attributes      = ('type',)
        self._input_words_layer     = input_words_layer
        self._input_sentences_layer = input_sentences_layer
        self.input_layers           = [input_words_layer, input_sentences_layer]
        # Set configuration flags
        self.allow_loose_match = allow_loose_match
        self.ignore_parenthesized_num=ignore_parenthesized_num
        self.ignore_parenthesized_num_greedy=ignore_parenthesized_num_greedy
        self.ignore_parenthesized_ref=ignore_parenthesized_ref
        self.ignore_parenthesized_title_words=ignore_parenthesized_title_words
        self.ignore_parenthesized_short_char_sequences=ignore_parenthesized_short_char_sequences
        self.ignore_consecutive_parenthesized_sentences=ignore_consecutive_parenthesized_sentences
        self.ignore_consecutive_enum_ucase_num_sentences=ignore_consecutive_enum_ucase_num_sentences
        self.ignore_sentences_consisting_of_numbers=ignore_sentences_consisting_of_numbers
        self.ignore_sentences_starting_with_time=ignore_sentences_starting_with_time
        self.ignore_sentences_with_comma_separated_num_name_lists=ignore_sentences_with_comma_separated_num_name_lists
        self.ignore_brackets=ignore_brackets
        # Populate vocabulary according to given settings
        patterns = []
        for ignore_pat in ignore_patterns:
            if ignore_pat['type'].startswith('parentheses_num') and \
               ignore_pat['type'].endswith('uncategorized'):
                # Allow/disallow greedy filtering of parentheses that contain numbers
                if self.ignore_parenthesized_num_greedy:
                    patterns.append( ignore_pat )
            elif (ignore_pat['type'] in ['parentheses_num_word', \
                  'parentheses_num_comma_word', 'parentheses_num_range', \
                  'parentheses_datetime', 'parentheses_num']):
                if self.ignore_parenthesized_num:
                    patterns.append( ignore_pat )
            elif ignore_pat['type'].startswith('parentheses_ref'):
                if self.ignore_parenthesized_ref:
                    patterns.append( ignore_pat )
            elif ignore_pat['type'].startswith('brackets'):
                if self.ignore_brackets:
                    patterns.append( ignore_pat )
            elif (ignore_pat['type'] in ['parentheses_1to3', \
                  'parentheses_1to4', 'parentheses_birdeah_year', \
                  'parentheses_ucase_number_seq']):
                if self.ignore_parenthesized_short_char_sequences:
                    patterns.append( ignore_pat )
            elif ignore_pat['type'].startswith('parentheses_title_words'):
                if self.ignore_parenthesized_title_words:
                    patterns.append( ignore_pat )
            else:
                patterns.append( ignore_pat )
        # Create a new tagger
        self._syntax_ignore_hints_tagger = RegexTagger(vocabulary=patterns,
                                                 output_attributes=['_priority_', 'type'],
                                                 priority_attribute='_priority_',
                                                 conflict_resolving_strategy="MAX",
                                                 overlapped=False,
                                                 output_layer='syntax_ignore_hints',
                                                 )

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        return Layer(name=self.output_layer,
                     enveloping=self._input_words_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     ambiguous=False)

    def _make_layer(self, text: 'Text', layers, status: dict):
        """Creates syntax_ignore layer.
        
        Parameters
        ----------
        text: Text
           Text object corresponding to the original text 
           which will be tagged;
          
        layers: MutableMapping[str, Layer]
           Layers of the raw_text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           the words and sentences layers.
          
        status: dict
           This can be used to store metadata on layer tagging.

        """
        layer = self._make_layer_template()
        layer.text_object = text

        # A) Apply RegexTagger to find text snippets that should be ignored
        conflict_status = {}
        hints_layer = self._syntax_ignore_hints_tagger.make_layer(text=text,
                                                                  layers=layers,
                                                                  status=conflict_status)
        words = layers[ self._input_words_layer ]
        # Create an alignment between words and spans
        wid = 0
        ignored_words_spans = []
        for sp in hints_layer:
            # Find words that fall within the span
            words_start = -1
            words_end   = -1
            current_wid = wid
            while current_wid < len(words):
                word = words[current_wid]
                # Exact match
                if word.start == sp.start:
                    words_start = current_wid
                if word.end   == sp.end:
                    words_end = current_wid
                if words_start != -1 and words_end != -1:
                    break
                # Loose match (if allowed)
                if self.allow_loose_match:
                    if word.start <= sp.start and sp.start <= word.end:
                        words_start = current_wid
                    if word.start <= sp.end and sp.end <= word.end:
                        words_end = current_wid
                if sp.end < word.start:
                    break
                current_wid += 1
            if words_start != -1 and words_end != -1:
                # Record ignored words
                spans = words[words_start:words_end+1]
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in spans), layer=layer)
                new_span.add_annotation(Annotation(new_span, type=sp.type))
                ignored_words_spans.append(new_span)
                #print('*',text.text[sp.start:sp.end], sp.start, sp.end)
                #print(words[words_start].start, words[words_end].end, new_spanlist.spans)
                # Advance in text
                wid = current_wid + 1

        # B) Add consecutive sentences containing ignored content 
        #        in parentheses and/or less than 3 lc words
        if self.ignore_consecutive_parenthesized_sentences:
            ignored_words_spans = \
                self._add_ignore_consecutive_parenthesized_sentences(text, layers, ignored_words_spans, layer)
        
        # C) Add sentences that start with time (e.g. a time schedule of a TV program)
        if self.ignore_sentences_starting_with_time:
            ignored_words_spans = \
                self._add_ignore_sentences_starting_with_time(text, layers, ignored_words_spans, layer)

        # D) Add sentences starting with an uppercase letter (or an ordinal number followed by 
        #        an uppercase letter), containing otherwise less than 3 lowercase words, and 
        #        forming lists of at least 4 consecutive sentences;
        if self.ignore_consecutive_enum_ucase_num_sentences:
            ignored_words_spans = \
                self._add_ignore_consecutive_enum_ucase_sentences(text,layers,ignored_words_spans, layer)

        # E) Add ignore sentences that consist of numbers only
        if self.ignore_sentences_consisting_of_numbers:
            ignored_words_spans = \
                self._add_ignore_sentences_consisting_of_numbers(text,layers,ignored_words_spans, layer)
        
        # F) Add ignore sentences that contain comma separated list of titlecase words /
        #        numbers (like sport results, player/country listings, game scores etc.)
        if self.ignore_sentences_with_comma_separated_num_name_lists:
            ignored_words_spans = \
                self._add_ignore_comma_separated_num_name_list_sentences(text,layers,ignored_words_spans, layer)
        
        # Finally: add spans to the layer
        for span in ignored_words_spans:
            layer.add_span(span)
        return layer

    def _add_ignore_consecutive_parenthesized_sentences( 
                self, text: 'Text', layers, ignored_words_spans:list, output_layer) -> list:
        """ First, detects consecutive sentences that:
            *) contain parenthesized ignore content (content from 
               ignored_words_spans) and,
            *) contain less than 3 consecutive lowercase words,
            and marks these sentences as 'ignored';
             
            Second, checks for sentences between the ignored sentences 
                 that contain less than 3 consecutive lowercase words:
                 and if found, marks such sentences also as 'ignored';
        """
        # Collect consecutive sentences containing ignored content 
        #         in parentheses and/or less than 3 lc words
        # 1) Collect candidates for ignored sentences
        ignored_sentence_candidates = []
        for sent_id, sentence_span in enumerate( layers[ self._input_sentences_layer ] ):
            ignored_words = []
            # collect ignored words inside sentences
            if ignored_words_spans:
                for ignore_span in ignored_words_spans:
                    if not ignore_span.type.startswith('parentheses'):
                        # consider only ignored content inside parentheses
                        continue
                    if sentence_span.start <= ignore_span.start and \
                       ignore_span.end <= sentence_span.end:
                        ignored_words.append( ignore_span )
            # check if the sentence does not contain 3 consecutive lc words
            sentence_text = sentence_span.enclosing_text
            misses_lc_words = not bool( _three_lc_words_compiled.search(sentence_text) )
            if misses_lc_words:
                ignore_item = { 'sent_id':sent_id, 'span': sentence_span, \
                                'ignored_words': ignored_words, 'ignore_sentence': False }
                ignored_sentence_candidates.append( ignore_item )
        # 2) Mark consecutive sentences containing ignored (parenthesized) word content as 'ignored'
        for ignored_sent_id, ignored_candidate in enumerate( ignored_sentence_candidates ):
            sent_id   = ignored_candidate['sent_id']
            sent_text = ignored_candidate['span'].enclosing_text
            contains_ignored = bool( ignored_candidate['ignored_words'] )
            consecutive = False
            if ignored_sent_id+1 < len( ignored_sentence_candidates ) and \
               ignored_sentence_candidates[ignored_sent_id+1]['sent_id'] == sent_id+1 and \
               contains_ignored and ignored_sentence_candidates[ignored_sent_id+1]['ignored_words']:
                consecutive = True
            elif ignored_sent_id-1 > -1 and \
                 ignored_sentence_candidates[ignored_sent_id-1]['sent_id'] == sent_id-1 and \
                 contains_ignored and ignored_sentence_candidates[ignored_sent_id-1]['ignored_words']:
                consecutive = True
            if consecutive:
                # Mark this sentence as 'ignored'
                ignored_candidate['ignore_sentence'] = True
        # 3) Mark consecutive sentences between previously detected ignored sentences as 'ignored'
        for ignored_sent_id, ignored_candidate in enumerate( ignored_sentence_candidates ):
            if ignored_candidate['ignore_sentence']:
                # Check if this sentence is followed by not-yet-ignored sentences, 
                #       and then again by ignored sentence(s)
                collected_sent_ids = []
                prev_sent_id = ignored_candidate['sent_id']
                j = ignored_sent_id + 1
                while j < len( ignored_sentence_candidates ):
                    sent_id = ignored_sentence_candidates[j]['sent_id']
                    if sent_id == prev_sent_id + 1:
                        if not ignored_sentence_candidates[j]['ignore_sentence']:
                            collected_sent_ids.append( j )
                        else:
                            # the next sentence is already ignored: stop
                            break
                    else:
                        # sentences are not consecutive: break
                        collected_sent_ids = []
                        break
                    prev_sent_id = sent_id
                    j += 1
                # If there were consecutive sentences between already ignored sentences,
                #    then mark these as 'ignored'
                if collected_sent_ids:
                    for collected_sid in collected_sent_ids:
                        # Mark as 'ignored'
                        ignored_sentence_candidates[collected_sid]['ignore_sentence'] = True
        # 4) Move all sentences that should be ignored to the list of ignored
        for ignored_candidate in ignored_sentence_candidates:
            if ignored_candidate['ignore_sentence']:
                # Collect words inside the sentence
                sent_words = []
                for word_span in ignored_candidate['span'].spans:
                    sent_words.append( word_span )
                # Make entire sentence as 'ignored'
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in sent_words),
                                          layer=output_layer)
                new_span.add_annotation(Annotation(new_span, type='consecutive_parenthesized_sentences'))
                # Remove overlapped spans
                if ignored_candidate['ignored_words']:
                    # Rewrite 'ignored_words_spans': leave out words inside 'ignored_words'
                    # of the current sentence (basically: remove overlapped ignore content)
                    new_ignored_words_spans = []
                    for ignore_span in ignored_words_spans:
                        if not ignore_span in ignored_candidate['ignored_words']:
                            new_ignored_words_spans.append( ignore_span )
                    ignored_words_spans = new_ignored_words_spans
                ignored_words_spans.append(new_span)
        return ignored_words_spans

    def _add_ignore_sentences_consisting_of_numbers( 
                self, text: 'Text', layers, ignored_words_spans:list, output_layer) -> list:
        """  Detects sentences that contain number or numbers, no letters
             and do not end with '?' nor '!', and marks such sentences as 
             ignore sentences (if they have note been marked already).
             Returns ignored_words_spans which is extended with new ignore 
             sentences;
        """
        for sent_id, sentence_span in enumerate( layers[ self._input_sentences_layer ] ):
            sentence_text   = sentence_span.enclosing_text
            contains_number = bool(_contains_number_compiled.search( sentence_text ))
            contains_letter = bool(_contains_letter_compiled.search( sentence_text ))
            if contains_number and not contains_letter and \
               not sentence_text.endswith('?') and not sentence_text.endswith('!'):
                # If the sentence contains only number (or numbers), and no
                # letters, then consider it as sentence to be 'ignored'
                # Collect words inside the sentence
                sent_words = []
                for word_span in sentence_span.spans:
                    sent_words.append( word_span )
                # Make entire sentence as 'ignored'
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in sent_words),
                                          layer=output_layer)
                new_span.add_annotation(Annotation(new_span, type='sentence_with_number_no_letters'))
                # Add the sentence only iff it is not already added
                add_sentence = True
                if ignored_words_spans:
                    # Check if it exists already
                    for ignore_span in ignored_words_spans:
                        if ignore_span.start == new_span.start and \
                           ignore_span.end == new_span.end:
                            add_sentence = False
                            break
                if add_sentence:
                    ignored_words_spans.append(new_span)
        return ignored_words_spans

    def _add_ignore_sentences_starting_with_time( 
                self, text: 'Text', layers, ignored_words_spans:list, output_layer) -> list:
        """  Detects sentences that start with a clock time, followed
             by a symbol that is not a lowercase letter. 
             Such sentences likely represent a part of a time schedule,
             and thus can be marked as ignore sentences.
             Returns ignored_words_spans which is extended with new ignore 
             sentences;
        """
        for sent_id, sentence_span in enumerate( layers[ self._input_sentences_layer ] ):
            sentence_text = sentence_span.enclosing_text
            if _clock_time_start_compiled.match( sentence_text ):
                # If the sentence begins with a clock time, it is likely 
                # a time schedule sentence (e.g. a TV schedule) which 
                # could be ignored 
                sent_words = []
                for word_span in sentence_span.spans:
                    sent_words.append( word_span )
                # Make entire sentence as 'ignored'
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in sent_words),
                                          layer=output_layer)
                new_span.add_annotation(Annotation(new_span, type='sentence_starts_with_time'))
                # Add the sentence only iff it is not already added
                add_sentence = True
                if ignored_words_spans:
                    # Check if it exists already
                    for ignore_span in ignored_words_spans:
                        if ignore_span.start == new_span.start and \
                           ignore_span.end == new_span.end:
                            add_sentence = False
                            break
                if add_sentence:
                    # Check for overlaps
                    if ignored_words_spans:
                        # Rewrite 'ignored_words_spans': leave out words inside 'ignored_words'
                        # of the current sentence (basically: remove overlapped ignore content)
                        new_ignored_words_spans = []
                        for ignore_span in ignored_words_spans:
                            if not (new_span.start <= ignore_span.start and
                                    ignore_span.end <= new_span.end):
                                new_ignored_words_spans.append( ignore_span )
                        ignored_words_spans = new_ignored_words_spans
                    # After overlaps have been removed, add the span
                    ignored_words_spans.append( new_span )
        return ignored_words_spans

    def _add_ignore_consecutive_enum_ucase_sentences(
            self, text: 'Text', layers, ignored_words_spans:list, output_layer) -> list:
        """ Detects sentences that:
             1) start with an uppercase letter, or an ordinal number 
               followed by an uppercase letter, or an ordinal number;
             2) contain at least one number;
             3) does not contain 3 consecutive lowercase words;
             4) are a part of at least 4 consecutive sentences
                that have the same properties (1, 2 and 3);
            Before adding detected sentences to ignored_words_spans,
            checks that sentences are not already added (by other methods),
            and removes elements of ignored_words_spans that are inside
            newly ignored sentences.
            
            Returns ignored_words_spans which is extended with new ignore 
            sentences;
        """
        # 1) Collect candidates for ignored sentences
        ignored_sentence_candidates = []
        for sent_id, sentence_span in enumerate( layers[ self._input_sentences_layer ] ):
            ignored_words = []
            # check if the sentence does not contain 3 consecutive lc words
            sentence_text = sentence_span.enclosing_text
            misses_lc_words = not bool( _three_lc_words_compiled.search(sentence_text) )
            enum_num       = bool( _enum_num_compiled.match(sentence_text) )
            enum_ucase_num = bool( _enum_ucase_num_compiled.match(sentence_text) )
            if misses_lc_words:
                ignore_item = { 'sent_id':sent_id, 'span': sentence_span,
                                'enum_ucase_num': enum_ucase_num,
                                'enum_num': enum_num,
                                'consecutive_with_next': False,
                                'consecutive_with_prev': False,
                                'ignore_sentence': False}
                ignored_sentence_candidates.append( ignore_item )
        # 2) Mark consecutive sentences starting with enumerations / uppercase letters, and 
        #   contain numbers
        for ignored_sent_id, ignored_candidate in enumerate( ignored_sentence_candidates ):
            sent_id   = ignored_candidate['sent_id']
            sent_text = ignored_candidate['span'].enclosing_text
            consecutive = False
            if ignored_sent_id+1 < len( ignored_sentence_candidates ) and \
               ignored_sentence_candidates[ignored_sent_id+1]['sent_id'] == sent_id+1 and \
               (ignored_candidate['enum_ucase_num'] or
                ignored_candidate['enum_num']) and \
               (ignored_sentence_candidates[ignored_sent_id+1]['enum_ucase_num'] or
                ignored_sentence_candidates[ignored_sent_id+1]['enum_num']):
                ignored_candidate['consecutive_with_next'] = True
            elif ignored_sent_id-1 > -1 and \
                 ignored_sentence_candidates[ignored_sent_id-1]['sent_id'] == sent_id-1 and \
                 (ignored_candidate['enum_ucase_num'] or
                  ignored_candidate['enum_num']) and \
                 (ignored_sentence_candidates[ignored_sent_id-1]['enum_ucase_num'] or
                  ignored_sentence_candidates[ignored_sent_id-1]['enum_num']):
                ignored_candidate['consecutive_with_prev'] = True
        # 3) Collects groups of sentences containing at least 4 consecutive sentences
        #    with the required properties; Marks these sentences as 'to be ignored'
        consecutive = []
        for ignored_candidate in ignored_sentence_candidates:
            if ignored_candidate['consecutive_with_next']:
                consecutive.append( ignored_candidate )
            elif not ignored_candidate['consecutive_with_next'] and \
                     ignored_candidate['consecutive_with_prev']:
                consecutive.append( ignored_candidate )
                if len(consecutive) > 3:
                    # Mark collected consecutive sentences as 'ignored'
                    for candidate in consecutive:
                        candidate['ignore_sentence'] = True
                consecutive = []
            else:
                consecutive = []
        # 4) Insert all sentences that should be ignored into the list of ignored;
        #    Perform check-ups and filterings before insertions
        for ignored_candidate in ignored_sentence_candidates:
            if ignored_candidate['ignore_sentence']:
                # Collect words inside the sentence
                sent_words = []
                for word_span in ignored_candidate['span'].spans:
                    sent_words.append( word_span )
                # Make entire sentence as 'ignored'
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in sent_words),
                                          layer=output_layer)
                new_span.add_annotation(Annotation(new_span, type='consecutive_enum_ucase_sentences'))
                # Add the sentence only iff it is not already added
                add_sentence = True
                if ignored_words_spans:
                    # Check if it exists already
                    for ignore_span in ignored_words_spans:
                        if ignore_span.start == new_span.start and \
                           ignore_span.end == new_span.end:
                            add_sentence = False
                            break
                if add_sentence:
                    # Check for overlaps
                    if ignored_words_spans:
                        # Rewrite 'ignored_words_spans': leave out words inside 'ignored_words'
                        # of the current sentence (basically: remove overlapped ignore content)
                        new_ignored_words_spans = []
                        for ignore_span in ignored_words_spans:
                            if not (new_span.start <= ignore_span.start and
                                    ignore_span.end <= new_span.end):
                                new_ignored_words_spans.append( ignore_span )
                        ignored_words_spans = new_ignored_words_spans
                    # After overlaps have been removed, add the span
                    ignored_words_spans.append( new_span )
        return ignored_words_spans

    def _add_ignore_comma_separated_num_name_list_sentences( 
                self, text: 'Text', layers, ignored_words_spans:list, output_layer) -> list:
        """ Detects sentences that:
            Contain less than 3 consecutive lowercase words, and 
               1.1) Start with up to three words and colon, or 
                      contain at least 2 colons;
               1.2) Contain at least 1 number;
               1.3) Contain at least 3 commas followed by uppercase 
                      word;
            or:
               2.1) Contain at least 2 hyphens followed by uppercase
                    words;
               2.2) Contain at least 2 commas, 2 colons and 1 number;
            
            In many cases, sentences that have these properties contain
            lists of sport results (e.g. names / countries, game scores 
            etc.);
            Returns ignored_words_spans which is extended with new ignore 
            sentences;
        """
        # 1) Collect candidates for ignored sentences
        ignored_sentence_candidates = []
        for sent_id, sentence_span in enumerate( layers[ self._input_sentences_layer ] ):
            ignored_words = []
            # check if the sentence has required properties
            sentence_text = sentence_span.enclosing_text
            misses_lc_words    = not bool( _three_lc_words_compiled.search(sentence_text) )
            comma_ucase_items  = len( re.findall(_comma_ucase_list_item, sentence_text) )
            hyphen_ucase_items = len( re.findall(_hyphen_pat+r'\s*['+_uc_letter+r']', sentence_text) )
            number_items       = len( re.findall(r'\d+', sentence_text) )
            colon_items        = sentence_text.count(':')
            comma_items        = sentence_text.count(',')
            colon_start        = bool( _colon_start_compiled.match(sentence_text) )
            if misses_lc_words and comma_ucase_items >= 3 and \
               number_items > 0 and (colon_items > 1 or colon_start):
                ignore_item = { 'sent_id':sent_id, 'span': sentence_span,
                                'ignore_sentence': True }
                ignored_sentence_candidates.append( ignore_item )
            elif misses_lc_words and hyphen_ucase_items >= 2 and \
                 comma_items >= 2 and colon_items >= 2 and number_items >= 1:
                ignore_item = {'sent_id':sent_id, 'span': sentence_span,
                               'ignore_sentence': True }
                ignored_sentence_candidates.append( ignore_item )
        # 2) Insert all sentences that should be ignored into the list of ignored;
        #    Perform check-ups and filterings before insertions
        for ignored_candidate in ignored_sentence_candidates:
            if ignored_candidate['ignore_sentence']:
                # Collect words inside the sentence
                sent_words = []
                for word_span in ignored_candidate['span'].spans:
                    sent_words.append( word_span )
                # Make entire sentence as 'ignored'
                new_span = EnvelopingSpan(base_span=EnvelopingBaseSpan(s.base_span for s in sent_words),
                                          layer=output_layer)
                new_span.add_annotation(Annotation(new_span, type='sentence_with_comma_separated_list'))
                # Add the sentence only iff it is not already added
                add_sentence = True
                if ignored_words_spans:
                    # Check if it exists already
                    for ignore_span in ignored_words_spans:
                        if ignore_span.start == new_span.start and \
                           ignore_span.end == new_span.end:
                            add_sentence = False
                            break
                if add_sentence:
                    # Check for overlaps
                    if ignored_words_spans:
                        # Rewrite 'ignored_words_spans': leave out words inside 'ignored_words'
                        # of the current sentence (basically: remove overlapped ignore content)
                        new_ignored_words_spans = []
                        for ignore_span in ignored_words_spans:
                            if not (new_span.start <= ignore_span.start and
                                    ignore_span.end <= new_span.end):
                                new_ignored_words_spans.append( ignore_span )
                        ignored_words_spans = new_ignored_words_spans
                    # After overlaps have been removed, add the span
                    ignored_words_spans.append( new_span )
        return ignored_words_spans
