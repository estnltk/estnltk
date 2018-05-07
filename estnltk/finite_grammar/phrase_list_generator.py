from typing import Union
from collections import defaultdict

from .grammar import Grammar


def phrase_list_generator(grammar: Grammar, depth_limit: Union[int, float]=None):
    """
    Generates all phrases in the finite grammar tree up to the depth_limit.
    """
    ruledict = defaultdict(list)
    for rule in grammar.rules:
        ruledict[rule.lhs].append(list(rule.rhs))
    nonterminals = grammar.nonterminals
    if depth_limit is None:
        depth_limit = grammar.depth_limit

    def gen(symbols, depth):
        nonterminal = None
        for i, s in enumerate(symbols):
            if s in nonterminals:
                nonterminal = s
                break
        if nonterminal is None:
            yield symbols
            return
        if depth <= 0:
            return
        for replacement in ruledict[nonterminal]:
            new_symbols = symbols[:i] + replacement + symbols[i+1:]
            yield from gen(new_symbols, depth-1)

    return gen(list(grammar.start_symbols), depth_limit)
