#
#  Tags sentence boundaries, and applies post-correction rules to sentence tokenization.
#
from typing import Iterator, Tuple
from typing import MutableMapping

import re

from estnltk import SpanList
from estnltk import Layer
from estnltk.taggers import Tagger

_hyphen_pat = '(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015|-)'
_lc_letter  = '[a-zöäüõžš]'
_uc_letter  = '[A-ZÖÄÜÕŽŠ]'
_not_letter = '[^A-ZÖÄÜÕŽŠa-zöäüõžš]'
_start_quotes  = '"\u00AB\u02EE\u030B\u201C\u201E'
_ending_quotes = '"\u00BB\u02EE\u030B\u201D\u201E'
# regexp for matching a single token consisting only of sentence-ending punctuation
_ending_punct_regexp = re.compile('^[.?!…]+$')

# regexps for quotation mark counting corrections:
_starting_quotes_regexp   = re.compile('^['+_start_quotes+']$')
_ending_quotes_regexp     = re.compile('^['+_ending_quotes+']$')
_indistinguishable_quotes = re.compile('^["\u02EE\u030B\u201E]$') # not clear, if start or end

# Patterns describing how two mistakenly split 
# adjacent sentences can be merged into one sentence
merge_patterns = [
   # ***********************************
   #   Fixes related to numbers, number ranges, dates and times 
   # ***********************************
   #   {Numeric_range_start} {period} + {dash} {Numeric_range_end}
   { 'comment'  : '{Numeric_range_start} {period} + {dash} {Numeric_range_end}', \
     'example'  : '"Tartu Muinsuskaitsepäevad toimusid 1988. a 14." + "- 17. aprillil."', \
     'fix_type' : 'numeric_range', \
     'regexes'  : [re.compile(r'(.+)?([0-9]+)\s*\.$', re.DOTALL),re.compile(_hyphen_pat+r'\s*([0-9]+)\s*\.(.*)?$', re.DOTALL)], \
   },
   #   {Numeric_range_start} {period} {dash} + {Numeric_range_end}
   { 'comment'  : '{Numeric_range_start} {period} {dash} + {Numeric_range_end}', \
     'example'  : '"Tartu Muinsuskaitsepäevad toimusid 1988. a 14." + "- 17. aprillil."', \
     'fix_type' : 'numeric_range', \
     'regexes'  : [re.compile(r'(.+)?([0-9]+)\s*\.\s*'+_hyphen_pat+'$', re.DOTALL), re.compile(r'([0-9]+)\s*\.(.+)?$', re.DOTALL) ], \
   },

   #   {Numeric_year} {period} {|a|} + {lowercase_or_number}
   { 'comment'  : '{Numeric_year} {period} {|a|} + {lowercase_or_number}', \
     'example'  : '"Luunja sai vallaõigused 1991.a." + " kevadel."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{3,4})\s*\.?\s*a\s*\.$', re.DOTALL), re.compile('^('+_lc_letter+'|[0-9])+')], \
   },
   { 'comment'  : '{Numeric_year} {period} {|a|} + {lowercase_or_number}', \
     'example'  : '"1946/47 õ.a." + "oli koolis 87 õpilast."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile(r'(^|.+)([0-9]{4}\s*\.?|/\s*[0-9]{2})\s*õ\s*\.?\s*a\.?$', re.DOTALL), re.compile('^('+_lc_letter+'|[0-9])+')], \
   },
   #   {Numeric_year} {period} + {|a|} {lowercase_or_number}
   { 'comment'  : '{Numeric_year} {period} + {|a|} {lowercase_or_number}', \
     'example'  : '"Luunja sai vallaõigused 1991.a." + " kevadel."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [ re.compile(r'(.+)?([0-9]{4})\s*\.$', re.DOTALL), re.compile(r'^\s*(õ\s*\.)?a\.?\s*('+_lc_letter+'|[0-9])+') ], \
   },
   #   {Numeric_year} {period} + {|aasta|}
   { 'comment'  : '{Numeric_year} {period} + {|aasta|}', \
     'example'  : '"BRK-de traditsioon sai alguse 1964 ." + "aastal Saksamaal Heidelbergis."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{3,4})\s*\.$', re.DOTALL), re.compile('^'+_lc_letter+'*aasta.*') ], \
   },
   #   {Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}
   { 'comment'  : '{Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}', \
     'example'  : '"... Mileetose koolkonnd (VI-V saj." + "e. Kr.) ..."', \
     'fix_type' : 'numeric_century', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{1,2}|[IVXLCDM]+)\s*\.?\s*saj\.?$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },
   
   #   {Date_dd.mm.yyyy.} + {time_HH:MM}
   { 'comment'  : '{Date_dd.mm.yyyy.} + {time_HH:MM}', \
     'example'  : "'Gert 02.03.2009.' + '14:40 Tahaks kindlalt sinna kooli:P'", \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{2})\.([0-9]{2})\.([0-9]{4})\.\s*$', re.DOTALL), re.compile(r'^\s*([0-9]{2}):([0-9]{2})')], \
   },
   #   {|kell|} {time_HH.} + {MM}
   { 'comment'  : '{|kell|} {time_HH.} + {MM}', \
     'example'  : "'Kell 22 .' + '00\nTV 3\n“ Thelma”\n'", \
     'fix_type' : 'numeric_time', \
     'regexes'  : [re.compile(r'(.+)?[kK]ell\S?\s([0-9]{1,2})\s*\.\s*$', re.DOTALL), re.compile(r'^\s*([0-9]{2})\s')], \
   },

   #   {Numeric_date} {period} + {month_name}
   { 'comment'  : '{Numeric_date} {period} + {month_name}', \
     'example'  : '"Kirijenko on sündinud 26 ." + "juulil 1962 . aastal ."', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{1,2})\s*\.$', re.DOTALL), re.compile('^(jaan|veeb|märts|apr|mai|juul|juun|augu|septe|okto|nove|detse).*') ], \
   },
   #   {Numeric_date} {period} + {month_name_short}
   { 'comment'  : '{Numeric_date} {period} + {month_name_short}', \
     'example'  : '"( NYT , 5 ." + "okt . )"', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile(r'(.+)?([0-9]{1,2})\s*\.$', re.DOTALL), re.compile(r'^(jaan|veebr?|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)(\s*\.|\s).*') ], \
   },
   #  {Month_name_short} {period} + {numeric_year}
   { 'comment'  : '{Numeric_date} {period} + {month_name_short}', \
     'example'  : '"17. okt." + "1998 a."', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile(r'^(.+)?\s(jaan|veebr?|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)\s*\..*', re.DOTALL), re.compile(r'([0-9]{4})\s*.*') ], \
   },

   #   {First_10_Roman_numerals} {period} + {lowercase_or_dash}
   { 'comment'  : '{First_10_Roman_numerals} {period} + {lowercase_or_dash}', \
     'example'  : '"III." + "- II." + "sajandil enne meie ajastut toimunud sõjad."', \
     'fix_type' : 'numeric_roman_numeral', \
     'regexes'  : [re.compile(r'(.+)?((VIII|III|VII|II|IV|VI|IX|V|I|X)\s*\.)$', re.DOTALL), re.compile('^('+_lc_letter+'|'+_hyphen_pat+')') ], \
   },
   
   #   {Number} {period} + {lowercase}
   { 'comment'  : '{Number} {period} + {lowercase}', \
     'example'  : '"sügisringi 4 ." + "vooru kohtumine"', \
     'fix_type' : 'numeric_ordinal_numeral', \
     'regexes'  : [re.compile(r'(.+)?([0-9]+)\s*\.$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },
   #   {Number} {period} + {hyphen}
   { 'comment'  : '{Number} {period} + {hyphen}', \
     'example'  : '"1500." + "- kuni 3000." + "- krooni"', \
     'fix_type' : 'numeric_monetary', \
     'regexes'  : [re.compile(r'(.+)?([0-9]+)\s*\.$', re.DOTALL), re.compile('^'+_hyphen_pat+'+') ], \
   },
   
   # ***********************************
   #   Fixes related to specific abbreviations
   # ***********************************
   #   {BCE} {period} + {lowercase}
   { 'comment'  : '{BCE} {period} + {lowercase}', \
     'example'  : '"Suur rahvasterändamine oli avanud IV-nda sajandiga p. Kr." + "segaduste ja sõdade ajastu."', \
     'fix_type' : 'abbrev_century', \
     'regexes'  : [re.compile(r'(.+)?[pe]\s*\.\s*Kr\s*\.?$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },

   { 'comment'  : '{Abbreviation} {period} + {numeric}', \
     'example'  : '"Hõimurahvaste Aeg Nr." + "7 lk." + "22."', \
     'fix_type' : 'abbrev_numeric', \
     'regexes'  : [re.compile(r'(.+)?([Ll]k|[Nn]r)\s*\.$', re.DOTALL), re.compile('^[0-9]+') ], \
   },
   { 'comment'  : '{Common_abbreviation} {period} + {lowercase|hyhen|,|)}', \
     'example'  : '"jooniste, tabelite jm." + "selgeks tehti."', \
     'fix_type' : 'abbrev_common', \
     'regexes'  : [re.compile(r'(.+)?\s(ingl|näit|'+
                                      r'jm[st]|jne|jp[mt]|mnt|pst|tbl|vm[st]|'+\
                                      r'j[tm]|mh|vm|e|t)\s?[.]$', re.DOTALL), \
                   re.compile(r'^('+_lc_letter+r'|'+_hyphen_pat+r'|,|;|\))') ], \
   },
   #   {abbreviation} {period} + {comma_or_semicolon}
   { 'comment'  : '{abbreviation} {period} + {comma_or_semicolon}', \
     'example'  : "(Ribas jt.' + ', 1995; Gebel jt.' + ', 1997; Kaya jt.' + ', 2004)", \
     'fix_type' : 'abbrev_common', \
     'regexes'  : [re.compile(r'.+\s[a-zöäüõ\-.]+[.]\s*$', re.DOTALL), re.compile('^([,;]).*') ], \
   },
   
   #   {uppercase_letter} {period} + {not_uppercase_followed_by_lowercase}
   { 'comment'  : '{uppercase_letter} {period} + {not_uppercase_followed_by_lowercase}', \
     'example'  : "'K.' + 'C.' + 'seal nime ees tähendab Kadri’s Choise'", \
     'fix_type' : 'abbrev_name_initial', \
     'regexes'  : [re.compile(r'(.*'+_not_letter+r'|^)'+_uc_letter+r'\s*[.]\s*$', re.DOTALL), \
                   re.compile(r'^(?!\s*'+_uc_letter+_lc_letter+r').*') ], \
   },

   # ***********************************
   #   Fixes related to parentheses 
   # ***********************************
   #   {period_ending_content_of_parentheses} + {lowercase_or_comma}
   { 'comment'  : '{period_ending_content_of_parentheses} + {lowercase_or_comma}', \
     'example'  : '"Lugesime Menippose (III saj. e.m.a.)" + "satiiri..."', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'(.+)?\([^()]+[.!]\s*\)$', re.DOTALL), re.compile('^('+_lc_letter+'|,)+.*')], \
   },
   #   {parentheses_start} {content_in_parentheses} + {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {parentheses_end}', \
     'example'  : '( " Easy FM , soft hits ! "\' + \') .', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'.*\([^()]+$', re.DOTALL), re.compile(r'^[^()A-ZÖÄÜÕŠŽ]*\)\s*$') ], \
   },
   #   {parentheses_start} {content_in_parentheses} + {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {parentheses_end}', \
     'example'  : '( " Easy FM , soft hits ! "\' + \') .', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'.*\([^()]+$', re.DOTALL), re.compile(r'^[^()A-ZÖÄÜÕŠŽ]*\)(\s|\n)*[^A-ZÖÄÜÕŠŽ \n].*') ], \
   },
   #   {ending_punctuation} + {parentheses_end}<end> {uppercase}
   { 'comment'   : '{ending_punctuation} + {parentheses_end}<end> {uppercase}', \
     'example'   : "'( Naerab . ' + ')\nEriti siis , kui sõidan mootorratta või jalgrattaga .'", \
     'fix_type'  : 'parentheses', \
     'regexes'   : [re.compile(r'.*[.!?]\s*$', re.DOTALL), re.compile(r'^(?P<end>\))(\s|\n)*[A-ZÖÄÜÕŠŽ].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {parentheses_start} {content_in_parentheses} + {lowercase_or_comma} {content_in_parentheses} {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {lowercase_or_comma} {content_in_parentheses} {parentheses_end}', \
     'example'  : '"(loe: ta läheb sügisel 11." + " klassi!)"', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'(.+)?\([^()]+$', re.DOTALL), re.compile(r'^('+_lc_letter+r'|,)[^()]+\).*')], \
   },
   #   {parentheses_start} {content_in_parentheses} + {numeric_patterns} {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {numeric_patterns} {parentheses_end}', \
     'example'  : '"rahvuskultuuriline missioon ( lk." + "217 )"', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'.*\([^()]+$', re.DOTALL), re.compile(r'^[0-9.\- ]+\).*') ], \
   },
   #   {content_in_parentheses} + {single_sentence_ending_symbol}
   { 'comment'  : '{content_in_parentheses} + {single_sentence_ending_symbol}', \
     'example'  : '\'( " Easy FM , soft hits ! " )\' + \'.\'', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile(r'.*\([^()]+\)$', re.DOTALL), _ending_punct_regexp ], \
   },
   
   # ***********************************
   #   Fixes related to double quotes
   # ***********************************
   #   {sentence_ending_punct} + {ending_quotes} {comma_or_semicolon_or_lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}', \
     'example'  : '\'ETV-s esietendub homme " Õnne 13 ! \' + \'", mis kuu aja eest jõudis lavale Ugalas .\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile(r'.+[?!.…]\s*$', re.DOTALL), re.compile(r'^['+_ending_quotes+r']\s*([,;]|'+_lc_letter+r')+') ], \
   },
   #   {sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}', \
     'example'  : '\'ETV-s esietendub homme " Õnne 13 ! "\' + \', mis kuu aja eest jõudis lavale Ugalas .\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile(r'.+[?!.…]\s*['+_ending_quotes+r']$', re.DOTALL), re.compile('^([,;]|'+_lc_letter+')+') ], \
   },
   #   {sentence_ending_punct} + {only_ending_quotes}
   { 'comment'  : '{sentence_ending_punct} + {ending_quotes}', \
     'example'  : '"« See amet on nii raske !" + "»"', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile('.+?[?!.…]$', re.DOTALL), re.compile('^['+_ending_quotes+']$') ], \
   },
   #   {ending_punctuation} + {ending_quotes}<end> {starting_quotes}
   { 'comment'   : '{ending_punctuation} + {ending_quotes}<end> {starting_quotes}', \
     'example'   : "'« Väga tore !' + '»\n\n« Mis siin ikka ! »'", \
     'fix_type'  : 'double_quotes', \
     'regexes'   : [re.compile(r'.*[.!?]\s*$', re.DOTALL), re.compile(r'^(?P<end>['+_ending_quotes+r'])(\s|\n)*['+_start_quotes+r'].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {ending_punctuation} + {ending_quotes}<end> {starting_brackets}
   { 'comment'   : '{ending_punctuation} + {ending_quotes}<end> {starting_brackets}', \
     'example'   : "'« Kus on minu mesi ?' + '»\n( Inglise keeles kallim . )'", \
     'fix_type'  : 'double_quotes', \
     'regexes'   : [re.compile(r'.*[.!?]\s*$', re.DOTALL), re.compile(r'^(?P<end>['+_ending_quotes+r'])(\s|\n)*[(\[].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {sentence_ending_punct} {ending_quotes} + {only_sentence_ending_punct}
   { 'comment'  : '{sentence_ending_punct} + {ending_quotes} {only_sentence_ending_punct}', \
     'example'  : ''' '\nNii ilus ! ' + '" .' + '\nNõmmel elav pensioniealine Maret' ''', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile(r'.+[?!.…]\s*$', re.DOTALL), re.compile(r'^['+_ending_quotes+r']\s*[?!.…]+$') ], \
   },
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {only_sentence_ending_punct}', \
     'example'  : ''' '\nNii ilus ! " ' + ' . \nNõmmel elav pensioniealine Maret' ''', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile(r'.+[?!.…]\s*['+_ending_quotes+r']$', re.DOTALL), _ending_punct_regexp ], \
   },

   # ***********************************
   #   Fixes related to prolonged sentence ending punctuation
   # ***********************************
   #   {sentence_ending_punct} + {only_sentence_ending_punct}
   { 'comment'  : '{sentence_ending_punct} + {only_sentence_ending_punct}', \
     'example'  : '"arvati , et veel sellel aastal j6uab kohale ; yess !" + "!" + "!"', \
     'fix_type' : 'repeated_ending_punct', \
     'regexes'  : [re.compile(r'.+[?!.…]\s*$', re.DOTALL), _ending_punct_regexp ], \
   },
   
   # ***********************************
   #   Fixes related to punctuation in titles inside the sentence
   # ***********************************
   #   {sentence_ending_punct} + {comma_or_semicolon} {lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} + {comma_or_semicolon} {lowercase_letter}', \
     'example'  : '"Jõulise naissolistiga Conflict OK !" + ", kitarripoppi mängivad Claires Birthday ja Seachers."', \
     'fix_type' : 'inner_title_punct', \
     'regexes'  : [re.compile(r'.+[?!]\s*$', re.DOTALL), re.compile(r'^([,;])\s*'+_lc_letter+r'+') ], \
   },
]


class SentenceTokenizer( Tagger ):
    """Tokenizes text into sentences, and makes sentence tokenization post-corrections where necessary."""
    conf_param = ['base_sentence_tokenizer',
                  'fix_paragraph_endings', 'fix_compound_tokens',
                  'fix_numeric', 'fix_parentheses', 'fix_double_quotes',
                  'fix_inner_title_punct', 'fix_repeated_ending_punct',
                  'fix_double_quotes_based_on_counts',
                  'use_emoticons_as_endings',
                  'record_fix_types',
                  # Inner parameters:
                  '_merge_rules',
                  '_apply_sentences_from_tokens',
                  # Names of the specific input layers
                  '_input_words_layer', '_input_compound_tokens_layer',
                  ]
    output_layer = 'sentences'
    output_attributes = ()

    def __init__(self, 
                 output_layer:str='sentences',
                 input_words_layer:str='words',
                 input_compound_tokens_layer:str='compound_tokens',
                 fix_paragraph_endings:bool = True,
                 fix_compound_tokens:bool = True,
                 fix_numeric:bool = True,
                 fix_parentheses:bool = True,
                 fix_double_quotes:bool = True,
                 fix_inner_title_punct:bool = True,
                 fix_repeated_ending_punct:bool = True,
                 fix_double_quotes_based_on_counts:bool = False,
                 use_emoticons_as_endings:bool = True,
                 record_fix_types:bool = False,
                 base_sentence_tokenizer = None,
                 patterns:list = merge_patterns
                 ):
        """Initializes this SentenceTokenizer.
        
        Parameters
        ----------
        output_layer: str (default: 'sentences')
            Name for the sentences layer;
        
        input_words_layer: str (default: 'words')
            Name of the input words layer;

        input_compound_tokens_layer: str (default: 'compound_tokens')
            Name of the input compound_tokens layer;
        
        fix_paragraph_endings: boolean (default: True)
            Paragraph endings (double newlines) will be treated as sentence 
            endings.
        
        fix_compound_tokens: boolean (default: True)
            If True, then following sentence boundary fixes are applied:
            *) a built-in logic  is used to remove all sentence endings
               that fall inside compound_tokens;
            *) sentence endings that are added after compound_tokens of 
               type non_ending_abbreviation are removed;
            *) if a regular abbreviation is followed by a sentence break, 
               and then by a lowercase word or non-ending punctuation 
               (comma or semicolon), then the sentence break is removed 
               after such abbreviation;
        
        fix_numeric: boolean (default: True)
            Removes sentence endings that are mistakenly added after periods 
            that end date, time and (other) numeric expressions;
        
        fix_parentheses: boolean (default: True)
            Removes sentence endings that are mistakenly added inside parentheses, 
            and fixes endings that are misplaced with respect to parentheses;
        
        fix_double_quotes: boolean (default: True)
            Removes sentence endings that are misplaced with respect to quotations 
            / double quotes.  Note: these are local fixes in adjacent sentences
            that to not take account of the balance of quotes (in the whole text). 
        
        fix_inner_title_punct: boolean (default: True)
            Removes sentence endings that are mistakenly placed after titles inside 
            the sentence. Currently only fixes cases when a question mark or an 
            exclamation mark is followed by a sentence ending and, a colon or a 
            semicolon starts the next sentence.
        
        fix_repeated_ending_punct: boolean (default: True)
            Adds sentence endings that are missed in places of prolonged ending 
            punctuation (including triple dots), and also fixes misplaced sentence 
            endings in such contexts.
        
        fix_double_quotes_based_on_counts: boolean (default: xxxx)
            Provides sentence boundary corrections based on counting quotation 
            marks in the whole text. Note: these are global fixes that consider 
            the balance of quotes in the whole text. 
        
        use_emoticons_as_endings: boolean (default: True)
            If switched on, then emoticons are treated as sentence endings.
        
        record_fix_types: boolean (default: False)
            If True, then attribute 'fix_types' is added to the sentences
            layer, which contains names of the applied postcorrection (merging) 
            fixes.
            Note: this attribute is only used for developing and debugging 
            purposes, it may change in the future and should not be relied 
            upon;
        
        base_sentence_tokenizer: nltk.tokenize.api.TokenizerI (default: None)
            Base string tokenizer to be used for initial sentence tokenization.
            If not set, then NLTK's PunktSentenceTokenizer with the Estonian-
            specific model ('tokenizers/punkt/estonian.pickle') is chosen as 
            the base sentence tokenizer.
            Use this argument, if you want to set a custom base tokenizer, e.g.
            LineTokenizer() from NLTK.
            Note:
            * If base_sentence_tokenizer is an instance of PunktSentenceTokenizer,
              then  its  method   sentences_from_tokens()   is  used  for initial 
              sentence tokenization;
            * otherwise (base_sentence_tokenizer is an instance of TokenizerI, 
              but not PunktSentenceTokenizer), then its method span_tokenize() is 
              used for initial sentence tokenization;

        patterns: list (default: merge_patterns)
            A list of all merge (and merge-and-split) patterns used by this 
            SentenceTokenizer. 
            If you want to manually add or remove merge patterns, then make a 
            copy of merge_patterns, modify it and pass it as patterns.
        """
        # Set input/output layer names
        self.output_layer = output_layer
        self._input_words_layer = input_words_layer
        self._input_compound_tokens_layer = input_compound_tokens_layer
        self.input_layers = [input_words_layer, input_compound_tokens_layer]
        # Set flags
        self.fix_paragraph_endings = fix_paragraph_endings
        self.fix_compound_tokens = fix_compound_tokens
        self.fix_numeric = fix_numeric
        self.fix_parentheses = fix_parentheses
        self.fix_double_quotes = fix_double_quotes
        self.fix_inner_title_punct = fix_inner_title_punct
        self.fix_repeated_ending_punct = fix_repeated_ending_punct
        self.fix_double_quotes_based_on_counts = fix_double_quotes_based_on_counts
        self.use_emoticons_as_endings = use_emoticons_as_endings
        self.record_fix_types = record_fix_types

        self.output_attributes = ()
        if record_fix_types:
            self.output_attributes = ('fix_types', )
        
        # 1) Set or initialize base sentence tokenizer
        import nltk as nltk
        from nltk.tokenize.punkt import PunktSentenceTokenizer
        from nltk.tokenize.api import TokenizerI

        self.base_sentence_tokenizer = None
        if not base_sentence_tokenizer:
            # If base tokenizer was not given by the user:
            #    Initialize NLTK's tokenizer
            #    use NLTK-s sentence tokenizer for Estonian, in case it is not 
            #    downloaded yet, try to download it first
            try:
                self.base_sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
            except LookupError:
                import nltk.downloader
                nltk.downloader.download('punkt')
            finally:
                if self.base_sentence_tokenizer is None:
                    self.base_sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
        else:
            # If base tokenizer was given by the user:
            #    check that it implements the correct interface
            assert isinstance(base_sentence_tokenizer, TokenizerI), \
                   ' (!) base_sentence_tokenizer should be an instance of nltk.tokenize.api.TokenizerI.'
            self.base_sentence_tokenizer = base_sentence_tokenizer
        # 2) Fix the tokenization method: 
        #  * use sentences_from_tokens() for PunktSentenceTokenizer()
        #  * use span_tokenize() for other / custom tokenizers;
        self._apply_sentences_from_tokens = True
        if not isinstance(self.base_sentence_tokenizer, PunktSentenceTokenizer):
            self._apply_sentences_from_tokens = False
        # 3) Filter rules according to the given configuration
        self._merge_rules = []
        for merge_pattern in patterns:
            # Fixes that use both built-in logic, and merge rules
            if fix_compound_tokens and merge_pattern['fix_type'].startswith('abbrev'):
                self._merge_rules.append( merge_pattern )
            if fix_repeated_ending_punct and merge_pattern['fix_type'].startswith('repeated_ending_punct'):
                self._merge_rules.append( merge_pattern )
            # Fixes that only use merge rules
            if fix_numeric and merge_pattern['fix_type'].startswith('numeric'):
                self._merge_rules.append( merge_pattern )
            if fix_parentheses and merge_pattern['fix_type'].startswith('parentheses'):
                self._merge_rules.append( merge_pattern )
            if fix_double_quotes and merge_pattern['fix_type'].startswith('double_quotes'):
                self._merge_rules.append( merge_pattern )
            if fix_inner_title_punct and merge_pattern['fix_type'].startswith('inner_title_punct'):
                self._merge_rules.append( merge_pattern )

    def _tokenize_text(self, raw_text: str) -> Iterator[Tuple[int, int]]:
        """Tokenizes into sentences based on the input text."""
        return self.base_sentence_tokenizer.span_tokenize(raw_text)

    def _sentences_from_tokens(self, layers) -> Iterator[Tuple[int, int]]:
        """Tokenizes into sentences based on the word tokens of the input text."""
        words = list(layers[self._input_words_layer])
        word_texts = layers[self._input_words_layer].text
        i = 0
        for sentence_words in self.base_sentence_tokenizer.sentences_from_tokens(word_texts):
            if sentence_words:
                first_token = i
                last_token  = i + len(sentence_words) - 1
                yield (words[first_token].start, words[last_token].end)
                i += len(sentence_words)

    def _make_layer_template(self):
        """Creates and returns a template of the sentences layer."""
        return Layer(enveloping=self._input_words_layer,
                     name=self.output_layer,
                     attributes=self.output_attributes,
                     text_object=None,
                     ambiguous=False)

    def _make_layer(self, text, layers, status: dict):
        """Creates the sentences layer.
        
        Parameters
        ----------
        raw_text: str
           Text string corresponding to the text which
           will be segmented into sentences.
          
        layers: MutableMapping[str, Layer]
           Layers of the raw_text. Contains mappings from the 
           name of the layer to the Layer object. Must contain
           words and compound_tokens layers.
          
        status: dict
           This can be used to store metadata on layer tagging.
        """
        raw_text = text.text
        # Apply the base sentence tokenizer
        # Depending on the available interface, use either
        # sentences_from_tokens() or span_tokenize()
        if self._apply_sentences_from_tokens:
            # Note: this should be the default choice for EstNLTK
            sentence_ends = {end for _, end in self._sentences_from_tokens(layers)}
        else:
            # Note: this is a customization, not default
            sentence_ends = {end for _, end in self._tokenize_text(raw_text)}
        # Required layers:
        words = layers[self._input_words_layer]
        compound_tokens = layers[self._input_compound_tokens_layer]
        # A) Remove sentence endings that:
        #   A.1) coincide with endings of non_ending_abbreviation's
        #   A.2) fall in the middle of compound tokens
        if self.fix_compound_tokens:
            for ct in compound_tokens:
                if 'non_ending_abbreviation' in ct.type:
                    sentence_ends -= {span.end for span in ct.base_span}
                else:
                    sentence_ends -= {span.end for span in ct.base_span[0:-1]}
        # B) Use repeated/prolonged sentence punctuation as sentence endings
        if self.fix_repeated_ending_punct:
            repeated_ending_punct = []
            for wid, word in enumerate( words ):
                # Collect prolonged punctuation
                if _ending_punct_regexp.match( word.text ):
                    repeated_ending_punct.append( word.text )
                elif repeated_ending_punct:
                    repeated_ending_punct = []
                # Check that the punctuation has some length
                if (len(repeated_ending_punct) > 1) or \
                   (len(repeated_ending_punct) == 1 and \
                    (repeated_ending_punct[0] == '…' or \
                    len(repeated_ending_punct[0]) > 1)):
                    # Check if the next word is titlecased
                    if wid+1 < len(words):
                        next_word = words[wid+1].text
                        if len(next_word) > 1 and \
                           next_word[0].isupper() and \
                           (next_word[1].islower() or next_word.isupper()):
                            # we have a likely sentence boundary:
                            # add it to the set of sentence ends
                            sentence_ends.add( word.end )
                            # Check if the token before punctuation is '[', 
                            # '(' or '"'; If so, then discard the sentence 
                            # ending ...
                            if wid - len(repeated_ending_punct) > -1:
                                prev_word = words[wid-len(repeated_ending_punct)]
                                if prev_word.text in ['[', '(', '"']:
                                    sentence_ends -= { word.end }
        # C) Use emoticons as sentence endings
        if self.use_emoticons_as_endings:
            # C.1) Collect all emoticons (record start locations)
            emoticon_locations = {}
            for ct in compound_tokens:
                if 'emoticon' in ct.type:
                    emoticon_locations[ct.start] = ct
            # C.2) Iterate over words and check emoticons
            repeated_emoticons = []
            for wid, word in enumerate( words ):
                if word.start in emoticon_locations:
                    repeated_emoticons.append( emoticon_locations[word.start] )
                else:
                    repeated_emoticons = []
                # Check that there is an emoticon (or even few of them)
                if len(repeated_emoticons) > 0:
                    # Check if the next word is not emoticon, and is titlecased
                    if wid+1 < len( words ):
                        next_word = words[wid+1].text
                        if words[wid+1].start not in emoticon_locations and \
                           len(next_word) > 1 and \
                           next_word[0].isupper() and \
                           next_word[1].islower():
                            # we have a likely sentence boundary:
                            # add it to the set of sentence ends
                            sentence_ends.add( word.end )
                            # Check if word before emoticons is already a sentence
                            # ending; if so, remove it's ending (assuming that 
                            # emoticons belong to the previous sentence)
                            if wid - len(repeated_emoticons) > -1:
                                prev_word = words[wid-len(repeated_emoticons)]
                                sentence_ends -= { prev_word.end }
        # D) Align sentence endings with word startings and endings
        #    Collect span lists of potential sentences
        start = 0
        if len( words ) > 0:
            sentence_ends.add( words[-1].end )
        sentences_list = []
        sentence_fixes_list = []
        for i, token in enumerate( words ):
            if token.end in sentence_ends:
                sentences_list.append(words[start:i+1])
                start = i + 1
        # E) Use '\n\n' (usually paragraph endings) as sentence endings
        if self.fix_paragraph_endings:
            sentences_list, sentence_fixes_list = \
                self._split_by_double_newlines( 
                            raw_text,
                            sentences_list)
        # F) Apply postcorrection fixes to sentence spans
        # F.1) Try to merge mistakenly split sentences
        if self._merge_rules:
            sentences_list, sentence_fixes_list = \
                self._merge_mistakenly_split_sentences(raw_text,
                                                       sentences_list,
                                                       sentence_fixes_list)
        # G) Count double quotes and provide corrections based on counts 
        #    (as far as the counts are in balance)
        if self.fix_double_quotes_based_on_counts:
            sentences_list, sentence_fixes_list = \
                self._counting_corrections_to_double_quotes(raw_text, sentences_list, sentence_fixes_list)
        # H) Create the layer and attach sentences
        layer = self._make_layer_template()
        layer.text_object = text
        for sid, sentence_span_list in enumerate(sentences_list):
            if self.record_fix_types:
                # Add information about which types of fixes 
                # were applied to sentences
                layer.add_annotation(sentence_span_list, fix_types=sentence_fixes_list[sid])
            else:
                layer.add_annotation(sentence_span_list)
        return layer

    def _merge_mistakenly_split_sentences(self, raw_text: str, sentences_list: list, sentence_fixes_list: list):
        """ Uses regular expression patterns (defined in self._merge_rules) to
            discover adjacent sentences (in sentences_list) that should actually 
            form a single sentence. Merges those adjacent sentences.
            
            The parameter sentence_fixes_list should contain a list of fixes that 
            were already previously added to the elements of sentences_list.
            These lists of fixes are then updated in correspondence with the fixes 
            newly added by this method.
            
            Returns a tuple of two lists:
            *) new version of sentences_list where merges have been made;
            *) correspondingly updated sentence_fixes_list;
        """
        assert len(sentences_list) == len(sentence_fixes_list)
        new_sentences_list = []
        new_sentence_fixes_list = []
        # Iterate over all adjacent sentences
        for sid, sentence_spl in enumerate(sentences_list):
            last_sentence_spl   = None
            last_sentence_fixes = None
            this_sentence_fixes = sentence_fixes_list[sid]
            # get text of the current sentence
            this_sent = \
                raw_text[sentence_spl[0].start:sentence_spl[-1].end].lstrip()
            current_fix_types = []
            shift_ending = None
            merge_span_lists = False
            if sid > 0:
                # get text of the previous sentence
                if new_sentences_list:
                    last_sentence_spl = new_sentences_list[-1]
                    last_sentence_fixes = new_sentence_fixes_list[-1]
                else:
                    last_sentence_spl = sentences_list[sid - 1]
                    last_sentence_fixes = sentence_fixes_list[sid - 1]

                prev_sent = raw_text[last_sentence_spl[0].start:last_sentence_spl[-1].end].rstrip()

                discard_merge = False
                if self.fix_paragraph_endings:
                    # If fixing paragraph endings has been switched on, then 
                    # do not merge over paragraph endings!
                    # ( otherwise, it may ruin paragraph ending fixes )
                    this_start = sentence_spl[0].start
                    last_end   = last_sentence_spl[-1].end
                    if '\n\n' in raw_text[last_end:this_start]:
                        discard_merge = True
                if not discard_merge:
                    # Check if the adjacent sentences should be joined / merged according 
                    # to one of the patterns ...
                    for pattern in self._merge_rules:
                        [beginPat, endPat] = pattern['regexes']
                        if endPat.match(this_sent) and beginPat.match(prev_sent):
                            merge_span_lists = True
                            current_fix_types.append(pattern['fix_type'])
                            # Check if ending also needs to be shifted
                            if 'shift_end' in pattern:
                                # Find new sentence ending position and validate it
                                shift_ending = self._find_new_sentence_ending(raw_text, pattern, sentence_spl,
                                                                              last_sentence_spl)
                            break
            if merge_span_lists:
                # -------------------------------------------
                #   1) Split-and-merge: First merge two sentences, then split at some 
                #      location (inside one of the old sentences)
                # -------------------------------------------
                if shift_ending:
                    prev_sent_spl = new_sentences_list[-1] if new_sentences_list else last_sentence_spl
                    merge_split_result = self._perform_merge_split(shift_ending, sentence_spl, prev_sent_spl)
                    if merge_split_result is not None:
                        if new_sentences_list:
                            # Update sentence spans
                            new_sentences_list[-1] = merge_split_result[0]
                            new_sentences_list.append ( merge_split_result[1])
                            # Update fix types list
                            new_sentence_fixes_list[-1] = \
                                last_sentence_fixes + current_fix_types
                            new_sentence_fixes_list.append(
                                this_sentence_fixes + current_fix_types)
                        else:
                            # Update sentence spans
                            new_sentences_list.extend(merge_split_result)
                            # Update fix types list
                            new_sentence_fixes_list.append(
                                last_sentence_fixes + current_fix_types)
                            new_sentence_fixes_list.append(
                                this_sentence_fixes + current_fix_types)
                    else:
                        # TODO: test or remove
                        # if merge-and-split failed, then discard the rule
                        # (sentences will remain split as they were)
                        # new_spanlist = EnvelopingSpan()
                        # if self.record_fix_types:
                        #     new_spanlist.fix_types = []
                        # new_spanlist.spans = sentence_spl.spans
                        new_sentences_list.append(sentence_spl)
                        # Update fix types list
                        new_sentence_fixes_list.append(this_sentence_fixes)
                else:
                    # -------------------------------------------
                    #   2) Merge only: join two consecutive sentences into one
                    # -------------------------------------------
                    # Perform the merging
                    if not new_sentences_list:
                        # No sentence has been added so far: add a new one
                        spans = last_sentence_spl + sentence_spl
                        new_sentences_list.append(spans)
                        # Update fix types list
                        all_fixes = \
                            last_sentence_fixes + \
                            this_sentence_fixes + \
                            current_fix_types
                        new_sentence_fixes_list.append( all_fixes )
                    else:
                        # At least one sentence has already been added:
                        # extend the last sentence
                        spans = list(new_sentences_list[-1]) + list(sentence_spl)
                        new_sentences_list[-1] = spans
                        # Update fix types list
                        all_fixes = \
                            last_sentence_fixes + \
                            this_sentence_fixes + \
                            current_fix_types
                        new_sentence_fixes_list[-1] = all_fixes
                    #print('>>1',prev_sent)
                    #print('>>2',this_sent)
            else:
                # Add sentence without merging
                new_sentences_list.append(sentence_spl)
                # Update fix types list
                new_sentence_fixes_list.append(this_sentence_fixes)
                #print('>>0',this_sent)
        assert len(new_sentences_list) == len(new_sentence_fixes_list)
        return new_sentences_list, new_sentence_fixes_list

    @staticmethod
    def _find_new_sentence_ending(raw_text: str,
                                  merge_split_pattern: dict,
                                  this_sent: SpanList,
                                  prev_sent: SpanList):
        ''' Finds the position where sentence ending should be shifted while 
            attempting to merge and re-split consecutive sentences prev_sent
            and this_sent. Returns the new ending position if it passes the 
            validation.
            
            More specifically: returns a span of the new sentence ending token, 
            in which the last element should be the new sentence ending position.
            
            Returns None, if:
             *) the ending group (<end>) was not marked in any of the regular 
                expressions in merge_split_pattern['regexes'];
             *) the ending group was not captured from the corresponding sentences
                (this_sent or prev_sent);
             *) the new ending of the sentence did not match a word ending in 
                the corresponding sentence;
        '''
        # Check if ending needs to be shifted
        if 'shift_end' in merge_split_pattern and \
           merge_split_pattern['shift_end']:
            [beginPat, endPat] = merge_split_pattern['regexes']
            if '?P<end>' in endPat.pattern:
                # extract ending from the current sentence
                this_sent_str = \
                    raw_text[this_sent[0].start:this_sent[-1].end].lstrip()
                m = endPat.match(this_sent_str)
                if m and m.span('end') != (-1, -1):
                    end_span = m.span('end')
                    # span's position in the text
                    start_in_text = this_sent[0].start + end_span[0]
                    end_in_text   = this_sent[0].start + end_span[1]
                    # validate that end_in_text overlaps with a word ending
                    matches_word_ending = False
                    for span in this_sent:
                        if span.end == end_in_text:
                            matches_word_ending = True
                        if span.end > end_in_text:
                            break
                    # If all validations have been passed, return ending's span
                    if matches_word_ending:
                        return ( start_in_text, end_in_text )
            if '?P<end>' in beginPat.pattern:
                # extract ending from the previous sentence
                prev_sent_str = \
                    raw_text[prev_sent[0].start:prev_sent[-1].end].lstrip()
                m = beginPat.match(prev_sent_str)
                if m and m.span('end') != (-1, -1):
                    end_span = m.span('end')
                    # span's position in the text
                    start_in_text = prev_sent[0].start + end_span[0]
                    end_in_text   = prev_sent[0].start + end_span[1]
                    # validate that end_in_text overlaps with a word ending
                    matches_word_ending = False
                    for span in prev_sent:
                        if span.end == end_in_text:
                            matches_word_ending = True
                        if span.end > end_in_text:
                            break
                    # If all validations have been passed, return ending's span
                    if matches_word_ending:
                        return ( start_in_text, end_in_text )
        # The new sentence ending was either not found, or did not pass 
        # the validation
        return None

    @staticmethod
    def _perform_merge_split(end_span: tuple, this_sent: SpanList, prev_sent: SpanList):
        """ Performs merge-split operation: 1) consecutive sentences prev_sent
            and this_sent will be joined into one sentence, 2) the new joined 
            sentence will be split (into two sentences) at the position end_span;
            
            In case of success, returns 2-element tuple containing SpanList-s 
            corresponding to the sentences that went through to the merge and 
            split;
            
            Returns None, if the sentences would be ill-formed after the merge-
            and-split. For instance, returns None if one of the new sentences 
            would be empty, or if the merge-and-split would result in duplication 
            of tokens;
        """
        if end_span and end_span != (-1, -1):
            new_sentence1 = []
            new_sentence2 = []
            for sid, span in enumerate(prev_sent):
                if span.end <= end_span[1]:
                    new_sentence1.append( span )
                elif span.start >= end_span[1]:
                    new_sentence2.append( span )
            for sid, span in enumerate(this_sent):
                if span.end <= end_span[1]:
                    new_sentence1.append( span )
                elif span.start >= end_span[1]:
                    new_sentence2.append( span )
            # Validity & sanity check
            # 1) The number of covered words/tokens should remain the same
            #    after the split/merge operation:
            if len(prev_sent) + len(this_sent) !=\
               len(new_sentence1) + len(new_sentence2):
                # The numbers of covered tokens do no match: something 
                # is wrong ...
                return None
            # 2) Both new sentences should have at least 1 token
            if len(new_sentence1) < 1  or  len(new_sentence2) < 1:
                # One of the sentence has 0 length: something is wrong
                return None
            return new_sentence1, new_sentence2
        return None

    @staticmethod
    def _split_by_double_newlines(raw_text: str, sentences_list: list):
        """ Splits sentences inside the given list of sentences by double
            newlines (usually paragraph endings).
            
            Returns a tuple containing two lists:
            *) a new list of sentences where splitting has been performed;
            *) a list of sentence fixes. Each element in this list 
               represents fixes that were applied to a single sentence by 
               this method. Fixes are given as a list (an empty list, 
               if no fixes were applied to the sentence);
        """
        double_newline = '\n\n'
        new_sentences_list  = []
        sentence_fixes_list = []
        for sentence_spl in sentences_list:
            # get text of the current sentence
            this_sent_text = \
                raw_text[sentence_spl.start:sentence_spl.end]
            # check for double newline (paragraph ending)
            if double_newline in this_sent_text:
                # iterate over words
                current_words = []
                for wid, span in enumerate( sentence_spl.spans ):
                    current_words.append( span )
                    if wid+1 < len(sentence_spl.spans):
                        next_span = sentence_spl.spans[wid+1]
                        # check what is between two word spans
                        space_between = \
                            raw_text[span.end:next_span.start]
                        if double_newline in space_between:
                            # Create a new split 
                            new_sentences_list.append(current_words)
                            sentence_fixes_list.append(['double_newline_ending'])
                            current_words = []
                if current_words:
                    new_sentences_list.append(current_words)
                    sentence_fixes_list.append([])
            else:
                new_sentences_list.append(sentence_spl.spans)
                sentence_fixes_list.append( [] )
        assert len(new_sentences_list) == len(sentence_fixes_list)
        return new_sentences_list, sentence_fixes_list



    @staticmethod
    def _counting_corrections_to_double_quotes(raw_text: str, sentences_list: list, sentence_fixes_list: list):
        """ Provides sentence boundary corrections based on counting quotation marks in the whole text.
            First, counts quotation marks in the text, and tries to find out for each quotation mark,
            whether it starts or ends a quotation. Keeps track that starts and ends are in balance.
            Then fixes sentence boundaries based on the found information: 
            * if a sentence starts with an ending quotation mark, then removes the ending quote and 
              adds to the end of the previous sentence;
            * if the movable ending quote is followed by the attribution part of the quote 
              (describing "who uttered the quote"), then moves the  ending  quotation  mark 
              along with the attribution part to the end of the previous sentence;
            * if there is an ending quotation mark inside a sentence, followed instantly by a 
              starting quotation mark, then split the sentence after the ending quotation mark;
            Notes:
            * if start and end quotes are indistinguishable, assumes a flat representation:
              no quotes nested inside other quotes;
            * fixes only in length where it is possible to maintain the balance;
        """
        # A) Find out all locations of starting and ending quotes
        #    Try to guess if an indistinguishable quotation mark is a start or an end
        #    Keep track of the quotes balance
        balance = 0
        starting_quotes_locs = {} 
        ending_quotes_locs   = {} 
        last_balance_location = 0
        for cid, c in enumerate(raw_text):
            # Detect whether we have potential starting or ending quotes
            if _starting_quotes_regexp.match(c):
                if _indistinguishable_quotes.match(c):
                    # Find out if the next letter is uppercase letter
                    nextIsUpper = False
                    next_cid = cid + 1
                    while next_cid < len(raw_text):
                        if not raw_text[next_cid].isspace():
                            if raw_text[next_cid].isupper():
                                nextIsUpper = True
                            break
                        next_cid += 1
                    if nextIsUpper and balance == 0:
                        # For simplicity, assume the flat
                        # representation (no nested quotes)
                        starting_quotes_locs[cid] = 1
                        balance += 1
                else:
                    starting_quotes_locs[cid] = 1
                    balance += 1
            if _ending_quotes_regexp.match(c):
                if _indistinguishable_quotes.match(c):
                    if balance > 0 and cid not in starting_quotes_locs:
                        # For simplicity, assume the flat
                        # representation (no nested quotes)
                        ending_quotes_locs[cid] = 1
                        balance -= 1
                else:
                    ending_quotes_locs[cid] = 1
                    balance -= 1
            if balance == 0:
                last_balance_location = cid
        #
        # B) if we are out of balance, then roll back to the last location where the balance held
        # 
        if balance != 0 and last_balance_location > 0:
            # Remove all the positions after the last balance location
            start_locs = list(starting_quotes_locs.keys())
            for s_loc in start_locs:
                if s_loc > last_balance_location:
                    del starting_quotes_locs[s_loc]
            end_locs = list(ending_quotes_locs.keys())
            for e_loc in end_locs:
                if e_loc > last_balance_location:
                    del ending_quotes_locs[e_loc]
            balance = 0
        
        # C) If we are in the balance, then found locations are likely correct, and 
        #    we can use these to post-correct misplaced sentence boundaries
        if balance == 0 and len(starting_quotes_locs.keys()) > 0 and \
           len(starting_quotes_locs.keys()) == len(ending_quotes_locs.keys()):
            
            sorted_ends = sorted(list(ending_quotes_locs.keys()))
            end_i = 0
            
            # Iterate over all (adjacent) sentences
            removable_sentence_ids = []
            new_splits = {}
            corrected_sid = 0 # <-- takes account of removed sentences
            for sid, sentence_spl in enumerate(sentences_list):
                this_sentence_fixes = sentence_fixes_list[sid]
                this_sentence_start = sentence_spl[0].start
                this_sentence_end   = sentence_spl[-1].end
                if last_balance_location < this_sentence_start:
                    # No more balance: break
                    break
                if sid > 0:
                    # If the sentence starts with an quote ending, then the ending
                    # is likely wrongly attributed from the last sentence
                    if sentence_spl[0].start in ending_quotes_locs.keys():
                        # Move the ending quotation mark to the previous sentence
                        last = sentence_spl.pop(0)
                        prev_sentence_spl = sentences_list[sid-1]
                        prev_sentence_spl.append(last)
                        this_sentence_fixes.append('double_quotes_counting')
                        last_sentence_fixes = sentence_fixes_list[sid-1]
                        last_sentence_fixes.append('double_quotes_counting')
                        # Check the remaining sentence: if it is likely
                        # the attribution part of the quote, describing "who 
                        # uttered the quote", then the whole sentence should
                        # be appended to the previous sentence ...
                        if len(sentence_spl) > 0:
                            # ... if the next token starts with a lowercase letter ...
                            # ( so, it doesn't look like a start of a new sentence )
                            nextTokenLower = raw_text[sentence_spl[0].start].islower()
                            # ... and the previous sentence begins with a titlecase 
                            #     word ...
                            # ( so, this text likely follows the convention that 
                            #   sentences start with titlecase words ) 
                            prevSentBeginsUpper = False
                            if raw_text[prev_sentence_spl[0].start].isupper() or \
                               (not raw_text[prev_sentence_spl[0].start].isalpha() and \
                                len(prev_sentence_spl) > 1 and \
                                raw_text[prev_sentence_spl[1].start].isupper()):
                                prevSentBeginsUpper = True
                            # ... there are no more quotation marks inside the sentence ...
                            noQuotationMarks = True
                            for cur_sent_span in sentence_spl:
                                if cur_sent_span.start in starting_quotes_locs.keys() or \
                                   cur_sent_span.start in ending_quotes_locs.keys():
                                    noQuotationMarks = False
                                    break
                            if nextTokenLower and prevSentBeginsUpper and noQuotationMarks:
                                # ... then append the whole current sentence to the last 
                                #     sentence:  this sentence is likely the attribution 
                                #     part of the quote, describing "who uttered the quote"
                                while len(sentence_spl) > 0:
                                    last = sentence_spl.pop(0)
                                    prev_sentence_spl.append(last)
                        # If the modified sentence is empty, add it to removables
                        if len(sentence_spl) == 0:
                            removable_sentence_ids.append( sid )
                            # Reduce corrected sentence index
                            corrected_sid -= 1
                # Check quotation ending marks inside the sentence: 
                #   iff a quotation ends, and another starts instantly 
                #   inside the sentence, then remember the location for 
                #   splitting the sentence;
                while end_i < len(sorted_ends) and len(sentence_spl) > 0:
                    # Get the latest sentence boundaries:
                    this_sentence_start = sentence_spl[0].start
                    this_sentence_end   = sentence_spl[-1].end
                    # Get the ending quote location:
                    end_loc = sorted_ends[end_i]
                    # If the ending quote falls into the sentence:
                    if this_sentence_start <= end_loc and \
                       end_loc < this_sentence_end:
                        # Find out if we have a reason for splitting:
                        # the next symbol is a quotation start,
                        foundSplitLocation = False
                        cur_loc = end_loc + 1
                        while cur_loc < this_sentence_end:
                            if not raw_text[cur_loc].isspace():
                                if cur_loc in starting_quotes_locs:
                                    foundSplitLocation = True
                                #elif raw_text[cur_loc].isupper():
                                #    foundSplitLocation = True
                                #
                                # A developer note: we could also split if the next symbol 
                                # is an uppercase letter,  put  that  would  give incorrect 
                                # splits in contexts like: 
                                #     Ian " Thorpedo " Thorpe'i valmistusid kaasmaalased 
                                #     kuningaks kroonima .
                                #
                                break
                            cur_loc += 1
                        if foundSplitLocation:
                            # Remember the splitting location
                            if corrected_sid not in new_splits:
                                new_splits[corrected_sid] = []
                            new_splits[corrected_sid].append( (end_loc, cur_loc) )
                    if this_sentence_end < end_loc:
                        break
                    end_i += 1
                # Advance corrected sentence index
                corrected_sid += 1

            if len(removable_sentence_ids) > 0:
                # If a sentence became empty after corrections, remove it 
                removable_sentence_ids.reverse()
                for i in removable_sentence_ids:
                    sentences_list.pop(i)
                    sentence_fixes_list.pop(i)
                assert len(sentence_fixes_list) == len(sentences_list)
            
            if len( new_splits ) > 0:
                # We have detected some new locations for splitting 
                new_sentences_list = []
                new_sentence_fixes_list = []
                for sid, sentence_spl in enumerate( sentences_list ):
                    cur_sent_fixes = sentence_fixes_list[sid]
                    if sid in new_splits:
                        this_sent_splits = new_splits[sid]
                        # Small sanity checks
                        this_sentence_start = sentence_spl[0].start
                        this_sentence_end   = sentence_spl[-1].end
                        assert this_sentence_start < this_sent_splits[0][0]+1
                        assert this_sentence_end   > this_sent_splits[-1][-1]
                        # Iterate over words & splits
                        cur_split_id = 0
                        current_words = []
                        for wid, span in enumerate( sentence_spl ):
                            current_words.append( span )
                            cur_split = this_sent_splits[cur_split_id]
                            if wid+1 < len(sentence_spl):
                                next_span = sentence_spl[wid+1]
                                # check if we are at the break location
                                if span.end == cur_split[0] + 1 and \
                                   next_span.start == cur_split[1]:
                                    # Create a new split 
                                    new_sentences_list.append( current_words )
                                    new_sentence_fixes_list.append( ['double_quotes_counting'] )
                                    current_words = []
                                    # Take the next split (if there is next one)
                                    if cur_split_id + 1 < len(this_sent_splits):
                                        cur_split_id += 1
                        if current_words:
                            # append remaining words
                            new_sentences_list.append( current_words )
                            new_sentence_fixes_list.append( ['double_quotes_counting'] )
                    else:
                        # Nothing to split here, move along
                        new_sentences_list.append( sentence_spl )
                        new_sentence_fixes_list.append( cur_sent_fixes )
                sentences_list = new_sentences_list
                sentence_fixes_list = new_sentence_fixes_list
                assert len(sentences_list) == len(sentence_fixes_list)
        return sentences_list, sentence_fixes_list


