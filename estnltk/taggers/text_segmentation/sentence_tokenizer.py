from typing import Iterator, Tuple

import re

import nltk as nltk

from estnltk.text import Layer, SpanList
from estnltk.taggers import Tagger

hypen_pat = '(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015)'
lc_letter = '[a-zöäüõžš]'

merge_patterns = [ \
   # ***********************************
   #   Fixes related to number ranges, dates and times 
   # ***********************************
   #   {Numeric_range_start} {period} + {dash} {Numeric_range_end}
   #    Example: "Tartu Muinsuskaitsepäevad toimusid 1988. a 14." + "- 17. aprillil."
   [re.compile('(.+\s)?([0-9]+)\s*\.$'), re.compile(hypen_pat+'\s*([0-9]+)\s*\.(.+)?$') ], \
   #   {Numeric_range_start} {period} {dash} + {Numeric_range_end}
   [re.compile('(.+\s)?([0-9]+)\s*\.\s*'+hypen_pat+'$'), re.compile('([0-9]+)\s*\.(.+)?$') ], \

   #   {Numeric_year} {period} {|a|} + {lowercase}
   #   Examples: "Luunja sai vallaõigused 1991.a." + " kevadel."
   #             "Manifest 2, mis kinnitati 2011.a." + "mais Budapestis."
   [re.compile('(.+)?([0-9]{3,4})\s*\.\s*a\.?$'), re.compile('^('+lc_letter+'|[0-9])+') ], \

   #   {Numeric_year} {period} + {|aasta|}
   #   Examples: "BRK-de traditsioon sai alguse 1964 ." + "aastal Saksamaal Heidelbergis."
   #             "Tartu Teaduspargil valmib 2005/2006." + "aastal uus maja."
   [re.compile('(.+)?([0-9]{3,4})\s*\.$'), re.compile('^'+lc_letter+'*aasta.*') ], \

   #   {Numeric|Roman_numeral_century} {period} {|sajand|} + {lowercase}
   #   Example: "... Mileetose koolkonnd (VI-V saj." + "e. Kr.) ..."
   [re.compile('(.+)?([0-9]{1,2}|[IVXLCDM]+)\s*\.?\s*saj\.?$'), re.compile('^'+lc_letter+'+') ], \
   #   {BCE} {period} + {lowercase}
   #   Example: "Suur rahvasterändamine oli avanud IV-nda sajandiga p. Kr." + "segaduste ja sõdade ajastu."
   [re.compile('(.+)?[pe]\s*\.\s*Kr\s*\.?$'), re.compile('^'+lc_letter+'+') ], \
   
   #   {Numeric_date} {period} + {month_name}
   #   Example:  "Kirijenko on sündinud 26 ." + "juulil 1962 . aastal ."
   [re.compile('(.+)?([0-9]{1,2})\s*\.$'), re.compile('^(jaan|veeb|märts|apr|mai|juul|juun|augu|septe|okto|nove|detse).*') ], \
   #   {Numeric_date} {period} + {month_name_short}
   #   Example:  "( NYT , 5 ." + "okt . )"
   [re.compile('(.+)?([0-9]{1,2})\s*\.$'), re.compile('^(jaan|veebr?|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)(\s*\.|\s).*') ], \
   
   # ***********************************
   #   Fixes related to parentheses 
   # ***********************************
   #   {period_ending_content_of_parentheses} + {lowercase_or_comma}
   #   Examples:  "Lugesime Menippose (III saj. e.m.a.)" + "satiiri..."
   #              "Ja kui ma sain 40 , olin siis Mikuga ( Mikk Mikiveriga - Toim. )" + "abi-elus ."
   #              "Kas kohanime ajaloolises tekstis ( nt . 18. saj . )" + "kirjutada tolleaegse nimetusega?"
   [re.compile('(.+)?\([^()]+[.!]\s*\)$'), re.compile('^('+lc_letter+'|,)+.*')], \
   
   #   {parentheses_start} {content_in_parentheses} + {parentheses_end}
   #   Examples:  '( " Easy FM , soft hits ! "' + ') .'
   [re.compile('.*\([^()]+$'), re.compile('^\).*') ], \
   
   #   {parentheses_start} {content_in_parentheses} + {lowercase_or_comma} {content_in_parentheses} {parentheses_end}
   #   Example:   "(loe: ta läheb sügisel 11." + " klassi!)"
   [re.compile('(.+)?\([^()]+$'), re.compile('^('+lc_letter+'|,)[^()]+\).*')], \
   
   #   {content_in_parentheses} + {single_sentence_ending_symbol}
   #   Example:   '( " Easy FM , soft hits ! " )' + '.'
   [re.compile('.*\([^()]+\)$'), re.compile('^[.?!]$') ], \
   
   # ***********************************
   #   Fixes related to double quotes
   # ***********************************
   #   {sentence_ending_punct} {ending_quotes}? + {comma_or_semicolon} {lowercase_letter}
   #   Examples:  'ETV-s esietendub homme " Õnne 13 ! "' + ', mis kuu aja eest jõudis lavale Ugalas .'
   #              "Jõulise naissolistiga Conflict OK !" + ", kitarripoppi mängivad Claires Birthday ja Seachers."
   [re.compile('.+[?!]\s*["\u00BB\u02EE\u030B\u201C\u201D\u201E]?$'), re.compile('^[,;]\s*'+lc_letter+'+') ], \
]


class SentenceTokenizer(Tagger):
    description = 'Tags adjacent words that form a sentence.'
    layer_name = 'sentences'
    attributes = []
    depends_on = ['compound_tokens', 'words']
    configuration = {}

    # use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
    sentence_tokenizer = None

    try:
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
    except LookupError:
        import nltk.downloader
        nltk.downloader.download('punkt')
    finally:
        if sentence_tokenizer is None:
            sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')

    def _tokenize(self, text: 'Text') -> Iterator[Tuple[int, int]]:
        return self.sentence_tokenizer.span_tokenize(text.text)

    def tag(self, text: 'Text', return_layer=False, fix=True) -> 'Text':
        sentence_ends = {end for _, end in self._tokenize(text)}
        if fix:
            # A) Remove sentence endings that coincide with 
            #    endings of non_ending_abbreviation's
            for ct in text.compound_tokens:
                if 'non_ending_abbreviation' in ct.type:
                    sentence_ends -= {span.end for span in ct}
                else:
                    sentence_ends -= {span.end for span in ct[0:-1]}
        # B) Align sentence endings with word startings and endings
        #    Collect span lists of potential sentences
        start = 0
        sentence_ends.add(text.words[-1].end)
        sentences_list = []
        for i, token in enumerate(text.words):
            if token.end in sentence_ends:
                sentences_list.append( text.words[start:i+1] )
                start = i + 1
        # C) Apply postcorrection fixes to sentence spans
        if fix:
            #
            # C.1) Try to merge mistakenly split sentences
            #
            sentences_list = \
                self._merge_mistakenly_split_sentences(text,\
                                                       sentences_list)
        
        # D) Create the layer and attach sentences
        layer = Layer(enveloping='words',
                      name=self.layer_name,
                      ambiguous=False)
        for sentence_span_list in sentences_list:
            layer.add_span( sentence_span_list )
        if return_layer:
            return layer
        text[self.layer_name] = layer
        return text
        
        
    def _merge_mistakenly_split_sentences(self, text:'Text', sentences_list:list):
        ''' 
            Uses regular expression patterns (defined  in  merge_patterns) to 
            discover adjacent sentences (in sentences_list) that should actually 
            form a single sentence. Merges those adjacent sentences.
            
            Returns a new version of sentences_list where merges have been made.
        '''
        new_sentences_list = []
        # Iterate over all adjacent sentences
        for sid, sentence_spl in enumerate(sentences_list):
            last_sentence_spl = None
            # get text of the current sentence
            this_sent = \
                text.text[sentence_spl.start:sentence_spl.end].lstrip()
            mergeSpanLists = False
            if sid-1 > -1:
                # get text of the previous sentence
                if not new_sentences_list:
                    last_sentence_spl = sentences_list[sid-1]
                else:
                    last_sentence_spl = new_sentences_list[-1]
                prev_sent = \
                    text.text[last_sentence_spl.start:last_sentence_spl.end].rstrip()
                # Check if the adjacent sentences should be joined / merged according 
                # to one of the patterns ...
                for [beginPat, endPat] in merge_patterns:
                    if beginPat.match(prev_sent) and endPat.match(this_sent):
                        mergeSpanLists = True
                        break
            if mergeSpanLists:
                # Perform the merging
                merged_spanlist = SpanList()
                if not new_sentences_list:
                    # No sentence has been added so far: add a new one
                    merged_spanlist.spans = \
                        last_sentence_spl.spans+sentence_spl.spans
                    new_sentences_list.append( merged_spanlist )
                else: 
                    # At least one sentence has already been added: 
                    # extend the last sentence
                    merged_spanlist.spans = \
                        new_sentences_list[-1].spans+sentence_spl.spans
                    new_sentences_list[-1] = merged_spanlist
                #print('>>1',prev_sent)
                #print('>>2',this_sent)
            else:
                # Add sentence without merging
                new_spanlist = SpanList()
                new_spanlist.spans = sentence_spl.spans
                new_sentences_list.append( new_spanlist )
                #print('>>0',this_sent)
        sentences_list = new_sentences_list
        return sentences_list
