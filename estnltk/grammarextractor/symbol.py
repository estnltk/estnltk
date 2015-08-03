# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import weakref
import logging
import regex as re
from copy import copy

from .match import Match

logger = logging.getLogger(__name__)


def split_by_case_sensitive(elems):
    case_sensitive = []
    case_insensitive = []
    for elem, case in elems:
        if case:
            case_sensitive.append(elem)
        else:
            case_insensitive.append(elem)
    return case_sensitive, case_insensitive


def concat_regexes(regexes, name):
    return '(?P<{0}>('.format(name) + ')|('.join(regexes) + '))'


class SymbolNode(object):

    def __init__(self, grammar, name, words, regexes, lemmas, postags, productions):
        logger.debug('Initializing symbolnode <{0}> with {1} words, {2} regexes, {3} lemmas and {4} productions'.format(name, len(words), len(regexes), len(lemmas), len(productions)))
        self.name = name
        self.grammar = weakref.proxy(grammar)
        self.productions = productions
        words, iwords = split_by_case_sensitive(words)
        regexes, iregexes = split_by_case_sensitive(regexes)
        patterns = []
        if len(words) > 0:
            regex = re.compile('(?P<{0}>\L<words>)'.format(name), words=words, flags=re.UNICODE)
            patterns.append(regex)
        if len(iwords) > 0:
            regex = re.compile('(?P<{0}>\L<words>)'.format(name), words=iwords, flags = re.UNICODE | re.IGNORECASE)
            patterns.append(regex)
        if len(regexes) > 0:
            regex = re.compile(concat_regexes(regexes, name), re.UNICODE)
            patterns.append(regex)
        if len(iregexes) > 0:
            regex = re.compile(concat_regexes(iregexes, name), re.UNICODE | re.IGNORECASE)
            patterns.append(regex)
        self.regexes = patterns
        self.lemmaregex = None
        if len(lemmas) > 0:
            self.lemmaregex = re.compile('(?P<{0}>\L<lemmas>)'.format(name), lemmas=lemmas, flags=re.UNICODE | re.IGNORECASE)
        self.postagregex = None
        if len(postags) > 0:
            self.postagregex = re.compile('(?P<{0}>\L<postags>)'.format(name), postags=postags, flags=re.UNICODE | re.IGNORECASE)

    def match(self, text, offset):
        #logger.debug('Matching symbol <{0}> on text {1}, productions {2}'.format(self.name, text, self.productions))
        matches = []
        if self.lemmaregex is not None:
            # there is a token starting at position offset
            if offset in text.lemmas:
                lemma = text.lemmas[offset]
                token = text.words[offset]
                mo = self.lemmaregex.match(lemma)
                # even if lemma matches, the match must reflect the position of the original token in the text
                if mo is not None:
                    matches.append(Match(self.name, offset, offset+len(token), token))
        if self.postagregex is not None:
            # there is a token starting at position offset
            if offset in text.postags:
                lemma = text.postags[offset]
                token = text.words[offset]
                mo = self.postagregex.match(lemma)
                # even if postag matches, the match must reflect the position of the original token in the text
                if mo is not None:
                    matches.append(Match(self.name, offset, offset+len(token), token))
        for regex in self.regexes:
            mo = regex.match(text.raw[offset:])
            #logger.debug('regex {0} mo {1}'.format(regex, mo))
            if mo is not None:
                #logger.debug('Matched {0}'.format(Match(self.name, mo.start()+offset, mo.end()+offset, mo.group())))
                matches.append(Match(self.name, mo.start()+offset, mo.end()+offset, mo.group()))
        for production in self.productions:
            for match in self.match_production(production, text, offset):
                matches.append(Match.encapsulate(self.name, match))
        return matches

    def match_production(self, production, text, offset):
        #logger.debug('match production {0} on text {1}'.format(production, text))
        name, elems = production
        if name == 'list':
            return self.match_list(production, text, offset)
        elif name == 'regex':
            return self.match_regex(production, text, offset)
        elif name == 'symbol':
            return self.match_symbol(production, text, offset)
        elif name == 'optional':
            return self.match_optional(production, text, offset)
        elif name == 'or':
            return self.match_or(production, text, offset)
        else:
            raise Exception('Invalid name {0} in production'.format(name))

    def match_list(self, production, text, offset):
        name, elems = production
        #logger.debug('Matching list <{0}>'.format(elems))
        if len(elems) == 1: # list has only one element
            return self.match_production(elems[0], text, offset)
        else:
            first, rest = elems[0], elems[1:]
            if first == 'or':
                return self.match_or(elems, text, offset)
            matches = []
            for match in self.match_production(first, text, offset):
                #logger.debug('Matched {0}'.format(match))
                for next_match in self.match_production(('list', rest), text, offset+match.length):
                    #logger.debug('{0} {1}'.format(match, next_match))
                    matches.append(copy(match).link(next_match))
            return matches

    def match_regex(self, production, text, offset):
        name, elems = production
        #logger.debug('Matching regex <{0}> on text {1}'.format(elems, text))
        regex = re.compile(elems, flags=re.UNICODE | re.IGNORECASE)
        mo = regex.match(text.raw[offset:])
        if mo is not None:
            #logger.debug('Matched')
            return [Match('__regex', mo.start()+offset, mo.end()+offset, mo.group())]
        return []

    def match_symbol(self, production, text, offset):
        name, elems = production
        symbolnode = self.grammar.symbolnodes[elems]
        return symbolnode.match(text, offset)

    def match_optional(self, production, text, offset):
        name, elems = production
        #logger.debug('Matching optional <{0}>'.format(elems))
        matches = []
        for match in self.match_production(elems, text, offset):
            matches.append(Match.encapsulate('__optional', match))
        matches.append(Match('__optional', offset, offset, ''))
        return matches

    def match_or(self, production, text, offset):
        name, elems = production
        #logger.debug('Matching or <{0}>'.format(elems))
        matches = []
        for clause in elems:
            for match in self.match_production(clause, text, offset):
                matches.append(Match.encapsulate('__or', match))
        return matches
