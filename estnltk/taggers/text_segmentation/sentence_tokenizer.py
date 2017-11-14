#
#  Tags sentence boundaries, and applies sentence tokenization post-corrections, if required.
#
from typing import Iterator, Tuple

import re

from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger

_hyphen_pat = '(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015|-)'
_lc_letter  = '[a-zöäüõžš]'
_uc_letter  = '[A-ZÖÄÜÕŽŠ]'
_not_letter = '[^A-ZÖÄÜÕŽŠa-zöäüõžš]'
_start_quotes  = '"\u00AB\u02EE\u030B\u201C\u201D\u201E'
_ending_quotes = '"\u00BB\u02EE\u030B\u201C\u201D\u201E'
# regexp for matching a single token consisting only of sentence-ending punctuation
_ending_punct_regexp = re.compile('^[.?!…]+$')

# Patterns describing how two mistakenly split 
# adjacent sentences can be merged into one sentence
merge_patterns = [ \
   # ***********************************
   #   Fixes related to numbers, number ranges, dates and times 
   # ***********************************
   #   {Numeric_range_start} {period} + {dash} {Numeric_range_end}
   { 'comment'  : '{Numeric_range_start} {period} + {dash} {Numeric_range_end}', \
     'example'  : '"Tartu Muinsuskaitsepäevad toimusid 1988. a 14." + "- 17. aprillil."', \
     'fix_type' : 'numeric_range', \
     'regexes'  : [re.compile('(.+)?([0-9]+)\s*\.$', re.DOTALL),re.compile(_hyphen_pat+'\s*([0-9]+)\s*\.(.*)?$', re.DOTALL)], \
   },
   #   {Numeric_range_start} {period} {dash} + {Numeric_range_end}
   { 'comment'  : '{Numeric_range_start} {period} {dash} + {Numeric_range_end}', \
     'example'  : '"Tartu Muinsuskaitsepäevad toimusid 1988. a 14." + "- 17. aprillil."', \
     'fix_type' : 'numeric_range', \
     'regexes'  : [re.compile('(.+)?([0-9]+)\s*\.\s*'+_hyphen_pat+'$', re.DOTALL), re.compile('([0-9]+)\s*\.(.+)?$', re.DOTALL) ], \
   },

   #   {Numeric_year} {period} {|a|} + {lowercase_or_number}
   { 'comment'  : '{Numeric_year} {period} {|a|} + {lowercase_or_number}', \
     'example'  : '"Luunja sai vallaõigused 1991.a." + " kevadel."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile('(.+)?([0-9]{3,4})\s*\.?\s*a\s*\.$', re.DOTALL), re.compile('^('+_lc_letter+'|[0-9])+')], \
   },
   { 'comment'  : '{Numeric_year} {period} {|a|} + {lowercase_or_number}', \
     'example'  : '"1946/47 õ.a." + "oli koolis 87 õpilast."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile('(^|.+)([0-9]{4}\s*\.?|/\s*[0-9]{2})\s*õ\s*\.?\s*a\.?$', re.DOTALL), re.compile('^('+_lc_letter+'|[0-9])+')], \
   },
   #   {Numeric_year} {period} + {|a|} {lowercase_or_number}
   { 'comment'  : '{Numeric_year} {period} + {|a|} {lowercase_or_number}', \
     'example'  : '"Luunja sai vallaõigused 1991.a." + " kevadel."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [ re.compile('(.+)?([0-9]{4})\s*\.$', re.DOTALL), re.compile('^\s*(õ\s*\.)?a\.?\s*('+_lc_letter+'|[0-9])+') ], \
   },
   #   {Numeric_year} {period} + {|aasta|}
   { 'comment'  : '{Numeric_year} {period} + {|aasta|}', \
     'example'  : '"BRK-de traditsioon sai alguse 1964 ." + "aastal Saksamaal Heidelbergis."', \
     'fix_type' : 'numeric_year', \
     'regexes'  : [re.compile('(.+)?([0-9]{3,4})\s*\.$', re.DOTALL), re.compile('^'+_lc_letter+'*aasta.*') ], \
   },
   #   {Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}
   { 'comment'  : '{Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}', \
     'example'  : '"... Mileetose koolkonnd (VI-V saj." + "e. Kr.) ..."', \
     'fix_type' : 'numeric_century', \
     'regexes'  : [re.compile('(.+)?([0-9]{1,2}|[IVXLCDM]+)\s*\.?\s*saj\.?$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },
   
   #   {Date_dd.mm.yyyy.} + {time_HH:MM}
   { 'comment'  : '{Date_dd.mm.yyyy.} + {time_HH:MM}', \
     'example'  : "'Gert 02.03.2009.' + '14:40 Tahaks kindlalt sinna kooli:P'", \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile('(.+)?([0-9]{2})\.([0-9]{2})\.([0-9]{4})\.\s*$', re.DOTALL), re.compile('^\s*([0-9]{2}):([0-9]{2})')], \
   },
   #   {|kell|} {time_HH.} + {MM}
   { 'comment'  : '{|kell|} {time_HH.} + {MM}', \
     'example'  : "'Kell 22 .' + '00\nTV 3\n“ Thelma”\n'", \
     'fix_type' : 'numeric_time', \
     'regexes'  : [re.compile('(.+)?[kK]ell\S?\s([0-9]{1,2})\s*\.\s*$', re.DOTALL), re.compile('^\s*([0-9]{2})\s')], \
   },

   #   {Numeric_date} {period} + {month_name}
   { 'comment'  : '{Numeric_date} {period} + {month_name}', \
     'example'  : '"Kirijenko on sündinud 26 ." + "juulil 1962 . aastal ."', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile('(.+)?([0-9]{1,2})\s*\.$', re.DOTALL), re.compile('^(jaan|veeb|märts|apr|mai|juul|juun|augu|septe|okto|nove|detse).*') ], \
   },
   #   {Numeric_date} {period} + {month_name_short}
   { 'comment'  : '{Numeric_date} {period} + {month_name_short}', \
     'example'  : '"( NYT , 5 ." + "okt . )"', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile('(.+)?([0-9]{1,2})\s*\.$', re.DOTALL), re.compile('^(jaan|veebr?|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)(\s*\.|\s).*') ], \
   },
   #  {Month_name_short} {period} + {numeric_year}
   { 'comment'  : '{Numeric_date} {period} + {month_name_short}', \
     'example'  : '"17. okt." + "1998 a."', \
     'fix_type' : 'numeric_date', \
     'regexes'  : [re.compile('^(.+)?\s(jaan|veebr?|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)\s*\..*', re.DOTALL), re.compile('([0-9]{4})\s*.*') ], \
   },

   #   {First_10_Roman_numerals} {period} + {lowercase_or_dash}
   { 'comment'  : '{First_10_Roman_numerals} {period} + {lowercase_or_dash}', \
     'example'  : '"III." + "- II." + "sajandil enne meie ajastut toimunud sõjad."', \
     'fix_type' : 'numeric_roman_numeral', \
     'regexes'  : [re.compile('(.+)?((VIII|III|VII|II|IV|VI|IX|V|I|X)\s*\.)$', re.DOTALL), re.compile('^('+_lc_letter+'|'+_hyphen_pat+')') ], \
   },
   
   #   {Number} {period} + {lowercase}
   { 'comment'  : '{Number} {period} + {lowercase}', \
     'example'  : '"sügisringi 4 ." + "vooru kohtumine"', \
     'fix_type' : 'numeric_ordinal_numeral', \
     'regexes'  : [re.compile('(.+)?([0-9]+)\s*\.$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },
   #   {Number} {period} + {hyphen}
   { 'comment'  : '{Number} {period} + {hyphen}', \
     'example'  : '"1500." + "- kuni 3000." + "- krooni"', \
     'fix_type' : 'numeric_monetary', \
     'regexes'  : [re.compile('(.+)?([0-9]+)\s*\.$', re.DOTALL), re.compile('^'+_hyphen_pat+'+') ], \
   },
   
   # ***********************************
   #   Fixes related to specific abbreviations
   # ***********************************
   #   {BCE} {period} + {lowercase}
   { 'comment'  : '{BCE} {period} + {lowercase}', \
     'example'  : '"Suur rahvasterändamine oli avanud IV-nda sajandiga p. Kr." + "segaduste ja sõdade ajastu."', \
     'fix_type' : 'abbrev_century', \
     'regexes'  : [re.compile('(.+)?[pe]\s*\.\s*Kr\s*\.?$', re.DOTALL), re.compile('^'+_lc_letter+'+') ], \
   },

   { 'comment'  : '{Abbreviation} {period} + {numeric}', \
     'example'  : '"Hõimurahvaste Aeg Nr." + "7 lk." + "22."', \
     'fix_type' : 'abbrev_numeric', \
     'regexes'  : [re.compile('(.+)?([Ll]k|[Nn]r)\s*\.$', re.DOTALL), re.compile('^[0-9]+') ], \
   },
   { 'comment'  : '{Common_abbreviation} {period} + {lowercase|hyhen|,|)}', \
     'example'  : '"jooniste, tabelite jm." + "selgeks tehti."', \
     'fix_type' : 'abbrev_common', \
     'regexes'  : [re.compile('(.+)?\s(ingl|näit|'+
                                      'jm[st]|jne|jp[mt]|mnt|pst|tbl|vm[st]|'+\
                                      'j[tm]|mh|vm|e|t)\s?[.]$', re.DOTALL), \
                   re.compile('^('+_lc_letter+'|'+_hyphen_pat+'|,|;|\))') ], \
   },
   #   {abbreviation} {period} + {comma_or_semicolon}
   { 'comment'  : '{abbreviation} {period} + {comma_or_semicolon}', \
     'example'  : "(Ribas jt.' + ', 1995; Gebel jt.' + ', 1997; Kaya jt.' + ', 2004)", \
     'fix_type' : 'abbrev_common', \
     'regexes'  : [re.compile('.+\s[a-zöäüõ\-.]+[.]\s*$', re.DOTALL), re.compile('^([,;]).*') ], \
   },
   
   #   {uppercase_letter} {period} + {not_uppercase_followed_by_lowercase}
   { 'comment'  : '{uppercase_letter} {period} + {not_uppercase_followed_by_lowercase}', \
     'example'  : "'K.' + 'C.' + 'seal nime ees tähendab Kadri’s Choise'", \
     'fix_type' : 'abbrev_name_initial', \
     'regexes'  : [re.compile('(.*'+_not_letter+'|^)'+_uc_letter+'\s*[.]\s*$', re.DOTALL), \
                   re.compile('^(?!\s*'+_uc_letter+_lc_letter+').*') ], \
   },

   # ***********************************
   #   Fixes related to parentheses 
   # ***********************************
   #   {period_ending_content_of_parentheses} + {lowercase_or_comma}
   { 'comment'  : '{period_ending_content_of_parentheses} + {lowercase_or_comma}', \
     'example'  : '"Lugesime Menippose (III saj. e.m.a.)" + "satiiri..."', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('(.+)?\([^()]+[.!]\s*\)$', re.DOTALL), re.compile('^('+_lc_letter+'|,)+.*')], \
   },
   #   {parentheses_start} {content_in_parentheses} + {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {parentheses_end}', \
     'example'  : '( " Easy FM , soft hits ! "\' + \') .', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('.*\([^()]+$', re.DOTALL), re.compile('^[^()A-ZÖÄÜÕŠŽ]*\)\s*$') ], \
   },
   #   {parentheses_start} {content_in_parentheses} + {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {parentheses_end}', \
     'example'  : '( " Easy FM , soft hits ! "\' + \') .', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('.*\([^()]+$', re.DOTALL), re.compile('^[^()A-ZÖÄÜÕŠŽ]*\)(\s|\n)*[^A-ZÖÄÜÕŠŽ \n].*') ], \
   },
   #   {ending_punctuation} + {parentheses_end}<end> {uppercase}
   { 'comment'   : '{ending_punctuation} + {parentheses_end}<end> {uppercase}', \
     'example'   : "'( Naerab . ' + ')\nEriti siis , kui sõidan mootorratta või jalgrattaga .'", \
     'fix_type'  : 'parentheses', \
     'regexes'   : [re.compile('.*[.!?]\s*$', re.DOTALL), re.compile('^(?P<end>\))(\s|\n)*[A-ZÖÄÜÕŠŽ].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {parentheses_start} {content_in_parentheses} + {lowercase_or_comma} {content_in_parentheses} {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {lowercase_or_comma} {content_in_parentheses} {parentheses_end}', \
     'example'  : '"(loe: ta läheb sügisel 11." + " klassi!)"', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('(.+)?\([^()]+$', re.DOTALL), re.compile('^('+_lc_letter+'|,)[^()]+\).*')], \
   },
   #   {parentheses_start} {content_in_parentheses} + {numeric_patterns} {parentheses_end}
   { 'comment'  : '{parentheses_start} {content_in_parentheses} + {numeric_patterns} {parentheses_end}', \
     'example'  : '"rahvuskultuuriline missioon ( lk." + "217 )"', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('.*\([^()]+$', re.DOTALL), re.compile('^[0-9.\- ]+\).*') ], \
   },
   #   {content_in_parentheses} + {single_sentence_ending_symbol}
   { 'comment'  : '{content_in_parentheses} + {single_sentence_ending_symbol}', \
     'example'  : '\'( " Easy FM , soft hits ! " )\' + \'.\'', \
     'fix_type' : 'parentheses', \
     'regexes'  : [re.compile('.*\([^()]+\)$', re.DOTALL), _ending_punct_regexp ], \
   },
   
   # ***********************************
   #   Fixes related to double quotes
   # ***********************************
   #   {sentence_ending_punct} + {ending_quotes} {comma_or_semicolon_or_lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}', \
     'example'  : '\'ETV-s esietendub homme " Õnne 13 ! \' + \'", mis kuu aja eest jõudis lavale Ugalas .\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile('.+[?!.…]\s*$', re.DOTALL), re.compile('^['+_ending_quotes+']\s*([,;]|'+_lc_letter+')+') ], \
   },
   #   {sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {comma_or_semicolon_or_lowercase_letter}', \
     'example'  : '\'ETV-s esietendub homme " Õnne 13 ! "\' + \', mis kuu aja eest jõudis lavale Ugalas .\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile('.+[?!.…]\s*['+_ending_quotes+']$', re.DOTALL), re.compile('^([,;]|'+_lc_letter+')+') ], \
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
     'regexes'   : [re.compile('.*[.!?]\s*$', re.DOTALL), re.compile('^(?P<end>['+_ending_quotes+'])(\s|\n)*['+_start_quotes+'].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {ending_punctuation} + {ending_quotes}<end> {starting_brackets}
   { 'comment'   : '{ending_punctuation} + {ending_quotes}<end> {starting_brackets}', \
     'example'   : "'« Kus on minu mesi ?' + '»\n( Inglise keeles kallim . )'", \
     'fix_type'  : 'double_quotes', \
     'regexes'   : [re.compile('.*[.!?]\s*$', re.DOTALL), re.compile('^(?P<end>['+_ending_quotes+'])(\s|\n)*[(\[].*') ], \
     'shift_end' : True,   # sentence end needs to be shifted to the string captured by the pattern <end>
   },
   #   {sentence_ending_punct} {ending_quotes} + {only_sentence_ending_punct}
   { 'comment'  : '{sentence_ending_punct} + {ending_quotes} {only_sentence_ending_punct}', \
     'example'  : '\'\nNii ilus ! \' + \'" .\' + \'\nNõmmel elav pensioniealine Maret\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile('.+[?!.…]\s*$', re.DOTALL), re.compile('^['+_ending_quotes+']\s*[?!.…]+$') ], \
   },
   { 'comment'  : '{sentence_ending_punct} {ending_quotes} + {only_sentence_ending_punct}', \
     'example'  : '\'\nNii ilus ! " \' + \' . \nNõmmel elav pensioniealine Maret\'', \
     'fix_type' : 'double_quotes', \
     'regexes'  : [re.compile('.+[?!.…]\s*['+_ending_quotes+']$', re.DOTALL), _ending_punct_regexp ], \
   },

   # ***********************************
   #   Fixes related to prolonged sentence ending punctuation
   # ***********************************
   #   {sentence_ending_punct} + {only_sentence_ending_punct}
   { 'comment'  : '{sentence_ending_punct} + {only_sentence_ending_punct}', \
     'example'  : '"arvati , et veel sellel aastal j6uab kohale ; yess !" + "!" + "!"', \
     'fix_type' : 'repeated_ending_punct', \
     'regexes'  : [re.compile('.+[?!.…]\s*$', re.DOTALL), _ending_punct_regexp ], \
   },
   
   # ***********************************
   #   Fixes related to punctuation in titles inside the sentence
   # ***********************************
   #   {sentence_ending_punct} + {comma_or_semicolon} {lowercase_letter}
   { 'comment'  : '{sentence_ending_punct} + {comma_or_semicolon} {lowercase_letter}', \
     'example'  : '"Jõulise naissolistiga Conflict OK !" + ", kitarripoppi mängivad Claires Birthday ja Seachers."', \
     'fix_type' : 'inner_title_punct', \
     'regexes'  : [re.compile('.+[?!]\s*$', re.DOTALL), re.compile('^([,;])\s*'+_lc_letter+'+') ], \
   },
]


class SentenceTokenizer(Tagger):
    description   = 'Groups words into sentences, and applies sentence tokenization post-corrections, if required.'
    layer_name    = 'sentences'
    attributes    = ()
    depends_on    = ['compound_tokens', 'words']
    configuration = {}
    sentence_tokenizer = None
    
    def __init__(self, 
                 fix_paragraph_endings:bool = True,
                 fix_compound_tokens:bool = True,
                 fix_numeric:bool = True,
                 fix_parentheses:bool = True,
                 fix_double_quotes:bool = True,
                 fix_inner_title_punct:bool = True,
                 fix_repeated_ending_punct:bool = True,
                 use_emoticons_as_endings:bool = True,
                 ):
        # 0) Record configuration
        self.configuration = {'fix_paragraph_endings': fix_paragraph_endings,
                              'fix_compound_tokens': fix_compound_tokens,
                              'fix_numeric': fix_numeric,
                              'fix_parentheses': fix_parentheses,
                              'fix_double_quotes': fix_double_quotes,
                              'fix_inner_title_punct':fix_inner_title_punct,
                              'fix_repeated_ending_punct':fix_repeated_ending_punct,
                              'use_emoticons_as_endings':use_emoticons_as_endings,}
        # 1) Initialize NLTK's tokenizer
        # use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
        import nltk as nltk
        try:
            self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
        except LookupError:
            import nltk.downloader
            nltk.downloader.download('punkt')
        finally:
            if self.sentence_tokenizer is None:
                self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
        # 2) Filter rules according to the given configuration
        self.merge_rules = []
        for merge_pattern in merge_patterns:
            # Fixes that use both built-in logic, and merge rules
            if fix_compound_tokens and merge_pattern['fix_type'].startswith('abbrev'):
                self.merge_rules.append( merge_pattern )
            if fix_repeated_ending_punct and merge_pattern['fix_type'].startswith('repeated_ending_punct'):
                self.merge_rules.append( merge_pattern )
            # Fixes that only use merge rules
            if fix_numeric and merge_pattern['fix_type'].startswith('numeric'):
                self.merge_rules.append( merge_pattern )
            if fix_parentheses and merge_pattern['fix_type'].startswith('parentheses'):
                self.merge_rules.append( merge_pattern )
            if fix_double_quotes and merge_pattern['fix_type'].startswith('double_quotes'):
                self.merge_rules.append( merge_pattern )
            if fix_inner_title_punct and merge_pattern['fix_type'].startswith('inner_title_punct'):
                self.merge_rules.append( merge_pattern )


    def _tokenize_text(self, text: 'Text') -> Iterator[Tuple[int, int]]:
        ''' Tokenizes into sentences based on the input text. '''
        return self.sentence_tokenizer.span_tokenize(text.text)

    def _sentences_from_tokens(self, text: 'Text') -> Iterator[Tuple[int, int]]:
        ''' Tokenizes into sentences based on the word tokens of the input text. '''
        words = list(text.words)
        word_texts = text.words.text
        i = 0
        for sentence_words in self.sentence_tokenizer.sentences_from_tokens(word_texts):
            if sentence_words:
                first_token = i
                last_token  = i + len(sentence_words) - 1
                yield (words[first_token].start, words[last_token].end)
                i += len(sentence_words)

    def tag(self, text:'Text', return_layer:bool=False,
                               record_fix_types:bool=False) -> 'Text':
        #sentence_ends = {end for _, end in self._tokenize_text(text)}
        sentence_ends = {end for _, end in self._sentences_from_tokens(text)}
        # A) Remove sentence endings that:
        #   A.1) coincide with endings of non_ending_abbreviation's
        #   A.2) fall in the middle of compound tokens
        if self.configuration['fix_compound_tokens']:
            for ct in text.compound_tokens:
                if 'non_ending_abbreviation' in ct.type:
                    sentence_ends -= {span.end for span in ct}
                else:
                    sentence_ends -= {span.end for span in ct[0:-1]}
        # B) Use repeated/prolonged sentence punctuation as sentence endings
        if self.configuration['fix_repeated_ending_punct']:
            repeated_ending_punct = []
            for wid, word in enumerate(text.words):
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
                    if wid+1 < len(text.words):
                        next_word = text.words[wid+1].text
                        if len(next_word) > 1 and \
                           next_word[0].isupper() and \
                           next_word[1].islower():
                            # we have a likely sentence boundary:
                            # add it to the set of sentence ends
                            sentence_ends.add( word.end )
                            # Check if the token before punctuation is '[', 
                            # '(' or '"'; If so, then discard the sentence 
                            # ending ...
                            if wid - len(repeated_ending_punct) > -1:
                                prev_word = text.words[wid-len(repeated_ending_punct)]
                                if prev_word.text in ['[', '(', '"']:
                                    sentence_ends -= { word.end }
        # C) Use emoticons as sentence endings
        if self.configuration['use_emoticons_as_endings']:
            # C.1) Collect all emoticons (record start locations)
            emoticon_locations = {}
            for ct in text.compound_tokens:
                if 'emoticon' in ct.type:
                    emoticon_locations[ct.start] = ct
            # C.2) Iterate over words and check emoticons
            repeated_emoticons = []
            for wid, word in enumerate( text.words ):
                if word.start in emoticon_locations:
                    repeated_emoticons.append( emoticon_locations[word.start] )
                else:
                    repeated_emoticons = []
                # Check that there is an emoticon (or even few of them)
                if len(repeated_emoticons) > 0:
                    # Check if the next word is not emoticon, and is titlecased
                    if wid+1 < len(text.words):
                        next_word = text.words[wid+1].text
                        if text.words[wid+1].start not in emoticon_locations and \
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
                                prev_word = text.words[wid-len(repeated_emoticons)]
                                sentence_ends -= { prev_word.end }
        # D) Align sentence endings with word startings and endings
        #    Collect span lists of potential sentences
        start = 0
        if len(text.words) > 0:
            sentence_ends.add( text.words[-1].end )
        sentences_list = []
        sentence_fixes_list = []
        for i, token in enumerate(text.words):
            if token.end in sentence_ends:
                sentences_list.append( text.words[start:i+1] )
                start = i + 1
        # E) Use '\n\n' (usually paragraph endings) as sentence endings
        if self.configuration['fix_paragraph_endings']:
            sentences_list, sentence_fixes_list = \
                self._split_by_double_newlines( 
                            text, \
                            sentences_list )
        # F) Apply postcorrection fixes to sentence spans
        # F.1) Try to merge mistakenly split sentences
        if self.merge_rules:
            sentences_list, sentence_fixes_list = \
                self._merge_mistakenly_split_sentences(text,\
                    sentences_list, sentence_fixes_list)
        
        # G) Create the layer and attach sentences
        layer_attributes=self.attributes
        if record_fix_types and 'fix_types' not in layer_attributes:
            layer_attributes += ('fix_types',)
        layer = Layer(enveloping='words',
                      name=self.layer_name,
                      attributes=layer_attributes,
                      ambiguous=False)
        for sid, sentence_span_list in enumerate(sentences_list):
            if record_fix_types:
                # Add information about which types of fixes 
                # were applied to sentences
                sentence_span_list.fix_types = \
                    sentence_fixes_list[sid]
            layer.add_span( sentence_span_list )
        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text


    def _merge_mistakenly_split_sentences(self, text:'Text', sentences_list:list, \
                                                             sentence_fixes_list:list ):
        ''' 
            Uses regular expression patterns (defined in self.merge_rules) to 
            discover adjacent sentences (in sentences_list) that should actually 
            form a single sentence. Merges those adjacent sentences.
            
            The parameter sentence_fixes_list should contain a list of fixes that 
            were already previously added to the elements of sentences_list.
            These lists of fixes are then updated in correspondence with the fixes 
            newly added by this method.
            
            Returns a tuple of two lists:
            *) new version of sentences_list where merges have been made;
            *) correspondingly updated sentence_fixes_list;
        '''
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
                text.text[sentence_spl.start:sentence_spl.end].lstrip()
            current_fix_types = []
            shiftEnding = None
            mergeSpanLists = False
            if sid-1 > -1:
                # get text of the previous sentence
                if not new_sentences_list:
                    last_sentence_spl   = sentences_list[sid-1]
                    last_sentence_fixes = sentence_fixes_list[sid-1]
                else:
                    last_sentence_spl   = new_sentences_list[-1]
                    last_sentence_fixes = new_sentence_fixes_list[-1]
                prev_sent = \
                    text.text[last_sentence_spl.start:last_sentence_spl.end].rstrip()
                # Check if the adjacent sentences should be joined / merged according 
                # to one of the patterns ...
                for pattern in self.merge_rules:
                    [beginPat, endPat] = pattern['regexes']
                    if endPat.match(this_sent) and beginPat.match(prev_sent):
                        mergeSpanLists = True
                        current_fix_types.append(pattern['fix_type'])
                        # Check if ending also needs to be shifted
                        if 'shift_end' in pattern:
                            # Find new sentence ending position and validate it
                            shiftEnding = self._find_new_sentence_ending(text, \
                                          pattern, sentence_spl, last_sentence_spl )
                        break
            if mergeSpanLists:
                # -------------------------------------------
                #   1) Split-and-merge: First merge two sentences, then split at some 
                #      location (inside one of the old sentences)
                # -------------------------------------------
                if shiftEnding:
                    prev_sent_spl = \
                        new_sentences_list[-1] if new_sentences_list else last_sentence_spl
                    merge_split_result = self._perform_merge_split( text, \
                                              shiftEnding, sentence_spl, prev_sent_spl )
                    if merge_split_result != None:
                        if new_sentences_list:
                            # Update sentence spans
                            new_sentences_list[-1] = merge_split_result[0]
                            new_sentences_list.append ( merge_split_result[1] )
                            # Update fix types list
                            new_sentence_fixes_list[-1] = \
                                last_sentence_fixes + current_fix_types
                            new_sentence_fixes_list.append( \
                                this_sentence_fixes + current_fix_types )
                        else:
                            # Update sentence spans
                            new_sentences_list.append ( merge_split_result[0] )
                            new_sentences_list.append ( merge_split_result[1] )
                            # Update fix types list
                            new_sentence_fixes_list.append( \
                                last_sentence_fixes + current_fix_types )
                            new_sentence_fixes_list.append( \
                                this_sentence_fixes + current_fix_types )
                    else:
                        # if merge-and-split failed, then discard the rule
                        # (sentences will remain split as they were)
                        new_spanlist = SpanList()
                        if record_fix_types:
                            new_spanlist.fix_types = []
                        new_spanlist.spans = sentence_spl.spans
                        new_sentences_list.append( new_spanlist )
                        # Update fix types list
                        new_sentence_fixes_list.append( \
                            this_sentence_fixes )
                else:
                    # -------------------------------------------
                    #   2) Merge only: join two consecutive sentences into one
                    # -------------------------------------------
                    # Perform the merging
                    merged_spanlist = SpanList()
                    if not new_sentences_list:
                        # No sentence has been added so far: add a new one
                        merged_spanlist.spans = \
                            last_sentence_spl.spans+sentence_spl.spans
                        new_sentences_list.append( merged_spanlist )
                        # Update fix types list
                        all_fixes = \
                            last_sentence_fixes + \
                            this_sentence_fixes + \
                            current_fix_types
                        new_sentence_fixes_list.append( all_fixes )
                    else: 
                        # At least one sentence has already been added: 
                        # extend the last sentence
                        merged_spanlist.spans = \
                            new_sentences_list[-1].spans+sentence_spl.spans
                        new_sentences_list[-1] = merged_spanlist
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
                new_spanlist = SpanList()
                new_spanlist.spans = sentence_spl.spans
                new_sentences_list.append( new_spanlist )
                # Update fix types list
                new_sentence_fixes_list.append( \
                    this_sentence_fixes )
                #print('>>0',this_sent)
        assert len(new_sentences_list) == len(new_sentence_fixes_list)
        return new_sentences_list, new_sentence_fixes_list



    def _find_new_sentence_ending(self, text:'Text', merge_split_pattern:dict, \
                                        this_sent:SpanList, \
                                        prev_sent:SpanList):
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
                    text.text[this_sent.start:this_sent.end].lstrip()
                m = endPat.match(this_sent_str)
                if m and m.span('end') != (-1, -1):
                    end_span = m.span('end')
                    # span's position in the text
                    start_in_text = this_sent.start + end_span[0]
                    end_in_text   = this_sent.start + end_span[1]
                    # validate that end_in_text overlaps with a word ending
                    matches_word_ending = False
                    for span in this_sent.spans:
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
                    text.text[prev_sent.start:prev_sent.end].lstrip()
                m = beginPat.match(prev_sent_str)
                if m and m.span('end') != (-1, -1):
                    end_span = m.span('end')
                    # span's position in the text
                    start_in_text = prev_sent.start + end_span[0]
                    end_in_text   = prev_sent.start + end_span[1]
                    # validate that end_in_text overlaps with a word ending
                    matches_word_ending = False
                    for span in prev_sent.spans:
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


    def _perform_merge_split(self, text:'Text', end_span:tuple, \
                                   this_sent:SpanList, prev_sent:SpanList ):
        ''' Performs merge-split operation: 1) consecutive sentences prev_sent
            and this_sent will be joined into one sentence, 2) the new joined 
            sentence will be split (into two sentences) at the position end_span;
            
            In case of success, returns 2-element tuple containing SpanList-s 
            corresponding to the sentences that went through to the merge and 
            split;
            
            Returns None, if the sentences would be ill-formed after the merge-
            and-split. For instance, returns None if one of the new sentences 
            would be empty, or if the merge-and-split would result in duplication 
            of tokens;
        '''
        if end_span and end_span != (-1, -1):
            new_sentence1 = []
            new_sentence2 = []
            for sid, span in enumerate( prev_sent.spans ):
                if span.end <= end_span[1]:
                    new_sentence1.append( span )
                elif span.start >= end_span[1]:
                    new_sentence2.append( span )
            for sid, span in enumerate( this_sent.spans ):
                if span.end <= end_span[1]:
                    new_sentence1.append( span )
                elif span.start >= end_span[1]:
                    new_sentence2.append( span )
            # Validity & sanity check
            # 1) The number of covered words/tokens should remain the same
            #    after the split/merge operation:
            if len(prev_sent.spans) + len(this_sent.spans) !=\
               len(new_sentence1)   + len(new_sentence2):
                # The numbers of covered tokens do no match: something 
                # is wrong ...
                return None
            # 2) Both new sentences should have at least 1 token
            if len(new_sentence1) < 1  or  len(new_sentence2) < 1:
                # One of the sentence has 0 length: something is wrong
                return None
            merged_spanlist1 = SpanList()
            merged_spanlist1.spans = new_sentence1
            merged_spanlist2 = SpanList()
            merged_spanlist2.spans = new_sentence2
            return merged_spanlist1, merged_spanlist2
        return None


    def _split_by_double_newlines(self, text:'Text', \
                                        sentences_list:list ):
        ''' Splits sentences inside the given list of sentences by double 
            newlines (usually paragraph endings).
            
            Returns a tuple containing two lists:
            *) a new list of sentences where splitting has been performed;
            *) a list of sentence fixes. Each element in this list 
               represents fixes that were applied to a single sentence by 
               this method. Fixes are given as a list (an empty list, 
               if no fixes were applied to the sentence);
        '''
        double_newline = '\n\n'
        new_sentences_list  = []
        sentence_fixes_list = []
        for sentence_spl in sentences_list:
            # get text of the current sentence
            this_sent_text = \
                text.text[sentence_spl.start:sentence_spl.end]
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
                            text.text[span.end:next_span.start]
                        if double_newline in space_between:
                            # Create a new split 
                            split_spanlist = SpanList()
                            split_spanlist.spans = current_words
                            new_sentences_list.append( split_spanlist )
                            sentence_fixes_list.append( \
                                ['double_newline_ending'] )
                            current_words = []
                if current_words:
                    new_spanlist = SpanList()
                    new_spanlist.spans = current_words
                    new_sentences_list.append( new_spanlist )
                    sentence_fixes_list.append( [] )
            else:
                new_sentences_list.append( sentence_spl )
                sentence_fixes_list.append( [] )
        assert len(new_sentences_list) == len(sentence_fixes_list)
        return new_sentences_list, sentence_fixes_list
