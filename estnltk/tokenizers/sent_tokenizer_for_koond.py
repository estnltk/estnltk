# -*- coding: utf-8 -*-
"""
  Sentence tokenizer for processing 'koondkorpus' text files ( as found in 
 http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip ).
 
  Performs the initial (NLTK) sentence tokenization, and then applies several post-processing fixes,
 addressing known sentence-splitting problems:
  *) erroneous split after year number:
     ... mis moodustati 1968 . || aastal .  ==>  ... mis moodustati 1968 . aastal .
  *) erroneous split after date expression:
     ... toimub 22 . || oktoobril Sakala keskuses  ==>  ... toimub 22 . oktoobril Sakala keskuses
  *) erroneous split of range expressions:
     ... 1 . || -3 .  ==>  ... 1. -3.
  *) erroneous break between parentheses:
     ... Kirjandusel ( resp. || raamatul ) on läbi aegade olnud erinevaid funktsioone .
  *) erroneous break after parentheses:
     ... lugeja kurdab ( EPL 31.03. ) || , et valla on pääsenud ...
  *) erroneous break before comma:
     ... telelavastus " Õnne 13 ! " || , mis kuu aja eest jõudis ...
  *) erroneous joining if there is no space after sentence ending punctuation:
     ... Iga päev teeme valikuid.Valime kõike alates ... ==> ...teeme valikuid.||Valime kõike ...
  
"""
from __future__ import unicode_literals, print_function, absolute_import

import re

from nltk.tokenize.api import StringTokenizer

hypen_pat = '(-|\u2212|\uFF0D|\u02D7|\uFE63|\u002D|\u2010|\u2011|\u2012|\u2013|\u2014|\u2015)'

merge_patterns = [ \
   #   AASTAARV PUNKT + aasta.*
   [re.compile('(.+\s)?'+hypen_pat+'?([0-9]+)\s+\.$'), re.compile('^aasta.*') ], \
   #   KUUPAEV PUNKT + KUUNIMI_PIKALT.*
   [re.compile('(.+\s)?'+hypen_pat+'?([0-9]{1,2})\s+\.$'), re.compile('^(jaan|veeb|märts|apr|mai|juul|juun|augu|septe|okto|nove|detse).*') ], \
   #   KUUPAEV PUNKT + KUUNIMI_LYHIDALT.*
   [re.compile('(.+\s)?'+hypen_pat+'?([0-9]{1,2})\s+\.$'), re.compile('^(jaan|veeb|mär|apr|mai|juul|juun|aug|sept|okt|nov|dets)\..*') ], \
   #   VAHEMIKU_ALGUS PUNKT + KRIIPS VAHEMIKU_LOPP PUNKT
   [re.compile('(.+\s)?([0-9]+)\s*\.$'), re.compile(hypen_pat+'\s*([0-9]+)\s*\.$') ], \
   #   VAHEMIKU_ALGUS PUNKT KRIIPS + VAHEMIKU_LOPP PUNKT
   [re.compile('(.+\s)?([0-9]+)\s*\.\s*'+hypen_pat+'$'), re.compile('([0-9]+)\s*\.$') ], \
   #   ALGAV_SULG + (väiketäht_või_koma) ja LOPPEV_SULG
   [re.compile('.*\([^()]+$'), re.compile('^[a-zöäüõ,][^()]*\).*') ], \
   #   ALGAV_SULG + LOPPEV_SULG
   [re.compile('.*\([^()]+$'), re.compile('^\).*') ], \
   #   SULUPAAR + väiketäht_või_koma
   [re.compile('.*\([^()]+\)$'), re.compile('[a-zöäüõ,].+') ], \
   #   SULUPAAR + lauselõpumärk
   [re.compile('.*\([^()]+\)$'), re.compile('[.?!]$') ], \
   #   hyyu/kysimärk_(ja_jutum2rgi_l6pp) + koma_väiketäht
   [re.compile('.+[?!]\s*["\u00BB\u02EE\u030B\u201C\u201D\u201E]?$'), re.compile('^[,;]\s*[a-zöäüõ]-*') ], \
]

break_patterns = [ \
   #   V2HEMALT_2_T2HE_PIKKUNE_SONA + PUNKT + V2HEMALT_2_T2HE_PIKKUNE_SUURT2HEGA_SONA
   [re.compile('([a-zöäüõšž]{2,})\.([A-ZÖÄÜÕŠŽ][a-zöäüõšž]+)'), 2, 'start'], \
]


class SentenceTokenizerForKoond( StringTokenizer ):
    sentence_tokenizer = None

    def __init__(self, **kwargs):
        # use NLTK-s sentence tokenizer for Estonian, in case it is not downloaded, try to download it first
        import nltk.data
        try:
            self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')
        except LookupError:
            import nltk.downloader
            nltk.downloader.download('punkt')
        finally:
            if self.sentence_tokenizer is None:
                self.sentence_tokenizer = nltk.data.load('tokenizers/punkt/estonian.pickle')

    def tokenize(self, s):
        return self.tokenize_text(s)[0]

    def span_tokenize(self, s):
        return self.tokenize_text(s)[1]

    def tokenize_text(self, text):
        #
        # 1) Perform the initial tokenization
        #
        spans = list(self.sentence_tokenizer.span_tokenize(text))
        #
        # 2) Try to merge mistakenly broken sentences
        #
        new_spans = []
        for sid, (s2, e2) in enumerate(spans):
            text_this  = text[s2:e2].strip()
            mergeSpans = False
            if sid-1 > -1:
                s1 = spans[sid-1][0]
                e1 = spans[sid-1][1]
                text_last = text[s1:e1].strip()
                for [beginPat, endPat] in merge_patterns:
                    if beginPat.match(text_last) and endPat.match(text_this):
                        mergeSpans = True
                        break
            if mergeSpans:
                if not new_spans:
                    new_spans.append( [s1, e2] )
                else:
                    new_spans[-1][1] = e2
            else:
                new_spans.append( [s2, e2] )
        #
        # 3) Try to break mistakenly joined sentences
        #
        spans = [(s, e) for [s, e] in new_spans]
        break_points = []
        # Find all breakpoints
        for [pattern, break_group, str_end] in break_patterns:
            for match in pattern.finditer( text ):
                if str_end == 'start':
                    break_point = match.start(break_group)
                elif str_end == 'end':
                    break_point = match.end(break_group)
                break_points.append( break_point )
        break_points = sorted(break_points)
        # Correct current spans using the newly found breakpoints
        new_spans = []
        for sid, (s1, e1) in enumerate( spans ):
            current_spans = [[s1, e1]]
            for break_point in break_points:
                if (break_point > current_spans[-1][0]) and (break_point < current_spans[-1][1]):
                    last_span = current_spans.pop()
                    current_spans.append( (last_span[0], break_point) )
                    current_spans.append( (break_point, last_span[1]) )
                if (break_point > current_spans[-1][1]):
                    break
            new_spans.extend( current_spans )
        #
        # 4) Convert new spans to tuples
        #
        spans = [(s, e) for [s, e] in new_spans]
        #for (s, e) in spans:
        #    print('>>>', s,e,text[s:e])
        texts = [text[s:e] for (s, e) in spans]
        return texts, spans

