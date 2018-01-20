from typing import Sequence


class Grammar:

    _internal_attributes = frozenset({'name', 'text', 'start', 'end', '_terminals_', '_support_', '_priority_', '_group_'})

    def __init__(self, *, start_symbols: Sequence, rules: list=None, max_depth: int=float('inf'), legal_attributes=None):
        if legal_attributes is None:
            self.legal_attributes = frozenset()
        else:
            legal_attributes = frozenset(legal_attributes)
            assert not legal_attributes & self._internal_attributes, 'legal attributes contain internal attributes'
            self.legal_attributes = legal_attributes
        if rules is None:
            self._rules = []
        else:
            self._rules = rules
        self.start_symbols = start_symbols
        self.max_depth = max_depth
        self._checked = True

    @property
    def rules(self):
        if not self._checked:
            self._check_rules()
            self._terminals_and_nonterminals()
            self._checked = True
        return self._rules

    def _terminals_and_nonterminals(self):
        self.nonterminals = frozenset(r['lhs'] for r in self._rules)
        terminals = set()
        for i in (set(i.rhs) for i in self._rules):
            terminals.update(i)
        self.terminals = frozenset(terminals - self.nonterminals)

    def _check_rules(self):
        assert len(self._rules) == len({(r.lhs, r.rhs) for r in self._rules}), 'repetitive rules'

    def add(self, rule):
        self._rules.append(rule)
        self._checked = False

    def __getitem__(self, key):
        if key in self.nonterminals:
            return [i for i in self.rules if i.lhs == key]
        else:
            return self.rules[key]

    def __str__(self):
        rules = '\n\t'.join([str(i) for i in self.rules])
        terminals = ', '.join(sorted(self.terminals))
        nonterminals = ', '.join(sorted(self.nonterminals))
        return '''
Grammar:
\tstart: {start}
\tterminals: {terminals}
\tnonterminals: {nonterminals}
\tlegal attributes: {self.legal_attributes}
\tmax_depth: {max_depth}
Rules:
\t{rules}
'''.format(start=', '.join(self.start_symbols), rules=rules, terminals=terminals,
           nonterminals=nonterminals, max_depth=self.max_depth, self=self)

    def __repr__(self):
        return str(self)


class Rule:
    @staticmethod
    def default_validator(x):
        return True

    @staticmethod
    def default_decorator(x):
        return {}

    def __init__(self, lhs, rhs, priority: int=0, group=None, decorator=None, validator=None):
        self.lhs = lhs
        if isinstance(rhs, str):
            rhs = rhs.split()
        self.rhs = tuple(rhs)

        self.priority = priority
        self.group = group
        if group is None:
            self.group = hash((self.lhs, self.rhs))

        if decorator:
            self.decorator = decorator
        else:
            self.decorator = self.default_decorator

        if validator:
            self.validator = validator
        else:
            self.validator = self.default_validator

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
        return '{self.lhs} -> {rhs}\t: {self.priority}, val: {self.validator.__name__}, dec: {self.decorator.__name__}'.format(self=self, rhs=' '.join(self.rhs))

    def __repr__(self):
        return str(self)
