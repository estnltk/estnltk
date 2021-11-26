from estnltk.taggers.system.grammar_taggers.finite_grammar import Grammar
from estnltk.taggers.system.grammar_taggers.finite_grammar import Rule
from estnltk.taggers.system.grammar_taggers.finite_grammar import phrase_list_generator
from estnltk.taggers.system.grammar_taggers.finite_grammar import ngram_fingerprint


def test_phrase_list_generator():
    grammar = Grammar(start_symbols=['S'],
                      rules=None,
                      depth_limit=float('inf'),
                      width_limit=float('inf'),
                      legal_attributes=None
                      )
    grammar.add(Rule('S', 'A'))
    grammar.add(Rule('S', 'B'))
    grammar.add(Rule('S', 'SEQ(B)'))
    grammar.add(Rule('B', 'SEQ(C)'))
    grammar.add(Rule('A', 'B F'))
    grammar.add(Rule('B', 'G'))
    grammar.add(Rule('S', 'K L M N'))
    assert [('C', 'F'),
            ('C', 'C', 'F'),
            ('G', 'F'),
            ('C',),
            ('C', 'C'),
            ('G',),
            ('C', 'C', 'C'),
            ('C', 'G'),
            ('C', 'C', 'C', 'C'),
            ('C', 'C', 'G'),
            ('G', 'C'),
            ('G', 'C', 'C'),
            ('G', 'G'),
            ('K', 'L', 'M', 'N')] == list(phrase_list_generator(grammar, depth_limit=None, width_limit=None, expand_seq=2))


def test_grammar_phrase_ngrams():
    grammar = Grammar(start_symbols=['S'],
                      rules=None,
                      depth_limit=float('inf'),
                      width_limit=float('inf'),
                      legal_attributes=None
                      )
    grammar.add(Rule('S', 'A'))
    grammar.add(Rule('S', 'B'))
    grammar.add(Rule('S', 'SEQ(B)'))
    grammar.add(Rule('B', 'SEQ(C)'))
    grammar.add(Rule('A', 'B F'))
    grammar.add(Rule('B', 'G'))
    grammar.add(Rule('S', 'K L M N'))

    assert [[('C',)],
            [('C', 'C')],
            [('C', 'F')],
            [('C', 'G')],
            [('G',)],
            [('G', 'C')],
            [('G', 'F')],
            [('G', 'G')],
            [('K', 'L'), ('L', 'M'), ('M', 'N')]] == ngram_fingerprint(2, grammar, depth_limit=None, width_limit=None, expand_seq=2)

    grammar = Grammar(start_symbols=['S'],
                      rules=None,
                      depth_limit=float('inf'),
                      width_limit=float('inf'),
                      legal_attributes=None
                      )
    grammar.add(Rule('S', 'A A'))
    grammar.add(Rule('A', 'B C'))
    grammar.add(Rule('A', 'B F'))
    grammar.add(Rule('S', 'I SEQ(G)'))
    grammar.add(Rule('S', 'F G H'))
    grammar.add(Rule('S', 'K'))
    result = ngram_fingerprint(n=2,
                               grammar=grammar,
                               depth_limit=None,
                               width_limit=4,
                               expand_seq=None
                               )
    assert result == [[('I', 'G')],
                      [('K',)],
                      [('B', 'C'), ('C', 'B')],
                      [('B', 'F'), ('F', 'B')],
                      [('F', 'G'), ('G', 'H')]]
