from collections import OrderedDict
import re
import sys


def generate_cats_mapping():
    cats = {}
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
                      '<gen>', '<ja>', '<kom>', '<mata>', '<mine>', '<nom>', '<nu>', '<nud>', '<part>', '<tav>', '<tu>',
                      '<tud>', '<v>' '<Ter>', '<Tr>', '<Intr>', '<NGP-P>', '<NGP>', '<Part-P>']
    cats['punctuation_type'] = ['Col', 'Com', 'Cpr', 'Cqu', 'Csq', 'Dsd', 'Dsh', 'Ell',
                                'Els', 'Exc', 'Fst', 'Int', 'Opr', 'Oqu', 'Osq', 'Quo', 'Scl', 'Sla', 'Sml']
    return cats


def get_analysed_forms(forms, postag):
    assert isinstance(forms, list), '(!)Unexpected type for "forms" argument! Expected a list.'
    assert isinstance(postag, str), '(!)Unexpected type for "postag" argument! Expected a string.'
    analysed_forms = OrderedDict()
    cats = generate_cats_mapping()

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


def get_postag(cats):
    assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
    if cats.startswith('Z '):
        postag = 'Z'
    else:
        postag = (cats.split())[1] if len(cats.split()) > 1 else 'X'
    return postag


def get_ending(cats):
    assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
    ending = re.findall('^L(\w+)', cats)
    ending = ending[0] if ending else ''
    return ending


def get_syntax_info(cats):
    assert isinstance(cats, str), '(!)Unexpected type for "cats" argument! Expected a string.'
    deprels = re.findall('(@\S+)', cats)
    deprel = deprels[0] if deprels else 'xxx'
    heads = re.findall('#\d+\s*->\s*\d+', cats)[0]
    return deprel, heads


def process_visl_analysis_line(line):
    assert isinstance(line, str), '(!) Unexpected type of input argument! Expected a string.'
    error_on_unexp = False
    pat_analysis_line = re.compile('^\s+"(.+)"\s([^"]+)$')
    # 5 types of analyses:
    pat_ending_pos_form = re.compile('^L\S+\s+\S\s+([^#@]+).*$')
    pat_pos_form = re.compile('^\S\s+([^#@]+).*$')
    pat_ending_pos = re.compile('^(L\S+\s+)?\S\s+[#@].+$')
    pat_ending_pos2 = re.compile('^(L\S+\s+)?\S$')
    pat_ending_form_pos = re.compile('^L\w+ ([a-z]+) (\S)([^#@]+).*$')
    if line.startswith('  ') or line.startswith('\t'):
        analysis_match = pat_analysis_line.match(line)
        if analysis_match:
            lemma = analysis_match.group(1)
            cats = analysis_match.group(2)
            print(cats)
            postag = get_postag(cats)
            ending = get_ending(cats)
            # Features matching
            m1 = pat_ending_pos_form.match(cats)
            m2 = pat_pos_form.match(cats)
            m3 = pat_ending_pos.match(cats)
            m4 = pat_ending_pos2.match(cats)
            m5 = pat_ending_form_pos.match(cats)
            if m1:
                forms = (m1.group(1)).split()
            elif m2:
                forms = (m2.group(1)).split()
            elif m5:
                forms = (m5.group(1)).split()
                postag = m5.group(2)
            elif m3 or m4:
                forms = ['_']  # no form (in case of adpositions and adverbs)
            else:
                # Unexpected format of analysis line
                if error_on_unexp:
                    raise Exception('(!) Unexpected format of analysis line: ' + line)
                else:
                    postag = 'X'
                    forms = ['_']
                    print('(!) Unexpected format of analysis line: ' + line, file=sys.stderr)
            # Visl row with syntactic analysis, e.g. "ole" Ln V main indic pres ps1 sg ps af @FMV #3->0
            if ' #' in cats:
                deprel, heads = get_syntax_info(cats)
                forms = get_analysed_forms(forms, postag)
                return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': forms, 'deprel': deprel,
                        'head': heads}
            # Visl row with verb or adpositions info, e.g. "ole" Ln V main indic pres ps1 sg ps af <FinV> <Intr>
            else:
                forms = get_analysed_forms(forms, postag)
                return {'lemma': lemma, 'ending': ending, 'partofspeech': postag, 'feats': forms}
