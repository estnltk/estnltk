from typing import Union
from collections import defaultdict

from estnltk.taggers.system.grammar_taggers.finite_grammar import Grammar
from estnltk.taggers.system.grammar_taggers.finite_grammar.grammar import match_SEQ_pattern


def phrase_list_generator(grammar: Grammar,
                          depth_limit: Union[int, float]=None,
                          width_limit: Union[int, float]=None,
                          expand_seq: int=None):
    """
    Generates all phrases in the finite grammar tree up to the depth_limit.
    """
    nonterminals = grammar.nonterminals
    if depth_limit is None:
        depth_limit = grammar.depth_limit
    if width_limit is None:
        width_limit = grammar.width_limit
    if expand_seq is None:
        expand_seq = width_limit
    assert width_limit == float('inf') or isinstance(width_limit, int) and width_limit > 0, width_limit
    assert expand_seq <= width_limit,\
        'expand_seq > width_limit: {} > {}'.format(expand_seq, width_limit)

    ruledict = defaultdict(list)
    for rule in grammar.rules:
        ruledict[rule.lhs].append(rule.rhs)

        for r in rule.rhs:
            if r not in ruledict and match_SEQ_pattern(r):
                assert isinstance(expand_seq, int) and expand_seq > 0, expand_seq
                m = match_SEQ_pattern(r)
                ruledict[r] = [(m,)*i for i in range(1, expand_seq+1)]
    yielded_phrases = set()

    def gen(phrase, depth):
        if len(phrase) > width_limit:
            return
        nonterminal = None
        for i, s in enumerate(phrase):
            if s in nonterminals:
                nonterminal = s
                break
        if nonterminal is None:
            if phrase not in yielded_phrases:
                yielded_phrases.add(phrase)
                yield phrase
            return
        if depth <= 0:
            return
        for replacement in ruledict[nonterminal]:
            new_symbols = phrase[:i] + replacement + phrase[i + 1:]
            yield from gen(new_symbols, depth-1)

    return gen(grammar.start_symbols, depth_limit)


def ngram_fingerprint(n: int, grammar: Grammar, depth_limit=None, width_limit=None, expand_seq=None):
    ngrams_set = set()
    for phrase in phrase_list_generator(grammar=grammar,
                                        depth_limit=depth_limit,
                                        width_limit=width_limit,
                                        expand_seq=expand_seq):
        ngrams = set()
        m = min(n, len(phrase))
        for i in range(len(phrase) - m + 1):
            ngrams.add(phrase[i: i + m])
        to_remove = []
        add = True
        for ng in ngrams_set:
            if ng <= ngrams:
                add = False
                break
            if ngrams <= ng:
                to_remove.append(ng)
        if add:
            ngrams_set.add(frozenset(ngrams))
        ngrams_set.difference_update(to_remove)
    # `sorted` in the following is only needed for determined output
    return sorted(map(sorted, ngrams_set), key=lambda x: (len(x), tuple(sorted(x))))
