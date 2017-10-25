from collections import defaultdict

from .trees import Grammar


def phrase_list_generator(grammar:Grammar):
    '''
    :param grammar: Grammar
    :return: iterator of phrases
    Generates all phrases of the finite grammar.
    '''
    ruledict = defaultdict(list)
    for rule in grammar.rules:
        ruledict[rule['lhs']].append( list(rule['rhs']))
    nonterminals = grammar.nonterminals

    def gen(symbols):
        nonterminal = None
        for i, s in enumerate(symbols):
            if s in nonterminals:
                nonterminal = s
                break
        if nonterminal is None:
            yield symbols
            return
        for replacement in ruledict[nonterminal]:
            new_symbols = symbols[:i] + replacement + symbols[i+1:]
            yield from gen(new_symbols)

    return gen([grammar.start_symbol])
