from typing import Sequence, Union, Iterable
from collections import defaultdict
import regex as re
import networkx as nx

_search_parenthesis = re.compile(r'\(|\)').search


def contains_parenthesis(s: str) -> bool:
    return _search_parenthesis(s) is not None


def match_SEQ_pattern(s: str) -> Union[str, None]:
    m = re.compile(r'SEQ\((.*)\)$').match(s)
    if m is not None:
        return m.group(1)


def match_mseq_pattern(s: str) -> Union[str, None]:
    m = re.compile(r'MSEQ\((.*)\)$').match(s)
    if m is not None:
        return m.group(1)


class Grammar:
    _internal_attributes = frozenset({'name', 'text', 'start', 'end', '_terminals_', '_support_', '_priority_', '_group_'})

    def __init__(self,
                 start_symbols: Sequence = (),
                 rules: list=None,
                 depth_limit: Union[int, float] = float('inf'),
                 width_limit: Union[int, float] = float('inf'),
                 legal_attributes: Iterable[str] = None):
        if legal_attributes is None:
            self.legal_attributes = frozenset()
        else:
            legal_attributes = frozenset(legal_attributes)
            assert not legal_attributes & self._internal_attributes, \
                'legal attributes contain internal attributes: ' + str(legal_attributes & self._internal_attributes)
            self.legal_attributes = legal_attributes
        if rules is None:
            self._rules = []
        else:
            self._rules = rules
        self.start_symbols = tuple(start_symbols)
        self.depth_limit = depth_limit
        self.width_limit = width_limit

        self._setup = False
        self._setup_grammar()

    @property
    def rules(self):
        self._setup_grammar()
        return self._rules

    @property
    def terminals(self):
        self._setup_grammar()
        return self._terminals

    @property
    def nonterminals(self):
        self._setup_grammar()
        return self._nonterminals

    @property
    def rule_map(self):
        self._setup_grammar()
        return self._rule_map

    @property
    def hidden_rule_map(self):
        self._setup_grammar()
        return self._hidden_rule_map

    @property
    def mseq_rule_map(self):
        self._setup_grammar()
        return self._mseq_rule_map

    def has_finite_max_depth(self):
        """
        Returns True, if the maximal possible height of the parse tree is finite even on an infinite text.

        Returns False if the set of rules is cyclic, for example
        cyclic: A -> B, B -> C, C -> A D
        cyclic: A -> SEQ(A)
        not cyclic: A -> B C
        not cyclic: A -> SEQ(B)
        """
        rule_graph = nx.DiGraph()
        for rule in self._rules:
            for r in rule.rhs:
                rule_graph.add_edge(rule.lhs, r)
        for ps, s in self._plus_symbols:
            rule_graph.add_edge(ps, s)
        return nx.is_directed_acyclic_graph(rule_graph)

    def _terminals_and_nonterminals(self):
        nonterminals = {r['lhs'] for r in self._rules}
        terminals = set()
        for r in {r for rule in self._rules for r in rule.rhs}:
            m = match_SEQ_pattern(r)
            if m is not None:
                nonterminals.add(r)
                terminals.add(m)
            else:
                terminals.add(r)
        self._nonterminals = frozenset(nonterminals)
        self._terminals = frozenset(terminals - nonterminals)

    def _rule_maps(self):
        self._rule_map = defaultdict(list)
        self._plus_symbols = set()
        self._mseq_symbols = set()
        for rule in self._rules:
            for pos, rhs in enumerate(rule.rhs):
                self._rule_map[rhs].append((rule, pos))
                seq = match_SEQ_pattern(rhs)
                mseq = match_mseq_pattern(rhs)
                if seq is not None:
                    self._plus_symbols.add((rhs, seq))
                elif mseq is not None:
                    self._mseq_symbols.add((rhs, mseq))

        self._hidden_rule_map = {}
        for ps, s in self._plus_symbols:
            self._hidden_rule_map[ps] = [(Rule(ps, (ps, ps)), 0),
                                         (Rule(ps, (ps, ps)), 1)]
            self._hidden_rule_map[s] = [(Rule(ps, s), 0)]

        self._mseq_rule_map = {}
        for ps, s in self._mseq_symbols:
            self._mseq_rule_map[ps] = [(Rule(ps, (ps, ps)), 0),
                                       (Rule(ps, (ps, ps)), 1)]
            self._mseq_rule_map[s] = [(Rule(ps, s), 0)]

    def _setup_grammar(self):
        if self._setup:
            return
        assert len(self._rules) == len({(r.lhs, r.rhs) for r in self._rules}), 'repetitive rules'
        self._rule_maps()
        assert (self.depth_limit < float('inf') or
                self.has_finite_max_depth()), 'infinite grammar without depth limit'
        self._terminals_and_nonterminals()
        self._setup = True

    def add(self, rule):
        self._rules.append(rule)
        self._setup = False

    def add_rule(self, *args, **kwargs):
        self._rules.append(Rule(*args, **kwargs))
        self._setup = False

    def __getitem__(self, key):
        if key in self.nonterminals:
            return [i for i in self.rules if i.lhs == key]
        else:
            return self.rules[key]

    def __str__(self):
        self._setup_grammar()
        rules = '\n\t'.join([str(i) for i in self.rules])
        terminals = ', '.join(sorted(self.terminals))
        nonterminals = ', '.join(sorted(self.nonterminals))
        return '''
Grammar:
\tstart: {start}
\tterminals: {terminals}
\tnonterminals: {nonterminals}
\tlegal attributes: {self.legal_attributes}
\tdepth_limit: {self.depth_limit}
\twidth_limit: {self.width_limit}
Rules:
\t{rules}
'''.format(start=', '.join(self.start_symbols), rules=rules, terminals=terminals,
           nonterminals=nonterminals, self=self)

    def __repr__(self):
        return str(self)


class Rule:
    @staticmethod
    def default_validator(x):
        return True

    @staticmethod
    def default_decorator(x):
        return {}

    @staticmethod
    def default_scoring(x):
        return 0

    def __init__(self,
                 lhs: str,
                 rhs: Union[str, Sequence[str]],
                 priority: int=0,
                 group=None,
                 decorator=None,
                 validator=None,
                 scoring=None
                 ):
        assert not contains_parenthesis(lhs) or match_SEQ_pattern(lhs) or match_mseq_pattern(lhs),\
            'parenthesis not allowed: ' + lhs
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        for r in rhs:
            assert isinstance(r, str), 'rhs must be a str or sequence of str'
            if contains_parenthesis(r):
                assert match_SEQ_pattern(r) is not None or match_mseq_pattern(r) is not None,\
                    'parenthesis only allowed with SEQ or REP: ' + str(rhs)
        self.rhs = tuple(rhs)

        self.priority = priority
        self.group = group
        if group is None:
            self.group = hash((self.lhs, self.rhs))

        if decorator is None:
            self.decorator = self.default_decorator
        else:
            self.decorator = decorator

        if validator is None:
            self.validator = self.default_validator
        else:
            self.validator = validator

        if scoring is None:
            self.scoring = self.default_scoring
        else:
            self.scoring = scoring

    def __lt__(self, other):
        return self.priority < other.priority

    def __getitem__(self, key):
        if key == 'lhs':
            return self.lhs
        elif key == 'rhs':
            return self.rhs
        else:
            raise AssertionError

    def __str__(self):
        return ('{self.lhs} -> {rhs}\t: {self.priority}, val: {self.validator.__name__},' +
                ' dec: {self.decorator.__name__}, scoring: {self.scoring.__name__}'
                ).format(self=self, rhs=' '.join(self.rhs))

    def __repr__(self):
        return str(self)
