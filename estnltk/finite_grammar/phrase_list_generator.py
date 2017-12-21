from collections import defaultdict

from .trees import Grammar


def phrase_list_generator(grammar: Grammar, max_depth: int=None):
    """
    Generates all phrases in the finite grammar tree up to the given depth.
    """
    ruledict = defaultdict(list)
    for rule in grammar.rules:
        ruledict[rule['lhs']].append(list(rule['rhs']))
    nonterminals = grammar.nonterminals
    if not max_depth:
        max_depth = grammar.max_depth

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

    return gen(grammar.start_symbols, max_depth)
