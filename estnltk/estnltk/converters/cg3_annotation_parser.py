"""
Parser for parsing VISL CG3 format analysis line.
Based on EstNLTK 1.4 estnltk.syntax.parsers and estnltk.syntax.vislcg3_syntax.py.
"""

from collections import defaultdict
from typing import Tuple, Optional
import re
import sys


def get_reversed_mapping(cats) -> dict:
    """
    Maps cats as 'form_value': 'category'.
    """
    reversed_cats_mapping = defaultdict(lambda: 'unknown_attribute')
    for cat, forms in cats.items():
        for form in forms:
            if form in reversed_cats_mapping:
                raise Exception("(!)Can't map form: '%s' and category: '%s'" % (form, cat))
            reversed_cats_mapping[form] = cat
    return reversed_cats_mapping


def get_cats(cats):
    """
    Checks that attribute is valid.
    """
    wrong_cats = ['lemma', 'ending', 'partofspeech', 'deprel', 'head']
    for key in cats.keys():
        if key in wrong_cats:
            raise Exception('(!)Wrong attribute for feature category: "%s"' % (key))
    return cats


class CG3AnnotationParser:
    """
    Example:
        line = '	"mari" Lle S com sg all cap @ADVL #1->4'
        parser = CG3AnnotationParser()
        processed_line = parser.parse(line)

    Output:
        {'capitalized': ['cap'],
         'case': ['all'],
         'deprel': ['@ADVL'],
         'ending': 'le',
         'head': '4',
         'id': '1',
         'lemma': 'mari',
         'number': ['sg'],
         'partofspeech': 'S',
         'subtype': ['com']}
    """
    pat_analysis_line = re.compile(r'^\s+"(?P<lemma>.+)" (?P<ending>L\w+)*(?P<cats>[^@#]*)(?P<syntax>[@#]*.*)$')
    pat_pos_form = re.compile(r'^ *[A-Z]\s*(?P<form>[^#@]*).*$')
    pat_form_pos = re.compile(r'^ *(?P<form>[a-z]+) (?P<postag>[A-Z]).*$')

    cats = {'case': {'nom', 'gen', 'part', 'ill', 'in', 'el', 'all', 'ad', 'abl',
                     'tr', 'term', 'es', 'abes', 'kom', 'adit'},
            'number': {'sg', 'pl'},
            'voice': {'imps', 'ps'},
            'tense': {'pres', 'past', 'impf'},
            'mood': {'indic', 'cond', 'imper', 'quot'},
            'person': {'ps1', 'ps2', 'ps3'},
            'polarity': {'af', 'neg'},
            'inf_form': {'sup', 'inf', 'ger', 'partic'},
            'subtype': {'pos', 'det', 'refl', 'dem', 'inter_rel', 'pers', 'rel', 'rec', 'indef', 'comp', 'super',
                        'main', 'mod', 'aux', 'prop', 'com', 'card', 'ord', 'pre', 'post', 'crd', 'sub', 'adjectival',
                        'adverbial', 'nominal', 'verbal', 'Col', 'Com', 'Cpr', 'Cqu', 'Csq', 'Dsd', 'Dsh', 'Ell',
                        'Els', 'Exc', 'Fst', 'Int', 'Opr', 'Oqu', 'Osq', 'Quo', 'Scl', 'Sla','Sml'},
            'number_format': {'l', 'roman', 'digit'},
            'capitalized': {'cap'},
            'finiteness': {'<FinV>', '<Inf>', '<InfP>'},
            'subcat': {'<Abl>', '<Ad>', '<All>', '<El>', '<Es>', '<Ill>', '<In>', '<Kom>', '<Part>',
                       '<all>', '<el>', '<gen>', '<ja>', '<kom>', '<mata>', '<mine>', '<nom>', '<nu>',
                       '<nud>', '<part>', '<tav>', '<tu>', '<tud>', '<v>', '<Ter>', '<Tr>', '<Intr>',
                       '<NGP-P>', '<NGP>', '<Part-P>'},
            'clause_boundary': {'CLB'}}

    reversed_cats = get_cats(get_reversed_mapping(cats))

    def __init__(self, supress_exceptions=False):
        self.supress_exceptions = supress_exceptions

    @staticmethod
    def get_forms(cats, postag, line):
        """
        Creates morphological features from morphological categories.
        """
        assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
        assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        forms = []
        # Features matching
        m1 = CG3AnnotationParser.pat_pos_form.match(cats)
        m2 = CG3AnnotationParser.pat_form_pos.match(cats)
        if m1:
            forms = (m1.group('form')).split()
        elif m2:
            forms = (m2.group('form')).split()
            postag = m2.group('postag')
        else:
            print('(!) Unexpected format of analysis line: ' + line, file=sys.stderr)
        return forms, postag

    @staticmethod
    def get_analysed_forms(forms):
        """
        Finds attribute to each feature element.
        """
        assert isinstance(forms, list), '(!)Unexpected type for "forms" argument! Expected a list.'
        analysed_forms = {}
        for form in forms:
            if CG3AnnotationParser.reversed_cats[form] in analysed_forms:
                analysed_forms[CG3AnnotationParser.reversed_cats[form]].append(form)
            else:
                analysed_forms[CG3AnnotationParser.reversed_cats[form]] = [form]
        return analysed_forms

    @staticmethod
    def get_postag(cats):
        """
        Finds postag from categories value.
        """
        assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
        if cats.startswith('Z '):
            postag = 'Z'
        elif cats.endswith('D '):
            postag = 'D'
        else:
            postag = (cats.split())[0] if len(cats.split()) >= 1 else 'X'
        return postag

    @staticmethod
    def get_syntax(syntax_analysis):
        """
        Finds deprel and head value if analysis has this info.
        """
        assert isinstance(syntax_analysis, str), '(!)Unexpected type for "syntax_analysis" argument! Expected a string.'
        syntax_chunks = syntax_analysis.split('#')
        deprel = syntax_chunks[0].strip(' ').split()
        id, head = syntax_chunks[1].split('->')
        if deprel == []:
            deprel = '_'
        return deprel, id, head

    def split_visl_analysis_line(self, line: str) -> Optional[Tuple[str]]:
        """
        Splits visl row analysis into four pieces 'lemma', 'ending', 'categories' and 'syntactical info'.
        If some info is missing, it's returned as ''.
        """
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        analysis_match = CG3AnnotationParser.pat_analysis_line.match(line)
        if not analysis_match:
            if line.startswith('  ') or line.startswith('\t'):
                if self.supress_exceptions:
                    return tuple(['', '', '', ''])
                else:
                    raise Exception('(!) Malformed analysis line: ' + line)
            return tuple(['', '', '', ''])
        return tuple(analysis_match.groups(default=''))

    def parse(self, line) -> dict:
        """
        Processes visl analysis line.
        """
        assert isinstance(line, str), '(!) Unexpected type of input argument! Expected a string.'
        if not (line.startswith('  ') or line.startswith('\t')):
            if self.supress_exceptions:
                return {}
            else:
                raise Exception('(!) Unexpected analysis line: ' + line)
        analysis = self.split_visl_analysis_line(line)
        lemma, ending, cats, syntax = analysis
        ending = ending.lstrip('L') if ending else '_'
        postag = self.get_postag(cats)
        forms, postag = self.get_forms(cats, postag, line)
        analysed_forms = self.get_analysed_forms(forms)
        # Visl row with syntactic analysis, e.g. "ole" Ln V main indic pres ps1 sg ps af @FMV #3->0
        if '#' in analysis[3]:
            deprel, id, head = self.get_syntax(syntax)
            return {'id': id, 'lemma': lemma, 'ending': ending, 'partofspeech': postag,
                    'deprel': deprel,
                    'head': head, **analysed_forms}
        # Visl row with verb or adpositions info, e.g. "ole" Ln V main indic pres ps1 sg ps af <FinV> <Intr>
        else:
            return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'deprel': '_',
                    'head': '_', **analysed_forms}
