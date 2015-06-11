# -*- coding: utf-8 -*-
'''
Module containing various feature extractors including local and global
features.
'''
from __future__ import unicode_literals, print_function

import re
import codecs
from collections import defaultdict
from functools import reduce


# Separator of field values.
separator = ' '

# Field names of the input data.
fields = 'y w pos chk'

# local features
def get_shape(token):
    r = u''
    for c in token:
        if c.isupper():
            r += 'U'
        elif c.islower():
            r += 'L'
        elif c.isdigit():
            r += 'D'
        elif c in ('.', ','):
            r += '.'
        elif c in (';', ':', '?', '!'):
            r += ';'
        elif c in ('+', '-', '*', '/', '=', '|', '_'):
            r += '-'
        elif c in ('(', '{', '[', '<'):
            r += '('
        elif c in (')', '}', ']', '>'):
            r += ')'
        else:
            r += c
    return r


def degenerate(src):
    dst = u''
    for c in src:
        if not dst or dst[-1] != c:
            dst += c
    return dst


def get_2d(token):
    return len(token) == 2 and token.isdigit()


def get_4d(token):
    return len(token) == 4 and token.isdigit()


def get_da(token):
    bd = False
    ba = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c.isalpha():
            ba = True
        else:
            return False
    return bd and ba


def get_dand(token, p):
    bd = False
    bdd = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c == p:
            bdd = True
        else:
            return False
    return bd and bdd


def get_all_other(token):
    for c in token:
        if c.isalnum():
            return False
    return True


def get_capperiod(token):
    return len(token) == 2 and token[0].isupper() and token[1] == '.'


def contains_upper(token):
    b = False
    for c in token:
        b |= c.isupper()
    return b


def contains_lower(token):
    b = False
    for c in token:
        b |= c.islower()
    return b


def contains_alpha(token):
    b = False
    for c in token:
        b |= c.isalpha()
    return b


def contains_digit(token):
    b = False
    for c in token:
        b |= c.isdigit()
    return b


def contains_symbol(token):
    for c in token:
        if not c.isalnum():
            return True
    return False


def split_char(token, char):
    return token.split(char, 1) if token.find(char) > -1 else [None, None]


def b(v):
    return 'y' if v else None


# morphological features
def get_lemma(morph_lemma):
    if len(morph_lemma) > 1:
        ridx = morph_lemma.rfind("=")
        if ridx == -1: ridx = morph_lemma.rfind("+")
        if ridx == -1: ridx = len(morph_lemma)
        if ridx > 0:
            morph_lemma = morph_lemma[:ridx]
        lemma = re.sub(r'(?<=[^\W_])_(?=[^\W_])', '', morph_lemma)
    else:
        lemma = morph_lemma 
    return lemma.lower()


def get_word_parts(morph_lemma):
    ridx = morph_lemma.rfind("=")
    if ridx == -1: ridx = morph_lemma.rfind("+")
    if ridx == -1: ridx = len(morph_lemma)
    lemma = morph_lemma[:ridx]
    lemma = lemma.lower()
    chunks = lemma.split("_")
    if len(chunks) > 1:
        prefix, postfix = chunks[0], chunks[-1]
    else:
        prefix, postfix = None, None
    return prefix, postfix


def get_case(morph):
    if morph.startswith("_S_") or morph.startswith("_H_"):
        try:
            case = morph[morph.rindex(" ") + 1: len(morph)]
        except ValueError:
            case = None
    else:
        case = None  
    return case


def get_ending(morph_lemma):
    try:
        end = morph_lemma[morph_lemma.index("+") + 1:]
    except ValueError:
        return None
    if end == "0":
        return None
    else:
        return end


def get_pos(morph):
    pos = morph.split()[0]
    return pos


def is_prop(morph):
    return morph.split()[0] == "_H_"


class BaseFeatureExtractor(object):
    '''Base class for all feature extractors.'''

    def __init__(self, *args, **kwargs):
        pass


    def prepare(self, docs):
        ''' Called before feature extraction actually happens. Can be used to 
        collect global statistics on the corpus. '''
        pass


    def process(self, doc):
        for token in doc.tokens:
            self._process(token)


    def _process(self, token):
        raise NotImplementedError("Not implemented!")


class MorphFeatureExtractor(BaseFeatureExtractor):
    '''Extracts features provided by the morphological analyser pyvabamorf. '''

    def _process(self, t):
        LEM  = "lem"
        POS  = "pos"
        PROP = "prop"
        PREF = "pref"
        POST = "post"
        CASE = "case"
        END  = "end"
        PUN  = "pun"
        t[LEM]  = get_lemma(t.lemma)
        t[POS]  = get_pos(t.morph)
        t[PROP] = b(is_prop(t.morph))
        t[PREF], t[POST] = get_word_parts(t.lemma)
        t[CASE] = get_case(t.morph)
        t[END]  = get_ending(t.lemma)
        t[PUN]  = b(t[POS] == '_Z_')


class GazetteerFeatureExtractor(BaseFeatureExtractor):
    '''Generates features indicating whether the token is present in a precompiled 
    list of organisations, geographical locations or person names. For instance, 
    if a token t occurs both in the list of person names (PER) and organisations (ORG), 
    assign t['gaz'] = ['PER', 'ORG']. With the parameter look_ahead, it is possible to 
    compose multi-token phrases for dictionary lookup. When look_ahead=N, phrases 
    (t[i], ..., t[i+N]) will be composed. If the phrase matches the dictionary, each
    token will be assigned the corresponding value. 
    '''

    def __init__(self, settings, look_ahead=3):
        '''Loads a gazetteer file. Can take some time!
        
        Parameters
        -----------
        
        settings: dict
            Global configuration dictionary.
        look_ahead: int
            A number of tokens to check to compose phrases.

        '''
        self.look_ahead = look_ahead
        self.data = defaultdict(set)
        with codecs.open(settings.GAZETTEER_FILE, 'rb', encoding="utf8") as f:
            for ln in f:
                word, lbl = ln.strip().rsplit("\t", 1)
                self.data[word].add(lbl)


    def process(self, doc):
        tokens = doc.tokens
        look_ahead = self.look_ahead
        for i in range(len(tokens)):
            if "iu" in tokens[i]: # Only capitalised strings
                for j in range(i + 1, i + 1 + look_ahead):
                    phrase = " ".join(token["lem"] for token in tokens[i:j])
                    if phrase in self.data:
                        labels = self.data[phrase]
                        for tok in tokens[i:j]:
                            try:
                                tok["gaz"] |= labels
                            except KeyError:
                                tok["gaz"] = labels


class GlobalContextFeatureExtractor(BaseFeatureExtractor):

    def process(self, doc):
        IUOC = 'iuoc'
        NPROP = 'nprop'
        PPROP = 'pprop'
        NGAZ = 'ngaz' 
        PGAZ = 'pgaz'
        ui_lems = set([t['lem'] for t in doc.tokens
                                    if ('iu' in t and 'fsnt' not in t and
                                        t.prew.word not in set([u'\u201d', u'\u201e', u'\u201c']))]) 
        sametoks_dict = defaultdict(list)
        for t in doc.tokens:
            if t['lem'] in ui_lems:
                sametoks_dict[t['lem']].append(t)

        for sametoks in sametoks_dict.values():
            for t in sametoks:
                t[IUOC] = 'y'

            if any(t.prew and 'prop' in t.prew for t in sametoks):
                for t in sametoks:
                    t[PPROP] = 'y'

            if any(t.next and 'prop' in t.next for t in sametoks):
                for t in sametoks:
                    t[NPROP] = 'y'

            pgaz_set = reduce(set.union, [t.prew["gaz"] for t in sametoks if t.prew and 'gaz' in t.prew], set([]))
            if pgaz_set: 
                for t in sametoks:
                    t[PGAZ] = pgaz_set

            ngaz_set = reduce(set.union, [t.next["gaz"] for t in sametoks if t.next and 'gaz' in t.next], set([]))
            if ngaz_set:
                for t in sametoks:
                    t[NGAZ] = ngaz_set


    def __process(self, doc):
        sametoks_dict = defaultdict(list)
        for t in doc.tokens:
            if "prop" in t:
                sametoks_dict[t['lem']].append(t)

        IUOC = 'iuoc'
        PLEM = 'plem'
        NLEM = 'nlem'
        NPROP = 'nprop'
        PPROP = 'pprop'
        NGAZ = 'ngaz' 
        PGAZ = 'pgaz'

        def add_feature(toks, fname, fvalue):
            for t in toks:
                t[fname] = fvalue

        def check_feature(sametoks, fname, fvalue, test_fun):
            for tok in sametoks:
                if test_fun(tok):
                    for t in sametoks:
                        t[fname] = fvalue
                    break

        for t in doc.tokens:
            if t['lem'] in sametoks_dict:
                sametoks = sametoks_dict[t['lem']]
                # Capitalized in other occurrences
                check_feature(sametoks, IUOC, "y", lambda tok: tok and "iu" in tok)
                # Prew proper in other occurrences
                check_feature(sametoks, PPROP, "y", lambda tok: tok.prew and "prop" in tok.prew)
                # Next proper in other occurrences
                check_feature(sametoks, NPROP, "y", lambda tok: tok.next and "prop" in tok.next)
                # Prew in gazeteer in other occurrences
                check_feature(sametoks, PGAZ, "y", lambda tok: tok.prew and "gaz" in tok.prew)
                # Next in gazeteer in other occurrences
                # Prew lemma in other occurrences
                check_feature(sametoks, PLEM, "y", lambda tok: tok.prew and "prop" in tok.prew)
                # Next lemma in other occurrences

                del sametoks_dict[t['lem']]


class SentenceFeatureExtractor(BaseFeatureExtractor):
    ''' Generates features for the first and last tokens in a sentence.'''

    def process(self, doc):
        FSNT = "fsnt"
        LSNT = "lsnt"
        for snt in doc.snts:
            if snt:
                snt[0][FSNT] = 'y'
                snt[-1][LSNT] = 'y'


class LocalFeatureExtractor(BaseFeatureExtractor):
    ''' Generates features for a token based on its character makeup '''

    def _process(self, t):
        W = "w" # token
        WL = "wl" # Lowercased token.
        SHAPE = "shape"
        SHAPED = "shaped"

        FEAT = 'lem'

        # Token.
        t[W] = t.word
        # Lowercased token.
        t[WL] = t.word.lower()
        # Token shape.
        t[SHAPE] = get_shape(t[W])
        # Token shape degenerated.
        t[SHAPED] = degenerate(t[SHAPE])

        P1 = "p1"
        P2 = "p2"
        P3 = "p3"
        P4 = "p4"

        # Prefixes (length between one to four).
        t[P1] = t[FEAT][0] if len(t[FEAT]) >= 1 else None
        t[P2] = t[FEAT][:2] if len(t[FEAT]) >= 2 else None
        t[P3] = t[FEAT][:3] if len(t[FEAT]) >= 3 else None
        t[P4] = t[FEAT][:4] if len(t[FEAT]) >= 4 else None

        S1 = "s1"
        S2 = "s2"
        S3 = "s3"
        S4 = "s4"

        # Suffixes (length between one to four).
        t[S1] = t[FEAT][-1] if len(t[FEAT]) >= 1 else None
        t[S2] = t[FEAT][-2:] if len(t[FEAT]) >= 2 else None
        t[S3] = t[FEAT][-3:] if len(t[FEAT]) >= 3 else None
        t[S4] = t[FEAT][-4:] if len(t[FEAT]) >= 4 else None

        DIG2 = "2d" # Two digits
        DIG4 = "4d" # Four digits.
        DIG_DASH = "d&-" # Digits and '-'.
        DIG_SLASH = "d&/" # Digits and '/'.
        DIG_COMA = "d&," # Digits and ','.
        DIG_DOT = "d&." # Digits and '.'.
        UP_DOT = "up" # A uppercase letter followed by '.'

        # Two digits
        t[DIG2] = b(get_2d(t[W]))
        # Four digits
        t[DIG4] = b(get_4d(t[W]))
        # Digits and '-'.
        t[DIG_DASH] = b(get_dand(t[W], '-'))
        # Digits and '/'.
        t[DIG_SLASH] = b(get_dand(t[W], '/'))
        # Digits and ','.
        t[DIG_COMA] = b(get_dand(t[W], ','))
        # Digits and '.'.
        t[DIG_DOT] = b(get_dand(t[W], '.'))
        # A uppercase letter followed by '.'
        t[UP_DOT] = b(get_capperiod(t[W]))

        IU = "iu"
        AU = "au"
        AL = "al"
        AD = "ad"
        AO = "ao"
        AN = "aan"

        # An initial uppercase letter.
        t[IU] = b(t[W] and t[W][0].isupper())
        # All uppercase letters.
        t[AU] = b(t[W].isupper())
        # All lowercase letters.
        t[AL] = b(t[W].islower())
        # All digit letters.
        t[AD] = b(t[W].isdigit())
        # All other (non-alphanumeric) letters.
        t[AO] = b(get_all_other(t[W]))
        # Alphanumeric token.
        t[AN] = b(t[W].isalnum())

        CU = "cu"
        CL = "cl"
        CA = "ca"
        CD = "cd"
        CS = "cs"
        CP = "cp"
        CDS = "cds"
        CDT = "cdt"

        # Contains an uppercase letter.
        t[CU] = b(contains_upper(t[W]))
        # Contains a lowercase letter.
        t[CL] = b(contains_lower(t[W]))
        # Contains a alphabet letter.
        t[CA] = b(contains_alpha(t[W]))
        # Contains a digit.
        t[CD] = b(contains_digit(t[W]))
        # Contains an apostrophe.
        t[CP] = b(t[W].find("'") > -1)
        # Contains a dash.
        t[CDS] = b(t[W].find("-") > -1)
        # Contains a dot.
        t[CDT] = b(t[W].find(".") > -1)
        # Contains a symbol.
        t[CS] = b(contains_symbol(t[W]))

        BDASH = "bdash"
        ADASH = "adash"
        BDOT = "bdot"
        ADOT = "adot"

        # Before, after dash
        t[BDASH], t[ADASH] = split_char(t[FEAT], '-')  

        # Before, after dot
        t[BDOT], t[ADOT] = split_char(t[FEAT], '.')

        # Length
        LEN = "len"
        t[LEN] = str(len(t[FEAT]))


def apply_templates(toks, templates):
    """
    Generate features for an item sequence by applying feature templates.
    A feature template consists of a tuple of (name, offset) pairs,
    where name and offset specify a field name and offset from which
    the template extracts a feature value. Generated features are stored
    in the 'F' field of each item in the sequence.

    Parameters
    ----------
    toks: list of tokens
        A list of processed toknes.

    templates: list of template tuples (str, int)
        A feature template consists of a tuple of (name, offset) pairs,
        where name and offset specify a field name and offset from which
        the template extracts a feature value.
    """
    def product(values_list):
        res = []
        if values_list:
            values = values_list[0]
            for head in values:
                for tail in product(values_list[1:]):
                    res.append([head] + tail)
        else:
            return [[]]
        return res

    for template in templates:
        name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
        for t in range(len(toks)):
            values_list = []
            for field, offset in template:
                p = t + offset
                if p < 0 or p >= len(toks):
                    values_list = []
                    break
                if field in toks[p]:
                    value = toks[p][field]
                    values_list.append(value if hasattr(value, "__iter__") else [value])
            if len(template) == len(values_list):
                for values in product(values_list):
                    toks[t]['F'].append('%s=%s' % (name, '|'.join(values)))


class FeatureExtractor(object):
    '''Feature extractor is used for decorating tokens of the documents
    with features specified in configuration files.
    '''

    def __init__(self, settings):
        '''Initialize the feature extractor.

        Parameters
        ----------
        settings: estnltk.estner.settings.Settings
            The settings and configuration of the NER system.
        '''
        self.settings = settings
        self.fex_list = []
        for fex_name in settings.FEATURE_EXTRACTORS:
            fex_class = FeatureExtractor._get_class(fex_name)
            fex_obj = fex_class(settings)
            self.fex_list.append(fex_obj)


    def prepare(self, docs):
        # init extractors
        for fex in self.fex_list:
            fex.prepare(docs)


    def process(self, docs):
        # extract features
        for fex in self.fex_list:
            for doc in docs:
                fex.process(doc)

        # apply the feature templates.
        for doc in docs:
            for snt in doc.snts:
                apply_templates(snt, self.settings.TEMPLATES)


    @staticmethod
    def _get_class(kls):
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
