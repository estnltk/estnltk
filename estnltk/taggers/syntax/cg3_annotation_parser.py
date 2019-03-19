from collections import OrderedDict, defaultdict
from typing import Tuple, Optional
import re
import sys


def get_reversed_mapping(cats):
    """
    Maps cats as 'form_value': ['category'].
    """
    reversed_cats_mapping = defaultdict(lambda: ['unknown_attribute'])
    for cat, forms in cats.items():
        for form in forms:
            if form not in reversed_cats_mapping:
                reversed_cats_mapping[form] = [cat]
            else:
                reversed_cats_mapping[form].append(cat)
    return reversed_cats_mapping


class CG3AnnotationParser:
    """
    Parser for parsing visl cg3 format analysis line.

    Example:
        line = '	"mari" Lle S com sg all cap @ADVL #1->4'
        parser = CG3AnnotationParser()
        processed_line = parser.process_visl_analysis_line(line)

    Output:
        {'lemma': 'mari', 'head': '#1->4', 'partofspeech': 'S', 'feats': \
        OrderedDict([('substantive_type', ['com']), ('number', ['sg']), ('case', ['all']), ('capitalized', ['cap'])]), \
        # 'deprel': '@ADVL ', 'ending': 'le'}
    """

    pat_analysis_line = re.compile('^\s+"(.+)" (L\w+)*([^@#]*)([@#]*.*)$')
    pat_pos_form = re.compile('^ *[A-Z]\s*([^#@]*).*$')
    pat_form_pos = re.compile('^ *([a-z]+) ([A-Z]).*$')

    cats = {'case': {'nom', 'gen', 'part', 'ill', 'in', 'el', 'all', 'ad', 'abl',
                     'tr', 'term', 'es', 'abes', 'kom', 'adit'},
            'number': {'sg', 'pl'},
            'voice': {'imps', 'ps'},
            'tense': {'pres', 'past', 'impf'},
            'mood': {'indic', 'cond', 'imper', 'quot'},
            'person': {'ps1', 'ps2', 'ps3'},
            'negation': {'af', 'neg'},
            'inf_form': {'sup', 'inf', 'ger', 'partic'},
            'pronoun_type': {'pos', 'det', 'refl', 'dem', 'inter_rel', 'pers', 'rel', 'rec', 'indef'},
            'adjective_type': {'pos', 'comp', 'super'},
            'verb_type': {'main', 'mod', 'aux'},
            'substantive_type': {'prop', 'com'},
            'numeral_type': {'card', 'ord'},
            'number_format': {'l', 'roman', 'digit'},
            'adposition_type': {'pre', 'post'},
            'conjunction_type': {'crd', 'sub'},
            'abbreviation_type': {'adjectival', 'adverbial', 'nominal', 'verbal'},
            'capitalized': {'cap'},
            'finiteness': {'<FinV>', '<Inf>', '<InfP>'},
            'subcat': {'<Abl>', '<Ad>', '<All>', '<El>', '<Es>', '<Ill>', '<In>', '<Kom>', '<Part>',
                       '<all>', '<el>', '<gen>', '<ja>', '<kom>', '<mata>', '<mine>', '<nom>', '<nu>',
                       '<nud>', '<part>', '<tav>', '<tu>', '<tud>', '<v>' '<Ter>', '<Tr>', '<Intr>',
                       '<NGP-P>', '<NGP>', '<Part-P>'},
            'punctuation_type': {'Col', 'Com', 'Cpr', 'Cqu', 'Csq', 'Dsd', 'Dsh', 'Ell',
                                 'Els', 'Exc', 'Fst', 'Int', 'Opr', 'Oqu', 'Osq', 'Quo', 'Scl', 'Sla',
                                 'Sml'},
            'clause_boundary': {'CLB'}}

    reversed_cats = get_reversed_mapping(cats)

    def get_forms(self, cats, postag, line):
        """
        Creates morphological features from morphological categories.
        """
        assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
        assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        # Features matching
        m1 = self.pat_pos_form.match(cats)
        m2 = self.pat_form_pos.match(cats)
        if m1:
            forms = (m1.group(1)).split()
        elif m2:
            forms = (m2.group(1)).split()
            postag = m2.group(2)
        else:
            postag = 'X'
            forms = ['']
            print('(!) Unexpected format of analysis line: ' + line, file=sys.stderr)
        return forms, postag

    def get_analysed_forms(self, forms, postag):
        """
        Finds attribute to each feature element.
        """
        assert isinstance(forms, list), '(!)Unexpected type for "forms" argument! Expected a list.'
        assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
        analysed_forms = OrderedDict()
        for form in forms:
            if form == 'pos':
                if postag == 'P':
                    analysed_forms['pronoun_type'] = ['pos']
                else:
                    analysed_forms['adjective_type'] = ['pos']
                continue
            if self.reversed_cats[form][0] not in analysed_forms:
                analysed_forms[self.reversed_cats[form][0]] = [form]
            else:
                analysed_forms[self.reversed_cats[form][0]].append(form)
        return analysed_forms

    def get_postag(self, cats):
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

    def get_syntax(self, syntax_analysis):
        """
        Finds deprel and head value if analysis has this info.
        """
        assert isinstance(syntax_analysis, str), '(!)Unexpected type for "syntax_analysis" argument! Expected a string.'
        syntax_chunks = syntax_analysis.split('#')
        deprel, heads = syntax_chunks[0], '#' + syntax_chunks[1]
        return deprel, heads

    def split_visl_analysis_line(self, line: str) -> Optional[Tuple[str]]:
        """
        Splits visl row analysis into four pieces 'lemma', 'ending', 'categories' and 'syntactical info'.
        If some info is missing, it's returned as ''.
        """
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        analysis_match = self.pat_analysis_line.match(line)
        if not analysis_match:
            if line.startswith('  ') or line.startswith('\t'):
                raise Exception('(!) Malformed analysis line: ' + line)
            return None
        return tuple(analysis_match.groups(default=''))

    def process_visl_analysis_line(self, line) -> dict:
        """
        Processes visl analysis line.
        """
        assert isinstance(line, str), '(!) Unexpected type of input argument! Expected a string.'
        if not (line.startswith('  ') or line.startswith('\t')):
            raise Exception('(!) Unexpected analysis line: ' + line)
        analysis = self.split_visl_analysis_line(line)
        lemma, ending, cats, syntax = analysis
        ending = ending.lstrip('L')
        postag = self.get_postag(cats)
        forms, postag = self.get_forms(cats, postag, line)
        analysed_forms = self.get_analysed_forms(forms, postag) if forms else ''
        # Visl row with syntactic analysis, e.g. "ole" Ln V main indic pres ps1 sg ps af @FMV #3->0
        if '#' in analysis[3]:
            deprel, heads = self.get_syntax(syntax)
            return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': analysed_forms,
                    'deprel': deprel,
                    'head': heads}
        # Visl row with verb or adpositions info, e.g. "ole" Ln V main indic pres ps1 sg ps af <FinV> <Intr>
        else:
            return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': analysed_forms}
