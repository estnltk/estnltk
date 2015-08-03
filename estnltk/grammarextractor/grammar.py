# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from .symbol import SymbolNode
from .common import StringIO

class Grammar(object):

    def __init__(self, symbols, exports, words, regexes, lemmas, postags, productions, examples):
        self.exports = exports
        # set up symbolnodes
        self.symbolnodes = {}
        for symbol in symbols:
            sym_words = words.get(symbol, [])
            sym_regexes = regexes.get(symbol, [])
            sym_lemmas = lemmas.get(symbol, [])
            sym_postags = postags.get(symbol, [])
            sym_productions = productions.get(symbol, [])
            self.symbolnodes[symbol] = SymbolNode(self, symbol, sym_words, sym_regexes, sym_lemmas, sym_postags, sym_productions)
        self.examples = examples
        self.estimate_canonical_form_precisions(examples)

    def estimate_canonical_form_precisions(self, examples):
        """Use examples in grammar to estimate the precisions for canonical form of the symbol matches."""
        true_positives = {}
        false_positives = {}
        canonics = set()
        # evaluate examples and compute true and false positives for each canonical form (for each symbol)
        for key, exs in examples.items():
            node = self.symbolnodes[key]
            for text, true_matches in exs:
                #logger.info(text)
                #logger.info(repr(true_matches))
                matched = []
                all_matches = self.match_all(text, [key])
                for match in all_matches:
                    #logger.info(match.grouptree())
                    canonic = match.canonical_form()
                    canonics.add(canonic)
                    if (match.start, match.end) in true_matches:
                        true_positives[canonic] = true_positives.get(canonic, 0) + 1
                        matched.append((match.start, match.end))
                    else:
                        false_positives[canonic] = false_positives.get(canonic, 0) + 1
                # report matches, that were not covered
                for true_match in true_matches:
                    if true_match not in matched:
                        err = 'Symbol <{0}> example <{1}> not covered in text <{2}>\n'.format(key, text[true_match[0]:true_match[1]], text)
                        stream = StringIO()
                        stream.write(err)
                        stream.write('There are {0} candidate matches:'.format(len(all_matches)))
                        for match in all_matches:
                            pprint(match.grouptree(), stream=stream)
                            stream.write('\n')
                        logger.warning(stream.getvalue())
                # check false positive matches
                if len(true_matches) == 0 and len(all_matches) > 0:
                    err = 'False positive matches for symbol <{0}> on text <{1}>\n:'.format(key, text)
                    stream = StringIO()
                    stream.write(err)
                    for match in all_matches:
                        pprint(match.grouptree(), stream=stream)
                        stream.write('\n')
                    logger.debug(stream.getvalue())
        # compute precision estimates for canonical forms
        precisions = {}
        for canonic in canonics:
            tp, fp = true_positives.get(canonic, 0), false_positives.get(canonic, 0)
            precision = float(tp) / (tp + fp)
            precisions[canonic] = precision
            logger.info('Precision {0:.2f} for canonical form <{1}>'.format(precision, canonic))
        self.canonic_precisions = precisions

    def matched_examples(self):
        match_stats = []
        for key, exs in self.examples.items():
            node = self.symbolnodes[key]
            key_text_spans = []
            tp, fp, fn = 0, 0, 0
            for text, true_matches in exs:
                matched = []
                matches = self.match(text, [key])
                spans = []
                for match in matches:
                    if (match.start, match.end) in true_matches:
                        matched.append((match.start, match.end))
                        spans.append((match.start, match.end, 'tp'))
                        tp += 1
                    else:
                        spans.append((match.start, match.end, 'fp'))
                        fp += 1
                for match in true_matches:
                    if match not in matched:
                        spans.append((match[0], match[1], 'fn'))
                        fn += 1
                text_spans = []
                lastend = 0
                for start, end, mtype in sorted(spans):
                    text_spans.append((text[lastend:start], 'normal'))
                    text_spans.append((text[start:end], mtype))
                    lastend = end
                text_spans.append((text[lastend:], 'normal'))
                key_text_spans.append(text_spans)
            precision = '{0:.2f}%'.format(100.0*tp / (fp + tp))
            recall = '{0:.2f}%'.format(100.0*tp / (fn + tp))
            match_stats.append((key, key_text_spans, tp, fp, fn, precision, recall))
        return match_stats

    def match_all(self, text, symbols=None):
        """Match the grammar on given text and give all matches.

        Parameters
        ----------
        text: str
            The text the grammar will be matched on.
        symbols: list of str (optional)
            Name of symbols to be matched. If None, then use symbols defined in the exports.
        """
        if symbols is None:
            symbols = self.exports.keys()
        text = Text(text)
        # we try to match symbols starting at each token
        matches = []
        for symbol in symbols:
            node = self.symbolnodes[symbol]
            for start, end in text.spans:
                matches.extend(node.match(text, start))
        return matches

    def match(self, text, symbols=None):
        """Match the grammar on given text and give highest scoring set of
        non-overlapping matches.

        Parameters
        ----------
        text: str
            The text the grammar will be matched on.
        symbols: list of str (optional)
            Name of symbols to be matched. If None, then use symbols defined in the exports.
        """
        matches = self.match_all(text, symbols)
        if len(matches) == 0:
            return matches
        matches.sort(key=lambda match: (match.start, match.end))
        scores = [self.match_score(match) for match in matches]
        N = len(matches)
        prev = [-1] * N
        for i in range(1, N):
            bestscore = -1
            bestprev = -1
            j = i
            numbefore = 0
            while j >= 0:
                # if matches do not overlap
                if matches[j].is_before(matches[i]):
                    l = scores[j] + self.match_score(matches[i])
                    if l >= bestscore:
                        bestscore = l
                        bestprev = j
                    numbefore += 1
                    if i-j > 200 and numbefore > 10: # prune if matcher more than 100 characters away and at least 10 matches between
                        break
                else: # in case of overlapping matches
                    l = scores[j] - self.match_score(matches[j]) + self.match_score(matches[i])
                    if l >= bestscore:
                        bestscore = l
                        bestprev = prev[j]
                j = j - 1
            scores[i] = bestscore
            prev[i] = bestprev
        # first find the matching with highest combined score
        bestscore = max(scores)
        bestidx = len(scores) - scores[-1::-1].index(bestscore) -1
        # then backtrack the non-conflicting matches that should be kept
        keepidxs = [bestidx]
        bestidx = prev[bestidx]
        while bestidx != -1:
            keepidxs.append(bestidx)
            bestidx = prev[bestidx]
        # filter the matches
        return [matches[idx] for idx in reversed(keepidxs)]

    def match_score(self, match):
        canon = match.canonical_form()
        s1 = self.canonic_precisions.get(canon, 1.0) + 1.0
        s2 = match.length
        return s1*s2
