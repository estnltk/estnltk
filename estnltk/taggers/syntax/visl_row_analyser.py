from collections import OrderedDict, defaultdict
from typing import Tuple, Optional
import re
import sys


class CG3AnnotationParser:
    '''
    Parser for parsing visl cg3 format analysis line.

    Example:
        line = '	"mari" Lle S com sg all cap @ADVL #1->4'
        parser = CG3AnnotationParser()
        processed_line = parser.process_visl_analysis_line(line)

    Output:
        {'lemma': 'mari', 'head': '#1->4', 'partofspeech': 'S', 'feats': \
        OrderedDict([('substantive_type', ['com']), ('number', ['sg']), ('case', ['all']), ('capitalized', ['cap'])]), \
        # 'deprel': '@ADVL ', 'ending': 'le'}
    '''

    def generate_cats_mapping(self):
        cats = defaultdict(lambda: "unknown_attribute")
        cats['case'] = ['nom', 'gen', 'part', 'ill', 'in', 'el', 'all', 'ad', 'abl',
                        'tr', 'term', 'es', 'abes', 'kom', 'adit']
        cats['number'] = ['sg', 'pl']
        cats['voice'] = ['imps', 'ps']
        cats['tense'] = ['pres', 'past', 'impf']
        cats['mood'] = ['indic', 'cond', 'imper', 'quot']
        cats['person'] = ['ps1', 'ps2', 'ps3']
        cats['negation'] = ['af', 'neg']
        cats['inf_form'] = ['sup', 'inf', 'ger', 'partic']
        cats['pronoun_type'] = ['pos', 'det', 'refl', 'dem', 'inter_rel', 'pers', 'rel', 'rec', 'indef']
        cats['adjective_type'] = ['pos', 'comp', 'super']
        cats['verb_type'] = ['main', 'mod', 'aux']
        cats['substantive_type'] = ['prop', 'com']
        cats['numeral_type'] = ['card', 'ord']
        cats['number_format'] = ['l', 'roman', 'digit']
        cats['adposition_type'] = ['precollections', 'post']
        cats['conjunction_type'] = ['crd', 'sub']
        cats['abbreviation_type'] = ['adjectival', 'adverbial', 'nominal', 'verbal']
        cats['capitalized'] = ['cap']
        cats['finiteness'] = ['<FinV>', '<Inf>', '<InfP>']
        cats['subcat'] = ['<Abl>', '<Ad>', '<All>', '<El>', '<Es>', '<Ill>', '<In>', '<Kom>', '<Part>', '<all>', '<el>',
                          '<gen>', '<ja>', '<kom>', '<mata>', '<mine>', '<nom>', '<nu>', '<nud>', '<part>', '<tav>',
                          '<tu>', '<tud>', '<v>' '<Ter>', '<Tr>', '<Intr>', '<NGP-P>', '<NGP>', '<Part-P>']
        cats['punctuation_type'] = ['Col', 'Com', 'Cpr', 'Cqu', 'Csq', 'Dsd', 'Dsh', 'Ell',
                                    'Els', 'Exc', 'Fst', 'Int', 'Opr', 'Oqu', 'Osq', 'Quo', 'Scl', 'Sla', 'Sml']
        return cats

    def get_forms(self, cats, postag, line):
        '''
        Creates morphological features from morphological categories.
        '''
        assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
        assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        error_on_unexp = False
        # Features matching
        pat_pos_form = re.compile('^\s*[A-Z]\s*([^#@]*).*$')
        pat_form_pos = re.compile('^ ([a-z]+) ([A-Z]).*$')
        m1 = pat_pos_form.match(cats)
        m2 = pat_form_pos.match(cats)
        if m1:
            forms = (m1.group(1)).split()
        elif m2:
            forms = (m2.group(1)).split()
            postag = m2.group(2)
        else:
            # Unexpected format of analysis line
            if error_on_unexp:
                raise Exception('(!) Unexpected format of analysis line: ' + line)
            else:
                postag = 'X'
                forms = ['_']
                print('(!) Unexpected format of analysis line: ' + line, file=sys.stderr)
        return forms, postag

    def get_analysed_forms(self, forms, postag):
        '''
        Finds attribute to each feature element.
        '''
        assert isinstance(forms, list), '(!)Unexpected type for "forms" argument! Expected a list.'
        assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
        analysed_forms = OrderedDict()
        cats = self.generate_cats_mapping()

        for form in forms:
            if form == 'pos':
                if postag == 'P':
                    analysed_forms['pronoun_type'] = ['pos']
                else:
                    analysed_forms['adjective_type'] = ['pos']
                continue
            for key in cats.keys():
                if form in cats[key]:
                    if key not in analysed_forms:
                        analysed_forms[key] = [form]
                    else:
                        analysed_forms[key].append(form)
        return analysed_forms

    def get_postag(self, cats):
        '''
        Finds postag from categories value.
        '''
        assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
        if cats.startswith('Z '):
            postag = 'Z'
        elif cats.endswith('D '):
            postag = 'D'
        else:
            postag = (cats.split())[0] if len(cats.split()) >= 1 else 'X'
        return postag

    def get_syntax(self, syntax_analysis):
        '''
        Finds deprel and head value if analysis has this info.
        '''
        assert isinstance(syntax_analysis, str), '(!)Unexpected type for "syntax_analysis" argument! Expected a string.'
        syntax_chunks = syntax_analysis.split('#')
        deprel, heads = syntax_chunks[0], '#' + syntax_chunks[1]
        return deprel, heads

    def split_visl_analysis_line(self, line: str) -> Optional[Tuple[str]]:
        '''
        Splits visl row analysis into four pieces 'lemma', 'ending', 'categories' and 'syntactical info'.
        If some info is missing, it's returned as ''.
        '''
        assert isinstance(line, str), '(!)Unexpected type for "line" argument! Expected a string.'
        pat_analysis_line = re.compile('^\s+"(.+)" (L\w+)*([^@#]*)([@#]*.*)$')
        analysis_match = pat_analysis_line.match(line)
        if not analysis_match:
            if line.startswith('  ') or line.startswith('\t'):
                raise Exception('(!) Malformed analysis line: ' + line)
            return None
        return tuple(analysis_match.groups(default=''))

    def process_visl_analysis_line(self, line) -> dict:
        '''
        Processes visl analysis line.
        '''
        assert isinstance(line, str), '(!) Unexpected type of input argument! Expected a string.'
        if line.startswith('  ') or line.startswith('\t'):
            analysis = self.split_visl_analysis_line(line)
            lemma = analysis[0]
            ending = analysis[1].strip('L')
            cats = analysis[2]
            postag = self.get_postag(cats)
            # Visl row with syntactic analysis, e.g. "ole" Ln V main indic pres ps1 sg ps af @FMV #3->0
            if '#' in analysis[3]:
                deprel, heads = self.get_syntax(analysis[3])
                forms, postag = self.get_forms(cats, postag, line)
                analysed_forms = self.get_analysed_forms(forms, postag)
                return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': analysed_forms,
                        'deprel': deprel,
                        'head': heads}
            # Visl row with verb or adpositions info, e.g. "ole" Ln V main indic pres ps1 sg ps af <FinV> <Intr>
            else:
                forms, postag = self.get_forms(cats, postag, line)
                analysed_forms = self.get_analysed_forms(forms, postag)
                return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': analysed_forms}
