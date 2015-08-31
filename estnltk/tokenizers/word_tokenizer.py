# -*- coding: utf-8 -*-
"""
Estonian word tokenizer module.

In a nutshell, it is exactly the same as NLTK-s WordPunctTokenizer, but it concatenates consequent tokens for
following cases:

- ordinal numbers: 1. 2. 3.
- ranges, compund words: 25-28, D-vitamiin
- fractions: 3.14 ; 3,14 ; 3/4

See https://github.com/estnltk/estnltk/issues/25 for more info.
"""
from __future__ import unicode_literals, print_function, absolute_import

from nltk.tokenize.regexp import WordPunctTokenizer
from nltk.tokenize.api import StringTokenizer
import regex as re

wptokenizer = WordPunctTokenizer()
digits = re.compile('\d+')


def join_ordinals(left, right):
    return right == '.' and digits.match(left) is not None


def join_hyphen(left, right):
    return left == '-' or right == '-'


def join_range(left, middle, right):
    return middle == '-'


def join_fraction(left, middle, right):
    return digits.match(left) is not None and middle in [',', '.', '/'] and digits.match(right) is not None


bi_rules = [join_ordinals, join_hyphen]
tri_rules = [join_range, join_fraction]


def apply_rules(tokens, spans, n, rules):
    res_tokens, res_spans = [], []
    for token, span in zip(tokens, spans):
        res_tokens.append(token)
        res_spans.append(span)
        # if there are enough tokens, we can try applying rules
        if len(res_tokens) >= n:
            # first check if the tokens are consequent
            span_match = True
            for i in range(n - 1):
                if res_spans[-i-1][0] != res_spans[-i-2][1]:
                    span_match = False
                    break
            if span_match:
                # test each rule
                test_tokens = res_tokens[-n:]
                for rule in rules:
                    if rule(*test_tokens):
                        # if a rule matches, concatenate the tokens and the spans
                        res_tokens[-n:] = [''.join(test_tokens)]
                        res_spans[-n:] = [(res_spans[-n][0], res_spans[-1][1])]
    return res_tokens, res_spans


def word_tokenize(text):
    spans = list(wptokenizer.span_tokenize(text))
    tokens = [text[s:e] for s, e in spans]
    tokens, spans = apply_rules(tokens, spans, 3, tri_rules)
    tokens, spans = apply_rules(tokens, spans, 2, bi_rules)
    return tokens, spans


class EstWordTokenizer(StringTokenizer):

    def tokenize(self, s):
        return word_tokenize(s)[0]

    def span_tokenize(self, s):
        return word_tokenize(s)[1]
