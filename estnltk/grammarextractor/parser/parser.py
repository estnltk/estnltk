# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import logging

from ..common import re
from ..exceptions import ParseException
from ..grammar.grammar import Grammar
from ..grammar.production_nodes import Name, Optional, Or, List, Regex
from . import production

logger = logging.getLogger(__name__)


def get_logger():
    return logger


def splitblocks(text):
    """Split the Grammar code into blocks."""
    blocks = []
    current_block = []
    for lineno, line in enumerate(text.splitlines()):
        if line.startswith('#') or len(line) < 4:
            continue
        if not line.startswith('    ') and len(current_block) > 0:
            blocks.append(current_block)
            current_block = []
        current_block.append((lineno+1, line))
    if len(current_block) > 0:
        blocks.append(current_block)
    return blocks


class GrammarParser(object):

    def __init__(self, text, importer=None):
        """Parse the given grammar text.

        Parameters
        ----------
        importer: parser.Importer
            The class to resolve import statements. If None, then all import statements fail.
        """
        self.current_symbol = None
        self.symbols = set()
        self.regexes = {}
        self.lemmas = {}
        self.postags = {}
        self.words = {}
        self.examples = {}
        self.exports = {}
        self.productions = {}
        self.importer = importer
        self.imported_grammars = {}
        self.example_re = re.compile('>>(?P<example>.+?)<<', re.UNICODE)
        blocks = splitblocks(text)
        for block in blocks:
            lineno, first_line = block[0]
            if 'symbol' in first_line:
                self.parse_symbol(block)
            elif 'regexes' in first_line:
                self.parse_regexes(block)
            elif 'words' in first_line:
                self.parse_words(block)
            elif first_line.startswith('import'):
                self.parse_import(block)
            elif first_line == 'lemmas':
                self.parse_lemmas(block)
            elif first_line == 'postags':
                self.parse_postags(block)
            elif first_line.startswith('export'):
                self.parse_export(block)
            elif first_line == 'productions':
                self.parse_productions(block)
            elif first_line == 'examples':
                self.parse_examples(block)
            else:
                raise ParseException('Invalid syntax on line {0}'.format(lineno))
        self.check_nonempty_symbols()
        self.check_productions()
        self.check_exports()

    def get_grammar(self):
        return Grammar(self.symbols, self.exports, self.words, self.regexes, self.lemmas, self.postags, self.productions, self.examples)

    def check_nonempty_symbols(self):
        for symbol in self.symbols:
            count = len(self.regexes.get(symbol, []))
            count += len(self.productions.get(symbol, []))
            count += len(self.words.get(symbol, []))
            count += len(self.lemmas.get(symbol, []))
            count += len(self.postags.get(symbol, []))
            if count == 0:
                raise ParseException('Symbol <{0}> has no lemma, production, regex or words section'.format(symbol))

    def check_productions(self):
        for symbol in self.symbols:
            for production in self.productions.get(symbol, []):
                self.check_production(symbol, production)

    def check_production(self, symbol_name, production):
        if isinstance(production, Name):
            if production.name not in self.symbols:
                raise ParseException('Undefined symbol <{0}> in a production of <{1}>'.format(production.name, symbol_name))
        for child in production.children:
            self.check_production(symbol_name, child)

    def check_exports(self):
        for k, v in self.exports.items():
            for var, dtype in v:
                if var not in self.symbols:
                    raise ParseException('Exported symbol <{0}> not defined!'.format(var))

    def parse_symbol(self, block):
        assert len(block) == 1
        lineno, line = block[0]
        tokens = line.split()
        if len(tokens) != 2:
            raise ParseException('Wrong number of tokens line {0}'.format(lineno))
        logger.debug('Symbol <{0}> on line {1}'.format(tokens[1], lineno))
        self.current_symbol = tokens[1]
        self.symbols.add(self.current_symbol)

    def parse_import(self, block):
        lineno, line = block[0]
        tokens = line.split()
        if self.importer is None:
            raise ParseException('Programming error: importer not defined!')
        if len(tokens) == 2:
            grammarname = tokens[1].strip()
            parser = self.imported_grammars.get(grammarname, GrammarParser(self.importer.import_grammar(grammarname), self.importer))
            if parser is None:
                raise ParseException('Grammar with name {0} not found with current importer'.format(grammarname))
            for symbol, data in parser.regexes.items():
                regexes = self.regexes.get(symbol, [])
                regexes.extend(data)
                logger.debug('Imported {0} regexes for symbol {1} from grammar {2}'.format(len(data), symbol, grammarname))
                self.regexes[symbol] = regexes
                self.symbols.add(symbol)
            for symbol, data in parser.words.items():
                words = self.words.get(symbol, [])
                words.extend(data)
                logger.debug('Imported {0} words for symbol {1} from grammar {2}'.format(len(data), symbol, grammarname))
                self.words[symbol] = words
                self.symbols.add(symbol)
            for symbol, data in parser.lemmas.items():
                lemmas = self.lemmas.get(symbol, [])
                lemmas.extend(data)
                logger.debug('Imported {0} lemmas for symbol {1} from grammar {2}'.format(len(data), symbol, grammarname))
                self.lemmas[symbol] = lemmas
                self.symbols.add(symbol)
            for symbol, data in parser.productions.items():
                productions = self.productions.get(symbol, [])
                productions.extend(data)
                logger.debug('Imported {0} productions for symbol {1} from grammar {2}'.format(len(data), symbol, grammarname))
                self.productions[symbol] = productions
                self.symbols.add(symbol)
        else:
            raise ParseException('Wrong number of tokens line {0}'.format(lineno))

    def parse_regexes(self, block):
        lineno, line = block[0]
        case_sensitive = False
        if 'case sensitive' in line:
            case_sensitive = True
            if len(line.split()) != 3:
                raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        elif len(line.split()) != 1:
            raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        regexes = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) == 0:
                raise ParseException('Zero-length regex on line {0}'.format(lineno))
            try:
                re.compile(line)
            except Exception:
                raise ParseException('Invalid regular expression on line {0}'.format(lineno))
            regexes.append((line, case_sensitive))
        symbol_regexes = self.regexes.get(self.current_symbol, [])
        symbol_regexes.extend(regexes)
        logger.debug('Parsed {0} regex(es) for symbol <{1}>'.format(len(regexes), self.current_symbol))
        self.regexes[self.current_symbol] = symbol_regexes

    def parse_words(self, block):
        lineno, line = block[0]
        case_sensitive = False
        if 'case sensitive' in line:
            case_sensitive = True
            if len(line.split()) != 3:
                raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        elif len(line.split()) != 1:
            raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        words = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) == 0:
                raise ParseException('Zero-length word on line {0}'.format(lineno))
            words.append((line, case_sensitive))
        symbol_words = self.words.get(self.current_symbol, [])
        symbol_words.extend(words)
        logger.debug('Parsed {0} word(s) for symbol <{1}>'.format(len(words), self.current_symbol))
        self.words[self.current_symbol] = symbol_words

    def parse_lemmas(self, block):
        lineno, line = block[0]
        case_sensitive = False
        if len(line.split()) != 1:
            raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        lemmas = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) == 0:
                raise ParseException('Zero-length lemma on line {0}'.format(lineno))
            lemmas.append(line.lower())
        symbol_lemmas = self.lemmas.get(self.current_symbol, [])
        symbol_lemmas.extend(lemmas)
        logger.debug('Parsed {0} lemma(s) for symbol <{1}>'.format(len(lemmas), self.current_symbol))
        self.lemmas[self.current_symbol] = symbol_lemmas

    def parse_postags(self, block):
        lineno, line = block[0]
        if len(line.split()) != 1:
            raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        postags = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) == 0:
                raise ParseException('Zero-length postag on line {0}'.format(lineno))
            postags.append(line.lower())
        symbol_postags = self.postags.get(self.current_symbol, [])
        symbol_postags.extend(postags)
        logger.debug('Parsed {0} postags(s) for symbol <{1}>'.format(len(postags), self.current_symbol))
        self.postags[self.current_symbol] = symbol_postags

    def parse_examples(self, block):
        lineno, line = block[0]
        if len(line.split()) != 1:
            raise ParseException('Wrong number of tokens on line {0}'.format(lineno))
        examples = []
        total = 0
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) == 0:
                continue
            matches = []
            filtered_text = ''
            prev_start = 0
            offset = 0
            for mo in self.example_re.finditer(line):
                start, end = mo.start('example'), mo.end('example')
                filtered_text += line[prev_start:mo.start()]
                filtered_text += line[start:end]
                prev_start = mo.end()
                offset += 2
                start -= offset
                end -= offset
                offset += 2
                matches.append((start, end))
            filtered_text += line[prev_start:]
            example = (filtered_text, matches)
            total += len(matches)
            examples.append(example)
        symbol_examples = self.examples.get(self.current_symbol, [])
        symbol_examples.extend(examples)
        self.examples[self.current_symbol] = symbol_examples
        logger.debug('Parsed {0} examples or symbol <{1}>'.format(total, self.current_symbol))

    def parse_export(self, block):
        lineno, line = block[0]
        tokens = line.split()
        if len(tokens) != 2:
            raise ParseException('Wrong number of tokens line {0}'.format(lineno))
        name = tokens[1]
        logger.debug('Parsign details for export <{0}> on line {1}'.format(name, lineno))
        variables = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            tokens = line.split()
            if len(tokens) != 2:
                raise ParseException('Wrong number of tokens line {0}'.format(lineno))
            varname, dtype = tokens
            if dtype not in ['integer', 'real', 'string']:
                raise ParseException('Illegal data type <{0}> on line {1}. Allowed are <integer>, <real> and <string>'.format(dtype, lineno))
            variables.append((varname, dtype))
        self.exports[name] = variables

    def parse_productions(self, block):
        productions = []
        for lineno, line in block[1:]:
            line = line[4:].strip()
            if len(line) > 0:
                productions.append(production.parse(line, lineno))
        symbol_productions = self.productions.get(self.current_symbol, [])
        symbol_productions.extend(productions)
        logger.debug('Parsed {0} productions for symbol <{1}>'.format(len(productions), self.current_symbol))
        self.productions[self.current_symbol] = symbol_productions



if __name__ == '__main__':
    # start point whenever a debugger is necessary
    source = """symbol number
regexes
    \d+

symbol any
productions
    number | number | number
    (number | number?)? number

export any
"""
    parser = GrammarParser(source)
    grammar = parser.get_grammar()
    #grammar.match('25 on number')

