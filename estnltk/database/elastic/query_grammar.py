import collections
import uuid
from estnltk.text import Text

try:
    import sympy
except ImportError as e:
    print('Query grammar is a helper module. It has "sympy" as an additional dependancy.')
    raise e

__all__ = ['Grammar', 'Word', 'And', 'Or']

# local constants
STRING = 0
ITERABLE = 1


class Node:
    def __or__(self, other):
        assert isinstance(other, Node), "Both arguments must be Node instances"
        return Or(self, other)

    def __and__(self, other):
        assert isinstance(other, Node), "Both arguments must be Node instances"
        return And(self, other)


def _is_word(node):
    return isinstance(node, Word)


def _is_operation(node):
    return isinstance(node, Operation)


class Grammar:
    def __init__(self, root):
        self.root = root


    def query(self):
        # list of all words in grammar
        words = []

        # list of all operations
        operations = []

        nodes = [self.root]

        while nodes:
            node = nodes.pop()
            if _is_word(node):
                words.append(node)
            elif _is_operation(node):
                nodes.extend(node.nodes)
                operations.append(node)
        words_to_symbols = dict(zip(words, sympy.symbols([word.id for word in words])))
        symbols_to_words = dict((v, k) for (k, v) in words_to_symbols.items())

        expression = sympy.to_dnf(node_to_symbol(words_to_symbols, self.root), simplify=True)


        if isinstance(expression, sympy.And):
            # We have no outer Or - the query is a single And
            main_query = {
                'query': {
                    'bool': {
                        'must': [word_to_query(word) for word in (symbols_to_words[i] for i in expression.args)]
                    }
                }
            }
        elif isinstance(expression, sympy.Or):
            query = []
            for arg in (expression.args):
                if isinstance(arg, sympy.And):
                    query.append(
                        {
                            'bool': {
                                'must': [word_to_query(word) for word in (symbols_to_words[i] for i in arg.args)]
                            }
                        }
                    )
                elif isinstance(arg, sympy.Symbol):
                    query.append(word_to_query(symbols_to_words[arg]))

            main_query = {
                'query': {
                    'bool': {
                        'should': query,
                        'minimum_number_should_match': 1
                    }
                }
            }
        elif isinstance(expression, sympy.Symbol):
            main_query = {
                'query': word_to_query(symbols_to_words[expression])
            }

        else:
            raise AssertionError("Don't know what I got or why.")

        main_query['fields'] = ['estnltk_text_object']
        return main_query

    def annotate(self, estnltk_text, label):
        # list of all words in grammar
        words = []

        # list of all operations
        operations = []

        nodes = [self.root]

        while nodes:
            node = nodes.pop()
            if _is_word(node):
                words.append(node)
            elif _is_operation(node):
                nodes.extend(node.nodes)
                operations.append(node)
        words_to_symbols = dict(zip(words, sympy.symbols([word.id for word in words])))
        symbols_to_words = dict((v, k) for (k, v) in words_to_symbols.items())
        expression = sympy.to_dnf(node_to_symbol(words_to_symbols, self.root), simplify=True)



        def match(word_object, estnltk_word):
            assert isinstance(word_object, Word)
            assert isinstance(estnltk_word, Text)


            for param, value in word_object.params.items():


                if set(value).issubset(set([i[param] for i in estnltk_word.analysis[0]])):
                    continue
                else:
                    return False
            return True


        words_to_matches = collections.defaultdict(set)
        e_words = estnltk_text.split_by_words()

        spans = [{'start':a, 'end':b} for a,b in  estnltk_text.word_spans]

        for _ind,e_word in enumerate(e_words):
            for word in words:
                if match(word, e_word):
                    words_to_matches[word].add(_ind)

        if words_to_matches:
            layer = [spans[i] for i in set.union( *words_to_matches.values() )]
        else:
            layer = []

        estnltk_text[label] = layer


def node_to_symbol(words_to_symbols, node):
    if _is_word(node):
        return words_to_symbols[node]
    elif _is_operation(node):
        if isinstance(node, Or):
            return sympy.Or(*[node_to_symbol(words_to_symbols, i) for i in node.nodes])
        elif isinstance(node, And):
            return sympy.And(*[node_to_symbol(words_to_symbols, i) for i in node.nodes])


def word_to_query(word):
    terms = []
    path = 'words.analysis'
    for k, v in word.params.items():
        terms.append(
            {'terms': {'.'.join((path, k)): v}}
        )
    return (
        {
            'nested': {
                'path': path,
                'query': {
                    'bool': {
                        'must': terms
                    }
                }
            }
        }
    )


class Operation(Node):
    def __init__(self, *nodes):
        self.nodes = nodes

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


Or = type('Or', (Operation,), {})
And = type('And', (Operation,), {})


class Word(Node):
    def __init__(self, lemma=None, text=None, partofspeech=None, ending=None, clitic=None, form=None, root=None, ):
        self.id = uuid.uuid4().hex

        self.params = {}
        for k, v in {'lemma': lemma, 'partofspeech': partofspeech, 'ending': ending, 'clitic':clitic, 'form':form, 'root':root}.items():
            if v is not None:
                self.params[k] = v

        for param, value in self.params.items():
            if value is None:
                continue

            # Wrap all strings into lists for consistency
            if self._test_string_or_other_iterable(value) is STRING:
                self.params[param] = [value]

    def __str__(self):
        return 'Word(**{}, id={})'.format(str(self.params), self.id[:6])

    def __repr__(self):
        return str(self)

    @staticmethod
    def _test_string_or_other_iterable(value):
        if isinstance(value, str):
            return STRING
        elif isinstance(value, collections.Iterable):
            return ITERABLE
        else:
            raise AssertionError("Don't know what you gave me, can't handle it.")
